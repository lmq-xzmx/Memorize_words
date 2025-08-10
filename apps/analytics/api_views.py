from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta, date, datetime
from django.http import HttpResponse
import csv
import json
from io import StringIO

from apps.words.models import Word
from apps.teaching.models import LearningGoal, LearningSession, WordLearningRecord, GoalWord
from .serializers import (
    AnalyticsOverviewSerializer, DailyActivitySerializer, WeeklyProgressSerializer,
    MonthlyStatisticsSerializer, WordMasteryDistributionSerializer,
    LearningGoalProgressSerializer, StudyPatternSerializer, WeekdayActivitySerializer,
    DifficultyAnalysisSerializer, LearningTrendSerializer, ComprehensiveAnalyticsSerializer,
    ExportDataSerializer, ChartDataSerializer, UserComparisonSerializer
)


class AnalyticsViewSet(viewsets.GenericViewSet):
    """分析数据视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取分析概览"""
        user = request.user
        
        # 基础统计
        total_words = Word.objects.filter(user=user).count()
        
        # 学习记录统计
        learning_records = WordLearningRecord.objects.filter(session__user=user)
        learned_words = learning_records.values('word').distinct().count()
        
        # 掌握率计算
        mastery_rate = (learned_words / total_words * 100) if total_words > 0 else 0
        
        # 学习连续天数（暂时设为0，可后续实现）
        study_streak = 0
        
        # 总学习时间
        sessions = LearningSession.objects.filter(user=user, end_time__isnull=False)
        total_study_time = 0
        for session in sessions:
            if session.end_time and session.start_time:
                duration = session.end_time - session.start_time
                total_study_time += duration.total_seconds() / 60
        
        # 平均正确率
        avg_accuracy = learning_records.aggregate(
            avg=Avg('is_correct')
        )['avg'] or 0
        avg_accuracy = avg_accuracy * 100 if avg_accuracy else 0
        
        # 本周统计
        week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
        week_end = week_start + timedelta(days=6)
        
        words_this_week = learning_records.filter(
            created_at__date__range=[week_start, week_end]
        ).values('word').distinct().count()
        
        sessions_this_week = LearningSession.objects.filter(
            user=user,
            start_time__date__range=[week_start, week_end]
        ).count()
        
        data = {
            'total_words': total_words,
            'learned_words': learned_words,
            'mastery_rate': round(mastery_rate, 2),
            'study_streak': study_streak,
            'total_study_time': round(total_study_time, 2),
            'average_accuracy': round(avg_accuracy, 2),
            'words_this_week': words_this_week,
            'sessions_this_week': sessions_this_week
        }
        
        serializer = AnalyticsOverviewSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_activity(self, request):
        """获取每日活动数据"""
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        activities = []
        for i in range(days):
            target_date = timezone.now().date() - timedelta(days=i)
            
            # 当日学习记录
            day_records = WordLearningRecord.objects.filter(
                session__user=user,
                created_at__date=target_date
            )
            
            # 当日学习会话
            day_sessions = LearningSession.objects.filter(
                user=user,
                start_time__date=target_date
            )
            
            # 统计数据
            words_learned = day_records.values('word').distinct().count()
            study_sessions = day_sessions.count()
            
            # 学习时间
            study_time = 0
            for session in day_sessions.filter(end_time__isnull=False):
                if session.end_time and session.start_time:
                    duration = session.end_time - session.start_time
                    study_time += duration.total_seconds() / 60
            
            # 正确率
            total_records = day_records.count()
            correct_records = day_records.filter(is_correct=True).count()
            accuracy_rate = (correct_records / total_records * 100) if total_records > 0 else 0
            
            activities.append({
                'date': target_date,
                'words_learned': words_learned,
                'study_sessions': study_sessions,
                'study_time': round(study_time, 2),
                'accuracy_rate': round(accuracy_rate, 2)
            })
        
        activities.reverse()  # 按时间正序排列
        serializer = DailyActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly_progress(self, request):
        """获取周进度数据"""
        user = request.user
        weeks = int(request.query_params.get('weeks', 12))
        
        weekly_data = []
        for i in range(weeks):
            # 计算周的开始和结束日期
            week_start = timezone.now().date() - timedelta(days=timezone.now().weekday() + i * 7)
            week_end = week_start + timedelta(days=6)
            
            # 周内学习记录
            week_records = WordLearningRecord.objects.filter(
                session__user=user,
                created_at__date__range=[week_start, week_end]
            )
            
            # 周内学习会话
            week_sessions = LearningSession.objects.filter(
                user=user,
                start_time__date__range=[week_start, week_end]
            )
            
            # 统计数据
            total_words = week_records.values('word').distinct().count()
            total_sessions = week_sessions.count()
            
            # 总学习时间
            total_time = 0
            for session in week_sessions.filter(end_time__isnull=False):
                if session.end_time and session.start_time:
                    duration = session.end_time - session.start_time
                    total_time += duration.total_seconds() / 60
            
            # 平均正确率
            total_records = week_records.count()
            correct_records = week_records.filter(is_correct=True).count()
            average_accuracy = (correct_records / total_records * 100) if total_records > 0 else 0
            
            # 每日活动
            daily_activities = []
            for j in range(7):
                day_date = week_start + timedelta(days=j)
                day_records = week_records.filter(created_at__date=day_date)
                day_sessions = week_sessions.filter(start_time__date=day_date)
                
                day_words = day_records.values('word').distinct().count()
                day_session_count = day_sessions.count()
                
                day_time = 0
                for session in day_sessions.filter(end_time__isnull=False):
                    if session.end_time and session.start_time:
                        duration = session.end_time - session.start_time
                        day_time += duration.total_seconds() / 60
                
                day_total = day_records.count()
                day_correct = day_records.filter(is_correct=True).count()
                day_accuracy = (day_correct / day_total * 100) if day_total > 0 else 0
                
                daily_activities.append({
                    'date': day_date,
                    'words_learned': day_words,
                    'study_sessions': day_session_count,
                    'study_time': round(day_time, 2),
                    'accuracy_rate': round(day_accuracy, 2)
                })
            
            weekly_data.append({
                'week_start': week_start,
                'week_end': week_end,
                'total_words': total_words,
                'total_sessions': total_sessions,
                'total_time': round(total_time, 2),
                'average_accuracy': round(average_accuracy, 2),
                'daily_activities': daily_activities
            })
        
        weekly_data.reverse()  # 按时间正序排列
        serializer = WeeklyProgressSerializer(weekly_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def monthly_statistics(self, request):
        """获取月度统计"""
        user = request.user
        months = int(request.query_params.get('months', 6))
        
        monthly_data = []
        for i in range(months):
            # 计算月份
            target_date = timezone.now().date().replace(day=1) - timedelta(days=i * 30)
            month_start = target_date.replace(day=1)
            
            # 计算月末
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            # 月内学习记录
            month_records = WordLearningRecord.objects.filter(
                session__user=user,
                created_at__date__range=[month_start, month_end]
            )
            
            # 月内学习会话
            month_sessions = LearningSession.objects.filter(
                user=user,
                start_time__date__range=[month_start, month_end]
            )
            
            # 统计数据
            total_words = month_records.values('word').distinct().count()
            total_sessions = month_sessions.count()
            
            # 总学习时间
            total_time = 0
            for session in month_sessions.filter(end_time__isnull=False):
                if session.end_time and session.start_time:
                    duration = session.end_time - session.start_time
                    total_time += duration.total_seconds() / 60
            
            # 平均正确率
            total_records = month_records.count()
            correct_records = month_records.filter(is_correct=True).count()
            average_accuracy = (correct_records / total_records * 100) if total_records > 0 else 0
            
            # 活跃天数
            active_days = month_records.values('created_at__date').distinct().count()
            
            monthly_data.append({
                'month': month_start.strftime('%Y-%m'),
                'total_words': total_words,
                'total_sessions': total_sessions,
                'total_time': round(total_time, 2),
                'average_accuracy': round(average_accuracy, 2),
                'active_days': active_days
            })
        
        monthly_data.reverse()  # 按时间正序排列
        serializer = MonthlyStatisticsSerializer(monthly_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mastery_distribution(self, request):
        """获取单词掌握分布"""
        user = request.user
        
        # 获取用户所有单词
        user_words = Word.objects.filter(user=user)
        total_words = user_words.count()
        
        if total_words == 0:
            return Response([])
        
        # 统计各掌握级别的单词数量
        distribution = {
            '未学习': 0,
            '初学': 0,
            '熟悉': 0,
            '掌握': 0,
            '精通': 0
        }
        
        # 根据学习记录统计掌握程度
        for word in user_words:
            records = WordLearningRecord.objects.filter(
                session__user=user,
                word=word
            )
            
            if not records.exists():
                distribution['未学习'] += 1
            else:
                correct_count = records.filter(is_correct=True).count()
                total_count = records.count()
                
                if correct_count == 0:
                    distribution['初学'] += 1
                elif correct_count < 3:
                    distribution['初学'] += 1
                elif correct_count < 6:
                    distribution['熟悉'] += 1
                elif correct_count < 10:
                    distribution['掌握'] += 1
                else:
                    distribution['精通'] += 1
        
        # 转换为序列化器格式
        result = []
        for level, count in distribution.items():
            percentage = (count / total_words * 100) if total_words > 0 else 0
            result.append({
                'mastery_level': level,
                'word_count': count,
                'percentage': round(percentage, 2)
            })
        
        serializer = WordMasteryDistributionSerializer(result, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def goal_progress(self, request):
        """获取学习目标进度"""
        user = request.user
        goals = LearningGoal.objects.filter(user=user, is_active=True)
        
        progress_data = []
        for goal in goals:
            # 目标单词数
            target_words = goal.target_words_count
            current_words = GoalWord.objects.filter(goal=goal).count()
            
            # 完成率
            completion_rate = (current_words / target_words * 100) if target_words > 0 else 0
            
            # 剩余天数
            today = timezone.now().date()
            days_remaining = (goal.end_date - today).days if goal.end_date > today else 0
            
            # 是否按计划进行
            total_days = (goal.end_date - goal.start_date).days
            elapsed_days = (today - goal.start_date).days
            expected_progress = (elapsed_days / total_days * 100) if total_days > 0 else 0
            is_on_track = completion_rate >= expected_progress
            
            progress_data.append({
                'goal_id': goal.pk,
                'goal_name': goal.name,
                'target_words': target_words,
                'current_words': current_words,
                'completion_rate': round(completion_rate, 2),
                'days_remaining': days_remaining,
                'is_on_track': is_on_track
            })
        
        serializer = LearningGoalProgressSerializer(progress_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出数据"""
        serializer = ExportDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        format_type = request.data.get('format', 'csv')
        data_type = request.data.get('data_type')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')
        
        user = request.user
        
        # 根据数据类型获取数据
        if data_type == 'words':
            queryset = Word.objects.filter(user=user)
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
            
            data = list(queryset.values(
                'word', 'translation', 'pronunciation', 'difficulty_level',
                'mastery_level', 'created_at'
            ))
            
        elif data_type == 'sessions':
            queryset = LearningSession.objects.filter(user=user)
            if date_from:
                queryset = queryset.filter(start_time__date__gte=date_from)
            if date_to:
                queryset = queryset.filter(start_time__date__lte=date_to)
            
            data = list(queryset.values(
                'start_time', 'end_time', 'words_studied',
                'correct_answers', 'total_answers'
            ))
            
        elif data_type == 'records':
            queryset = WordLearningRecord.objects.filter(session__user=user)
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
            
            data = list(queryset.values(
                'word__word', 'user_answer', 'is_correct',
                'response_time', 'created_at'
            ))
            
        else:
            return Response(
                {'error': '不支持的数据类型'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 根据格式导出
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{data_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
            
            if data:
                writer = csv.DictWriter(response, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return response
            
        elif format_type == 'json':
            response = HttpResponse(
                json.dumps(data, default=str, ensure_ascii=False, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="{data_type}_{timezone.now().strftime("%Y%m%d")}.json"'
            return response
            
        else:
            return Response(
                {'error': '不支持的导出格式'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def comprehensive(self, request):
        """获取综合分析数据"""
        # 调用其他方法获取各部分数据
        overview_response = self.overview(request)
        weekly_response = self.weekly_progress(request)
        monthly_response = self.monthly_statistics(request)
        mastery_response = self.mastery_distribution(request)
        goal_response = self.goal_progress(request)
        
        # 组合数据
        comprehensive_data = {
            'overview': overview_response.data,
            'weekly_progress': weekly_response.data,
            'monthly_statistics': monthly_response.data,
            'mastery_distribution': mastery_response.data,
            'goal_progress': goal_response.data,
            'study_patterns': [],  # 可以后续扩展
            'weekday_activity': [],  # 可以后续扩展
            'difficulty_analysis': [],  # 可以后续扩展
            'learning_trends': []  # 可以后续扩展
        }
        
        return Response(comprehensive_data)