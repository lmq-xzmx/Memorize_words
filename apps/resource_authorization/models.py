from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import json
from datetime import timedelta

User = get_user_model()


class ResourceAuthorization(models.Model):
    """资源授权模型 - 管理资源的访问控制"""
    ACCESS_LEVEL_CHOICES = [
        ('FREE', '免费'),
        ('PREMIUM', '高级'),
        ('USER_GENERATED', '用户生成'),
        ('SHARED', '分享内容'),
    ]
    
    RESOURCE_TYPE_CHOICES = [
        ('word', '单词'),
        ('word_set', '单词集'),
        ('vocabulary_list', '词库列表'),
        ('word_resource', '单词资源'),
    ]
    
    # 资源标识
    resource_type = models.CharField(
        '资源类型', 
        max_length=20, 
        choices=RESOURCE_TYPE_CHOICES
    )
    resource_id = models.PositiveIntegerField('资源ID')
    
    # 访问控制
    access_level = models.CharField(
        '访问级别', 
        max_length=20, 
        choices=ACCESS_LEVEL_CHOICES,
        default='FREE'
    )
    
    # 创建者和所有者
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_authorizations',
        verbose_name='创建者',
        null=True,
        blank=True
    )
    
    # 权限设置
    is_active = models.BooleanField('是否激活', default=True)
    is_public = models.BooleanField('是否公开', default=False)
    requires_subscription = models.BooleanField('需要订阅', default=False)
    
    # 时间控制
    valid_from = models.DateTimeField('生效时间', default=timezone.now)
    valid_until = models.DateTimeField('失效时间', null=True, blank=True)
    
    # 元数据
    metadata = models.JSONField('元数据', default=dict, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资源授权'
        verbose_name_plural = '资源授权'
        unique_together = [['resource_type', 'resource_id']]
        indexes = [
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['access_level']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]
    
    def __str__(self):
        return f"{self.get_resource_type_display()} #{self.resource_id} - {self.get_access_level_display()}"
    
    def clean(self):
        """验证数据"""
        if self.valid_until and self.valid_until <= self.valid_from:
            raise ValidationError({'valid_until': '失效时间必须晚于生效时间'})
    
    def is_valid(self):
        """检查授权是否有效"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return True
    
    def get_resource_object(self):
        """获取关联的资源对象"""
        try:
            if self.resource_type == 'word':
                from apps.words.models import Word
                return Word.objects.get(pk=self.resource_id)
            elif self.resource_type == 'word_set':
                from apps.words.models import WordSet
                return WordSet.objects.get(pk=self.resource_id)
            elif self.resource_type == 'vocabulary_list':
                from apps.words.models import VocabularyList
                return VocabularyList.objects.get(pk=self.resource_id)
            elif self.resource_type == 'word_resource':
                from apps.words.models import WordResource
                return WordResource.objects.get(pk=self.resource_id)
        except Exception:
            return None
        return None


class ResourceShare(models.Model):
    """资源分享模型 - 管理内容分享关系"""
    SHARE_TYPE_CHOICES = [
        ('teacher_to_student', '教师分享给学生'),
        ('user_to_group', '用户分享给群组'),
        ('public_share', '公开分享'),
    ]
    
    # 分享关系
    authorization = models.ForeignKey(
        ResourceAuthorization,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name='资源授权'
    )
    
    share_type = models.CharField(
        '分享类型',
        max_length=20,
        choices=SHARE_TYPE_CHOICES
    )
    
    # 分享者和接收者
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_resources',
        verbose_name='分享者'
    )
    
    shared_with = models.ManyToManyField(
        User,
        related_name='received_shares',
        verbose_name='分享对象',
        blank=True
    )
    
    # 分享设置
    is_active = models.BooleanField('是否激活', default=True)
    allow_reshare = models.BooleanField('允许再分享', default=False)
    
    # 时间控制
    shared_at = models.DateTimeField('分享时间', auto_now_add=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    
    # 分享消息
    share_message = models.TextField('分享消息', blank=True)
    
    # 元数据
    metadata = models.JSONField('分享元数据', default=dict, blank=True)
    
    class Meta:
        verbose_name = '资源分享'
        verbose_name_plural = '资源分享'
        indexes = [
            models.Index(fields=['shared_by']),
            models.Index(fields=['share_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['shared_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.shared_by.username} 分享 {self.authorization} ({self.get_share_type_display()})"
    
    def is_valid(self):
        """检查分享是否有效"""
        if not self.is_active:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        return self.authorization.is_valid()
    
    def can_access(self, user):
        """检查用户是否可以访问分享的资源"""
        if not self.is_valid():
            return False
        
        if self.shared_by == user:
            return True
        
        if self.share_type == 'public_share':
            return True
        
        return self.shared_with.filter(pk=user.pk).exists()


class ResourceCategory(models.Model):
    """资源分类模型 - 支持分层组织"""
    name = models.CharField('分类名称', max_length=100)
    description = models.TextField('分类描述', blank=True)
    
    # 分层结构
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父分类',
        null=True,
        blank=True
    )
    
    # 创建者
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_categories',
        verbose_name='创建者'
    )
    
    # 分类设置
    is_public = models.BooleanField('是否公开', default=False)
    sort_order = models.IntegerField('排序', default=0)
    
    # 关联资源
    authorizations = models.ManyToManyField(
        ResourceAuthorization,
        related_name='categories',
        verbose_name='关联授权',
        blank=True
    )
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资源分类'
        verbose_name_plural = '资源分类'
        ordering = ['sort_order', 'name']
        unique_together = [['name', 'parent', 'created_by']]
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_public']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """获取完整路径"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)
    
    def get_descendants(self):
        """获取所有子分类"""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_resource_count(self):
        """获取分类下的资源数量（包括子分类）"""
        count = self.authorizations.count()
        for child in self.children.all():
            count += child.get_resource_count()
        return count


class ResourceUsageAnalytics(models.Model):
    """资源使用分析模型 - 跟踪和分析"""
    ACTION_CHOICES = [
        ('view', '查看'),
        ('select', '选择'),
        ('download', '下载'),
        ('share', '分享'),
        ('favorite', '收藏'),
        ('unfavorite', '取消收藏'),
    ]
    
    # 关联资源
    authorization = models.ForeignKey(
        ResourceAuthorization,
        on_delete=models.CASCADE,
        related_name='usage_analytics',
        verbose_name='资源授权'
    )
    
    # 用户和操作
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resource_usage',
        verbose_name='用户'
    )
    
    action = models.CharField(
        '操作类型',
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    # 时间和会话
    timestamp = models.DateTimeField('操作时间', auto_now_add=True)
    session_id = models.CharField('会话ID', max_length=100, blank=True)
    
    # 上下文信息
    platform = models.CharField('平台', max_length=20, blank=True)  # mobile, web
    user_agent = models.TextField('用户代理', blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    
    # 元数据
    metadata = models.JSONField('操作元数据', default=dict, blank=True)
    
    class Meta:
        verbose_name = '资源使用分析'
        verbose_name_plural = '资源使用分析'
        indexes = [
            models.Index(fields=['authorization']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['platform']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['authorization', 'action']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.authorization} at {self.timestamp}"


class UserSubscription(models.Model):
    """用户订阅模型 - 管理用户订阅状态"""
    SUBSCRIPTION_TYPE_CHOICES = [
        ('free', '免费'),
        ('basic', '基础版'),
        ('premium', '高级版'),
        ('pro', '专业版'),
    ]
    
    STATUS_CHOICES = [
        ('active', '激活'),
        ('expired', '过期'),
        ('cancelled', '已取消'),
        ('suspended', '暂停'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='用户'
    )
    
    subscription_type = models.CharField(
        '订阅类型',
        max_length=20,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default='free'
    )
    
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # 时间管理
    start_date = models.DateTimeField('开始时间', default=timezone.now)
    end_date = models.DateTimeField('结束时间', null=True, blank=True)
    
    # 订阅信息
    features = models.JSONField('功能列表', default=list, blank=True)
    metadata = models.JSONField('订阅元数据', default=dict, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户订阅'
        verbose_name_plural = '用户订阅'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['subscription_type']),
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_subscription_type_display()} ({self.get_status_display()})"
    
    def is_active(self):
        """检查订阅是否激活"""
        if self.status != 'active':
            return False
        
        if self.end_date and timezone.now() > self.end_date:
            return False
        
        return True
    
    def has_premium_access(self):
        """检查是否有高级访问权限"""
        return self.is_active() and self.subscription_type in ['premium', 'pro']
    
    def get_remaining_days(self):
        """获取剩余天数"""
        if not self.end_date:
            return None
        
        remaining = self.end_date - timezone.now()
        return max(0, remaining.days)
    
    def extend_subscription(self, days):
        """延长订阅"""
        if not self.end_date:
            self.end_date = timezone.now() + timedelta(days=days)
        else:
            self.end_date += timedelta(days=days)
        self.save()


class SubscriptionFeature(models.Model):
    """订阅功能模型 - 定义不同订阅级别的功能"""
    name = models.CharField('功能名称', max_length=100)
    code = models.CharField('功能代码', max_length=50, unique=True)
    description = models.TextField('功能描述', blank=True)
    
    # 功能配置
    is_active = models.BooleanField('是否激活', default=True)
    subscription_types = models.JSONField(
        '适用订阅类型',
        default=list,
        help_text='适用的订阅类型列表'
    )
    
    # 限制设置
    usage_limit = models.IntegerField('使用限制', null=True, blank=True)
    daily_limit = models.IntegerField('每日限制', null=True, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '订阅功能'
        verbose_name_plural = '订阅功能'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_available_for_subscription(self, subscription_type):
        """检查功能是否对指定订阅类型可用"""
        if not self.is_active:
            return False
        return subscription_type in self.subscription_types
