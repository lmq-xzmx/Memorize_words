from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.words.models import Word
# UserStreak已移除，因为该模型不存在
from apps.teaching.models import LearningGoal, LearningSession, WordLearningRecord
from .models import (
    UserEngagementMetrics, UserRetentionData, ABTestExperiment, ABTestParticipant,
    UserBehaviorPattern, GameElementEffectiveness
)
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta, date

User = get_user_model()


class AnalyticsOverviewSerializer(serializers.Serializer):
    """分析概览序列化器"""
    total_words = serializers.IntegerField(help_text='总单词数')
    learned_words = serializers.IntegerField(help_text='已学单词数')
    mastery_rate = serializers.FloatField(help_text='掌握率')
    study_streak = serializers.IntegerField(help_text='学习连续天数')
    total_study_time = serializers.FloatField(help_text='总学习时间（分钟）')
    average_accuracy = serializers.FloatField(help_text='平均正确率')
    words_this_week = serializers.IntegerField(help_text='本周学习单词数')
    sessions_this_week = serializers.IntegerField(help_text='本周学习会话数')
    

class DailyActivitySerializer(serializers.Serializer):
    """每日活动序列化器"""
    date = serializers.DateField(help_text='日期')
    words_learned = serializers.IntegerField(help_text='学习单词数')
    study_sessions = serializers.IntegerField(help_text='学习会话数')
    study_time = serializers.FloatField(help_text='学习时间（分钟）')
    accuracy_rate = serializers.FloatField(help_text='正确率')
    

class WeeklyProgressSerializer(serializers.Serializer):
    """周进度序列化器"""
    week_start = serializers.DateField(help_text='周开始日期')
    week_end = serializers.DateField(help_text='周结束日期')
    total_words = serializers.IntegerField(help_text='总学习单词数')
    total_sessions = serializers.IntegerField(help_text='总学习会话数')
    total_time = serializers.FloatField(help_text='总学习时间（分钟）')
    average_accuracy = serializers.FloatField(help_text='平均正确率')
    daily_activities = DailyActivitySerializer(many=True, help_text='每日活动')
    

class MonthlyStatisticsSerializer(serializers.Serializer):
    """月度统计序列化器"""
    month = serializers.CharField(help_text='月份（YYYY-MM）')
    total_words = serializers.IntegerField(help_text='总学习单词数')
    total_sessions = serializers.IntegerField(help_text='总学习会话数')
    total_time = serializers.FloatField(help_text='总学习时间（分钟）')
    average_accuracy = serializers.FloatField(help_text='平均正确率')
    active_days = serializers.IntegerField(help_text='活跃天数')
    

class WordMasteryDistributionSerializer(serializers.Serializer):
    """单词掌握分布序列化器"""
    mastery_level = serializers.CharField(help_text='掌握级别')
    word_count = serializers.IntegerField(help_text='单词数量')
    percentage = serializers.FloatField(help_text='百分比')
    

class LearningGoalProgressSerializer(serializers.Serializer):
    """学习目标进度序列化器"""
    goal_id = serializers.IntegerField(help_text='目标ID')
    goal_name = serializers.CharField(help_text='目标名称')
    target_words = serializers.IntegerField(help_text='目标单词数')
    current_words = serializers.IntegerField(help_text='当前单词数')
    completion_rate = serializers.FloatField(help_text='完成率')
    days_remaining = serializers.IntegerField(help_text='剩余天数')
    is_on_track = serializers.BooleanField(help_text='是否按计划进行')
    

class StudyPatternSerializer(serializers.Serializer):
    """学习模式序列化器"""
    hour = serializers.IntegerField(help_text='小时（0-23）')
    session_count = serializers.IntegerField(help_text='会话数量')
    average_accuracy = serializers.FloatField(help_text='平均正确率')
    

class WeekdayActivitySerializer(serializers.Serializer):
    """工作日活动序列化器"""
    weekday = serializers.CharField(help_text='星期几')
    session_count = serializers.IntegerField(help_text='会话数量')
    word_count = serializers.IntegerField(help_text='单词数量')
    average_time = serializers.FloatField(help_text='平均学习时间（分钟）')
    

class DifficultyAnalysisSerializer(serializers.Serializer):
    """难度分析序列化器"""
    difficulty_level = serializers.CharField(help_text='难度级别')
    word_count = serializers.IntegerField(help_text='单词数量')
    average_attempts = serializers.FloatField(help_text='平均尝试次数')
    average_accuracy = serializers.FloatField(help_text='平均正确率')
    

class LearningTrendSerializer(serializers.Serializer):
    """学习趋势序列化器"""
    period = serializers.CharField(help_text='时间段')
    words_learned = serializers.IntegerField(help_text='学习单词数')
    accuracy_rate = serializers.FloatField(help_text='正确率')
    study_time = serializers.FloatField(help_text='学习时间（分钟）')
    

class ComprehensiveAnalyticsSerializer(serializers.Serializer):
    """综合分析序列化器"""
    overview = AnalyticsOverviewSerializer(help_text='概览统计')
    weekly_progress = WeeklyProgressSerializer(many=True, help_text='周进度')
    monthly_statistics = MonthlyStatisticsSerializer(many=True, help_text='月度统计')
    mastery_distribution = WordMasteryDistributionSerializer(many=True, help_text='掌握分布')
    goal_progress = LearningGoalProgressSerializer(many=True, help_text='目标进度')
    study_patterns = StudyPatternSerializer(many=True, help_text='学习模式')
    weekday_activity = WeekdayActivitySerializer(many=True, help_text='工作日活动')
    difficulty_analysis = DifficultyAnalysisSerializer(many=True, help_text='难度分析')
    learning_trends = LearningTrendSerializer(many=True, help_text='学习趋势')
    

class ExportDataSerializer(serializers.Serializer):
    """导出数据序列化器"""
    format = serializers.ChoiceField(
        choices=[('csv', 'CSV'), ('json', 'JSON'), ('excel', 'Excel')],
        default='csv',
        help_text='导出格式'
    )
    data_type = serializers.ChoiceField(
        choices=[
            ('words', '单词数据'),
            ('sessions', '学习会话数据'),
            ('records', '学习记录数据'),
            ('goals', '学习目标数据'),
            ('analytics', '分析数据')
        ],
        help_text='数据类型'
    )
    date_from = serializers.DateField(
        required=False,
        help_text='开始日期'
    )
    date_to = serializers.DateField(
        required=False,
        help_text='结束日期'
    )
    
    def validate(self, attrs):
        """验证日期范围"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError('开始日期不能晚于结束日期')
        
        return attrs


class ChartDataSerializer(serializers.Serializer):
    """图表数据序列化器"""
    chart_type = serializers.ChoiceField(
        choices=[
            ('line', '折线图'),
            ('bar', '柱状图'),
            ('pie', '饼图'),
            ('area', '面积图'),
            ('scatter', '散点图')
        ],
        help_text='图表类型'
    )
    data_source = serializers.ChoiceField(
        choices=[
            ('daily_activity', '每日活动'),
            ('weekly_progress', '周进度'),
            ('monthly_stats', '月度统计'),
            ('mastery_distribution', '掌握分布'),
            ('study_patterns', '学习模式'),
            ('difficulty_analysis', '难度分析')
        ],
        help_text='数据源'
    )
    period = serializers.ChoiceField(
        choices=[
            ('7d', '最近7天'),
            ('30d', '最近30天'),
            ('90d', '最近90天'),
            ('1y', '最近1年'),
            ('all', '全部')
        ],
        default='30d',
        help_text='时间段'
    )
    

class UserComparisonSerializer(serializers.Serializer):
    """用户对比序列化器"""
    user_rank = serializers.IntegerField(help_text='用户排名')
    total_users = serializers.IntegerField(help_text='总用户数')
    percentile = serializers.FloatField(help_text='百分位数')
    words_learned = serializers.IntegerField(help_text='学习单词数')
    study_time = serializers.FloatField(help_text='学习时间（分钟）')
    accuracy_rate = serializers.FloatField(help_text='正确率')
    streak_days = serializers.IntegerField(help_text='连续学习天数')
    above_average = serializers.BooleanField(help_text='是否高于平均水平')


class UserEngagementMetricsSerializer(serializers.ModelSerializer):
    """用户粘性指标序列化器"""
    class Meta:
        model = UserEngagementMetrics
        fields = '__all__'
        read_only_fields = ('created_at', 'last_updated')


class UserRetentionDataSerializer(serializers.ModelSerializer):
    """用户留存数据序列化器"""
    class Meta:
        model = UserRetentionData
        fields = '__all__'
        read_only_fields = ('created_at',)


class ABTestExperimentSerializer(serializers.ModelSerializer):
    """A/B测试实验序列化器"""
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ABTestExperiment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_participants_count(self, obj):
        return obj.participants.count()


class ABTestParticipantSerializer(serializers.ModelSerializer):
    """A/B测试参与者序列化器"""
    experiment_name = serializers.CharField(source='experiment.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ABTestParticipant
        fields = '__all__'
        read_only_fields = ('joined_at',)


class UserBehaviorPatternSerializer(serializers.ModelSerializer):
    """用户行为模式序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserBehaviorPattern
        fields = '__all__'
        read_only_fields = ('last_updated',)


class GameElementEffectivenessSerializer(serializers.ModelSerializer):
    """游戏化元素效果序列化器"""
    measurement_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = GameElementEffectiveness
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_measurement_duration(self, obj):
        if obj.measurement_period_start and obj.measurement_period_end:
            duration = obj.measurement_period_end - obj.measurement_period_start
            return duration.days
        return 0


class EngagementAnalysisSerializer(serializers.Serializer):
    """用户粘性分析序列化器"""
    user_id = serializers.IntegerField()
    daily_active_days = serializers.IntegerField()
    weekly_active_days = serializers.IntegerField()
    monthly_active_days = serializers.IntegerField()
    total_study_time = serializers.FloatField()
    avg_session_length = serializers.FloatField()
    retention_rate = serializers.FloatField()
    engagement_score = serializers.FloatField()
    last_updated = serializers.DateTimeField()


class BehaviorAnalysisSerializer(serializers.Serializer):
    """用户行为分析序列化器"""
    user_id = serializers.IntegerField()
    preferred_study_time = serializers.CharField()
    avg_session_length = serializers.IntegerField()
    preferred_difficulty = serializers.CharField()
    engagement_type = serializers.CharField()
    motivation_factors = serializers.ListField()
    social_activity_level = serializers.CharField()
    competitive_tendency = serializers.FloatField()
    learning_style = serializers.CharField()
    retention_rate = serializers.FloatField()
    churn_risk_score = serializers.FloatField()
    engagement_score = serializers.FloatField()
    last_updated = serializers.DateTimeField()


class ABTestResultSerializer(serializers.Serializer):
    """A/B测试结果序列化器"""
    experiment = serializers.DictField()
    results = serializers.DictField()


class GameElementAnalysisSerializer(serializers.Serializer):
    """游戏化元素分析序列化器"""
    element_name = serializers.CharField()
    element_type = serializers.CharField()
    engagement_impact = serializers.FloatField()
    retention_impact = serializers.FloatField()
    learning_efficiency_impact = serializers.FloatField()
    total_interactions = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    avg_interaction_frequency = serializers.FloatField()
    measurement_period = serializers.DictField()