from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache
import logging

from .models import MenuModuleConfig, RoleMenuPermission, RoleGroupMapping, RoleManagement
from .models_optimized import PermissionSyncLog
from .serializers import (
    MenuModuleConfigSerializer, RoleMenuPermissionSerializer, GroupSerializer,
    PermissionSerializer, RoleGroupMappingSerializer, PermissionSyncLogSerializer,
    RolePermissionSerializer, MenuAccessCheckSerializer, BulkPermissionUpdateSerializer
)
from apps.accounts.models import UserRole

logger = logging.getLogger(__name__)

# 尝试导入RoleManagement模型，如果不存在则跳过
try:
    from apps.permissions.models import RoleManagement
except ImportError:
    RoleManagement = None


class MenuModuleConfigViewSet(viewsets.ModelViewSet):
    """前台菜单模块配置视图集"""
    queryset = MenuModuleConfig.objects.all()
    serializer_class = MenuModuleConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤可见菜单"""
        user = self.request.user
        if not user.is_authenticated:
            return MenuModuleConfig.objects.none()
        
        # 超级管理员可以看到所有菜单
        if getattr(user, 'is_superuser', False):
            return MenuModuleConfig.objects.filter(is_active=True)
        
        # 根据用户角色过滤菜单
        user_role = getattr(user, 'role', None)
        if user_role:
            accessible_menus = RoleMenuPermission.objects.filter(
                role=user_role,
                can_access=True
            ).values_list('menu_module_id', flat=True)
            return MenuModuleConfig.objects.filter(id__in=accessible_menus, is_active=True)
        
        return MenuModuleConfig.objects.none()
    
    @action(detail=False, methods=['get'])
    def user_menus(self, request):
        """获取当前用户可访问的菜单"""
        user = request.user
        if not user.is_authenticated:
            return Response({'menus': []}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 超级管理员获取所有菜单
        if getattr(user, 'is_superuser', False):
            menus = MenuModuleConfig.objects.filter(is_active=True).order_by('sort_order')
            menu_list = [{
                'key': menu.key,
                'name': menu.name,
                'icon': menu.icon,
                'url': menu.url,
                'sort_order': menu.sort_order
            } for menu in menus]
            return Response({'menus': menu_list})
        
        # 普通用户根据角色权限获取菜单
        user_role = getattr(user, 'role', None)
        if not user_role:
            return Response({'menus': []})
        
        accessible_menus = RoleMenuPermission.objects.filter(
            role=user_role,
            can_access=True,
            menu_module__is_active=True
        ).select_related('menu_module').order_by('menu_module__sort_order')
        
        menus = []
        for perm in accessible_menus:
            menu = perm.menu_module
            menus.append({
                'key': menu.key,
                'name': menu.name,
                'icon': menu.icon,
                'url': menu.url,
                'sort_order': menu.sort_order
            })
        
        return Response({'menus': menus})
    
    @action(detail=True, methods=['post'])
    def check_permission(self, request, pk=None):
        """检查用户对特定菜单的访问权限"""
        menu = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response({'has_permission': False}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 超级管理员拥有所有权限
        if getattr(user, 'is_superuser', False):
            return Response({'has_permission': True})
        
        # 检查角色权限
        user_role = getattr(user, 'role', None)
        if user_role:
            try:
                permission = RoleMenuPermission.objects.get(
                    role=user_role,
                    menu_module=menu
                )
                return Response({'has_permission': permission.can_access})
            except RoleMenuPermission.DoesNotExist:
                pass
        
        return Response({'has_permission': False})


class RoleMenuPermissionViewSet(viewsets.ModelViewSet):
    """角色菜单权限配置视图集"""
    queryset = RoleMenuPermission.objects.all()
    serializer_class = RoleMenuPermissionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def check_access(self, request):
        """检查菜单访问权限"""
        serializer = MenuAccessCheckSerializer(data=request.data)
        if serializer.is_valid():
            role = request.data.get('role')
            menu_key = request.data.get('menu_key')
            
            try:
                menu = MenuModuleConfig.objects.get(key=menu_key, is_active=True)
                permission = RoleMenuPermission.objects.get(
                    role=role,
                    menu_module=menu
                )
                return Response({
                    'has_access': permission.can_access,
                    'menu_name': menu.name
                })
            except (MenuModuleConfig.DoesNotExist, RoleMenuPermission.DoesNotExist):
                return Response({'has_access': False})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """批量更新角色菜单权限"""
        serializer = BulkPermissionUpdateSerializer(data=request.data)
        if serializer.is_valid():
            role = request.data.get('role')
            menu_permissions = request.data.get('menu_permissions', {})
            
            with transaction.atomic():
                updated_count = 0
                for menu_key, can_access in menu_permissions.items():
                    try:
                        menu = MenuModuleConfig.objects.get(key=menu_key)
                        permission, created = RoleMenuPermission.objects.get_or_create(
                            role=role,
                            menu_module=menu,
                            defaults={'can_access': can_access}
                        )
                        if not created and permission.can_access != can_access:
                            permission.can_access = can_access
                            permission.save()
                            updated_count += 1
                        elif created:
                            updated_count += 1
                    except MenuModuleConfig.DoesNotExist:
                        continue
                
                # 记录同步日志
                PermissionSyncLog.objects.create(
                    sync_type='manual',
                    target_type='role',
                    target_id=role,
                    action=f'批量更新菜单权限',
                    result=f'更新了{updated_count}个权限配置',
                    success=True
                )
            
            return Response({
                'message': f'成功更新{updated_count}个权限配置',
                'updated_count': updated_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ModelViewSet):
    """Django组管理视图集"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """权限查看视图集"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 可以根据内容类型过滤
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type__model=content_type)
        return queryset


@api_view(['GET'])
@permission_classes([])
def get_menu_version(request):
    """
    获取菜单版本信息
    用于前端版本控制和同步检查
    """
    try:
        # 获取最新的菜单配置更新时间
        from django.db.models import Max
        from django.utils import timezone
        import hashlib
        import json
        
        # 获取菜单模块的最后更新时间
        last_updated = MenuModuleConfig.objects.aggregate(
            max_updated=Max('updated_at')
        )['max_updated']
        
        if not last_updated:
            last_updated = timezone.now()
        
        # 生成版本号（基于时间戳）
        version = int(last_updated.timestamp())
        
        # 获取所有菜单配置用于生成校验和
        menus = MenuModuleConfig.objects.filter(is_active=True).values(
            'key', 'name', 'icon', 'url', 'sort_order', 'updated_at'
        )
        
        # 生成配置校验和
        menu_data = json.dumps(list(menus), sort_keys=True, default=str)
        checksum = hashlib.md5(menu_data.encode()).hexdigest()
        
        # 获取最近的变更记录（如果有的话）
        changes = []
        try:
            # 获取最近10条同步日志作为变更记录
            sync_logs = PermissionSyncLog.objects.filter(
                operation_type__in=['menu_sync', 'menu_update']
            ).order_by('-created_at')[:10]
            
            for log in sync_logs:
                changes.append({
                    'type': 'update',
                    'target': 'menu',
                    'targetId': log.target_id or 'unknown',
                    'targetName': log.description or '菜单更新',
                    'timestamp': int(log.created_at.timestamp()),
                    'author': log.user.username if log.user else 'system',
                    'reason': log.description or '菜单配置更新'
                })
        except Exception as e:
            logger.warning(f"获取变更记录失败: {str(e)}")
        
        version_info = {
            'version': version,
            'timestamp': int(last_updated.timestamp()),
            'checksum': checksum,
            'changes': changes,
            'author': 'system',
            'description': '菜单配置版本信息'
        }
        
        return Response(version_info)
        
    except Exception as e:
        logger.error(f"获取菜单版本信息失败: {str(e)}")
        return Response({
            'version': 1,
            'timestamp': int(timezone.now().timestamp()),
            'checksum': 'error',
            'changes': [],
            'author': 'system',
            'description': f'获取版本信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_available_roles(request):
    """
    获取可用角色列表
    GET /api/permissions/roles/available/
    """
    try:
        from apps.accounts.services.role_service import RoleService
        
        # 获取角色选择项
        roles = RoleService.get_role_choices(include_empty=False)
        
        # 转换为前端需要的格式
        role_list = []
        for role_value, role_label in roles:
            role_list.append({
                'id': role_value,
                'name': role_label,
                'code': role_value,
                'display_name': role_label
            })
        
        return Response({
            'success': True,
            'data': role_list,
            'count': len(role_list)
        })
        
    except Exception as e:
        logger.error(f"获取可用角色列表失败: {str(e)}")
        return Response({
            'success': False,
            'error': f'获取可用角色列表失败: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_role_fields(request, role_id):
    """
    获取角色字段配置
    GET /api/permissions/roles/{role_id}/fields/
    """
    try:
        from apps.accounts.services.role_service import RoleService
        
        # 获取角色字段配置
        fields = RoleService.get_role_fields(role_id)
        
        return Response({
            'success': True,
            'data': {
                'fields': fields
            },
            'role_id': role_id
        })
        
    except Exception as e:
        logger.error(f"获取角色字段配置失败: {str(e)}")
        return Response({
            'success': False,
            'error': f'获取角色字段配置失败: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_frontend_menus(request):
    """
    同步前端菜单配置到后端数据库
    接收前端菜单配置并更新数据库中的菜单模块配置
    """
    try:
        # 检查用户权限
        if not request.user.is_superuser and getattr(request.user, 'role', None) != UserRole.ADMIN:
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以同步菜单配置'
            }, status=status.HTTP_403_FORBIDDEN)
        
        menu_data = request.data.get('menus', [])
        if not menu_data:
            return Response({
                'success': False,
                'message': '菜单数据不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for menu_item in menu_data:
                menu_key = menu_item.get('key') or menu_item.get('id')
                if not menu_key:
                    continue
                
                # 构建菜单配置数据
                menu_config = {
                    'key': menu_key,
                    'name': menu_item.get('name') or menu_item.get('title', ''),
                    'icon': menu_item.get('icon', ''),
                    'url': menu_item.get('url') or menu_item.get('path', ''),
                    'description': menu_item.get('description', ''),
                    'sort_order': menu_item.get('sort_order', 0),
                    'menu_level': menu_item.get('menu_level', 'root'),
                    'parent_key': menu_item.get('parent_key', ''),
                    'is_active': menu_item.get('enabled', True),
                    'permission_required': menu_item.get('permission', '')
                }
                
                # 更新或创建菜单配置
                menu_obj, created = MenuModuleConfig.objects.update_or_create(
                    key=menu_key,
                    defaults=menu_config
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        return Response({
            'success': True,
            'message': f'菜单同步成功：创建 {created_count} 个，更新 {updated_count} 个',
            'data': {
                'created': created_count,
                'updated': updated_count,
                'total': created_count + updated_count
            }
        })
        
    except Exception as e:
        logger.error(f"菜单同步失败: {str(e)}")
        return Response({
            'success': False,
            'message': f'菜单同步失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_frontend_menu_config(request):
    """
    获取前端菜单配置格式的数据
    返回适合前端使用的菜单配置格式
    """
    try:
        user = request.user
        
        # 如果用户未认证，提供默认菜单配置
        if not user.is_authenticated:
            # 返回默认的基础菜单配置
            default_menu_config = {
                'bottomNavMenus': [
                    {
                        'id': 'word',
                        'key': 'word',
                        'name': '单词学习',
                        'title': '单词学习',
                        'icon': 'book',
                        'path': '/word',
                        'url': '/word',
                        'permission': '',
                        'description': '单词学习功能',
                        'enabled': True,
                        'sort_order': 1
                    },
                    {
                        'id': 'profile',
                        'key': 'profile',
                        'name': '个人中心',
                        'title': '个人中心',
                        'icon': 'user',
                        'path': '/profile',
                        'url': '/profile',
                        'permission': '',
                        'description': '个人中心',
                        'enabled': True,
                        'sort_order': 4
                    }
                ],
                'toolsMenuConfig': {'title': '开发工具', 'items': []},
                'fashionMenuConfig': {'title': '时尚内容', 'items': []},
                'adminMenuConfig': {'title': '管理功能', 'items': []}
            }
            
            return Response({
                'success': True,
                'data': default_menu_config,
                'message': '使用默认菜单配置（未认证用户）'
            })
        
        user_role = getattr(user, 'role', None)
        
        # 获取用户可访问的菜单
        if user.is_superuser:
            menus = MenuModuleConfig.objects.filter(is_active=True)
        elif user_role:
            accessible_menu_ids = RoleMenuPermission.objects.filter(
                role=user_role,
                can_access=True
            ).values_list('menu_module_id', flat=True)
            menus = MenuModuleConfig.objects.filter(
                id__in=accessible_menu_ids,
                is_active=True
            )
        else:
            menus = MenuModuleConfig.objects.none()
        
        # 按菜单级别分组
        menu_config = {
            'bottomNavMenus': [],
            'toolsMenuConfig': {'title': '开发工具', 'items': []},
            'fashionMenuConfig': {'title': '时尚内容', 'items': []},
            'adminMenuConfig': {'title': '管理功能', 'items': []}
        }
        
        for menu in menus.order_by('sort_order'):
            menu_item = {
                'id': menu.key,
                'key': menu.key,
                'name': menu.name,
                'title': menu.name,
                'icon': menu.icon,
                'path': menu.url,
                'url': menu.url,
                'permission': menu.permission_required,
                'description': menu.description,
                'enabled': menu.is_active,
                'sort_order': menu.sort_order
            }
            
            # 根据菜单类型分类
            if menu.key in ['word', 'tools', 'fashion', 'profile']:
                menu_config['bottomNavMenus'].append(menu_item)
            elif 'dev' in menu.key or 'tool' in menu.key:
                menu_config['toolsMenuConfig']['items'].append(menu_item)
            elif 'fashion' in menu.key or 'community' in menu.key or 'listening' in menu.key:
                menu_config['fashionMenuConfig']['items'].append(menu_item)
            elif 'admin' in menu.key:
                menu_config['adminMenuConfig']['items'].append(menu_item)
        
        return Response({
            'success': True,
            'data': menu_config
        })
        
    except Exception as e:
        logger.error(f"获取前端菜单配置失败: {str(e)}")
        return Response({
            'success': False,
            'message': f'获取菜单配置失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_permissions(request):
    """
    获取当前用户的权限信息
    返回格式与前端permission.js中的ROLE_PERMISSIONS保持一致
    """
    try:
        user = request.user
        
        # 获取用户角色权限
        role_permissions = []
        
        # 根据用户角色获取默认权限
        default_permissions = UserRole.get_role_permissions(user.role)
        role_permissions.extend(default_permissions)
        
        # 获取用户的具体权限
        user_permissions = user.get_all_permissions()
        
        # 权限映射：Django权限 -> 前端权限
        permission_mapping = {
            'view_dashboard': 'view_dashboard',
            'view_own_profile': 'view_own_profile', 
            'change_own_settings': 'change_own_settings',
            'view_help': 'view_help',
            'view_word_learning': 'view_word_learning',
            'practice_spelling': 'practice_spelling',
            'use_flashcard': 'use_flashcard',
            'practice_reading': 'practice_reading',
            'view_word_detail': 'view_word_detail',
            'view_word_examples': 'view_word_examples',
            'practice_story_reading': 'practice_story_reading',
            'practice_listening': 'practice_listening',
            'participate_challenge': 'participate_challenge',
            'practice_word_selection': 'practice_word_selection',
            'review_words': 'review_words',
            'analyze_word_roots': 'analyze_word_roots',
            'use_pattern_memory': 'use_pattern_memory',
            'access_community': 'access_community',
            'access_fashion_content': 'access_fashion_content',
            'discover_content': 'discover_content',
            'access_dev_tools': 'access_dev_tools',
            'view_analytics': 'view_analytics',
            'manage_resource_auth': 'manage_resource_auth',
            'manage_subscriptions': 'manage_subscriptions',
            'share_resources': 'share_resources',
            'manage_academic': 'manage_academic',
            'manage_teaching': 'manage_teaching',
            'manage_curriculum': 'manage_curriculum',
            'manage_research': 'manage_research',
            'manage_teaching_methods': 'manage_teaching_methods',
            'view_student': 'view_student',
            'change_student': 'change_student',
            'view_own_children': 'view_own_children',
            'view_child_progress': 'view_child_progress',
            'view_child_reports': 'view_child_reports',
            'communicate_with_teacher': 'communicate_with_teacher',
            'view_reports': 'view_reports',
            'view_academic_reports': 'view_academic_reports',
            'view_research_reports': 'view_research_reports',
            'manage_users': 'manage_users',
        }
        
        # 添加用户的具体权限
        for perm in user_permissions:
            perm_code = perm.split('.')[-1] if '.' in perm else perm
            if perm_code in permission_mapping:
                frontend_perm = permission_mapping[perm_code]
                if frontend_perm not in role_permissions:
                    role_permissions.append(frontend_perm)
        
        # 管理员拥有所有权限
        if user.role == UserRole.ADMIN:
            role_permissions = ['*']
        
        return Response({
            'success': True,
            'data': {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'permissions': role_permissions,
                'role_display': dict(UserRole.choices).get(user.role, user.role)
            }
        })
        
    except Exception as e:
        logger.error(f"获取用户权限失败: {str(e)}")
        return Response({
            'success': False,
            'message': f'获取权限信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_role_permissions_config(request):
    """
    获取所有角色的权限配置
    用于前端权限配置同步
    """
    try:
        # 构建角色权限配置
        role_permissions_config = {}
        
        # 遍历所有角色
        for role_choice in UserRole.choices:
            role_code = role_choice[0]
            role_name = role_choice[1]
            
            # 获取角色的默认权限
            default_permissions = UserRole.get_role_permissions(role_code)
            
            # 获取角色管理中的额外权限
            if RoleManagement:
                 try:
                     role_management = RoleManagement.objects.get(role=role_code)
                     django_permissions = role_management.get_all_permissions()
                     
                     # 转换Django权限为前端权限格式
                     additional_permissions = []
                     for perm in django_permissions:
                         perm_code = perm.codename if hasattr(perm, 'codename') else str(perm)
                         additional_permissions.append(perm_code)
                     
                     # 合并权限
                     all_permissions = list(set(default_permissions + additional_permissions))
                     
                 except RoleManagement.DoesNotExist:
                     all_permissions = default_permissions
            else:
                all_permissions = default_permissions
            
            role_permissions_config[role_code] = {
                'name': role_name,
                'permissions': all_permissions
            }
        
        return Response({
            'success': True,
            'data': role_permissions_config
        })
        
    except Exception as e:
        logger.error(f"获取角色权限配置失败: {str(e)}")
        return Response({
            'success': False,
            'message': f'获取角色权限配置失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleGroupMappingViewSet(viewsets.ModelViewSet):
    """角色组映射配置视图集"""
    queryset = RoleGroupMapping.objects.all()
    serializer_class = RoleGroupMappingSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync_user_groups(self, request):
        """同步用户组"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        sync_count = 0
        error_count = 0
        
        with transaction.atomic():
            for mapping in RoleGroupMapping.objects.filter(auto_sync=True):
                try:
                    # 获取该角色的所有用户
                    users = User.objects.filter(role=mapping.role)
                    for user in users:
                        # 清除用户的所有组
                        user.groups.clear()
                        # 添加到对应组
                        user.groups.add(mapping.group)
                        sync_count += 1
                except Exception as e:
                    error_count += 1
                    continue
        
        # 记录同步日志
        PermissionSyncLog.objects.create(
            sync_type='manual',
            target_type='all_users',
            target_id='batch',
            action='同步用户组',
            result=f'成功同步{sync_count}个用户，失败{error_count}个',
            success=error_count == 0
        )
        
        return Response({
            'message': f'同步完成：成功{sync_count}个，失败{error_count}个',
            'sync_count': sync_count,
            'error_count': error_count
        })


class PermissionSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """权限同步日志视图集"""
    queryset = PermissionSyncLog.objects.all()
    serializer_class = PermissionSyncLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 可以根据同步类型过滤
        sync_type = self.request.query_params.get('sync_type')
        if sync_type:
            queryset = queryset.filter(sync_type=sync_type)
        
        # 可以根据目标类型过滤
        target_type = self.request.query_params.get('target_type')
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        
        return queryset