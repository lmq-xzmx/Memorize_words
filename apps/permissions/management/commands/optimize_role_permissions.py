#!/usr/bin/env python
"""
角色权限优化管理命令

根据权限管理通用原则，重新设计和分配各角色的权限，
实现更合理的权限分层和继承关系。
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.accounts.models import UserRole
from apps.permissions.models import RoleManagement, RoleGroupMapping
from apps.permissions.utils import PermissionUtils


class Command(BaseCommand):
    help = '优化角色权限分配，实现合理的权限分层'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要执行的操作，不实际修改数据库'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有角色权限后重新分配'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.reset = options['reset']
        
        self.stdout.write(self.style.SUCCESS('🚀 开始优化角色权限分配...'))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN 模式 - 仅显示操作，不修改数据库'))
        
        try:
            with transaction.atomic():
                # 1. 权限分析
                self.analyze_current_permissions()
                
                # 2. 权限分类
                permission_categories = self.categorize_permissions()
                
                # 3. 角色权限重新设计
                role_permissions = self.design_role_permissions(permission_categories)
                
                # 4. 应用权限配置
                if not self.dry_run:
                    self.apply_permission_configuration(role_permissions)
                else:
                    self.preview_permission_configuration(role_permissions)
                
                # 5. 验证权限配置
                self.verify_permission_configuration()
                
                self.stdout.write(self.style.SUCCESS('✅ 角色权限优化完成！'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 权限优化失败: {str(e)}'))
            raise
    
    def analyze_current_permissions(self):
        """分析当前权限状态"""
        self.stdout.write('\n📊 当前权限状态分析:')
        
        total_permissions = Permission.objects.count()
        self.stdout.write(f'  总权限数量: {total_permissions}')
        
        # 按应用分组统计
        apps_stats = {}
        for perm in Permission.objects.select_related('content_type'):
            app_label = perm.content_type.app_label
            if app_label not in apps_stats:
                apps_stats[app_label] = 0
            apps_stats[app_label] += 1
        
        self.stdout.write('  按应用分组:')
        for app, count in sorted(apps_stats.items()):
            self.stdout.write(f'    {app}: {count}个权限')
        
        # 角色权限统计
        self.stdout.write('\n  当前角色权限:')
        for role in RoleManagement.objects.all():
            perm_count = len(role.get_all_permissions())
            self.stdout.write(f'    {role.get_role_display()}: {perm_count}个权限')
    
    def categorize_permissions(self):
        """权限分类"""
        self.stdout.write('\n🏷️  权限分类中...')
        
        categories = {
            'core_admin': [],      # 核心管理权限
            'user_management': [], # 用户管理权限
            'course_management': [], # 课程管理权限
            'teaching': [],        # 教学相关权限
            'learning': [],        # 学习相关权限
            'analytics': [],       # 分析统计权限
            'basic': [],          # 基础权限
            'system': []          # 系统权限
        }
        
        for perm in Permission.objects.select_related('content_type'):
            app_label = perm.content_type.app_label
            codename = perm.codename
            perm_code = f'{app_label}.{codename}'
            
            # 根据应用和权限名称分类
            if app_label in ['admin', 'auth', 'sessions', 'contenttypes']:
                categories['system'].append(perm_code)
            elif app_label == 'accounts':
                if any(x in codename for x in ['add_', 'delete_', 'change_']):
                    categories['user_management'].append(perm_code)
                else:
                    categories['basic'].append(perm_code)
            elif app_label == 'courses':
                categories['course_management'].append(perm_code)
            elif app_label == 'teaching':
                categories['teaching'].append(perm_code)
            elif app_label == 'analytics':
                categories['analytics'].append(perm_code)
            elif app_label == 'permissions':
                categories['core_admin'].append(perm_code)
            elif 'view_' in codename:
                categories['basic'].append(perm_code)
            else:
                categories['learning'].append(perm_code)
        
        # 显示分类结果
        for category, perms in categories.items():
            self.stdout.write(f'  {category}: {len(perms)}个权限')
        
        return categories
    
    def design_role_permissions(self, categories):
        """设计角色权限分配"""
        self.stdout.write('\n🎨 设计角色权限分配...')
        
        role_permissions = {
            UserRole.ADMIN: {
                'name': '管理员',
                'permissions': (
                    categories['core_admin'] +
                    categories['user_management'] +
                    categories['course_management'] +
                    categories['teaching'] +
                    categories['analytics'] +
                    categories['system'] +
                    categories['basic']
                ),
                'description': '拥有系统全部管理权限'
            },
            UserRole.TEACHER: {
                'name': '教师',
                'permissions': (
                    categories['course_management'] +
                    categories['teaching'] +
                    categories['analytics'] +
                    categories['basic'] +
                    # 部分用户管理权限（仅查看）
                    [p for p in categories['user_management'] if 'view_' in p]
                ),
                'description': '拥有教学和课程管理权限'
            },
            UserRole.PARENT: {
                'name': '家长',
                'permissions': (
                    # 仅查看权限
                    [p for p in categories['analytics'] if 'view_' in p] +
                    [p for p in categories['basic'] if 'view_' in p] +
                    # 特定的家长权限
                    ['accounts.view_learningprofile', 'analytics.view_child_progress']
                ),
                'description': '拥有查看孩子学习情况的权限'
            },
            UserRole.STUDENT: {
                'name': '学生',
                'permissions': (
                    # 基础学习权限
                    [p for p in categories['learning'] if any(x in p for x in ['view_', 'add_studysession', 'change_studysession'])] +
                    # 基础查看权限
                    [p for p in categories['basic'] if 'view_' in p and 'customuser' not in p]
                ),
                'description': '拥有基础学习权限'
            }
        }
        
        # 显示设计结果
        for role, config in role_permissions.items():
            perm_count = len(config['permissions'])
            self.stdout.write(f'  {config["name"]}: {perm_count}个权限 - {config["description"]}')
        
        return role_permissions
    
    def apply_permission_configuration(self, role_permissions):
        """应用权限配置"""
        self.stdout.write('\n⚙️  应用权限配置...')
        
        for role, config in role_permissions.items():
            self.stdout.write(f'  配置 {config["name"]} 角色权限...')
            
            # 获取或创建角色管理对象
            role_mgmt, created = RoleManagement.objects.get_or_create(
                role=role,
                defaults={'name': config['name']}
            )
            
            if self.reset:
                # 清除现有权限
                role_mgmt.permissions.clear()
                self.stdout.write(f'    已清除 {config["name"]} 的现有权限')
            
            # 添加新权限
            added_count = 0
            for perm_code in config['permissions']:
                try:
                    app_label, codename = perm_code.split('.', 1)
                    permission = Permission.objects.get(
                        codename=codename,
                        content_type__app_label=app_label
                    )
                    role_mgmt.permissions.add(permission)
                    added_count += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'    警告: 权限 {perm_code} 不存在')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    错误: 添加权限 {perm_code} 失败: {str(e)}')
                    )
            
            self.stdout.write(f'    已添加 {added_count} 个权限')
            
            # 同步到Django组
            self.sync_role_to_group(role_mgmt)
    
    def preview_permission_configuration(self, role_permissions):
        """预览权限配置"""
        self.stdout.write('\n👀 权限配置预览:')
        
        for role, config in role_permissions.items():
            self.stdout.write(f'\n  {config["name"]} ({len(config["permissions"])}个权限):')
            
            # 按类别显示权限
            perm_by_app = {}
            for perm_code in config['permissions']:
                app_label = perm_code.split('.')[0]
                if app_label not in perm_by_app:
                    perm_by_app[app_label] = []
                perm_by_app[app_label].append(perm_code)
            
            for app, perms in sorted(perm_by_app.items()):
                self.stdout.write(f'    {app}: {len(perms)}个权限')
                if len(perms) <= 5:
                    for perm in perms:
                        self.stdout.write(f'      - {perm}')
                else:
                    for perm in perms[:3]:
                        self.stdout.write(f'      - {perm}')
                    self.stdout.write(f'      ... 还有{len(perms)-3}个权限')
    
    def sync_role_to_group(self, role_mgmt):
        """同步角色权限到Django组"""
        try:
            # 获取角色组映射
            mapping = RoleGroupMapping.objects.get(role=role_mgmt.role)
            group = mapping.group
            
            # 清除组的现有权限
            group.permissions.clear()
            
            # 添加角色的所有权限到组
            all_permissions = role_mgmt.get_all_permissions()
            group.permissions.set(all_permissions)
            
            self.stdout.write(f'    已同步 {len(all_permissions)} 个权限到组 {group.name}')
            
        except RoleGroupMapping.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f'    警告: 角色 {role_mgmt.get_role_display()} 没有对应的组映射')
            )
    
    def verify_permission_configuration(self):
        """验证权限配置"""
        self.stdout.write('\n🔍 验证权限配置...')
        
        # 检查角色权限数量
        expected_ranges = {
            UserRole.ADMIN: (180, 220),
            UserRole.TEACHER: (80, 120),
            UserRole.PARENT: (20, 40),
            UserRole.STUDENT: (15, 30)
        }
        
        all_valid = True
        for role in RoleManagement.objects.all():
            perm_count = len(role.get_all_permissions())
            expected_min, expected_max = expected_ranges.get(role.role, (0, 999))
            
            if expected_min <= perm_count <= expected_max:
                status = '✅'
            else:
                status = '❌'
                all_valid = False
            
            self.stdout.write(
                f'  {status} {role.get_role_display()}: {perm_count}个权限 '
                f'(期望: {expected_min}-{expected_max}个)'
            )
        
        # 检查权限继承关系
        self.stdout.write('\n  权限继承关系检查:')
        admin_perms = set()
        teacher_perms = set()
        parent_perms = set()
        student_perms = set()
        
        for role in RoleManagement.objects.all():
            perms = set(p.codename for p in role.get_all_permissions())
            if role.role == UserRole.ADMIN:
                admin_perms = perms
            elif role.role == UserRole.TEACHER:
                teacher_perms = perms
            elif role.role == UserRole.PARENT:
                parent_perms = perms
            elif role.role == UserRole.STUDENT:
                student_perms = perms
        
        # 验证权限包含关系（应该是部分包含，而不是完全包含）
        if student_perms.issubset(parent_perms):
            self.stdout.write('  ❌ 学生权限完全包含在家长权限中（不合理）')
            all_valid = False
        else:
            self.stdout.write('  ✅ 学生和家长权限有适当的差异化')
        
        if teacher_perms.issuperset(parent_perms):
            self.stdout.write('  ✅ 教师权限包含家长权限')
        else:
            self.stdout.write('  ⚠️  教师权限不完全包含家长权限')
        
        if admin_perms.issuperset(teacher_perms):
            self.stdout.write('  ✅ 管理员权限包含教师权限')
        else:
            self.stdout.write('  ❌ 管理员权限不包含教师权限（不合理）')
            all_valid = False
        
        if all_valid:
            self.stdout.write(self.style.SUCCESS('\n✅ 权限配置验证通过！'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  权限配置存在问题，请检查'))
    
    def get_permission_summary(self):
        """获取权限摘要"""
        summary = {}
        for role in RoleManagement.objects.all():
            permissions = role.get_all_permissions()
            summary[role.get_role_display()] = {
                'total': len(permissions),
                'by_app': {}
            }
            
            for perm in permissions:
                app_label = perm.content_type.app_label
                if app_label not in summary[role.get_role_display()]['by_app']:
                    summary[role.get_role_display()]['by_app'][app_label] = 0
                summary[role.get_role_display()]['by_app'][app_label] += 1
        
        return summary