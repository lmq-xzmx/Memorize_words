from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserGameProfileViewSet, PointTransactionViewSet, LevelViewSet,
    AchievementViewSet, UserAchievementViewSet, LeaderboardViewSet,
    CompetitionViewSet, GameStatsViewSet
)

router = DefaultRouter()
router.register(r'profiles', UserGameProfileViewSet, basename='gamification-profile')
router.register(r'transactions', PointTransactionViewSet, basename='gamification-transaction')
router.register(r'levels', LevelViewSet, basename='gamification-level')
router.register(r'achievements', AchievementViewSet, basename='gamification-achievement')
router.register(r'user-achievements', UserAchievementViewSet, basename='gamification-user-achievement')
router.register(r'leaderboards', LeaderboardViewSet, basename='gamification-leaderboard')
router.register(r'competitions', CompetitionViewSet, basename='gamification-competition')
router.register(r'stats', GameStatsViewSet, basename='gamification-stats')

app_name = 'gamification'
urlpatterns = [
    path('api/v1/gamification/', include(router.urls)),
]