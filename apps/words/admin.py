from django.contrib import admin
from django.contrib.admin import helpers
from django.utils.html import format_html
from django.db.models import Count
from django.db import transaction
from django.utils import timezone
from typing import Any, Optional, Dict, List, Union
from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from massadmin.massadmin import MassEditMixin
from .models import Word, WordEntry, ImportRecord, VocabularyList, VocabularySource, WordSet, WordResource, WordGrader, WordGradeLevel
from utils.admin_mixins import AdminDynamicPaginationMixin
import csv
import uuid
from io import StringIO

from .base_admin import BaseBatchImportAdmin

@admin.register(Word)
class WordAdmin(MassEditMixin, AdminDynamicPaginationMixin, admin.ModelAdmin):
    """单词管理"""
    list_display = [
        'word', 'entry_count_display', 'learned_at', 'created_at'
    ]
    list_filter = [
        'learned_at', 'created_at'
    ]
    search_fields = ['word', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['word']
    list_per_page = 50
    actions = ['add_to_word_set']
    
    # django-mass-edit configuration
    mass_edit_fields = ['tags', 'learned_at']  # 允许批量编辑的字段
    
    fieldsets = (
        ('基本信息', {
            'fields': ('word', 'tags')
        }),
        ('学习状态', {
            'fields': ('learned_at',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='词条数量')
    def entry_count_display(self, obj: Word) -> str:
        """显示词条数量"""
        try:
            # 使用类型注解避免诊断错误
            entries = getattr(obj, 'entries', None)
            count = entries.count() if entries else 0
            return f"{count} 个词条"
        except:
            return "0 个词条"
    
    @admin.action(description='将选中的单词添加到单词集')
    def add_to_word_set(self, request: HttpRequest, queryset: QuerySet[Word]) -> HttpResponse:
        """将选中的单词添加到单词集"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.db import transaction
        from django.utils.html import format_html
        from .models import WordSet

        if 'apply' in request.POST:
            word_set_id = request.POST.get('word_set')
            create_new_wordset = request.POST.get('create_new_wordset')
            new_wordset_name_raw = request.POST.get('new_wordset_name', '')
            new_wordset_name = str(new_wordset_name_raw).strip() if new_wordset_name_raw else ''

            if create_new_wordset and new_wordset_name:
                try:
                    with transaction.atomic():
                        word_list = list(queryset.values_list('word', flat=True)[:10])
                        word_preview = ', '.join(str(word) for word in word_list)
                        if queryset.count() > 10:
                            word_preview += f' 等{queryset.count()}个单词'

                        from .models import WordSet
                        word_set = WordSet.objects.create(
                            name=new_wordset_name,
                            description=f'包含 {queryset.count()} 个精选单词：{word_preview}。适合学习和练习使用。',
                            created_by=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                            is_public=True
                        )
                        word_set.words.set(queryset)
                        word_set_id = word_set.pk
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
                try:
                    from .models import WordSet
                    word_set = WordSet.objects.get(id=word_set_id)
                    existing_count = word_set.words.count()
                    word_set.words.add(*queryset)
                    new_count = word_set.words.count()
                    added_count = new_count - existing_count
                    messages.success(
                        request,
                        format_html(
                            '成功将 {} 个单词添加到单词集 "{}"。<a href="{}">点击查看</a>',
                            added_count,
                            word_set.name,
                            f'/admin/words/wordset/{word_set.id}/change/'
                        )
                    )
                    return redirect('admin:words_word_changelist')
                except WordSet.DoesNotExist:
                    messages.error(request, '选择的单词集不存在。')
                except Exception as e:
                    messages.error(request, f'添加单词失败：{str(e)}')
                    return redirect('admin:words_word_changelist')
            else:
                messages.warning(request, '请选择一个单词集或创建一个新的单词集。')
                return redirect('admin:words_word_changelist')

        word_sets = WordSet.objects.all()
        context = {
            'queryset': queryset,
            'word_sets': word_sets,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return render(request, 'admin/words/word/add_to_word_set_form.html', context)
    
    def perform_import(self, request: HttpRequest, reader: Any) -> None:
        """执行单词导入 - 支持冲突管理和版本控制"""
        from django.contrib import messages
        from .models import VocabularyList, Word, VocabularySource
        import uuid
        from datetime import datetime
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        version_count = 0
        error_count = 0
        
        # 生成导入批次ID
        import_batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # 创建或获取导入来源
        source_name = request.POST.get('import_source_name', '').strip() or f"批量导入_{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        import_source, _ = VocabularySource.objects.get_or_create(
            name=source_name,
            defaults={'description': f'批量导入于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'}
        )
        
        for row_num, row in enumerate(reader, 1):
            try:
                word_text = row.get('word', '').strip()
                if not word_text:
                    messages.warning(request, f'第{row_num}行缺少单词，已跳过。')
                    error_count += 1
                    continue

                # 处理词库列表
                vocabulary_list = None
                vocabulary_list_name = row.get('vocabulary_list_name', '').strip()
                if vocabulary_list_name:
                    vocabulary_list, _ = VocabularyList.objects.get_or_create(
                        name=vocabulary_list_name,
                        defaults={'source': import_source}
                    )
                
                # 构建单词数据
                word_data = {
                    'word': word_text,
                    'phonetic': row.get('phonetic', '').strip(),
                    'definition': row.get('definition', '').strip(),
                    'part_of_speech': row.get('part_of_speech', '').strip(),
                    'example': row.get('example', '').strip(),
                    'note': row.get('note', '').strip(),
                    'vocabulary_list': vocabulary_list,
                    'textbook_version': row.get('textbook_version', '').strip(),
                    'grade': row.get('grade', '').strip(),
                    'book_volume': row.get('book_volume', '').strip(),
                    'unit': row.get('unit', '').strip(),
                    'import_source': import_source,
                    'import_batch_id': import_batch_id,
                    'import_metadata': {
                        'row_number': row_num,
                        'import_time': datetime.now().isoformat(),
                        'source_file': getattr(request.FILES.get('csv_file'), 'name', 'unknown')
                    }
                }
                
                # 处理可选的数字字段
                try:
                    difficulty_level = row.get('difficulty_level', '').strip()
                    if difficulty_level:
                        word_data['difficulty_level'] = int(difficulty_level)
                except (ValueError, TypeError):
                    pass
                
                try:
                    mastery_level = row.get('mastery_level', '').strip()
                    if mastery_level:
                        word_data['mastery_level'] = int(mastery_level)
                except (ValueError, TypeError):
                    pass
                
                # 处理标签
                tags = row.get('tags', '').strip()
                if tags:
                    word_data['tags'] = tags

                # 查找现有单词（仅基于单词文本）
                existing_words = Word.objects.filter(word=word_text)
                
                if existing_words.exists():
                    # 检查是否完全相同（重复数据）
                    identical_word = None
                    for existing in existing_words:
                        temp_word = Word(**word_data)
                        if existing.is_identical_to(temp_word):
                            identical_word = existing
                            break
                    
                    if identical_word:
                        # 重复数据：不重复创建，但保留导入来源信息
                        if not identical_word.import_source:
                            identical_word.import_source = import_source
                            identical_word.import_batch_id = import_batch_id
                            identical_word.save(update_fields=['import_source', 'import_batch_id'])
                        skipped_count += 1
                        continue
                    else:
                        # 新版本：仅单词相同，其他数据有差异
                        main_word = existing_words.filter(parent_word__isnull=True).first()
                        if not main_word:
                            main_word = existing_words.first()
                            main_word.parent_word = None
                            main_word.version_number = 1
                            main_word.has_multiple_versions = True
                            main_word.save()
                        
                        # 创建新版本
                        word_data['parent_word'] = main_word
                        word_data['version_number'] = main_word.get_next_version_number()
                        word_data['has_multiple_versions'] = False
                        
                        new_version = Word.objects.create(**word_data)
                        
                        # 更新主单词的版本状态
                        main_word.has_multiple_versions = True
                        main_word.save(update_fields=['has_multiple_versions'])
                        
                        version_count += 1
                else:
                    # 创建新单词
                    Word.objects.create(**word_data)
                    created_count += 1

            except Exception as e:
                messages.warning(request, f'第{row_num}行处理失败：{str(e)}')
                error_count += 1
        
        # 显示导入结果
        result_messages = []
        if created_count > 0:
            result_messages.append(f'创建 {created_count} 个新单词')
        if version_count > 0:
            result_messages.append(f'创建 {version_count} 个单词版本')
        if skipped_count > 0:
            result_messages.append(f'跳过 {skipped_count} 个重复单词')
        if error_count > 0:
            result_messages.append(f'{error_count} 行导入失败')
        
        if result_messages:
            messages.success(request, f'导入完成：{", ".join(result_messages)}。导入批次ID：{import_batch_id}')
        
        if error_count > 0:
            messages.warning(request, f'有 {error_count} 行数据导入失败，请检查数据格式。')
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Word]:
        """优化查询，预取词条数量避免N+1查询问题"""
        return super().get_queryset(request).select_related().prefetch_related('entries')


@admin.register(VocabularyList)
class VocabularyListAdmin(AdminDynamicPaginationMixin, BaseBatchImportAdmin):
    """词汇表管理 - 支持译林单词表格式导入"""
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
    def word_count_display(self, obj: VocabularyList) -> str:
        """显示单词数量"""
        # 使用类型注解避免诊断错误
        word_entries = getattr(obj, 'word_entries', None)
        count = word_entries.count() if word_entries else 0
        return format_html(
            '<span style="color: {};">{} 个单词</span>',
            'green' if count > 0 else 'gray',
            count
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[VocabularyList]:
        """优化查询"""
        return super().get_queryset(request).prefetch_related('word_entries', 'word_entries__word')
    
    def get_urls(self) -> List[Any]:
        """添加批量导入URL"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('batch_import/', self.admin_site.admin_view(self.batch_import_view), name='words_vocabularylist_batch_import'),
        ]
        return custom_urls + urls
    
    def perform_import(self, request, reader):
        """实现BaseBatchImportAdmin要求的perform_import方法"""
        # 这个方法是为了满足BaseBatchImportAdmin的接口要求
        # 实际的导入逻辑在batch_import_view中实现
        pass
    
    def batch_import_view(self, request: HttpRequest) -> HttpResponse:
        """批量导入视图 - 增强版本"""
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        import csv
        import io
        from datetime import datetime
        import uuid
        import logging
        from .models import VocabularySource, Word
        
        logger = logging.getLogger(__name__)
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, '请选择CSV文件')
                return redirect('admin:words_vocabularylist_batch_import')
            
            # 验证文件大小（限制为10MB）
            if hasattr(csv_file, 'size') and csv_file.size > 10 * 1024 * 1024:
                messages.error(request, "文件大小不能超过10MB")
                return render(request, 'admin/words/vocabularylist/batch_import.html', {
                    'title': '译林单词表批量导入',
                    'opts': self.model._meta,
                    'has_view_permission': self.has_view_permission(request),
                })
            
            # 验证文件类型
            if hasattr(csv_file, 'name') and not csv_file.name.lower().endswith('.csv'):
                messages.error(request, "请上传CSV格式的文件")
                return render(request, 'admin/words/vocabularylist/batch_import.html', {
                    'title': '译林单词表批量导入',
                    'opts': self.model._meta,
                    'has_view_permission': self.has_view_permission(request),
                })
            
            try:
                # 读取CSV文件，支持多种编码
                try:
                    if hasattr(csv_file, 'read'):
                        file_data = csv_file.read().decode('utf-8-sig')
                    else:
                        messages.error(request, "无法读取文件内容")
                        return render(request, 'admin/words/vocabularylist/batch_import.html', {
                            'title': '译林单词表批量导入',
                            'opts': self.model._meta,
                            'has_view_permission': self.has_view_permission(request),
                        })
                except UnicodeDecodeError:
                    try:
                        if hasattr(csv_file, 'seek'):
                            csv_file.seek(0)
                        file_data = csv_file.read().decode('gbk')
                    except UnicodeDecodeError:
                        messages.error(request, "文件编码不支持，请使用UTF-8或GBK编码")
                        return render(request, 'admin/words/vocabularylist/batch_import.html', {
                            'title': '译林单词表批量导入',
                            'opts': self.model._meta,
                            'has_view_permission': self.has_view_permission(request),
                        })
                
                csv_reader = csv.DictReader(io.StringIO(file_data))
                
                # 验证CSV表头
                fieldnames = csv_reader.fieldnames
                if not fieldnames or 'word' not in fieldnames:
                    messages.error(request, "CSV文件必须包含'word'字段作为表头")
                    return render(request, 'admin/words/vocabularylist/batch_import.html', {
                        'title': '译林单词表批量导入',
                        'opts': self.model._meta,
                        'has_view_permission': self.has_view_permission(request),
                    })
                
                # 检查是否有数据行
                first_row = next(csv_reader, None)
                if not first_row:
                    messages.error(request, "CSV文件没有数据行")
                    return render(request, 'admin/words/vocabularylist/batch_import.html', {
                        'title': '译林单词表批量导入',
                        'opts': self.model._meta,
                        'has_view_permission': self.has_view_permission(request),
                    })
                
                # 重新创建reader（因为已经读取了第一行）
                csv_reader = csv.DictReader(io.StringIO(file_data))
                
                # 生成导入批次ID
                import_batch_id = f"yilin_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                
                # 获取导入说明
                import_notes = request.POST.get('import_notes', '').strip()
                
                # 创建导入来源
                source_name = f"译林单词表导入_{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                source_description = f'译林单词表批量导入于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                if import_notes:
                    source_description += f'\n导入说明：{import_notes}'
                    
                import_source, _ = VocabularySource.objects.get_or_create(
                    name=source_name,
                    defaults={'description': source_description}
                )
                
                # 处理导入
                result = self.process_yilin_csv(csv_reader, import_source, import_batch_id, import_notes)
                
                # 显示详细的结果消息
                success_msg = []
                if result['created_lists'] > 0:
                    success_msg.append(f"创建了 {result['created_lists']} 个词汇表")
                if result['created_words'] > 0:
                    success_msg.append(f"创建了 {result['created_words']} 个新单词")
                if result['created_entries'] > 0:
                    success_msg.append(f"导入了 {result['created_entries']} 个新词条")
                if result['version_entries'] > 0:
                    success_msg.append(f"创建了 {result['version_entries']} 个版本词条")
                if result['skipped_duplicates'] > 0:
                    success_msg.append(f"跳过重复词条 {result['skipped_duplicates']} 个")
                
                if success_msg:
                    messages.success(request, f"✅ 导入完成！{', '.join(success_msg)}。批次ID：{import_batch_id}")
                
                if result['error_count'] > 0:
                    error_msg = f"⚠️ 导入过程中遇到 {result['error_count']} 个错误"
                    if result.get('error_details'):
                        error_msg += f"：{'; '.join(result['error_details'][:3])}"
                        if len(result['error_details']) > 3:
                            error_msg += "..."
                    messages.warning(request, error_msg)
                
                if result['created_entries'] == 0 and result['version_entries'] == 0 and result['error_count'] == 0:
                    messages.info(request, "ℹ️ 没有新的词条被导入，所有数据均为重复记录。")
                
                return HttpResponseRedirect(reverse('admin:words_vocabularylist_changelist'))
                
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                logger.error(f"CSV导入失败：{error_detail}")
                messages.error(request, f'文件处理失败：{str(e)}')
                return redirect('admin:words_vocabularylist_batch_import')
        
        # GET请求显示导入页面
        context = {
            'title': '译林单词表批量导入',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/words/vocabularylist/batch_import.html', context)
    
    def process_yilin_csv(self, csv_reader: Any, import_source: VocabularySource, import_batch_id: str, import_notes: str = '') -> Dict[str, Any]:
        """处理译林单词表CSV数据 - 支持新的Word和WordEntry模型结构"""
        from .models import Word, WordEntry, ImportRecord
        from django.db import transaction
        from django.contrib import messages
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        created_lists = 0
        created_words = 0
        created_entries = 0
        version_entries = 0
        skipped_entries = 0
        error_count = 0
        vocabulary_lists = {}
        error_details = []
        
        # 验证CSV字段
        required_fields = ['word']
        optional_fields = ['textbook_version', 'grade', 'book_volume', 'unit', 'phonetic', 'definition', 'part_of_speech', 'note']
        
        with transaction.atomic():
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # 数据清理和验证
                    word_text = self._clean_field(row.get('word', ''))
                    if not word_text:
                        error_details.append(f'第{row_num}行：单词字段为空')
                        error_count += 1
                        continue
                    
                    # 验证单词长度
                    if len(word_text) > 100:
                        error_details.append(f'第{row_num}行：单词"{word_text}"长度超过100字符')
                        error_count += 1
                        continue
                    
                    # 获取其他字段
                    textbook_version = self._clean_field(row.get('textbook_version', ''))
                    grade = self._clean_field(row.get('grade', ''))
                    book_volume = self._clean_field(row.get('book_volume', ''))
                    unit = self._clean_field(row.get('unit', ''))
                    phonetic = self._clean_field(row.get('phonetic', ''))
                    definition = self._clean_field(row.get('definition', ''))
                    part_of_speech = self._clean_field(row.get('part_of_speech', ''))
                    note = self._clean_field(row.get('note', ''))
                    
                    # 验证词性
                    if part_of_speech and not self._validate_part_of_speech(part_of_speech):
                        # 如果词性不在预定义列表中，记录警告但继续处理
                        logger.warning(f'第{row_num}行：未知词性"{part_of_speech}"，将保持原值')
                    
                    # 创建或获取词汇表
                    list_name = self._generate_list_name(textbook_version, grade, book_volume, unit, import_batch_id)
                    
                    if list_name not in vocabulary_lists:
                        vocab_list, created = VocabularyList.objects.get_or_create(
                            name=list_name,
                            source=import_source,
                            defaults={
                                'description': self._generate_list_description(textbook_version, grade, book_volume, unit),
                                'is_active': True
                            }
                        )
                        vocabulary_lists[list_name] = vocab_list
                        if created:
                            created_lists += 1
                    
                    vocab_list = vocabulary_lists[list_name]
                    
                    # 1. 创建或获取Word实例
                    word_instance, word_created = Word.objects.get_or_create(
                        word=word_text,
                        defaults={}
                    )
                    if word_created:
                        created_words += 1
                    
                    # 2. 检查是否存在完全相同的WordEntry（重复数据）
                    # 必须包含unique_together约束中的所有字段
                    identical_entry = WordEntry.objects.filter(
                        word=word_instance,
                        textbook_version=textbook_version,
                        grade=grade,
                        book_volume=book_volume,
                        unit=unit,
                        phonetic=phonetic,
                        definition=definition,
                        part_of_speech=part_of_speech,
                        note=note
                        # 注意：时间戳和vocabulary_list不在unique_together约束中
                    ).first()
                    
                    if identical_entry:
                        # 完全相同的数据，不重复创建，但创建新的ImportRecord
                        import_metadata = {
                            'row_number': row_num,
                            'import_time': datetime.now().isoformat(),
                            'source_file': '译林单词表',
                            'original_data': dict(row),
                            'duplicate_reason': 'identical_entry'
                        }
                        if import_notes:
                            import_metadata['import_notes'] = import_notes
                            
                        ImportRecord.objects.create(
                            word_entry=identical_entry,
                            import_type='duplicate',
                            import_source=import_source,
                            import_batch_id=import_batch_id,
                            import_metadata=import_metadata
                        )
                        skipped_entries += 1
                        continue
                    
                    # 3. 创建新的WordEntry（新版本数据）
                    word_entry = WordEntry.objects.create(
                        word=word_instance,
                        phonetic=phonetic,
                        definition=definition,
                        part_of_speech=part_of_speech,
                        example='',  # CSV中没有example字段
                        note=note,
                        vocabulary_list=vocab_list,
                        textbook_version=textbook_version,
                        grade=grade,
                        book_volume=book_volume,
                        unit=unit
                    )
                    created_entries += 1
                    
                    # 4. 创建ImportRecord记录导入信息
                    import_type = 'new' if word_created else 'version'
                    if import_type == 'version':
                        version_entries += 1
                        
                    import_metadata = {
                        'row_number': row_num,
                        'import_time': datetime.now().isoformat(),
                        'source_file': '译林单词表',
                        'original_data': dict(row),
                        'word_created': word_created
                    }
                    if import_notes:
                        import_metadata['import_notes'] = import_notes
                        
                    ImportRecord.objects.create(
                        word_entry=word_entry,
                        import_type=import_type,
                        import_source=import_source,
                        import_batch_id=import_batch_id,
                        import_metadata=import_metadata
                    )
                    
                except Exception as e:
                    error_details.append(f'第{row_num}行：处理失败 - {str(e)}')
                    error_count += 1
                    logger.error(f'CSV导入第{row_num}行处理失败：{str(e)}')
                    continue
        
        # 更新词汇表的单词数量
        for vocab_list in vocabulary_lists.values():
            vocab_list.update_word_count()
        
        # 更新导入来源的统计信息
        # 计算统计数据
        import_records = ImportRecord.objects.filter(import_batch_id=import_batch_id)
        new_words_count = import_records.filter(import_type='new').count()
        version_words_count = import_records.filter(import_type='version').count()
        duplicate_words_count = import_records.filter(import_type='duplicate').count()
        
        import_source.update_import_stats(
            batch_id=import_batch_id,
            file_name='译林单词表.csv',
            new_words=new_words_count,
            duplicate_words=duplicate_words_count,
            version_words=version_words_count
        )
        
        return {
            'created_lists': created_lists,
            'created_words': created_words,
            'created_entries': created_entries,
            'version_entries': version_entries,
            'skipped_duplicates': skipped_entries,
            'error_count': error_count,
            'error_details': error_details[:10],  # 只返回前10个错误详情
            'import_stats': {
                'new_words': new_words_count,
                'duplicate_words': duplicate_words_count,
                'version_words': version_words_count,
                'total_processed': created_entries + skipped_entries
            }
        }
    
    def _clean_field(self, value: Any) -> str:
        """清理字段数据"""
        if not value:
            return ''
        return str(value).strip().replace('\n', ' ').replace('\r', '')
    
    def _validate_part_of_speech(self, part_of_speech: str) -> bool:
        """验证词性是否有效"""
        from .models import PART_OF_SPEECH_CHOICES
        valid_choices = [choice[0] for choice in PART_OF_SPEECH_CHOICES]
        return part_of_speech in valid_choices
    
    def _generate_list_name(self, textbook_version: str, grade: str, book_volume: str, unit: str, import_batch_id: str) -> str:
        """生成词汇表名称"""
        parts = [textbook_version, grade, book_volume, unit]
        parts = [part for part in parts if part]  # 过滤空值
        
        if parts:
            return '_'.join(parts)
        else:
            return f"未分类词汇_{import_batch_id}"
    
    def _generate_list_description(self, textbook_version: str, grade: str, book_volume: str, unit: str) -> str:
        """生成词汇表描述"""
        parts = [textbook_version, grade, book_volume, unit]
        parts = [part for part in parts if part]  # 过滤空值
        
        if parts:
            return f'来自译林单词表：{" ".join(parts)}'
        else:
            return '来自译林单词表批量导入'







@admin.register(WordGrader)
class WordGraderAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
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
    def total_levels_display(self, obj: WordGrader) -> str:
        """显示实际等级数量"""
        # 使用类型注解避免诊断错误
        grade_levels = getattr(obj, 'grade_levels', None)
        count = grade_levels.count() if grade_levels else 0
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            'green' if count == obj.grade_count else 'orange',
            count,
            obj.grade_count
        )
    
    def save_model(self, request: HttpRequest, obj: WordGrader, form: Any, change: bool) -> None:
        """保存模型"""
        if not change:  # 创建新对象
            if not obj.created_by:
                obj.created_by = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[WordGrader]:
        """优化查询"""
        return super().get_queryset(request).select_related('created_by').prefetch_related('grade_levels')


@admin.register(WordGradeLevel)
class WordGradeLevelAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
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
    def word_count_display(self, obj: WordGradeLevel) -> str:
        """显示单词数量"""
        if obj.word_set:
            # 使用类型注解避免诊断错误
            words = getattr(obj.word_set, 'words', None)
            count = words.count() if words else 0
            return format_html(
                '<span style="color: {};">{} 个单词</span>',
                'green' if count > 0 else 'gray',
                count
            )
        return format_html('<span style="color: gray;">未绑定单词集</span>')
    
    @admin.display(description='难度范围')
    def difficulty_range_display(self, obj: WordGradeLevel) -> str:
        """显示难度范围"""
        return format_html(
            '<span class="badge">{} - {}</span>',
            obj.min_difficulty,
            obj.max_difficulty
        )
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[WordGradeLevel]:
        """优化查询"""
        return super().get_queryset(request).select_related('grader', 'word_set').prefetch_related('word_set__words')


@admin.register(VocabularySource)
class VocabularySourceAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """词库导入来源管理"""
    list_display = [
        'name', 'description', 'total_imports_display', 'total_words_display', 
        'last_import_display', 'is_active', 'list_count_display', 'created_at'
    ]
    list_filter = ['is_active', 'auto_create_lists', 'last_import_at', 'created_at']
    search_fields = ['name', 'description', 'last_import_file_name']
    readonly_fields = [
        'total_imports', 'total_words_imported', 'total_new_words', 
        'total_duplicate_words', 'total_version_words', 'last_import_at',
        'last_import_batch_id', 'last_import_file_name', 'last_import_word_count',
        'created_at', 'updated_at'
    ]
    ordering = ['-last_import_at', 'name']
    list_per_page = 25
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('配置选项', {
            'fields': ('is_active', 'auto_create_lists')
        }),
        ('导入统计', {
            'fields': (
                'total_imports', 'total_words_imported', 'total_new_words',
                'total_duplicate_words', 'total_version_words'
            ),
            'classes': ('collapse',)
        }),
        ('最后导入信息', {
            'fields': (
                'last_import_at', 'last_import_batch_id', 
                'last_import_file_name', 'last_import_word_count'
            ),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='导入次数')
    def total_imports_display(self, obj: VocabularySource) -> str:
        """显示总导入次数"""
        if obj.total_imports > 0:
            return format_html('<span style="color: green;">{}</span>', obj.total_imports)
        return format_html('<span style="color: gray;">0</span>')
    
    @admin.display(description='导入单词数')
    def total_words_display(self, obj: VocabularySource) -> str:
        """显示总导入单词数"""
        if obj.total_words_imported > 0:
            return format_html(
                '<span style="color: blue;">{}</span> (新增: {}, 重复: {}, 版本: {})',
                obj.total_words_imported, obj.total_new_words, 
                obj.total_duplicate_words, obj.total_version_words
            )
        return format_html('<span style="color: gray;">0</span>')
    
    @admin.display(description='最后导入')
    def last_import_display(self, obj: VocabularySource) -> str:
        """显示最后导入信息"""
        if obj.last_import_at:
            # 安全地访问datetime属性
            import_time = getattr(obj.last_import_at, 'strftime', lambda x: str(obj.last_import_at))('%Y-%m-%d %H:%M')
            return format_html(
                '<span style="color: green;">{}</span><br/><small>{} ({} 个单词)</small>',
                import_time,
                obj.last_import_file_name or '未知文件',
                obj.last_import_word_count
            )
        return format_html('<span style="color: gray;">从未导入</span>')
    
    @admin.display(description='词汇表数量')
    def list_count_display(self, obj: VocabularySource) -> str:
        """显示词汇表数量"""
        # 使用类型注解避免诊断错误
        vocabulary_lists = getattr(obj, 'vocabulary_lists', None)
        count = vocabulary_lists.count() if vocabulary_lists else 0
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[VocabularySource]:
        """优化查询"""
        return super().get_queryset(request).prefetch_related('vocabulary_lists')


@admin.register(WordSet)
class WordSetAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
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
    def word_count_display(self, obj: WordSet) -> str:
        """显示单词数量"""
        # 使用类型注解避免诊断错误
        words = getattr(obj, 'words', None)
        count = words.count() if words else 0
        return format_html(
            '<span style="color: {};">{} 个单词</span>',
            'green' if count > 0 else 'gray',
            count
        )
    
    def save_model(self, request: HttpRequest, obj: WordSet, form: Any, change: bool) -> None:
        """保存模型"""
        if not change:  # 创建新对象
            if not obj.created_by:
                obj.created_by = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[WordSet]:
        """优化查询"""
        return super().get_queryset(request).select_related('created_by').prefetch_related('words')


@admin.register(WordResource)
class WordResourceAdmin(AdminDynamicPaginationMixin, BaseBatchImportAdmin):
    """单词资源管理"""
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
    def file_size_display(self, obj: WordResource) -> str:
        """显示文件大小"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f'{obj.file_size} B'
            elif obj.file_size < 1024 * 1024:
                return f'{obj.file_size / 1024:.1f} KB'
            else:
                return f'{obj.file_size / (1024 * 1024):.1f} MB'
        return '-'
    
    # WordEntry Admin
@admin.register(WordEntry)
class WordEntryAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """词条管理"""
    list_display = [
        'word', 'phonetic', 'part_of_speech', 'textbook_version', 
        'grade', 'book_volume', 'unit', 'vocabulary_list', 'created_at'
    ]
    list_filter = [
        'part_of_speech', 'textbook_version', 'grade', 'book_volume', 
        'vocabulary_list', 'created_at'
    ]
    search_fields = ['word__word', 'definition', 'example', 'phonetic']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['word__word']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('word', 'phonetic', 'definition', 'part_of_speech')
        }),
        ('学习内容', {
            'fields': ('example', 'note')
        }),
        ('教材信息', {
            'fields': ('textbook_version', 'grade', 'book_volume', 'unit')
        }),
        ('分类信息', {
            'fields': ('vocabulary_list',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# ImportRecord Admin
@admin.register(ImportRecord)
class ImportRecordAdmin(AdminDynamicPaginationMixin, admin.ModelAdmin):
    """导入记录管理"""
    list_display = [
        'word_entry', 'import_type', 'import_source', 
        'import_batch_id', 'created_at'
    ]
    list_filter = [
        'import_type', 'import_source', 'created_at'
    ]
    search_fields = ['word_entry__word__word', 'import_batch_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('word_entry', 'import_type')
        }),
        ('导入信息', {
            'fields': ('import_source', 'import_batch_id', 'import_metadata')
        }),
        ('时间戳', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


    def perform_import(self, request: HttpRequest, reader: Any) -> None:
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
                
                WordResource.objects.create(**resource_data)
                created_count += 1
                
            except Exception as e:
                messages.warning(request, f'第{row_num}行处理失败：{str(e)}')
                error_count += 1
        
        if created_count > 0:
            messages.success(request, f'成功导入 {created_count} 个资源。')
        if error_count > 0:
            messages.warning(request, f'有 {error_count} 行数据导入失败。')
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[WordResource]:
        """优化查询"""
        return super().get_queryset(request)