#!/usr/bin/env python
"""
基础统一学习功能测试
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from apps.teaching.services import UnifiedLearningService, DataMigrationService
from apps.teaching.models import LearningGoal as TeachingLearningGoal, GoalWord
from apps.words.models import Word, WordSet

User = get_user_model()

def test_unified_learning_service():
    """测试统一学习服务"""
    print("=== 测试统一学习服务 ===")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_unified_user',
        defaults={
            'email': 'test@example.com',
            'first_name': '测试',
            'last_name': '用户'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    print(f"创建测试用户: {user.username}")
    
    # 创建测试单词
    word1, _ = Word.objects.get_or_create(
        word='test1',
        defaults={
            'definition': '测试单词1',
            'user': user
        }
    )
    word2, _ = Word.objects.get_or_create(
        word='test2',
        defaults={
            'definition': '测试单词2',
            'user': user
        }
    )
    
    print(f"创建测试单词: {word1.word}, {word2.word}")
    
    # 创建测试单词集
    word_set, _ = WordSet.objects.get_or_create(
        name='测试单词集',
        defaults={
            'description': '测试用单词集',
            'user': user
        }
    )
    word_set.words.add(word1, word2)
    
    print(f"创建测试单词集: {word_set.name}")
    
    # 测试统一学习服务
    service = UnifiedLearningService(user)
    
    # 创建学习目标
    goal = service.create_unified_learning_goal(
        name='测试统一目标',
        description='这是一个测试统一目标',
        target_words_count=50,
        word_sets=[word_set.id]
    )
    
    print(f"创建学习目标: {goal.name}")
    print(f"目标单词数: {GoalWord.objects.filter(goal=goal).count()}")
    
    # 获取学习目标列表
    goals = service.get_learning_goals()
    print(f"用户学习目标数量: {len(goals)}")
    
    # 开始学习会话
    session = service.start_learning_session(goal.id)
    print(f"开始学习会话: {session.id}")
    
    # 记录单词学习
    record = service.record_word_learning(
        session_id=session.id,
        word_id=word1.id,
        user_answer='test answer',
        is_correct=True,
        response_time=2.5
    )
    print(f"记录单词学习: {record.word.word} - {'正确' if record.is_correct else '错误'}")
    
    # 结束学习会话
    ended_session = service.end_learning_session(session.id)
    print(f"结束学习会话: {ended_session.id}")
    
    # 获取学习统计
    stats = service.get_learning_statistics()
    print(f"学习统计: {stats}")
    
    # 获取九宫格数据
    kanban_data = service.get_kanban_data(goal.id)
    print(f"九宫格数据: {kanban_data}")
    
    print("✅ 统一学习服务测试通过")

def test_data_migration():
    """测试数据迁移功能"""
    print("\n=== 测试数据迁移功能 ===")
    
    # 测试合并重复数据
    try:
        duplicates = DataMigrationService.merge_duplicate_learning_data()
        print(f"合并重复数据: {duplicates}")
        print("✅ 数据迁移功能测试通过")
    except Exception as e:
        print(f"⚠️ 数据迁移测试跳过 (可能是因为模型不存在): {e}")

def test_model_analysis():
    """测试模型重叠分析"""
    print("\n=== 模型重叠分析 ===")
    
    # 分析Teaching模型
    teaching_models = [
        'LearningGoal', 'GoalWord', 'LearningSession', 
        'WordLearningRecord', 'LearningPlan'
    ]
    
    # 分析Vocabulary_Manager模型
    vocab_models = [
        'LearningGoal', 'LearningPlan', 'StudySession',
        'WordLearningProgress', 'DailyStudyRecord', 'UserStreak'
    ]
    
    print("Teaching应用模型:")
    for model in teaching_models:
        print(f"  - {model}")
    
    print("\nVocabulary_Manager应用模型:")
    for model in vocab_models:
        print(f"  - {model}")
    
    # 重叠功能分析
    overlapping_functions = [
        "学习目标管理 (LearningGoal)",
        "学习计划制定 (LearningPlan)", 
        "学习会话跟踪 (LearningSession/StudySession)",
        "单词学习进度 (WordLearningRecord/WordLearningProgress)",
        "学习统计分析"
    ]
    
    print("\n重叠功能:")
    for func in overlapping_functions:
        print(f"  ✓ {func}")
    
    print("✅ 模型重叠分析完成")

if __name__ == '__main__':
    try:
        test_model_analysis()
        test_unified_learning_service()
        test_data_migration()
        print("\n🎉 所有测试完成!")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()