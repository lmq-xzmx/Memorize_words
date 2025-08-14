# -*- coding: utf-8 -*-
"""
统一权限检查器
提供统一的权限检查接口，减少代码冗余
"""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.apps import apps
from .optimized_permissions import (
    has_learning_goal_permission,
    has_learning_plan_permission,
    has_menu_permission,
    get_menu_actions,
    LEARNING_GOALS_PERMISSIONS,
    LEARNING_PLANS_PERMISSIONS,
    MENU_PERMISSIONS
)
from apps.accounts.models import UserRole
import logging

# 延迟导入模型以避免循环导入
def get_menu_module_model():
    return apps.get_model('permissions', 'MenuModuleConfig')

def get_role_menu_permission_model():
    return apps.get_model('permissions', 'RoleMenuPermission')

User = get_user_model()
logger = logging.getLogger(__name__)

class PermissionChecker:
    """
    统一权限检查器类
    提供各种权限检查方法，支持缓存优化
    """
    
    def __init__(self, user=None):
        self.user = user
        self.user_role = getattr(user, 'role', None) if user else None
        self._cache_prefix = f'perm_{user.id}' if user and user.id else 'perm_anonymous'
    
    def can_access_menu(self, menu_key):
        """
        检查用户是否可以访问指定菜单
        
        Args:
            menu_key: 菜单标识
        
        Returns:
            bool: 是否可以访问
        """
        if not self.user or not self.user.is_authenticated:
            return False
        
        # 超级管理员拥有所有权限
        if getattr(self.user, 'is_superuser', False):
            return True
        
        # 检查缓存
        cache_key = f'{self._cache_prefix}_menu_{menu_key}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # 使用优化后的菜单权限配置
            if menu_key in MENU_PERMISSIONS and self.user_role:
                menu_perms = MENU_PERMISSIONS[menu_key]
                permission = menu_perms.get(self.user_role, False)
                
                # 缓存结果（5分钟）
                cache.set(cache_key, permission, 300)
                return permission
            
            # 如果菜单不在配置中，回退到数据库查询
            MenuModuleConfig = get_menu_module_model()
            RoleMenuPermission = get_role_menu_permission_model()
            
            menu = MenuModuleConfig.objects.get(key=menu_key, is_active=True)
            
            # 检查角色权限
            if self.user_role:
                permission = RoleMenuPermission.objects.filter(
                    role=self.user_role,
                    menu_module=menu,
                    can_access=True
                ).exists()
                
                # 缓存结果（5分钟）
                cache.set(cache_key, permission, 300)
                return permission
        
        except Exception as e:
            if 'DoesNotExist' in str(type(e)):
                logger.warning(f'菜单不存在: {menu_key}')
            else:
                logger.error(f'检查菜单权限失败: {e}')
        
        # 默认拒绝访问
        cache.set(cache_key, False, 300)
        return False
    
    def has_permission(self, permission_type, resource_type=None, context=None):
        """
        检查用户是否具有指定权限
        
        Args:
            permission_type: 权限类型 (view, create, edit, delete等)
            resource_type: 资源类型 (learning_goal, learning_plan等)
            context: 上下文信息
        
        Returns:
            bool: 是否有权限
        """
        if not self.user or not self.user.is_authenticated:
            return False
        
        # 超级管理员拥有所有权限
        if getattr(self.user, 'is_superuser', False):
            return True
        
        if not self.user_role:
            return False
        
        # 根据资源类型调用相应的权限检查函数
        if resource_type == 'learning_goal':
            return has_learning_goal_permission(self.user_role, permission_type, context)
        elif resource_type == 'learning_plan':
            return has_learning_plan_permission(self.user_role, permission_type, context)
        else:
            # 通用权限检查（可扩展）
            return self._check_generic_permission(permission_type, context)
    
    def get_menu_actions(self, menu_key):
        """
        获取用户在指定菜单下的可用操作列表
        
        Args:
            menu_key: 菜单标识
        
        Returns:
            list: 可用操作列表
        """
        if not self.user or not self.user.is_authenticated:
            return []
        
        # 超级管理员拥有所有权限
        if getattr(self.user, 'is_superuser', False):
            return ['view', 'create', 'edit', 'delete', 'manage', 'approve', 'export', 'analyze']
        
        if not self.user_role:
            return []
        
        # 检查缓存
        cache_key = f'{self._cache_prefix}_actions_{menu_key}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        actions = get_menu_actions(self.user_role, menu_key)
        
        # 缓存结果（5分钟）
        cache.set(cache_key, actions, 300)
        return actions
    
    def can_manage_learning_goals(self, goal=None):
        """
        检查是否可以管理学习目标
        
        Args:
            goal: 学习目标对象（可选）
        
        Returns:
            bool: 是否可以管理
        """
        if not self.user or not self.user_role:
            return False
        
        # 构建上下文
        context = {}
        if goal:
            context.update({
                'is_own_created': goal.user_id == self.user.id,
                'is_own_goal': goal.user_id == self.user.id,
                'is_personal_goal': goal.goal_type in ['vocabulary', 'reading', 'listening', 'speaking', 'writing'],
                'is_own_personal_goal': goal.user_id == self.user.id and goal.goal_type in ['vocabulary', 'reading', 'listening', 'speaking', 'writing'],
                'is_class_goal': goal.goal_type in ['vocabulary_list', 'word_set', 'grade_level'],
                # 可以根据需要添加更多上下文信息
            })
        
        return self.has_permission('edit', 'learning_goal', context)
    
    def can_manage_learning_plans(self, plan=None):
        """
        检查是否可以管理学习计划
        
        Args:
            plan: 学习计划对象（可选）
        
        Returns:
            bool: 是否可以管理
        """
        if not self.user or not self.user_role:
            return False
        
        # 构建上下文
        context = {}
        if plan:
            context.update({
                'is_own_plan': plan.user_id == self.user.id,
                'is_personal_plan': plan.plan_type in ['daily', 'weekly', 'custom'],
                'is_own_personal_plan': plan.user_id == self.user.id and plan.plan_type in ['daily', 'weekly', 'custom'],
                'is_student_plan': hasattr(plan.user, 'role') and plan.user.role == UserRole.STUDENT,
                # 可以根据需要添加更多上下文信息
            })
        
        return self.has_permission('edit', 'learning_plan', context)
    
    def get_accessible_menus(self):
        """
        获取用户可访问的菜单列表
        
        Returns:
            list: 可访问的菜单列表
        """
        if not self.user or not self.user.is_authenticated:
            return []
        
        # 获取模型类
        MenuModuleConfig = get_menu_module_model()
        RoleMenuPermission = get_role_menu_permission_model()
        
        # 超级管理员可以访问所有菜单
        if getattr(self.user, 'is_superuser', False):
            return list(MenuModuleConfig.objects.filter(is_active=True).values_list('key', flat=True))
        
        # 检查缓存
        cache_key = f'{self._cache_prefix}_accessible_menus'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        accessible_menus = []
        
        if self.user_role:
            # 获取用户角色可访问的菜单
            permissions = RoleMenuPermission.objects.filter(
                role=self.user_role,
                can_access=True,
                menu_module__is_active=True
            ).select_related('menu_module')
            
            accessible_menus = [perm.menu_module.key for perm in permissions]
        
        # 缓存结果（10分钟）
        cache.set(cache_key, accessible_menus, 600)
        return accessible_menus
    
    def _check_generic_permission(self, permission_type, context=None):
        """
        通用权限检查（可扩展）
        
        Args:
            permission_type: 权限类型
            context: 上下文信息
        
        Returns:
            bool: 是否有权限
        """
        # 这里可以实现通用的权限检查逻辑
        # 目前返回False，可以根据需要扩展
        return False
    
    def clear_cache(self):
        """
        清除用户权限缓存
        """
        if self.user and self.user.id:
            cache_pattern = f'{self._cache_prefix}_*'
            # 注意：这里需要根据缓存后端实现来清除匹配的缓存键
            # 简单实现：清除常用的缓存键
            common_keys = [
                f'{self._cache_prefix}_accessible_menus',
                f'{self._cache_prefix}_menu_learning_goals',
                f'{self._cache_prefix}_menu_learning_plans',
                f'{self._cache_prefix}_menu_learning_progress',
                f'{self._cache_prefix}_menu_learning_practice',
                f'{self._cache_prefix}_actions_learning_goals',
                f'{self._cache_prefix}_actions_learning_plans',
                f'{self._cache_prefix}_actions_learning_progress',
                f'{self._cache_prefix}_actions_learning_practice',
            ]
            
            for key in common_keys:
                cache.delete(key)

# 便捷函数
def get_permission_checker(user):
    """
    获取权限检查器实例
    
    Args:
        user: 用户对象
    
    Returns:
        PermissionChecker: 权限检查器实例
    """
    return PermissionChecker(user)

def check_user_permission(user, permission_type, resource_type=None, context=None):
    """
    检查用户权限的便捷函数
    
    Args:
        user: 用户对象
        permission_type: 权限类型
        resource_type: 资源类型
        context: 上下文信息
    
    Returns:
        bool: 是否有权限
    """
    checker = PermissionChecker(user)
    return checker.has_permission(permission_type, resource_type, context)

def check_menu_access(user, menu_key):
    """
    检查菜单访问权限的便捷函数
    
    Args:
        user: 用户对象
        menu_key: 菜单标识
    
    Returns:
        bool: 是否可以访问
    """
    checker = PermissionChecker(user)
    return checker.can_access_menu(menu_key)