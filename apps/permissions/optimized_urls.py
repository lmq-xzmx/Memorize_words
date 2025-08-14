"""优化后的权限检查API路由配置"""

from django.urls import path
from . import optimized_views

app_name = 'permissions_optimized'

urlpatterns = [
    # 统一权限检查接口
    path('api/check/', optimized_views.OptimizedPermissionAPIView.as_view(), name='check_permission'),
    
    # 获取用户权限信息
    path('api/user-permissions/', optimized_views.get_user_permissions, name='user_permissions'),
    
    # 获取用户菜单权限信息（与前端兼容）
    path('api/user-menu-permissions/', optimized_views.get_user_menu_permissions, name='user_menu_permissions'),
    
    # 菜单权限检查
    path('api/check-menu/', optimized_views.check_menu_permission, name='check_menu'),
    
    # 学习目标权限检查
    path('api/check-learning-goal/', optimized_views.check_learning_goal_permission, name='check_learning_goal'),
    
    # 学习计划权限检查
    path('api/check-learning-plan/', optimized_views.check_learning_plan_permission, name='check_learning_plan'),
    
    # 清除权限缓存
    path('api/clear-cache/', optimized_views.clear_permission_cache, name='clear_cache'),
    
    # 权限统计信息（仅管理员）
    path('api/stats/', optimized_views.get_permission_stats, name='permission_stats'),
]