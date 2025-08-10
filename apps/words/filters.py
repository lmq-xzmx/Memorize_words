from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Word


class DifficultyLevelFilter(admin.SimpleListFilter):
    """难度等级过滤器"""
    title = _('难度等级')
    parameter_name = 'difficulty_level'

    def lookups(self, request, model_admin):
        return (
            ('1', _('等级1')),
            ('2', _('等级2')),
            ('3', _('等级3')),
            ('4', _('等级4')),
            ('5', _('等级5')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(difficulty_level=self.value())
        return queryset


class MasteryLevelFilter(admin.SimpleListFilter):
    """掌握程度过滤器"""
    title = _('掌握程度')
    parameter_name = 'mastery_level'

    def lookups(self, request, model_admin):
        return (
            ('0-20', _('初学者 (0-20)')),
            ('21-40', _('入门 (21-40)')),
            ('41-60', _('中等 (41-60)')),
            ('61-80', _('熟练 (61-80)')),
            ('81-100', _('精通 (81-100)')),
        )

    def queryset(self, request, queryset):
        if self.value() == '0-20':
            return queryset.filter(mastery_level__gte=0, mastery_level__lte=20)
        elif self.value() == '21-40':
            return queryset.filter(mastery_level__gte=21, mastery_level__lte=40)
        elif self.value() == '41-60':
            return queryset.filter(mastery_level__gte=41, mastery_level__lte=60)
        elif self.value() == '61-80':
            return queryset.filter(mastery_level__gte=61, mastery_level__lte=80)
        elif self.value() == '81-100':
            return queryset.filter(mastery_level__gte=81, mastery_level__lte=100)
        return queryset


class LearnedStatusFilter(admin.SimpleListFilter):
    """学习状态过滤器"""
    title = _('学习状态')
    parameter_name = 'learned_status'

    def lookups(self, request, model_admin):
        return (
            ('learned', _('已学习')),
            ('not_learned', _('未学习')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'learned':
            return queryset.filter(is_learned=True)
        elif self.value() == 'not_learned':
            return queryset.filter(is_learned=False)
        return queryset


class WordLengthFilter(admin.SimpleListFilter):
    """单词长度过滤器"""
    title = _('单词长度')
    parameter_name = 'word_length'

    def lookups(self, request, model_admin):
        return (
            ('short', _('短单词 (1-4字母)')),
            ('medium', _('中等单词 (5-8字母)')),
            ('long', _('长单词 (9+字母)')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'short':
            return queryset.extra(where=["LENGTH(word) <= 4"])
        elif self.value() == 'medium':
            return queryset.extra(where=["LENGTH(word) BETWEEN 5 AND 8"])
        elif self.value() == 'long':
            return queryset.extra(where=["LENGTH(word) >= 9"])
        return queryset


class ConflictStatusFilter(admin.SimpleListFilter):
    """冲突状态过滤器（用于ImportedVocabulary）"""
    title = _('冲突状态')
    parameter_name = 'conflict_status'

    def lookups(self, request, model_admin):
        return (
            ('has_conflict', _('有冲突')),
            ('no_conflict', _('无冲突')),
            ('resolved', _('已解决')),
            ('unresolved', _('未解决')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'has_conflict':
            return queryset.filter(has_conflict=True)
        elif self.value() == 'no_conflict':
            return queryset.filter(has_conflict=False)
        elif self.value() == 'resolved':
            return queryset.filter(has_conflict=True, conflict_resolved=True)
        elif self.value() == 'unresolved':
            return queryset.filter(has_conflict=True, conflict_resolved=False)
        return queryset


class FirstLetterFilter(admin.SimpleListFilter):
    """首字母过滤器"""
    title = _('首字母')
    parameter_name = 'first_letter'

    def lookups(self, request, model_admin):
        letters = []
        for i in range(26):
            letter = chr(ord('A') + i)
            letters.append((letter.lower(), letter))
        return letters

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(word__istartswith=self.value())
        return queryset


class ResourceTypeFilter(admin.SimpleListFilter):
    """资源类型过滤器"""
    title = _('资源类型')
    parameter_name = 'resource_type'

    def lookups(self, request, model_admin):
        return (
            ('audio', _('音频')),
            ('video', _('视频')),
            ('image', _('图片')),
            ('pdf', _('PDF文档')),
            ('markdown', _('Markdown文档')),
            ('text', _('文本文档')),
            ('url', _('网络链接')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(resource_type=self.value())
        return queryset