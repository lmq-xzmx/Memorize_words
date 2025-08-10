#!/usr/bin/env python
"""
检查Admin列表第10列数据的正确性

第10列是StudentUserAdmin中的get_extension_summary，显示用户的角色增项摘要
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.accounts.models import CustomUser, UserExtensionData, RoleExtension, UserRole
from apps.accounts.admin import StudentUserAdmin
from django.contrib import admin
from django.utils.html import strip_tags
import re


def check_extension_summary_data():
    """检查get_extension_summary方法的数据正确性"""
    print("🔍 检查第10列 (get_extension_summary) 数据正确性...")
    print("=" * 60)
    
    # 获取所有学生用户
    students = CustomUser.objects.filter(role=UserRole.STUDENT).order_by('username')
    print(f"📊 找到 {students.count()} 个学生用户")
    
    # 创建StudentUserAdmin实例
    admin_instance = StudentUserAdmin(CustomUser, admin.site)
    
    issues_found = []
    correct_count = 0
    
    for student in students:
        print(f"\n👤 检查学生: {student.username} ({student.real_name or '无姓名'})")
        
        # 获取实际的增项数据
        actual_extensions = UserExtensionData.objects.filter(user=student).select_related('role_extension')
        actual_count = actual_extensions.count()
        
        # 调用admin方法获取显示结果
        display_result = admin_instance.get_extension_summary(student)
        display_text = strip_tags(display_result)
        
        print(f"  📋 实际增项数量: {actual_count}")
        print(f"  🖥️  显示结果: {display_text}")
        
        # 验证数据正确性
        if actual_count > 0:
            # 应该显示增项数量
            expected_pattern = f"{actual_count} 项增项"
            if expected_pattern in display_text:
                print(f"  ✅ 数据正确: 显示了正确的增项数量")
                correct_count += 1
            else:
                issue = f"学生 {student.username}: 期望显示 '{expected_pattern}', 实际显示 '{display_text}'"
                issues_found.append(issue)
                print(f"  ❌ 数据错误: {issue}")
        else:
            # 应该显示"无增项"
            if "无增项" in display_text:
                print(f"  ✅ 数据正确: 正确显示无增项")
                correct_count += 1
            else:
                issue = f"学生 {student.username}: 期望显示 '无增项', 实际显示 '{display_text}'"
                issues_found.append(issue)
                print(f"  ❌ 数据错误: {issue}")
        
        # 显示具体的增项信息
        if actual_count > 0:
            print(f"  📝 增项详情:")
            for ext_data in actual_extensions:
                print(f"    - {ext_data.role_extension.field_label}: {ext_data.field_value}")
    
    return issues_found, correct_count, students.count()


def check_extension_data_consistency():
    """检查增项数据的一致性"""
    print("\n🔍 检查增项数据一致性...")
    print("=" * 40)
    
    # 检查是否有孤立的增项数据（用户不存在或角色不匹配）
    orphaned_data = []
    
    all_extension_data = UserExtensionData.objects.select_related('user', 'role_extension')
    
    for ext_data in all_extension_data:
        user = ext_data.user
        role_extension = ext_data.role_extension
        
        # 检查用户是否存在且角色匹配
        if not user:
            orphaned_data.append(f"增项数据 ID {ext_data.id}: 关联的用户不存在")
        elif user.role != role_extension.role:
            orphaned_data.append(
                f"用户 {user.username}: 用户角色 '{user.role}' 与增项角色 '{role_extension.role}' 不匹配"
            )
    
    if orphaned_data:
        print("❌ 发现数据不一致问题:")
        for issue in orphaned_data:
            print(f"  - {issue}")
    else:
        print("✅ 增项数据一致性检查通过")
    
    return orphaned_data


def check_role_extension_config():
    """检查角色增项配置"""
    print("\n🔍 检查角色增项配置...")
    print("=" * 30)
    
    # 检查学生角色的增项配置
    student_extensions = RoleExtension.objects.filter(role=UserRole.STUDENT, is_active=True)
    print(f"📋 学生角色增项配置数量: {student_extensions.count()}")
    
    for ext in student_extensions:
        print(f"  - {ext.field_label} ({ext.field_name}): {ext.field_type}")
        
        # 检查该增项的数据数量
        data_count = UserExtensionData.objects.filter(role_extension=ext).count()
        print(f"    数据记录数: {data_count}")
    
    return student_extensions.count()


def generate_summary_report(issues_found, correct_count, total_count, orphaned_count, config_count):
    """生成检查报告"""
    print("\n📊 第10列数据检查报告")
    print("=" * 50)
    
    print(f"📈 统计信息:")
    print(f"  - 检查的学生用户数: {total_count}")
    print(f"  - 数据正确的用户数: {correct_count}")
    print(f"  - 数据错误的用户数: {len(issues_found)}")
    print(f"  - 数据一致性问题数: {orphaned_count}")
    print(f"  - 角色增项配置数: {config_count}")
    
    accuracy_rate = (correct_count / total_count * 100) if total_count > 0 else 0
    print(f"  - 数据准确率: {accuracy_rate:.1f}%")
    
    if len(issues_found) == 0 and orphaned_count == 0:
        print("\n🎉 第10列数据完全正确！")
        print("✅ 所有学生用户的角色增项摘要显示正确")
        print("✅ 数据一致性检查通过")
    else:
        print(f"\n⚠️  发现 {len(issues_found) + orphaned_count} 个问题需要修复")
        
        if issues_found:
            print("\n❌ 显示错误问题:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue}")
        
        if orphaned_count > 0:
            print(f"\n❌ 数据一致性问题: {orphaned_count} 个")
    
    print(f"\n🔧 建议操作:")
    if len(issues_found) > 0:
        print("1. 检查get_extension_summary方法的实现")
        print("2. 验证UserExtensionData查询逻辑")
        print("3. 确认HTML格式化是否正确")
    
    if orphaned_count > 0:
        print("4. 清理孤立的增项数据")
        print("5. 修复用户角色与增项角色不匹配的问题")
    
    if len(issues_found) == 0 and orphaned_count == 0:
        print("1. 数据状态良好，无需特殊操作")
        print("2. 可以继续正常使用admin界面")


def main():
    """主检查函数"""
    print("🚀 开始检查Admin列表第10列数据正确性...")
    print("=" * 70)
    
    try:
        # 1. 检查get_extension_summary数据正确性
        issues_found, correct_count, total_count = check_extension_summary_data()
        
        # 2. 检查增项数据一致性
        orphaned_data = check_extension_data_consistency()
        
        # 3. 检查角色增项配置
        config_count = check_role_extension_config()
        
        # 4. 生成报告
        generate_summary_report(
            issues_found, 
            correct_count, 
            total_count, 
            len(orphaned_data), 
            config_count
        )
        
        return len(issues_found) == 0 and len(orphaned_data) == 0
        
    except Exception as e:
        print(f"❌ 检查过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)