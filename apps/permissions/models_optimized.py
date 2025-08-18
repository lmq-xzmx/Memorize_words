from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.accounts.models import CustomUser, UserRole
import json
import logging

logger = logging.getLogger(__name__)


class OptimizedRoleGroupMapping(models.Model):
    """优化的角色组映射 - 权限同步层"""
    
    SYNC_STATUS_CHOICES = [
        ('pending', '待同步'),
        ('syncing', '同步中'),
        ('success', '同步成功'),
        ('failed', '同步失败'),
    ]
    
    role = models.CharField(max_length=50, choices=UserRole.choices, unique=True, help_text="角色类型")
    group = models.OneToOneField(Group, on_delete=models.CASCADE, help_text="对应的Django组")
    
    # 同步配置
    auto_sync = models.BooleanField(default=True, help_text="是否自动同步")
    sync_permissions = models.BooleanField(default=True, help_text="是否同步权限")
    sync_users = models.BooleanField(default=True, help_text="是否同步用户")
    
    # 权限配置
    base_permissions = models.JSONField(default=dict, help_text="基础权限配置")
    menu_permissions = models.JSONField(default=dict, help_text="菜单权限配置")
    custom_permissions = models.JSONField(default=dict, help_text="自定义权限配置")
    
    # 同步状态
    last_sync_status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, default='pending', help_text="最后同步状态")
    last_sync_time = models.DateTimeField(null=True, blank=True, help_text="最后同步时间")
    sync_error_message = models.TextField(blank=True, help_text="同步错误信息")
    sync_count = models.IntegerField(default=0, help_text="同步次数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'optimized_role_group_mapping'
        verbose_name = '优化角色组映射'
        verbose_name_plural = '优化角色组映射'
        ordering = ['role']
    
    def get_sync_status_display_name(self):
        """获取同步状态显示名称"""
        return dict(self.SYNC_STATUS_CHOICES).get(self.last_sync_status, '未知')
    
    def set_base_permissions(self, permissions_dict):
        """设置基础权限"""
        self.base_permissions = {
            'permissions': permissions_dict,
            'updated_at': timezone.now().isoformat()
        }
    
    def set_menu_permissions(self, menu_list):
        """设置菜单权限"""
        self.menu_permissions = {
            'menus': menu_list,
            'updated_at': timezone.now().isoformat()
        }
    
    def set_custom_permissions(self, permissions_dict):
        """设置自定义权限"""
        self.custom_permissions = {
            'permissions': permissions_dict,
            'updated_at': timezone.now().isoformat()
        }
    
    def get_base_permissions_dict(self):
        """获取基础权限字典"""
        if isinstance(self.base_permissions, dict):
            return self.base_permissions.get('permissions', {})
        return {}
    
    def get_menu_permissions_list(self):
        """获取菜单权限列表"""
        if isinstance(self.menu_permissions, dict):
            return self.menu_permissions.get('menus', [])
        return []
    
    def get_custom_permissions_dict(self):
        """获取自定义权限字典"""
        if isinstance(self.custom_permissions, dict):
            return self.custom_permissions.get('permissions', {})
        return {}
    
    def get_all_permissions(self):
        """获取所有权限"""
        all_perms = {}
        all_perms.update(self.get_base_permissions_dict())
        all_perms.update(self.get_custom_permissions_dict())
        return all_perms
    
    def sync_to_django_group(self):
        """同步到Django组"""
        if not self.auto_sync:
            return False, "自动同步已禁用"
        
        try:
            self.last_sync_status = 'syncing'
            self.save(update_fields=['last_sync_status'])
            
            # 同步权限
            if self.sync_permissions:
                self._sync_permissions_to_group()
            
            # 同步用户
            if self.sync_users:
                self._sync_users_to_group()
            
            # 更新同步状态
            self.last_sync_status = 'success'
            self.last_sync_time = timezone.now()
            self.sync_error_message = ''
            self.sync_count += 1
            self.save(update_fields=['last_sync_status', 'last_sync_time', 'sync_error_message', 'sync_count'])
            
            # 记录同步日志
            PermissionSyncLog.objects.create(
                sync_type='role_group_sync',
                target_type='group',
                target_id=str(self.group.id),
                operation='sync',
                result=f"角色 {self.role} 同步到组 {self.group.name} 成功",
                is_success=True
            )
            
            return True, "同步成功"
            
        except Exception as e:
            error_msg = str(e)
            self.last_sync_status = 'failed'
            self.sync_error_message = error_msg
            self.save(update_fields=['last_sync_status', 'sync_error_message'])
            
            # 记录错误日志
            PermissionSyncLog.objects.create(
                sync_type='role_group_sync',
                target_type='group',
                target_id=str(self.group.id),
                operation='sync',
                result=f"角色 {self.role} 同步到组 {self.group.name} 失败: {error_msg}",
                is_success=False
            )
            
            logger.error(f"角色组映射同步失败: {error_msg}")
            return False, error_msg
    
    def _sync_permissions_to_group(self):
        """同步权限到组"""
        # 清除现有权限
        self.group.permissions.clear()
        
        # 获取所有权限
        all_permissions = self.get_all_permissions()
        
        # 添加权限到组
        for perm_codename, has_perm in all_permissions.items():
            if has_perm:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    self.group.permissions.add(permission)
                except Permission.DoesNotExist:
                    logger.warning(f"权限 {perm_codename} 不存在")
                    continue
    
    def _sync_users_to_group(self):
        """同步用户到组"""
        # 获取该角色的所有用户
        users = CustomUser.objects.filter(role=self.role, is_active=True)
        
        # 清除组中现有用户
        self.group.user_set.clear()
        
        # 添加用户到组
        for user in users:
            self.group.user_set.add(user)
    
    def auto_configure_for_role(self):
        """根据角色自动配置权限"""
        role_permissions = {
            'student': {
                'base': {
                    'view_own_profile': True,
                    'change_own_profile': True,
                    'view_learning_progress': True,
                    'add_learning_record': True,
                },
                'menus': ['dashboard', 'learning_center', 'vocabulary_practice']
            },
            'parent': {
                'base': {
                    'view_own_profile': True,
                    'change_own_profile': True,
                    'view_child_progress': True,
                    'view_learning_reports': True,
                },
                'menus': ['dashboard', 'learning_center', 'progress_tracking', 'reports']
            },
            'teacher': {
                'base': {
                    'view_own_profile': True,
                    'change_own_profile': True,
                    'view_student_progress': True,
                    'add_teaching_plan': True,
                    'change_teaching_plan': True,
                    'view_vocabulary': True,
                    'add_vocabulary': True,
                    'change_vocabulary': True,
                },
                'menus': ['dashboard', 'teaching_management', 'vocabulary_management', 'student_management']
            },
            'admin': {
                'base': {
                    'view_all': True,
                    'add_all': True,
                    'change_all': True,
                    'delete_all': True,
                },
                'menus': ['*']  # 所有菜单
            }
        }
        
        config = role_permissions.get(self.role, role_permissions['student'])
        
        self.set_base_permissions(config['base'])
        self.set_menu_permissions(config['menus'])
    
    @classmethod
    def create_for_role(cls, role, group_name=None):
        """为角色创建映射"""
        if not group_name:
            group_name = f"{dict(UserRole.choices).get(role, role)}组"
        
        # 创建或获取Django组
        group, created = Group.objects.get_or_create(name=group_name)
        
        # 创建映射
        mapping, created = cls.objects.get_or_create(
            role=role,
            defaults={'group': group}
        )
        
        if created:
            # 自动配置权限
            mapping.auto_configure_for_role()
            mapping.save()
            
            # 执行初始同步
            mapping.sync_to_django_group()
        
        return mapping, created
    
    def __str__(self):
        return f"{dict(UserRole.choices).get(self.role, self.role)} -> {self.group.name}"


class PermissionSyncLog(models.Model):
    """权限同步日志"""
    
    SYNC_TYPE_CHOICES = [
        ('role_group_sync', '角色组同步'),
        ('user_permission_sync', '用户权限同步'),
        ('menu_permission_sync', '菜单权限同步'),
        ('bulk_sync', '批量同步'),
        ('manual_sync', '手动同步'),
    ]
    
    TARGET_TYPE_CHOICES = [
        ('user', '用户'),
        ('group', '组'),
        ('role', '角色'),
        ('menu', '菜单'),
        ('system', '系统'),
    ]
    
    OPERATION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('sync', '同步'),
        ('assign', '分配'),
        ('revoke', '撤销'),
    ]
    
    sync_type = models.CharField(max_length=50, choices=SYNC_TYPE_CHOICES, help_text="同步类型")
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES, help_text="目标类型")
    target_id = models.CharField(max_length=100, help_text="目标ID")
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES, help_text="操作类型")
    
    result = models.TextField(help_text="同步结果")
    is_success = models.BooleanField(help_text="是否成功")
    
    # 额外信息
    extra_data = models.JSONField(default=dict, blank=True, help_text="额外数据")
    duration_ms = models.IntegerField(null=True, blank=True, help_text="执行时长（毫秒）")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_sync_logs',
        verbose_name='操作人'
    )
    
    class Meta:
        db_table = 'permission_sync_log'
        verbose_name = '权限同步日志'
        verbose_name_plural = '权限同步日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sync_type', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['is_success', 'created_at']),
        ]
    
    def get_sync_type_display_name(self):
        """获取同步类型显示名称"""
        return dict(self.SYNC_TYPE_CHOICES).get(self.sync_type, '未知')
    
    def get_target_type_display_name(self):
        """获取目标类型显示名称"""
        return dict(self.TARGET_TYPE_CHOICES).get(self.target_type, '未知')
    
    def get_operation_display_name(self):
        """获取操作类型显示名称"""
        return dict(self.OPERATION_CHOICES).get(self.operation, '未知')
    
    def set_extra_data(self, data_dict):
        """设置额外数据"""
        self.extra_data = data_dict
    
    def get_extra_data_dict(self):
        """获取额外数据字典"""
        if isinstance(self.extra_data, dict):
            return self.extra_data
        return {}
    
    @classmethod
    def log_sync_operation(cls, sync_type, target_type, target_id, operation, result, is_success, created_by=None, extra_data=None, duration_ms=None):
        """记录同步操作"""
        return cls.objects.create(
            sync_type=sync_type,
            target_type=target_type,
            target_id=str(target_id),
            operation=operation,
            result=result,
            is_success=is_success,
            created_by=created_by,
            extra_data=extra_data or {},
            duration_ms=duration_ms
        )
    
    @classmethod
    def get_recent_logs(cls, limit=50):
        """获取最近的日志"""
        return cls.objects.all()[:limit]
    
    @classmethod
    def get_failed_logs(cls, limit=50):
        """获取失败的日志"""
        return cls.objects.filter(is_success=False)[:limit]
    
    @classmethod
    def get_logs_by_target(cls, target_type, target_id, limit=20):
        """根据目标获取日志"""
        return cls.objects.filter(
            target_type=target_type,
            target_id=str(target_id)
        )[:limit]
    
    def __str__(self):
        status = "成功" if self.is_success else "失败"
        return f"{self.get_sync_type_display_name()} - {self.get_operation_display_name()} - {status}"


class AutoSyncConfig(models.Model):
    """自动同步配置"""
    
    # 全局开关
    enable_auto_sync = models.BooleanField(default=True, help_text="是否启用自动同步")
    
    # 同步策略
    sync_on_user_create = models.BooleanField(default=True, help_text="用户创建时同步")
    sync_on_user_update = models.BooleanField(default=True, help_text="用户更新时同步")
    sync_on_role_change = models.BooleanField(default=True, help_text="角色变更时同步")
    sync_on_permission_change = models.BooleanField(default=True, help_text="权限变更时同步")
    
    # 同步频率
    auto_sync_interval_minutes = models.IntegerField(default=60, help_text="自动同步间隔（分钟）")
    batch_sync_size = models.IntegerField(default=100, help_text="批量同步大小")
    
    # 错误处理
    max_retry_attempts = models.IntegerField(default=3, help_text="最大重试次数")
    retry_delay_seconds = models.IntegerField(default=30, help_text="重试延迟（秒）")
    
    # 通知配置
    notify_on_sync_failure = models.BooleanField(default=True, help_text="同步失败时通知")
    notification_emails = models.JSONField(default=list, help_text="通知邮箱列表")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auto_sync_config'
        verbose_name = '自动同步配置'
        verbose_name_plural = '自动同步配置'
    
    def get_notification_emails_list(self):
        """获取通知邮箱列表"""
        if isinstance(self.notification_emails, list):
            return self.notification_emails
        return []
    
    def should_sync_on_event(self, event_type):
        """判断是否应该在特定事件时同步"""
        if not self.enable_auto_sync:
            return False
        
        event_mapping = {
            'user_create': self.sync_on_user_create,
            'user_update': self.sync_on_user_update,
            'role_change': self.sync_on_role_change,
            'permission_change': self.sync_on_permission_change,
        }
        
        return event_mapping.get(event_type, False)
    
    def __str__(self):
        status = "启用" if self.enable_auto_sync else "禁用"
        return f"自动同步配置 - {status}"


# 权限同步工具函数
def sync_all_role_groups():
    """同步所有角色组"""
    results = []
    
    for mapping in OptimizedRoleGroupMapping.objects.filter(auto_sync=True):
        success, message = mapping.sync_to_django_group()
        results.append({
            'role': mapping.role,
            'group': mapping.group.name,
            'success': success,
            'message': message
        })
    
    return results


def sync_user_to_role_group(user):
    """将用户同步到对应的角色组"""
    try:
        mapping = OptimizedRoleGroupMapping.objects.get(role=user.role)
        
        # 移除用户从其他组
        user.groups.clear()
        
        # 添加到对应组
        user.groups.add(mapping.group)
        
        # 记录日志
        PermissionSyncLog.log_sync_operation(
            sync_type='user_permission_sync',
            target_type='user',
            target_id=user.id,
            operation='assign',
            result=f"用户 {user.username} 同步到角色组 {mapping.group.name}",
            is_success=True
        )
        
        return True, f"用户同步到角色组 {mapping.group.name} 成功"
        
    except OptimizedRoleGroupMapping.DoesNotExist:
        error_msg = f"角色 {user.role} 的组映射不存在"
        
        # 记录错误日志
        PermissionSyncLog.log_sync_operation(
            sync_type='user_permission_sync',
            target_type='user',
            target_id=user.id,
            operation='assign',
            result=error_msg,
            is_success=False
        )
        
        return False, error_msg
    
    except Exception as e:
        error_msg = f"用户同步失败: {str(e)}"
        
        # 记录错误日志
        PermissionSyncLog.log_sync_operation(
            sync_type='user_permission_sync',
            target_type='user',
            target_id=user.id,
            operation='assign',
            result=error_msg,
            is_success=False
        )
        
        return False, error_msg