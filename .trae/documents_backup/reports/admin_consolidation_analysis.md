from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'teaching'

# API路由
router = DefaultRouter()
router.register(r'learning-goals', api_views.LearningGoalViewSet, basename='learninggoal')
router.register(r'goal-words', api_views.GoalWordViewSet, basename='goalword')
router.register(r'learning-sessions', api_views.LearningSessionViewSet, basename='learningsession')
router.register(r'word-learning-records', api_views.WordLearningRecordViewSet, basename='wordlearningrecord')
router.register(r'learning-plans', api_views.LearningPlanViewSet, basename='learningplan')
# vocabulary-lists 和 vocabulary-words 路由已移除
router.register(r'statistics', api_views.TeachingStatisticsViewSet, basename='teachingstatistics')
# 指导练习相关路由
router.register(r'guided-practice-sessions', api_views.GuidedPracticeSessionViewSet, basename='guidedpracticesession')
router.register(r'guided-practice-questions', api_views.GuidedPracticeQuestionViewSet, basename='guidedpracticequestion')
router.register(r'guided-practice-answers', api_views.GuidedPracticeAnswerViewSet, basename='guidedpracticeanswer')

urlpatterns = [
    # API路由 - 直接暴露在根路径下，供前端调用
    path('', include(router.urls)),
    
    # 传统Web视图（保留兼容性）
    # 教学主页
    path('web/', views.index, name='index'),
    
    # 学习目标
    path('web/goals/', views.goals_list, name='goals_list'),
    
    # 学习看板
    path('web/learning-dashboard/', views.learning_dashboard, name='learning_dashboard'),
    
    # 词汇管理功能已移除，现在通过学习目标管理单词
    path('web/ajax/search-words/', views.search_words, name='search_words'),
]