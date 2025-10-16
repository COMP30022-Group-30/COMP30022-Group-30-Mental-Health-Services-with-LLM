from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminLogoutView,
    AdminManagementViewSet,
    AdminMeView,
    AdminTokenObtainPairView,
    AdminTokenRefreshView,
    ProviderManagementViewSet,
    UserManagementViewSet,
)
from services.views import ServiceCategoryViewSet, ServiceManagementViewSet

router = DefaultRouter()
router.register("users", UserManagementViewSet, basename="admin-users")
router.register("admins", AdminManagementViewSet, basename="admin-admins")
router.register("providers", ProviderManagementViewSet, basename="admin-providers")
router.register("services", ServiceManagementViewSet, basename="admin-services")
router.register("service-categories", ServiceCategoryViewSet, basename="admin-service-categories")

urlpatterns = [
    path("auth/login/", AdminTokenObtainPairView.as_view(), name="admin-auth-login"),
    path("auth/refresh/", AdminTokenRefreshView.as_view(), name="admin-auth-refresh"),
    path("auth/logout/", AdminLogoutView.as_view(), name="admin-auth-logout"),
    path("auth/me/", AdminMeView.as_view(), name="admin-auth-me"),
    path("", include(router.urls)),
]
