from __future__ import annotations

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from accounts.models import Profile
from accounts.permissions import IsAdmin
from accounts.pagination import AdminPagination
from .models import Service, ServiceCategory
from .serializers import (
    ServiceCategorySerializer,
    ServiceCreateUpdateSerializer,
    ServiceSerializer,
    ServiceStatusUpdateSerializer,
)


class ServiceManagementViewSet(viewsets.ModelViewSet):
    """
    Administrative CRUD interface for managing services and approvals.
    """

    queryset = (
        Service.objects.select_related(
            "provider",
            "provider__user",
            "provider__user__profile",
            "category",
            "created_by",
            "updated_by",
            "approved_by",
        )
        .all()
        .order_by("-updated_at")
    )
    permission_classes = [IsAdmin]
    pagination_class = AdminPagination
    search_fields = ("name", "provider__display_name", "category__name")
    ordering_fields = ("name", "status", "updated_at", "created_at")
    filterset_fields = {
        "status": ["exact"],
        "category": ["exact"],
    }

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return ServiceCreateUpdateSerializer
        if self.action in {"approve", "disable", "reject", "set_status"}:
            return ServiceStatusUpdateSerializer
        return ServiceSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(provider__display_name__icontains=search)
                | Q(category__name__icontains=search)
            )
        return queryset

    def _actor_profile(self) -> Profile:
        profile = getattr(self.request.user, "profile", None)
        if not profile:
            raise PermissionDenied("Missing administrator profile.")
        return profile

    def perform_create(self, serializer):
        profile = self._actor_profile()
        if profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot create services.")
        serializer.save()

    def perform_update(self, serializer):
        profile = self._actor_profile()
        if profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot update services directly.")
        serializer.save()

    def perform_destroy(self, instance):
        profile = self._actor_profile()
        if profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot delete services.")
        instance.delete()

    def _set_status(self, service: Service, status_value: str, notes: str = ""):
        profile = self._actor_profile()
        allowed_for_moderators = {
            Service.Status.APPROVED,
            Service.Status.DISABLED,
            Service.Status.REJECTED,
        }
        if profile.role == Profile.Role.MODERATOR and status_value not in allowed_for_moderators:
            raise PermissionDenied("Moderators do not have permission to set this status.")

        serializer = ServiceStatusUpdateSerializer(
            service,
            data={"status": status_value, "approval_notes": notes},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated = serializer.save(
            approved_by=self.request.user,
            approved_at=timezone.now(),
        )
        return Response(ServiceSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        service = self.get_object()
        notes = request.data.get("approval_notes", "")
        return self._set_status(service, Service.Status.APPROVED, notes)

    @action(detail=True, methods=["post"], url_path="disable")
    def disable(self, request, pk=None):
        service = self.get_object()
        notes = request.data.get("approval_notes", "")
        return self._set_status(service, Service.Status.DISABLED, notes)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        service = self.get_object()
        notes = request.data.get("approval_notes", "")
        return self._set_status(service, Service.Status.REJECTED, notes)

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        service = self.get_object()
        status_value = request.data.get("status")
        if status_value not in dict(Service.Status.choices):
            raise ValidationError({"status": "Invalid service status."})
        notes = request.data.get("approval_notes", "")
        return self._set_status(service, status_value, notes)


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    Manage service categories and taxonomy.
    """

    queryset = ServiceCategory.objects.all().order_by("name")
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAdmin]
    pagination_class = None

    def _actor_profile(self) -> Profile:
        profile = getattr(self.request.user, "profile", None)
        if not profile:
            raise PermissionDenied("Missing administrator profile.")
        return profile

    def perform_create(self, serializer):
        profile = self._actor_profile()
        if profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot create categories.")
        serializer.save()

    def perform_destroy(self, instance):
        profile = self._actor_profile()
        if profile.role == Profile.Role.MODERATOR:
            raise PermissionDenied("Moderators cannot delete categories.")
        instance.delete()
