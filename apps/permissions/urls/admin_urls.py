from django.urls import path
from ..views.group_admin_views import (
    group_consistency_check,
    group_fix_issues,
    batch_sync_groups,
    group_stats
)

app_name = 'permissions_admin'

urlpatterns = [
    # 组一致性检查
    path(
        'group/<int:group_id>/consistency-check/',
        group_consistency_check,
        name='group_consistency_check'
    ),
    
    # 组问题修复
    path(
        'group/<int:group_id>/fix-issues/',
        group_fix_issues,
        name='group_fix_issues'
    ),
    
    # 批量同步组
    path(
        'group/batch-sync/',
        batch_sync_groups,
        name='batch_sync_groups'
    ),
    
    # 组统计信息
    path(
        'group/stats/',
        group_stats,
        name='group_stats'
    ),
]