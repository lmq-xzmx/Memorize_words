#!/usr/bin/env python
"""
测试vocabulary_manager的admin URL
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

def test_vocabulary_manager_admin():
    """测试vocabulary_manager的admin URL"""
    print("=== 测试vocabulary_manager的admin URL ===")
    
    print("1. 检查URL配置...")
    
    # 检查vocabulary_manager的URL配置
    try:
        from apps.vocabulary_manager.urls import urlpatterns
        print("   ✅ vocabulary_manager URL配置正常")
        print(f"   共有 {len(urlpatterns)} 个URL配置")
        
        for url_pattern in urlpatterns:
            print(f"   • {url_pattern.pattern}")
            
    except Exception as e:
        print(f"   ❌ vocabulary_manager URL配置错误: {e}")
    
    print("\n2. 检查Admin站点配置...")
    
    try:
        from apps.vocabulary_manager.admin import vocabulary_manager_admin
        print("   ✅ vocabulary_manager_admin 配置正常")
        print(f"   站点标题: {vocabulary_manager_admin.site_title}")
        print(f"   站点头部: {vocabulary_manager_admin.site_header}")
        print(f"   索引标题: {vocabulary_manager_admin.index_title}")
        
    except Exception as e:
        print(f"   ❌ vocabulary_manager_admin 配置错误: {e}")
    
    print("\n3. 检查注册的模型...")
    
    try:
        from apps.vocabulary_manager.admin import vocabulary_manager_admin
        registered_models = vocabulary_manager_admin._registry
        print(f"   ✅ 注册了 {len(registered_models)} 个模型")
        
        for model, admin_class in registered_models.items():
            print(f"   • {model._meta.verbose_name} ({model.__name__})")
            
    except Exception as e:
        print(f"   ❌ 检查注册模型时出错: {e}")
    
    print("\n4. URL列表...")
    print("   成长中心主页: http://localhost:8001/vocabulary-manager/")
    print("   成长中心Admin: http://localhost:8001/vocabulary-manager/admin/")
    print("   学习中（看板）: http://localhost:8001/vocabulary-manager/kanban/")
    print("   学习目标管理: http://localhost:8001/vocabulary-manager/admin/vocabulary_manager/learninggoal/")
    print("   学习计划管理: http://localhost:8001/vocabulary-manager/admin/vocabulary_manager/learningplan/")
    print("   单词学习进度: http://localhost:8001/vocabulary-manager/admin/vocabulary_manager/wordlearningprogress/")
    
    print("\n5. 使用说明...")
    print("   • 访问 http://localhost:8001/vocabulary-manager/admin/ 进入成长中心管理后台")
    print("   • 在管理后台中可以管理学习目标、学习计划、单词学习进度等")
    print("   • 访问 http://localhost:8001/vocabulary-manager/kanban/ 查看学习中（看板）")
    print("   • 访问 http://localhost:8001/vocabulary-manager/ 查看成长中心主页")
    
    print("\n✅ vocabulary_manager admin URL测试完成！")

if __name__ == '__main__':
    test_vocabulary_manager_admin() 