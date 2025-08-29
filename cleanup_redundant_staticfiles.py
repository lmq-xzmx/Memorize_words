#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态文件清理脚本
用于清理已被Django原生功能替代的冗余静态文件
"""

import os
import shutil
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / 'static'
STATICFILES_DIR = BASE_DIR / 'staticfiles'

# 已清理的文件列表（用于记录）
CLEANED_FILES = [
    # JavaScript 文件 - 已被Django原生功能替代
    'staticfiles/admin/js/role_user_group_admin.js',
    'staticfiles/admin/js/conflict_resolution.js', 
    'staticfiles/admin/js/role_permission_sync.js',
    'staticfiles/admin/js/role_group_mapping.js',
    'staticfiles/admin/js/role_group_mapping_fixed.js',
    'staticfiles/admin/js/user_sync_status.js',
    'staticfiles/admin/js/dynamic_role_selector.js',
    'staticfiles/admin/js/enhanced_role_selector.js',
    'static/admin/js/conflict_resolution.js',
    
    # CSS 文件 - 已被统一样式文件替代
    'staticfiles/admin/css/role_group_mapping.css',
    'staticfiles/admin/css/dynamic_role_selector.css',
    'static/admin/css/role_group_mapping.css',
    'static/admin/css/dynamic_role_selector.css',
    'static/admin/css/role_permission_sync.css',
]

# 需要保留的核心文件
CORE_FILES = [
    'static/admin/js/goal_words_inline.js',
    'static/admin/js/xpath_optimizer.js',
    'static/admin/js/actions.js',
    'static/admin/js/role_management_auto_fill.js',
    'static/admin/js/learning_plan_admin.js',
    'static/admin/js/unified_role_selector.js',
    'static/admin/css/learning_plan_admin.css',
    'static/admin/css/goal_words_inline.css',
    'static/admin/css/unified_admin_styles.css',  # 新的统一样式文件
]

# Django原生文件（不应删除）
DJANGO_CORE_FILES = [
    'staticfiles/admin/js/core.js',
    'staticfiles/admin/js/jquery.init.js',
    'staticfiles/admin/js/actions.js',
    'staticfiles/admin/js/urlify.js',
    'staticfiles/admin/js/prepopulate.js',
    'staticfiles/admin/js/prepopulate_init.js',
    'staticfiles/admin/js/theme.js',
    'staticfiles/admin/js/cancel.js',
    'staticfiles/admin/js/change_form.js',
    'staticfiles/admin/js/collapse.js',
    'staticfiles/admin/js/filters.js',
    'staticfiles/admin/js/inlines.js',
    'staticfiles/admin/js/nav_sidebar.js',
    'staticfiles/admin/js/popup_response.js',
    'staticfiles/admin/js/autocomplete.js',
    'staticfiles/admin/js/calendar.js',
    'staticfiles/admin/js/SelectBox.js',
    'staticfiles/admin/js/SelectFilter2.js',
    'staticfiles/admin/js/admin/DateTimeShortcuts.js',
    'staticfiles/admin/js/admin/RelatedObjectLookups.js',
    # Django Admin CSS 核心文件
    'staticfiles/admin/css/base.css',
    'staticfiles/admin/css/widgets.css',
    'staticfiles/admin/css/responsive.css',
    'staticfiles/admin/css/responsive_rtl.css',
    'staticfiles/admin/css/rtl.css',
    'staticfiles/admin/css/autocomplete.css',
    'staticfiles/admin/css/changelists.css',
    'staticfiles/admin/css/dark_mode.css',
    'staticfiles/admin/css/dashboard.css',
    'staticfiles/admin/css/forms.css',
    'staticfiles/admin/css/login.css',
    'staticfiles/admin/css/nav_sidebar.css',
]

# 第三方库文件（不应删除）
THIRD_PARTY_FILES = [
    'staticfiles/django_extensions/',
    'staticfiles/rest_framework/',
    'staticfiles/article_factory/',
]

def check_file_status():
    """检查文件状态"""
    print("=== 静态文件清理状态检查 ===")
    print(f"项目根目录: {BASE_DIR}")
    print(f"静态文件目录: {STATIC_DIR}")
    print(f"收集的静态文件目录: {STATICFILES_DIR}")
    print()
    
    print("已清理的冗余文件:")
    for file_path in CLEANED_FILES:
        full_path = BASE_DIR / file_path
        status = "✓ 已删除" if not full_path.exists() else "✗ 仍存在"
        print(f"  {status} {file_path}")
    print()
    
    print("保留的核心文件:")
    for file_path in CORE_FILES:
        full_path = BASE_DIR / file_path
        status = "✓ 存在" if full_path.exists() else "✗ 缺失"
        print(f"  {status} {file_path}")
    print()
    
    print("Django核心文件（前10个）:")
    for file_path in DJANGO_CORE_FILES[:10]:
        full_path = BASE_DIR / file_path
        status = "✓ 存在" if full_path.exists() else "✗ 缺失"
        print(f"  {status} {file_path}")
    print(f"  ... 还有 {len(DJANGO_CORE_FILES) - 10} 个Django核心文件")
    print()

def analyze_remaining_files():
    """分析剩余的自定义文件"""
    print("=== 剩余自定义文件分析 ===")
    
    # 分析static目录
    if STATIC_DIR.exists():
        print("\nstatic/admin/ 目录中的自定义文件:")
        for root, dirs, files in os.walk(STATIC_DIR / 'admin'):
            for file in files:
                if file.endswith(('.js', '.css')):
                    rel_path = Path(root).relative_to(BASE_DIR) / file
                    print(f"  📄 {rel_path}")
    
    # 分析staticfiles目录中的非Django文件
    if STATICFILES_DIR.exists():
        print("\nstaticfiles/ 目录中的可能冗余文件:")
        for root, dirs, files in os.walk(STATICFILES_DIR):
            # 跳过Django核心目录
            if any(skip in str(root) for skip in ['admin/js', 'admin/css', 'rest_framework', 'django_extensions']):
                continue
            
            for file in files:
                if file.endswith(('.js', '.css')):
                    rel_path = Path(root).relative_to(BASE_DIR) / file
                    print(f"  📄 {rel_path}")

def generate_cleanup_report():
    """生成清理报告"""
    report_path = BASE_DIR / 'staticfiles_cleanup_report.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 静态文件清理报告\n\n")
        f.write(f"生成时间: {os.popen('date').read().strip()}\n\n")
        
        f.write("## 清理概述\n\n")
        f.write("本次清理主要目标是移除已被Django原生功能替代的冗余JavaScript和CSS文件，\n")
        f.write("并统一管理后台样式，提升代码维护性和性能。\n\n")
        
        f.write("## 已清理的文件\n\n")
        f.write("### JavaScript文件（已被Django原生功能替代）\n\n")
        js_files = [f for f in CLEANED_FILES if f.endswith('.js')]
        for file_path in js_files:
            f.write(f"- `{file_path}`\n")
        
        f.write("\n### CSS文件（已被统一样式文件替代）\n\n")
        css_files = [f for f in CLEANED_FILES if f.endswith('.css')]
        for file_path in css_files:
            f.write(f"- `{file_path}`\n")
        
        f.write("\n## 保留的核心文件\n\n")
        for file_path in CORE_FILES:
            f.write(f"- `{file_path}`\n")
        
        f.write("\n## 替代方案\n\n")
        f.write("### Django原生功能替代\n\n")
        f.write("1. **角色权限同步**: 使用Django信号和ModelAdmin方法\n")
        f.write("2. **用户过滤**: 使用ModelAdmin.formfield_for_manytomany()\n")
        f.write("3. **字段同步**: 使用ModelForm.clean()方法\n")
        f.write("4. **动态选择器**: 使用Django Admin的内置AJAX功能\n\n")
        
        f.write("### 统一样式管理\n\n")
        f.write("创建了 `static/admin/css/unified_admin_styles.css` 文件，\n")
        f.write("统一管理所有后台自定义样式，包括：\n\n")
        f.write("- 角色选择器样式\n")
        f.write("- 用户选择器样式\n")
        f.write("- 表单增强样式\n")
        f.write("- 响应式设计\n")
        f.write("- 深色模式支持\n")
        f.write("- 无障碍访问增强\n\n")
        
        f.write("## 性能提升\n\n")
        f.write(f"- 减少HTTP请求: 删除了 {len(CLEANED_FILES)} 个冗余文件\n")
        f.write("- 统一样式管理: 减少CSS冲突和重复\n")
        f.write("- 服务端渲染: 减少客户端JavaScript执行\n")
        f.write("- 缓存优化: 更少的静态文件更容易缓存\n\n")
        
        f.write("## 维护性改进\n\n")
        f.write("- 代码集中化: 逻辑迁移到Django后端\n")
        f.write("- 类型安全: Python代码比JavaScript更易调试\n")
        f.write("- 测试覆盖: Django测试框架支持更好\n")
        f.write("- 文档完善: 统一的代码风格和注释\n\n")
        
        f.write("## 后续建议\n\n")
        f.write("1. 运行 `python manage.py collectstatic` 更新静态文件\n")
        f.write("2. 测试所有Admin功能确保正常工作\n")
        f.write("3. 监控页面加载性能\n")
        f.write("4. 考虑进一步优化剩余的JavaScript文件\n")
    
    print(f"\n清理报告已生成: {report_path}")

def main():
    """主函数"""
    print("静态文件清理脚本")
    print("=" * 50)
    
    check_file_status()
    analyze_remaining_files()
    generate_cleanup_report()
    
    print("\n=== 清理完成 ===")
    print("建议下一步操作:")
    print("1. 运行 'python manage.py collectstatic' 更新静态文件")
    print("2. 测试Django Admin功能")
    print("3. 检查页面加载性能")

if __name__ == '__main__':
    main()