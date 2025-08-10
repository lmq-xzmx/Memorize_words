from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import MenuModuleConfig, RoleMenuPermission, RoleGroupMapping, PermissionSyncLog
from .serializers import (
    MenuModuleConfigSerializer, RoleMenuPermissionSerializer, GroupSerializer,
    PermissionSerializer, RoleGroupMappingSerializer, PermissionSyncLogSerializer,
    RolePermissionSerializer, MenuAccessCheckSerializer, BulkPermissionUpdateSerializer
)
from apps.accounts.models import UserRole


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