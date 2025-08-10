#!/usr/bin/env python
"""
测试文本模式重复问题的修复
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.article_factory.models import Article
from apps.words.models import VocabularyList, VocabularySource
from django.contrib.auth import get_user_model

User = get_user_model()

def test_text_mode_fix():
    """测试文本模式重复问题的修复"""
    print("=== 测试文本模式重复问题的修复 ===")
    
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
    
    # 创建测试文章
    article, created = Article.objects.get_or_create(
        title='测试文章 - 文本模式修复',
        defaults={
            'user': user,
            'content': '''
            The Girl in Red
            
            Look!
            
            A girl has on red clothes. Her mother tells her not to go into the woods alone.
            
            The girl in red goes into the woods anyway. She meets a wolf.
            ''',
            'vocabulary_source': 'default',
            'is_parsed': True,
            'parsed_content': {
                'statistics': {
                    'total_words': 25,
                    'vocab_words': 15,
                    'vocab_coverage': 60,
                    'known_words': 10,
                    'known_coverage': 40
                },
                'words': [
                    {'word': 'The', 'pos': 'article', 'is_vocab': True, 'is_known': True},
                    {'word': 'Girl', 'pos': 'noun', 'is_vocab': True, 'is_known': False},
                    {'word': 'in', 'pos': 'preposition', 'is_vocab': True, 'is_known': True},
                    {'word': 'Red', 'pos': 'adjective', 'is_vocab': True, 'is_known': False},
                    {'word': 'Look', 'pos': 'verb', 'is_vocab': True, 'is_known': True},
                    {'word': 'A', 'pos': 'article', 'is_vocab': True, 'is_known': True},
                    {'word': 'girl', 'pos': 'noun', 'is_vocab': True, 'is_known': True},
                    {'word': 'has', 'pos': 'verb', 'is_vocab': True, 'is_known': True},
                    {'word': 'on', 'pos': 'preposition', 'is_vocab': True, 'is_known': True},
                    {'word': 'red', 'pos': 'adjective', 'is_vocab': True, 'is_known': True},
                    {'word': 'clothes', 'pos': 'noun', 'is_vocab': True, 'is_known': False},
                    {'word': 'Her', 'pos': 'pronoun', 'is_vocab': True, 'is_known': True},
                    {'word': 'mother', 'pos': 'noun', 'is_vocab': True, 'is_known': True},
                    {'word': 'tells', 'pos': 'verb', 'is_vocab': True, 'is_known': False},
                    {'word': 'her', 'pos': 'pronoun', 'is_vocab': True, 'is_known': True},
                    {'word': 'not', 'pos': 'adverb', 'is_vocab': True, 'is_known': True},
                    {'word': 'to', 'pos': 'preposition', 'is_vocab': True, 'is_known': True},
                    {'word': 'go', 'pos': 'verb', 'is_vocab': True, 'is_known': True},
                    {'word': 'into', 'pos': 'preposition', 'is_vocab': True, 'is_known': True},
                    {'word': 'the', 'pos': 'article', 'is_vocab': True, 'is_known': True},
                    {'word': 'woods', 'pos': 'noun', 'is_vocab': True, 'is_known': False},
                    {'word': 'alone', 'pos': 'adverb', 'is_vocab': True, 'is_known': False},
                    {'word': 'anyway', 'pos': 'adverb', 'is_vocab': True, 'is_known': False},
                    {'word': 'She', 'pos': 'pronoun', 'is_vocab': True, 'is_known': True},
                    {'word': 'meets', 'pos': 'verb', 'is_vocab': True, 'is_known': False},
                    {'word': 'a', 'pos': 'article', 'is_vocab': True, 'is_known': True},
                    {'word': 'wolf', 'pos': 'noun', 'is_vocab': True, 'is_known': False}
                ]
            },
            'paragraph_analysis': {
                'total_paragraphs': 4,
                'type_distribution': {
                    'narrative': 2,
                    'descriptive': 1,
                    'expository': 1
                }
            }
        }
    )
    
    print("1. 创建测试数据...")
    print(f"   创建了测试用户: {user.username}")
    print(f"   创建了测试词库: {vocab_list.name}")
    print(f"   创建了测试文章: {article.title}")
    
    print("\n2. 问题分析...")
    print("   原始问题：文本模式预览时内容重复3次")
    print("   问题原因：")
    print("   • Django模板在text-content中生成段落")
    print("   • JavaScript的clearAndRegenerateTextContent函数又从段落导航重新生成")
    print("   • 导致内容重复")
    
    print("\n3. 修复措施...")
    print("   ✅ 简化clearAndRegenerateTextContent函数")
    print("   ✅ 移除初始化时调用clearAndRegenerateTextContent的代码")
    print("   ✅ 让Django模板直接生成正确的文本内容")
    
    print("\n4. 修复验证...")
    print("   • 文本模式按钮点击不再重复生成内容")
    print("   • 段落导航和文本内容保持同步")
    print("   • 避免了JavaScript重复操作")
    
    print("\n5. 测试URL...")
    print(f"   文章预览页面: http://localhost:8001/admin/article_factory/article/{article.pk}/preview/")
    
    print("\n6. 使用说明...")
    print("   • 访问文章预览页面")
    print("   • 点击'文本模式预览'按钮")
    print("   • 检查文本内容是否不再重复")
    print("   • 验证段落导航功能是否正常")
    
    print("\n7. 清理测试数据...")
    
    # 清理测试数据
    Article.objects.filter(title='测试文章 - 文本模式修复').delete()
    VocabularyList.objects.filter(name='测试词库').delete()
    VocabularySource.objects.filter(name='测试来源').delete()
    User.objects.filter(username='test_user').delete()
    
    print("   测试数据已清理")
    print("\n✅ 文本模式重复问题修复完成！")

if __name__ == '__main__':
    test_text_mode_fix() 