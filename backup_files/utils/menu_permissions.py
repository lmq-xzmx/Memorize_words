"""菜单权限控制工具 - 英语学习平台版本"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import UserRole


class MenuPermissionManager:
    """菜单权限管理器"""
    
    # 前台侧边栏菜单权限映射
    SIDEBAR_MENU_PERMISSIONS = {
        # 学习模块
        'learning': {
            'roles': [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT],
            'name': '学习中心',
            'icon': 'fas fa-book-open',
            'url': '/learning/',
            'permissions': [
                'courses.view_lesson',
                'analytics.view_progress',
            ]
        },
        
        # 课程管理
        'courses': {
            'roles': [UserRole.ADMIN, UserRole.TEACHER],
            'name': '课程管理',
            'icon': 'fas fa-layer-group',
            'url': '/courses/',
            'permissions': [
                'courses.view_course',
                'courses.add_course',
                'courses.change_course',
            ]
        },
        
        # 学习分析
        'analytics': {
            'roles': [UserRole.ADMIN, UserRole.TEACHER, UserRole.PARENT],
            'name': '学习分析',
            'icon': 'fas fa-chart-line',
            'url': '/analytics/',
            'permissions': [
                'analytics.view_learningprogress',
                'analytics.view_statistics',
            ]
        },
        
        # 教学管理
        'teaching': {
            'roles': [UserRole.ADMIN, UserRole.TEACHER],
            'name': '教学管理',
            'icon': 'fas fa-chalkboard-teacher',
            'url': '/teaching/',
            'permissions': [
                'teaching.view_teachingplan',
                'teaching.add_teachingplan',
                'teaching.change_teachingplan',
            ]
        },
        
        # 用户管理
        'accounts': {
            'roles': [UserRole.ADMIN],
            'name': '用户管理',
            'icon': 'fas fa-users',
            'url': '/accounts/',
            'permissions': [
                'accounts.view_customuser',
                'accounts.add_customuser',
                'accounts.change_customuser',
            ]
        },
        
        # 家长中心
        'parent_center': {
            'roles': [UserRole.PARENT],
            'name': '家长中心',
            'icon': 'fas fa-heart',
            'url': '/parent/',
            'permissions': [
                'accounts.view_learningprofile',
                'analytics.view_child_progress',
            ]
        },
    }
    
    # 后台菜单权限映射
    BACKEND_MENU_PERMISSIONS = {
        'accounts': [
            'accounts.view_customuser',
            'accounts.add_customuser',
            'accounts.change_customuser',
            'accounts.delete_customuser',
        ],
        'auth': [
            'auth.view_group',
            'auth.add_group',
            'auth.change_group',
            'auth.view_permission',
        ],
        'courses_admin': [
            'courses.add_course',
            'courses.change_course',
            'courses.delete_course',
            'courses.view_lesson',
        ],
        'permissions': [
            'permissions.view_permission',
            'permissions.change_permission',
        ],
        'teaching_admin': [
            'teaching.add_teachingplan',
            'teaching.change_teachingplan',
            'teaching.delete_teachingplan',
        ],
        'analytics_admin': [
            'analytics.view_all_statistics',
            'analytics.export_data',
        ]
    }
    
    @classmethod
    def get_user_sidebar_menus(cls, user):
        """获取用户可访问的侧边栏菜单"""
        if not user or not user.is_authenticated:
            return {}
        
        # 超级用户可以看到所有菜单
        if user.is_superuser:
            return cls.SIDEBAR_MENU_PERMISSIONS
        
        # 获取用户角色
        user_role = getattr(user, 'role', None)
        if not user_role:
            return {}
        
        # 过滤用户可访问的菜单
        accessible_menus = {}
        for menu_key, menu_config in cls.SIDEBAR_MENU_PERMISSIONS.items():
            if user_role in menu_config['roles']:
                accessible_menus[menu_key] = menu_config
        
        return accessible_menus
    
    @classmethod
    def get_user_frontend_menus(cls, user):
        """获取用户可访问的前台菜单（兼容旧方法）"""
        accessible_menus = cls.get_user_sidebar_menus(user)
        return list(accessible_menus.keys())
    
    @classmethod
    def get_user_backend_menus(cls, user):
        """获取用户可访问的后台菜单"""
        if user.is_superuser:
            return list(cls.BACKEND_MENU_PERMISSIONS.keys())
        
        user_permissions = cls._get_user_permissions(user)
        accessible_menus = []
        
        for menu_key, required_perms in cls.BACKEND_MENU_PERMISSIONS.items():
            if cls._has_any_permission(user_permissions, required_perms):
                accessible_menus.append(menu_key)
        
        return accessible_menus
    
    @classmethod
    def can_access_sidebar_menu(cls, user, menu_key):
        """检查用户是否可以访问特定侧边栏菜单"""
        if not user or not user.is_authenticated:
            return False
            
        if user.is_superuser:
            return True
        
        if menu_key not in cls.SIDEBAR_MENU_PERMISSIONS:
            return False
        
        user_role = getattr(user, 'role', None)
        if not user_role:
            return False
        
        return user_role in cls.SIDEBAR_MENU_PERMISSIONS[menu_key]['roles']
    
    @classmethod
    def can_access_frontend_menu(cls, user, menu_key):
        """检查用户是否可以访问特定前台菜单（兼容旧方法）"""
        return cls.can_access_sidebar_menu(user, menu_key)
    
    @classmethod
    def can_access_backend_menu(cls, user, menu_key):
        """检查用户是否可以访问特定后台菜单"""
        if user.is_superuser:
            return True
        
        if menu_key not in cls.BACKEND_MENU_PERMISSIONS:
            return False
        
        user_permissions = cls._get_user_permissions(user)
        required_perms = cls.BACKEND_MENU_PERMISSIONS[menu_key]
        
        return cls._has_any_permission(user_permissions, required_perms)
    
    @classmethod
    def get_user_menu_summary(cls, user):
        """获取用户菜单权限摘要"""
        if not user or not user.is_authenticated:
            return {
                'sidebar_menus': [],
                'backend_menus': [],
                'total_sidebar': 0,
                'total_backend': 0,
                'role_display': '未登录'
            }
        
        sidebar_menus = cls.get_user_sidebar_menus(user)
        backend_menus = cls.get_user_backend_menus(user)
        
        # 转换为显示格式
        sidebar_menu_list = []
        for menu_key, menu_config in sidebar_menus.items():
            sidebar_menu_list.append({
                'key': menu_key,
                'name': menu_config['name'],
                'icon': menu_config['icon'],
                'url': menu_config['url']
            })
        
        return {
            'sidebar_menus': sidebar_menu_list,
            'backend_menus': backend_menus,
            'total_sidebar': len(sidebar_menu_list),
            'total_backend': len(backend_menus),
            'role_display': user.get_role_display() if hasattr(user, 'get_role_display') else '未知角色'
        }
    
    @classmethod
    def _get_user_permissions(cls, user):
        """获取用户的所有权限"""
        if not user.is_authenticated:
            return set()
        
        # 获取用户直接权限
        user_perms = set(user.user_permissions.values_list('codename', flat=True))
        
        # 获取用户组权限
        group_perms = set()
        for group in user.groups.all():
            group_perms.update(group.permissions.values_list('codename', flat=True))
        
        # 组合权限，格式为 app_label.codename
        all_perms = set()
        for perm in Permission.objects.filter(
            codename__in=user_perms.union(group_perms)
        ).select_related('content_type'):
            all_perms.add(f"{perm.content_type.app_label}.{perm.codename}")
        
        return all_perms
    
    @classmethod
    def _has_any_permission(cls, user_permissions, required_permissions):
        """检查用户是否拥有任一所需权限"""
        return bool(user_permissions.intersection(set(required_permissions)))
    
    @classmethod
    def get_menu_structure_for_user(cls, user, menu_type='frontend'):
        """获取用户的完整菜单结构"""
        if menu_type == 'frontend':
            return cls.get_user_sidebar_menus(user)
        else:
            accessible_menus = cls.get_user_backend_menus(user)
            menu_config = cls._get_backend_menu_config()
            
            # 过滤菜单结构
            filtered_menu = {}
            for menu_key in accessible_menus:
                if menu_key in menu_config:
                    filtered_menu[menu_key] = menu_config[menu_key]
            
            return filtered_menu
    
    @classmethod
    def _get_frontend_menu_config(cls):
        """获取前台菜单配置（兼容旧方法）"""
        return cls.SIDEBAR_MENU_PERMISSIONS
    
    @classmethod
    def _get_backend_menu_config(cls):
        """获取后台菜单配置"""
        return {
            'accounts': {'name': '用户管理', 'icon': 'fas fa-users'},
            'auth': {'name': '认证权限', 'icon': 'fas fa-lock'},
            'courses_admin': {'name': '课程管理', 'icon': 'fas fa-book'},
            'permissions': {'name': '权限管理', 'icon': 'fas fa-key'},
            'teaching_admin': {'name': '教学管理', 'icon': 'fas fa-chalkboard'},
            'analytics_admin': {'name': '分析管理', 'icon': 'fas fa-chart-bar'}
        }


# 模板标签支持
def get_user_menus(user, menu_type='frontend'):
    """模板标签：获取用户菜单"""
    return MenuPermissionManager.get_menu_structure_for_user(user, menu_type)


def can_access_menu(user, menu_key, menu_type='frontend'):
    """模板标签：检查菜单访问权限"""
    if menu_type == 'frontend':
        return MenuPermissionManager.can_access_frontend_menu(user, menu_key)
    else:
        return MenuPermissionManager.can_access_backend_menu(user, menu_key)