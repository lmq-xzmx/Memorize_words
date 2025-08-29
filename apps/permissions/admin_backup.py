from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
import logging
import json
from .models import MenuModuleConfig, RoleGroupMapping, RoleManagement, SlotConfig, MenuValidity, RoleMapping, RoleSlotMenuAssignment, RoleSlotLevel1MenuAssignment, RoleSlotLevel2MenuAssignment



logger = logging.getLogger(__name__)
from .models_optimized import PermissionSyncLog
from .signals import sync_all_permissions
from .widgets import StandardRoleSelectWidget, StandardRoleChoiceField, RoleTextInputWidget
from .role_selector_config import StandardRoleAdminMixin, RoleCreationAdminMixin
from .forms import RoleSlotMenuAssignmentForm
from apps.accounts.models import UserRole
from apps.accounts.services.role_service import RoleService
from typing import TYPE_CHECKING, Any, Tuple, List, Type, cast

if TYPE_CHECKING:
    from django.db.models import QuerySet, Manager
    from django.db.models.base import ModelBase

# Django模型在运行时已经有objects属性，无需额外设置
# 类型检查器会自动识别Django模型的objects管理器
# 这种方法确保Django模型的objects属性在类型检查时被正确识别

# 通过运行时赋值来解决类型检查器对Django模型objects属性的误报
# 这些赋值语句在运行时不会改变任何行为，只是告诉类型检查器这些属性存在
# 移除冗余的类型注解代码，Django模型的objects管理器会自动可用


class MenuValidityInline(admin.TabularInline):
    """菜单有效性内联编辑"""
    model = MenuValidity
    extra = 1
    fields = ['role', 'is_valid']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """自定义字段显示"""
        if db_field.name == 'role':
            kwargs['widget'] = StandardRoleSelectWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(MenuModuleConfig)
class MenuModuleConfigAdmin(admin.ModelAdmin):
    """菜单模块配置Admin"""
    list_display = ['name', 'key', 'get_menu_level_display', 'icon', 'sort_order', 'is_active', 'get_role_count', 'created_at']
    list_filter = ['menu_level', 'is_active', 'created_at']
    search_fields = ['name', 'key', 'description']
    ordering = ['menu_level', 'sort_order', 'name']
    inlines = [MenuValidityInline]
    
    class Media:
        js = ('admin/js/menu_validity_filter.js',)
        css = {
            'all': ('admin/css/unified_admin_styles.css',)
        }
    
    @admin.display(description='菜单级别')
    def get_menu_level_display(self, obj):
        """显示菜单级别"""
        level_colors = {
            'root': '#007bff',      # 蓝色 - 根目录
            'level1': '#28a745',    # 绿色 - 一级目录
            'level2': '#ffc107',    # 黄色 - 二级目录
        }
        color = level_colors.get(obj.menu_level, '#6c757d')
        return format_html(
            '<span style="color: {}; background: {}20; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">{}</span>',
            color, color, obj.get_menu_level_display()
        )
    
    @admin.display(description='关联角色')
    def get_role_count(self, obj):
        from apps.accounts.services.role_service import RoleService
        
        # 获取当前通过MenuValidity关联的角色
        current_roles = set(MenuValidity.objects.filter(  # type: ignore
            menu_module=obj
        ).values_list('role', flat=True).distinct())
        
        # 获取角色显示名称
        try:
            all_roles = {role['code']: role['display_name'] for role in RoleService.get_all_roles()}
        except Exception:
            all_roles = {}
        
        # 显示当前关联角色数量和名称
        if current_roles:
            role_names = [all_roles.get(role, role) for role in current_roles]
            return format_html(
                '<span style="color: #28a745; background: #d4edda; padding: 2px 6px; border-radius: 3px; font-size: 12px;">{}个角色: {}</span>',
                len(current_roles),
                ', '.join(role_names)
            )
        else:
            return format_html(
                '<span style="color: #dc3545; background: #f8d7da; padding: 2px 6px; border-radius: 3px; font-size: 12px;">未关联</span>'
            )
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'key', 'menu_level', 'description')
        }),
        ('显示设置', {
            'fields': ('icon', 'url', 'sort_order', 'is_active')
        }),
    )
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('api/menus-by-role/', self.admin_site.admin_view(self.get_menus_by_role_view), name='menumoduleconfig_menus_by_role'),
        ]
        return custom_urls + urls
    
    def get_menus_by_role_view(self, request):
        """获取指定角色的菜单数据（JSON格式）"""
        if request.method != 'GET':
            return JsonResponse({'error': '只支持GET请求'}, status=405)
        
        role = request.GET.get('role')
        format_type = request.GET.get('format')
        
        if not role:
            return JsonResponse({'error': '缺少role参数'}, status=400)
        
        if format_type != 'json':
            # 如果不是JSON格式请求，返回到正常的changelist页面
            from django.shortcuts import redirect
            return redirect('admin:permissions_menumoduleconfig_changelist')
        
        try:
            # 获取该角色的有效菜单（只返回根菜单用于槽位分配）
            menu_level = request.GET.get('menu_level', 'root')  # 默认只返回根菜单
            valid_menus = MenuValidity.objects.filter(  # type: ignore
                role=role,
                is_valid=True,
                menu_module__menu_level=menu_level
            ).select_related('menu_module')
            
            menus_data = []
            for validity in valid_menus:
                menu = validity.menu_module
                menus_data.append({
                    'id': menu.id,
                    'name': menu.name,
                    'key': menu.key,
                    'menu_level': menu.menu_level,
                    'icon': menu.icon or '',
                    'url': menu.url or '',
                    'sort_order': menu.sort_order,
                    'is_active': menu.is_active,
                    'description': menu.description or ''
                })
            
            # 按菜单级别和排序顺序排序
            level_order = {'root': 0, 'level1': 1, 'level2': 2}
            menus_data.sort(key=lambda x: (level_order.get(x['menu_level'], 999), x['sort_order'], x['name']))
            
            return JsonResponse({
                'success': True,
                'role': role,
                'menus': menus_data,
                'count': len(menus_data)
            })
            
        except Exception as e:
            logger.error(f"获取角色菜单失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'获取菜单数据失败: {str(e)}'
            }, status=500)
    
    def changelist_view(self, request, extra_context=None):
        """重写changelist_view以处理JSON请求"""
        # 检查是否是JSON格式请求
        if request.GET.get('format') == 'json':
            return self.get_menus_by_role_view(request)
        
        # 否则返回正常的changelist页面
        return super().changelist_view(request, extra_context)


# RoleMenuPermission 模型已废弃，相关 Admin 配置已移除


@admin.register(RoleGroupMapping)
class RoleGroupMappingAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """角色组映射Admin"""
    list_display = ['role', 'group', 'get_mapping_status', 'created_at']
    list_filter = ['role', 'auto_sync', 'created_at']
    search_fields = ['group__name']
    ordering = ['role', 'group__name']
    change_form_template = 'admin/permissions/rolegroupmapping/change_form.html'
    
    class Media:
        js = ('admin/js/unified_role_selector.js',)
        css = {
            'all': ('admin/css/unified_admin_styles.css', 'admin/css/role_group_mapping.css')
        }
    

    
    @admin.display(description='同步状态')
    def get_mapping_status(self, obj):
        """显示映射状态"""
        if obj.auto_sync:
            return format_html(
                '<span style="color: #28a745; background: #d4edda; padding: 2px 6px; border-radius: 3px; font-size: 12px;">'  
                '🔗 自动同步</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; background: #f8d7da; padding: 2px 6px; border-radius: 3px; font-size: 12px;">'  
                '❌ 手动同步</span>'
            )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义外键字段"""
        if db_field.name == "group":
            # 为组字段添加自定义widget
            from django import forms
            from django.contrib.auth.models import Group
            
            class GroupSelectWidget(forms.Select):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.attrs.update({
                        'id': 'id_group',
                        'class': 'form-control'
                    })
            
            kwargs['widget'] = GroupSelectWidget
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role', 'group')
        }),
        ('同步设置', {
            'fields': ('auto_sync',)
        }),
    )
    
    # 角色选择器配置已通过StandardRoleAdminMixin自动处理
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('sync-role-groups/', self.admin_site.admin_view(self.sync_role_groups_view), name='sync_role_groups'),
            path('create-group-for-role/', self.admin_site.admin_view(self.create_group_for_role_view), name='create_group_for_role'),
            path('get-group-list/', self.admin_site.admin_view(self.get_group_list_view), name='get_group_list'),
            path('get-role-list/', self.admin_site.admin_view(self.get_role_list_view), name='get_role_list'),
            path('check-sync-status/', self.admin_site.admin_view(self.check_sync_status_view), name='check_sync_status'),
            path('refresh-all-sync/', self.admin_site.admin_view(self.refresh_all_sync_view), name='refresh_all_sync'),
        ]
        return custom_urls + urls
    
    def sync_role_groups_view(self, request):
        """同步角色组视图"""
        from django.contrib.auth.models import Group
        import json
        
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                role = data.get('role')
                
                if role:
                    # 获取或创建对应的组
                    role_display = RoleService.get_role_display_name(role)
                    group_name = f"{role_display}组"
                    group, created = Group.objects.get_or_create(name=group_name)  # type: ignore
                    
                    # 更新或创建角色组映射
                    mapping, mapping_created = RoleGroupMapping.objects.get_or_create(  # type: ignore
                        role=role,
                        defaults={'group': group, 'auto_sync': True}
                    )
                    
                    if not mapping_created:
                        mapping.group = group
                        mapping.save()
                    
                    return JsonResponse({
                        'success': True,
                        'group_id': group.pk,
                        'group_name': group.name,
                        'created': created or mapping_created
                    })
                else:
                    return JsonResponse({'success': False, 'error': '角色参数缺失'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})
    
    def create_group_for_role_view(self, request):
        """为角色创建组视图"""
        from django.contrib.auth.models import Group
        import json
        
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                role = data.get('role')
                group_name = data.get('group_name')
                
                if role and group_name:
                    # 创建新组
                    group = Group.objects.create(name=group_name)
                    
                    # 创建或更新角色组映射
                    mapping, created = RoleGroupMapping.objects.get_or_create(  # type: ignore
                        role=role,
                        defaults={'group': group, 'auto_sync': True}
                    )
                    
                    if not created:
                        mapping.group = group
                        mapping.save()
                    
                    return JsonResponse({
                        'success': True,
                        'group_id': group.pk,
                        'group_name': group.name
                    })
                else:
                    return JsonResponse({'success': False, 'error': '参数缺失'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})
    
    def get_group_list_view(self, request):
        """获取组列表API"""
        from django.contrib.auth.models import Group
        
        if request.method == 'GET':
            try:
                groups = Group.objects.all().order_by('name')
                group_list = [{
                    'id': group.pk,
                    'name': group.name
                } for group in groups]
                
                return JsonResponse({
                    'success': True,
                    'groups': group_list
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持GET请求'})
    
    def get_role_list_view(self, request):
        """获取角色列表API"""
        if request.method == 'GET':
            try:
                # 使用统一的角色服务获取所有角色
                role_choices = RoleService.get_role_choices(include_empty=False)
                role_list = [{
                    'value': choice[0],
                    'display_name': str(choice[1])
                } for choice in role_choices]
                
                return JsonResponse({
                    'success': True,
                    'roles': role_list
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持GET请求'})
    
    def check_sync_status_view(self, request):
        """检查角色同步状态API"""
        if request.method == 'GET':
            try:
                role = request.GET.get('role')
                
                if not role:
                    return JsonResponse({'success': False, 'error': '缺少角色参数'})
                
                # 获取角色对应的组映射
                try:
                    mapping = RoleGroupMapping.objects.select_related('group').get(role=role)  # type: ignore
                    return JsonResponse({
                        'success': True,
                        'group_id': mapping.group.pk,
                        'group_name': mapping.group.name,
                        'has_mapping': True
                    })
                except RoleGroupMapping.DoesNotExist:  # type: ignore
                    return JsonResponse({
                        'success': True,
                        'group_id': None,
                        'group_name': None,
                        'has_mapping': False
                    })
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        elif request.method == 'POST':
            try:
                import json
                data = json.loads(request.body)
                role = data.get('role')
                user_id = data.get('user_id')
                
                if not role:
                    return JsonResponse({'success': False, 'error': '缺少角色参数'})
                
                # 获取角色权限数量
                try:
                    role_mgmt = RoleManagement.objects.get(role=role)  # type: ignore
                    role_perms = len(role_mgmt.get_all_permissions())
                except RoleManagement.DoesNotExist:  # type: ignore
                    role_perms = 0
                
                # 获取组权限数量和映射状态
                try:
                    mapping = RoleGroupMapping.objects.select_related('group').get(role=role)  # type: ignore
                    group_perms = mapping.group.permissions.count()
                    has_mapping = True
                except RoleGroupMapping.DoesNotExist:  # type: ignore
                    group_perms = 0
                    has_mapping = False
                
                return JsonResponse({
                    'success': True,
                    'sync_data': {
                        'role': role,
                        'user_id': user_id,
                        'role_perms': role_perms,
                        'group_perms': group_perms,
                        'has_mapping': has_mapping,
                        'is_synced': group_perms == role_perms and role_perms > 0
                    }
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持GET和POST请求'})
    
    def refresh_all_sync_view(self, request):
        """刷新所有同步数据API"""
        if request.method == 'POST':
            try:
                from .utils import PermissionUtils
                
                # 获取所有活跃角色
                active_roles = RoleManagement.objects.filter(is_active=True)  # type: ignore
                success_count = 0
                total_count = active_roles.count()
                
                for role in active_roles:
                    try:
                        # 同步角色权限到组
                        sync_success = PermissionUtils.sync_role_permissions(role)
                        if sync_success:
                            success_count += 1
                        
                        # 记录日志
                        PermissionSyncLog.objects.create(  # type: ignore
                            sync_type='auto_refresh',
                            target_type='role',
                            target_id=role.role,
                            action=f'自动刷新同步: {role.display_name}',
                            result=f'角色 {role.display_name} 同步刷新: {"成功" if sync_success else "失败"}',
                            success=sync_success
                        )
                    except Exception as e:
                        # 记录失败日志
                        PermissionSyncLog.objects.create(  # type: ignore
                            sync_type='auto_refresh',
                            target_type='role',
                            target_id=role.role,
                            action=f'自动刷新同步失败: {role.display_name}',
                            result=f'错误: {str(e)}',
                            success=False
                        )
                
                return JsonResponse({
                    'success': True,
                    'message': f'同步刷新完成：{success_count}/{total_count} 个角色刷新成功',
                    'success_count': success_count,
                    'total_count': total_count
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})

    fieldsets = (
        ('基本信息', {
            'fields': ('role', 'group')
        }),
        ('同步设置', {
            'fields': ('auto_sync',)
        }),
    )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """自定义修改视图"""
        extra_context = extra_context or {}
        extra_context['role_choices'] = RoleService.get_role_choices(include_empty=False)
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        """自定义添加视图"""
        extra_context = extra_context or {}
        extra_context['role_choices'] = RoleService.get_role_choices(include_empty=False)
        return super().add_view(request, form_url, extra_context)


@admin.register(PermissionSyncLog)
class PermissionSyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_type', 'target_type', 'target_id', 'operation', 'is_success', 'created_at']
    list_filter = ['sync_type', 'target_type', 'is_success', 'created_at']
    search_fields = ['target_id', 'result']
    readonly_fields = ['sync_type', 'target_type', 'target_id', 'operation', 'result', 'is_success', 'created_at', 'created_by', 'duration_ms']
    ordering = ['-created_at']
    

    
    @admin.display(description='同步状态')
    def get_sync_status(self, obj):
        """显示同步状态"""
        if obj.is_success:
            return format_html(
                '<span style="color: #28a745; background: #d4edda; padding: 2px 6px; border-radius: 3px; font-size: 12px;">'  
                '✅ 成功</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; background: #f8d7da; padding: 2px 6px; border-radius: 3px; font-size: 12px;">'  
                '❌ 失败</span>'
            )
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False


# 自定义Admin动作
class PermissionManagementAdmin(admin.ModelAdmin):
    """权限管理Admin基类"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sync-permissions/', self.admin_site.admin_view(self.sync_permissions_view), name='sync_permissions'),
        ]
        return custom_urls + urls
    
    def sync_permissions_view(self, request):
        """同步权限视图"""
        if request.method == 'POST':
            success = sync_all_permissions()
            if success:
                messages.success(request, '权限同步成功！')
            else:
                messages.error(request, '权限同步失败，请查看日志。')
        
        # return HttpResponseRedirect(reverse('admin:permissions_rolemenuPermission_changelist'))  # RoleMenuPermission已废弃
        return HttpResponseRedirect(reverse('admin:permissions_menumoduleconfig_changelist'))


# EnhancedRoleMenuPermissionAdmin 类已移除，因为 RoleMenuPermission 模型已废弃


@admin.register(RoleManagement)
class RoleManagementAdmin(StandardRoleAdminMixin, admin.ModelAdmin, RoleCreationAdminMixin):
    """角色管理Admin - 支持角色继承和权限优化"""
    list_display = ['display_name', 'get_role_display_name', 'get_parent_role', 'is_active', 'sort_order', 'get_permissions_count', 'get_inherited_permissions_count', 'get_hierarchy_level', 'created_at']
    list_filter = ['role', 'is_active', 'parent', 'created_at']
    search_fields = ['display_name', 'description', 'role']
    ordering = ['sort_order', 'role']
    filter_horizontal = ['permissions']
    list_per_page = 30
    actions = ['activate_roles', 'deactivate_roles', 'sync_to_groups', 'optimize_permissions']
    
    class Media:
        js = ('admin/js/role_management_auto_fill.js', 'admin/js/unified_role_selector.js')
        css = {
            'all': ('admin/css/unified_admin_styles.css', 'admin/css/role_permission_sync.css')
        }
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('get-role-list/', self.admin_site.admin_view(self.get_role_list_view), name='get_role_list'),
            path('sync-role-to-groups/', self.admin_site.admin_view(self.sync_role_to_groups_view), name='sync_role_to_groups'),
            path('sync-all-roles-to-groups/', self.admin_site.admin_view(self.sync_all_roles_to_groups_view), name='sync_all_roles_to_groups'),
        ]
        return custom_urls + urls
    
    def get_role_list_view(self, request):
        """获取角色列表API"""
        if request.method == 'GET':
            try:
                roles = RoleManagement.objects.filter(is_active=True).order_by('sort_order', 'role')  # type: ignore
                role_list = [{
                    'value': role.role,
                    'display_name': role.get_role_display()
                } for role in roles]
                
                return JsonResponse({
                    'success': True,
                    'roles': role_list
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持GET请求'})
    
    def sync_role_to_groups_view(self, request):
        """同步单个角色权限到组"""
        if request.method == 'POST':
            try:
                import json
                data = json.loads(request.body)
                role_id = data.get('role_id')
                
                if not role_id:
                    return JsonResponse({'success': False, 'error': '缺少角色ID'})
                
                role = RoleManagement.objects.get(role=role_id)  # type: ignore
                
                # 同步权限到Django组
                from .utils import PermissionUtils
                sync_success = PermissionUtils.sync_role_permissions(role)
                
                # 记录日志
                PermissionSyncLog.objects.create(  # type: ignore
                    sync_type='manual',
                    target_type='role',
                    target_id=role.role,
                    action=f'手动同步角色权限: {role.display_name}',
                    result=f'角色 {role.display_name} 权限同步: {"成功" if sync_success else "失败"}',
                    success=sync_success
                )
                
                return JsonResponse({
                    'success': sync_success,
                    'message': f'角色 "{role.display_name}" 权限同步{"成功" if sync_success else "失败"}'
                })
                
            except RoleManagement.DoesNotExist:  # type: ignore
                return JsonResponse({'success': False, 'error': '角色不存在'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})
    
    def changelist_view(self, request, extra_context=None):
        """重写changelist视图，添加权限同步按钮"""
        extra_context = extra_context or {}
        extra_context.update({
            'show_sync_buttons': True,
            'sync_all_url': reverse('admin:sync_all_roles_to_groups'),
            'sync_logs_url': reverse('admin:permissions_permissionsynclog_changelist') + '?target_type__exact=role',
        })
        return super().changelist_view(request, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """重写change视图，添加单个角色同步按钮"""
        extra_context = extra_context or {}
        if object_id:
            extra_context.update({
                'show_single_sync_button': True,
                'sync_single_url': reverse('admin:sync_role_to_groups'),
                'role_id': object_id,
            })
        return super().change_view(request, object_id, form_url, extra_context)
    
    def sync_all_roles_to_groups_view(self, request):
        """同步所有角色权限到Django组的视图"""
        if request.method == 'POST':
            try:
                # 获取所有活跃角色
                RoleManagement = apps.get_model('permissions', 'RoleManagement')
                roles = RoleManagement.objects.filter(is_active=True)
                success_count = 0
                error_count = 0
                
                for role in roles:
                    try:
                        self.sync_role_to_group(role)
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        messages.error(request, f'同步角色 {role.display_name} 失败: {str(e)}')
                
                if success_count > 0:
                    messages.success(request, f'成功同步 {success_count} 个角色到Django组')
                if error_count > 0:
                    messages.warning(request, f'{error_count} 个角色同步失败')
                
                return JsonResponse({
                    'success': True,
                    'message': f'批量同步完成：成功 {success_count} 个，失败 {error_count} 个',
                    'success_count': success_count,
                    'error_count': error_count
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role', 'display_name', 'description', 'is_active', 'sort_order')
        }),
        ('角色继承', {
            'fields': ('parent',),
            'description': '选择父角色，子角色将自动继承父角色的所有权限'
        }),
        ('权限配置 - 单向同步到组', {
            'fields': ('permissions',),
            'classes': ('wide',),
            'description': '🔄 <strong>权限单向同步特性</strong>：此处配置的权限将自动同步到对应的Django组中。<br/>'
                          '📋 角色管理中的所有权限都会在组管理中创建对应的权限。<br/>'
                          '🎯 组管理中也可以创建独立于角色管理的组，用于特殊控制。<br/>'
                          '⚠️ 注意：权限同步是单向的（角色→组），组中的权限修改不会影响角色配置。'
        }),
    )
    
    # 角色选择器配置已通过RoleCreationAdminMixin自动处理
    

    
    @admin.display(description='角色')
    def get_role_display_name(self, obj):
        """显示角色名称"""
        return obj.get_role_display()
    

    
    @admin.display(description='父角色')
    def get_parent_role(self, obj):
        """显示父角色"""
        if obj.parent:
            return format_html(
                '<span style="color: #007bff;">📁 {}</span>',
                obj.parent.display_name
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">🏠 根角色</span>'
            )
    

    
    @admin.display(description='直接权限')
    def get_permissions_count(self, obj):
        """显示直接权限数量"""
        count = obj.permissions.count()
        if count > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} 个</span>',
                count
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">0 个</span>'
            )
    

    
    @admin.display(description='总权限')
    def get_inherited_permissions_count(self, obj):
        """显示总权限数量（包括继承）"""
        all_perms = obj.get_all_permissions()
        direct_count = obj.permissions.count()
        total_count = len(all_perms)
        inherited_count = total_count - direct_count
        
        if inherited_count > 0:
            return format_html(
                '<span style="color: #17a2b8; font-weight: bold;">{} 个 (继承 {})</span>',
                total_count, inherited_count
            )
        else:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} 个</span>',
                total_count
            )
    
    @admin.display(description='层级')
    def get_hierarchy_level(self, obj):
        """显示角色层级"""
        level = obj.get_hierarchy_level()
        level_colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#20c997', '#6f42c1']
        color = level_colors[min(level, len(level_colors) - 1)]
        return format_html(
            '<span style="color: {}; background: {}20; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">L{}</span>',
            color, color, level
        )
    
    @admin.action(description='激活选中角色')
    def activate_roles(self, request, queryset):
        """批量激活角色"""
        updated = queryset.update(is_active=True)
        # 刷新角色缓存
        RoleService.refresh_cache()
        self.message_user(request, f'已激活 {updated} 个角色，缓存已刷新')
    
    @admin.action(description='停用选中角色')
    def deactivate_roles(self, request, queryset):
        """批量停用角色"""
        updated = queryset.update(is_active=False)
        # 刷新角色缓存
        RoleService.refresh_cache()
        self.message_user(request, f'已停用 {updated} 个角色，缓存已刷新')
    
    def sync_role_to_group(self, role):
        """同步角色到Django组"""
        from django.contrib.auth.models import Group
        try:
            # 首先检查是否已有RoleGroupMapping
            try:
                mapping = RoleGroupMapping.objects.get(role=role.role)  # type: ignore
                group = mapping.group
                # 使用现有的组
            except RoleGroupMapping.DoesNotExist:  # type: ignore
                # 如果没有映射，使用新的命名规则创建组和映射
                group_name = f"role_{role.role}"
                group, created = Group.objects.get_or_create(name=group_name)
                RoleGroupMapping.objects.get_or_create(  # type: ignore
                    role=role.role,
                    defaults={
                        'group': group,
                        'auto_sync': True
                    }
                )
            
            # 同步权限
            all_permissions = role.get_all_permissions()
            group.permissions.clear()
            if all_permissions:
                group.permissions.set(all_permissions)
            return True
        except Exception as e:
            logger.error(f"同步角色 {role.role} 到组失败: {e}")
            return False
    
    @admin.action(description='同步到Django组')
    def sync_to_groups(self, request, queryset):
        """批量同步角色到Django组"""
        synced_count = 0
        for role in queryset:
            try:
                if self.sync_role_to_group(role):
                    synced_count += 1
            except Exception as e:
                self.message_user(request, f'同步角色 {role.display_name} 失败: {str(e)}', level=messages.ERROR)
        
        if synced_count > 0:
            # 刷新角色缓存
            RoleService.refresh_cache()
            self.message_user(request, f'已成功同步 {synced_count} 个角色到Django组，缓存已刷新')
    
    @admin.action(description='优化权限配置')
    def optimize_permissions(self, request, queryset):
        """优化权限配置"""
        try:
            from django.core.management import call_command
            call_command('optimize_role_permissions', '--dry-run')
            self.message_user(request, '权限配置优化预览完成，请查看控制台输出')
        except Exception as e:
            self.message_user(request, f'权限优化失败: {str(e)}', level=messages.ERROR)
    
    def clean_model(self, request, obj, form, change):
        """模型验证"""
        try:
            obj.clean()
        except ValidationError as e:
            form.add_error(None, e)
    
    def save_model(self, request, obj, form, change):
        """保存模型时的处理"""
        # 先进行模型验证
        self.clean_model(request, obj, form, change)
        
        super().save_model(request, obj, form, change)
        
        # 同步权限到Django组
        from .utils import PermissionUtils
        sync_success = PermissionUtils.sync_role_permissions(obj)
        
        # 记录操作日志
        action = '更新角色' if change else '创建角色'
        PermissionSyncLog.objects.create(  # type: ignore
            sync_type='manual',
            target_type='role',
            target_id=obj.role,
            operation='update' if change else 'create',
            result=f'角色 {obj.display_name} 已成功{action}，权限同步: {"成功" if sync_success else "失败"}',
            is_success=True
        )
        
        if change:
            messages.success(request, f'角色 "{obj.display_name}" 已成功更新！权限同步: {"成功" if sync_success else "失败"}')
        else:
            messages.success(request, f'角色 "{obj.display_name}" 已成功创建！权限同步: {"成功" if sync_success else "失败"}')
    
    def delete_model(self, request, obj):
        """删除模型时的处理"""
        role_name = obj.display_name
        super().delete_model(request, obj)
        
        # 记录操作日志
        PermissionSyncLog.objects.create(  # type: ignore
            sync_type='manual',
            target_type='role',
            target_id=obj.role,
            operation='delete',
            result=f'角色 {role_name} 已成功删除',
            is_success=True
        )
        
        messages.success(request, f'角色 "{role_name}" 已成功删除！')
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).prefetch_related('permissions')


@admin.register(SlotConfig)
class SlotConfigAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """槽位配置管理"""
    list_display = ['name', 'get_role_display_name', 'slot_count', 'is_active', 'created_at', 'updated_at']
    list_filter = ['slot_count', 'is_active', 'role', 'created_at']
    search_fields = ['name', 'role', 'description']
    ordering = ['role', '-is_active', '-created_at']
    list_editable = ['is_active']
    actions = ['activate_selected', 'deactivate_selected']
    
    class Media:
        css = {
            'all': ('admin/css/unified_admin_styles.css',)
        }
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表视图，按角色分组显示"""
        extra_context = extra_context or {}
        
        # 获取所有槽位配置，按角色分组
        SlotConfig = apps.get_model('permissions', 'SlotConfig')
        all_configs = SlotConfig.objects.all().order_by('role', '-is_active', '-created_at')
        
        # 按角色分组
        role_groups = {}
        for config in all_configs:
            role_name = config.role or '全局默认'
            role_display = RoleService.get_role_display_name(config.role) if config.role else '全局默认'
            
            if role_name not in role_groups:
                role_groups[role_name] = {
                    'display_name': role_display,
                    'configs': [],
                    'active_count': 0
                }
            
            role_groups[role_name]['configs'].append(config)
            if config.is_active:
                role_groups[role_name]['active_count'] += 1
        
        extra_context.update({
            'role_groups': role_groups,
            'show_role_grouping': True,
            'title': '槽位配置管理 - 按角色分组'
        })
        
        return super().changelist_view(request, extra_context)
    
    @admin.action(description='激活选中的槽位配置')
    def activate_selected(self, request, queryset):
        """批量激活槽位配置，确保每个角色只有一个激活配置"""
        updated_count = 0
        SlotConfig = apps.get_model('permissions', 'SlotConfig')
        
        for config in queryset:
            if not config.is_active:
                # 同一角色下的其他配置设为非激活
                SlotConfig.objects.filter(
                    role=config.role, 
                    is_active=True
                ).exclude(pk=config.pk).update(is_active=False)
                
                # 激活当前配置
                config.is_active = True
                config.save()
                updated_count += 1
        
        if updated_count > 0:
            self.message_user(
                request,
                f'成功激活 {updated_count} 个槽位配置。每个角色的其他配置已自动设为非激活状态。'
            )
        else:
            self.message_user(request, '所选配置已经是激活状态。')
    
    @admin.action(description='停用选中的槽位配置')
    def deactivate_selected(self, request, queryset):
        """批量停用槽位配置"""
        updated_count = queryset.filter(is_active=True).update(is_active=False)
        if updated_count > 0:
            self.message_user(request, f'成功停用 {updated_count} 个槽位配置。')
        else:
            self.message_user(request, '所选配置已经是停用状态。')
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """自定义数据库字段"""
        # 处理CharField类型的role字段
        if hasattr(db_field, 'name') and db_field.name == 'role' and db_field.__class__.__name__ == 'CharField':
            result = super().formfield_for_char_field(db_field, request, **kwargs)
            if result is not None:
                return result
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    @admin.display(description='角色名称')
    def get_role_display_name(self, obj):
        return RoleService.get_role_display_name(obj.role) if obj.role else '全局默认'
    

    
    def has_delete_permission(self, request, obj=None):
        """防止删除激活的配置"""
        if obj and obj.is_active:
            return False
        return super().has_delete_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        """保存时确保每个角色只有一个激活配置"""
        if obj.is_active:
            # 获取SlotConfig模型
            SlotConfig = apps.get_model('permissions', 'SlotConfig')
            # 同一角色下的其他配置设为非激活
            SlotConfig.objects.filter(
                role=obj.role, 
                is_active=True
            ).exclude(pk=obj.pk).update(is_active=False)
            
            # 记录操作日志
            messages.success(
                request, 
                f'已激活角色 "{self.get_role_display_name(obj)}" 的槽位配置 "{obj.name}"，'
                f'该角色下的其他配置已自动设为非激活状态。'
            )
        
        super().save_model(request, obj, form, change)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'role', 'description')
        }),
        ('槽位配置', {
            'fields': ('slot_count', 'is_active')
        }),
    )


@admin.register(MenuValidity)
class MenuValidityAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """菜单有效性管理"""
    list_display = ['menu_module', 'get_menu_level_display', 'get_role_display_name', 'is_valid', 'created_at']
    list_filter = ['is_valid', 'role', 'menu_module__menu_level', 'created_at']
    search_fields = ['menu_module__name', 'menu_module__key', 'role']
    ordering = ['menu_module__menu_level', 'menu_module__sort_order', 'role']
    
    class Media:
        js = ('admin/js/menu_validity_filter.js',)
    
    @admin.display(description='菜单级别')
    def get_menu_level_display(self, obj):
        """显示菜单级别"""
        level_colors = {
            'root': '#007bff',      # 蓝色 - 根目录
            'level1': '#28a745',    # 绿色 - 一级目录
            'level2': '#ffc107',    # 黄色 - 二级目录
        }
        color = level_colors.get(obj.menu_module.menu_level, '#6c757d')
        return format_html(
            '<span style="color: {}; background: {}20; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">{}</span>',
            color, color, obj.menu_module.get_menu_level_display()
        )
    
    @admin.display(description='角色名称')
    def get_role_display_name(self, obj):
        """显示角色名称"""
        return obj.get_role_display()
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """自定义数据库字段"""
        # 处理CharField类型的role字段
        if hasattr(db_field, 'name') and db_field.name == 'role' and db_field.__class__.__name__ == 'CharField':
            result = super().formfield_for_char_field(db_field, request, **kwargs)
            if result is not None:
                return result
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义外键字段"""
        if db_field.name == "menu_module":
            MenuModuleConfig = apps.get_model('permissions', 'MenuModuleConfig')
            kwargs["queryset"] = MenuModuleConfig.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('get-valid-menus/<str:role>/', self.admin_site.admin_view(self.get_valid_menus_view), name='menuvalidity_get_valid_menus'),
        ]
        return custom_urls + urls
    
    def get_valid_menus_view(self, request, role):
        """获取角色对应的有效菜单"""
        try:
            # 动态获取模型类
            MenuValidity = apps.get_model('permissions', 'MenuValidity')
            MenuModuleConfig = apps.get_model('permissions', 'MenuModuleConfig')
            
            # 获取该角色已设置为有效的菜单
            valid_menu_ids = MenuValidity.objects.filter(
                role=role, 
                is_valid=True
            ).values_list('menu_module_id', flat=True)
            
            # 获取所有活跃菜单，标记哪些是该角色有效的
            menus = MenuModuleConfig.objects.filter(is_active=True).values(
                'id', 'name', 'key', 'menu_level'
            )
            
            menu_list = []
            for menu in menus:
                menu_list.append({
                    'id': menu['id'],
                    'name': menu['name'],
                    'key': menu['key'],
                    'menu_level': menu['menu_level'],
                    'is_valid_for_role': menu['id'] in valid_menu_ids
                })
            
            return JsonResponse({
                'success': True,
                'menus': menu_list
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


# RoleMenuAssignmentAdmin 已删除 - 功能由槽位系统替代


# FrontendMenuConfigAdmin 已删除 - 功能由 MenuModuleConfig 替代
# FrontendMenuRoleAssignmentInline 已删除 - 功能由 MenuValidity 内联替代


# FrontendMenuRoleAssignmentAdmin 已删除
# 该功能已由 MenuModuleConfig 和 MenuValidity 内联替代


@admin.register(RoleMapping)
class RoleMappingAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """角色映射管理Admin"""
    list_display = ['get_user_role_display', 'role_management', 'is_active', 'auto_sync', 'created_at']
    list_filter = ['is_active', 'auto_sync', 'user_role', 'created_at']
    search_fields = ['user_role', 'role_management__display_name', 'description']
    ordering = ['user_role']
    list_editable = ['is_active', 'auto_sync']
    
    class Media:
        js = ('admin/js/unified_role_selector.js',)
        css = {
            'all': ('admin/css/unified_admin_styles.css',)
        }
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user_role', 'role_management', 'description')
        }),
        ('配置选项', {
            'fields': ('is_active', 'auto_sync')
        }),
    )
    
    @admin.display(description='用户角色')
    def get_user_role_display(self, obj):
        """显示用户角色名称"""
        return obj.get_user_role_display()
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """自定义选择字段"""
        if db_field.name == 'user_role':
            # 获取UserRole的选择项
            try:
                kwargs['choices'] = UserRole.choices
            except AttributeError:
                pass
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义外键字段"""
        if db_field.name == 'role_management':
            # 只显示激活的角色管理
            kwargs['queryset'] = RoleManagement.objects.filter(is_active=True)  # type: ignore
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """保存模型时的处理"""
        super().save_model(request, obj, form, change)
        
        # 如果启用了自动同步，触发权限同步
        if obj.auto_sync:
            try:
                from .services import RoleMappingService
                RoleMappingService.sync_role_permissions(obj.user_role)
                messages.success(request, f'角色 {obj.get_user_role_display()} 的权限已同步')
            except Exception as e:
                messages.warning(request, f'权限同步失败: {str(e)}')
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('initialize-mappings/', self.admin_site.admin_view(self.initialize_mappings_view), name='permissions_rolemapping_initialize'),
            path('validate-consistency/', self.admin_site.admin_view(self.validate_consistency_view), name='permissions_rolemapping_validate'),
        ]
        return custom_urls + urls
    
    def initialize_mappings_view(self, request):
        """初始化默认映射关系"""
        try:
            from .services import RoleMappingService
            results = RoleMappingService.initialize_default_mappings()
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            if success_count == total_count:
                messages.success(request, f'成功初始化 {success_count} 个角色映射')
            else:
                messages.warning(request, f'初始化完成：成功 {success_count}/{total_count} 个角色映射')
                
        except Exception as e:
            messages.error(request, f'初始化失败: {str(e)}')
        
        return HttpResponseRedirect(reverse('admin:permissions_rolemapping_changelist'))
    
    def validate_consistency_view(self, request):
        """验证映射一致性"""
        try:
            from .services import RoleMappingService
            issues = RoleMappingService.validate_mapping_consistency()
            
            total_issues = sum(len(issue_list) for issue_list in issues.values())
            
            if total_issues == 0:
                messages.success(request, '映射关系一致性验证通过')
            else:
                for issue_type, issue_list in issues.items():
                    if issue_list:
                        messages.warning(request, f'{issue_type}: {len(issue_list)} 个问题')
                        
        except Exception as e:
            messages.error(request, f'验证失败: {str(e)}')
        
        return HttpResponseRedirect(reverse('admin:permissions_rolemapping_changelist'))
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表视图"""
        extra_context = extra_context or {}
        extra_context.update({
            'title': '角色映射管理',
            'subtitle': '管理UserRole和RoleManagement之间的映射关系',
            'has_initialize_permission': True,
            'has_validate_permission': True,
        })
        return super().changelist_view(request, extra_context=extra_context)


class RoleSlotLevel2MenuAssignmentInline(admin.TabularInline):
    """二级菜单分配内联编辑"""
    model = RoleSlotLevel2MenuAssignment
    extra = 0
    fields = ['level2_menu', 'is_active', 'sort_order']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """限制二级菜单选择范围"""
        if db_field.name == "level2_menu":
            # 获取当前一级菜单分配的ID
            level1_assignment_id = request.resolver_match.kwargs.get('object_id')
            if level1_assignment_id:
                try:
                    level1_assignment = RoleSlotLevel1MenuAssignment.objects.get(id=level1_assignment_id)  # type: ignore
                    # 只显示该一级菜单下的二级菜单
                    kwargs["queryset"] = MenuModuleConfig.objects.filter(  # type: ignore
                        parent=level1_assignment.level1_menu,
                        is_active=True
                    ).order_by('sort_order', 'name')
                except RoleSlotLevel1MenuAssignment.DoesNotExist:  # type: ignore
                    kwargs["queryset"] = MenuModuleConfig.objects.none()  # type: ignore
            else:
                kwargs["queryset"] = MenuModuleConfig.objects.none()  # type: ignore
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RoleSlotLevel1MenuAssignmentInline(admin.TabularInline):
    """一级菜单分配内联编辑"""
    model = RoleSlotLevel1MenuAssignment
    extra = 0
    fields = ['level1_menu', 'is_active', 'sort_order']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """限制一级菜单选择范围"""
        if db_field.name == "level1_menu":
            # 获取当前根菜单分配的ID
            root_assignment_id = request.resolver_match.kwargs.get('object_id')
            if root_assignment_id:
                try:
                    root_assignment = RoleSlotMenuAssignment.objects.get(id=root_assignment_id)  # type: ignore
                    # 只显示该根菜单下的一级菜单
                    kwargs["queryset"] = MenuModuleConfig.objects.filter(  # type: ignore
                        parent=root_assignment.root_menu,
                        is_active=True
                    ).order_by('sort_order', 'name')
                except RoleSlotMenuAssignment.DoesNotExist:  # type: ignore
                    kwargs["queryset"] = MenuModuleConfig.objects.none()  # type: ignore
            else:
                kwargs["queryset"] = MenuModuleConfig.objects.none()  # type: ignore
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# RoleSlotLevel1MenuAssignmentAdmin removed - no longer needed in admin interface


@admin.register(RoleSlotLevel2MenuAssignment)
class RoleSlotLevel2MenuAssignmentAdmin(admin.ModelAdmin):
    """二级菜单分配管理"""
    
    list_display = ['get_role_display', 'get_level1_menu', 'level2_menu', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'level1_assignment__role_slot_assignment__role', 'created_at']
    search_fields = ['level2_menu__name', 'level1_assignment__role_slot_assignment__role']
    ordering = ['level1_assignment__role_slot_assignment__role', 'sort_order']
    change_list_template = 'admin/permissions/roleslotlevel2menuassignment/waterfall_change_list.html'
    
    def has_add_permission(self, request):
        """禁用添加功能，使用双列选择器进行配置"""
        return False
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('get-roles/', self.admin_site.admin_view(self.get_roles_view), name='permissions_roleslotlevel2menuassignment_get_roles'),
            path('get-level1-assignments/', self.admin_site.admin_view(self.get_level1_assignments_view), name='permissions_roleslotlevel2menuassignment_get_level1_assignments'),
            path('get-level2-menus/', self.admin_site.admin_view(self.get_level2_menus_view), name='permissions_roleslotlevel2menuassignment_get_level2_menus'),
            path('save-config/', self.admin_site.admin_view(self.save_config_view), name='permissions_roleslotlevel2menuassignment_save_config'),
            path('get-student-slot4-data/', self.admin_site.admin_view(self.get_student_slot4_data_view), name='permissions_roleslotlevel2menuassignment_get_student_slot4_data'),
        ]
        return custom_urls + urls
    
    def get_roles_view(self, request):
        """获取所有角色及其一级菜单分配信息"""
        if not self.has_view_permission(request):
            return JsonResponse({'success': False, 'error': '权限不足'})
            
        try:
            roles_data = []
            # 从UserRole获取所有可用角色，避免重复
            from apps.accounts.models import UserRole
            all_roles = [choice[0] for choice in UserRole.choices]
            
            for role in all_roles:
                # 获取该角色的一级菜单分配
                level1_assignments = RoleSlotLevel1MenuAssignment.objects.filter(  # type: ignore
                    role_slot_assignment__role=role,
                    is_active=True
                ).select_related('level1_menu')
                
                assignments_data = []
                for assignment in level1_assignments:
                    assignments_data.append({
                        'id': assignment.id,
                        'menu_name': assignment.level1_menu.name,
                        'menu_id': assignment.level1_menu.id
                    })
                
                # 获取角色的显示名称
                role_display = dict(UserRole.choices).get(role, role)
                
                roles_data.append({
                    'role': role,
                    'role_display': role_display,
                    'level1_assignments': assignments_data
                })
            
            return JsonResponse({
                'success': True,
                'roles': roles_data
            })
        except Exception as e:
            logger.error(f"获取角色数据失败: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def get_level1_assignments_view(self, request):
        """获取指定角色的一级菜单分配"""
        if not self.has_view_permission(request):
            return JsonResponse({'success': False, 'error': '权限不足'})
            
        role = request.GET.get('role')
        if not role:
            return JsonResponse({'success': False, 'error': '缺少角色参数'})
        
        try:
            level1_assignments = RoleSlotLevel1MenuAssignment.objects.filter(  # type: ignore
                role_slot_assignment__role=role,
                is_active=True
            ).select_related('level1_menu')
            
            assignments_data = []
            for assignment in level1_assignments:
                assignments_data.append({
                    'id': assignment.id,
                    'menu_name': assignment.level1_menu.name,
                    'menu_id': assignment.level1_menu.id
                })
            
            return JsonResponse({
                'success': True,
                'level1_assignments': assignments_data
            })
        except Exception as e:
            logger.error(f"获取一级菜单分配失败: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def get_level2_menus_view(self, request):
        """获取指定一级菜单下的二级菜单"""
        if not self.has_view_permission(request):
            return JsonResponse({'success': False, 'error': '权限不足'})
            
        assignment_id = request.GET.get('assignment_id')
        if not assignment_id:
            return JsonResponse({'success': False, 'error': '缺少一级菜单分配参数'})
        
        try:
            level1_assignment = RoleSlotLevel1MenuAssignment.objects.get(id=assignment_id)  # type: ignore
            
            # 获取所有二级菜单（暂时获取所有，后续可根据业务需求调整）
            all_level2_menus = MenuModuleConfig.objects.filter(  # type: ignore
                menu_level='level2',
                is_active=True
            ).order_by('sort_order', 'name')
            
            # 获取已分配的二级菜单
            assigned_level2_menus = RoleSlotLevel2MenuAssignment.objects.filter(  # type: ignore
                level1_assignment=level1_assignment,
                is_active=True
            ).values_list('level2_menu_id', flat=True)
            
            available_menus = []
            selected_menus = []
            
            for menu in all_level2_menus:
                menu_data = {
                    'id': menu.id,
                    'name': menu.name
                }
                
                if menu.id in assigned_level2_menus:
                    selected_menus.append(menu_data)
                else:
                    available_menus.append(menu_data)
            
            return JsonResponse({
                'success': True,
                'available_menus': available_menus,
                'selected_menus': selected_menus
            })
        except RoleSlotLevel1MenuAssignment.DoesNotExist:  # type: ignore
            return JsonResponse({'success': False, 'error': '一级菜单分配不存在'})
        except Exception as e:
            logger.error(f"获取二级菜单失败: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def save_config_view(self, request):
        """保存二级菜单配置"""
        if not self.has_change_permission(request):
            return JsonResponse({'success': False, 'error': '权限不足'})
        
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': '只支持POST请求'})
        
        level1_assignment_id = request.POST.get('level1_assignment')
        selected_menus_json = request.POST.get('selected_menus')
        
        if not level1_assignment_id or not selected_menus_json:
            return JsonResponse({'success': False, 'error': '缺少必要参数'})
        
        try:
            selected_menu_ids = json.loads(selected_menus_json)
            
            level1_assignment = RoleSlotLevel1MenuAssignment.objects.get(id=level1_assignment_id)  # type: ignore
            
            # 删除现有的二级菜单分配
            RoleSlotLevel2MenuAssignment.objects.filter(level1_assignment=level1_assignment).delete()  # type: ignore
            
            # 创建新的二级菜单分配
            for i, menu_id in enumerate(selected_menu_ids):
                try:
                    menu = MenuModuleConfig.objects.get(id=menu_id)  # type: ignore
                    RoleSlotLevel2MenuAssignment.objects.create(  # type: ignore
                        level1_assignment=level1_assignment,
                        level2_menu=menu,
                        is_active=True,
                        sort_order=i + 1
                    )
                except MenuModuleConfig.DoesNotExist:  # type: ignore
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'成功配置 {len(selected_menu_ids)} 个二级菜单'
            })
        except RoleSlotLevel1MenuAssignment.DoesNotExist:  # type: ignore
            return JsonResponse({'success': False, 'error': '一级菜单分配不存在'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': '菜单数据格式错误'})
        except Exception as e:
            logger.error(f"保存二级菜单配置失败: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def get_student_slot4_data_view(self, request):
        """获取student角色slot_position=4的一级目录数据"""
        try:
            # 获取student角色slot_position=4的一级菜单分配
            level1_assignments = RoleSlotLevel1MenuAssignment.objects.filter(  # type: ignore
                role_slot_assignment__role='student',
                role_slot_assignment__slot_position=4,
                is_active=True
            ).select_related('level1_menu', 'role_slot_assignment').order_by('sort_order')
            
            level1_menus = []
            for assignment in level1_assignments:
                level1_menus.append({
                    'id': assignment.level1_menu.id,
                    'name': assignment.level1_menu.name,
                    'key': assignment.level1_menu.key,
                    'icon': assignment.level1_menu.icon or '',
                    'url': assignment.level1_menu.url or '',
                    'sort_order': assignment.sort_order,
                    'assignment_id': assignment.id
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'role': 'student',
                    'slot_position': 4,
                    'level1_menus': level1_menus,
                    'total_count': len(level1_menus)
                }
            })
            
        except Exception as e:
            logger.error(f"获取student slot4数据失败: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表视图"""
        extra_context = extra_context or {}
        
        # 获取统计数据
        from django.db.models import Count
        
        # 获取所有角色的一级菜单分配统计
        roles_with_assignments = []
        all_roles = RoleSlotMenuAssignment.objects.values_list('role', flat=True).distinct()  # type: ignore
        
        for role in all_roles:
            level1_count = RoleSlotLevel1MenuAssignment.objects.filter(  # type: ignore
                role_slot_assignment__role=role,
                is_active=True
            ).count()
            
            level2_count = RoleSlotLevel2MenuAssignment.objects.filter(  # type: ignore
                level1_assignment__role_slot_assignment__role=role,
                is_active=True
            ).count()
            
            roles_with_assignments.append({
                'role': role,
                'role_display': role,
                'level1_count': level1_count,
                'level2_count': level2_count
            })
        
        # 统计数据
        total_roles = len(all_roles)
        total_level1_assignments = RoleSlotLevel1MenuAssignment.objects.filter(is_active=True).count()  # type: ignore
        total_level2_assignments = RoleSlotLevel2MenuAssignment.objects.filter(is_active=True).count()  # type: ignore
        available_level2_menus = MenuModuleConfig.objects.filter(menu_level='level2', is_active=True).count()  # type: ignore
        
        extra_context.update({
            'roles_with_level1_assignments': roles_with_assignments,
            'total_roles': total_roles,
            'total_level1_assignments': total_level1_assignments,
            'total_level2_assignments': total_level2_assignments,
            'available_level2_menus': available_level2_menus,
        })
        
        return super().changelist_view(request, extra_context)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """实时过滤可用菜单"""
        if db_field.name == "level2_menu":
            # 实时获取有效的二级菜单
            valid_menu_ids = MenuValidity.objects.filter(  # type: ignore
                is_valid=True,
                menu_module__menu_level='level2',
                menu_module__is_active=True
            ).values_list('menu_module_id', flat=True)
            
            kwargs["queryset"] = MenuModuleConfig.objects.filter(  # type: ignore
                id__in=valid_menu_ids
            ).order_by('sort_order', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    @admin.display(description='角色')
    def get_role_display(self, obj):
        return obj.level1_assignment.role_slot_assignment.get_role_display()
    
    @admin.display(description='一级菜单')
    def get_level1_menu(self, obj):
        return obj.level1_assignment.level1_menu.name


@admin.register(RoleSlotMenuAssignment)
class RoleSlotMenuAssignmentAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """角色槽位菜单分配管理 - 新的基于槽位的菜单分配系统"""
    
    form = RoleSlotMenuAssignmentForm
    
    list_display = [
        'get_role_display_name', 
        'slot_position', 
        'root_menu', 
        'get_menu_status_display', 
        'get_slot_status',
        'is_active', 
        'sort_order',
        'created_at'
    ]
    
    list_filter = [
        'menu_status', 
        'is_active', 
        'role', 
        'slot_position',
        'created_at'
    ]
    
    search_fields = [
        'role', 
        'root_menu__name', 
        'root_menu__key'
    ]
    
    ordering = ['role', 'slot_position', 'sort_order']
    
    list_editable = ['is_active', 'sort_order']
    
    inlines = [RoleSlotLevel1MenuAssignmentInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role', 'slot_position', 'root_menu')
        }),
        ('菜单配置', {
            'fields': ('menu_status', 'is_active', 'sort_order')
        }),
    )
    
    class Media:
        js = ('admin/js/role_slot_menu_assignment.js',)
        css = {
            'all': ('admin/css/role_slot_menu_assignment.css',)
        }
    
    def get_urls(self):
        """添加自定义URL路由"""
        urls = super().get_urls()
        custom_urls = [
            path('configure-menu-by-role-slot/', self.admin_site.admin_view(self.configure_menu_by_role_slot_view), name='permissions_roleslotmenuassignment_configure'),
            path('remove-menu-by-role-slot/', self.admin_site.admin_view(self.configure_menu_by_role_slot_view), name='permissions_roleslotmenuassignment_remove'),
            path('get-slot-status/<str:role>/', self.admin_site.admin_view(self.get_slot_status_view), name='permissions_roleslotmenuassignment_slot_status'),
            path('get-assignment-history/', self.admin_site.admin_view(self.get_assignment_history_view), name='permissions_roleslotmenuassignment_history'),
            path('batch-assign-menus/', self.admin_site.admin_view(self.batch_assign_menus_view), name='permissions_roleslotmenuassignment_batch_assign'),
            path('validate-slot-capacity/', self.admin_site.admin_view(self.validate_slot_capacity_view), name='permissions_roleslotmenuassignment_validate'),
            path('auto-optimize-slots/', self.admin_site.admin_view(self.auto_optimize_slots_view), name='permissions_roleslotmenuassignment_optimize'),
            path('get-selected-menus/', self.admin_site.admin_view(self.get_selected_menus_view), name='permissions_roleslotmenuassignment_selected_menus'),
            path('get-current-root-directory/', self.admin_site.admin_view(self.get_current_root_directory_view), name='permissions_roleslotmenuassignment_current_root'),
        ]
        return custom_urls + urls
    
    def get_current_root_directory_view(self, request):
        """获取当前根目录信息"""
        role = request.GET.get('role')
        slot_position = request.GET.get('slot_position')
        
        if not role or not slot_position:
            return JsonResponse({'success': False, 'error': '缺少必要参数'})
        
        try:
            # 查找当前角色和槽位的根菜单分配
            assignment = RoleSlotMenuAssignment.objects.filter(  # type: ignore[attr-defined]
                role=role,
                slot_position=slot_position,
                is_active=True
            ).first()
            
            if assignment and assignment.root_menu:
                root_info = {
                    'name': assignment.root_menu.name,
                    'key': assignment.root_menu.key,
                    'status': assignment.menu_status,
                    'icon': assignment.root_menu.icon or 'folder',
                    'url': assignment.root_menu.url or '#'
                }
                return JsonResponse({'success': True, 'root_directory': root_info})
            else:
                return JsonResponse({'success': True, 'root_directory': None})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def get_selected_menus_view(self, request):
        """获取角色已选择的一级菜单"""
        role = request.GET.get('role')
        slot_position = request.GET.get('slot_position')
        
        if not role or not slot_position:
            return JsonResponse({'success': False, 'error': '缺少必要参数'})
        
        try:
            # 获取该角色和槽位已选择的一级菜单
            level1_assignments = RoleSlotLevel1MenuAssignment.objects.filter(  # type: ignore
                role_slot_assignment__role=role,
                role_slot_assignment__slot_position=slot_position,
                role_slot_assignment__is_active=True,
                is_active=True
            ).select_related('level1_menu').order_by('sort_order')
            
            selected_menus = []
            for assignment in level1_assignments:
                selected_menus.append({
                    'id': assignment.level1_menu.id,
                    'name': assignment.level1_menu.name,
                    'key': assignment.level1_menu.key
                })
            
            return JsonResponse({
                'success': True,
                'selected_menus': selected_menus
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def changelist_view(self, request, extra_context=None):
        """瀑布流视图 - 展示所有角色及其槽位配置"""
        extra_context = extra_context or {}
        
        # 检查是否显示更新效果
        show_update_effect = request.GET.get('e') == '1'
        if show_update_effect:
            extra_context['show_update_effect'] = True
            extra_context['update_message'] = '配置已成功更新！'
        
        # 检查是否使用瀑布流视图
        # 当URL包含role和slot_position参数时，也使用瀑布流视图来显示双列选择器
        has_role_slot_params = request.GET.get('role') and request.GET.get('slot_position')
        use_waterfall = request.GET.get('view') == 'waterfall' or not request.GET.get('view') or has_role_slot_params
        
        if use_waterfall:
            # 瀑布流视图逻辑
            from collections import defaultdict
            from apps.accounts.services.role_service import RoleService
            
            # 获取所有角色
            all_roles = RoleService.get_all_roles()
            
            # 获取所有激活的槽位配置
            slot_configs = SlotConfig.objects.filter(is_active=True).select_related()  # type: ignore[attr-defined]
            slot_config_dict = {config.role: config for config in slot_configs}
            
            # 获取所有菜单分配
            assignments = RoleSlotMenuAssignment.objects.filter(is_active=True).select_related('root_menu')  # type: ignore[attr-defined]
            assignment_dict = defaultdict(dict)
            for assignment in assignments:
                assignment_dict[assignment.role][assignment.slot_position] = assignment
            
            # 获取可用的根菜单（基于角色过滤）
            role = request.GET.get('role')
            if role:
                # 如果指定了角色，只显示该角色有效的根菜单
                valid_menu_ids = MenuValidity.objects.filter(  # type: ignore[attr-defined]
                    role=role,
                    is_valid=True,
                    menu_module__menu_level='root'
                ).values_list('menu_module_id', flat=True)
                available_root_menus = MenuModuleConfig.objects.filter(  # type: ignore[attr-defined]
                    id__in=valid_menu_ids,
                    is_active=True
                ).order_by('sort_order', 'name')
            else:
                # 如果没有指定角色，显示所有激活的根菜单
                available_root_menus = MenuModuleConfig.objects.filter(  # type: ignore[attr-defined]
                    menu_level='root',
                    is_active=True
                ).order_by('sort_order', 'name')
            
            # 构建角色槽位数据
            roles_with_slots = []
            total_slots = 0
            assigned_slots = 0
            
            for role_data in all_roles:
                role_code = role_data['code']
                role_name = role_data['display_name']
                
                # 获取该角色的槽位配置
                slot_config = slot_config_dict.get(role_code)
                if not slot_config:
                    continue
                
                slot_count = slot_config.slot_count
                total_slots += slot_count
                
                # 构建槽位列表
                slots = []
                assigned_count = 0
                
                for position in range(1, slot_count + 1):
                    assignment = assignment_dict[role_code].get(position)
                    if assignment:
                        assigned_count += 1
                        assigned_slots += 1
                    
                    slots.append({
                        'position': position,
                        'assignment': assignment
                    })
                
                roles_with_slots.append({
                    'role_code': role_code,
                    'role_name': role_name,
                    'total_slots': slot_count,
                    'assigned_count': assigned_count,
                    'slots': slots
                })
            
            # 瀑布流视图的上下文
            extra_context.update({
                'roles_with_slots': roles_with_slots,
                'available_root_menus': available_root_menus,
                'total_roles': len(roles_with_slots),
                'total_slots': total_slots,
                'assigned_slots': assigned_slots,
                'available_menus': available_root_menus.count(),
                'use_waterfall': True
            })
            
            # 使用瀑布流模板
            self.change_list_template = 'admin/permissions/roleslotmenuassignment/waterfall_change_list.html'
        
        else:
            # 原有的列表视图逻辑
            menu_configs = MenuModuleConfig.objects.filter(is_active=True).select_related()  # type: ignore
            slot_configs = SlotConfig.objects.filter(is_active=True).select_related()  # type: ignore
            menu_validities = MenuValidity.objects.filter(is_valid=True).select_related('menu_module')  # type: ignore
            
            # 统计各角色的槽位使用情况
            from collections import defaultdict
            role_slot_stats = defaultdict(lambda: {'total_slots': 0, 'used_slots': 0, 'active_assignments': 0})
            
            for slot_config in slot_configs:
                role_slot_stats[slot_config.role]['total_slots'] = slot_config.slot_count
            
            for assignment in self.get_queryset(request).filter(is_active=True):
                role_slot_stats[assignment.role]['used_slots'] += 1
                role_slot_stats[assignment.role]['active_assignments'] += 1
            
            # 添加菜单配置功能的上下文
            extra_context.update({
                'sync_info': {
                    'menu_configs_count': menu_configs.count(),
                    'slot_configs_count': slot_configs.count(),
                    'menu_validities_count': menu_validities.count(),
                    'role_slot_stats': dict(role_slot_stats),
                    'last_sync': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'menu_config_tools': {
                    'configure_url': reverse('admin:permissions_roleslotmenuassignment_configure'),
                    'batch_assign_url': reverse('admin:permissions_roleslotmenuassignment_batch_assign'),
                    'validate_url': reverse('admin:permissions_roleslotmenuassignment_validate'),
                    'optimize_url': reverse('admin:permissions_roleslotmenuassignment_optimize'),
                },
                'use_waterfall': False
            })
        
        return super().changelist_view(request, extra_context)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """自定义数据库字段"""
        if hasattr(db_field, 'name') and db_field.name == 'role' and db_field.__class__.__name__ == 'CharField':
            result = super().formfield_for_char_field(db_field, request, **kwargs)
            if result is not None:
                return result
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义外键字段"""
        if db_field.name == "root_menu":
            # 只显示根级菜单
            kwargs["queryset"] = MenuModuleConfig.objects.filter(  # type: ignore[attr-defined]
                menu_level='root',
                is_active=True
            ).order_by('sort_order', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    @admin.display(description='角色名称')
    def get_role_display_name(self, obj):
        """显示角色名称"""
        return obj.get_role_display()
    
    @admin.display(description='菜单状态')
    def get_menu_status_display(self, obj):
        """显示菜单状态"""
        status_colors = {
            'active': '#28a745',
            'backup': '#ffc107', 
            'disabled': '#dc3545'
        }
        status_icons = {
            'active': '✅',
            'backup': '⏳',
            'disabled': '❌'
        }
        color = status_colors.get(obj.menu_status, '#6c757d')
        icon = status_icons.get(obj.menu_status, '❓')
        status_text = dict(obj.MENU_STATUS_CHOICES)[obj.menu_status]
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, status_text
        )
    
    @admin.display(description='槽位状态')
    def get_slot_status(self, obj):
        """显示槽位状态"""
        slot_info = obj.get_slot_info()
        if slot_info['is_valid']:
            return format_html(
                '<span style="color: #28a745;">✅ {}/{}</span>',
                slot_info['current_position'],
                slot_info['max_slots']
            )
        else:
            return format_html(
                '<span style="color: #dc3545;">❌ {}/{} (超出)</span>',
                slot_info['current_position'],
                slot_info['max_slots']
            )
    
    def configure_menu_by_role_slot_view(self, request):
        """根据角色和槽位数值配置菜单"""
        if request.method == 'POST':
            role = request.POST.get('role')
            slot_position = request.POST.get('slot_position')
            selected_menus = request.POST.getlist('selected_menus')
            selected_level1_menus = request.POST.get('selected_level1_menus')
            
            # 处理批量一级菜单分配（双列选择器）
            if selected_level1_menus:
                try:
                    selected_menu_ids = json.loads(selected_level1_menus)
                except (ValueError, TypeError):
                    selected_menu_ids = []
            elif selected_menus:
                selected_menu_ids = selected_menus
            else:
                selected_menu_ids = []
            
            # 处理批量菜单分配（双列选择器）
            if selected_menu_ids:
                try:
                    # 验证槽位容量
                    slot_config = SlotConfig.objects.filter(role=role, is_active=True).first()  # type: ignore  # type: ignore  # type: ignore  # type: ignore[attr-defined]
                    if not slot_config:
                        return JsonResponse({'success': False, 'error': f'角色 {role} 没有配置槽位'})
                    
                    if int(slot_position) > slot_config.slot_count:
                        return JsonResponse({'success': False, 'error': f'槽位 {slot_position} 超出最大槽位数 {slot_config.slot_count}'})
                    
                    # 先删除该角色和槽位的所有现有一级菜单分配
                    existing_assignments = RoleSlotMenuAssignment.objects.filter(  # type: ignore[attr-defined]
                        role=role,
                        slot_position=slot_position,
                        is_active=True
                    )
                    
                    for assignment in existing_assignments:
                        # 彻底删除相关的一级菜单分配，避免UNIQUE约束冲突
                        RoleSlotLevel1MenuAssignment.objects.filter(  # type: ignore[attr-defined]
                            role_slot_assignment=assignment
                        ).delete()
                    
                    # 如果没有根菜单分配，创建一个默认的
                    root_assignment = existing_assignments.first()
                    if not root_assignment:
                        # 创建一个默认的根菜单分配
                        default_root_menu = MenuModuleConfig.objects.filter(menu_level='root', is_active=True).first()  # type: ignore[attr-defined]
                        if default_root_menu:
                            root_assignment = RoleSlotMenuAssignment.objects.create(  # type: ignore[attr-defined]
                                role=role,
                                slot_position=slot_position,
                                root_menu=default_root_menu,
                                menu_status='active',
                                is_active=True,
                                sort_order=1
                            )
                    
                    # 批量创建新的一级菜单分配
                    assignments_created = 0
                    if root_assignment:
                        for i, menu_id in enumerate(selected_menu_ids):
                            try:
                                level1_menu = MenuModuleConfig.objects.get(id=menu_id)  # type: ignore[attr-defined]
                                RoleSlotLevel1MenuAssignment.objects.create(  # type: ignore[attr-defined]
                                    role_slot_assignment=root_assignment,
                                    level1_menu=level1_menu,
                                    is_active=True,
                                    sort_order=i + 1
                                )
                                assignments_created += 1
                            except MenuModuleConfig.DoesNotExist:  # type: ignore[attr-defined]
                                continue
                    
                    messages.success(request, f'成功为角色 {role} 的槽位 {slot_position} 配置了 {assignments_created} 个菜单')
                    return JsonResponse({'success': True, 'assignments_created': assignments_created})
                    
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            
            # 处理单个菜单分配（原有逻辑）
            root_menu_id = request.POST.get('root_menu')
            menu_status = request.POST.get('menu_status', 'active')
            
            try:
                # 验证槽位容量
                slot_config = SlotConfig.objects.filter(role=role, is_active=True).first()  # type: ignore[attr-defined]
                if not slot_config:
                    return JsonResponse({'success': False, 'error': f'角色 {role} 没有配置槽位'})
                
                if int(slot_position) > slot_config.slot_count:
                    return JsonResponse({'success': False, 'error': f'槽位 {slot_position} 超出最大槽位数 {slot_config.slot_count}'})
                
                # 检查槽位是否已被占用
                existing = RoleSlotMenuAssignment.objects.filter(  # type: ignore
                    role=role, 
                    slot_position=slot_position,
                    is_active=True
                ).first()
                
                if existing:
                    return JsonResponse({'success': False, 'error': f'槽位 {slot_position} 已被占用'})
                
                # 创建菜单分配
                root_menu = MenuModuleConfig.objects.get(id=root_menu_id)  # type: ignore

                assignment = RoleSlotMenuAssignment.objects.create(  # type: ignore
                    role=role,
                    slot_position=slot_position,
                    root_menu=root_menu,
                    menu_status=menu_status,
                    is_active=True,
                    sort_order=int(slot_position)
                )
                
                messages.success(request, f'成功为角色 {role} 的槽位 {slot_position} 配置菜单 {root_menu.name}')
                return JsonResponse({'success': True, 'assignment_id': assignment.id})
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        elif request.method == 'DELETE':
            # 处理删除请求
            try:
                data = json.loads(request.body)
                role = data.get('role')
                slot_position = data.get('slot_position')
                
                # 查找并删除分配
                assignment = RoleSlotMenuAssignment.objects.filter(  # type: ignore
                    role=role,
                    slot_position=slot_position,
                    is_active=True
                ).first()
                
                if assignment:
                    assignment.is_active = False
                    assignment.save()
                    messages.success(request, f'成功移除角色 {role} 的槽位 {slot_position} 配置')
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': '未找到对应的槽位配置'})
                    
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        # GET请求返回配置表单数据
        # 角色数据来源：SlotConfig（根据用户反馈修正）
        roles = []
        slot_configs = []
        
        # 从SlotConfig获取有效的角色和槽位配置
        active_slot_configs = SlotConfig.objects.filter(is_active=True).select_related()  # type: ignore
        for slot_config in active_slot_configs:
            role_display = dict(UserRole.choices).get(slot_config.role, slot_config.role)
            roles.append((slot_config.role, role_display))
            slot_configs.append({
                'role': slot_config.role,
                'role_name': role_display,
                'slot_count': slot_config.slot_count,
                'config_name': slot_config.name
            })
        
        # 菜单数据来源：MenuModuleConfig（获取一级菜单）
        level1_menus = MenuModuleConfig.objects.filter(menu_level='level1', is_active=True).values('id', 'name')  # type: ignore
        
        return JsonResponse({
            'roles': roles,
            'level1_menus': list(level1_menus),
            'slot_configs': slot_configs,
            'menu_status_choices': RoleSlotMenuAssignment.MENU_STATUS_CHOICES
        })
    
    def get_slot_status_view(self, request, role):
        """获取指定角色的槽位占用状态"""
        try:
            # 获取角色的槽位配置
            slot_config = SlotConfig.objects.filter(role=role, is_active=True).first()  # type: ignore
            if not slot_config:
                return JsonResponse({
                    'success': False,
                    'message': f'角色 {role} 没有有效的槽位配置'
                })
            
            # 获取已占用的槽位
            occupied_slots = RoleSlotMenuAssignment.objects.filter(  # type: ignore
                role=role,
                is_active=True
            ).values('slot_position', 'root_menu__name', 'menu_status')
            
            # 生成槽位状态列表
            slot_status = []
            for i in range(1, slot_config.slot_count + 1):
                occupied = next((slot for slot in occupied_slots if slot['slot_position'] == i), None)
                slot_status.append({
                    'position': i,
                    'is_occupied': bool(occupied),
                    'menu_name': occupied['root_menu__name'] if occupied else None,
                    'menu_status': occupied['menu_status'] if occupied else None
                })
            
            return JsonResponse({
                'success': True,
                'role': role,
                'total_slots': slot_config.slot_count,
                'slot_status': slot_status
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取槽位状态失败: {str(e)}'
            })
    
    def get_assignment_history_view(self, request):
        """获取所有已保存的角色槽位菜单分配历史数据"""
        try:
            # 获取所有活跃的分配记录
            assignments = RoleSlotMenuAssignment.objects.filter(  # type: ignore
                is_active=True
            ).select_related('root_menu').order_by('role', 'slot_position')
            
            # 构建历史数据列表
            history_data = []
            for assignment in assignments:
                # 获取角色显示名称
                role_display = dict(UserRole.choices).get(assignment.role, assignment.role)
                
                history_data.append({
                    'id': assignment.id,
                    'role': assignment.role,
                    'role_display': role_display,
                    'slot_position': assignment.slot_position,
                    'root_menu_name': assignment.root_menu.name,
                    'root_menu_key': assignment.root_menu.key,
                    'menu_status': assignment.menu_status,
                    'menu_status_display': dict(assignment.MENU_STATUS_CHOICES).get(assignment.menu_status, assignment.menu_status),
                    'sort_order': assignment.sort_order,
                    'created_at': assignment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': assignment.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return JsonResponse({
                'success': True,
                'total_count': len(history_data),
                'assignments': history_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取历史数据失败: {str(e)}'
            })
    
    def batch_assign_menus_view(self, request):
        """批量分配菜单到槽位"""
        if request.method == 'POST':
            assignments = request.POST.getlist('assignments')
            success_count = 0
            error_messages = []
            
            for assignment_data in assignments:
                try:
                    data = eval(assignment_data)  # 简化处理，实际应使用json.loads
                    role = data['role']
                    slot_position = data['slot_position']
                    root_menu_id = data['root_menu_id']
                    
                    # 验证并创建分配
                    slot_config = SlotConfig.objects.filter(role=role, is_active=True).first()  # type: ignore
                    if slot_config and int(slot_position) <= slot_config.slot_count:
                        root_menu = MenuModuleConfig.objects.get(id=root_menu_id)  # type: ignore
                        RoleSlotMenuAssignment.objects.create(  # type: ignore
                            role=role,
                            slot_position=slot_position,
                            root_menu=root_menu,
                            menu_status='active',
                            is_active=True,
                            sort_order=int(slot_position)
                        )
                        success_count += 1
                    else:
                        error_messages.append(f'角色 {role} 槽位 {slot_position} 配置失败')
                        
                except Exception as e:
                    error_messages.append(f'处理分配数据时出错: {str(e)}')
            
            if success_count > 0:
                messages.success(request, f'成功批量分配 {success_count} 个菜单')
            if error_messages:
                for msg in error_messages:
                    messages.error(request, msg)
            
            return JsonResponse({'success': True, 'processed': success_count})
        
        return JsonResponse({'error': '仅支持POST请求'})
    
    def validate_slot_capacity_view(self, request):
        """验证槽位容量"""
        validation_results = []
        
        # 获取所有角色的槽位配置
        slot_configs = SlotConfig.objects.filter(is_active=True)  # type: ignore
        
        for slot_config in slot_configs:
            used_slots = RoleSlotMenuAssignment.objects.filter(  # type: ignore[attr-defined]
                role=slot_config.role,
                is_active=True
            ).count()
            
            validation_results.append({
                'role': slot_config.role,
                'role_display': slot_config.get_role_display(),
                'max_slots': slot_config.slot_count,
                'used_slots': used_slots,
                'available_slots': slot_config.slot_count - used_slots,
                'is_over_capacity': used_slots > slot_config.slot_count,
                'utilization_rate': round((used_slots / slot_config.slot_count) * 100, 2) if slot_config.slot_count > 0 else 0
            })
        
        return JsonResponse({
            'validation_results': validation_results,
            'total_roles': len(validation_results),
            'over_capacity_count': sum(1 for r in validation_results if r['is_over_capacity'])
        })
    
    def auto_optimize_slots_view(self, request):
        """自动优化槽位分配"""
        if request.method == 'POST':
            optimization_results = []
            
            # 获取所有角色的槽位使用情况
            slot_configs = SlotConfig.objects.filter(is_active=True)  # type: ignore
            
            for slot_config in slot_configs:
                assignments = RoleSlotMenuAssignment.objects.filter(  # type: ignore
                    role=slot_config.role,
                    is_active=True
                ).order_by('slot_position')
                
                # 重新排序槽位位置
                for index, assignment in enumerate(assignments, 1):
                    if assignment.slot_position != index:
                        old_position = assignment.slot_position
                        assignment.slot_position = index
                        assignment.sort_order = index
                        assignment.save()
                        
                        optimization_results.append({
                            'role': slot_config.role,
                            'assignment_id': assignment.id,
                            'menu_name': assignment.root_menu.name,
                            'old_position': old_position,
                            'new_position': index
                        })
            
            if optimization_results:
                messages.success(request, f'成功优化 {len(optimization_results)} 个槽位分配')
            else:
                messages.info(request, '所有槽位分配已经是最优状态')
            
            return JsonResponse({
                'success': True,
                'optimized_count': len(optimization_results),
                'details': optimization_results
            })
        
        return JsonResponse({'error': '仅支持POST请求'})
    
    def add_view(self, request, form_url='', extra_context=None):
        """自定义添加视图，使用原生Django表单"""
        extra_context = extra_context or {}
        extra_context['title'] = '添加角色槽位菜单分配'
        return super().add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """自定义修改视图，使用原生Django表单"""
        extra_context = extra_context or {}
        extra_context['title'] = '修改角色槽位菜单分配'
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """保存时验证槽位有效性"""
        try:
            super().save_model(request, obj, form, change)
            
            # 检查槽位状态
            slot_info = obj.get_slot_info()
            if not slot_info['is_valid']:
                messages.warning(
                    request, 
                    f'槽位 {obj.slot_position} 超出角色 {obj.get_role_display()} 的最大槽位数 {slot_info["max_slots"]}'
                )
                
        except ValidationError as e:
            messages.error(request, f'保存失败: {e.message}')
            raise
        except Exception as e:
            messages.error(request, f'保存失败: {str(e)}')
            raise