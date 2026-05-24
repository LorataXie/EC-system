from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductAdminViewSet, CategoryAdminViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')

admin_router = DefaultRouter(trailing_slash=False)
admin_router.register(r'admin/products', ProductAdminViewSet, basename='admin-products')
admin_router.register(r'admin/categories', CategoryAdminViewSet, basename='admin-categories')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(admin_router.urls)),
]
