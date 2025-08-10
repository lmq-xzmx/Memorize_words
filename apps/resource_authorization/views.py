from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from typing import Dict, Any

from .models import (
    ResourceAuthorization,
    ResourceShare,
    ResourceCategory,
    ResourceUsageAnalytics,
    UserSubscription,
    SubscriptionFeature
)
from .services import (
    ResourceAuthorizationService,
    ResourceSharingService,
    ResourceCategoryService,
    ResourceAnalyticsService,
    SubscriptionService
)


class ResourceAuthorizationViewSet(viewsets.ModelViewSet):
    """资源授权视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        
        # 管理员可以看到所有授权
        if user.is_staff:
            return ResourceAuthorization.objects.all()
        
        # 普通用户只能看到自己创建的或有权访问的
        return ResourceAuthorization.objects.filter(
            Q(created_by=user) |
            Q(is_public=True) |
            Q(shares__shared_with=user, shares__is_active=True)
        ).distinct()
    
    @action(detail=False, methods=['post'])
    def check_access(self, request):
        """检查资源访问权限"""
        resource_type = request.data.get('resource_type')
        resource_id = request.data.get('resource_id')
        
        if not resource_type or not resource_id:
            return Response(
                {'error': '缺少必要参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_access = ResourceAuthorizationService.check_access(
            request.user, resource_type, int(resource_id)
        )
        
        return Response({
            'has_access': has_access,
            'resource_type': resource_type,
            'resource_id': resource_id
        })
    
    @action(detail=False, methods=['get'])
    def accessible_resources(self, request):
        """获取用户可访问的资源"""
        resource_type = request.query_params.get('resource_type')
        limit = int(request.query_params.get('limit', 50))
        
        if not resource_type:
            return Response(
                {'error': '缺少resource_type参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resources = ResourceAuthorizationService.get_user_accessible_resources(
            request.user, resource_type, limit
        )
        
        # 简化序列化
        data = [{
            'id': r.id,
            'resource_type': r.resource_type,
            'resource_id': r.resource_id,
            'access_level': r.access_level,
            'is_public': r.is_public
        } for r in resources]
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def track_usage(self, request, pk=None):
        """跟踪资源使用"""
        authorization = self.get_object()
        action_type = request.data.get('action', 'view')
        platform = request.data.get('platform', 'web')
        session_id = request.data.get('session_id', '')
        metadata = request.data.get('metadata', {})
        
        # 检查访问权限
        if not ResourceAuthorizationService.check_access(
            request.user, authorization.resource_type, authorization.resource_id
        ):
            return Response(
                {'error': '无权访问此资源'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 记录使用情况
        analytics = ResourceAnalyticsService.track_usage(
            authorization=authorization,
            user=request.user,
            action=action_type,
            platform=platform,
            session_id=session_id,
            metadata=metadata
        )
        
        return Response({
            'message': '使用记录已保存',
            'analytics_id': analytics.id
        })


class ResourceShareViewSet(viewsets.ModelViewSet):
    """资源分享视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        
        # 返回用户分享的和接收到的分享
        return ResourceShare.objects.filter(
            Q(shared_by=user) | Q(shared_with=user)
        ).distinct()
    
    def perform_create(self, serializer):
        """创建分享"""
        serializer.save(shared_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_shares(self, request):
        """获取我的分享"""
        share_type = request.query_params.get('share_type')
        shares = ResourceSharingService.get_user_shares(request.user, share_type)
        
        data = [{
            'id': s.id,
            'authorization_id': s.authorization.id,
            'share_type': s.share_type,
            'shared_at': s.shared_at,
            'is_active': s.is_active
        } for s in shares]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def received_shares(self, request):
        """获取接收到的分享"""
        shares = ResourceSharingService.get_received_shares(request.user)
        
        data = [{
            'id': s.id,
            'authorization_id': s.authorization.id,
            'shared_by': s.shared_by.username,
            'share_type': s.share_type,
            'shared_at': s.shared_at,
            'share_message': s.share_message
        } for s in shares]
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """撤销分享"""
        success = ResourceSharingService.revoke_share(int(pk), request.user)
        
        if success:
            return Response({'message': '分享已撤销'})
        else:
            return Response(
                {'error': '撤销失败'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResourceCategoryViewSet(viewsets.ModelViewSet):
    """资源分类视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        include_public = self.request.query_params.get('include_public', 'true').lower() == 'true'
        
        categories = ResourceCategoryService.get_user_categories(user, include_public)
        return ResourceCategory.objects.filter(id__in=[c.id for c in categories])
    
    def perform_create(self, serializer):
        """创建分类"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_resource(self, request, pk=None):
        """添加资源到分类"""
        category = self.get_object()
        resource_type = request.data.get('resource_type')
        resource_id = request.data.get('resource_id')
        
        if not resource_type or not resource_id:
            return Response(
                {'error': '缺少必要参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            authorization = ResourceAuthorization.objects.get(
                resource_type=resource_type,
                resource_id=resource_id
            )
        except ResourceAuthorization.DoesNotExist:
            return Response(
                {'error': '资源授权不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        success = ResourceCategoryService.add_resource_to_category(
            category, authorization, request.user
        )
        
        if success:
            return Response({'message': '资源已添加到分类'})
        else:
            return Response(
                {'error': '添加失败'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """用户订阅视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        
        # 管理员可以看到所有订阅
        if user.is_staff:
            return UserSubscription.objects.all()
        
        # 普通用户只能看到自己的订阅
        return UserSubscription.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        """获取我的订阅"""
        try:
            subscription = getattr(request.user, 'subscription', None)
            if subscription:
                data = {
                    'id': subscription.id,
                    'subscription_type': subscription.subscription_type,
                    'status': subscription.status,
                    'start_date': subscription.start_date,
                    'end_date': subscription.end_date,
                    'is_active': subscription.is_active(),
                    'remaining_days': subscription.get_remaining_days()
                }
                return Response(data)
            else:
                # 创建默认免费订阅
                subscription = SubscriptionService.create_subscription(request.user)
                data = {
                    'id': subscription.id,
                    'subscription_type': subscription.subscription_type,
                    'status': subscription.status,
                    'start_date': subscription.start_date,
                    'end_date': subscription.end_date,
                    'is_active': subscription.is_active(),
                    'remaining_days': subscription.get_remaining_days()
                }
                return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def check_feature(self, request):
        """检查功能访问权限"""
        feature_code = request.data.get('feature_code')
        
        if not feature_code:
            return Response(
                {'error': '缺少feature_code参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_access = SubscriptionService.check_feature_access(request.user, feature_code)
        
        return Response({
            'has_access': has_access,
            'feature_code': feature_code
        })
