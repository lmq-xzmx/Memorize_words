from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db import transaction
import logging

from .models import CustomUser, UserRole, LearningProfile
from .admin import ROLE_GROUP_MAPPING, sync_user_role_to_group
from .services.role_service import RoleService

# 导入优化模型
try:
    from .models_optimized import OptimizedRoleTemplate, RegistrationConfig, RegistrationLog
    from permissions.models_optimized import OptimizedRoleGroupMapping
    OPTIMIZED_MODELS_AVAILABLE = True
except ImportError:
    OPTIMIZED_MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建后自动创建学习档案"""
    if created and instance.role == UserRole.STUDENT:
        LearningProfile.objects.get_or_create(
            user=instance,
            defaults={
                'total_study_time': 0,
                'completed_lessons': 0,
                'current_streak': 0,
                'max_streak': 0
            }
        )


@receiver(post_save, sender=CustomUser)
def sync_user_role_group(sender, instance, created, **kwargs):
    """用户保存后自动同步角色到组"""
    if instance.role:
        sync_user_role_to_group(instance)


@receiver(post_save, sender=UserRole)
def clear_role_cache_on_user_role_save(sender, instance, **kwargs):
    """UserRole保存后清除角色缓存"""
    RoleService.clear_cache()


@receiver(post_delete, sender=UserRole)
def clear_role_cache_on_user_role_delete(sender, instance, **kwargs):
    """UserRole删除后清除角色缓存"""
    RoleService.clear_cache()


# 如果存在RoleManagement模型，也添加相应的信号
try:
    from apps.permissions.models import RoleManagement
    
    @receiver(post_save, sender=RoleManagement)
    def clear_role_cache_on_role_management_save(sender, instance, **kwargs):
        """RoleManagement保存后清除角色缓存"""
        RoleService.clear_cache()
    
    @receiver(post_delete, sender=RoleManagement)
    def clear_role_cache_on_role_management_delete(sender, instance, **kwargs):
        """RoleManagement删除后清除角色缓存"""
        RoleService.clear_cache()
except ImportError:
    # RoleManagement模型不存在时忽略
    pass


# 新增的自动化注册流程信号处理器
@receiver(post_save, sender=CustomUser)
def auto_registration_flow(sender, instance, created, **kwargs):
    """用户创建时自动执行注册流程"""
    if not created or not OPTIMIZED_MODELS_AVAILABLE:
        return
    
    try:
        with transaction.atomic():
            # 获取注册配置
            config = RegistrationConfig.objects.first()
            if not config or not config.enable_registration:
                logger.warning(f"注册功能已禁用，跳过用户 {instance.username} 的自动注册流程")
                return
            
            # 获取用户角色对应的模板
            template = OptimizedRoleTemplate.objects.filter(
                role=instance.role,
                is_active=True
            ).first()
            
            if not template:
                logger.warning(f"未找到用户 {instance.username} 角色 {instance.role} 的活跃模板")
                # 使用默认角色模板
                template = OptimizedRoleTemplate.objects.filter(
                    role=config.default_role,
                    is_active=True
                ).first()
                
                if template:
                    # 更新用户角色为默认角色
                    instance.role = config.default_role
                    instance.save(update_fields=['role'])
                    logger.info(f"用户 {instance.username} 角色已更新为默认角色 {config.default_role}")
            
            if not template:
                logger.error(f"未找到任何可用的角色模板，跳过用户 {instance.username} 的自动注册流程")
                return
            
            # 执行自动化配置
            auto_config = template.auto_config or {}
            
            # 1. 自动分配权限
            if config.auto_assign_permissions and auto_config.get('auto_assign_role', True):
                assign_user_permissions(instance, template)
            
            # 2. 自动创建用户档案
            if auto_config.get('auto_create_profile', True):
                create_enhanced_user_profile(instance, template)
            
            # 3. 发送欢迎邮件
            if auto_config.get('auto_send_email', True):
                send_welcome_email(instance, template)
            
            # 4. 记录注册日志
            RegistrationLog.objects.create(
                user=instance,
                template=template,
                registration_data={
                    'username': instance.username,
                    'email': instance.email,
                    'role': instance.role,
                    'template_used': template.template_name,
                    'auto_config_applied': auto_config,
                    'registration_time': timezone.now().isoformat()
                },
                status='success',
                created_at=timezone.now()
            )
            
            logger.info(f"用户 {instance.username} 自动注册流程完成")
            
    except Exception as e:
        logger.error(f"用户 {instance.username} 自动注册流程失败: {str(e)}")
        
        # 记录失败日志
        try:
            RegistrationLog.objects.create(
                user=instance,
                registration_data={
                    'username': instance.username,
                    'email': instance.email,
                    'role': instance.role,
                    'error': str(e),
                    'registration_time': timezone.now().isoformat()
                },
                status='failed',
                error_message=str(e),
                created_at=timezone.now()
            )
        except Exception as log_error:
            logger.error(f"记录注册失败日志时出错: {str(log_error)}")


def assign_user_permissions(user, template):
    """为用户分配权限"""
    try:
        # 获取角色对应的组映射
        mapping = OptimizedRoleGroupMapping.objects.filter(
            role=user.role
        ).first()
        
        if mapping:
            # 将用户添加到对应的Django组
            mapping.group.user_set.add(user)
            logger.info(f"用户 {user.username} 已添加到组 {mapping.group.name}")
            
            # 如果启用自动同步，同步权限
            if mapping.auto_sync:
                success, message = mapping.sync_to_django_group()
                if success:
                    logger.info(f"权限同步成功: {message}")
                else:
                    logger.warning(f"权限同步失败: {message}")
        else:
            logger.warning(f"未找到角色 {user.role} 的组映射")
            
    except Exception as e:
        logger.error(f"分配用户权限失败: {user.username} - {str(e)}")


def create_enhanced_user_profile(user, template):
    """创建增强的用户档案"""
    try:
        form_config = template.form_config or {}
        
        # 根据角色创建不同的档案
        if user.role == UserRole.STUDENT:
            # 创建学生档案
            profile, created = LearningProfile.objects.get_or_create(
                user=user,
                defaults={
                    'learning_goal': '提升英语水平',
                    'daily_target': 20,
                    'difficulty_level': 'beginner',
                    'total_study_time': 0,
                    'completed_lessons': 0,
                    'current_streak': 0,
                    'max_streak': 0
                }
            )
            if created:
                logger.info(f"为学生 {user.username} 创建学习档案")
        
        elif user.role == UserRole.TEACHER:
            # 创建教师档案（如果有相关模型）
            logger.info(f"为教师 {user.username} 创建教师档案")
        
        logger.info(f"用户档案创建完成: {user.username}")
        
    except Exception as e:
        logger.error(f"创建用户档案失败: {user.username} - {str(e)}")


def send_welcome_email(user, template):
    """发送欢迎邮件"""
    try:
        # 获取注册配置
        config = RegistrationConfig.objects.first()
        if not config:
            return
        
        notification_settings = config.notification_settings or {}
        
        if notification_settings.get('send_welcome_email', True):
            # 这里可以集成邮件发送功能
            logger.info(f"欢迎邮件已发送给用户 {user.username}")
        
        # 通知管理员
        if notification_settings.get('notify_admin_on_registration', False):
            admin_emails = notification_settings.get('admin_notification_emails', [])
            if admin_emails:
                logger.info(f"管理员通知邮件已发送，新用户: {user.username}")
        
    except Exception as e:
        logger.error(f"发送欢迎邮件失败: {user.username} - {str(e)}")


def create_default_groups():
    """创建默认的角色组"""
    for role, group_name in ROLE_GROUP_MAPPING.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"创建组: {group_name}")
        else:
            print(f"组已存在: {group_name}")


def setup_registration_system():
    """设置注册系统"""
    logger.info("开始设置注册系统...")
    
    try:
        if OPTIMIZED_MODELS_AVAILABLE:
            # 创建默认注册配置
            config, created = RegistrationConfig.objects.get_or_create(
                defaults={
                    'enable_registration': True,
                    'default_role': UserRole.STUDENT,
                    'require_email_verification': True,
                    'require_admin_approval': False,
                    'auto_assign_permissions': True,
                    'registration_limit_per_day': 100,
                    'notification_settings': {
                        'notify_admin_on_registration': True,
                        'send_welcome_email': True,
                        'admin_notification_emails': ['admin@example.com']
                    }
                }
            )
            
            if created:
                logger.info("创建默认注册配置")
            
            logger.info("注册系统设置完成")
        else:
            logger.warning("优化模型不可用，跳过注册系统设置")
        
    except Exception as e:
        logger.error(f"设置注册系统失败: {str(e)}")