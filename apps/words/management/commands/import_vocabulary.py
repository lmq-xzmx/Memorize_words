import csv
import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.words.models import VocabularySource, VocabularyList, ImportedVocabulary, Word, ConflictResolution
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = '导入词汇数据从CSV或JSON文件'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='词汇文件路径（支持CSV和JSON格式）'
        )
        parser.add_argument(
            '--source-name',
            type=str,
            required=True,
            help='词库来源名称'
        )
        parser.add_argument(
            '--list-name',
            type=str,
            required=True,
            help='词库列表名称'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json'],
            default='csv',
            help='文件格式（默认：csv）'
        )
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8',
            help='文件编码（默认：utf-8）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行，不实际导入数据'
        )
        parser.add_argument(
            '--detect-conflicts',
            action='store_true',
            help='检测并标记冲突单词'
        )
        parser.add_argument(
            '--similarity-threshold',
            type=float,
            default=0.8,
            help='相似度阈值（0.0-1.0），用于检测变体单词（默认：0.8）'
        )
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        source_name = options['source_name']
        list_name = options['list_name']
        file_format = options['format']
        encoding = options['encoding']
        dry_run = options['dry_run']
        detect_conflicts = options['detect_conflicts']
        similarity_threshold = options['similarity_threshold']
        
        try:
            # 获取或创建词库来源
            source, created = VocabularySource.objects.get_or_create(
                name=source_name,
                defaults={'description': f'通过命令行导入的词库来源：{source_name}'}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'创建新的词库来源：{source_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'使用现有词库来源：{source_name}')
                )
            
            # 获取或创建词库列表
            vocabulary_list, created = VocabularyList.objects.get_or_create(
                source=source,
                name=list_name,
                defaults={'description': f'通过命令行导入的词库列表：{list_name}'}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'创建新的词库列表：{list_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'使用现有词库列表：{list_name}')
                )
            
            # 读取和导入数据
            if file_format == 'csv':
                imported_count = self.import_from_csv(
                    file_path, vocabulary_list, encoding, dry_run, detect_conflicts, similarity_threshold
                )
            else:
                imported_count = self.import_from_json(
                    file_path, vocabulary_list, encoding, dry_run, detect_conflicts, similarity_threshold
                )
            
            if not dry_run:
                # 更新词库列表的单词数量
                vocabulary_list.update_word_count()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'成功导入 {imported_count} 个单词到词库列表 "{list_name}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'试运行完成，将导入 {imported_count} 个单词'
                    )
                )
        
        except Exception as e:
            raise CommandError(f'导入失败：{str(e)}')
    
    def import_from_csv(self, file_path, vocabulary_list, encoding, dry_run, detect_conflicts=False, similarity_threshold=0.8):
        """从CSV文件导入词汇"""
        imported_count = 0
        
        try:
            with open(file_path, 'r', encoding=encoding) as csvfile:
                # 自动检测CSV格式
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # 验证必需的列
                required_fields = ['word']
                fieldnames = reader.fieldnames or []
                if not all(field in fieldnames for field in required_fields):
                    raise CommandError(
                        f'CSV文件必须包含以下列：{required_fields}\n'
                        f'当前列：{fieldnames}'
                    )
                
                words_to_create = []
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        word_data = self.parse_word_data(row)
                        
                        if not dry_run:
                            # 检查是否已存在
                            existing = ImportedVocabulary.objects.filter(
                                vocabulary_list=vocabulary_list,
                                word=word_data['word']
                            ).first()
                            
                            if existing:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'第{row_num}行：单词 "{word_data["word"]}" 已存在，跳过'
                                    )
                                )
                                continue
                            
                            words_to_create.append(
                                ImportedVocabulary(
                                    vocabulary_list=vocabulary_list,
                                    **word_data
                                )
                            )
                        
                        imported_count += 1
                        
                        if imported_count % 100 == 0:
                            self.stdout.write(
                                f'已处理 {imported_count} 个单词...'
                            )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'第{row_num}行处理失败：{str(e)}'
                            )
                        )
                        continue
                
                # 批量创建
                if not dry_run and words_to_create:
                    with transaction.atomic():
                        ImportedVocabulary.objects.bulk_create(
                            words_to_create, batch_size=100
                        )
        
        except FileNotFoundError:
            raise CommandError(f'文件不存在：{file_path}')
        except UnicodeDecodeError:
            raise CommandError(f'文件编码错误，请尝试不同的编码格式')
        
        return imported_count
    
    def import_from_json(self, file_path, vocabulary_list, encoding, dry_run, detect_conflicts=False, similarity_threshold=0.8):
        """从JSON文件导入词汇"""
        imported_count = 0
        
        try:
            with open(file_path, 'r', encoding=encoding) as jsonfile:
                data = json.load(jsonfile)
                
                # 支持两种JSON格式：
                # 1. 直接是单词列表
                # 2. 包含words字段的对象
                if isinstance(data, dict) and 'words' in data:
                    words_data = data['words']
                elif isinstance(data, list):
                    words_data = data
                else:
                    raise CommandError('JSON格式不正确，应该是单词列表或包含words字段的对象')
                
                words_to_create = []
                
                for index, word_item in enumerate(words_data):
                    try:
                        word_data = self.parse_word_data(word_item)
                        
                        if not dry_run:
                            # 检查是否已存在
                            existing = ImportedVocabulary.objects.filter(
                                vocabulary_list=vocabulary_list,
                                word=word_data['word']
                            ).first()
                            
                            if existing:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'索引{index}：单词 "{word_data["word"]}" 已存在，跳过'
                                    )
                                )
                                continue
                            
                            words_to_create.append(
                                ImportedVocabulary(
                                    vocabulary_list=vocabulary_list,
                                    **word_data
                                )
                            )
                        
                        imported_count += 1
                        
                        if imported_count % 100 == 0:
                            self.stdout.write(
                                f'已处理 {imported_count} 个单词...'
                            )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'索引{index}处理失败：{str(e)}'
                            )
                        )
                        continue
                
                # 批量创建
                if not dry_run and words_to_create:
                    with transaction.atomic():
                        ImportedVocabulary.objects.bulk_create(
                            words_to_create, batch_size=100
                        )
        
        except FileNotFoundError:
            raise CommandError(f'文件不存在：{file_path}')
        except json.JSONDecodeError as e:
            raise CommandError(f'JSON格式错误：{str(e)}')
        except UnicodeDecodeError:
            raise CommandError(f'文件编码错误，请尝试不同的编码格式')
        
        return imported_count
    
    def parse_word_data(self, data):
        """解析单词数据"""
        if isinstance(data, dict):
            word_data = {
                'word': data.get('word', '').strip(),
                'phonetic': data.get('phonetic', '').strip(),
                'definition': data.get('definition', '').strip(),
                'part_of_speech': data.get('part_of_speech', '').strip(),
                'textbook_version': data.get('textbook_version', '').strip(),
                'grade': data.get('grade', '').strip(),
                'example': data.get('example', '').strip(),
                'note': data.get('note', '').strip(),
            }
        else:
            # 如果是字符串，只设置单词
            word_data = {
                'word': str(data).strip(),
                'phonetic': '',
                'definition': '',
                'part_of_speech': '',
                'textbook_version': '',
                'grade': '',
                'example': '',
                'note': '',
            }
        
        # 验证必需字段
        if not word_data['word']:
            raise ValueError('单词字段不能为空')
        
        return word_data
    
    def detect_word_conflicts(self, word, word_data, detect_conflicts, similarity_threshold):
        """检测单词冲突"""
        if not detect_conflicts:
            return False, {}
        
        conflicts = []
        
        # 检查完全重复（在ImportedVocabulary中）
        existing_imported = ImportedVocabulary.objects.filter(word__iexact=word)
        if existing_imported.exists():
            for existing_word in existing_imported:
                conflicts.append({
                    'type': 'duplicate',
                    'existing_word_id': existing_word.pk,
                    'existing_word': existing_word.word,
                    'existing_definition': existing_word.definition,
                    'new_definition': word_data.get('definition', ''),
                    'source': 'imported_vocabulary'
                })
        
        # 检查在用户单词库中的重复
        existing_user_words = Word.objects.filter(word__iexact=word)
        if existing_user_words.exists():
            for existing_word in existing_user_words:
                conflicts.append({
                    'type': 'duplicate',
                    'existing_word_id': existing_word.pk,
                    'existing_word': existing_word.word,
                    'existing_definition': existing_word.definition,
                    'new_definition': word_data.get('definition', ''),
                    'source': 'user_words'
                })
        
        # 检查相似变体（在ImportedVocabulary中）
        all_imported_words = ImportedVocabulary.objects.all().values_list('word', 'id', 'definition')
        for existing_word, word_id, definition in all_imported_words:
            similarity = SequenceMatcher(None, word.lower(), existing_word.lower()).ratio()
            if similarity >= similarity_threshold and word.lower() != existing_word.lower():
                conflicts.append({
                    'type': 'variant',
                    'existing_word_id': word_id,
                    'existing_word': existing_word,
                    'existing_definition': definition,
                    'new_definition': word_data.get('definition', ''),
                    'similarity': similarity,
                    'source': 'imported_vocabulary'
                })
        
        # 检查版本差异（相同单词但不同教材版本）
        if word_data.get('textbook_version'):
            version_conflicts = ImportedVocabulary.objects.filter(
                word__iexact=word
            ).exclude(
                textbook_version=word_data['textbook_version']
            )
            for existing_word in version_conflicts:
                conflicts.append({
                    'type': 'version',
                    'existing_word_id': existing_word.pk,
                    'existing_word': existing_word.word,
                    'existing_version': existing_word.textbook_version,
                    'new_version': word_data['textbook_version'],
                    'existing_definition': existing_word.definition,
                    'new_definition': word_data.get('definition', ''),
                    'source': 'imported_vocabulary'
                })
        
        has_conflict = len(conflicts) > 0
        conflict_data = {'conflicts': conflicts, 'total_conflicts': len(conflicts)} if has_conflict else {}
        
        return has_conflict, conflict_data