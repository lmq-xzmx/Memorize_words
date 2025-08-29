from django.contrib import admin
from django.utils.html import format_html
from django.http import JsonResponse
from django.urls import path
from django.core.exceptions import ValidationError
from django.contrib import messages
from apps.accounts.services.role_service import RoleService
from .models import SlotConfig, MenuModuleConfig, FrontendMenuConfig
from .models_slot_menu import (
    RoleSlotMenuAssignment,
    RoleSlotLevel1MenuAssignment,
    RoleSlotLevel2MenuAssignment
)
from .widgets import StandardRoleSelectWidget
from .role_selector_config import StandardRoleAdminMixin


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
                    level1_assignment = RoleSlotLevel1MenuAssignment.objects.get(id=level1_assignment_id)
                    # 只显示该一级菜单下的二级菜单
                    kwargs["queryset"] = MenuModuleConfig.objects.filter(
                        parent=level1_assignment.level1_menu,
                        is_active=True
                    ).order_by('sort_order', 'name')
                except RoleSlotLevel1MenuAssignment.DoesNotExist:
                    kwargs["queryset"] = MenuModuleConfig.objects.none()
            else:
                kwargs["queryset"] = MenuModuleConfig.objects.none()
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
                    root_assignment = RoleSlotMenuAssignment.objects.get(id=root_assignment_id)
                    # 只显示该根菜单下的一级菜单
                    kwargs["queryset"] = MenuModuleConfig.objects.filter(
                        parent=root_assignment.root_menu,
                        is_active=True
                    ).order_by('sort_order', 'name')
                except RoleSlotMenuAssignment.DoesNotExist:
                    kwargs["queryset"] = FrontendMenuConfig.objects.none()
            else:
                kwargs["queryset"] = FrontendMenuConfig.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# RoleSlotLevel1MenuAssignment 的 Admin 类已在 admin.py 中定义，避免重复注册


# RoleSlotLevel2MenuAssignment 的 Admin 类已在 admin.py 中定义，避免重复注册


@admin.register(RoleSlotMenuAssignment)
class RoleSlotMenuAssignmentAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
    """角色槽位菜单分配管理 - 新的基于槽位的菜单分配系统"""
    
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
        'root_menu__menu_type',
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
            kwargs["queryset"] = FrontendMenuConfig.objects.filter(
                parent__isnull=True,
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
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('get-roles-list/', self.admin_site.admin_view(self.get_roles_list_view), name='get_roles_list'),
            path('get-slot-info/', self.admin_site.admin_view(self.get_slot_info_view), name='get_slot_info'),
            path('get-available-menus/', self.admin_site.admin_view(self.get_available_menus_view), name='get_available_menus'),
            path('bulk-create-assignments/', self.admin_site.admin_view(self.bulk_create_assignments_view), name='bulk_create_assignments'),
        ]
        return custom_urls + urls
    
    def get_roles_list_view(self, request):
        """获取所有角色列表API"""
        try:
            roles = RoleService.get_all_roles()
            role_list = []
            
            for role_data in roles:
                role_code = role_data['code']
                role_name = role_data['display_name']
                
                # 获取该角色的槽位配置
                slot_count = SlotConfig.get_slot_count_for_role(role_code)
                
                # 获取该角色已分配的槽位数量
                assigned_slots = RoleSlotMenuAssignment.objects.filter(
                    role=role_code,
                    is_active=True
                ).values('slot_position').distinct().count()
                
                role_list.append({
                    'code': role_code,
                    'name': role_name,
                    'slot_count': slot_count,
                    'assigned_slots': assigned_slots,
                    'available_slots': slot_count - assigned_slots
                })
            
            return JsonResponse({
                'success': True,
                'roles': role_list,
                'total': len(role_list)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def get_slot_info_view(self, request):
        """获取指定角色的槽位信息API"""
        role = request.GET.get('role')
        if not role:
            return JsonResponse({'success': False, 'error': '缺少角色参数'})
        
        try:
            slot_count = SlotConfig.get_slot_count_for_role(role)
            
            # 获取已分配的槽位
            assignments = RoleSlotMenuAssignment.objects.filter(
                role=role,
                is_active=True
            ).order_by('slot_position')
            
            slot_info = []
            for i in range(1, slot_count + 1):
                slot_assignments = assignments.filter(slot_position=i)
                slot_data = {
                    'position': i,
                    'assignments': []
                }
                
                for assignment in slot_assignments:
                    slot_data['assignments'].append({
                        'id': assignment.id,
                        'root_menu': assignment.root_menu.name,
                        'menu_status': assignment.menu_status,
                        'sort_order': assignment.sort_order
                    })
                
                slot_info.append(slot_data)
            
            return JsonResponse({
                'success': True,
                'role': role,
                'slot_count': slot_count,
                'slots': slot_info
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def get_available_menus_view(self, request):
        """获取可用菜单列表API"""
        menu_level = request.GET.get('level', 'root')
        parent_id = request.GET.get('parent_id')
        
        try:
            if menu_level == 'root':
                # 获取根菜单
                menus = FrontendMenuConfig.objects.filter(
                    parent__isnull=True,
                    is_active=True
                ).order_by('sort_order', 'name')
            else:
                # 获取子菜单
                if not parent_id:
                    return JsonResponse({'success': False, 'error': '缺少父菜单ID'})
                
                menus = FrontendMenuConfig.objects.filter(
                    parent_id=parent_id,
                    is_active=True
                ).order_by('sort_order', 'name')
            
            menu_list = []
            for menu in menus:
                menu_list.append({
                    'id': menu.id,
                    'name': menu.name,
                    'key': menu.key,
                    'icon': menu.icon,
                    'url': menu.url,
                    'sort_order': menu.sort_order
                })
            
            return JsonResponse({
                'success': True,
                'menus': menu_list,
                'level': menu_level,
                'parent_id': parent_id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def bulk_create_assignments_view(self, request):
        """批量创建槽位分配API"""
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': '仅支持POST请求'})
        
        try:
            import json
            data = json.loads(request.body)
            role = data.get('role')
            assignments = data.get('assignments', [])
            
            if not role or not assignments:
                return JsonResponse({'success': False, 'error': '缺少必要参数'})
            
            created_count = 0
            errors = []
            
            for assignment_data in assignments:
                try:
                    assignment = RoleSlotMenuAssignment(
                        role=role,
                        slot_position=assignment_data['slot_position'],
                        root_menu_id=assignment_data['root_menu_id'],
                        menu_status=assignment_data.get('menu_status', 'active'),
                        is_active=assignment_data.get('is_active', True),
                        sort_order=assignment_data.get('sort_order', 0)
                    )
                    assignment.full_clean()
                    assignment.save()
                    created_count += 1
                except ValidationError as e:
                    errors.append(f"槽位{assignment_data['slot_position']}: {e.message}")
                except Exception as e:
                    errors.append(f"槽位{assignment_data['slot_position']}: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'created_count': created_count,
                'errors': errors,
                'message': f'成功创建 {created_count} 个槽位分配'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
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