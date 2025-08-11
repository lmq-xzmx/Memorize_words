from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import (
    UserEngagementMetrics,
    UserRetentionData,
    ABTestExperiment,
    ABTestParticipant,
    UserBehaviorPattern,
    GameElementEffectiveness
)


@admin.register(UserEngagementMetrics)
class UserEngagementMetricsAdmin(admin.ModelAdmin):
    """用户粘性指标管理"""
    list_display = [
        'user', 'date', 'session_count', 'total_session_duration_display',
        'words_practiced', 'accuracy_rate_display', 'exp_gained', 'streak_count'
    ]
    list_filter = [
        'date', 'session_count', 'accuracy_rate',
        ('user', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', '-session_count']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'date')
        }),
        ('会话指标', {
            'fields': ('session_count', 'total_session_duration', 'avg_session_duration', 'peak_activity_hour')
        }),
        ('学习指标', {
            'fields': ('words_practiced', 'correct_answers', 'total_answers', 'accuracy_rate')
        }),
        ('游戏化指标', {
            'fields': ('exp_gained', 'coins_earned', 'achievements_unlocked', 'streak_count')
        }),
        ('社交指标', {
            'fields': ('battles_participated', 'battles_won', 'social_interactions')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='总会话时长')
    def total_session_duration_display(self, obj):
        """格式化显示总会话时长"""
        minutes = obj.total_session_duration // 60
        seconds = obj.total_session_duration % 60
        return f"{minutes}分{seconds}秒"
    
    @admin.display(description='准确率')
    def accuracy_rate_display(self, obj):
        """格式化显示准确率"""
        return f"{obj.accuracy_rate:.1%}"


@admin.register(UserRetentionData)
class UserRetentionDataAdmin(admin.ModelAdmin):
    """用户留存数据管理"""
    list_display = [
        'user', 'registration_date', 'retention_status_display',
        'total_active_days', 'consecutive_active_days', 'last_active_date'
    ]
    list_filter = [
        'registration_date', 'day_1_retention', 'day_7_retention', 'day_30_retention',
        'last_active_date', ('user', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'registration_date'
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-registration_date']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'registration_date')
        }),
        ('留存指标', {
            'fields': ('day_1_retention', 'day_3_retention', 'day_7_retention', 'day_14_retention', 'day_30_retention')
        }),
        ('活跃度指标', {
            'fields': ('total_active_days', 'consecutive_active_days', 'last_active_date')
        }),
        ('生命周期价值', {
            'fields': ('total_sessions', 'total_study_time', 'total_words_learned')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='留存状态')
    def retention_status_display(self, obj):
        """显示留存状态"""
        status = []
        if obj.day_1_retention:
            status.append('1日')
        if obj.day_7_retention:
            status.append('7日')
        if obj.day_30_retention:
            status.append('30日')
        
        if status:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                ', '.join(status)
            )
        else:
            return format_html('<span style="color: red;">✗ 未留存</span>')


@admin.register(ABTestExperiment)
class ABTestExperimentAdmin(admin.ModelAdmin):
    """A/B测试实验管理"""
    list_display = [
        'name', 'is_active', 'start_date', 'end_date',
        'control_group_ratio', 'participant_count', 'target_metric'
    ]
    list_filter = ['is_active', 'start_date', 'end_date', 'target_metric']
    search_fields = ['name', 'description', 'target_metric']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at', 'participant_count']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('实验配置', {
            'fields': ('start_date', 'end_date', 'control_group_ratio', 'experiment_config')
        }),
        ('目标指标', {
            'fields': ('target_metric', 'success_criteria')
        }),
        ('统计信息', {
            'fields': ('participant_count',),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='参与者数量')
    def participant_count(self, obj):
        """参与者数量"""
        return obj.participants.count()


@admin.register(ABTestParticipant)
class ABTestParticipantAdmin(admin.ModelAdmin):
    """A/B测试参与者管理"""
    list_display = [
        'user', 'experiment', 'group', 'joined_at',
        'conversion_achieved', 'conversion_date', 'metric_value'
    ]
    list_filter = [
        'group', 'conversion_achieved', 'joined_at',
        ('experiment', admin.RelatedOnlyFieldListFilter),
        ('user', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['user__username', 'user__email', 'experiment__name']
    date_hierarchy = 'joined_at'
    readonly_fields = ['joined_at']
    ordering = ['-joined_at']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('experiment', 'user', 'group')
        }),
        ('参与数据', {
            'fields': ('joined_at', 'conversion_achieved', 'conversion_date')
        }),
        ('指标数据', {
            'fields': ('metric_value', 'additional_data')
        })
    )


@admin.register(UserBehaviorPattern)
class UserBehaviorPatternAdmin(admin.ModelAdmin):
    """用户行为模式管理"""
    list_display = [
        'user', 'preferred_study_time', 'avg_session_length',
        'engagement_type', 'churn_risk_display', 'engagement_score_display', 'last_updated'
    ]
    list_filter = [
        'preferred_study_time', 'preferred_difficulty', 'engagement_type',
        'social_activity_level', 'learning_style', 'last_updated',
        ('user', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'last_updated'
    readonly_fields = ['last_updated']
    ordering = ['-last_updated']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'last_updated')
        }),
        ('学习偏好', {
            'fields': ('preferred_study_time', 'avg_session_length', 'preferred_difficulty')
        }),
        ('游戏化偏好', {
            'fields': ('engagement_type', 'motivation_factors')
        }),
        ('社交偏好', {
            'fields': ('social_activity_level', 'competitive_tendency')
        }),
        ('学习模式', {
            'fields': ('learning_style', 'retention_rate')
        }),
        ('风险指标', {
            'fields': ('churn_risk_score', 'engagement_score')
        })
    )
    
    @admin.display(description='流失风险')
    def churn_risk_display(self, obj):
        """流失风险显示"""
        if obj.churn_risk_score >= 0.7:
            color = 'red'
            level = '高风险'
        elif obj.churn_risk_score >= 0.4:
            color = 'orange'
            level = '中风险'
        else:
            color = 'green'
            level = '低风险'
        
        percentage = f"{obj.churn_risk_score:.1%}"
        return format_html(
            '<span style="color: {};">{}({})</span>',
            color, level, percentage
        )
    
    @admin.display(description='参与度评分')
    def engagement_score_display(self, obj):
        """参与度评分显示"""
        return f"{obj.engagement_score:.2f}"


@admin.register(GameElementEffectiveness)
class GameElementEffectivenessAdmin(admin.ModelAdmin):
    """游戏化元素效果管理"""
    list_display = [
        'element_name', 'element_type', 'engagement_impact_display',
        'retention_impact_display', 'unique_users', 'measurement_period'
    ]
    list_filter = [
        'element_type', 'measurement_period_start', 'measurement_period_end'
    ]
    search_fields = ['element_name', 'element_type']
    date_hierarchy = 'measurement_period_start'
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-measurement_period_start']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('element_name', 'element_type')
        }),
        ('效果指标', {
            'fields': ('engagement_impact', 'retention_impact', 'learning_efficiency_impact')
        }),
        ('使用数据', {
            'fields': ('total_interactions', 'unique_users', 'avg_interaction_frequency')
        }),
        ('测量周期', {
            'fields': ('measurement_period_start', 'measurement_period_end')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='参与度影响')
    def engagement_impact_display(self, obj):
        """参与度影响显示"""
        if obj.engagement_impact > 0:
            value = f"+{obj.engagement_impact:.2f}"
            return format_html(
                '<span style="color: green;">{}</span>',
                value
            )
        elif obj.engagement_impact < 0:
            value = f"{obj.engagement_impact:.2f}"
            return format_html(
                '<span style="color: red;">{}</span>',
                value
            )
        else:
            return '0.00'
    
    @admin.display(description='留存影响')
    def retention_impact_display(self, obj):
        """留存影响显示"""
        if obj.retention_impact > 0:
            value = f"+{obj.retention_impact:.2f}"
            return format_html(
                '<span style="color: green;">{}</span>',
                value
            )
        elif obj.retention_impact < 0:
            value = f"{obj.retention_impact:.2f}"
            return format_html(
                '<span style="color: red;">{}</span>',
                value
            )
        else:
            return '0.00'
    
    @admin.display(description='测量周期')
    def measurement_period(self, obj):
        """测量周期显示"""
        return f"{obj.measurement_period_start.strftime('%Y-%m-%d')} 至 {obj.measurement_period_end.strftime('%Y-%m-%d')}"