#!/usr/bin/env python3
"""
清理重复的Word记录脚本

这个脚本会：
1. 找到所有重复的Word记录
2. 对于每个重复的单词，保留最早创建的记录
3. 将其他重复记录的WordEntry转移到保留的Word记录上
4. 删除重复的Word记录
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.words.models import Word, WordEntry
from django.db.models import Count
from django.db import transaction

def clean_duplicate_words():
    """清理重复的Word记录"""
    print("开始清理重复的Word记录...")
    
    # 查找所有重复的单词
    duplicates = Word.objects.values('word').annotate(count=Count('word')).filter(count__gt=1)
    total_duplicates = duplicates.count()
    
    print(f"发现 {total_duplicates} 个重复的单词")
    
    cleaned_count = 0
    deleted_count = 0
    
    with transaction.atomic():
        for dup in duplicates:
            word_text = dup['word']
            duplicate_words = Word.objects.filter(word=word_text).order_by('created_at')
            
            if duplicate_words.count() <= 1:
                continue
                
            # 保留最早创建的Word记录
            primary_word = duplicate_words.first()
            duplicate_words_to_delete = duplicate_words[1:]
            
            print(f"处理单词: {word_text} (保留ID: {primary_word.id}, 删除 {len(duplicate_words_to_delete)} 个重复记录)")
            
            # 将重复记录的WordEntry转移到主记录
            for word_to_delete in duplicate_words_to_delete:
                # 转移WordEntry
                entries_to_transfer = WordEntry.objects.filter(word=word_to_delete)
                for entry in entries_to_transfer:
                    entry.word = primary_word
                    entry.save()
                
                # 删除重复的Word记录
                word_to_delete.delete()
                deleted_count += 1
            
            cleaned_count += 1
            
            if cleaned_count % 100 == 0:
                print(f"已处理 {cleaned_count}/{total_duplicates} 个重复单词")
    
    print(f"清理完成！")
    print(f"- 处理了 {cleaned_count} 个重复单词")
    print(f"- 删除了 {deleted_count} 个重复的Word记录")
    
    # 验证清理结果
    remaining_duplicates = Word.objects.values('word').annotate(count=Count('word')).filter(count__gt=1).count()
    print(f"- 剩余重复单词: {remaining_duplicates}")

if __name__ == '__main__':
    clean_duplicate_words()