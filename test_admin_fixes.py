#!/usr/bin/env python
"""
测试Admin界面修复

验证内容：
1. JavaScript错误是否修复
2. Admin名称是否正确修改
3. 权限设置是否正确
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from apps.accounts.models import RoleApproval, RoleUserGroup, UserExtensionData
from django.contrib import admin


def test_javascript_fix():
    """测试JavaScript修复"""
    print("🔍 测试JavaScript修复...")
    
    js_file_path = 'static/admin/js/role_user_group_admin.js'
    
    if not os.path.exists(js_file_path):
        print(f"❌ JavaScript文件不存在: {js_file_path}")
        return False
    
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查修复内容
    checks = [
        ('typeof django !== \'undefined\' && django.jQuery', '✅ Django jQuery检查'),
        ('typeof jQuery !== \'undefined\'', '✅ 标准jQuery检查'),
        ('typeof window.$ !== \'undefined\'', '✅ 全局$检查'),
        ('console.error(\'jQuery not found', '✅ 错误处理'),
        ('})();', '✅ 立即执行函数结构'),
    ]
    
    all_passed = True
    for pattern, message in checks:
        if pattern in content:
            print(message)
        else:
            print(f"❌ {message.replace('✅', '缺失:')}")
            all_passed = False
    
    return all_passed


def test_model_verbose_names():
    """测试模型verbose_name修改"""
    print("\n🔍 测试模型名称修改...")
    
    # 检查模型的verbose_name
    models_to_check = [
        (RoleApproval, '注册管理员审批', '注册管理员审批'),
        (RoleUserGroup, '角色所辖用户', '角色所辖用户'),
        (UserExtensionData, '角色所辖用户增项', '角色所辖用户增项'),
    ]
    
    all_passed = True
    for model, expected_verbose_name, expected_verbose_name_plural in models_to_check:
        actual_verbose_name = model._meta.verbose_name
        actual_verbose_name_plural = model._meta.verbose_name_plural
        
        if actual_verbose_name == expected_verbose_name:
            print(f"✅ {model.__name__}.verbose_name: {actual_verbose_name}")
        else:
            print(f"❌ {model.__name__}.verbose_name: 期望 '{expected_verbose_name}', 实际 '{actual_verbose_name}'")
            all_passed = False
        
        if actual_verbose_name_plural == expected_verbose_name_plural:
            print(f"✅ {model.__name__}.verbose_name_plural: {actual_verbose_name_plural}")
        else:
            print(f"❌ {model.__name__}.verbose_name_plural: 期望 '{expected_verbose_name_plural}', 实际 '{actual_verbose_name_plural}'")
            all_passed = False
    
    return all_passed


def test_admin_permissions():
    """测试Admin权限设置"""
    print("\n🔍 测试Admin权限设置...")
    
    # 获取UserExtensionDataAdmin
    from apps.accounts.admin import UserExtensionDataAdmin
    
    # 创建一个模拟的request对象
    class MockRequest:
        def __init__(self):
            self.user = None
    
    mock_request = MockRequest()
    admin_instance = UserExtensionDataAdmin(UserExtensionData, admin.site)
    
    # 测试权限方法
    permissions_to_check = [
        ('has_add_permission', False, '添加权限应该被禁用'),
        ('has_change_permission', False, '修改权限应该被禁用'),
        ('has_delete_permission', False, '删除权限应该被禁用'),
    ]
    
    all_passed = True
    for permission_method, expected_result, description in permissions_to_check:
        method = getattr(admin_instance, permission_method)
        actual_result = method(mock_request)
        
        if actual_result == expected_result:
            print(f"✅ {description}: {actual_result}")
        else:
            print(f"❌ {description}: 期望 {expected_result}, 实际 {actual_result}")
            all_passed = False
    
    return all_passed


def test_file_sync():
    """测试文件同步"""
    print("\n🔍 测试文件同步...")
    
    source_file = 'static/admin/js/role_user_group_admin.js'
    target_file = 'staticfiles/admin/js/role_user_group_admin.js'
    
    if not os.path.exists(source_file):
        print(f"⚠️  源文件不存在: {source_file}")
        return False
    
    if not os.path.exists(target_file):
        print(f"⚠️  目标文件不存在: {target_file}")
        return False
    
    with open(source_file, 'r', encoding='utf-8') as f:
        source_content = f.read()
    
    with open(target_file, 'r', encoding='utf-8') as f:
        target_content = f.read()
    
    if source_content == target_content:
        print("✅ 源文件和目标文件内容一致")
        return True
    else:
        print("⚠️  源文件和目标文件内容不一致")
        print(f"源文件大小: {len(source_content)} 字符")
        print(f"目标文件大小: {len(target_content)} 字符")
        return False


def generate_summary():
    """生成修复总结"""
    print("\n📋 Admin界面修复总结:")
    print("=" * 50)
    
    print("""
🔧 修复的问题:
1. role_user_group_admin.js中的jQuery未定义错误
2. Admin界面名称不符合需求
3. UserExtensionData权限设置

✅ 修复内容:
1. JavaScript兼容性处理:
   - 添加了jQuery可用性检查
   - 支持多种jQuery加载方式
   - 改进了错误处理

2. Admin名称修改:
   - RoleApproval: "角色审批管理" → "注册管理员审批"
   - RoleUserGroup: "角色用户组管理" → "角色所辖用户"
   - UserExtensionData: "用户增项数据管理" → "角色所辖用户增项"

3. 权限控制:
   - UserExtensionData禁用增删改操作
   - 只提供查看功能
   - 按角色筛选功能保持不变

📁 修改的文件:
- static/admin/js/role_user_group_admin.js
- staticfiles/admin/js/role_user_group_admin.js
- apps/accounts/models.py
- apps/accounts/admin.py

🎯 预期效果:
- 消除JavaScript控制台错误
- Admin界面名称符合需求
- 用户增项数据只读访问
- 改善整体用户体验
    """)


def main():
    """主测试函数"""
    print("🚀 开始测试Admin界面修复...")
    print("=" * 60)
    
    test_results = []
    
    # 1. 测试JavaScript修复
    test_results.append(("JavaScript修复", test_javascript_fix()))
    
    # 2. 测试模型名称修改
    test_results.append(("模型名称修改", test_model_verbose_names()))
    
    # 3. 测试Admin权限设置
    test_results.append(("Admin权限设置", test_admin_permissions()))
    
    # 4. 测试文件同步
    test_results.append(("文件同步", test_file_sync()))
    
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
        print("\n🎉 所有测试通过！Admin界面修复完成。")
        generate_summary()
    else:
        print("\n⚠️  部分测试失败，请检查相关配置。")
    
    return all_passed


if __name__ == '__main__':
    main()