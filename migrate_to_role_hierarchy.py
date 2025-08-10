#!/usr/bin/env python
"""
迁移到角色所辖用户增项级联模型

将现有的用户增项数据迁移到新的三级级联结构：
1. RoleLevel (角色级别)
2. RoleUser (角色用户) 
3. UserExtension (用户增项)
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.db import transaction
from apps.accounts.models import CustomUser, UserRole, RoleExtension, UserExtensionData
from apps.accounts.models import RoleLevel, RoleUser, UserExtension


def create_role_levels():
    """创建角色级别"""
    print("🔧 创建角色级别...")
    
    created_count = 0
    for role_choice in RoleService.get_role_choices(include_empty=False):
        role_code, role_name = role_choice
        
        role_level, created = RoleLevel.objects.get_or_create(
            role=role_code,
            defaults={
                'role_name': role_name,
                'description': f'{role_name}角色，负责{role_name}相关的工作和学习',
                'is_active': True,
                'sort_order': list(RoleService.get_role_choices(include_empty=False)).index(role_choice)
            }
        )
        
        if created:
            print(f"  ✅ 创建角色级别: {role_name} ({role_code})")
            created_count += 1
        else:
            print(f"  ℹ️  角色级别已存在: {role_name} ({role_code})")
    
    print(f"📊 角色级别创建完成，新增 {created_count} 个")
    return RoleLevel.objects.all().count()


def create_role_users():
    """创建角色用户关联"""
    print("\n🔧 创建角色用户关联...")
    
    users = CustomUser.objects.filter(is_active=True)
    created_count = 0
    updated_count = 0
    
    for user in users:
        if not hasattr(user, 'role') or not user.role:
            print(f"  ⚠️  用户 {user.username} 没有角色，跳过")
            continue
        
        try:
            role_level = RoleLevel.objects.get(role=user.role)
        except RoleLevel.DoesNotExist:
            print(f"  ❌ 用户 {user.username} 的角色 {user.role} 不存在对应的角色级别")
            continue
        
        role_user, created = RoleUser.objects.get_or_create(
            user=user,
            defaults={
                'role_level': role_level,
                'is_active': user.is_active,
                'notes': f'从用户模型自动迁移，原角色: {user.role}'
            }
        )
        
        if created:
            print(f"  ✅ 创建角色用户: {user.username} -> {role_level.role_name}")
            created_count += 1
        else:
            # 检查是否需要更新
            if role_user.role_level != role_level or role_user.is_active != user.is_active:
                role_user.role_level = role_level
                role_user.is_active = user.is_active
                role_user.save()
                print(f"  🔄 更新角色用户: {user.username} -> {role_level.role_name}")
                updated_count += 1
            else:
                print(f"  ℹ️  角色用户已存在: {user.username}")
    
    print(f"📊 角色用户创建完成，新增 {created_count} 个，更新 {updated_count} 个")
    return RoleUser.objects.all().count()


def migrate_user_extensions():
    """迁移用户增项数据"""
    print("\n🔧 迁移用户增项数据...")
    
    old_extensions = UserExtensionData.objects.all().select_related('user', 'role_extension')
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for old_ext in old_extensions:
        try:
            # 查找对应的RoleUser
            role_user = RoleUser.objects.filter(user=old_ext.user).first()
            if not role_user:
                print(f"  ❌ 用户 {old_ext.user.username} 没有对应的RoleUser记录")
                error_count += 1
                continue
            
            # 检查角色一致性
            if role_user.role_level.role != old_ext.role_extension.role:
                print(f"  ⚠️  用户 {old_ext.user.username} 角色不匹配: {role_user.role_level.role} vs {old_ext.role_extension.role}")
                # 尝试找到正确的角色级别
                correct_role_level = RoleLevel.objects.filter(role=old_ext.role_extension.role).first()
                if correct_role_level:
                    # 创建或更新正确的RoleUser记录
                    role_user, _ = RoleUser.objects.get_or_create(
                        user=old_ext.user,
                        role_level=correct_role_level,
                        defaults={
                            'is_active': old_ext.user.is_active,
                            'notes': f'从增项数据迁移创建，角色: {correct_role_level.role}'
                        }
                    )
                else:
                    print(f"  ❌ 找不到角色 {old_ext.role_extension.role} 的角色级别")
                    error_count += 1
                    continue
            
            # 创建新的用户增项记录
            new_ext, created = UserExtension.objects.get_or_create(
                role_user=role_user,
                role_extension=old_ext.role_extension,
                defaults={
                    'field_value': old_ext.field_value,
                    'is_active': True,
                    'created_by': None  # 原数据没有创建者信息
                }
            )
            
            if created:
                print(f"  ✅ 迁移增项: {old_ext.user.username} - {old_ext.role_extension.field_label}")
                migrated_count += 1
            else:
                # 检查是否需要更新值
                if new_ext.field_value != old_ext.field_value:
                    new_ext.field_value = old_ext.field_value
                    new_ext.save()
                    print(f"  🔄 更新增项: {old_ext.user.username} - {old_ext.role_extension.field_label}")
                    migrated_count += 1
                else:
                    print(f"  ℹ️  增项已存在: {old_ext.user.username} - {old_ext.role_extension.field_label}")
                    skipped_count += 1
                    
        except Exception as e:
            print(f"  ❌ 迁移失败: {old_ext.user.username} - {old_ext.role_extension.field_label}: {e}")
            error_count += 1
    
    print(f"📊 用户增项迁移完成，迁移 {migrated_count} 个，跳过 {skipped_count} 个，错误 {error_count} 个")
    return UserExtension.objects.all().count()


def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    # 统计数据
    role_level_count = RoleLevel.objects.count()
    role_user_count = RoleUser.objects.count()
    user_extension_count = UserExtension.objects.count()
    
    print(f"📊 迁移后统计:")
    print(f"  - 角色级别: {role_level_count} 个")
    print(f"  - 角色用户: {role_user_count} 个")
    print(f"  - 用户增项: {user_extension_count} 个")
    
    # 验证数据一致性
    print(f"\n🔍 数据一致性检查:")
    
    # 检查角色用户的角色一致性
    inconsistent_role_users = 0
    for role_user in RoleUser.objects.select_related('user', 'role_level'):
        if hasattr(role_user.user, 'role') and role_user.user.role != role_user.role_level.role:
            print(f"  ⚠️  角色不一致: {role_user.user.username} - 用户角色({role_user.user.role}) vs 级别角色({role_user.role_level.role})")
            inconsistent_role_users += 1
    
    if inconsistent_role_users == 0:
        print(f"  ✅ 所有角色用户的角色一致性检查通过")
    else:
        print(f"  ❌ 发现 {inconsistent_role_users} 个角色不一致的记录")
    
    # 检查用户增项的角色一致性
    inconsistent_extensions = 0
    for user_ext in UserExtension.objects.select_related('role_user__role_level', 'role_extension'):
        if user_ext.role_user.role_level.role != user_ext.role_extension.role:
            print(f"  ⚠️  增项角色不一致: {user_ext.role_user.user.username} - {user_ext.role_extension.field_label}")
            inconsistent_extensions += 1
    
    if inconsistent_extensions == 0:
        print(f"  ✅ 所有用户增项的角色一致性检查通过")
    else:
        print(f"  ❌ 发现 {inconsistent_extensions} 个增项角色不一致的记录")
    
    return inconsistent_role_users == 0 and inconsistent_extensions == 0


def generate_access_urls():
    """生成访问URL"""
    print(f"\n🔗 访问URL:")
    print(f"  - 角色所辖用户增项首页: http://127.0.0.1:8000/accounts/role-hierarchy/")
    print(f"  - Django Admin管理: http://127.0.0.1:8000/admin/")
    print(f"    - 角色级别管理: http://127.0.0.1:8000/admin/accounts/rolelevel/")
    print(f"    - 角色用户管理: http://127.0.0.1:8000/admin/accounts/roleuser/")
    print(f"    - 用户增项管理: http://127.0.0.1:8000/admin/accounts/userextension/")


def main():
    """主迁移函数"""
    print("🚀 开始迁移到角色所辖用户增项级联模型...")
    print("=" * 70)
    
    try:
        with transaction.atomic():
            # 1. 创建角色级别
            role_level_count = create_role_levels()
            
            # 2. 创建角色用户关联
            role_user_count = create_role_users()
            
            # 3. 迁移用户增项数据
            user_extension_count = migrate_user_extensions()
            
            # 4. 验证迁移结果
            verification_passed = verify_migration()
            
            # 5. 生成访问URL
            generate_access_urls()
            
        if verification_passed:
            print(f"\n🎉 迁移成功完成！")
            print(f"✅ 角色级别: {role_level_count} 个")
            print(f"✅ 角色用户: {role_user_count} 个") 
            print(f"✅ 用户增项: {user_extension_count} 个")
            print(f"\n📋 后续步骤:")
            print(f"1. 访问 http://127.0.0.1:8000/accounts/role-hierarchy/ 查看新的管理界面")
            print(f"2. 在Django Admin中管理角色级别、角色用户和用户增项")
            print(f"3. 测试三级级联功能是否正常工作")
        else:
            print(f"\n⚠️  迁移完成但存在数据一致性问题，请检查上述警告信息")
        
        return verification_passed
        
    except Exception as e:
        print(f"❌ 迁移过程中出现错误: {e}")
        import traceback
from apps.accounts.services.role_service import RoleService
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)