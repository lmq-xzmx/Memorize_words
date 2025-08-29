from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.http import JsonResponse
from ..services.role_service import RoleService
from ..models import UserRole, CustomUser
from typing import Dict, List, Any


class RoleAPIViewSet(viewsets.ViewSet):
    """
    角色API视图集
    提供统一的角色数据访问接口
    """
    permission_classes = []  # 暂时移除认证要求，允许公开访问
    
    @action(detail=False, methods=['get'])
    def choices(self, request) -> Response:
        """
        获取角色选择项
        GET /api/roles/choices/
        """
        try:
            choices = RoleService.get_role_choices()
            return Response({
                'success': True,
                'data': choices,
                'count': len(choices)
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def all(self, request) -> Response:
        """
        获取所有角色信息
        GET /api/roles/all/
        """
        try:
            roles = RoleService.get_all_roles()
            return Response({
                'success': True,
                'data': roles,
                'count': len(roles)
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request) -> Response:
        """
        获取角色层级关系
        GET /api/roles/hierarchy/
        """
        try:
            hierarchy = RoleService.get_role_hierarchy()
            return Response({
                'success': True,
                'data': hierarchy
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None) -> Response:
        """
        获取单个角色详细信息
        GET /api/roles/{role_code}/detail/
        """
        if not pk:
            return Response({
                'success': False,
                'error': '角色代码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            role_info = RoleService.get_role_info(str(pk))
            if role_info:
                return Response({
                    'success': True,
                    'data': role_info
                })
            else:
                return Response({
                    'success': False,
                    'error': '角色不存在'
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get', 'post'])
    def validate(self, request, pk=None) -> Response:
        """
        验证角色是否有效
        POST /api/roles/{role_code}/validate/
        """
        if not pk:
            return Response({
                'success': False,
                'error': '角色代码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            is_valid = RoleService.validate_role(str(pk))
            return Response({
                'success': True,
                'valid': is_valid,
                'role': str(pk)
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def clear_cache(self, request) -> Response:
        """
        清除角色缓存
        POST /api/roles/clear_cache/
        需要管理员权限
        """
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            RoleService.clear_cache()
            return Response({
                'success': True,
                'message': '角色缓存已清除'
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def refresh_cache(self, request) -> Response:
        """
        刷新角色缓存
        POST /api/roles/refresh_cache/
        需要管理员权限
        """
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            RoleService.refresh_cache()
            return Response({
                'success': True,
                'message': '角色缓存已刷新'
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request) -> Response:
        """
        获取角色统计信息
        GET /api/roles/stats/
        """
        try:
            from django.db.models import Count
            from ..models import CustomUser
            
            # 统计各角色用户数量
            role_stats = {}
            for role_value, role_label in RoleService.get_role_choices(include_empty=False):
                count = CustomUser.objects.filter(role=role_value).count()
                role_stats[role_value] = {
                    'label': role_label,
                    'count': count
                }
            
            # 获取角色管理中的自定义角色统计
            try:
                from apps.permissions.models import RoleManagement
                custom_roles = RoleManagement.objects.filter(is_active=True)
                for role in custom_roles:
                    if role.role not in role_stats:
                        count = CustomUser.objects.filter(role=role.role).count()
                        role_stats[role.role] = {
                            'label': role.display_name,
                            'count': count
                        }
            except ImportError:
                pass
            
            return Response({
                'success': True,
                'data': role_stats,
                'total_users': sum(stat['count'] for stat in role_stats.values())
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 兼容性函数，用于非DRF环境
def role_choices_api(request):
    """
    角色选择项API（非DRF版本）
    GET /api/role-choices/
    """
    try:
        choices = RoleService.get_role_choices()
        return JsonResponse({
            'success': True,
            'data': choices,
            'count': len(choices)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def role_validate_api(request, role_code):
    """
    角色验证API（非DRF版本）
    GET /api/role-validate/{role_code}/
    """
    try:
        is_valid = RoleService.validate_role(role_code)
        return JsonResponse({
            'success': True,
            'valid': is_valid,
            'role': role_code
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)