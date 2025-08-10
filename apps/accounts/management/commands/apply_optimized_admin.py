from django.core.management.base import BaseCommand
from django.contrib import admin
from django.apps import apps
from apps.accounts.models import CustomUser
from apps.accounts.optimized_admin import (
    OptimizedCustomUserAdmin,
    OptimizedAdminUserAdmin,
    OptimizedTeacherUserAdmin,
    OptimizedStudentUserAdmin,
    OptimizedParentUserAdmin
)
import sys


class Command(BaseCommand):
    help = '应用优化后的用户管理Admin配置，移除冗余的组和权限设置'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，不实际应用更改'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制应用，即使存在冲突'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('开始应用优化后的用户管理Admin配置...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN 模式 - 仅预览更改 ==='))
        
        # 检查当前Admin注册状态
        self.check_current_admin_registration()
        
        if not dry_run:
            # 应用优化配置
            self.apply_optimized_admin_config(force)
        else:
            self.preview_optimized_config()
        
        self.stdout.write(self.style.SUCCESS('优化配置应用完成！'))
    
    def check_current_admin_registration(self):
        """检查当前Admin注册状态"""
        self.stdout.write('\n检查当前Admin注册状态:')
        
        # 检查CustomUser是否已注册
        if CustomUser in admin.site._registry:
            current_admin = admin.site._registry[CustomUser]
            self.stdout.write(f'  - CustomUser已注册: {current_admin.__class__.__name__}')
            
            # 检查当前配置的字段
            if hasattr(current_admin, 'fieldsets') and current_admin.fieldsets:
                self.stdout.write('  - 当前fieldsets配置:')
                for name, options in current_admin.fieldsets:
                    fields = options.get('fields', [])
                    if 'groups' in str(fields) or 'user_permissions' in str(fields):
                        self.stdout.write(f'    * {name}: 包含冗余权限字段')
                    else:
                        self.stdout.write(f'    * {name}: 正常')
        else:
            self.stdout.write('  - CustomUser未注册到Admin')
    
    def preview_optimized_config(self):
        """预览优化配置"""
        self.stdout.write('\n=== 优化配置预览 ===')
        
        # 显示将要应用的配置
        configs = {
            'OptimizedCustomUserAdmin': OptimizedCustomUserAdmin,
            'OptimizedAdminUserAdmin': OptimizedAdminUserAdmin,
            'OptimizedTeacherUserAdmin': OptimizedTeacherUserAdmin,
            'OptimizedStudentUserAdmin': OptimizedStudentUserAdmin,
            'OptimizedParentUserAdmin': OptimizedParentUserAdmin,
        }
        
        for name, admin_class in configs.items():
            self.stdout.write(f'\n{name}:')
            
            # 显示字段配置
            if hasattr(admin_class, 'fieldsets'):
                self.stdout.write('  字段配置:')
                for fieldset_name, options in admin_class.fieldsets:
                    fields = options.get('fields', [])
                    self.stdout.write(f'    - {fieldset_name}: {fields}')
            
            # 显示列表显示字段
            if hasattr(admin_class, 'list_display'):
                self.stdout.write(f'  列表显示: {admin_class.list_display}')
            
            # 显示过滤字段
            if hasattr(admin_class, 'list_filter'):
                self.stdout.write(f'  过滤字段: {admin_class.list_filter}')
        
        self.stdout.write('\n优化特点:')
        self.stdout.write('  ✓ 移除了groups和user_permissions字段')
        self.stdout.write('  ✓ 添加了角色权限信息显示')
        self.stdout.write('  ✓ 提供权限详情查看功能')
        self.stdout.write('  ✓ 自动同步角色到Django组')
    
    def apply_optimized_admin_config(self, force=False):
        """应用优化的Admin配置"""
        self.stdout.write('\n应用优化配置:')
        
        try:
            # 如果CustomUser已经注册，先注销
            if CustomUser in admin.site._registry:
                if not force:
                    confirm = input('CustomUser已注册到Admin，是否替换？(y/N): ')
                    if confirm.lower() != 'y':
                        self.stdout.write(self.style.WARNING('操作已取消'))
                        return
                
                admin.site.unregister(CustomUser)
                self.stdout.write('  - 已注销原有CustomUser Admin配置')
            
            # 注册优化后的Admin配置
            admin.site.register(CustomUser, OptimizedCustomUserAdmin)
            self.stdout.write('  - 已注册OptimizedCustomUserAdmin')
            
            # 验证配置
            self.verify_optimized_config()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'应用配置时出错: {e}')
            )
            sys.exit(1)
    
    def verify_optimized_config(self):
        """验证优化配置"""
        self.stdout.write('\n验证优化配置:')
        
        if CustomUser in admin.site._registry:
            admin_class = admin.site._registry[CustomUser]
            
            # 检查是否为优化版本
            if admin_class.__class__.__name__ == 'OptimizedCustomUserAdmin':
                self.stdout.write('  ✓ 已应用OptimizedCustomUserAdmin')
            else:
                self.stdout.write('  ✗ 未正确应用优化配置')
                return False
            
            # 检查字段配置
            has_groups = False
            has_user_permissions = False
            
            if hasattr(admin_class, 'fieldsets') and admin_class.fieldsets:
                for name, options in admin_class.fieldsets:
                    fields = options.get('fields', [])
                    if 'groups' in str(fields):
                        has_groups = True
                    if 'user_permissions' in str(fields):
                        has_user_permissions = True
            
            if not has_groups and not has_user_permissions:
                self.stdout.write('  ✓ 已移除冗余的groups和user_permissions字段')
            else:
                self.stdout.write('  ✗ 仍存在冗余字段')
                if has_groups:
                    self.stdout.write('    - 发现groups字段')
                if has_user_permissions:
                    self.stdout.write('    - 发现user_permissions字段')
            
            # 检查新增功能
            if hasattr(admin_class, 'get_role_permissions_info'):
                self.stdout.write('  ✓ 已添加角色权限信息功能')
            else:
                self.stdout.write('  ✗ 缺少角色权限信息功能')
            
            if hasattr(admin_class, 'get_urls'):
                self.stdout.write('  ✓ 已添加自定义URL功能')
            else:
                self.stdout.write('  ✗ 缺少自定义URL功能')
            
            return True
        else:
            self.stdout.write('  ✗ CustomUser未注册到Admin')
            return False