#!/usr/bin/env python
"""
测试vocabulary_manager的URL和功能
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.vocabulary_manager.models import LearningGoal
from apps.words.models import VocabularyList, VocabularySource

User = get_user_model()

def test_vocabulary_manager_urls():
    """测试vocabulary_manager的URL和功能"""
    print("=== 测试vocabulary_manager的URL和功能 ===")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    # 创建测试词库来源
    source, created = VocabularySource.objects.get_or_create(
        name='测试来源',
        defaults={'description': '测试用词库来源'}
    )
    
    # 创建测试词库列表
    vocab_list, created = VocabularyList.objects.get_or_create(
        name='测试词库',
        defaults={
            'source': source,
            'description': '测试用词库',
            'is_active': True
        }
    )
    
    # 创建学习目标
    learning_goal, created = LearningGoal.objects.get_or_create(
        user=user,
        name='测试学习目标',
        defaults={
            'description': '用于测试的学习目标',
            'goal_type': 'vocabulary_list',
            'vocabulary_list': vocab_list,
            'is_current': True
        }
    )
    
    print("1. 创建测试数据...")
    print(f"   创建了测试用户: {user.username}")
    print(f"   创建了测试词库: {vocab_list.name}")
    print(f"   创建了学习目标: {learning_goal.name}")
    
    # 创建Django测试客户端
    client = Client()
    
    # 登录用户
    client.force_login(user)
    
    print("\n2. 测试URL访问...")
    
    # 测试URL列表
    test_urls = [
        {
            'name': '成长中心主页',
            'url': '/vocabulary-manager/',
            'expected_status': 200
        },
        {
            'name': '学习目标列表',
            'url': '/vocabulary-manager/goals/',
            'expected_status': 200
        },
        {
            'name': '学习计划列表',
            'url': '/vocabulary-manager/plans/',
            'expected_status': 200
        },
        {
            'name': '学习中（看板）',
            'url': '/vocabulary-manager/kanban/',
            'expected_status': 200
        },
        {
            'name': '学习统计',
            'url': '/vocabulary-manager/statistics/',
            'expected_status': 200
        }
    ]
    
    for test_url in test_urls:
        try:
            response = client.get(test_url['url'])
            status = response.status_code
            success = status == test_url['expected_status']
            status_icon = "✅" if success else "❌"
            
            print(f"   {status_icon} {test_url['name']}: {test_url['url']}")
            print(f"      状态码: {status} (期望: {test_url['expected_status']})")
            
            if success:
                print(f"      ✅ 访问成功")
            else:
                print(f"      ❌ 访问失败")
                
        except Exception as e:
            print(f"   ❌ {test_url['name']}: {test_url['url']}")
            print(f"      错误: {e}")
    
    print("\n3. 检查页面内容...")
    
    # 检查成长中心主页是否包含"学习中（看板）"按钮
    try:
        response = client.get('/vocabulary-manager/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if '学习中（看板）' in content:
                print("   ✅ 成长中心主页包含'学习中（看板）'按钮")
            else:
                print("   ❌ 成长中心主页不包含'学习中（看板）'按钮")
                print("      页面内容片段:")
                print("      " + content[:200] + "...")
        else:
            print(f"   ❌ 成长中心主页访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 检查页面内容时出错: {e}")
    
    print("\n4. 测试看板页面...")
    
    try:
        response = client.get('/vocabulary-manager/kanban/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if '学习中（看板）' in content:
                print("   ✅ 看板页面标题正确")
            else:
                print("   ❌ 看板页面标题不正确")
            
            if '九宫格' in content or '看板' in content:
                print("   ✅ 看板页面包含看板内容")
            else:
                print("   ❌ 看板页面不包含看板内容")
        else:
            print(f"   ❌ 看板页面访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 测试看板页面时出错: {e}")
    
    print("\n5. URL列表...")
    print("   成长中心主页: http://localhost:8001/vocabulary-manager/")
    print("   学习目标列表: http://localhost:8001/vocabulary-manager/goals/")
    print("   学习计划列表: http://localhost:8001/vocabulary-manager/plans/")
    print("   学习中（看板）: http://localhost:8001/vocabulary-manager/kanban/")
    print("   学习统计: http://localhost:8001/vocabulary-manager/statistics/")
    
    print("\n6. 清理测试数据...")
    
    # 清理测试数据
    LearningGoal.objects.filter(user=user, name='测试学习目标').delete()
    VocabularyList.objects.filter(name='测试词库').delete()
    VocabularySource.objects.filter(name='测试来源').delete()
    User.objects.filter(username='test_user').delete()
    
    print("   测试数据已清理")
    print("\n✅ vocabulary_manager URL测试完成！")

if __name__ == '__main__':
    test_vocabulary_manager_urls() 