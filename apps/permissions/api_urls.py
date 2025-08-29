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

# DRF路由器配置
router = DefaultRouter()
router.register(r'unified', UnifiedAjaxAPIViewSet, basename='unified-ajax')

# URL模式配置
urlpatterns = [
    # DRF ViewSet路由
    path('api/', include(router.urls)),
    
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

1. DRF ViewSet端点（推荐使用）：
   - GET /api/unified/role_choices/ - 获取角色选择项
   - GET /api/unified/role_info/?role=<role> - 获取角色信息
   - POST /api/unified/sync_role_group/ - 同步角色组
   - GET /api/unified/menu_validity/?role=<role> - 获取菜单有效性
   - GET /api/unified/user_sync_status/ - 获取用户同步状态
   - POST /api/unified/sync_role_permissions/ - 同步角色权限

2. 传统Django View端点（兼容性）：
   - GET /ajax/role-choices/ - 获取角色选择项
   - GET /ajax/role-info/<role>/ - 获取角色信息
   - POST /ajax/sync-role-group/ - 同步角色组
   - GET /ajax/menu-validity/ - 获取菜单有效性
   - GET /ajax/user-sync-status/ - 获取用户同步状态
   - POST /ajax/sync-role-permissions/ - 同步角色权限

使用建议：
- 新开发的功能优先使用DRF ViewSet端点
- 现有代码可以逐步迁移到DRF端点
- 两套端点提供相同的功能，确保向后兼容性
"""