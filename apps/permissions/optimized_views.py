"""优化后的权限检查视图"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.core.cache import cache
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
import logging

from .permission_checker import get_permission_checker
from .decorators import require_permission, require_menu_access

logger = logging.getLogger(__name__)


class OptimizedPermissionAPIView(View):
    """优化后的权限检查API视图"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """统一的权限检查接口"""
        try:
            data = json.loads(request.body)
            resource_type = data.get('resource_type')
            action = data.get('action')
            context = data.get('context', {})
            
            if not resource_type or not action:
                return JsonResponse({
                    'success': False,
                    'error': '缺少必要参数：resource_type 和 action'
                }, status=400)
            
            checker = get_permission_checker(request.user)
            
            # 根据资源类型进行权限检查
            if resource_type == 'menu':
                menu_id = context.get('menu_id') or action
                has_permission = checker.can_access_menu(menu_id)
            elif resource_type == 'learning_goal':
                has_permission = checker.has_permission('learning_goal', action, context)
            elif resource_type == 'learning_plan':
                has_permission = checker.has_permission('learning_plan', action, context)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'不支持的资源类型：{resource_type}'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'has_permission': has_permission,
                'user_role': request.user.role if hasattr(request.user, 'role') else None
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f'权限检查失败: {e}')
            return JsonResponse({
                'success': False,
                'error': '权限检查失败'
            }, status=500)


@require_http_methods(["GET"])
@login_required
def get_user_permissions(request):
    """获取用户权限信息"""
    try:
        checker = get_permission_checker(request.user)
        
        # 获取用户可访问的菜单
        accessible_menus = checker.get_accessible_menus()
        
        # 获取用户角色
        user_role = request.user.role if hasattr(request.user, 'role') else None
        
        return JsonResponse({
            'success': True,
            'data': {
                'user_id': request.user.id,
                'username': request.user.username,
                'role': user_role,
                'accessible_menus': accessible_menus,
                'permissions': {
                    'learning_goals': {
                        'can_view': checker.has_permission('learning_goal', 'view'),
                        'can_create': checker.has_permission('learning_goal', 'create'),
                        'can_edit': checker.has_permission('learning_goal', 'edit'),
                        'can_delete': checker.has_permission('learning_goal', 'delete')
                    },
                    'learning_plans': {
                        'can_view': checker.has_permission('learning_plan', 'view'),
                        'can_create': checker.has_permission('learning_plan', 'create'),
                        'can_edit': checker.has_permission('learning_plan', 'edit'),
                        'can_delete': checker.has_permission('learning_plan', 'delete')
                    }
                }
            }
        })
        
    except Exception as e:
        logger.error(f'获取用户权限失败: {e}')
        return JsonResponse({
            'success': False,
            'error': '获取权限信息失败'
        }, status=500)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_menu_permissions(request):
    """获取用户菜单权限信息（与前端兼容的接口）"""
    try:
        from .optimized_permissions import MENU_PERMISSIONS
        from django.apps import apps
        
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # 获取所有激活的菜单
        MenuModuleConfig = apps.get_model('permissions', 'MenuModuleConfig')
        menus = MenuModuleConfig.objects.filter(is_active=True).order_by('sort_order')
        
        menu_list = []
        all_permissions = {}
        
        for menu in menus:
            # 检查用户是否有权限访问此菜单
            has_access = False
            if user.is_superuser:
                has_access = True
            elif user_role and menu.key in MENU_PERMISSIONS:
                has_access = MENU_PERMISSIONS[menu.key].get(user_role, False)
            
            if has_access:
                menu_list.append({
                    'id': menu.id,
                    'key': menu.key,
                    'name': menu.name,
                    'menu_level': menu.menu_level,
                    'icon': menu.icon,
                    'url': menu.url,
                    'sort_order': menu.sort_order,
                    'description': menu.description
                })
            
            # 为all_permissions添加所有菜单的权限状态
            all_permissions[menu.key] = has_access
        
        return Response({
            'success': True,
            'data': {
                'menus': menu_list,
                'all_permissions': all_permissions,
                'user_role': user_role,
                'is_superuser': user.is_superuser
            }
        })
        
    except Exception as e:
        logger.error(f'获取用户菜单权限时出错: {e}')
        return Response({
            'success': False,
            'error': '获取菜单权限失败'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def check_menu_permission(request):
    """检查菜单权限"""
    try:
        data = json.loads(request.body)
        menu_id = data.get('menu_id')
        
        if not menu_id:
            return JsonResponse({
                'success': False,
                'error': '缺少menu_id参数'
            }, status=400)
        
        checker = get_permission_checker(request.user)
        has_permission = checker.can_access_menu(menu_id)
        
        return JsonResponse({
            'success': True,
            'has_permission': has_permission,
            'menu_id': menu_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f'菜单权限检查失败: {e}')
        return JsonResponse({
            'success': False,
            'error': '权限检查失败'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def check_learning_goal_permission(request):
    """检查学习目标权限"""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        goal_id = data.get('goal_id')
        context = data.get('context', {})
        
        if not action:
            return JsonResponse({
                'success': False,
                'error': '缺少action参数'
            }, status=400)
        
        # 如果提供了goal_id，获取目标的上下文信息
        if goal_id:
            try:
                from django.apps import apps
                LearningGoal = apps.get_model('teaching', 'LearningGoal')
                goal = LearningGoal.objects.get(id=goal_id)
                context.update({
                    'is_own': goal.user_id == request.user.id,
                    'is_personal': goal.goal_type in ['vocabulary', 'reading', 'listening', 'speaking', 'writing'],
                    'is_class_goal': goal.goal_type in ['vocabulary_list', 'word_set', 'grade_level'],
                })
            except Exception as e:
                logger.warning(f'获取学习目标上下文失败: {e}')
        
        checker = get_permission_checker(request.user)
        has_permission = checker.has_permission('learning_goal', action, context)
        
        return JsonResponse({
            'success': True,
            'has_permission': has_permission,
            'action': action,
            'goal_id': goal_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f'学习目标权限检查失败: {e}')
        return JsonResponse({
            'success': False,
            'error': '权限检查失败'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def check_learning_plan_permission(request):
    """检查学习计划权限"""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        plan_id = data.get('plan_id')
        context = data.get('context', {})
        
        if not action:
            return JsonResponse({
                'success': False,
                'error': '缺少action参数'
            }, status=400)
        
        # 如果提供了plan_id，获取计划的上下文信息
        if plan_id:
            try:
                from django.apps import apps
                LearningPlan = apps.get_model('teaching', 'LearningPlan')
                plan = LearningPlan.objects.get(id=plan_id)
                context.update({
                    'is_own': plan.user_id == request.user.id,
                    'is_personal': plan.plan_type in ['daily', 'weekly', 'custom'],
                    'is_class_plan': plan.plan_type in ['class_daily', 'class_weekly'],
                })
            except Exception as e:
                logger.warning(f'获取学习计划上下文失败: {e}')
        
        checker = get_permission_checker(request.user)
        has_permission = checker.has_permission('learning_plan', action, context)
        
        return JsonResponse({
            'success': True,
            'has_permission': has_permission,
            'action': action,
            'plan_id': plan_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f'学习计划权限检查失败: {e}')
        return JsonResponse({
            'success': False,
            'error': '权限检查失败'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def clear_permission_cache(request):
    """清除权限缓存"""
    try:
        # 清除用户相关的权限缓存
        cache_pattern = f'permission_{request.user.id}_*'
        
        # Django缓存不直接支持模式删除，这里使用简单的方式
        # 在实际项目中可能需要使用Redis等支持模式删除的缓存
        cache.clear()  # 简单粗暴的方式，清除所有缓存
        
        return JsonResponse({
            'success': True,
            'message': '权限缓存已清除'
        })
        
    except Exception as e:
        logger.error(f'清除权限缓存失败: {e}')
        return JsonResponse({
            'success': False,
            'error': '清除缓存失败'
        }, status=500)


@require_http_methods(["GET"])
@require_menu_access('admin')
def get_permission_stats(request):
    """获取权限统计信息（仅管理员）"""
    try:
        from django.contrib.auth import get_user_model
        from django.db.models import Count
        
        User = get_user_model()
        
        # 统计各角色用户数量
        role_stats = User.objects.values('role').annotate(count=Count('id'))
        
        # 使用 MenuValidity 和 RoleMenuAssignment 统计权限配置
        from apps.permissions.models import MenuValidity, RoleManagement
        
        permission_stats = []
        roles = RoleManagement.objects.all()
        for role in roles:
            menu_count = MenuValidity.objects.filter(role=role, is_valid=True).count()
            permission_stats.append({
                'role_name': role.role_name,
                'display_name': role.display_name,
                'menu_permissions': menu_count
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'role_distribution': list(role_stats),
                'permission_configurations': list(permission_stats),
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count()
            }
        })
        
    except Exception as e:
        logger.error(f'获取权限统计失败: {e}')
        return JsonResponse({
            'success': False,
            'error': '获取统计信息失败'
        }, status=500)