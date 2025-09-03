from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.permissions.models import MenuModuleConfig, MenuValidity, RoleSlotMenuAssignment, RoleManagement
from apps.accounts.models import UserRole
import logging
import json

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
        
        # 获取用户可访问的菜单 - 使用 MenuValidity 和 RoleSlotMenuAssignment
        
        try:
            role_management = RoleManagement.objects.get(role_name=user_role)
        except RoleManagement.DoesNotExist:
            return Response({
                'success': False,
                'message': f'角色 {user_role} 未找到',
                'menus': [],
                'user_role': user_role
            })
        
        # 获取角色可访问的菜单
        valid_menus = MenuModuleConfig.objects.filter(
            is_active=True,
            menuvalidity__role=role_management,
            menuvalidity__is_valid=True
        ).order_by('sort_order')
        
        menu_list = []
        all_permissions = {}
        
        for menu in valid_menus:
            menu_list.append({
                'key': menu.module_name,
                'name': menu.display_name,
                'menu_level': 1,
                'icon': menu.icon,
                'url': menu.url_pattern,
                'sort_order': menu.sort_order,
                'can_access': True
            })
            all_permissions[menu.module_name] = True
        
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


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_navigation_menus(request):
    """
    获取用户导航菜单数据
    返回适合前端导航栏渲染的菜单结构
    """
    try:
        user = request.user
        
        # 获取用户可访问的菜单
        if user.is_superuser:
            # 超级管理员获取所有活跃菜单
            menus = MenuModuleConfig.objects.filter(is_active=True)
        else:
            # 普通用户根据MenuValidity获取菜单
            user_role = getattr(user, 'role', None)
            if user_role:
                valid_menu_keys = MenuValidity.objects.filter(
                    role=user_role,
                    is_valid=True
                ).values_list('menu_key', flat=True)
                
                menus = MenuModuleConfig.objects.filter(
                    key__in=valid_menu_keys,
                    is_active=True
                )
            else:
                menus = MenuModuleConfig.objects.none()
        
        # 按菜单级别分组并构建层级结构
        menu_data = {
            'root_menus': [],
            'level1_menus': [],
            'level2_menus': []
        }
        
        # 分别获取不同级别的菜单
        for menu in menus.order_by('sort_order', 'name'):
            menu_item = {
                'key': menu.key,
                'name': menu.name,
                'icon': menu.icon,
                'url': menu.url,
                'sort_order': menu.sort_order,
                'menu_level': menu.menu_level,
                'description': menu.description
            }
            
            if menu.menu_level == 'root':
                menu_data['root_menus'].append(menu_item)
            elif menu.menu_level == 'level1':
                menu_data['level1_menus'].append(menu_item)
            elif menu.menu_level == 'level2':
                menu_data['level2_menus'].append(menu_item)
        
        # 构建导航栏结构
        navigation_structure = _build_navigation_structure(menu_data)
        
        return Response({
            'success': True,
            'data': {
                'navigation': navigation_structure,
                'user_info': {
                    'username': user.username,
                    'is_authenticated': True,
                    'is_superuser': user.is_superuser,
                    'role': getattr(user, 'role', None)
                }
            },
            'message': '菜单数据获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取用户导航菜单失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': '获取菜单数据失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _build_navigation_structure(menu_data):
    """
    构建导航栏结构
    将菜单数据转换为适合前端渲染的导航结构
    """
    navigation = {
        'main_nav': [],
        'user_nav': []
    }
    
    # 根据菜单key映射到导航结构
    menu_mapping = {
        # 主导航菜单
        'teaching': {
            'name': '教学中心',
            'icon': 'fas fa-chalkboard-teacher',
            'type': 'dropdown',
            'children': []
        },
        'words': {
            'name': '词汇管理', 
            'icon': 'fas fa-book',
            'type': 'dropdown',
            'children': []
        },
        'reports': {
            'name': '报告中心',
            'icon': 'fas fa-chart-bar',
            'type': 'link',
            'url': '/reports/'
        }
    }
    
    # 处理一级菜单
    for menu in menu_data['level1_menus']:
        if menu['key'] in menu_mapping:
            nav_item = menu_mapping[menu['key']].copy()
            nav_item.update({
                'key': menu['key'],
                'url': menu['url']
            })
            
            # 查找对应的二级菜单
            children = []
            for submenu in menu_data['level2_menus']:
                # 根据命名约定匹配二级菜单
                if submenu['key'].startswith(menu['key']):
                    children.append({
                        'name': submenu['name'],
                        'icon': submenu['icon'],
                        'url': submenu['url'],
                        'key': submenu['key']
                    })
            
            if nav_item['type'] == 'dropdown':
                nav_item['children'] = sorted(children, key=lambda x: x.get('sort_order', 0))
            
            navigation['main_nav'].append(nav_item)
    
    # 用户导航菜单（固定结构）
    navigation['user_nav'] = [
        {
            'name': '个人资料',
            'icon': 'fas fa-user-edit',
            'url': '/accounts/profile/'
        },
        {
            'name': '设置',
            'icon': 'fas fa-cog', 
            'url': '/accounts/settings/'
        },
        {
            'type': 'divider'
        },
        {
            'name': '退出登录',
            'icon': 'fas fa-sign-out-alt',
            'url': '/accounts/logout/'
        }
    ]
    
    return navigation


@api_view(['GET'])
@permission_classes([])
def get_public_navigation(request):
    """
    获取公共导航菜单（未登录用户）
    """
    try:
        navigation = {
            'main_nav': [
                {
                    'name': '首页',
                    'icon': 'fas fa-home',
                    'url': '/',
                    'type': 'link'
                }
            ],
            'auth_nav': [
                {
                    'name': '登录',
                    'icon': 'fas fa-sign-in-alt',
                    'url': '/accounts/login/'
                },
                {
                    'name': '注册',
                    'icon': 'fas fa-user-plus',
                    'url': '/accounts/register/'
                }
            ]
        }
        
        return Response({
            'success': True,
            'data': {
                'navigation': navigation,
                'user_info': {
                    'is_authenticated': False
                }
            },
            'message': '公共菜单数据获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取公共导航菜单失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': '获取公共菜单数据失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["GET"])
def get_menu_config_json(request):
    """
    获取菜单配置的JSON格式数据
    用于前端JavaScript直接调用
    """
    try:
        if request.user.is_authenticated:
            # 调用认证用户的菜单API
            from django.test import RequestFactory
            factory = RequestFactory()
            api_request = factory.get('/api/navigation-menus/')
            api_request.user = request.user
            
            response = get_user_navigation_menus(api_request)
            return JsonResponse(response.data)
        else:
            # 调用公共菜单API
            response = get_public_navigation(request)
            return JsonResponse(response.data)
            
    except Exception as e:
        logger.error(f"获取菜单配置JSON失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': '获取菜单配置失败'
        }, status=500)


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
        
        # 使用 MenuValidity 检查权限
        
        try:
            role_management = RoleManagement.objects.get(role_name=user_role)
            has_permission = MenuValidity.objects.filter(
                menu=menu,
                role=role_management,
                is_valid=True
            ).exists()
        except RoleManagement.DoesNotExist:
            has_permission = False
        
        return Response({
            'success': True,
            'has_permission': has_permission,
            'menu_key': menu_key,
            'menu_name': menu.display_name
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
            # 检查权限 - 使用 MenuValidity
            has_permission = True  # 默认为True，超级管理员或未设置角色时
            if user_role and not user.is_superuser:
                try:
                    role_management = RoleManagement.objects.get(role_name=user_role)
                    has_permission = MenuValidity.objects.filter(
                        menu=menu,
                        role=role_management,
                        is_valid=True
                    ).exists()
                except RoleManagement.DoesNotExist:
                    has_permission = False
            
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