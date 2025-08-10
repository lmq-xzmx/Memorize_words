#!/usr/bin/env python
"""
测试JavaScript错误修复

验证内容：
1. handleRoleChange函数是否正确定义
2. JavaScript文件是否正确加载
3. 相关URL是否正常工作
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import re


def test_javascript_file_content():
    """测试JavaScript文件内容"""
    print("🔍 测试JavaScript文件内容...")
    
    js_file_path = 'staticfiles/admin/js/role_group_mapping.js'
    
    if not os.path.exists(js_file_path):
        print(f"❌ JavaScript文件不存在: {js_file_path}")
        return False
    
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键函数是否存在
    checks = [
        ('window.handleRoleChange', 'handleRoleChange函数定义'),
        ('function(roleValue)', '函数参数定义'),
        ('fetch(', 'AJAX请求实现'),
        ('CSRF', 'CSRF token处理'),
        ('DOMContentLoaded', 'DOM加载事件'),
    ]
    
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ {description}: 存在")
        else:
            print(f"❌ {description}: 缺失")
            all_passed = False
    
    # 检查文件大小
    file_size = len(content)
    print(f"📊 文件大小: {file_size} 字符")
    
    return all_passed


def test_admin_page_access():
    """测试admin页面访问"""
    print("\n🔍 测试admin页面访问...")
    
    client = Client()
    
    # 创建超级用户进行测试
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ 没有找到超级用户，无法测试admin页面")
        return False
    
    # 登录
    client.force_login(admin_user)
    
    # 测试相关页面
    test_urls = [
        ('/admin/', 'Admin首页'),
        ('/admin/permissions/rolegroupmapping/', '角色组映射列表'),
        ('/admin/permissions/rolegroupmapping/add/', '添加角色组映射'),
        ('/admin/accounts/customuser/', '用户管理'),
    ]
    
    all_passed = True
    for url, description in test_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description}: 访问正常 (200)")
            else:
                print(f"❌ {description}: 状态码 {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {description}: 访问异常 - {e}")
            all_passed = False
    
    return all_passed


def test_javascript_loading():
    """测试JavaScript文件加载"""
    print("\n🔍 测试JavaScript文件加载...")
    
    client = Client()
    
    # 测试静态文件访问
    js_url = '/static/admin/js/role_group_mapping.js'
    
    try:
        response = client.get(js_url)
        if response.status_code == 200:
            print(f"✅ JavaScript文件加载: 正常 (200)")
            
            # 检查内容类型
            content_type = response.get('Content-Type', '')
            if 'javascript' in content_type or 'text/plain' in content_type:
                print(f"✅ 内容类型: {content_type}")
            else:
                print(f"⚠️  内容类型: {content_type} (可能不正确)")
            
            # 检查文件内容
            content = response.content.decode('utf-8')
            if 'handleRoleChange' in content:
                print("✅ 函数定义: handleRoleChange存在")
            else:
                print("❌ 函数定义: handleRoleChange缺失")
                return False
            
            return True
        else:
            print(f"❌ JavaScript文件加载: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ JavaScript文件加载异常: {e}")
        return False


def test_role_group_mapping_api():
    """测试角色组映射API"""
    print("\n🔍 测试角色组映射API...")
    
    client = Client()
    
    # 创建超级用户进行测试
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ 没有找到超级用户，无法测试API")
        return False
    
    # 登录
    client.force_login(admin_user)
    
    # 测试API端点
    api_url = '/admin/permissions/rolegroupmapping/sync-role-groups/'
    
    try:
        # 发送POST请求测试API
        response = client.post(
            api_url,
            data='{"role": "student"}',
            content_type='application/json'
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ API端点: 正常 ({response.status_code})")
            
            # 检查响应内容
            try:
                import json
                data = json.loads(response.content.decode('utf-8'))
                if 'success' in data:
                    print(f"✅ API响应: 包含success字段")
                else:
                    print(f"⚠️  API响应: 缺少success字段")
            except json.JSONDecodeError:
                print(f"⚠️  API响应: 非JSON格式")
            
            return True
        else:
            print(f"❌ API端点: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API测试异常: {e}")
        return False


def generate_fix_summary():
    """生成修复总结"""
    print("\n📋 JavaScript错误修复总结:")
    print("=" * 50)
    
    print("""
🔧 修复的问题:
1. handleRoleChange函数未定义错误
2. JavaScript作用域问题
3. CSRF token处理
4. 错误处理和用户反馈

✅ 修复方案:
1. 将handleRoleChange定义为全局函数
2. 使用原生JavaScript实现，兼容jQuery
3. 添加完整的错误处理
4. 改进用户体验和消息提示

📁 修改的文件:
- staticfiles/admin/js/role_group_mapping.js
- static/admin/js/role_group_mapping.js

🎯 预期效果:
- 消除JavaScript控制台错误
- 角色选择功能正常工作
- 改善admin界面用户体验
    """)


def main():
    """主测试函数"""
    print("🚀 开始测试JavaScript错误修复...")
    print("=" * 60)
    
    test_results = []
    
    # 1. 测试JavaScript文件内容
    test_results.append(("JavaScript文件内容", test_javascript_file_content()))
    
    # 2. 测试JavaScript文件加载
    test_results.append(("JavaScript文件加载", test_javascript_loading()))
    
    # 3. 测试admin页面访问
    test_results.append(("Admin页面访问", test_admin_page_access()))
    
    # 4. 测试API端点
    test_results.append(("角色组映射API", test_role_group_mapping_api()))
    
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
        print("\n🎉 所有测试通过！JavaScript错误已修复。")
        generate_fix_summary()
    else:
        print("\n⚠️  部分测试失败，请检查相关配置。")
    
    return all_passed


if __name__ == '__main__':
    main()