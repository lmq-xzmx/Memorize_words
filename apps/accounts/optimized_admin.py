from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse, path
from django.db import models
from django.contrib.auth.models import Group
from django import forms
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.template.response import TemplateResponse
from .models import CustomUser, UserLoginLog, UserRole, LearningProfile, RoleApproval, RoleExtension, UserExtensionData
from apps.permissions.models import RoleManagement, RoleGroupMapping


class OptimizedCustomUserForm(forms.ModelForm):
    """优化的用户表单 - 移除组和权限字段"""
    
    class Meta:
        model = CustomUser
        exclude = ['groups', 'user_permissions']  # 排除组和权限字段
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加角色说明
        if 'role' in self.fields:
            self.fields['role'].help_text = (
                '💡 角色决定用户的权限范围，系统会自动分配对应的权限组。'
                '权限通过角色管理模块统一配置。'
            )
        
        # 为必填字段添加样式
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs.update({
                    'class': 'required-field',
                    'style': 'border-left: 3px solid #007cba;'
                })


class OptimizedCustomUserAdmin(UserAdmin):
    """优化的用户管理Admin - 专注于角色管理"""
    form = OptimizedCustomUserForm
    
    class Media:
        js = (
            'admin/js/user_sync_status.js',
        )
    
    # 列表显示
    list_display = [
        'username', 'real_name', 'role', 'get_role_permissions_info', 
        'email', 'phone', 'english_level', 'is_active', 'date_joined'
    ]
    
    # 过滤器
    list_filter = ['role', 'english_level', 'is_active', 'date_joined']
    
    # 搜索字段
    search_fields = ['username', 'real_name', 'email', 'phone']
    
    # 排序
    ordering = ['-date_joined']
    
    # 字段集配置 - 移除权限相关字段
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password', 'real_name', 'email', 'phone')
        }),
        ('角色配置', {
            'fields': ('role',),
            'description': '角色决定用户的权限范围，权限通过角色管理模块统一配置'
        }),
        ('学习信息', {
            'fields': ('grade_level', 'english_level'),
            'classes': ('collapse',)
        }),
        ('账号状态', {
            'fields': ('is_active', 'is_staff', 'admin_approval_status'),
            'classes': ('collapse',)
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('备注信息', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    # 添加用户字段集
    add_fieldsets = (
        ('基本信息', {
            'classes': ('wide',),
            'fields': ('username', 'real_name', 'email', 'phone', 'role', 'password1', 'password2'),
        }),
        ('学习信息', {
            'classes': ('wide', 'collapse'),
            'fields': ('grade_level', 'english_level'),
        }),
    )
    
    # 只读字段
    readonly_fields = ['last_login', 'date_joined']
    
    def get_role_permissions_info(self, obj):
        """显示角色权限信息 - 实时同步状态"""
        try:
            # 强制刷新数据，避免缓存问题
            role_mgmt = RoleManagement.objects.select_related().get(role=obj.role)
            direct_perms = role_mgmt.permissions.count()
            all_perms = len(role_mgmt.get_all_permissions())
            
            # 检查组同步状态 - 实时获取
            try:
                mapping = RoleGroupMapping.objects.select_related('group').get(role=obj.role)
                group_perms = mapping.group.permissions.count()
                
                # 更精确的同步状态检查
                if group_perms == all_perms and all_perms > 0:
                    sync_status = "✅"
                    sync_color = "#28a745"
                    sync_bg = "#d4edda"
                    sync_text = "已同步"
                elif group_perms > 0 and group_perms != all_perms:
                    sync_status = "⚠️"
                    sync_color = "#ffc107"
                    sync_bg = "#fff3cd"
                    sync_text = "部分同步"
                else:
                    sync_status = "❌"
                    sync_color = "#dc3545"
                    sync_bg = "#f8d7da"
                    sync_text = "未同步"
                    
            except RoleGroupMapping.DoesNotExist:
                sync_status = "❌"
                sync_color = "#dc3545"
                sync_bg = "#f8d7da"
                sync_text = "无映射"
                group_perms = 0
            
            # 添加唯一ID以便JavaScript更新
            unique_id = f"role_info_{obj.pk}_{obj.role}"
            
            return format_html(
                '<div id="{}" style="font-size: 12px;" data-role="{}" data-user-id="{}">' +
                '<span style="color: #007cba; background: #e7f3ff; padding: 2px 6px; border-radius: 3px; margin-right: 5px;">' +
                '🎯 直接: {}个</span>' +
                '<span style="color: #28a745; background: #d4edda; padding: 2px 6px; border-radius: 3px; margin-right: 5px;">' +
                '📊 总计: {}个</span>' +
                '<span id="sync_status_{}" style="color: {}; background: {}; padding: 2px 6px; border-radius: 3px;" ' +
                'title="组权限: {}个 / 角色权限: {}个">' +
                '{} {}</span>' +
                '</div>',
                unique_id, obj.role, obj.pk,
                direct_perms, all_perms,
                obj.pk, sync_color, sync_bg,
                group_perms, all_perms,
                sync_status, sync_text
            )
        except RoleManagement.DoesNotExist:
            return format_html(
                '<span style="color: #dc3545; background: #f8d7da; padding: 2px 6px; border-radius: 3px; font-size: 12px;">' +
                '❌ 角色未配置</span>'
            )
    
    get_role_permissions_info.short_description = '权限信息'  # type: ignore
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        """保存模型时自动同步角色权限"""
        super().save_model(request, obj, form, change)
        
        # 自动同步角色到组
        try:
            mapping = RoleGroupMapping.objects.get(role=obj.role)
            if mapping.auto_sync:
                # 清除用户现有组
                obj.groups.clear()
                # 添加到角色对应的组
                obj.groups.add(mapping.group)
                
                self.message_user(
                    request, 
                    f'✅ 用户已自动分配到角色组: {mapping.group.name}',
                    level=messages.SUCCESS
                )
        except RoleGroupMapping.DoesNotExist:
            self.message_user(
                request,
                f'⚠️ 角色 {obj.get_role_display()} 未配置对应的权限组，请联系管理员',
                level=messages.WARNING
            )
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/role-permissions/',
                self.admin_site.admin_view(self.view_role_permissions),
                name='accounts_customuser_role_permissions'
            ),
            path(
                'role-permissions-help/',
                self.admin_site.admin_view(self.role_permissions_help),
                name='accounts_customuser_role_help'
            ),
            path(
                'check-user-sync-status/',
                self.admin_site.admin_view(self.check_user_sync_status_view),
                name='check_user_sync_status'
            ),
            path(
                'batch-check-sync-status/',
                self.admin_site.admin_view(self.batch_check_sync_status_view),
                name='batch_check_sync_status'
            ),
        ]
        return custom_urls + urls
    
    def view_role_permissions(self, request, user_id):
        """查看用户角色权限详情"""
        user = get_object_or_404(CustomUser, pk=user_id)
        
        role_mgmt = None
        group_info = None
        
        try:
            role_mgmt = RoleManagement.objects.get(role=user.role)
            direct_permissions = list(role_mgmt.permissions.all())
            all_permissions = list(role_mgmt.get_all_permissions())
            inherited_permissions = [p for p in all_permissions if p not in direct_permissions]
            
            # 获取组权限信息
            try:
                mapping = RoleGroupMapping.objects.get(role=user.role)
                group_permissions = list(mapping.group.permissions.all())
                group_info = {
                    'group': mapping.group,
                    'permissions': group_permissions,
                    'sync_status': len(group_permissions) == len(all_permissions)
                }
            except RoleGroupMapping.DoesNotExist:
                pass
            
        except RoleManagement.DoesNotExist:
            direct_permissions = []
            inherited_permissions = []
            all_permissions = []
        
        context = {
            'title': f'用户角色权限详情: {user.username}',
            'user_obj': user,
            'role_mgmt': role_mgmt,
            'direct_permissions': direct_permissions,
            'inherited_permissions': inherited_permissions,
            'all_permissions': all_permissions,
            'group_info': group_info,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(
            request,
            'admin/accounts/role_permissions_detail.html',
            context
        )
    
    def role_permissions_help(self, request):
        """角色权限帮助页面"""
        context = {
            'title': '角色权限管理说明',
            'opts': self.model._meta,
        }
        
        return TemplateResponse(
            request,
            'admin/accounts/role_permissions_help.html',
            context
        )
    
    def check_user_sync_status_view(self, request):
        """检查单个用户同步状态API"""
        if request.method == 'POST':
            try:
                import json
                data = json.loads(request.body)
                user_id = data.get('user_id')
                
                if not user_id:
                    return JsonResponse({'success': False, 'error': '缺少用户ID参数'})
                
                try:
                    user = CustomUser.objects.get(id=user_id)
                    sync_info = self._get_user_sync_status(user)
                    
                    return JsonResponse({
                        'success': True,
                        'user_id': user_id,
                        'sync_status': sync_info
                    })
                    
                except CustomUser.DoesNotExist:
                    return JsonResponse({'success': False, 'error': '用户不存在'})
                    
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})
    
    def batch_check_sync_status_view(self, request):
        """批量检查用户同步状态API"""
        if request.method == 'POST':
            try:
                import json
                data = json.loads(request.body)
                user_ids = data.get('user_ids', [])
                
                if not user_ids:
                    return JsonResponse({'success': False, 'error': '缺少用户ID列表'})
                
                results = []
                for user_id in user_ids:
                    try:
                        user = CustomUser.objects.get(id=user_id)
                        sync_info = self._get_user_sync_status(user)
                        results.append({
                            'user_id': user_id,
                            'sync_status': sync_info
                        })
                    except CustomUser.DoesNotExist:
                        results.append({
                            'user_id': user_id,
                            'error': '用户不存在'
                        })
                
                return JsonResponse({
                    'success': True,
                    'results': results
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': '仅支持POST请求'})
    
    def _get_user_sync_status(self, user):
        """获取用户同步状态信息"""
        from apps.permissions.models import RoleManagement, RoleGroupMapping
        
        if not user.role:
            return {
                'status': 'no_role',
                'message': '无角色',
                'icon': '❌'
            }
        
        try:
            # 获取角色权限数量
            role_mgmt = RoleManagement.objects.get(role=user.role)
            role_perms = len(role_mgmt.get_all_permissions())
            
            # 获取组权限数量和映射状态
            try:
                mapping = RoleGroupMapping.objects.select_related('group').get(role=user.role)
                group_perms = mapping.group.permissions.count()
                
                if group_perms == role_perms and role_perms > 0:
                    return {
                        'status': 'synced',
                        'message': f'已同步 ({role_perms}个权限)',
                        'icon': '✅'
                    }
                elif group_perms > 0:
                    return {
                        'status': 'partial',
                        'message': f'部分同步 (角色:{role_perms}, 组:{group_perms})',
                        'icon': '⚠️'
                    }
                else:
                    return {
                        'status': 'not_synced',
                        'message': '未同步',
                        'icon': '❌'
                    }
                    
            except RoleGroupMapping.DoesNotExist:
                return {
                    'status': 'no_mapping',
                    'message': '无映射',
                    'icon': '❌'
                }
                
        except RoleManagement.DoesNotExist:
            return {
                'status': 'role_not_found',
                'message': '角色不存在',
                'icon': '❌'
            }
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表视图，添加权限管理提示"""
        extra_context = extra_context or {}
        extra_context['role_permissions_help_url'] = reverse(
            'admin:accounts_customuser_role_help'
        )
        return super().changelist_view(request, extra_context)


# 角色特定的Admin类（继承优化的基类）
class OptimizedAdminUserAdmin(OptimizedCustomUserAdmin):
    """管理员用户Admin"""
    list_display = [
        'username', 'real_name', 'role', 'get_role_permissions_info', 
        'email', 'phone', 'english_level', 'is_active', 'date_joined',
        'is_superuser', 'is_staff'
    ]
    list_filter = ['role', 'english_level', 'is_active', 'date_joined', 'is_superuser', 'is_staff']
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=UserRole.ADMIN)


class OptimizedTeacherUserAdmin(OptimizedCustomUserAdmin):
    """教师用户Admin"""
    list_display = [
        'username', 'real_name', 'role', 'get_role_permissions_info', 
        'email', 'phone', 'english_level', 'is_active', 'date_joined'
    ]
    list_filter = ['role', 'english_level', 'is_active', 'date_joined']
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=UserRole.TEACHER)


class OptimizedStudentUserAdmin(OptimizedCustomUserAdmin):
    """学生用户Admin"""
    list_display = [
        'username', 'real_name', 'role', 'get_role_permissions_info', 
        'email', 'phone', 'english_level', 'is_active', 'date_joined',
        'grade_level'
    ]
    list_filter = ['role', 'english_level', 'is_active', 'date_joined', 'grade_level']
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=UserRole.STUDENT)





class OptimizedParentUserAdmin(OptimizedCustomUserAdmin):
    """家长用户Admin"""
    list_display = [
        'username', 'real_name', 'role', 'get_role_permissions_info', 
        'email', 'phone', 'english_level', 'is_active', 'date_joined'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=UserRole.PARENT)


# 注册优化的Admin
# 注意：这个文件是示例实现，实际使用时需要替换原有的admin注册