from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, CouponAdminViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'coupons', CouponViewSet, basename='coupons')

admin_router = DefaultRouter(trailing_slash=False)
admin_router.register(r'admin/coupons', CouponAdminViewSet, basename='admin-coupons')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(admin_router.urls)),
]
