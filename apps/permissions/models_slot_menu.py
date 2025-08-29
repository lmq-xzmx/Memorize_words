from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.accounts.services.role_service import RoleService
from .models import SlotConfig, FrontendMenuConfig


class RoleSlotMenuAssignment(models.Model):
    """
    角色槽位菜单分配模型 - 基于槽位数量的新菜单角色分配系统
    
    设计理念：
    1. 穷举所有已存在的角色，列表形式排列
    2. 每个角色根据激活槽位数量，设置当前根菜单和候补根菜单
    3. 每个根菜单允许添加多个一级菜单，菜单值来自同一角色下的所有一级菜单
    4. 二级菜单亦同
    """
    
    MENU_STATUS_CHOICES = [
        ('active', '当前菜单'),
        ('backup', '候补菜单'),
        ('disabled', '已禁用'),
    ]
    
    # 基本信息
    role = models.CharField(
        '角色',
        max_length=50,
        help_text='角色标识符，支持预定义和自定义角色'
    )
    
    # 槽位配置
    slot_position = models.IntegerField(
        '槽位位置',
        help_text='在底部导航中的位置（1-5），基于角色的槽位数量限制'
    )
    
    # 根菜单配置
    root_menu = models.ForeignKey(
        FrontendMenuConfig,
        on_delete=models.CASCADE,
        related_name='root_assignments',
        verbose_name='根菜单',
        limit_choices_to={'parent__isnull': True},  # 只允许根菜单
        help_text='根级菜单配置'
    )
    
    # 菜单状态
    menu_status = models.CharField(
        '菜单状态',
        max_length=20,
        choices=MENU_STATUS_CHOICES,
        default='active',
        help_text='当前菜单：显示在前台；候补菜单：允许添加但不显示'
    )
    
    # 一级子菜单（多对多关系）
    level1_menus = models.ManyToManyField(
        FrontendMenuConfig,
        through='RoleSlotLevel1MenuAssignment',
        related_name='level1_assignments',
        blank=True,
        verbose_name='一级子菜单',
        help_text='该根菜单下的一级子菜单'
    )
    
    # 控制字段
    is_active = models.BooleanField(
        '是否启用',
        default=True,
        help_text='该槽位配置是否启用'
    )
    
    sort_order = models.IntegerField(
        '排序',
        default=0,
        help_text='同一槽位内的排序'
    )
    
    # 时间字段
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
            models.Index(fields=['role', 'menu_status']),
        ]
    
    def clean(self):
        """模型验证"""
        # 验证角色有效性
        valid_roles = [choice[0] for choice in RoleService.get_role_choices(include_empty=False)]
        if self.role not in valid_roles:
            raise ValidationError(f'无效的角色: {self.role}')
        
        # 验证根菜单
        if self.root_menu and self.root_menu.parent is not None:
            raise ValidationError('只能分配根级别的菜单')
        
        # 获取当前角色的最大槽位数量
        max_slots = SlotConfig.get_slot_count_for_role(self.role)
        
        # 验证槽位位置
        if self.slot_position < 1:
            raise ValidationError('槽位位置必须大于0')
        
        if self.slot_position > max_slots:
            raise ValidationError(f'槽位位置不能超过当前角色的最大槽位数量({max_slots})')
        
        # 验证当前菜单数量限制
        if self.menu_status == 'active':
            active_count = RoleSlotMenuAssignment.objects.filter(
                role=self.role,
                slot_position=self.slot_position,
                menu_status='active',
                is_active=True
            ).exclude(pk=self.pk).count()
            
            if active_count >= 1:
                raise ValidationError(f'槽位 {self.slot_position} 已有当前菜单，请先设置为候补菜单')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def get_role_display(self) -> str:
        """获取角色显示名称"""
        return RoleService.get_role_display_name(self.role)
    
    def get_slot_info(self):
        """获取槽位信息"""
        max_slots = SlotConfig.get_slot_count_for_role(self.role)
        return {
            'current_position': self.slot_position,
            'max_slots': max_slots,
            'is_valid': self.slot_position <= max_slots
        }
    
    def get_level1_menus_for_role(self):
        """获取该角色下可用的一级菜单"""
        # 获取同一角色下的所有一级菜单
        return FrontendMenuConfig.objects.filter(
            parent=self.root_menu,
            is_active=True
        ).order_by('sort_order', 'name')
    
    def __str__(self) -> str:
        status_display = dict(self.MENU_STATUS_CHOICES)[self.menu_status]
        return f"{self.get_role_display()} - 槽位{self.slot_position} - {self.root_menu.name} ({status_display})"


class RoleSlotLevel1MenuAssignment(models.Model):
    """
    角色槽位一级菜单分配 - 中间表，管理根菜单下的一级子菜单
    """
    
    role_slot_assignment = models.ForeignKey(
        RoleSlotMenuAssignment,
        on_delete=models.CASCADE,
        verbose_name='槽位分配'
    )
    
    level1_menu = models.ForeignKey(
        FrontendMenuConfig,
        on_delete=models.CASCADE,
        verbose_name='一级菜单',
        help_text='一级子菜单'
    )
    
    # 二级子菜单（多对多关系）
    level2_menus = models.ManyToManyField(
        FrontendMenuConfig,
        through='RoleSlotLevel2MenuAssignment',
        related_name='level2_assignments',
        blank=True,
        verbose_name='二级子菜单',
        help_text='该一级菜单下的二级子菜单'
    )
    
    is_active = models.BooleanField('是否启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '一级菜单分配'
        verbose_name_plural = '一级菜单分配管理'
        unique_together = ['role_slot_assignment', 'level1_menu']
        ordering = ['sort_order', 'level1_menu__sort_order']
    
    def clean(self):
        """验证一级菜单必须是根菜单的子菜单"""
        if self.level1_menu.parent != self.role_slot_assignment.root_menu:
            raise ValidationError('一级菜单必须是对应根菜单的子菜单')
    
    def get_level2_menus_for_role(self):
        """获取该一级菜单下可用的二级菜单"""
        return FrontendMenuConfig.objects.filter(
            parent=self.level1_menu,
            is_active=True
        ).order_by('sort_order', 'name')
    
    def __str__(self) -> str:
        return f"{self.role_slot_assignment.get_role_display()} - {self.level1_menu.name}"


class RoleSlotLevel2MenuAssignment(models.Model):
    """
    角色槽位二级菜单分配 - 中间表，管理一级菜单下的二级子菜单
    """
    
    level1_assignment = models.ForeignKey(
        RoleSlotLevel1MenuAssignment,
        on_delete=models.CASCADE,
        verbose_name='一级菜单分配'
    )
    
    level2_menu = models.ForeignKey(
        FrontendMenuConfig,
        on_delete=models.CASCADE,
        verbose_name='二级菜单',
        help_text='二级子菜单'
    )
    
    is_active = models.BooleanField('是否启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '二级菜单分配'
        verbose_name_plural = '二级菜单分配管理'
        unique_together = ['level1_assignment', 'level2_menu']
        ordering = ['sort_order', 'level2_menu__sort_order']
    
    def clean(self):
        """验证二级菜单必须是一级菜单的子菜单"""
        if self.level2_menu.parent != self.level1_assignment.level1_menu:
            raise ValidationError('二级菜单必须是对应一级菜单的子菜单')
    
    def __str__(self) -> str:
        return f"{self.level1_assignment.role_slot_assignment.get_role_display()} - {self.level2_menu.name}"