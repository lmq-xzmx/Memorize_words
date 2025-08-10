"""
角色所辖用户增项的URL配置
"""

from django.urls import path
from . import views_role_hierarchy

# 设置app_name以支持命名空间URL反向解析
app_name = 'accounts'

urlpatterns = [
    # 第一级：角色级别列表
    path('role-hierarchy/', 
         views_role_hierarchy.role_hierarchy_index, 
         name='role_hierarchy_index'),
    
    # 第二级：角色用户列表
    path('role-hierarchy/role/<int:role_level_id>/users/', 
         views_role_hierarchy.role_users_list, 
         name='role_users_list'),
    
    # 第三级：用户增项详情
    path('role-hierarchy/user/<int:role_user_id>/extensions/', 
         views_role_hierarchy.user_extensions_detail, 
         name='user_extensions_detail'),
    
    # 更新用户增项
    path('role-hierarchy/user/<int:role_user_id>/extensions/update/', 
         views_role_hierarchy.update_user_extensions, 
         name='update_user_extensions'),
    
    # 同步角色数据
    path('role-hierarchy/sync/', 
         views_role_hierarchy.sync_role_data, 
         name='sync_role_data'),
    
    # API接口
    path('role-hierarchy/api/role/<int:role_level_id>/stats/', 
         views_role_hierarchy.role_statistics_api, 
         name='role_statistics_api'),
    
    # 批量操作
    path('role-hierarchy/batch-update/', 
         views_role_hierarchy.batch_update_extensions, 
         name='batch_update_extensions'),
]