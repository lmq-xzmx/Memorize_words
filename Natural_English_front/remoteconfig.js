from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    LearningGoal, GoalWord, LearningSession, WordLearningRecord, LearningPlan,
    GuidedPracticeSession, GuidedPracticeQuestion, GuidedPracticeAnswer,
    UserStreak, DailyStudyRecord, WordLearningProgress
)

class GoalWordInline(admin.TabularInline):
    """目标单词内联编辑 - 优化为分步加载"""
    model = GoalWord
    extra = 0  # 减少默认显示的空行
    raw_id_fields = ['word']
    readonly_fields = ['added_at']
    fields = ['word', 'added_at']
    
    # 添加自定义CSS和JS来实现下拉+点击分步加载
    class Media:
        css = {
            'all': ('admin/css/goal_words_inline.css',)
        }
        js = ('admin/js/goal_words_inline.js',)
    
    def get_queryset(self, request):
        """优化查询，分页加载"""
        qs = super().get_queryset(request)
        return qs.select_related('word').order_by('-added_at')[:50]  # 限制初始加载数量
    
    def has_add_permission(self, request, obj=None):
        """控制添加权限"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """控制修改权限"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """控制删除权限"""
        return True

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_words_count', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['word_sets', 'vocabulary_lists']  # 添加多对多字段的水平过滤器
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'name', 'description', 'target_words_count')
        }),
        ('时间设置', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('关联资源', {
            'fields': ('goal_type', 'vocabulary_list', 'word_set'),
            'description': '选择目标类型和对应的单一资源'
        }),
        ('批量添加单词', {
            'fields': ('word_sets', 'vocabulary_lists'),
            'description': '选择多个单词集或单词库来批量添加目标单词'
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        """自定义表单，在新建时隐藏多对多字段"""
        form = super().get_form(request, obj, change, **kwargs)
        if obj is None:  # 新建对象时
            # 移除多对多字段，避免在保存前使用
            if 'word_sets' in form.base_fields:
                del form.base_fields['word_sets']
            if 'vocabulary_lists' in form.base_fields:
                del form.base_fields['vocabulary_lists']
        return form
    
    def get_fieldsets(self, request, obj=None):
        """动态调整字段集"""
        if obj is None:  # 新建对象时
            # 移除包含多对多字段的字段集
            return [
                ('基本信息', {
                    'fields': ('user', 'name', 'description', 'target_words_count')
                }),
                ('关联资源', {
                    'fields': ('goal_type', 'vocabulary_list', 'word_set'),
                    'description': '选择目标类型和对应的单一资源'
                }),
                ('时间设置', {
                    'fields': ('start_date', 'end_date', 'is_active')
                }),
                ('系统信息', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            ]
        return super().get_fieldsets(request, obj)
    
    def get_inlines(self, request, obj):
        """只在编辑现有对象时显示内联"""
        if obj is None:  # 新建对象时不显示内联
            return ()
        return (GoalWordInline,)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """自定义编辑视图，添加分步加载支持"""
        extra_context = extra_context or {}
        
        # 添加目标单词统计信息
        if object_id:
            try:
                obj = self.get_object(request, object_id)
                if obj:
                    extra_context.update({
                        'goal_words_count': obj.goal_words.count(),
                        'goal_id': object_id,
                        'has_goal_words': obj.goal_words.exists()
                    })
            except Exception:
                pass
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related('user').prefetch_related(
            'goal_words__word', 'word_sets', 'vocabulary_lists'
        )
    
    class Media:
        """添加自定义CSS和JS"""
        css = {
            'all': ('admin/css/goal_words_inline.css',)
        }
        js = ('admin/js/goal_words_inline.js',)

@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal', 'start_time', 'end_time', 'words_studied', 'accuracy_rate']
    list_filter = ['start_time', 'end_time']
    search_fields = ['user__username', 'goal__name']
    readonly_fields = ['start_time', 'end_time', 'accuracy_rate', 'duration']

@admin.register(WordLearningRecord)
class WordLearningRecordAdmin(admin.ModelAdmin):
    list_display = ['word', 'session', 'goal', 'is_correct', 'response_time', 'created_at']
    list_filter = ['is_correct', 'created_at', 'goal']
    search_fields = ['word__word', 'goal__name', 'session__user__username']
    readonly_fields = ['created_at']

# DailyStudyRecordInline 已移除，因为 vocabulary_manager.DailyStudyRecord 
# 与 teaching.LearningPlan 没有直接的外键关系
# 如需要可以创建专门的 teaching 应用内联模型

@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'goal', 'plan_mode', 'plan_type', 
        'daily_target', 'status', 'progress_display', 'is_active'
    ]
    list_filter = ['plan_mode', 'plan_type', 'status', 'is_active', 'created_at']
    search_fields = ['name', 'user__username', 'goal__name']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage', 'total_days', 'elapsed_days', 'remaining_days']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'goal', 'name', 'description')
        }),
        ('计划设置', {
            'fields': ('plan_type', 'plan_mode', 'difficulty', 'status')
        }),
        ('学习参数', {
            'fields': ('total_words', 'daily_target', 'words_per_day', 'review_interval')
        }),
        ('时间设置', {
            'fields': ('start_date', 'end_date', 'daily_study_time')
        }),
        ('进度信息', {
            'fields': ('progress_percentage', 'total_days', 'elapsed_days', 'remaining_days'),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='进度', ordering='progress_percentage')
    def progress_display(self, obj):
        """进度显示"""
        progress = obj.progress_percentage
        color = 'green' if progress >= 80 else 'orange' if progress >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, f'{progress:.1f}'
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user', 'goal')
    
    actions = ['activate_plans', 'deactivate_plans', 'update_daily_targets']
    
    @admin.action(description='激活选中的学习计划')
    def activate_plans(self, request, queryset):
        """批量激活学习计划"""
        updated = queryset.update(is_active=True, status='active')
        self.message_user(request, f'成功激活 {updated} 个学习计划')
    
    @admin.action(description='停用选中的学习计划')
    def deactivate_plans(self, request, queryset):
        """批量停用学习计划"""
        updated = queryset.update(is_active=False, status='paused')
        self.message_user(request, f'成功停用 {updated} 个学习计划')
    
    @admin.action(description='更新每日目标')
    def update_daily_targets(self, request, queryset):
        """批量更新每日目标"""
        count = 0
        for plan in queryset:
            plan.update_daily_target()
            count += 1
        self.message_user(request, f'成功更新 {count} 个学习计划的每日目标')

@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    """用户连续学习记录管理"""
    list_display = ['user', 'current_streak', 'longest_streak', 'last_study_date']
    list_filter = ['last_study_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['current_streak', 'longest_streak']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(DailyStudyRecord)
class DailyStudyRecordAdmin(admin.ModelAdmin):
    """每日学习记录管理"""
    list_display = ['user', 'date', 'words_studied', 'words_learned', 'learning_efficiency', 'study_time', 'sessions_count']
    list_filter = ['date', 'words_studied', 'words_learned']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'date'
    readonly_fields = ['learning_efficiency']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(WordLearningProgress)
class WordLearningProgressAdmin(admin.ModelAdmin):
    """单词学习进度管理"""
    list_display = [
        'user', 'word', 'goal', 'total_attempts', 'mastery_level_display',
        'accuracy_rate_display', 'created_at'
    ]
    list_filter = [
        'mastery_level', 'total_attempts', 'goal',
        'created_at'
    ]
    search_fields = [
        'user__username', 'user__real_name', 
        'goal__name', 'word__word'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'accuracy_rate'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'goal', 'word')
        }),
        ('学习进度', {
            'fields': ('mastery_level', 'correct_count', 'total_attempts', 'accuracy_rate')
        }),
        ('时间信息', {
            'fields': ('first_learned_at', 'last_reviewed_at', 'next_review_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='掌握程度', ordering='mastery_level')
    def mastery_level_display(self, obj):
        """掌握程度显示"""
        return obj.get_mastery_level_display()
    
    @admin.display(description='正确率')
    def accuracy_rate_display(self, obj):
        """正确率显示"""
        rate = obj.accuracy_rate
        color = 'green' if rate >= 80 else 'orange' if rate >= 60 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, rate
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'user', 'goal', 'word'
        )
    
    actions = ['mark_as_mastered', 'reset_progress']
    
    @admin.action(description='标记为已掌握')
    def mark_as_mastered(self, request, queryset):
        """批量标记为已掌握"""
        updated = queryset.update(
            mastery_level='mastered'
        )
        self.message_user(
            request, 
            f'成功将 {updated} 个单词标记为已掌握'
        )
    
    @admin.action(description='重置学习进度')
    def reset_progress(self, request, queryset):
        """批量重置学习进度"""
        updated = queryset.update(
            mastery_level='new',
            correct_count=0,
            total_attempts=0
        )
        self.message_user(
            request, 
            f'成功重置 {updated} 个单词的学习进度'
        )

# VocabularyList 和 VocabularyWord 模型已移除
