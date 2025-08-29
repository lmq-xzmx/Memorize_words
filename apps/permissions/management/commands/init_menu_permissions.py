from django.core.management.base import BaseCommand
from django.db import transaction
from apps.permissions.models import MenuModuleConfig
from apps.accounts.models import UserRole
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '初始化菜单配置和角色权限'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有菜单配置和权限',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)
        
        if reset:
            self.stdout.write('正在重置菜单配置和权限...')
            MenuModuleConfig.objects.all().delete()
            # RoleMenuPermission 已被废弃，跳过删除
        
        with transaction.atomic():
            self.create_menu_configs()
            self.create_role_permissions()
        
        self.stdout.write(
            self.style.SUCCESS('菜单配置和权限初始化完成！')
        )

    def create_menu_configs(self):
        """创建菜单配置"""
        menu_configs = [
            # 根级菜单
            {
                'key': 'dashboard',
                'name': '仪表板',
                'menu_level': 'root',
                'icon': 'fas fa-tachometer-alt',
                'url': '/dashboard',
                'sort_order': 1,
                'description': '系统仪表板，显示概览信息'
            },
            {
                'key': 'learning',
                'name': '学习中心',
                'menu_level': 'root',
                'icon': 'fas fa-graduation-cap',
                'url': '/learning',
                'sort_order': 2,
                'description': '学习相关功能模块'
            },
            {
                'key': 'teaching',
                'name': '教学管理',
                'menu_level': 'root',
                'icon': 'fas fa-chalkboard-teacher',
                'url': '/teaching',
                'sort_order': 3,
                'description': '教学管理功能模块'
            },
            {
                'key': 'words',
                'name': '词汇管理',
                'menu_level': 'root',
                'icon': 'fas fa-book',
                'url': '/words',
                'sort_order': 4,
                'description': '词汇相关功能模块'
            },
            {
                'key': 'accounts',
                'name': '用户管理',
                'menu_level': 'root',
                'icon': 'fas fa-users',
                'url': '/accounts',
                'sort_order': 5,
                'description': '用户账户管理'
            },
            {
                'key': 'permissions',
                'name': '权限管理',
                'menu_level': 'root',
                'icon': 'fas fa-shield-alt',
                'url': '/permissions',
                'sort_order': 6,
                'description': '系统权限配置'
            },
            {
                'key': 'access_dev_tools',
                'name': '开发工具',
                'menu_level': 'root',
                'icon': 'fas fa-tools',
                'url': '/dev',
                'sort_order': 7,
                'description': '开发工具和调试功能'
            },
            
            # 一级子菜单
            {
                'key': 'learning_practice',
                'name': '学习练习',
                'menu_level': 'level1',
                'icon': 'fas fa-dumbbell',
                'url': '/learning/practice',
                'sort_order': 21,
                'description': '各种学习练习模式'
            },
            {
                'key': 'learning_progress',
                'name': '学习进度',
                'menu_level': 'level1',
                'icon': 'fas fa-chart-line',
                'url': '/learning/progress',
                'sort_order': 22,
                'description': '学习进度跟踪'
            },
            {
                'key': 'teaching_plans',
                'name': '教学计划',
                'menu_level': 'level1',
                'icon': 'fas fa-calendar-alt',
                'url': '/teaching/plans',
                'sort_order': 31,
                'description': '教学计划管理'
            },
            {
                'key': 'teaching_goals',
                'name': '教学目标',
                'menu_level': 'level1',
                'icon': 'fas fa-bullseye',
                'url': '/teaching/goals',
                'sort_order': 32,
                'description': '教学目标设定'
            },
            {
                'key': 'words_vocabulary',
                'name': '词汇库',
                'menu_level': 'level1',
                'icon': 'fas fa-database',
                'url': '/words/vocabulary',
                'sort_order': 41,
                'description': '词汇数据库管理'
            },
            {
                'key': 'words_management',
                'name': '词汇管理',
                'menu_level': 'level1',
                'icon': 'fas fa-edit',
                'url': '/words/management',
                'sort_order': 42,
                'description': '词汇增删改查'
            },
            {
                'key': 'accounts_users',
                'name': '用户列表',
                'menu_level': 'level1',
                'icon': 'fas fa-user-friends',
                'url': '/accounts/users',
                'sort_order': 51,
                'description': '用户账户列表'
            },
            {
                'key': 'accounts_roles',
                'name': '角色管理',
                'menu_level': 'level1',
                'icon': 'fas fa-user-tag',
                'url': '/accounts/roles',
                'sort_order': 52,
                'description': '用户角色配置'
            },
            {
                'key': 'permissions_menu',
                'name': '菜单权限',
                'menu_level': 'level1',
                'icon': 'fas fa-bars',
                'url': '/permissions/menu',
                'sort_order': 61,
                'description': '菜单访问权限配置'
            },
            {
                'key': 'permissions_role',
                'name': '角色权限',
                'menu_level': 'level1',
                'icon': 'fas fa-key',
                'url': '/permissions/role',
                'sort_order': 62,
                'description': '角色权限配置'
            },
            
            # 二级子菜单
            {
                'key': 'learning_practice_word',
                'name': '单词练习',
                'menu_level': 'level2',
                'icon': 'fas fa-spell-check',
                'url': '/learning/practice/word',
                'sort_order': 211,
                'description': '单词学习练习'
            },
            {
                'key': 'learning_practice_test',
                'name': '测试练习',
                'menu_level': 'level2',
                'icon': 'fas fa-clipboard-check',
                'url': '/learning/practice/test',
                'sort_order': 212,
                'description': '测试练习模式'
            },
        ]
        
        for config in menu_configs:
            menu, created = MenuModuleConfig.objects.get_or_create(
                key=config['key'],
                defaults=config
            )
            if created:
                self.stdout.write(f'创建菜单: {menu.name}')
            else:
                self.stdout.write(f'菜单已存在: {menu.name}')

    def create_role_permissions(self):
        """创建角色权限配置"""
        # 角色权限映射
        role_permissions = {
            UserRole.ADMIN: {
                # 管理员拥有所有权限
                'dashboard': True,
                'learning': True,
                'teaching': True,
                'words': True,
                'accounts': True,
                'permissions': True,
                'learning_practice': True,
                'learning_progress': True,
                'teaching_plans': True,
                'teaching_goals': True,
                'words_vocabulary': True,
                'words_management': True,
                'accounts_users': True,
                'accounts_roles': True,
                'permissions_menu': True,
                'permissions_role': True,
                'learning_practice_word': True,
                'learning_practice_test': True,
                'access_dev_tools': True,
            },
            UserRole.DEAN: {
                # 教导主任权限
                'dashboard': True,
                'learning': True,
                'teaching': True,
                'words': True,
                'accounts': True,
                'permissions': True,
                'learning_practice': True,
                'learning_progress': True,
                'teaching_plans': True,
                'teaching_goals': True,
                'words_vocabulary': True,
                'words_management': True,
                'accounts_users': True,
                'accounts_roles': True,
                'permissions_menu': True,
                'permissions_role': True,
                'learning_practice_word': False,
                'learning_practice_test': False,
            },
            UserRole.ACADEMIC_DIRECTOR: {
                # 教务主任权限
                'dashboard': True,
                'learning': True,
                'teaching': True,
                'words': True,
                'accounts': False,
                'permissions': False,
                'learning_practice': True,
                'learning_progress': True,
                'teaching_plans': True,
                'teaching_goals': True,
                'words_vocabulary': True,
                'words_management': False,
                'accounts_users': False,
                'accounts_roles': False,
                'permissions_menu': False,
                'permissions_role': False,
                'learning_practice_word': False,
                'learning_practice_test': False,
            },
            UserRole.RESEARCH_LEADER: {
                # 教研组长权限
                'dashboard': True,
                'learning': True,
                'teaching': True,
                'words': True,
                'accounts': False,
                'permissions': False,
                'learning_practice': True,
                'learning_progress': True,
                'teaching_plans': True,
                'teaching_goals': False,
                'words_vocabulary': True,
                'words_management': False,
                'accounts_users': False,
                'accounts_roles': False,
                'permissions_menu': False,
                'permissions_role': False,
                'learning_practice_word': False,
                'learning_practice_test': False,
            },
            UserRole.TEACHER: {
                # 教师权限
                'dashboard': True,
                'learning': True,
                'teaching': True,
                'words': True,
                'accounts': False,
                'permissions': False,
                'learning_practice': True,
                'learning_progress': True,
                'teaching_plans': True,
                'teaching_goals': False,
                'words_vocabulary': True,
                'words_management': False,
                'accounts_users': False,
                'accounts_roles': False,
                'permissions_menu': False,
                'permissions_role': False,
                'learning_practice_word': False,
                'learning_practice_test': False,
            },
            UserRole.PARENT: {
                # 家长权限
                'dashboard': True,
                'learning': True,
                'teaching': False,
                'words': False,
                'accounts': False,
                'permissions': False,
                'learning_practice': False,
                'learning_progress': True,
                'teaching_plans': False,
                'teaching_goals': False,
                'words_vocabulary': False,
                'words_management': False,
                'accounts_users': False,
                'accounts_roles': False,
                'permissions_menu': False,
                'permissions_role': False,
                'learning_practice_word': False,
                'learning_practice_test': False,
            },
            UserRole.STUDENT: {
                # 学生权限
                'dashboard': True,
                'learning': True,
                'teaching': False,
                'words': False,
                'accounts': False,
                'permissions': False,
                'learning_practice': True,
                'learning_progress': True,
                'teaching_plans': False,
                'teaching_goals': False,
                'words_vocabulary': False,
                'words_management': False,
                'accounts_users': False,
                'accounts_roles': False,
                'permissions_menu': False,
                'permissions_role': False,
                'learning_practice_word': True,
                'learning_practice_test': True,
            },
        }
        
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        # 请使用 MenuValidity 和 RoleMenuAssignment 替代
        self.stdout.write('跳过角色权限配置（RoleMenuPermission 已废弃）')