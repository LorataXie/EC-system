"""
优惠券模块 - URL 路由配置 (urls)

定义优惠券相关的 API 端点路由。

使用 DRF 的 DefaultRouter 自动生成 RESTful 路由:
- Router 会根据 ViewSet 中的方法自动生成标准 URL 映射
- trailing_slash=False: URL 末尾不加斜杠，风格更简洁

生成的路由端点:

普通用户端 (CouponViewSet):
  GET /api/v1/coupons/my  — 查看我的优惠券 (支持 ?status= 筛选)

管理员端 (CouponAdminViewSet):
  GET    /api/v1/admin/coupons        — 优惠券列表
  POST   /api/v1/admin/coupons        — 创建单张优惠券
  GET    /api/v1/admin/coupons/{id}   — 优惠券详情
  PUT    /api/v1/admin/coupons/{id}   — 完整更新优惠券
  PATCH  /api/v1/admin/coupons/{id}   — 部分更新优惠券
  DELETE /api/v1/admin/coupons/{id}   — 删除优惠券
  POST   /api/v1/admin/coupons/issue  — 批量发放优惠券

为何使用两个 Router: 普通用户和管理员接口在逻辑上属于不同权限域，
分开注册使路由更清晰，也便于后续对两个 ViewSet 使用不同的中间件或限流策略。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, CouponAdminViewSet

# =========================================================================
# 普通用户路由
# trailing_slash=False: 生成的路由不带尾部斜杠，如 /coupons/my
# =========================================================================
router = DefaultRouter(trailing_slash=False)
router.register(r'coupons', CouponViewSet, basename='coupons')

# =========================================================================
# 管理员路由 (独立 Router，便于配置不同的中间件/限流)
# =========================================================================
admin_router = DefaultRouter(trailing_slash=False)
admin_router.register(r'admin/coupons', CouponAdminViewSet, basename='admin-coupons')

# =========================================================================
# 合并两个 Router 的 URL 到 urlpatterns
# =========================================================================
urlpatterns = [
    path('', include(router.urls)),
    path('', include(admin_router.urls)),
]
