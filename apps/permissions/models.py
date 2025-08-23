from django.db import models
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
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


class MenuField(models.Model):
    """菜单字段表 - 定义菜单对应的数据模型字段"""
    model = models.CharField('表名', max_length=64, help_text='数据模型表名')
    menu = models.ForeignKey(
        MenuModuleConfig, 
        on_delete=models.CASCADE, 
        verbose_name='菜单', 
        help_text='关联的菜单模块'
    )
    field_name = models.CharField('字段名', max_length=64, help_text='模型表字段名')
    title = models.CharField('字段显示名', max_length=64, help_text='字段的显示名称')
    field_type = models.CharField('字段类型', max_length=32, default='text', help_text='字段数据类型')
    is_required = models.BooleanField('是否必填', default=False, help_text='字段是否必填')
    is_sensitive = models.BooleanField('是否敏感', default=False, help_text='是否为敏感字段')
    sort_order = models.IntegerField('排序', default=0, help_text='字段显示排序')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '菜单字段表'
        verbose_name_plural = '菜单字段表'
        ordering = ['sort_order', 'field_name']
        unique_together = [['menu', 'field_name']]
    
    def __str__(self):
        return f"{self.menu.name} - {self.title}"


class FieldPermission(models.Model):
    """字段权限表 - 控制角色对字段的操作权限"""
    role = models.CharField('角色', max_length=50, help_text='角色标识')
    field = models.ForeignKey(
        MenuField, 
        on_delete=models.CASCADE, 
        related_name='field_permissions', 
        verbose_name='字段', 
        help_text='关联的菜单字段'
    )
    is_query = models.BooleanField('可查询', default=True, help_text='是否可查询此字段')
    is_create = models.BooleanField('可创建', default=True, help_text='是否可在创建时设置此字段')
    is_update = models.BooleanField('可更新', default=True, help_text='是否可更新此字段')
    is_export = models.BooleanField('可导出', default=True, help_text='是否可导出此字段')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '字段权限表'
        verbose_name_plural = '字段权限表'
        ordering = ['role', 'field']
        unique_together = [['role', 'field']]
    
    def __str__(self):
        return f"{self.role} - {self.field.title}"


class MenuButton(models.Model):
    """菜单按钮表 - 定义菜单的操作按钮和API权限"""
    menu = models.ForeignKey(
        MenuModuleConfig,
        on_delete=models.CASCADE,
        related_name='menu_buttons',
        verbose_name='关联菜单',
        help_text='关联的菜单模块'
    )
    name = models.CharField('按钮名称', max_length=64, help_text='按钮显示名称')
    value = models.CharField('权限值', max_length=64, help_text='权限标识值')
    api = models.CharField('接口地址', max_length=200, help_text='对应的API接口地址')
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]
    method = models.CharField('请求方法', max_length=10, choices=METHOD_CHOICES, default='GET', help_text='API请求方法')
    
    icon = models.CharField('图标', max_length=64, blank=True, help_text='按钮图标')
    sort_order = models.IntegerField('排序', default=0, help_text='按钮显示排序')
    is_active = models.BooleanField('是否激活', default=True, help_text='按钮是否激活')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '菜单按钮表'
        verbose_name_plural = '菜单按钮表'
        ordering = ['sort_order', 'name']
        unique_together = [['menu', 'value']]
    
    def __str__(self):
        return f"{self.menu.name} - {self.name}"


class RoleMenuButtonPermission(models.Model):
    """角色按钮权限表 - 控制角色对按钮的访问权限和数据权限范围"""
    role = models.CharField('角色', max_length=50, help_text='角色标识')
    menu_button = models.ForeignKey(
        MenuButton,
        on_delete=models.CASCADE,
        related_name='button_permissions',
        verbose_name='关联按钮',
        help_text='关联的菜单按钮'
    )
    
    # 数据权限范围
    DATASCOPE_CHOICES = [
        (0, '仅本人数据权限'),
        (1, '本部门及以下数据权限'),
        (2, '本部门数据权限'),
        (3, '全部数据权限'),
        (4, '自定义数据权限'),
    ]
    data_range = models.IntegerField(
        '数据权限范围', 
        choices=DATASCOPE_CHOICES, 
        default=0, 
        help_text='数据权限范围控制'
    )
    
    # 自定义数据权限相关部门（当data_range=4时使用）
    custom_dept_ids = models.JSONField(
        '自定义部门权限', 
        default=list, 
        blank=True, 
        help_text='自定义数据权限关联的部门ID列表'
    )
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色按钮权限表'
        verbose_name_plural = '角色按钮权限表'
        ordering = ['role', 'menu_button']
        unique_together = [['role', 'menu_button']]
    
    def __str__(self):
        return f"{self.role} - {self.menu_button.name}"


class OperationLog(models.Model):
    """操作日志模型 - 从Django-Vue3-Admin迁移"""
    request_modular = models.CharField(
        max_length=64,
        verbose_name='请求模块',
        null=True,
        blank=True,
        help_text='请求模块'
    )
    request_path = models.CharField(
        max_length=400,
        verbose_name='请求地址',
        null=True,
        blank=True,
        help_text='请求地址'
    )
    request_body = models.TextField(
        verbose_name='请求参数',
        null=True,
        blank=True,
        help_text='请求参数'
    )
    request_method = models.CharField(
        max_length=8,
        verbose_name='请求方式',
        null=True,
        blank=True,
        help_text='请求方式'
    )
    request_msg = models.TextField(
        verbose_name='操作说明',
        null=True,
        blank=True,
        help_text='操作说明'
    )
    request_ip = models.CharField(
        max_length=32,
        verbose_name='请求IP地址',
        null=True,
        blank=True,
        help_text='请求IP地址'
    )
    request_browser = models.CharField(
        max_length=64,
        verbose_name='请求浏览器',
        null=True,
        blank=True,
        help_text='请求浏览器'
    )
    response_code = models.CharField(
        max_length=32,
        verbose_name='响应状态码',
        null=True,
        blank=True,
        help_text='响应状态码'
    )
    request_os = models.CharField(
        max_length=64,
        verbose_name='操作系统',
        null=True,
        blank=True,
        help_text='操作系统'
    )
    json_result = models.TextField(
        verbose_name='返回信息',
        null=True,
        blank=True,
        help_text='返回信息'
    )
    status = models.BooleanField(
        default=False,
        verbose_name='响应状态',
        help_text='响应状态'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='操作用户',
        help_text='执行操作的用户'
    )
    create_datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='操作发生时间'
    )
    
    class Meta:
        db_table = 'system_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['create_datetime']),
            models.Index(fields=['creator', 'create_datetime']),
            models.Index(fields=['request_method', 'create_datetime']),
            models.Index(fields=['status', 'create_datetime']),
        ]
    
    def __str__(self):
        return f'{self.creator} - {self.request_method} {self.request_path}'


class Department(models.Model):
    """部门模型 - 支持层级结构的部门管理"""
    name = models.CharField('部门名称', max_length=100, help_text='部门名称')
    code = models.CharField('部门编码', max_length=50, unique=True, help_text='部门唯一编码')
    description = models.TextField('部门描述', blank=True, help_text='部门职能描述')
    
    # 层级结构
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='上级部门',
        null=True,
        blank=True,
        help_text='上级部门，支持多级部门结构'
    )
    
    # 部门负责人
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='led_departments',
        verbose_name='部门负责人',
        null=True,
        blank=True,
        help_text='部门负责人'
    )
    
    # 部门设置
    is_active = models.BooleanField('是否启用', default=True, help_text='部门是否启用')
    sort_order = models.IntegerField('排序', default=0, help_text='部门显示排序')
    
    # 联系信息
    phone = models.CharField('联系电话', max_length=20, blank=True, help_text='部门联系电话')
    email = models.EmailField('邮箱', blank=True, help_text='部门邮箱')
    address = models.TextField('地址', blank=True, help_text='部门地址')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_full_name(self):
        """获取部门全名（包含上级部门）"""
        names = []
        current = self
        while current:
            names.append(current.name)
            current = current.parent
        return ' > '.join(reversed(names))
    
    def get_descendants(self):
        """递归获取所有下级部门"""
        descendants = []
        for child in self.children.filter(is_active=True):
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_all_children_ids(self):
        """获取所有下级部门ID列表（包含自己）"""
        ids = [self.id]
        for child in self.get_descendants():
            ids.append(child.id)
        return ids


class UserDepartment(models.Model):
    """用户部门关联模型 - 支持用户多部门归属"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_departments',
        verbose_name='用户'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='department_users',
        verbose_name='部门'
    )
    
    # 关联设置
    is_primary = models.BooleanField('是否主部门', default=False, help_text='用户的主要部门')
    position = models.CharField('职位', max_length=100, blank=True, help_text='在该部门的职位')
    join_date = models.DateField('加入日期', default=timezone.now, help_text='加入部门的日期')
    is_active = models.BooleanField('是否有效', default=True, help_text='关联是否有效')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户部门关联'
        verbose_name_plural = '用户部门关联'
        ordering = ['-is_primary', 'department__sort_order']
        unique_together = [['user', 'department']]
    
    def __str__(self):
        primary_text = '(主)' if self.is_primary else ''
        return f"{self.user.username} - {self.department.name}{primary_text}"


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