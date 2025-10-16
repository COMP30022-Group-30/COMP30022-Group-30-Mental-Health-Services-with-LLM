from __future__ import annotations

from typing import Any

import structlog

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.middleware.csrf import get_token
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .authentication import (
    AdminCookieJWTAuthentication,
    clear_auth_cookies,
    set_auth_cookies,
)
from .models import Profile, ProviderProfile
from .pagination import AdminPagination
from .permissions import IsAdmin, IsSuperAdmin
from .serializers import (
    AdminUserCreateSerializer,
    AdminUserSerializer,
    ProviderModerationSerializer,
    ProviderProfileSerializer,
    UserAdminCreateSerializer,
    UserAdminUpdateSerializer,
    UserSerializer,
)
from .throttles import AdminLoginRateThrottle
from .tokens import AdminTokenObtainPairSerializer

User = get_user_model()
logger = structlog.get_logger(__name__)


class AdminTokenObtainPairView(TokenObtainPairView):
    """
    JWT authentication endpoint restricted to admin-tier accounts.
    """

    serializer_class = AdminTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AdminLoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc

        data = serializer.validated_data
        response = Response(data, status=status.HTTP_200_OK)
        csrf_token = get_token(request)
        set_auth_cookies(response, data["access"], data["refresh"], csrf_token)
        response.data["csrfToken"] = csrf_token
        return response


class AdminTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh") or request.COOKIES.get(
            AdminCookieJWTAuthentication.refresh_cookie_name
        )
        if not refresh_token:
            raise ValidationError({"refresh": "Refresh token is required."})

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc

        data = serializer.validated_data
        response = Response(data, status=status.HTTP_200_OK)
        access_token = data["access"]
        refresh_value = data.get("refresh", refresh_token)
        csrf_token = request.COOKIES.get(AdminCookieJWTAuthentication.csrf_cookie_name) or get_token(request)
        set_auth_cookies(response, access_token, refresh_value, csrf_token)
        response.data["csrfToken"] = csrf_token
        try:
            payload = AccessToken(access_token)
            user = User.objects.get(id=payload["user_id"])
            response.data["user"] = AdminUserSerializer(user).data
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to attach user to refresh response", error=str(exc))
        return response


class AdminLogoutView(APIView):
    """
    Blacklists the provided refresh token to invalidate the session.
    """

    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh") or request.COOKIES.get(
            AdminCookieJWTAuthentication.refresh_cookie_name
        )
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = Response({"detail": "Logged out."}, status=status.HTTP_205_RESET_CONTENT)
        clear_auth_cookies(response)
        return response


class AdminMeView(APIView):
    """
    Provides profile information for the authenticated administrator.
    """

    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):
        serializer = AdminUserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        serializer = UserAdminUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminUserSerializer(request.user).data)


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for platform users managed by administrators.
    """

    queryset = (
        User.objects.select_related("profile")
        .all()
        .order_by("-date_joined")
    )
    permission_classes = [IsAdmin]
    pagination_class = AdminPagination
    search_fields = ("username", "email", "first_name", "last_name")
    ordering_fields = ("username", "email", "date_joined", "last_login")
    filterset_fields = {
        "is_active": ["exact"],
        "profile__role": ["exact"],
    }

    def get_serializer_class(self):
        if self.action == "create":
            return UserAdminCreateSerializer
        if self.action in {"update", "partial_update"}:
            return UserAdminUpdateSerializer
        return UserSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return queryset

    def _assert_can_manage_role(self, target_profile: Profile):
        actor_profile = getattr(self.request.user, "profile", None)
        if not actor_profile:
            raise PermissionDenied("Missing profile.")

        if target_profile.role in {
            Profile.Role.ADMIN,
            Profile.Role.SUPER_ADMIN,
            Profile.Role.MODERATOR,
        } and actor_profile.role != Profile.Role.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can manage admin accounts.")

        if actor_profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot modify user accounts.")

    def perform_create(self, serializer):
        profile_payload = serializer.validated_data.get("profile", {})
        role = profile_payload.get("role", Profile.Role.USER)
        if role in {
            Profile.Role.ADMIN,
            Profile.Role.SUPER_ADMIN,
            Profile.Role.MODERATOR,
        }:
            actor_profile = getattr(self.request.user, "profile", None)
            if not actor_profile or actor_profile.role != Profile.Role.SUPER_ADMIN:
                raise PermissionDenied("Only super admins can create admin accounts.")
        serializer.save()

    def perform_update(self, serializer):
        instance = serializer.instance
        self._assert_can_manage_role(instance.profile)
        serializer.save()

    def perform_destroy(self, instance):
        self._assert_can_manage_role(instance.profile)
        instance.delete()


class AdminManagementViewSet(viewsets.ModelViewSet):
    """
    Dedicated endpoints for super admins to manage other administrator accounts.
    """

    permission_classes = [IsSuperAdmin]
    pagination_class = AdminPagination
    search_fields = ("username", "email", "first_name", "last_name")
    ordering_fields = ("username", "email", "date_joined", "last_login")

    def get_queryset(self):
        return (
            User.objects.select_related("profile")
            .filter(
                profile__role__in=[
                    Profile.Role.ADMIN,
                    Profile.Role.SUPER_ADMIN,
                    Profile.Role.MODERATOR,
                ]
            )
            .order_by("-date_joined")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return AdminUserCreateSerializer
        if self.action in {"update", "partial_update"}:
            return UserAdminUpdateSerializer
        return AdminUserSerializer

    def perform_destroy(self, instance):
        if instance == self.request.user:
            raise PermissionDenied("You cannot delete your own account.")
        instance.delete()


class ProviderManagementViewSet(viewsets.ModelViewSet):
    """
    Admin and moderators can manage provider applications and directory entries.
    """

    queryset = ProviderProfile.objects.select_related("user", "user__profile").all()
    permission_classes = [IsAdmin]
    pagination_class = AdminPagination
    serializer_class = ProviderProfileSerializer
    search_fields = ("display_name", "contact_email", "user__username")
    ordering_fields = ("display_name", "status", "created_at")
    filterset_fields = {"status": ["exact"]}

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(display_name__icontains=search)
                | Q(contact_email__icontains=search)
                | Q(user__username__icontains=search)
            )
        return queryset

    def get_serializer_class(self):
        if self.action in {"approve", "disable", "set_status"}:
            return ProviderModerationSerializer
        return super().get_serializer_class()

    def _actor_profile(self) -> Profile:
        profile = getattr(self.request.user, "profile", None)
        if not profile:
            raise PermissionDenied("Missing administrator profile.")
        return profile

    def perform_create(self, serializer):
        profile = self._actor_profile()
        if profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot manually create providers.")
        serializer.save()

    def perform_destroy(self, instance):
        profile = self._actor_profile()
        if profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot delete providers.")
        instance.delete()

    def _set_status(self, request, instance: ProviderProfile, status_value: str):
        profile = getattr(request.user, "profile", None)
        if not profile:
            raise PermissionDenied("Missing administrator profile.")
        if profile.role == Profile.Role.MODERATOR and status_value not in {
            ProviderProfile.Status.APPROVED,
            ProviderProfile.Status.DISABLED,
        }:
            raise PermissionDenied("Moderators may only approve or disable providers.")

        serializer = ProviderModerationSerializer(
            instance,
            data={"status": status_value, "notes": request.data.get("notes", "")},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.reviewed_by = request.user
        instance.reviewed_at = timezone.now()
        instance.save()
        return Response(ProviderProfileSerializer(instance).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        provider = self.get_object()
        return self._set_status(request, provider, ProviderProfile.Status.APPROVED)

    @action(detail=True, methods=["post"], url_path="disable")
    def disable(self, request, pk=None):
        provider = self.get_object()
        return self._set_status(request, provider, ProviderProfile.Status.DISABLED)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        provider = self.get_object()
        return self._set_status(request, provider, ProviderProfile.Status.REJECTED)

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        provider = self.get_object()
        status_value = request.data.get("status")
        if status_value not in dict(ProviderProfile.Status.choices).keys():
            raise ValidationError({"status": "Invalid provider status."})
        return self._set_status(request, provider, status_value)
