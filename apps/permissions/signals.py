from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import RoleMenuPermission, RoleGroupMapping, RoleManagement
from .models_optimized import PermissionSyncLog
from .models_optimized import OptimizedRoleGroupMapping, AutoSyncConfig
from apps.accounts.models import UserRole, RoleExtension, CustomUser
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=RoleMenuPermission)
def sync_role_menu_permission(sender, instance, created, **kwargs):
    """角色菜单权限变更时同步"""
    try:
        # 记录权限同步日志
        PermissionSyncLog.objects.create(
            sync_type='menu_permission_sync',
            target_type='role',
            target_id=instance.role,
            operation='sync',
            result=f'菜单权限 {instance.menu_module.name} 已同步',
            is_success=True
        )
        logger.info(f"角色 {instance.get_role_display()} 的菜单权限 {instance.menu_module.name} 已同步")
    except Exception as e:
        logger.error(f"同步角色菜单权限失败: {e}")
        PermissionSyncLog.objects.create(
            sync_type='menu_permission_sync',
            target_type='role',
            target_id=instance.role,
            operation='sync',
            result=f'同步失败: {str(e)}',
            is_success=False
        )


@receiver(post_save, sender=RoleGroupMapping)
def sync_role_group_mapping(sender, instance, created, **kwargs):
    """角色组映射变更时同步"""
    try:
        # 确保组存在
        group, group_created = Group.objects.get_or_create(name=instance.group.name)
        
        if group_created:
            logger.info(f"创建新组: {instance.group.name}")
        
        # 记录同步日志
        PermissionSyncLog.objects.create(
            sync_type='auto',
            target_type='role',
            target_id=instance.role,
            action=f'角色组映射同步: {instance.group.name}',
            result=f'角色组映射 {instance.group.name} 已同步',
            success=True
        )
        logger.info(f"角色 {instance.get_role_display()} 的组映射 {instance.group.name} 已同步")
    except Exception as e:
        logger.error(f"同步角色组映射失败: {e}")
        PermissionSyncLog.objects.create(
            sync_type='auto',
            target_type='role',
            target_id=instance.role,
            action=f'角色组映射同步失败: {instance.group.name}',
            result=f'同步失败: {str(e)}',
            success=False
        )


def create_default_permissions():
    """创建默认权限"""
    # 创建默认的角色组映射
    default_mappings = [
        (UserRole.ADMIN, '管理员组'),
        (UserRole.TEACHER, '教师组'),
        (UserRole.STUDENT, '学生组'),
        (UserRole.PARENT, '家长组'),
    ]
    
    for role, group_name in default_mappings:
        # 先创建或获取组
        group, group_created = Group.objects.get_or_create(name=group_name)
        
        # 创建角色组映射
        mapping, created = RoleGroupMapping.objects.get_or_create(
            role=role,
            defaults={'group': group, 'auto_sync': True}
        )
        if created:
            logger.info(f"创建默认角色组映射: {role} -> {group_name}")
    
    logger.info("默认权限创建完成")


def sync_all_permissions():
    """同步所有权限"""
    try:
        # 创建默认权限
        create_default_permissions()
        
        # 同步所有角色组映射
        for mapping in RoleGroupMapping.objects.filter(auto_sync=True):
            Group.objects.get_or_create(name=mapping.group.name)
        
        logger.info("所有权限同步完成")
        return True
    except Exception as e:
        logger.error(f"权限同步失败: {e}")
        return False


@receiver(post_save, sender=RoleManagement)
def create_role_extension_on_role_creation(sender, instance, created, **kwargs):
    """角色创建时自动创建对应的角色数据增项配置"""
    if created:
        try:
            # 根据不同角色创建默认的增项配置
            default_extensions = get_default_extensions_for_role(instance.role)
            
            for ext_config in default_extensions:
                RoleExtension.objects.get_or_create(
                    role=instance.role,
                    field_name=ext_config['field_name'],
                    defaults={
                        'field_label': ext_config['field_label'],
                        'field_type': ext_config['field_type'],
                        'is_required': ext_config.get('is_required', False),
                        'is_active': ext_config.get('is_active', True),
                        'sort_order': ext_config.get('sort_order', 0),
                        'help_text': ext_config.get('help_text', ''),
                        'show_in_profile': ext_config.get('show_in_profile', True)
                    }
                )
            
            # 记录同步日志
            PermissionSyncLog.objects.create(
                sync_type='auto',
                target_type='role',
                target_id=instance.role,
                action=f'角色增项自动创建: {instance.display_name}',
                result=f'为角色 {instance.display_name} 创建了 {len(default_extensions)} 个默认增项配置',
                success=True
            )
            logger.info(f"为角色 {instance.display_name} 自动创建了 {len(default_extensions)} 个增项配置")
            
        except Exception as e:
            logger.error(f"为角色 {instance.display_name} 创建增项配置失败: {e}")
            PermissionSyncLog.objects.create(
                sync_type='auto',
                target_type='role',
                target_id=instance.role,
                action=f'角色增项创建失败: {instance.display_name}',
                result=f'创建失败: {str(e)}',
                success=False
            )


@receiver(post_save, sender=RoleManagement)
def create_role_group_mapping_on_role_creation(sender, instance, created, **kwargs):
    """角色创建时自动创建对应的角色组映射和权限同步"""
    if created:
        try:
            # 为自定义角色创建对应的Django组
            group_name = f"{instance.display_name}组" if instance.display_name else f"{instance.role}组"
            group, group_created = Group.objects.get_or_create(name=group_name)
            
            if group_created:
                logger.info(f"为角色 {instance.role} 创建新组: {group_name}")
            
            # 创建角色组映射
            mapping, mapping_created = RoleGroupMapping.objects.get_or_create(
                role=instance.role,
                defaults={
                    'group': group,
                    'auto_sync': True
                }
            )
            
            if mapping_created:
                logger.info(f"为角色 {instance.role} 创建角色组映射: {instance.role} -> {group_name}")
                
                # 同步权限到组
                from .utils import PermissionUtils
                PermissionUtils.sync_role_permissions(instance)
                
                # 记录成功日志
                PermissionSyncLog.objects.create(
                    sync_type='auto',
                    target_type='role',
                    target_id=instance.role,
                    action=f'角色组映射自动创建: {instance.display_name}',
                    result=f'为角色 {instance.display_name} 创建了组映射 {group_name} 并同步权限',
                    success=True
                )
                logger.info(f"角色 {instance.display_name} 的权限同步完成")
            else:
                logger.info(f"角色 {instance.role} 的组映射已存在")
                
        except Exception as e:
            logger.error(f"为角色 {instance.display_name} 创建组映射失败: {e}")
            PermissionSyncLog.objects.create(
                sync_type='auto',
                target_type='role',
                target_id=instance.role,
                action=f'角色组映射创建失败: {instance.display_name}',
                result=f'创建失败: {str(e)}',
                success=False
            )


def get_default_extensions_for_role(role):
    """获取不同角色的默认增项配置"""
    # 处理字符串角色值，转换为对应的UserRole枚举值
    if isinstance(role, str):
        role_mapping = {
            'student': UserRole.STUDENT,
            'teacher': UserRole.TEACHER,
            'parent': UserRole.PARENT,
            'admin': UserRole.ADMIN,
        }
        role = role_mapping.get(role, role)
    
    role_extensions = {
        UserRole.STUDENT: [
            {
                'field_name': 'school',
                'field_label': '所在学校',
                'field_type': 'text',
                'is_required': True,
                'sort_order': 1,
                'help_text': '学生当前就读的学校名称'
            },
            {
                'field_name': 'grade',
                'field_label': '年级',
                'field_type': 'choice',
                'field_choices': '[{"value": "1", "label": "一年级"}, {"value": "2", "label": "二年级"}, {"value": "3", "label": "三年级"}, {"value": "4", "label": "四年级"}, {"value": "5", "label": "五年级"}, {"value": "6", "label": "六年级"}]',
                'is_required': True,
                'sort_order': 2,
                'help_text': '学生当前所在年级'
            },
            {
                'field_name': 'class_name',
                'field_label': '班级',
                'field_type': 'text',
                'is_required': False,
                'sort_order': 3,
                'help_text': '学生所在班级，如：三年级一班'
            },
            {
                'field_name': 'student_id',
                'field_label': '学号',
                'field_type': 'text',
                'is_required': False,
                'sort_order': 4,
                'help_text': '学生在学校的学号'
            }
        ],
        UserRole.TEACHER: [
            {
                'field_name': 'school',
                'field_label': '任教学校',
                'field_type': 'text',
                'is_required': True,
                'sort_order': 1,
                'help_text': '教师当前任教的学校名称'
            },
            {
                'field_name': 'subject',
                'field_label': '任教科目',
                'field_type': 'choice',
                'field_choices': '[{"value": "english", "label": "英语"}, {"value": "chinese", "label": "语文"}, {"value": "math", "label": "数学"}, {"value": "other", "label": "其他"}]',
                'is_required': True,
                'sort_order': 2,
                'help_text': '教师主要任教的科目'
            },
            {
                'field_name': 'teaching_grade',
                'field_label': '任教年级',
                'field_type': 'text',
                'is_required': False,
                'sort_order': 3,
                'help_text': '教师任教的年级，如：三年级、四年级'
            },
            {
                'field_name': 'teacher_id',
                'field_label': '教师编号',
                'field_type': 'text',
                'is_required': False,
                'sort_order': 4,
                'help_text': '教师在学校的工号或编号'
            }
        ],
        UserRole.PARENT: [
            {
                'field_name': 'relation',
                'field_label': '与学生关系',
                'field_type': 'choice',
                'field_choices': '[{"value": "father", "label": "父亲"}, {"value": "mother", "label": "母亲"}, {"value": "guardian", "label": "监护人"}, {"value": "other", "label": "其他"}]',
                'is_required': True,
                'sort_order': 1,
                'help_text': '家长与学生的关系'
            },
            {
                'field_name': 'student_name',
                'field_label': '学生姓名',
                'field_type': 'text',
                'is_required': True,
                'sort_order': 2,
                'help_text': '关联学生的姓名'
            },
            {
                'field_name': 'contact_time',
                'field_label': '联系时间偏好',
                'field_type': 'choice',
                'field_choices': '[{"value": "morning", "label": "上午"}, {"value": "afternoon", "label": "下午"}, {"value": "evening", "label": "晚上"}, {"value": "anytime", "label": "任何时间"}]',
                'is_required': False,
                'sort_order': 3,
                'help_text': '家长希望被联系的时间段'
            }
        ],
        UserRole.ADMIN: [
            {
                'field_name': 'department',
                'field_label': '所属部门',
                'field_type': 'choice',
                'field_choices': '[{"value": "tech", "label": "技术部"}, {"value": "education", "label": "教务部"}, {"value": "operation", "label": "运营部"}, {"value": "other", "label": "其他"}]',
                'is_required': True,
                'sort_order': 1,
                'help_text': '管理员所属的部门'
            },
            {
                'field_name': 'admin_level',
                'field_label': '管理级别',
                'field_type': 'choice',
                'field_choices': '[{"value": "super", "label": "超级管理员"}, {"value": "senior", "label": "高级管理员"}, {"value": "junior", "label": "初级管理员"}]',
                'is_required': True,
                'sort_order': 2,
                'help_text': '管理员的权限级别'
            },
            {
                'field_name': 'responsibility',
                'field_label': '主要职责',
                'field_type': 'textarea',
                'is_required': False,
                'sort_order': 3,
                'help_text': '管理员的主要工作职责描述'
            }
        ]
    }
    
    # 确保role是UserRole类型，如果不是则返回空列表
    if not isinstance(role, type(UserRole.STUDENT)):
        return []
    
    return role_extensions.get(role, [])


# 新增的自动化权限同步信号处理器
@receiver(post_save, sender=CustomUser)
def auto_sync_user_permissions(sender, instance, created, **kwargs):
    """用户创建或更新时自动同步权限"""
    try:
        # 检查是否启用自动同步
        config = AutoSyncConfig.objects.first()
        if not config or not config.enable_auto_sync:
            return
        
        # 判断是否需要同步
        should_sync = False
        sync_reason = ""
        
        if created and config.sync_on_user_create:
            should_sync = True
            sync_reason = "用户创建"
        elif not created and config.sync_on_user_update:
            should_sync = True
            sync_reason = "用户更新"
        
        if not should_sync:
            return
        
        # 执行权限同步
        from .models_optimized import sync_user_to_role_group
        success, message = sync_user_to_role_group(instance)
        
        if success:
            logger.info(f"自动权限同步成功 - {sync_reason}: 用户 {instance.username} - {message}")
        else:
            logger.warning(f"自动权限同步失败 - {sync_reason}: 用户 {instance.username} - {message}")
            
    except Exception as e:
        logger.error(f"自动权限同步异常: 用户 {instance.username} - {str(e)}")


@receiver(pre_save, sender=CustomUser)
def detect_role_change(sender, instance, **kwargs):
    """检测角色变更并标记需要同步"""
    if instance.pk:  # 只对已存在的用户检查
        try:
            old_instance = CustomUser.objects.get(pk=instance.pk)
            if old_instance.role != instance.role:
                # 角色发生变更，标记需要同步
                instance._role_changed = True
                instance._old_role = old_instance.role
                instance._new_role = instance.role
        except CustomUser.DoesNotExist:
            pass


@receiver(post_save, sender=CustomUser)
def handle_role_change_sync(sender, instance, created, **kwargs):
    """处理角色变更后的权限同步"""
    if not created and hasattr(instance, '_role_changed') and instance._role_changed:
        try:
            # 检查是否启用角色变更同步
            config = AutoSyncConfig.objects.first()
            if not config or not config.sync_on_role_change:
                return
            
            old_role = getattr(instance, '_old_role', None)
            new_role = getattr(instance, '_new_role', None)
            
            logger.info(f"检测到角色变更: 用户 {instance.username} 从 {old_role} 变更为 {new_role}")
            
            # 移除用户从旧角色组
            if old_role:
                try:
                    old_mapping = OptimizedRoleGroupMapping.objects.get(role=old_role)
                    old_mapping.group.user_set.remove(instance)
                    logger.info(f"从旧角色组移除用户: {instance.username} -> {old_mapping.group.name}")
                except OptimizedRoleGroupMapping.DoesNotExist:
                    logger.warning(f"旧角色 {old_role} 的组映射不存在")
            
            # 添加用户到新角色组
            from .models_optimized import sync_user_to_role_group
            success, message = sync_user_to_role_group(instance)
            
            if success:
                logger.info(f"角色变更权限同步成功: 用户 {instance.username} - {message}")
            else:
                logger.error(f"角色变更权限同步失败: 用户 {instance.username} - {message}")
            
            # 清理临时标记
            if hasattr(instance, '_role_changed'):
                delattr(instance, '_role_changed')
            if hasattr(instance, '_old_role'):
                delattr(instance, '_old_role')
            if hasattr(instance, '_new_role'):
                delattr(instance, '_new_role')
            
        except Exception as e:
            logger.error(f"处理角色变更同步异常: 用户 {instance.username} - {str(e)}")


@receiver(post_save, sender=OptimizedRoleGroupMapping)
def auto_sync_role_group_mapping(sender, instance, created, **kwargs):
    """角色组映射创建或更新时自动同步"""
    try:
        # 检查是否启用自动同步
        config = AutoSyncConfig.objects.first()
        if not config or not config.sync_on_permission_change:
            return
        
        # 如果启用自动同步，执行同步
        if instance.auto_sync:
            success, message = instance.sync_to_django_group()
            
            if success:
                logger.info(f"角色组映射自动同步成功: {instance} - {message}")
            else:
                logger.warning(f"角色组映射自动同步失败: {instance} - {message}")
                
    except Exception as e:
        logger.error(f"角色组映射自动同步异常: {instance} - {str(e)}")


def create_default_auto_sync_config():
    """创建默认的自动同步配置"""
    try:
        config, created = AutoSyncConfig.objects.get_or_create(
            defaults={
                'enable_auto_sync': True,
                'sync_on_user_create': True,
                'sync_on_user_update': False,
                'sync_on_role_change': True,
                'sync_on_permission_change': True,
                'auto_sync_interval_minutes': 60,
                'batch_sync_size': 100,
                'max_retry_attempts': 3,
                'retry_delay_seconds': 30,
                'notify_on_sync_failure': True,
                'notification_emails': []
            }
        )
        
        if created:
            logger.info("创建默认自动同步配置")
        
        return config
        
    except Exception as e:
        logger.error(f"创建默认自动同步配置失败: {str(e)}")
        return None


def initialize_role_group_mappings():
    """初始化所有角色的组映射"""
    try:
        created_count = 0
        for role_choice in UserRole.choices:
            role = role_choice[0]
            mapping, created = OptimizedRoleGroupMapping.create_for_role(role)
            if created:
                created_count += 1
                logger.info(f"创建角色组映射: {mapping}")
        
        if created_count > 0:
            logger.info(f"初始化完成，创建了 {created_count} 个角色组映射")
        else:
            logger.info("所有角色组映射已存在")
            
    except Exception as e:
        logger.error(f"初始化角色组映射失败: {str(e)}")


def setup_permissions_system():
    """设置权限系统"""
    logger.info("开始设置权限系统...")
    
    # 创建默认配置
    create_default_auto_sync_config()
    
    # 初始化角色组映射
    initialize_role_group_mappings()
    
    logger.info("权限系统设置完成")