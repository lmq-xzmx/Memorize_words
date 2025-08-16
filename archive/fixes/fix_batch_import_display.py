#!/usr/bin/env python
"""
修复批量导入显示问题
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

def check_and_fix_batch_import():
    """检查并修复批量导入显示问题"""
    
    print("=== 批量导入功能诊断 ===")
    
    # 1. 检查admin.py中的URL配置
    print("1. 检查admin.py中的URL配置...")
    from apps.words.admin import WordAdmin, VocabularyListAdmin, WordResourceAdmin
    
    # 检查是否有get_urls方法
    for admin_class, name in [(WordAdmin, 'WordAdmin'), (VocabularyListAdmin, 'VocabularyListAdmin'), (WordResourceAdmin, 'WordResourceAdmin')]:
        if hasattr(admin_class, 'get_urls'):
            print(f"   ✅ {name} 有 get_urls 方法")
        else:
            print(f"   ❌ {name} 缺少 get_urls 方法")
        
        if hasattr(admin_class, 'batch_import_view'):
            print(f"   ✅ {name} 有 batch_import_view 方法")
        else:
            print(f"   ❌ {name} 缺少 batch_import_view 方法")
    
    # 2. 检查模板文件
    print("\n2. 检查模板文件...")
    template_files = [
        'templates/admin/words/word/change_list.html',
        'templates/admin/words/vocabularylist/change_list.html', 
        'templates/admin/words/wordresource/change_list.html',
        'templates/admin/words/base_change_list.html'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"   ✅ {template_file} 存在")
        else:
            print(f"   ❌ {template_file} 不存在")
    
    # 3. 检查URL反向解析
    print("\n3. 检查URL反向解析...")
    from django.urls import reverse
    
    urls_to_check = [
        ('admin:words_word_batch_import', 'Word批量导入'),
        ('admin:words_vocabularylist_batch_import', 'VocabularyList批量导入'),
        ('admin:words_wordresource_batch_import', 'WordResource批量导入'),
    ]
    
    for url_name, description in urls_to_check:
        try:
            url = reverse(url_name)
            print(f"   ✅ {description}: {url}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")
    
    # 4. 生成修复建议
    print("\n=== 修复建议 ===")
    print("如果批量导入按钮仍然不显示，请尝试以下步骤：")
    print("1. 重启Django开发服务器")
    print("2. 清除浏览器缓存")
    print("3. 检查用户权限（需要staff权限）")
    print("4. 在admin界面的URL后手动添加 /batch_import/ 来直接访问")
    print("   例如：http://localhost:8000/admin/words/word/batch_import/")
    
    # 5. 创建直接访问链接
    print("\n=== 直接访问链接 ===")
    base_url = "http://localhost:8000"
    direct_links = [
        f"{base_url}/admin/words/word/batch_import/",
        f"{base_url}/admin/words/vocabularylist/batch_import/",
        f"{base_url}/admin/words/wordresource/batch_import/",
    ]
    
    for link in direct_links:
        print(f"   {link}")

if __name__ == '__main__':
    check_and_fix_batch_import()