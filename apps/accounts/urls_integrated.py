# -*- coding: utf-8 -*-
"""
整合管理中心URL配置

提供统一的管理界面访问入口：
- 整合管理站点路由
- 自定义管理视图路由
- API接口路由
"""

from django.urls import path, include
from django.contrib import admin
from .admin_integrated_site import integrated_admin_site

# 整合管理中心URL配置
app_name = 'integrated_admin'

urlpatterns = [
    # 整合管理站点
    path('', integrated_admin_site.urls),
    
    # 自定义管理视图
    path('dashboard/', integrated_admin_site.admin_view(integrated_admin_site.dashboard_view), name='dashboard'),
    path('user-stats/', integrated_admin_site.admin_view(integrated_admin_site.user_stats_view), name='user_stats'),
    path('permission-stats/', integrated_admin_site.admin_view(integrated_admin_site.permission_stats_view), name='permission_stats'),
    path('system-health/', integrated_admin_site.admin_view(integrated_admin_site.system_health_view), name='system_health'),
]