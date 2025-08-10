from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Q, Count, Avg, Sum, QuerySet
from django.utils import timezone
from datetime import timedelta
from typing import Type, Union

from .models import (
    Word, WordResource, VocabularySource, VocabularyList
)
from apps.vocabulary_manager.models import UserStreak, StudySession
from .serializers import (
    WordSerializer, WordListSerializer, WordResourceSerializer,
    VocabularySourceSerializer, VocabularyListSerializer,
    UserStreakSerializer, StudySessionSerializer, WordStatisticsSerializer,
    BulkWordOperationSerializer
)


class WordResourceViewSet(viewsets.ModelViewSet):
    """单词资源视图集"""
    queryset = WordResource.objects.all()
    serializer_class = WordResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']


class WordViewSet(viewsets.ModelViewSet):
    """单词视图集"""
    serializer_class = WordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_learned', 'difficulty_level', 'part_of_speech']
    search_fields = ['word', 'definition', 'example', 'tags']
    ordering_fields = ['created_at', 'word', 'mastery_level', 'difficulty_level']
    ordering = ['-created_at']
    
    def get_queryset(self) -> QuerySet:
        """获取当前用户的单词"""
        return Word.objects.filter(user=self.request.user).prefetch_related('resources')
    
    def get_serializer_class(self) -> Type[Union[WordListSerializer, WordSerializer]]:
        """根据动作选择序列化器"""
        if self.action == 'list':
            return WordListSerializer
        return WordSerializer
    
    def perform_create(self, serializer):
        """创建单词时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取单词统计信息"""
        queryset = self.get_queryset()
        
        # 基础统计
        total_words = queryset.count()
        learned_words = queryset.filter(is_learned=True).count()
        unlearned_words = total_words - learned_words
        learning_rate = (learned_words / total_words * 100) if total_words > 0 else 0
        
        # 平均掌握程度
        mastery_result = queryset.aggregate(avg=Avg('mastery_level'))
        avg_mastery = mastery_result['avg'] or 0
        
        # 按难度分组
        words_by_difficulty = {}
        for i in range(1, 6):
            count = queryset.filter(difficulty_level=i).count()
            words_by_difficulty[f'level_{i}'] = count
        
        # 按词性分组
        words_by_part_of_speech = {}
        pos_stats = queryset.values('part_of_speech').annotate(count=Count('id'))
        for stat in pos_stats:
            pos = stat['part_of_speech'] or '未分类'
            words_by_part_of_speech[pos] = stat['count']
        
        # 最近活动（最近7天的学习情况）
        recent_activity = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            count = queryset.filter(
                learned_at__date=date,
                is_learned=True
            ).count()
            recent_activity.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        data = {
            'total_words': total_words,
            'learned_words': learned_words,
            'unlearned_words': unlearned_words,
            'learning_rate': round(learning_rate, 2),
            'average_mastery': round(avg_mastery, 2),
            'words_by_difficulty': words_by_difficulty,
            'words_by_part_of_speech': words_by_part_of_speech,
            'recent_activity': recent_activity
        }
        
        serializer = WordStatisticsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_operation(self, request):
        """批量操作单词"""
        serializer = BulkWordOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        word_ids = serializer.validated_data['word_ids']
        operation = serializer.validated_data['operation']
        tag = serializer.validated_data.get('tag')
        
        # 获取用户的单词
        words = self.get_queryset().filter(id__in=word_ids)
        
        if not words.exists():
            return Response(
                {'error': '未找到指定的单词'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 执行批量操作
        if operation == 'mark_learned':
            updated = words.update(is_learned=True, learned_at=timezone.now())
        elif operation == 'mark_unlearned':
            updated = words.update(is_learned=False, learned_at=None)
        elif operation == 'reset_mastery':
            updated = words.update(mastery_level=0)
        elif operation == 'delete':
            updated = words.count()
            words.delete()
        elif operation == 'add_tag':
            updated = 0
            for word in words:
                word.add_tag(tag)
                updated += 1
        elif operation == 'remove_tag':
            updated = 0
            for word in words:
                word.remove_tag(tag)
                updated += 1
        else:
            return Response(
                {'error': '不支持的操作类型'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': f'成功处理 {updated} 个单词',
            'operation': operation,
            'affected_count': updated
        })
    
    @action(detail=True, methods=['post'])
    def mark_learned(self, request, pk=None):
        """标记单词为已学习"""
        word = self.get_object()
        word.is_learned = True
        word.learned_at = timezone.now()
        word.save()
        
        # 更新用户学习记录
        streak, created = UserStreak.objects.get_or_create(user=request.user)
        streak.update_streak()
        streak.total_words_learned += 1
        streak.save()
        
        return Response({'message': '单词已标记为已学习'})
    
    @action(detail=True, methods=['post'])
    def update_mastery(self, request, pk=None):
        """更新单词掌握程度"""
        word = self.get_object()
        mastery_level = request.data.get('mastery_level')
        
        if mastery_level is None or not (0 <= mastery_level <= 100):
            return Response(
                {'error': '掌握程度必须在0-100之间'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        word.mastery_level = mastery_level
        word.save()
        
        return Response({'message': f'掌握程度已更新为 {mastery_level}'})


class VocabularySourceViewSet(viewsets.ModelViewSet):
    """词库来源视图集"""
    queryset = VocabularySource.objects.all()
    serializer_class = VocabularySourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['name']


class VocabularyListViewSet(viewsets.ModelViewSet):
    """词库列表视图集"""
    queryset = VocabularyList.objects.select_related('source')
    serializer_class = VocabularyListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'word_count']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def update_word_count(self, request, pk=None):
        """更新词库列表的单词数量"""
        vocabulary_list = self.get_object()
        count = vocabulary_list.update_word_count()
        return Response({
            'message': f'单词数量已更新为 {count}',
            'word_count': count
        })


# ImportedVocabularyViewSet已合并到WordViewSet中


class UserStreakViewSet(viewsets.ReadOnlyModelViewSet):
    """用户学习记录视图集"""
    serializer_class = UserStreakSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self) -> QuerySet:
        """获取当前用户的学习记录"""
        return UserStreak.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_streak(self, request):
        """获取我的学习记录"""
        streak, created = UserStreak.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(streak)
        return Response(serializer.data)


class StudySessionViewSet(viewsets.ModelViewSet):
    """学习会话视图集"""
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['completed_at']
    ordering_fields = ['created_at', 'completed_at', 'words_count']
    ordering = ['-created_at']
    
    def get_queryset(self) -> QuerySet:
        """获取当前用户的学习会话"""
        return StudySession.objects.filter(user=self.request.user).prefetch_related('words_studied')
    
    def perform_create(self, serializer):
        """创建学习会话时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成学习会话"""
        session = self.get_object()
        
        if session.completed_at:
            return Response(
                {'error': '该学习会话已经完成'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取会话时长和正确率
        session_duration = request.data.get('session_duration')
        accuracy_rate = request.data.get('accuracy_rate')
        
        if session_duration:
            session.session_duration = timezone.timedelta(seconds=session_duration)
        
        if accuracy_rate is not None:
            if not (0 <= accuracy_rate <= 1):
                return Response(
                    {'error': '正确率必须在0-1之间'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            session.accuracy_rate = accuracy_rate
        
        session.complete_session()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取学习会话统计"""
        queryset = self.get_queryset()
        
        # 基础统计
        total_sessions = queryset.count()
        completed_sessions = queryset.filter(completed_at__isnull=False).count()
        total_words_studied = queryset.aggregate(
            total=Sum('words_count')
        )['total'] or 0
        
        # 平均正确率
        avg_accuracy = queryset.filter(
            accuracy_rate__isnull=False
        ).aggregate(avg=Avg('accuracy_rate'))['avg'] or 0
        
        # 最近7天的学习情况
        recent_sessions = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            count = queryset.filter(created_at__date=date).count()
            words_count = queryset.filter(
                created_at__date=date
            ).aggregate(total=Sum('words_count'))['total'] or 0
            
            recent_sessions.append({
                'date': date.strftime('%Y-%m-%d'),
                'sessions_count': count,
                'words_count': words_count
            })
        
        data = {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_words_studied': total_words_studied,
            'average_accuracy': round(avg_accuracy * 100, 2) if avg_accuracy else 0,
            'recent_sessions': recent_sessions
        }
        
        return Response(data)


def word_challenge_view(request):
    """单词斩页面视图"""
    from django.shortcuts import render
    from .models import Word
    
    # 获取所有单词（因为Word模型没有user字段，我们获取所有单词）
    all_words = Word.objects.all()
    
    # 获取未掌握的单词（基于mastery_level判断）
    unlearned_words = all_words.filter(
        mastery_level__lt=50  # 掌握度低于50%的单词
    ).order_by('?')[:10]  # 随机选择10个单词
    
    # 获取学习统计
    total_words = all_words.count()
    learned_words = all_words.filter(mastery_level__gte=80).count()  # 掌握度80%以上算已掌握
    learning_progress = (learned_words / total_words * 100) if total_words > 0 else 0
    
    context = {
        'unlearned_words': unlearned_words,
        'total_words': total_words,
        'learned_words': learned_words,
        'learning_progress': round(learning_progress, 1),
        'challenge_words': unlearned_words[:5],  # 挑战模式显示5个单词
    }
    
    return render(request, 'words/word_challenge.html', context)


def word_examples_view(request):
    """单词例句页面视图"""
    from django.shortcuts import render
    from django.core.paginator import Paginator
    from django.db.models import Q
    from .models import Word
    
    # 获取搜索参数
    search_query = request.GET.get('search', '') if request.GET else ''
    grade_filter = request.GET.get('grade', '') if request.GET else ''
    
    # 构建查询条件
    words = Word.objects.filter(
        example__isnull=False,
        example__gt=''
    ).exclude(example='')
    
    # 应用搜索过滤
    if search_query:
        words = words.filter(
            Q(word__icontains=search_query) |
            Q(definition__icontains=search_query) |
            Q(example__icontains=search_query)
        )
    
    # 应用年级过滤
    if grade_filter:
        words = words.filter(grade=grade_filter)
    
    # 排序
    words = words.order_by('word')
    
    # 分页
    paginator = Paginator(words, 20)  # 每页显示20个单词
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取年级选择列表
    from .models import GRADE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'grade_filter': grade_filter,
        'grade_choices': GRADE_CHOICES,
        'total_words': words.count(),
    }
    
    return render(request, 'words/word_examples.html', context)