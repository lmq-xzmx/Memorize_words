import os
import csv
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.words.models import VocabularySource, VocabularyList, ImportedVocabulary

class Command(BaseCommand):
    help = '从CSV文件导入词库到Natural_English项目'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV文件路径')
        parser.add_argument('--source-name', type=str, default='CSV导入', help='词库来源名称')
        parser.add_argument('--list-name', type=str, help='词库列表名称（默认使用文件名）')
        parser.add_argument('--description', type=str, default='', help='词库描述')
        parser.add_argument('--conflict-strategy', type=str, default='mark', 
                           choices=['mark', 'skip', 'overwrite', 'merge'],
                           help='冲突处理策略: mark(标记冲突), skip(跳过), overwrite(覆盖), merge(合并)')
        parser.add_argument('--encoding', type=str, default='utf-8', help='CSV文件编码')
        parser.add_argument('--delimiter', type=str, default=',', help='CSV分隔符')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        source_name = options['source_name']
        list_name = options['list_name'] or os.path.splitext(os.path.basename(csv_file_path))[0]
        description = options['description']
        conflict_strategy = options['conflict_strategy']
        encoding = options['encoding']
        delimiter = options['delimiter']

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'文件不存在: {csv_file_path}'))
            return

        # 获取或创建词库来源
        source, created = VocabularySource.objects.get_or_create(
            name=source_name,
            defaults={'description': f'{source_name}词库来源'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'创建了新的词库来源: {source_name}'))

        # 创建词库列表
        vocabulary_list = VocabularyList.objects.create(
            source=source,
            name=list_name,
            description=description or f'从{os.path.basename(csv_file_path)}导入的词库'
        )
        self.stdout.write(self.style.SUCCESS(f'创建了新的词库列表: {list_name}'))

        # 读取CSV文件
        try:
            with open(csv_file_path, 'r', encoding=encoding) as file:
                # 检测CSV格式
                sample = file.read(1024)
                file.seek(0)
                
                # 尝试检测分隔符
                if delimiter == ',':
                    if '\t' in sample and sample.count('\t') > sample.count(','):
                        delimiter = '\t'
                        self.stdout.write(self.style.WARNING('检测到制表符分隔，自动切换到TAB分隔符'))
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                # 打印CSV信息
                self.stdout.write(self.style.SUCCESS(f'CSV文件编码: {encoding}'))
                self.stdout.write(self.style.SUCCESS(f'CSV分隔符: {repr(delimiter)}'))
                self.stdout.write(self.style.SUCCESS(f'CSV表头: {headers}'))
                
                # 创建字段映射
                field_mapping = self.create_field_mapping(headers)
                self.stdout.write(self.style.SUCCESS(f'字段映射: {field_mapping}'))
                
                # 检查必要字段
                if 'word' not in field_mapping:
                    self.stdout.write(self.style.ERROR('CSV文件中未找到单词字段，请确保有"word"、"单词"或类似的列'))
                    return
                
                # 导入数据
                stats = self.import_data(reader, field_mapping, vocabulary_list, conflict_strategy)
                
                # 更新词库列表的单词数量
                vocabulary_list.update_word_count()
                
                # 打印统计信息
                self.print_import_stats(stats)
                
        except UnicodeDecodeError as e:
            self.stdout.write(self.style.ERROR(f'文件编码错误: {e}'))
            self.stdout.write(self.style.WARNING('请尝试使用 --encoding 参数指定正确的编码，如: --encoding gbk'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导入过程中发生错误: {e}'))
            raise

    def create_field_mapping(self, headers):
        """创建CSV字段到模型字段的映射"""
        # 初始化字段映射（包含所有可能的字段）
        field_mapping = {}
        
        # 支持的字段列表
        supported_fields = [
            'word', 'phonetic', 'definition', 'part_of_speech',
            'textbook_version', 'grade', 'example', 'note',
            'book_volume', 'unit'  # 额外字段，将合并到note中
        ]
        
        for i, header in enumerate(headers):
            header_lower = header.lower().strip()
            
            # 直接匹配
            if header_lower in supported_fields:
                field_mapping[header_lower] = i
            # 单词字段映射
            elif header_lower in ['word', '单词', 'english', 'english_word']:
                field_mapping['word'] = i
            # 音标字段映射
            elif header_lower in ['phonetic', '音标', 'pronunciation', 'ipa']:
                field_mapping['phonetic'] = i
            # 释义字段映射
            elif header_lower in ['definition', '释义', '意思', 'meaning', 'chinese', '中文']:
                field_mapping['definition'] = i
            # 词性字段映射
            elif header_lower in ['part_of_speech', '词性', 'pos', 'speech']:
                field_mapping['part_of_speech'] = i
            # 教材版本字段映射
            elif 'textbook' in header_lower or '教材' in header_lower or 'version' in header_lower:
                field_mapping['textbook_version'] = i
            # 年级字段映射
            elif header_lower in ['grade', '年级', 'level']:
                field_mapping['grade'] = i
            # 例句字段映射
            elif header_lower in ['example', '例句', 'sentence', 'sample']:
                field_mapping['example'] = i
            # 备注字段映射
            elif header_lower in ['note', '备注', '说明', 'remark', 'comment']:
                field_mapping['note'] = i
            # 单元字段映射
            elif header_lower in ['unit', '单元', 'lesson', '课']:
                field_mapping['unit'] = i
            # 册数字段映射
            elif header_lower in ['book_volume', '册', 'volume', 'book']:
                field_mapping['book_volume'] = i
        
        return field_mapping

    def import_data(self, reader, field_mapping, vocabulary_list, conflict_strategy):
        """导入CSV数据"""
        stats = {
            'total_processed': 0,
            'new_words': 0,
            'conflict_words': 0,
            'skipped_words': 0,
            'error_words': 0,
            'errors': []
        }
        
        # 年级映射
        grade_mapping = {
            '一年级': '1', '二年级': '2', '三年级': '3', '四年级': '4',
            '五年级': '5', '六年级': '6', '初一': '7', '初二': '8',
            '初三': '9', '高一': '10', '高二': '11', '高三': '12'
        }
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
                if not row or len(row) < len(field_mapping):
                    continue
                
                try:
                    # 提取数据
                    word_data = self.extract_word_data(row, field_mapping)
                    
                    word = word_data.get('word', '').strip()
                    if not word:
                        continue
                    
                    # 处理年级数据
                    grade = word_data.get('grade', '').strip()
                    if grade in grade_mapping:
                        word_data['grade'] = grade_mapping[grade]
                    
                    # 检查是否存在冲突
                    existing_word = ImportedVocabulary.objects.filter(
                        vocabulary_list=vocabulary_list,
                        word=word
                    ).first()
                    
                    if existing_word:
                        # 处理冲突
                        if self.handle_conflict(existing_word, word_data, conflict_strategy):
                            stats['conflict_words'] += 1
                        else:
                            stats['skipped_words'] += 1
                    else:
                        # 创建新单词，只包含模型支持的字段
                        filtered_data = self.filter_supported_fields(word_data)
                        ImportedVocabulary.objects.create(
                            vocabulary_list=vocabulary_list,
                            **filtered_data
                        )
                        stats['new_words'] += 1
                    
                    stats['total_processed'] += 1
                    
                    # 每1000个单词打印一次进度
                    if stats['total_processed'] % 1000 == 0:
                        self.stdout.write(f'已处理 {stats["total_processed"]} 个单词...')
                        
                except Exception as e:
                    error_msg = f'第{row_num}行导入失败: {str(e)}'
                    stats['errors'].append(error_msg)
                    stats['error_words'] += 1
                    
                    if len(stats['errors']) <= 10:  # 只记录前10个错误
                        self.stdout.write(self.style.WARNING(error_msg))
        
        return stats

    def extract_word_data(self, row, field_mapping):
        """从CSV行中提取单词数据"""
        word_data = {}
        
        for field, index in field_mapping.items():
            if index < len(row):
                value = row[index].strip()
                word_data[field] = value
            else:
                word_data[field] = ''
        
        # 确保必要字段存在
        required_fields = ['word', 'phonetic', 'definition', 'part_of_speech', 
                          'textbook_version', 'grade', 'example', 'note']
        for field in required_fields:
            if field not in word_data:
                word_data[field] = ''
        
        return word_data

    def handle_conflict(self, existing_word, new_data, strategy):
        """处理单词冲突"""
        if strategy == 'skip':
            return False
        
        elif strategy == 'overwrite':
            # 覆盖现有数据
            for field, value in new_data.items():
                if field != 'word':  # 不覆盖单词本身
                    setattr(existing_word, field, value)
            existing_word.has_conflict = False
            existing_word.conflict_data = {}
            existing_word.save()
            return True
        
        elif strategy == 'merge':
            # 智能合并数据
            changes = {}
            for field, new_value in new_data.items():
                if field == 'word':
                    continue
                
                current_value = getattr(existing_word, field, '')
                
                if not current_value and new_value:
                    # 当前字段为空，使用新值
                    setattr(existing_word, field, new_value)
                    changes[field] = new_value
                elif new_value and new_value != current_value:
                    # 合并不同的值
                    if field in ['definition', 'example', 'note']:
                        # 文本字段合并
                        merged_value = self.merge_text_fields(current_value, new_value)
                        setattr(existing_word, field, merged_value)
                        changes[field] = merged_value
                    elif field == 'part_of_speech':
                        # 词性合并
                        merged_pos = self.merge_part_of_speech(current_value, new_value)
                        setattr(existing_word, field, merged_pos)
                        changes[field] = merged_pos
                    else:
                        # 其他字段保留新值
                        setattr(existing_word, field, new_value)
                        changes[field] = new_value
            
            if changes:
                existing_word.save()
            return True
        
        else:  # 'mark' 策略
            # 标记冲突
            conflict_data = existing_word.conflict_data or {}
            import_id = f"csv_import_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            
            conflict_data[import_id] = {
                'timestamp': timezone.now().isoformat(),
                'source': 'CSV导入',
                'data': new_data
            }
            
            existing_word.has_conflict = True
            existing_word.conflict_data = conflict_data
            existing_word.save()
            return True

    def merge_text_fields(self, current, new):
        """合并文本字段"""
        if not current:
            return new
        if not new:
            return current
        
        # 避免重复内容
        if new in current:
            return current
        
        return f"{current}; {new}"

    def merge_part_of_speech(self, current, new):
        """合并词性"""
        if not current:
            return new
        if not new:
            return current
        
        # 分割并去重
        current_parts = set(p.strip() for p in current.split(';') if p.strip())
        new_parts = set(p.strip() for p in new.split(';') if p.strip())
        
        merged_parts = current_parts.union(new_parts)
        return '; '.join(sorted(merged_parts))

    def print_import_stats(self, stats):
        """打印导入统计信息"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('导入完成统计:'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'总处理单词数: {stats["total_processed"]}')
        self.stdout.write(f'新增单词数: {stats["new_words"]}')
        self.stdout.write(f'冲突处理数: {stats["conflict_words"]}')
        self.stdout.write(f'跳过单词数: {stats["skipped_words"]}')
        self.stdout.write(f'错误单词数: {stats["error_words"]}')
        
        if stats['errors']:
            self.stdout.write(self.style.WARNING('\n错误详情:'))
            for error in stats['errors'][:5]:  # 只显示前5个错误
                self.stdout.write(f'  - {error}')
            if len(stats['errors']) > 5:
                self.stdout.write(f'  ... 还有 {len(stats["errors"]) - 5} 个错误')
        
        self.stdout.write(self.style.SUCCESS('\n导入完成！'))
    
    def filter_supported_fields(self, word_data):
        """过滤出模型支持的字段，将额外字段合并到note中"""
        # ImportedVocabulary模型支持的字段
        supported_fields = {
            'word', 'phonetic', 'definition', 'part_of_speech',
            'textbook_version', 'grade', 'example', 'note'
        }
        
        filtered_data = {}
        extra_info = []
        
        for field, value in word_data.items():
            if field in supported_fields:
                filtered_data[field] = value
            elif value:  # 只处理非空的额外字段
                if field == 'book_volume':
                    extra_info.append(f"册数: {value}")
                elif field == 'unit':
                    extra_info.append(f"单元: {value}")
                else:
                    extra_info.append(f"{field}: {value}")
        
        # 将额外信息合并到note字段
        if extra_info:
            original_note = filtered_data.get('note', '')
            extra_note = f"[导入信息] {', '.join(extra_info)}"
            if original_note:
                filtered_data['note'] = f"{original_note}\n{extra_note}"
            else:
                filtered_data['note'] = extra_note
        
        return filtered_data