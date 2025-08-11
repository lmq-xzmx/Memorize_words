from django.contrib import admin
from django.contrib.admin import helpers
from django.utils.html import format_html
from django.db.models import Count
from .models import Word, VocabularyList, VocabularySource, WordSet


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """单词管理"""
    list_display = [
        'word', 'phonetic', 'part_of_speech', 'vocabulary_list',
        'difficulty_level', 'mastery_level', 'created_at'
    ]
    list_filter = [
        'part_of_speech', 'difficulty_level', 'mastery_level',
        'vocabulary_list', 'created_at'
    ]
    search_fields = ['word', 'definition', 'example']
    readonly_fields = ['created_at']
    ordering = ['word']
    list_per_page = 50
    actions = ['add_to_word_set']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('word', 'phonetic', 'definition', 'part_of_speech')
        }),
        ('学习内容', {
            'fields': ('example', 'note', 'tags')
        }),
        ('分类信息', {
            'fields': ('vocabulary_list', 'difficulty_level', 'mastery_level')
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.action(description='将选中的单词添加到单词集')
    def add_to_word_set(self, request, queryset):
        """将选中的单词添加到单词集"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.db import transaction
        
        if request.method == 'POST':
            word_set_id = request.POST.get('word_set')
            create_new_wordset = request.POST.get('create_new_wordset')
            new_wordset_name = request.POST.get('new_wordset_name', '').strip()
            
            if create_new_wordset and new_wordset_name:
                # 创建新的单词集（成品状态）
                try:
                    with transaction.atomic():
                        # 获取选中单词的详细信息用于描述
                        word_list = list(queryset.values_list('word', flat=True)[:10])  # 取前10个单词作为示例
                        word_preview = ', '.join(word_list)
                        if queryset.count() > 10:
                            word_preview += f' 等{queryset.count()}个单词'
                        
                        # 创建完整的单词集
                        word_set = WordSet.objects.create(
                            name=new_wordset_name,
                            description=f'包含 {queryset.count()} 个精选单词：{word_preview}。适合学习和练习使用。',
                            created_by=request.user,
                            is_public=True  # 设置为公开，成为可用的成品
                        )
                        
                        # 添加所有选中的单词
                        word_set.words.set(queryset)
                        
                        # 成功消息，引导用户查看创建的单词集
                        word_set_id = word_set.pk  # 使用 pk 属性
                        messages.success(
                            request, 
                            format_html(
                                '成功创建单词集 "{}" 并添加了 {} 个单词。<a href="{}">点击查看</a>',
                                new_wordset_name,
                                queryset.count(),
                                f'/admin/words/wordset/{word_set_id}/change/'
                            )
                        )
                        return redirect('admin:words_wordset_changelist')
                        
                except Exception as e:
                    messages.error(request, f'创建单词集失败：{str(e)}')
                    return redirect('admin:words_word_changelist')
            
            elif word_set_id:
                # 添加到现有单词集
                try:
                    word_set = WordSet.objects.get(id=word_set_id)
                    existing_count = word_set.words.count()
                    word_set.words.add(*queryset)
                    new_count = word_set.words.count()
                    added_count = new_count - existing_count
                    
                    if added_count > 0:
                        messages.success(request, f'成功向单词集 "{word_set.name}" 添加了 {added_count} 个新单词')
                    else:
                        messages.info(request, '所选单词已存在于该单词集中')
                    
                    return redirect('admin:words_word_changelist')
                except WordSet.DoesNotExist:
                    messages.error(request, '选择的单词集不存在')
                    return redirect('admin:words_word_changelist')
                except Exception as e:
                    messages.error(request, f'添加到单词集失败：{str(e)}')
                    return redirect('admin:words_word_changelist')
            else:
                messages.error(request, '请选择一个单词集或创建新的单词集')
        
        # GET请求显示选择页面
        word_sets = WordSet.objects.filter(created_by=request.user).order_by('-created_at')
        
        context = {
            'title': '添加单词到单词集',
            'queryset': queryset,
            'word_sets': word_sets,
            'opts': self.model._meta,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/words/word/add_to_word_set.html', context)
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('vocabulary_list')


@admin.register(VocabularyList)
class VocabularyListAdmin(admin.ModelAdmin):
    """词汇表管理"""
    list_display = [
        'name', 'source', 'word_count_display', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'source', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'source', 'description')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='单词数量')
    def word_count_display(self, obj):
        """显示单词数量"""
        count = obj.words.count() if hasattr(obj, 'words') else 0
        return format_html(
            '<span style="color: {};">{}个单词</span>',
            'green' if count > 0 else 'gray',
            count
        )
    
    def get_urls(self):
        """添加自定义URL"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('batch_import/', self.admin_site.admin_view(self.batch_import_view), name='%s_%s_batch_import' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return custom_urls + urls
    
    def batch_import_view(self, request):
        """批量导入单词到词库列表"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.db import transaction
        import csv
        import io
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            vocabulary_list_id = request.POST.get('vocabulary_list')
            
            if not csv_file:
                messages.error(request, '请选择CSV文件')
                return redirect('.')
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, '请上传CSV格式文件')
                return redirect('.')
            
            if not vocabulary_list_id:
                messages.error(request, '请选择目标词库列表')
                return redirect('.')
            
            try:
                vocabulary_list = VocabularyList.objects.get(id=vocabulary_list_id)
            except VocabularyList.DoesNotExist:
                messages.error(request, '选择的词库列表不存在')
                return redirect('.')
            
            try:
                # 读取CSV文件
                file_data = csv_file.read().decode('utf-8-sig')  # 支持BOM
                csv_reader = csv.DictReader(io.StringIO(file_data))
                
                created_count = 0
                updated_count = 0
                error_count = 0
                
                with transaction.atomic():
                    for row_num, row in enumerate(csv_reader, start=2):
                        try:
                            word_text = row.get('word', '').strip()
                            if not word_text:
                                messages.warning(request, f'第{row_num}行：单词不能为空，跳过')
                                error_count += 1
                                continue
                            
                            # 创建或更新单词
                            word, created = Word.objects.get_or_create(
                                word=word_text,
                                vocabulary_list=vocabulary_list,
                                defaults={
                                    'phonetic': row.get('phonetic', '').strip(),
                                    'definition': row.get('definition', '').strip(),
                                    'part_of_speech': row.get('part_of_speech', '').strip(),
                                    'note': row.get('note', '').strip(),
                                    'textbook_version': row.get('textbook_version', '').strip(),
                                    'grade': row.get('grade', '').strip(),
                                    'book_volume': row.get('book_volume', '').strip(),
                                    'unit': row.get('unit', '').strip(),
                                }
                            )
                            
                            if created:
                                created_count += 1
                            else:
                                # 更新现有单词
                                updated = False
                                for field in ['phonetic', 'definition', 'part_of_speech', 'note', 
                                            'textbook_version', 'grade', 'book_volume', 'unit']:
                                    new_value = row.get(field, '').strip()
                                    if new_value and getattr(word, field) != new_value:
                                        setattr(word, field, new_value)
                                        updated = True
                                
                                if updated:
                                    word.save()
                                    updated_count += 1
                                
                        except Exception as e:
                            messages.error(request, f'第{row_num}行处理失败：{str(e)}')
                            error_count += 1
                
                # 更新词库列表的单词数量
                vocabulary_list.update_word_count()
                
                # 显示结果
                if created_count > 0:
                    messages.success(request, f'成功创建 {created_count} 个单词')
                if updated_count > 0:
                    messages.info(request, f'更新了 {updated_count} 个单词')
                if error_count > 0:
                    messages.warning(request, f'处理失败 {error_count} 行')
                
                return redirect('admin:words_vocabularylist_changelist')
                
            except Exception as e:
                messages.error(request, f'文件处理失败：{str(e)}')
                return redirect('.')
        
        # GET请求显示导入页面
        vocabulary_lists = VocabularyList.objects.filter(is_active=True).order_by('name')
        context = {
            'title': '批量导入单词',
            'opts': self.model._meta,
            'vocabulary_lists': vocabulary_lists,
        }
        return render(request, 'admin/words/vocabularylist/batch_import.html', context)

    def changelist_view(self, request, extra_context=None):
        """自定义changelist视图，添加批量导入按钮"""
        extra_context = extra_context or {}
        extra_context['batch_import_url'] = 'batch_import/'
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('source').prefetch_related('words')


@admin.register(VocabularySource)
class VocabularySourceAdmin(admin.ModelAdmin):
    """词汇来源管理"""
    list_display = ['name', 'description', 'list_count_display', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    ordering = ['name']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='词汇表数量')
    def list_count_display(self, obj):
        """显示词汇表数量"""
        count = obj.vocabulary_lists.count() if hasattr(obj, 'vocabulary_lists') else 0
        return format_html(
            '<span style="color: {};">{}个词汇表</span>',
            'blue' if count > 0 else 'gray',
            count
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).prefetch_related('vocabulary_lists')


@admin.register(WordSet)
class WordSetAdmin(admin.ModelAdmin):
    """单词集管理"""
    list_display = [
        'name', 'description', 'word_count_display', 'created_by', 
        'is_public', 'created_at'
    ]
    list_filter = ['is_public', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['words']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('设置', {
            'fields': ('is_public', 'words')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='单词数量')
    def word_count_display(self, obj):
        """显示单词数量"""
        count = obj.words.count() if hasattr(obj, 'words') else 0
        return format_html(
            '<span style="color: {};">{}个单词</span>',
            'green' if count > 0 else 'gray',
            count
        )
    
    def save_model(self, request, obj, form, change):
        """保存模型"""
        if not change:  # 创建新对象
            if not obj.created_by:
                obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('created_by').prefetch_related('words')