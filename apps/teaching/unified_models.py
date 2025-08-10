"""
统一学习管理数据模型
整合Teaching与Vocabulary_Manager的重叠功能
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from typing import Dict, List

User = get_user_model()


class UnifiedLearningGoal(models.Model):
    """统一学习目标模型"""
    GOAL_TYPE_CHOICES = [
        ('vocabulary_list', '词库'),
        ('word_set', '词集'),
        ('grade_level', '分级'),
        ('custom', '自定义'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='unified_learning_goals',
        verbose_name='用户'
    )
    name = models.CharField(max_length=200, verbose_name='目标名称')
    description = models.TextField(blank=True, verbose_name='目标描述')
    goal_type = models.CharField(
        max_length=20, 
        choices=GOAL_TYPE_CHOICES, 
        default='custom',
        verbose_name='目标类型'
    )
    
    # 目标参数
    target_words_count = models.IntegerField(default=100, verbose_name='目标单词数量')
    start_date = models.DateField(default=timezone.now, verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_current = models.BooleanField(default=False, verbose_name='是否为当前目标')
    
    # 关联资源
    word_sets = models.ManyToManyField(
        'words.WordSet', 
        blank=True, 
        verbose_name='关联单词集',
        related_name='unified_goals'
    )
    vocabulary_lists = models.ManyToManyField(
        'words.VocabularyList', 
        blank=True, 
        verbose_name='关联单词库',
        related_name='unified_goals'
    )
    
    # 进度统计
    total_words = models.IntegerField(default=0, verbose_name='总单词数')
    learned_words = models.IntegerField(default=0, verbose_name='已学单词数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '统一学习目标'
        verbose_name_plural = '统一学习目标'
        ordering = ['-is_current', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'is_current']),
        ]
    
    def __str__(self):
        current_mark = "[当前]" if self.is_current else ""
        return f"{current_mark}{self.name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        # 如果设置为当前目标，取消其他目标的当前状态
        if self.is_current:
            UnifiedLearningGoal.objects.filter(
                user=self.user, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        
        super().save(*args, **kwargs)
        
        # 同步单词
        if self.pk:
            self.sync_words_from_sources()
    
    def sync_words_from_sources(self):
        """从关联的单词集和单词库同步单词"""
        from apps.words.models import Word
        
        # 获取所有关联的单词
        wordset_words = Word.objects.filter(
            wordset__in=self.word_sets.all()
        ).distinct()
        
        vocabularylist_words = Word.objects.filter(
            vocabulary_list__in=self.vocabulary_lists.all()
        ).distinct()
        
        # 合并所有单词
        all_words = wordset_words.union(vocabularylist_words)
        
        # 为每个单词创建UnifiedGoalWord关联
        for word in all_words:
            UnifiedGoalWord.objects.get_or_create(
                goal=self,
                word=word,
                defaults={'added_at': timezone.now()}
            )
        
        # 更新总单词数
        self.total_words = UnifiedGoalWord.objects.filter(goal=self).count()
        self.save(update_fields=['total_words'])
    
    def get_progress_stats(self) -> Dict:
        """获取九宫格进度统计"""
        goal_words = UnifiedGoalWord.objects.filter(goal=self)
        progress_records = UnifiedWordProgress.objects.filter(
            user=self.user,
            goal=self
        )
        
        # 创建进度字典
        progress_dict = {
            record.word_id: record for record in progress_records
        }
        
        stats = {
            'review_1': 0, 'review_2': 0, 'review_3': 0,
            'review_4': 0, 'review_5': 0, 'review_6': 0,
            'mastered': 0, 'forgotten': 0, 'pending': 0
        }
        
        for goal_word in goal_words:
            progress = progress_dict.get(goal_word.word_id)
            if progress:
                if progress.is_mastered:
                    stats['mastered'] += 1
                elif progress.is_forgotten:
                    stats['forgotten'] += 1
                elif progress.review_count > 0:
                    review_key = f'review_{min(progress.review_count, 6)}'
                    stats[review_key] += 1
                else:
                    stats['pending'] += 1
            else:
                stats['pending'] += 1
        
        return stats
    
    @property
    def progress_percentage(self):
        """学习进度百分比"""
        if self.total_words == 0:
            return 0
        return round((self.learned_words / self.total_words) * 100, 2)


class UnifiedGoalWord(models.Model):
    """统一目标单词关联模型"""
    goal = models.ForeignKey(
        UnifiedLearningGoal, 
        on_delete=models.CASCADE, 
        related_name='goal_words',
        verbose_name='学习目标'
    )
    word = models.ForeignKey(
        'words.Word', 
        on_delete=models.CASCADE, 
        related_name='unified_goal_associations',
        verbose_name='单词'
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    
    class Meta:
        verbose_name = '统一目标单词'
        verbose_name_plural = '统一目标单词'
        unique_together = ['goal', 'word']
        indexes = [
            models.Index(fields=['goal', 'word']),
        ]
    
    def __str__(self):
        return f"{self.goal.name} - {self.word.word}"


class UnifiedLearningSession(models.Model):
    """统一学习会话模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='unified_learning_sessions',
        verbose_name='用户'
    )
    goal = models.ForeignKey(
        UnifiedLearningGoal, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        verbose_name='学习目标'
    )
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    
    # 会话统计
    words_studied = models.IntegerField(default=0, verbose_name='学习单词数')
    words_learned = models.IntegerField(default=0, verbose_name='掌握单词数')
    correct_answers = models.IntegerField(default=0, verbose_name='正确答案数')
    total_answers = models.IntegerField(default=0, verbose_name='总答案数')
    
    class Meta:
        verbose_name = '统一学习会话'
        verbose_name_plural = '统一学习会话'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def accuracy_rate(self):
        """正确率"""
        if self.total_answers == 0:
            return 0
        return round((self.correct_answers / self.total_answers) * 100, 2)
    
    @property
    def duration(self):
        """学习时长（分钟）"""
        if not self.end_time:
            return 0
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 60, 2)
    
    @property
    def learning_efficiency(self):
        """学习效率（掌握率）"""
        if self.words_studied == 0:
            return 0
        return round((self.words_learned / self.words_studied) * 100, 2)
    
    def end_session(self):
        """结束学习会话"""
        if not self.end_time:
            self.end_time = timezone.now()
            self.save(update_fields=['end_time'])


class UnifiedWordProgress(models.Model):
    """统一单词学习进度模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='unified_word_progress',
        verbose_name='用户'
    )
    goal = models.ForeignKey(
        UnifiedLearningGoal, 
        on_delete=models.CASCADE, 
        related_name='word_progress',
        verbose_name='学习目标'
    )
    word = models.ForeignKey(
        'words.Word', 
        on_delete=models.CASCADE, 
        related_name='unified_progress',
        verbose_name='单词'
    )
    
    # 学习次数统计
    review_count = models.IntegerField(default=0, verbose_name='复习次数')
    last_review_date = models.DateTimeField(null=True, blank=True, verbose_name='最后复习时间')
    
    # 学习状态
    is_mastered = models.BooleanField(default=False, verbose_name='是否已掌握')
    is_forgotten = models.BooleanField(default=False, verbose_name='是否已遗忘')
    mastered_date = models.DateTimeField(null=True, blank=True, verbose_name='掌握时间')
    
    # 时间记录
    first_learned_date = models.DateTimeField(auto_now_add=True, verbose_name='首次学习时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '统一单词学习进度'
        verbose_name_plural = '统一单词学习进度'
        unique_together = ['user', 'goal', 'word']
        indexes = [
            models.Index(fields=['user', 'goal']),
            models.Index(fields=['review_count']),
            models.Index(fields=['is_mastered']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.word.word} ({self.review_count}次)"
    
    def add_review(self):
        """添加一次复习"""
        self.review_count += 1
        self.last_review_date = timezone.now()
        
        # 如果复习次数达到6次以上，标记为已掌握
        if self.review_count >= 6 and not self.is_mastered:
            self.is_mastered = True
            self.mastered_date = timezone.now()
        
        self.save()
    
    def mark_as_forgotten(self):
        """标记为遗忘"""
        self.is_forgotten = True
        self.save()
    
    def reset_progress(self):
        """重置学习进度"""
        self.review_count = 0
        self.is_mastered = False
        self.is_forgotten = False
        self.mastered_date = None
        self.last_review_date = None
        self.save()
    
    @property
    def status(self):
        """获取学习状态"""
        if self.is_mastered:
            return 'mastered'
        elif self.is_forgotten:
            return 'forgotten'
        elif self.review_count > 0:
            return f'review_{min(self.review_count, 6)}'
        else:
            return 'not_started'


class UnifiedLearningPlan(models.Model):
    """统一学习计划模型"""
    PLAN_MODE_CHOICES = [
        ('mechanical', '机械模式 - 固定每日学习量'),
        ('daily_progress', '日进模式 - 根据学习进展每日更新'),
        ('workday', '工作日模式 - 只在工作日学习'),
        ('weekend', '周末模式 - 只在周末学习'),
    ]
    
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('completed', '已完成'),
        ('paused', '已暂停'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='unified_learning_plans',
        verbose_name='用户'
    )
    goal = models.ForeignKey(
        UnifiedLearningGoal, 
        on_delete=models.CASCADE, 
        related_name='learning_plans',
        verbose_name='学习目标'
    )
    name = models.CharField(max_length=100, verbose_name='计划名称')
    plan_mode = models.CharField(
        max_length=20, 
        choices=PLAN_MODE_CHOICES,
        default='daily_progress',
        verbose_name='计划模式'
    )
    
    # 计划参数
    start_date = models.DateField(default=date.today, verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    daily_target = models.IntegerField(default=10, verbose_name='每日目标单词数')
    
    # 状态
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='状态'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '统一学习计划'
        verbose_name_plural = '统一学习计划'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['goal']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def clean(self):
        """验证数据"""
        if self.end_date <= self.start_date:
            raise ValidationError({'end_date': '结束日期必须晚于开始日期'})
    
    def calculate_daily_target(self):
        """计算每日目标单词数"""
        remaining_words = self.goal.total_words - self.goal.learned_words
        
        if self.plan_mode == 'mechanical':
            total_days = (self.end_date - self.start_date).days + 1
            self.daily_target = max(1, remaining_words // total_days)
        elif self.plan_mode == 'daily_progress':
            remaining_days = (self.end_date - date.today()).days + 1
            self.daily_target = max(1, remaining_words // max(1, remaining_days))
        elif self.plan_mode == 'workday':
            remaining_workdays = self._count_workdays(date.today(), self.end_date)
            self.daily_target = max(1, remaining_words // max(1, remaining_workdays))
        elif self.plan_mode == 'weekend':
            remaining_weekends = self._count_weekends(date.today(), self.end_date)
            self.daily_target = max(1, remaining_words // max(1, remaining_weekends))
    
    def _count_workdays(self, start_date, end_date):
        """计算工作日数量"""
        workdays = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:
                workdays += 1
            current_date += timedelta(days=1)
        return workdays
    
    def _count_weekends(self, start_date, end_date):
        """计算周末天数"""
        weekend_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() >= 5:
                weekend_days += 1
            current_date += timedelta(days=1)
        return weekend_days


class UnifiedDailyRecord(models.Model):
    """统一每日学习记录"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='unified_daily_records',
        verbose_name='用户'
    )
    plan = models.ForeignKey(
        UnifiedLearningPlan, 
        on_delete=models.CASCADE, 
        related_name='daily_records',
        verbose_name='学习计划'
    )
    study_date = models.DateField(default=date.today, verbose_name='学习日期')
    target_words = models.IntegerField(default=0, verbose_name='目标单词数')
    completed_words = models.IntegerField(default=0, verbose_name='完成单词数')
    study_duration = models.DurationField(null=True, blank=True, verbose_name='学习时长')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '统一每日学习记录'
        verbose_name_plural = '统一每日学习记录'
        ordering = ['-study_date']
        unique_together = ['user', 'plan', 'study_date']
        indexes = [
            models.Index(fields=['user', 'study_date']),
            models.Index(fields=['plan', 'study_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.study_date} ({self.completed_words}/{self.target_words})"
    
    @property
    def completion_rate(self):
        """完成率"""
        if self.target_words == 0:
            return 0
        return round((self.completed_words / self.target_words) * 100, 2)
    
    @property
    def is_completed(self):
        """是否完成当日目标"""
        return self.completed_words >= self.target_words