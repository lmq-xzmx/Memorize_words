from django.contrib.auth.models import Permission
from guardian.shortcuts import get_perms, get_objects_for_user
from typing import Optional, Union
import logging

try:
    from .models import RoleManagement, RoleGroupMapping
except ImportError:
    RoleManagement = None
    RoleGroupMapping = None

logger = logging.getLogger(__name__)


class RolePermissionChecker:
    """
    角色权限检查器 - 支持角色继承
    """
    
    def __init__(self, user):
        self.user = user
        self._role_cache = None
        self._permissions_cache = None
    
    @property
    def role_management(self):
        """获取用户的角色管理对象（缓存）"""
        if self._role_cache is None and RoleManagement:
            try:
                self._role_cache = RoleManagement.objects.get(role=getattr(self.user, 'role', None))
            except (RoleManagement.DoesNotExist, AttributeError):
                self._role_cache = None
        return self._role_cache
    
    @property
    def all_permissions(self):
        """获取用户所有权限（包括继承的权限）"""
        if self._permissions_cache is None:
            role_mgmt = self.role_management
            if role_mgmt:
                self._permissions_cache = role_mgmt.get_all_permissions()
            else:
                self._permissions_cache = set()
        return self._permissions_cache
    
    def has_permission(self, permission_codename, app_label=None):
        """检查用户是否有指定权限"""
        if self.user.is_superuser:
            return True
        
        # 构建完整的权限名称
        if app_label:
            full_perm = f"{app_label}.{permission_codename}"
        else:
            full_perm = permission_codename
        
        # 检查Django内置权限
        if self.user.has_perm(full_perm):
            return True
        
        # 检查角色继承权限
        for perm in self.all_permissions:
            if perm.codename == permission_codename:
                if not app_label or perm.content_type.app_label == app_label:
                    return True
        
        return False
    
    def has_object_permission(self, permission_codename, obj, app_label=None):
        """检查用户是否对特定对象有权限"""
        if self.user.is_superuser:
            return True
        
        # 构建完整的权限名称
        if app_label:
            full_perm = f"{app_label}.{permission_codename}"
        else:
            full_perm = permission_codename
        
        # 使用guardian检查对象级权限
        user_perms = get_perms(self.user, obj)
        return full_perm in user_perms or permission_codename in user_perms
    
    def get_accessible_objects(self, model_class, permission_codename, app_label=None):
        """获取用户有权限访问的对象列表"""
        if self.user.is_superuser:
            return model_class.objects.all()
        
        # 构建完整的权限名称
        if app_label:
            full_perm = f"{app_label}.{permission_codename}"
        else:
            full_perm = permission_codename
        
        return get_objects_for_user(self.user, full_perm, model_class)
    
    def can_access_admin(self):
        """检查用户是否可以访问Django Admin"""
        if self.user.is_superuser or self.user.is_staff:
            return True
        
        # 检查角色是否有admin相关权限
        admin_permissions = [
            'auth.view_user',
            'auth.add_user', 
            'auth.change_user',
            'auth.delete_user',
        ]
        
        return any(self.has_permission(perm.split('.')[1], perm.split('.')[0]) 
                  for perm in admin_permissions)
    
    def get_role_hierarchy(self):
        """获取角色层级信息"""
        role_mgmt = self.role_management
        if not role_mgmt:
            return []
        
        hierarchy = []
        current = role_mgmt
        
        while current:
            hierarchy.append({
                'role': getattr(current, 'role', ''),
                'display_name': getattr(current, 'display_name', ''),
                'level': getattr(current, 'get_hierarchy_level', lambda: 0)()
            })
            current = getattr(current, 'parent', None)
        
        return hierarchy


class PermissionUtils:
    """
    权限工具类
    """
    
    @staticmethod
    def sync_role_permissions(role_management):
        """同步角色权限到Django组"""
        
        if not RoleGroupMapping or not role_management:
            return False
            
        try:
            # 获取对应的Django组
            mapping = RoleGroupMapping.objects.get(role=getattr(role_management, 'role', None))
            group = mapping.group
            
            # 清除现有权限
            group.permissions.clear()
            
            # 添加所有权限（包括继承的）
            all_permissions = getattr(role_management, 'get_all_permissions', lambda: [])()
            group.permissions.set(all_permissions)
            
            logger.info(f"Synced {len(all_permissions)} permissions for role {getattr(role_management, 'role', 'unknown')}")
            return True
            
        except (RoleGroupMapping.DoesNotExist, AttributeError):
            logger.warning(f"No group mapping found for role {getattr(role_management, 'role', 'unknown')}")
            return False
    
    @staticmethod
    def create_custom_permission(codename, name, content_type):
        """创建自定义权限"""
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={'name': name}
        )
        return permission, created
    
    @staticmethod
    def assign_object_permission(user, permission, obj):
        """为用户分配对象级权限"""
        from guardian.shortcuts import assign_perm
        assign_perm(permission, user, obj)
    
    @staticmethod
    def remove_object_permission(user, permission, obj):
        """移除用户的对象级权限"""
        from guardian.shortcuts import remove_perm
        remove_perm(permission, user, obj)


def get_user_permissions(user):
    """获取用户的所有权限"""
    if user.is_superuser:
        return Permission.objects.all()
    
    checker = RolePermissionChecker(user)
    return checker.all_permissions


def get_user_role(user):
    """获取用户的角色"""
    if hasattr(user, 'role'):
        return user.role
    return None


def get_client_ip(request):
    """获取客户端真实IP地址"""
    # 优先从代理头获取真实IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For可能包含多个IP，取第一个
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # 从其他代理头获取
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    
    # 从Cloudflare获取
    cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_connecting_ip:
        return cf_connecting_ip.strip()
    
    # 最后使用REMOTE_ADDR
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def get_user_agent_info(request):
    """解析用户代理信息"""
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    
    try:
        # 简单解析浏览器信息
        browser = 'Unknown'
        os = 'Unknown'
        
        if 'Chrome' in user_agent_string:
            browser = 'Chrome'
        elif 'Firefox' in user_agent_string:
            browser = 'Firefox'
        elif 'Safari' in user_agent_string:
            browser = 'Safari'
        elif 'Edge' in user_agent_string:
            browser = 'Edge'
        
        if 'Windows' in user_agent_string:
            os = 'Windows'
        elif 'Mac' in user_agent_string:
            os = 'macOS'
        elif 'Linux' in user_agent_string:
            os = 'Linux'
        elif 'Android' in user_agent_string:
            os = 'Android'
        elif 'iOS' in user_agent_string:
            os = 'iOS'
        
        return {
            'browser': browser,
            'os': os,
            'raw': user_agent_string
        }
    except Exception:
        return {
            'browser': 'Unknown',
            'os': 'Unknown',
            'raw': user_agent_string
        }