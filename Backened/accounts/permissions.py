from __future__ import annotations

from typing import Iterable

from rest_framework.permissions import BasePermission

from .models import Profile


def _has_role(user, roles: Iterable[str]) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    profile = getattr(user, "profile", None)
    if not profile:
        return False
    return profile.role in roles


class IsAdmin(BasePermission):
    """
    Allows access only to authenticated users with an admin-tier role.
    """

    admin_roles = {
        Profile.Role.ADMIN,
        Profile.Role.SUPER_ADMIN,
        Profile.Role.MODERATOR,
    }

    def has_permission(self, request, view):
        return _has_role(request.user, self.admin_roles)


class IsSuperAdmin(BasePermission):
    """
    Restrict access to super administrators.
    """

    def has_permission(self, request, view):
        return _has_role(request.user, {Profile.Role.SUPER_ADMIN})


class IsAdminOrReadOnly(IsAdmin):
    """
    Allow reads for any authenticated admin while restricting mutations to admins.
    """

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return super().has_permission(request, view)
        return _has_role(
            request.user,
            {
                Profile.Role.ADMIN,
                Profile.Role.SUPER_ADMIN,
            },
        )
