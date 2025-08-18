from django.core.management.base import BaseCommand
from django.db import transaction
from apps.permissions.models import MenuModuleConfig


class Command(BaseCommand):
    help = '创建3级菜单体系的基础菜单模块配置'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有菜单模块配置',
        )

    def handle(self, *args, **options):
        reset = options.get('reset')
        
        if reset:
            self.stdout.write('重置所有菜单模块配置...')
            MenuModuleConfig.objects.all().delete()
        
        self.stdout.write('创建3级菜单体系配置...')
        self.create_menu_modules()
        
        self.stdout.write(self.style.SUCCESS('菜单模块配置完成！'))

    def create_menu_modules(self):
        """创建菜单模块配置"""
        with transaction.atomic():
            # 定义3级菜单结构
            menu_structure = {
                # 根目录菜单
                'dashboard': {
                    'name': '仪表盘',
                    'level': 'root',
                    'icon': 'fas fa-tachometer-alt',
                    'url': '/dashboard',
                    'sort_order': 10,
                    'description': '系统概览和统计信息'
                },
                
                # 用户管理模块
                'user_management': {
                    'name': '用户管理',
                    'level': 'root',
                    'icon': 'fas fa-users',
                    'url': '/users',
                    'sort_order': 20,
                    'description': '用户账户管理'
                },
                'user_list': {
                    'name': '用户列表',
                    'level': 'level1',
                    'icon': 'fas fa-list',
                    'url': '/users/list',
                    'sort_order': 21,
                    'description': '查看和管理用户列表'
                },
                'user_create': {
                    'name': '创建用户',
                    'level': 'level1',
                    'icon': 'fas fa-user-plus',
                    'url': '/users/create',
                    'sort_order': 22,
                    'description': '创建新用户账户'
                },
                'user_roles': {
                    'name': '角色分配',
                    'level': 'level1',
                    'icon': 'fas fa-user-tag',
                    'url': '/users/roles',
                    'sort_order': 23,
                    'description': '用户角色分配管理'
                },
                
                # 角色权限管理
                'role_management': {
                    'name': '角色管理',
                    'level': 'root',
                    'icon': 'fas fa-user-shield',
                    'url': '/roles',
                    'sort_order': 30,
                    'description': '角色和权限管理'
                },
                'role_list': {
                    'name': '角色列表',
                    'level': 'level1',
                    'icon': 'fas fa-list-ul',
                    'url': '/roles/list',
                    'sort_order': 31,
                    'description': '查看和管理角色列表'
                },
                'role_permissions': {
                    'name': '权限配置',
                    'level': 'level1',
                    'icon': 'fas fa-key',
                    'url': '/roles/permissions',
                    'sort_order': 32,
                    'description': '角色权限配置'
                },
                'role_templates': {
                    'name': '角色模板',
                    'level': 'level1',
                    'icon': 'fas fa-clipboard-list',
                    'url': '/roles/templates',
                    'sort_order': 33,
                    'description': '角色模板管理'
                },
                
                # 教学管理模块
                'academic_management': {
                    'name': '教学管理',
                    'level': 'root',
                    'icon': 'fas fa-graduation-cap',
                    'url': '/academic',
                    'sort_order': 40,
                    'description': '教学相关管理功能'
                },
                'curriculum_management': {
                    'name': '课程管理',
                    'level': 'level1',
                    'icon': 'fas fa-book',
                    'url': '/academic/curriculum',
                    'sort_order': 41,
                    'description': '课程内容和计划管理'
                },
                'course_list': {
                    'name': '课程列表',
                    'level': 'level2',
                    'icon': 'fas fa-list',
                    'url': '/academic/curriculum/list',
                    'sort_order': 411,
                    'description': '查看所有课程'
                },
                'course_create': {
                    'name': '创建课程',
                    'level': 'level2',
                    'icon': 'fas fa-plus',
                    'url': '/academic/curriculum/create',
                    'sort_order': 412,
                    'description': '创建新课程'
                },
                'teaching_management': {
                    'name': '教学管理',
                    'level': 'level1',
                    'icon': 'fas fa-chalkboard-teacher',
                    'url': '/academic/teaching',
                    'sort_order': 42,
                    'description': '教学活动管理'
                },
                'student_management': {
                    'name': '学生管理',
                    'level': 'level1',
                    'icon': 'fas fa-user-graduate',
                    'url': '/academic/students',
                    'sort_order': 43,
                    'description': '学生信息和学习管理'
                },
                
                # 教研管理模块
                'research_management': {
                    'name': '教研管理',
                    'level': 'root',
                    'icon': 'fas fa-microscope',
                    'url': '/research',
                    'sort_order': 50,
                    'description': '教学研究和方法管理'
                },
                'research_activities': {
                    'name': '教研活动',
                    'level': 'level1',
                    'icon': 'fas fa-calendar-alt',
                    'url': '/research/activities',
                    'sort_order': 51,
                    'description': '教研活动组织和管理'
                },
                'quality_assessment': {
                    'name': '质量评估',
                    'level': 'level1',
                    'icon': 'fas fa-chart-line',
                    'url': '/research/assessment',
                    'sort_order': 52,
                    'description': '教学质量评估'
                },
                
                # 学习中心（学生专用）
                'learning_center': {
                    'name': '学习中心',
                    'level': 'root',
                    'icon': 'fas fa-brain',
                    'url': '/learning',
                    'sort_order': 60,
                    'description': '学生学习功能中心'
                },
                'my_courses': {
                    'name': '我的课程',
                    'level': 'level1',
                    'icon': 'fas fa-book-open',
                    'url': '/learning/courses',
                    'sort_order': 61,
                    'description': '学生个人课程'
                },
                'practice_exercises': {
                    'name': '练习题库',
                    'level': 'level1',
                    'icon': 'fas fa-dumbbell',
                    'url': '/learning/exercises',
                    'sort_order': 62,
                    'description': '练习和测试'
                },
                'progress_tracking': {
                    'name': '学习进度',
                    'level': 'level1',
                    'icon': 'fas fa-chart-bar',
                    'url': '/learning/progress',
                    'sort_order': 63,
                    'description': '学习进度跟踪'
                },
                
                # 家长中心
                'parent_center': {
                    'name': '家长中心',
                    'level': 'root',
                    'icon': 'fas fa-home',
                    'url': '/parent',
                    'sort_order': 70,
                    'description': '家长功能中心'
                },
                'student_progress': {
                    'name': '孩子进度',
                    'level': 'level1',
                    'icon': 'fas fa-child',
                    'url': '/parent/progress',
                    'sort_order': 71,
                    'description': '查看孩子学习进度'
                },
                'communication': {
                    'name': '沟通交流',
                    'level': 'level1',
                    'icon': 'fas fa-comments',
                    'url': '/parent/communication',
                    'sort_order': 72,
                    'description': '与老师沟通交流'
                },
                
                # 系统设置
                'system_settings': {
                    'name': '系统设置',
                    'level': 'root',
                    'icon': 'fas fa-cogs',
                    'url': '/settings',
                    'sort_order': 80,
                    'description': '系统配置和设置'
                },
                'permission_management': {
                    'name': '权限管理',
                    'level': 'level1',
                    'icon': 'fas fa-shield-alt',
                    'url': '/settings/permissions',
                    'sort_order': 81,
                    'description': '系统权限配置'
                },
                'menu_management': {
                    'name': '菜单管理',
                    'level': 'level1',
                    'icon': 'fas fa-bars',
                    'url': '/settings/menus',
                    'sort_order': 82,
                    'description': '菜单配置管理'
                },
                
                # 个人资料
                'profile_management': {
                    'name': '个人资料',
                    'level': 'root',
                    'icon': 'fas fa-user-circle',
                    'url': '/profile',
                    'sort_order': 90,
                    'description': '个人信息管理'
                },
                'profile_edit': {
                    'name': '编辑资料',
                    'level': 'level1',
                    'icon': 'fas fa-edit',
                    'url': '/profile/edit',
                    'sort_order': 91,
                    'description': '编辑个人信息'
                },
                'password_change': {
                    'name': '修改密码',
                    'level': 'level1',
                    'icon': 'fas fa-lock',
                    'url': '/profile/password',
                    'sort_order': 92,
                    'description': '修改登录密码'
                },
                
                # 报表统计
                'reports': {
                    'name': '报表统计',
                    'level': 'root',
                    'icon': 'fas fa-chart-pie',
                    'url': '/reports',
                    'sort_order': 100,
                    'description': '数据报表和统计分析'
                },
                'user_reports': {
                    'name': '用户统计',
                    'level': 'level1',
                    'icon': 'fas fa-users',
                    'url': '/reports/users',
                    'sort_order': 101,
                    'description': '用户数据统计'
                },
                'learning_reports': {
                    'name': '学习统计',
                    'level': 'level1',
                    'icon': 'fas fa-graduation-cap',
                    'url': '/reports/learning',
                    'sort_order': 102,
                    'description': '学习数据统计'
                },
                
                # 系统日志
                'logs': {
                    'name': '系统日志',
                    'level': 'root',
                    'icon': 'fas fa-file-alt',
                    'url': '/logs',
                    'sort_order': 110,
                    'description': '系统操作日志'
                },
                'login_logs': {
                    'name': '登录日志',
                    'level': 'level1',
                    'icon': 'fas fa-sign-in-alt',
                    'url': '/logs/login',
                    'sort_order': 111,
                    'description': '用户登录日志'
                },
                'operation_logs': {
                    'name': '操作日志',
                    'level': 'level1',
                    'icon': 'fas fa-history',
                    'url': '/logs/operations',
                    'sort_order': 112,
                    'description': '用户操作日志'
                },
            }
            
            # 批量创建菜单模块
            created_count = 0
            updated_count = 0
            
            for key, config in menu_structure.items():
                menu_module, created = MenuModuleConfig.objects.get_or_create(
                    key=key,
                    defaults={
                        'name': config['name'],
                        'menu_level': config['level'],
                        'icon': config['icon'],
                        'url': config['url'],
                        'sort_order': config['sort_order'],
                        'description': config['description'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  创建菜单: {config["name"]} ({key})')
                else:
                    # 更新现有菜单
                    menu_module.name = config['name']
                    menu_module.menu_level = config['level']
                    menu_module.icon = config['icon']
                    menu_module.url = config['url']
                    menu_module.sort_order = config['sort_order']
                    menu_module.description = config['description']
                    menu_module.save()
                    updated_count += 1
                    self.stdout.write(f'  更新菜单: {config["name"]} ({key})')
            
            self.stdout.write(f'\n菜单模块配置完成:')
            self.stdout.write(f'  创建: {created_count} 个')
            self.stdout.write(f'  更新: {updated_count} 个')
            self.stdout.write(f'  总计: {created_count + updated_count} 个菜单模块')
            
            # 显示菜单层级统计
            root_count = MenuModuleConfig.objects.filter(menu_level='root').count()
            level1_count = MenuModuleConfig.objects.filter(menu_level='level1').count()
            level2_count = MenuModuleConfig.objects.filter(menu_level='level2').count()
            
            self.stdout.write(f'\n菜单层级统计:')
            self.stdout.write(f'  根目录菜单: {root_count} 个')
            self.stdout.write(f'  一级菜单: {level1_count} 个')
            self.stdout.write(f'  二级菜单: {level2_count} 个')