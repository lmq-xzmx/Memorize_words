#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色选择器迁移脚本

本脚本用于将项目中所有使用 RoleService.get_role_choices(include_empty=False) 的地方迁移到统一的 RoleService。
使用方法：
    python migrate_role_choices_to_service.py
"""

import os
import re
import sys
from pathlib import Path


class RoleChoicesMigrator:
    """角色选择器迁移工具"""
    
    def __init__(self, project_root=None):
        self.project_root = project_root or Path.cwd()
        self.migrated_files = []
        self.skipped_files = []
        self.error_files = []
        
        # 迁移模式配置
        self.migration_patterns = [
            # 基本替换模式
            {
                'pattern': r'UserRole\.choices',
                'replacement': 'RoleService.get_role_choices(include_empty=False)',
                'description': '基本RoleService.get_role_choices(include_empty=False)替换'
            },
            # 带参数的choices
            {
                'pattern': r'choices\s*=\s*UserRole\.choices',
                'replacement': 'choices=RoleService.get_role_choices(include_empty=False)',
                'description': '表单字段choices参数'
            },
            # dict转换
            {
                'pattern': r'dict\(UserRole\.choices\)',
                'replacement': 'dict(RoleService.get_role_choices(include_empty=False))',
                'description': 'dict(RoleService.get_role_choices(include_empty=False))转换'
            },
            # 列表推导式中的使用
            {
                'pattern': r'\[choice\[0\]\s+for\s+choice\s+in\s+UserRole\.choices\]',
                'replacement': '[choice[0] for choice in RoleService.get_role_choices(include_empty=False)]',
                'description': '列表推导式中的角色代码提取'
            },
            # 循环中的使用
            {
                'pattern': r'for\s+(\w+)\s+in\s+UserRole\.choices:',
                'replacement': r'for \1 in RoleService.get_role_choices(include_empty=False):',
                'description': '循环中的RoleService.get_role_choices(include_empty=False)'
            },
            # 序列化器中的使用
            {
                'pattern': r'serializers\.ChoiceField\(choices=UserRole\.choices\)',
                'replacement': 'DynamicRoleChoiceField()',
                'description': '序列化器中的角色字段'
            }
        ]
        
        # 需要特殊处理的文件
        self.special_files = {
            'apps/permissions/serializers.py': self._migrate_serializers,
            'apps/accounts/forms.py': self._migrate_forms,
        }
        
        # 排除的文件模式
        self.exclude_patterns = [
            r'.*/__pycache__/.*',
            r'.*\.pyc$',
            r'.*migrations/.*',
            r'.*\.md$',  # 文档文件
            r'.*test.*\.py$',  # 测试文件（可选）
        ]
    
    def should_exclude_file(self, file_path):
        """检查文件是否应该被排除"""
        file_str = str(file_path)
        for pattern in self.exclude_patterns:
            if re.match(pattern, file_str):
                return True
        return False
    
    def find_python_files(self):
        """查找所有需要处理的Python文件"""
        python_files = []
        
        # 主要目录
        search_dirs = ['apps', 'static', 'templates']
        
        for search_dir in search_dirs:
            search_path = self.project_root / search_dir
            if search_path.exists():
                for file_path in search_path.rglob('*.py'):
                    if not self.should_exclude_file(file_path):
                        python_files.append(file_path)
        
        # 根目录的Python文件
        for file_path in self.project_root.glob('*.py'):
            if not self.should_exclude_file(file_path):
                python_files.append(file_path)
        
        return python_files
    
    def check_file_needs_migration(self, file_path):
        """检查文件是否需要迁移"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'RoleService.get_role_choices(include_empty=False)' in content
        except Exception as e:
            print(f"⚠️ 无法读取文件 {file_path}: {e}")
            return False
    
    def add_import_if_needed(self, content):
        """如果需要，添加RoleService导入"""
        if 'RoleService' in content and 'from apps.accounts.services.role_service import RoleService' not in content:
            # 查找合适的导入位置
            lines = content.split('\n')
            import_insert_line = 0
            
            # 找到最后一个import语句的位置
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#'):
                    import_insert_line = i + 1
            
            # 插入导入语句
            lines.insert(import_insert_line, 'from apps.accounts.services.role_service import RoleService')
            content = '\n'.join(lines)
        
        return content
    
    def migrate_file_content(self, content, file_path):
        """迁移文件内容"""
        original_content = content
        modified = False
        applied_patterns = []
        
        # 应用迁移模式
        for pattern_config in self.migration_patterns:
            pattern = pattern_config['pattern']
            replacement = pattern_config['replacement']
            description = pattern_config['description']
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                applied_patterns.append(description)
        
        # 添加必要的导入
        if modified:
            content = self.add_import_if_needed(content)
        
        return content, modified, applied_patterns
    
    def _migrate_serializers(self, file_path):
        """特殊处理序列化器文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加动态角色字段类
        dynamic_field_class = '''
class DynamicRoleChoiceField(serializers.ChoiceField):
    """动态角色选择字段"""
    def __init__(self, **kwargs):
        kwargs['choices'] = RoleService.get_role_choices(include_empty=False)
        super().__init__(**kwargs)
'''
        
        # 检查是否已经存在
        if 'DynamicRoleChoiceField' not in content:
            # 在导入语句后添加
            import_end = 0
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    import_end = i + 1
            
            lines.insert(import_end, dynamic_field_class)
            content = '\n'.join(lines)
        
        # 应用标准迁移
        content, modified, patterns = self.migrate_file_content(content, file_path)
        
        return content, modified, patterns
    
    def _migrate_forms(self, file_path):
        """特殊处理表单文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换表单字段定义
        form_field_pattern = r'(\w+)\s*=\s*forms\.ChoiceField\(\s*choices\s*=\s*UserRole\.choices[^)]*\)'
        
        def replace_form_field(match):
            field_name = match.group(1)
            return f'{field_name} = StandardRoleChoiceField(widget=StandardRoleSelectWidget())'
        
        if re.search(form_field_pattern, content):
            content = re.sub(form_field_pattern, replace_form_field, content)
            # 添加widget导入
            if 'StandardRoleChoiceField' not in content:
                content = 'from apps.permissions.widgets import StandardRoleChoiceField, StandardRoleSelectWidget\n' + content
        
        # 应用标准迁移
        content, modified, patterns = self.migrate_file_content(content, file_path)
        
        return content, modified, patterns
    
    def migrate_file(self, file_path):
        """迁移单个文件"""
        try:
            # 检查是否需要特殊处理
            relative_path = str(file_path.relative_to(self.project_root))
            
            if relative_path in self.special_files:
                content, modified, patterns = self.special_files[relative_path](file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content, modified, patterns = self.migrate_file_content(content, file_path)
            
            if modified:
                # 备份原文件
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    with open(file_path, 'r', encoding='utf-8') as original:
                        f.write(original.read())
                
                # 写入迁移后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.migrated_files.append({
                    'path': relative_path,
                    'patterns': patterns,
                    'backup': str(backup_path.relative_to(self.project_root))
                })
                
                print(f"✅ 已迁移: {relative_path}")
                for pattern in patterns:
                    print(f"   - {pattern}")
            else:
                self.skipped_files.append(relative_path)
        
        except Exception as e:
            self.error_files.append({'path': str(file_path), 'error': str(e)})
            print(f"❌ 迁移失败: {file_path} - {e}")
    
    def migrate_project(self):
        """迁移整个项目"""
        print("🚀 开始角色选择器迁移...")
        print(f"📁 项目根目录: {self.project_root}")
        
        # 查找需要迁移的文件
        python_files = self.find_python_files()
        files_to_migrate = [f for f in python_files if self.check_file_needs_migration(f)]
        
        print(f"📋 发现 {len(files_to_migrate)} 个文件需要迁移")
        
        if not files_to_migrate:
            print("✅ 没有文件需要迁移！")
            return
        
        # 确认迁移
        print("\n需要迁移的文件:")
        for file_path in files_to_migrate:
            print(f"  - {file_path.relative_to(self.project_root)}")
        
        response = input("\n是否继续迁移？(y/N): ")
        if response.lower() != 'y':
            print("❌ 迁移已取消")
            return
        
        # 执行迁移
        print("\n🔄 开始迁移...")
        for file_path in files_to_migrate:
            self.migrate_file(file_path)
        
        # 输出结果
        self.print_migration_summary()
    
    def print_migration_summary(self):
        """打印迁移摘要"""
        print("\n" + "="*60)
        print("📊 迁移摘要")
        print("="*60)
        
        print(f"✅ 成功迁移: {len(self.migrated_files)} 个文件")
        print(f"⏭️ 跳过文件: {len(self.skipped_files)} 个文件")
        print(f"❌ 失败文件: {len(self.error_files)} 个文件")
        
        if self.migrated_files:
            print("\n📝 迁移详情:")
            for file_info in self.migrated_files:
                print(f"  ✅ {file_info['path']}")
                print(f"     备份: {file_info['backup']}")
        
        if self.error_files:
            print("\n❌ 失败文件:")
            for error_info in self.error_files:
                print(f"  ❌ {error_info['path']}: {error_info['error']}")
        
        print("\n🔧 后续步骤:")
        print("1. 运行测试确保迁移正确")
        print("2. 检查应用功能是否正常")
        print("3. 如有问题，可使用备份文件恢复")
        print("4. 运行 python manage.py test_role_selector_consistency 验证一致性")
    
    def rollback_migration(self):
        """回滚迁移"""
        print("🔄 开始回滚迁移...")
        
        rollback_count = 0
        for file_info in self.migrated_files:
            file_path = self.project_root / file_info['path']
            backup_path = self.project_root / file_info['backup']
            
            if backup_path.exists():
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(backup_content)
                    
                    backup_path.unlink()  # 删除备份文件
                    rollback_count += 1
                    print(f"✅ 已回滚: {file_info['path']}")
                
                except Exception as e:
                    print(f"❌ 回滚失败: {file_info['path']} - {e}")
            else:
                print(f"⚠️ 备份文件不存在: {file_info['backup']}")
        
        print(f"\n🎉 回滚完成！共回滚 {rollback_count} 个文件")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        # 回滚模式（需要实现状态保存）
        print("❌ 回滚功能需要先执行迁移")
        return
    
    # 创建迁移器
    migrator = RoleChoicesMigrator()
    
    # 执行迁移
    migrator.migrate_project()


if __name__ == '__main__':
    main()