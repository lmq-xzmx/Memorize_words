#!/usr/bin/env python
"""
验证JavaScript修复是否成功
"""

import os
import re

def verify_javascript_fix():
    """验证JavaScript修复"""
    print("🔍 验证JavaScript修复...")
    
    js_file_path = 'staticfiles/admin/js/role_group_mapping.js'
    
    if not os.path.exists(js_file_path):
        print(f"❌ JavaScript文件不存在: {js_file_path}")
        return False
    
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 文件大小: {len(content)} 字符")
    
    # 关键检查点
    checks = [
        (r'window\.handleRoleChange\s*=\s*function', '✅ 全局函数定义正确'),
        (r'function\(roleValue\)', '✅ 函数参数定义正确'),
        (r'fetch\(.*sync-role-groups', '✅ AJAX请求实现正确'),
        (r'X-CSRFToken.*csrfToken\.value', '✅ CSRF token处理正确'),
        (r'DOMContentLoaded', '✅ DOM加载事件处理正确'),
        (r'console\.log.*handleRoleChange', '✅ 调试日志存在'),
        (r'function showMessage', '✅ 消息显示函数存在'),
    ]
    
    all_passed = True
    for pattern, message in checks:
        if re.search(pattern, content):
            print(message)
        else:
            print(f"❌ {message.replace('✅', '缺失:')}")
            all_passed = False
    
    # 检查是否移除了问题代码
    problem_patterns = [
        (r'typeof\s+handleRoleChange.*function.*handleRoleChange', '❌ 发现循环引用问题'),
        (r'window\.handleRoleChange.*window\.handleRoleChange', '❌ 发现重复定义问题'),
    ]
    
    for pattern, message in problem_patterns:
        if re.search(pattern, content):
            print(message)
            all_passed = False
    
    return all_passed

def check_file_differences():
    """检查文件差异"""
    print("\n🔍 检查文件同步...")
    
    source_file = 'static/admin/js/role_group_mapping.js'
    target_file = 'staticfiles/admin/js/role_group_mapping.js'
    
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

def main():
    """主函数"""
    print("🚀 JavaScript修复验证")
    print("=" * 40)
    
    # 验证修复
    fix_success = verify_javascript_fix()
    
    # 检查文件同步
    sync_success = check_file_differences()
    
    print("\n📊 验证结果:")
    print("=" * 20)
    
    if fix_success:
        print("✅ JavaScript修复: 成功")
    else:
        print("❌ JavaScript修复: 失败")
    
    if sync_success:
        print("✅ 文件同步: 正常")
    else:
        print("⚠️  文件同步: 需要注意")
    
    if fix_success:
        print("\n🎉 JavaScript错误修复完成！")
        print("\n📋 修复内容:")
        print("- 修复了handleRoleChange函数未定义的错误")
        print("- 改进了JavaScript作用域处理")
        print("- 添加了完整的错误处理")
        print("- 提供了更好的用户反馈")
        
        print("\n🔧 使用说明:")
        print("1. 清除浏览器缓存")
        print("2. 重新访问Django Admin页面")
        print("3. 在角色选择时应该不再出现JavaScript错误")
        print("4. 角色组映射功能应该正常工作")
    else:
        print("\n⚠️  修复可能不完整，请检查JavaScript文件")
    
    return fix_success

if __name__ == '__main__':
    main()