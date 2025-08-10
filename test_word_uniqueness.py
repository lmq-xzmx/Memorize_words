#!/usr/bin/env python
"""
测试单词唯一性和变体功能
"""

import os
import sys
import django
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.words.models import Word, VocabularyList, VocabularySource

def test_word_uniqueness():
    """测试单词唯一性和变体功能"""
    print("=== 测试单词唯一性和变体功能 ===")
    
    # 创建测试词库
    source, _ = VocabularySource.objects.get_or_create(
        name="测试词库来源",
        defaults={'description': '用于测试单词唯一性的词库来源'}
    )
    
    vocab_list, _ = VocabularyList.objects.get_or_create(
        name="测试词库列表",
        defaults={
            'source': source,
            'description': '用于测试单词唯一性的词库列表',
            'is_active': True
        }
    )
    
    # 清理之前的测试数据
    Word.objects.filter(word="test").delete()
    
    print("\n1. 创建第一个单词（主单词）")
    word1 = Word.objects.create(
        word="test",
        phonetic="/test/",
        definition="第一个定义",
        part_of_speech="noun",
        example="This is a test.",
        vocabulary_list=vocab_list
    )
    print(f"创建单词: {word1.word}, ID: {word1.pk}, 是否变体: {word1.is_variant}")
    
    print("\n2. 创建第二个相同单词（应该成为变体）")
    word2 = Word.objects.create(
        word="test",
        phonetic="/tɛst/",
        definition="第二个定义",
        part_of_speech="verb",
        example="Let's test this.",
        vocabulary_list=vocab_list
    )
    print(f"创建单词: {word2.word}, ID: {word2.pk}, 是否变体: {word2.is_variant}")
    if word2.parent_word:
        print(f"父单词: {word2.parent_word.word}, ID: {word2.parent_word.pk}")
    
    print("\n3. 创建第三个相同单词（应该成为变体）")
    word3 = Word.objects.create(
        word="test",
        phonetic="/test/",
        definition="第一个定义",  # 相同定义
        part_of_speech="noun",
        example="Another test example.",
        vocabulary_list=vocab_list
    )
    print(f"创建单词: {word3.word}, ID: {word3.pk}, 是否变体: {word3.is_variant}")
    if word3.parent_word:
        print(f"父单词: {word3.parent_word.word}, ID: {word3.parent_word.pk}")
    
    print("\n4. 检查主单词的变体")
    # 重新获取word1以确保数据是最新的
    word1.refresh_from_db()
    variants = word1.get_all_variants()
    print(f"主单词 {word1.word} 的变体数量: {variants.count()}")
    for variant in variants:
        print(f"  - 变体ID: {variant.pk}, 定义: {variant.definition}, 词性: {variant.part_of_speech}")
    
    print("\n5. 检查冲突数据")
    for word in [word1, word2, word3]:
        word.refresh_from_db()
        print(f"单词ID {word.pk}: 有冲突={word.has_conflict}, 冲突数据={word.conflict_data}")
    
    print("\n=== 测试完成 ===")
    return word1, word2, word3

if __name__ == '__main__':
    test_word_uniqueness()