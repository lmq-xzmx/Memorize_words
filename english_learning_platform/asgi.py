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

# 简化的ASGI配置 - 暂时禁用WebSocket以避免复杂依赖问题
try:
    # 尝试导入WebSocket相关模块
    from channels.routing import ProtocolTypeRouter, URLRouter
    from apps.permissions.routing import websocket_urlpatterns
    from apps.permissions.middleware import TokenAuthMiddlewareStack
    import logging

    logger = logging.getLogger(__name__)

    # 使用简化的WebSocket配置
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": TokenAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    })
    
    logger.info("WebSocket支持已启用")
    
except ImportError as e:
    # 如果WebSocket依赖不可用，使用纯HTTP配置
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"WebSocket依赖不可用，使用纯HTTP配置: {e}")
    
    application = django_asgi_app
