# -*- coding: utf-8 -*-
"""
WebSocket路由配置
定义权限相关的WebSocket路由
"""

from django.urls import re_path
from . import websocket_service

websocket_urlpatterns = [
    re_path(r'^ws/permissions/$', websocket_service.PermissionWebSocketConsumer.as_asgi()),
    re_path(r'^ws/permissions/(?P<user_id>\d+)/$', websocket_service.PermissionWebSocketConsumer.as_asgi()),
    re_path(r'^ws/permissions/anonymous/?$', websocket_service.PermissionWebSocketConsumer.as_asgi()),
]