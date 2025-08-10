#!/usr/bin/env python
"""
角色继承系统演示脚本

展示核心功能：
1. 角色继承层级结构
2. 权限继承机制
3. Django组同步
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth.models import Group
from apps.accounts.models import UserRole
from apps.permissions.models import RoleManagement, RoleGroupMapping


def display_role_hierarchy():
    """显示角色继承层级"""
    print("\n🏗️  角色继承层级结构")
    print("=" * 50)
    
    # 获取所有角色并按层级排序
    roles = RoleManagement.objects.all()
    
    # 找到根角色（没有父角色的角色）
    root_roles = [role for role in roles if role.parent is None]
    
    def print_role_tree(role, level=0):
        """递归打印角色树"""
        indent = "  " * level
        icon = "👑" if level == 0 else "📁"
        
        # 获取权限信息
        direct_perms = role.permissions.count()
        total_perms = len(role.get_all_permissions())
        inherited_perms = total_perms - direct_perms
        
        print(f"{indent}{icon} {role.display_name}")
        print(f"{indent}   └─ 层级: {level}")
        print(f"{indent}   └─ 直接权限: {direct_perms}")
        print(f"{indent}   └─ 继承权限: {inherited_perms}")
        print(f"{indent}   └─ 总权限: {total_perms}")
        
        # 显示对应的Django组
        try:
            mapping = RoleGroupMapping.objects.get(role=role.role)
            print(f"{indent}   └─ Django组: {mapping.group.name}")
        except RoleGroupMapping.DoesNotExist:
            print(f"{indent}   └─ Django组: 未映射")
        
        print()
        
        # 递归显示子角色
        children = role.get_children().order_by('role')
        for child in children:
            print_role_tree(child, level + 1)
    
    # 打印所有根角色的树
    for root in root_roles:
        print_role_tree(root)


def display_inheritance_chain():
    """显示权限继承链"""
    print("\n🔗 权限继承链分析")
    print("=" * 50)
    
    try:
        # 从学生角色开始，向上追溯继承链
        student_role = RoleManagement.objects.get(role=UserRole.STUDENT)
        
        current_role = student_role
        chain = []
        
        # 构建继承链
        while current_role:
            chain.append(current_role)
            current_role = current_role.parent
        
        # 反转链条，从根角色开始显示
        chain.reverse()
        
        print("📊 继承链路径:")
        for i, role in enumerate(chain):
            arrow = " → " if i < len(chain) - 1 else ""
            print(f"  {role.display_name}{arrow}", end="")
        print("\n")
        
        # 显示每个角色的权限贡献
        print("📋 权限贡献分析:")
        accumulated_perms = set()
        
        for role in chain:
            direct_perms = set(role.permissions.values_list('codename', flat=True))
            new_perms = direct_perms - accumulated_perms
            accumulated_perms.update(direct_perms)
            
            print(f"  {role.display_name}:")
            print(f"    └─ 新增权限: {len(new_perms)}")
            print(f"    └─ 累计权限: {len(accumulated_perms)}")
            
            if new_perms and len(new_perms) <= 5:  # 只显示少量权限作为示例
                print(f"    └─ 示例权限: {', '.join(list(new_perms)[:3])}...")
            print()
        
    except RoleManagement.DoesNotExist:
        print("❌ 学生角色不存在")


def display_group_sync_status():
    """显示Django组同步状态"""
    print("\n🔄 Django组同步状态")
    print("=" * 50)
    
    from apps.permissions.models import RoleGroupMapping
    
    print("📊 角色组映射状态:")
    mappings = RoleGroupMapping.objects.all().order_by('role')
    
    for mapping in mappings:
        role_obj = RoleManagement.objects.get(role=mapping.role)
        group_perms = mapping.group.permissions.count()
        role_total_perms = len(role_obj.get_all_permissions())
        
        sync_status = "✅ 同步" if group_perms == role_total_perms else "❌ 不同步"
        
        print(f"  {mapping.get_role_display()}:")
        print(f"    └─ Django组: {mapping.group.name}")
        print(f"    └─ 组权限数: {group_perms}")
        print(f"    └─ 角色权限数: {role_total_perms}")
        print(f"    └─ 同步状态: {sync_status}")
        print(f"    └─ 自动同步: {'✅' if mapping.auto_sync else '❌'}")
        print()


def display_role_relationships():
    """显示角色关系矩阵"""
    print("\n🔍 角色关系分析")
    print("=" * 50)
    
    roles = list(RoleManagement.objects.all().order_by('role'))
    
    print("📊 角色层级关系:")
    for role in roles:
        ancestors = []
        current = role.parent
        while current:
            ancestors.append(current.display_name)
            current = current.parent
        
        descendants = []
        def collect_descendants(r):
            for child in r.get_children():
                descendants.append(child.display_name)
                collect_descendants(child)
        
        collect_descendants(role)
        
        print(f"  {role.display_name}:")
        print(f"    └─ 祖先角色: {' → '.join(reversed(ancestors)) if ancestors else '无'}")
        print(f"    └─ 后代角色: {' → '.join(descendants) if descendants else '无'}")
        print(f"    └─ 层级深度: {role.get_hierarchy_level()}")
        print()


def main():
    """主演示函数"""
    print("🎭 Django 角色继承系统演示")
    print("=" * 60)
    print("本演示展示了基于Django的角色继承和权限管理系统")
    print("包含角色层级、权限继承、Django组同步等核心功能")
    
    try:
        display_role_hierarchy()
        display_inheritance_chain()
        display_group_sync_status()
        display_role_relationships()
        
        print("\n🎉 演示完成！")
        print("=" * 60)
        print("\n💡 核心特性总结:")
        print("  ✅ 支持多层级角色继承")
        print("  ✅ 自动权限继承机制")
        print("  ✅ Django组权限同步")
        print("  ✅ 循环继承检测")
        print("  ✅ 灵活的权限管理")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()