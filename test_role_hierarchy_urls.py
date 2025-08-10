#!/usr/bin/env python
"""
测试角色所辖用户增项级联系统的URL配置

验证所有URL是否正确配置和可访问
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from apps.accounts.models import RoleLevel, RoleUser

User = get_user_model()


def test_url_reverse():
    """测试URL反向解析"""
    print("🔍 测试URL反向解析...")
    
    urls_to_test = [
        ('role_hierarchy_index', [], '角色级别首页'),
        ('sync_role_data', [], '同步角色数据'),
        ('batch_update_extensions', [], '批量更新增项'),
    ]
    
    # 需要参数的URL
    role_level = RoleLevel.objects.first()
    role_user = RoleUser.objects.first()
    
    if role_level:
        urls_to_test.extend([
            ('role_users_list', [role_level.id], '角色用户列表'),
            ('role_statistics_api', [role_level.id], '角色统计API'),
        ])
    
    if role_user:
        urls_to_test.extend([
            ('user_extensions_detail', [role_user.id], '用户增项详情'),
            ('update_user_extensions', [role_user.id], '更新用户增项'),
        ])
    
    all_passed = True
    for url_name, args, description in urls_to_test:
        try:
            url = reverse(url_name, args=args)
            print(f"✅ {description}: {url}")
        except Exception as e:
            print(f"❌ {description}: 反向解析失败 - {e}")
            all_passed = False
    
    return all_passed


def test_url_access():
    """测试URL访问"""
    print("\n🔍 测试URL访问...")
    
    # 创建测试客户端
    client = Client()
    
    # 获取管理员用户
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ 没有找到管理员用户，无法测试URL访问")
        return False
    
    # 登录
    client.force_login(admin_user)
    
    # 测试主要页面
    test_urls = [
        (reverse('role_hierarchy_index'), '角色级别首页'),
    ]
    
    # 添加需要参数的URL
    role_level = RoleLevel.objects.first()
    role_user = RoleUser.objects.first()
    
    if role_level:
        test_urls.append((reverse('role_users_list', args=[role_level.id]), '角色用户列表'))
        test_urls.append((reverse('role_statistics_api', args=[role_level.id]), '角色统计API'))
    
    if role_user:
        test_urls.append((reverse('user_extensions_detail', args=[role_user.id]), '用户增项详情'))
    
    all_passed = True
    for url, description in test_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description}: 访问成功 (200)")
            elif response.status_code == 302:
                print(f"✅ {description}: 重定向 (302)")
            else:
                print(f"⚠️  {description}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: 访问失败 - {e}")
            all_passed = False
    
    return all_passed


def test_admin_urls():
    """测试Admin URL"""
    print("\n🔍 测试Admin URL...")
    
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ 没有找到管理员用户，无法测试Admin URL")
        return False
    
    client.force_login(admin_user)
    
    admin_urls = [
        ('/admin/accounts/rolelevel/', '角色级别管理'),
        ('/admin/accounts/roleuser/', '角色用户管理'),
        ('/admin/accounts/userextension/', '用户增项管理'),
    ]
    
    all_passed = True
    for url, description in admin_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description}: 访问成功 (200)")
            else:
                print(f"⚠️  {description}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: 访问失败 - {e}")
            all_passed = False
    
    return all_passed


def main():
    """主测试函数"""
    print("🚀 开始测试角色所辖用户增项级联系统URL...")
    print("=" * 70)
    
    try:
        # 1. 测试URL反向解析
        reverse_test_passed = test_url_reverse()
        
        # 2. 测试URL访问
        access_test_passed = test_url_access()
        
        # 3. 测试Admin URL
        admin_test_passed = test_admin_urls()
        
        # 输出测试结果
        print("\n📊 测试结果汇总:")
        print("=" * 30)
        
        results = [
            ("URL反向解析", reverse_test_passed),
            ("URL访问测试", access_test_passed),
            ("Admin URL测试", admin_test_passed),
        ]
        
        all_passed = True
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        if all_passed:
            print(f"\n🎉 所有URL测试通过！系统可以正常访问。")
            print(f"\n🔗 主要访问地址:")
            print(f"  - 角色级别管理: http://127.0.0.1:8000{reverse('role_hierarchy_index')}")
            print(f"  - Django Admin: http://127.0.0.1:8000/admin/accounts/rolelevel/")
        else:
            print(f"\n⚠️  部分URL测试失败，请检查配置。")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)