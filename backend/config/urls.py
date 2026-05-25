"""
Django 项目根 URL 配置 (root URLConf)

定义所有 API 路由的入口。

URL 结构:
- /admin/                     Django Admin 管理后台
- /api/v1/accounts/           用户账户 API (注册、登录、个人信息)
- /api/v1/products/           商品 API (商品、分类、规格)
- /api/v1/cart/               购物车 API
- /api/v1/orders/             订单 API
- /api/v1/reviews/            评价 API
- /api/v1/coupons/            优惠券 API
- /api/v1/schema/             OpenAPI 3.0 Schema (JSON 格式)
- /api/v1/docs/               Swagger UI (交互式 API 文档)
- /api/v1/redoc/              ReDoc (美观的 API 文档)

为何统一使用 /api/v1/ 前缀:
1. 版本管理: 未来 API 升级为 v2 时，可同时运行 /api/v1/ 和 /api/v2/
   避免升级 API 时破坏旧版客户端
2. 清晰分离: 将 API 与 Django Admin (/admin/) 和未来可能的 SSR 页面路由区分开
3. 反向代理友好: Nginx 可根据 /api/ 前缀统一做限流、缓存、日志等处理

开发环境下，当 DEBUG=True 时，额外提供 media 文件的直接访问路由。
"""

from django.conf import settings
from django.conf.urls.static import static  # 静态文件服务 (仅开发环境)
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,       # 生成 OpenAPI Schema JSON
    SpectacularSwaggerView,   # Swagger UI 界面
    SpectacularRedocView,     # ReDoc 界面
)


# =============================================================================
# URL 路由表
# =============================================================================
urlpatterns = [
    # ---- Django Admin 后台 ----
    # 路径: /admin/
    # Django 内置的管理后台，用于数据管理和运维操作
    path('admin/', admin.site.urls),

    # ---- 用户账户模块 ----
    # 包含: 注册、登录 (JWT Token 获取/刷新)、个人信息、密码修改等
    path('api/v1/', include('apps.accounts.urls')),

    # ---- 商品模块 ----
    # 包含: 商品 CRUD、分类树、规格管理等
    path('api/v1/', include('apps.products.urls')),

    # ---- 购物车模块 ----
    # 包含: 购物车商品添加/修改/删除、数量变更等
    path('api/v1/', include('apps.cart.urls')),

    # ---- 订单模块 ----
    # 包含: 订单创建/支付/取消、订单状态流转等
    path('api/v1/', include('apps.orders.urls')),

    # ---- 评价模块 ----
    # 包含: 商品评价的创建/查看/编辑/删除、管理员评价管理
    path('api/v1/', include('apps.reviews.urls')),

    # ---- 优惠券模块 ----
    # 包含: 用户优惠券查看、管理员优惠券管理/批量发放
    path('api/v1/', include('apps.coupons.urls')),

    # ---- API 文档 (drf-spectacular) ----
    # Schema: 原始 OpenAPI 3.0 JSON，供前端代码生成工具使用
    # 路径: /api/v1/schema/
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI: 交互式 API 文档，支持在线测试 API
    # url_name='schema' 告诉 Swagger 从哪个 URL 获取 Schema JSON
    # 路径: /api/v1/docs/
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc: 美观的只读 API 文档，适合对外发布
    # 路径: /api/v1/redoc/
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


# =============================================================================
# 开发环境: 提供用户上传文件 (Media) 的静态服务
#
# Django 在生产环境不负责静态文件的服务 (由 Nginx/Apache 负责)，
# 但在开发环境下使用 static() 辅助函数挂载 media 路由。
# DEBUG=True 时生效，生产环境 (DEBUG=False) 时此路由不会被添加。
# =============================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
