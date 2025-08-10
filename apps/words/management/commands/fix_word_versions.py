from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from apps.words.models import Word
from collections import defaultdict
import json


class Command(BaseCommand):
    help = '修复现有单词的版本数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要进行的修改，不实际执行'
        )
        parser.add_argument(
            '--word',
            type=str,
            help='指定要修复的单词（可选）'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        specific_word = options.get('word')
        
        self.stdout.write('开始修复单词版本数据...')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN 模式 - 不会实际修改数据'))
        
        # 获取所有单词，按单词名称分组
        if specific_word:
            words = Word.objects.filter(word=specific_word).order_by('created_at')
            self.stdout.write(f'处理单词: {specific_word}')
        else:
            words = Word.objects.all().order_by('word', 'created_at')
            self.stdout.write('处理所有单词...')
        
        # 按单词名称分组
        word_groups = defaultdict(list)
        for word in words:
            word_groups[word.word].append(word)
        
        total_fixed = 0
        total_groups = len(word_groups)
        
        for word_name, word_list in word_groups.items():
            if len(word_list) == 1:
                # 单个单词，设置为版本1
                word = word_list[0]
                if self.fix_single_word(word, dry_run):
                    total_fixed += 1
            else:
                # 多个单词，需要版本管理
                if self.fix_multiple_words(word_list, dry_run):
                    total_fixed += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'版本数据修复完成！共处理 {total_groups} 个单词组，修复 {total_fixed} 个'
            )
        )
    
    def fix_single_word(self, word, dry_run):
        """修复单个单词的版本数据"""
        changes = []
        
        # 检查并修复版本号
        if word.version_number != 1:
            changes.append(f'版本号: {word.version_number} -> 1')
            if not dry_run:
                word.version_number = 1
        
        # 检查并修复主单词引用
        if word.parent_word is not None:
            changes.append(f'主单词引用: {word.parent_word.pk} -> None')
            if not dry_run:
                word.parent_word = None
        
        # 检查并修复多版本标记
        if word.has_multiple_versions:
            changes.append('多版本标记: True -> False')
            if not dry_run:
                word.has_multiple_versions = False
        
        # 检查并修复版本数据
        if word.version_data:
            changes.append('清空版本数据')
            if not dry_run:
                word.version_data = {}
        
        if changes:
            self.stdout.write(f'修复单词 "{word.word}": {", ".join(changes)}')
            if not dry_run:
                word.save()
            return True
        
        return False
    
    def fix_multiple_words(self, word_list, dry_run):
        """修复多个同名单词的版本数据"""
        word_name = word_list[0].word
        self.stdout.write(f'处理多版本单词 "{word_name}" (共 {len(word_list)} 个)')
        
        # 按创建时间排序
        word_list.sort(key=lambda w: w.created_at)
        
        # 第一个单词作为主单词
        main_word = word_list[0]
        versions = word_list[1:]
        
        changes = []
        
        # 修复主单词
        if main_word.version_number != 1:
            changes.append(f'主单词版本号: {main_word.version_number} -> 1')
            if not dry_run:
                main_word.version_number = 1
        
        if main_word.parent_word is not None:
            changes.append(f'主单词引用: {main_word.parent_word.pk} -> None')
            if not dry_run:
                main_word.parent_word = None
        
        if not main_word.has_multiple_versions:
            changes.append('主单词多版本标记: False -> True')
            if not dry_run:
                main_word.has_multiple_versions = True
        
        # 清空主单词的版本数据
        if main_word.version_data:
            changes.append('清空主单词版本数据')
            if not dry_run:
                main_word.version_data = {}
        
        # 修复版本单词
        for i, version in enumerate(versions, start=2):
            version_changes = []
            
            # 设置版本号
            if version.version_number != i:
                version_changes.append(f'版本号: {version.version_number} -> {i}')
                if not dry_run:
                    version.version_number = i
            
            # 设置主单词引用
            if version.parent_word != main_word:
                version_changes.append(f'主单词引用: {version.parent_word.pk if version.parent_word else None} -> {main_word.pk}')
                if not dry_run:
                    version.parent_word = main_word
            
            # 设置多版本标记
            if version.has_multiple_versions:
                version_changes.append('多版本标记: True -> False')
                if not dry_run:
                    version.has_multiple_versions = False
            
            # 更新版本数据
            version_data = {
                'parent_word_id': main_word.pk,
                'differences': self.get_differences_from_main(version, main_word),
                'created_as_version': True,
                'fix_timestamp': timezone.now().isoformat()
            }
            
            if version.version_data != version_data:
                version_changes.append('更新版本数据')
                if not dry_run:
                    version.version_data = version_data
            
            if version_changes:
                changes.append(f'版本 {i}: {", ".join(version_changes)}')
        
        if changes:
            self.stdout.write(f'修复单词 "{word_name}": {", ".join(changes)}')
            if not dry_run:
                # 保存所有修改
                main_word.save()
                for version in versions:
                    version.save()
            return True
        
        return False
    
    def get_differences_from_main(self, version, main_word):
        """获取版本与主单词的差异"""
        differences = {}
        fields_to_compare = ['phonetic', 'definition', 'part_of_speech', 'example', 'note']
        
        for field in fields_to_compare:
            version_value = getattr(version, field)
            main_value = getattr(main_word, field)
            
            if version_value != main_value:
                differences[field] = {
                    'current': version_value,
                    'main': main_value
                }
        
        return differences 