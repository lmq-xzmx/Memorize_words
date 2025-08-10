#!/usr/bin/env python
"""
角色继承和权限系统测试脚本

测试内容：
1. 角色继承关系
2. 权限继承功能
3. 对象级权限
4. 中间件权限检查
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import CustomUser, UserRole
from apps.permissions.models import RoleManagement
from apps.permissions.utils import RolePermissionChecker, PermissionUtils
from guardian.shortcuts import assign_perm, get_perms


def test_role_hierarchy():
    """测试角色继承层级"""
    print("\n🔍 测试角色继承层级")
    print("=" * 50)
    
    roles = RoleManagement.objects.all().order_by('role')
    for role in roles:
        level = role.get_hierarchy_level()
        parent = role.parent.display_name if role.parent else "无"
        children = role.get_children()
        children_names = [child.display_name for child in children]
        
        print(f"📁 {role.display_name}:")
        print(f"   层级: {level}")
        print(f"   父角色: {parent}")
        print(f"   子角色: {', '.join(children_names) if children_names else '无'}")
        print(f"   直接权限: {role.permissions.count()}")
        print(f"   总权限: {len(role.get_all_permissions())}")
        print()


def test_permission_inheritance():
    """测试权限继承"""
    print("\n🔍 测试权限继承")
    print("=" * 50)
    
    try:
        # 获取角色
        admin_role = RoleManagement.objects.get(role=UserRole.ADMIN)
        teacher_role = RoleManagement.objects.get(role=UserRole.TEACHER)
        parent_role = RoleManagement.objects.get(role=UserRole.PARENT)
        student_role = RoleManagement.objects.get(role=UserRole.STUDENT)
        
        # 测试继承关系
        print(f"✅ 教师是否继承管理员: {teacher_role.parent == admin_role}")
        print(f"✅ 家长是否继承教师: {parent_role.parent == teacher_role}")
        print(f"✅ 学生是否继承家长: {student_role.parent == parent_role}")
        
        # 测试权限继承
        admin_perms = set(admin_role.get_all_permissions())
        teacher_perms = set(teacher_role.get_all_permissions())
        parent_perms = set(parent_role.get_all_permissions())
        student_perms = set(student_role.get_all_permissions())
        
        print(f"\n📊 权限数量对比:")
        print(f"   管理员: {len(admin_perms)}")
        print(f"   教师: {len(teacher_perms)}")
        print(f"   家长: {len(parent_perms)}")
        print(f"   学生: {len(student_perms)}")
        
        # 验证权限包含关系（由于当前设置所有角色都有相同权限，这里只是演示）
        print(f"\n🔍 权限包含关系:")
        print(f"   教师包含管理员权限: {admin_perms.issubset(teacher_perms)}")
        print(f"   家长包含教师权限: {teacher_perms.issubset(parent_perms)}")
        print(f"   学生包含家长权限: {parent_perms.issubset(student_perms)}")
        
    except RoleManagement.DoesNotExist as e:
        print(f"❌ 角色不存在: {e}")


def test_role_permission_checker():
    """测试角色权限检查器"""
    print("\n🔍 测试角色权限检查器")
    print("=" * 50)
    
    try:
        # 创建测试用户
        test_user, created = CustomUser.objects.get_or_create(
            username='test_teacher',
            defaults={
                'email': 'test@example.com',
                'role': UserRole.TEACHER,
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ 创建测试用户: {test_user.username}")
        else:
            print(f"ℹ️  使用现有测试用户: {test_user.username}")
        
        # 测试权限检查器
        checker = RolePermissionChecker(test_user)
        
        print(f"\n📋 用户信息:")
        print(f"   用户名: {test_user.username}")
        print(f"   角色: {dict(UserRole.choices).get(test_user.role, test_user.role)}")
        print(f"   角色管理对象: {checker.role_management is not None}")
        
        if checker.role_management:
            print(f"   角色层级: {checker.role_management.get_hierarchy_level()}")
            print(f"   父角色: {checker.role_management.parent.display_name if checker.role_management.parent else '无'}")
            
            # 测试权限检查
            all_perms = checker.all_permissions
            print(f"   总权限数: {len(all_perms)}")
            
            # 测试具体权限
            test_perms = [
                'accounts.view_customuser',
                'accounts.add_customuser',
                'accounts.change_customuser',
                'accounts.delete_customuser'
            ]
            
            print(f"\n🔍 权限检查结果:")
            for perm in test_perms:
                # 检查权限是否在用户的所有权限中
                has_perm = perm in [f"{p.content_type.app_label}.{p.codename}" for p in all_perms]
                print(f"   {perm}: {'✅' if has_perm else '❌'}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_object_permissions():
    """测试对象级权限"""
    print("\n🔍 测试对象级权限")
    print("=" * 50)
    
    try:
        # 获取或创建测试用户
        teacher_user, _ = CustomUser.objects.get_or_create(
            username='test_teacher_obj',
            defaults={
                'email': 'teacher_obj@example.com',
                'role': UserRole.TEACHER,
                'is_active': True
            }
        )
        
        student_user, _ = CustomUser.objects.get_or_create(
            username='test_student_obj',
            defaults={
                'email': 'student_obj@example.com',
                'role': UserRole.STUDENT,
                'is_active': True
            }
        )
        
        print(f"✅ 测试用户准备完成")
        print(f"   教师: {teacher_user.username}")
        print(f"   学生: {student_user.username}")
        
        # 为教师分配对学生的特定权限
        assign_perm('accounts.change_customuser', teacher_user, student_user)
        assign_perm('accounts.view_customuser', teacher_user, student_user)
        
        print(f"\n📋 对象级权限分配:")
        print(f"   教师对学生的权限: {', '.join(get_perms(teacher_user, student_user))}")
        
        # 测试对象级权限检查
        teacher_perms = get_perms(teacher_user, student_user)
        
        has_view = 'view_customuser' in teacher_perms
        has_change = 'change_customuser' in teacher_perms
        has_delete = 'delete_customuser' in teacher_perms
        
        print(f"\n🔍 对象级权限检查:")
        print(f"   查看学生: {'✅' if has_view else '❌'}")
        print(f"   修改学生: {'✅' if has_change else '❌'}")
        print(f"   删除学生: {'✅' if has_delete else '❌'}")
        
    except Exception as e:
        print(f"❌ 对象级权限测试失败: {e}")


def test_permission_utils():
    """测试权限工具类"""
    print("\n🔍 测试权限工具类")
    print("=" * 50)
    
    try:
        # 测试自定义权限创建
        content_type = ContentType.objects.get_for_model(CustomUser)
        
        custom_perm_result = PermissionUtils.create_custom_permission(
            'test_custom_action',
            '测试自定义操作',
            content_type
        )
        
        if isinstance(custom_perm_result, tuple):
            custom_perm, created = custom_perm_result
            if created:
                print(f"✅ 创建自定义权限: {custom_perm.codename}")
            else:
                print(f"ℹ️  自定义权限已存在: {custom_perm.codename}")
        else:
            print(f"ℹ️  自定义权限处理完成")
        
        # 测试角色权限同步
        teacher_role = RoleManagement.objects.get(role=UserRole.TEACHER)
        sync_result = PermissionUtils.sync_role_permissions(teacher_role)
        
        print(f"\n🔄 权限同步结果: {'✅ 成功' if sync_result else '❌ 失败'}")
        
        # 显示组权限数量
        try:
            teacher_group = Group.objects.get(name='自由老师')
            group_perms = teacher_group.permissions.count()
            print(f"   教师组权限数量: {group_perms}")
        except Group.DoesNotExist:
            print(f"   ❌ 教师组不存在")
        
    except Exception as e:
        print(f"❌ 权限工具测试失败: {e}")


def main():
    """主测试函数"""
    print("🚀 Django 角色继承和权限系统测试")
    print("=" * 60)
    
    try:
        test_role_hierarchy()
        test_permission_inheritance()
        test_role_permission_checker()
        test_object_permissions()
        test_permission_utils()
        
        print("\n🎉 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()