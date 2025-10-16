from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import Profile, ProviderProfile

User = get_user_model()


def _apply_role_flags(user: User, role: str | None) -> None:
    if role is None:
        return
    user.is_staff = role in {
        Profile.Role.ADMIN,
        Profile.Role.MODERATOR,
        Profile.Role.SUPER_ADMIN,
    }
    user.is_superuser = role == Profile.Role.SUPER_ADMIN


class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.Role.choices)

    class Meta:
        model = Profile
        fields = (
            "role",
            "phone_number",
            "job_title",
            "organisation",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
            "profile",
        )
        read_only_fields = ("id", "date_joined", "last_login", "profile")


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        source="profile.role",
        choices=Profile.Role.choices,
        required=False,
    )
    phone_number = serializers.CharField(source="profile.phone_number", required=False, allow_blank=True)
    job_title = serializers.CharField(source="profile.job_title", required=False, allow_blank=True)
    organisation = serializers.CharField(source="profile.organisation", required=False, allow_blank=True)
    notes = serializers.CharField(source="profile.notes", required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "role",
            "phone_number",
            "job_title",
            "organisation",
            "notes",
        )

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        profile_data = validated_data.pop("profile", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        pending_role = profile_data.get("role")
        if pending_role:
            _apply_role_flags(instance, pending_role)
        instance.save()

        if profile_data:
            profile, _ = Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12, trim_whitespace=False)
    role = serializers.ChoiceField(
        choices=[
            (Profile.Role.ADMIN, Profile.Role.ADMIN.label),
            (Profile.Role.MODERATOR, Profile.Role.MODERATOR.label),
            (Profile.Role.SUPER_ADMIN, Profile.Role.SUPER_ADMIN.label),
        ],
        source="profile.role",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
        )
        read_only_fields = ("id",)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> User:
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        _apply_role_flags(user, profile_data.get("role"))
        user.save()

        Profile.objects.update_or_create(
            user=user,
            defaults={**profile_data},
        )
        return user


class UserAdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10, trim_whitespace=False)
    role = serializers.ChoiceField(
        choices=Profile.Role.choices,
        default=Profile.Role.USER,
        source="profile.role",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
        )
        read_only_fields = ("id",)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> User:
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        _apply_role_flags(user, profile_data.get("role"))
        user.save()

        Profile.objects.update_or_create(
            user=user,
            defaults={**profile_data},
        )
        return user


class AdminUserSerializer(UserSerializer):
    profile = ProfileSerializer()


class ProviderProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=True,
    )
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProviderProfile
        fields = (
            "id",
            "user",
            "user_id",
            "display_name",
            "contact_email",
            "phone_number",
            "website",
            "description",
            "address",
            "status",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        )

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> ProviderProfile:
        user = validated_data["user"]
        provider = super().create(validated_data)
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = Profile.Role.PROVIDER
        profile.save()
        return provider

    @transaction.atomic
    def update(self, instance: ProviderProfile, validated_data: dict[str, Any]) -> ProviderProfile:
        provider = super().update(instance, validated_data)
        profile, _ = Profile.objects.get_or_create(user=provider.user)
        if profile.role != Profile.Role.PROVIDER:
            profile.role = Profile.Role.PROVIDER
            profile.save()
        return provider


class ProviderModerationSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=ProviderProfile.Status.choices)
    notes = serializers.CharField(source="user.profile.notes", required=False, allow_blank=True)

    class Meta:
        model = ProviderProfile
        fields = ("status", "notes")

    def update(self, instance: ProviderProfile, validated_data: dict[str, Any]) -> ProviderProfile:
        profile_updates = validated_data.pop("user", {}).get("profile", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if profile_updates:
            profile = instance.user.profile
            for attr, value in profile_updates.items():
                setattr(profile, attr, value)
            profile.save()

        instance.save()
        return instance
