from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserPreferenceViewSet, LearningBehaviorViewSet,
    RecommendationModelViewSet, PersonalizedRecommendationViewSet,
    LearningPathViewSet, LearningStepViewSet,
    AdaptiveDifficultyViewSet, PersonalizationStatsViewSet
)

app_name = 'personalization'

router = DefaultRouter()
router.register(r'preferences', UserPreferenceViewSet, basename='userpreference')
router.register(r'behaviors', LearningBehaviorViewSet, basename='learningbehavior')
router.register(r'models', RecommendationModelViewSet, basename='recommendationmodel')
router.register(r'recommendations', PersonalizedRecommendationViewSet, basename='personalizedrecommendation')
router.register(r'learning-paths', LearningPathViewSet, basename='learningpath')
router.register(r'learning-steps', LearningStepViewSet, basename='learningstep')
router.register(r'adaptive-difficulty', AdaptiveDifficultyViewSet, basename='adaptivedifficulty')
router.register(r'stats', PersonalizationStatsViewSet, basename='personalizationstats')

urlpatterns = [
    path('api/', include(router.urls)),
]