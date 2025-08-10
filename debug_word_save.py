#!/usr/bin/env python
"""
调试Word模型保存问题的脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.words.models import Word, VocabularyList, VocabularySource
from apps.accounts.models import CustomUser
from django.db import transaction

def test_word_save():
    """测试Word模型的保存功能"""
    print("开始测试Word模型保存...")
    
    try:
        # 创建测试用户
        user, created = CustomUser.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        print(f"测试用户: {user.username} ({'新创建' if created else '已存在'})")
        
        # 创建词库来源和列表
        source, created = VocabularySource.objects.get_or_create(
            name='测试来源',
            defaults={'description': '用于测试的词库来源'}
        )
        print(f"词库来源: {source.name} ({'新创建' if created else '已存在'})")
        
        vocab_list, created = VocabularyList.objects.get_or_create(
            name='测试词库',
            defaults={
                'source': source,
                'description': '用于测试的词库列表'
            }
        )
        print(f"词库列表: {vocab_list.name} ({'新创建' if created else '已存在'})")
        
        # 测试1: 创建基本单词
        print("\n=== 测试1: 创建基本单词 ===")
        try:
            word1 = Word.objects.create(
                word='test',
                phonetic='/test/',
                definition='测试',
                part_of_speech='名词',
                vocabulary_list=vocab_list,
                user=user
            )
            print(f"✓ 成功创建单词: {word1}")
        except Exception as e:
            print(f"✗ 创建单词失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试2: 创建可能冲突的单词
        print("\n=== 测试2: 创建可能冲突的单词 ===")
        try:
            word2 = Word.objects.create(
                word='test',
                phonetic='/test2/',
                definition='测试2',
                part_of_speech='动词',
                vocabulary_list=vocab_list,
                user=user
            )
            print(f"✓ 成功创建冲突单词: {word2}")
            print(f"  冲突状态: {word2.has_conflict}")
            print(f"  冲突数据: {word2.conflict_data}")
        except Exception as e:
            print(f"✗ 创建冲突单词失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试3: 更新单词
        print("\n=== 测试3: 更新单词 ===")
        try:
            existing_word = Word.objects.filter(word='test').first()
            if existing_word:
                existing_word.definition = '更新的定义'
                existing_word.save()
                print(f"✓ 成功更新单词: {existing_word}")
            else:
                print("✗ 没有找到要更新的单词")
        except Exception as e:
            print(f"✗ 更新单词失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试4: 批量创建
        print("\n=== 测试4: 批量创建单词 ===")
        try:
            words_to_create = []
            for i in range(5):
                words_to_create.append(Word(
                    word=f'batch_test_{i}',
                    phonetic=f'/batch_test_{i}/',
                    definition=f'批量测试单词{i}',
                    vocabulary_list=vocab_list,
                    user=user
                ))
            
            created_words = Word.objects.bulk_create(words_to_create)
            print(f"✓ 成功批量创建 {len(created_words)} 个单词")
        except Exception as e:
            print(f"✗ 批量创建失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 显示统计信息
        print("\n=== 统计信息 ===")
        total_words = Word.objects.count()
        conflict_words = Word.objects.filter(has_conflict=True).count()
        print(f"总单词数: {total_words}")
        print(f"冲突单词数: {conflict_words}")
        
        # 显示最近创建的单词
        print("\n=== 最近创建的单词 ===")
        recent_words = Word.objects.order_by('-created_at')[:10]
        for word in recent_words:
            print(f"- {word.word}: {word.definition[:50]}... (冲突: {word.has_conflict})")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_word_save()