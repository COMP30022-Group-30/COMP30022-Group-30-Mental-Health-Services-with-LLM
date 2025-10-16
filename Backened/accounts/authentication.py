from __future__ import annotations

from typing import Optional

from django.conf import settings
from rest_framework import exceptions
from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication


class AdminCookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that prefers secure HttpOnly cookies and enforces CSRF
    validation for state-changing requests.
    """

    access_cookie_name = "admin_access"
    refresh_cookie_name = "admin_refresh"
    csrf_cookie_name = "admin_csrf"
    csrf_header_name = "HTTP_X_CSRFTOKEN"

    def authenticate(self, request):
        header = self.get_header(request)
        raw_token = None

        if header is not None:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            raw_token = request.COOKIES.get(self.access_cookie_name)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        self._enforce_csrf(request)
        return self.get_user(validated_token), validated_token

    def _enforce_csrf(self, request):
        if request.method in SAFE_METHODS:
            return

        csrf_cookie = request.COOKIES.get(self.csrf_cookie_name)
        header_token = request.META.get(self.csrf_header_name) or request.headers.get("X-CSRFToken")

        if not csrf_cookie or not header_token:
            raise exceptions.PermissionDenied("CSRF token missing.")

        if csrf_cookie != header_token:
            raise exceptions.PermissionDenied("CSRF token mismatch.")


def set_auth_cookies(response, access: str, refresh: str, csrf_token: str, secure: Optional[bool] = None):
    """
    Helper to apply secure authentication cookies to a response.
    """

    secure_flag = secure if secure is not None else not settings.DEBUG
    samesite = getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax")

    response.set_cookie(
        AdminCookieJWTAuthentication.access_cookie_name,
        access,
        httponly=True,
        secure=secure_flag,
        samesite=samesite,
        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
    )
    response.set_cookie(
        AdminCookieJWTAuthentication.refresh_cookie_name,
        refresh,
        httponly=True,
        secure=secure_flag,
        samesite=samesite,
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
    )
    response.set_cookie(
        AdminCookieJWTAuthentication.csrf_cookie_name,
        csrf_token,
        httponly=False,
        secure=secure_flag,
        samesite=samesite,
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
    )


def clear_auth_cookies(response):
    """
    Removes auth cookies from the client.
    """

    response.delete_cookie(AdminCookieJWTAuthentication.access_cookie_name)
    response.delete_cookie(AdminCookieJWTAuthentication.refresh_cookie_name)
    response.delete_cookie(AdminCookieJWTAuthentication.csrf_cookie_name)
