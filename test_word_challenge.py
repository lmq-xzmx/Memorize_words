#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单词斩页面功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.words.models import Word

User = get_user_model()

def test_word_challenge_page():
    """测试单词斩页面"""
    print("=" * 50)
    print("测试单词斩页面")
    print("=" * 50)
    
    # 创建测试客户端
    client = Client()
    
    # 获取或创建测试用户
    try:
        user = User.objects.get(username='testuser')
        print(f"使用现有用户: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"创建新用户: {user.username}")
    
    # 获取现有的单词
    existing_words = Word.objects.all()[:10]  # 获取前10个单词
    print(f"找到 {existing_words.count()} 个现有单词")
    
    # 更新一些单词的掌握度用于测试
    for i, word in enumerate(existing_words):
        word.mastery_level = (i + 1) * 10  # 设置不同的掌握度
        word.save()
        print(f"更新单词: {word.word} - 掌握度: {word.mastery_level}%")
    
    created_words = list(existing_words)
    
    print(f"总共创建了 {len(created_words)} 个测试单词")
    
    # 登录用户
    client.force_login(user)
    
    # 测试访问单词斩页面
    print("\n测试访问单词斩页面...")
    response = client.get('/words/word-challenge/')
    
    if response.status_code == 200:
        print("✅ 单词斩页面访问成功")
        print(f"页面标题: {response.context.get('title', 'N/A')}")
        
        # 检查上下文数据
        context = response.context
        print(f"总单词数: {context.get('total_words', 0)}")
        print(f"已掌握单词数: {context.get('learned_words', 0)}")
        print(f"学习进度: {context.get('learning_progress', 0)}%")
        print(f"挑战单词数: {len(context.get('challenge_words', []))}")
        
        # 检查模板内容
        content = response.content.decode('utf-8')
        if '单词斩' in content:
            print("✅ 页面包含正确的标题")
        if '今日挑战' in content:
            print("✅ 页面包含挑战区域")
        if '学习建议' in content:
            print("✅ 页面包含学习建议")
            
    else:
        print(f"❌ 单词斩页面访问失败，状态码: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"错误内容: {response.content.decode('utf-8')}")
    
    # 测试API端点
    print("\n测试API端点...")
    
    # 测试标记为已掌握
    if created_words:
        word = created_words[0]
        response = client.post(f'/words/api/words/{word.id}/mark_learned/', {})
        if response.status_code == 200:
            print("✅ 标记为已掌握API测试成功")
        else:
            print(f"❌ 标记为已掌握API测试失败，状态码: {response.status_code}")
    
    # 测试更新掌握度
    if len(created_words) > 1:
        word = created_words[1]
        response = client.post(f'/words/api/words/{word.id}/update_mastery/', 
                             {'mastery_level': 2}, 
                             content_type='application/json')
        if response.status_code == 200:
            print("✅ 更新掌握度API测试成功")
        else:
            print(f"❌ 更新掌握度API测试失败，状态码: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_word_challenge_page() 