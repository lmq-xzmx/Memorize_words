from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import AnalyticsViewSet

# API路由配置
router = DefaultRouter()
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

app_name = 'analytics'

urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    
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