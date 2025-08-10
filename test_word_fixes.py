#!/usr/bin/env python
"""
测试Word和WordSet修复的脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.words.models import Word, WordSet, VocabularyList, VocabularySource
from django.contrib.auth import get_user_model

User = get_user_model()

def test_word_save():
    """测试Word保存功能"""
    print("=== 测试Word保存功能 ===")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    # 创建测试词库列表
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
    
    try:
        # 测试创建Word
        word = Word.objects.create(
            word='test',
            phonetic='test',
            definition='测试',
            part_of_speech='名词',
            vocabulary_list=vocab_list,
            user=user
        )
        print(f"✅ Word创建成功: {word.word}")
        
        # 测试更新Word
        word.definition = '更新的测试'
        word.save()
        print(f"✅ Word更新成功: {word.word}")
        
        return True
    except Exception as e:
        print(f"❌ Word保存失败: {e}")
        return False

def test_wordset_save():
    """测试WordSet保存功能"""
    print("\n=== 测试WordSet保存功能 ===")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    try:
        # 创建WordSet
        wordset = WordSet.objects.create(
            name='测试单词集',
            description='测试用单词集',
            created_by=user
        )
        print(f"✅ WordSet创建成功: {wordset.name}, 单词数量: {wordset.word_count}")
        
        # 创建测试单词
        word1 = Word.objects.create(word='apple', definition='苹果')
        word2 = Word.objects.create(word='banana', definition='香蕉')
        
        # 添加单词到WordSet
        wordset.words.add(word1, word2)
        wordset.refresh_from_db()
        print(f"✅ WordSet添加单词成功: {wordset.name}, 单词数量: {wordset.word_count}")
        
        # 测试更新WordSet
        wordset.description = '更新的测试用单词集'
        wordset.save()
        print(f"✅ WordSet更新成功: {wordset.name}, 单词数量: {wordset.word_count}")
        
        return True
    except Exception as e:
        print(f"❌ WordSet保存失败: {e}")
        return False

def test_admin_display():
    """测试Admin显示功能"""
    print("\n=== 测试Admin显示功能 ===")
    
    try:
        # 获取WordSet列表
        wordsets = WordSet.objects.all()
        for wordset in wordsets:
            print(f"WordSet: {wordset.name}, 数据库word_count: {wordset.word_count}")
        
        return True
    except Exception as e:
        print(f"❌ Admin显示测试失败: {e}")
        return False

def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    try:
        # 删除测试数据
        Word.objects.filter(word__in=['test', 'apple', 'banana']).delete()
        WordSet.objects.filter(name='测试单词集').delete()
        VocabularyList.objects.filter(name='测试词库').delete()
        VocabularySource.objects.filter(name='测试来源').delete()
        User.objects.filter(username='test_user').delete()
        
        print("✅ 测试数据清理完成")
        return True
    except Exception as e:
        print(f"❌ 测试数据清理失败: {e}")
        return False

if __name__ == '__main__':
    print("开始测试Word和WordSet修复...")
    
    # 运行测试
    word_test = test_word_save()
    wordset_test = test_wordset_save()
    admin_test = test_admin_display()
    
    # 清理测试数据
    cleanup_test_data()
    
    # 输出测试结果
    print("\n=== 测试结果 ===")
    print(f"Word保存测试: {'✅ 通过' if word_test else '❌ 失败'}")
    print(f"WordSet保存测试: {'✅ 通过' if wordset_test else '❌ 失败'}")
    print(f"Admin显示测试: {'✅ 通过' if admin_test else '❌ 失败'}")
    
    if all([word_test, wordset_test, admin_test]):
        print("\n🎉 所有测试通过！修复成功！")
    else:
        print("\n⚠️ 部分测试失败，需要进一步检查。") 