#!/usr/bin/env python3
"""
移除已被Django原生功能和统一API替代的冗余JavaScript文件

这些文件的功能已经通过以下方式替代：
1. unified_ajax_api.py - 提供统一的REST API端点
2. Django信号处理 - 自动同步权限
3. ModelAdmin方法 - 内置表单验证和处理
"""

import os
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
STATIC_JS_DIR = PROJECT_ROOT / 'static' / 'admin' / 'js'

# 需要移除的冗余JavaScript文件列表
REDUNDANT_JS_FILES = [
    # 角色权限同步相关 - 已被unified_ajax_api.py替代
    'role_permission_sync.js',
    
    # 角色组映射相关 - 已被unified_ajax_api.py替代
    'role_group_mapping.js',
    'role_group_mapping_fixed.js',  # 重复文件
    
    # 用户同步状态相关 - 已被unified_ajax_api.py替代
    'user_sync_status.js',
    
    # 菜单有效性过滤 - 已被unified_ajax_api.py替代
    'menu_validity_filter.js',
    
    # 角色用户组管理 - 已被Django ModelAdmin替代
    'role_user_group_admin.js',
]

# 需要保留的文件（已优化或仍需要的）
KEEP_FILES = [
    'unified_role_selector.js',  # 已优化的统一角色选择器
    'xpath_optimizer.js',        # XPath优化工具
    'role_management_auto_fill.js',  # 角色管理自动填充
]

def backup_files():
    """备份要删除的文件"""
    backup_dir = PROJECT_ROOT / 'backup_js_files'
    backup_dir.mkdir(exist_ok=True)
    
    backed_up_files = []
    
    for js_file in REDUNDANT_JS_FILES:
        source_path = STATIC_JS_DIR / js_file
        if source_path.exists():
            backup_path = backup_dir / js_file
            shutil.copy2(source_path, backup_path)
            backed_up_files.append(js_file)
            print(f"✅ 已备份: {js_file}")
        else:
            print(f"⚠️  文件不存在: {js_file}")
    
    return backed_up_files

def remove_redundant_files():
    """移除冗余文件"""
    removed_files = []
    
    for js_file in REDUNDANT_JS_FILES:
        file_path = STATIC_JS_DIR / js_file
        if file_path.exists():
            os.remove(file_path)
            removed_files.append(js_file)
            print(f"🗑️  已删除: {js_file}")
        else:
            print(f"⚠️  文件不存在，跳过: {js_file}")
    
    return removed_files

def check_template_references():
    """检查模板文件中是否还有对这些JS文件的引用"""
    templates_dir = PROJECT_ROOT / 'templates'
    references_found = []
    
    if not templates_dir.exists():
        print("⚠️  templates目录不存在")
        return references_found
    
    for js_file in REDUNDANT_JS_FILES:
        js_name = js_file.replace('.js', '')
        
        # 搜索模板文件中的引用
        for template_file in templates_dir.rglob('*.html'):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if js_file in content or js_name in content:
                        references_found.append({
                            'template': str(template_file.relative_to(PROJECT_ROOT)),
                            'js_file': js_file
                        })
            except Exception as e:
                print(f"⚠️  读取模板文件失败 {template_file}: {e}")
    
    return references_found

def generate_migration_report(backed_up_files, removed_files, references):
    """生成迁移报告"""
    report_path = PROJECT_ROOT / 'js_cleanup_report.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# JavaScript文件清理报告\n\n")
        f.write(f"生成时间: {os.popen('date').read().strip()}\n\n")
        
        f.write("## 已移除的冗余文件\n\n")
        for file in removed_files:
            f.write(f"- ✅ {file}\n")
        
        f.write("\n## 已备份的文件\n\n")
        for file in backed_up_files:
            f.write(f"- 💾 {file}\n")
        
        f.write("\n## 保留的文件\n\n")
        for file in KEEP_FILES:
            f.write(f"- 🔄 {file} (已优化)\n")
        
        f.write("\n## 替代方案\n\n")
        f.write("### 统一API端点 (apps/permissions/unified_ajax_api.py)\n")
        f.write("- `/api/unified/role-choices/` - 替代角色选择器AJAX调用\n")
        f.write("- `/api/unified/role-info/` - 替代角色信息获取\n")
        f.write("- `/api/unified/sync-role-groups/` - 替代角色组同步\n")
        f.write("- `/api/unified/menu-validity/` - 替代菜单有效性检查\n")
        f.write("- `/api/unified/user-sync-status/` - 替代用户同步状态\n")
        f.write("- `/api/unified/role-permission-sync/` - 替代权限同步\n")
        
        if references:
            f.write("\n## ⚠️ 需要手动更新的模板引用\n\n")
            for ref in references:
                f.write(f"- {ref['template']} 引用了 {ref['js_file']}\n")
        else:
            f.write("\n## ✅ 未发现模板文件引用\n")
        
        f.write("\n## 下一步操作\n\n")
        f.write("1. 检查应用功能是否正常\n")
        f.write("2. 如有问题，可从backup_js_files目录恢复文件\n")
        f.write("3. 更新相关文档\n")
        f.write("4. 清理备份文件（确认无问题后）\n")
    
    print(f"📋 报告已生成: {report_path}")

def main():
    """主函数"""
    print("🚀 开始清理冗余JavaScript文件...\n")
    
    # 1. 备份文件
    print("📦 备份文件...")
    backed_up_files = backup_files()
    print(f"备份完成，共备份 {len(backed_up_files)} 个文件\n")
    
    # 2. 检查模板引用
    print("🔍 检查模板文件引用...")
    references = check_template_references()
    if references:
        print(f"⚠️  发现 {len(references)} 个模板引用，需要手动更新")
        for ref in references:
            print(f"   - {ref['template']} -> {ref['js_file']}")
    else:
        print("✅ 未发现模板文件引用")
    print()
    
    # 3. 移除冗余文件
    print("🗑️  移除冗余文件...")
    removed_files = remove_redundant_files()
    print(f"移除完成，共删除 {len(removed_files)} 个文件\n")
    
    # 4. 生成报告
    print("📋 生成迁移报告...")
    generate_migration_report(backed_up_files, removed_files, references)
    
    print("\n🎉 JavaScript文件清理完成！")
    print("\n📝 重要提醒:")
    print("   1. 请测试相关功能是否正常")
    print("   2. 如有问题可从backup_js_files恢复")
    print("   3. 查看js_cleanup_report.md了解详情")

if __name__ == '__main__':
    main()