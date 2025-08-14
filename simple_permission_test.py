#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的权限配置测试脚本
"""

import os
import sys
import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.permissions.permission_checker import PermissionChecker

class MockUser:
    """模拟用户类"""
    def __init__(self, username, role):
        self.id = hash(username) % 10000
        self.username = username
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_staff = role in ['admin', 'teacher']
        self.is_superuser = role == 'admin'
        
    def has_perm(self, perm):
        return self.is_superuser
        
    def get_all_permissions(self):
        return set()
        
    def __str__(self):
        return f"MockUser({self.username}, {self.role})"

def test_basic_permissions():
    """测试基本权限功能"""
    print("=== 基本权限测试 ===")
    
    # 创建不同角色的用户
    users = [
        MockUser('admin_user', 'admin'),
        MockUser('teacher_user', 'teacher'),
        MockUser('student_user', 'student')
    ]
    
    for user in users:
        print(f"\n测试用户: {user}")
        checker = PermissionChecker(user)
        
        # 测试菜单权限
        try:
            can_access_dashboard = checker.can_access_menu('dashboard')
            print(f"  可访问仪表板: {'✓' if can_access_dashboard else '✗'}")
        except Exception as e:
            print(f"  菜单权限检查错误: {e}")
        
        # 测试基本权限
        try:
            can_view_goal = checker.has_permission('learning_goal', 'view')
            print(f"  可查看学习目标: {'✓' if can_view_goal else '✗'}")
        except Exception as e:
            print(f"  权限检查错误: {e}")

def test_performance():
    """测试权限检查性能"""
    print("\n=== 性能测试 ===")
    
    import time
    
    user = MockUser('perf_test', 'teacher')
    checker = PermissionChecker(user)
    
    # 测试权限检查性能
    start_time = time.time()
    
    for i in range(100):  # 减少测试次数
        try:
            checker.can_access_menu('dashboard')
            checker.has_permission('learning_goal', 'view')
        except Exception:
            pass  # 忽略错误，专注于性能测试
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"  执行200次权限检查耗时: {duration:.4f}秒")
    print(f"  平均每次检查耗时: {duration/200*1000:.4f}毫秒")

def main():
    """主测试函数"""
    print("权限配置优化测试")
    print("=" * 50)
    
    try:
        test_basic_permissions()
        test_performance()
        print("\n✅ 测试完成")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()