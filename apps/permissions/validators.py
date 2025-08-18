# -*- coding: utf-8 -*-
"""
权限验证器和安全规则管理
提供权限验证、安全规则检查和一致性验证功能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.conf import settings

from .models import UserRole
from .audit import audit_service, AuditActionType, AuditResult, AuditRiskLevel

User = get_user_model()
logger = logging.getLogger(__name__)


class SecurityRuleType(models.TextChoices):
    """安全规则类型"""
    ACCESS_CONTROL = 'access_control', '访问控制'
    RATE_LIMIT = 'rate_limit', '频率限制'
    IP_WHITELIST = 'ip_whitelist', 'IP白名单'
    IP_BLACKLIST = 'ip_blacklist', 'IP黑名单'
    TIME_RESTRICTION = 'time_restriction', '时间限制'
    ROLE_RESTRICTION = 'role_restriction', '角色限制'
    PERMISSION_VALIDATION = 'permission_validation', '权限验证'
    CONCURRENT_SESSION = 'concurrent_session', '并发会话限制'
    GEOLOCATION = 'geolocation', '地理位置限制'
    DEVICE_RESTRICTION = 'device_restriction', '设备限制'


class SecurityRule(models.Model):
    """安全规则模型"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='规则名称'
    )
    rule_type = models.CharField(
        max_length=30,
        choices=SecurityRuleType.choices,
        verbose_name='规则类型'
    )
    description = models.TextField(
        verbose_name='规则描述'
    )
    
    # 规则配置
    config = models.JSONField(
        default=dict,
        verbose_name='规则配置',
        help_text='规则的具体配置参数'
    )
    
    # 应用范围
    target_roles = models.JSONField(
        default=list,
        verbose_name='目标角色',
        help_text='规则应用的角色列表'
    )
    target_resources = models.JSONField(
        default=list,
        verbose_name='目标资源',
        help_text='规则应用的资源列表'
    )
    target_actions = models.JSONField(
        default=list,
        verbose_name='目标操作',
        help_text='规则应用的操作列表'
    )
    
    # 状态和优先级
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    priority = models.IntegerField(
        default=0,
        verbose_name='优先级',
        help_text='数值越大优先级越高'
    )
    
    # 违规处理
    violation_action = models.CharField(
        max_length=20,
        choices=[
            ('deny', '拒绝访问'),
            ('warn', '警告'),
            ('log', '仅记录'),
            ('block', '阻止用户'),
        ],
        default='deny',
        verbose_name='违规处理'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建者'
    )
    
    class Meta:
        db_table = 'security_rule'
        verbose_name = '安全规则'
        verbose_name_plural = '安全规则'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['rule_type', 'is_active']),
            models.Index(fields=['priority', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
    
    def validate_rule(self, user, resource_type, action=None, **context) -> Tuple[bool, str, Dict]:
        """验证规则"""
        try:
            if not self.is_active:
                return True, "规则未启用", {}
            
            # 检查角色范围
            if self.target_roles and user.role not in self.target_roles:
                return True, "用户角色不在规则范围内", {}
            
            # 检查资源范围
            if self.target_resources and resource_type not in self.target_resources:
                return True, "资源类型不在规则范围内", {}
            
            # 检查操作范围
            if self.target_actions and action and action not in self.target_actions:
                return True, "操作不在规则范围内", {}
            
            # 根据规则类型执行验证
            validation_method = getattr(self, f'_validate_{self.rule_type}', None)
            if validation_method:
                return validation_method(user, resource_type, action, **context)
            else:
                logger.warning(f"未找到规则类型 {self.rule_type} 的验证方法")
                return True, "未实现的规则类型", {}
            
        except Exception as e:
            logger.error(f"规则验证失败: {self.name} - {str(e)}")
            return False, f"规则验证异常: {str(e)}", {'error': str(e)}
    
    def _validate_access_control(self, user, resource_type, action, **context):
        """验证访问控制"""
        config = self.config
        allowed_actions = config.get('allowed_actions', [])
        denied_actions = config.get('denied_actions', [])
        required_permissions = config.get('required_permissions', [])
        
        # 检查拒绝的操作
        if denied_actions and action in denied_actions:
            return False, f"操作 {action} 被明确禁止", {'denied_action': action}
        
        # 检查允许的操作
        if allowed_actions and action not in allowed_actions:
            return False, f"操作 {action} 不在允许列表中", {'action': action, 'allowed': allowed_actions}
        
        # 检查必需权限
        if required_permissions:
            user_permissions = set(user.get_all_permissions())
            missing_permissions = set(required_permissions) - user_permissions
            if missing_permissions:
                return False, f"缺少必需权限: {', '.join(missing_permissions)}", {
                    'missing_permissions': list(missing_permissions)
                }
        
        return True, "访问控制验证通过", {}
    
    def _validate_rate_limit(self, user, resource_type, action, **context):
        """验证频率限制"""
        config = self.config
        max_requests = config.get('max_requests', 100)
        time_window = config.get('time_window', 3600)  # 秒
        
        # 检查用户在时间窗口内的请求次数
        since_time = timezone.now() - timedelta(seconds=time_window)
        
        # 从审计日志中统计请求次数
        from .audit import PermissionAuditLog
        request_count = PermissionAuditLog.objects.filter(
            user=user,
            resource=resource_type,
            timestamp__gte=since_time
        ).count()
        
        if request_count >= max_requests:
            return False, f"超过频率限制: {request_count}/{max_requests} 在 {time_window} 秒内", {
                'current_count': request_count,
                'max_requests': max_requests,
                'time_window': time_window
            }
        
        return True, "频率限制验证通过", {
            'current_count': request_count,
            'max_requests': max_requests
        }
    
    def _validate_ip_whitelist(self, user, resource_type, action, **context):
        """验证IP白名单"""
        config = self.config
        whitelist = config.get('ip_addresses', [])
        
        ip_address = context.get('ip_address')
        if not ip_address:
            return False, "无法获取IP地址", {}
        
        if whitelist and ip_address not in whitelist:
            return False, f"IP地址 {ip_address} 不在白名单中", {
                'ip_address': ip_address,
                'whitelist': whitelist
            }
        
        return True, "IP白名单验证通过", {'ip_address': ip_address}
    
    def _validate_ip_blacklist(self, user, resource_type, action, **context):
        """验证IP黑名单"""
        config = self.config
        blacklist = config.get('ip_addresses', [])
        
        ip_address = context.get('ip_address')
        if not ip_address:
            return True, "无法获取IP地址，跳过黑名单检查", {}
        
        if blacklist and ip_address in blacklist:
            return False, f"IP地址 {ip_address} 在黑名单中", {
                'ip_address': ip_address,
                'blacklist': blacklist
            }
        
        return True, "IP黑名单验证通过", {'ip_address': ip_address}
    
    def _validate_time_restriction(self, user, resource_type, action, **context):
        """验证时间限制"""
        config = self.config
        allowed_hours = config.get('allowed_hours', [])
        allowed_days = config.get('allowed_days', [])
        timezone_name = config.get('timezone', 'UTC')
        
        now = timezone.now()
        current_hour = now.hour
        current_day = now.weekday()  # 0=Monday, 6=Sunday
        
        if allowed_hours and current_hour not in allowed_hours:
            return False, f"当前时间 {current_hour}:00 不在允许的时间范围内", {
                'current_hour': current_hour,
                'allowed_hours': allowed_hours
            }
        
        if allowed_days and current_day not in allowed_days:
            day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            return False, f"当前日期 {day_names[current_day]} 不在允许的日期范围内", {
                'current_day': current_day,
                'allowed_days': allowed_days
            }
        
        return True, "时间限制验证通过", {
            'current_hour': current_hour,
            'current_day': current_day
        }
    
    def _validate_role_restriction(self, user, resource_type, action, **context):
        """验证角色限制"""
        config = self.config
        min_role_level = config.get('min_role_level')
        max_role_level = config.get('max_role_level')
        excluded_roles = config.get('excluded_roles', [])
        required_roles = config.get('required_roles', [])
        
        # 定义角色级别映射
        role_levels = {
            UserRole.STUDENT: 1,
            UserRole.TEACHER: 2,
            UserRole.ADMIN: 3,
            UserRole.SUPER_ADMIN: 4
        }
        
        user_level = role_levels.get(user.role, 0)
        
        # 检查排除的角色
        if excluded_roles and user.role in excluded_roles:
            return False, f"角色 {user.role} 被明确排除", {
                'user_role': user.role,
                'excluded_roles': excluded_roles
            }
        
        # 检查必需的角色
        if required_roles and user.role not in required_roles:
            return False, f"角色 {user.role} 不在必需角色列表中", {
                'user_role': user.role,
                'required_roles': required_roles
            }
        
        # 检查最低角色级别
        if min_role_level and user_level < min_role_level:
            return False, f"用户角色级别 {user_level} 低于最低要求 {min_role_level}", {
                'user_level': user_level,
                'min_required': min_role_level
            }
        
        # 检查最高角色级别
        if max_role_level and user_level > max_role_level:
            return False, f"用户角色级别 {user_level} 高于最高限制 {max_role_level}", {
                'user_level': user_level,
                'max_allowed': max_role_level
            }
        
        return True, "角色限制验证通过", {'user_level': user_level}
    
    def _validate_permission_validation(self, user, resource_type, action, **context):
        """验证权限"""
        config = self.config
        required_permissions = config.get('required_permissions', [])
        forbidden_permissions = config.get('forbidden_permissions', [])
        
        if required_permissions or forbidden_permissions:
            user_permissions = set(user.get_all_permissions())
            
            # 检查必需权限
            if required_permissions:
                missing_permissions = set(required_permissions) - user_permissions
                if missing_permissions:
                    return False, f"缺少必需权限: {', '.join(missing_permissions)}", {
                        'missing_permissions': list(missing_permissions)
                    }
            
            # 检查禁止权限
            if forbidden_permissions:
                forbidden_found = set(forbidden_permissions) & user_permissions
                if forbidden_found:
                    return False, f"拥有禁止权限: {', '.join(forbidden_found)}", {
                        'forbidden_permissions': list(forbidden_found)
                    }
        
        return True, "权限验证通过", {}
    
    def _validate_concurrent_session(self, user, resource_type, action, **context):
        """验证并发会话限制"""
        config = self.config
        max_sessions = config.get('max_sessions', 1)
        
        # 这里需要实现会话计数逻辑
        # 暂时返回通过
        return True, "并发会话验证通过", {'max_sessions': max_sessions}


class PermissionValidator:
    """权限验证器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate_user_access(self, user, resource_type, action=None, request=None, **context) -> Tuple[bool, str, List[str], Dict]:
        """验证用户访问权限"""
        try:
            # 提取请求信息
            if request:
                context.update({
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'session_key': request.session.session_key if hasattr(request, 'session') else None
                })
            
            # 获取适用的安全规则
            rules = SecurityRule.objects.filter(
                is_active=True
            ).order_by('-priority')
            
            violations = []
            rule_results = {}
            
            # 逐一验证规则
            for rule in rules:
                is_valid, message, details = rule.validate_rule(
                    user, resource_type, action, **context
                )
                
                rule_results[rule.name] = {
                    'valid': is_valid,
                    'message': message,
                    'details': details
                }
                
                if not is_valid:
                    violations.append(f"{rule.name}: {message}")
                    
                    # 记录违规日志
                    audit_service.log_security_violation(
                        user=user,
                        violation_type=rule.rule_type,
                        severity=AuditRiskLevel.MEDIUM,
                        description=f"安全规则违规: {rule.name} - {message}",
                        details={
                            'rule_name': rule.name,
                            'rule_type': rule.rule_type,
                            'resource_type': resource_type,
                            'action': action,
                            'violation_details': details,
                            'context': context
                        },
                        request=request
                    )
                    
                    # 根据违规处理策略执行相应操作
                    if rule.violation_action == 'block':
                        # 这里可以实现用户阻止逻辑
                        self.logger.warning(f"用户 {user.username} 因违反规则 {rule.name} 应被阻止")
            
            # 如果有违规，拒绝访问
            if violations:
                audit_service.log_permission_check(
                    user=user,
                    resource=resource_type,
                    action=action or '',
                    has_permission=False,
                    request=request,
                    details={
                        'violations': violations,
                        'rule_results': rule_results
                    }
                )
                return False, "访问被拒绝", violations, rule_results
            
            # 记录成功访问日志
            audit_service.log_permission_check(
                user=user,
                resource=resource_type,
                action=action or '',
                has_permission=True,
                request=request,
                details={
                    'rule_results': rule_results
                }
            )
            
            return True, "访问允许", [], rule_results
            
        except Exception as e:
            self.logger.error(f"权限验证失败: {str(e)}")
            return False, f"验证异常: {str(e)}", [], {}
    
    def check_permission_consistency(self, user) -> Dict[str, Any]:
        """检查用户权限一致性"""
        try:
            report = {
                'user': user.username,
                'user_id': user.id,
                'role': user.role,
                'issues': [],
                'recommendations': [],
                'statistics': {},
                'timestamp': timezone.now().isoformat()
            }
            
            # 获取用户权限信息
            user_groups = user.groups.all()
            group_permissions = set()
            for group in user_groups:
                group_permissions.update(group.permissions.all())
            
            user_permissions = set(user.user_permissions.all())
            all_permissions = group_permissions | user_permissions
            
            # 统计信息
            report['statistics'] = {
                'total_groups': user_groups.count(),
                'group_permissions': len(group_permissions),
                'direct_permissions': len(user_permissions),
                'total_permissions': len(all_permissions)
            }
            
            # 获取角色应有的权限
            expected_permissions = self._get_expected_permissions_for_role(user.role)
            
            # 检查缺失的权限
            missing_permissions = expected_permissions - all_permissions
            if missing_permissions:
                report['issues'].append({
                    'type': 'missing_permissions',
                    'severity': 'medium',
                    'description': '缺少角色应有的权限',
                    'count': len(missing_permissions),
                    'details': [{
                        'codename': perm.codename,
                        'name': perm.name,
                        'content_type': str(perm.content_type)
                    } for perm in missing_permissions]
                })
            
            # 检查多余的权限
            extra_permissions = all_permissions - expected_permissions
            if extra_permissions:
                report['issues'].append({
                    'type': 'extra_permissions',
                    'severity': 'low',
                    'description': '拥有超出角色范围的权限',
                    'count': len(extra_permissions),
                    'details': [{
                        'codename': perm.codename,
                        'name': perm.name,
                        'content_type': str(perm.content_type)
                    } for perm in extra_permissions]
                })
            
            # 检查重复权限（同时通过组和直接分配获得）
            duplicate_permissions = group_permissions & user_permissions
            if duplicate_permissions:
                report['issues'].append({
                    'type': 'duplicate_permissions',
                    'severity': 'low',
                    'description': '通过组和直接分配重复获得的权限',
                    'count': len(duplicate_permissions),
                    'details': [{
                        'codename': perm.codename,
                        'name': perm.name,
                        'content_type': str(perm.content_type)
                    } for perm in duplicate_permissions]
                })
            
            # 检查空组
            empty_groups = [group for group in user_groups if group.permissions.count() == 0]
            if empty_groups:
                report['issues'].append({
                    'type': 'empty_groups',
                    'severity': 'low',
                    'description': '用户属于没有权限的组',
                    'count': len(empty_groups),
                    'details': [{'name': group.name, 'id': group.id} for group in empty_groups]
                })
            
            # 生成建议
            if missing_permissions:
                report['recommendations'].append(
                    f"建议为用户添加 {len(missing_permissions)} 个缺失权限"
                )
            
            if extra_permissions:
                report['recommendations'].append(
                    f"建议移除用户的 {len(extra_permissions)} 个多余权限"
                )
            
            if duplicate_permissions:
                report['recommendations'].append(
                    f"建议清理 {len(duplicate_permissions)} 个重复权限"
                )
            
            if empty_groups:
                report['recommendations'].append(
                    f"建议移除用户从 {len(empty_groups)} 个空组中的关联"
                )
            
            return report
            
        except Exception as e:
            self.logger.error(f"权限一致性检查失败: {str(e)}")
            return {
                'user': user.username,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_expected_permissions_for_role(self, role):
        """获取角色应有的权限"""
        try:
            # 尝试从角色组映射获取权限
            from .models import OptimizedRoleGroupMapping
            
            mapping = OptimizedRoleGroupMapping.objects.filter(role=role).first()
            if mapping and mapping.django_group:
                return set(mapping.django_group.permissions.all())
            
            # 如果没有映射，返回空集合
            return set()
            
        except Exception as e:
            self.logger.error(f"获取角色 {role} 的期望权限失败: {str(e)}")
            return set()
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def generate_security_report(self, days=30) -> Dict[str, Any]:
        """生成安全报告"""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # 获取审计日志
            from .audit import PermissionAuditLog
            logs = PermissionAuditLog.objects.filter(
                timestamp__range=[start_date, end_date]
            )
            
            report = {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_events': logs.count(),
                    'failed_events': logs.filter(result='failure').count(),
                    'denied_events': logs.filter(result='denied').count(),
                    'suspicious_events': logs.filter(is_suspicious=True).count(),
                    'unique_users': logs.values('user').distinct().count(),
                    'unique_resources': logs.values('resource').distinct().count()
                },
                'by_action': {},
                'by_risk_level': {},
                'by_user': {},
                'security_incidents': [],
                'recommendations': [],
                'rule_violations': []
            }
            
            # 按操作类型统计
            action_stats = logs.values('action_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            for stat in action_stats:
                report['by_action'][stat['action_type']] = stat['count']
            
            # 按风险等级统计
            risk_stats = logs.values('risk_level').annotate(
                count=Count('id')
            ).order_by('-count')
            
            for stat in risk_stats:
                report['by_risk_level'][stat['risk_level']] = stat['count']
            
            # 按用户统计（前10名）
            user_stats = logs.values('user__username').annotate(
                total=Count('id'),
                failed=Count('id', filter=Q(result='failure')),
                denied=Count('id', filter=Q(result='denied'))
            ).order_by('-total')[:10]
            
            for stat in user_stats:
                username = stat['user__username'] or '匿名用户'
                total = stat['total']
                failed = stat['failed']
                denied = stat['denied']
                success_rate = ((total - failed - denied) / total * 100) if total > 0 else 0
                
                report['by_user'][username] = {
                    'total': total,
                    'failed': failed,
                    'denied': denied,
                    'success_rate': round(success_rate, 2)
                }
            
            # 识别安全事件（高风险和严重风险）
            high_risk_events = logs.filter(
                risk_level__in=['high', 'critical']
            ).order_by('-timestamp')[:20]
            
            for event in high_risk_events:
                report['security_incidents'].append({
                    'timestamp': event.timestamp.isoformat(),
                    'user': event.user.username if event.user else '匿名用户',
                    'action_type': event.action_type,
                    'risk_level': event.risk_level,
                    'resource': event.resource,
                    'description': event.description,
                    'result': event.result
                })
            
            # 统计规则违规
            violation_logs = logs.filter(
                action_type=AuditActionType.SECURITY_VIOLATION
            ).order_by('-timestamp')[:10]
            
            for violation in violation_logs:
                report['rule_violations'].append({
                    'timestamp': violation.timestamp.isoformat(),
                    'user': violation.user.username if violation.user else '匿名用户',
                    'description': violation.description,
                    'details': violation.details
                })
            
            # 生成建议
            total_events = report['summary']['total_events']
            failed_events = report['summary']['failed_events']
            denied_events = report['summary']['denied_events']
            suspicious_events = report['summary']['suspicious_events']
            
            if total_events > 0:
                failure_rate = (failed_events + denied_events) / total_events * 100
                if failure_rate > 10:
                    report['recommendations'].append(
                        f"失败率过高 ({failure_rate:.1f}%)，建议检查权限配置和安全规则"
                    )
                
                suspicious_rate = suspicious_events / total_events * 100
                if suspicious_rate > 5:
                    report['recommendations'].append(
                        f"可疑活动比例较高 ({suspicious_rate:.1f}%)，建议加强监控"
                    )
            
            if len(report['security_incidents']) > 0:
                report['recommendations'].append(
                    f"发现 {len(report['security_incidents'])} 个高风险安全事件，需要立即关注"
                )
            
            if len(report['rule_violations']) > 0:
                report['recommendations'].append(
                    f"发现 {len(report['rule_violations'])} 个规则违规事件，建议审查安全规则配置"
                )
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成安全报告失败: {str(e)}")
            return {
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }


# 全局验证器实例
permission_validator = PermissionValidator()


def create_default_security_rules():
    """创建默认安全规则"""
    try:
        default_rules = [
            {
                'name': '管理员IP白名单',
                'rule_type': SecurityRuleType.IP_WHITELIST,
                'description': '限制管理员只能从特定IP访问',
                'config': {
                    'ip_addresses': ['127.0.0.1', '::1']  # 本地IP
                },
                'target_roles': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'priority': 100,
                'violation_action': 'deny'
            },
            {
                'name': '全局频率限制',
                'rule_type': SecurityRuleType.RATE_LIMIT,
                'description': '限制所有用户的访问频率',
                'config': {
                    'max_requests': 1000,
                    'time_window': 3600  # 1小时
                },
                'target_roles': [],
                'priority': 50,
                'violation_action': 'deny'
            },
            {
                'name': '学生工作时间限制',
                'rule_type': SecurityRuleType.TIME_RESTRICTION,
                'description': '限制学生的访问时间为工作时间',
                'config': {
                    'allowed_hours': list(range(8, 18)),  # 8:00-17:59
                    'allowed_days': list(range(0, 5)),    # 周一到周五
                    'timezone': 'Asia/Shanghai'
                },
                'target_roles': [UserRole.STUDENT],
                'priority': 30,
                'violation_action': 'warn'
            },
            {
                'name': '敏感操作权限验证',
                'rule_type': SecurityRuleType.PERMISSION_VALIDATION,
                'description': '对敏感操作进行严格的权限验证',
                'config': {
                    'required_permissions': ['auth.change_user', 'auth.delete_user']
                },
                'target_resources': ['user_management', 'role_management'],
                'target_actions': ['create', 'update', 'delete'],
                'priority': 80,
                'violation_action': 'deny'
            }
        ]
        
        created_count = 0
        for rule_data in default_rules:
            rule, created = SecurityRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            if created:
                created_count += 1
                logger.info(f"创建安全规则: {rule.name}")
            else:
                logger.info(f"安全规则已存在: {rule.name}")
        
        logger.info(f"默认安全规则设置完成，共创建 {created_count} 个新规则")
        
    except Exception as e:
        logger.error(f"创建默认安全规则失败: {str(e)}")


def setup_validation_system():
    """设置验证系统"""
    logger.info("开始设置权限验证系统...")
    
    try:
        # 创建默认安全规则
        create_default_security_rules()
        
        logger.info("权限验证系统设置完成")
        
    except Exception as e:
        logger.error(f"设置权限验证系统失败: {str(e)}")