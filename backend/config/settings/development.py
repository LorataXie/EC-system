"""
Django 开发环境配置 (development settings)

继承 base.py 的所有配置，并覆盖/扩展为开发友好的设置。

开发环境特点:
- DEBUG=True: 启用详细错误页面，方便调试
- 数据库: MySQL (与生产一致，避免环境差异导致的问题)
- 时区: USE_TZ=False (简化本地开发的时间处理)
- 邮件: QQ 邮箱 SMTP (开发中发送真实验证码邮件)
- 缓存: 本地内存缓存 (无需安装 Redis)
- CORS: 允许所有源 (开发环境安全要求较低)
- DRF Browsable API: 启用浏览器可浏览的 API 界面

使用方式: python manage.py runserver --settings=config.settings.development
"""

from .base import *  # noqa: F403, F401  导入基础配置的所有内容
# 注意: flake8 会报 F403 (import *) 和 F401 (unused import)，
# 这是 Django settings 的标准模式，通过 # noqa 抑制警告


# ======================================================
# Django 核心覆盖
# ======================================================

# DEBUG 模式: 开启后 Django 会显示详细的错误页面 (含堆栈跟踪和局部变量)
# 同时启用静态文件开发服务 (django.contrib.staticfiles)
DEBUG = True

# 允许所有主机访问 (开发环境无需限制)
# 为何用 ['*']: 开发时可能从不同 IP 或域名访问 (局域网其他设备、ngrok 等)
ALLOWED_HOSTS = ['*']


# ======================================================
# 数据库配置 (MySQL)
# ======================================================

# 覆盖 base.py 中的数据库配置，使用开发环境的 MySQL 连接参数
# 包括密码等敏感信息 (开发环境独享数据库，密码泄露风险较低)
DATABASES['default'].update({
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'ecommerce',
    'USER': 'root',
    'PASSWORD': '123456',          # 改成你的 MySQL 密码
    'HOST': '127.0.0.1',
    'PORT': '3306',
})


# ======================================================
# 时区设置
# ======================================================

# 关闭时区支持 (开发环境简化时间处理)
# USE_TZ=False 时: 数据库存储本地时间 (Asia/Shanghai)，不需要 UTC 换算
# 为何开发环境关闭: 减少开发时反复确认 UTC 转换的麻烦，直接看到北京时间
# 生产环境 base.py 中 USE_TZ=True，所有时间以 UTC 存储
USE_TZ = False


# ======================================================
# CORS 跨域配置
# ======================================================

# 开发环境允许所有源 (安全要求低，方便开发调试)
# 生产环境 production.py 中使用 CORS_ALLOWED_ORIGINS 白名单限制
CORS_ALLOW_ALL_ORIGINS = True


# ======================================================
# 邮件配置 (QQ 邮箱 SMTP)
# ======================================================

# QQ 邮箱 SMTP 服务器配置
# 用于发送邮箱验证码等邮件通知
# 开发环境使用真实的 QQ 邮箱 (而非 console backend)，以验证邮件发送功能
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'                     # QQ 邮箱 SMTP 服务器地址
EMAIL_PORT = 587                               # TLS 加密端口 (非 SSL 的 465)
EMAIL_USE_TLS = True                           # 启用 TLS 传输加密
EMAIL_HOST_USER = '1073954509@qq.com'          # ← 改成你的 QQ 邮箱
EMAIL_HOST_PASSWORD = 'rwzeoenfpnxpigcj'       # ← 改成授权码（不是 QQ 密码）
# 说明: QQ 邮箱要求使用"授权码"而非登录密码，在 QQ 邮箱设置 → 账户 → POP3/SMTP 服务中生成
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ======================================================
# 缓存配置 (本地内存)
# ======================================================

# 开发环境使用本地内存缓存 (LocMemCache)
# 优点:
# 1. 无需安装额外服务 (Redis/Memcached)
# 2. 进程重启后缓存自动清空，避免开发时缓存污染
# 3. 线程安全
# 缺点: 每个进程独立缓存，不支持分布式，不适合生产
#
# 用途: 存储邮箱验证码等临时数据
#
# 生产环境应替换为 Redis:
#   BACKEND: 'django.core.cache.backends.redis.RedisCache'
#   LOCATION: 'redis://127.0.0.1:6379/1'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# ======================================================
# DRF 渲染器扩展
# ======================================================

# 开发环境额外启用 BrowsableAPIRenderer (浏览器可浏览的 API)
# CustomJSONRenderer 在前: 确保 JSON 格式优先 (Accept: application/json)
# BrowsableAPIRenderer 在后: 浏览器访问时显示可交互的 API 界面
# 生产环境不包含 BrowsableAPIRenderer，仅提供 JSON 响应
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'apps.core.renderers.CustomJSONRenderer',          # 自定义 JSON 格式
    'rest_framework.renderers.BrowsableAPIRenderer',   # 浏览器可浏览 API (仅开发)
)
