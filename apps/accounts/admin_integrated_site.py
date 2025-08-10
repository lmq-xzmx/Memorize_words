# -*- coding: utf-8 -*-
"""
整合管理中心站点配置

实现高内聚、低耦合的管理界面架构：
- 用户与角色管理中心
- 权限与菜单管理中心
- 数据统计与监控中心
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta

# 导入模型
from apps.accounts.models import (
    CustomUser, RoleApproval, RoleExtension, 
    RoleUserGroup, UserExtensionData
)
from apps.permissions.models import (
    MenuModuleConfig, RoleMenuPermission, RoleGroupMapping,
    RoleManagement, PermissionSyncLog
)

# 导入整合的管理类
from .admin_integrated import (
    IntegratedUserAdmin, IntegratedRoleExtensionAdmin
)
from .admin_integrated_permissions import (
    IntegratedRoleManagementAdmin, IntegratedMenuConfigAdmin
)


class IntegratedAdminSite(AdminSite):
    """整合管理站点
    
    提供统一的管理界面入口，实现：
    - 业务模块化管理
    - 数据统计仪表板
    - 快速操作入口
    - 系统状态监控
    """
    
    site_header = '系统管理中心'
    site_title = '管理中心'
    index_title = '欢迎使用系统管理中心'
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('user-stats/', self.admin_view(self.user_stats_view), name='user_stats'),
            path('permission-stats/', self.admin_view(self.permission_stats_view), name='permission_stats'),
            path('system-health/', self.admin_view(self.system_health_view), name='system_health'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """自定义首页"""
        extra_context = extra_context or {}
        
        # 获取统计数据
        stats = self.get_dashboard_stats()
        extra_context.update({
            'dashboard_stats': stats,
            'quick_actions': self.get_quick_actions(),
            'recent_activities': self.get_recent_activities(),
        })
        
        return super().index(request, extra_context)
    
    def get_dashboard_stats(self):
        """获取仪表板统计数据"""
        try:
            return {
                'user_stats': {
                    'total_users': CustomUser.objects.count(),
                    'active_users': CustomUser.objects.filter(is_active=True).count(),
                    'pending_approvals': RoleApproval.objects.filter(status='pending').count(),
                    'extension_data': UserExtensionData.objects.count(),
                },
                'role_stats': {
                    'total_roles': RoleManagement.objects.count(),
                    'active_roles': RoleManagement.objects.filter(is_active=True).count(),
                    'role_extensions': RoleExtension.objects.count(),
                    'role_groups': RoleUserGroup.objects.count(),
                },
                'permission_stats': {
                    'menu_modules': MenuModuleConfig.objects.count(),
                    'active_menus': MenuModuleConfig.objects.filter(is_active=True).count(),
                    'role_permissions': RoleMenuPermission.objects.count(),
                    'group_mappings': RoleGroupMapping.objects.count(),
                },
                'sync_stats': {
                    'total_syncs': PermissionSyncLog.objects.count(),
                    'successful_syncs': PermissionSyncLog.objects.filter(success=True).count(),
                    'failed_syncs': PermissionSyncLog.objects.filter(success=False).count(),
                    'recent_syncs': PermissionSyncLog.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=7)
                    ).count(),
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_quick_actions(self):
        """获取快速操作链接"""
        return [
            {
                'title': '用户管理',
                'description': '管理用户账户、角色分配、扩展数据',
                'url': reverse('admin:accounts_customuser_changelist'),
                'icon': '👥',
                'color': '#28a745'
            },
            {
                'title': '角色权限',
                'description': '配置角色权限、菜单访问控制',
                'url': reverse('admin:permissions_rolemanagement_changelist'),
                'icon': '🔐',
                'color': '#007bff'
            },
            {
                'title': '菜单配置',
                'description': '管理前台菜单模块、访问权限',
                'url': reverse('admin:permissions_menumoduleconfig_changelist'),
                'icon': '📋',
                'color': '#17a2b8'
            },
            {
                'title': '角色增项',
                'description': '配置角色扩展功能、用户增项数据',
                'url': reverse('admin:accounts_roleextension_changelist'),
                'icon': '⚙️',
                'color': '#ffc107'
            },
            {
                'title': '同步日志',
                'description': '查看权限同步记录、系统操作日志',
                'url': reverse('admin:permissions_permissionsynclog_changelist'),
                'icon': '📊',
                'color': '#6c757d'
            },
            {
                'title': '系统健康',
                'description': '监控系统状态、性能指标',
                'url': reverse('admin:system_health'),
                'icon': '💚',
                'color': '#20c997'
            },
        ]
    
    def get_recent_activities(self):
        """获取最近活动"""
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            recent_logs = PermissionSyncLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).order_by('-created_at')[:10]
            
            activities = []
            for log in recent_logs:
                activities.append({
                    'time': log.created_at,
                    'action': log.action,
                    'target': f'{log.target_type}({log.target_id})',
                    'result': log.result[:50] + '...' if len(log.result) > 50 else log.result,
                    'success': log.success,
                })
            
            return activities
        except Exception:
            return []
    
    @method_decorator(staff_member_required)
    def dashboard_view(self, request):
        """仪表板视图"""
        context = {
            'title': '系统仪表板',
            'stats': self.get_dashboard_stats(),
            'quick_actions': self.get_quick_actions(),
            'recent_activities': self.get_recent_activities(),
        }
        return render(request, 'admin/integrated/dashboard.html', context)
    
    @method_decorator(staff_member_required)
    def user_stats_view(self, request):
        """用户统计视图"""
        from django.db.models import Count
        
        # 按角色统计用户
        role_stats = CustomUser.objects.values('role').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按状态统计用户
        status_stats = {
            'active': CustomUser.objects.filter(is_active=True).count(),
            'inactive': CustomUser.objects.filter(is_active=False).count(),
            'staff': CustomUser.objects.filter(is_staff=True).count(),
            'superuser': CustomUser.objects.filter(is_superuser=True).count(),
        }
        
        context = {
            'title': '用户统计',
            'role_stats': role_stats,
            'status_stats': status_stats,
        }
        return render(request, 'admin/integrated/user_stats.html', context)
    
    @method_decorator(staff_member_required)
    def permission_stats_view(self, request):
        """权限统计视图"""
        # 菜单权限统计
        menu_stats = RoleMenuPermission.objects.values('role').annotate(
            menu_count=Count('menu_module')
        ).order_by('-menu_count')
        
        # 角色层级统计
        hierarchy_stats = RoleManagement.objects.values('parent').annotate(
            child_count=Count('id')
        ).order_by('-child_count')
        
        context = {
            'title': '权限统计',
            'menu_stats': menu_stats,
            'hierarchy_stats': hierarchy_stats,
        }
        return render(request, 'admin/integrated/permission_stats.html', context)
    
    @method_decorator(staff_member_required)
    def system_health_view(self, request):
        """系统健康检查视图"""
        from django.utils import timezone
        from datetime import timedelta
        
        health_checks = {
            'database': self.check_database_health(),
            'permissions': self.check_permission_health(),
            'sync_status': self.check_sync_health(),
            'user_data': self.check_user_data_health(),
        }
        
        context = {
            'title': '系统健康检查',
            'health_checks': health_checks,
            'overall_status': all(check['status'] == 'healthy' for check in health_checks.values()),
        }
        return render(request, 'admin/integrated/system_health.html', context)
    
    def check_database_health(self):
        """检查数据库健康状态"""
        try:
            # 简单的数据库连接测试
            CustomUser.objects.count()
            return {
                'status': 'healthy',
                'message': '数据库连接正常',
                'details': '所有表可正常访问'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': '数据库连接异常',
                'details': str(e)
            }
    
    def check_permission_health(self):
        """检查权限配置健康状态"""
        try:
            # 检查是否有孤立的权限配置
            orphaned_perms = RoleMenuPermission.objects.filter(
                menu_module__isnull=True
            ).count()
            
            if orphaned_perms > 0:
                return {
                    'status': 'warning',
                    'message': f'发现 {orphaned_perms} 个孤立权限配置',
                    'details': '建议清理无效的权限配置'
                }
            
            return {
                'status': 'healthy',
                'message': '权限配置正常',
                'details': '所有权限配置有效'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': '权限检查失败',
                'details': str(e)
            }
    
    def check_sync_health(self):
        """检查同步状态健康"""
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            recent_failures = PermissionSyncLog.objects.filter(
                success=False,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            if recent_failures > 5:
                return {
                    'status': 'error',
                    'message': f'24小时内有 {recent_failures} 次同步失败',
                    'details': '建议检查同步配置'
                }
            elif recent_failures > 0:
                return {
                    'status': 'warning',
                    'message': f'24小时内有 {recent_failures} 次同步失败',
                    'details': '请关注同步状态'
                }
            
            return {
                'status': 'healthy',
                'message': '同步状态正常',
                'details': '最近无同步失败记录'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': '同步状态检查失败',
                'details': str(e)
            }
    
    def check_user_data_health(self):
        """检查用户数据健康状态"""
        try:
            # 检查用户数据完整性
            users_without_role = CustomUser.objects.filter(
                Q(role__isnull=True) | Q(role='')
            ).count()
            
            if users_without_role > 0:
                return {
                    'status': 'warning',
                    'message': f'发现 {users_without_role} 个用户未分配角色',
                    'details': '建议为所有用户分配适当角色'
                }
            
            return {
                'status': 'healthy',
                'message': '用户数据完整',
                'details': '所有用户都已分配角色'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': '用户数据检查失败',
                'details': str(e)
            }


# 创建整合管理站点实例
integrated_admin_site = IntegratedAdminSite(name='integrated_admin')

# 注册整合的管理类
integrated_admin_site.register(CustomUser, IntegratedUserAdmin)
integrated_admin_site.register(RoleExtension, IntegratedRoleExtensionAdmin)
integrated_admin_site.register(RoleManagement, IntegratedRoleManagementAdmin)
integrated_admin_site.register(MenuModuleConfig, IntegratedMenuConfigAdmin)

# 注册其他相关模型（使用默认管理类）
integrated_admin_site.register(RoleApproval)
integrated_admin_site.register(RoleUserGroup)
integrated_admin_site.register(UserExtensionData)
integrated_admin_site.register(RoleMenuPermission)
integrated_admin_site.register(RoleGroupMapping)
integrated_admin_site.register(PermissionSyncLog)