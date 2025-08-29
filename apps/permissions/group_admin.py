from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from typing import Optional, Any

from .models import RoleGroupMapping, GroupRoleIdentifier
from .services.group_consistency_checker import GroupConsistencyChecker


class EnhancedGroupAdmin(GroupAdmin):
    """增强的Django组管理界面
    
    为Django组添加角色关联状态和标识显示功能
    """
    
    list_display = [
        'name', 
        'get_role_status', 
        'get_role_identifier', 
        'get_sync_status',
        'get_user_count',
        'get_permission_count',
        'get_actions'
    ]
    
    list_filter = [
        'grouproleidentifier__status',
        'grouproleidentifier__sync_status',
        'rolegroupmapping__is_active'
    ]
    
    search_fields = [
        'name', 
        'grouproleidentifier__role_identifier',
        'rolegroupmapping__role'
    ]
    
    ordering = ['name']
    
    def get_queryset(self, request):
        """优化查询性能"""
        try:
            return super().get_queryset(request).select_related(
                'grouproleidentifier'
            ).prefetch_related(
                'user_set',
                'permissions',
                'rolegroupmapping_set'
            ).annotate(
                user_count=Count('user_set'),
                permission_count=Count('permissions')
            )
        except Exception:
            return super().get_queryset(request)
    
    def get_role_status(self, obj: Group) -> str:
        """获取角色关联状态"""
        try:
            identifier = getattr(obj, 'grouproleidentifier', None)
            if identifier:
                status_colors = {
                    'role_linked': '#28a745',  # 绿色
                    'orphaned': '#ffc107',     # 黄色
                    'inactive': '#6c757d',     # 灰色
                    'error': '#dc3545'         # 红色
                }
                
                status_labels = {
                    'role_linked': '已关联角色',
                    'orphaned': '孤立组',
                    'inactive': '未激活',
                    'error': '错误状态'
                }
                
                color = status_colors.get(identifier.status, '#6c757d')
                label = status_labels.get(identifier.status, identifier.status)
                
                return format_html(
                    '<span style="color: {}; font-weight: bold;">🔗 {}</span>',
                    color, label
                )
            else:
                return format_html(
                    '<span style="color: #dc3545;">❌ 无标识符</span>'
                )
        except Exception:
            return format_html(
                '<span style="color: #dc3545;">❌ 无标识符</span>'
            )
    
    get_role_status.short_description = '角色状态'
    get_role_status.admin_order_field = 'grouproleidentifier__status'
    
    def get_role_identifier(self, obj: Group) -> str:
        """获取角色标识符"""
        try:
            identifier = getattr(obj, 'grouproleidentifier', None)
            if identifier and identifier.role_identifier:
                # 尝试获取角色映射以显示更友好的名称
                try:
                    mapping = obj.rolegroupmapping_set.first()
                    role_display = mapping.get_role_display() if mapping and hasattr(mapping, 'get_role_display') else identifier.role_identifier
                    return format_html(
                        '<span style="background: #e3f2fd; padding: 2px 6px; border-radius: 3px; font-family: monospace;">👤 {}</span>',
                        role_display
                    )
                except Exception:
                    return format_html(
                        '<span style="background: #fff3e0; padding: 2px 6px; border-radius: 3px; font-family: monospace;">⚠️ {}</span>',
                        identifier.role_identifier
                    )
            else:
                return format_html('<span style="color: #6c757d;">-</span>')
        except Exception:
            return format_html('<span style="color: #dc3545;">未设置</span>')
    
    get_role_identifier.short_description = '关联角色'
    get_role_identifier.admin_order_field = 'grouproleidentifier__role_identifier'
    
    def get_sync_status(self, obj: Group) -> str:
        """获取同步状态"""
        try:
            identifier = getattr(obj, 'grouproleidentifier', None)
            if identifier:
                sync_colors = {
                    'synced': '#28a745',      # 绿色
                    'pending': '#ffc107',     # 黄色
                    'failed': '#dc3545',      # 红色
                    'disabled': '#6c757d'     # 灰色
                }
                
                sync_labels = {
                    'synced': '已同步',
                    'pending': '待同步',
                    'failed': '同步失败',
                    'disabled': '已禁用'
                }
                
                color = sync_colors.get(identifier.sync_status, '#6c757d')
                label = sync_labels.get(identifier.sync_status, identifier.sync_status)
                
                return format_html(
                    '<span style="color: {};">🔄 {}</span>',
                    color, label
                )
            return format_html('<span style="color: #6c757d;">-</span>')
        except Exception:
            return format_html('<span style="color: #6c757d;">-</span>')
    
    get_sync_status.short_description = '同步状态'
    get_sync_status.admin_order_field = 'grouproleidentifier__sync_status'
    
    def get_user_count(self, obj: Group) -> str:
        """获取用户数量"""
        try:
            count = getattr(obj, 'user_count', None)
            if count is None:
                count = obj.user_set.count() if hasattr(obj, 'user_set') else 0
            if count > 0:
                return format_html(
                    '<span style="background: #e8f5e8; padding: 2px 6px; border-radius: 3px;">👥 {} 人</span>',
                    count
                )
            else:
                return format_html('<span style="color: #6c757d;">无用户</span>')
        except Exception:
            return format_html('<span style="color: #6c757d;">无用户</span>')
    
    get_user_count.short_description = '用户数量'
    
    def get_permission_count(self, obj: Group) -> str:
        """获取权限数量"""
        try:
            count = getattr(obj, 'permission_count', None)
            if count is None:
                count = obj.permissions.count() if hasattr(obj, 'permissions') else 0
            if count > 0:
                return format_html(
                    '<span style="background: #fff3e0; padding: 2px 6px; border-radius: 3px;">🔐 {} 项</span>',
                    count
                )
            else:
                return format_html('<span style="color: #6c757d;">无权限</span>')
        except Exception:
            return format_html('<span style="color: #6c757d;">无权限</span>')
    
    get_permission_count.short_description = '权限数量'
    
    def get_actions(self, obj: Group) -> str:
        """获取操作按钮"""
        actions = []
        
        # 查看详情按钮
        detail_url = reverse('admin:auth_group_change', args=[obj.pk])
        actions.append(
            f'<a href="{detail_url}" style="color: #007cba; text-decoration: none;">📝 编辑</a>'
        )
        
        # 角色映射管理按钮
        try:
            mapping = obj.rolegroupmapping_set.first()
            if mapping:
                mapping_url = reverse('admin:permissions_rolegroupmapping_change', args=[mapping.pk])
                actions.append(
                    f'<a href="{mapping_url}" style="color: #28a745; text-decoration: none;">🔗 映射</a>'
                )
            else:
                # 创建映射按钮
                create_mapping_url = reverse('admin:permissions_rolegroupmapping_add') + f'?group={obj.pk}'
                actions.append(
                    f'<a href="{create_mapping_url}" style="color: #ffc107; text-decoration: none;">➕ 创建映射</a>'
                )
        except Exception:
            # 创建映射按钮
            try:
                create_mapping_url = reverse('admin:permissions_rolegroupmapping_add') + f'?group={obj.pk}'
                actions.append(
                    f'<a href="{create_mapping_url}" style="color: #ffc107; text-decoration: none;">➕ 创建映射</a>'
                )
            except Exception:
                pass
        
        # 一致性检查按钮
        actions.append(
            f'<a href="javascript:void(0)" onclick="checkGroupConsistency({obj.pk})" style="color: #17a2b8; text-decoration: none;">🔍 检查</a>'
        )
        
        return format_html(' | '.join(actions))
    
    get_actions.short_description = '操作'
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表视图"""
        extra_context = extra_context or {}
        
        # 添加统计信息
        total_groups = Group.objects.count()
        role_linked_groups = Group.objects.filter(
            grouproleidentifier__status='role_linked'
        ).count()
        orphaned_groups = Group.objects.filter(
            grouproleidentifier__status='orphaned'
        ).count()
        
        extra_context.update({
            'group_stats': {
                'total': total_groups,
                'role_linked': role_linked_groups,
                'orphaned': orphaned_groups,
                'no_identifier': total_groups - role_linked_groups - orphaned_groups
            }
        })
        
        return super().changelist_view(request, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """自定义详情视图"""
        extra_context = extra_context or {}
        
        # 获取组对象
        try:
            group = get_object_or_404(Group, pk=object_id)
            
            # 添加角色关联信息
            role_info = {}
            try:
                identifier = getattr(group, 'grouproleidentifier', None)
                if identifier:
                    role_info['has_identifier'] = True
                    role_info['status'] = identifier.status
                    role_info['sync_status'] = identifier.sync_status
                    role_info['role_identifier'] = identifier.role_identifier
                    role_info['last_sync'] = getattr(identifier, 'last_sync_at', None)
                else:
                    role_info['has_identifier'] = False
            except Exception:
                role_info['has_identifier'] = False
            
            # 添加映射信息
            mapping_info = {}
            try:
                mapping = group.rolegroupmapping_set.first()
                if mapping:
                    mapping_info['has_mapping'] = True
                    mapping_info['role'] = mapping.role
                    mapping_info['auto_sync'] = getattr(mapping, 'auto_sync', False)
                    mapping_info['is_active'] = getattr(mapping, 'is_active', True)
                    mapping_info['priority'] = getattr(mapping, 'priority', 0)
                else:
                    mapping_info['has_mapping'] = False
            except Exception:
                mapping_info['has_mapping'] = False
            
            extra_context.update({
                'role_info': role_info,
                'mapping_info': mapping_info
            })
            
        except Exception:
            pass
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    class Media:
        js = ('admin/js/group_admin_enhanced.js',)
        css = {
            'all': ('admin/css/group_admin_enhanced.css',)
        }


# 注销默认的Group Admin并注册增强版本
admin.site.unregister(Group)
admin.site.register(Group, EnhancedGroupAdmin)