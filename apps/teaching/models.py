from django.db import models
from django.contrib.auth import get_user_model
from apps.words.models import Word, WordSet, VocabularyList
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import uuid
import json

User = get_user_model()

class LearningGoal(models.Model):
    """学习目标模型"""
    GOAL_TYPE_CHOICES = [
        ('vocabulary_list', '词库'),
        ('word_set', '词集'),
        ('grade_level', '分级'),
        ('mixed', '混合'),  # 支持多种资源混合
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(max_length=200, verbose_name='目标名称')
    description = models.TextField(blank=True, verbose_name='目标描述')
    
    # 合并vocabulary_manager的字段
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='mixed', verbose_name='目标类型')
    is_current = models.BooleanField(default=False, verbose_name='是否为当前目标')
    total_words = models.IntegerField(default=0, verbose_name='总单词数')
    learned_words = models.IntegerField(default=0, verbose_name='已学单词数')
    
    target_words_count = models.IntegerField(default=100, verbose_name='目标单词数量')
    start_date = models.DateField(default=timezone.now, verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    # 关联单词集和单词库，支持批量添加单词
    word_sets = models.ManyToManyField(WordSet, blank=True, verbose_name='关联单词集', related_name='teaching_goals')
    vocabulary_lists = models.ManyToManyField(VocabularyList, blank=True, verbose_name='关联单词库', related_name='teaching_goals')
    
    # 单一关联字段（来自vocabulary_manager）
    vocabulary_list = models.ForeignKey(
        VocabularyList,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='single_learning_goals',
        verbose_name='单一词库列表'
    )
    word_set = models.ForeignKey(
        WordSet,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='single_learning_goals',
        verbose_name='单一词集'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习目标'
        verbose_name_plural = '学习目标'
        ordering = ['-created_at']
    
    def __str__(self):
        current_mark = "[当前]" if self.is_current else ""
        return f"{current_mark}{self.name} ({self.user.username})"
    
    def clean(self):
        """验证数据"""
        from django.core.exceptions import ValidationError
        # 确保目标类型与关联字段匹配
        if self.goal_type == 'vocabulary_list' and not self.vocabulary_list:
            raise ValidationError({'vocabulary_list': '词库类型必须选择词库列表'})
        elif self.goal_type == 'word_set' and not self.word_set:
            raise ValidationError({'word_set': '词集类型必须选择词集'})
    
    def get_word_count(self):
        """获取目标包含的单词数量（合并两种计算方式）"""
        # 单一关联模式（来自vocabulary_manager）
        if self.goal_type == 'vocabulary_list' and self.vocabulary_list:
            return self.vocabulary_list.words.count()
        elif self.goal_type == 'word_set' and self.word_set:
            return self.word_set.words.count()
        
        # 多对多关联模式（原teaching模式）
        total = 0
        for word_set in self.word_sets.all():
            total += word_set.words.count()
        for vocab_list in self.vocabulary_lists.all():
            total += vocab_list.words.count()
        return total
    
    def get_words(self):
        """获取目标包含的所有单词（合并两种获取方式）"""
        from apps.words.models import Word
        
        # 单一关联模式
        if self.goal_type == 'vocabulary_list' and self.vocabulary_list:
            return self.vocabulary_list.words.all()
        elif self.goal_type == 'word_set' and self.word_set:
            return self.word_set.words.all()
        
        # 多对多关联模式
        word_ids = set()
        for word_set in self.word_sets.all():
            word_ids.update(word_set.words.values_list('id', flat=True))
        for vocab_list in self.vocabulary_lists.all():
            word_ids.update(vocab_list.words.values_list('id', flat=True))
        
        if word_ids:
            return Word.objects.filter(id__in=word_ids)
        return Word.objects.none()
    
    def get_total_words(self):
        """获取目标包含的总单词数（兼容原方法名）"""
        return self.get_word_count()
    
    def get_learned_words_count(self):
        """获取已学习的单词数量"""
        learned_words = set()
        
        # 从词集中获取已学习的单词
        for word_set in self.word_sets.all():
            for word in word_set.words.all():
                if hasattr(word, 'learning_records') and word.learning_records.filter(
                    user=self.user, is_learned=True
                ).exists():
                    learned_words.add(word.id)
        
        # 从词库列表中获取已学习的单词
        for vocab_list in self.vocabulary_lists.all():
            for word in vocab_list.words.all():
                if hasattr(word, 'learning_records') and word.learning_records.filter(
                    user=self.user, is_learned=True
                ).exists():
                    learned_words.add(word.id)
        
        return len(learned_words)
    
    def update_progress(self):
        """更新学习进度（来自vocabulary_manager）"""
        # 统计用户已学习的单词数量
        words = self.get_words()
        learned_count = words.filter(
            learning_records__user=self.user,
            learning_records__is_learned=True
        ).distinct().count()
        
        self.learned_words = learned_count
        self.save(update_fields=['learned_words', 'updated_at'])
        return learned_count
    
    def get_progress_percentage(self):
        """获取学习进度百分比"""
        total = self.get_total_words()
        if total == 0:
            return 0
        learned = self.get_learned_words_count()
        return round((learned / total) * 100, 2)
    
    @property
    def progress_percentage(self):
        """学习进度百分比（来自vocabulary_manager）"""
        if self.total_words == 0:
            return 0
        return round((self.learned_words / self.total_words) * 100, 2)
    
    @property
    def remaining_words(self):
        """剩余单词数（来自vocabulary_manager）"""
        return max(0, self.total_words - self.learned_words)
    
    def sync_words_from_sets_and_lists(self):
        """从关联的单词集和单词库同步单词到目标单词"""
        # 获取所有关联的单词集中的单词
        wordset_words = Word.objects.filter(wordset__in=self.word_sets.all()).distinct()
        
        # 获取所有关联的单词库中的单词
        vocabularylist_words = Word.objects.filter(vocabulary_list__in=self.vocabulary_lists.all()).distinct()
        
        # 合并所有单词
        all_words = wordset_words.union(vocabularylist_words)
        
        # 为每个单词创建GoalWord关联（如果不存在）
        for word in all_words:
            GoalWord.objects.get_or_create(
                goal=self,
                word=word,
                defaults={'added_at': timezone.now()}
            )
    
    def save(self, *args, **kwargs):
        """保存时自动同步关联的单词"""
        # 如果设置为当前目标，取消其他目标的当前状态
        if self.is_current:
            LearningGoal.objects.filter(
                user=self.user, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        
        # 计算总单词数
        if not self.total_words:
            self.total_words = self.get_word_count()
        
        super().save(*args, **kwargs)
        # 如果是更新操作且有关联的单词集或单词库，则同步单词
        if self.pk and (self.word_sets.exists() or self.vocabulary_lists.exists()):
            self.sync_words_from_sets_and_lists()
    
    def get_progress_stats(self):
        """获取九宫格进度统计"""
        # 使用反向查询获取目标单词
        goal_word_ids = GoalWord.objects.filter(goal=self).values_list('word_id', flat=True)
        records = WordLearningRecord.objects.filter(
            goal=self,
            word_id__in=goal_word_ids
        )
        
        # 统计各阶段单词数量
        stats = {
            'review_1': 0,  # 第1次复习
            'review_2': 0,  # 第2次复习
            'review_3': 0,  # 第3次复习
            'review_4': 0,  # 第4次复习
            'review_5': 0,  # 第5次复习
            'review_6': 0,  # 第6次复习
            'mastered': 0,  # 掌握（6次以上）
            'forgotten': 0, # 遗忘
            'pending': 0    # 待学习
        }
        
        # 统计每个单词的学习次数
        word_counts = {}
        for record in records:
            word_id = record.word.id
            if word_id not in word_counts:
                word_counts[word_id] = {'count': 0, 'last_correct': None}
            
            word_counts[word_id]['count'] += 1
            if record.is_correct:
                word_counts[word_id]['last_correct'] = record.created_at
        
        # 分类统计
        learned_words = set()
        
        for word_id, data in word_counts.items():
            learned_words.add(word_id)
            count = data['count']
            last_correct = data['last_correct']
            
            # 判断是否遗忘（超过7天未正确回答）
            if last_correct and (timezone.now() - last_correct).days > 7:
                stats['forgotten'] += 1
            elif count >= 7:
                stats['mastered'] += 1
            elif count == 6:
                stats['review_6'] += 1
            elif count == 5:
                stats['review_5'] += 1
            elif count == 4:
                stats['review_4'] += 1
            elif count == 3:
                stats['review_3'] += 1
            elif count == 2:
                stats['review_2'] += 1
            elif count == 1:
                stats['review_1'] += 1
        
        # 计算待学习数量
        total_goal_words = GoalWord.objects.filter(goal=self).count()
        stats['pending'] = total_goal_words - len(learned_words)
        
        return stats

class GoalWord(models.Model):
    """目标单词关联模型"""
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='goal_words', verbose_name='学习目标')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='goal_associations', verbose_name='单词')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    
    class Meta:
        verbose_name = '目标单词'
        verbose_name_plural = '目标单词'
        unique_together = ['goal', 'word']
    
    def __str__(self):
        return f"{self.goal.name} - {self.word.word}"

class LearningSession(models.Model):
    """学习会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions', verbose_name='用户')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='sessions', verbose_name='学习目标')
    start_time = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    words_studied = models.IntegerField(default=0, verbose_name='学习单词数')
    correct_answers = models.IntegerField(default=0, verbose_name='正确答案数')
    total_answers = models.IntegerField(default=0, verbose_name='总答案数')
    
    # 合并vocabulary_manager的字段
    duration = models.DurationField(verbose_name='学习时长', null=True, blank=True)
    words_learned = models.IntegerField(verbose_name='掌握单词数', default=0)
    
    # 指导模式相关字段
    is_guided = models.BooleanField(default=False, verbose_name='是否为指导模式')
    guided_session = models.ForeignKey(
        'GuidedPracticeSession', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='指导练习会话'
    )
    teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='guided_learning_sessions',
        verbose_name='指导老师'
    )
    
    class Meta:
        verbose_name = '学习会话'
        verbose_name_plural = '学习会话'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def get_duration(self):
        """获取会话持续时间"""
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time
    
    def end_session(self):
        """结束学习会话（合并vocabulary_manager逻辑）"""
        if not self.end_time:
            self.end_time = timezone.now()
            self.duration = self.end_time - self.start_time
            self.save(update_fields=['end_time', 'duration'])
    
    @property
    def is_active(self):
        """是否为活跃会话（来自vocabulary_manager）"""
        return self.end_time is None
    
    @property
    def learning_efficiency(self):
        """学习效率（掌握率）（来自vocabulary_manager）"""
        if self.words_studied == 0:
            return 0
        return round((self.words_learned / self.words_studied) * 100, 2)
    
    @property
    def accuracy_rate(self):
        """正确率"""
        if self.total_answers == 0:
            return 0
        return round((self.correct_answers / self.total_answers) * 100, 2)
    
    @property
    def duration_minutes(self):
        """学习时长（分钟）"""
        if not self.end_time:
            return 0
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 60, 2)

class WordLearningRecord(models.Model):
    """单词学习记录模型"""
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='records', verbose_name='学习会话')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='learning_records', verbose_name='学习目标')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='learning_records', verbose_name='单词')
    user_answer = models.CharField(max_length=200, verbose_name='用户答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    response_time = models.FloatField(verbose_name='响应时间（秒）')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # 指导模式相关字段
    is_guided = models.BooleanField(default=False, verbose_name='是否为指导模式')
    guided_question = models.ForeignKey(
        'GuidedPracticeQuestion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='指导练习题目'
    )
    
    class Meta:
        verbose_name = '单词学习记录'
        verbose_name_plural = '单词学习记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.word.word} - {'正确' if self.is_correct else '错误'}"

class UserStreak(models.Model):
    """用户连续学习记录（来自vocabulary_manager）"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teaching_streak', verbose_name='用户')
    current_streak = models.IntegerField(default=0, verbose_name='当前连续天数')
    longest_streak = models.IntegerField(default=0, verbose_name='最长连续天数')
    last_study_date = models.DateField(null=True, blank=True, verbose_name='最后学习日期')
    
    class Meta:
        verbose_name = '用户连续学习记录'
        verbose_name_plural = '用户连续学习记录'
    
    def __str__(self):
        return f"{self.user.username} - 连续{self.current_streak}天"
    
    def update_streak(self, study_date=None):
        """更新连续学习记录"""
        if study_date is None:
            study_date = timezone.now().date()
        
        if self.last_study_date is None:
            # 首次学习
            self.current_streak = 1
            self.longest_streak = 1
        elif study_date == self.last_study_date:
            # 同一天，不更新
            return
        elif study_date == self.last_study_date + timedelta(days=1):
            # 连续学习
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            # 中断了连续学习
            self.current_streak = 1
        
        self.last_study_date = study_date
        self.save()

class DailyStudyRecord(models.Model):
    """每日学习记录（来自vocabulary_manager）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_daily_records', verbose_name='用户')
    date = models.DateField(verbose_name='日期')
    words_studied = models.IntegerField(default=0, verbose_name='学习单词数')
    words_learned = models.IntegerField(default=0, verbose_name='掌握单词数')
    study_time = models.DurationField(default=timedelta(0), verbose_name='学习时长')
    sessions_count = models.IntegerField(default=0, verbose_name='学习会话数')
    
    class Meta:
        verbose_name = '每日学习记录'
        verbose_name_plural = '每日学习记录'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    @property
    def learning_efficiency(self):
        """学习效率（掌握率）"""
        if self.words_studied == 0:
            return 0
        return round((self.words_learned / self.words_studied) * 100, 2)

class WordLearningProgress(models.Model):
    """单词学习进度（来自vocabulary_manager）"""
    MASTERY_LEVEL_CHOICES = [
        ('new', '新单词'),
        ('learning', '学习中'),
        ('reviewing', '复习中'),
        ('mastered', '已掌握'),
        ('forgotten', '已遗忘'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_word_progress', verbose_name='用户')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='user_progress', verbose_name='单词')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='word_progress', verbose_name='学习目标')
    
    mastery_level = models.CharField(max_length=20, choices=MASTERY_LEVEL_CHOICES, default='new', verbose_name='掌握程度')
    correct_count = models.IntegerField(default=0, verbose_name='正确次数')
    total_attempts = models.IntegerField(default=0, verbose_name='总尝试次数')
    
    first_learned_at = models.DateTimeField(null=True, blank=True, verbose_name='首次学习时间')
    last_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='最后复习时间')
    next_review_at = models.DateTimeField(null=True, blank=True, verbose_name='下次复习时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '单词学习进度'
        verbose_name_plural = '单词学习进度'
        unique_together = ['user', 'word', 'goal']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.word.word} - {self.get_mastery_level_display()}"
    
    @property
    def accuracy_rate(self):
        """正确率"""
        if self.total_attempts == 0:
            return 0
        return round((self.correct_count / self.total_attempts) * 100, 2)
    
    def update_progress(self, is_correct):
        """更新学习进度"""
        self.total_attempts += 1
        if is_correct:
            self.correct_count += 1
        
        # 更新掌握程度
        if self.mastery_level == 'new':
            self.mastery_level = 'learning'
            self.first_learned_at = timezone.now()
        
        # 根据正确率调整掌握程度
        if self.accuracy_rate >= 80 and self.total_attempts >= 3:
            if self.mastery_level in ['learning', 'reviewing']:
                self.mastery_level = 'mastered'
        elif self.accuracy_rate < 50 and self.total_attempts >= 3:
            if self.mastery_level == 'mastered':
                self.mastery_level = 'forgotten'
        
        self.last_reviewed_at = timezone.now()
        # 计算下次复习时间（简单的间隔重复算法）
        if self.mastery_level == 'mastered':
            self.next_review_at = timezone.now() + timedelta(days=7)
        else:
            self.next_review_at = timezone.now() + timedelta(days=1)
        
        self.save()

class LearningPlan(models.Model):
    """学习计划模型（增强版来自vocabulary_manager）"""
    PLAN_TYPE_CHOICES = [
        ('daily', '每日计划'),
        ('weekly', '每周计划'),
        ('monthly', '每月计划'),
        ('custom', '自定义计划'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_learning_plans', verbose_name='用户')
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='plans', verbose_name='学习目标')
    
    name = models.CharField(max_length=200, verbose_name='计划名称')
    description = models.TextField(blank=True, verbose_name='计划描述')
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='daily', verbose_name='计划类型')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='难度等级')
    
    # 学习设置
    words_per_day = models.IntegerField(default=10, verbose_name='每日单词数')
    review_interval = models.IntegerField(default=1, verbose_name='复习间隔（天）')
    daily_study_time = models.DurationField(default=timedelta(minutes=30), verbose_name='每日学习时长')
    
    # 计划状态
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    start_date = models.DateField(default=timezone.now, verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')
    
    # 进度跟踪
    total_days = models.IntegerField(default=0, verbose_name='总天数')
    completed_days = models.IntegerField(default=0, verbose_name='已完成天数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习计划'
        verbose_name_plural = '学习计划'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @property
    def completion_rate(self):
        """完成率"""
        if self.total_days == 0:
            return 0
        return round((self.completed_days / self.total_days) * 100, 2)
    
    @property
    def is_completed(self):
        """是否已完成"""
        return self.end_date and timezone.now().date() > self.end_date
    
    def get_today_target(self):
        """获取今日学习目标"""
        return {
            'words_count': self.words_per_day,
            'study_time': self.daily_study_time,
        }
    
    def mark_day_completed(self, date=None):
        """标记某天完成"""
        if date is None:
            date = timezone.now().date()
        
        # 检查是否已经标记过
        if not hasattr(self, '_completed_dates'):
            self._completed_dates = set()
        
        if date not in self._completed_dates:
            self.completed_days += 1
            self._completed_dates.add(date)
            self.save(update_fields=['completed_days', 'updated_at'])

class GuidedPracticeSession(models.Model):
    """老师指导练习会话模型"""
    SESSION_STATUS_CHOICES = [
        ('waiting', '等待中'),
        ('active', '进行中'),
        ('paused', '暂停'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    PRACTICE_MODE_CHOICES = [
        ('multiple_choice', '选择题'),
        ('fill_blank', '填空题'),
        ('translation', '翻译题'),
        ('mixed', '混合模式'),
    ]
    
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guided_sessions', verbose_name='指导老师')
    students = models.ManyToManyField(User, related_name='participated_sessions', verbose_name='参与学生')
    learning_goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, verbose_name='学习目标')
    session_name = models.CharField(max_length=200, verbose_name='会话名称')
    practice_mode = models.CharField(max_length=20, choices=PRACTICE_MODE_CHOICES, default='multiple_choice', verbose_name='练习模式')
    
    # 会话状态
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='waiting', verbose_name='会话状态')
    current_question_index = models.IntegerField(default=0, verbose_name='当前题目索引')
    total_questions = models.IntegerField(default=0, verbose_name='总题目数')
    
    # 时间记录
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # WebSocket房间标识
    room_name = models.CharField(max_length=100, unique=True, verbose_name='房间名称')
    
    class Meta:
        verbose_name = '指导练习会话'
        verbose_name_plural = '指导练习会话'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.teacher.username} - {self.session_name}"
    
    def save(self, *args, **kwargs):
        if not self.room_name:
            self.room_name = f"guided_practice_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    def get_current_question(self):
        """获取当前题目"""
        try:
            return self.questions.filter(question_order=self.current_question_index).first()
        except:
            return None
    
    def next_question(self):
        """切换到下一题"""
        if self.current_question_index < self.total_questions - 1:
            self.current_question_index += 1
            self.save()
            return True
        return False
    
    def get_progress_percentage(self):
        """获取进度百分比"""
        if self.total_questions == 0:
            return 0
        return round((self.current_question_index / self.total_questions) * 100, 2)

class GuidedPracticeQuestion(models.Model):
    """指导练习题目模型"""
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', '选择题'),
        ('fill_blank', '填空题'),
        ('translation', '翻译题'),
    ]
    
    session = models.ForeignKey(GuidedPracticeSession, on_delete=models.CASCADE, related_name='questions', verbose_name='练习会话')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    question_order = models.IntegerField(verbose_name='题目顺序')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice', verbose_name='题目类型')
    
    # 题目内容
    options = models.JSONField(default=list, verbose_name='选项列表')  # 选项列表
    correct_answer = models.IntegerField(verbose_name='正确答案索引')  # 正确答案索引
    time_limit = models.IntegerField(default=30, verbose_name='答题时限(秒)')  # 答题时限(秒)
    
    # 状态跟踪
    is_active = models.BooleanField(default=False, verbose_name='是否激活')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    
    class Meta:
        verbose_name = '指导练习题目'
        verbose_name_plural = '指导练习题目'
        unique_together = ['session', 'question_order']
        ordering = ['question_order']
    
    def __str__(self):
        return f"{self.session.session_name} - 第{self.question_order + 1}题 - {self.word.word}"
    
    def activate(self):
        """激活题目"""
        # 先将会话中的其他题目设为非激活状态
        GuidedPracticeQuestion.objects.filter(session=self.session).update(is_active=False)
        # 激活当前题目
        self.is_active = True
        self.started_at = timezone.now()
        self.save()
    
    def deactivate(self):
        """停用题目"""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()
    
    def get_student_answers(self):
        """获取学生答案统计"""
        answers = self.answers.all()
        total_students = self.session.students.count()
        answered_count = answers.count()
        correct_count = answers.filter(is_correct=True).count()
        
        return {
            'total_students': total_students,
            'answered_count': answered_count,
            'correct_count': correct_count,
            'accuracy_rate': round((correct_count / answered_count) * 100, 2) if answered_count > 0 else 0,
            'completion_rate': round((answered_count / total_students) * 100, 2) if total_students > 0 else 0
        }

class GuidedPracticeAnswer(models.Model):
    """学生在指导练习中的答案记录"""
    question = models.ForeignKey(GuidedPracticeQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name='题目')
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='学生')
    selected_answer = models.IntegerField(verbose_name='选择的答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    response_time = models.FloatField(verbose_name='响应时间(秒)')  # 响应时间(秒)
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='答题时间')
    
    class Meta:
        verbose_name = '指导练习答案'
        verbose_name_plural = '指导练习答案'
        unique_together = ['question', 'student']
        ordering = ['-answered_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.question.word.word} - {'正确' if self.is_correct else '错误'}"

# VocabularyList 和 VocabularyWord 模型已移除
# 这些功能现在通过 LearningGoal 和 GoalWord 模型实现

@receiver(m2m_changed, sender=LearningGoal.word_sets.through)
@receiver(m2m_changed, sender=LearningGoal.vocabulary_lists.through)
def sync_goal_words_on_m2m_change(sender, instance, action, pk_set, **kwargs):
    """当WordSet或VocabularyList关联发生变化时，自动同步目标单词"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        instance.sync_words_from_sets_and_lists()