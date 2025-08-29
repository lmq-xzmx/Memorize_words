from django.db import models
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from apps.accounts.models import UserRole
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

# 为Django模型添加类型注解以解决objects属性访问问题
if TYPE_CHECKING:
    from django.db.models.manager import Manager
    
    # 为所有模型类添加objects属性类型注解
    models.Model.objects = Manager()  # type: ignore


class RoleMapping(models.Model):
    """UserRole和RoleManagement之间的映射关系"""
    
    user_role = models.CharField(
        '用户角色',
        max_length=50,
        unique=True,
        help_text='UserRole中定义的角色标识符'
    )
    role_management = models.ForeignKey(
        'RoleManagement',
        on_delete=models.CASCADE,
        verbose_name='角色管理',
        help_text='对应的RoleManagement实例'
    )
    is_active = models.BooleanField(
        '是否启用',
        default=True,
        help_text='映射关系是否启用'
    )
    auto_sync = models.BooleanField(
        '自动同步',
        default=True,
        help_text='是否自动同步权限变更'
    )
    description = models.TextField(
        '描述',
        blank=True,
        help_text='映射关系说明'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色映射'
        verbose_name_plural = '角色映射管理'
        ordering = ['user_role']
        indexes = [
            models.Index(fields=['user_role']),
            models.Index(fields=['is_active']),
        ]
    
    def get_user_role_display(self):
        """获取UserRole的显示名称"""
        try:
            predefined_roles = dict(UserRole.choices)
            return predefined_roles.get(self.user_role, self.user_role)
        except:
            return self.user_role
    
    def clean(self):
        """验证user_role是否在UserRole.choices中"""
        try:
            valid_roles = [choice[0] for choice in UserRole.choices]
            if self.user_role not in valid_roles:
                raise ValidationError(f'无效的用户角色: {self.user_role}')
        except AttributeError:
            # 如果UserRole没有choices属性，跳过验证
            pass
    
    def __str__(self) -> str:
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.get_user_role_display()} → {self.role_management.display_name}"

if TYPE_CHECKING:
    # 为静态类型检查提供方法签名
    class ModelWithChoices(models.Model):
        def get_role_display(self) -> str: ...
        def get_sync_type_display(self) -> str: ...


class SlotConfig(models.Model):
    """槽位配置模型 - 用于设置前端底部导航菜单的数量，支持角色依赖"""
    
    SLOT_COUNT_CHOICES = [
        (4, '4个槽位'),
        (5, '5个槽位'),
    ]
    
    name = models.CharField('配置名称', max_length=100, default='默认配置')
    role = models.CharField('角色', max_length=50, help_text='角色标识，不同角色可以有不同的槽位配置', null=True, blank=True)
    slot_count = models.IntegerField('槽位数量', choices=SLOT_COUNT_CHOICES, default=4, 
                                   help_text='前端底部导航菜单的槽位数量，仅允许4或5个')
    is_active = models.BooleanField('是否启用', default=True, help_text='是否为当前生效的配置')
    description = models.TextField('描述', blank=True, help_text='配置说明')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '槽位配置'
        verbose_name_plural = '槽位配置管理'
        ordering = ['-is_active', 'role', '-created_at']
        unique_together = ['role', 'slot_count']  # 每个角色的每种槽位数量只能有一个配置
    
    def clean(self):
        """确保每个角色只有一个激活配置"""
        if self.is_active:
            # 如果当前配置要设为激活，则将同角色的其他配置设为非激活
            if self.role:
                SlotConfig.objects.filter(role=self.role, is_active=True).exclude(pk=self.pk).update(is_active=False)
            else:
                # 全局默认配置，将其他全局配置设为非激活
                SlotConfig.objects.filter(role__isnull=True, is_active=True).exclude(pk=self.pk).update(is_active=False)
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_slot_count_for_role(cls, role=None):
        """获取指定角色的槽位数量"""
        try:
            # 首先尝试获取角色特定的配置
            if role:
                role_config = cls.objects.get(role=role, is_active=True)
                return role_config.slot_count
        except cls.DoesNotExist:
            pass
        
        try:
            # 如果没有角色特定配置，使用全局默认配置
            default_config = cls.objects.get(role__isnull=True, is_active=True)
            return default_config.slot_count
        except cls.DoesNotExist:
            # 如果没有任何配置，返回默认值4
            return 4
    
    @classmethod
    def get_current_slot_count(cls):
        """获取当前激活的槽位数量（保持向后兼容）"""
        return cls.get_slot_count_for_role()
    
    def get_role_display(self) -> str:
        """获取角色显示名称"""
        if not self.role:
            return '全局默认'
        
        # 尝试从UserRole获取显示名称
        try:
            from apps.accounts.models import UserRole
            for choice in UserRole.choices:
                if choice[0] == self.role:
                    return choice[1]
        except ImportError:
            pass
        
        return self.role
    
    def __str__(self) -> str:
        role_display = self.get_role_display()
        status = "(当前)" if self.is_active else ""
        return f"{role_display} - {dict(self.SLOT_COUNT_CHOICES)[self.slot_count]}{status}"


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

    def __str__(self) -> str:
        return f"{self.name} ({self.key})"


class MenuValidity(models.Model):
    """菜单有效性配置 - 每个菜单针对每个角色设置是否有效"""
    role = models.CharField('角色', max_length=50, help_text='支持预定义和自定义角色')
    menu_module = models.ForeignKey(MenuModuleConfig, on_delete=models.CASCADE, verbose_name='菜单模块')
    is_valid = models.BooleanField('是否有效', default=True, help_text='该菜单对该角色是否有效')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '菜单有效性'
        verbose_name_plural = '菜单有效性配置'
        unique_together = ['role', 'menu_module']
        ordering = ['role', 'menu_module__menu_level', 'menu_module__sort_order']

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

    def __str__(self) -> str:
        status = "有效" if self.is_valid else "无效"
        return f"{self.get_role_display()} - {self.menu_module.name} ({status})"


# RoleMenuAssignment 模型已删除，功能由槽位系统替代
# RoleMenuPermission 模型已被删除，请使用 MenuValidity 和槽位系统替代


class GroupRoleIdentifier(models.Model):
    """Django组角色标识扩展模型"""
    
    GROUP_STATUS_CHOICES = [
        ('role_linked', '已关联角色'),
        ('orphaned', '孤立组'),
        ('system', '系统组'),
        ('manual', '手动创建'),
    ]
    
    SYNC_STATUS_CHOICES = [
        ('synced', '已同步'),
        ('pending', '待同步'),
        ('failed', '同步失败'),
        ('disabled', '已禁用'),
    ]
    
    group = models.OneToOneField(
        Group, 
        on_delete=models.CASCADE, 
        verbose_name='Django组',
        related_name='role_identifier'
    )
    status = models.CharField(
        '组状态', 
        max_length=20, 
        choices=GROUP_STATUS_CHOICES, 
        default='manual',
        help_text='组的角色关联状态'
    )
    sync_status = models.CharField(
        '同步状态',
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default='synced',
        help_text='与角色系统的同步状态'
    )
    role_identifier = models.CharField(
        '关联角色标识', 
        max_length=50, 
        blank=True, 
        null=True,
        help_text='关联的角色标识符，为空表示未关联角色'
    )
    display_prefix = models.CharField(
        '显示前缀',
        max_length=20,
        default='[ROLE]',
        help_text='在管理界面显示的前缀标识'
    )
    last_sync_time = models.DateTimeField(
        '最后同步时间',
        null=True,
        blank=True,
        help_text='最后一次同步的时间'
    )
    sync_error_message = models.TextField(
        '同步错误信息',
        blank=True,
        help_text='同步失败时的错误信息'
    )
    is_auto_managed = models.BooleanField(
        '自动管理',
        default=True,
        help_text='是否由系统自动管理此组'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'Django组角色标识'
        verbose_name_plural = 'Django组角色标识管理'
        ordering = ['status', 'group__name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['sync_status']),
            models.Index(fields=['role_identifier']),
            models.Index(fields=['is_auto_managed']),
        ]
    
    def get_display_name(self):
        """获取带标识的显示名称"""
        if self.status == 'role_linked' and self.role_identifier:
            return f"{self.display_prefix} {self.group.name}"
        return self.group.name
    
    def get_status_display_with_icon(self):
        """获取带图标的状态显示"""
        status_icons = {
            'role_linked': '🔗',
            'orphaned': '⚠️',
            'system': '⚙️',
            'manual': '👤',
        }
        icon = status_icons.get(self.status, '❓')
        return f"{icon} {self.get_status_display()}"
    
    def mark_as_role_linked(self, role_identifier):
        """标记为已关联角色"""
        self.status = 'role_linked'
        self.role_identifier = role_identifier
        self.sync_status = 'synced'
        self.last_sync_time = timezone.now()
        self.sync_error_message = ''
        self.save()
    
    def mark_as_orphaned(self):
        """标记为孤立组"""
        self.status = 'orphaned'
        self.role_identifier = None
        self.sync_status = 'disabled'
        self.save()
    
    def mark_sync_failed(self, error_message):
        """标记同步失败"""
        self.sync_status = 'failed'
        self.sync_error_message = error_message
        self.save()
    
    def __str__(self) -> str:
        return f"{self.get_display_name()} ({self.get_status_display()})"


class RoleGroupMapping(models.Model):
    """角色组映射配置"""
    role = models.CharField('角色', max_length=50, unique=True, help_text='角色标识符，支持自定义角色名称')
    group = models.OneToOneField(Group, on_delete=models.CASCADE, verbose_name='Django组')
    auto_sync = models.BooleanField('自动同步', default=True, help_text='用户角色变更时自动分配到对应组')
    is_active = models.BooleanField('是否启用', default=True, help_text='映射是否启用')
    priority = models.IntegerField('优先级', default=0, help_text='同步优先级，数字越大优先级越高')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '角色组映射'
        verbose_name_plural = '角色组映射配置'
        ordering = ['-priority', 'role']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
        ]

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
    
    def sync_group_identifier(self):
        """同步组标识信息"""
        try:
            identifier, created = GroupRoleIdentifier.objects.get_or_create(
                group=self.group,
                defaults={
                    'status': 'role_linked',
                    'role_identifier': self.role,
                    'sync_status': 'synced',
                    'last_sync_time': timezone.now(),
                    'is_auto_managed': True,
                }
            )
            
            if not created:
                identifier.mark_as_role_linked(self.role)
            
            return identifier
        except Exception as e:
            # 如果标识符存在，标记同步失败
            try:
                identifier = GroupRoleIdentifier.objects.get(group=self.group)
                identifier.mark_sync_failed(str(e))
            except GroupRoleIdentifier.DoesNotExist:
                pass
            raise e
    
    def _sync_permissions_to_group(self):
        """同步权限到Django组"""
        try:
            # 获取对应的RoleManagement实例
            role_mgmt = RoleManagement.objects.get(role=self.role)
            
            # 清除组的现有权限
            self.group.permissions.clear()
            
            # 获取角色的所有权限（包括继承的）
            all_permissions = role_mgmt.get_all_permissions()
            
            # 添加权限到组
            self.group.permissions.set(all_permissions)
            
            logger.info(f"已为组 {self.group.name} 同步 {len(all_permissions)} 个权限")
            return True
            
        except RoleManagement.DoesNotExist:
            logger.warning(f"角色 {self.role} 在RoleManagement中不存在，无法同步权限")
            return False
        except Exception as e:
            logger.error(f"同步权限到组失败: {str(e)}")
            return False
    
    def sync_permissions_to_group(self):
        """公开的权限同步方法"""
        return self._sync_permissions_to_group()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 保存后自动同步组标识
        if self.is_active:
            self.sync_group_identifier()
            # 如果启用自动同步，同步权限
            if self.auto_sync:
                self._sync_permissions_to_group()

    def __str__(self) -> str:
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.get_role_display()} → {self.group.name}"


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
    
    def __str__(self) -> str:
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
    
    def __str__(self) -> str:
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
    
    def __str__(self) -> str:
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
    
    def __str__(self) -> str:
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
    
    def __str__(self) -> str:
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
    
    def __str__(self) -> str:
        return str(self.name)
    
    def get_full_name(self):
        """获取部门全名（包含上级部门）"""
        names = []
        current = self
        while current:
            names.append(str(current.name))
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
        ids = [self.pk]
        for child in self.get_descendants():
            ids.append(child.pk)
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
    
    def __str__(self) -> str:
        primary_text = '(主)' if self.is_primary else ''
        return f"{str(self.user.username)} - {str(self.department.name)}{primary_text}"


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
        return str(self.display_name or self.role)

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

    def __str__(self) -> str:
        hierarchy_prefix = "  " * self.get_hierarchy_level()
        return f"{hierarchy_prefix}{str(self.display_name)} ({str(self.get_role_display())})"


# FrontendMenuConfig 模型已删除，功能由 MenuModuleConfig 替代
# FrontendMenuRoleAssignment 模型已删除，功能由槽位系统替代


class RoleSlotMenuAssignment(models.Model):
    """角色槽位菜单分配 - 基于槽位数量的新菜单分配系统"""
    
    MENU_STATUS_CHOICES = [
        ('active', '当前激活'),
        ('backup', '候补菜单'),
        ('disabled', '已禁用'),
    ]
    
    role = models.CharField(
        '角色',
        max_length=50,
        help_text='角色标识符，支持预定义和自定义角色'
    )
    slot_position = models.IntegerField(
        '槽位位置',
        help_text='在底部导航中的位置（1-5），根据角色槽位配置确定'
    )
    root_menu = models.ForeignKey(
        MenuModuleConfig,
        on_delete=models.CASCADE,
        limit_choices_to={'menu_level': 'root'},
        verbose_name='根菜单',
        help_text='分配的根级菜单'
    )
    menu_status = models.CharField(
        '菜单状态',
        max_length=20,
        choices=MENU_STATUS_CHOICES,
        default='active',
        help_text='菜单的激活状态：当前激活、候补菜单或已禁用'
    )
    is_active = models.BooleanField(
        '是否启用',
        default=True,
        help_text='该槽位分配是否启用'
    )
    sort_order = models.IntegerField(
        '排序',
        default=0,
        help_text='同一槽位内的排序'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色槽位菜单分配'
        verbose_name_plural = '角色槽位菜单分配管理'
        unique_together = ['role', 'slot_position', 'root_menu']
        ordering = ['role', 'slot_position', 'sort_order']
        indexes = [
            models.Index(fields=['role', 'slot_position']),
            models.Index(fields=['menu_status', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def get_role_display(self) -> str:
        """获取角色显示名称"""
        from apps.accounts.services.role_service import RoleService
        try:
            roles = RoleService.get_all_roles()
            for role_data in roles:
                if role_data['code'] == self.role:
                    return role_data['display_name']
            return self.role
        except Exception:
            return self.role
    
    def get_slot_info(self):
        """获取槽位信息"""
        max_slots = SlotConfig.get_slot_count_for_role(self.role)
        return {
            'current_position': self.slot_position,
            'max_slots': max_slots,
            'is_valid': self.slot_position <= max_slots
        }
    
    def clean(self):
        """验证槽位有效性"""
        super().clean()
        
        # 验证槽位位置不能超过该角色的最大槽位数
        max_slots = SlotConfig.get_slot_count_for_role(self.role)
        if self.slot_position > max_slots:
            raise ValidationError(
                f'槽位位置 {self.slot_position} 超出角色 {self.get_role_display()} 的最大槽位数 {max_slots}'
            )
        
        # 验证根菜单必须是根级菜单
        if self.root_menu and self.root_menu.parent is not None:
            raise ValidationError('只能分配根级菜单')
    
    def __str__(self) -> str:
        return f"{self.get_role_display()} - 槽位{self.slot_position} - {self.root_menu.name}"


class RoleSlotLevel1MenuAssignment(models.Model):
    """角色槽位一级菜单分配"""
    
    role_slot_assignment = models.ForeignKey(
        RoleSlotMenuAssignment,
        on_delete=models.CASCADE,
        related_name='level1_assignments',
        verbose_name='槽位分配'
    )
    level1_menu = models.ForeignKey(
        MenuModuleConfig,
        on_delete=models.CASCADE,
        limit_choices_to={'menu_level': 'level1'},
        verbose_name='一级菜单',
        help_text='分配的一级菜单'
    )
    is_active = models.BooleanField(
        '是否启用',
        default=True,
        help_text='该一级菜单是否启用'
    )
    sort_order = models.IntegerField(
        '排序',
        default=0,
        help_text='一级菜单的排序'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色槽位一级菜单分配'
        verbose_name_plural = '角色槽位根菜单和一级菜单分配管理'
        unique_together = ['role_slot_assignment', 'level1_menu']
        ordering = ['role_slot_assignment', 'sort_order']
    
    def clean(self):
        """验证一级菜单必须是根菜单的子菜单"""
        super().clean()
        
        if self.level1_menu and self.role_slot_assignment:
            if self.level1_menu.parent != self.role_slot_assignment.root_menu:
                raise ValidationError(
                    f'一级菜单 {self.level1_menu.name} 必须是根菜单 {self.role_slot_assignment.root_menu.name} 的子菜单'
                )
    
    def __str__(self) -> str:
        return f"{self.role_slot_assignment} - {self.level1_menu.name}"


class RoleSlotLevel2MenuAssignment(models.Model):
    """角色槽位二级菜单分配"""
    
    level1_assignment = models.ForeignKey(
        RoleSlotLevel1MenuAssignment,
        on_delete=models.CASCADE,
        related_name='level2_assignments',
        verbose_name='一级菜单分配'
    )
    level2_menu = models.ForeignKey(
        MenuModuleConfig,
        on_delete=models.CASCADE,
        limit_choices_to={'menu_level': 'level2'},
        verbose_name='二级菜单',
        help_text='分配的二级菜单'
    )
    is_active = models.BooleanField(
        '是否启用',
        default=True,
        help_text='该二级菜单是否启用'
    )
    sort_order = models.IntegerField(
        '排序',
        default=0,
        help_text='二级菜单的排序'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色槽位二级菜单分配'
        verbose_name_plural = '角色槽位二级菜单分配管理'
        unique_together = ['level1_assignment', 'level2_menu']
        ordering = ['level1_assignment', 'sort_order']
    
    def clean(self):
        """验证二级菜单必须是一级菜单的子菜单"""
        super().clean()
        
        if self.level2_menu and self.level1_assignment:
            if self.level2_menu.parent != self.level1_assignment.level1_menu:
                raise ValidationError(
                    f'二级菜单 {self.level2_menu.name} 必须是一级菜单 {self.level1_assignment.level1_menu.name} 的子菜单'
                )
    
    def __str__(self) -> str:
        return f"{self.level1_assignment} - {self.level2_menu.name}"


# PermissionSyncLog 模型已移至 models_optimized.py