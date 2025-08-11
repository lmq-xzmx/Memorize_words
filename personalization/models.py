from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


class UserPreference(models.Model):
    """用户偏好设置"""
    DIFFICULTY_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    ]
    
    LEARNING_STYLE_CHOICES = [
        ('visual', '视觉型'),
        ('auditory', '听觉型'),
        ('kinesthetic', '动觉型'),
        ('reading', '阅读型'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLE_CHOICES, default='visual')
    daily_goal_minutes = models.PositiveIntegerField(default=30, validators=[MinValueValidator(5), MaxValueValidator(480)])
    preferred_topics = models.JSONField(default=list, help_text='用户感兴趣的学习主题')
    weak_areas = models.JSONField(default=list, help_text='用户薄弱环节')
    study_time_preferences = models.JSONField(default=dict, help_text='学习时间偏好')
    notification_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '用户偏好'
        verbose_name_plural = '用户偏好'
    
    def __str__(self):
        return f'{self.user.username}的偏好设置'


class LearningBehavior(models.Model):
    """学习行为记录"""
    ACTION_CHOICES = [
        ('study', '学习'),
        ('practice', '练习'),
        ('review', '复习'),
        ('test', '测试'),
        ('skip', '跳过'),
        ('favorite', '收藏'),
        ('share', '分享'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_behaviors')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.CharField(max_length=50, help_text='内容类型：word, article, exercise等')
    content_id = models.PositiveIntegerField(help_text='内容ID')
    duration_seconds = models.PositiveIntegerField(default=0, help_text='学习时长（秒）')
    score = models.FloatField(null=True, blank=True, help_text='得分或正确率')
    difficulty_level = models.CharField(max_length=20, null=True, blank=True)
    context_data = models.JSONField(default=dict, help_text='上下文数据')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '学习行为'
        verbose_name_plural = '学习行为'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['content_type', 'content_id']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.get_action_display()}'


class RecommendationModel(models.Model):
    """推荐模型配置"""
    MODEL_TYPES = [
        ('collaborative', '协同过滤'),
        ('content_based', '基于内容'),
        ('hybrid', '混合推荐'),
        ('knowledge_based', '基于知识'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict, help_text='模型参数配置')
    is_active = models.BooleanField(default=True)
    weight = models.FloatField(default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '推荐模型'
        verbose_name_plural = '推荐模型'
    
    def __str__(self):
        return self.name


class PersonalizedRecommendation(models.Model):
    """个性化推荐记录"""
    RECOMMENDATION_TYPES = [
        ('word', '单词推荐'),
        ('article', '文章推荐'),
        ('exercise', '练习推荐'),
        ('course', '课程推荐'),
        ('study_plan', '学习计划推荐'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    content_id = models.PositiveIntegerField(help_text='推荐内容ID')
    model = models.ForeignKey(RecommendationModel, on_delete=models.CASCADE)
    score = models.FloatField(help_text='推荐分数')
    reason = models.TextField(blank=True, help_text='推荐理由')
    metadata = models.JSONField(default=dict, help_text='推荐元数据')
    is_clicked = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    feedback_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='用户反馈评分（1-5）'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = '个性化推荐'
        verbose_name_plural = '个性化推荐'
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['user', 'recommendation_type', 'content_id', 'created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_recommendation_type_display()}'
    
    def mark_clicked(self):
        """标记为已点击"""
        if not self.is_clicked:
            self.is_clicked = True
            self.clicked_at = timezone.now()
            self.save(update_fields=['is_clicked', 'clicked_at'])
    
    def mark_completed(self):
        """标记为已完成"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])


class LearningPath(models.Model):
    """学习路径"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '激活'),
        ('completed', '已完成'),
        ('paused', '暂停'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_level = models.CharField(max_length=20, choices=UserPreference.DIFFICULTY_CHOICES)
    estimated_duration_days = models.PositiveIntegerField(help_text='预计完成天数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    progress_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    milestones = models.JSONField(default=list, help_text='学习里程碑')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = '学习路径'
        verbose_name_plural = '学习路径'
    
    def __str__(self):
        return f'{self.user.username} - {self.name}'
    
    def update_progress(self):
        """更新学习进度"""
        # 这里可以根据完成的学习步骤计算进度
        completed_steps = self.steps.filter(is_completed=True).count()
        total_steps = self.steps.count()
        if total_steps > 0:
            self.progress_percentage = (completed_steps / total_steps) * 100
            if self.progress_percentage >= 100 and self.status != 'completed':
                self.status = 'completed'
                self.completed_at = timezone.now()
            self.save(update_fields=['progress_percentage', 'status', 'completed_at'])


class LearningStep(models.Model):
    """学习步骤"""
    STEP_TYPES = [
        ('word_study', '单词学习'),
        ('reading', '阅读练习'),
        ('listening', '听力练习'),
        ('speaking', '口语练习'),
        ('writing', '写作练习'),
        ('grammar', '语法学习'),
        ('test', '测试评估'),
    ]
    
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content_id = models.PositiveIntegerField(help_text='关联内容ID')
    order = models.PositiveIntegerField(help_text='步骤顺序')
    estimated_duration_minutes = models.PositiveIntegerField(help_text='预计完成时间（分钟）')
    is_required = models.BooleanField(default=True, help_text='是否必须完成')
    is_completed = models.BooleanField(default=False)
    completion_score = models.FloatField(null=True, blank=True, help_text='完成得分')
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = '学习步骤'
        verbose_name_plural = '学习步骤'
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'order']
    
    def __str__(self):
        return f'{self.learning_path.name} - {self.title}'
    
    def mark_completed(self, score=None):
        """标记步骤为已完成"""
        self.is_completed = True
        self.completed_at = timezone.now()
        if score is not None:
            self.completion_score = score
        self.save(update_fields=['is_completed', 'completed_at', 'completion_score'])
        
        # 更新学习路径进度
        self.learning_path.update_progress()


class AdaptiveDifficulty(models.Model):
    """自适应难度调整"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='difficulty_adjustments')
    content_type = models.CharField(max_length=50)
    current_difficulty = models.CharField(max_length=20, choices=UserPreference.DIFFICULTY_CHOICES)
    success_rate = models.FloatField(help_text='成功率')
    adjustment_reason = models.TextField(help_text='调整原因')
    previous_difficulty = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '自适应难度'
        verbose_name_plural = '自适应难度'
    
    def __str__(self):
        return f'{self.user.username} - {self.content_type} - {self.current_difficulty}'
