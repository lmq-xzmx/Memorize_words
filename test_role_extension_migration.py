#!/usr/bin/env python
"""
测试角色增项迁移结果

验证内容：
1. 学生角色增项配置是否正确创建
2. 原有学习信息数据是否正确迁移
3. admin界面功能是否正常
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.accounts.models import CustomUser, RoleExtension, UserExtensionData, UserRole
from django.db.models import Count
import json


def test_role_extension_config():
    """测试角色增项配置"""
    print("🔍 测试角色增项配置...")
    
    # 检查学生角色的增项配置
    student_extensions = RoleExtension.objects.filter(role=UserRole.STUDENT, is_active=True)
    print(f"📋 学生角色增项配置数量: {student_extensions.count()}")
    
    # 检查必要的增项是否存在
    required_fields = ['grade_level', 'english_level']
    existing_fields = list(student_extensions.values_list('field_name', flat=True))
    
    for field in required_fields:
        if field in existing_fields:
            ext = student_extensions.get(field_name=field)
            print(f"✅ {ext.field_label} ({field}): {ext.field_type}")
            
            # 检查选择字段的选项
            if ext.field_type == 'choice' and ext.field_choices:
                choices = json.loads(ext.field_choices)
                print(f"   选项数量: {len(choices)}")
                print(f"   示例选项: {choices[:3]}")
        else:
            print(f"❌ 缺少必要字段: {field}")
    
    return student_extensions.count() > 0


def test_data_migration():
    """测试数据迁移结果"""
    print("\n🔍 测试数据迁移结果...")
    
    # 统计迁移的数据
    extension_data = UserExtensionData.objects.filter(
        role_extension__role=UserRole.STUDENT
    ).select_related('user', 'role_extension')
    
    print(f"📊 学生增项数据总数: {extension_data.count()}")
    
    # 按字段统计
    stats = extension_data.values('role_extension__field_name').annotate(
        count=Count('id')
    ).order_by('role_extension__field_name')
    
    for stat in stats:
        field_name = stat['role_extension__field_name']
        count = stat['count']
        print(f"  - {field_name}: {count} 条记录")
    
    # 检查一些具体的迁移数据
    print("\n📝 数据迁移示例:")
    sample_data = extension_data.filter(
        role_extension__field_name__in=['grade_level', 'english_level']
    )[:10]
    
    for data in sample_data:
        print(f"  - {data.user.username}: {data.role_extension.field_label} = {data.field_value}")
    
    return extension_data.count() > 0


def test_original_data_comparison():
    """对比原始数据和迁移数据"""
    print("\n🔍 对比原始数据和迁移数据...")
    
    # 获取有原始学习信息的学生
    students_with_original_data = CustomUser.objects.filter(
        role=UserRole.STUDENT
    ).exclude(
        grade_level='', english_level=''
    )
    
    print(f"📋 有原始学习信息的学生数量: {students_with_original_data.count()}")
    
    # 检查迁移完整性
    migration_issues = []
    
    for student in students_with_original_data:
        # 检查年级迁移
        if student.grade_level:
            try:
                grade_ext = RoleExtension.objects.get(role=UserRole.STUDENT, field_name='grade_level')
                grade_data = UserExtensionData.objects.get(user=student, role_extension=grade_ext)
                print(f"✅ {student.username} 年级迁移: {student.grade_level} -> {grade_data.field_value}")
            except UserExtensionData.DoesNotExist:
                migration_issues.append(f"{student.username} 年级数据未迁移")
        
        # 检查英语水平迁移
        if student.english_level:
            try:
                english_ext = RoleExtension.objects.get(role=UserRole.STUDENT, field_name='english_level')
                english_data = UserExtensionData.objects.get(user=student, role_extension=english_ext)
                print(f"✅ {student.username} 英语水平迁移: {student.english_level} -> {english_data.field_value}")
            except UserExtensionData.DoesNotExist:
                migration_issues.append(f"{student.username} 英语水平数据未迁移")
    
    if migration_issues:
        print("\n❌ 发现迁移问题:")
        for issue in migration_issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ 数据迁移完整性检查通过")
        return True


def test_admin_url_access():
    """测试admin URL配置"""
    print("\n🔍 测试admin URL配置...")
    
    from django.urls import reverse
    from django.test import Client
    from django.contrib.auth import get_user_model
    
    # 获取一个学生用户进行测试
    student = CustomUser.objects.filter(role=UserRole.STUDENT).first()
    if not student:
        print("❌ 没有找到学生用户进行测试")
        return False
    
    try:
        # 测试URL反向解析
        extension_url = reverse('admin:accounts_customuser_extensions', args=[student.pk])
        print(f"✅ 增项管理URL: {extension_url}")
        
        # 学生代理模型使用相同的URL
        print(f"✅ 学生增项管理URL: {extension_url} (共用)")
        
        return True
    except Exception as e:
        print(f"❌ URL配置错误: {e}")
        return False


def generate_admin_usage_guide():
    """生成admin使用指南"""
    print("\n📖 Admin使用指南:")
    print("=" * 50)
    
    print("""
1. 访问学生管理页面:
   - 进入Django Admin后台
   - 选择 "用户管理" -> "学生账号管理"
   - 或选择 "用户管理" -> "用户" (统一管理)

2. 管理学生角色增项:
   - 在学生列表中点击 "📝 管理增项" 按钮
   - 填写或修改学生的年级、英语水平等信息
   - 点击保存完成更新

3. 配置角色增项:
   - 选择 "用户管理" -> "角色增项配置管理"
   - 可以添加新的学生角色增项字段
   - 支持多种字段类型：文本、选择、日期等

4. 查看增项数据:
   - 选择 "用户管理" -> "用户增项数据管理"
   - 可以查看所有用户的增项数据记录
    """)


def main():
    """主测试函数"""
    print("🚀 开始测试角色增项迁移结果...")
    print("=" * 60)
    
    test_results = []
    
    # 1. 测试角色增项配置
    test_results.append(("角色增项配置", test_role_extension_config()))
    
    # 2. 测试数据迁移
    test_results.append(("数据迁移", test_data_migration()))
    
    # 3. 测试数据完整性
    test_results.append(("数据完整性", test_original_data_comparison()))
    
    # 4. 测试admin URL
    test_results.append(("Admin URL配置", test_admin_url_access()))
    
    # 输出测试结果
    print("\n📊 测试结果汇总:")
    print("=" * 30)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！角色增项迁移成功完成。")
        generate_admin_usage_guide()
    else:
        print("\n⚠️  部分测试失败，请检查相关配置。")
    
    return all_passed


if __name__ == '__main__':
    main()