from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import calendar


class StudySession(models.Model):
    """学习会话模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_sessions',
        verbose_name=_('用户')
    )
    learning_goal = models.ForeignKey(
        'LearningGoal',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='study_sessions',
        verbose_name=_('学习目标')
    )
    start_time = models.DateTimeField(_('开始时间'), auto_now_add=True)
    end_time = models.DateTimeField(_('结束时间'), null=True, blank=True)
    duration = models.DurationField(_('学习时长'), null=True, blank=True)
    words_studied = models.IntegerField(_('学习单词数'), default=0)
    words_learned = models.IntegerField(_('掌握单词数'), default=0)
    
    class Meta:
        verbose_name = _('学习会话')
        verbose_name_plural = _('学习会话')
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def end_session(self):
        """结束学习会话"""
        if not self.end_time:
            self.end_time = timezone.now()
            self.duration = self.end_time - self.start_time
            self.save(update_fields=['end_time', 'duration'])
    
    @property
    def is_active(self):
        """是否为活跃会话"""
        return self.end_time is None
    
    @property
    def learning_efficiency(self):
        """学习效率（掌握率）"""
        if self.words_studied == 0:
            return 0
        return round((self.words_learned / self.words_studied) * 100, 2)


class UserStreak(models.Model):
    """用户连续学习记录"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak',
        verbose_name=_('用户')
    )
    current_streak = models.IntegerField(_('当前连续天数'), default=0)
    longest_streak = models.IntegerField(_('最长连续天数'), default=0)
    last_study_date = models.DateField(_('最后学习日期'), null=True, blank=True)
    total_study_days = models.IntegerField(_('总学习天数'), default=0)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('用户连续学习记录')
        verbose_name_plural = _('用户连续学习记录')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['last_study_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - 连续{self.current_streak}天"
    
    def update_streak(self, study_date=None):
        """更新连续学习记录"""
        if study_date is None:
            study_date = date.today()
        
        if self.last_study_date is None:
            # 第一次学习
            self.current_streak = 1
            self.longest_streak = 1
            self.total_study_days = 1
        elif study_date == self.last_study_date:
            # 同一天，不更新连续天数
            return
        elif study_date == self.last_study_date + timedelta(days=1):
            # 连续学习
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
            self.total_study_days += 1
        elif study_date > self.last_study_date + timedelta(days=1):
            # 中断了连续学习
            self.current_streak = 1
            self.total_study_days += 1
        
        self.last_study_date = study_date
        self.save()
    
    def reset_streak(self):
        """重置连续学习记录"""
        self.current_streak = 0
        self.save(update_fields=['current_streak', 'updated_at'])


class LearningGoal(models.Model):
    """学习目标模型"""
    GOAL_TYPE_CHOICES = [
        ('vocabulary_list', '词库'),
        ('word_set', '词集'),
        ('grade_level', '分级'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_goals',
        verbose_name=_('用户')
    )
    name = models.CharField(_('目标名称'), max_length=100)
    description = models.TextField(_('目标描述'), blank=True)
    goal_type = models.CharField(_('目标类型'), max_length=20, choices=GOAL_TYPE_CHOICES)
    
    # 关联不同类型的目标源
    vocabulary_list = models.ForeignKey(
        'words.VocabularyList',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_('词库列表')
    )
    word_set = models.ForeignKey(
        'words.WordSet',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_('词集')
    )
    grade_level = models.ForeignKey(
        'words.WordGradeLevel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_('分级等级')
    )
    
    is_current = models.BooleanField(_('是否为当前目标'), default=False)
    total_words = models.IntegerField(_('总单词数'), default=0)
    learned_words = models.IntegerField(_('已学单词数'), default=0)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('学习目标')
        verbose_name_plural = _('学习目标')
        ordering = ['-is_current', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_current']),
            models.Index(fields=['goal_type']),
        ]
    
    def __str__(self):
        current_mark = "[当前]" if self.is_current else ""
        return f"{current_mark}{self.name} ({self.user.username})"
    
    def clean(self):
        """验证数据"""
        # 确保目标类型与关联字段匹配
        if self.goal_type == 'vocabulary_list' and not self.vocabulary_list:
            raise ValidationError({'vocabulary_list': '词库类型必须选择词库列表'})
        elif self.goal_type == 'word_set' and not self.word_set:
            raise ValidationError({'word_set': '词集类型必须选择词集'})
        elif self.goal_type == 'grade_level' and not self.grade_level:
            raise ValidationError({'grade_level': '分级类型必须选择分级等级'})
    
    def save(self, *args, **kwargs):
        # 如果设置为当前目标，取消其他目标的当前状态
        if self.is_current:
            LearningGoal.objects.filter(
                user=self.user, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        
        # 计算总单词数
        if not self.total_words:
            self.total_words = self.get_word_count()
        
        super().save(*args, **kwargs)
    
    def get_word_count(self):
        """获取目标包含的单词数量"""
        if self.goal_type == 'vocabulary_list' and self.vocabulary_list:
            return self.vocabulary_list.words.count()
        elif self.goal_type == 'word_set' and self.word_set:
            return self.word_set.words.count()
        elif self.goal_type == 'grade_level' and self.grade_level:
            return self.grade_level.get_words().count()
        return 0
    
    def get_words(self):
        """获取目标包含的所有单词"""
        from apps.words.models import Word
        if self.goal_type == 'vocabulary_list' and self.vocabulary_list:
            return self.vocabulary_list.words.all()
        elif self.goal_type == 'word_set' and self.word_set:
            return self.word_set.words.all()
        elif self.goal_type == 'grade_level' and self.grade_level:
            return self.grade_level.get_words()
        return Word.objects.none()
    
    def update_progress(self):
        """更新学习进度"""
        # 统计用户已学习的单词数量
        words = self.get_words()
        learned_count = words.filter(
            user=self.user,
            is_learned=True
        ).count()
        
        self.learned_words = learned_count
        self.save(update_fields=['learned_words', 'updated_at'])
        return learned_count
    
    @property
    def progress_percentage(self):
        """学习进度百分比"""
        if self.total_words == 0:
            return 0
        return round((self.learned_words / self.total_words) * 100, 2)
    
    @property
    def remaining_words(self):
        """剩余单词数"""
        return max(0, self.total_words - self.learned_words)


class LearningPlan(models.Model):
    """学习计划模型"""
    PLAN_MODE_CHOICES = [
        ('mechanical', '机械模式 - 固定每日学习量，不考虑学习进展更新'),
        ('daily_progress', '日进模式 - 根据学习进展每日更新，按剩余时间均分'),
        ('workday', '工作日模式 - 只在工作日学习，按剩余工作日均分'),
        ('weekend', '周末模式 - 只在周末学习，按剩余周末天数均分'),
    ]
    
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('completed', '已完成'),
        ('paused', '已暂停'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_plans',
        verbose_name=_('用户')
    )
    learning_goal = models.ForeignKey(
        LearningGoal,
        on_delete=models.CASCADE,
        related_name='learning_plans',
        verbose_name=_('学习目标')
    )
    name = models.CharField(_('计划名称'), max_length=100)
    plan_mode = models.CharField(_('计划模式'), max_length=20, choices=PLAN_MODE_CHOICES)
    
    start_date = models.DateField(_('开始日期'), default=date.today)
    end_date = models.DateField(_('结束日期'))
    
    total_words = models.IntegerField(_('总单词数'), default=0)
    daily_target = models.IntegerField(_('每日目标单词数'), default=0)
    
    status = models.CharField(_('状态'), max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('学习计划')
        verbose_name_plural = _('学习计划')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['learning_goal']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user.username}) - {dict(self.PLAN_MODE_CHOICES).get(self.plan_mode, self.plan_mode)}"
    
    def clean(self):
        """验证数据"""
        if self.end_date <= self.start_date:
            raise ValidationError({'end_date': '结束日期必须晚于开始日期'})
    
    def save(self, *args, **kwargs):
        # 从学习目标获取总单词数
        if not self.total_words and self.learning_goal:
            self.total_words = self.learning_goal.remaining_words
        
        # 计算每日目标
        self.calculate_daily_target()
        
        super().save(*args, **kwargs)
    
    def calculate_daily_target(self):
        """计算每日目标单词数"""
        if self.plan_mode == 'mechanical':
            # 机械模式：不考虑学习进展，均分到每天
            total_days = (self.end_date - self.start_date).days + 1
            self.daily_target = max(1, self.total_words // total_days)
        
        elif self.plan_mode == 'daily_progress':
            # 日进模式：考虑学习进展，每天更新
            remaining_words = self.get_remaining_words()
            remaining_days = (self.end_date - date.today()).days + 1
            self.daily_target = max(1, remaining_words // max(1, remaining_days))
        
        elif self.plan_mode == 'workday':
            # 工作日模式：只计算工作日
            remaining_words = self.get_remaining_words()
            remaining_workdays = self.count_workdays(date.today(), self.end_date)
            self.daily_target = max(1, remaining_words // max(1, remaining_workdays))
        
        elif self.plan_mode == 'weekend':
            # 周末模式：只计算周末
            remaining_words = self.get_remaining_words()
            remaining_weekends = self.count_weekends(date.today(), self.end_date)
            self.daily_target = max(1, remaining_words // max(1, remaining_weekends))
    
    def get_remaining_words(self):
        """获取剩余单词数"""
        if self.learning_goal:
            self.learning_goal.update_progress()
            return self.learning_goal.remaining_words
        return self.total_words
    
    def count_workdays(self, start_date, end_date):
        """计算工作日数量（周一到周五）"""
        workdays = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 0-4 表示周一到周五
                workdays += 1
            current_date += timedelta(days=1)
        return workdays
    
    def count_weekends(self, start_date, end_date):
        """计算周末天数（周六和周日）"""
        weekend_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() >= 5:  # 5-6 表示周六和周日
                weekend_days += 1
            current_date += timedelta(days=1)
        return weekend_days
    
    def update_daily_target(self):
        """更新每日目标（用于日进、工作日、周末模式）"""
        if self.plan_mode in ['daily_progress', 'workday', 'weekend']:
            self.calculate_daily_target()
            self.save(update_fields=['daily_target', 'updated_at'])
    
    @property
    def total_days(self):
        """计划总天数"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def elapsed_days(self):
        """已过天数"""
        if date.today() < self.start_date:
            return 0
        return min((date.today() - self.start_date).days + 1, self.total_days)
    
    @property
    def remaining_days(self):
        """剩余天数"""
        if date.today() > self.end_date:
            return 0
        return (self.end_date - date.today()).days + 1
    
    @property
    def progress_percentage(self):
        """计划进度百分比"""
        if self.total_days == 0:
            return 0
        return round((self.elapsed_days / self.total_days) * 100, 2)


class DailyStudyRecord(models.Model):
    """每日学习记录"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_study_records',
        verbose_name=_('用户')
    )
    learning_plan = models.ForeignKey(
        LearningPlan,
        on_delete=models.CASCADE,
        related_name='daily_records',
        verbose_name=_('学习计划')
    )
    study_date = models.DateField(_('学习日期'), default=date.today)
    target_words = models.IntegerField(_('目标单词数'), default=0)
    completed_words = models.IntegerField(_('完成单词数'), default=0)
    study_duration = models.DurationField(_('学习时长'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('每日学习记录')
        verbose_name_plural = _('每日学习记录')
        ordering = ['-study_date']
        unique_together = [['user', 'learning_plan', 'study_date']]
        indexes = [
            models.Index(fields=['user', 'study_date']),
            models.Index(fields=['learning_plan', 'study_date']),
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


class WordLearningProgress(models.Model):
    """单词学习进度模型"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='word_learning_progress',
        verbose_name=_('用户')
    )
    learning_goal = models.ForeignKey(
        LearningGoal,
        on_delete=models.CASCADE,
        related_name='word_progress',
        verbose_name=_('学习目标')
    )
    word = models.ForeignKey(
        'words.Word',
        on_delete=models.CASCADE,
        related_name='learning_progress',
        verbose_name=_('单词')
    )
    
    # 学习次数统计
    review_count = models.IntegerField(_('复习次数'), default=0)
    last_review_date = models.DateTimeField(_('最后复习时间'), null=True, blank=True)
    
    # 学习状态
    is_mastered = models.BooleanField(_('是否已掌握'), default=False)
    is_forgotten = models.BooleanField(_('是否已遗忘'), default=False)
    mastered_date = models.DateTimeField(_('掌握时间'), null=True, blank=True)
    
    # 学习记录
    first_learned_date = models.DateTimeField(_('首次学习时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('单词学习进度')
        verbose_name_plural = _('单词学习进度')
        unique_together = [['user', 'learning_goal', 'word']]
        indexes = [
            models.Index(fields=['user', 'learning_goal']),
            models.Index(fields=['review_count']),
            models.Index(fields=['is_mastered']),
            models.Index(fields=['is_forgotten']),
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
    
    @property
    def status_display(self):
        """获取状态显示文本"""
        status_map = {
            'mastered': '已掌握',
            'forgotten': '已遗忘',
            'review_1': '第1次复习',
            'review_2': '第2次复习',
            'review_3': '第3次复习',
            'review_4': '第4次复习',
            'review_5': '第5次复习',
            'review_6': '第6次复习',
            'not_started': '未开始'
        }
        return status_map.get(self.status, '未知状态')
