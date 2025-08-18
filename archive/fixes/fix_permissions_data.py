#!/usr/bin/env python
"""
权限系统数据修复脚本

功能：
1. 初始化菜单模块配置
2. 创建角色组映射
3. 设置角色菜单权限
4. 同步用户权限
5. 创建角色管理数据
"""

import os
import sys
import django
from django.db import transaction

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import CustomUser, UserRole
from apps.permissions.models import (
    MenuModuleConfig, RoleMenuPermission, RoleGroupMapping, 
    RoleManagement
)
from apps.permissions.models_optimized import PermissionSyncLog
from apps.accounts.services.role_service import RoleService


def create_menu_modules():
    """创建前台菜单模块配置"""
    print("\n=== 创建菜单模块配置 ===")
    
    menu_configs = [
        # 根目录菜单
        {
            'key': 'dashboard',
            'name': '仪表盘',
            'menu_level': 'root',
            'icon': 'fas fa-tachometer-alt',
            'url': '/dashboard/',
            'sort_order': 1,
            'description': '系统主页和数据概览'
        },
        {
            'key': 'learning',
            'name': '学习中心',
            'menu_level': 'root',
            'icon': 'fas fa-graduation-cap',
            'url': '/learning/',
            'sort_order': 2,
            'description': '学习功能模块'
        },
        {
            'key': 'teaching',
            'name': '教学管理',
            'menu_level': 'root',
            'icon': 'fas fa-chalkboard-teacher',
            'url': '/teaching/',
            'sort_order': 3,
            'description': '教学相关功能'
        },
        {
            'key': 'words',
            'name': '词汇管理',
            'menu_level': 'root',
            'icon': 'fas fa-book',
            'url': '/words/',
            'sort_order': 4,
            'description': '单词和词汇表管理'
        },
        {
            'key': 'accounts',
            'name': '用户管理',
            'menu_level': 'root',
            'icon': 'fas fa-users',
            'url': '/accounts/',
            'sort_order': 5,
            'description': '用户账号管理'
        },
        {
            'key': 'permissions',
            'name': '权限管理',
            'menu_level': 'root',
            'icon': 'fas fa-shield-alt',
            'url': '/permissions/',
            'sort_order': 6,
            'description': '角色权限配置'
        },
        
        # 一级子菜单
        {
            'key': 'learning_practice',
            'name': '练习模块',
            'menu_level': 'level1',
            'icon': 'fas fa-dumbbell',
            'url': '/learning/practice/',
            'sort_order': 21,
            'description': '单词练习和测试'
        },
        {
            'key': 'learning_progress',
            'name': '学习进度',
            'menu_level': 'level1',
            'icon': 'fas fa-chart-line',
            'url': '/learning/progress/',
            'sort_order': 22,
            'description': '学习进度查看'
        },
        {
            'key': 'teaching_plans',
            'name': '教学计划',
            'menu_level': 'level1',
            'icon': 'fas fa-calendar-alt',
            'url': '/teaching/plans/',
            'sort_order': 31,
            'description': '教学计划管理'
        },
        {
            'key': 'teaching_goals',
            'name': '学习目标',
            'menu_level': 'level1',
            'icon': 'fas fa-bullseye',
            'url': '/teaching/goals/',
            'sort_order': 32,
            'description': '学习目标设置'
        },
        {
            'key': 'words_vocabulary',
            'name': '词汇表',
            'menu_level': 'level1',
            'icon': 'fas fa-list',
            'url': '/words/vocabulary/',
            'sort_order': 41,
            'description': '词汇表管理'
        },
        {
            'key': 'words_management',
            'name': '单词管理',
            'menu_level': 'level1',
            'icon': 'fas fa-spell-check',
            'url': '/words/management/',
            'sort_order': 42,
            'description': '单词增删改查'
        },
        {
            'key': 'accounts_users',
            'name': '用户列表',
            'menu_level': 'level1',
            'icon': 'fas fa-user-friends',
            'url': '/accounts/users/',
            'sort_order': 51,
            'description': '用户账号列表'
        },
        {
            'key': 'accounts_roles',
            'name': '角色管理',
            'menu_level': 'level1',
            'icon': 'fas fa-user-tag',
            'url': '/accounts/roles/',
            'sort_order': 52,
            'description': '用户角色配置'
        },
        {
            'key': 'permissions_menu',
            'name': '菜单权限',
            'menu_level': 'level1',
            'icon': 'fas fa-sitemap',
            'url': '/permissions/menu/',
            'sort_order': 61,
            'description': '菜单访问权限'
        },
        {
            'key': 'permissions_role',
            'name': '角色权限',
            'menu_level': 'level1',
            'icon': 'fas fa-key',
            'url': '/permissions/role/',
            'sort_order': 62,
            'description': '角色权限配置'
        },
        
        # 二级子菜单
        {
            'key': 'learning_practice_word',
            'name': '单词练习',
            'menu_level': 'level2',
            'icon': 'fas fa-font',
            'url': '/learning/practice/word/',
            'sort_order': 211,
            'description': '单词记忆练习'
        },
        {
            'key': 'learning_practice_test',
            'name': '单词测试',
            'menu_level': 'level2',
            'icon': 'fas fa-clipboard-check',
            'url': '/learning/practice/test/',
            'sort_order': 212,
            'description': '单词测试评估'
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for config_data in menu_configs:
        menu_config, created = MenuModuleConfig.objects.get_or_create(
            key=config_data['key'],
            defaults=config_data
        )
        
        if created:
            created_count += 1
            print(f"✓ 创建菜单: {menu_config.name} ({menu_config.key})")
        else:
            # 更新现有配置
            for field, value in config_data.items():
                if field != 'key':  # key是唯一标识，不更新
                    setattr(menu_config, field, value)
            menu_config.save()
            updated_count += 1
            print(f"↻ 更新菜单: {menu_config.name} ({menu_config.key})")
    
    print(f"\n菜单配置完成: 创建 {created_count} 个，更新 {updated_count} 个")


def create_role_groups():
    """创建角色对应的用户组"""
    print("\n=== 创建角色用户组 ===")
    
    role_group_configs = [
        {'role': UserRole.ADMIN, 'group_name': '管理员组', 'auto_sync': True},
        {'role': UserRole.DEAN, 'group_name': '教导主任组', 'auto_sync': True},
        {'role': UserRole.ACADEMIC_DIRECTOR, 'group_name': '教务主任组', 'auto_sync': True},
        {'role': UserRole.RESEARCH_LEADER, 'group_name': '教研组长组', 'auto_sync': True},
        {'role': UserRole.TEACHER, 'group_name': '教师组', 'auto_sync': True},
        {'role': UserRole.PARENT, 'group_name': '家长组', 'auto_sync': True},
        {'role': UserRole.STUDENT, 'group_name': '学生组', 'auto_sync': True},
    ]
    
    created_groups = 0
    created_mappings = 0
    
    for config in role_group_configs:
        # 创建或获取用户组
        group, group_created = Group.objects.get_or_create(
            name=config['group_name']
        )
        
        if group_created:
            created_groups += 1
            print(f"✓ 创建用户组: {group.name}")
        
        # 创建角色组映射
        mapping, mapping_created = RoleGroupMapping.objects.get_or_create(
            role=config['role'],
            defaults={
                'group': group,
                'auto_sync': config['auto_sync']
            }
        )
        
        if mapping_created:
            created_mappings += 1
            print(f"✓ 创建角色映射: {config['role']} → {group.name}")
        else:
            # 更新现有映射
            mapping.group = group
            mapping.auto_sync = config['auto_sync']
            mapping.save()
            print(f"↻ 更新角色映射: {config['role']} → {group.name}")
    
    print(f"\n角色组配置完成: 创建 {created_groups} 个组，{created_mappings} 个映射")


def create_role_management():
    """创建角色管理数据"""
    print("\n=== 创建角色管理数据 ===")
    
    # 获取所有权限
    all_permissions = Permission.objects.all()
    
    # 定义角色层级和权限
    role_configs = [
        {
            'role': UserRole.ADMIN,
            'display_name': '系统管理员',
            'description': '拥有系统最高权限，可以管理所有功能模块',
            'parent': None,
            'sort_order': 1,
            'permissions': all_permissions  # 管理员拥有所有权限
        },
        {
            'role': UserRole.DEAN,
            'display_name': '教导主任',
            'description': '负责教学管理和教师管理',
            'parent': UserRole.ADMIN,
            'sort_order': 2,
            'permissions': all_permissions.filter(
                content_type__app_label__in=['teaching', 'accounts', 'words']
            )
        },
        {
            'role': UserRole.ACADEMIC_DIRECTOR,
            'display_name': '教务主任',
            'description': '负责课程安排和教学计划',
            'parent': UserRole.DEAN,
            'sort_order': 3,
            'permissions': all_permissions.filter(
                content_type__app_label__in=['teaching', 'words']
            )
        },
        {
            'role': UserRole.RESEARCH_LEADER,
            'display_name': '教研组长',
            'description': '负责教学研究和方法改进',
            'parent': UserRole.DEAN,
            'sort_order': 4,
            'permissions': all_permissions.filter(
                content_type__app_label__in=['teaching', 'words'],
                codename__in=['view_learninggoal', 'add_learninggoal', 'change_learninggoal']
            )
        },
        {
            'role': UserRole.TEACHER,
            'display_name': '教师',
            'description': '负责学生教学和学习指导',
            'parent': UserRole.ACADEMIC_DIRECTOR,
            'sort_order': 5,
            'permissions': all_permissions.filter(
                content_type__app_label__in=['teaching', 'words'],
                codename__in=['view_learningplan', 'add_learningplan', 'change_learningplan',
                             'view_word', 'add_word', 'change_word']
            )
        },
        {
            'role': UserRole.PARENT,
            'display_name': '家长',
            'description': '可以查看孩子的学习进度',
            'parent': None,
            'sort_order': 6,
            'permissions': all_permissions.filter(
                codename__in=['view_learningplan', 'view_word']
            )
        },
        {
            'role': UserRole.STUDENT,
            'display_name': '学生',
            'description': '进行学习和练习',
            'parent': UserRole.TEACHER,
            'sort_order': 7,
            'permissions': all_permissions.filter(
                codename__in=['view_learningplan', 'view_word', 'change_customuser']
            )
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    # 首先创建所有角色（不设置父角色）
    for config in role_configs:
        role_mgmt, created = RoleManagement.objects.get_or_create(
            role=config['role'],
            defaults={
                'display_name': config['display_name'],
                'description': config['description'],
                'sort_order': config['sort_order'],
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ 创建角色: {role_mgmt.display_name} ({role_mgmt.role})")
        else:
            # 更新现有角色
            role_mgmt.display_name = config['display_name']
            role_mgmt.description = config['description']
            role_mgmt.sort_order = config['sort_order']
            role_mgmt.save()
            updated_count += 1
            print(f"↻ 更新角色: {role_mgmt.display_name} ({role_mgmt.role})")
        
        # 设置权限
        role_mgmt.permissions.set(config['permissions'])
        print(f"  └─ 设置权限: {config['permissions'].count()} 个")
    
    # 然后设置父子关系
    for config in role_configs:
        if config['parent']:
            try:
                child_role = RoleManagement.objects.get(role=config['role'])
                parent_role = RoleManagement.objects.get(role=config['parent'])
                child_role.parent = parent_role
                child_role.save()
                print(f"  └─ 设置继承: {child_role.display_name} ← {parent_role.display_name}")
            except RoleManagement.DoesNotExist:
                print(f"  ✗ 设置继承失败: {config['role']} ← {config['parent']}")
    
    print(f"\n角色管理配置完成: 创建 {created_count} 个，更新 {updated_count} 个")


def create_role_menu_permissions():
    """创建角色菜单权限配置"""
    print("\n=== 创建角色菜单权限 ===")
    
    # 获取所有菜单模块
    menu_modules = MenuModuleConfig.objects.all()
    
    # 定义角色菜单权限矩阵
    role_menu_matrix = {
        UserRole.ADMIN: {  # 管理员可以访问所有菜单
            'allowed_menus': [menu.key for menu in menu_modules]
        },
        UserRole.DEAN: {  # 教导主任
            'allowed_menus': [
                'dashboard', 'teaching', 'teaching_plans', 'teaching_goals',
                'words', 'words_vocabulary', 'words_management',
                'accounts', 'accounts_users', 'accounts_roles',
                'permissions', 'permissions_menu', 'permissions_role'
            ]
        },
        UserRole.ACADEMIC_DIRECTOR: {  # 教务主任
            'allowed_menus': [
                'dashboard', 'teaching', 'teaching_plans', 'teaching_goals',
                'words', 'words_vocabulary', 'words_management',
                'accounts', 'accounts_users'
            ]
        },
        UserRole.RESEARCH_LEADER: {  # 教研组长
            'allowed_menus': [
                'dashboard', 'teaching', 'teaching_goals',
                'words', 'words_vocabulary', 'words_management'
            ]
        },
        UserRole.TEACHER: {  # 教师
            'allowed_menus': [
                'dashboard', 'teaching', 'teaching_plans',
                'words', 'words_vocabulary',
                'learning', 'learning_practice', 'learning_progress'
            ]
        },
        UserRole.PARENT: {  # 家长
            'allowed_menus': [
                'dashboard', 'learning', 'learning_progress'
            ]
        },
        UserRole.STUDENT: {  # 学生
            'allowed_menus': [
                'dashboard', 'learning', 'learning_practice', 'learning_progress',
                'learning_practice_word', 'learning_practice_test'
            ]
        }
    }
    
    created_count = 0
    updated_count = 0
    
    for role, config in role_menu_matrix.items():
        allowed_menus = config['allowed_menus']
        
        for menu_module in menu_modules:
            can_access = menu_module.key in allowed_menus
            
            permission, created = RoleMenuPermission.objects.get_or_create(
                role=role,
                menu_module=menu_module,
                defaults={'can_access': can_access}
            )
            
            if created:
                created_count += 1
                status = "✓" if can_access else "✗"
                print(f"{status} {role} → {menu_module.name}")
            else:
                # 更新现有权限
                if permission.can_access != can_access:
                    permission.can_access = can_access
                    permission.save()
                    updated_count += 1
                    status = "✓" if can_access else "✗"
                    print(f"↻ {role} → {menu_module.name} ({status})")
    
    print(f"\n菜单权限配置完成: 创建 {created_count} 个，更新 {updated_count} 个")


def sync_user_groups():
    """同步用户到对应的组"""
    print("\n=== 同步用户组 ===")
    
    users = CustomUser.objects.filter(is_active=True)
    synced_count = 0
    
    for user in users:
        try:
            # 获取用户角色对应的组映射
            mapping = RoleGroupMapping.objects.get(role=user.role)
            
            # 清除用户现有的所有组
            user.groups.clear()
            
            # 添加用户到对应组
            user.groups.add(mapping.group)
            
            synced_count += 1
            print(f"✓ {user.username} ({user.role}) → {mapping.group.name}")
            
        except RoleGroupMapping.DoesNotExist:
            print(f"✗ {user.username} ({user.role}) - 未找到对应的组映射")
        except Exception as e:
            print(f"✗ {user.username} ({user.role}) - 同步失败: {e}")
    
    print(f"\n用户组同步完成: {synced_count} 个用户")


def create_sync_log(action, result, success=True):
    """创建同步日志"""
    PermissionSyncLog.objects.create(
        sync_type='manual',
        target_type='system',
        target_id='fix_permissions_data',
        action=action,
        result=result,
        success=success
    )


def main():
    """主函数"""
    print("开始修复权限系统数据...")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # 1. 创建菜单模块配置
            create_menu_modules()
            create_sync_log("创建菜单模块配置", "成功创建和更新菜单模块配置")
            
            # 2. 创建角色用户组
            create_role_groups()
            create_sync_log("创建角色用户组", "成功创建角色对应的用户组和映射")
            
            # 3. 创建角色管理数据
            create_role_management()
            create_sync_log("创建角色管理数据", "成功创建角色管理配置和权限")
            
            # 4. 创建角色菜单权限
            create_role_menu_permissions()
            create_sync_log("创建角色菜单权限", "成功配置角色菜单访问权限")
            
            # 5. 同步用户组
            sync_user_groups()
            create_sync_log("同步用户组", "成功同步用户到对应组")
            
        print("\n" + "=" * 50)
        print("✅ 权限系统数据修复完成！")
        print("\n📊 数据统计:")
        print(f"   菜单模块: {MenuModuleConfig.objects.count()} 个")
        print(f"   用户组: {Group.objects.count()} 个")
        print(f"   角色映射: {RoleGroupMapping.objects.count()} 个")
        print(f"   角色管理: {RoleManagement.objects.count()} 个")
        print(f"   菜单权限: {RoleMenuPermission.objects.count()} 个")
        print(f"   活跃用户: {CustomUser.objects.filter(is_active=True).count()} 个")
        
        print("\n🔗 访问链接:")
        print("   后台管理: http://127.0.0.1:8001/admin/")
        print("   权限管理: http://127.0.0.1:8001/admin/permissions/")
        print("   用户管理: http://127.0.0.1:8001/admin/accounts/")
        
    except Exception as e:
        print(f"\n❌ 修复过程中出现错误: {e}")
        create_sync_log("权限数据修复", f"修复失败: {e}", success=False)
        sys.exit(1)


if __name__ == '__main__':
    main()