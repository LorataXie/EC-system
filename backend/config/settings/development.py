from .base import *


#=========开发环境配置文件============


DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES['default'].update({
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'ecommerce',
    'USER': 'root',
    'PASSWORD': '123456',          # 改成你的 MySQL 密码
    'HOST': '127.0.0.1',
    'PORT': '3306',
})

USE_TZ = False

CORS_ALLOW_ALL_ORIGINS = True

# QQ 邮箱 SMTP 配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '1073954509@qq.com'        # ← 改成你的 QQ 邮箱
EMAIL_HOST_PASSWORD = 'rwzeoenfpnxpigcj'    # ← 改成授权码（不是 QQ 密码）
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 缓存（存验证码，开发用本地内存，生产换 Redis）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'apps.core.renderers.CustomJSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)
