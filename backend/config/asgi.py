import os
from django.core.asgi import get_asgi_application
# 设置默认的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_asgi_application()
