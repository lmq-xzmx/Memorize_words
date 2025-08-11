from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import LearningGoal, LearningPlan, DailyStudyRecord


@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    """学习目标管理"""
    list_display = [
        'name', 'user', 'goal_type', 'progress_display', 
        'is_current', 'created_at'
    ]
    list_filter = ['goal_type', 'is_current', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_current', '-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'name', 'description', 'goal_type')
        }),
        ('关联对象', {
            'fields': ('vocabulary_list', 'word_set', 'grade_level')
        }),
        ('学习进度', {
            'fields': ('total_words', 'learned_words', 'is_current')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='学习进度')
    def progress_display(self, obj):
        """显示学习进度"""
        percentage = obj.progress_percentage
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background: #f0f0f0; border-radius: 3px;">'  
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'  
            '{}%</div></div>',
            percentage, color, percentage
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user', 'vocabulary_list', 'word_set', 'grade_level')


@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    """学习计划管理"""
    list_display = [
        'name', 'user', 'learning_goal', 'plan_mode', 
        'duration_display', 'status', 'created_at'
    ]
    list_filter = ['plan_mode', 'status', 'created_at']
    search_fields = ['name', 'user__username', 'learning_goal__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'learning_goal', 'name', 'plan_mode')
        }),
        ('计划设置', {
            'fields': ('start_date', 'end_date', 'total_words', 'daily_target')
        }),
        ('状态', {
            'fields': ('status',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='持续时间')
    def duration_display(self, obj):
        """显示计划持续时间"""
        days = obj.duration_days
        return format_html(
            '<span style="color: {};">{} 天</span>',
            'blue' if days > 0 else 'gray',
            days
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user', 'learning_goal')


@admin.register(DailyStudyRecord)
class DailyStudyRecordAdmin(admin.ModelAdmin):
    """每日学习记录管理"""
    list_display = [
        'user', 'learning_plan', 'study_date', 
        'completion_display', 'study_duration'
    ]
    list_filter = ['study_date', 'learning_plan__status']
    search_fields = ['user__username', 'learning_plan__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-study_date']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'learning_plan', 'study_date')
        }),
        ('学习数据', {
            'fields': ('target_words', 'completed_words', 'study_duration')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='完成情况')
    def completion_display(self, obj):
        """显示完成情况"""
        rate = obj.completion_rate
        color = 'green' if rate >= 100 else 'orange' if rate >= 80 else 'red'
        return format_html(
            '<span style="color: {};">{}/ {} ({}%)</span>',
            color, obj.completed_words, obj.target_words, rate
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user', 'learning_plan')