# -*- coding: utf-8 -*-
"""
统一权限检查API视图
整合所有权限检查相关的API接口，提供统一的权限验证服务
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction
import logging

from apps.accounts.models import UserRole
from apps.permissions.optimized_permissions import (
    LEARNING_GOALS_PERMISSIONS,
    LEARNING_PLANS_PERMISSIONS,
    MENU_PERMISSIONS,
    has_learning_goal_permission,
    has_learning_plan_permission,
    has_menu_permission
)

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_permission_check(request):
    """
    统一权限检查接口
    支持菜单权限、学习目标权限、学习计划权限等多种权限类型的检查
    """
    try:
        permission_type = request.data.get('permission_type')
        permission_key = request.data.get('permission_key')
        action = request.data.get('action', 'view')
        context = request.data.get('context', {})
        
        user = request.user
        user_role = getattr(user, 'role', None)
        
        if not permission_type or not permission_key:
            return Response({
                'success': False,
                'error': '缺少必要参数：permission_type 和 permission_key'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        has_permission = False
        
        # 根据权限类型进行检查
        if permission_type == 'menu':
            has_permission = has_menu_permission(user_role, permission_key, action)
        elif permission_type == 'learning_goal':
            has_permission = has_learning_goal_permission(user_role, action, context)
        elif permission_type == 'learning_plan':
            has_permission = has_learning_plan_permission(user_role, action, context)
        else:
            return Response({
                'success': False,
                'error': f'不支持的权限类型：{permission_type}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'has_permission': has_permission,
            'permission_type': permission_type,
            'permission_key': permission_key,
            'action': action,
            'user_role': user_role
        })
        
    except Exception as e:
        logger.error(f"统一权限检查失败: {str(e)}")
        return Response({
            'success': False,
            'error': '权限检查失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_menu_permission(request):
    """
    检查菜单权限
    """
    try:
        menu_key = request.GET.get('menu_key')
        action = request.GET.get('action', 'view')
        
        if not menu_key:
            return Response({
                'success': False,
                'error': '缺少菜单键值'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user_role = getattr(user, 'role', None)
        
        has_permission = has_menu_permission(user_role, menu_key, action)
        
        return Response({
            'success': True,
            'has_permission': has_permission,
            'menu_key': menu_key,
            'action': action,
            'user_role': user_role
        })
        
    except Exception as e:
        logger.error(f"菜单权限检查失败: {str(e)}")
        return Response({
            'success': False,
            'error': '菜单权限检查失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_permissions(request):
    """
    获取用户权限信息
    """
    try:
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # 获取菜单权限
        menu_permissions = {}
        for menu_key in MENU_PERMISSIONS.keys():
            menu_permissions[menu_key] = has_menu_permission(user_role, menu_key, 'view')
        
        # 获取学习目标权限
        learning_goal_permissions = {}
        if user_role and user_role in LEARNING_GOALS_PERMISSIONS:
            learning_goal_permissions = LEARNING_GOALS_PERMISSIONS[user_role]
        
        # 获取学习计划权限
        learning_plan_permissions = {}
        if user_role and user_role in LEARNING_PLANS_PERMISSIONS:
            learning_plan_permissions = LEARNING_PLANS_PERMISSIONS[user_role]
        
        return Response({
            'success': True,
            'user_role': user_role,
            'menu_permissions': menu_permissions,
            'learning_goal_permissions': learning_goal_permissions,
            'learning_plan_permissions': learning_plan_permissions
        })
        
    except Exception as e:
        logger.error(f"获取用户权限失败: {str(e)}")
        return Response({
            'success': False,
            'error': '获取用户权限失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_permission_check(request):
    """
    批量权限检查
    """
    try:
        permissions = request.data.get('permissions', [])
        
        if not permissions:
            return Response({
                'success': False,
                'error': '缺少权限检查列表'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user_role = getattr(user, 'role', None)
        
        results = []
        
        for perm in permissions:
            permission_type = perm.get('permission_type')
            permission_key = perm.get('permission_key')
            action = perm.get('action', 'view')
            context = perm.get('context', {})
            
            has_permission = False
            
            if permission_type == 'menu':
                has_permission = has_menu_permission(user_role, permission_key, action)
            elif permission_type == 'learning_goal':
                has_permission = has_learning_goal_permission(user_role, action, context)
            elif permission_type == 'learning_plan':
                has_permission = has_learning_plan_permission(user_role, action, context)
            
            results.append({
                'permission_type': permission_type,
                'permission_key': permission_key,
                'action': action,
                'has_permission': has_permission
            })
        
        return Response({
            'success': True,
            'results': results,
            'user_role': user_role
        })
        
    except Exception as e:
        logger.error(f"批量权限检查失败: {str(e)}")
        return Response({
            'success': False,
            'error': '批量权限检查失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_permission_cache(request):
    """
    清除权限缓存
    """
    try:
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # 只有管理员可以清除缓存
        if user_role != UserRole.ADMIN:
            return Response({
                'success': False,
                'error': '权限不足，只有管理员可以清除权限缓存'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 清除权限相关缓存
        cache_keys = [
            'menu_permissions_*',
            'user_permissions_*',
            'role_permissions_*'
        ]
        
        cleared_count = 0
        for pattern in cache_keys:
            keys = cache.keys(pattern)
            if keys:
                cache.delete_many(keys)
                cleared_count += len(keys)
        
        return Response({
            'success': True,
            'message': f'已清除 {cleared_count} 个权限缓存项',
            'cleared_count': cleared_count
        })
        
    except Exception as e:
        logger.error(f"清除权限缓存失败: {str(e)}")
        return Response({
            'success': False,
            'error': '清除权限缓存失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_permission_stats(request):
    """
    获取权限统计信息
    """
    try:
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # 只有管理员可以查看统计信息
        if user_role != UserRole.ADMIN:
            return Response({
                'success': False,
                'error': '权限不足，只有管理员可以查看权限统计'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 统计菜单权限
        total_menus = len(MENU_PERMISSIONS)
        
        # 统计角色权限
        total_roles = len(UserRole.choices)
        
        # 统计学习目标权限
        total_goal_permissions = len(LEARNING_GOALS_PERMISSIONS)
        
        # 统计学习计划权限
        total_plan_permissions = len(LEARNING_PLANS_PERMISSIONS)
        
        return Response({
            'success': True,
            'stats': {
                'total_menus': total_menus,
                'total_roles': total_roles,
                'total_goal_permissions': total_goal_permissions,
                'total_plan_permissions': total_plan_permissions,
                'last_updated': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"获取权限统计失败: {str(e)}")
        return Response({
            'success': False,
            'error': '获取权限统计失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)