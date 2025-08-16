from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

app_name = 'teaching'

# 创建DRF路由器
router = DefaultRouter()
router.register(r'goals', api_views.LearningGoalViewSet, basename='learninggoal')
router.register(r'goal-words', api_views.GoalWordViewSet, basename='goalword')
router.register(r'plans', api_views.LearningPlanViewSet, basename='learningplan')
router.register(r'sessions', api_views.LearningSessionViewSet, basename='learningsession')
router.register(r'records', api_views.WordLearningRecordViewSet, basename='wordlearningrecord')
router.register(r'statistics', api_views.TeachingStatisticsViewSet, basename='teachingstatistics')
router.register(r'guided-practice', api_views.GuidedPracticeSessionViewSet, basename='guidedpracticesession')

urlpatterns = [
    # API路由 - 直接包含router.urls，因为主URL配置中已经有api/teaching/前缀
    path('', include(router.urls)),
    
    # 页面路由
    path('', views.index, name='index'),
    path('dashboard/', views.learning_dashboard, name='dashboard'),
    path('goals/', views.goals_list, name='goals_list'),
    path('search-words/', views.search_words, name='search_words'),
]
