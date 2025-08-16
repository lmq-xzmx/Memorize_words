"""统一的权限检查API路由配置

根据差异分析报告的建议，整合所有权限检查API，提供统一的接口端点。
这个文件将替代分散的API配置，提供标准化的权限检查接口。
"""

from django.urls import path
from . import unified_api_views

app_name = 'permissions_unified'

urlpatterns = [
    # 核心权限检查接口
    path('check/', unified_api_views.UnifiedPermissionCheckView.as_view(), name='check_permission'),
    
    # 菜单相关权限接口
    path('menu/check/', unified_api_views.MenuPermissionCheckView.as_view(), name='menu_check'),
    path('menu/hierarchy/', unified_api_views.MenuHierarchyView.as_view(), name='menu_hierarchy'),
    path('menu/accessible/', unified_api_views.AccessibleMenusView.as_view(), name='accessible_menus'),
    
    # 学习目标权限接口
    path('learning-goal/check/', unified_api_views.LearningGoalPermissionView.as_view(), name='learning_goal_check'),
    path('learning-goal/accessible/', unified_api_views.AccessibleLearningGoalsView.as_view(), name='accessible_learning_goals'),
    
    # 学习计划权限接口
    path('learning-plan/check/', unified_api_views.LearningPlanPermissionView.as_view(), name='learning_plan_check'),
    path('learning-plan/accessible/', unified_api_views.AccessibleLearningPlansView.as_view(), name='accessible_learning_plans'),
    
    # 用户权限信息接口
    path('user/permissions/', unified_api_views.UserPermissionsView.as_view(), name='user_permissions'),
    path('user/role/', unified_api_views.UserRoleView.as_view(), name='user_role'),
    
    # 角色权限配置接口
    path('role/permissions/', unified_api_views.RolePermissionsView.as_view(), name='role_permissions'),
    path('role/menus/', unified_api_views.RoleMenusView.as_view(), name='role_menus'),
    
    # 批量权限检查接口
    path('batch/check/', unified_api_views.BatchPermissionCheckView.as_view(), name='batch_check'),
    
    # 权限缓存管理接口
    path('cache/clear/', unified_api_views.ClearCacheView.as_view(), name='clear_cache'),
    path('cache/stats/', unified_api_views.CacheStatsView.as_view(), name='cache_stats'),
    
    # 权限统计和监控接口
    path('stats/overview/', unified_api_views.PermissionStatsView.as_view(), name='permission_stats'),
    path('stats/usage/', unified_api_views.PermissionUsageView.as_view(), name='permission_usage'),
    
    # 权限同步接口
    path('sync/frontend/', unified_api_views.SyncFrontendPermissionsView.as_view(), name='sync_frontend'),
    path('sync/status/', unified_api_views.SyncStatusView.as_view(), name='sync_status'),
]