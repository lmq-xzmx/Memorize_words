# -*- coding: utf-8 -*-
"""
权限模板标签
提供在Django模板中进行权限检查的标签
"""

from django import template
from django.contrib.auth.models import AnonymousUser
from ..permission_checker import PermissionChecker
import logging

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def check_menu_permission(context, menu_key):
    """
    检查用户是否有菜单访问权限
    
    用法：{% check_menu_permission 'learning_goals' as can_access %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return False
    
    try:
        checker = PermissionChecker(request.user)
        return checker.can_access_menu(menu_key)
    except Exception as e:
        logger.error(f"检查菜单权限时出错: {e}")
        return False


@register.simple_tag(takes_context=True)
def has_action_permission(context, action, resource_type, **kwargs):
    """
    检查用户是否有操作权限
    
    用法：{% has_action_permission 'create' 'learning_goal' as can_create %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return False
    
    try:
        checker = PermissionChecker(request.user)
        return checker.has_permission(action, resource_type, kwargs)
    except Exception as e:
        logger.error(f"检查操作权限时出错: {e}")
        return False


class PermissionRequiredNode(template.Node):
    def __init__(self, nodelist, menu_key=None, action=None, resource_type=None):
        self.nodelist = nodelist
        self.menu_key = menu_key
        self.action = action
        self.resource_type = resource_type
    
    def render(self, context):
        request = context.get('request')
        has_permission = False
        
        if request and not isinstance(request.user, AnonymousUser):
            try:
                checker = PermissionChecker(request.user)
                
                # 检查菜单权限
                if self.menu_key:
                    menu_key_value = self.menu_key.resolve(context) if hasattr(self.menu_key, 'resolve') else self.menu_key
                    has_permission = checker.can_access_menu(menu_key_value)
                
                # 检查操作权限
                if has_permission and self.action and self.resource_type:
                    action_value = self.action.resolve(context) if hasattr(self.action, 'resolve') else self.action
                    resource_type_value = self.resource_type.resolve(context) if hasattr(self.resource_type, 'resolve') else self.resource_type
                    has_permission = checker.has_permission(action_value, resource_type_value, {})
                elif self.action and self.resource_type:  # 没有菜单权限检查，只检查操作权限
                    action_value = self.action.resolve(context) if hasattr(self.action, 'resolve') else self.action
                    resource_type_value = self.resource_type.resolve(context) if hasattr(self.resource_type, 'resolve') else self.resource_type
                    has_permission = checker.has_permission(action_value, resource_type_value, {})
                elif self.menu_key:  # 只检查菜单权限
                    menu_key_value = self.menu_key.resolve(context) if hasattr(self.menu_key, 'resolve') else self.menu_key
                    has_permission = checker.can_access_menu(menu_key_value)
                    
            except Exception as e:
                logger.error(f"权限检查时出错: {e}")
                has_permission = False
        
        if has_permission:
            return self.nodelist.render(context)
        return ''


@register.tag
def permission_required(parser, token):
    """
    权限检查块标签
    
    用法：{% permission_required 'menu_key' 'action' %}
          内容只有在有权限时才显示
          {% endpermission_required %}
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("permission_required 标签至少需要一个参数")
    
    menu_key = parser.compile_filter(bits[1]) if len(bits) > 1 else None
    action = parser.compile_filter(bits[2]) if len(bits) > 2 else None
    resource_type = parser.compile_filter(bits[3]) if len(bits) > 3 else None
    
    nodelist = parser.parse(('endpermission_required',))
    parser.delete_first_token()
    
    return PermissionRequiredNode(nodelist, menu_key, action, resource_type)


@register.filter
def can_access_menu(user, menu_key):
    """
    过滤器：检查用户是否可以访问菜单
    
    用法：{{ user|can_access_menu:'learning_goals' }}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    try:
        checker = PermissionChecker(user)
        return checker.can_access_menu(menu_key)
    except Exception as e:
        logger.error(f"检查菜单权限时出错: {e}")
        return False


@register.filter
def has_menu_permission(user, menu_key):
    """
    过滤器：检查用户是否有菜单权限
    
    用法：{{ user|has_menu_permission:'learning_goals' }}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    try:
        checker = PermissionChecker(user)
        return checker.can_access_menu(menu_key)
    except Exception as e:
        logger.error(f"检查菜单权限时出错: {e}")
        return False


@register.filter
def has_permission(user, permission_string):
    """
    过滤器：检查用户是否有指定权限
    
    用法：{{ user|has_permission:'create:learning_goal' }}
    """
    if isinstance(user, AnonymousUser):
        return False
    
    try:
        if ':' in permission_string:
            action, resource_type = permission_string.split(':', 1)
        else:
            # 如果没有冒号，假设是菜单权限
            return can_access_menu(user, permission_string)
        
        checker = PermissionChecker(user)
        return checker.has_permission(action, resource_type, {})
    except Exception as e:
        logger.error(f"检查权限时出错: {e}")
        return False


@register.simple_tag(takes_context=True)
def user_menu_list(context):
    """
    获取用户可访问的菜单列表
    
    用法：{% user_menu_list as menu_list %}
    """
    request = context.get('request')
    if not request or isinstance(request.user, AnonymousUser):
        return []
    
    try:
        checker = PermissionChecker(request.user)
        return checker.get_accessible_menus()
    except Exception as e:
        logger.error(f"获取用户菜单列表时出错: {e}")
        return []


@register.simple_tag(takes_context=True)
def check_multiple_permissions(context, permissions_dict):
    """
    批量检查多个权限
    
    用法：{% check_multiple_permissions permissions_dict as perm_results %}
    其中 permissions_dict 格式为：
    {
        'can_create_goal': {'action': 'create', 'resource_type': 'learning_goal'},
        'can_view_reports': {'menu_key': 'reports'}
    }
    """
    request = context.get('request')
    results = {}
    
    if not request or isinstance(request.user, AnonymousUser):
        return {key: False for key in permissions_dict.keys()}
    
    try:
        checker = PermissionChecker(request.user)
        
        for key, perm_config in permissions_dict.items():
            if 'menu_key' in perm_config:
                results[key] = checker.can_access_menu(perm_config['menu_key'])
            elif 'action' in perm_config and 'resource_type' in perm_config:
                context_data = perm_config.get('context', {})
                results[key] = checker.has_permission(
                    perm_config['action'], 
                    perm_config['resource_type'], 
                    context_data
                )
            else:
                results[key] = False
                
    except Exception as e:
        logger.error(f"批量检查权限时出错: {e}")
        results = {key: False for key in permissions_dict.keys()}
    
    return results


@register.simple_tag
def permission_debug(user, action=None, resource_type=None, menu_key=None):
    """
    权限调试标签，用于开发时调试权限问题
    
    用法：{% permission_debug user action='create' resource_type='learning_goal' %}
    """
    if isinstance(user, AnonymousUser):
        return "用户未登录"
    
    try:
        checker = PermissionChecker(user)
        debug_info = {
            'user': user.username,
            'role': getattr(user, 'role', 'None'),
            'is_superuser': user.is_superuser,
        }
        
        if menu_key:
            debug_info['menu_access'] = checker.can_access_menu(menu_key)
        
        if action and resource_type:
            debug_info['action_permission'] = checker.has_permission(action, resource_type, {})
        
        return debug_info
    except Exception as e:
        return f"调试时出错: {e}"