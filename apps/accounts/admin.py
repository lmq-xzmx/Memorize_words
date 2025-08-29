from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CustomUser, UserLoginLog, UserRole, RoleApproval, LearningProfile,
    RoleTemplate, RoleExtension, RoleUserGroup, UserExtensionData
)
from django.contrib.auth.models import Group
from apps.permissions.role_selector_config import StandardRoleAdminMixin


@admin.register(CustomUser)
class CustomUserAdmin(StandardRoleAdminMixin, UserAdmin):
    """自定义用户管理"""
    model = CustomUser
    list_display = [
        'username', 'real_name', 'role_display', 'phone', 'email', 
        'grade_level', 'english_level', 'is_active_display', 
        'admin_approval_status_display', 'date_joined'
    ]
    list_filter = [
        'role', 'admin_approval_status', 'is_active', 'english_level', 
        'date_joined', 'last_login'
    ]
    search_fields = ['username', 'real_name', 'phone', 'email', 'nickname']
    ordering = ['-date_joined']
    
    # 字段集配置
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password', 'real_name', 'nickname')
        }),
        ('联系方式', {
            'fields': ('email', 'phone')
        }),
        ('角色与权限', {
            'fields': ('role', 'admin_approval_status', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('学习信息', {
            'fields': ('grade_level', 'english_level'),
            'classes': ('collapse',)
        }),
        ('其他信息', {
            'fields': ('notes', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        })
    )
    
    # 添加用户时的字段集
    add_fieldsets = (
        ('基本信息', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'real_name', 'phone')
        }),
        ('角色设置', {
            'fields': ('role', 'email')
        }),
        ('学习信息', {
            'fields': ('grade_level', 'english_level'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['date_joined', 'last_login']
    filter_horizontal = ['groups', 'user_permissions']
    
    @admin.display(description='角色', ordering='role')
    def role_display(self, obj):
        """角色显示"""
        role_colors = {
            UserRole.ADMIN: '#dc3545',
            UserRole.DEAN: '#fd7e14', 
            UserRole.ACADEMIC_DIRECTOR: '#ffc107',
            UserRole.RESEARCH_LEADER: '#20c997',
            UserRole.TEACHER: '#0d6efd',
            UserRole.PARENT: '#6f42c1',
            UserRole.STUDENT: '#198754'
        }
        color = role_colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_role_display()
        )
    
    @admin.display(description='账号状态', ordering='is_active')
    def is_active_display(self, obj):
        """账号状态显示"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ 正常</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ 禁用</span>'
            )
    
    @admin.display(description='审批状态', ordering='admin_approval_status')
    def admin_approval_status_display(self, obj):
        """审批状态显示"""
        if obj.role != UserRole.ADMIN:
            return '-'
        
        status_colors = {
            'pending': '#ffc107',
            'approved': '#198754',
            'rejected': '#dc3545'
        }
        color = status_colors.get(obj.admin_approval_status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_admin_approval_status_display()
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related()
    
    actions = ['activate_users', 'deactivate_users', 'approve_admins', 'reject_admins']
    
    @admin.action(description='激活选中的用户')
    def activate_users(self, request, queryset):
        """批量激活用户"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个用户')
    
    @admin.action(description='禁用选中的用户')
    def deactivate_users(self, request, queryset):
        """批量禁用用户"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功禁用 {updated} 个用户')
    
    @admin.action(description='批准选中的管理员申请')
    def approve_admins(self, request, queryset):
        """批量批准管理员申请"""
        admin_users = queryset.filter(role=UserRole.ADMIN)
        updated = admin_users.update(admin_approval_status='approved')
        self.message_user(request, f'成功批准 {updated} 个管理员申请')
    
    @admin.action(description='拒绝选中的管理员申请')
    def reject_admins(self, request, queryset):
        """批量拒绝管理员申请"""
        admin_users = queryset.filter(role=UserRole.ADMIN)
        updated = admin_users.update(admin_approval_status='rejected')
        self.message_user(request, f'成功拒绝 {updated} 个管理员申请')


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    """用户登录日志管理"""
    list_display = [
        'username', 'login_time', 'ip_address', 
        'login_success_display', 'user_agent_short'
    ]
    list_filter = ['login_success', 'login_time']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['username', 'login_time', 'ip_address', 'user_agent', 'login_success']
    ordering = ['-login_time']
    date_hierarchy = 'login_time'
    
    @admin.display(description='登录状态', ordering='login_success')
    def login_success_display(self, obj):
        """登录状态显示"""
        if obj.login_success:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ 成功</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ 失败</span>'
            )
    
    @admin.display(description='用户代理')
    def user_agent_short(self, obj):
        """用户代理简短显示"""
        if len(obj.user_agent) > 50:
            return obj.user_agent[:50] + '...'
        return obj.user_agent
    
    def has_add_permission(self, request):
        """禁止添加登录日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改登录日志"""
        return False


@admin.register(RoleApproval)
class RoleApprovalAdmin(admin.ModelAdmin):
    """角色审批管理"""
    list_display = [
        'user', 'requested_role', 'current_role', 'status_display',
        'approved_by', 'created_at'
    ]
    list_filter = ['status', 'requested_role', 'current_role', 'created_at']
    search_fields = ['user__username', 'user__real_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('申请信息', {
            'fields': ('user', 'requested_role', 'current_role', 'reason')
        }),
        ('审批信息', {
            'fields': ('status', 'admin_comment', 'approved_by')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='审批状态', ordering='status')
    def status_display(self, obj):
        """审批状态显示"""
        status_colors = {
            'pending': '#ffc107',
            'approved': '#198754',
            'rejected': '#dc3545'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )


@admin.register(LearningProfile)
class LearningProfileAdmin(admin.ModelAdmin):
    """学习档案管理"""
    list_display = [
        'user', 'total_study_time_display', 'completed_lessons',
        'current_streak', 'max_streak', 'last_study_date'
    ]
    list_filter = ['last_study_date', 'created_at']
    search_fields = ['user__username', 'user__real_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-total_study_time']
    
    @admin.display(description='总学习时长', ordering='total_study_time')
    def total_study_time_display(self, obj):
        """总学习时长显示"""
        hours = obj.total_study_time // 60
        minutes = obj.total_study_time % 60
        return f"{hours}小时{minutes}分钟"


@admin.register(RoleTemplate)
class RoleTemplateAdmin(admin.ModelAdmin):
    """角色模板管理"""
    list_display = [
        'template_name', 'role', 'version', 'field_count_display',
        'user_count_display', 'is_active', 'created_at'
    ]
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['template_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['role', 'template_name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role', 'template_name', 'description')
        }),
        ('版本控制', {
            'fields': ('version', 'is_active')
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='字段数量')
    def field_count_display(self, obj):
        """字段数量显示"""
        return obj.get_field_count()
    
    @admin.display(description='用户数量')
    def user_count_display(self, obj):
        """用户数量显示"""
        return obj.get_user_count()
    
    def save_model(self, request, obj, form, change):
        """保存时设置创建者"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RoleExtension)
class RoleExtensionAdmin(admin.ModelAdmin):
    """角色增项配置管理"""
    list_display = [
        'field_label', 'role', 'field_type', 'is_required',
        'show_in_frontend_register', 'show_in_backend_admin',
        'sort_order', 'is_active'
    ]
    list_filter = [
        'role', 'field_type', 'is_required', 'is_active',
        'show_in_frontend_register', 'show_in_backend_admin'
    ]
    search_fields = ['field_label', 'field_name', 'help_text']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['role', 'sort_order', 'field_name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('role_template', 'role', 'field_name', 'field_label')
        }),
        ('字段配置', {
            'fields': ('field_type', 'field_choices', 'default_value', 'help_text')
        }),
        ('验证规则', {
            'fields': ('is_required', 'validation_rules')
        }),
        ('显示控制', {
            'fields': (
                'show_in_frontend_register', 'show_in_backend_admin',
                'show_in_profile', 'sort_order', 'is_active'
            )
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(RoleUserGroup)
class RoleUserGroupAdmin(admin.ModelAdmin):
    """角色用户组管理"""
    list_display = [
        'name', 'role_display', 'user_count_display',
        'is_active', 'created_at'
    ]
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['users']
    ordering = ['role', 'name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'role', 'description')
        }),
        ('组成员', {
            'fields': ('users',)
        }),
        ('状态设置', {
            'fields': ('is_active',)
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='角色', ordering='role')
    def role_display(self, obj):
        """角色显示"""
        return obj.get_role_display_name()
    
    @admin.display(description='用户数量')
    def user_count_display(self, obj):
        """用户数量显示"""
        return obj.get_user_count()
    
    def save_model(self, request, obj, form, change):
        """保存时设置创建者"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserExtensionData)
class UserExtensionDataAdmin(admin.ModelAdmin):
    """用户角色增项数据管理"""
    list_display = [
        'user', 'role_extension', 'field_value_short',
        'created_at', 'updated_at'
    ]
    list_filter = [
        'role_extension__role', 'role_extension__field_type',
        'created_at'
    ]
    search_fields = [
        'user__username', 'user__real_name',
        'role_extension__field_label', 'field_value'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user', 'role_extension__sort_order']
    
    @admin.display(description='字段值')
    def field_value_short(self, obj):
        """字段值简短显示"""
        if len(obj.field_value) > 50:
            return obj.field_value[:50] + '...'
        return obj.field_value


# 已删除RoleLevel、RoleUser、UserExtension相关的Admin类


# 注册模型到admin
# CustomUser已通过@admin.register装饰器注册，无需重复注册

# 自定义admin站点标题
admin.site.site_header = '英语学习平台管理系统'
admin.site.site_title = '管理后台'
admin.site.index_title = '欢迎使用英语学习平台管理系统'