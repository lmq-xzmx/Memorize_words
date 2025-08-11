from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class ContentCategory(models.Model):
    """内容分类模型"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='父分类'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '内容分类'
        verbose_name_plural = '内容分类'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ContentTag(models.Model):
    """内容标签模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='标签颜色')
    description = models.TextField(blank=True, verbose_name='标签描述')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '内容标签'
        verbose_name_plural = '内容标签'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name


class SmartContent(models.Model):
    """智能内容模型"""
    CONTENT_TYPE_CHOICES = [
        ('article', '文章'),
        ('video', '视频'),
        ('audio', '音频'),
        ('exercise', '练习'),
        ('quiz', '测验'),
        ('game', '游戏'),
        ('course', '课程'),
    ]
    
    DIFFICULTY_CHOICES = [
        (1, '初级'),
        (2, '初中级'),
        (3, '中级'),
        (4, '中高级'),
        (5, '高级'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    content_type = models.CharField(
        max_length=20, 
        choices=CONTENT_TYPE_CHOICES, 
        verbose_name='内容类型'
    )
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES, 
        default=1, 
        verbose_name='难度等级'
    )
    category = models.ForeignKey(
        ContentCategory, 
        on_delete=models.CASCADE, 
        verbose_name='分类'
    )
    tags = models.ManyToManyField(ContentTag, blank=True, verbose_name='标签')
    
    # 内容数据
    content_data = models.JSONField(default=dict, verbose_name='内容数据')
    
    # 学习目标和技能
    learning_objectives = models.JSONField(default=list, verbose_name='学习目标')
    skills_covered = models.JSONField(default=list, verbose_name='涵盖技能')
    
    # 时间相关
    estimated_duration = models.IntegerField(
        default=0, 
        help_text='预估学习时长（分钟）',
        verbose_name='预估时长'
    )
    
    # 质量评分
    quality_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name='质量评分'
    )
    
    # 状态管理
    is_published = models.BooleanField(default=False, verbose_name='是否发布')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    
    # 统计数据
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    like_count = models.IntegerField(default=0, verbose_name='点赞次数')
    completion_count = models.IntegerField(default=0, verbose_name='完成次数')
    
    # 创建者和时间
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_contents',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '智能内容'
        verbose_name_plural = '智能内容'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'difficulty_level']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['-quality_score']),
        ]
    
    def __str__(self):
        return self.title


class ContentRecommendation(models.Model):
    """内容推荐模型"""
    RECOMMENDATION_TYPE_CHOICES = [
        ('similar', '相似内容'),
        ('next_level', '进阶内容'),
        ('review', '复习内容'),
        ('trending', '热门内容'),
        ('personalized', '个性化推荐'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    content = models.ForeignKey(SmartContent, on_delete=models.CASCADE, verbose_name='推荐内容')
    recommendation_type = models.CharField(
        max_length=20, 
        choices=RECOMMENDATION_TYPE_CHOICES,
        verbose_name='推荐类型'
    )
    
    # 推荐算法相关
    algorithm_used = models.CharField(max_length=100, verbose_name='使用算法')
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='置信度'
    )
    
    # 推荐原因
    reason = models.TextField(blank=True, verbose_name='推荐原因')
    
    # 用户反馈
    is_clicked = models.BooleanField(default=False, verbose_name='是否点击')
    is_liked = models.BooleanField(null=True, blank=True, verbose_name='是否喜欢')
    feedback_score = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='反馈评分'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    clicked_at = models.DateTimeField(null=True, blank=True, verbose_name='点击时间')
    
    class Meta:
        verbose_name = '内容推荐'
        verbose_name_plural = '内容推荐'
        ordering = ['-created_at']
        unique_together = ['user', 'content', 'recommendation_type']
    
    def __str__(self):
        return f'{self.user.username} - {self.content.title}'


class UserContentInteraction(models.Model):
    """用户内容交互模型"""
    INTERACTION_TYPE_CHOICES = [
        ('view', '浏览'),
        ('like', '点赞'),
        ('bookmark', '收藏'),
        ('share', '分享'),
        ('comment', '评论'),
        ('complete', '完成'),
        ('download', '下载'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    content = models.ForeignKey(SmartContent, on_delete=models.CASCADE, verbose_name='内容')
    interaction_type = models.CharField(
        max_length=20, 
        choices=INTERACTION_TYPE_CHOICES,
        verbose_name='交互类型'
    )
    
    # 交互详情
    duration = models.IntegerField(null=True, blank=True, verbose_name='持续时间（秒）')
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name='进度百分比'
    )
    
    # 设备和环境信息
    device_type = models.CharField(max_length=50, blank=True, verbose_name='设备类型')
    platform = models.CharField(max_length=50, blank=True, verbose_name='平台')
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='交互时间')
    
    class Meta:
        verbose_name = '用户内容交互'
        verbose_name_plural = '用户内容交互'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['content', 'interaction_type']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.interaction_type} - {self.content.title}'


class ContentAnalytics(models.Model):
    """内容分析模型"""
    content = models.OneToOneField(
        SmartContent, 
        on_delete=models.CASCADE, 
        related_name='analytics',
        verbose_name='内容'
    )
    
    # 基础统计
    total_views = models.IntegerField(default=0, verbose_name='总浏览量')
    unique_viewers = models.IntegerField(default=0, verbose_name='独立浏览者')
    total_likes = models.IntegerField(default=0, verbose_name='总点赞数')
    total_shares = models.IntegerField(default=0, verbose_name='总分享数')
    total_completions = models.IntegerField(default=0, verbose_name='总完成数')
    
    # 时间统计
    avg_view_duration = models.FloatField(default=0.0, verbose_name='平均浏览时长')
    avg_completion_time = models.FloatField(default=0.0, verbose_name='平均完成时间')
    
    # 用户反馈
    avg_rating = models.FloatField(default=0.0, verbose_name='平均评分')
    total_ratings = models.IntegerField(default=0, verbose_name='评分总数')
    
    # 转化率
    view_to_completion_rate = models.FloatField(default=0.0, verbose_name='浏览完成转化率')
    like_rate = models.FloatField(default=0.0, verbose_name='点赞率')
    
    # 趋势数据
    weekly_views = models.JSONField(default=list, verbose_name='周浏览量')
    monthly_views = models.JSONField(default=list, verbose_name='月浏览量')
    
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    
    class Meta:
        verbose_name = '内容分析'
        verbose_name_plural = '内容分析'
    
    def __str__(self):
        return f'{self.content.title} - 分析数据'
    
    def update_analytics(self):
        """更新分析数据"""
        interactions = UserContentInteraction.objects.filter(content=self.content)
        
        # 更新基础统计
        self.total_views = interactions.filter(interaction_type='view').count()
        self.unique_viewers = interactions.filter(
            interaction_type='view'
        ).values('user').distinct().count()
        self.total_likes = interactions.filter(interaction_type='like').count()
        self.total_shares = interactions.filter(interaction_type='share').count()
        self.total_completions = interactions.filter(interaction_type='complete').count()
        
        # 计算转化率
        if self.total_views > 0:
            self.view_to_completion_rate = (self.total_completions / self.total_views) * 100
            self.like_rate = (self.total_likes / self.total_views) * 100
        
        self.save()
