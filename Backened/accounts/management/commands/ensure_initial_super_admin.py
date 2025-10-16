from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Profile


class Command(BaseCommand):
    help = "Creates or updates the initial super admin from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("INITIAL_SUPER_ADMIN_USERNAME")
        email = os.getenv("INITIAL_SUPER_ADMIN_EMAIL")
        password = os.getenv("INITIAL_SUPER_ADMIN_PASSWORD")
        password_hash = os.getenv("INITIAL_SUPER_ADMIN_PASSWORD_HASH")

        if not username or not email:
            self.stdout.write(self.style.WARNING("Super admin env vars not provided; skipping."))
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created super admin '{username}'."))
        else:
            self.stdout.write(self.style.WARNING(f"Super admin '{username}' already exists; ensuring attributes."))

        if user.email != email:
            user.email = email

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        if password_hash:
            user.password = password_hash
        elif password:
            user.set_password(password)
        elif created:
            self.stdout.write(self.style.ERROR("INITIAL_SUPER_ADMIN_PASSWORD or *_PASSWORD_HASH must be set for new account."))
            user.delete()
            return

        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = Profile.Role.SUPER_ADMIN
        profile.save()

        self.stdout.write(self.style.SUCCESS("Super admin credentials ensured."))
