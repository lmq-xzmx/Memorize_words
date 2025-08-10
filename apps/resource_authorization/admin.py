from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    ResourceAuthorization,
    ResourceShare,
    ResourceCategory,
    ResourceUsageAnalytics,
    UserSubscription,
    SubscriptionFeature
)


@admin.register(ResourceAuthorization)
class ResourceAuthorizationAdmin(admin.ModelAdmin):
    """资源授权管理"""
    list_display = [
        'id', 'resource_type', 'resource_id', 'access_level',
        'created_by', 'is_active', 'is_public', 'created_at'
    ]
    list_filter = [
        'resource_type', 'access_level', 'is_active', 'is_public',
        'requires_subscription', 'created_at'
    ]
    search_fields = ['resource_id', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('resource_type', 'resource_id', 'access_level')
        }),
        ('权限设置', {
            'fields': ('created_by', 'is_active', 'is_public', 'requires_subscription')
        }),
        ('时间控制', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('元数据', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(ResourceShare)
class ResourceShareAdmin(admin.ModelAdmin):
    """资源分享管理"""
    list_display = [
        'id', 'authorization', 'shared_by', 'share_type',
        'is_active', 'shared_at', 'expires_at'
    ]
    list_filter = [
        'share_type', 'is_active', 'allow_reshare',
        'shared_at', 'expires_at'
    ]
    search_fields = ['shared_by__username', 'share_message']
    readonly_fields = ['shared_at']
    filter_horizontal = ['shared_with']
    
    fieldsets = (
        ('分享信息', {
            'fields': ('authorization', 'shared_by', 'share_type')
        }),
        ('分享对象', {
            'fields': ('shared_with',)
        }),
        ('分享设置', {
            'fields': ('is_active', 'allow_reshare', 'expires_at')
        }),
        ('分享内容', {
            'fields': ('share_message',)
        }),
        ('元数据', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'authorization', 'shared_by'
        ).prefetch_related('shared_with')


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    """资源分类管理"""
    list_display = [
        'id', 'name', 'parent', 'created_by',
        'is_public', 'sort_order', 'resource_count'
    ]
    list_filter = ['is_public', 'created_at', 'parent']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'resource_count']
    filter_horizontal = ['authorizations']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'parent')
        }),
        ('设置', {
            'fields': ('created_by', 'is_public', 'sort_order')
        }),
        ('关联资源', {
            'fields': ('authorizations',)
        }),
        ('统计信息', {
            'fields': ('resource_count',),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def resource_count(self, obj):
        """显示资源数量"""
        return obj.get_resource_count()
    resource_count.short_description = '资源数量'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'parent', 'created_by'
        ).prefetch_related('authorizations')


@admin.register(ResourceUsageAnalytics)
class ResourceUsageAnalyticsAdmin(admin.ModelAdmin):
    """资源使用分析管理"""
    list_display = [
        'id', 'authorization', 'user', 'action',
        'platform', 'timestamp'
    ]
    list_filter = [
        'action', 'platform', 'timestamp'
    ]
    search_fields = ['user__username', 'session_id', 'ip_address']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('authorization', 'user', 'action')
        }),
        ('上下文信息', {
            'fields': ('platform', 'session_id', 'timestamp')
        }),
        ('技术信息', {
            'fields': ('user_agent', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'authorization', 'user'
        )
    
    def has_add_permission(self, request):
        """禁止手动添加分析记录"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改分析记录"""
        return False


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """用户订阅管理"""
    list_display = [
        'id', 'user', 'subscription_type', 'status',
        'start_date', 'end_date', 'is_active_display', 'remaining_days_display'
    ]
    list_filter = [
        'subscription_type', 'status', 'start_date', 'end_date'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'is_active_display', 'remaining_days_display']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('订阅信息', {
            'fields': ('subscription_type', 'status')
        }),
        ('时间管理', {
            'fields': ('start_date', 'end_date')
        }),
        ('订阅详情', {
            'fields': ('features', 'metadata'),
            'classes': ('collapse',)
        }),
        ('状态信息', {
            'fields': ('is_active_display', 'remaining_days_display'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_active_display(self, obj):
        """显示激活状态"""
        if obj.is_active():
            return format_html('<span style="color: green;">✓ 激活</span>')
        else:
            return format_html('<span style="color: red;">✗ 未激活</span>')
    is_active_display.short_description = '激活状态'
    
    def remaining_days_display(self, obj):
        """显示剩余天数"""
        days = obj.get_remaining_days()
        if days is None:
            return '无限制'
        elif days > 30:
            return format_html('<span style="color: green;">{} 天</span>', days)
        elif days > 7:
            return format_html('<span style="color: orange;">{} 天</span>', days)
        else:
            return format_html('<span style="color: red;">{} 天</span>', days)
    remaining_days_display.short_description = '剩余天数'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SubscriptionFeature)
class SubscriptionFeatureAdmin(admin.ModelAdmin):
    """订阅功能管理"""
    list_display = [
        'id', 'name', 'code', 'is_active',
        'subscription_types_display', 'usage_limit', 'daily_limit'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'description')
        }),
        ('功能配置', {
            'fields': ('is_active', 'subscription_types')
        }),
        ('限制设置', {
            'fields': ('usage_limit', 'daily_limit')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def subscription_types_display(self, obj):
        """显示适用订阅类型"""
        if obj.subscription_types:
            return ', '.join(obj.subscription_types)
        return '无'
    subscription_types_display.short_description = '适用订阅类型'


# 自定义管理站点标题
admin.site.site_header = 'Natural English 资源授权系统'
admin.site.site_title = '资源授权管理'
admin.site.index_title = '资源授权系统管理'
