from django.contrib import admin
from .models import LearningGoal, GoalWord, LearningSession, WordLearningRecord, LearningPlan

class GoalWordInline(admin.TabularInline):
    """目标单词内联编辑"""
    model = GoalWord
    extra = 3
    raw_id_fields = ['word']
    readonly_fields = ['added_at']
    fields = ['word', 'added_at']

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_words_count', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['word_sets', 'vocabulary_lists']  # 添加多对多字段的水平过滤器
    inlines = [GoalWordInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'name', 'description', 'target_words_count')
        }),
        ('时间设置', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('批量添加单词', {
            'fields': ('word_sets', 'vocabulary_lists'),
            'description': '选择单词集或单词库来批量添加目标单词'
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

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

@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    list_display = ['goal', 'plan_type', 'words_per_day', 'review_interval', 'is_active']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['goal__name']
    readonly_fields = ['created_at']

# VocabularyList 和 VocabularyWord 模型已移除
