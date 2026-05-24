from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, ProfileViewSet, AddressViewSet, AdminUserViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'addresses', AddressViewSet, basename='addresses')

admin_router = DefaultRouter(trailing_slash=False)
admin_router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(admin_router.urls)),
]
