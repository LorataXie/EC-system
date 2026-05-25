"""
Django 生产环境配置 (production settings)

继承 base.py 的所有配置，并覆盖为生产环境的安全设置。

生产环境特点:
- DEBUG=False: 不暴露错误详情，保护系统内部信息
- ALLOWED_HOSTS: 从环境变量读取，仅允许指定域名
- 强制 HTTPS: 启用 SSL 重定向和安全 Cookie
- CORS: 从环境变量读取允许的前端域名白名单
- 不启用 BrowsableAPIRenderer (仅 JSON 响应)

使用方式: python manage.py runserver --settings=config.settings.production
(生产环境建议使用 gunicorn + nginx，而非 runserver)
"""

from .base import *  # noqa: F403, F401  导入基础配置的所有内容


# ======================================================
# Django 安全配置
# ======================================================

# 生产环境必须关闭 DEBUG
# DEBUG=True 会泄露: 堆栈跟踪、局部变量、数据库查询、settings 配置等敏感信息
DEBUG = False

# ALLOWED_HOSTS: 从环境变量读取，用逗号分隔
# 示例: ALLOWED_HOSTS=example.com,www.example.com,api.example.com
# 为何必须设置: DEBUG=False 时，Django 强制要求 ALLOWED_HOSTS 非空，防止 Host 头攻击
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')


# ======================================================
# HTTPS / SSL 安全配置
# ======================================================

# 强制 SSL 重定向: 所有 HTTP 请求自动跳转到 HTTPS
# 为何需要: HTTPS 加密传输保护用户数据 (密码、支付信息)，防止中间人攻击
# 前提: 服务器必须配置 SSL 证书 (如 Let's Encrypt 免费证书)
SECURE_SSL_REDIRECT = True

# Session Cookie 仅通过 HTTPS 传输
# 防止 Cookie 在 HTTP 连接中被窃取 (网络嗅探)
SESSION_COOKIE_SECURE = True

# CSRF Cookie 仅通过 HTTPS 传输
# 防止 CSRF Token 在 HTTP 连接中被窃取
CSRF_COOKIE_SECURE = True


# ======================================================
# CORS 跨域配置 (生产)
# ======================================================

# 从环境变量读取前端的域名列表
# 示例: CORS_ORIGINS=https://example.com,https://www.example.com
# 为何不用 CORS_ALLOW_ALL_ORIGINS: 出于安全考虑，应限制只有自家的前端域名
# 才能发起跨域请求，防止其他网站恶意调用 API
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
