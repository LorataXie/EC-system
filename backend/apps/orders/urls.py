from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderAdminViewSet, dashboard_view, sales_trend_view, hot_products_view, recent_orders_view

router = DefaultRouter(trailing_slash=False)
router.register(r'orders', OrderViewSet, basename='orders')

admin_router = DefaultRouter(trailing_slash=False)
admin_router.register(r'admin/orders', OrderAdminViewSet, basename='admin-orders')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(admin_router.urls)),
    path('admin/analytics/overview', dashboard_view, name='admin-analytics-overview'),
    path('admin/analytics/sales-trend', sales_trend_view, name='admin-analytics-trend'),
    path('admin/analytics/hot-products', hot_products_view, name='admin-analytics-hot'),
    path('admin/analytics/recent-orders', recent_orders_view, name='admin-analytics-orders'),
]
