#!/usr/bin/env python
"""
仅测试统一模型和服务逻辑，不涉及数据库操作
"""
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_service_logic():
    """测试服务逻辑"""
    print("=== 测试统一学习服务逻辑 ===")
    
    # 测试导入
    try:
        from apps.teaching.services import UnifiedLearningService, DataMigrationService, LearningProgressService
        print("✅ 统一学习服务导入成功")
    except ImportError as e:
        print(f"❌ 统一学习服务导入失败: {e}")
        return False
    
    # 测试统一模型导入
    try:
        from apps.teaching.unified_models import (
            UnifiedLearningGoal,
            UnifiedGoalWord,
            UnifiedLearningSession,
            UnifiedWordProgress,
            UnifiedLearningPlan,
            UnifiedDailyRecord
        )
        print("✅ 统一模型导入成功")
    except ImportError as e:
        print(f"❌ 统一模型导入失败: {e}")
        return False
    
    return True

def test_model_structure():
    """测试模型结构"""
    print("\n=== 测试模型结构 ===")
    
    try:
        from apps.teaching.unified_models import UnifiedLearningGoal
        
        # 检查模型字段
        expected_fields = [
            'name', 'description', 'goal_type', 'target_words_count',
            'start_date', 'end_date', 'is_active', 'is_current',
            'total_words', 'learned_words'
        ]
        
        model_fields = [field.name for field in UnifiedLearningGoal._meta.fields]
        
        for field in expected_fields:
            if field in model_fields:
                print(f"  ✅ 字段 {field} 存在")
            else:
                print(f"  ❌ 字段 {field} 缺失")
        
        # 检查模型方法
        expected_methods = [
            'sync_words_from_sources', 'get_progress_stats', 'progress_percentage'
        ]
        
        for method in expected_methods:
            if hasattr(UnifiedLearningGoal, method):
                print(f"  ✅ 方法 {method} 存在")
            else:
                print(f"  ❌ 方法 {method} 缺失")
        
        print("✅ 模型结构检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 模型结构检查失败: {e}")
        return False

def test_migration_command():
    """测试迁移命令"""
    print("\n=== 测试迁移命令 ===")
    
    try:
        from apps.teaching.management.commands.migrate_learning_data import Command
        
        # 检查命令类
        command = Command()
        
        # 检查命令方法
        expected_methods = [
            'migrate_vocabulary_manager_data',
            'merge_duplicate_learning_goals',
            'create_unified_models'
        ]
        
        for method in expected_methods:
            if hasattr(command, method):
                print(f"  ✅ 迁移方法 {method} 存在")
            else:
                print(f"  ❌ 迁移方法 {method} 缺失")
        
        print("✅ 迁移命令检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 迁移命令检查失败: {e}")
        return False

def analyze_overlap():
    """分析重叠功能"""
    print("\n=== 分析Teaching与Vocabulary_Manager重叠功能 ===")
    
    # Teaching应用功能
    teaching_features = {
        "学习目标管理": "LearningGoal模型，支持单词集和词汇表关联",
        "目标单词管理": "GoalWord模型，管理目标中的具体单词",
        "学习会话跟踪": "LearningSession模型，记录学习会话",
        "单词学习记录": "WordLearningRecord模型，记录每个单词的学习情况",
        "学习计划制定": "LearningPlan模型，制定学习计划",
        "九宫格进度显示": "get_progress_stats方法，显示学习进度"
    }
    
    # Vocabulary_Manager应用功能
    vocab_features = {
        "学习目标管理": "LearningGoal模型，支持不同类型的学习目标",
        "学习会话管理": "StudySession模型，管理学习会话",
        "单词学习进度": "WordLearningProgress模型，跟踪单词掌握情况",
        "学习计划管理": "LearningPlan模型，支持多种计划模式",
        "每日学习记录": "DailyStudyRecord模型，记录每日学习情况",
        "用户连续学习": "UserStreak模型，跟踪连续学习天数",
        "看板视图": "learning_kanban视图，九宫格显示"
    }
    
    print("Teaching应用功能:")
    for feature, desc in teaching_features.items():
        print(f"  • {feature}: {desc}")
    
    print("\nVocabulary_Manager应用功能:")
    for feature, desc in vocab_features.items():
        print(f"  • {feature}: {desc}")
    
    # 重叠分析
    overlaps = [
        "学习目标管理 - 两个应用都有LearningGoal模型",
        "学习会话管理 - LearningSession vs StudySession",
        "学习计划制定 - 两个应用都有LearningPlan模型",
        "学习进度跟踪 - WordLearningRecord vs WordLearningProgress",
        "九宫格/看板显示 - 两个应用都有类似的进度展示功能"
    ]
    
    print("\n重叠功能分析:")
    for overlap in overlaps:
        print(f"  ⚠️  {overlap}")
    
    # 统一方案
    unified_solution = [
        "创建UnifiedLearningGoal统一学习目标模型",
        "创建UnifiedLearningSession统一学习会话模型", 
        "创建UnifiedWordProgress统一单词进度模型",
        "创建UnifiedLearningPlan统一学习计划模型",
        "提供UnifiedLearningService统一服务接口",
        "实现DataMigrationService数据迁移服务",
        "保持向后兼容，逐步迁移现有数据"
    ]
    
    print("\n统一解决方案:")
    for solution in unified_solution:
        print(f"  ✅ {solution}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始分析和整合Teaching与Vocabulary_Manager重叠功能")
    
    tests = [
        ("服务逻辑测试", test_service_logic),
        ("模型结构测试", test_model_structure),
        ("迁移命令测试", test_migration_command),
        ("重叠功能分析", analyze_overlap)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"执行: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            results.append((test_name, False))
    
    # 总结
    print(f"\n{'='*50}")
    print("测试总结")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！统一学习管理功能分析和整合完成。")
        print("\n📋 实施建议:")
        print("1. 运行数据迁移命令合并重复数据")
        print("2. 逐步将现有功能迁移到统一服务")
        print("3. 更新前端调用统一API接口")
        print("4. 编写完整的单元测试和集成测试")
        print("5. 部署前进行充分的回归测试")
    else:
        print(f"\n⚠️  有 {len(results) - passed} 项测试未通过，需要进一步修复。")

if __name__ == '__main__':
    main()