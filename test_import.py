#!/usr/bin/env python
"""
测试导入脚本 - 验证单词导入和冲突检测功能
"""

import os
import sys
import django
import csv
import json
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth.models import User
from apps.words.models import VocabularySource, VocabularyList, ImportedVocabulary, Word
from django.core.management import call_command

def create_test_data():
    """创建测试数据"""
    print("创建测试数据...")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"创建测试用户: {user.username}")
    
    # 创建一些现有单词（用于测试冲突检测）
    existing_words = [
        {
            'word': 'apple',
            'definition': '苹果，一种水果',
            'part_of_speech': '名词',
            'user': user
        },
        {
            'word': 'book',
            'definition': '书籍，用于阅读的物品',
            'part_of_speech': '名词', 
            'user': user
        }
    ]
    
    for word_data in existing_words:
        word, created = Word.objects.get_or_create(
            user=word_data['user'],
            word=word_data['word'],
            defaults=word_data
        )
        if created:
            print(f"创建现有单词: {word.word}")
    
    return user

def create_test_csv():
    """创建测试CSV文件"""
    csv_file = Path('test_vocabulary.csv')
    
    test_data = [
        ['word', 'phonetic', 'definition', 'part_of_speech', 'textbook_version', 'grade', 'example_sentence', 'notes'],
        ['apple', '/ˈæpəl/', '苹果，红色的水果', '名词', '人教版', '3', 'I like to eat an apple.', '常见水果'],
        ['apples', '/ˈæpəlz/', '苹果的复数形式', '名词', '人教版', '3', 'There are many apples on the tree.', '复数形式'],
        ['book', '/bʊk/', '书本，学习用品', '名词', '牛津版', '2', 'This is my English book.', '学习必需品'],
        ['cat', '/kæt/', '猫，家养宠物', '名词', '人教版', '1', 'The cat is sleeping.', '可爱的动物'],
        ['dog', '/dɔːɡ/', '狗，忠诚的朋友', '名词', '人教版', '1', 'My dog likes to play.', '人类的好朋友'],
        ['run', '/rʌn/', '跑步，快速移动', '动词', '人教版', '2', 'I run every morning.', '健康运动'],
        ['happy', '/ˈhæpi/', '快乐的，高兴的', '形容词', '人教版', '2', 'She is very happy today.', '积极情绪'],
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    print(f"创建测试CSV文件: {csv_file}")
    return csv_file

def create_test_json():
    """创建测试JSON文件"""
    json_file = Path('test_vocabulary.json')
    
    test_data = {
        "words": [
            {
                "word": "hello",
                "phonetic": "/həˈloʊ/",
                "definition": "你好，问候语",
                "part_of_speech": "感叹词",
                "textbook_version": "人教版",
                "grade": "1",
                "example_sentence": "Hello, how are you?",
                "notes": "最基础的问候"
            },
            {
                "word": "world",
                "phonetic": "/wɜːrld/",
                "definition": "世界，地球",
                "part_of_speech": "名词",
                "textbook_version": "人教版",
                "grade": "2",
                "example_sentence": "Hello world!",
                "notes": "编程入门经典"
            },
            {
                "word": "apple",
                "phonetic": "/ˈæpəl/",
                "definition": "苹果，绿色的水果",
                "part_of_speech": "名词",
                "textbook_version": "剑桥版",
                "grade": "3",
                "example_sentence": "Green apple is sour.",
                "notes": "版本冲突测试"
            }
        ]
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"创建测试JSON文件: {json_file}")
    return json_file

def test_import_without_conflicts():
    """测试无冲突检测的导入"""
    print("\n=== 测试无冲突检测的导入 ===")
    csv_file = create_test_csv()
    
    try:
        call_command(
            'import_vocabulary',
            str(csv_file),
            '--source', 'Test Source 1',
            '--list-name', 'Test List 1',
            '--format', 'csv'
        )
        print("✅ 无冲突检测导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
    finally:
        if csv_file.exists():
            csv_file.unlink()

def test_import_with_conflicts():
    """测试带冲突检测的导入"""
    print("\n=== 测试带冲突检测的导入 ===")
    json_file = create_test_json()
    
    try:
        call_command(
            'import_vocabulary',
            str(json_file),
            '--source', 'Test Source 2',
            '--list-name', 'Test List 2',
            '--format', 'json',
            '--detect-conflicts',
            '--similarity-threshold', '0.8'
        )
        print("✅ 带冲突检测导入成功")
        
        # 检查冲突检测结果
        conflict_words = ImportedVocabulary.objects.filter(has_conflict=True)
        print(f"检测到 {conflict_words.count()} 个冲突单词:")
        for word in conflict_words:
            print(f"  - {word.word}: {len(word.conflict_data.get('conflicts', []))} 个冲突")
            
    except Exception as e:
        print(f"❌ 导入失败: {e}")
    finally:
        if json_file.exists():
            json_file.unlink()

def test_dry_run():
    """测试试运行模式"""
    print("\n=== 测试试运行模式 ===")
    csv_file = create_test_csv()
    
    try:
        call_command(
            'import_vocabulary',
            str(csv_file),
            '--source', 'Dry Run Source',
            '--list-name', 'Dry Run List',
            '--format', 'csv',
            '--dry-run',
            '--detect-conflicts'
        )
        print("✅ 试运行模式测试成功")
    except Exception as e:
        print(f"❌ 试运行失败: {e}")
    finally:
        if csv_file.exists():
            csv_file.unlink()

def show_statistics():
    """显示统计信息"""
    print("\n=== 导入统计信息 ===")
    print(f"词库来源数量: {VocabularySource.objects.count()}")
    print(f"词库列表数量: {VocabularyList.objects.count()}")
    print(f"导入单词总数: {ImportedVocabulary.objects.count()}")
    print(f"冲突单词数量: {ImportedVocabulary.objects.filter(has_conflict=True).count()}")
    print(f"用户单词数量: {Word.objects.count()}")
    
    # 显示冲突详情
    conflict_words = ImportedVocabulary.objects.filter(has_conflict=True)
    if conflict_words.exists():
        print("\n冲突详情:")
        for word in conflict_words:
            conflicts = word.conflict_data.get('conflicts', [])
            print(f"  {word.word}:")
            for conflict in conflicts:
                print(f"    - {conflict['type']}: {conflict.get('existing_word', 'N/A')}")

def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    # 删除测试导入的数据
    test_sources = VocabularySource.objects.filter(name__startswith='Test')
    for source in test_sources:
        print(f"删除词库来源: {source.name}")
        source.delete()
    
    # 删除试运行相关数据
    dry_run_sources = VocabularySource.objects.filter(name__startswith='Dry Run')
    for source in dry_run_sources:
        print(f"删除试运行数据: {source.name}")
        source.delete()
    
    print("✅ 测试数据清理完成")

def main():
    """主函数"""
    print("开始测试单词导入功能...")
    
    try:
        # 创建基础测试数据
        user = create_test_data()
        
        # 运行各种测试
        test_import_without_conflicts()
        test_import_with_conflicts()
        test_dry_run()
        
        # 显示统计信息
        show_statistics()
        
        # 询问是否清理数据
        response = input("\n是否清理测试数据？(y/N): ")
        if response.lower() == 'y':
            cleanup_test_data()
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()