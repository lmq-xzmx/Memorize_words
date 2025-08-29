# -*- coding: utf-8 -*-
"""
权限WebSocket服务
实现权限变更的实时推送服务，支持用户权限、角色变更和菜单访问权限的实时通知
"""

import json
import logging
import asyncio
from typing import Dict, Set, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

from .models import (
    RoleManagement, 
    # RoleMenuPermission,  # 已废弃，使用 MenuValidity 和 RoleMenuAssignment 替代
    MenuModuleConfig
)
from .models_optimized import PermissionSyncLog
from .utils import get_user_permissions, get_user_role

User = get_user_model()
logger = logging.getLogger(__name__)


class PermissionWebSocketConsumer(AsyncWebsocketConsumer):
    """
    权限WebSocket消费者
    处理权限相关的实时通信
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.user_groups = set()
        self.room_groups = set()
        self.last_heartbeat = None
        self.connection_time = None
        
    async def connect(self):
        """处理WebSocket连接"""
        try:
            logger.info("开始建立WebSocket连接")
            
            # 接受连接
            logger.info("准备接受WebSocket连接")
            await self.accept()
            logger.info("WebSocket连接已接受")
            
            # 首先尝试从URL参数中获取用户ID
            url_user_id = self.scope['url_route']['kwargs'].get('user_id')
            if url_user_id:
                self.user_id = int(url_user_id)
                logger.info(f"WebSocket从URL参数获取用户ID: {self.user_id}")
            else:
                # 如果URL中没有用户ID，则从scope中获取用户信息（由middleware设置）
                user = self.scope.get('user')
                if user and hasattr(user, 'id') and user.id:
                    self.user_id = user.id
                    logger.info(f"WebSocket认证用户连接: {user.username} (ID: {user.id})")
                else:
                    self.user_id = 0  # 匿名用户ID设为0
                    logger.info("WebSocket匿名连接已允许")
            
            # 设置用户组
            logger.info("即将调用setup_user_groups")
            await self.setup_user_groups()
            logger.info("setup_user_groups调用完成")
            
            # 加入房间组
            logger.info("即将调用join_room_groups")
            await self.join_room_groups()
            logger.info("join_room_groups调用完成")
            
            # 不立即发送连接确认消息，等待前端发送连接消息后再确认
            logger.info("等待前端发送连接消息进行握手确认")
            
            logger.info("WebSocket连接建立完成")
            
            # 记录连接到管理器
            headers = dict(self.scope.get('headers', []))
            user_agent = headers.get(b'user-agent', b'').decode('utf-8')
            client_ip = self.scope.get('client', ['unknown', None])[0]
            
            connection_manager.add_connection(
                self.channel_name, 
                self.user_id, 
                {
                    'connected_at': datetime.now(),
                    'user_agent': user_agent,
                    'client_ip': client_ip
                }
            )
            
            # 记录连接日志
            await self.log_connection('connected')
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {str(e)}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            await self.close()
    
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        try:
            logger.info(f"WebSocket断开连接开始处理，用户: {self.user_id}, 代码: {close_code}")
            
            # 分析断开代码
            close_code_meanings = {
                1000: "正常关闭",
                1001: "端点离开",
                1002: "协议错误", 
                1003: "不支持的数据类型",
                1006: "异常关闭（无关闭帧）",
                1007: "无效的帧载荷数据",
                1008: "策略违规",
                1009: "消息过大",
                1010: "缺少扩展",
                1011: "内部错误",
                1015: "TLS握手失败"
            }
            
            close_reason = close_code_meanings.get(close_code, f"未知代码: {close_code}")
            logger.info(f"断开原因: {close_reason}")
            
            # 离开所有房间组
            await self.leave_room_groups()
            
            # 从连接管理器中移除连接
            connection_manager.remove_connection(self.channel_name)
            
            # 记录断开连接日志
            await self.log_connection('disconnected', close_code)
            
            logger.info(f"用户 {self.user_id} WebSocket连接已断开，代码: {close_code} ({close_reason})")
            
        except Exception as e:
            logger.error(f"WebSocket断开连接处理失败: {e}")
            import traceback
            logger.error(f"断开处理错误堆栈: {traceback.format_exc()}")
    
    async def receive(self, text_data):
        """接收客户端消息"""
        try:
            logger.info(f"[RECEIVE] 收到WebSocket消息: {text_data}")
            logger.info(f"[RECEIVE] 当前连接状态 - 用户ID: {self.user_id}, Channel: {self.channel_name}")
            
            # 解析JSON数据
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}, 原始数据: {text_data}")
                await self.send_error('INVALID_JSON', 'Invalid JSON format')
                return
            
            message_type = data.get('type')
            logger.info(f"消息类型: {message_type}, 数据: {data}")
            
            # 更新心跳时间
            self.last_heartbeat = datetime.now()
            
            # 处理不同类型的消息
            if message_type == 'connect':
                await self.handle_connect_message(data)
            elif message_type == 'heartbeat' or message_type == 'ping':
                await self.handle_heartbeat(data)
            elif message_type == 'permission_check':
                await self.handle_permission_check(data)
            elif message_type == 'subscribe_notifications':
                await self.handle_subscribe_notifications(data)
            elif message_type == 'unsubscribe_notifications':
                await self.handle_unsubscribe_notifications(data)
            else:
                logger.warning(f"未知消息类型: {message_type}")
                await self.send_error('UNKNOWN_MESSAGE_TYPE', f'Unknown message type: {message_type}')
                
        except Exception as e:
            logger.error(f"处理WebSocket消息时发生错误: {e}")
            await self.send_error('INTERNAL_ERROR', 'Internal server error')
    
    async def handle_connect_message(self, data):
        """处理前端连接消息并发送确认"""
        logger.info(f"收到前端连接消息: {data}")
        logger.info(f"WebSocket连接状态: readyState={getattr(self, '_websocket_ready', 'unknown')}")
        
        try:
            # 收到前端连接消息后，发送连接确认消息
            await self.send_connection_confirmation()
            logger.info(f"用户 {self.user_id} 的连接握手完成，确认消息已发送")
        except Exception as e:
            logger.error(f"发送连接确认消息失败: {e}")
            raise
    
    async def handle_heartbeat(self, data):
        """处理心跳消息"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'heartbeat_response',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'server_time': datetime.now().timestamp()
            }))
            logger.info(f"心跳响应已发送给用户 {self.user_id}")
        except Exception as e:
            logger.error(f"发送心跳响应失败: {e}")
    
    async def handle_permission_check(self, data):
        """处理权限检查请求"""
        try:
            resource = data.get('resource')
            action = data.get('action')
            request_id = data.get('request_id')
            
            if not resource or not action:
                await self.send_error('missing_parameters', '缺少resource或action参数')
                return
            
            # 检查用户权限
            has_permission = await self.check_user_permission(resource, action)
            
            await self.send(text_data=json.dumps({
                'type': 'permission_check_response',
                'request_id': request_id,
                'resource': resource,
                'action': action,
                'has_permission': has_permission,
                'timestamp': datetime.now().isoformat()
            }))
            
        except Exception as e:
            logger.error(f"权限检查失败: {e}")
            await self.send_error('permission_check_error', str(e))
    
    async def handle_subscribe_notifications(self, data):
        """处理订阅通知请求"""
        notification_types = data.get('types', [])
        
        # 加入通知组
        for notification_type in notification_types:
            group_name = f"notification_{notification_type}_{self.user_id}"
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.room_groups.add(group_name)
        
        await self.send(text_data=json.dumps({
            'type': 'subscription_confirmed',
            'subscribed_types': notification_types,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def handle_unsubscribe_notifications(self, data):
        """处理取消订阅通知请求"""
        notification_types = data.get('types', [])
        
        # 离开通知组
        for notification_type in notification_types:
            group_name = f"notification_{notification_type}_{self.user_id}"
            await self.channel_layer.group_discard(group_name, self.channel_name)
            self.room_groups.discard(group_name)
        
        await self.send(text_data=json.dumps({
            'type': 'unsubscription_confirmed',
            'unsubscribed_types': notification_types,
            'timestamp': datetime.now().isoformat()
        }))
    
    # 权限变更通知处理方法
    async def permission_changed(self, event):
        """处理权限变更通知"""
        await self.send(text_data=json.dumps({
            'type': 'permission_changed',
            'data': event['data'],
            'timestamp': event.get('timestamp', datetime.now().isoformat())
        }))
    
    async def role_updated(self, event):
        """处理角色更新通知"""
        await self.send(text_data=json.dumps({
            'type': 'role_updated',
            'data': event['data'],
            'timestamp': event.get('timestamp', datetime.now().isoformat())
        }))
    
    async def menu_access_changed(self, event):
        """处理菜单访问权限变更通知"""
        await self.send(text_data=json.dumps({
            'type': 'menu_access_changed',
            'data': event['data'],
            'timestamp': event.get('timestamp', datetime.now().isoformat())
        }))
    
    async def system_notification(self, event):
        """处理系统通知"""
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'data': event['data'],
            'timestamp': event.get('timestamp', datetime.now().isoformat())
        }))
    
    async def cache_invalidation(self, event):
        """处理缓存失效通知"""
        await self.send(text_data=json.dumps({
            'type': 'cache_invalidation',
            'data': event['data'],
            'timestamp': event.get('timestamp', datetime.now().isoformat())
        }))
    
    # 辅助方法
    async def setup_user_groups(self):
        """设置用户组信息"""
        try:
            logger.info(f"开始设置用户组，用户ID: {self.user_id}")
            user = await self.get_user()
            logger.info(f"获取到用户对象: {user}")
            
            if user and user.is_authenticated:
                logger.info(f"认证用户: {user.username}")
                # 获取用户角色（返回字符串类型的角色代码）
                user_role = await self.get_user_role_async(user)
                logger.info(f"用户角色: {user_role}")
                if user_role:
                    role_group = f"role_{user_role}"
                    self.user_groups.add(role_group)
                    logger.info(f"添加角色组: {role_group}")
                
                # 获取用户所属的Django组
                user_groups = await self.get_user_django_groups(user)
                logger.info(f"Django组列表: {user_groups}")
                for group in user_groups:
                    group_name = f"group_{group.id}"
                    self.user_groups.add(group_name)
                    logger.info(f"添加Django组: {group_name}")
            else:
                logger.info("匿名用户，添加匿名组")
                # 匿名用户加入匿名组
                self.user_groups.add("anonymous_users")
            
            logger.info(f"用户组设置完成，总共 {len(self.user_groups)} 个组: {self.user_groups}")
                    
        except Exception as e:
            logger.error(f"设置用户组失败: {e}", exc_info=True)
    
    async def join_room_groups(self):
        """加入房间组"""
        try:
            logger.info(f"开始加入房间组，用户ID: {self.user_id}")
            
            # 加入用户专属组（仅认证用户）
            if self.user_id:
                user_group = f"user_{self.user_id}"
                logger.info(f"加入用户专属组: {user_group}")
                await self.channel_layer.group_add(user_group, self.channel_name)
                self.room_groups.add(user_group)
                logger.info(f"成功加入用户专属组: {user_group}")
            
            # 加入角色和组相关的房间
            logger.info(f"用户组列表: {self.user_groups}")
            for group in self.user_groups:
                logger.info(f"加入角色/组房间: {group}")
                await self.channel_layer.group_add(group, self.channel_name)
                self.room_groups.add(group)
                logger.info(f"成功加入角色/组房间: {group}")
            
            # 加入全局通知组
            global_group = "global_notifications"
            logger.info(f"加入全局通知组: {global_group}")
            await self.channel_layer.group_add(global_group, self.channel_name)
            self.room_groups.add(global_group)
            logger.info(f"成功加入全局通知组: {global_group}")
            
            logger.info(f"房间组加入完成，总共加入 {len(self.room_groups)} 个组")
            
        except Exception as e:
            logger.error(f"加入房间组失败: {e}", exc_info=True)
    
    async def leave_room_groups(self):
        """离开房间组"""
        try:
            for group in self.room_groups:
                await self.channel_layer.group_discard(group, self.channel_name)
            self.room_groups.clear()
            
        except Exception as e:
            logger.error(f"离开房间组失败: {e}")
    
    async def send_connection_confirmation(self):
        """发送连接确认消息"""
        try:
            confirmation_message = {
                'type': 'connection_confirmed',
                'data': {
                    'user_id': self.user_id,
                    'groups': list(self.room_groups),
                    'server_time': datetime.now().isoformat(),
                    'sessionId': self.channel_name,
                    'features': {
                        'heartbeat': True,
                        'notifications': True,
                        'permission_check': True
                    }
                },
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            
            logger.info(f"准备发送连接确认消息: {confirmation_message}")
            await self.send(text_data=json.dumps(confirmation_message))
            logger.info(f"连接确认消息发送成功，用户: {self.user_id}")
        except Exception as e:
            logger.error(f"发送连接确认消息失败: {e}")
            # 不要抛出异常，避免导致连接断开
    
    async def send_error(self, error_code, message):
        """发送错误消息"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error_code': error_code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }))
    
    @database_sync_to_async
    def get_user(self):
        """获取当前用户"""
        return self.scope.get('user')
    
    @database_sync_to_async
    def check_anonymous_permission(self):
        """检查匿名用户权限"""
        # 可以根据需要配置匿名用户是否允许连接
        return getattr(settings, 'WEBSOCKET_ALLOW_ANONYMOUS', True)
    
    @database_sync_to_async
    def get_user_role_async(self, user):
        """异步获取用户角色"""
        return get_user_role(user)
    
    @database_sync_to_async
    def get_user_django_groups(self, user):
        """获取用户Django组"""
        return list(user.groups.all())
    
    @database_sync_to_async
    def check_user_permission(self, resource, action):
        """检查用户权限"""
        try:
            user = User.objects.get(id=self.user_id)
            permissions = get_user_permissions(user)
            
            # 简化的权限检查逻辑
            permission_key = f"{resource}.{action}"
            return permission_key in permissions or user.is_superuser
            
        except Exception as e:
            logger.error(f"权限检查失败: {e}")
            return False
    
    @database_sync_to_async
    def log_connection(self, action, close_code=None):
        """记录连接日志"""
        try:
            log_data = {
                'user_id': self.user_id,
                'action': action,
                'timestamp': datetime.now(),
                'client_info': self.scope.get('client', ['unknown', 0])[0]
            }
            
            if close_code:
                log_data['close_code'] = close_code
            
            # 这里可以保存到数据库或日志文件
            logger.info(f"WebSocket连接日志: {log_data}")
            
        except Exception as e:
            logger.error(f"记录连接日志失败: {e}")


class PermissionNotificationService:
    """
    权限通知服务
    负责发送各种权限相关的通知
    """
    
    def __init__(self):
        self.channel_layer = None
        self._setup_channel_layer()
    
    def _setup_channel_layer(self):
        """设置Channel Layer"""
        try:
            from channels.layers import get_channel_layer
            self.channel_layer = get_channel_layer()
        except Exception as e:
            logger.error(f"设置Channel Layer失败: {e}")
    
    async def notify_permission_change(self, user_id: int, permissions: List[str], 
                                     action: str, resource: str, **kwargs):
        """通知权限变更"""
        if not self.channel_layer:
            return
        
        try:
            notification_data = {
                'userId': user_id,
                'permissions': permissions,
                'action': action,
                'resource': resource,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            # 发送给特定用户
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    'type': 'permission_changed',
                    'data': notification_data,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"权限变更通知已发送给用户 {user_id}: {action} {resource}")
            
        except Exception as e:
            logger.error(f"发送权限变更通知失败: {e}")
    
    async def notify_role_update(self, user_id: int, old_role: str, new_role: str, 
                               permissions: List[str], **kwargs):
        """通知角色更新"""
        if not self.channel_layer:
            return
        
        try:
            notification_data = {
                'userId': user_id,
                'oldRole': old_role,
                'newRole': new_role,
                'permissions': permissions,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    'type': 'role_updated',
                    'data': notification_data,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"角色更新通知已发送给用户 {user_id}: {old_role} -> {new_role}")
            
        except Exception as e:
            logger.error(f"发送角色更新通知失败: {e}")
    
    async def notify_menu_access_change(self, user_id: int, menu_changes: Dict, **kwargs):
        """通知菜单访问权限变更"""
        if not self.channel_layer:
            return
        
        try:
            notification_data = {
                'userId': user_id,
                'menuChanges': menu_changes,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    'type': 'menu_access_changed',
                    'data': notification_data,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"菜单访问变更通知已发送给用户 {user_id}")
            
        except Exception as e:
            logger.error(f"发送菜单访问变更通知失败: {e}")
    
    async def notify_batch_permission_update(self, user_ids: List[int], 
                                           update_summary: Dict, **kwargs):
        """通知批量权限更新"""
        if not self.channel_layer:
            return
        
        try:
            notification_data = {
                'updateSummary': update_summary,
                'affectedUsers': len(user_ids),
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            # 发送给所有受影响的用户
            for user_id in user_ids:
                await self.channel_layer.group_send(
                    f"user_{user_id}",
                    {
                        'type': 'system_notification',
                        'data': {
                            **notification_data,
                            'userId': user_id,
                            'type': 'batch_permission_update'
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            logger.info(f"批量权限更新通知已发送给 {len(user_ids)} 个用户")
            
        except Exception as e:
            logger.error(f"发送批量权限更新通知失败: {e}")
    
    async def notify_system_maintenance(self, message: str, priority: str = 'medium', 
                                      target_users: Optional[List[int]] = None, **kwargs):
        """通知系统维护"""
        if not self.channel_layer:
            return
        
        try:
            notification_data = {
                'type': 'maintenance',
                'message': message,
                'priority': priority,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            if target_users:
                # 发送给特定用户
                for user_id in target_users:
                    await self.channel_layer.group_send(
                        f"user_{user_id}",
                        {
                            'type': 'system_notification',
                            'data': notification_data,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
            else:
                # 发送给所有在线用户
                await self.channel_layer.group_send(
                    "global_notifications",
                    {
                        'type': 'system_notification',
                        'data': notification_data,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            logger.info(f"系统维护通知已发送: {message}")
            
        except Exception as e:
            logger.error(f"发送系统维护通知失败: {e}")
    
    async def invalidate_cache(self, user_id: int, cache_keys: List[str], **kwargs):
        """通知缓存失效"""
        if not self.channel_layer:
            return
        
        try:
            notification_data = {
                'userId': user_id,
                'cacheKeys': cache_keys,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    'type': 'cache_invalidation',
                    'data': notification_data,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"缓存失效通知已发送给用户 {user_id}: {cache_keys}")
            
        except Exception as e:
            logger.error(f"发送缓存失效通知失败: {e}")


class WebSocketConnectionManager:
    """
    WebSocket连接管理器
    管理活跃连接、连接统计和健康检查
    """
    
    def __init__(self):
        self.active_connections: Dict[str, Dict] = {}
        self.user_connections: Dict[int, Set[str]] = defaultdict(set)
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'disconnections': 0
        }
    
    def add_connection(self, channel_name: str, user_id: int, connection_info: Dict):
        """添加连接"""
        self.active_connections[channel_name] = {
            'user_id': user_id,
            'connected_at': datetime.now(),
            'last_activity': datetime.now(),
            **connection_info
        }
        
        self.user_connections[user_id].add(channel_name)
        self.connection_stats['total_connections'] += 1
        self.connection_stats['active_connections'] += 1
        
        logger.info(f"新增WebSocket连接: {channel_name}, 用户: {user_id}")
    
    def remove_connection(self, channel_name: str):
        """移除连接"""
        if channel_name in self.active_connections:
            connection_info = self.active_connections[channel_name]
            user_id = connection_info['user_id']
            
            del self.active_connections[channel_name]
            self.user_connections[user_id].discard(channel_name)
            
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
            
            self.connection_stats['active_connections'] -= 1
            self.connection_stats['disconnections'] += 1
            
            logger.info(f"移除WebSocket连接: {channel_name}, 用户: {user_id}")
    
    def update_activity(self, channel_name: str):
        """更新连接活动时间"""
        if channel_name in self.active_connections:
            self.active_connections[channel_name]['last_activity'] = datetime.now()
    
    def get_user_connections(self, user_id: int) -> List[str]:
        """获取用户的所有连接"""
        return list(self.user_connections.get(user_id, set()))
    
    def get_connection_stats(self) -> Dict:
        """获取连接统计"""
        return {
            **self.connection_stats,
            'current_active': len(self.active_connections),
            'unique_users': len(self.user_connections)
        }
    
    def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """清理不活跃的连接"""
        timeout_threshold = datetime.now() - timedelta(minutes=timeout_minutes)
        inactive_connections = []
        
        for channel_name, connection_info in self.active_connections.items():
            if connection_info['last_activity'] < timeout_threshold:
                inactive_connections.append(channel_name)
        
        for channel_name in inactive_connections:
            self.remove_connection(channel_name)
            logger.info(f"清理不活跃连接: {channel_name}")
        
        return len(inactive_connections)


# 全局实例
notification_service = PermissionNotificationService()
connection_manager = WebSocketConnectionManager()


# 定期清理任务
async def cleanup_inactive_connections():
    """定期清理不活跃的连接"""
    while True:
        try:
            cleaned_count = connection_manager.cleanup_inactive_connections()
            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 个不活跃的WebSocket连接")
        except Exception as e:
            logger.error(f"清理不活跃连接失败: {e}")
        
        # 每5分钟执行一次
        await asyncio.sleep(300)


# 启动清理任务
if hasattr(settings, 'WEBSOCKET_CLEANUP_ENABLED') and settings.WEBSOCKET_CLEANUP_ENABLED:
    asyncio.create_task(cleanup_inactive_connections())