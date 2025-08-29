from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.permissions.models import RoleManagement, RoleGroupMapping, MenuModuleConfig
from apps.accounts.models import UserRole


class Command(BaseCommand):
    help = '为角色配置自动权限分配'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            help='指定角色进行权限配置（可选）',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有角色权限配置',
        )

    def handle(self, *args, **options):
        role = options.get('role')
        reset = options.get('reset')
        
        if reset:
            self.stdout.write('重置所有角色权限配置...')
            self.reset_all_permissions()
        
        if role:
            self.stdout.write(f'配置角色 {role} 的权限...')
            self.setup_role_permissions(role)
        else:
            self.stdout.write('配置所有角色的权限...')
            self.setup_all_role_permissions()
        
        self.stdout.write(self.style.SUCCESS('角色权限配置完成！'))

    def reset_all_permissions(self):
        """重置所有角色权限"""
        with transaction.atomic():
            # RoleMenuPermission 已被废弃，跳过清除菜单权限
            # 清除所有角色管理权限
            for role_mgmt in RoleManagement.objects.all():
                role_mgmt.permissions.clear()
            self.stdout.write('已清除所有角色权限配置')

    def setup_all_role_permissions(self):
        """为所有角色配置权限"""
        for role_choice in UserRole.choices:
            role_code = role_choice[0]
            self.setup_role_permissions(role_code)

    def setup_role_permissions(self, role_code):
        """为指定角色配置权限"""
        try:
            with transaction.atomic():
                # 1. 确保角色管理记录存在
                role_mgmt = self.ensure_role_management(role_code)
                
                # 2. 确保角色组映射存在
                group = self.ensure_role_group_mapping(role_code)
                
                # 3. 配置基础权限
                self.setup_basic_permissions(role_mgmt, group, role_code)
                
                # 4. 配置菜单权限
                self.setup_menu_permissions(role_code)
                
                self.stdout.write(f'✓ 角色 {role_code} 权限配置完成')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'配置角色 {role_code} 权限时出错: {str(e)}')
            )

    def ensure_role_management(self, role_code):
        """确保角色管理记录存在"""
        role_display = dict(UserRole.choices).get(role_code, role_code)
        
        role_mgmt, created = RoleManagement.objects.get_or_create(
            role=role_code,
            defaults={
                'display_name': role_display,
                'description': f'{role_display}角色',
                'is_active': True,
                'sort_order': self.get_role_sort_order(role_code)
            }
        )
        
        if created:
            self.stdout.write(f'  创建角色管理记录: {role_code}')
        
        return role_mgmt

    def ensure_role_group_mapping(self, role_code):
        """确保角色组映射存在"""
        role_display = dict(UserRole.choices).get(role_code, role_code)
        
        # 创建或获取Django组
        group, group_created = Group.objects.get_or_create(
            name=f'{role_display}组'
        )
        
        if group_created:
            self.stdout.write(f'  创建Django组: {group.name}')
        
        # 创建或获取角色组映射
        mapping, mapping_created = RoleGroupMapping.objects.get_or_create(
            role=role_code,
            defaults={
                'group': group,
                'auto_sync': True
            }
        )
        
        if mapping_created:
            self.stdout.write(f'  创建角色组映射: {role_code} -> {group.name}')
        
        return group

    def setup_basic_permissions(self, role_mgmt, group, role_code):
        """配置基础权限"""
        permissions = self.get_role_permissions(role_code)
        
        # 为角色管理添加权限
        role_mgmt.permissions.set(permissions)
        
        # 为Django组添加权限
        group.permissions.set(permissions)
        
        self.stdout.write(f'  配置基础权限: {len(permissions)} 个权限')

    def setup_menu_permissions(self, role_code):
        """配置菜单权限"""
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        # 请使用 MenuValidity 和 RoleMenuAssignment 替代
        self.stdout.write(f'  跳过菜单权限配置（RoleMenuPermission 已废弃）')

    def get_role_sort_order(self, role_code):
        """获取角色排序"""
        sort_orders = {
            UserRole.ADMIN: 10,
            UserRole.DEAN: 20,
            UserRole.ACADEMIC_DIRECTOR: 30,
            UserRole.RESEARCH_LEADER: 40,
            UserRole.TEACHER: 50,
            UserRole.PARENT: 60,
            UserRole.STUDENT: 70,
        }
        return sort_orders.get(role_code, 999)

    def get_role_permissions(self, role_code):
        """获取角色对应的权限列表"""
        # 基础权限映射
        permission_mappings = {
            UserRole.ADMIN: [
                'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
                'auth.add_group', 'auth.change_group', 'auth.delete_group', 'auth.view_group',
                'accounts.add_customuser', 'accounts.change_customuser', 'accounts.delete_customuser', 'accounts.view_customuser',
                'permissions.add_rolemanagement', 'permissions.change_rolemanagement', 'permissions.delete_rolemanagement', 'permissions.view_rolemanagement',
            ],
            UserRole.DEAN: [
                'accounts.view_customuser', 'accounts.change_customuser',
                'permissions.view_rolemanagement',
            ],
            UserRole.ACADEMIC_DIRECTOR: [
                'accounts.view_customuser', 'accounts.change_customuser',
                'permissions.view_rolemanagement',
            ],
            UserRole.RESEARCH_LEADER: [
                'accounts.view_customuser',
                'permissions.view_rolemanagement',
            ],
            UserRole.TEACHER: [
                'accounts.view_customuser',
            ],
            UserRole.PARENT: [
                'accounts.view_customuser',
            ],
            UserRole.STUDENT: [
                'accounts.view_customuser',
            ],
        }
        
        permission_codenames = permission_mappings.get(role_code, [])
        permissions = []
        
        for codename in permission_codenames:
            try:
                app_label, perm_codename = codename.split('.', 1)
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type__app_label=app_label
                )
                permissions.append(permission)
            except (Permission.DoesNotExist, ValueError):
                self.stdout.write(
                    self.style.WARNING(f'  权限不存在: {codename}')
                )
        
        return permissions

    def get_role_menu_configs(self, role_code):
        """获取角色对应的菜单配置"""
        # 菜单权限映射
        menu_mappings = {
            UserRole.ADMIN: {
                'dashboard': True,
                'user_management': True,
                'role_management': True,
                'permission_management': True,
                'system_settings': True,
                'reports': True,
                'logs': True,
            },
            UserRole.DEAN: {
                'dashboard': True,
                'user_management': True,
                'role_management': True,
                'reports': True,
                'academic_management': True,
            },
            UserRole.ACADEMIC_DIRECTOR: {
                'dashboard': True,
                'user_management': True,
                'academic_management': True,
                'curriculum_management': True,
                'reports': True,
            },
            UserRole.RESEARCH_LEADER: {
                'dashboard': True,
                'research_management': True,
                'curriculum_management': True,
                'reports': True,
            },
            UserRole.TEACHER: {
                'dashboard': True,
                'teaching_management': True,
                'student_management': True,
                'course_management': True,
            },
            UserRole.PARENT: {
                'dashboard': True,
                'student_progress': True,
                'communication': True,
                'profile_management': True,
            },
            UserRole.STUDENT: {
                'dashboard': True,
                'learning_center': True,
                'progress_tracking': True,
                'profile_management': True,
            },
        }
        
        return menu_mappings.get(role_code, {})