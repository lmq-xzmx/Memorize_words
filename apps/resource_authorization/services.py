from django.db import transaction, models
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from typing import List, Dict, Optional, Any, Union
from datetime import timedelta, datetime

from .models import (
    ResourceAuthorization,
    ResourceShare,
    ResourceCategory,
    ResourceUsageAnalytics,
    UserSubscription,
    SubscriptionFeature
)

User = get_user_model()


class ResourceAuthorizationService:
    """资源授权服务 - 核心授权逻辑"""
    
    @staticmethod
    def check_access(user: User, resource_type: str, resource_id: int) -> bool:
        """检查用户是否有权访问指定资源"""
        try:
            authorization = ResourceAuthorization.objects.get(
                resource_type=resource_type,
                resource_id=resource_id
            )
            
            # 检查授权是否有效
            if not authorization.is_valid():
                return False
            
            # 免费资源直接允许
            if authorization.access_level == 'FREE':
                return True
            
            # 公开资源允许访问
            if authorization.is_public:
                return True
            
            # 创建者总是有权限
            if authorization.created_by == user:
                return True
            
            # 检查分享权限
            if ResourceAuthorizationService._check_share_access(user, authorization):
                return True
            
            # 检查订阅权限
            if authorization.requires_subscription:
                return ResourceAuthorizationService._check_subscription_access(user, authorization)
            
            # 高级资源需要订阅
            if authorization.access_level == 'PREMIUM':
                return ResourceAuthorizationService._has_premium_subscription(user)
            
            return False
            
        except ResourceAuthorization.DoesNotExist:
            # 如果没有授权记录，默认为免费访问
            return True
    
    @staticmethod
    def _check_share_access(user: User, authorization: ResourceAuthorization) -> bool:
        """检查分享访问权限"""
        shares = ResourceShare.objects.filter(
            authorization=authorization,
            is_active=True
        )
        
        for share in shares:
            if share.can_access(user):
                return True
        
        return False
    
    @staticmethod
    def _check_subscription_access(user: User, authorization: ResourceAuthorization) -> bool:
        """检查订阅访问权限"""
        try:
            subscription = getattr(user, 'subscription', None)
            if subscription:
                return subscription.is_active()
            return False
        except (UserSubscription.DoesNotExist, AttributeError):
            return False
    
    @staticmethod
    def _has_premium_subscription(user: User) -> bool:
        """检查是否有高级订阅"""
        try:
            subscription = getattr(user, 'subscription', None)
            if subscription:
                return subscription.has_premium_access()
            return False
        except (UserSubscription.DoesNotExist, AttributeError):
            return False
    
    @staticmethod
    def create_authorization(
        resource_type: str,
        resource_id: int,
        access_level: str = 'FREE',
        created_by: Optional[User] = None,
        **kwargs
    ) -> ResourceAuthorization:
        """创建资源授权"""
        authorization, created = ResourceAuthorization.objects.get_or_create(
            resource_type=resource_type,
            resource_id=resource_id,
            defaults={
                'access_level': access_level,
                'created_by': created_by,
                **kwargs
            }
        )
        return authorization
    
    @staticmethod
    def update_authorization(
        resource_type: str,
        resource_id: int,
        **updates
    ) -> Optional[ResourceAuthorization]:
        """更新资源授权"""
        try:
            authorization = ResourceAuthorization.objects.get(
                resource_type=resource_type,
                resource_id=resource_id
            )
            
            for key, value in updates.items():
                setattr(authorization, key, value)
            
            authorization.save()
            return authorization
            
        except ResourceAuthorization.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_accessible_resources(
        user: User,
        resource_type: str,
        limit: int = 100
    ) -> List[ResourceAuthorization]:
        """获取用户可访问的资源列表"""
        # 基础查询：有效的授权
        base_query = ResourceAuthorization.objects.filter(
            resource_type=resource_type,
            is_active=True
        )
        
        accessible_resources = []
        
        for auth in base_query[:limit * 2]:  # 获取更多以便过滤
            if ResourceAuthorizationService.check_access(user, auth.resource_type, auth.resource_id):
                accessible_resources.append(auth)
                
                if len(accessible_resources) >= limit:
                    break
        
        return accessible_resources


class ResourceSharingService:
    """资源分享服务"""
    
    @staticmethod
    @transaction.atomic
    def share_resource(
        authorization: ResourceAuthorization,
        shared_by: User,
        share_type: str,
        shared_with_users: Optional[List[User]] = None,
        share_message: str = '',
        expires_at: Optional[datetime] = None,
        **kwargs
    ) -> ResourceShare:
        """分享资源"""
        # 检查分享权限
        if not ResourceAuthorizationService.check_access(shared_by, authorization.resource_type, authorization.resource_id):
            raise PermissionDenied("您没有权限分享此资源")
        
        # 创建分享记录
        share = ResourceShare.objects.create(
            authorization=authorization,
            shared_by=shared_by,
            share_type=share_type,
            share_message=share_message,
            expires_at=expires_at,
            **kwargs
        )
        
        # 添加分享对象
        if shared_with_users:
            share.shared_with.set(shared_with_users)
        
        return share
    
    @staticmethod
    def get_user_shares(user: User, share_type: str = None) -> List[ResourceShare]:
        """获取用户的分享记录"""
        query = ResourceShare.objects.filter(
            shared_by=user,
            is_active=True
        )
        
        if share_type:
            query = query.filter(share_type=share_type)
        
        return list(query.order_by('-shared_at'))
    
    @staticmethod
    def get_received_shares(user: User) -> List[ResourceShare]:
        """获取用户接收到的分享"""
        return list(ResourceShare.objects.filter(
            shared_with=user,
            is_active=True
        ).order_by('-shared_at'))
    
    @staticmethod
    def revoke_share(share_id: int, user: User) -> bool:
        """撤销分享"""
        try:
            share = ResourceShare.objects.get(id=share_id, shared_by=user)
            share.is_active = False
            share.save()
            return True
        except ResourceShare.DoesNotExist:
            return False


class ResourceCategoryService:
    """资源分类服务"""
    
    @staticmethod
    def create_category(
        name: str,
        created_by: User,
        parent: Optional[ResourceCategory] = None,
        description: str = '',
        is_public: bool = False
    ) -> ResourceCategory:
        """创建资源分类"""
        return ResourceCategory.objects.create(
            name=name,
            created_by=created_by,
            parent=parent,
            description=description,
            is_public=is_public
        )
    
    @staticmethod
    def get_user_categories(user: User, include_public: bool = True) -> List[ResourceCategory]:
        """获取用户的分类"""
        query = ResourceCategory.objects.filter(created_by=user)
        
        if include_public:
            public_query = ResourceCategory.objects.filter(is_public=True)
            query = query.union(public_query)
        
        return list(query.order_by('sort_order', 'name'))
    
    @staticmethod
    def add_resource_to_category(
        category: ResourceCategory,
        authorization: ResourceAuthorization,
        user: User
    ) -> bool:
        """将资源添加到分类"""
        # 检查权限
        if category.created_by != user and not category.is_public:
            return False
        
        category.authorizations.add(authorization)
        return True
    
    @staticmethod
    def remove_resource_from_category(
        category: ResourceCategory,
        authorization: ResourceAuthorization,
        user: User
    ) -> bool:
        """从分类中移除资源"""
        # 检查权限
        if category.created_by != user:
            return False
        
        category.authorizations.remove(authorization)
        return True


class ResourceAnalyticsService:
    """资源分析服务"""
    
    @staticmethod
    def track_usage(
        authorization: ResourceAuthorization,
        user: User,
        action: str,
        platform: str = '',
        session_id: str = '',
        metadata: Optional[Dict[str, Any]] = None
    ) -> ResourceUsageAnalytics:
        """跟踪资源使用"""
        return ResourceUsageAnalytics.objects.create(
            authorization=authorization,
            user=user,
            action=action,
            platform=platform,
            session_id=session_id,
            metadata=metadata or {}
        )
    
    @staticmethod
    def get_resource_usage_stats(
        authorization: ResourceAuthorization,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取资源使用统计"""
        since = timezone.now() - timedelta(days=days)
        
        analytics = ResourceUsageAnalytics.objects.filter(
            authorization=authorization,
            timestamp__gte=since
        )
        
        stats = {
            'total_views': analytics.filter(action='view').count(),
            'total_selects': analytics.filter(action='select').count(),
            'total_downloads': analytics.filter(action='download').count(),
            'total_shares': analytics.filter(action='share').count(),
            'unique_users': analytics.values('user').distinct().count(),
            'daily_stats': {}
        }
        
        # 按日统计
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            daily_count = analytics.filter(timestamp__date=date).count()
            stats['daily_stats'][str(date)] = daily_count
        
        return stats
    
    @staticmethod
    def get_user_usage_stats(user: User, days: int = 30) -> Dict[str, Any]:
        """获取用户使用统计"""
        since = timezone.now() - timedelta(days=days)
        
        analytics = ResourceUsageAnalytics.objects.filter(
            user=user,
            timestamp__gte=since
        )
        
        return {
            'total_actions': analytics.count(),
            'resources_accessed': analytics.values('authorization').distinct().count(),
            'most_used_action': analytics.values('action').annotate(
                count=models.Count('action')
            ).order_by('-count').first() or {},
            'platform_usage': dict(
                analytics.values('platform').annotate(
                    count=models.Count('platform')
                ).values_list('platform', 'count')
            )
        }


class SubscriptionService:
    """订阅服务"""
    
    @staticmethod
    def create_subscription(
        user: User,
        subscription_type: str = 'free',
        duration_days: Optional[int] = None
    ) -> UserSubscription:
        """创建用户订阅"""
        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'subscription_type': subscription_type,
                'status': 'active'
            }
        )
        
        if duration_days and not subscription.end_date:
            subscription.end_date = timezone.now() + timedelta(days=duration_days)
            subscription.save()
        
        return subscription
    
    @staticmethod
    def upgrade_subscription(
        user: User,
        new_type: str,
        duration_days: Optional[int] = None
    ) -> UserSubscription:
        """升级订阅"""
        subscription = SubscriptionService.create_subscription(user)
        subscription.subscription_type = new_type
        subscription.status = 'active'
        
        if duration_days:
            subscription.extend_subscription(duration_days)
        
        subscription.save()
        return subscription
    
    @staticmethod
    def check_feature_access(user: User, feature_code: str) -> bool:
        """检查功能访问权限"""
        try:
            subscription = getattr(user, 'subscription', None)
            if not subscription or not subscription.is_active():
                return False
            
            feature = SubscriptionFeature.objects.get(
                code=feature_code,
                is_active=True
            )
            
            return feature.is_available_for_subscription(subscription.subscription_type)
            
        except (UserSubscription.DoesNotExist, SubscriptionFeature.DoesNotExist):
            return False
    
    @staticmethod
    def get_available_features(user: User) -> List[SubscriptionFeature]:
        """获取用户可用的功能列表"""
        try:
            subscription = getattr(user, 'subscription', None)
            if not subscription or not subscription.is_active():
                return []
            
            return list(SubscriptionFeature.objects.filter(
                is_active=True,
                subscription_types__contains=subscription.subscription_type
            ))
            
        except UserSubscription.DoesNotExist:
            return []


class ResourceIntegrationService:
    """资源整合服务 - 处理Teaching和Vocabulary_Manager的整合"""
    
    @staticmethod
    def migrate_teaching_resources():
        """迁移Teaching应用的资源到授权系统"""
        from apps.teaching.models import LearningGoal, WordLearningRecord
        
        # 迁移学习目标
        for goal in LearningGoal.objects.all():
            ResourceAuthorizationService.create_authorization(
                resource_type='learning_goal',
                resource_id=goal.id,
                access_level='USER_GENERATED',
                created_by=goal.user,
                is_public=False
            )
        
        # 迁移学习记录
        for record in WordLearningRecord.objects.all():
            ResourceAuthorizationService.create_authorization(
                resource_type='learning_record',
                resource_id=record.id,
                access_level='USER_GENERATED',
                created_by=record.session.user,
                is_public=False
            )
    
    @staticmethod
    def migrate_vocabulary_resources():
        """迁移Vocabulary_Manager应用的资源到授权系统"""
        from apps.teaching.models import LearningGoal as VocabGoal
        
        # 迁移词汇学习目标
        for goal in VocabGoal.objects.all():
            ResourceAuthorizationService.create_authorization(
                resource_type='vocab_learning_goal',
                resource_id=goal.id,
                access_level='USER_GENERATED',
                created_by=goal.user,
                is_public=False
            )
    
    @staticmethod
    def sync_word_resources():
        """同步单词资源的授权"""
        from apps.words.models import Word, WordSet, VocabularyList
        
        # 同步单词
        for word in Word.objects.filter(is_main_word=True):
            ResourceAuthorizationService.create_authorization(
                resource_type='word',
                resource_id=word.id,
                access_level='FREE',
                is_public=True
            )
        
        # 同步单词集
        for word_set in WordSet.objects.all():
            ResourceAuthorizationService.create_authorization(
                resource_type='word_set',
                resource_id=word_set.id,
                access_level='FREE',
                is_public=True
            )
        
        # 同步词库列表
        for vocab_list in VocabularyList.objects.all():
            ResourceAuthorizationService.create_authorization(
                resource_type='vocabulary_list',
                resource_id=vocab_list.id,
                access_level='FREE',
                is_public=True
            )