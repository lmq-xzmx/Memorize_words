"""
统一AJAX API的URL配置
提供统一的API端点路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .unified_ajax_api import (
    UnifiedAjaxAPIViewSet,
    UnifiedAjaxView,
    get_role_choices_compat,
    sync_role_groups_compat,
    get_menu_validity_compat
)
from .api.menu_api import (
    get_user_menu_permissions,
    check_menu_permission,
    get_role_display_name,
    get_menu_hierarchy
)

# DRF路由器配置
router = DefaultRouter()
router.register(r'unified', UnifiedAjaxAPIViewSet, basename='unified-ajax')

# URL模式配置
urlpatterns = [
    # DRF ViewSet路由
    path('api/', include(router.urls)),
    
    # 菜单权限API路由
    path('api/permissions/user-menu-permissions/', get_user_menu_permissions, name='user-menu-permissions'),
    path('api/permissions/check-menu-permission/', check_menu_permission, name='check-menu-permission'),
    path('api/permissions/role-display-name/', get_role_display_name, name='role-display-name'),
    path('api/permissions/menu-hierarchy/', get_menu_hierarchy, name='menu-hierarchy'),
    
    # 传统Django View路由
    path('ajax/', UnifiedAjaxView.as_view(), name='ajax-unified'),
    
    # 兼容性API函数路由
    path('ajax/role-choices/', get_role_choices_compat, name='ajax-role-choices-compat'),
    path('ajax/sync-role-groups/', sync_role_groups_compat, name='ajax-sync-role-groups-compat'),
    path('ajax/menu-validity/', get_menu_validity_compat, name='ajax-menu-validity-compat'),
]

# API端点说明
"""
API端点说明：

1. 菜单权限API端点（推荐使用）：
   - GET /api/permissions/user-menu-permissions/ - 获取用户菜单权限
   - POST /api/permissions/check-menu-permission/ - 检查菜单权限
   - GET /api/permissions/role-display-name/ - 获取角色显示名称
   - GET /api/permissions/menu-hierarchy/ - 获取菜单层级结构

2. DRF ViewSet端点（统一AJAX API）：
   - GET /api/unified/role_choices/ - 获取角色选择项
   - GET /api/unified/role_info/?role=<role> - 获取角色信息
   - POST /api/unified/sync_role_group/ - 同步角色组
   - GET /api/unified/menu_validity/?role=<role> - 获取菜单有效性
   - GET /api/unified/user_sync_status/ - 获取用户同步状态
   - POST /api/unified/sync_role_permissions/ - 同步角色权限

3. 传统Django View端点（兼容性）：
   - GET /ajax/role-choices/ - 获取角色选择项
   - GET /ajax/role-info/<role>/ - 获取角色信息
   - POST /ajax/sync-role-group/ - 同步角色组
   - GET /ajax/menu-validity/ - 获取菜单有效性
   - GET /ajax/user-sync-status/ - 获取用户同步状态
   - POST /ajax/sync-role-permissions/ - 同步角色权限

使用建议：
- 菜单权限相关功能优先使用菜单权限API端点
- 角色管理相关功能使用DRF ViewSet端点
- 现有代码可以逐步迁移到新的API端点
- 多套端点提供相同的功能，确保向后兼容性
"""