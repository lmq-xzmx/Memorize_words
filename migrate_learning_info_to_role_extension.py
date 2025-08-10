#!/usr/bin/env python
"""
将用户信息中的学习信息字段迁移到学生角色增项系统

迁移内容：
- grade_level (年级) -> 学生角色增项
- english_level (英语水平) -> 学生角色增项

迁移步骤：
1. 创建学生角色的增项配置
2. 将现有用户的学习信息数据迁移到增项数据表
3. 验证迁移结果
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.db import transaction
from apps.accounts.models import CustomUser, RoleExtension, UserExtensionData, UserRole
import json


def create_student_role_extensions():
    """创建学生角色的增项配置"""
    print("🔧 创建学生角色增项配置...")
    
    # 年级增项配置
    grade_extension, created = RoleExtension.objects.get_or_create(
        role=UserRole.STUDENT,
        field_name='grade_level',
        defaults={
            'field_label': '年级',
            'field_type': 'choice',
            'field_choices': json.dumps([
                ['primary_1', '小学一年级'],
                ['primary_2', '小学二年级'],
                ['primary_3', '小学三年级'],
                ['primary_4', '小学四年级'],
                ['primary_5', '小学五年级'],
                ['primary_6', '小学六年级'],
                ['junior_1', '初中一年级'],
                ['junior_2', '初中二年级'],
                ['junior_3', '初中三年级'],
                ['senior_1', '高中一年级'],
                ['senior_2', '高中二年级'],
                ['senior_3', '高中三年级'],
                ['other', '其他']
            ]),
            'is_required': False,
            'help_text': '请选择学生当前的年级',
            'show_in_frontend_register': True,
            'show_in_backend_admin': True,
            'show_in_profile': True,
            'sort_order': 1,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ 创建年级增项配置: {grade_extension}")
    else:
        print(f"ℹ️  年级增项配置已存在: {grade_extension}")
    
    # 英语水平增项配置
    english_level_extension, created = RoleExtension.objects.get_or_create(
        role=UserRole.STUDENT,
        field_name='english_level',
        defaults={
            'field_label': '英语水平',
            'field_type': 'choice',
            'field_choices': json.dumps([
                ['beginner', '初级'],
                ['elementary', '基础'],
                ['intermediate', '中级'],
                ['advanced', '高级']
            ]),
            'is_required': False,
            'help_text': '请选择学生当前的英语水平',
            'show_in_frontend_register': True,
            'show_in_backend_admin': True,
            'show_in_profile': True,
            'sort_order': 2,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ 创建英语水平增项配置: {english_level_extension}")
    else:
        print(f"ℹ️  英语水平增项配置已存在: {english_level_extension}")
    
    return grade_extension, english_level_extension


def migrate_existing_data():
    """迁移现有用户的学习信息数据"""
    print("\n📊 开始迁移现有用户数据...")
    
    # 获取增项配置
    try:
        grade_extension = RoleExtension.objects.get(role=UserRole.STUDENT, field_name='grade_level')
        english_level_extension = RoleExtension.objects.get(role=UserRole.STUDENT, field_name='english_level')
    except RoleExtension.DoesNotExist as e:
        print(f"❌ 增项配置不存在: {e}")
        return
    
    # 获取所有学生用户
    students = CustomUser.objects.filter(role=UserRole.STUDENT)
    print(f"📋 找到 {students.count()} 个学生用户")
    
    migrated_count = 0
    skipped_count = 0
    
    for student in students:
        print(f"\n👤 处理学生: {student.username} ({student.real_name})")
        
        # 迁移年级数据
        if student.grade_level:
            # 尝试映射到新的选择值
            grade_mapping = {
                '小学一年级': 'primary_1',
                '小学二年级': 'primary_2', 
                '小学三年级': 'primary_3',
                '小学四年级': 'primary_4',
                '小学五年级': 'primary_5',
                '小学六年级': 'primary_6',
                '初中一年级': 'junior_1',
                '初中二年级': 'junior_2',
                '初中三年级': 'junior_3',
                '高中一年级': 'senior_1',
                '高中二年级': 'senior_2',
                '高中三年级': 'senior_3',
            }
            
            mapped_grade = grade_mapping.get(student.grade_level, student.grade_level)
            
            grade_data, created = UserExtensionData.objects.get_or_create(
                user=student,
                role_extension=grade_extension,
                defaults={'field_value': mapped_grade}
            )
            
            if created:
                print(f"  ✅ 迁移年级数据: {student.grade_level} -> {mapped_grade}")
                migrated_count += 1
            else:
                print(f"  ℹ️  年级数据已存在: {grade_data.field_value}")
                skipped_count += 1
        
        # 迁移英语水平数据
        if student.english_level:
            english_data, created = UserExtensionData.objects.get_or_create(
                user=student,
                role_extension=english_level_extension,
                defaults={'field_value': student.english_level}
            )
            
            if created:
                print(f"  ✅ 迁移英语水平数据: {student.english_level}")
                migrated_count += 1
            else:
                print(f"  ℹ️  英语水平数据已存在: {english_data.field_value}")
                skipped_count += 1
    
    print(f"\n📈 迁移统计:")
    print(f"  - 成功迁移: {migrated_count} 条记录")
    print(f"  - 跳过重复: {skipped_count} 条记录")


def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    # 检查增项配置
    student_extensions = RoleExtension.objects.filter(role=UserRole.STUDENT, is_active=True)
    print(f"📋 学生角色增项配置数量: {student_extensions.count()}")
    
    for ext in student_extensions:
        print(f"  - {ext.field_label} ({ext.field_name}): {ext.field_type}")
    
    # 检查迁移的数据
    student_extension_data = UserExtensionData.objects.filter(
        role_extension__role=UserRole.STUDENT
    ).select_related('user', 'role_extension')
    
    print(f"📊 学生增项数据记录数量: {student_extension_data.count()}")
    
    # 按字段类型统计
    from django.db.models import Count
    stats = student_extension_data.values('role_extension__field_name').annotate(
        count=Count('id')
    )
    
    for stat in stats:
        field_name = stat['role_extension__field_name']
        count = stat['count']
        print(f"  - {field_name}: {count} 条记录")
    
    # 显示一些示例数据
    print("\n📝 示例数据:")
    sample_data = student_extension_data[:5]
    for data in sample_data:
        print(f"  - {data.user.username}: {data.role_extension.field_label} = {data.field_value}")


def update_admin_fieldsets():
    """更新admin.py中的fieldsets配置"""
    print("\n🔧 更新admin配置建议...")
    
    print("""
📝 需要手动更新 apps/accounts/admin.py 中的fieldsets配置:

原来的配置:
    fieldsets = (
        ...
        ('学习信息', {'fields': ('grade_level', 'english_level', 'parent')}),
        ...
    )

建议更新为:
    fieldsets = (
        ...
        ('关联信息', {'fields': ('parent',)}),
        ...
    )

同时在CustomUserAdmin类中添加学生角色增项的管理链接。
    """)


def main():
    """主函数"""
    print("🚀 开始学习信息迁移到角色增项系统...")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # 1. 创建学生角色增项配置
            create_student_role_extensions()
            
            # 2. 迁移现有数据
            migrate_existing_data()
            
            # 3. 验证迁移结果
            verify_migration()
            
            # 4. 提供admin配置更新建议
            update_admin_fieldsets()
            
        print("\n✅ 迁移完成!")
        print("\n📋 后续步骤:")
        print("1. 手动更新 apps/accounts/admin.py 中的fieldsets配置")
        print("2. 在admin界面中验证学生角色增项功能")
        print("3. 测试前端注册和个人资料页面的显示")
        print("4. 考虑是否需要从CustomUser模型中移除原字段")
        
    except Exception as e:
        print(f"❌ 迁移过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()