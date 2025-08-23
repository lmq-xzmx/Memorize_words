from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    MenuModuleConfigViewSet, RoleMenuPermissionViewSet, GroupViewSet,
    PermissionViewSet, RoleGroupMappingViewSet, PermissionSyncLogViewSet,
    get_user_permissions, get_role_permissions_config,
    sync_frontend_menus, get_frontend_menu_config,
    get_available_roles, get_role_fields, get_menu_version
)
from .operation_log_views import OperationLogViewSet
from .api.menu_api import (
    get_user_menu_permissions, check_menu_permission, 
    get_role_display_name, get_menu_hierarchy
)

# API路由配置
router = DefaultRouter()
router.register(r'menu-modules', MenuModuleConfigViewSet, basename='menumoduleconfig')
router.register(r'role-menu-permissions', RoleMenuPermissionViewSet, basename='rolemenupermission')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'role-group-mappings', RoleGroupMappingViewSet, basename='rolegroupmapping')
router.register(r'sync-logs', PermissionSyncLogViewSet, basename='permissionsynclog')
router.register(r'operation-logs', OperationLogViewSet, basename='operationlog')

app_name = 'permissions'

urlpatterns = [
    # 优化后的权限API（优先使用）
    path('optimized/', include('apps.permissions.optimized_urls')),
    
    # API路由
    path('api/', include(router.urls)),
    
    # 菜单权限API（传统接口，保持兼容）
    path('api/user-menu-permissions/', get_user_menu_permissions, name='user_menu_permissions'),
    path('api/check-menu-permission/', check_menu_permission, name='check_menu_permission'),
    path('api/role-display-name/', get_role_display_name, name='role_display_name'),
    path('api/menu-hierarchy/', get_menu_hierarchy, name='menu_hierarchy'),
    
    # 前后端权限同步API
    path('user-permissions/', get_user_permissions, name='get_user_permissions'),
    path('role-permissions-config/', get_role_permissions_config, name='get_role_permissions_config'),
    
    # 前后端菜单同步API
    path('sync-frontend-menus/', sync_frontend_menus, name='sync_frontend_menus'),
    path('frontend-menu-config/', get_frontend_menu_config, name='get_frontend_menu_config'),
    
    # 菜单版本控制API
    path('api/menu/version/', get_menu_version, name='get_menu_version'),
    
    # 角色相关API
    path('roles/available/', get_available_roles, name='get_available_roles'),
    path('roles/<str:role_id>/fields/', get_role_fields, name='get_role_fields'),
    
    # 权限管理主页
    path('', views.PermissionIndexView.as_view(), name='index'),
    
    # 菜单模块配置
    path('menu-modules/', views.MenuModuleListView.as_view(), name='menu_module_list'),
    path('menu-modules/create/', views.MenuModuleCreateView.as_view(), name='menu_module_create'),
    path('menu-modules/<int:pk>/', views.MenuModuleDetailView.as_view(), name='menu_module_detail'),
    path('menu-modules/<int:pk>/edit/', views.MenuModuleUpdateView.as_view(), name='menu_module_update'),
    path('menu-modules/<int:pk>/delete/', views.MenuModuleDeleteView.as_view(), name='menu_module_delete'),
    
    # 角色菜单权限
    path('role-menu-permissions/', views.RoleMenuPermissionListView.as_view(), name='role_menu_permission_list'),
    path('role-menu-permissions/create/', views.RoleMenuPermissionCreateView.as_view(), name='role_menu_permission_create'),
    path('role-menu-permissions/<int:pk>/', views.RoleMenuPermissionDetailView.as_view(), name='role_menu_permission_detail'),
    path('role-menu-permissions/<int:pk>/edit/', views.RoleMenuPermissionUpdateView.as_view(), name='role_menu_permission_update'),
    path('role-menu-permissions/<int:pk>/delete/', views.RoleMenuPermissionDeleteView.as_view(), name='role_menu_permission_delete'),
    
    # 角色组映射
    path('role-group-mappings/', views.RoleGroupMappingListView.as_view(), name='role_group_mapping_list'),
    path('role-group-mappings/create/', views.RoleGroupMappingCreateView.as_view(), name='role_group_mapping_create'),
    path('role-group-mappings/<int:pk>/', views.RoleGroupMappingDetailView.as_view(), name='role_group_mapping_detail'),
    path('role-group-mappings/<int:pk>/edit/', views.RoleGroupMappingUpdateView.as_view(), name='role_group_mapping_update'),
    path('role-group-mappings/<int:pk>/delete/', views.RoleGroupMappingDeleteView.as_view(), name='role_group_mapping_delete'),
    
    # 权限同步日志
    path('sync-logs/', views.PermissionSyncLogListView.as_view(), name='permission_sync_log_list'),
    path('sync-logs/<int:pk>/', views.PermissionSyncLogDetailView.as_view(), name='permission_sync_log_detail'),
    
    # AJAX接口
    path('ajax/sync-permissions/', views.sync_permissions_ajax, name='sync_permissions_ajax'),
    path('ajax/check-permission/', views.check_permission_ajax, name='check_permission_ajax'),
    path('ajax/get-role-permissions/', views.get_role_permissions_ajax, name='get_role_permissions_ajax'),
    
    # 批量操作
    path('batch/assign-permissions/', views.BatchAssignPermissionsView.as_view(), name='batch_assign_permissions'),
    path('batch/remove-permissions/', views.BatchRemovePermissionsView.as_view(), name='batch_remove_permissions'),
]