from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from typing import Dict, List, Any
import json
import logging

from ..models import RoleGroupMapping, GroupRoleIdentifier
from ..services.group_consistency_checker import GroupConsistencyChecker
from ..models_optimized import PermissionSyncLog

logger = logging.getLogger(__name__)


@staff_member_required
@require_http_methods(["POST"])
def group_consistency_check(request, group_id: int) -> JsonResponse:
    """组一致性检查API视图
    
    Args:
        request: HTTP请求对象
        group_id: 组ID
        
    Returns:
        JsonResponse: 检查结果
    """
    try:
        # 获取组对象
        group = get_object_or_404(Group, pk=group_id)
        
        # 解析请求数据
        try:
            data = json.loads(request.body)
            action = data.get('action')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({
                'success': False,
                'error': '无效的请求数据'
            }, status=400)
        
        if action != 'check_consistency':
            return JsonResponse({
                'success': False,
                'error': '无效的操作类型'
            }, status=400)
        
        # 执行一致性检查
        checker = GroupConsistencyChecker()
        result = checker.check_group_consistency(group)
        
        # 构建响应数据
        response_data = {
            'success': True,
            'result': {
                'group_id': getattr(group, 'id', None),
                'is_consistent': result.get('is_consistent', False),
                'issues': result.get('issues', []),
                'group_info': {
                    'name': getattr(group, 'name', '未知'),
                    'user_count': getattr(group, 'user_set', None) and group.user_set.count() or 0,
                    'permission_count': getattr(group, 'permissions', None) and group.permissions.count() or 0,
                }
            }
        }
        
        # 添加角色标识信息
        try:
            identifier = getattr(group, 'grouproleidentifier', None)
            if identifier:
                response_data['result']['group_info']['role_identifier'] = getattr(identifier, 'role_identifier', None)
                response_data['result']['group_info']['status'] = getattr(identifier, 'status', None)
                response_data['result']['group_info']['sync_status'] = getattr(identifier, 'sync_status', None)
            else:
                response_data['result']['group_info']['role_identifier'] = None
        except Exception:
            response_data['result']['group_info']['role_identifier'] = None
        
        # 记录检查日志
        PermissionSyncLog.objects.create(
            action='consistency_check',
            target_type='group',
            target_id=str(group.id),
            details={
                'group_name': group.name,
                'is_consistent': result['is_consistent'],
                'issues_count': len(result.get('issues', [])),
                'checked_by': request.user.username
            },
            status='success' if result['is_consistent'] else 'warning',
            created_by=request.user
        )
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"组一致性检查失败 (group_id={group_id}): {str(e)}", exc_info=True)
        
        # 记录错误日志
        try:
            PermissionSyncLog.objects.create(
                action='consistency_check',
                target_type='group',
                target_id=str(group_id),
                details={
                    'error': str(e),
                    'checked_by': request.user.username
                },
                status='error',
                created_by=request.user
            )
        except Exception:
            pass  # 避免日志记录失败影响主要功能
        
        return JsonResponse({
            'success': False,
            'error': f'检查过程中发生错误: {str(e)}'
        }, status=500)


@staff_member_required
@require_http_methods(["POST"])
def group_fix_issues(request, group_id: int) -> JsonResponse:
    """组问题修复API视图
    
    Args:
        request: HTTP请求对象
        group_id: 组ID
        
    Returns:
        JsonResponse: 修复结果
    """
    try:
        # 获取组对象
        group = get_object_or_404(Group, pk=group_id)
        
        # 解析请求数据
        try:
            data = json.loads(request.body)
            action = data.get('action')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({
                'success': False,
                'error': '无效的请求数据'
            }, status=400)
        
        if action != 'fix_issues':
            return JsonResponse({
                'success': False,
                'error': '无效的操作类型'
            }, status=400)
        
        # 执行问题修复
        with transaction.atomic():
            checker = GroupConsistencyChecker()
            result = checker.fix_group_issues(group)
        
        # 记录修复日志
        PermissionSyncLog.objects.create(
            action='fix_issues',
            target_type='group',
            target_id=str(group.id),
            details={
                'group_name': group.name,
                'fixed_issues': result.get('fixed_issues', []),
                'success': result.get('success', False),
                'fixed_by': request.user.username
            },
            status='success' if result.get('success') else 'error',
            created_by=request.user
        )
        
        return JsonResponse({
            'success': result.get('success', False),
            'fixed_issues': result.get('fixed_issues', []),
            'message': result.get('message', '修复完成')
        })
        
    except Exception as e:
        logger.error(f"组问题修复失败 (group_id={group_id}): {str(e)}", exc_info=True)
        
        # 记录错误日志
        try:
            PermissionSyncLog.objects.create(
                action='fix_issues',
                target_type='group',
                target_id=str(group_id),
                details={
                    'error': str(e),
                    'fixed_by': request.user.username
                },
                status='error',
                created_by=request.user
            )
        except Exception:
            pass
        
        return JsonResponse({
            'success': False,
            'error': f'修复过程中发生错误: {str(e)}'
        }, status=500)


@staff_member_required
@require_http_methods(["POST"])
def batch_sync_groups(request) -> JsonResponse:
    """批量同步所有组API视图
    
    Args:
        request: HTTP请求对象
        
    Returns:
        JsonResponse: 同步结果
    """
    try:
        # 解析请求数据
        try:
            data = json.loads(request.body)
            action = data.get('action')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({
                'success': False,
                'error': '无效的请求数据'
            }, status=400)
        
        if action != 'batch_sync_all':
            return JsonResponse({
                'success': False,
                'error': '无效的操作类型'
            }, status=400)
        
        # 执行批量同步
        with transaction.atomic():
            checker = GroupConsistencyChecker()
            result = checker.batch_sync_all_groups()
        
        # 记录批量同步日志
        PermissionSyncLog.objects.create(
            action='batch_sync',
            target_type='all_groups',
            target_id='*',
            details={
                'total_groups': result.get('total_groups', 0),
                'success_count': result.get('success_count', 0),
                'error_count': result.get('error_count', 0),
                'errors': result.get('errors', []),
                'synced_by': request.user.username
            },
            status='success' if result.get('error_count', 0) == 0 else 'warning',
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'total_groups': result.get('total_groups', 0),
            'success_count': result.get('success_count', 0),
            'error_count': result.get('error_count', 0),
            'errors': result.get('errors', [])
        })
        
    except Exception as e:
        logger.error(f"批量同步失败: {str(e)}", exc_info=True)
        
        # 记录错误日志
        try:
            PermissionSyncLog.objects.create(
                action='batch_sync',
                target_type='all_groups',
                target_id='*',
                details={
                    'error': str(e),
                    'synced_by': request.user.username
                },
                status='error',
                created_by=request.user
            )
        except Exception:
            pass
        
        return JsonResponse({
            'success': False,
            'error': f'批量同步过程中发生错误: {str(e)}'
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def group_stats(request) -> JsonResponse:
    """获取组统计信息API视图
    
    Args:
        request: HTTP请求对象
        
    Returns:
        JsonResponse: 统计信息
    """
    try:
        # 计算统计信息
        total_groups = Group.objects.count()
        
        # 有角色标识的组
        try:
            role_linked_groups = Group.objects.filter(
                grouproleidentifier__status='role_linked'
            ).count()
        except Exception:
            role_linked_groups = 0
        
        # 孤立组
        try:
            orphaned_groups = Group.objects.filter(
                grouproleidentifier__status='orphaned'
            ).count()
        except Exception:
            orphaned_groups = 0
        
        # 无标识符的组
        try:
            no_identifier_groups = Group.objects.filter(
                grouproleidentifier__isnull=True
            ).count()
        except Exception:
            no_identifier_groups = 0
        
        # 活跃映射数量
        try:
            active_mappings = RoleGroupMapping.objects.filter(
                is_active=True
            ).count()
        except Exception:
            active_mappings = 0
        
        # 同步状态统计
        sync_stats = {}
        try:
            sync_stats = {
                'synced': GroupRoleIdentifier.objects.filter(sync_status='synced').count(),
                'pending': GroupRoleIdentifier.objects.filter(sync_status='pending').count(),
                'failed': GroupRoleIdentifier.objects.filter(sync_status='failed').count(),
                'disabled': GroupRoleIdentifier.objects.filter(sync_status='disabled').count()
            }
        except Exception:
            sync_stats = {'synced': 0, 'pending': 0, 'failed': 0, 'disabled': 0}
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_groups': total_groups,
                'role_linked_groups': role_linked_groups,
                'orphaned_groups': orphaned_groups,
                'no_identifier_groups': no_identifier_groups,
                'active_mappings': active_mappings,
                'sync_stats': sync_stats
            }
        })
        
    except Exception as e:
        logger.error(f"获取组统计信息失败: {str(e)}", exc_info=True)
        
        return JsonResponse({
            'success': False,
            'error': f'获取统计信息时发生错误: {str(e)}'
        }, status=500)