import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from apps.words.models import Word

User = get_user_model()

class LearningGoal(models.Model):
    """学习目标模型 - 整合了vocabulary_manager的功能"""
    GOAL_TYPE_CHOICES = [
        ('vocabulary_list', '词库'),
        ('word_set', '词集'),
        ('grade_level', '分级'),
        ('vocabulary', '词汇学习'),
        ('reading', '阅读理解'),
        ('listening', '听力训练'),
        ('speaking', '口语练习'),
        ('writing', '写作训练'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teaching_learning_goals',
        verbose_name='用户'
    )
    name = models.CharField(max_length=200, verbose_name='目标名称')
    description = models.TextField(blank=True, verbose_name='目标描述')
    goal_type = models.CharField(
        max_length=20, 
        choices=GOAL_TYPE_CHOICES, 
        default='vocabulary', 
        verbose_name='目标类型'
    )
    is_current = models.BooleanField(default=False, verbose_name='是否为当前目标')
    total_words = models.IntegerField(default=0, verbose_name='总单词数')
    learned_words = models.IntegerField(default=0, verbose_name='已学单词数')
    target_words_count = models.IntegerField(default=100, verbose_name='目标单词数量')
    start_date = models.DateField(default=timezone.now, verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 关联字段 - 整合vocabulary_manager的字段
    vocabulary_list = models.ForeignKey(
        'words.VocabularyList',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teaching_learning_goals',
        verbose_name='词库列表'
    )
    word_set = models.ForeignKey(
        'words.WordSet',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teaching_learning_goals',
        verbose_name='词集'
    )
    grade_level = models.ForeignKey(
        'words.WordGradeLevel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='分级等级'
    )
    
    # 多对多关系字段 - 保留原有功能
    vocabulary_lists = models.ManyToManyField(
        'words.VocabularyList',
        blank=True,
        related_name='teaching_multi_goals',
        verbose_name='词汇表',
        help_text='选择要学习的词汇表'
    )
    word_sets = models.ManyToManyField(
        'words.WordSet',
        blank=True,
        related_name='teaching_multi_goals',
        verbose_name='单词集',
        help_text='选择要学习的单词集'
    )
    
    class Meta:
        verbose_name = '学习目标'
        verbose_name_plural = '学习目标'
        ordering = ['-is_current', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_current']),
            models.Index(fields=['goal_type']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.name}'
    
    @property
    def progress_percentage(self):
        """学习进度百分比"""
        if self.total_words == 0:
            return 0
        return round((self.learned_words / self.total_words) * 100, 2)
    
    def get_progress_stats(self):
        """获取学习进度统计"""
        # 通过反向关系获取目标单词
        goal_words = GoalWord.objects.filter(goal=self)
        total_words = goal_words.count()
        if total_words == 0:
            return {
                'total_words': 0,
                'learned_words': 0,
                'progress_percentage': 0,
                'remaining_words': 0
            }
        
        # 计算已学习的单词数（有学习记录且正确率>70%的单词）
        learned_words = 0
        for goal_word in goal_words:
            records = WordLearningRecord.objects.filter(
                goal=self,
                word=goal_word.word
            )
            if records.exists():
                correct_count = records.filter(is_correct=True).count()
                total_count = records.count()
                if total_count > 0 and (correct_count / total_count) >= 0.7:
                    learned_words += 1
        
        progress_percentage = (learned_words / total_words) * 100 if total_words > 0 else 0
        
        return {
            'total_words': total_words,
            'learned_words': learned_words,
            'progress_percentage': round(progress_percentage, 1),
            'remaining_words': total_words - learned_words
        }

class GoalWord(models.Model):
    """学习目标单词关联模型"""
    goal = models.ForeignKey(
        LearningGoal, 
        on_delete=models.CASCADE, 
        related_name='goal_words',
        verbose_name='学习目标'
    )
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    
    class Meta:
        verbose_name = '目标单词'
        verbose_name_plural = '目标单词'
        unique_together = ('goal', 'word')
    
    def __str__(self):
        return f'{self.goal.name} - {self.word.word}'

class LearningSession(models.Model):
    """学习会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, verbose_name='学习目标')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    words_studied = models.IntegerField(default=0, verbose_name='学习单词数')
    correct_answers = models.IntegerField(default=0, verbose_name='正确答案数')
    total_answers = models.IntegerField(default=0, verbose_name='总答案数')
    
    class Meta:
        verbose_name = '学习会话'
        verbose_name_plural = '学习会话'
        ordering = ['-start_time']
    
    def __str__(self):
        return f'{self.user.username} - {self.goal.name} - {self.start_time.strftime("%Y-%m-%d %H:%M")}'
    
    @property
    def accuracy_rate(self):
        """正确率"""
        if self.total_answers == 0:
            return 0
        return round((self.correct_answers / self.total_answers) * 100, 1)
    
    @property
    def duration(self):
        """学习时长（分钟）"""
        if not self.end_time:
            return 0
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 60, 1)

class WordLearningRecord(models.Model):
    """单词学习记录模型"""
    session = models.ForeignKey(
        LearningSession, 
        on_delete=models.CASCADE, 
        related_name='records',
        verbose_name='学习会话'
    )
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, verbose_name='学习目标')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    user_answer = models.CharField(max_length=200, verbose_name='用户答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    response_time = models.FloatField(verbose_name='响应时间（秒）')
    is_forgotten = models.BooleanField(default=False, verbose_name='是否遗忘')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '单词学习记录'
        verbose_name_plural = '单词学习记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.word.word} - {"正确" if self.is_correct else "错误"}'

class LearningPlan(models.Model):
    """学习计划模型 - 整合了vocabulary_manager的功能"""
    PLAN_TYPE_CHOICES = [
        ('mechanical', '机械模式'),
        ('daily_progress', '日进模式'),
        ('weekday', '工作日模式'),
        ('weekend', '周末模式'),
        ('daily', '每日计划'),
        ('weekly', '每周计划'),
        ('custom', '自定义计划'),
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
        related_name='teaching_learning_plans',
        verbose_name='用户'
    )
    goal = models.ForeignKey(
        LearningGoal, 
        on_delete=models.CASCADE, 
        related_name='plans',
        verbose_name='学习目标'
    )
    name = models.CharField(max_length=100, verbose_name='计划名称')
    plan_type = models.CharField(
        max_length=20, 
        choices=PLAN_TYPE_CHOICES, 
        default='daily',
        verbose_name='计划类型'
    )
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    total_words = models.IntegerField(default=0, verbose_name='总单词数')
    daily_target = models.IntegerField(default=0, verbose_name='每日目标单词数')
    words_per_day = models.IntegerField(default=10, verbose_name='每日单词数')
    review_interval = models.IntegerField(default=1, verbose_name='复习间隔（天）')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习计划'
        verbose_name_plural = '学习计划'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['goal']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.name}'
    
    @property
    def duration_days(self):
        """计划持续天数"""
        return (self.end_date - self.start_date).days + 1
    
    def get_plan_type_display(self):
        """获取计划类型显示名称"""
        return dict(self.PLAN_TYPE_CHOICES).get(self.plan_type, self.plan_type)
    
    def calculate_daily_words(self):
        """根据计划类型计算每日单词数 - 整合vocabulary_manager逻辑"""
        if self.plan_type == 'mechanical':
            # 机械模式：固定每日学习量
            return self.daily_target or self.words_per_day
        
        elif self.plan_type == 'daily_progress':
            # 日进模式：根据剩余时间和剩余单词数计算
            remaining_days = (self.end_date - datetime.date.today()).days + 1
            if remaining_days <= 0:
                return 0
            remaining_words = self.total_words - self.goal.learned_words
            return max(1, remaining_words // remaining_days)
        
        elif self.plan_type == 'weekday':
            # 工作日模式：只在工作日学习
            remaining_workdays = self._count_workdays(datetime.date.today(), self.end_date)
            if remaining_workdays <= 0:
                return 0
            remaining_words = self.total_words - self.goal.learned_words
            return max(1, remaining_words // remaining_workdays)
        
        elif self.plan_type == 'weekend':
            # 周末模式：只在周末学习
            remaining_weekends = self._count_weekends(datetime.date.today(), self.end_date)
            if remaining_weekends <= 0:
                return 0
            remaining_words = self.total_words - self.goal.learned_words
            return max(1, remaining_words // remaining_weekends)
        
        elif self.plan_type == 'daily':
            # 每日计划：标准每日学习
            return self.words_per_day
        
        elif self.plan_type == 'weekly':
            # 每周计划：按周分配
            return self.words_per_day * 7  # 一周的总量
        
        elif self.plan_type == 'custom':
            # 自定义计划：使用设定值
            return self.words_per_day
        
        return self.daily_target or self.words_per_day
    
    def _count_workdays(self, start_date, end_date):
        """计算工作日天数（周一至周五）"""
        workdays = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 0-4 表示周一至周五
                workdays += 1
            current_date += datetime.timedelta(days=1)
        return workdays
    
    def _count_weekends(self, start_date, end_date):
        """计算周末天数（周六和周日）"""
        weekend_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() >= 5:  # 5-6 表示周六和周日
                weekend_days += 1
            current_date += datetime.timedelta(days=1)
        return weekend_days
    
    def is_study_day_for_plan(self, date=None):
        """判断指定日期是否为该计划的学习日"""
        if date is None:
            date = datetime.date.today()
        
        if self.plan_type in ['mechanical', 'daily_progress', 'daily', 'custom']:
            # 这些模式每天都学习
            return True
        elif self.plan_type == 'weekday':
            # 工作日模式：只在工作日学习
            return date.weekday() < 5  # 0-4 表示周一至周五
        elif self.plan_type == 'weekend':
            # 周末模式：只在周末学习
            return date.weekday() >= 5  # 5-6 表示周六和周日
        elif self.plan_type == 'weekly':
            # 每周计划：可以灵活安排，默认每天都可以
            return True
        
        return True
    
    def is_study_day(self, date=None):
        """判断指定日期是否为学习日 - 兼容vocabulary_manager"""
        return self.is_study_day_for_plan(date)
    
    def get_today_words_target(self):
        """获取今日单词学习目标"""
        if not self.is_study_day_for_plan():
            return 0
        return self.calculate_daily_words()
    
    def get_today_target(self):
        """获取今日学习目标 - 兼容vocabulary_manager"""
        return self.get_today_words_target()
    
    def update_words_per_day(self):
        """更新每日单词数（用于动态调整的模式）"""
        if self.plan_type in ['daily_progress', 'weekday', 'weekend']:
            new_words_per_day = self.calculate_daily_words()
            if new_words_per_day != self.words_per_day:
                self.words_per_day = new_words_per_day
                self.save(update_fields=['words_per_day'])
    
    def update_daily_target(self):
        """更新每日目标（用于动态调整的模式） - 兼容vocabulary_manager"""
        if self.plan_type in ['daily_progress', 'weekday', 'weekend']:
            new_target = self.calculate_daily_words()
            if new_target != self.daily_target:
                self.daily_target = new_target
                self.save(update_fields=['daily_target'])
    
    def get_plan_type_display_with_description(self):
        """获取计划类型的详细描述"""
        descriptions = {
            'mechanical': '机械模式 - 固定每日学习量，严格执行',
            'daily_progress': '日进模式 - 智能调整每日学习量',
            'weekday': '工作日模式 - 仅工作日学习',
            'weekend': '周末模式 - 仅周末学习',
            'daily': '每日计划 - 标准每日学习',
            'weekly': '每周计划 - 按周安排学习',
            'custom': '自定义计划 - 完全个性化设置'
        }
        return descriptions.get(self.plan_type, self.plan_type)


class DailyStudyRecord(models.Model):
    """每日学习记录模型 - 从vocabulary_manager迁移"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teaching_daily_study_records',
        verbose_name='用户'
    )
    learning_plan = models.ForeignKey(
        LearningPlan,
        on_delete=models.CASCADE,
        related_name='daily_records',
        verbose_name='学习计划'
    )
    study_date = models.DateField(null=True, blank=True, verbose_name='学习日期')
    target_words = models.IntegerField(default=0, verbose_name='目标单词数')
    completed_words = models.IntegerField(default=0, verbose_name='完成单词数')
    study_duration = models.DurationField(null=True, blank=True, verbose_name='学习时长')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '每日学习记录'
        verbose_name_plural = '每日学习记录'
        ordering = ['-study_date']
        unique_together = [['user', 'learning_plan', 'study_date']]
        indexes = [
            models.Index(fields=['user', 'study_date']),
            models.Index(fields=['learning_plan', 'study_date']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.study_date}'
    
    @property
    def completion_rate(self):
        """完成率"""
        if self.target_words == 0:
            return 0
        return round((self.completed_words / self.target_words) * 100, 2)


# VocabularyList和VocabularyWord已在words应用中定义，此处不再重复定义

class GuidedPracticeSession(models.Model):
    """引导练习会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, verbose_name='学习目标')
    session_type = models.CharField(max_length=50, default='guided_practice', verbose_name='会话类型')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    total_questions = models.IntegerField(default=0, verbose_name='总题数')
    correct_answers = models.IntegerField(default=0, verbose_name='正确答案数')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    
    class Meta:
        verbose_name = '引导练习会话'
        verbose_name_plural = '引导练习会话'
        ordering = ['-start_time']
    
    def __str__(self):
        return f'{self.user.username} - {self.goal.name} - {self.start_time.strftime("%Y-%m-%d %H:%M")}'

class GuidedPracticeQuestion(models.Model):
    """引导练习问题模型"""
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', '选择题'),
        ('fill_blank', '填空题'),
        ('translation', '翻译题'),
        ('pronunciation', '发音题'),
    ]
    
    session = models.ForeignKey(
        GuidedPracticeSession, 
        on_delete=models.CASCADE, 
        related_name='questions',
        verbose_name='练习会话'
    )
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    question_type = models.CharField(
        max_length=20, 
        choices=QUESTION_TYPE_CHOICES, 
        default='multiple_choice',
        verbose_name='问题类型'
    )
    question_text = models.TextField(verbose_name='问题内容')
    correct_answer = models.CharField(max_length=200, verbose_name='正确答案')
    options = models.JSONField(default=list, blank=True, verbose_name='选项')
    order = models.IntegerField(default=0, verbose_name='顺序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '引导练习问题'
        verbose_name_plural = '引导练习问题'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f'{self.word.word} - {self.question_type}'

class GuidedPracticeAnswer(models.Model):
    """引导练习答案模型"""
    question = models.ForeignKey(
        GuidedPracticeQuestion, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name='问题'
    )
    user_answer = models.CharField(max_length=200, verbose_name='用户答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    response_time = models.FloatField(verbose_name='响应时间（秒）')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '引导练习答案'
        verbose_name_plural = '引导练习答案'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.question.word.word} - {"正确" if self.is_correct else "错误"}'