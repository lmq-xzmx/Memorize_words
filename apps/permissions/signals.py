from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import RoleGroupMapping, RoleManagement
from .models_optimized import PermissionSyncLog
from .models_optimized import OptimizedRoleGroupMapping, AutoSyncConfig
from apps.accounts.models import UserRole, RoleExtension, CustomUser
from apps.accounts.services.role_service import RoleService
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db import models

logger = logging.getLogger(__name__)


# RoleMenuPermission 信号处理已被移除（模型已废弃）
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


@receiver(post_save, sender=RoleGroupMapping)
def sync_role_group_mapping(sender, instance, created, **kwargs):
    """角色组映射变更时同步"""
    try:
        # 确保组存在
        group, group_created = Group.objects.get_or_create(name=instance.group.name)
        
        if group_created:
            logger.info(f"创建新组: {instance.group.name}")
        
        # 记录同步日志
        PermissionSyncLog.objects.create(  # type: ignore
            sync_type='auto',
            target_type='role',
            target_id=instance.role,
            operation=f'角色组映射同步: {instance.group.name}',
            result=f'角色组映射 {instance.group.name} 已同步',
            is_success=True
        )
        logger.info(f"角色 {instance.get_role_display()} 的组映射 {instance.group.name} 已同步")
    except Exception as e:
        logger.error(f"同步角色组映射失败: {e}")
        PermissionSyncLog.objects.create(  # type: ignore
            sync_type='auto',
            target_type='role',
            target_id=instance.role,
            operation=f'角色组映射同步失败: {instance.group.name}',
            result=f'同步失败: {str(e)}',
            is_success=False
        )


@receiver(post_delete, sender=RoleGroupMapping)
def cleanup_role_group_mapping(sender, instance, **kwargs):
    """角色组映射删除时清理"""
    try:
        logger.info(f"角色组映射 {instance.role} -> {instance.group.name} 已删除")
    except Exception as e:
        logger.error(f"清理角色组映射失败: {e}")


def create_default_permissions():
    """创建默认权限"""
    # 获取所有内容类型
    content_types = ContentType.objects.all()
    
    # 为每个内容类型创建基本权限
    for ct in content_types:
        Permission.objects.get_or_create(
            codename=f'view_{ct.model}',
            name=f'Can view {ct.name}',
            content_type=ct
        )
        Permission.objects.get_or_create(
            codename=f'add_{ct.model}',
            name=f'Can add {ct.name}',
            content_type=ct
        )
        Permission.objects.get_or_create(
            codename=f'change_{ct.model}',
            name=f'Can change {ct.name}',
            content_type=ct
        )
        Permission.objects.get_or_create(
            codename=f'delete_{ct.model}',
            name=f'Can delete {ct.name}',
            content_type=ct
        )


def sync_all_permissions():
    """同步所有权限"""
    # 同步所有角色组映射
    for mapping in RoleGroupMapping.objects.filter(auto_sync=True):  # type: ignore
        Group.objects.get_or_create(name=mapping.group.name)


def initialize_role_group_mappings():
    """初始化角色组映射"""
    for mapping in RoleGroupMapping.objects.all():  # type: ignore
        Group.objects.get_or_create(name=mapping.group.name)


@receiver(post_save, sender=RoleManagement)
def create_role_extension_on_role_creation(sender, instance, created, **kwargs):
    """角色创建时自动创建角色扩展配置"""
    if created:
        try:
            # 获取角色的默认扩展配置
            default_extensions = get_default_extensions_for_role(instance.role)
            
            # 创建或获取角色扩展
            extension, created = RoleExtension.objects.get_or_create(  # type: ignore
                role=instance.role,
                defaults=default_extensions
            )
            
            if created:
                # 记录成功日志
                PermissionSyncLog.objects.create(  # type: ignore
                    sync_type='auto',
                    target_type='role',
                    target_id=instance.role,
                    operation='create',
                    result=f'为角色 {instance.display_name} 创建了扩展配置',
                    is_success=True
                )
                logger.info(f"为角色 {instance.display_name} 创建了扩展配置")
            else:
                logger.info(f"角色 {instance.display_name} 的扩展配置已存在")
                
        except Exception as e:
            logger.error(f"为角色 {instance.display_name} 创建扩展配置失败: {e}")
            # 记录失败日志
            PermissionSyncLog.objects.create(  # type: ignore
                sync_type='auto',
                target_type='role',
                target_id=instance.role,
                operation='create',
                result=f'创建失败: {str(e)}',
                is_success=False
            )


@receiver(post_save, sender=RoleManagement)
def create_role_group_mapping_on_role_creation(sender, instance, created, **kwargs):
    """角色创建时自动创建角色组映射"""
    if created:
        try:
            # 检查是否已存在组映射
            if not RoleGroupMapping.objects.filter(role=instance.role).exists():  # type: ignore
                # 创建组映射
                group_name = f"role_{instance.role}"
                group, group_created = Group.objects.get_or_create(name=group_name)
                
                # 创建角色组映射
                mapping = RoleGroupMapping.objects.create(
                    role=instance.role,
                    group=group,
                    auto_sync=True
                )
                
                # 同步权限
                try:
                    # 获取角色的所有权限（包括继承的）
                    all_permissions = instance.get_all_permissions()
                    
                    # 清除组的现有权限
                    group.permissions.clear()
                    
                    # 添加权限到组
                    if all_permissions:
                        group.permissions.set(all_permissions)
                    
                    perm_count = len(all_permissions) if all_permissions else 0
                    logger.info(f"已为组 {group.name} 同步 {perm_count} 个权限")
                except Exception as sync_error:
                    logger.error(f"同步权限到组失败: {sync_error}")
                
                # 记录成功日志
                PermissionSyncLog.objects.create(  # type: ignore
                    sync_type='auto',
                    target_type='role',
                    target_id=instance.role,
                    operation='create',
                    result=f'为角色 {instance.display_name} 创建了组映射 {group_name} 并同步权限',
                    is_success=True
                )
                logger.info(f"为角色 {instance.display_name} 创建了组映射 {group_name}")
            else:
                logger.info(f"角色 {instance.display_name} 的组映射已存在")
                
        except Exception as e:
            logger.error(f"为角色 {instance.display_name} 创建组映射失败: {e}")
            # 记录失败日志
            PermissionSyncLog.objects.create(  # type: ignore
                sync_type='auto',
                target_type='role',
                target_id=instance.role,
                operation='create',
                result=f'创建失败: {str(e)}',
                is_success=False
            )


@receiver(post_delete, sender=RoleManagement)
def refresh_cache_on_role_deletion(sender, instance, **kwargs):
    """角色删除时刷新缓存"""
    try:
        # 清理相关缓存
        from django.core.cache import cache
        cache.delete_many([f'role_{instance.role}', f'permissions_{instance.role}'])
        logger.info(f"角色 {instance.role} 删除后缓存已清理")
    except Exception as e:
        logger.error(f"清理角色缓存失败: {e}")


def get_default_extensions_for_role(role):
    """获取角色的默认扩展配置"""
    base_config = {
        'max_login_attempts': 5,
        'session_timeout_minutes': 30,
        'password_expiry_days': 90,
        'require_2fa': False,
        'allowed_ip_ranges': [],
        'max_concurrent_sessions': 3
    }
    
    role_specific_configs = {
        'admin': {
            **base_config,
            'max_login_attempts': 10,
            'session_timeout_minutes': 60,
            'require_2fa': True,
            'max_concurrent_sessions': 5
        },
        'teacher': {
            **base_config,
            'session_timeout_minutes': 45,
            'max_concurrent_sessions': 3
        },
        'student': {
            **base_config,
            'session_timeout_minutes': 20,
            'max_concurrent_sessions': 2
        },
        'parent': {
            **base_config,
            'session_timeout_minutes': 30,
            'max_concurrent_sessions': 2
        },
        'guest': {
            **base_config,
            'max_login_attempts': 3,
            'session_timeout_minutes': 15,
            'max_concurrent_sessions': 1
        },
        'moderator': {
            **base_config,
            'session_timeout_minutes': 45,
            'require_2fa': True,
            'max_concurrent_sessions': 3
        },
        'content_creator': {
            **base_config,
            'session_timeout_minutes': 60,
            'max_concurrent_sessions': 3
        },
        'analyst': {
            **base_config,
            'session_timeout_minutes': 45,
            'max_concurrent_sessions': 2
        },
        'support': {
            **base_config,
            'session_timeout_minutes': 45,
            'max_concurrent_sessions': 3
        },
        'reviewer': {
            **base_config,
            'session_timeout_minutes': 30,
            'max_concurrent_sessions': 2
        }
    }
    
    return role_specific_configs.get(role, base_config)


# 用户角色变更检测
_user_role_cache = {}


@receiver(post_save, sender=CustomUser)
def auto_sync_user_permissions(sender, instance, created, **kwargs):
    """用户保存时自动同步权限"""
    try:
        # 获取自动同步配置
        config = AutoSyncConfig.objects.first()  # type: ignore
        if not config or not config.sync_on_user_save:
            return
            
        # 获取用户对象
        try:
            user = CustomUser.objects.get(id=instance.id)
        except CustomUser.DoesNotExist:  # type: ignore
            logger.warning(f"用户 {instance.id} 不存在，跳过权限同步")
            return
        
        # 获取自动同步配置
        config = AutoSyncConfig.objects.first()  # type: ignore
        if not config or not config.auto_sync_enabled:
            return
            
        # 同步用户到对应的组
        try:
            mapping = OptimizedRoleGroupMapping.objects.get(role=user.role)  # type: ignore
            user.groups.clear()
            user.groups.add(mapping.group)
        except OptimizedRoleGroupMapping.DoesNotExist:  # type: ignore
            logger.warning(f"用户 {user.username} 的角色 {user.role} 没有对应的组映射")
            
        logger.info(f"用户 {user.username} 的权限已同步")
        
    except Exception as e:
        logger.error(f"同步用户权限失败: {e}")


@receiver(pre_save, sender=CustomUser)
def detect_role_change(sender, instance, **kwargs):
    """检测用户角色变更"""
    if instance.pk:
        try:
            old_instance = CustomUser.objects.get(pk=instance.pk)
            _user_role_cache[instance.pk] = old_instance.role
        except CustomUser.DoesNotExist:  # type: ignore
            pass


@receiver(post_save, sender=CustomUser)
def handle_role_change_sync(sender, instance, created, **kwargs):
    """处理用户角色变更后的权限同步"""
    if not created and instance.pk in _user_role_cache:
        old_role = _user_role_cache.pop(instance.pk)
        if old_role != instance.role:
            try:
                # 获取自动同步配置
                config = AutoSyncConfig.objects.first()  # type: ignore
                if config and config.sync_on_role_change:
                    # 使用角色服务进行权限同步
                    role_service = RoleService()
                    role_service.sync_user_permissions(instance)
                    
                    logger.info(f"用户 {instance.username} 角色从 {old_role} 变更为 {instance.role}，权限已同步")
                    
                    # 发送WebSocket通知
                    try:
                        from .websocket_service import notification_service
                        notification_data = {
                            'type': 'role_change',
                            'user_id': instance.id,
                            'old_role': old_role,
                            'new_role': instance.role,
                            'timestamp': str(timezone.now())
                        }
                        notification_service.notify_role_change(instance.id, notification_data)
                    except ImportError:
                        logger.warning("WebSocket通知服务不可用")
                    except Exception as e:
                        logger.error(f"发送角色变更通知失败: {e}")
                        
            except Exception as e:
                logger.error(f"处理用户角色变更失败: {e}")


@receiver(post_save, sender=OptimizedRoleGroupMapping)
def auto_sync_role_group_mapping(sender, instance, created, **kwargs):
    """优化角色组映射变更时自动同步"""
    try:
        # 获取自动同步配置
        config = AutoSyncConfig.objects.first()  # type: ignore
        if not config or not config.auto_sync_enabled:
            return
            
        # 确保组存在
        group, group_created = Group.objects.get_or_create(name=instance.group.name)
        
        if group_created:
            logger.info(f"创建新组: {instance.group.name}")
            
        # 同步权限
        if hasattr(instance, '_sync_permissions_to_group'):
            instance._sync_permissions_to_group()
            
        logger.info(f"优化角色组映射 {instance.role} -> {instance.group.name} 已同步")
        
    except Exception as e:
        logger.error(f"同步优化角色组映射失败: {e}")


def create_default_auto_sync_config():
    """创建默认的自动同步配置"""
    AutoSyncConfig.objects.get_or_create(  # type: ignore
        defaults={
            'auto_sync_enabled': True,
            'sync_on_role_change': True,
            'sync_on_user_save': True,
            'sync_interval_minutes': 60,
            'max_sync_retries': 3,
            'enable_notifications': True,
            'notification_channels': ['websocket', 'email'],
            'batch_size': 100,
            'sync_timeout_seconds': 300,
            'enable_audit_log': True,
            'log_level': 'INFO',
            'enable_cache_invalidation': True,
            'cache_timeout_seconds': 3600
        }
    )


def setup_permissions_system():
    """设置权限系统"""
    create_default_permissions()
    initialize_role_group_mappings()
    create_default_auto_sync_config()
    sync_all_permissions()


# FrontendMenuRoleAssignment 信号处理已被移除（模型已废弃）
# 请使用 MenuModuleConfig 和相关槽位系统替代


# FrontendMenuRoleAssignment 删除信号处理已被移除（模型已废弃）
# 请使用 MenuModuleConfig 和相关槽位系统替代