#!/usr/bin/env python
"""
检查用户角色组同步状态
"""

import os
import sys
import django
from typing import Any

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth.models import Group
from apps.accounts.models import CustomUser, UserRole
from apps.accounts.admin import ROLE_GROUP_MAPPING

def check_groups_exist():
    """检查所有角色组是否存在"""
    print("=== 检查角色组是否存在 ===")
    for role, group_name in ROLE_GROUP_MAPPING.items():
        try:
            group = Group.objects.get(name=group_name)
            print(f"✅ {role} -> {group_name} (ID: {group.pk})")
        except Group.DoesNotExist:
            print(f"❌ {role} -> {group_name} (不存在)")
    print()

def check_user_sync_status():
    """检查用户同步状态"""
    print("=== 检查用户角色组同步状态 ===")
    users = CustomUser.objects.all().prefetch_related('groups')
    
    for user in users:
        role_group = ROLE_GROUP_MAPPING.get(user.role)
        user_groups = list(user.groups.values_list('name', flat=True))
        
        print(f"用户: {user.username} (ID: {user.pk})")
        print(f"  角色: {user.role} ({getattr(user, 'get_role_display', lambda: user.role)()})")
        print(f"  期望组: {role_group}")
        print(f"  实际组: {user_groups}")
        
        if role_group:
            if role_group in user_groups:
                print(f"  状态: ✅ 已同步")
            else:
                print(f"  状态: ❌ 未同步")
                # 检查原因
                try:
                    Group.objects.get(name=role_group)
                    print(f"  原因: 用户未被分配到组 '{role_group}'")
                except Group.DoesNotExist:
                    print(f"  原因: 组 '{role_group}' 不存在")
        else:
            print(f"  状态: ⚠️ 角色无对应组")
        print()

def check_specific_users():
    """检查前两个用户的详细信息"""
    print("=== 检查前两个用户详细信息 ===")
    users = CustomUser.objects.all().order_by('id')[:2]
    
    for i, user in enumerate(users, 1):
        print(f"第{i}个用户:")
        print(f"  ID: {user.pk}")
        print(f"  用户名: {user.username}")
        print(f"  真实姓名: {getattr(user, 'real_name', '')}")
        print(f"  角色: {user.role} ({getattr(user, 'get_role_display', lambda: user.role)()})")
        print(f"  所属组: {list(user.groups.values_list('name', flat=True))}")
        
        role_group = ROLE_GROUP_MAPPING.get(user.role)
        if role_group:
            print(f"  期望组: {role_group}")
            if role_group in user.groups.values_list('name', flat=True):
                print(f"  同步状态: ✅ 已同步")
            else:
                print(f"  同步状态: ❌ 未同步")
        print()

if __name__ == '__main__':
    check_groups_exist()
    check_user_sync_status()
    check_specific_users()