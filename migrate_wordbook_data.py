#!/usr/bin/env python
"""
将wordbook_backend中的单词数据迁移到Natural_English项目

使用方法:
python migrate_wordbook_data.py --source /path/to/wordbook_backend --action [import_words|import_vocabulary|sync_all]

参数说明:
--source: wordbook_backend项目的路径
--action: 迁移动作
  - import_words: 将wordbook_backend中的Word模型数据导入到Natural_English的Word模型
  - import_vocabulary: 将wordbook_backend中的ImportedVocabulary数据导入到Natural_English
  - sync_all: 同步所有数据
--user-mapping: 用户映射文件(JSON格式)，用于映射两个项目中的用户
"""

import os
import sys
import json
import django
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone

# 添加Django项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

# 导入Natural_English的模型
from apps.words.models import (
    Word, VocabularySource, VocabularyList, ImportedVocabulary, 
    UserStreak, ConflictResolution, StudySession
)

class WordbookDataMigrator:
    """wordbook_backend数据迁移器"""
    
    def __init__(self, wordbook_path, user_mapping=None):
        self.wordbook_path = Path(wordbook_path)
        self.user_mapping = user_mapping or {}
        self.stats = {
            'users_created': 0,
            'words_imported': 0,
            'vocabulary_lists_imported': 0,
            'imported_vocabulary_imported': 0,
            'conflicts_detected': 0,
            'errors': []
        }
        
        # 设置wordbook_backend的Django环境
        self.setup_wordbook_environment()
    
    def setup_wordbook_environment(self):
        """设置wordbook_backend的Django环境"""
        wordbook_manage_py = self.wordbook_path / 'manage.py'
        if not wordbook_manage_py.exists():
            raise FileNotFoundError(f"wordbook_backend项目路径无效: {self.wordbook_path}")
        
        # 添加wordbook_backend到Python路径
        sys.path.insert(0, str(self.wordbook_path))
        
        # 设置wordbook的Django设置
        os.environ['WORDBOOK_SETTINGS_MODULE'] = 'wordbook.settings'
        
        # 动态导入wordbook的模型
        try:
            from apps.words.models import (
                Word as WordbookWord,
                VocabularySource as WordbookVocabularySource,
                VocabularyList as WordbookVocabularyList,
                ImportedVocabulary as WordbookImportedVocabulary,
                UserStreak as WordbookUserStreak
            )
            
            self.wordbook_models = {
                'Word': WordbookWord,
                'VocabularySource': WordbookVocabularySource,
                'VocabularyList': WordbookVocabularyList,
                'ImportedVocabulary': WordbookImportedVocabulary,
                'UserStreak': WordbookUserStreak
            }
            
            print(f"✓ 成功连接到wordbook_backend: {self.wordbook_path}")
            
        except ImportError as e:
            raise ImportError(f"无法导入wordbook_backend模型: {e}")
    
    def get_or_create_user(self, wordbook_user):
        """获取或创建用户映射"""
        # 检查用户映射
        if str(wordbook_user.id) in self.user_mapping:
            target_user_id = self.user_mapping[str(wordbook_user.id)]
            try:
                return User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                pass
        
        # 尝试通过用户名匹配
        try:
            return User.objects.get(username=wordbook_user.username)
        except User.DoesNotExist:
            pass
        
        # 尝试通过邮箱匹配
        if wordbook_user.email:
            try:
                return User.objects.get(email=wordbook_user.email)
            except User.DoesNotExist:
                pass
        
        # 创建新用户
        new_user = User.objects.create_user(
            username=f"{wordbook_user.username}_migrated",
            email=wordbook_user.email or f"{wordbook_user.username}@migrated.local",
            first_name=wordbook_user.first_name,
            last_name=wordbook_user.last_name,
            is_active=wordbook_user.is_active
        )
        self.stats['users_created'] += 1
        print(f"✓ 创建新用户: {new_user.username}")
        return new_user
    
    def import_words(self):
        """导入wordbook_backend中的Word数据"""
        print("\n开始导入单词数据...")
        
        WordbookWord = self.wordbook_models['Word']
        wordbook_words = WordbookWord.objects.all()
        
        with transaction.atomic():
            for wb_word in wordbook_words:
                try:
                    # 获取或创建用户
                    user = self.get_or_create_user(wb_word.user)
                    
                    # 检查是否已存在相同单词
                    existing_word = Word.objects.filter(
                        user=user, 
                        word=wb_word.word
                    ).first()
                    
                    if existing_word:
                        # 处理冲突
                        self.handle_word_conflict(existing_word, wb_word, user)
                        continue
                    
                    # 创建新单词
                    new_word = Word.objects.create(
                        user=user,
                        word=wb_word.word,
                        phonetic=wb_word.phonetic or '',
                        definition=wb_word.definition or '',
                        example=wb_word.example or '',
                        note=wb_word.note or '',
                        is_learned=wb_word.is_learned,
                        learned_at=wb_word.learned_at,
                        created_at=wb_word.created_at,
                        updated_at=wb_word.updated_at
                    )
                    
                    self.stats['words_imported'] += 1
                    
                    if self.stats['words_imported'] % 100 == 0:
                        print(f"已导入 {self.stats['words_imported']} 个单词...")
                        
                except Exception as e:
                    error_msg = f"导入单词失败 {wb_word.word}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"✗ {error_msg}")
        
        print(f"✓ 单词导入完成，共导入 {self.stats['words_imported']} 个单词")
    
    def handle_word_conflict(self, existing_word, wordbook_word, user):
        """处理单词冲突"""
        # 创建冲突解决记录
        conflict_data = {
            'existing': {
                'phonetic': existing_word.phonetic,
                'definition': existing_word.definition,
                'example': existing_word.example,
                'note': existing_word.note,
                'is_learned': existing_word.is_learned,
                'learned_at': existing_word.learned_at.isoformat() if existing_word.learned_at else None
            },
            'imported': {
                'phonetic': wordbook_word.phonetic or '',
                'definition': wordbook_word.definition or '',
                'example': wordbook_word.example or '',
                'note': wordbook_word.note or '',
                'is_learned': wordbook_word.is_learned,
                'learned_at': wordbook_word.learned_at.isoformat() if wordbook_word.learned_at else None
            }
        }
        
        # 智能合并策略
        merged_data = self.merge_word_data(existing_word, wordbook_word)
        
        # 更新现有单词
        for field, value in merged_data.items():
            setattr(existing_word, field, value)
        existing_word.save()
        
        # 记录冲突
        ConflictResolution.objects.create(
            existing_word=existing_word,
            resolution_type='merge',
            resolution_data=conflict_data,
            notes=f"自动合并来自wordbook_backend的数据"
        )
        
        self.stats['conflicts_detected'] += 1
    
    def merge_word_data(self, existing_word, wordbook_word):
        """智能合并单词数据"""
        merged = {}
        
        # 音标：优先使用非空值
        if wordbook_word.phonetic and not existing_word.phonetic:
            merged['phonetic'] = wordbook_word.phonetic
        
        # 释义：合并去重
        existing_def = existing_word.definition or ''
        imported_def = wordbook_word.definition or ''
        if imported_def and imported_def not in existing_def:
            if existing_def:
                merged['definition'] = f"{existing_def}; {imported_def}"
            else:
                merged['definition'] = imported_def
        
        # 例句：合并去重
        existing_example = existing_word.example or ''
        imported_example = wordbook_word.example or ''
        if imported_example and imported_example not in existing_example:
            if existing_example:
                merged['example'] = f"{existing_example}\n\n{imported_example}"
            else:
                merged['example'] = imported_example
        
        # 笔记：合并
        existing_note = existing_word.note or ''
        imported_note = wordbook_word.note or ''
        if imported_note and imported_note not in existing_note:
            if existing_note:
                merged['note'] = f"{existing_note}\n\n[来自wordbook]: {imported_note}"
            else:
                merged['note'] = f"[来自wordbook]: {imported_note}"
        
        # 学习状态：保持最新的学习状态
        if wordbook_word.is_learned and not existing_word.is_learned:
            merged['is_learned'] = True
            merged['learned_at'] = wordbook_word.learned_at or timezone.now()
        
        return merged
    
    def import_vocabulary_data(self):
        """导入词库数据"""
        print("\n开始导入词库数据...")
        
        # 导入词库来源
        self.import_vocabulary_sources()
        
        # 导入词库列表
        self.import_vocabulary_lists()
        
        # 导入导入的词汇
        self.import_imported_vocabulary()
    
    def import_vocabulary_sources(self):
        """导入词库来源"""
        WordbookVocabularySource = self.wordbook_models['VocabularySource']
        
        for wb_source in WordbookVocabularySource.objects.all():
            source, created = VocabularySource.objects.get_or_create(
                name=wb_source.name,
                defaults={
                    'description': wb_source.description,
                    'created_at': wb_source.created_at
                }
            )
            if created:
                print(f"✓ 创建词库来源: {source.name}")
    
    def import_vocabulary_lists(self):
        """导入词库列表"""
        WordbookVocabularyList = self.wordbook_models['VocabularyList']
        
        for wb_list in WordbookVocabularyList.objects.all():
            try:
                # 获取对应的词库来源
                source = None
                if wb_list.source:
                    source = VocabularySource.objects.get(name=wb_list.source.name)
                
                vocab_list, created = VocabularyList.objects.get_or_create(
                    name=wb_list.name,
                    source=source,
                    defaults={
                        'description': wb_list.description,
                        'is_active': getattr(wb_list, 'is_active', True),
                        'word_count': wb_list.word_count,
                        'created_at': wb_list.created_at
                    }
                )
                
                if created:
                    self.stats['vocabulary_lists_imported'] += 1
                    print(f"✓ 创建词库列表: {vocab_list.name}")
                    
            except Exception as e:
                error_msg = f"导入词库列表失败 {wb_list.name}: {str(e)}"
                self.stats['errors'].append(error_msg)
                print(f"✗ {error_msg}")
    
    def import_imported_vocabulary(self):
        """导入导入的词汇数据"""
        WordbookImportedVocabulary = self.wordbook_models['ImportedVocabulary']
        
        with transaction.atomic():
            for wb_vocab in WordbookImportedVocabulary.objects.all():
                try:
                    # 获取对应的词库列表
                    vocab_list = VocabularyList.objects.get(
                        name=wb_vocab.vocabulary_list.name
                    )
                    
                    # 检查是否已存在
                    existing = ImportedVocabulary.objects.filter(
                        vocabulary_list=vocab_list,
                        word=wb_vocab.word
                    ).first()
                    
                    if existing:
                        # 更新冲突数据
                        self.update_imported_vocabulary_conflict(existing, wb_vocab)
                        continue
                    
                    # 创建新的导入词汇记录
                    ImportedVocabulary.objects.create(
                        vocabulary_list=vocab_list,
                        word=wb_vocab.word,
                        phonetic=wb_vocab.phonetic or '',
                        definition=wb_vocab.definition or '',
                        part_of_speech=wb_vocab.part_of_speech or '',
                        textbook_version=getattr(wb_vocab, 'textbook_version', ''),
                        grade=getattr(wb_vocab, 'grade', ''),
                        example=getattr(wb_vocab, 'example', ''),
                        note=getattr(wb_vocab, 'official_note', '') or getattr(wb_vocab, 'user_note', ''),
                        has_conflict=wb_vocab.has_conflict,
                        conflict_data=wb_vocab.conflict_data,
                        conflict_resolved=wb_vocab.conflict_resolved,
                        created_at=wb_vocab.created_at if hasattr(wb_vocab, 'created_at') else timezone.now()
                    )
                    
                    self.stats['imported_vocabulary_imported'] += 1
                    
                    if self.stats['imported_vocabulary_imported'] % 500 == 0:
                        print(f"已导入 {self.stats['imported_vocabulary_imported']} 个词汇...")
                        
                except Exception as e:
                    error_msg = f"导入词汇失败 {wb_vocab.word}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"✗ {error_msg}")
        
        print(f"✓ 词汇导入完成，共导入 {self.stats['imported_vocabulary_imported']} 个词汇")
    
    def update_imported_vocabulary_conflict(self, existing, wordbook_vocab):
        """更新导入词汇的冲突数据"""
        # 合并冲突数据
        conflict_data = existing.conflict_data or {}
        wb_conflict_data = wordbook_vocab.conflict_data or {}
        
        # 添加来自wordbook的冲突数据
        if wb_conflict_data:
            conflict_data['wordbook_import'] = {
                'timestamp': timezone.now().isoformat(),
                'data': wb_conflict_data
            }
            
            existing.conflict_data = conflict_data
            existing.has_conflict = True
            existing.save()
            
            self.stats['conflicts_detected'] += 1
    
    def sync_all(self):
        """同步所有数据"""
        print("开始完整数据同步...")
        
        # 导入词库数据
        self.import_vocabulary_data()
        
        # 导入单词数据
        self.import_words()
        
        # 打印统计信息
        self.print_stats()
    
    def print_stats(self):
        """打印统计信息"""
        print("\n" + "="*50)
        print("数据迁移完成统计:")
        print("="*50)
        print(f"创建用户数: {self.stats['users_created']}")
        print(f"导入单词数: {self.stats['words_imported']}")
        print(f"导入词库列表数: {self.stats['vocabulary_lists_imported']}")
        print(f"导入词汇数: {self.stats['imported_vocabulary_imported']}")
        print(f"检测到冲突数: {self.stats['conflicts_detected']}")
        print(f"错误数: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\n错误详情:")
            for error in self.stats['errors'][:10]:  # 只显示前10个错误
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... 还有 {len(self.stats['errors']) - 10} 个错误")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='迁移wordbook_backend数据到Natural_English')
    parser.add_argument('--source', required=True, help='wordbook_backend项目路径')
    parser.add_argument('--action', choices=['import_words', 'import_vocabulary', 'sync_all'], 
                       default='sync_all', help='迁移动作')
    parser.add_argument('--user-mapping', help='用户映射文件路径(JSON格式)')
    
    args = parser.parse_args()
    
    # 加载用户映射
    user_mapping = {}
    if args.user_mapping and os.path.exists(args.user_mapping):
        with open(args.user_mapping, 'r', encoding='utf-8') as f:
            user_mapping = json.load(f)
    
    # 创建迁移器
    migrator = WordbookDataMigrator(args.source, user_mapping)
    
    # 执行迁移
    if args.action == 'import_words':
        migrator.import_words()
    elif args.action == 'import_vocabulary':
        migrator.import_vocabulary_data()
    elif args.action == 'sync_all':
        migrator.sync_all()
    
    migrator.print_stats()


if __name__ == '__main__':
    main()