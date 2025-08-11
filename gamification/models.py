from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

User = get_user_model()


class UserGameProfile(models.Model):
    """用户游戏化档案"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户', related_name='game_profile')
    total_points = models.PositiveIntegerField('总积分', default=0)
    available_points = models.PositiveIntegerField('可用积分', default=0)
    current_level = models.PositiveIntegerField('当前等级', default=1)
    experience_points = models.PositiveIntegerField('经验值', default=0)
    current_streak = models.PositiveIntegerField('当前连击', default=0)
    max_streak = models.PositiveIntegerField('最高连击', default=0)
    last_activity_date = models.DateField('最后活动日期', null=True, blank=True)
    achievements_count = models.PositiveIntegerField('成就数量', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户游戏档案'
        verbose_name_plural = '用户游戏档案'
        
    def __str__(self):
        return f"{self.user.username} - Level {self.current_level}"
    
    def add_points(self, points, reason=''):
        """添加积分"""
        self.total_points += points
        self.available_points += points
        self.save()
        
        # 记录积分交易
        PointTransaction.objects.create(
            user=self.user,
            points=points,
            transaction_type='earn',
            reason=reason
        )
    
    def spend_points(self, points, reason=''):
        """消费积分"""
        if self.available_points >= points:
            self.available_points -= points
            self.save()
            
            # 记录积分交易
            PointTransaction.objects.create(
                user=self.user,
                points=-points,
                transaction_type='spend',
                reason=reason
            )
            return True
        return False
    
    def update_streak(self):
        """更新连击"""
        today = timezone.now().date()
        if self.last_activity_date:
            if self.last_activity_date == today:
                return  # 今天已经更新过
            elif self.last_activity_date == today - timedelta(days=1):
                self.current_streak += 1
            else:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        if self.current_streak > self.max_streak:
            self.max_streak = self.current_streak
        
        self.last_activity_date = today
        self.save()


class PointTransaction(models.Model):
    """积分交易记录"""
    TRANSACTION_TYPES = [
        ('earn', '获得'),
        ('spend', '消费'),
        ('bonus', '奖励'),
        ('penalty', '扣除'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    points = models.IntegerField('积分变化')
    transaction_type = models.CharField('交易类型', max_length=10, choices=TRANSACTION_TYPES)
    reason = models.CharField('原因', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '积分交易记录'
        verbose_name_plural = '积分交易记录'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} {self.get_transaction_type_display()} {self.points}积分"


class Level(models.Model):
    """等级配置"""
    level = models.PositiveIntegerField('等级', unique=True)
    name = models.CharField('等级名称', max_length=50)
    required_experience = models.PositiveIntegerField('所需经验值')
    rewards = models.JSONField('奖励配置', default=dict, help_text='JSON格式的奖励配置')
    icon = models.CharField('图标', max_length=100, blank=True)
    description = models.TextField('描述', blank=True)
    
    class Meta:
        verbose_name = '等级配置'
        verbose_name_plural = '等级配置'
        ordering = ['level']
        
    def __str__(self):
        return f"Level {self.level}: {self.name}"


class Achievement(models.Model):
    """成就配置"""
    ACHIEVEMENT_TYPES = [
        ('learning', '学习类'),
        ('social', '社交类'),
        ('streak', '连击类'),
        ('points', '积分类'),
        ('special', '特殊类'),
    ]
    
    name = models.CharField('成就名称', max_length=100)
    description = models.TextField('成就描述')
    achievement_type = models.CharField('成就类型', max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField('图标', max_length=100, blank=True)
    points_reward = models.PositiveIntegerField('积分奖励', default=0)
    conditions = models.JSONField('解锁条件', default=dict, help_text='JSON格式的解锁条件')
    is_hidden = models.BooleanField('隐藏成就', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '成就配置'
        verbose_name_plural = '成就配置'
        
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """用户成就"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name='成就')
    unlocked_at = models.DateTimeField('解锁时间', auto_now_add=True)
    progress = models.JSONField('进度数据', default=dict, blank=True)
    
    class Meta:
        verbose_name = '用户成就'
        verbose_name_plural = '用户成就'
        unique_together = ['user', 'achievement']
        
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class Leaderboard(models.Model):
    """排行榜配置"""
    LEADERBOARD_TYPES = [
        ('points', '积分榜'),
        ('streak', '连击榜'),
        ('achievements', '成就榜'),
        ('learning_time', '学习时长榜'),
        ('weekly', '周榜'),
        ('monthly', '月榜'),
    ]
    
    name = models.CharField('排行榜名称', max_length=100)
    leaderboard_type = models.CharField('排行榜类型', max_length=20, choices=LEADERBOARD_TYPES)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    reset_frequency = models.CharField('重置频率', max_length=20, choices=[
        ('never', '永不重置'),
        ('daily', '每日'),
        ('weekly', '每周'),
        ('monthly', '每月'),
    ], default='never')
    last_reset = models.DateTimeField('最后重置时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '排行榜配置'
        verbose_name_plural = '排行榜配置'
        
    def __str__(self):
        return self.name


class Competition(models.Model):
    """竞赛活动"""
    COMPETITION_STATUS = [
        ('upcoming', '即将开始'),
        ('active', '进行中'),
        ('ended', '已结束'),
        ('cancelled', '已取消'),
    ]
    
    name = models.CharField('竞赛名称', max_length=100)
    description = models.TextField('竞赛描述')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    status = models.CharField('状态', max_length=20, choices=COMPETITION_STATUS, default='upcoming')
    rules = models.JSONField('竞赛规则', default=dict)
    rewards = models.JSONField('奖励配置', default=dict)
    max_participants = models.PositiveIntegerField('最大参与人数', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '竞赛活动'
        verbose_name_plural = '竞赛活动'
        
    def __str__(self):
        return self.name


class CompetitionParticipant(models.Model):
    """竞赛参与者"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, verbose_name='竞赛')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    score = models.PositiveIntegerField('得分', default=0)
    rank = models.PositiveIntegerField('排名', null=True, blank=True)
    joined_at = models.DateTimeField('参与时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '竞赛参与者'
        verbose_name_plural = '竞赛参与者'
        unique_together = ['competition', 'user']
        
    def __str__(self):
        return f"{self.user.username} - {self.competition.name}"
