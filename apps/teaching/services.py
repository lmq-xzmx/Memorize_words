"""
统一学习管理服务层
整合Teaching与Vocabulary_Manager的重叠功能
"""
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from typing import Dict, List, Optional, Union

from .models import (
    LearningGoal as TeachingLearningGoal,
    GoalWord,
    LearningSession as TeachingLearningSession,
    WordLearningRecord as TeachingWordLearningRecord,
    LearningPlan as TeachingLearningPlan
)
from apps.vocabulary_manager.models import (
    LearningGoal as VocabLearningGoal,
    LearningPlan as VocabLearningPlan,
    StudySession,
    WordLearningProgress,
    DailyStudyRecord,
    UserStreak
)
from apps.words.models import Word, WordSet, VocabularyList

User = get_user_model()


class UnifiedLearningService:
    """统一学习管理服务"""
    
    def __init__(self, user: User):
        self.user = user
    
    # 学习目标管理
    def create_unified_learning_goal(self, 
                                   name: str,
                                   description: str = "",
                                   target_words_count: int = 100,
                                   start_date: date = None,
                                   end_date: date = None,
                                   word_sets: List[int] = None,
                                   vocabulary_lists: List[int] = None) -> TeachingLearningGoal:
        """创建统一的学习目标"""
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        with transaction.atomic():
            # 创建Teaching应用的学习目标
            goal = TeachingLearningGoal.objects.create(
                user=self.user,
                name=name,
                description=description,
                target_words_count=target_words_count,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            # 关联单词集和词汇表
            if word_sets:
                word_set_objects = WordSet.objects.filter(id__in=word_sets)
                goal.word_sets.set(word_set_objects)
            
            if vocabulary_lists:
                vocab_list_objects = VocabularyList.objects.filter(id__in=vocabulary_lists)
                goal.vocabulary_lists.set(vocab_list_objects)
            
            # 同步单词到目标
            goal.sync_words_from_sets_and_lists()
            
            return goal
    
    def get_learning_goals(self, active_only: bool = False) -> List[TeachingLearningGoal]:
        """获取学习目标列表"""
        queryset = TeachingLearningGoal.objects.filter(user=self.user)
        if active_only:
            queryset = queryset.filter(is_active=True)
        return list(queryset.order_by('-created_at'))
    
    def get_goal_progress(self, goal_id: int) -> Dict:
        """获取学习目标进度"""
        try:
            goal = TeachingLearningGoal.objects.get(id=goal_id, user=self.user)
            return goal.get_progress_stats()
        except TeachingLearningGoal.DoesNotExist:
            return {}
    
    # 学习会话管理
    def start_learning_session(self, goal_id: int) -> TeachingLearningSession:
        """开始学习会话"""
        goal = TeachingLearningGoal.objects.get(id=goal_id, user=self.user)
        
        # 结束之前未结束的会话
        active_sessions = TeachingLearningSession.objects.filter(
            user=self.user,
            end_time__isnull=True
        )
        for session in active_sessions:
            session.end_time = timezone.now()
            session.save()
        
        # 创建新会话
        session = TeachingLearningSession.objects.create(
            user=self.user,
            goal=goal
        )
        
        return session
    
    def end_learning_session(self, session_id: int) -> TeachingLearningSession:
        """结束学习会话"""
        session = TeachingLearningSession.objects.get(
            id=session_id, 
            user=self.user
        )
        
        if not session.end_time:
            session.end_time = timezone.now()
            session.save()
            
            # 更新用户连续学习记录
            self._update_user_streak()
        
        return session
    
    def record_word_learning(self,
                           session_id: int,
                           word_id: int,
                           user_answer: str,
                           is_correct: bool,
                           response_time: float) -> TeachingWordLearningRecord:
        """记录单词学习"""
        session = TeachingLearningSession.objects.get(
            id=session_id,
            user=self.user
        )
        word = Word.objects.get(id=word_id)
        
        # 创建学习记录
        record = TeachingWordLearningRecord.objects.create(
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
    
    # 学习计划管理
    def create_learning_plan(self,
                           goal_id: int,
                           plan_type: str = 'daily',
                           words_per_day: int = 10,
                           review_interval: int = 1) -> TeachingLearningPlan:
        """创建学习计划"""
        goal = TeachingLearningGoal.objects.get(id=goal_id, user=self.user)
        
        plan = TeachingLearningPlan.objects.create(
            goal=goal,
            plan_type=plan_type,
            words_per_day=words_per_day,
            review_interval=review_interval,
            is_active=True
        )
        
        return plan
    
    # 统计和分析
    def get_learning_statistics(self) -> Dict:
        """获取学习统计数据"""
        # 学习目标统计
        goals = TeachingLearningGoal.objects.filter(user=self.user)
        total_goals = goals.count()
        active_goals = goals.filter(is_active=True).count()
        
        # 学习会话统计
        sessions = TeachingLearningSession.objects.filter(user=self.user)
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(end_time__isnull=False).count()
        
        # 学习记录统计
        records = TeachingWordLearningRecord.objects.filter(session__user=self.user)
        total_records = records.count()
        correct_records = records.filter(is_correct=True).count()
        accuracy_rate = (correct_records / total_records * 100) if total_records > 0 else 0
        
        # 总学习时间
        total_study_minutes = 0
        for session in completed_sessions:
            if session.end_time and session.start_time:
                duration = session.end_time - session.start_time
                total_study_minutes += duration.total_seconds() / 60
        
        return {
            'total_goals': total_goals,
            'active_goals': active_goals,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_records': total_records,
            'correct_records': correct_records,
            'accuracy_rate': round(accuracy_rate, 2),
            'total_study_time': round(total_study_minutes, 2),
        }
    
    def get_kanban_data(self, goal_id: int) -> Dict:
        """获取九宫格看板数据"""
        goal = TeachingLearningGoal.objects.get(id=goal_id, user=self.user)
        return goal.get_progress_stats()
    
    # 私有方法
    def _update_user_streak(self):
        """更新用户连续学习记录"""
        try:
            streak, created = UserStreak.objects.get_or_create(
                user=self.user,
                defaults={
                    'current_streak': 1,
                    'longest_streak': 1,
                    'last_study_date': date.today(),
                    'total_study_days': 1
                }
            )
            
            if not created:
                streak.update_streak(date.today())
        except Exception:
            # 如果UserStreak模型不存在，忽略错误
            pass


class DataMigrationService:
    """数据迁移服务"""
    
    @staticmethod
    def migrate_vocabulary_manager_to_teaching():
        """将Vocabulary_Manager数据迁移到Teaching应用"""
        migrated_count = 0
        
        # 迁移学习目标
        vocab_goals = VocabLearningGoal.objects.all()
        
        for vocab_goal in vocab_goals:
            # 检查是否已经迁移
            existing_goal = TeachingLearningGoal.objects.filter(
                user=vocab_goal.user,
                name=vocab_goal.name
            ).first()
            
            if existing_goal:
                continue
            
            # 创建新的学习目标
            teaching_goal = TeachingLearningGoal.objects.create(
                user=vocab_goal.user,
                name=vocab_goal.name,
                description=vocab_goal.description,
                target_words_count=vocab_goal.total_words,
                start_date=vocab_goal.created_at.date(),
                end_date=vocab_goal.created_at.date() + timedelta(days=30),
                is_active=vocab_goal.is_current,
                created_at=vocab_goal.created_at,
                updated_at=vocab_goal.updated_at
            )
            
            # 关联单词集或词汇表
            if vocab_goal.word_set:
                teaching_goal.word_sets.add(vocab_goal.word_set)
            if vocab_goal.vocabulary_list:
                teaching_goal.vocabulary_lists.add(vocab_goal.vocabulary_list)
            
            # 同步单词
            teaching_goal.sync_words_from_sets_and_lists()
            
            migrated_count += 1
        
        return migrated_count
    
    @staticmethod
    def merge_duplicate_learning_data():
        """合并重复的学习数据"""
        # 查找重复的学习目标
        duplicates = []
        
        goals = TeachingLearningGoal.objects.values('user', 'name').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for goal_info in goals:
            user_goals = TeachingLearningGoal.objects.filter(
                user_id=goal_info['user'],
                name=goal_info['name']
            ).order_by('created_at')
            
            # 保留最早创建的目标，合并其他目标的数据
            primary_goal = user_goals.first()
            duplicate_goals = user_goals[1:]
            
            for dup_goal in duplicate_goals:
                # 迁移目标单词
                GoalWord.objects.filter(goal=dup_goal).update(goal=primary_goal)
                
                # 迁移学习会话
                TeachingLearningSession.objects.filter(goal=dup_goal).update(goal=primary_goal)
                
                # 迁移学习记录
                TeachingWordLearningRecord.objects.filter(goal=dup_goal).update(goal=primary_goal)
                
                # 删除重复目标
                dup_goal.delete()
                duplicates.append(dup_goal.name)
        
        return duplicates


class LearningProgressService:
    """学习进度服务"""
    
    def __init__(self, user: User):
        self.user = user
    
    def update_word_progress(self, goal_id: int, word_id: int, action: str) -> Dict:
        """更新单词学习进度"""
        goal = TeachingLearningGoal.objects.get(id=goal_id, user=self.user)
        word = Word.objects.get(id=word_id)
        
        # 获取或创建单词学习进度
        try:
            progress = WordLearningProgress.objects.get(
                user=self.user,
                learning_goal_id=goal_id,
                word=word
            )
        except WordLearningProgress.DoesNotExist:
            # 如果WordLearningProgress不存在，通过学习记录来模拟进度
            records = TeachingWordLearningRecord.objects.filter(
                goal=goal,
                word=word,
                session__user=self.user
            )
            
            review_count = records.filter(is_correct=True).count()
            last_review = records.order_by('-created_at').first()
            
            return {
                'review_count': review_count,
                'is_mastered': review_count >= 6,
                'is_forgotten': False,
                'status': f'review_{min(review_count, 6)}' if review_count > 0 else 'not_started',
                'last_review_date': last_review.created_at if last_review else None
            }
        
        # 根据操作更新进度
        if action == 'review':
            progress.add_review()
        elif action == 'master':
            progress.is_mastered = True
            progress.mastered_date = timezone.now()
            progress.save()
        elif action == 'forget':
            progress.mark_as_forgotten()
        elif action == 'reset':
            progress.reset_progress()
        
        return {
            'review_count': progress.review_count,
            'is_mastered': progress.is_mastered,
            'is_forgotten': progress.is_forgotten,
            'status': progress.status,
            'last_review_date': progress.last_review_date
        }