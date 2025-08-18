from django.db import models
from django.contrib.auth.models import Group, Permission
from apps.accounts.models import UserRole
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 为静态类型检查提供方法签名
    class ModelWithChoices(models.Model):
        def get_role_display(self) -> str: ...
        def get_sync_type_display(self) -> str: ...


class MenuModuleConfig(models.Model):
    """前台菜单模块配置"""
    
    # 菜单级别选择
    MENU_LEVEL_CHOICES = [
        ('root', '根目录'),
        ('level1', '一级目录'),
        ('level2', '二级目录'),
    ]
    
    key = models.CharField('菜单标识', max_length=50, unique=True)
    name = models.CharField('菜单名称', max_length=100)
    menu_level = models.CharField('菜单级别', max_length=10, choices=MENU_LEVEL_CHOICES, default='root')
    icon = models.CharField('图标类名', max_length=100, default='fas fa-circle')
    url = models.CharField('菜单链接', max_length=200)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '前台菜单模块'
        verbose_name_plural = '前台菜单模块管理'
        ordering = ['sort_order', 'key']

    def __str__(self):
        return f"{self.name} ({self.key})"


class RoleMenuPermission(models.Model):
    """角色菜单权限配置"""
    role = models.CharField('角色', max_length=50, help_text='支持预定义和自定义角色')
    menu_module = models.ForeignKey(MenuModuleConfig, on_delete=models.CASCADE, verbose_name='菜单模块')
    can_access = models.BooleanField('可访问', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '角色菜单权限'
        verbose_name_plural = '角色菜单权限配置'
        unique_together = ['role', 'menu_module']

    def get_role_display(self) -> str:
        """获取角色显示名称"""
        # 首先尝试从预定义角色中获取显示名称
        predefined_roles = dict(UserRole.choices)
        if self.role in predefined_roles:
            return str(predefined_roles[self.role])
        
        # 如果是自定义角色，尝试从RoleManagement获取显示名称
        try:
            role_management = RoleManagement.objects.get(role=self.role)
            return role_management.get_role_display()
        except RoleManagement.DoesNotExist:
            return self.role

    def clean(self):
        """模型验证：确保角色有效"""
        from django.core.exceptions import ValidationError
        from apps.accounts.services.role_service import RoleService
        
        valid_roles = [choice[0] for choice in RoleService.get_role_choices(include_empty=False)]
        if self.role not in valid_roles:
            raise ValidationError(f'无效的角色: {self.role}')

    def __str__(self):
        return f"{self.get_role_display()} - {self.menu_module.name}"


class RoleGroupMapping(models.Model):
    """角色组映射配置"""
    role = models.CharField('角色', max_length=50, unique=True, help_text='角色标识符，支持自定义角色名称')
    group = models.OneToOneField(Group, on_delete=models.CASCADE, verbose_name='Django组')
    auto_sync = models.BooleanField('自动同步', default=True, help_text='用户角色变更时自动分配到对应组')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '角色组映射'
        verbose_name_plural = '角色组映射配置'

    def get_role_display(self) -> str:
        """获取角色显示名称"""
        # 首先尝试从预定义角色中获取显示名称
        predefined_roles = dict(UserRole.choices)
        if self.role in predefined_roles:
            return str(predefined_roles[self.role])
        
        # 如果是自定义角色，尝试从RoleManagement获取显示名称
        try:
            role_management = RoleManagement.objects.get(role=self.role)
            return role_management.get_role_display()
        except RoleManagement.DoesNotExist:
            return self.role

    def __str__(self):
        return f"{self.get_role_display()} → {self.group.name}"


class RoleManagement(models.Model):
    """角色管理 - 支持角色继承"""
    role = models.CharField('角色', max_length=50, unique=True, help_text='角色标识符，支持自定义角色名称')
    display_name = models.CharField('显示名称', max_length=50)
    description = models.TextField('角色描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    permissions = models.ManyToManyField(Permission, verbose_name='直接权限', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              verbose_name='父角色', help_text='角色继承关系，子角色自动继承父角色权限')
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '角色管理'
        verbose_name_plural = '角色管理'
        ordering = ['sort_order', 'role']

    def get_role_display(self) -> str:
        """获取角色显示名称"""
        # 首先尝试从预定义角色中获取显示名称
        predefined_roles = dict(UserRole.choices)
        if self.role in predefined_roles:
            return str(predefined_roles[self.role])
        # 如果是自定义角色，返回 display_name 或角色标识符
        return self.display_name or self.role

    def get_all_permissions(self):
        """获取所有权限（包括继承的权限）"""
        permissions = set(self.permissions.all())
        
        # 递归获取父角色权限
        if self.parent:
            permissions.update(self.parent.get_all_permissions())
        
        return permissions

    def get_children(self):
        """获取所有子角色"""
        return RoleManagement.objects.filter(parent=self)

    def get_hierarchy_level(self):
        """获取角色层级深度"""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level

    def is_ancestor_of(self, role):
        """判断是否为指定角色的祖先"""
        current = role.parent
        while current:
            if current == self:
                return True
            current = current.parent
        return False

    def clean(self):
        """模型验证：防止循环继承"""
        from django.core.exceptions import ValidationError
        if self.parent:
            if self.parent == self:
                raise ValidationError('角色不能继承自己')
            if self.is_ancestor_of(self.parent):
                raise ValidationError('不能创建循环继承关系')

    def __str__(self):
        hierarchy_prefix = "  " * self.get_hierarchy_level()
        return f"{hierarchy_prefix}{self.display_name} ({self.get_role_display()})"


# PermissionSyncLog 模型已移至 models_optimized.py