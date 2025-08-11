from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()
import json


class UserEngagementMetrics(models.Model):
    """用户粘性指标模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField(default=timezone.now)
    
    # 基础指标
    session_count = models.IntegerField(default=0, help_text='当日会话次数')
    total_session_duration = models.IntegerField(default=0, help_text='总会话时长(秒)')
    avg_session_duration = models.FloatField(default=0.0, help_text='平均会话时长(秒)')
    peak_activity_hour = models.IntegerField(null=True, blank=True, help_text='活跃高峰时段(0-23)')
    
    # 学习指标
    words_practiced = models.IntegerField(default=0, help_text='练习单词数')
    correct_answers = models.IntegerField(default=0, help_text='正确答题数')
    total_answers = models.IntegerField(default=0, help_text='总答题数')
    accuracy_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # 游戏化指标
    exp_gained = models.IntegerField(default=0, help_text='获得经验值')
    coins_earned = models.IntegerField(default=0, help_text='获得金币')
    achievements_unlocked = models.IntegerField(default=0, help_text='解锁成就数')
    streak_count = models.IntegerField(default=0, help_text='连击次数')
    
    # 社交指标
    battles_participated = models.IntegerField(default=0, help_text='参与对战次数')
    battles_won = models.IntegerField(default=0, help_text='对战胜利次数')
    social_interactions = models.IntegerField(default=0, help_text='社交互动次数')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = '用户粘性指标'
        verbose_name_plural = '用户粘性指标'
    
    def __str__(self):
        return f'{self.user.username} - {self.date}'


class UserRetentionData(models.Model):
    """用户留存数据模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='retention_data')
    registration_date = models.DateField(help_text='注册日期')
    
    # 留存指标
    day_1_retention = models.BooleanField(default=False, help_text='次日留存')
    day_3_retention = models.BooleanField(default=False, help_text='3日留存')
    day_7_retention = models.BooleanField(default=False, help_text='7日留存')
    day_14_retention = models.BooleanField(default=False, help_text='14日留存')
    day_30_retention = models.BooleanField(default=False, help_text='30日留存')
    
    # 活跃度指标
    total_active_days = models.IntegerField(default=0, help_text='总活跃天数')
    consecutive_active_days = models.IntegerField(default=0, help_text='连续活跃天数')
    last_active_date = models.DateField(null=True, blank=True, help_text='最后活跃日期')
    
    # 生命周期价值
    total_sessions = models.IntegerField(default=0, help_text='总会话数')
    total_study_time = models.IntegerField(default=0, help_text='总学习时长(分钟)')
    total_words_learned = models.IntegerField(default=0, help_text='总学习单词数')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'registration_date']
        ordering = ['-registration_date']
        verbose_name = '用户留存数据'
        verbose_name_plural = '用户留存数据'
    
    def __str__(self):
        return f'{self.user.username} - 注册于{self.registration_date}'


class ABTestExperiment(models.Model):
    """A/B测试实验模型"""
    name = models.CharField(max_length=100, unique=True, help_text='实验名称')
    description = models.TextField(help_text='实验描述')
    
    # 实验配置
    start_date = models.DateTimeField(help_text='开始时间')
    end_date = models.DateTimeField(help_text='结束时间')
    is_active = models.BooleanField(default=True, help_text='是否激活')
    
    # 实验参数
    control_group_ratio = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text='对照组比例')
    experiment_config = models.JSONField(default=dict, help_text='实验配置参数')
    
    # 目标指标
    target_metric = models.CharField(max_length=50, help_text='目标指标')
    success_criteria = models.TextField(help_text='成功标准')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'A/B测试实验'
        verbose_name_plural = 'A/B测试实验'
    
    def __str__(self):
        return self.name


class ABTestParticipant(models.Model):
    """A/B测试参与者模型"""
    GROUP_CHOICES = [
        ('control', '对照组'),
        ('experiment', '实验组'),
    ]
    
    experiment = models.ForeignKey(ABTestExperiment, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ab_test_participations')
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, help_text='分组')
    
    # 参与数据
    joined_at = models.DateTimeField(auto_now_add=True, help_text='加入时间')
    conversion_achieved = models.BooleanField(default=False, help_text='是否达成转化')
    conversion_date = models.DateTimeField(null=True, blank=True, help_text='转化时间')
    
    # 指标数据
    metric_value = models.FloatField(null=True, blank=True, help_text='指标值')
    additional_data = models.JSONField(default=dict, help_text='额外数据')
    
    class Meta:
        unique_together = ['experiment', 'user']
        ordering = ['-joined_at']
        verbose_name = 'A/B测试参与者'
        verbose_name_plural = 'A/B测试参与者'
    
    def __str__(self):
        return f'{self.user.username} - {self.experiment.name} ({self.group})'


class UserBehaviorPattern(models.Model):
    """用户行为模式模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behavior_patterns')
    
    # 学习偏好
    preferred_study_time = models.CharField(max_length=20, help_text='偏好学习时间段')
    avg_session_length = models.IntegerField(help_text='平均会话时长(分钟)')
    preferred_difficulty = models.CharField(max_length=20, help_text='偏好难度')
    
    # 游戏化偏好
    engagement_type = models.CharField(max_length=30, help_text='参与类型')
    motivation_factors = models.JSONField(default=list, help_text='激励因素')
    
    # 社交偏好
    social_activity_level = models.CharField(max_length=20, help_text='社交活跃度')
    competitive_tendency = models.FloatField(default=0.0, help_text='竞争倾向')
    
    # 学习模式
    learning_style = models.CharField(max_length=30, help_text='学习风格')
    retention_rate = models.FloatField(default=0.0, help_text='记忆保持率')
    
    # 风险指标
    churn_risk_score = models.FloatField(default=0.0, help_text='流失风险评分')
    engagement_score = models.FloatField(default=0.0, help_text='参与度评分')
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_updated']
        verbose_name = '用户行为模式'
        verbose_name_plural = '用户行为模式'
    
    def __str__(self):
        return f'{self.user.username} - 行为模式'


class GameElementEffectiveness(models.Model):
    """游戏化元素效果模型"""
    element_name = models.CharField(max_length=50, help_text='游戏化元素名称')
    element_type = models.CharField(max_length=30, help_text='元素类型')
    
    # 效果指标
    engagement_impact = models.FloatField(default=0.0, help_text='参与度影响')
    retention_impact = models.FloatField(default=0.0, help_text='留存影响')
    learning_efficiency_impact = models.FloatField(default=0.0, help_text='学习效率影响')
    
    # 使用数据
    total_interactions = models.IntegerField(default=0, help_text='总交互次数')
    unique_users = models.IntegerField(default=0, help_text='独立用户数')
    avg_interaction_frequency = models.FloatField(default=0.0, help_text='平均交互频率')
    
    # 时间数据
    measurement_period_start = models.DateTimeField(help_text='测量周期开始')
    measurement_period_end = models.DateTimeField(help_text='测量周期结束')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '游戏化元素效果'
        verbose_name_plural = '游戏化元素效果'
    
    def __str__(self):
        return f'{self.element_name} - 效果分析'