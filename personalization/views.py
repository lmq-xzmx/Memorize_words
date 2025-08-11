from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
from typing import Any

from .models import (
    UserPreference, LearningBehavior, RecommendationModel,
    PersonalizedRecommendation, LearningPath, LearningStep,
    AdaptiveDifficulty
)
from .serializers import (
    UserPreferenceSerializer, LearningBehaviorSerializer,
    RecommendationModelSerializer, PersonalizedRecommendationSerializer,
    LearningPathSerializer, LearningStepSerializer,
    AdaptiveDifficultySerializer, PersonalizationStatsSerializer
)

User = get_user_model()


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """用户偏好视图集"""
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> Any:
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role in ['admin', 'teacher']:
            return UserPreference.objects.all()
        return UserPreference.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LearningBehaviorViewSet(viewsets.ModelViewSet):
    """学习行为视图集"""
    serializer_class = LearningBehaviorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> Any:
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role in ['admin', 'teacher']:
            return LearningBehavior.objects.all().order_by('-timestamp')
        return LearningBehavior.objects.filter(user=user).order_by('-timestamp')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近的学习行为"""
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(timestamp__gte=since)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """学习行为分析"""
        queryset = self.get_queryset()
        
        # 按行为类型统计
        behavior_stats = queryset.values('behavior_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按时间段统计
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        recent_behaviors = queryset.filter(timestamp__gte=since)
        
        # 学习时长统计
        total_duration = sum(
            behavior.duration_seconds for behavior in recent_behaviors 
            if behavior.duration_seconds
        )
        
        return Response({
            'behavior_stats': behavior_stats,
            'total_behaviors': queryset.count(),
            'recent_behaviors_count': recent_behaviors.count(),
            'total_duration_minutes': total_duration,
            'avg_session_duration': total_duration / max(recent_behaviors.count(), 1)
        })


class RecommendationModelViewSet(viewsets.ModelViewSet):
    """推荐模型视图集"""
    queryset = RecommendationModel.objects.all()
    serializer_class = RecommendationModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> Any:
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role == 'admin':
            return RecommendationModel.objects.all()
        return RecommendationModel.objects.filter(is_active=True)


class PersonalizedRecommendationViewSet(viewsets.ModelViewSet):
    """个性化推荐视图集"""
    serializer_class = PersonalizedRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> Any:
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role in ['admin', 'teacher']:
            return PersonalizedRecommendation.objects.all().order_by('-created_at')
        return PersonalizedRecommendation.objects.filter(
            user=user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接受推荐"""
        recommendation = self.get_object()
        recommendation.is_accepted = True
        recommendation.save()
        return Response({'status': 'accepted'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝推荐"""
        recommendation = self.get_object()
        recommendation.is_accepted = False
        recommendation.save()
        return Response({'status': 'rejected'})
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """获取待处理的推荐"""
        queryset = self.get_queryset().filter(is_accepted__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LearningPathViewSet(viewsets.ModelViewSet):
    """学习路径视图集"""
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> Any:
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role in ['admin', 'teacher']:
            return LearningPath.objects.all().order_by('-created_at')
        return LearningPath.objects.filter(user=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """开始学习路径"""
        path = self.get_object()
        path.is_active = True
        path.save()
        return Response({'status': 'started'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成学习路径"""
        path = self.get_object()
        path.is_completed = True
        path.completed_at = timezone.now()
        path.save()
        return Response({'status': 'completed'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取活跃的学习路径"""
        queryset = self.get_queryset().filter(is_active=True, is_completed=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LearningStepViewSet(viewsets.ModelViewSet):
    """学习步骤视图集"""
    serializer_class = LearningStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> Any:
        path_id = getattr(self.request, 'query_params', self.request.GET).get('path_id')
        if path_id:
            return LearningStep.objects.filter(path_id=path_id).order_by('order')
        return LearningStep.objects.all().order_by('order')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成学习步骤"""
        step = self.get_object()
        step.is_completed = True
        step.completed_at = timezone.now()
        step.save()
        return Response({'status': 'completed'})


class AdaptiveDifficultyViewSet(viewsets.ModelViewSet):
    """自适应难度调整视图集"""
    serializer_class = AdaptiveDifficultySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> Any:
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role in ['admin', 'teacher']:
            return AdaptiveDifficulty.objects.all().order_by('-updated_at')
        return AdaptiveDifficulty.objects.filter(user=user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PersonalizationStatsViewSet(viewsets.ViewSet):
    """个性化统计视图集"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """获取个性化统计数据"""
        user = request.user
        
        # 推荐统计
        recommendations = PersonalizedRecommendation.objects.filter(user=user)
        total_recommendations = recommendations.count()
        accepted_recommendations = recommendations.filter(is_accepted=True).count()
        acceptance_rate = (accepted_recommendations / max(total_recommendations, 1)) * 100
        
        # 学习路径统计
        learning_paths = LearningPath.objects.filter(user=user)
        learning_paths_count = learning_paths.count()
        active_learning_paths = learning_paths.filter(is_active=True, is_completed=False).count()
        
        # 难度统计
        difficulty_adjustments = AdaptiveDifficulty.objects.filter(user=user)
        avg_difficulty = difficulty_adjustments.aggregate(
            avg=Avg('current_difficulty')
        )['avg'] or 0
        
        # 偏好内容类型
        preferences = UserPreference.objects.filter(user=user).first()
        preferred_types = []
        if preferences and hasattr(preferences, 'preferred_topics'):
            preferred_types = preferences.preferred_topics or []
        
        # 学习时间分布
        behaviors = LearningBehavior.objects.filter(user=user)
        time_distribution = {}
        for behavior in behaviors:
            hour = behavior.timestamp.hour
            time_distribution[hour] = time_distribution.get(hour, 0) + 1
        
        # 最近行为
        recent_behaviors = behaviors.order_by('-timestamp')[:10]
        
        stats_data = {
            'total_recommendations': total_recommendations,
            'accepted_recommendations': accepted_recommendations,
            'acceptance_rate': round(acceptance_rate, 2),
            'learning_paths_count': learning_paths_count,
            'active_learning_paths': active_learning_paths,
            'avg_difficulty_level': round(avg_difficulty, 2),
            'preferred_content_types': preferred_types,
            'learning_time_distribution': time_distribution,
            'recent_behaviors': LearningBehaviorSerializer(recent_behaviors, many=True).data
        }
        
        serializer = PersonalizationStatsSerializer(stats_data)
        return Response(serializer.data)
