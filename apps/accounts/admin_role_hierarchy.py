"""角色所辖用户增项的Admin注册

提供级联管理界面
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from typing import Any

from .models import RoleLevel, RoleUser, UserExtension
from .models import RoleExtension
from apps.permissions.role_selector_config import StandardRoleAdminMixin


class RoleLevelAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """角色级别管理"""
    list_display = [
        'role_name', 'role', 'get_user_count', 'get_extension_config_count', 
        'is_active', 'sort_order', 'view_users_link', 'updated_at'
    ]
    list_filter = ['is_active', 'role', 'created_at']
    search_fields = ['role_name', 'role', 'description']
    ordering = ['sort_order', 'role']
    readonly_fields = ['created_at', 'updated_at']
    
    class Media:
        js = ('admin/js/dynamic_role_selector.js',)
        css = {
            'all': ('admin/css/dynamic_role_selector.css',)
        }
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role', 'role_name', 'description')
        }),
        ('设置', {
            'fields': ('is_active', 'sort_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_count(self, obj):
        """获取用户数量"""
        count = obj.get_user_count()
        if count > 0:
            return format_html(
                '<span style="color: #007cba; font-weight: bold;">{} 个用户</span>',
                count
            )
        return format_html('<span style="color: #666;">无用户</span>')
    get_user_count.short_description = '用户数量'  # type: ignore
    
    def get_extension_config_count(self, obj: Any) -> str:
        """获取增项配置数量"""
        count = obj.get_extension_config_count()
        if count > 0:
            return format_html(
                '<span style="color: #007cba; font-weight: bold;">{} 项</span>',
                count
            )
        return format_html('<span style="color: #666;">无配置</span>')
    get_extension_config_count.short_description = '增项配置'  # type: ignore
    
    def view_users_link(self, obj: Any) -> str:
        """查看用户链接"""
        url = reverse('accounts:role_users_list', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" style="background: #007cba; color: white; '
            'padding: 4px 8px; text-decoration: none; border-radius: 3px; font-size: 12px;">'
            '👥 查看用户</a>',
            url
        )
    view_users_link.short_description = '操作'  # type: ignore
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('sync-all/', self.admin_site.admin_view(self.sync_all_view), name='rolelevel_sync_all'),
        ]
        return custom_urls + urls
    
    def sync_all_view(self, request):
        """同步所有角色数据"""
        try:
            with transaction.atomic():
                from apps.accounts.services.role_service import RoleService
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # 同步角色级别 - 使用RoleService获取统一的角色数据
                role_choices = RoleService.get_role_choices()
                for role_code, role_name in role_choices:
                    RoleLevel.objects.get_or_create(
                        role=role_code,
                        defaults={
                            'role_name': role_name,
                            'description': f'{role_name}角色',
                            'is_active': True,
                            'sort_order': 0
                        }
                    )
                
                # 同步用户数据
                users = User.objects.filter(is_active=True)
                synced_count = 0
                
                for user in users:
                    if hasattr(user, 'role') and getattr(user, 'role', None):
                        role_level = RoleLevel.objects.get(role=getattr(user, 'role'))
                        role_user, created = RoleUser.objects.get_or_create(
                            user=user,
                            defaults={
                                'role_level': role_level,
                                'is_active': user.is_active
                            }
                        )
                        synced_count += 1
                
                messages.success(request, f'成功同步 {synced_count} 个用户的角色数据')
                
        except Exception as e:
            messages.error(request, f'同步失败: {str(e)}')
        
        return HttpResponseRedirect(reverse('admin:accounts_rolelevel_changelist'))


class RoleUserAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """角色用户管理"""
    list_display = [
        'user', 'get_user_real_name', 'role_level', 'get_extension_count', 
        'is_active', 'joined_at'
    ]
    list_filter = ['role_level', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__real_name', 'user__email']
    ordering = ['role_level', 'user__username']
    readonly_fields = ['joined_at', 'updated_at']
    
    class Media:
        js = ('admin/js/dynamic_role_selector.js',)
        css = {
            'all': ('admin/css/dynamic_role_selector.css',)
        }
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role_level', 'user', 'is_active')
        }),
        ('附加信息', {
            'fields': ('notes',)
        }),
        ('时间信息', {
            'fields': ('joined_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_real_name(self, obj: Any) -> str:
        """获取用户真实姓名"""
        return obj.user.real_name or '未设置'
    get_user_real_name.short_description = '真实姓名'  # type: ignore
    
    def get_extension_count(self, obj: Any) -> str:
        """获取增项数量"""
        count = obj.get_extension_count()
        if count > 0:
            return format_html(
                '<span style="color: #007cba; font-weight: bold;">{} 项</span>',
                count
            )
        return format_html('<span style="color: #666;">无增项</span>')
    get_extension_count.short_description = '增项数量'  # type: ignore
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('<int:role_user_id>/extensions/', 
                 self.admin_site.admin_view(self.extensions_view), 
                 name='roleuser_extensions'),
        ]
        return custom_urls + urls
    
    def extensions_view(self, request, role_user_id):
        """查看用户增项"""
        from django.shortcuts import get_object_or_404, redirect
        role_user = get_object_or_404(RoleUser, id=role_user_id)
        # 重定向到角色层级管理页面的用户增项详情
        return redirect('accounts:user_extensions_detail', role_user_id=role_user_id)


class UserExtensionAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """用户增项管理"""
    list_display = [
        'role_user', 'get_user_name', 'get_role_name', 'role_extension', 
        'get_display_value', 'is_active', 'created_by', 'updated_at'
    ]
    list_filter = [
        'role_user__role_level__role', 'role_extension__field_type', 
        'is_active', 'created_at'
    ]
    search_fields = [
        'role_user__user__username', 'role_user__user__real_name',
        'role_extension__field_label', 'field_value'
    ]
    ordering = ['role_user__role_level', 'role_user__user__username', 'role_extension__sort_order']
    readonly_fields = ['created_at', 'updated_at']
    
    class Media:
        js = ('admin/js/dynamic_role_selector.js',)
        css = {
            'all': ('admin/css/dynamic_role_selector.css',)
        }
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role_user', 'role_extension', 'field_value')
        }),
        ('设置', {
            'fields': ('is_active', 'created_by')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_name(self, obj: Any) -> str:
        """获取用户名"""
        return obj.role_user.user.username
    get_user_name.short_description = '用户名'  # type: ignore
    
    def get_role_name(self, obj: Any) -> str:
        """获取角色名"""
        return obj.role_user.role_level.role_name
    get_role_name.short_description = '角色'  # type: ignore
    
    def get_display_value(self, obj: Any) -> str:
        """获取显示值"""
        display_value = obj.get_display_value()
        if len(display_value) > 50:
            return display_value[:50] + '...'
        return display_value
    get_display_value.short_description = '字段值'  # type: ignore
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'role_user__user', 'role_user__role_level', 'role_extension', 'created_by'
        )


# 自定义Admin站点配置
class RoleHierarchyAdminSite(admin.AdminSite):
    """角色所辖用户增项专用Admin站点"""
    site_header = '角色所辖用户增项管理'
    site_title = '角色所辖用户增项'
    index_title = '欢迎使用角色所辖用户增项管理系统'
    
    def get_urls(self):
        """添加自定义首页"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.custom_index), name='index'),
        ]
        return custom_urls + urls
    
    def custom_index(self, request):
        """自定义首页"""
        return redirect('accounts:role_hierarchy_index')


# 创建专用Admin站点实例
role_hierarchy_admin = RoleHierarchyAdminSite(name='role_hierarchy_admin')

# 注册模型到专用站点
role_hierarchy_admin.register(RoleLevel, RoleLevelAdmin)
role_hierarchy_admin.register(RoleUser, RoleUserAdmin)
role_hierarchy_admin.register(UserExtension, UserExtensionAdmin)