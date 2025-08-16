#!/usr/bin/env python
"""
修复数据库中用户不一致的学习计划
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.teaching.models import LearningPlan, LearningGoal
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

def fix_inconsistent_plans():
    """修复用户不一致的学习计划"""
    print("=== 修复用户不一致的学习计划 ===")
    
    # 查找用户不一致的学习计划
    inconsistent_plans = LearningPlan.objects.exclude(
        user=models.F('goal__user')
    ).select_related('user', 'goal', 'goal__user')
    
    print(f"发现 {inconsistent_plans.count()} 个用户不一致的学习计划")
    
    fixed_count = 0
    deleted_count = 0
    
    for plan in inconsistent_plans:
        print(f"\n处理计划: {plan.name} (ID: {plan.pk})")
        print(f"  当前用户: {plan.user.username if plan.user else 'None'}")
        print(f"  目标用户: {plan.goal.user.username if plan.goal and plan.goal.user else 'None'}")
        
        if plan.goal and plan.goal.user:
            # 修复：将计划的用户设置为目标的用户
            old_user = plan.user
            plan.user = plan.goal.user
            plan.save()
            
            print(f"  ✅ 已修复: {old_user.username if old_user else 'None'} -> {plan.user.username}")
            fixed_count += 1
        else:
            # 如果目标或目标用户不存在，删除这个计划
            plan_name = plan.name
            plan.delete()
            print(f"  🗑️ 已删除无效计划: {plan_name}")
            deleted_count += 1
    
    print(f"\n=== 修复完成 ===")
    print(f"修复计划数: {fixed_count}")
    print(f"删除计划数: {deleted_count}")
    
    # 验证修复结果
    remaining_inconsistent = LearningPlan.objects.exclude(
        user=models.F('goal__user')
    ).count()
    
    if remaining_inconsistent == 0:
        print("✅ 所有用户不一致问题已解决")
        return True
    else:
        print(f"❌ 仍有 {remaining_inconsistent} 个不一致的计划")
        return False

def verify_data_integrity():
    """验证数据完整性"""
    print("\n=== 验证数据完整性 ===")
    
    # 检查孤立的学习计划
    orphaned_plans = LearningPlan.objects.filter(goal__isnull=True)
    print(f"孤立的学习计划: {orphaned_plans.count()}")
    
    # 检查用户不一致的学习计划
    from django.db import models
    inconsistent_plans = LearningPlan.objects.exclude(
        user=models.F('goal__user')
    )
    print(f"用户不一致的学习计划: {inconsistent_plans.count()}")
    
    # 检查无效的学习目标
    invalid_goals = LearningGoal.objects.filter(user__isnull=True)
    print(f"无效的学习目标: {invalid_goals.count()}")
    
    total_issues = orphaned_plans.count() + inconsistent_plans.count() + invalid_goals.count()
    
    if total_issues == 0:
        print("✅ 数据库完整性检查通过")
        return True
    else:
        print(f"❌ 发现 {total_issues} 个数据完整性问题")
        return False

if __name__ == '__main__':
    print("开始修复数据库不一致问题...")
    print(f"时间: {datetime.now()}")
    
    # 修复不一致的计划
    success = fix_inconsistent_plans()
    
    # 验证修复结果
    verify_data_integrity()
    
    if success:
        print("\n🎉 数据库修复完成！")
    else:
        print("\n⚠️ 修复过程中遇到问题，请检查日志")