from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    LearningGoal,
    LearningPlan,
    LearningSession,
    WordLearningRecord,
    GuidedPracticeSession,
    GuidedPracticeQuestion,
    GuidedPracticeAnswer,
    GoalWord,
    DailyStudyRecord
)
from apps.words.models import Word, VocabularyList, WordSet
from typing import Dict, List, Optional
import datetime
import random

User = get_user_model()

class TeachingLearningService:
    """教学应用学习服务"""
    
    def __init__(self, user):
        self.user = user
    
    def create_learning_goal(self, name: str, description: str = '', 
                           goal_type: str = 'vocabulary',
                           target_words_count: int = 100,
                           end_date=None) -> LearningGoal:
        """创建学习目标"""
        if end_date is None:
            end_date = timezone.now().date() + datetime.timedelta(days=30)
        
        goal = LearningGoal.objects.create(
            user=self.user,
            name=name,
            description=description,
            goal_type=goal_type,
            target_words_count=target_words_count,
            end_date=end_date,
            is_active=True
        )
        
        return goal
    
    def create_learning_plan(self, goal_id: int, plan_type: str = 'daily',
                           words_per_day: int = 10,
                           review_interval: int = 1) -> LearningPlan:
        """创建学习计划"""
        goal = LearningGoal.objects.get(id=goal_id, user=self.user)
        
        plan = LearningPlan.objects.create(
            goal=goal,
            plan_type=plan_type,
            words_per_day=words_per_day,
            review_interval=review_interval,
            is_active=True
        )
        
        return plan
    
    def get_today_learning_schedule(self, plan_id: int):
        """获取今日学习安排"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, goal__user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        today = datetime.date.today()
        
        # 检查今天是否为学习日
        if not plan.is_study_day_for_plan(today):
            return {
                'is_study_day': False,
                'target_words': 0,
                'message': f"今天是休息日（{plan.get_plan_type_display_with_description()}）"
            }
        
        # 获取今日学习目标
        target_words = plan.get_today_words_target()
        
        return {
            'is_study_day': True,
            'target_words': target_words,
            'plan_type': plan.plan_type,
            'plan_description': plan.get_plan_type_display_with_description(),
            'review_interval': plan.review_interval
        }
    
    def start_learning_session(self, goal_id: int) -> LearningSession:
        """开始学习会话"""
        goal = LearningGoal.objects.get(id=goal_id, user=self.user)
        
        session = LearningSession.objects.create(
            user=self.user,
            goal=goal
        )
        
        return session
    
    def end_learning_session(self, session_id: int) -> LearningSession:
        """结束学习会话"""
        session = LearningSession.objects.get(
            id=session_id, 
            user=self.user
        )
        
        session.end_time = timezone.now()
        session.save()
        
        return session
    
    def record_word_learning(self, session_id: int, word_id: int, 
                           user_answer: str, is_correct: bool,
                           response_time: float = 0.0) -> WordLearningRecord:
        """记录单词学习"""
        session = LearningSession.objects.get(id=session_id, user=self.user)
        word = Word.objects.get(id=word_id)
        
        record = WordLearningRecord.objects.create(
            session=session,
            goal=session.goal,
            word=word,
            user_answer=user_answer,
            is_correct=is_correct,
            response_time=response_time
        )
        
        # 更新会话统计
        session.total_answers += 1
        if is_correct:
            session.correct_answers += 1
        session.save()
        
        return record
    
    def get_learning_statistics(self) -> Dict:
        """获取学习统计"""
        goals = LearningGoal.objects.filter(user=self.user)
        sessions = LearningSession.objects.filter(user=self.user)
        
        stats = {
            'total_goals': goals.count(),
            'active_goals': goals.filter(is_active=True).count(),
            'total_sessions': sessions.count(),
            'total_study_time': sum(
                session.duration for session in sessions 
                if session.end_time
            ),
            'average_accuracy': 0
        }
        
        # 计算平均准确率
        total_answers = sum(session.total_answers for session in sessions)
        total_correct = sum(session.correct_answers for session in sessions)
        
        if total_answers > 0:
              stats['average_accuracy'] = int(round(
                  (total_correct / total_answers) * 100
              ))
        
        return stats
    
    def get_plan_effectiveness(self, plan_id: int):
        """获取学习计划效果分析"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, goal__user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        # 获取学习会话数据
        sessions = LearningSession.objects.filter(
            goal=plan.goal,
            user=self.user
        ).order_by('-start_time')
        
        if not sessions.exists():
            return {
                'plan': plan,
                'total_sessions': 0,
                'avg_accuracy': 0,
                'total_words_studied': 0,
                'avg_session_duration': 0,
                'effectiveness_score': 0
            }
        
        # 计算统计数据
        total_sessions = sessions.count()
        total_correct = sum(session.correct_answers for session in sessions)
        total_answers = sum(session.total_answers for session in sessions)
        total_words_studied = sum(session.words_studied for session in sessions)
        
        avg_accuracy = (total_correct / total_answers * 100) if total_answers > 0 else 0
        
        # 计算平均会话时长
        completed_sessions = sessions.filter(end_time__isnull=False)
        if completed_sessions.exists():
            total_duration = sum(
                session.duration for session in completed_sessions
            )
            avg_session_duration = total_duration / completed_sessions.count()
        else:
            avg_session_duration = 0
        
        # 计算效果评分（0-100）
        effectiveness_score = min(100, (
            avg_accuracy * 0.4 +  # 准确率权重40%
            min(100, total_words_studied / plan.words_per_day * 10) * 0.3 +  # 学习量权重30%
            min(100, total_sessions * 5) * 0.3  # 坚持度权重30%
        ))
        
        return {
            'plan': plan,
            'total_sessions': total_sessions,
            'avg_accuracy': round(avg_accuracy, 2),
            'total_words_studied': total_words_studied,
            'avg_session_duration': round(avg_session_duration, 2),
            'effectiveness_score': round(effectiveness_score, 2),
            'recent_sessions': sessions[:10]  # 最近10次会话
        }
    
    def sync_words_to_goal(self, goal: LearningGoal):
        """同步词汇表和单词集中的单词到目标"""
        # 获取所有相关单词
        words = set()
        
        # 从单词集获取单词
        for word_set in goal.word_sets.all():
            words.update(word_set.words.all())
        
        # 从词汇表获取单词
        for vocab_list in goal.vocabulary_lists.all():
            words.update(vocab_list.words.all())
        
        # 创建目标单词关联
        for word in words:
            GoalWord.objects.get_or_create(
                goal=goal,
                word=word
            )
        
        # 更新目标单词总数
        goal.target_words_count = max(goal.target_words_count, len(words))
        goal.save(update_fields=['target_words_count'])


class LearningPlanService:
    """学习计划服务类（从vocabulary_manager迁移）"""
    
    def __init__(self, user):
        self.user = user
    
    def create_learning_plan(self, learning_goal_id, plan_type='daily_progress', 
                           daily_target=10, start_date=None, end_date=None):
        """创建学习计划"""
        try:
            learning_goal = LearningGoal.objects.get(id=learning_goal_id, user=self.user)
        except LearningGoal.DoesNotExist:
            raise ValueError("学习目标不存在")
        
        if start_date is None:
            start_date = datetime.date.today()
        
        if end_date is None:
            # 根据总单词数和每日目标计算结束日期
            if plan_type == 'weekday':
                # 工作日模式：只计算工作日
                days_needed = (learning_goal.total_words // daily_target) * 7 // 5
            elif plan_type == 'weekend':
                # 周末模式：只计算周末
                days_needed = (learning_goal.total_words // daily_target) * 7 // 2
            else:
                # 其他模式：按每日计算
                days_needed = learning_goal.total_words // daily_target
            
            end_date = start_date + datetime.timedelta(days=max(days_needed, 1))
        
        with transaction.atomic():
            plan = LearningPlan.objects.create(
                user=self.user,
                goal=learning_goal,
                name=f"{learning_goal.name}学习计划",
                plan_type=plan_type,
                start_date=start_date,
                end_date=end_date,
                total_words=learning_goal.total_words,
                daily_target=daily_target,
                status='active'
            )
            
            # 初始化每日目标
            plan.update_daily_target()
            
        return plan
    
    def get_today_study_plan(self, plan_id):
        """获取今日学习计划"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        today = datetime.date.today()
        
        # 检查今天是否为学习日
        if not plan.is_study_day(today):
            return {
                'is_study_day': False,
                'target_words': 0,
                'message': f"今天是休息日（{plan.get_plan_type_display()}）"
            }
        
        # 获取或创建今日学习记录
        record, created = DailyStudyRecord.objects.get_or_create(
            user=self.user,
            learning_plan=plan,
            study_date=today,
            defaults={
                'target_words': plan.get_today_target(),
                'completed_words': 0
            }
        )
        
        return {
            'is_study_day': True,
            'target_words': record.target_words,
            'completed_words': record.completed_words,
            'remaining_words': record.target_words - record.completed_words,
            'completion_rate': record.completion_rate,
            'plan_type': plan.plan_type,
            'plan_type_display': plan.get_plan_type_display()
        }
    
    def update_study_progress(self, plan_id, completed_words, study_duration=None):
        """更新学习进度"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        today = datetime.date.today()
        
        with transaction.atomic():
            # 更新今日学习记录
            record, created = DailyStudyRecord.objects.get_or_create(
                user=self.user,
                learning_plan=plan,
                study_date=today,
                defaults={
                    'target_words': plan.get_today_target(),
                    'completed_words': 0
                }
            )
            
            record.completed_words = completed_words
            if study_duration:
                record.study_duration = study_duration
            record.save()
            
            # 更新学习目标的已学单词数
            plan.goal.learned_words += completed_words
            plan.goal.save(update_fields=['learned_words'])
            
            # 如果是动态调整模式，更新每日目标
            plan.update_daily_target()
            
            # 检查是否完成计划
            if plan.goal.learned_words >= plan.total_words:
                plan.status = 'completed'
                plan.save(update_fields=['status'])
        
        return record
    
    def get_plan_statistics(self, plan_id):
        """获取学习计划统计信息"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        # 获取学习记录
        records = DailyStudyRecord.objects.filter(
            learning_plan=plan
        ).order_by('study_date')
        
        total_study_days = records.count()
        total_completed_words = sum(record.completed_words for record in records)
        total_target_words = sum(record.target_words for record in records)
        
        # 计算平均完成率
        avg_completion_rate = 0
        if total_target_words > 0:
            avg_completion_rate = (total_completed_words / total_target_words) * 100
        
        # 计算学习进度
        progress_percentage = plan.goal.progress_percentage
        
        return {
            'plan': plan,
            'total_study_days': total_study_days,
            'total_completed_words': total_completed_words,
            'total_target_words': total_target_words,
            'avg_completion_rate': round(avg_completion_rate, 2),
            'progress_percentage': progress_percentage,
            'remaining_words': plan.total_words - plan.goal.learned_words,
            'remaining_days': (plan.end_date - datetime.date.today()).days,
            'records': records
        }
    
    def adjust_plan_schedule(self, plan_id, new_end_date=None, new_daily_target=None):
        """调整学习计划安排"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        with transaction.atomic():
            if new_end_date:
                plan.end_date = new_end_date
            
            if new_daily_target:
                plan.daily_target = new_daily_target
            
            plan.save()
            
            # 重新计算每日目标
            plan.update_daily_target()
        
        return plan
    
    def pause_plan(self, plan_id):
        """暂停学习计划"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        plan.status = 'paused'
        plan.save(update_fields=['status'])
        return plan
    
    def resume_plan(self, plan_id):
        """恢复学习计划"""
        try:
            plan = LearningPlan.objects.get(id=plan_id, user=self.user)
        except LearningPlan.DoesNotExist:
            raise ValueError("学习计划不存在")
        
        plan.status = 'active'
        plan.save(update_fields=['status'])
        
        # 重新计算每日目标
        plan.update_daily_target()
        return plan