from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser, UserRole, LearningProfile
from .admin import ROLE_GROUP_MAPPING, sync_user_role_to_group
from .services.role_service import RoleService


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


def create_default_groups():
    """创建默认的角色组"""
    for role, group_name in ROLE_GROUP_MAPPING.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"创建组: {group_name}")
        else:
            print(f"组已存在: {group_name}")