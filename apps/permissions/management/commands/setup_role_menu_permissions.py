from django.core.management.base import BaseCommand
from django.db import transaction
from apps.permissions.models import RoleMenuPermission, MenuModuleConfig
from apps.accounts.models import UserRole


class Command(BaseCommand):
    help = '配置角色菜单权限映射'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有角色菜单权限',
        )
        parser.add_argument(
            '--role',
            type=str,
            help='指定角色进行配置',
        )

    def handle(self, *args, **options):
        reset = options.get('reset')
        specific_role = options.get('role')
        
        if reset:
            self.stdout.write('重置所有角色菜单权限...')
            RoleMenuPermission.objects.all().delete()
        
        if specific_role:
            self.stdout.write(f'配置角色 {specific_role} 的菜单权限...')
            self.setup_role_menu_permissions(specific_role)
        else:
            self.stdout.write('配置所有角色的菜单权限...')
            self.setup_all_role_menu_permissions()
        
        self.stdout.write(self.style.SUCCESS('角色菜单权限配置完成！'))

    def setup_all_role_menu_permissions(self):
        """配置所有角色的菜单权限"""
        roles = [
            UserRole.STUDENT.value,
            UserRole.PARENT.value,
            UserRole.TEACHER.value,
            UserRole.ADMIN.value,
            UserRole.DEAN.value,
            UserRole.ACADEMIC_DIRECTOR.value,
            UserRole.RESEARCH_LEADER.value,
        ]
        
        for role in roles:
            self.setup_role_menu_permissions(role)

    def setup_role_menu_permissions(self, role):
        """为指定角色配置菜单权限"""
        with transaction.atomic():
            # 定义角色菜单权限映射
            role_menu_mapping = self.get_role_menu_mapping()
            
            if role not in role_menu_mapping:
                self.stdout.write(f'  警告: 角色 {role} 未定义菜单权限')
                return
            
            menu_keys = role_menu_mapping[role]
            created_count = 0
            updated_count = 0
            
            for menu_key in menu_keys:
                try:
                    menu_module = MenuModuleConfig.objects.get(key=menu_key)
                    
                    permission, created = RoleMenuPermission.objects.get_or_create(
                        role=role,
                        menu_module=menu_module,
                        defaults={
                            'can_access': True
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # 更新现有权限
                        permission.can_access = True
                        permission.save()
                        updated_count += 1
                        
                except MenuModuleConfig.DoesNotExist:
                    self.stdout.write(f'  警告: 菜单模块 {menu_key} 不存在')
                    continue
            
            self.stdout.write(f'  角色 {role}: 创建 {created_count} 个，更新 {updated_count} 个权限')

    def get_role_menu_mapping(self):
        """获取角色菜单权限映射"""
        return {
            # 学生角色 - 主要访问学习相关功能
            UserRole.STUDENT.value: [
                'dashboard',
                'learning_center',
                'my_courses',
                'practice_exercises',
                'progress_tracking',
                'profile_management',
                'profile_edit',
                'password_change',
            ],
            
            # 家长角色 - 主要查看孩子学习情况
            UserRole.PARENT.value: [
                'dashboard',
                'parent_center',
                'student_progress',
                'communication',
                'profile_management',
                'profile_edit',
                'password_change',
            ],
            
            # 教师角色 - 教学相关功能
            UserRole.TEACHER.value: [
                'dashboard',
                'academic_management',
                'curriculum_management',
                'course_list',
                'course_create',
                'teaching_management',
                'student_management',
                'learning_center',
                'my_courses',
                'profile_management',
                'profile_edit',
                'password_change',
                'reports',
                'learning_reports',
            ],
            
            # 系统管理员 - 全部功能访问
            UserRole.ADMIN.value: [
                'dashboard',
                'user_management',
                'user_list',
                'user_create',
                'user_roles',
                'role_management',
                'role_list',
                'role_permissions',
                'role_templates',
                'academic_management',
                'curriculum_management',
                'course_list',
                'course_create',
                'teaching_management',
                'student_management',
                'research_management',
                'research_activities',
                'quality_assessment',
                'learning_center',
                'my_courses',
                'practice_exercises',
                'progress_tracking',
                'parent_center',
                'student_progress',
                'communication',
                'system_settings',
                'permission_management',
                'menu_management',
                'profile_management',
                'profile_edit',
                'password_change',
                'reports',
                'user_reports',
                'learning_reports',
                'logs',
                'login_logs',
                'operation_logs',
            ],
            
            # 教导主任 - 教学管理和学生管理
            UserRole.DEAN.value: [
                'dashboard',
                'user_management',
                'user_list',
                'user_create',
                'user_roles',
                'academic_management',
                'curriculum_management',
                'course_list',
                'course_create',
                'teaching_management',
                'student_management',
                'research_management',
                'research_activities',
                'quality_assessment',
                'parent_center',
                'student_progress',
                'communication',
                'profile_management',
                'profile_edit',
                'password_change',
                'reports',
                'user_reports',
                'learning_reports',
                'logs',
                'operation_logs',
            ],
            
            # 教务主任 - 课程和教学管理
            UserRole.ACADEMIC_DIRECTOR.value: [
                'dashboard',
                'academic_management',
                'curriculum_management',
                'course_list',
                'course_create',
                'teaching_management',
                'student_management',
                'research_management',
                'research_activities',
                'quality_assessment',
                'profile_management',
                'profile_edit',
                'password_change',
                'reports',
                'learning_reports',
                'logs',
                'operation_logs',
            ],
            
            # 教研组长 - 教研和质量管理
            UserRole.RESEARCH_LEADER.value: [
                'dashboard',
                'academic_management',
                'curriculum_management',
                'course_list',
                'teaching_management',
                'research_management',
                'research_activities',
                'quality_assessment',
                'profile_management',
                'profile_edit',
                'password_change',
                'reports',
                'learning_reports',
            ],
        }

    def can_edit_menu(self, role, menu_key):
        """判断角色是否可以编辑指定菜单"""
        # 管理员可以编辑所有菜单
        if role == UserRole.ADMIN.value:
            return True
        
        # 教导主任可以编辑用户和学生相关菜单
        if role == UserRole.DEAN.value:
            edit_menus = [
                'user_create', 'user_roles', 'student_management',
                'teaching_management', 'communication'
            ]
            return menu_key in edit_menus
        
        # 教务主任可以编辑课程和教学菜单
        if role == UserRole.ACADEMIC_DIRECTOR.value:
            edit_menus = [
                'course_create', 'curriculum_management', 'teaching_management',
                'quality_assessment'
            ]
            return menu_key in edit_menus
        
        # 教研组长可以编辑教研相关菜单
        if role == UserRole.RESEARCH_LEADER.value:
            edit_menus = ['research_activities', 'quality_assessment']
            return menu_key in edit_menus
        
        # 教师可以编辑自己的课程和教学内容
        if role == UserRole.TEACHER.value:
            edit_menus = ['course_create', 'teaching_management', 'my_courses']
            return menu_key in edit_menus
        
        # 学生和家长只能编辑个人资料
        if role in [UserRole.STUDENT.value, UserRole.PARENT.value]:
            edit_menus = ['profile_edit', 'password_change']
            return menu_key in edit_menus
        
        return False

    def can_delete_menu(self, role, menu_key):
        """判断角色是否可以删除指定菜单内容"""
        # 只有管理员可以删除内容
        if role == UserRole.ADMIN.value:
            # 管理员也不能删除系统核心菜单
            protected_menus = [
                'dashboard', 'system_settings', 'permission_management',
                'menu_management', 'profile_management'
            ]
            return menu_key not in protected_menus
        
        # 教导主任可以删除学生相关内容
        if role == UserRole.DEAN.value:
            delete_menus = ['student_management']
            return menu_key in delete_menus
        
        # 教务主任可以删除课程内容
        if role == UserRole.ACADEMIC_DIRECTOR.value:
            delete_menus = ['course_list']
            return menu_key in delete_menus
        
        # 其他角色不能删除内容
        return False