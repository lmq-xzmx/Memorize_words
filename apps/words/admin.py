from django.contrib import admin
from django.contrib.admin import helpers
from django.utils.html import format_html
from django.db.models import Count
from django.db import transaction
from typing import Any, Optional
from .models import Word, VocabularyList, VocabularySource, WordSet, WordResource, WordGrader, WordGradeLevel


from .base_admin import BaseBatchImportAdmin

@admin.register(Word)
class WordAdmin(BaseBatchImportAdmin):
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
                    with transaction.atomic():  # type: ignore  # type: ignore
                        # 获取选中单词的详细信息用于描述
                        word_list = list(queryset.values_list('word', flat=True)[:10])  # 取前10个单词作为示例
                        word_preview = ', '.join(word_list)
                        if queryset.count() > 10:
                            word_preview += f' 等{queryset.count()}个单词'
                        
                        # 创建完整的单词集
                        word_set = WordSet.objects.create(  # type: ignore
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
                    word_set = WordSet.objects.get(id=word_set_id)  # type: ignore
                    existing_count = word_set.words.count()
                    word_set.words.add(*queryset)
                    new_count = word_set.words.count()
                    added_count = new_count - existing_count
                    
                    if added_count > 0:
                        messages.success(request, f'成功向单词集 "{word_set.name}" 添加了 {added_count} 个新单词')
                    else:
                        messages.info(request, '所选单词已存在于该单词集中')
                    
                    return redirect('admin:words_word_changelist')
                except WordSet.DoesNotExist:  # type: ignore
                    messages.error(request, '选择的单词集不存在')
                    return redirect('admin:words_word_changelist')
                except Exception as e:
                    messages.error(request, f'添加到单词集失败：{str(e)}')
                    return redirect('admin:words_word_changelist')
            else:
                messages.error(request, '请选择一个单词集或创建新的单词集')
        
        # GET请求显示选择页面
        word_sets = WordSet.objects.filter(created_by=request.user).order_by('-created_at')  # type: ignore
        
        context = {
            'title': '添加单词到单词集',
            'queryset': queryset,
            'word_sets': word_sets,
            'opts': self.model._meta,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }
        
        return render(request, 'admin/words/word/add_to_word_set.html', context)
    
    def get_urls(self):
        """添加自定义URL"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('batch_import/', self.admin_site.admin_view(self.batch_import_view), name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_batch_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """重写changelist视图以添加批量导入按钮"""
        extra_context = extra_context or {}
        extra_context['show_batch_import'] = True
        extra_context['batch_import_url'] = 'admin:words_word_batch_import'
        return super().changelist_view(request, extra_context=extra_context)
    
    def batch_import_view(self, request, *args, **kwargs):
        """批量导入单词视图"""
        return self.process_batch_import(request)

    def perform_import(self, request, reader):
        """执行单词导入"""
        from django.contrib import messages
        from .models import VocabularyList, Word
        created_count = 0
        error_count = 0
        for row_num, row in enumerate(reader, 1):
            try:
                vocabulary_list_name = row.get('vocabulary_list_name', '').strip()
                if not vocabulary_list_name:
                    messages.warning(request, f'第{row_num}行缺少词库列表名称，已跳过。')
                    error_count += 1
                    continue

                vocabulary_list, _ = VocabularyList.objects.get_or_create(name=vocabulary_list_name)  # type: ignore
                
                word_data = {
                    'word': row.get('word', '').strip(),
                    'phonetic': row.get('phonetic', '').strip(),
                    'definition': row.get('definition', '').strip(),
                    'part_of_speech': row.get('part_of_speech', '').strip(),
                    'example': row.get('example', '').strip(),
                    'note': row.get('note', '').strip(),
                    'vocabulary_list': vocabulary_list,
                }
                
                if not word_data['word']:
                    messages.warning(request, f'第{row_num}行缺少单词，已跳过。')
                    error_count += 1
                    continue

                Word.objects.create(**word_data)  # type: ignore
                created_count += 1

            except Exception as e:
                messages.warning(request, f'第{row_num}行处理失败：{str(e)}')
                error_count += 1
        
        if created_count > 0:
            messages.success(request, f'成功导入 {created_count} 个单词。')
        if error_count > 0:
            messages.warning(request, f'有 {error_count} 行数据导入失败。')
    

    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request)


@admin.register(WordGrader)
class WordGraderAdmin(admin.ModelAdmin):
    """单词分级器管理"""
    list_display = [
        'name', 'grade_count', 'total_levels_display', 'created_by', 
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('分级设置', {
            'fields': ('grade_count', 'is_active')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='实际等级数')
    def total_levels_display(self, obj):
        """显示实际等级数量"""
        count = obj.get_total_levels()
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            'green' if count == obj.grade_count else 'orange',
            count,
            obj.grade_count
        )
    
    def save_model(self, request, obj, form, change):
        """保存模型"""
        if not change:  # 创建新对象
            if not obj.created_by:
                obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('created_by').prefetch_related('grade_levels')


@admin.register(WordGradeLevel)
class WordGradeLevelAdmin(admin.ModelAdmin):
    """单词分级等级管理"""
    list_display = [
        'grader', 'level', 'name', 'word_count_display', 
        'difficulty_range_display', 'created_at'
    ]
    list_filter = ['grader', 'level', 'created_at']
    search_fields = ['name', 'description', 'grader__name']
    readonly_fields = ['created_at']
    ordering = ['grader', 'level']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('grader', 'level', 'name', 'description')
        }),
        ('单词设置', {
            'fields': ('word_set',)
        }),
        ('难度范围', {
            'fields': ('min_difficulty', 'max_difficulty')
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='单词数量')
    def word_count_display(self, obj):
        """显示单词数量"""
        if obj.word_set:
            count = obj.word_set.words.count()
            return format_html(
                '<span style="color: {};">{} 个单词</span>',
                'green' if count > 0 else 'gray',
                count
            )
        return format_html('<span style="color: gray;">未绑定单词集</span>')
    
    @admin.display(description='难度范围')
    def difficulty_range_display(self, obj):
        """显示难度范围"""
        return format_html(
            '<span class="badge">{} - {}</span>',
            obj.min_difficulty,
            obj.max_difficulty
        )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('grader', 'word_set').prefetch_related('word_set__words')


@admin.register(VocabularyList)
class VocabularyListAdmin(BaseBatchImportAdmin):
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
            path('batch_import/', self.admin_site.admin_view(self.batch_import_view), name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_batch_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """重写changelist视图以添加批量导入按钮"""
        extra_context = extra_context or {}
        extra_context['show_batch_import'] = True
        extra_context['batch_import_url'] = 'admin:words_vocabularylist_batch_import'
        return super().changelist_view(request, extra_context=extra_context)
    
    def batch_import_view(self, request, *args, **kwargs):
        """批量导入单词到词库列表（支持去重和版本管理）"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.db import transaction
        from django.core.exceptions import ValidationError
        from django.contrib.admin.views.decorators import staff_member_required
        import csv
        import io
        
        # 检查权限
        if not self.has_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            vocabulary_list_id = request.POST.get('vocabulary_list')
            enable_versioning = request.POST.get('enable_versioning') == 'on'
            conflict_resolution = request.POST.get('conflict_resolution', 'create_version')
            batch_size = int(request.POST.get('batch_size', 100))
            
            if not csv_file:
                messages.error(request, '请选择CSV文件')
                return redirect('.')
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, '请上传CSV格式文件')
                return redirect('.')
            
            if not vocabulary_list_id:
                messages.error(request, '请选择目标词库列表')
                return redirect('.')
            
            # 验证批次大小
            if batch_size < 10 or batch_size > 1000:
                messages.error(request, '批次大小必须在10-1000之间')
                return redirect('.')
            
            try:
                vocabulary_list = VocabularyList.objects.get(id=vocabulary_list_id)  # type: ignore
            except VocabularyList.DoesNotExist:  # type: ignore
                messages.error(request, '选择的词库列表不存在')
                return redirect('.')
            
            try:
                # 读取CSV文件
                file_data = csv_file.read().decode('utf-8-sig')  # 支持BOM
                csv_reader = csv.DictReader(io.StringIO(file_data))
                
                created_count = 0
                updated_count = 0
                version_count = 0
                skipped_count = 0
                error_count = 0
                duplicate_count = 0
                
                with transaction.atomic():
                    for row_num, row in enumerate(csv_reader, start=2):
                        try:
                            word_text = row.get('word', '').strip()
                            if not word_text:
                                messages.warning(request, f'第{row_num}行：单词不能为空，跳过')
                                error_count += 1
                                continue
                            
                            # 准备单词数据
                            word_data = {
                                'phonetic': row.get('phonetic', '').strip(),
                                'definition': row.get('definition', '').strip(),
                                'part_of_speech': row.get('part_of_speech', '').strip(),
                                'note': row.get('note', '').strip(),
                                'textbook_version': row.get('textbook_version', '').strip(),
                                'grade': row.get('grade', '').strip(),
                                'book_volume': row.get('book_volume', '').strip(),
                                'unit': row.get('unit', '').strip(),
                                'vocabulary_list': vocabulary_list,
                            }
                            
                            # 查找已存在的同名单词
                            existing_words = Word.objects.filter(  # type: ignore
                                word=word_text,
                                vocabulary_list=vocabulary_list
                            ).order_by('created_at')
                            
                            if not existing_words.exists():
                                # 新单词，直接创建
                                new_word = Word(word=word_text, **word_data)
                                if enable_versioning:
                                    # 使用版本管理系统
                                    new_word.save()  # 会自动调用handle_word_versioning
                                else:
                                    # 不使用版本管理，直接保存
                                    new_word.save()
                                created_count += 1
                            else:
                                # 存在同名单词，处理冲突
                                existing_word = existing_words.first()
                                
                                # 创建临时单词对象用于比较
                                temp_word = Word(word=word_text, **word_data)
                                
                                if temp_word.is_identical_to(existing_word):
                                    # 完全相同，跳过
                                    duplicate_count += 1
                                    continue
                                
                                # 根据冲突解决策略处理
                                if conflict_resolution == 'skip':
                                    skipped_count += 1
                                    continue
                                elif conflict_resolution == 'update':
                                    # 更新现有单词
                                    if existing_word:
                                        updated = False
                                        for field, value in word_data.items():
                                            if field != 'vocabulary_list' and value and getattr(existing_word, field) != value:
                                                setattr(existing_word, field, value)
                                                updated = True
                                        
                                        if updated:
                                            existing_word.save()
                                            updated_count += 1
                                elif conflict_resolution == 'create_version' and enable_versioning:
                                    # 创建新版本
                                    try:
                                        new_word = Word(word=word_text, **word_data)
                                        new_word.save()  # 会自动处理版本管理
                                        version_count += 1
                                    except ValidationError as ve:
                                        if "完全相同" in str(ve):
                                            duplicate_count += 1
                                        else:
                                            raise ve
                                else:
                                    # 默认创建版本（使用版本管理）
                                    new_word = Word(word=word_text, **word_data)
                                    new_word.save()
                                    version_count += 1
                                
                        except ValidationError as ve:
                            if "完全相同" in str(ve):
                                duplicate_count += 1
                            else:
                                messages.error(request, f'第{row_num}行处理失败：{str(ve)}')
                                error_count += 1
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
                if version_count > 0:
                    messages.info(request, f'创建了 {version_count} 个版本')
                if duplicate_count > 0:
                    messages.info(request, f'跳过了 {duplicate_count} 个重复单词')
                if skipped_count > 0:
                    messages.info(request, f'跳过了 {skipped_count} 个冲突单词')
                if error_count > 0:
                    messages.warning(request, f'处理失败 {error_count} 行')
                
                return redirect('admin:words_vocabularylist_changelist')
                
            except Exception as e:
                messages.error(request, f'文件处理失败：{str(e)}')
                return redirect('.')
        
        # GET请求显示导入页面
        vocabulary_lists = VocabularyList.objects.filter(is_active=True).order_by('name')  # type: ignore
        context = {
            'title': '批量导入单词',
            'opts': self.model._meta,
            'vocabulary_lists': vocabulary_lists,
        }
        return render(request, 'admin/words/vocabularylist/batch_import.html', context)

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


@admin.register(WordResource)
class WordResourceAdmin(BaseBatchImportAdmin):
    """单词配套资源管理"""
    list_display = [
        'name', 'resource_type', 'file_size_display', 'created_at'
    ]
    list_filter = ['resource_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'file_size']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'resource_type')
        }),
        ('文件信息', {
            'fields': ('file', 'url')
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='文件大小')
    def file_size_display(self, obj):
        """显示文件大小"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f'{obj.file_size} B'
            elif obj.file_size < 1024 * 1024:
                return f'{obj.file_size / 1024:.1f} KB'
            else:
                return f'{obj.file_size / (1024 * 1024):.1f} MB'
        return '-'
    
    def get_urls(self):
        """添加自定义URL"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('batch_import/', self.admin_site.admin_view(self.batch_import_view), name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_batch_import'),
        ]
        return custom_urls + urls
    
    def batch_import_view(self, request, *args, **kwargs):
        """批量导入单词配套资源视图"""
        return self.process_batch_import(request)

    def perform_import(self, request, reader):
        """执行单词配套资源导入"""
        from django.contrib import messages
        from .models import WordResource
        
        created_count = 0
        error_count = 0
        
        for row_num, row in enumerate(reader, 1):
            try:
                name = row.get('name', '').strip()
                url = row.get('url', '').strip()
                resource_type = row.get('resource_type', '').strip()
                
                if not name:
                    messages.warning(request, f'第{row_num}行：资源名称不能为空，已跳过。')
                    error_count += 1
                    continue
                
                if not resource_type:
                    messages.warning(request, f'第{row_num}行：资源类型不能为空，已跳过。')
                    error_count += 1
                    continue
                
                # 创建资源
                resource_data = {
                    'name': name,
                    'description': row.get('description', '').strip(),
                    'resource_type': resource_type,
                }
                
                # 如果是URL类型，添加URL字段
                if resource_type == 'url' and url:
                    resource_data['url'] = url
                
                WordResource.objects.create(**resource_data)  # type: ignore
                created_count += 1
                
            except Exception as e:
                messages.warning(request, f'第{row_num}行处理失败：{str(e)}')
                error_count += 1
        
        if created_count > 0:
            messages.success(request, f'成功导入 {created_count} 个资源。')
        if error_count > 0:
            messages.warning(request, f'有 {error_count} 行数据导入失败。')
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request)