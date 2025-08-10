from django.urls import path
from . import views
from .admin import vocabulary_manager_admin

app_name = 'vocabulary_manager'

urlpatterns = [
    # 仪表板
    path('', views.dashboard, name='dashboard'),
    
    # 学习目标管理
    path('goals/', views.learning_goals, name='learning_goals'),
    path('goals/create/', views.create_learning_goal, name='create_goal'),
    path('goals/<int:goal_id>/set-current/', views.set_current_goal, name='set_current_goal'),
    
    # 学习计划管理
    path('plans/', views.learning_plans, name='learning_plans'),
    path('plans/create/', views.create_learning_plan, name='create_plan'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    
    # 学习进度更新
    path('update-progress/', views.update_daily_progress, name='update_progress'),
    
    # 学习统计
    path('statistics/', views.study_statistics, name='statistics'),
    
    # 学习中（看板）
    path('kanban/', views.learning_kanban, name='learning_kanban'),
    path('update-word-progress/', views.update_word_progress, name='update_word_progress'),
    
    # 自定义Admin站点
    path('admin/', vocabulary_manager_admin.urls),
]