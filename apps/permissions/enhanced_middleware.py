# -*- coding: utf-8 -*-
"""
增强的权限中间件
提供页面级和功能级权限控制
"""

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from .permission_checker import PermissionChecker
from .models import MenuModuleConfig
import logging
import re

logger = logging.getLogger(__name__)


class EnhancedPermissionMiddleware(MiddlewareMixin):
    """
    增强的权限中间件
    提供基于URL模式的权限检查
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
        
        # 不需要权限检查的路径
        self.exempt_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/admin/login/',
            '/admin/logout/',
            '/static/',
            '/media/',
            '/api/auth/',
            '/permissions/api/public-navigation/',
            '/permissions/api/menu-config/',
        ]
        
        # 需要登录但不需要特殊权限的路径
        self.login_required_paths = [
            '/dashboard/',
            '/profile/',
            '/settings/',
        ]
        
        # URL模式到菜单权限的映射
        self.url_menu_mapping = {
            r'^/teaching/': 'teaching_center',
            r'^/words/': 'vocabulary_management', 
            r'^/reports/': 'report_center',
            r'^/learning-goals/': 'learning_goals',
            r'^/learning-plans/': 'learning_plans',
            r'^/admin/': 'admin_panel',
        }
        
        # URL模式到操作权限的映射
        self.url_action_mapping = {
            r'^/teaching/goals/create/': {'action': 'create', 'resource_type': 'learning_goal'},
            r'^/teaching/goals/\d+/edit/': {'action': 'edit', 'resource_type': 'learning_goal'},
            r'^/teaching/goals/\d+/delete/': {'action': 'delete', 'resource_type': 'learning_goal'},
            r'^/teaching/plans/create/': {'action': 'create', 'resource_type': 'learning_plan'},
            r'^/teaching/plans/\d+/edit/': {'action': 'edit', 'resource_type': 'learning_plan'},
            r'^/teaching/plans/\d+/delete/': {'action': 'delete', 'resource_type': 'learning_plan'},
            r'^/words/create/': {'action': 'create', 'resource_type': 'vocabulary'},
            r'^/words/\d+/edit/': {'action': 'edit', 'resource_type': 'vocabulary'},
            r'^/words/\d+/delete/': {'action': 'delete', 'resource_type': 'vocabulary'},
        }
    
    def process_request(self, request):
        """
        处理请求前的权限检查
        """
        # 跳过不需要检查的路径
        if self.should_exempt(request):
            return None
        
        # API请求由DRF处理
        if request.path.startswith('/api/') or request.path.startswith('/permissions/api/'):
            return None
        
        # 检查用户是否已登录
        if isinstance(request.user, AnonymousUser):
            if self.requires_login(request):
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'message': '请先登录',
                        'error_code': 'LOGIN_REQUIRED'
                    }, status=401)
                return redirect('accounts:login')
            return None
        
        # 执行权限检查
        permission_result = self.check_permissions(request)
        if permission_result:
            return permission_result
        
        return None
    
    def should_exempt(self, request):
        """
        检查是否应该跳过权限检查
        """
        path = request.path
        
        # 检查豁免路径
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        
        # 检查WebSocket请求
        if request.META.get('HTTP_UPGRADE') == 'websocket':
            return True
        
        return False
    
    def requires_login(self, request):
        """
        检查是否需要登录
        """
        path = request.path
        
        # 检查需要登录的路径
        for login_path in self.login_required_paths:
            if path.startswith(login_path):
                return True
        
        # 检查是否匹配需要权限的URL模式
        for pattern in self.url_menu_mapping.keys():
            if re.match(pattern, path):
                return True
        
        for pattern in self.url_action_mapping.keys():
            if re.match(pattern, path):
                return True
        
        return False
    
    def check_permissions(self, request):
        """
        执行权限检查
        """
        path = request.path
        user = request.user
        
        try:
            checker = PermissionChecker(user)
            
            # 检查菜单权限
            menu_key = self.get_menu_key_for_path(path)
            if menu_key and not checker.can_access_menu(menu_key):
                logger.warning(f'用户 {user.username} 尝试访问无权限菜单: {menu_key} (路径: {path})')
                return self.handle_permission_denied(request, f'您没有权限访问该功能')
            
            # 检查操作权限
            action_config = self.get_action_config_for_path(path)
            if action_config:
                context = self.extract_context_from_request(request, action_config['resource_type'])
                if not checker.has_permission(action_config['action'], action_config['resource_type'], context):
                    logger.warning(f'用户 {user.username} 尝试执行无权限操作: {action_config["action"]} on {action_config["resource_type"]} (路径: {path})')
                    return self.handle_permission_denied(request, f'您没有权限执行该操作')
            
            # 将权限检查器添加到请求中
            request.permission_checker = checker
            
        except Exception as e:
            logger.error(f'权限检查时出错: {e}')
            return self.handle_permission_denied(request, '权限检查失败')
        
        return None
    
    def get_menu_key_for_path(self, path):
        """
        根据路径获取菜单键
        """
        for pattern, menu_key in self.url_menu_mapping.items():
            if re.match(pattern, path):
                return menu_key
        return None
    
    def get_action_config_for_path(self, path):
        """
        根据路径获取操作配置
        """
        for pattern, config in self.url_action_mapping.items():
            if re.match(pattern, path):
                return config
        return None
    
    def extract_context_from_request(self, request, resource_type):
        """
        从请求中提取上下文信息
        """
        context = {
            'user_id': request.user.id,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        # 从URL中提取资源ID
        try:
            resolved = resolve(request.path)
            if 'pk' in resolved.kwargs:
                context['resource_id'] = resolved.kwargs['pk']
            elif 'id' in resolved.kwargs:
                context['resource_id'] = resolved.kwargs['id']
        except Exception:
            pass
        
        # 从POST数据中提取相关信息
        if request.method == 'POST':
            if resource_type == 'learning_goal':
                context['goal_type'] = request.POST.get('goal_type')
                context['difficulty_level'] = request.POST.get('difficulty_level')
            elif resource_type == 'learning_plan':
                context['plan_type'] = request.POST.get('plan_type')
                context['target_audience'] = request.POST.get('target_audience')
        
        return context
    
    def handle_permission_denied(self, request, message):
        """
        处理权限拒绝
        """
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'message': message,
                'error_code': 'PERMISSION_DENIED'
            }, status=403)
        
        messages.error(request, message)
        return redirect('/dashboard/')
    
    def get_client_ip(self, request):
        """
        获取客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PermissionContextMiddleware(MiddlewareMixin):
    """
    权限上下文中间件
    为模板提供权限相关的上下文变量
    """
    
    def process_template_response(self, request, response):
        """
        在模板渲染前添加权限上下文
        """
        if hasattr(response, 'context_data') and response.context_data is not None:
            if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                try:
                    checker = getattr(request, 'permission_checker', None)
                    if not checker:
                        checker = PermissionChecker(request.user)
                    
                    # 添加权限相关的上下文
                    response.context_data.update({
                        'user_permissions': {
                            'can_access_teaching': checker.can_access_menu('teaching_center'),
                            'can_access_vocabulary': checker.can_access_menu('vocabulary_management'),
                            'can_access_reports': checker.can_access_menu('report_center'),
                            'can_create_goals': checker.has_permission('create', 'learning_goal', {}),
                            'can_create_plans': checker.has_permission('create', 'learning_plan', {}),
                            'can_manage_users': checker.can_access_menu('user_management'),
                            'is_admin': request.user.is_superuser or checker.can_access_menu('admin_panel'),
                        },
                        'permission_checker': checker,
                    })
                except Exception as e:
                    logger.error(f'添加权限上下文时出错: {e}')
        
        return response