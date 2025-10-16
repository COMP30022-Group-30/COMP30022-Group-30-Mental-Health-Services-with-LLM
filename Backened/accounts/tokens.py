from __future__ import annotations

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT serializer to enforce admin-only authentication.
    """

    default_error_messages = {
        "no_active_account": "Invalid credentials or inactive account.",
        "insufficient_role": "Administrator access required.",
    }

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        profile = getattr(user, "profile", None)
        if not profile or profile.role not in {
            Profile.Role.ADMIN,
            Profile.Role.SUPER_ADMIN,
            Profile.Role.MODERATOR,
        }:
            raise serializers.ValidationError(self.error_messages["insufficient_role"])

        from .serializers import AdminUserSerializer  # local import to avoid circular dep

        data["user"] = AdminUserSerializer(user).data
        return data
