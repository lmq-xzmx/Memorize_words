from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import AnalyticsViewSet

# API路由配置
router = DefaultRouter()
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

# 用户粘性游戏化系统的额外URL模式
engagement_patterns = [
    path('user-engagement-metrics/', AnalyticsViewSet.as_view({'get': 'user_engagement_metrics'}), name='user_engagement_metrics'),
    path('behavior-analysis/', AnalyticsViewSet.as_view({'get': 'behavior_analysis'}), name='behavior_analysis'),
    path('game-element-effectiveness/', AnalyticsViewSet.as_view({'get': 'game_element_effectiveness'}), name='game_element_effectiveness'),
    path('create-ab-test/', AnalyticsViewSet.as_view({'post': 'create_ab_test'}), name='create_ab_test'),
    path('ab-test-results/', AnalyticsViewSet.as_view({'get': 'ab_test_results'}), name='ab_test_results'),
]

app_name = 'analytics'

urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    
    # 用户粘性游戏化系统API
    path('api/engagement/', include(engagement_patterns)),
    
    # 分析主页
    path('', views.AnalyticsIndexView.as_view(), name='index'),
    
    # 学习分析
    path('learning/', views.LearningAnalyticsView.as_view(), name='learning_analytics'),
    path('progress/', views.ProgressAnalyticsView.as_view(), name='progress_analytics'),
    path('performance/', views.PerformanceAnalyticsView.as_view(), name='performance_analytics'),
    
    # 用户分析
    path('users/', views.UserAnalyticsView.as_view(), name='user_analytics'),
    path('engagement/', views.EngagementAnalyticsView.as_view(), name='engagement_analytics'),
    
    # 课程分析
    path('courses/', views.CourseAnalyticsView.as_view(), name='course_analytics'),
    path('content/', views.ContentAnalyticsView.as_view(), name='content_analytics'),
    
    # 报告
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/generate/', views.GenerateReportView.as_view(), name='generate_report'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    
    # AJAX接口
    path('ajax/get-chart-data/', views.get_chart_data_ajax, name='get_chart_data_ajax'),
    path('ajax/export-data/', views.export_data_ajax, name='export_data_ajax'),
]