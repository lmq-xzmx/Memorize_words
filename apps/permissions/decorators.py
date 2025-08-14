# -*- coding: utf-8 -*-
"""
权限验证装饰器
提供统一的后端权限验证装饰器
"""

from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import View
from .permission_checker import PermissionChecker
import logging

logger = logging.getLogger(__name__)

def require_permission(menu_key=None, action=None, resource_type=None, 
                      redirect_url=None, ajax_response=False):
    """
    权限验证装饰器
    
    Args:
        menu_key: 菜单标识
        action: 操作类型 (view, create, edit, delete等)
        resource_type: 资源类型 (learning_goal, learning_plan等)
        redirect_url: 权限不足时的重定向URL
        ajax_response: 是否返回JSON响应
    
    Returns:
        装饰器函数
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            checker = PermissionChecker(user)
            
            # 检查菜单访问权限
            if menu_key and not checker.can_access_menu(menu_key):
                logger.warning(f'用户 {user.username} 尝试访问无权限菜单: {menu_key}')
                
                if ajax_response or request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'message': f'您没有权限访问 {menu_key} 菜单',
                        'error_code': 'MENU_ACCESS_DENIED'
                    }, status=403)
                
                messages.error(request, f'您没有权限访问该功能')
                return redirect(redirect_url or '/dashboard/')
            
            # 检查操作权限
            if action and resource_type:
                # 从请求中获取上下文信息
                context = _extract_context_from_request(request, resource_type, *args, **kwargs)
                
                if not checker.has_permission(action, resource_type, context):
                    logger.warning(f'用户 {user.username} 尝试执行无权限操作: {action} on {resource_type}')
                    
                    if ajax_response or request.headers.get('Content-Type') == 'application/json':
                        return JsonResponse({
                            'success': False,
                            'message': f'您没有权限执行 {action} 操作',
                            'error_code': 'ACTION_PERMISSION_DENIED'
                        }, status=403)
                    
                    messages.error(request, '您没有权限执行该操作')
                    return redirect(redirect_url or '/dashboard/')
            
            # 将权限检查器添加到请求中，供视图使用
            request.permission_checker = checker
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator

def require_menu_access(menu_key, redirect_url=None, ajax_response=False):
    """
    菜单访问权限装饰器
    
    Args:
        menu_key: 菜单标识
        redirect_url: 权限不足时的重定向URL
        ajax_response: 是否返回JSON响应
    
    Returns:
        装饰器函数
    """
    return require_permission(menu_key=menu_key, redirect_url=redirect_url, ajax_response=ajax_response)

def require_learning_goal_permission(action, redirect_url=None, ajax_response=False):
    """
    学习目标权限装饰器
    
    Args:
        action: 操作类型 (view, create, edit, delete等)
        redirect_url: 权限不足时的重定向URL
        ajax_response: 是否返回JSON响应
    
    Returns:
        装饰器函数
    """
    return require_permission(
        menu_key='learning_goals',
        action=action,
        resource_type='learning_goal',
        redirect_url=redirect_url,
        ajax_response=ajax_response
    )

def require_learning_plan_permission(action, redirect_url=None, ajax_response=False):
    """
    学习计划权限装饰器
    
    Args:
        action: 操作类型 (view, create, edit, delete等)
        redirect_url: 权限不足时的重定向URL
        ajax_response: 是否返回JSON响应
    
    Returns:
        装饰器函数
    """
    return require_permission(
        menu_key='learning_plans',
        action=action,
        resource_type='learning_plan',
        redirect_url=redirect_url,
        ajax_response=ajax_response
    )

def require_role(*allowed_roles, redirect_url=None, ajax_response=False):
    """
    角色权限装饰器
    
    Args:
        allowed_roles: 允许的角色列表
        redirect_url: 权限不足时的重定向URL
        ajax_response: 是否返回JSON响应
    
    Returns:
        装饰器函数
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            user_role = getattr(user, 'role', None)
            
            if not user_role or user_role not in allowed_roles:
                logger.warning(f'用户 {user.username} (角色: {user_role}) 尝试访问需要角色 {allowed_roles} 的功能')
                
                if ajax_response or request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'message': '您的角色权限不足',
                        'error_code': 'ROLE_PERMISSION_DENIED'
                    }, status=403)
                
                messages.error(request, '您的角色权限不足')
                return redirect(redirect_url or '/dashboard/')
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator

def _extract_context_from_request(request, resource_type, *args, **kwargs):
    """
    从请求中提取上下文信息
    
    Args:
        request: HTTP请求对象
        resource_type: 资源类型
        args: 位置参数
        kwargs: 关键字参数
    
    Returns:
        dict: 上下文信息
    """
    context = {}
    
    # 从URL参数中获取资源ID
    resource_id = kwargs.get('pk') or kwargs.get('id')
    
    if resource_type == 'learning_goal' and resource_id:
        try:
            from django.apps import apps
            LearningGoal = apps.get_model('teaching', 'LearningGoal')
            goal = LearningGoal.objects.get(id=resource_id)
            context.update({
                'is_own_created': goal.user_id == request.user.id,
                'is_own_goal': goal.user_id == request.user.id,
                'is_personal_goal': goal.goal_type in ['vocabulary', 'reading', 'listening', 'speaking', 'writing'],
                'is_own_personal_goal': goal.user_id == request.user.id and goal.goal_type in ['vocabulary', 'reading', 'listening', 'speaking', 'writing'],
                'is_class_goal': goal.goal_type in ['vocabulary_list', 'word_set', 'grade_level'],
            })
        except Exception as e:
            logger.error(f'获取学习目标上下文失败: {e}')
    
    elif resource_type == 'learning_plan' and resource_id:
        try:
            from django.apps import apps
            LearningPlan = apps.get_model('teaching', 'LearningPlan')
            plan = LearningPlan.objects.get(id=resource_id)
            context.update({
                'is_own_plan': plan.user_id == request.user.id,
                'is_personal_plan': plan.plan_type in ['daily', 'weekly', 'custom'],
                'is_own_personal_plan': plan.user_id == request.user.id and plan.plan_type in ['daily', 'weekly', 'custom'],
                'is_student_plan': hasattr(plan.user, 'role') and plan.user.role == 'student',
            })
        except Exception as e:
            logger.error(f'获取学习计划上下文失败: {e}')
    
    return context

# 类装饰器版本
class PermissionRequiredMixin(View):
    """
    权限验证混入类，用于基于类的视图
    """
    menu_key = None
    action = None
    resource_type = None
    redirect_url = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        
        checker = PermissionChecker(request.user)
        
        # 检查菜单访问权限
        if self.menu_key and not checker.can_access_menu(self.menu_key):
            messages.error(request, '您没有权限访问该功能')
            return redirect(self.redirect_url or '/dashboard/')
        
        # 检查操作权限
        if self.action and self.resource_type:
            context = _extract_context_from_request(request, self.resource_type, *args, **kwargs)
            
            if not checker.has_permission(self.action, self.resource_type, context):
                messages.error(request, '您没有权限执行该操作')
                return redirect(self.redirect_url or '/dashboard/')
        
        # 将权限检查器添加到请求中
        request.permission_checker = checker
        
        return super().dispatch(request, *args, **kwargs)

class LearningGoalPermissionMixin(PermissionRequiredMixin):
    """
    学习目标权限混入类
    """
    menu_key = 'learning_goals'
    resource_type = 'learning_goal'

class LearningPlanPermissionMixin(PermissionRequiredMixin):
    """
    学习计划权限混入类
    """
    menu_key = 'learning_plans'
    resource_type = 'learning_plan'