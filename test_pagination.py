#!/usr/bin/env python
"""
测试动态分页功能
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.words.models import Word, VocabularyList, WordSet
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite

User = get_user_model()

def test_dynamic_pagination():
    """测试动态分页功能"""
    print("=== 测试动态分页功能 ===")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    # 创建测试数据
    print("1. 创建测试数据...")
    
    # 创建测试词库列表
    from apps.words.models import VocabularySource
    source, created = VocabularySource.objects.get_or_create(
        name='测试来源',
        defaults={'description': '测试用词库来源'}
    )
    
    vocab_list, created = VocabularyList.objects.get_or_create(
        name='测试词库',
        defaults={
            'source': source,
            'description': '测试用词库',
            'is_active': True
        }
    )
    
    # 创建测试单词
    test_words = []
    for i in range(50):
        word, created = Word.objects.get_or_create(
            word=f'test_word_{i}',
            defaults={
                'vocabulary_list': vocab_list,
                'definition': f'测试单词{i}的定义',
                'part_of_speech': '名词',
                'grade': '1'
            }
        )
        test_words.append(word)
    
    # 创建测试单词集
    word_set, created = WordSet.objects.get_or_create(
        name='测试单词集',
        defaults={
            'description': '测试用单词集',
            'created_by': user
        }
    )
    
    print(f"   创建了 {len(test_words)} 个测试单词")
    print(f"   创建了 1 个测试词库列表")
    print(f"   创建了 1 个测试单词集")
    
    # 测试分页功能
    print("\n2. 测试分页功能...")
    
    # 模拟请求
    factory = RequestFactory()
    
    # 测试不同分页大小
    test_cases = [
        {'show': '10', 'expected': 10},
        {'show': '20', 'expected': 20},
        {'show': '50', 'expected': 50},
        {'show': 'all', 'expected': len(test_words)},  # 应该显示所有测试单词
    ]
    
    for test_case in test_cases:
        print(f"   测试每页显示 {test_case['show']} 条记录...")
        
        # 模拟GET请求
        request = factory.get(f'/admin/words/word/?show={test_case["show"]}')
        request.user = user
        
        # 获取查询集
        from apps.words.admin import WordAdmin
        admin_site = AdminSite()
        word_admin = WordAdmin(Word, admin_site)
        
        # 获取分页器
        queryset = Word.objects.filter(word__startswith='test_word_')
        paginator = word_admin.get_paginator(request, queryset, word_admin.list_per_page)
        
        if test_case['show'] == 'all':
            # 显示全部记录
            page_obj = paginator.get_page(1)
            actual_count = len(page_obj.object_list)
        else:
            # 显示指定数量
            page_obj = paginator.get_page(1)
            actual_count = len(page_obj.object_list)
        
        print(f"     预期: {test_case['expected']} 条")
        print(f"     实际: {actual_count} 条")
        
        if actual_count == test_case['expected']:
            print("     ✅ 通过")
        else:
            print("     ❌ 失败")
    
    print("\n3. 测试URL参数处理...")
    
    # 测试URL参数
    test_urls = [
        '/admin/words/word/?show=10',
        '/admin/words/word/?show=20&p=2',
        '/admin/words/word/?show=all',
        '/admin/words/word/?show=50&search=test',
    ]
    
    for url in test_urls:
        print(f"   测试URL: {url}")
        request = factory.get(url)
        request.user = user
        
        # 测试changelist_view方法
        try:
            response = word_admin.changelist_view(request)
            print("     ✅ URL处理正常")
        except Exception as e:
            print(f"     ❌ URL处理失败: {e}")
    
    print("\n4. 清理测试数据...")
    
    # 清理测试数据
    Word.objects.filter(word__startswith='test_word_').delete()
    VocabularyList.objects.filter(name='测试词库').delete()
    WordSet.objects.filter(name='测试单词集').delete()
    VocabularySource.objects.filter(name='测试来源').delete()
    User.objects.filter(username='test_user').delete()
    
    print("   测试数据已清理")
    print("\n✅ 动态分页功能测试完成！")

if __name__ == '__main__':
    test_dynamic_pagination() 