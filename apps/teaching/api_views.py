from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.renderers import JSONRenderer
from django.db.models import Q, Count, Avg, Sum, QuerySet
from django.utils import timezone
from datetime import timedelta
from typing import Type, Union, Any, Optional

from .models import (
    LearningGoal, GoalWord, LearningSession, WordLearningRecord,
    LearningPlan, GuidedPracticeSession, GuidedPracticeQuestion, GuidedPracticeAnswer
)
from apps.words.models import Word
from .serializers import (
    LearningGoalSerializer, GoalWordSerializer, LearningSessionSerializer,
    WordLearningRecordSerializer, LearningPlanSerializer,
    LearningSessionCreateSerializer, WordLearningRecordCreateSerializer,
    LearningStatisticsSerializer, BulkGoalWordSerializer,
    GuidedPracticeSessionSerializer, GuidedPracticeQuestionSerializer,
    GuidedPracticeAnswerSerializer, GuidedPracticeAnswerCreateSerializer,
    GuidedPracticeSessionDetailSerializer
)


class LearningGoalViewSet(viewsets.ModelViewSet):
    """学习目标视图集"""
    serializer_class = LearningGoalSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    ordering = ['-created_at']
    
    # 禁用可浏览的API渲染器以避免模板错误
    renderer_classes = [JSONRenderer]
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action == 'list':
            # 允许匿名用户查看学习目标列表
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):  # type: ignore
        """获取学习目标"""
        if self.request.user.is_authenticated:
            return LearningGoal.objects.filter(user=self.request.user)
        else:
            # 匿名用户只能看到活跃的公共学习目标
            return LearningGoal.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        """创建学习目标时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取学习目标进度"""
        goal = self.get_object()
        progress_stats = goal.get_progress_stats()
        return Response(progress_stats)
    
    @action(detail=True, methods=['post'])
    def add_words(self, request, pk=None):
        """添加单词到学习目标"""
        goal = self.get_object()
        word_ids = request.data.get('word_ids', [])
        
        if not word_ids:
            return Response(
                {'error': '请提供单词ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证单词是否属于当前用户
        words = Word.objects.filter(
            id__in=word_ids,
            user=request.user
        )
        
        if words.count() != len(word_ids):
            return Response(
                {'error': '部分单词不存在或无权限访问'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 添加单词到目标
        added_count = 0
        for word in words:
            goal_word, created = GoalWord.objects.get_or_create(
                goal=goal,
                word=word
            )
            if created:
                added_count += 1
        
        return Response({
            'message': f'成功添加 {added_count} 个单词到学习目标',
            'added_count': added_count,
            'total_words': GoalWord.objects.filter(goal=goal).count()
        })
    
    @action(detail=True, methods=['post'])
    def remove_words(self, request, pk=None):
        """从学习目标中移除单词"""
        goal = self.get_object()
        word_ids = request.data.get('word_ids', [])
        
        if not word_ids:
            return Response(
                {'error': '请提供单词ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 移除单词
        removed_count = GoalWord.objects.filter(
            goal=goal,
            word_id__in=word_ids
        ).delete()[0]
        
        return Response({
            'message': f'成功移除 {removed_count} 个单词',
            'removed_count': removed_count,
            'total_words': GoalWord.objects.filter(goal=goal).count()
        })
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前活跃的学习目标"""
        current_goal = LearningGoal.objects.filter(
            user=request.user,
            is_active=True
        ).first()
        
        if not current_goal:
            return Response(
                {'message': '暂无活跃的学习目标'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(current_goal)
        goal_data = serializer.data
        
        # 添加进度信息
        progress_stats = current_goal.get_progress_stats()
        goal_data.update(progress_stats)
        
        return Response(goal_data)
    
    @action(detail=True, methods=['get'])
    def words(self, request, pk=None):
        """分页获取学习目标的单词列表"""
        goal = self.get_object()
        
        # 获取查询参数
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        filter_type = request.GET.get('filter', 'all')
        
        # 构建查询集
        queryset = goal.goal_words.select_related('word')
        
        # 应用筛选
        if filter_type == 'recent':
            queryset = queryset.order_by('-added_at')
        elif filter_type == 'alphabetical':
            queryset = queryset.order_by('word__word')
        else:
            queryset = queryset.order_by('-added_at')
        
        # 分页处理
        from django.core.paginator import Paginator
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        # 序列化数据
        results = []
        for goal_word in page_obj:
            results.append({
                'id': goal_word.id,
                'word': {
                    'id': goal_word.word.id,
                    'word': goal_word.word.word,
                    'definition': getattr(goal_word.word, 'definition', ''),
                    'pronunciation': getattr(goal_word.word, 'pronunciation', ''),
                },
                'added_at': goal_word.added_at.isoformat(),
            })
        
        return Response({
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
    
    @action(detail=True, methods=['post'])
    def remove_word(self, request, pk=None):
        """从学习目标中移除单个单词"""
        goal = self.get_object()
        word_id = request.data.get('word_id')
        
        if not word_id:
            return Response(
                {'detail': '请提供单词ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            goal_word = GoalWord.objects.get(goal=goal, word_id=word_id)
            goal_word.delete()
            
            return Response({
                'detail': '单词删除成功',
                'remaining_count': goal.goal_words.count()
            })
        except GoalWord.DoesNotExist:
            return Response(
                {'detail': '单词不存在于此学习目标中'},
                status=status.HTTP_404_NOT_FOUND
            )


class GoalWordViewSet(viewsets.ModelViewSet):
    """目标单词视图集"""
    serializer_class = GoalWordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering_fields = ['added_at']
    ordering = ['-added_at']
    
    def get_queryset(self):  # type: ignore
        """获取当前用户的目标单词"""
        return GoalWord.objects.filter(goal__user=self.request.user)


class LearningSessionViewSet(viewsets.ModelViewSet):
    """学习会话视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering_fields = ['start_time', 'end_time']
    ordering = ['-start_time']
    
    def get_queryset(self):  # type: ignore
        """获取当前用户的学习会话"""
        return LearningSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):  # type: ignore
        """根据动作选择序列化器"""
        if self.action == 'create':
            return LearningSessionCreateSerializer
        return LearningSessionSerializer
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """结束学习会话"""
        session = self.get_object()
        
        if session.end_time:
            return Response(
                {'error': '该学习会话已经结束'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.end_time = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        """获取学习会话的记录"""
        session = self.get_object()
        records = session.records.all().order_by('-created_at')
        
        # 分页
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = WordLearningRecordSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = WordLearningRecordSerializer(records, many=True)
        return Response(serializer.data)


class WordLearningRecordViewSet(viewsets.ModelViewSet):
    """单词学习记录视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['session', 'goal', 'word', 'is_correct']
    ordering_fields = ['created_at', 'response_time']
    ordering = ['-created_at']
    
    def get_queryset(self):  # type: ignore
        """获取当前用户的学习记录"""
        return WordLearningRecord.objects.filter(session__user=self.request.user)
    
    def get_serializer_class(self):  # type: ignore
        """根据动作选择序列化器"""
        if self.action == 'create':
            return WordLearningRecordCreateSerializer
        return WordLearningRecordSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取学习记录统计"""
        queryset = self.get_queryset()
        
        # 基础统计
        total_records = queryset.count()
        correct_records = queryset.filter(is_correct=True).count()
        accuracy_rate = (correct_records / total_records * 100) if total_records > 0 else 0
        
        # 平均响应时间
        avg_response_time = queryset.aggregate(
            avg=Avg('response_time')
        )['avg'] or 0
        
        # 最近7天的学习情况
        recent_activity = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            day_records = queryset.filter(created_at__date=date)
            correct_count = day_records.filter(is_correct=True).count()
            total_count = day_records.count()
            
            recent_activity.append({
                'date': date.strftime('%Y-%m-%d'),
                'total_records': total_count,
                'correct_records': correct_count,
                'accuracy_rate': (correct_count / total_count * 100) if total_count > 0 else 0
            })
        
        data = {
            'total_records': total_records,
            'correct_records': correct_records,
            'accuracy_rate': round(accuracy_rate, 2),
            'average_response_time': round(avg_response_time, 2),
            'recent_activity': recent_activity
        }
        
        return Response(data)


class LearningPlanViewSet(viewsets.ModelViewSet):
    """学习计划视图集"""
    serializer_class = LearningPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal', 'plan_type', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):  # type: ignore
        """获取当前用户的学习计划"""
        return LearningPlan.objects.filter(goal__user=self.request.user)


# VocabularyListViewSet 和 VocabularyWordViewSet 已移除
# 词汇管理功能现在通过 LearningGoal 和 GoalWord 模型实现


class TeachingStatisticsViewSet(viewsets.GenericViewSet):
    """教学统计视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取教学统计概览"""
        user = request.user
        
        # 学习目标统计
        goals = LearningGoal.objects.filter(user=user)
        total_goals = goals.count()
        active_goals = goals.filter(is_active=True).count()
        
        # 学习会话统计
        sessions = LearningSession.objects.filter(user=user)
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(end_time__isnull=False).count()
        
        # 学习记录统计
        records = WordLearningRecord.objects.filter(session__user=user)
        total_records = records.count()
        correct_records = records.filter(is_correct=True).count()
        accuracy_rate = (correct_records / total_records * 100) if total_records > 0 else 0
        
        # 总学习时间
        completed_sessions_qs = sessions.filter(end_time__isnull=False)
        total_study_minutes = 0
        for session in completed_sessions_qs:
            if session.end_time and session.start_time:
                duration = session.end_time - session.start_time
                total_study_minutes += duration.total_seconds() / 60
        
        # 目标单词统计
        total_goal_words = GoalWord.objects.filter(goal__user=user).count()
        
        # 最近活动（最近7天）
        recent_activity = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            day_sessions = sessions.filter(start_time__date=date).count()
            day_records = records.filter(created_at__date=date).count()
            
            recent_activity.append({
                'date': date.strftime('%Y-%m-%d'),
                'sessions': day_sessions,
                'records': day_records
            })
        
        # 目标进度
        goal_progress = []
        for goal in goals.filter(is_active=True)[:5]:  # 最近5个活跃目标
            progress_stats = goal.get_progress_stats()
            goal_progress.append({
                'goal_id': goal.pk,
                'goal_name': goal.name,
                'target_words': goal.target_words_count,
                'current_words': GoalWord.objects.filter(goal=goal).count(),
                'progress_stats': progress_stats
            })
        
        data = {
            'total_goals': total_goals,
            'active_goals': active_goals,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_records': total_records,
            'correct_records': correct_records,
            'accuracy_rate': round(accuracy_rate, 2),
            'total_study_time': round(total_study_minutes, 2),
            'total_goal_words': total_goal_words,
            'recent_activity': recent_activity,
            'goal_progress': goal_progress
        }
        
        serializer = LearningStatisticsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_add_goal_words(self, request):
        """批量添加目标单词"""
        serializer = BulkGoalWordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        goal_id = request.data.get('goal_id')
        word_ids = request.data.get('word_ids', [])
        
        goal = LearningGoal.objects.get(pk=goal_id)
        words = Word.objects.filter(id__in=word_ids)
        
        # 批量创建目标单词关联
        goal_words = []
        for word in words:
            goal_word, created = GoalWord.objects.get_or_create(
                goal=goal,
                word=word
            )
            if created:
                goal_words.append(goal_word)
        
        return Response({
            'message': f'成功添加 {len(goal_words)} 个单词到学习目标',
            'added_count': len(goal_words),
            'total_words': GoalWord.objects.filter(goal=goal).count()
        })


class GuidedPracticeSessionViewSet(viewsets.ModelViewSet):
    """指导练习会话视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal', 'is_completed']
    ordering_fields = ['created_at', 'completed_at']
    ordering = ['-created_at']
    
    def get_queryset(self):  # type: ignore
        """获取当前用户的指导练习会话"""
        return GuidedPracticeSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):  # type: ignore
        """根据动作选择序列化器"""
        if self.action == 'retrieve':
            return GuidedPracticeSessionDetailSerializer
        return GuidedPracticeSessionSerializer
    
    def perform_create(self, serializer):
        """创建指导练习会话时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成指导练习会话"""
        session = self.get_object()
        
        if session.is_completed:
            return Response(
                {'error': '该指导练习会话已经完成'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.is_completed = True
        session.completed_at = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def current_question(self, request, pk=None):
        """获取当前问题"""
        session = self.get_object()
        current_question = session.get_current_question()
        
        if not current_question:
            return Response(
                {'message': '没有更多问题'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = GuidedPracticeQuestionSerializer(current_question)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        """添加问题到会话"""
        session = self.get_object()
        
        if session.is_completed:
            return Response(
                {'error': '无法向已完成的会话添加问题'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question_data = request.data.copy()
        question_data['session'] = session.pk
        
        serializer = GuidedPracticeQuestionSerializer(data=question_data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        
        return Response(
            GuidedPracticeQuestionSerializer(question).data,
            status=status.HTTP_201_CREATED
        )


class GuidedPracticeQuestionViewSet(viewsets.ModelViewSet):
    """指导练习问题视图集"""
    serializer_class = GuidedPracticeQuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['session', 'word', 'question_type']
    ordering_fields = ['created_at', 'order']
    ordering = ['order', 'created_at']
    
    def get_queryset(self):  # type: ignore
        """获取当前用户的指导练习问题"""
        return GuidedPracticeQuestion.objects.filter(session__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def answers(self, request, pk=None):
        """获取问题的所有答案"""
        question = self.get_object()
        answers = question.get_student_answers()
        
        # 分页
        page = self.paginate_queryset(answers)
        if page is not None:
            serializer = GuidedPracticeAnswerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = GuidedPracticeAnswerSerializer(answers, many=True)
        return Response(serializer.data)


class GuidedPracticeAnswerViewSet(viewsets.ModelViewSet):
    """指导练习答案视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['question', 'student', 'is_correct']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):  # type: ignore
        """获取相关的指导练习答案"""
        user = self.request.user
        # 用户可以看到自己会话中的所有答案
        return GuidedPracticeAnswer.objects.filter(
            Q(question__session__user=user)
        )
    
    def get_serializer_class(self):  # type: ignore
        """根据动作选择序列化器"""
        if self.action == 'create':
            return GuidedPracticeAnswerCreateSerializer
        return GuidedPracticeAnswerSerializer
    
    def perform_create(self, serializer):
        """创建答案时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_answers(self, request):
        """获取当前用户的答案"""
        answers = self.get_queryset().filter(student=request.user)
        
        # 分页
        page = self.paginate_queryset(answers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(answers, many=True)
        return Response(serializer.data)