from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewAdminViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'reviews', ReviewViewSet, basename='reviews')

admin_router = DefaultRouter(trailing_slash=False)
admin_router.register(r'admin/reviews', ReviewAdminViewSet, basename='admin-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(admin_router.urls)),
]
