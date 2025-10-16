from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ServiceCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PENDING = "pending", _("Pending Review")
        APPROVED = "approved", _("Approved")
        DISABLED = "disabled", _("Disabled")
        REJECTED = "rejected", _("Rejected")

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    category = models.ForeignKey(
        ServiceCategory,
        related_name="services",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    provider = models.ForeignKey(
        "accounts.ProviderProfile",
        related_name="services",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False,
    )
    created_by = models.ForeignKey(
        User,
        related_name="created_services",
        on_delete=models.SET_NULL,
        null=True,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="updated_services",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        User,
        related_name="approved_services",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    approval_notes = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.name

    def mark_approved(self, user: User, notes: str = ""):
        from django.utils import timezone

        self.status = self.Status.APPROVED
        self.approval_notes = notes
        self.approved_by = user
        self.approved_at = timezone.now()


@receiver(pre_save, sender=ServiceCategory)
def service_category_slug(sender, instance: ServiceCategory, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Service)
def service_slug(sender, instance: Service, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)
