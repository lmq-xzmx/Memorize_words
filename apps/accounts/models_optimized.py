from django.db import models
from django.contrib.auth.models import Group
from .models import CustomUser, UserRole
from django.core.exceptions import ValidationError
from django.utils import timezone
import json


class OptimizedRoleTemplate(models.Model):
    """优化的角色模板 - 注册配置层"""
    
    # 注册流程类型
    REGISTER_TYPE_CHOICES = [
        ('auto', '自动注册'),
        ('approval', '需要审批'),
        ('invitation', '邀请注册'),
        ('disabled', '禁用注册'),
    ]
    
    # 权限分配策略
    PERMISSION_STRATEGY_CHOICES = [
        ('inherit', '继承默认权限'),
        ('custom', '自定义权限'),
        ('template', '基于模板'),
    ]
    
    role = models.CharField(max_length=50, choices=UserRole.choices, unique=True, help_text="角色类型")
    template_name = models.CharField(max_length=100, help_text="模板名称")
    description = models.TextField(blank=True, help_text="模板描述")
    
    # 注册流程配置
    register_type = models.CharField(max_length=20, choices=REGISTER_TYPE_CHOICES, default='auto', help_text="注册流程类型")
    auto_assign_on_register = models.BooleanField(default=True, help_text="注册时自动分配此角色")
    require_approval = models.BooleanField(default=False, help_text="是否需要管理员审批")
    approval_roles = models.JSONField(default=list, help_text="可审批的角色列表")
    
    # 权限配置
    permission_strategy = models.CharField(max_length=20, choices=PERMISSION_STRATEGY_CHOICES, default='inherit', help_text="权限分配策略")
    default_permissions = models.JSONField(default=dict, help_text="默认权限配置")
    default_menu_access = models.JSONField(default=dict, help_text="默认菜单访问配置")
    
    # 注册表单配置
    required_fields = models.JSONField(default=list, help_text="必填字段列表")
    optional_fields = models.JSONField(default=list, help_text="可选字段列表")
    form_config = models.JSONField(default=dict, help_text="表单配置")
    
    # 自动化配置
    auto_create_group = models.BooleanField(default=True, help_text="自动创建对应的Django组")
    auto_sync_permissions = models.BooleanField(default=True, help_text="自动同步权限")
    
    # 状态和版本
    is_active = models.BooleanField(default=True, help_text="是否启用")
    version = models.CharField(max_length=20, default='1.0.0', help_text="模板版本")
    sort_order = models.IntegerField(default=0, help_text="排序顺序")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_role_templates_optimized',
        verbose_name='创建者'
    )
    
    class Meta:
        db_table = 'optimized_role_template'
        verbose_name = '优化角色模板'
        verbose_name_plural = '优化角色模板'
        ordering = ['sort_order', 'role']
    
    def get_register_type_display_name(self):
        """获取注册类型显示名称"""
        return dict(self.REGISTER_TYPE_CHOICES).get(self.register_type, '未知')
    
    def get_permission_strategy_display_name(self):
        """获取权限策略显示名称"""
        return dict(self.PERMISSION_STRATEGY_CHOICES).get(self.permission_strategy, '未知')
    
    def set_required_fields(self, fields_list):
        """设置必填字段"""
        self.required_fields = fields_list
    
    def set_optional_fields(self, fields_list):
        """设置可选字段"""
        self.optional_fields = fields_list
    
    def set_default_permissions(self, permissions_dict):
        """设置默认权限"""
        self.default_permissions = {
            'permissions': permissions_dict,
            'updated_at': timezone.now().isoformat()
        }
    
    def set_default_menu_access(self, menu_list):
        """设置默认菜单访问"""
        self.default_menu_access = {
            'menus': menu_list,
            'updated_at': timezone.now().isoformat()
        }
    
    def get_required_fields_list(self):
        """获取必填字段列表"""
        if isinstance(self.required_fields, list):
            return self.required_fields
        return []
    
    def get_optional_fields_list(self):
        """获取可选字段列表"""
        if isinstance(self.optional_fields, list):
            return self.optional_fields
        return []
    
    def get_default_permissions_dict(self):
        """获取默认权限字典"""
        if isinstance(self.default_permissions, dict):
            return self.default_permissions.get('permissions', {})
        return {}
    
    def get_default_menu_list(self):
        """获取默认菜单列表"""
        if isinstance(self.default_menu_access, dict):
            return self.default_menu_access.get('menus', [])
        return []
    
    def can_auto_register(self):
        """判断是否可以自动注册"""
        return self.is_active and self.register_type == 'auto' and self.auto_assign_on_register
    
    def needs_approval(self):
        """判断是否需要审批"""
        return self.require_approval or self.register_type == 'approval'
    
    def get_approval_roles_list(self):
        """获取可审批的角色列表"""
        if isinstance(self.approval_roles, list):
            return self.approval_roles
        return []
    
    def auto_configure_for_role(self):
        """根据角色自动配置模板"""
        role_configs = {
            'student': {
                'register_type': 'auto',
                'required_fields': ['real_name', 'grade_level', 'english_level'],
                'optional_fields': ['nickname', 'notes'],
                'default_permissions': {'view': True, 'add_own': True},
                'default_menus': ['dashboard', 'learning_center']
            },
            'parent': {
                'register_type': 'auto',
                'required_fields': ['real_name', 'phone'],
                'optional_fields': ['nickname', 'notes'],
                'default_permissions': {'view': True, 'view_child': True},
                'default_menus': ['dashboard', 'learning_center', 'progress_tracking']
            },
            'teacher': {
                'register_type': 'approval',
                'required_fields': ['real_name', 'phone', 'teaching_experience'],
                'optional_fields': ['nickname', 'notes', 'specialization'],
                'default_permissions': {'view': True, 'add': True, 'change_own': True},
                'default_menus': ['dashboard', 'teaching_management', 'vocabulary_management']
            },
            'admin': {
                'register_type': 'invitation',
                'required_fields': ['real_name', 'phone'],
                'optional_fields': ['nickname', 'notes'],
                'default_permissions': {'all': True},
                'default_menus': ['*']
            }
        }
        
        config = role_configs.get(self.role, role_configs['student'])
        
        self.register_type = config['register_type']
        self.set_required_fields(config['required_fields'])
        self.set_optional_fields(config['optional_fields'])
        self.set_default_permissions(config['default_permissions'])
        self.set_default_menu_access(config['default_menus'])
        
        if self.register_type == 'approval':
            self.require_approval = True
            self.approval_roles = ['admin', 'dean', 'academic_director']
    
    def create_user_with_template(self, user_data):
        """根据模板创建用户"""
        if not self.can_auto_register() and not self.needs_approval():
            raise ValidationError(f"角色 {self.role} 不允许注册")
        
        # 验证必填字段
        required_fields = self.get_required_fields_list()
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValidationError(f"必填字段 {field} 不能为空")
        
        # 创建用户
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data.get('email', ''),
            password=user_data['password'],
            role=self.role,
            real_name=user_data.get('real_name', ''),
            phone=user_data.get('phone', ''),
            nickname=user_data.get('nickname', ''),
            notes=user_data.get('notes', ''),
            grade_level=user_data.get('grade_level', ''),
            english_level=user_data.get('english_level', ''),
        )
        
        # 如果需要审批，设置审批状态
        if self.needs_approval():
            user.admin_approval_status = 'pending'
            user.is_active = False
            user.save()
        
        # 自动分配权限和组
        if self.auto_sync_permissions:
            self._assign_permissions_to_user(user)
        
        return user
    
    def _assign_permissions_to_user(self, user):
        """为用户分配权限"""
        try:
            # 自动分配到对应的Django组
            if self.auto_create_group:
                group, created = Group.objects.get_or_create(name=f"{self.template_name}组")
                user.groups.add(group)
        except Exception:
            pass  # 如果分配失败，跳过
    
    def save(self, *args, **kwargs):
        # 如果是新创建的模板，自动配置
        if not self.pk and not self.default_permissions:
            self.auto_configure_for_role()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.template_name} ({self.get_role_display()})"


class RegistrationConfig(models.Model):
    """注册配置 - 全局注册设置"""
    
    # 注册开关
    enable_registration = models.BooleanField(default=True, help_text="是否开启用户注册")
    enable_role_selection = models.BooleanField(default=True, help_text="是否允许用户选择角色")
    default_role = models.CharField(max_length=50, choices=UserRole.choices, default='student', help_text="默认角色")
    
    # 验证配置
    require_email_verification = models.BooleanField(default=False, help_text="是否需要邮箱验证")
    require_phone_verification = models.BooleanField(default=False, help_text="是否需要手机验证")
    enable_captcha = models.BooleanField(default=True, help_text="是否启用验证码")
    
    # 审批配置
    auto_approval_roles = models.JSONField(default=list, help_text="自动审批的角色列表")
    manual_approval_roles = models.JSONField(default=list, help_text="需要手动审批的角色列表")
    
    # 通知配置
    notify_admin_on_register = models.BooleanField(default=True, help_text="注册时通知管理员")
    notify_user_on_approval = models.BooleanField(default=True, help_text="审批时通知用户")
    
    # 限制配置
    max_daily_registrations = models.IntegerField(default=100, help_text="每日最大注册数量")
    registration_cooldown_minutes = models.IntegerField(default=5, help_text="注册冷却时间（分钟）")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'registration_config'
        verbose_name = '注册配置'
        verbose_name_plural = '注册配置'
    
    def get_auto_approval_roles_list(self):
        """获取自动审批角色列表"""
        if isinstance(self.auto_approval_roles, list):
            return self.auto_approval_roles
        return []
    
    def get_manual_approval_roles_list(self):
        """获取手动审批角色列表"""
        if isinstance(self.manual_approval_roles, list):
            return self.manual_approval_roles
        return []
    
    def is_role_auto_approved(self, role):
        """判断角色是否自动审批"""
        return role in self.get_auto_approval_roles_list()
    
    def is_role_manual_approved(self, role):
        """判断角色是否需要手动审批"""
        return role in self.get_manual_approval_roles_list()
    
    def can_register_role(self, role):
        """判断角色是否可以注册"""
        if not self.enable_registration:
            return False
        
        if not self.enable_role_selection and role != self.default_role:
            return False
        
        return True
    
    def __str__(self):
        status = "开启" if self.enable_registration else "关闭"
        return f"注册配置 - {status}"


class RegistrationLog(models.Model):
    """注册日志"""
    
    STATUS_CHOICES = [
        ('success', '注册成功'),
        ('pending', '待审批'),
        ('failed', '注册失败'),
        ('rejected', '审批拒绝'),
    ]
    
    username = models.CharField(max_length=150, help_text="用户名")
    email = models.EmailField(blank=True, help_text="邮箱")
    role = models.CharField(max_length=50, choices=UserRole.choices, help_text="申请角色")
    template_used = models.ForeignKey(OptimizedRoleTemplate, on_delete=models.SET_NULL, null=True, blank=True, help_text="使用的模板")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="注册状态")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP地址")
    user_agent = models.TextField(blank=True, help_text="用户代理")
    
    error_message = models.TextField(blank=True, help_text="错误信息")
    approval_notes = models.TextField(blank=True, help_text="审批备注")
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True, help_text="审批时间")
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_registrations',
        verbose_name='审批人'
    )
    
    class Meta:
        db_table = 'registration_log'
        verbose_name = '注册日志'
        verbose_name_plural = '注册日志'
        ordering = ['-created_at']
    
    def get_status_display_name(self):
        """获取状态显示名称"""
        return dict(self.STATUS_CHOICES).get(self.status, '未知')
    
    def __str__(self):
        return f"{self.username} - {self.get_status_display_name()}"