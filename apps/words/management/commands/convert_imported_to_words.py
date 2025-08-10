from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from apps.words.models import ImportedVocabulary, Word, ConflictResolution
import json

class Command(BaseCommand):
    help = '将ImportedVocabulary数据转换为用户的Word数据，实现"导入的单词"和"单词"的统一'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='指定用户ID，如果不指定则为所有用户转换')
        parser.add_argument('--vocabulary-list-id', type=int, help='指定词库列表ID，如果不指定则转换所有词库')
        parser.add_argument('--conflict-strategy', type=str, default='merge', 
                           choices=['merge', 'skip', 'overwrite'],
                           help='冲突处理策略: merge(合并), skip(跳过), overwrite(覆盖)')
        parser.add_argument('--batch-size', type=int, default=1000, help='批处理大小')
        parser.add_argument('--dry-run', action='store_true', help='试运行，不实际修改数据')
        parser.add_argument('--auto-assign-user', action='store_true', 
                           help='自动为ImportedVocabulary分配用户（基于词库列表创建者或第一个用户）')

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        vocabulary_list_id = options.get('vocabulary_list_id')
        conflict_strategy = options['conflict_strategy']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        auto_assign_user = options['auto_assign_user']

        if dry_run:
            self.stdout.write(self.style.WARNING('试运行模式，不会实际修改数据'))

        # 构建查询条件
        query_filters = {}
        if vocabulary_list_id:
            query_filters['vocabulary_list_id'] = vocabulary_list_id

        # 获取要转换的ImportedVocabulary记录
        imported_words = ImportedVocabulary.objects.filter(**query_filters)
        
        if user_id:
            # 如果指定了用户，只处理该用户相关的数据
            try:
                target_user = User.objects.get(id=user_id)
                self.stdout.write(f'为用户 {target_user.username} 转换单词')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'用户ID {user_id} 不存在'))
                return
        else:
            target_user = None

        total_count = imported_words.count()
        self.stdout.write(f'找到 {total_count} 个导入的单词需要转换')

        if total_count == 0:
            self.stdout.write(self.style.WARNING('没有找到需要转换的单词'))
            return

        # 统计信息
        stats = {
            'total_processed': 0,
            'words_created': 0,
            'words_updated': 0,
            'conflicts_resolved': 0,
            'skipped': 0,
            'errors': []
        }

        # 批量处理
        processed = 0
        while processed < total_count:
            batch = imported_words[processed:processed + batch_size]
            
            if not dry_run:
                with transaction.atomic():
                    self.process_batch(batch, target_user, conflict_strategy, auto_assign_user, stats)
            else:
                self.process_batch(batch, target_user, conflict_strategy, auto_assign_user, stats, dry_run=True)
            
            processed += batch_size
            self.stdout.write(f'已处理 {min(processed, total_count)}/{total_count} 个单词...')

        # 打印统计信息
        self.print_stats(stats, dry_run)

    def process_batch(self, batch, target_user, conflict_strategy, auto_assign_user, stats, dry_run=False):
        """处理一批ImportedVocabulary记录"""
        for imported_word in batch:
            try:
                # 确定目标用户
                user = self.determine_target_user(imported_word, target_user, auto_assign_user)
                if not user:
                    stats['skipped'] += 1
                    continue

                # 检查是否已存在相同单词
                existing_word = Word.objects.filter(
                    user=user,
                    word=imported_word.word
                ).first()

                if existing_word:
                    # 处理冲突
                    if conflict_strategy == 'skip':
                        stats['skipped'] += 1
                        continue
                    elif conflict_strategy == 'overwrite':
                        if not dry_run:
                            self.overwrite_word(existing_word, imported_word)
                        stats['words_updated'] += 1
                    else:  # merge
                        if not dry_run:
                            self.merge_word(existing_word, imported_word)
                            self.create_conflict_resolution(existing_word, imported_word)
                        stats['words_updated'] += 1
                        stats['conflicts_resolved'] += 1
                else:
                    # 创建新单词
                    if not dry_run:
                        self.create_word_from_imported(user, imported_word)
                    stats['words_created'] += 1

                stats['total_processed'] += 1

            except Exception as e:
                error_msg = f'处理单词 {imported_word.word} 时出错: {str(e)}'
                stats['errors'].append(error_msg)
                if len(stats['errors']) <= 10:
                    self.stdout.write(self.style.ERROR(error_msg))

    def determine_target_user(self, imported_word, target_user, auto_assign_user):
        """确定目标用户"""
        if target_user:
            return target_user

        if not auto_assign_user:
            # 如果没有指定用户且不自动分配，跳过
            return None

        # 自动分配用户逻辑
        # 1. 尝试从词库列表的创建者推断
        # 2. 使用第一个活跃用户
        # 3. 使用超级用户
        
        # 获取第一个活跃用户
        user = User.objects.filter(is_active=True).first()
        if not user:
            # 如果没有活跃用户，获取超级用户
            user = User.objects.filter(is_superuser=True).first()
        
        return user

    def create_word_from_imported(self, user, imported_word):
        """从ImportedVocabulary创建Word"""
        word = Word.objects.create(
            user=user,
            word=imported_word.word,
            phonetic=imported_word.phonetic or '',
            definition=imported_word.definition or '',
            part_of_speech=imported_word.part_of_speech or '',
            example=imported_word.example or '',
            note=self.build_note_from_imported(imported_word),
            tags=self.build_tags_from_imported(imported_word),
            created_at=imported_word.created_at
        )
        return word

    def overwrite_word(self, existing_word, imported_word):
        """覆盖现有单词"""
        existing_word.phonetic = imported_word.phonetic or existing_word.phonetic
        existing_word.definition = imported_word.definition or existing_word.definition
        existing_word.part_of_speech = imported_word.part_of_speech or existing_word.part_of_speech
        existing_word.example = imported_word.example or existing_word.example
        
        # 合并备注
        imported_note = self.build_note_from_imported(imported_word)
        if imported_note:
            if existing_word.note:
                existing_word.note = f"{existing_word.note}\n\n[导入更新]: {imported_note}"
            else:
                existing_word.note = f"[导入]: {imported_note}"
        
        # 合并标签
        imported_tags = self.build_tags_from_imported(imported_word)
        if imported_tags:
            existing_tags = existing_word.tag_list
            new_tags = [tag for tag in imported_tags.split(', ') if tag not in existing_tags]
            if new_tags:
                all_tags = existing_tags + new_tags
                existing_word.tags = ', '.join(all_tags)
        
        existing_word.save()

    def merge_word(self, existing_word, imported_word):
        """智能合并单词数据"""
        # 音标：优先使用非空值
        if imported_word.phonetic and not existing_word.phonetic:
            existing_word.phonetic = imported_word.phonetic
        
        # 释义：合并去重
        if imported_word.definition:
            existing_def = existing_word.definition or ''
            if imported_word.definition not in existing_def:
                if existing_def:
                    existing_word.definition = f"{existing_def}; {imported_word.definition}"
                else:
                    existing_word.definition = imported_word.definition
        
        # 词性：合并去重
        if imported_word.part_of_speech:
            existing_pos = existing_word.part_of_speech or ''
            if imported_word.part_of_speech not in existing_pos:
                if existing_pos:
                    pos_set = set(existing_pos.split(';') + [imported_word.part_of_speech])
                    existing_word.part_of_speech = ';'.join(sorted(filter(None, pos_set)))
                else:
                    existing_word.part_of_speech = imported_word.part_of_speech
        
        # 例句：合并
        if imported_word.example:
            if existing_word.example:
                if imported_word.example not in existing_word.example:
                    existing_word.example = f"{existing_word.example}\n\n{imported_word.example}"
            else:
                existing_word.example = imported_word.example
        
        # 备注：合并
        imported_note = self.build_note_from_imported(imported_word)
        if imported_note:
            if existing_word.note:
                existing_word.note = f"{existing_word.note}\n\n[导入合并]: {imported_note}"
            else:
                existing_word.note = f"[导入]: {imported_note}"
        
        # 标签：合并
        imported_tags = self.build_tags_from_imported(imported_word)
        if imported_tags:
            existing_tags = existing_word.tag_list
            new_tags = [tag for tag in imported_tags.split(', ') if tag not in existing_tags]
            if new_tags:
                all_tags = existing_tags + new_tags
                existing_word.tags = ', '.join(all_tags)
        
        existing_word.save()

    def build_note_from_imported(self, imported_word):
        """从ImportedVocabulary构建备注"""
        note_parts = []
        
        if imported_word.note:
            note_parts.append(imported_word.note)
        
        # 添加词库信息
        vocab_info = []
        if imported_word.textbook_version:
            vocab_info.append(f"教材: {imported_word.textbook_version}")
        if imported_word.grade:
            vocab_info.append(f"年级: {imported_word.grade}")
        if hasattr(imported_word, 'unit') and imported_word.unit:
            vocab_info.append(f"单元: {imported_word.unit}")
        if hasattr(imported_word, 'book_volume') and imported_word.book_volume:
            vocab_info.append(f"册数: {imported_word.book_volume}")
        
        if vocab_info:
            note_parts.append(f"来源: {', '.join(vocab_info)}")
        
        # 添加词库列表信息
        if imported_word.vocabulary_list:
            note_parts.append(f"词库: {imported_word.vocabulary_list.name}")
        
        return '\n'.join(note_parts)

    def build_tags_from_imported(self, imported_word):
        """从ImportedVocabulary构建标签"""
        tags = []
        
        # 添加年级标签
        if imported_word.grade:
            grade_names = {
                '1': '一年级', '2': '二年级', '3': '三年级', '4': '四年级',
                '5': '五年级', '6': '六年级', '7': '初一', '8': '初二',
                '9': '初三', '10': '高一', '11': '高二', '12': '高三'
            }
            grade_name = grade_names.get(imported_word.grade, f'{imported_word.grade}年级')
            tags.append(grade_name)
        
        # 添加教材标签
        if imported_word.textbook_version:
            tags.append(imported_word.textbook_version)
        
        # 添加词库标签
        if imported_word.vocabulary_list:
            tags.append(f"词库:{imported_word.vocabulary_list.name}")
        
        # 添加导入标签
        tags.append('导入单词')
        
        return ', '.join(tags) if tags else ''

    def create_conflict_resolution(self, existing_word, imported_word):
        """创建冲突解决记录"""
        resolution_data = {
            'imported_from': {
                'vocabulary_list': imported_word.vocabulary_list.name,
                'textbook_version': imported_word.textbook_version,
                'grade': imported_word.grade,
                'phonetic': imported_word.phonetic,
                'definition': imported_word.definition,
                'part_of_speech': imported_word.part_of_speech,
                'example': imported_word.example,
                'note': imported_word.note
            },
            'merge_strategy': 'auto_merge',
            'timestamp': timezone.now().isoformat()
        }
        
        ConflictResolution.objects.create(
            existing_word=existing_word,
            resolution_type='merge',
            resolution_data=resolution_data,
            notes=f"自动合并来自词库 {imported_word.vocabulary_list.name} 的数据"
        )

    def print_stats(self, stats, dry_run):
        """打印统计信息"""
        mode_text = "试运行" if dry_run else "实际执行"
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS(f'转换完成统计 ({mode_text}):'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'总处理数: {stats["total_processed"]}')
        self.stdout.write(f'创建单词数: {stats["words_created"]}')
        self.stdout.write(f'更新单词数: {stats["words_updated"]}')
        self.stdout.write(f'解决冲突数: {stats["conflicts_resolved"]}')
        self.stdout.write(f'跳过数: {stats["skipped"]}')
        self.stdout.write(f'错误数: {len(stats["errors"])}')
        
        if stats['errors']:
            self.stdout.write(self.style.WARNING('\n错误详情:'))
            for error in stats['errors'][:5]:
                self.stdout.write(f'  - {error}')
            if len(stats['errors']) > 5:
                self.stdout.write(f'  ... 还有 {len(stats["errors"]) - 5} 个错误')
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS('\n转换完成！现在"导入的单词"和"单词"已经统一。'))
        else:
            self.stdout.write(self.style.WARNING('\n试运行完成！使用 --dry-run=false 执行实际转换。'))