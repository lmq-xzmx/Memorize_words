from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Sum, Avg, Max
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    UserGameProfile, PointTransaction, Level, Achievement,
    UserAchievement, Leaderboard, Competition, CompetitionParticipant
)
from .serializers import (
    UserGameProfileSerializer, PointTransactionSerializer, LevelSerializer,
    AchievementSerializer, UserAchievementSerializer, LeaderboardSerializer,
    LeaderboardEntrySerializer, CompetitionSerializer, CompetitionParticipantSerializer,
    GameStatsSerializer
)
from datetime import timedelta

User = get_user_model()


class UserGameProfileViewSet(viewsets.ModelViewSet):
    """用户游戏档案视图集"""
    serializer_class = UserGameProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['admin', 'teacher']:
            return UserGameProfile.objects.all().select_related('user')
        return UserGameProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """获取当前用户的游戏档案"""
        profile, created = UserGameProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """添加积分"""
        if request.user.role not in ['admin', 'teacher']:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        profile = self.get_object()
        points = request.data.get('points', 0)
        reason = request.data.get('reason', '')
        
        if points <= 0:
            return Response({'error': '积分必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.add_points(points, reason)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_streak(self, request, pk=None):
        """更新连击"""
        profile = self.get_object()
        if profile.user != request.user and request.user.role not in ['admin', 'teacher']:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        profile.update_streak()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class PointTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """积分交易记录视图集"""
    serializer_class = PointTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['admin', 'teacher']:
            return PointTransaction.objects.all().select_related('user')
        return PointTransaction.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """获取当前用户的积分交易记录"""
        transactions = PointTransaction.objects.filter(user=request.user)
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    """等级配置视图集"""
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def current_level(self, request):
        """获取当前用户等级信息"""
        profile, created = UserGameProfile.objects.get_or_create(user=request.user)
        try:
            current_level = Level.objects.get(level=profile.current_level)
            next_level = Level.objects.filter(level=profile.current_level + 1).first()
            
            data = {
                'current_level': LevelSerializer(current_level).data,
                'next_level': LevelSerializer(next_level).data if next_level else None,
                'experience_points': profile.experience_points,
                'progress_percentage': 0
            }
            
            if next_level:
                required_exp = next_level.required_experience - current_level.required_experience
                current_exp = profile.experience_points - current_level.required_experience
                data['progress_percentage'] = min(100, (current_exp / required_exp) * 100)
            
            return Response(data)
        except Level.DoesNotExist:
            return Response({'error': '等级配置不存在'}, status=status.HTTP_404_NOT_FOUND)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """成就配置视图集"""
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Achievement.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取可用成就列表"""
        user_achievements = UserAchievement.objects.filter(user=request.user).values_list('achievement_id', flat=True)
        achievements = Achievement.objects.filter(is_active=True, is_hidden=False).exclude(id__in=user_achievements)
        serializer = self.get_serializer(achievements, many=True)
        return Response(serializer.data)


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """用户成就视图集"""
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['admin', 'teacher']:
            return UserAchievement.objects.all().select_related('user', 'achievement')
        return UserAchievement.objects.filter(user=self.request.user).select_related('achievement')
    
    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        """获取当前用户的成就"""
        achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
        serializer = self.get_serializer(achievements, many=True)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """排行榜视图集"""
    queryset = Leaderboard.objects.filter(is_active=True)
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def rankings(self, request, pk=None):
        """获取排行榜排名"""
        leaderboard = self.get_object()
        limit = int(request.query_params.get('limit', 50))
        
        if leaderboard.leaderboard_type == 'points':
            profiles = UserGameProfile.objects.select_related('user').order_by('-total_points')[:limit]
            entries = [{
                'rank': idx + 1,
                'username': profile.user.username,
                'real_name': profile.user.real_name or profile.user.username,
                'score': profile.total_points
            } for idx, profile in enumerate(profiles)]
        
        elif leaderboard.leaderboard_type == 'streak':
            profiles = UserGameProfile.objects.select_related('user').order_by('-current_streak')[:limit]
            entries = [{
                'rank': idx + 1,
                'username': profile.user.username,
                'real_name': profile.user.real_name or profile.user.username,
                'score': profile.current_streak
            } for idx, profile in enumerate(profiles)]
        
        elif leaderboard.leaderboard_type == 'achievements':
            profiles = UserGameProfile.objects.select_related('user').order_by('-achievements_count')[:limit]
            entries = [{
                'rank': idx + 1,
                'username': profile.user.username,
                'real_name': profile.user.real_name or profile.user.username,
                'score': profile.achievements_count
            } for idx, profile in enumerate(profiles)]
        
        else:
            entries = []
        
        serializer = LeaderboardEntrySerializer(entries, many=True)
        return Response(serializer.data)


class CompetitionViewSet(viewsets.ReadOnlyModelViewSet):
    """竞赛活动视图集"""
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Competition.objects.all().order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取进行中的竞赛"""
        competitions = Competition.objects.filter(status='active')
        serializer = self.get_serializer(competitions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """参加竞赛"""
        competition = self.get_object()
        
        if competition.status != 'active':
            return Response({'error': '竞赛未开始或已结束'}, status=status.HTTP_400_BAD_REQUEST)
        
        if competition.max_participants:
            current_participants = CompetitionParticipant.objects.filter(competition=competition).count()
            if current_participants >= competition.max_participants:
                return Response({'error': '参与人数已满'}, status=status.HTTP_400_BAD_REQUEST)
        
        participant, created = CompetitionParticipant.objects.get_or_create(
            competition=competition,
            user=request.user
        )
        
        if created:
            return Response({'message': '成功参加竞赛'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': '您已参加此竞赛'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """获取竞赛参与者"""
        competition = self.get_object()
        participants = CompetitionParticipant.objects.filter(
            competition=competition
        ).select_related('user').order_by('-score', 'joined_at')
        
        # 更新排名
        for idx, participant in enumerate(participants):
            participant.rank = idx + 1
            participant.save(update_fields=['rank'])
        
        serializer = CompetitionParticipantSerializer(participants, many=True)
        return Response(serializer.data)


class GameStatsViewSet(viewsets.ViewSet):
    """游戏统计视图集"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取游戏统计概览"""
        if request.user.role not in ['admin', 'teacher']:
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        today = timezone.now().date()
        
        stats = {
            'total_users': UserGameProfile.objects.count(),
            'active_users_today': UserGameProfile.objects.filter(last_activity_date=today).count(),
            'total_points_distributed': UserGameProfile.objects.aggregate(total=Sum('total_points'))['total'] or 0,
            'total_achievements_unlocked': UserAchievement.objects.count(),
            'average_level': UserGameProfile.objects.aggregate(avg=Avg('current_level'))['avg'] or 0,
            'top_streak': UserGameProfile.objects.aggregate(max=Max('max_streak'))['max'] or 0
        }
        
        serializer = GameStatsSerializer(stats)
        return Response(serializer.data)
