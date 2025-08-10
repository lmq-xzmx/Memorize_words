from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from apps.permissions.models import RoleManagement
from apps.accounts.models import UserRole


class Command(BaseCommand):
    help = '创建默认角色管理数据'

    def handle(self, *args, **options):
        """创建默认角色"""
        
        # 角色配置
        role_configs = [
            {
                'role': UserRole.STUDENT,
                'display_name': '学生',
                'description': '学生角色，可以参与学习活动、查看学习内容、提交作业等',
                'sort_order': 1,
                'permissions': [
                    'view_learningprofile',
                    'change_learningprofile',
                ]
            },
            {
                'role': UserRole.PARENT,
                'display_name': '家长',
                'description': '家长角色，可以查看孩子的学习进度、成绩等信息',
                'sort_order': 2,
                'permissions': [
                    'view_learningprofile',
                ]
            },
            {
                'role': UserRole.TEACHER,
                'display_name': '教师',
                'description': '教师角色，可以管理课程、布置作业、查看学生学习情况等',
                'sort_order': 3,
                'permissions': [
                    'view_learningprofile',
                    'change_learningprofile',
                    'add_learningprofile',
                ]
            },
            {
                'role': UserRole.ADMIN,
                'display_name': '管理员',
                'description': '系统管理员，拥有所有权限',
                'sort_order': 4,
                'permissions': []  # 管理员权限将在后面单独处理
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for config in role_configs:
            role_obj, created = RoleManagement.objects.get_or_create(
                role=config['role'],
                defaults={
                    'display_name': config['display_name'],
                    'description': config['description'],
                    'sort_order': config['sort_order'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建角色: {role_obj.display_name}')
                )
            else:
                # 更新现有角色信息
                role_obj.display_name = config['display_name']
                role_obj.description = config['description']
                role_obj.sort_order = config['sort_order']
                role_obj.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新角色: {role_obj.display_name}')
                )
            
            # 设置权限
            if config['permissions']:
                permissions = Permission.objects.filter(
                    codename__in=config['permissions']
                )
                role_obj.permissions.set(permissions)
                self.stdout.write(
                    f'  为 {role_obj.display_name} 设置了 {permissions.count()} 个权限'
                )
            elif config['role'] == UserRole.ADMIN:
                # 为管理员设置所有权限
                all_permissions = Permission.objects.all()
                role_obj.permissions.set(all_permissions)
                self.stdout.write(
                    f'  为 {role_obj.display_name} 设置了所有权限 ({all_permissions.count()} 个)'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n角色管理数据初始化完成！'
                f'\n创建: {created_count} 个角色'
                f'\n更新: {updated_count} 个角色'
            )
        )