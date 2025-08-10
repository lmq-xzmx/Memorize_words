#!/usr/bin/env python
"""
检查角色与增项不匹配的问题并修正

从截图中看到有些用户角色与增项显示不匹配，需要深入检查原因
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.accounts.models import CustomUser, UserExtensionData, RoleExtension, UserRole
from django.db import transaction


def check_role_extension_mismatch():
    """检查角色与增项不匹配的问题"""
    print("🔍 检查角色与增项不匹配的问题...")
    print("=" * 60)
    
    # 获取所有用户的增项数据
    all_extension_data = UserExtensionData.objects.select_related('user', 'role_extension').order_by('user__username')
    
    mismatched_data = []
    correct_data = []
    
    for ext_data in all_extension_data:
        user = ext_data.user
        role_extension = ext_data.role_extension
        
        print(f"\n👤 用户: {user.username} ({user.real_name or '无姓名'})")
        print(f"  🏷️  用户角色: {user.role} ({user.get_role_display()})")
        print(f"  📋 增项角色: {role_extension.role} ({dict(RoleService.get_role_choices(include_empty=False)).get(role_extension.role, role_extension.role)})")
        print(f"  📝 增项字段: {role_extension.field_label} = {ext_data.field_value}")
        
        if user.role != role_extension.role:
            mismatch_info = {
                'user': user,
                'user_role': user.role,
                'extension_role': role_extension.role,
                'extension_data': ext_data,
                'field_label': role_extension.field_label,
                'field_value': ext_data.field_value
            }
            mismatched_data.append(mismatch_info)
            print(f"  ❌ 角色不匹配！")
        else:
            correct_data.append(ext_data)
            print(f"  ✅ 角色匹配正确")
    
    return mismatched_data, correct_data


def analyze_mismatch_patterns(mismatched_data):
    """分析不匹配的模式"""
    print(f"\n🔍 分析不匹配模式...")
    print("=" * 40)
    
    if not mismatched_data:
        print("✅ 没有发现角色不匹配的数据")
        return
    
    print(f"❌ 发现 {len(mismatched_data)} 条不匹配的数据:")
    
    # 按用户角色分组
    role_groups = {}
    for item in mismatched_data:
        user_role = item['user_role']
        if user_role not in role_groups:
            role_groups[user_role] = []
        role_groups[user_role].append(item)
    
    for user_role, items in role_groups.items():
        print(f"\n📊 用户角色 '{user_role}' 的不匹配情况 ({len(items)} 条):")
        for item in items:
            print(f"  - {item['user'].username}: {item['field_label']} (增项角色: {item['extension_role']})")
    
    # 分析可能的原因
    print(f"\n🔍 可能的原因分析:")
    
    # 检查是否有用户角色变更但增项数据未更新
    for item in mismatched_data:
        user = item['user']
        print(f"\n👤 {user.username}:")
        print(f"  当前角色: {user.role}")
        print(f"  增项角色: {item['extension_role']}")
        
        # 检查该用户是否有正确角色的增项配置
        correct_extensions = RoleExtension.objects.filter(role=user.role, is_active=True)
        if correct_extensions.exists():
            print(f"  ✅ 该用户角色有 {correct_extensions.count()} 个可用增项配置")
            for ext in correct_extensions:
                print(f"    - {ext.field_label} ({ext.field_name})")
        else:
            print(f"  ❌ 该用户角色没有可用的增项配置")


def fix_role_mismatch(mismatched_data, dry_run=True):
    """修复角色不匹配的问题"""
    print(f"\n🔧 修复角色不匹配问题 ({'预览模式' if dry_run else '执行模式'})...")
    print("=" * 50)
    
    if not mismatched_data:
        print("✅ 没有需要修复的数据")
        return
    
    fix_strategies = []
    
    for item in mismatched_data:
        user = item['user']
        ext_data = item['extension_data']
        
        print(f"\n👤 处理用户: {user.username}")
        print(f"  问题: 用户角色 '{user.role}' 与增项角色 '{item['extension_role']}' 不匹配")
        
        # 策略1: 查找用户当前角色的对应增项配置
        matching_extension = RoleExtension.objects.filter(
            role=user.role,
            field_name=ext_data.role_extension.field_name,
            is_active=True
        ).first()
        
        if matching_extension:
            strategy = {
                'type': 'update_extension_reference',
                'user': user,
                'old_extension_data': ext_data,
                'new_extension': matching_extension,
                'description': f"将增项引用从 {item['extension_role']} 更新为 {user.role}"
            }
            fix_strategies.append(strategy)
            print(f"  ✅ 策略: 更新增项引用到正确的角色配置")
        else:
            # 策略2: 删除不匹配的增项数据
            strategy = {
                'type': 'delete_mismatched_data',
                'user': user,
                'extension_data': ext_data,
                'description': f"删除不匹配的增项数据 ({item['field_label']})"
            }
            fix_strategies.append(strategy)
            print(f"  ⚠️  策略: 删除不匹配的增项数据（用户角色无对应配置）")
    
    # 执行修复策略
    if not dry_run:
        print(f"\n🚀 执行修复操作...")
        with transaction.atomic():
            for strategy in fix_strategies:
                if strategy['type'] == 'update_extension_reference':
                    old_data = strategy['old_extension_data']
                    new_extension = strategy['new_extension']
                    
                    old_data.role_extension = new_extension
                    old_data.save()
                    print(f"  ✅ 已更新 {strategy['user'].username} 的增项引用")
                    
                elif strategy['type'] == 'delete_mismatched_data':
                    ext_data = strategy['extension_data']
                    ext_data.delete()
                    print(f"  ✅ 已删除 {strategy['user'].username} 的不匹配增项数据")
        
        print(f"\n🎉 修复完成！处理了 {len(fix_strategies)} 条数据")
    else:
        print(f"\n📋 预览修复策略 ({len(fix_strategies)} 条):")
        for i, strategy in enumerate(fix_strategies, 1):
            print(f"  {i}. {strategy['description']}")
    
    return fix_strategies


def verify_fix_results():
    """验证修复结果"""
    print(f"\n🔍 验证修复结果...")
    print("=" * 30)
    
    # 重新检查是否还有不匹配的数据
    all_extension_data = UserExtensionData.objects.select_related('user', 'role_extension')
    
    remaining_mismatches = []
    for ext_data in all_extension_data:
        if ext_data.user.role != ext_data.role_extension.role:
            remaining_mismatches.append(ext_data)
    
    if remaining_mismatches:
        print(f"❌ 仍有 {len(remaining_mismatches)} 条不匹配的数据:")
        for ext_data in remaining_mismatches:
            print(f"  - {ext_data.user.username}: {ext_data.user.role} vs {ext_data.role_extension.role}")
        return False
    else:
        print(f"✅ 所有数据角色匹配正确")
        return True


def main():
    """主函数"""
    print("🚀 开始检查和修复角色与增项不匹配问题...")
    print("=" * 70)
    
    try:
        # 1. 检查不匹配的数据
        mismatched_data, correct_data = check_role_extension_mismatch()
        
        print(f"\n📊 检查结果统计:")
        print(f"  - 正确匹配的数据: {len(correct_data)} 条")
        print(f"  - 不匹配的数据: {len(mismatched_data)} 条")
        
        if not mismatched_data:
            print(f"\n🎉 所有数据角色匹配正确，无需修复！")
            return True
        
        # 2. 分析不匹配模式
        analyze_mismatch_patterns(mismatched_data)
        
        # 3. 预览修复策略
        fix_strategies = fix_role_mismatch(mismatched_data, dry_run=True)
        
        # 4. 询问是否执行修复
        print(f"\n❓ 是否执行修复操作？")
        print(f"   输入 'yes' 执行修复，其他任意键取消")
        
        # 自动执行修复（在脚本中）
        print(f"🔧 自动执行修复...")
        fix_role_mismatch(mismatched_data, dry_run=False)
        
        # 5. 验证修复结果
        success = verify_fix_results()
        
        if success:
            print(f"\n🎉 修复成功完成！")
        else:
            print(f"\n⚠️  修复后仍有问题，需要进一步检查")
        
        return success
        
    except Exception as e:
        print(f"❌ 检查过程中出现错误: {e}")
        import traceback
from apps.accounts.services.role_service import RoleService
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)