from __future__ import annotations

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """
    Stores per-user metadata and role assignments for access control.
    """

    class Role(models.TextChoices):
        USER = "user", _("Service User")
        PROVIDER = "provider", _("Service Provider")
        MODERATOR = "moderator", _("Moderator")
        ADMIN = "admin", _("Administrator")
        SUPER_ADMIN = "super_admin", _("Super Administrator")

    user = models.OneToOneField(
        User,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.USER,
    )
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\-().\s]{7,32}$",
                message=_("Enter a valid phone number."),
            )
        ],
    )
    job_title = models.CharField(max_length=128, blank=True)
    organisation = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self) -> bool:
        return self.role in {
            self.Role.ADMIN,
            self.Role.SUPER_ADMIN,
            self.Role.MODERATOR,
        }

    @property
    def is_super_admin(self) -> bool:
        return self.role == self.Role.SUPER_ADMIN


class ProviderProfile(models.Model):
    """
    Domain-specific profile used by admins to vet and manage providers.
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending Review")
        APPROVED = "approved", _("Approved")
        DISABLED = "disabled", _("Disabled")
        REJECTED = "rejected", _("Rejected")

    user = models.OneToOneField(
        User,
        related_name="provider_profile",
        on_delete=models.CASCADE,
    )
    display_name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\-().\s]{7,32}$",
                message=_("Enter a valid phone number."),
            )
        ],
    )
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reviewed_by = models.ForeignKey(
        User,
        related_name="reviewed_providers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name


@receiver(post_save, sender=User)
def ensure_profile(sender, instance: User, created: bool, **kwargs):
    """
    Guarantee that every Django user has a matching Profile row.
    """

    if created:
        Profile.objects.create(user=instance)
