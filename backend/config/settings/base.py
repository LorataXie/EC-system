"""
Django 项目基础配置 (base settings)

所有环境 (开发/测试/生产) 共享的基础配置。
环境特定的覆盖配置在 development.py 和 production.py 中，通过 `from .base import *` 继承。

配置结构:
- 第一部分: Django 核心配置 (路径、密钥、应用、中间件)
- 第二部分: 数据库配置 (MySQL)
- 第三部分: 认证与密码策略
- 第四部分: 国际化与静态文件
- 第五部分: DRF 配置 (REST Framework、JWT、CORS、API 文档)
"""

import os
from pathlib import Path
from datetime import timedelta


# =============================================================================
# 第一部分: Django 核心配置
# =============================================================================

# ----- 项目路径 -----
# BASE_DIR: 项目根目录 (backend/)
# Path(__file__).resolve().parent.parent.parent 解释:
#   __file__              → config/settings/base.py
#   .parent               → config/settings/
#   .parent.parent        → config/
#   .parent.parent.parent → backend/  (项目根目录)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ----- 安全密钥 -----
# SECRET_KEY: Django 的加盐密钥，用于 session、CSRF token、密码重置等加密操作
# 从环境变量读取，开发环境使用 dev-secret-key-change-in-production 作为默认值
# 生产环境必须通过环境变量设置强密钥，否则会导致安全漏洞
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# ----- 调试模式 -----
# DEBUG: 生产环境必须为 False，开发环境在 development.py 中覆盖为 True
# DEBUG=True 时: 显示详细错误页面、启用 Django Debug Toolbar
# DEBUG=False 时: 显示通用错误页面、必须配置 ALLOWED_HOSTS
DEBUG = False

# ----- 允许的主机名 -----
# ALLOWED_HOSTS: 限制 Django 响应的 HTTP Host 头，防止 HTTP Host 头攻击
# 空列表表示仅允许 localhost/127.0.0.1
# 生产环境在 production.py 中通过环境变量覆盖
ALLOWED_HOSTS = []

# ----- 已安装的应用 -----
# INSTALLED_APPS 决定了 Django 启动时加载哪些应用
# 加载顺序: Django 内置 → 第三方库 → 本地应用
INSTALLED_APPS = [
    # ---- Django 内置应用 ----
    'django.contrib.admin',           # Django Admin 管理后台
    'django.contrib.auth',            # 用户认证系统
    'django.contrib.contenttypes',    # 内容类型框架 (GenericForeignKey 依赖)
    'django.contrib.sessions',        # Session 管理
    'django.contrib.messages',        # 消息框架 (flash messages)
    'django.contrib.staticfiles',     # 静态文件管理 (collectstatic)

    # ---- 第三方库 ----
    'rest_framework',                 # Django REST Framework: API 构建框架
    'rest_framework_simplejwt',       # Simple JWT: JWT 认证实现
    'rest_framework_simplejwt.token_blacklist',  # JWT 黑名单 (支持 token 吊销)
    'corsheaders',                    # django-cors-headers: 跨域请求支持
    'django_filters',                 # django-filter: 查询参数过滤
    'mptt',                           # django-mptt: 树形结构 (商品分类使用)
    'drf_spectacular',                # drf-spectacular: OpenAPI 3.0 自动文档生成

    # ---- 本地应用 ----
    'apps.core',                      # 核心模块 (基础模型、分页、异常处理等)
    'apps.accounts',                  # 用户账户模块 (注册、登录、个人信息)
    'apps.products',                  # 商品模块 (商品、分类、规格)
    'apps.cart',                      # 购物车模块
    'apps.orders',                    # 订单模块
    'apps.reviews',                   # 评价模块
    'apps.coupons',                   # 优惠券模块
]

# ----- 中间件 -----
# 中间件执行顺序: 请求从上到下，响应从下到上
# CorsMiddleware 必须放在最前面 (或其他靠前的位置)，
# 以便在响应中添加 CORS 头，并处理预检请求
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # CORS 跨域中间件 (必须靠前)
    'django.middleware.security.SecurityMiddleware',  # 安全中间件 (SSL重定向、XSS防护等)
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session 管理
    'django.middleware.common.CommonMiddleware',      # 通用中间件 (URL 规范化、禁止 DISALLOWED_USER_AGENTS)
    'django.middleware.csrf.CsrfViewMiddleware',      # CSRF 防护 (只对非 API 的 Django View 有效)
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 用户认证中间件 (设置 request.user)
    'django.contrib.messages.middleware.MessageMiddleware',     # 消息框架
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # 防止点击劫持攻击
]

# ----- URL 配置入口 -----
ROOT_URLCONF = 'config.urls'

# ----- 模板引擎配置 -----
# APP_DIRS=True: 自动在每个已安装应用的 templates/ 目录下查找模板
# DIRS=[]: 全局模板目录 (当前不需要)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',      # 模板中添加 debug 变量
                'django.template.context_processors.request',    # 模板中访问 request 对象
                'django.contrib.auth.context_processors.auth',   # 模板中访问 user 和 perms
                'django.contrib.messages.context_processors.messages',  # 模板中访问 messages
            ],
        },
    },
]

# ----- WSGI 应用入口 -----
WSGI_APPLICATION = 'config.wsgi.application'


# =============================================================================
# 第二部分: 数据库配置
# =============================================================================

# 默认使用 MySQL 数据库
# 为何选择 MySQL: 关系型电商数据 (订单、商品、用户) 适合使用关系型数据库，
# MySQL 在写入性能和事务支持方面表现良好，且生态成熟
#
# 所有数据库连接参数从环境变量读取，未设置时使用默认值:
# - DB_NAME:     数据库名 (默认 ecommerce)
# - DB_USER:     数据库用户名 (默认 root)
# - DB_PASSWORD: 数据库密码 (默认空，生产务必设置)
# - DB_HOST:     数据库主机地址 (默认 127.0.0.1)
# - DB_PORT:     数据库端口 (默认 3306)
#
# OPTIONS 中设置 charset=utf8mb4:
#   utf8mb4 是 MySQL 的真正 UTF-8 实现，支持 emoji 和生僻汉字 (4字节编码)
#   普通 utf8 在 MySQL 中只支持最多 3 字节，会导致 emoji 插入报错
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'ecommerce'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}


# =============================================================================
# 第三部分: 认证与密码策略
# =============================================================================

# ----- 自定义用户模型 -----
# 使用 accounts.User 替代 Django 默认的 auth.User
# 为何自定义: 默认 User 模型字段有限 (username, email, password)，
# 电商场景需要扩展字段 (手机号、头像、收货地址等)
# 注意: 此项必须在第一次 migrate 前设置，否则无法更改
AUTH_USER_MODEL = 'accounts.User'

# ----- 密码验证器 -----
# 注册新用户时的密码强度校验规则
AUTH_PASSWORD_VALIDATORS = [
    # 最小长度: 至少 8 个字符，防止弱密码
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    # 常见密码检查: 禁止使用 "password"、"12345678" 等常见弱密码
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # 纯数字密码检查: 禁止使用纯数字密码 (如 "12345678")
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# 第四部分: 国际化与静态文件
# =============================================================================

# ----- 语言与时区 -----
# LANGUAGE_CODE='zh-hans': 简体中文 (Django Admin 和错误信息显示中文)
LANGUAGE_CODE = 'zh-hans'
# TIME_ZONE='Asia/Shanghai': 上海时区 (UTC+8)，与中国用户时区一致
TIME_ZONE = 'Asia/Shanghai'
# USE_I18N=True: 启用国际化，支持多语言翻译
USE_I18N = True
# USE_TZ=True: 启用时区支持，数据库中存储 UTC 时间，展示时转换为本地时区
# 为何启用: 避免跨时区用户的时间混乱，所有时间存储统一为 UTC
USE_TZ = True

# ----- 静态文件 (CSS/JS/图片) -----
# STATIC_URL='static/': 静态文件的 URL 前缀
STATIC_URL = 'static/'
# STATIC_ROOT: collectstatic 命令收集静态文件的目标目录
STATIC_ROOT = BASE_DIR / 'static'

# ----- 用户上传文件 (Media) -----
# MEDIA_URL='media/': 用户上传文件的 URL 前缀
MEDIA_URL = 'media/'
# MEDIA_ROOT: 用户上传文件的物理存储目录
# 如商品图片存储在 MEDIA_ROOT/products/，评价图片存储在 MEDIA_ROOT/reviews/
MEDIA_ROOT = BASE_DIR / 'media'

# ----- 默认主键类型 -----
# BigAutoField: 64位自增整数，最大约 9.22 × 10^18
# 比默认的 AutoField (32位，约 21亿) 容量大得多，适合电商场景的高并发数据增长
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# 第五部分: Django REST Framework 配置
# =============================================================================

REST_FRAMEWORK = {
    # ----- 认证类 -----
    # 默认使用 JWT 认证 (Simple JWT)
    # 为何选择 JWT: 无状态、适合前后端分离架构、适合移动端、不需要服务端 session 存储
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    # ----- 权限类 -----
    # 默认允许所有请求 (不要求认证)
    # 为何用 AllowAny 而非 IsAuthenticated: 电商系统有大量公开接口 (商品浏览、首页)，
    # 应该默认开放，在需要认证的 ViewSet 中单独配置 IsAuthenticated
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),

    # ----- 分页配置 -----
    # 使用项目自定义的分页类，标准化分页响应格式
    # PAGE_SIZE=20: 每页默认 20 条记录，平衡前端展示和数据传输量
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardPageNumberPagination',
    'PAGE_SIZE': 20,

    # ----- 过滤后端 -----
    # 配置三合一过滤后端:
    # 1. DjangoFilterBackend: 精确字段过滤 (?category=1, ?status=active)
    # 2. SearchFilter:        全文搜索 (?search=关键词)
    # 3. OrderingFilter:      排序字段 (?ordering=-price, ?ordering=created_at)
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),

    # ----- 渲染器 -----
    # 使用项目自定义的 JSON 渲染器，统一所有 API 响应的 JSON 格式
    # 如统一包装为 { "code": 200, "message": "success", "data": {...} }
    'DEFAULT_RENDERER_CLASSES': (
        'apps.core.renderers.CustomJSONRenderer',
    ),

    # ----- 异常处理 -----
    # 自定义异常处理器: 统一将 DRF 和 Django 异常转换为标准 JSON 格式
    # 如将 ValidationError 转为 { "code": 400, "message": "...", "errors": {...} }
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',

    # ----- API 文档 Schema -----
    # 使用 drf-spectacular 自动生成 OpenAPI 3.0 Schema
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# =============================================================================
# 第六部分: Simple JWT 配置
# =============================================================================

SIMPLE_JWT = {
    # Access Token 有效期: 30 分钟
    # 为何较短: Access Token 用于每次 API 请求的认证，短期有效减少泄露风险
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),

    # Refresh Token 有效期: 7 天
    # 为何较长: Refresh Token 用于获取新的 Access Token，较长有效期提升用户体验
    # 用户 7 天内无需重新登录，但 Access Token 泄露后 30 分钟即失效
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    # 刷新时轮换 Refresh Token: 每次使用 Refresh Token 获取新的 Access Token 时，
    # 同时生成一个新的 Refresh Token，旧的 Refresh Token 失效
    # 为何开启: 防止 Refresh Token 被截获后长期滥用
    'ROTATE_REFRESH_TOKENS': True,

    # 轮换后将旧 Refresh Token 加入黑名单
    # 需要启用 token_blacklist 应用 (已在 INSTALLED_APPS 中添加)
    # 为何开启: 确保旧的 Refresh Token 即使被截获也无法使用
    'BLACKLIST_AFTER_ROTATION': True,

    # 更新最后登录时间: 每次获取新 Token 时更新用户的 last_login 字段
    'UPDATE_LAST_LOGIN': True,

    # 认证头类型: Authorization: Bearer <token>
    # Bearer 是 OAuth 2.0 标准的前缀
    'AUTH_HEADER_TYPES': ('Bearer',),

    # Token 类: 使用标准的 AccessToken 实现
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}


# =============================================================================
# 第七部分: CORS 跨域配置
# =============================================================================

# 允许携带 Cookie (跨域请求携带认证信息)
CORS_ALLOW_CREDENTIALS = True

# 允许的前端源 (开发环境)
# 为何限制: 防止其他域名的恶意网站通过 AJAX 请求窃取用户数据
# localhost:5173 和 127.0.0.1:5173 都是 Vite 开发服务器的默认地址
# 生产环境在 production.py 中通过环境变量覆盖
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]


# =============================================================================
# 第八部分: drf-spectacular (API 文档) 配置
# =============================================================================

SPECTACULAR_SETTINGS = {
    # API 文档标题
    'TITLE': 'E-Commerce API',
    # API 文档描述
    'DESCRIPTION': 'E-Commerce System REST API',
    # API 版本号
    'VERSION': '1.0.0',
    # 不在 Schema 端点中包含自身 (避免文档递归)
    'SERVE_INCLUDE_SCHEMA': False,
}
