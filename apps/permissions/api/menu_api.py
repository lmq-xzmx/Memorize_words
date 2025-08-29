from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.permissions.models import MenuModuleConfig
# RoleMenuPermission 模型已废弃，请使用 MenuValidity 和 RoleMenuAssignment 替代
from apps.accounts.models import UserRole
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_menu_permissions(request):
    """
    获取当前用户的菜单权限
    返回用户可访问的菜单列表
    """
    user = request.user
    
    try:
        # 超级管理员获取所有菜单
        if user.is_superuser:
            menus = MenuModuleConfig.objects.filter(is_active=True).order_by('sort_order')
            menu_list = []
            all_permissions = {}
            
            for menu in menus:
                menu_list.append({
                    'key': menu.key,
                    'name': menu.name,
                    'menu_level': menu.menu_level,
                    'icon': menu.icon,
                    'url': menu.url,
                    'sort_order': menu.sort_order,
                    'can_access': True
                })
                # 超级管理员拥有所有权限
                all_permissions[menu.key] = True
            
            return Response({
                'success': True,
                'menus': menu_list,
                'all_permissions': all_permissions,
                'user_role': 'admin',
                'is_superuser': True
            })
        
        # 普通用户根据角色权限获取菜单
        user_role = getattr(user, 'role', None)
        if not user_role:
            return Response({
                'success': False,
                'message': '用户角色未设置',
                'menus': [],
                'user_role': None
            })
        
        # 获取用户可访问的菜单 - 暂时返回所有活跃菜单
        # TODO: 使用 MenuValidity 和 RoleMenuAssignment 替代 RoleMenuPermission
        all_menus = MenuModuleConfig.objects.filter(is_active=True).order_by('sort_order')
        
        menu_list = []
        all_permissions = {}
        
        for menu in all_menus:
            menu_list.append({
                'key': menu.module_name,
                'name': menu.display_name,
                'menu_level': 1,  # 默认级别
                'icon': menu.icon,
                'url': menu.url_pattern,
                'sort_order': menu.sort_order,
                'can_access': True  # 暂时允许所有访问
            })
            all_permissions[menu.module_name] = True  # 暂时允许所有访问
        
        return Response({
            'success': True,
            'menus': menu_list,
            'all_permissions': all_permissions,
            'user_role': user_role,
            'is_superuser': False
        })
        
    except Exception as e:
        logger.error(f"获取用户菜单权限失败: {e}")
        return Response({
            'success': False,
            'message': f'获取菜单权限失败: {str(e)}',
            'menus': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def check_menu_permission(request):
    """
    检查用户对特定菜单的访问权限
    """
    user = request.user
    menu_key = request.data.get('menu_key')
    
    if not menu_key:
        return Response({
            'success': False,
            'message': '菜单标识不能为空'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 超级管理员拥有所有权限
        if user.is_superuser:
            return Response({
                'success': True,
                'has_permission': True,
                'menu_key': menu_key
            })
        
        # 检查菜单是否存在
        try:
            menu = MenuModuleConfig.objects.get(key=menu_key, is_active=True)
        except MenuModuleConfig.DoesNotExist:
            return Response({
                'success': False,
                'message': '菜单不存在或已禁用',
                'has_permission': False
            })
        
        # 检查用户角色权限
        user_role = getattr(user, 'role', None)
        if not user_role:
            return Response({
                'success': False,
                'message': '用户角色未设置',
                'has_permission': False
            })
        
        # TODO: 使用 MenuValidity 和 RoleMenuAssignment 替代 RoleMenuPermission
        # 暂时允许所有访问
        return Response({
            'success': True,
            'has_permission': True,  # 暂时允许所有访问
            'menu_key': menu_key,
            'menu_name': menu.display_name,
            'message': 'RoleMenuPermission已废弃，暂时允许所有访问'
        })
            
    except Exception as e:
        logger.error(f"检查菜单权限失败: {e}")
        return Response({
            'success': False,
            'message': f'检查权限失败: {str(e)}',
            'has_permission': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_role_display_name(request):
    """
    获取角色显示名称
    """
    user = request.user
    user_role = getattr(user, 'role', None)
    
    if not user_role:
        return Response({
            'success': False,
            'message': '用户角色未设置'
        })
    
    # 获取角色显示名称
    role_choices = dict(UserRole.choices)
    role_display_name = role_choices.get(user_role, user_role)
    
    return Response({
        'success': True,
        'role': user_role,
        'role_display_name': role_display_name,
        'is_superuser': user.is_superuser
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_menu_hierarchy(request):
    """
    获取菜单层级结构
    """
    user = request.user
    user_role = getattr(user, 'role', None)
    
    try:
        # 获取所有激活的菜单
        all_menus = MenuModuleConfig.objects.filter(is_active=True).order_by('sort_order')
        
        # 构建层级结构
        menu_hierarchy = {
            'root': [],
            'level1': [],
            'level2': []
        }
        
        for menu in all_menus:
            # 检查权限 - 暂时允许所有访问
            # TODO: 使用 MenuValidity 和 RoleMenuAssignment 替代 RoleMenuPermission
            has_permission = True  # 暂时允许所有访问
            
            menu_data = {
                'key': menu.module_name,
                'name': menu.display_name,
                'icon': menu.icon,
                'url': menu.url_pattern,
                'sort_order': menu.sort_order,
                'has_permission': has_permission,
                'description': menu.description
            }
            
            menu_hierarchy[menu.menu_level].append(menu_data)
        
        return Response({
            'success': True,
            'menu_hierarchy': menu_hierarchy,
            'user_role': user_role
        })
        
    except Exception as e:
        logger.error(f"获取菜单层级失败: {e}")
        return Response({
            'success': False,
            'message': f'获取菜单层级失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)