from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Word, WordResource, VocabularySource, VocabularyList,
    WordSet, WordGrader, WordGradeLevel
)
from .filters import (
    DifficultyLevelFilter, MasteryLevelFilter, LearnedStatusFilter,
    WordLengthFilter, ConflictStatusFilter, FirstLetterFilter,
    ResourceTypeFilter
)


class DynamicPaginationMixin:
    """动态分页Mixin类"""
    
    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """动态设置分页大小"""
        # 从URL参数获取每页显示条数
        show_param = request.GET.get('show')
        if show_param == 'all':
            # 显示全部记录 - 使用查询集的总数
            per_page = queryset.count()
        elif show_param and show_param.isdigit():
            # 使用指定的条数
            per_page = int(show_param)
        else:
            # 使用默认值
            per_page = getattr(self, 'list_per_page', 20)
        
        from django.core.paginator import Paginator
        return Paginator(queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)


class WordSetAdminForm(forms.ModelForm):
    """WordSet管理表单"""
    
    class Meta:
        model = WordSet
        fields = '__all__'
    
    def clean_name(self):
        """验证名称"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError('单词集名称不能为空')
        
        name = name.strip()
        if len(name) > 100:
            raise ValidationError('单词集名称不能超过100个字符')
        
        return name
    
    def clean(self):
        """表单验证"""
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
            
        name = cleaned_data.get('name')
        created_by = cleaned_data.get('created_by')
        
        if name and created_by:
            # 检查同一用户的重复名称
            existing = WordSet.objects.filter(
                name=name.strip(),
                created_by=created_by
            )
            if self.instance.pk:  # 如果是更新操作，排除自己
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError({'name': '您已创建过同名的单词集'})
        
        return cleaned_data


@admin.register(WordSet)
class WordSetAdmin(DynamicPaginationMixin, admin.ModelAdmin):
    """单词集管理"""
    list_display = ['name', 'description', 'word_count', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['words']  # 多对多字段的水平过滤器
    
    # 动态分页大小
    list_per_page = 20  # 默认每页显示20条
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表视图，支持动态分页"""
        # 动态分页通过get_paginator方法实现，这里只需要调用父类方法
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('设置', {
            'fields': ('is_public', 'words', 'word_count')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_urls(self):
        """自定义URL配置"""
        urls = super().get_urls()
        custom_urls = [
            path('quick-create/', self.admin_site.admin_view(self.quick_create_view), name='words_wordset_quick_create'),
        ]
        return custom_urls + urls
    
    def quick_create_view(self, request):
        """快速创建单词集视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.http import JsonResponse
        
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            is_public = request.POST.get('is_public') == 'on'
            
            if not name:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': '单词集名称不能为空'})
                messages.error(request, '单词集名称不能为空')
                return redirect('admin:words_wordset_changelist')
            
            # 检查是否已存在同名单词集
            if WordSet.objects.filter(name=name, created_by=request.user).exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': '您已经有同名的单词集了'})
                messages.error(request, '您已经有同名的单词集了')
                return redirect('admin:words_wordset_changelist')
            
            try:
                word_set = WordSet.objects.create(
                    name=name,
                    description=description,
                    created_by=request.user,
                    is_public=is_public
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True, 
                        'word_set_id': word_set.pk,
                        'word_set_name': word_set.name,
                        'message': f'单词集 "{name}" 创建成功！'
                    })
                
                messages.success(request, f'单词集 "{name}" 创建成功！')
                return redirect('admin:words_wordset_change', word_set.pk)
                
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': f'创建失败：{str(e)}'})
                messages.error(request, f'创建失败：{str(e)}')
                return redirect('admin:words_wordset_changelist')
        
        return redirect('admin:words_wordset_changelist')
    
    def save_model(self, request, obj, form, change):
        """保存模型"""
        if not change:  # 创建新对象
            if not obj.created_by:
                obj.created_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # 更新单词数量
        obj.word_count = obj.words.count()
        obj.save(update_fields=['word_count'])


class WordResourceAdminForm(forms.ModelForm):
    """WordResource管理表单"""
    
    class Meta:
        model = WordResource
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加绑定单词字段
        self.fields['bind_words'] = forms.ModelMultipleChoiceField(
            queryset=Word.objects.all().order_by('word'),
            widget=FilteredSelectMultiple('单词', False),
            required=False,
            label='绑定单词',
            help_text='选择要绑定到此资源的单词（可选）'
        )
        
        if self.instance.pk:
            # 编辑时显示已绑定的单词
            self.fields['bind_words'].initial = self.instance.words.all()
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            # 保存绑定的单词
            bind_words = self.cleaned_data.get('bind_words')
            if bind_words is not None:
                instance.words.set(bind_words)
        return instance


@admin.register(WordResource)
class WordResourceAdmin(admin.ModelAdmin):
    """单词资源管理"""
    form = WordResourceAdminForm
    list_display = ['name', 'resource_type', 'file_display', 'url_display', 'bound_words_count', 'created_at']
    list_filter = ['resource_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'file_size', 'file_extension']
    actions = ['bind_to_words_action']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'resource_type', 'description')
        }),
        ('资源内容', {
            'fields': ('file', 'url')
        }),
        ('单词绑定', {
            'fields': ('bind_words',),
            'description': '选择要绑定到此资源的单词，可以在创建资源时直接绑定，也可以稍后修改。'
        }),
        ('文件信息', {
            'fields': ('file_size', 'file_extension'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_urls(self):
        """自定义URL配置"""
        urls = super().get_urls()
        custom_urls = [
            path('bind-to-words/', self.admin_site.admin_view(self.bind_to_words_view), name='words_wordresource_bind_to_words'),
            path('batch-import/', self.admin_site.admin_view(self.batch_import_view), name='words_wordresource_batch_import'),
        ]
        return custom_urls + urls
    
    def file_display(self, obj):
        """文件显示"""
        if obj.file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.file.name)
        return '-'
    
    def url_display(self, obj):
        """URL显示"""
        if obj.url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url[:50] + '...' if len(obj.url) > 50 else obj.url)
        return '-'
    
    def bound_words_count(self, obj):
        """绑定单词数量"""
        count = obj.words.count()
        if count > 0:
            url = reverse('admin:words_word_changelist') + f'?resources__id__exact={obj.pk}'
            return format_html('<a href="{}">{} 个单词</a>', url, count)
        return '0 个单词'
    
    def bind_to_words_action(self, request, queryset):
        """批量绑定到单词的动作"""
        selected = queryset.values_list('pk', flat=True)
        selected_ids = ','.join(str(pk) for pk in selected)
        from django.shortcuts import redirect
        return redirect(f'/admin/words/wordresource/bind-to-words/?ids={selected_ids}')
    
    def bind_to_words_view(self, request):
        """绑定到单词的视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.http import JsonResponse
        
        # 获取选中的资源ID
        ids = request.GET.get('ids', '')
        if not ids:
            messages.error(request, '没有选中任何资源')
            return redirect('admin:words_wordresource_changelist')
        
        try:
            resource_ids = [int(id_str) for id_str in ids.split(',') if id_str.strip()]
        except ValueError:
            messages.error(request, '无效的资源ID')
            return redirect('admin:words_wordresource_changelist')
        
        queryset = WordResource.objects.filter(pk__in=resource_ids)
        if not queryset.exists():
            messages.error(request, '没有找到指定的资源')
            return redirect('admin:words_wordresource_changelist')
        
        if request.method == 'POST':
            word_ids = request.POST.getlist('words')
            if not word_ids:
                messages.error(request, '请选择要绑定的单词')
            else:
                try:
                    words = Word.objects.filter(pk__in=word_ids)
                    bound_count = 0
                    for resource in queryset:
                        for word in words:
                            if not word.resources.filter(pk=resource.pk).exists():
                                word.resources.add(resource)
                                bound_count += 1
                    
                    messages.success(request, f'成功绑定了 {bound_count} 个单词-资源关联')
                    return redirect('admin:words_wordresource_changelist')
                except Exception as e:
                    messages.error(request, f'绑定失败：{str(e)}')
        
        # 获取所有单词用于选择
        words = Word.objects.all().order_by('word')[:1000]  # 限制数量避免页面过大
        
        return render(request, 'admin/words/wordresource/bind_to_words.html', {
            'title': '绑定资源到单词',
            'queryset': queryset,
            'words': words,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })
    
    def batch_import_view(self, request):
        """批量导入视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        import csv
        import io
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, '请选择CSV文件')
                return render(request, 'admin/words/wordresource/batch_import.html', {
                    'title': '批量导入单词配套资源'
                })
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, '请上传CSV格式的文件')
                return render(request, 'admin/words/wordresource/batch_import.html', {
                    'title': '批量导入单词配套资源'
                })
            
            try:
                # 读取CSV文件
                file_data = csv_file.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(file_data))
                
                success_count = 0
                error_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # 验证必需字段
                        if not row.get('name', '').strip():
                            errors.append(f'第{row_num}行：资源名称不能为空')
                            error_count += 1
                            continue
                        
                        # 创建资源
                        resource = WordResource(
                            name=row['name'].strip(),
                            resource_type=row.get('resource_type', 'text').strip() or 'text',
                            description=row.get('description', '').strip(),
                            url=row.get('url', '').strip() or None
                        )
                        
                        # 验证资源类型
                        from .models import RESOURCE_TYPE_CHOICES
                        valid_types = [choice[0] for choice in RESOURCE_TYPE_CHOICES]
                        if resource.resource_type not in valid_types:
                            resource.resource_type = 'text'
                        
                        resource.full_clean()
                        resource.save()
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f'第{row_num}行：{str(e)}')
                        error_count += 1
                
                # 显示结果
                if success_count > 0:
                    messages.success(request, f'成功导入 {success_count} 个资源')
                
                if error_count > 0:
                    error_msg = f'导入失败 {error_count} 个资源：\n' + '\n'.join(errors[:10])
                    if len(errors) > 10:
                        error_msg += f'\n... 还有 {len(errors) - 10} 个错误'
                    messages.error(request, error_msg)
                
                if success_count > 0:
                    return redirect('admin:words_wordresource_changelist')
                    
            except Exception as e:
                messages.error(request, f'文件处理失败：{str(e)}')
        
        return render(request, 'admin/words/wordresource/batch_import.html', {
            'title': '批量导入单词配套资源'
        })
    
    # 设置显示名称
    file_display.short_description = '文件'  # type: ignore
    url_display.short_description = '网络链接'  # type: ignore
    bound_words_count.short_description = '绑定单词'  # type: ignore
    bind_to_words_action.short_description = '绑定选中的资源到单词'  # type: ignore


class WordAdminForm(forms.ModelForm):
    """Word管理表单"""
    
    class Meta:
        model = Word
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加绑定资源字段
        self.fields['bind_resources'] = forms.ModelMultipleChoiceField(
            queryset=WordResource.objects.all().order_by('name'),
            widget=FilteredSelectMultiple('资源', False),
            required=False,
            label='绑定资源',
            help_text='选择要绑定到此单词的资源（可选）'
        )
        
        if self.instance.pk:
            # 编辑时显示已绑定的资源
            self.fields['bind_resources'].initial = self.instance.resources.all()
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            # 保存绑定的资源
            bind_resources = self.cleaned_data.get('bind_resources')
            if bind_resources is not None:
                instance.resources.set(bind_resources)
        return instance


@admin.register(Word)
class WordAdmin(DynamicPaginationMixin, admin.ModelAdmin):
    """单词管理"""
    form = WordAdminForm
    list_display = [
        'word', 'vocabulary_list', 'phonetic', 'part_of_speech', 
        'textbook_version', 'grade', 'version_status', 'has_multiple_versions',
        'created_at'
    ]
    list_filter = [
        'vocabulary_list', 'textbook_version', 'grade',
        WordLengthFilter, FirstLetterFilter, 'part_of_speech', 
        'has_multiple_versions', 'version_number', 'created_at'
    ]
    search_fields = ['word', 'definition', 'example', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'learned_at']
    # 移除filter_horizontal，因为我们使用自定义表单字段
    
    # 动态分页大小
    list_per_page = 20  # 默认每页显示20条
    
    fieldsets = (
        ('基本信息', {
            'fields': ('word', 'phonetic', 'definition', 'part_of_speech')
        }),
        ('学习内容', {
            'fields': ('example', 'note', 'tags')
        }),
        ('来源信息', {
            'fields': ('vocabulary_list', 'textbook_version', 'grade')
        }),
        ('学习状态', {
            'fields': ('learned_at', 'mastery_level', 'difficulty_level')
        }),
        ('资源绑定', {
            'fields': ('bind_resources',),
            'description': '选择要绑定到此单词的资源，可以在创建单词时直接绑定，也可以稍后修改。'
        }),
        ('版本管理', {
            'fields': ('version_number', 'has_multiple_versions', 'parent_word', 'version_data'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_urls(self):
        """自定义URL配置"""
        urls = super().get_urls()
        custom_urls = [
            path('add-to-word-set/', self.admin_site.admin_view(self.add_to_word_set_view), name='words_word_add_to_word_set'),
            path('batch-import/', self.admin_site.admin_view(self.batch_import_view), name='words_word_batch_import'),
            path('version-management/', self.admin_site.admin_view(self.version_management_view), name='words_word_version_management'),
            path('word-circle-generator/', self.admin_site.admin_view(self.word_circle_generator_view), name='words_word_circle_generator'),
        ]
        return custom_urls + urls
    
    def add_to_word_set_action(self, request, queryset):
        """批量添加到单词集的动作"""
        selected = queryset.values_list('pk', flat=True)
        selected_ids = ','.join(str(pk) for pk in selected)
        from django.shortcuts import redirect
        return redirect(f'/admin/words/word/add-to-word-set/?ids={selected_ids}')
    
    add_to_word_set_action.short_description = '添加选中的单词到单词集'  # type: ignore
    
    def add_to_word_set_view(self, request):
        """添加到单词集的视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.http import JsonResponse
        
        # 获取选中的单词ID
        ids = request.GET.get('ids', '')
        if not ids:
            messages.error(request, '没有选中任何单词')
            return redirect('admin:words_word_changelist')
        
        try:
            word_ids = [int(id_str) for id_str in ids.split(',') if id_str.strip()]
        except ValueError:
            messages.error(request, '无效的单词ID')
            return redirect('admin:words_word_changelist')
        
        queryset = Word.objects.filter(pk__in=word_ids)
        if not queryset.exists():
            messages.error(request, '没有找到指定的单词')
            return redirect('admin:words_word_changelist')
        
        if request.method == 'POST':
            word_set_id = request.POST.get('word_set')
            create_new = request.POST.get('create_new_wordset')
            new_wordset_name = request.POST.get('new_wordset_name', '').strip()
            
            if create_new and new_wordset_name:
                # 创建新单词集
                if WordSet.objects.filter(name=new_wordset_name, created_by=request.user).exists():
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': '您已经有同名的单词集了'})
                    messages.error(request, '您已经有同名的单词集了')
                    return render(request, 'admin/words/word/add_to_word_set.html', {
                        'title': '添加到单词集',
                        'queryset': queryset,
                        'word_sets': WordSet.objects.filter(created_by=request.user),
                        'action_checkbox_name': ACTION_CHECKBOX_NAME,
                    })
                
                try:
                    word_set = WordSet.objects.create(
                        name=new_wordset_name,
                        created_by=request.user
                    )
                    word_set_id = word_set.pk
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': f'创建单词集失败：{str(e)}'})
                    messages.error(request, f'创建单词集失败：{str(e)}')
                    return render(request, 'admin/words/word/add_to_word_set.html', {
                        'title': '添加到单词集',
                        'queryset': queryset,
                        'word_sets': WordSet.objects.filter(created_by=request.user),
                        'action_checkbox_name': ACTION_CHECKBOX_NAME,
                    })
            
            if not word_set_id:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': '请选择一个单词集或创建新的单词集'})
                messages.error(request, '请选择一个单词集或创建新的单词集')
                return render(request, 'admin/words/word/add_to_word_set.html', {
                    'title': '添加到单词集',
                    'queryset': queryset,
                    'word_sets': WordSet.objects.filter(created_by=request.user),
                    'action_checkbox_name': ACTION_CHECKBOX_NAME,
                })
            
            try:
                word_set = WordSet.objects.get(pk=word_set_id, created_by=request.user)
            except WordSet.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': '单词集不存在或您没有权限访问'})
                messages.error(request, '单词集不存在或您没有权限访问')
                return redirect('admin:words_word_changelist')
            
            # 添加单词到单词集
            added_count = 0
            for word in queryset:
                if not word_set.words.filter(pk=word.pk).exists():
                    word_set.words.add(word)
                    added_count += 1
            
            # 更新单词集的单词数量
            word_set.word_count = word_set.words.count()
            word_set.save(update_fields=['word_count'])
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'成功添加 {added_count} 个单词到单词集 "{word_set.name}"',
                    'added_count': added_count,
                    'total_count': queryset.count()
                })
            
            messages.success(request, f'成功添加 {added_count} 个单词到单词集 "{word_set.name}"')
            return redirect('admin:words_word_changelist')
        
        # GET请求，显示表单
        context = {
            'title': '添加到单词集',
            'queryset': queryset,
            'word_sets': WordSet.objects.filter(created_by=request.user).order_by('name'),
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        }
        return render(request, 'admin/words/word/add_to_word_set.html', context)
    

    
    def version_management_view(self, request):
        """单词版本管理视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.http import JsonResponse
        
        if request.method == 'POST':
            action = request.POST.get('action')
            word_id = request.POST.get('word_id')
            version_number = request.POST.get('version_number')
            
            if not action or not word_id:
                return JsonResponse({'success': False, 'error': '缺少必要参数'})
            
            try:
                word = Word.objects.get(pk=word_id)
            except Word.DoesNotExist:
                return JsonResponse({'success': False, 'error': '单词不存在'})
            
            if action == 'delete_version':
                if not version_number:
                    return JsonResponse({'success': False, 'error': '缺少版本号'})
                
                if word.is_main_word():
                    success = word.delete_version(int(version_number))
                    if success:
                        return JsonResponse({
                            'success': True,
                            'message': f'已删除单词 "{word.word}" 的版本 {version_number}'
                        })
                    else:
                        return JsonResponse({'success': False, 'error': f'未找到版本 {version_number}'})
                else:
                    return JsonResponse({'success': False, 'error': '只有主单词可以删除版本'})
            
            elif action == 'create_version':
                # 创建新版本
                new_version = word.create_version()
                return JsonResponse({
                    'success': True,
                    'message': f'已创建单词 "{word.word}" 的版本 {new_version.version_number}',
                    'version_id': new_version.pk
                })
            
            else:
                return JsonResponse({'success': False, 'error': '无效的操作类型'})
        
        # GET请求，显示版本管理页面
        # 获取所有有多版本的单词
        words_with_versions = Word.objects.filter(has_multiple_versions=True).order_by('word')
        
        context = {
            'title': '单词版本管理',
            'words_with_versions': words_with_versions,
            'opts': self.model._meta,
        }
        return render(request, 'admin/words/word/version_management.html', context)
    
    def batch_import_view(self, request):
        """批量导入单词视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.http import JsonResponse
        import csv
        import io
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            list_name = request.POST.get('list_name', '').strip()
            source_name = request.POST.get('source_name', '').strip()
            
            if not csv_file:
                messages.error(request, '请选择CSV文件')
                return render(request, 'admin/words/word/batch_import.html', {
                    'title': '批量导入单词',
                    'opts': self.model._meta,
                })
            
            if not list_name:
                messages.error(request, '请输入词库列表名称')
                return render(request, 'admin/words/word/batch_import.html', {
                    'title': '批量导入单词',
                    'opts': self.model._meta,
                })
            
            try:
                # 创建或获取词库来源
                vocabulary_source = None
                if source_name:
                    vocabulary_source, created = VocabularySource.objects.get_or_create(
                        name=source_name,
                        defaults={'description': f'通过批量导入创建的词库来源: {source_name}'}
                    )
                
                # 创建或获取词库列表
                vocabulary_list, created = VocabularyList.objects.get_or_create(
                    name=list_name,
                    defaults={
                        'source': vocabulary_source,
                        'description': f'通过批量导入创建的词库列表: {list_name}',
                        'is_active': True
                    }
                )
                
                # 读取CSV文件
                file_data = csv_file.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(file_data))
                
                imported_count = 0
                error_count = 0
                
                for row_num, row in enumerate(csv_reader, start=2):  # 从第2行开始（第1行是标题）
                    try:
                        word_text = row.get('word', '').strip()
                        if not word_text:
                            continue
                        
                        # 准备单词数据
                        word_data = {
                            'word': word_text,
                            'phonetic': row.get('phonetic', '').strip(),
                            'definition': row.get('definition', '').strip(),
                            'part_of_speech': row.get('part_of_speech', '').strip(),
                            'example': row.get('example', '').strip(),
                            'note': row.get('note', '').strip(),
                            'textbook_version': row.get('textbook_version', '').strip(),
                            'grade': row.get('grade', '').strip(),
                            'vocabulary_list': vocabulary_list,
                        }
                        
                        # 查找已存在的同名单词
                        existing_words = Word.objects.filter(word=word_text).order_by('created_at')
                        
                        if existing_words.exists():
                            # 获取最早创建的单词作为主单词
                            parent_word = existing_words.first()
                            
                            # 检查是否完全相同
                            temp_word = Word(**word_data)
                            if temp_word.is_identical_to(parent_word):
                                # 完全相同，跳过导入
                                continue
                            
                            # 检查是否有差异，视为不同版本
                            if temp_word.has_differences_from(parent_word):
                                # 有差异，创建新版本
                                word_data['parent_word'] = parent_word
                                if parent_word and hasattr(parent_word, 'get_next_version_number'):
                                    word_data['version_number'] = parent_word.get_next_version_number()
                                else:
                                    word_data['version_number'] = 2
                                word_data['has_multiple_versions'] = False
                                
                                # 更新主单词的多版本标记
                                if parent_word and hasattr(parent_word, 'has_multiple_versions'):
                                    parent_word.has_multiple_versions = True
                                    if hasattr(parent_word, 'save'):
                                        parent_word.save(update_fields=['has_multiple_versions'])
                                
                                # 记录版本信息
                                word_data['version_data'] = {
                                    'parent_word_id': parent_word.pk if parent_word and hasattr(parent_word, 'pk') else None,
                                    'differences': temp_word.get_differences_from(parent_word),
                                    'created_as_version': True,
                                    'import_timestamp': timezone.now().isoformat()
                                }
                            else:
                                # 无显著差异，但仍保存为版本
                                word_data['parent_word'] = parent_word
                                if parent_word and hasattr(parent_word, 'get_next_version_number'):
                                    word_data['version_number'] = parent_word.get_next_version_number()
                                else:
                                    word_data['version_number'] = 2
                                word_data['has_multiple_versions'] = False
                                
                                # 更新主单词的多版本标记
                                if parent_word and hasattr(parent_word, 'has_multiple_versions'):
                                    parent_word.has_multiple_versions = True
                                    if hasattr(parent_word, 'save'):
                                        parent_word.save(update_fields=['has_multiple_versions'])
                                
                                word_data['version_data'] = {
                                    'parent_word_id': parent_word.pk if parent_word and hasattr(parent_word, 'pk') else None,
                                    'duplicate_import': True,
                                    'import_timestamp': timezone.now().isoformat()
                                }
                        
                        # 创建新单词
                        Word.objects.create(**word_data)
                        imported_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        print(f"导入第 {row_num} 行时出错: {e}")
                        continue
                
                # 更新词库列表的单词数量
                vocabulary_list.update_word_count()
                
                # 显示导入结果
                result_message = f'导入完成！新增单词: {imported_count} 个'
                if error_count > 0:
                    result_message += f'，错误: {error_count} 个'
                
                messages.success(request, result_message)
                return redirect('admin:words_word_changelist')
                
            except Exception as e:
                messages.error(request, f'导入失败: {str(e)}')
                return render(request, 'admin/words/word/batch_import.html', {
                    'title': '批量导入单词',
                    'opts': self.model._meta,
                })
        
        # GET请求，显示导入表单
        return render(request, 'admin/words/word/batch_import.html', {
            'title': '批量导入单词',
            'opts': self.model._meta,
        })
    
    def word_circle_generator_view(self, request):
        """单词环生成器视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.http import JsonResponse
        import json
        import os
        from django.conf import settings
        
        # 默认单词列表（15个单词）
        default_words = [
            'apple', 'banana', 'cat', 'dog', 'elephant',
            'flower', 'guitar', 'house', 'ice', 'jungle',
            'kite', 'lion', 'mountain', 'nature', 'ocean'
        ]
        
        # 获取图集列表
        # 优先使用STATICFILES_DIRS，如果不存在则使用STATIC_ROOT
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            static_base = settings.STATICFILES_DIRS[0]
        elif hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            static_base = settings.STATIC_ROOT
        else:
            # 默认使用项目根目录下的static
            static_base = os.path.join(settings.BASE_DIR, 'static')
        
        image_gallery_path = os.path.join(static_base, 'images', 'word_circle_gallery')
        if not os.path.exists(image_gallery_path):
            os.makedirs(image_gallery_path, exist_ok=True)
        
        # 扫描图集目录
        gallery_images = []
        if os.path.exists(image_gallery_path):
            for filename in os.listdir(image_gallery_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    gallery_images.append({
                        'filename': filename,
                        'url': f'/static/images/word_circle_gallery/{filename}'
                    })
        
        # 按文件名排序
        gallery_images.sort(key=lambda x: x['filename'])
        
        if request.method == 'POST':
            # 处理JSON请求
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    # 保存单词环配置
                    if 'words' in data and 'image' in data:
                        # 这里可以保存到数据库或文件
                        return JsonResponse({'success': True, 'message': '配置已保存'})
                    else:
                        return JsonResponse({'success': False, 'error': '配置数据不完整'})
                except json.JSONDecodeError:
                    return JsonResponse({'success': False, 'error': '配置数据格式错误'})
            
            # 处理表单请求
            action = request.POST.get('action')
            
            if action == 'generate_circle':
                # 生成单词环
                words_input = request.POST.get('words', '').strip()
                center_image = request.POST.get('center_image', '')
                
                if words_input:
                    words = [word.strip() for word in words_input.split(',') if word.strip()]
                else:
                    words = default_words
                
                # 计算单词环位置
                import math
                circle_data = []
                total_words = len(words)
                
                for i, word in enumerate(words):
                    angle = (2 * math.pi * i) / total_words
                    x = 50 + 35 * math.cos(angle)  # 中心点(50%, 50%)，半径35%
                    y = 50 + 35 * math.sin(angle)
                    
                    circle_data.append({
                        'word': word,
                        'x': round(x, 2),
                        'y': round(y, 2),
                        'angle': round(math.degrees(angle), 2)
                    })
                
                return JsonResponse({
                    'success': True,
                    'circle_data': circle_data,
                    'center_image': center_image,
                    'total_words': total_words
                })
            
            elif action == 'save_circle':
                # 保存单词环配置
                circle_config = request.POST.get('circle_config')
                if circle_config:
                    try:
                        config_data = json.loads(circle_config)
                        # 这里可以保存到数据库或文件
                        messages.success(request, '单词环配置已保存！')
                        return JsonResponse({'success': True, 'message': '配置已保存'})
                    except json.JSONDecodeError:
                        return JsonResponse({'success': False, 'error': '配置数据格式错误'})
                
                return JsonResponse({'success': False, 'error': '没有配置数据'})
        
        # GET请求，显示单词环生成器页面
        context = {
            'title': '单词环生成器',
            'default_words': default_words,
            'gallery_images': json.dumps(gallery_images),  # 转换为JSON字符串
            'opts': self.model._meta,
        }
        return render(request, 'admin/words/word/word_circle_generator.html', context)
    
    def tag_list(self, obj):
        """标签列表"""
        return ', '.join(obj.tag_list)
    

    
    def version_status(self, obj):
        """版本状态显示"""
        if not obj:
            return format_html('<span style="color: #999;">-</span>')
        
        if obj.is_version():
            return format_html('<span style="color: #6c757d;">版本 {}</span>', obj.version_number)
        elif obj.has_multiple_versions:
            version_count = obj.get_version_count()
            return format_html('<span style="color: #007cba; font-weight: bold;">主单词 ({} 个版本)</span>', version_count)
        else:
            return format_html('<span style="color: #28a745;">单版本</span>')
    
    # 设置显示名称
    tag_list.short_description = '标签列表'  # type: ignore
    version_status.short_description = '版本状态'  # type: ignore


@admin.register(VocabularySource)
class VocabularySourceAdmin(admin.ModelAdmin):
    """词库来源管理"""
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(VocabularyList)
class VocabularyListAdmin(DynamicPaginationMixin, admin.ModelAdmin):
    """词库列表管理"""
    list_display = [
        'name', 'source', 'is_active', 'word_count', 'created_at'
    ]
    list_filter = ['is_active', 'source', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['word_count', 'created_at']
    change_list_template = 'admin/words/vocabularylist/change_list.html'
    
    # 动态分页大小
    list_per_page = 20  # 默认每页显示20条
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'source', 'description')
        }),
        ('状态信息', {
            'fields': ('is_active', 'word_count')
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_urls(self):
        """自定义URL配置"""
        urls = super().get_urls()
        custom_urls = [
            path('batch-import/', self.admin_site.admin_view(self.batch_import_view), name='words_vocabularylist_batch_import'),
        ]
        return custom_urls + urls
    
    def batch_import_view(self, request):
        """批量导入词库列表视图"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        import csv
        import io
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, '请选择CSV文件')
                return render(request, 'admin/words/vocabularylist/batch_import.html', {
                    'title': '批量导入词库列表',
                    'opts': self.model._meta,
                })
            
            try:
                # 读取CSV文件
                file_data = csv_file.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(file_data))
                
                imported_count = 0
                error_count = 0
                
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        name = row.get('name', '').strip()
                        if not name:
                            continue
                        
                        # 检查是否已存在
                        if VocabularyList.objects.filter(name=name).exists():
                            continue
                        
                        # 创建或获取词库来源
                        source_name = row.get('source', '').strip()
                        vocabulary_source = None
                        if source_name:
                            vocabulary_source, created = VocabularySource.objects.get_or_create(
                                name=source_name,
                                defaults={'description': f'通过批量导入创建: {source_name}'}
                            )
                        
                        # 创建词库列表
                        VocabularyList.objects.create(
                            name=name,
                            source=vocabulary_source,
                            description=row.get('description', '').strip(),
                            is_active=row.get('is_active', 'true').lower() in ['true', '1', 'yes']
                        )
                        imported_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        print(f"导入第 {row_num} 行时出错: {e}")
                        continue
                
                # 显示导入结果
                result_message = f'导入完成！新增词库列表: {imported_count} 个'
                if error_count > 0:
                    result_message += f'，错误: {error_count} 个'
                
                messages.success(request, result_message)
                return redirect('admin:words_vocabularylist_changelist')
                
            except Exception as e:
                messages.error(request, f'导入失败: {str(e)}')
                return render(request, 'admin/words/vocabularylist/batch_import.html', {
                    'title': '批量导入词库列表',
                    'opts': self.model._meta,
                })
        
        # GET请求，显示导入表单
        return render(request, 'admin/words/vocabularylist/batch_import.html', {
            'title': '批量导入词库列表',
            'opts': self.model._meta,
        })
    
    def save_model(self, request, obj, form, change):
        """保存模型"""
        super().save_model(request, obj, form, change)
        # 更新单词数量
        obj.update_word_count()


# StudySession 和 UserStreak 管理已移动到 vocabulary_manager 应用





class WordGradeLevelInline(admin.TabularInline):
    """单词分级等级内联"""
    model = WordGradeLevel
    extra = 1
    fields = ['level', 'name', 'description', 'word_set', 'min_difficulty', 'max_difficulty']


@admin.register(WordGrader)
class WordGraderAdmin(admin.ModelAdmin):
    """单词分级器管理"""
    list_display = ['name', 'grade_count', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WordGradeLevelInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'grade_count')
        }),
        ('设置', {
            'fields': ('created_by', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """保存模型"""
        if not change:  # 创建新对象
            if not obj.created_by:
                obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(WordGradeLevel)
class WordGradeLevelAdmin(admin.ModelAdmin):
    """单词分级等级管理"""
    list_display = ['grader', 'level', 'name', 'word_set', 'min_difficulty', 'max_difficulty', 'created_at']
    list_filter = ['grader', 'level', 'min_difficulty', 'max_difficulty']
    search_fields = ['name', 'description', 'grader__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('分级信息', {
            'fields': ('grader', 'level', 'name', 'description')
        }),
        ('单词集绑定', {
            'fields': ('word_set',)
        }),
        ('难度范围', {
            'fields': ('min_difficulty', 'max_difficulty')
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )