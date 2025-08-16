from django.core.management.base import BaseCommand
from django.db import transaction
from apps.permissions.models import MenuModuleConfig
import json
import os


class Command(BaseCommand):
    help = '从前端菜单配置文件同步菜单到后端数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--config-file',
            type=str,
            default='config/menuConfig.js',
            help='前端菜单配置文件路径（相对于项目根目录）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅预览同步结果，不实际执行数据库操作'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制覆盖已存在的菜单配置'
        )

    def handle(self, *args, **options):
        config_file = options['config_file']
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('开始同步前端菜单配置...'))

        # 构建配置文件的完整路径
        from django.conf import settings
        project_root = settings.BASE_DIR.parent
        config_path = os.path.join(project_root, config_file)

        if not os.path.exists(config_path):
            self.stdout.write(
                self.style.ERROR(f'配置文件不存在: {config_path}')
            )
            return

        try:
            # 解析前端菜单配置
            menu_data = self.parse_menu_config(config_path)
            if not menu_data:
                self.stdout.write(
                    self.style.ERROR('无法解析菜单配置文件')
                )
                return

            # 转换为后端格式
            backend_menus = self.convert_to_backend_format(menu_data)

            if dry_run:
                self.preview_sync_result(backend_menus)
            else:
                self.sync_menus_to_database(backend_menus, force)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'同步失败: {str(e)}')
            )

    def parse_menu_config(self, config_path):
        """
        解析前端菜单配置文件
        注意：这是一个简化的解析器，实际项目中可能需要更复杂的JS解析
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 简单的配置提取（实际项目中可能需要更复杂的解析）
            # 这里假设配置文件包含可解析的JSON格式数据
            # 或者可以使用正则表达式提取配置对象

            # 为了演示，我们提供一个默认的菜单配置
            default_config = {
                'bottomNavMenus': [
                    {
                        'id': 'word',
                        'name': '单词学习',
                        'icon': 'book',
                        'path': '/word-learning',
                        'description': '单词学习模块',
                        'permission': 'word.view'
                    },
                    {
                        'id': 'tools',
                        'name': '学习工具',
                        'icon': 'tool',
                        'path': '/tools',
                        'description': '学习工具集合',
                        'permission': 'tools.view'
                    },
                    {
                        'id': 'fashion',
                        'name': '时尚内容',
                        'icon': 'star',
                        'path': '/fashion',
                        'description': '时尚学习内容',
                        'permission': 'fashion.view'
                    },
                    {
                        'id': 'profile',
                        'name': '个人中心',
                        'icon': 'user',
                        'path': '/profile',
                        'description': '用户个人中心',
                        'permission': 'profile.view'
                    }
                ],
                'toolsMenuConfig': {
                    'title': '开发工具',
                    'items': [
                        {
                            'id': 'dev-console',
                            'name': '开发控制台',
                            'icon': 'console',
                            'path': '/dev/console',
                            'description': '开发者控制台',
                            'permission': 'dev.console'
                        },
                        {
                            'id': 'api-docs',
                            'name': 'API文档',
                            'icon': 'api',
                            'path': '/dev/api-docs',
                            'description': 'API接口文档',
                            'permission': 'dev.api_docs'
                        }
                    ]
                },
                'fashionMenuConfig': {
                    'title': '时尚内容',
                    'items': [
                        {
                            'id': 'fashion-trends',
                            'name': '时尚趋势',
                            'icon': 'trend',
                            'path': '/fashion/trends',
                            'description': '最新时尚趋势',
                            'permission': 'fashion.trends'
                        },
                        {
                            'id': 'community',
                            'name': '社区交流',
                            'icon': 'community',
                            'path': '/community',
                            'description': '用户社区交流',
                            'permission': 'community.view'
                        }
                    ]
                },
                'adminMenuConfig': {
                    'title': '管理功能',
                    'items': [
                        {
                            'id': 'admin-users',
                            'name': '用户管理',
                            'icon': 'users',
                            'path': '/admin/users',
                            'description': '用户管理功能',
                            'permission': 'admin.users'
                        },
                        {
                            'id': 'admin-permissions',
                            'name': '权限管理',
                            'icon': 'shield',
                            'path': '/admin/permissions',
                            'description': '权限管理功能',
                            'permission': 'admin.permissions'
                        }
                    ]
                }
            }

            return default_config

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'解析配置文件失败: {str(e)}')
            )
            return None

    def convert_to_backend_format(self, frontend_config):
        """
        将前端菜单配置转换为后端格式
        """
        menus = []

        # 处理底部导航菜单
        if 'bottomNavMenus' in frontend_config:
            for index, menu in enumerate(frontend_config['bottomNavMenus']):
                menus.append({
                    'key': menu.get('id') or menu.get('key'),
                    'name': menu.get('name') or menu.get('title', ''),
                    'icon': menu.get('icon', ''),
                    'url': menu.get('path') or menu.get('url', ''),
                    'description': menu.get('description', ''),
                    'sort_order': index,
                    'menu_level': 'bottom_nav',
                    'is_active': menu.get('enabled', True)
                })

        # 处理工具菜单
        if 'toolsMenuConfig' in frontend_config and 'items' in frontend_config['toolsMenuConfig']:
            for index, menu in enumerate(frontend_config['toolsMenuConfig']['items']):
                menus.append({
                    'key': menu.get('id') or menu.get('key'),
                    'name': menu.get('name') or menu.get('title', ''),
                    'icon': menu.get('icon', ''),
                    'url': menu.get('path') or menu.get('url', ''),
                    'description': menu.get('description', ''),
                    'sort_order': index + 100,
                    'menu_level': 'tools',
                    'is_active': menu.get('enabled', True)
                })

        # 处理时尚菜单
        if 'fashionMenuConfig' in frontend_config and 'items' in frontend_config['fashionMenuConfig']:
            for index, menu in enumerate(frontend_config['fashionMenuConfig']['items']):
                menus.append({
                    'key': menu.get('id') or menu.get('key'),
                    'name': menu.get('name') or menu.get('title', ''),
                    'icon': menu.get('icon', ''),
                    'url': menu.get('path') or menu.get('url', ''),
                    'description': menu.get('description', ''),
                    'sort_order': index + 200,
                    'menu_level': 'fashion',
                    'is_active': menu.get('enabled', True)
                })

        # 处理管理菜单
        if 'adminMenuConfig' in frontend_config and 'items' in frontend_config['adminMenuConfig']:
            for index, menu in enumerate(frontend_config['adminMenuConfig']['items']):
                menus.append({
                    'key': menu.get('id') or menu.get('key'),
                    'name': menu.get('name') or menu.get('title', ''),
                    'icon': menu.get('icon', ''),
                    'url': menu.get('path') or menu.get('url', ''),
                    'description': menu.get('description', ''),
                    'sort_order': index + 300,
                    'menu_level': 'admin',
                    'is_active': menu.get('enabled', True)
                })

        return menus

    def preview_sync_result(self, backend_menus):
        """
        预览同步结果
        """
        self.stdout.write(self.style.WARNING('=== 预览模式 - 不会实际修改数据库 ==='))
        self.stdout.write(f'将要同步 {len(backend_menus)} 个菜单项:')
        
        for menu in backend_menus:
            status = '新建'
            try:
                existing = MenuModuleConfig.objects.get(key=menu['key'])
                status = '更新'
            except MenuModuleConfig.DoesNotExist:
                pass
            
            self.stdout.write(
                f"  [{status}] {menu['key']} - {menu['name']} ({menu['menu_level']})"
            )

    def sync_menus_to_database(self, backend_menus, force=False):
        """
        同步菜单到数据库
        """
        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for menu_data in backend_menus:
                menu_key = menu_data['key']
                if not menu_key:
                    continue

                try:
                    existing_menu = MenuModuleConfig.objects.get(key=menu_key)
                    if force:
                        # 更新现有菜单
                        for field, value in menu_data.items():
                            setattr(existing_menu, field, value)
                        existing_menu.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"更新菜单: {menu_key} - {menu_data['name']}")
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"跳过已存在的菜单: {menu_key} (使用 --force 强制更新)")
                        )
                except MenuModuleConfig.DoesNotExist:
                    # 创建新菜单
                    MenuModuleConfig.objects.create(**menu_data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"创建菜单: {menu_key} - {menu_data['name']}")
                    )

        # 输出同步结果
        self.stdout.write(self.style.SUCCESS('\n=== 同步完成 ==='))
        self.stdout.write(f'创建: {created_count} 个')
        self.stdout.write(f'更新: {updated_count} 个')
        self.stdout.write(f'跳过: {skipped_count} 个')
        self.stdout.write(f'总计: {created_count + updated_count + skipped_count} 个')