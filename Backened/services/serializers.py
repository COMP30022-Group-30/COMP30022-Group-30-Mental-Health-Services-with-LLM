from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import ProviderProfileSerializer
from accounts.models import ProviderProfile, Profile
from .models import Service, ServiceCategory

User = get_user_model()


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "slug", "description", "created_at", "updated_at")
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class ServiceSerializer(serializers.ModelSerializer):
    provider = ProviderProfileSerializer(read_only=True)
    category = ServiceCategorySerializer(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    approved_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "slug",
            "summary",
            "description",
            "category",
            "provider",
            "created_by",
            "updated_by",
            "approved_by",
            "status",
            "approval_notes",
            "approved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "created_by",
            "updated_by",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        )


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=ProviderProfile.objects.all(),
        source="provider",
        required=False,
        allow_null=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        source="category",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "summary",
            "description",
            "status",
            "provider_id",
            "category_id",
            "approval_notes",
        )
        read_only_fields = ("id",)

    def validate_status(self, value: str):
        """
        Restrict moderators from creating services in privileged states.
        """

        request = self.context.get("request")
        if not request:
            return value
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == Profile.Role.MODERATOR and value not in {
            Service.Status.PENDING,
            Service.Status.APPROVED,
            Service.Status.DISABLED,
        }:
            raise serializers.ValidationError("Moderators cannot set this status.")
        return value

    def create(self, validated_data: dict[str, Any]) -> Service:
        request = self.context.get("request")
        if request:
            validated_data.setdefault("created_by", request.user)
            validated_data.setdefault("updated_by", request.user)
        return super().create(validated_data)

    def update(self, instance: Service, validated_data: dict[str, Any]) -> Service:
        request = self.context.get("request")
        if request:
            validated_data["updated_by"] = request.user
        return super().update(instance, validated_data)


class ServiceStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Service.Status.choices)
    approval_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Service
        fields = ("status", "approval_notes")
