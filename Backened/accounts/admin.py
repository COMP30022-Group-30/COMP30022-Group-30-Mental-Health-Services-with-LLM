from django.contrib import admin

from .models import Profile, ProviderProfile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone_number", "created_at", "updated_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "organisation")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "status", "contact_email", "phone_number", "updated_at")
    list_filter = ("status",)
    search_fields = ("display_name", "contact_email", "user__username")
    readonly_fields = ("created_at", "updated_at", "reviewed_at")
