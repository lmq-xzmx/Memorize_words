from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WordViewSet, WordEntryViewSet, WordResourceViewSet, VocabularySourceViewSet,
    VocabularyListViewSet, ImportRecordViewSet, StudySessionViewSet,
    word_challenge_view, word_examples_view
)
from . import batch_views

# 应用命名空间
app_name = 'words'

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'words', WordViewSet, basename='word')
router.register(r'word-entries', WordEntryViewSet, basename='wordentry')
router.register(r'word-resources', WordResourceViewSet, basename='wordresource')
router.register(r'vocabulary-sources', VocabularySourceViewSet, basename='vocabularysource')
router.register(r'vocabulary-lists', VocabularyListViewSet, basename='vocabularylist')
router.register(r'import-records', ImportRecordViewSet, basename='importrecord')
# imported-vocabulary已合并到words中
# user-streaks已移除，因为UserStreak模型不存在
router.register(r'study-sessions', StudySessionViewSet, basename='studysession')

# URL模式
urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    
    # 单词版本列表
    path('word-versions/', batch_views.word_version_list, name='word_version_list'),
    
    # 单词斩页面
    path('word-challenge/', word_challenge_view, name='word_challenge'),
    
    # 单词例句页面
    path('word-examples/', word_examples_view, name='word_examples'),
]