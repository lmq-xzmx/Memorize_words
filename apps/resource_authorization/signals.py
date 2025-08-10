from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache

from .models import (
    ResourceAuthorization,
    ResourceShare,
    ResourceUsageAnalytics,
    UserSubscription
)
from apps.teaching.models import LearningGoal, LearningSession
from apps.vocabulary_manager.models import LearningGoal as VocabLearningGoal
from apps.words.models import Word, WordSet

User = get_user_model()


@receiver(post_save, sender=LearningGoal)
def create_learning_goal_authorization(sender, instance, created, **kwargs):
    """为新创建的学习目标自动创建资源授权"""
    if created:
        ResourceAuthorization.objects.get_or_create(
            resource_type='learning_goal',
            resource_id=str(instance.id),
            created_by=instance.user,
            defaults={
                'access_level': 'owner',
                'is_active': True,
                'is_public': False,
                'metadata': {
                    'auto_created': True,
                    'source': 'teaching_app'
                }
            }
        )


@receiver(post_save, sender=VocabLearningGoal)
def create_vocab_learning_goal_authorization(sender, instance, created, **kwargs):
    """为新创建的词汇学习目标自动创建资源授权"""
    if created:
        ResourceAuthorization.objects.get_or_create(
            resource_type='vocab_learning_goal',
            resource_id=str(instance.id),
            created_by=instance.user,
            defaults={
                'access_level': 'owner',
                'is_active': True,
                'is_public': False,
                'metadata': {
                    'auto_created': True,
                    'source': 'vocabulary_manager_app'
                }
            }
        )


@receiver(post_save, sender=Word)
def create_word_authorization(sender, instance, created, **kwargs):
    """为新创建的单词自动创建资源授权"""
    if created and hasattr(instance, 'created_by') and instance.created_by:
        ResourceAuthorization.objects.get_or_create(
            resource_type='word',
            resource_id=str(instance.id),
            created_by=instance.created_by,
            defaults={
                'access_level': 'owner',
                'is_active': True,
                'is_public': True,  # 单词默认公开
                'metadata': {
                    'auto_created': True,
                    'source': 'words_app'
                }
            }
        )


@receiver(post_save, sender=WordSet)
def create_wordset_authorization(sender, instance, created, **kwargs):
    """为新创建的单词集自动创建资源授权"""
    if created and hasattr(instance, 'created_by') and instance.created_by:
        ResourceAuthorization.objects.get_or_create(
            resource_type='word_set',
            resource_id=str(instance.id),
            created_by=instance.created_by,
            defaults={
                'access_level': 'owner',
                'is_active': True,
                'is_public': False,
                'metadata': {
                    'auto_created': True,
                    'source': 'words_app'
                }
            }
        )


@receiver(post_save, sender=LearningSession)
def track_learning_session_usage(sender, instance, created, **kwargs):
    """跟踪学习会话的资源使用"""
    if created:
        # 查找相关的学习目标授权
        try:
            auth = ResourceAuthorization.objects.get(
                resource_type='learning_goal',
                resource_id=str(instance.goal.id)
            )
            
            # 记录使用分析
            ResourceUsageAnalytics.objects.create(
                authorization=auth,
                user=instance.user,
                action='session_start',
                platform='web',
                metadata={
                    'session_id': str(instance.id),
                    'auto_tracked': True
                }
            )
        except ResourceAuthorization.DoesNotExist:
            pass


@receiver(post_save, sender=ResourceShare)
def invalidate_share_cache(sender, instance, **kwargs):
    """资源分享变更时清除相关缓存"""
    cache_keys = [
        f'resource_shares_{instance.authorization.id}',
        f'user_shared_resources_{instance.shared_by.id}',
    ]
    
    # 清除分享对象的缓存
    for user in instance.shared_with.all():
        cache_keys.append(f'user_accessible_resources_{user.id}')
    
    cache.delete_many(cache_keys)


@receiver(post_delete, sender=ResourceShare)
def invalidate_share_cache_on_delete(sender, instance, **kwargs):
    """资源分享删除时清除相关缓存"""
    cache_keys = [
        f'resource_shares_{instance.authorization.id}',
        f'user_shared_resources_{instance.shared_by.id}',
    ]
    
    # 清除分享对象的缓存
    for user in instance.shared_with.all():
        cache_keys.append(f'user_accessible_resources_{user.id}')
    
    cache.delete_many(cache_keys)


@receiver(post_save, sender=ResourceAuthorization)
def invalidate_authorization_cache(sender, instance, **kwargs):
    """资源授权变更时清除相关缓存"""
    cache_keys = [
        f'user_authorizations_{instance.created_by.id}',
        f'resource_authorization_{instance.resource_type}_{instance.resource_id}',
        f'user_accessible_resources_{instance.created_by.id}',
    ]
    cache.delete_many(cache_keys)


@receiver(post_delete, sender=ResourceAuthorization)
def invalidate_authorization_cache_on_delete(sender, instance, **kwargs):
    """资源授权删除时清除相关缓存"""
    cache_keys = [
        f'user_authorizations_{instance.created_by.id}',
        f'resource_authorization_{instance.resource_type}_{instance.resource_id}',
        f'user_accessible_resources_{instance.created_by.id}',
    ]
    cache.delete_many(cache_keys)


@receiver(pre_save, sender=UserSubscription)
def track_subscription_changes(sender, instance, **kwargs):
    """跟踪用户订阅状态变更"""
    if instance.pk:  # 更新现有订阅
        try:
            old_instance = UserSubscription.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # 状态发生变化，记录到元数据
                if not instance.metadata:
                    instance.metadata = {}
                
                if 'status_history' not in instance.metadata:
                    instance.metadata['status_history'] = []
                
                instance.metadata['status_history'].append({
                    'from_status': old_instance.status,
                    'to_status': instance.status,
                    'changed_at': timezone.now().isoformat()
                })
        except UserSubscription.DoesNotExist:
            pass


@receiver(post_save, sender=UserSubscription)
def invalidate_subscription_cache(sender, instance, **kwargs):
    """用户订阅变更时清除相关缓存"""
    cache_keys = [
        f'user_subscription_{instance.user.id}',
        f'user_subscription_features_{instance.user.id}',
        f'user_accessible_resources_{instance.user.id}',
    ]
    cache.delete_many(cache_keys)


@receiver(post_delete, sender=UserSubscription)
def invalidate_subscription_cache_on_delete(sender, instance, **kwargs):
    """用户订阅删除时清除相关缓存"""
    cache_keys = [
        f'user_subscription_{instance.user.id}',
        f'user_subscription_features_{instance.user.id}',
        f'user_accessible_resources_{instance.user.id}',
    ]
    cache.delete_many(cache_keys)