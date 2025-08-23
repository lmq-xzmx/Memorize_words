# -*- coding: utf-8 -*-
"""
权限审计日志系统
提供完整的权限操作审计和追踪机制
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


class AuditActionType(models.TextChoices):
    """审计操作类型"""
    PERMISSION_GRANT = 'permission_grant', '权限授予'
    PERMISSION_REVOKE = 'permission_revoke', '权限撤销'
    ROLE_ASSIGN = 'role_assign', '角色分配'
    ROLE_REMOVE = 'role_remove', '角色移除'
    ROLE_CREATE = 'role_create', '角色创建'
    ROLE_UPDATE = 'role_update', '角色更新'
    ROLE_DELETE = 'role_delete', '角色删除'
    MENU_ACCESS_GRANT = 'menu_access_grant', '菜单访问授权'
    MENU_ACCESS_REVOKE = 'menu_access_revoke', '菜单访问撤销'
    PERMISSION_CHECK = 'permission_check', '权限检查'
    LOGIN_SUCCESS = 'login_success', '登录成功'
    LOGIN_FAILURE = 'login_failure', '登录失败'
    LOGOUT = 'logout', '登出'
    PASSWORD_CHANGE = 'password_change', '密码修改'
    ACCOUNT_LOCK = 'account_lock', '账户锁定'
    ACCOUNT_UNLOCK = 'account_unlock', '账户解锁'
    SECURITY_VIOLATION = 'security_violation', '安全违规'
    BATCH_OPERATION = 'batch_operation', '批量操作'
    SYSTEM_CONFIG = 'system_config', '系统配置'
    DATA_EXPORT = 'data_export', '数据导出'
    DATA_IMPORT = 'data_import', '数据导入'


class AuditResult(models.TextChoices):
    """审计结果"""
    SUCCESS = 'success', '成功'
    FAILURE = 'failure', '失败'
    DENIED = 'denied', '拒绝'
    ERROR = 'error', '错误'


# 移除复杂的风险等级分析，简化为基础日志记录


class PermissionAuditLog(models.Model):
    """权限审计日志模型"""
    
    # 基本信息
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='时间戳')
    action_type = models.CharField(
        max_length=50, 
        choices=AuditActionType.choices,
        db_index=True,
        verbose_name='操作类型'
    )
    result = models.CharField(
        max_length=20,
        choices=AuditResult.choices,
        default=AuditResult.SUCCESS,
        db_index=True,
        verbose_name='操作结果'
    )
    
    # 用户信息
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        verbose_name='操作用户'
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs_as_target',
        verbose_name='目标用户'
    )
    
    # 操作详情
    resource = models.CharField(max_length=200, blank=True, db_index=True, verbose_name='资源')
    action = models.CharField(max_length=100, blank=True, verbose_name='动作')
    permission = models.CharField(max_length=200, blank=True, db_index=True, verbose_name='权限')
    role = models.CharField(max_length=100, blank=True, verbose_name='角色')
    
    # 通用外键，用于关联任何模型
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 详细信息
    description = models.TextField(blank=True, verbose_name='描述')
    details = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        verbose_name='详细信息'
    )
    
    # 环境信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    session_key = models.CharField(max_length=40, blank=True, verbose_name='会话密钥')
    request_id = models.CharField(max_length=100, blank=True, db_index=True, verbose_name='请求ID')
    
    # 简化状态信息，仅保留基础审查功能
    is_reviewed = models.BooleanField(default=False, db_index=True, verbose_name='已审查')
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_audit_logs',
        verbose_name='审查人'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='审查时间')
    
    class Meta:
        db_table = 'permission_audit_log'
        verbose_name = '权限审计日志'
        verbose_name_plural = '权限审计日志'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'action_type']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['target_user', 'timestamp']),
            models.Index(fields=['resource', 'action']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.get_action_type_display()} - {self.user}"
    
    def mark_as_reviewed(self, reviewer):
        """标记为已审查"""
        self.is_reviewed = True
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save(update_fields=['is_reviewed', 'reviewed_by', 'reviewed_at'])


class AuditLogService:
    """审计日志服务"""
    
    def __init__(self):
        pass
    
    def log_permission_action(self, 
                            action_type: str,
                            user: Optional[User] = None,
                            target_user: Optional[User] = None,
                            resource: str = '',
                            action: str = '',
                            permission: str = '',
                            role: str = '',
                            result: str = AuditResult.SUCCESS,
                            description: str = '',
                            details: Optional[Dict] = None,
                            request=None,
                            content_object=None) -> PermissionAuditLog:
        """记录权限操作日志"""
        
        try:
            # 准备基本数据
            log_data = {
                'action_type': action_type,
                'user': user,
                'target_user': target_user,
                'resource': resource,
                'action': action,
                'permission': permission,
                'role': role,
                'result': result,
                'description': description,
                'details': details or {},
            }
            
            # 添加内容对象
            if content_object:
                log_data['content_object'] = content_object
            
            # 从请求中提取环境信息
            if request:
                log_data.update(self._extract_request_info(request))
            
            # 创建审计日志
            audit_log = PermissionAuditLog.objects.create(**log_data)
            
            logger.info(f"权限审计日志已创建: {audit_log.id}")
            return audit_log
            
        except Exception as e:
            logger.error(f"创建审计日志失败: {e}")
            # 即使审计失败，也不应该影响主要业务逻辑
            return None
    
    def log_permission_check(self, 
                           user: User,
                           resource: str,
                           action: str,
                           has_permission: bool,
                           request=None,
                           details: Optional[Dict] = None) -> PermissionAuditLog:
        """记录权限检查日志"""
        
        result = AuditResult.SUCCESS if has_permission else AuditResult.DENIED
        description = f"权限检查: {resource}.{action} - {'允许' if has_permission else '拒绝'}"
        
        check_details = {
            'has_permission': has_permission,
            'check_timestamp': timezone.now().isoformat(),
            **(details or {})
        }
        
        return self.log_permission_action(
            action_type=AuditActionType.PERMISSION_CHECK,
            user=user,
            resource=resource,
            action=action,
            result=result,
            description=description,
            details=check_details,
            request=request
        )
    
    def log_role_change(self,
                       user: User,
                       target_user: User,
                       old_role: str,
                       new_role: str,
                       action_type: str = AuditActionType.ROLE_ASSIGN,
                       request=None) -> PermissionAuditLog:
        """记录角色变更日志"""
        
        description = f"角色变更: {old_role} -> {new_role}"
        details = {
            'old_role': old_role,
            'new_role': new_role,
            'change_timestamp': timezone.now().isoformat()
        }
        
        return self.log_permission_action(
            action_type=action_type,
            user=user,
            target_user=target_user,
            role=new_role,
            description=description,
            details=details,
            request=request
        )
    
    def log_batch_operation(self,
                          user: User,
                          operation_type: str,
                          affected_users: List[int],
                          operation_details: Dict,
                          request=None) -> PermissionAuditLog:
        """记录批量操作日志"""
        
        description = f"批量操作: {operation_type}, 影响用户数: {len(affected_users)}"
        details = {
            'operation_type': operation_type,
            'affected_users': affected_users,
            'affected_count': len(affected_users),
            'operation_details': operation_details,
            'batch_timestamp': timezone.now().isoformat()
        }
        
        return self.log_permission_action(
            action_type=AuditActionType.BATCH_OPERATION,
            user=user,
            description=description,
            details=details,
            request=request
        )
    
    def log_security_violation(self,
                             user: Optional[User],
                             violation_type: str,
                             description: str,
                             details: Optional[Dict] = None,
                             request=None) -> PermissionAuditLog:
        """记录安全违规日志 - 简化版本"""
        
        violation_details = {
            'violation_type': violation_type,
            'detection_timestamp': timezone.now().isoformat(),
            **(details or {})
        }
        
        audit_log = self.log_permission_action(
            action_type=AuditActionType.SECURITY_VIOLATION,
            user=user,
            result=AuditResult.FAILURE,
            description=description,
            details=violation_details,
            request=request
        )
        
        return audit_log
    
    def _extract_request_info(self, request) -> Dict:
        """从请求中提取环境信息"""
        info = {}
        
        if hasattr(request, 'META'):
            info['ip_address'] = self._get_client_ip(request)
            info['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        if hasattr(request, 'session'):
            info['session_key'] = request.session.session_key or ''
        
        # 添加请求ID（如果存在）
        if hasattr(request, 'id'):
            info['request_id'] = str(request.id)
        elif hasattr(request, 'META') and 'HTTP_X_REQUEST_ID' in request.META:
            info['request_id'] = request.META['HTTP_X_REQUEST_ID']
        
        return info
    
    def _get_client_ip(self, request) -> str:
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    # 移除复杂的风险评估和可疑活动检测功能
    

    

    

    
    def get_audit_statistics(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           user: Optional[User] = None) -> Dict:
        """获取基础审计统计信息"""
        
        queryset = PermissionAuditLog.objects.all()
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        if user:
            queryset = queryset.filter(user=user)
        
        # 基础统计
        total_count = queryset.count()
        success_count = queryset.filter(result=AuditResult.SUCCESS).count()
        failure_count = queryset.filter(result=AuditResult.FAILURE).count()
        
        return {
            'total_count': total_count,
            'success_count': success_count,
            'failure_count': failure_count,
            'success_rate': (success_count / total_count * 100) if total_count > 0 else 0
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """清理旧的审计日志"""
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # 只删除已审查的日志
        deleted_count, _ = PermissionAuditLog.objects.filter(
            timestamp__lt=cutoff_date,
            is_reviewed=True
        ).delete()
        
        logger.info(f"清理了 {deleted_count} 条旧的审计日志")
        return deleted_count


# 全局审计服务实例
audit_service = AuditLogService()


# 装饰器：自动记录权限操作
def audit_permission_action(action_type: str, 
                          description: str = ''):
    """权限操作审计装饰器 - 简化版本"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = None
            user = None
            
            # 尝试从参数中提取request和user
            for arg in args:
                if hasattr(arg, 'user') and hasattr(arg, 'META'):
                    request = arg
                    user = getattr(arg, 'user', None)
                    break
                elif hasattr(arg, 'is_authenticated'):
                    user = arg
                    break
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 记录成功操作
                audit_service.log_permission_action(
                    action_type=action_type,
                    user=user,
                    result=AuditResult.SUCCESS,
                    description=description or f"{func.__name__} 执行成功",
                    details={'function': func.__name__},
                    request=request
                )
                
                return result
                
            except Exception as e:
                # 记录失败操作
                audit_service.log_permission_action(
                    action_type=action_type,
                    user=user,
                    result=AuditResult.ERROR,
                    description=f"{description or func.__name__} 执行失败: {str(e)}",
                    details={
                        'function': func.__name__, 
                        'error': str(e)
                    },
                    request=request
                )
                raise
        
        return wrapper
    return decorator