from django.contrib import admin

from .models import Service, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "provider",
        "category",
        "updated_at",
    )
    list_filter = ("status", "category")
    search_fields = ("name", "provider__display_name")
    autocomplete_fields = ("provider", "category", "created_by", "updated_by", "approved_by")
