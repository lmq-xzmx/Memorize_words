#!/usr/bin/env python
"""
测试增项显示修复

验证修复后的get_extension_summary方法是否正确按角色过滤增项数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.accounts.models import CustomUser, UserExtensionData, RoleExtension, UserRole
from apps.accounts.admin import StudentUserAdmin, CustomUserAdmin
from django.contrib import admin
from django.utils.html import strip_tags


def test_extension_display_fix():
    """测试增项显示修复"""
    print("🔍 测试增项显示修复...")
    print("=" * 50)
    
    # 创建admin实例
    student_admin = StudentUserAdmin(CustomUser, admin.site)
    custom_admin = CustomUserAdmin(CustomUser, admin.site)
    
    # 测试不同角色的用户
    test_cases = [
        # 学生用户（应该显示学生增项）
        ('student1', 'student', '学生'),
        ('test_student_001', 'student', '学生'),
        # 教师用户（应该显示教师增项或无增项）
        ('test_teacher_obj', 'teacher', '教师'),
        # 其他角色用户（应该显示无增项）
        ('AnonymousUser', 'student', '学生'),
        ('admin333', 'student', '学生'),
    ]
    
    print("📊 测试结果:")
    all_correct = True
    
    for username, expected_role, role_display in test_cases:
        try:
            user = CustomUser.objects.get(username=username)
            print(f"\n👤 用户: {user.username} ({role_display})")
            print(f"  实际角色: {user.role}")
            
            # 获取该用户的所有增项数据
            all_extensions = UserExtensionData.objects.filter(user=user).select_related('role_extension')
            matching_extensions = UserExtensionData.objects.filter(
                user=user,
                role_extension__role=user.role
            ).select_related('role_extension')
            
            print(f"  所有增项数据: {all_extensions.count()} 条")
            print(f"  匹配角色的增项: {matching_extensions.count()} 条")
            
            # 测试StudentUserAdmin
            student_result = student_admin.get_extension_summary(user)
            student_text = strip_tags(student_result)
            print(f"  StudentUserAdmin显示: {student_text}")
            
            # 测试CustomUserAdmin
            custom_result = custom_admin.get_extension_summary(user)
            custom_text = strip_tags(custom_result)
            print(f"  CustomUserAdmin显示: {custom_text}")
            
            # 验证结果是否正确
            expected_count = matching_extensions.count()
            if expected_count > 0:
                expected_text = f"{expected_count} 项增项"
                if expected_text in student_text and expected_text in custom_text:
                    print(f"  ✅ 显示正确: 显示了 {expected_count} 项匹配的增项")
                else:
                    print(f"  ❌ 显示错误: 期望显示 {expected_count} 项增项")
                    all_correct = False
            else:
                if "无增项" in student_text and "无增项" in custom_text:
                    print(f"  ✅ 显示正确: 正确显示无增项")
                else:
                    print(f"  ❌ 显示错误: 期望显示无增项")
                    all_correct = False
            
            # 显示具体的增项信息
            if matching_extensions.exists():
                print(f"  📝 匹配的增项详情:")
                for ext in matching_extensions:
                    print(f"    - {ext.role_extension.field_label}: {ext.field_value}")
            
            if all_extensions.count() != matching_extensions.count():
                print(f"  ⚠️  不匹配的增项:")
                for ext in all_extensions:
                    if ext.role_extension.role != user.role:
                        print(f"    - {ext.role_extension.field_label}: {ext.field_value} (角色: {ext.role_extension.role})")
            
        except CustomUser.DoesNotExist:
            print(f"❌ 用户 {username} 不存在")
    
    return all_correct


def test_cross_role_scenarios():
    """测试跨角色场景"""
    print("\n🔍 测试跨角色场景...")
    print("=" * 40)
    
    # 创建一个测试场景：如果有用户的角色发生了变化，但增项数据还是旧角色的
    print("📋 模拟角色变更场景:")
    
    # 查找有增项数据的学生
    student_with_data = CustomUser.objects.filter(
        role=UserRole.STUDENT,
        userextensiondata__isnull=False
    ).first()
    
    if student_with_data:
        print(f"👤 测试用户: {student_with_data.username}")
        
        # 获取原始数据
        original_extensions = UserExtensionData.objects.filter(user=student_with_data)
        print(f"  原始增项数据: {original_extensions.count()} 条")
        
        # 模拟角色变更（不实际修改，只是测试显示逻辑）
        print(f"  当前角色: {student_with_data.role}")
        
        # 测试如果角色变为teacher会如何显示
        student_with_data.role = UserRole.TEACHER
        
        custom_admin = CustomUserAdmin(CustomUser, admin.site)
        result = custom_admin.get_extension_summary(student_with_data)
        result_text = strip_tags(result)
        print(f"  如果角色变为teacher，显示结果: {result_text}")
        
        # 恢复原始角色
        student_with_data.role = UserRole.STUDENT
        
        if "无增项" in result_text:
            print(f"  ✅ 正确: 角色变更后正确显示无匹配增项")
        else:
            print(f"  ❌ 错误: 角色变更后仍显示不匹配的增项")
    else:
        print("❌ 没有找到有增项数据的学生用户进行测试")


def generate_fix_summary():
    """生成修复总结"""
    print("\n📋 增项显示修复总结:")
    print("=" * 50)
    
    print("""
🔧 修复的问题:
- CustomUserAdmin和StudentUserAdmin的get_extension_summary方法
- 原来显示用户的所有增项数据，不管角色是否匹配
- 现在只显示与用户当前角色匹配的增项数据

✅ 修复内容:
1. 在查询中添加角色过滤条件:
   extensions = UserExtensionData.objects.filter(
       user=obj,
       role_extension__role=obj.role  # 新增的角色匹配条件
   ).select_related('role_extension')

2. 确保两个Admin类都使用相同的逻辑

🎯 预期效果:
- 学生用户只显示学生角色的增项数据
- 教师用户只显示教师角色的增项数据
- 其他角色用户只显示对应角色的增项数据
- 消除角色不匹配的显示问题
    """)


def main():
    """主测试函数"""
    print("🚀 开始测试增项显示修复...")
    print("=" * 70)
    
    try:
        # 1. 测试基本显示修复
        basic_test_passed = test_extension_display_fix()
        
        # 2. 测试跨角色场景
        test_cross_role_scenarios()
        
        # 3. 生成修复总结
        generate_fix_summary()
        
        if basic_test_passed:
            print(f"\n🎉 增项显示修复测试通过！")
            print(f"✅ 所有用户的增项显示都按角色正确过滤")
        else:
            print(f"\n⚠️  部分测试失败，需要进一步检查")
        
        return basic_test_passed
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)