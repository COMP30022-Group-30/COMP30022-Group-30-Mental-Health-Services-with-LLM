from django.conf import settings
from django.core import validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("user", "Service User"),
                            ("provider", "Service Provider"),
                            ("moderator", "Moderator"),
                            ("admin", "Administrator"),
                            ("super_admin", "Super Administrator"),
                        ],
                        default="user",
                        max_length=32,
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=32,
                        validators=[
                            validators.RegexValidator(
                                message="Enter a valid phone number.",
                                regex="^\\+?[0-9\\-().\\s]{7,32}$",
                            )
                        ],
                    ),
                ),
                ("job_title", models.CharField(blank=True, max_length=128)),
                ("organisation", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=models.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["user__username"],
            },
        ),
        migrations.CreateModel(
            name="ProviderProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("display_name", models.CharField(max_length=255)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=32,
                        validators=[
                            validators.RegexValidator(
                                message="Enter a valid phone number.",
                                regex="^\\+?[0-9\\-().\\s]{7,32}$",
                            )
                        ],
                    ),
                ),
                ("website", models.URLField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("address", models.CharField(blank=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending Review"),
                            ("approved", "Approved"),
                            ("disabled", "Disabled"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="reviewed_providers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=models.CASCADE,
                        related_name="provider_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["display_name"],
            },
        ),
    ]
