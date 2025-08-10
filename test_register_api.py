#!/usr/bin/env python3
"""
注册页面API测试脚本
用于验证角色列表和角色增项API是否正常工作
"""

import requests
import json
from datetime import datetime

def test_roles_api():
    """测试角色列表API"""
    print("\n=== 测试角色列表API ===")
    try:
        response = requests.get('http://127.0.0.1:8000/accounts/api/auth/roles/')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("角色列表:")
            for role in data.get('roles', []):
                if role[0]:  # 过滤空选项
                    print(f"  - {role[0]}: {role[1]}")
            return True
        else:
            print(f"API调用失败: {response.text}")
            return False
    except Exception as e:
        print(f"API调用异常: {e}")
        return False

def test_role_extensions_api(role):
    """测试角色增项API"""
    print(f"\n=== 测试 {role} 角色增项API ===")
    try:
        response = requests.get(f'http://127.0.0.1:8000/accounts/api/auth/role-extensions/?role={role}')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            extensions = data.get('extensions', [])
            print(f"找到 {len(extensions)} 个增项字段:")
            
            for ext in extensions:
                required = "*" if ext.get('is_required') else ""
                print(f"  - {ext['field_name']}: {ext['field_label']}{required} ({ext['field_type']})")
                if ext.get('help_text'):
                    print(f"    帮助: {ext['help_text']}")
                if ext.get('choices'):
                    print(f"    选项: {[f'{c[0]}:{c[1]}' for c in ext['choices']]}")
            return True
        else:
            print(f"API调用失败: {response.text}")
            return False
    except Exception as e:
        print(f"API调用异常: {e}")
        return False

def test_register_api():
    """测试注册API"""
    print("\n=== 测试注册API ===")
    
    # 测试数据
    test_data = {
        'username': f'test_user_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'email': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
        'real_name': '测试用户',
        'phone': '13800138000',
        'nickname': f'测试昵称_{datetime.now().strftime("%H%M%S")}',
        'role': 'student',
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        # 学生角色增项
        'ext_english_level': 'beginner',
        'ext_grade': 'grade1',
        'ext_class_name': '一年级一班',
        'ext_student_id': 'S001'
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8000/accounts/api/auth/register-with-extensions/',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("注册成功!")
            print(f"用户ID: {data.get('user', {}).get('id')}")
            print(f"用户名: {data.get('user', {}).get('username')}")
            print(f"Token: {data.get('token', '')[:20]}...")
            return True
        else:
            print(f"注册失败: {response.text}")
            return False
    except Exception as e:
        print(f"注册API调用异常: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试注册页面相关API...")
    print(f"测试时间: {datetime.now()}")
    
    # 测试角色列表API
    roles_ok = test_roles_api()
    
    # 测试各角色的增项API
    roles_to_test = ['student', 'parent', 'teacher', 'admin']
    extensions_ok = True
    
    for role in roles_to_test:
        if not test_role_extensions_api(role):
            extensions_ok = False
    
    # 测试注册API（可选，会创建真实用户）
    # register_ok = test_register_api()
    
    print("\n=== 测试结果汇总 ===")
    print(f"角色列表API: {'✓ 正常' if roles_ok else '✗ 异常'}")
    print(f"角色增项API: {'✓ 正常' if extensions_ok else '✗ 异常'}")
    # print(f"注册API: {'✓ 正常' if register_ok else '✗ 异常'}")
    
    if roles_ok and extensions_ok:
        print("\n🎉 所有API测试通过！注册页面应该可以正常工作。")
    else:
        print("\n❌ 部分API测试失败，请检查后端服务。")

if __name__ == '__main__':
    main()