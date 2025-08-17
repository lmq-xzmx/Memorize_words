"""
ASGI config for english_learning_platform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_learning_platform.settings")

# 初始化Django ASGI应用
django_asgi_app = get_asgi_application()

# 在Django应用初始化后导入WebSocket相关模块
from channels.routing import ProtocolTypeRouter, URLRouter
from apps.permissions.routing import websocket_urlpatterns
from apps.permissions.middleware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
