#!/usr/bin/env python
"""
设置优化的角色权限分配

根据权限管理通用原则，为每个角色直接分配合适的权限，
不依赖继承关系，实现更精确的权限控制。
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.accounts.models import UserRole
from apps.permissions.models import RoleManagement, RoleGroupMapping
from apps.accounts.services.role_service import RoleService


class Command(BaseCommand):
    help = '设置优化的角色权限分配'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要执行的操作，不实际修改数据库'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('🚀 开始设置优化的角色权限分配...'))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN 模式 - 仅显示操作，不修改数据库'))
        
        try:
            with transaction.atomic():
                # 1. 清除角色继承关系
                self.clear_role_inheritance()
                
                # 2. 设置精确的角色权限
                self.setup_precise_role_permissions()
                
                # 3. 同步权限到Django组
                self.sync_permissions_to_groups()
                
                # 4. 验证权限配置
                self.verify_permissions()
                
                self.stdout.write(self.style.SUCCESS('✅ 优化的角色权限设置完成！'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 权限设置失败: {str(e)}'))
            raise
    
    def clear_role_inheritance(self):
        """清除角色继承关系"""
        self.stdout.write('\n🧹 清除角色继承关系...')
        
        if not self.dry_run:
            updated = RoleManagement.objects.filter(parent__isnull=False).update(parent=None)
            self.stdout.write(f'  已清除 {updated} 个角色的继承关系')
        else:
            count = RoleManagement.objects.filter(parent__isnull=False).count()
            self.stdout.write(f'  将清除 {count} 个角色的继承关系')
    
    def setup_precise_role_permissions(self):
        """设置精确的角色权限"""
        self.stdout.write('\n🎯 设置精确的角色权限...')
        
        # 定义每个角色的精确权限
        role_permissions = {
            UserRole.ADMIN: self.get_admin_permissions(),
            UserRole.TEACHER: self.get_teacher_permissions(),
            UserRole.PARENT: self.get_parent_permissions(),
            UserRole.STUDENT: self.get_student_permissions()
        }
        
        for role, permission_codes in role_permissions.items():
            self.setup_role_permissions(role, permission_codes)
    
    def get_admin_permissions(self):
        """获取管理员权限列表"""
        return [
            # 用户管理
            'accounts.view_customuser',
            'accounts.add_customuser',
            'accounts.change_customuser',
            'accounts.delete_customuser',
            'accounts.view_learningprofile',
            'accounts.change_learningprofile',
            
            # 权限管理
            'auth.view_group',
            'auth.add_group',
            'auth.change_group',
            'auth.delete_group',
            'auth.view_permission',
            'permissions.view_rolemanagement',
            'permissions.add_rolemanagement',
            'permissions.change_rolemanagement',
            'permissions.delete_rolemanagement',
            'permissions.view_rolegroupmapping',
            'permissions.add_rolegroupmapping',
            'permissions.change_rolegroupmapping',
            'permissions.delete_rolegroupmapping',
            'permissions.view_menumoduleconfig',
            'permissions.add_menumoduleconfig',
            'permissions.change_menumoduleconfig',
            'permissions.delete_menumoduleconfig',
            
            # 教学管理
            'teaching.view_learninggoal',
            'teaching.add_learninggoal',
            'teaching.change_learninggoal',
            'teaching.delete_learninggoal',
            'teaching.view_learningplan',
            'teaching.add_learningplan',
            'teaching.change_learningplan',
            'teaching.delete_learningplan',
            'teaching.view_teachingplan',
            'teaching.add_teachingplan',
            'teaching.change_teachingplan',
            'teaching.delete_teachingplan',
            
            # 单词管理
            'words.view_word',
            'words.add_word',
            'words.change_word',
            'words.delete_word',
            'words.view_wordbook',
            'words.add_wordbook',
            'words.change_wordbook',
            'words.delete_wordbook',
            'words.view_studysession',
            'words.add_studysession',
            'words.change_studysession',
            'words.delete_studysession',
            
            # 分析统计
            'analytics.view_learningprogress',
            'analytics.view_statistics',
            
            # 系统管理
            'admin.view_logentry',
            'sessions.view_session',
            'sessions.delete_session',
        ]
    
    def get_teacher_permissions(self):
        """获取教师权限列表"""
        return [
            # 学生管理（仅查看）
            'accounts.view_customuser',
            'accounts.view_learningprofile',
            'accounts.change_learningprofile',
            
            # 教学管理
            'teaching.view_learninggoal',
            'teaching.add_learninggoal',
            'teaching.change_learninggoal',
            'teaching.view_learningplan',
            'teaching.add_learningplan',
            'teaching.change_learningplan',
            'teaching.view_teachingplan',
            'teaching.add_teachingplan',
            'teaching.change_teachingplan',
            
            # 单词管理
            'words.view_word',
            'words.add_word',
            'words.change_word',
            'words.view_wordbook',
            'words.add_wordbook',
            'words.change_wordbook',
            'words.view_studysession',
            'words.add_studysession',
            'words.change_studysession',
            
            # 学习分析
            'analytics.view_learningprogress',
            'analytics.view_statistics',
            
            # 词汇管理
            'vocabulary_manager.view_learninggoal',
            'vocabulary_manager.add_learninggoal',
            'vocabulary_manager.change_learninggoal',
            'vocabulary_manager.view_learningplan',
            'vocabulary_manager.add_learningplan',
            'vocabulary_manager.change_learningplan',
            'vocabulary_manager.view_dailystudyrecord',
        ]
    
    def get_parent_permissions(self):
        """获取家长权限列表"""
        return [
            # 查看孩子信息
            'accounts.view_learningprofile',
            
            # 查看学习进度
            'analytics.view_learningprogress',
            
            # 查看学习记录
            'words.view_studysession',
            'vocabulary_manager.view_dailystudyrecord',
            'vocabulary_manager.view_learninggoal',
            'vocabulary_manager.view_learningplan',
            
            # 查看教学计划
            'teaching.view_learninggoal',
            'teaching.view_learningplan',
            'teaching.view_teachingplan',
            
            # 基础查看权限
            'words.view_word',
            'words.view_wordbook',
        ]
    
    def get_student_permissions(self):
        """获取学生权限列表"""
        return [
            # 个人信息
            'accounts.view_learningprofile',
            
            # 学习功能
            'words.view_word',
            'words.view_wordbook',
            'words.view_studysession',
            'words.add_studysession',
            'words.change_studysession',
            
            # 学习记录
            'vocabulary_manager.view_dailystudyrecord',
            'vocabulary_manager.add_dailystudyrecord',
            'vocabulary_manager.change_dailystudyrecord',
            'vocabulary_manager.view_learninggoal',
            'vocabulary_manager.view_learningplan',
            
            # 查看学习进度
            'analytics.view_learningprogress',
            
            # 查看教学内容
            'teaching.view_learninggoal',
            'teaching.view_learningplan',
            
            # 文章阅读
            'article_factory.view_article',
            'article_factory.view_parsedparagraph',
        ]
    
    def setup_role_permissions(self, role, permission_codes):
        """为指定角色设置权限"""
        role_display = dict(RoleService.get_role_choices(include_empty=False)).get(role, role)
        self.stdout.write(f'\n  设置 {role_display} 权限...')
        
        # 获取或创建角色管理对象
        role_mgmt, created = RoleManagement.objects.get_or_create(
            role=role,
            defaults={
                'display_name': role_display,
                'description': f'{role_display}角色权限',
                'parent': None  # 确保没有继承关系
            }
        )
        
        if not self.dry_run:
            # 清除现有权限
            role_mgmt.permissions.clear()
            
            # 添加新权限
            added_count = 0
            missing_permissions = []
            
            for perm_code in permission_codes:
                try:
                    app_label, codename = perm_code.split('.', 1)
                    permission = Permission.objects.get(
                        codename=codename,
                        content_type__app_label=app_label
                    )
                    role_mgmt.permissions.add(permission)
                    added_count += 1
                except Permission.DoesNotExist:
                    missing_permissions.append(perm_code)
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    错误: 添加权限 {perm_code} 失败: {str(e)}')
                    )
            
            self.stdout.write(f'    ✅ 已添加 {added_count} 个权限')
            
            if missing_permissions:
                self.stdout.write(
                    self.style.WARNING(f'    ⚠️  缺失权限: {len(missing_permissions)}个')
                )
                for perm in missing_permissions[:5]:  # 只显示前5个
                    self.stdout.write(f'      - {perm}')
                if len(missing_permissions) > 5:
                    self.stdout.write(f'      ... 还有{len(missing_permissions)-5}个')
        else:
            self.stdout.write(f'    将设置 {len(permission_codes)} 个权限')
    
    def sync_permissions_to_groups(self):
        """同步权限到Django组"""
        self.stdout.write('\n🔄 同步权限到Django组...')
        
        for role_mgmt in RoleManagement.objects.all():
            try:
                mapping = RoleGroupMapping.objects.get(role=role_mgmt.role)
                group = mapping.group
                
                if not self.dry_run:
                    # 清除组的现有权限
                    group.permissions.clear()
                    
                    # 添加角色的直接权限（不包括继承）
                    direct_permissions = role_mgmt.permissions.all()
                    group.permissions.set(direct_permissions)
                    
                    self.stdout.write(
                        f'  ✅ {role_mgmt.get_role_display()}: '
                        f'已同步 {direct_permissions.count()} 个权限到组 {group.name}'
                    )
                else:
                    perm_count = role_mgmt.permissions.count()
                    self.stdout.write(
                        f'  将同步 {role_mgmt.get_role_display()}: '
                        f'{perm_count} 个权限到组 {group.name}'
                    )
                    
            except RoleGroupMapping.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠️  角色 {role_mgmt.get_role_display()} 没有对应的组映射'
                    )
                )
    
    def verify_permissions(self):
        """验证权限配置"""
        self.stdout.write('\n🔍 验证权限配置...')
        
        # 期望的权限数量范围
        expected_ranges = {
            UserRole.ADMIN: (40, 60),
            UserRole.TEACHER: (25, 35),
            UserRole.PARENT: (8, 15),
            UserRole.STUDENT: (12, 20)
        }
        
        all_valid = True
        
        for role_mgmt in RoleManagement.objects.all():
            # 只计算直接权限，不包括继承
            direct_perm_count = role_mgmt.permissions.count()
            expected_min, expected_max = expected_ranges.get(role_mgmt.role, (0, 999))
            
            if expected_min <= direct_perm_count <= expected_max:
                status = '✅'
            else:
                status = '❌'
                all_valid = False
            
            self.stdout.write(
                f'  {status} {role_mgmt.get_role_display()}: '
                f'{direct_perm_count}个直接权限 (期望: {expected_min}-{expected_max}个)'
            )
        
        # 检查继承关系
        inheritance_count = RoleManagement.objects.filter(parent__isnull=False).count()
        if inheritance_count == 0:
            self.stdout.write('  ✅ 已清除所有角色继承关系')
        else:
            self.stdout.write(f'  ❌ 仍有 {inheritance_count} 个角色存在继承关系')
            all_valid = False
        
        # 检查组权限同步
        self.stdout.write('\n  Django组权限同步检查:')
        for role_mgmt in RoleManagement.objects.all():
            try:
                mapping = RoleGroupMapping.objects.get(role=role_mgmt.role)
                group = mapping.group
                role_perm_count = role_mgmt.permissions.count()
                group_perm_count = group.permissions.count()
                
                if role_perm_count == group_perm_count:
                    self.stdout.write(
                        f'    ✅ {role_mgmt.get_role_display()}: '
                        f'角色权限({role_perm_count}) = 组权限({group_perm_count})'
                    )
                else:
                    self.stdout.write(
                        f'    ❌ {role_mgmt.get_role_display()}: '
                        f'角色权限({role_perm_count}) ≠ 组权限({group_perm_count})'
                    )
                    all_valid = False
                    
            except RoleGroupMapping.DoesNotExist:
                self.stdout.write(
                    f'    ⚠️  {role_mgmt.get_role_display()}: 没有组映射'
                )
        
        if all_valid:
            self.stdout.write(self.style.SUCCESS('\n✅ 权限配置验证通过！'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  权限配置存在问题，请检查'))
        
        # 显示最终统计
        self.show_final_statistics()
    
    def show_final_statistics(self):
        """显示最终统计信息"""
        self.stdout.write('\n📊 最终权限统计:')
        
        total_permissions = Permission.objects.count()
        self.stdout.write(f'  系统总权限数: {total_permissions}')
        
        for role_mgmt in RoleManagement.objects.all().order_by('role'):
            direct_count = role_mgmt.permissions.count()
            percentage = (direct_count / total_permissions * 100) if total_permissions > 0 else 0
            
            self.stdout.write(
                f'  {role_mgmt.get_role_display()}: '
                f'{direct_count}个权限 ({percentage:.1f}%)'
            )