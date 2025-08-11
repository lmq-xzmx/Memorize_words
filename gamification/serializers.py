from rest_framework import serializers
from .models import (
    UserGameProfile, PointTransaction, Level, Achievement, 
    UserAchievement, Leaderboard, Competition, CompetitionParticipant
)
from django.contrib.auth import get_user_model

User = get_user_model()


class UserGameProfileSerializer(serializers.ModelSerializer):
    """用户游戏档案序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    
    class Meta:
        model = UserGameProfile
        fields = [
            'id', 'username', 'real_name', 'total_points', 'available_points',
            'current_level', 'experience_points', 'current_streak', 'max_streak',
            'last_activity_date', 'achievements_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_points', 'achievements_count', 'created_at', 'updated_at']


class PointTransactionSerializer(serializers.ModelSerializer):
    """积分交易记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = [
            'id', 'username', 'points', 'transaction_type', 'transaction_type_display',
            'reason', 'created_at'
        ]
        read_only_fields = ['created_at']


class LevelSerializer(serializers.ModelSerializer):
    """等级配置序列化器"""
    
    class Meta:
        model = Level
        fields = [
            'id', 'level', 'name', 'required_experience', 'rewards',
            'icon', 'description'
        ]


class AchievementSerializer(serializers.ModelSerializer):
    """成就配置序列化器"""
    achievement_type_display = serializers.CharField(source='get_achievement_type_display', read_only=True)
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'achievement_type', 'achievement_type_display',
            'icon', 'points_reward', 'conditions', 'is_hidden', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    """用户成就序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    achievement_name = serializers.CharField(source='achievement.name', read_only=True)
    achievement_description = serializers.CharField(source='achievement.description', read_only=True)
    achievement_icon = serializers.CharField(source='achievement.icon', read_only=True)
    points_reward = serializers.IntegerField(source='achievement.points_reward', read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = [
            'id', 'username', 'achievement_name', 'achievement_description',
            'achievement_icon', 'points_reward', 'unlocked_at', 'progress'
        ]
        read_only_fields = ['unlocked_at']


class LeaderboardSerializer(serializers.ModelSerializer):
    """排行榜配置序列化器"""
    leaderboard_type_display = serializers.CharField(source='get_leaderboard_type_display', read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'name', 'leaderboard_type', 'leaderboard_type_display',
            'description', 'is_active', 'reset_frequency', 'last_reset', 'created_at'
        ]
        read_only_fields = ['last_reset', 'created_at']


class LeaderboardEntrySerializer(serializers.Serializer):
    """排行榜条目序列化器"""
    rank = serializers.IntegerField()
    username = serializers.CharField()
    real_name = serializers.CharField()
    score = serializers.IntegerField()
    avatar = serializers.CharField(required=False)


class CompetitionSerializer(serializers.ModelSerializer):
    """竞赛活动序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Competition
        fields = [
            'id', 'name', 'description', 'start_time', 'end_time',
            'status', 'status_display', 'rules', 'rewards',
            'max_participants', 'participants_count', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_participants_count(self, obj):
        return obj.competitionparticipant_set.count()


class CompetitionParticipantSerializer(serializers.ModelSerializer):
    """竞赛参与者序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.real_name', read_only=True)
    competition_name = serializers.CharField(source='competition.name', read_only=True)
    
    class Meta:
        model = CompetitionParticipant
        fields = [
            'id', 'username', 'real_name', 'competition_name',
            'score', 'rank', 'joined_at'
        ]
        read_only_fields = ['joined_at']


class GameStatsSerializer(serializers.Serializer):
    """游戏统计数据序列化器"""
    total_users = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    total_points_distributed = serializers.IntegerField()
    total_achievements_unlocked = serializers.IntegerField()
    average_level = serializers.FloatField()
    top_streak = serializers.IntegerField()