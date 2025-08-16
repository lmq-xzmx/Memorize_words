#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加开发工具权限脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.permissions.models import RoleManagement

def add_dev_tools_permission():
    """添加开发工具权限"""
    try:
        # 获取Permission模型的ContentType
        ct = ContentType.objects.get_for_model(Permission)
        
        # 创建access_dev_tools权限
        perm, created = Permission.objects.get_or_create(
            codename='access_dev_tools',
            name='Can access development tools',
            content_type=ct
        )
        
        print(f'权限创建结果: {"新创建" if created else "已存在"} - {perm}')
        
        # 获取管理员角色
        admin_role = RoleManagement.objects.filter(role='admin').first()
        if admin_role:
            # 添加权限到管理员角色
            admin_role.permissions.add(perm)
            print(f'已将access_dev_tools权限添加到管理员角色: {admin_role.display_name}')
            
            # 验证权限是否添加成功
            has_permission = admin_role.permissions.filter(codename='access_dev_tools').exists()
            print(f'验证结果: 管理员是否有access_dev_tools权限 - {has_permission}')
        else:
            print('错误: 未找到管理员角色')
            
        # 同时为教师角色添加此权限
        teacher_role = RoleManagement.objects.filter(role='teacher').first()
        if teacher_role:
            teacher_role.permissions.add(perm)
            print(f'已将access_dev_tools权限添加到教师角色: {teacher_role.display_name}')
            
    except Exception as e:
        print(f'添加权限失败: {e}')
        return False
        
    return True

if __name__ == '__main__':
    print('开始添加开发工具权限...')
    success = add_dev_tools_permission()
    if success:
        print('权限添加完成！')
    else:
        print('权限添加失败！')
        sys.exit(1)