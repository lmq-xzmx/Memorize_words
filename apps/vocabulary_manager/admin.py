from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import LearningGoal, LearningPlan, DailyStudyRecord, StudySession, UserStreak, WordLearningProgress
from django.utils import timezone
from django.contrib.admin import AdminSite


@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    """学习目标管理"""
    list_display = [
        'name', 'user', 'goal_type', 'is_current', 
        'progress_display', 'total_words', 'learned_words', 'created_at'
    ]
    list_filter = ['goal_type', 'is_current', 'created_at']
    search_fields = ['name', 'user__username', 'user__real_name']
    readonly_fields = ['total_words', 'learned_words']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'name', 'description', 'goal_type')
        }),
        ('目标源', {
            'fields': ('vocabulary_list', 'word_set', 'grade_level'),
            'description': '根据目标类型选择对应的源'
        }),
        ('状态', {
            'fields': ('is_current',)
        }),
        ('统计信息', {
            'fields': ('total_words', 'learned_words'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='学习进度', ordering='learned_words')
    def progress_display(self, obj):
        """进度显示"""
        percentage = obj.progress_percentage
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {}">{}%</span>',
            color, f'{percentage:.1f}'
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'user', 'vocabulary_list', 'word_set', 'grade_level'
        )


@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    """学习计划管理"""
    list_display = [
        'name', 'user', 'plan_mode', 'status',
        'start_date', 'end_date', 'daily_target', 
        'progress_display', 'created_at'
    ]
    list_filter = ['plan_mode', 'status', 'start_date', 'end_date']
    search_fields = ['name', 'user__username', 'user__real_name']
    readonly_fields = ['total_words', 'daily_target']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'learning_goal', 'name')
        }),
        ('计划模式', {
            'fields': ('plan_mode',),
            'description': '选择学习计划的执行模式'
        }),
        ('时间设置', {
            'fields': ('start_date', 'end_date')
        }),
        ('计划详情', {
            'fields': ('total_words', 'daily_target', 'status'),
            'classes': ('collapse',)
        })
    )
    
    radio_fields = {'plan_mode': admin.HORIZONTAL}
    
    @admin.display(description='计划进度')
    def progress_display(self, obj):
        """进度显示"""
        percentage = obj.get_completion_percentage() if hasattr(obj, 'get_completion_percentage') else 0
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {}">{}%</span>',
            color, f'{percentage:.1f}'
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'user', 'learning_goal'
        )


class DailyStudyRecordInline(admin.TabularInline):
    """每日学习记录内联"""
    model = DailyStudyRecord
    extra = 0
    readonly_fields = ['completion_rate', 'is_completed']
    fields = [
        'study_date', 'target_words', 'completed_words', 
        'completion_rate', 'study_duration'
    ]


@admin.register(DailyStudyRecord)
class DailyStudyRecordAdmin(admin.ModelAdmin):
    """每日学习记录管理"""
    list_display = [
        'user', 'learning_plan', 'study_date',
        'target_words', 'completed_words', 'completion_display',
        'study_duration'
    ]
    list_filter = ['study_date', 'learning_plan__plan_mode']
    search_fields = ['user__username', 'user__real_name', 'learning_plan__name']
    readonly_fields = ['completion_rate', 'is_completed']
    date_hierarchy = 'study_date'
    
    @admin.display(description='完成率', ordering='completed_words')
    def completion_display(self, obj):
        """完成率显示"""
        rate = obj.completion_rate
        color = 'green' if rate >= 100 else 'orange' if rate >= 80 else 'red'
        return format_html(
            '<span style="color: {}">{}%</span>',
            color, f'{rate:.1f}'
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'user', 'learning_plan'
        )


# 将DailyStudyRecord内联添加到LearningPlan
LearningPlanAdmin.inlines = [DailyStudyRecordInline]


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    """用户学习记录管理"""
    list_display = ['user', 'current_streak', 'longest_streak', 'total_study_days', 'last_study_date']
    list_filter = ['last_study_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_study_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('学习记录', {
            'fields': ('current_streak', 'longest_streak', 'total_study_days')
        }),
        ('时间信息', {
            'fields': ('last_study_date', 'created_at', 'updated_at')
        })
    )


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    """学习会话管理"""
    list_display = ['user', 'learning_goal', 'words_studied', 'words_learned', 'learning_efficiency', 'duration', 'start_time', 'end_time']
    list_filter = ['start_time', 'end_time', 'learning_goal']
    search_fields = ['user__username', 'learning_goal__name']
    readonly_fields = ['start_time', 'end_time', 'duration', 'learning_efficiency']
    
    fieldsets = (
        ('会话信息', {
            'fields': ('user', 'learning_goal')
        }),
        ('学习统计', {
            'fields': ('words_studied', 'words_learned', 'learning_efficiency')
        }),
        ('时间信息', {
            'fields': ('start_time', 'end_time', 'duration')
        })
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义外键字段"""
        if db_field.name == "learning_goal":
            # 显示所有学习目标，在表单中进行过滤
            kwargs["queryset"] = LearningGoal.objects.select_related('user').order_by('user__username', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(WordLearningProgress)
class WordLearningProgressAdmin(admin.ModelAdmin):
    """单词学习进度管理"""
    list_display = [
        'user', 'learning_goal', 'word', 'review_count', 
        'status_display', 'is_mastered', 'is_forgotten', 
        'last_review_date', 'first_learned_date'
    ]
    list_filter = [
        'is_mastered', 'is_forgotten', 'review_count',
        'learning_goal', 'first_learned_date', 'last_review_date'
    ]
    search_fields = [
        'user__username', 'user__real_name', 
        'learning_goal__name', 'word__word'
    ]
    readonly_fields = [
        'first_learned_date', 'updated_at', 'status', 'status_display'
    ]
    date_hierarchy = 'first_learned_date'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'learning_goal', 'word')
        }),
        ('学习进度', {
            'fields': ('review_count', 'last_review_date')
        }),
        ('学习状态', {
            'fields': ('is_mastered', 'is_forgotten', 'mastered_date')
        }),
        ('状态信息', {
            'fields': ('status', 'status_display'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('first_learned_date', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='学习状态')
    def status_display(self, obj):
        """状态显示"""
        status_colors = {
            'mastered': 'green',
            'forgotten': 'red',
            'review_1': 'blue',
            'review_2': 'blue',
            'review_3': 'blue',
            'review_4': 'blue',
            'review_5': 'blue',
            'review_6': 'blue',
            'not_started': 'gray'
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status_display
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'user', 'learning_goal', 'word'
        )
    
    actions = ['mark_as_mastered', 'mark_as_forgotten', 'reset_progress']
    
    @admin.action(description='标记为已掌握')
    def mark_as_mastered(self, request, queryset):
        """批量标记为已掌握"""
        updated = queryset.update(
            is_mastered=True,
            is_forgotten=False,
            mastered_date=timezone.now()
        )
        self.message_user(
            request, 
            f'成功将 {updated} 个单词标记为已掌握'
        )
    
    @admin.action(description='标记为已遗忘')
    def mark_as_forgotten(self, request, queryset):
        """批量标记为已遗忘"""
        updated = queryset.update(
            is_forgotten=True,
            is_mastered=False,
            mastered_date=None
        )
        self.message_user(
            request, 
            f'成功将 {updated} 个单词标记为已遗忘'
        )
    
    @admin.action(description='重置学习进度')
    def reset_progress(self, request, queryset):
        """批量重置学习进度"""
        updated = queryset.update(
            review_count=0,
            is_mastered=False,
            is_forgotten=False,
            mastered_date=None,
            last_review_date=None
        )
        self.message_user(
            request, 
            f'成功重置 {updated} 个单词的学习进度'
        )

# 自定义Admin站点
class VocabularyManagerAdminSite(AdminSite):
    """词汇管理器管理站点"""
    site_header = '成长中心'
    site_title = '成长中心 Admin'
    index_title = '欢迎使用成长中心管理系统'

# 创建自定义admin站点实例
vocabulary_manager_admin = VocabularyManagerAdminSite(name='vocabulary_manager_admin')

# 注册模型到自定义admin站点
vocabulary_manager_admin.register(LearningGoal, LearningGoalAdmin)
vocabulary_manager_admin.register(LearningPlan, LearningPlanAdmin)
vocabulary_manager_admin.register(DailyStudyRecord, DailyStudyRecordAdmin)
vocabulary_manager_admin.register(UserStreak, UserStreakAdmin)
vocabulary_manager_admin.register(StudySession, StudySessionAdmin)
vocabulary_manager_admin.register(WordLearningProgress, WordLearningProgressAdmin)
