from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from . import views  # 暂时注释，因为views.py文件不存在

# 应用命名空间
app_name = 'vocabulary_manager'

# 创建路由器
router = DefaultRouter()

# 注册视图集（如果有的话）
# router.register(r'learning-goals', views.LearningGoalViewSet, basename='learninggoal')
# router.register(r'learning-plans', views.LearningPlanViewSet, basename='learningplan')
# router.register(r'daily-records', views.DailyStudyRecordViewSet, basename='dailystudyrecord')

# URL模式
urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    
    # 其他URL模式可以在这里添加
]