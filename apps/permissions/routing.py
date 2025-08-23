# -*- coding: utf-8 -*-
"""
WebSocket路由配置
定义权限相关的WebSocket路由
"""

from django.urls import path
from . import websocket_service
import logging

logger = logging.getLogger(__name__)

logger.info("加载WebSocket路由配置")

websocket_urlpatterns = [
    path('ws/permissions/', websocket_service.PermissionWebSocketConsumer.as_asgi()),
    path('ws/permissions/anonymous/', websocket_service.PermissionWebSocketConsumer.as_asgi()),
]

# 调试信息：打印路由配置
for i, pattern in enumerate(websocket_urlpatterns, 1):
    logger.info(f"路由 {i}: {pattern.pattern} -> {pattern.callback}")

logger.info(f"WebSocket路由模式已配置: {len(websocket_urlpatterns)} 个路由")