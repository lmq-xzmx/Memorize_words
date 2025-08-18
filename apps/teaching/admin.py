from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from utils.admin_mixins import AdminDynamicPaginationMixin
from .models import (
    LearningGoal, GoalWord, LearningSession, WordLearningRecord, LearningPlan,
    DailyStudyRecord, GuidedPracticeSession, GuidedPracticeQuestion, GuidedPracticeAnswer
)


class GoalWordInline(admin.TabularInline):
    """学习目标单词内联编辑"""
    model = GoalWord
    extra = 0
    fields = ['word', 'added_at']
    readonly_fields = ['added_at']
    autocomplete_fields = ['word']


class LearningPlanInline(admin.TabularInline):
    """学习计划内联编辑"""
    model = LearningPlan
    extra = 0
    fields = ['plan_type', 'words_per_day', 'review_interval', 'is_active']
    
    def get_formset(self, request, obj=None, **kwargs):
        """获取表单集时设置初始值"""
        # 处理测试环境中request为None的情况
        if request is None:
            # 创建一个模拟的request对象用于测试
            from django.http import HttpRequest
            from django.contrib.auth.models import AnonymousUser
            request = HttpRequest()
            # 使用setattr避免类型检查器警告
            setattr(request, 'user', AnonymousUser())
        
        formset = super().get_formset(request, obj, **kwargs)
        
        class CustomFormSet(formset):
            def save_new(self, form, commit=True):
                """保存新对象时自动设置user"""
                instance = super().save_new(form, commit=False)
                if obj:  # obj是父对象LearningGoal
                    instance.user = obj.user
                    instance.goal = obj
                if commit:
                    instance.save()
                return instance
        
        return CustomFormSet


@admin.register(LearningGoal)
class LearningGoalAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """学习目标管理"""
    list_display = [
        'name', 'user', 'goal_type', 'target_words_count',
        'progress_display', 'is_active', 'start_date', 'end_date'
    ]
    list_filter = [
        'goal_type', 'is_active', 'start_date', 'end_date',
        ('user', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['name', 'description', 'user__username', 'user__email']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25

    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'name', 'description', 'goal_type')
        }),
        ('目标设置', {
            'fields': ('target_words_count', 'start_date', 'end_date', 'is_active')
        }),
        ('词汇来源', {
            'fields': ('vocabulary_lists', 'word_sets'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['vocabulary_lists', 'word_sets']
    inlines = [GoalWordInline, LearningPlanInline]
    
    @admin.display(description='学习进度')
    def progress_display(self, obj):
        """显示学习进度"""
        stats = obj.get_progress_stats()
        percentage = stats['progress_percentage']
        
        if percentage >= 80:
            color = 'green'
        elif percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{} % ({}/{})</span>',
            color, round(percentage, 1), stats['learned_words'], stats['total_words']
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user').prefetch_related(
            'goal_words__word', 'vocabulary_lists', 'word_sets'
        )


@admin.register(GoalWord)
class GoalWordAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """目标单词管理"""
    list_display = ['goal', 'word', 'added_at']
    list_filter = [
        ('goal', admin.RelatedOnlyFieldListFilter),
        'added_at'
    ]
    search_fields = ['goal__name', 'word__word', 'word__meaning']
    date_hierarchy = 'added_at'
    readonly_fields = ['added_at']
    ordering = ['-added_at']
    list_per_page = 50
    
    autocomplete_fields = ['goal', 'word']
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('goal', 'word')


class WordLearningRecordInline(admin.TabularInline):
    """单词学习记录内联编辑"""
    model = WordLearningRecord
    extra = 0
    fields = ['word', 'user_answer', 'is_correct', 'response_time', 'is_forgotten']
    readonly_fields = ['created_at']
    autocomplete_fields = ['word']


@admin.register(LearningSession)
class LearningSessionAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """学习会话管理"""
    list_display = [
        'user', 'goal', 'start_time', 'duration_display',
        'words_studied', 'accuracy_rate_display', 'status_display'
    ]
    list_filter = [
        'start_time', 'end_time',
        ('user', admin.RelatedOnlyFieldListFilter),
        ('goal', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['user__username', 'goal__name']
    date_hierarchy = 'start_time'
    readonly_fields = ['start_time']
    ordering = ['-start_time']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'goal')
        }),
        ('会话数据', {
            'fields': ('start_time', 'end_time', 'words_studied')
        }),
        ('学习成果', {
            'fields': ('correct_answers', 'total_answers')
        })
    )
    
    inlines = [WordLearningRecordInline]
    
    @admin.display(description='学习时长')
    def duration_display(self, obj):
        """显示学习时长"""
        duration = obj.duration
        if duration == 0:
            return '进行中'
        return f'{duration}分钟'
    
    @admin.display(description='正确率')
    def accuracy_rate_display(self, obj):
        """显示正确率"""
        rate = obj.accuracy_rate
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{} %</span>',
            color, round(rate, 1)
        )
    
    @admin.display(description='状态')
    def status_display(self, obj):
        """显示会话状态"""
        if obj.end_time:
            return format_html('<span style="color: green;">✓ 已完成</span>')
        else:
            return format_html('<span style="color: orange;">⏳ 进行中</span>')
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user', 'goal')


@admin.register(WordLearningRecord)
class WordLearningRecordAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """单词学习记录管理"""
    list_display = [
        'word', 'user_answer', 'is_correct_display', 'response_time_display',
        'is_forgotten', 'session', 'created_at'
    ]
    list_filter = [
        'is_correct', 'is_forgotten', 'created_at',
        ('session__user', admin.RelatedOnlyFieldListFilter),
        ('goal', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['word__word', 'user_answer', 'session__user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('session', 'goal', 'word')
        }),
        ('学习数据', {
            'fields': ('user_answer', 'is_correct', 'response_time')
        }),
        ('状态', {
            'fields': ('is_forgotten', 'created_at')
        })
    )
    
    autocomplete_fields = ['session', 'goal', 'word']
    
    @admin.display(description='正确性')
    def is_correct_display(self, obj):
        """显示正确性"""
        if obj.is_correct:
            return format_html('<span style="color: green;">✓ 正确</span>')
        else:
            return format_html('<span style="color: red;">✗ 错误</span>')
    
    @admin.display(description='响应时间')
    def response_time_display(self, obj):
        """显示响应时间"""
        time = obj.response_time
        if time < 2:
            color = 'green'
        elif time < 5:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{} 秒</span>',
            color, round(time, 1)
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'session__user', 'goal', 'word'
        )


@admin.register(LearningPlan)
class LearningPlanAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """学习计划管理"""
    list_display = [
        'goal', 'plan_type_display', 'words_per_day',
        'review_interval', 'is_active', 'created_at'
    ]
    list_filter = [
        'plan_type', 'is_active', 'created_at',
        ('goal', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['goal__name', 'goal__user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('goal', 'plan_type', 'is_active'),
            'description': '选择学习目标和计划类型。不同的计划类型适用于不同的学习习惯和时间安排。'
        }),
        ('计划设置', {
            'fields': ('name', 'start_date', 'end_date', 'total_words', 'daily_target', 'words_per_day', 'review_interval', 'status'),
            'description': '根据选择的计划类型设置相应的学习参数。不同类型的计划需要不同的配置参数。',
            'classes': ('dynamic-fieldset',)
        }),
        ('学习模式说明', {
            'fields': (),
            'description': '''
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h4 style="color: #495057; margin-top: 0;">📚 学习模式详细说明：</h4>
                <ul style="line-height: 1.6; color: #6c757d;">
                    <li><strong>🔧 机械模式：</strong>固定每日学习量，不考虑学习进展更新。适合有固定学习时间和习惯的用户。</li>
                    <li><strong>📈 日进模式：</strong>根据学习进展每日更新，按剩余时间均分。智能调整学习量，确保按时完成目标。</li>
                    <li><strong>💼 工作日模式：</strong>只在工作日学习，按剩余工作日均分。适合工作日有规律学习时间的用户。</li>
                    <li><strong>🎯 周末模式：</strong>只在周末学习，按剩余周末天数均分。适合平时忙碌，周末集中学习的用户。</li>
                    <li><strong>📅 每日计划：</strong>标准每日学习计划，平均分配学习任务。</li>
                    <li><strong>📊 每周计划：</strong>按周制定学习计划，灵活安排每周学习进度。</li>
                    <li><strong>⚙️ 自定义计划：</strong>用户自定义学习节奏，完全个性化的学习安排。</li>
                </ul>
            </div>
            ''',
            'classes': ('wide',)
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    autocomplete_fields = ['goal']
    
    class Media:
        js = ('admin/js/learning_plan_admin.js',)
        css = {
            'all': ('admin/css/learning_plan_admin.css',)
        }
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        """自定义表单，根据计划类型显示不同字段"""
        form = super().get_form(request, obj, change, **kwargs)
        
        # 为计划类型字段添加onchange事件
        base_fields = getattr(form, 'base_fields', {})
        if 'plan_type' in base_fields:
            base_fields['plan_type'].widget.attrs.update({
                'onchange': 'updatePlanSettings(this.value);'
            })
        
        return form
    
    @admin.display(description='计划类型')
    def plan_type_display(self, obj):
        """显示计划类型"""
        type_icons = {
            'mechanical': '🔧',
            'daily_progress': '📈',
            'weekday': '💼',
            'weekend': '🎯',
            'daily': '📅',
            'weekly': '📊',
            'custom': '⚙️'
        }
        icon = type_icons.get(obj.plan_type, '📋')
        return format_html(
            '<span title="{}">{} {}</span>',
            obj.get_plan_type_display(),
            icon,
            obj.get_plan_type_display().split(' - ')[0] if ' - ' in obj.get_plan_type_display() else obj.get_plan_type_display()
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('goal__user')


@admin.register(DailyStudyRecord)
class DailyStudyRecordAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """每日学习记录管理"""
    list_display = [
        'user', 'learning_plan', 'study_date', 'target_words', 'completed_words',
        'completion_rate_display', 'study_duration_display', 'created_at'
    ]
    list_filter = ['study_date', 'created_at', 'learning_plan']
    search_fields = ['user__username', 'learning_plan__goal__name']
    date_hierarchy = 'study_date'
    readonly_fields = ['created_at', 'completion_rate']
    ordering = ['-study_date']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'learning_plan', 'study_date')
        }),
        ('学习数据', {
            'fields': ('target_words', 'completed_words', 'completion_rate', 'study_duration')
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='完成率')
    def completion_rate_display(self, obj):
        """显示完成率"""
        rate = obj.completion_rate
        color = 'green' if rate >= 80 else 'orange' if rate >= 60 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    
    @admin.display(description='学习时长')
    def study_duration_display(self, obj):
        """显示学习时长"""
        if obj.study_duration:
            minutes = obj.study_duration.total_seconds() / 60
            return f'{int(minutes)} 分钟'
        return '-'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user', 'learning_plan__goal')


@admin.register(GuidedPracticeSession)
class GuidedPracticeSessionAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """引导练习会话管理"""
    list_display = [
        'user', 'goal', 'session_type', 'total_questions', 'correct_answers',
        'accuracy_rate_display', 'is_completed', 'start_time'
    ]
    list_filter = ['session_type', 'is_completed', 'start_time']
    search_fields = ['user__username', 'goal__name']
    date_hierarchy = 'start_time'
    readonly_fields = ['start_time']
    ordering = ['-start_time']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'goal', 'session_type')
        }),
        ('会话数据', {
            'fields': ('start_time', 'end_time', 'total_questions', 'correct_answers', 'is_completed')
        })
    )
    
    @admin.display(description='正确率')
    def accuracy_rate_display(self, obj):
        """显示正确率"""
        if obj.total_questions > 0:
            rate = (obj.correct_answers / obj.total_questions) * 100
            color = 'green' if rate >= 80 else 'orange' if rate >= 60 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, rate
            )
        return '-'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('user', 'goal')


@admin.register(GuidedPracticeQuestion)
class GuidedPracticeQuestionAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """引导练习题目管理"""
    list_display = [
        'session', 'question_type', 'question_text_short', 'correct_answer',
        'order', 'created_at'
    ]
    list_filter = ['question_type', 'created_at']
    search_fields = ['question_text', 'correct_answer', 'session__user__username']
    readonly_fields = ['created_at']
    ordering = ['session', 'order']
    list_per_page = 100
    
    fieldsets = (
        ('基本信息', {
            'fields': ('session', 'question_type', 'order')
        }),
        ('题目内容', {
            'fields': ('question_text', 'correct_answer', 'options')
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='题目内容')
    def question_text_short(self, obj):
        """显示题目内容简短版"""
        content = obj.question_text
        if len(content) > 50:
            return content[:50] + '...'
        return content
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('session__user', 'session__goal')


@admin.register(GuidedPracticeAnswer)
class GuidedPracticeAnswerAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """引导练习答案管理"""
    list_display = [
        'question', 'user_answer', 'is_correct_display', 'response_time_display',
        'created_at'
    ]
    list_filter = ['is_correct', 'created_at']
    search_fields = ['user_answer', 'question__question_text', 'question__session__user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('question', 'user_answer', 'is_correct')
        }),
        ('响应数据', {
            'fields': ('response_time',)
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='正确性')
    def is_correct_display(self, obj):
        """显示正确性"""
        if obj.is_correct:
            return format_html('<span style="color: green;">✓ 正确</span>')
        else:
            return format_html('<span style="color: red;">✗ 错误</span>')
    
    @admin.display(description='响应时间')
    def response_time_display(self, obj):
        """显示响应时间"""
        time = obj.response_time
        if time < 2:
            color = 'green'
        elif time < 5:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{}秒</span>',
            color, round(time, 1)
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related(
            'question__session__user', 'question__session__goal'
        )