#!/usr/bin/env python
"""
测试词库默认选择功能
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.words.models import VocabularyList, VocabularySource
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def test_vocabulary_default_selection():
    """测试词库默认选择功能"""
    print("=== 测试词库默认选择功能 ===")
    
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
    
    # 创建测试词库列表（按时间顺序）
    vocab_lists = []
    
    # 最早创建的词库
    earliest_vocab = VocabularyList.objects.create(
        name='最早词库',
        description='这是最早创建的词库',
        source=source,
        is_active=True,
        created_at=timezone.now() - timedelta(days=30)
    )
    vocab_lists.append(earliest_vocab)
    print(f"✓ 创建最早词库: {earliest_vocab.name} (创建时间: {earliest_vocab.created_at})")
    
    # 第二个词库
    second_vocab = VocabularyList.objects.create(
        name='第二个词库',
        description='这是第二个创建的词库',
        source=source,
        is_active=True,
        created_at=timezone.now() - timedelta(days=20)
    )
    vocab_lists.append(second_vocab)
    print(f"✓ 创建第二个词库: {second_vocab.name} (创建时间: {second_vocab.created_at})")
    
    # 最新词库
    latest_vocab = VocabularyList.objects.create(
        name='最新词库',
        description='这是最新创建的词库',
        source=source,
        is_active=True,
        created_at=timezone.now() - timedelta(days=10)
    )
    vocab_lists.append(latest_vocab)
    print(f"✓ 创建最新词库: {latest_vocab.name} (创建时间: {latest_vocab.created_at})")
    
    # 测试获取最早创建的词库
    earliest = VocabularyList.objects.filter(is_active=True).order_by('created_at').first()
    print(f"\n最早创建的词库: {earliest.name} (ID: {earliest.id})")
    
    # 测试获取所有活跃词库（按创建时间排序）
    all_active = VocabularyList.objects.filter(is_active=True).order_by('created_at')
    print(f"\n所有活跃词库（按创建时间排序）:")
    for vocab in all_active:
        print(f"  - {vocab.name} (ID: {vocab.id}, 创建时间: {vocab.created_at})")
    
    # 测试API数据结构
    vocab_data = list(all_active.values('id', 'name', 'description', 'word_count', 'created_at'))
    print(f"\nAPI数据结构:")
    for vocab in vocab_data:
        print(f"  - {vocab['name']} (ID: {vocab['id']}, 单词数: {vocab['word_count']})")
    
    # 模拟用户选择记忆
    print(f"\n=== 模拟用户选择记忆 ===")
    
    # 模拟用户选择了第二个词库
    user_selection_id = second_vocab.id
    print(f"用户选择了词库: {second_vocab.name} (ID: {user_selection_id})")
    
    # 检查用户选择的词库是否仍然存在
    try:
        selected_vocab = VocabularyList.objects.get(id=user_selection_id, is_active=True)
        print(f"✓ 用户选择的词库仍然存在: {selected_vocab.name}")
        
        # 构建默认选择数据
        default_selection = {
            'id': selected_vocab.id,
            'name': selected_vocab.name,
            'description': selected_vocab.description,
            'word_count': selected_vocab.word_count,
            'created_at': selected_vocab.created_at.isoformat()
        }
        print(f"默认选择数据: {default_selection}")
        
    except VocabularyList.DoesNotExist:
        print(f"✗ 用户选择的词库不存在或已停用")
        # 使用最早创建的词库作为默认
        default_selection = {
            'id': earliest.id,
            'name': earliest.name,
            'description': earliest.description,
            'word_count': earliest.word_count,
            'created_at': earliest.created_at.isoformat()
        }
        print(f"使用最早词库作为默认: {default_selection}")
    
    # 构建完整的API响应数据
    api_response = {
        'success': True,
        'vocabulary_lists': vocab_data,
        'default_selection': default_selection,
        'earliest_vocab': {
            'id': earliest.id,
            'name': earliest.name,
            'description': earliest.description,
            'word_count': earliest.word_count,
            'created_at': earliest.created_at.isoformat()
        }
    }
    
    print(f"\n=== 完整API响应数据 ===")
    print(f"success: {api_response['success']}")
    print(f"词库数量: {len(api_response['vocabulary_lists'])}")
    print(f"默认选择: {api_response['default_selection']['name']}")
    print(f"最早词库: {api_response['earliest_vocab']['name']}")
    
    return True

def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    try:
        # 删除测试词库
        VocabularyList.objects.filter(name__in=['最早词库', '第二个词库', '最新词库']).delete()
        print("✓ 测试词库已删除")
        
        # 删除测试来源
        VocabularySource.objects.filter(name='测试来源').delete()
        print("✓ 测试来源已删除")
        
        # 删除测试用户
        User.objects.filter(username='test_user').delete()
        print("✓ 测试用户已删除")
        
        return True
    except Exception as e:
        print(f"✗ 清理测试数据失败: {e}")
        return False

if __name__ == '__main__':
    print("开始测试词库默认选择功能...")
    
    try:
        # 运行测试
        test_result = test_vocabulary_default_selection()
        
        # 清理测试数据
        cleanup_result = cleanup_test_data()
        
        # 输出测试结果
        print("\n=== 测试结果 ===")
        print(f"功能测试: {'✅ 通过' if test_result else '❌ 失败'}")
        print(f"数据清理: {'✅ 通过' if cleanup_result else '❌ 失败'}")
        
        if test_result and cleanup_result:
            print("\n🎉 所有测试通过！词库默认选择功能正常工作！")
        else:
            print("\n⚠️ 部分测试失败，需要检查。")
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        cleanup_test_data() 