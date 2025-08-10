"""
数据迁移命令：整合Teaching与Vocabulary_Manager重叠功能
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
import logging

from apps.teaching.models import (
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
    DailyStudyRecord
)
from apps.teaching.unified_models import (
    UnifiedLearningGoal,
    UnifiedGoalWord,
    UnifiedLearningSession,
    UnifiedWordProgress,
    UnifiedLearningPlan,
    UnifiedDailyRecord
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '迁移和整合Teaching与Vocabulary_Manager的重叠功能数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='执行干运行，不实际修改数据',
        )
        parser.add_argument(
            '--merge-duplicates',
            action='store_true',
            help='合并重复的学习目标数据',
        )
        parser.add_argument(
            '--migrate-vocab-manager',
            action='store_true',
            help='迁移Vocabulary_Manager数据到统一模型',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.stdout.write(
            self.style.SUCCESS(
                f"开始数据迁移 {'(干运行模式)' if self.dry_run else ''}"
            )
        )

        try:
            if options['migrate_vocab_manager']:
                self.migrate_vocabulary_manager_data()
            
            if options['merge_duplicates']:
                self.merge_duplicate_learning_goals()
            
            self.create_unified_models()
            
            self.stdout.write(
                self.style.SUCCESS('数据迁移完成！')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'数据迁移失败: {str(e)}')
            )
            logger.error(f'数据迁移失败: {str(e)}', exc_info=True)

    def migrate_vocabulary_manager_data(self):
        """迁移Vocabulary_Manager数据到Teaching应用"""
        self.stdout.write('正在迁移Vocabulary_Manager数据...')
        
        migrated_goals = 0
        migrated_sessions = 0
        migrated_progress = 0
        
        # 迁移学习目标
        vocab_goals = VocabLearningGoal.objects.all()
        for vocab_goal in vocab_goals:
            # 检查是否已经存在相同的目标
            existing_goal = TeachingLearningGoal.objects.filter(
                user=vocab_goal.user,
                name=vocab_goal.name
            ).first()
            
            if existing_goal:
                self.stdout.write(f'跳过重复目标: {vocab_goal.name}')
                continue
            
            if not self.dry_run:
                # 创建新的Teaching学习目标
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
            
            migrated_goals += 1
        
        # 迁移学习会话
        study_sessions = StudySession.objects.all()
        for study_session in study_sessions:
            if study_session.learning_goal:
                # 查找对应的Teaching目标
                teaching_goal = TeachingLearningGoal.objects.filter(
                    user=study_session.user,
                    name=study_session.learning_goal.name
                ).first()
                
                if teaching_goal and not self.dry_run:
                    TeachingLearningSession.objects.create(
                        user=study_session.user,
                        goal=teaching_goal,
                        start_time=study_session.start_time,
                        end_time=study_session.end_time,
                        words_studied=study_session.words_studied,
                        correct_answers=study_session.words_learned,
                        total_answers=study_session.words_studied
                    )
                
                migrated_sessions += 1
        
        # 迁移单词学习进度
        word_progress_records = WordLearningProgress.objects.all()
        for progress in word_progress_records:
            # 查找对应的Teaching目标
            teaching_goal = TeachingLearningGoal.objects.filter(
                user=progress.user,
                name=progress.learning_goal.name
            ).first()
            
            if teaching_goal and not self.dry_run:
                # 创建模拟的学习记录
                session = TeachingLearningSession.objects.filter(
                    user=progress.user,
                    goal=teaching_goal
                ).first()
                
                if session:
                    for i in range(progress.review_count):
                        TeachingWordLearningRecord.objects.create(
                            session=session,
                            goal=teaching_goal,
                            word=progress.word,
                            user_answer='migrated',
                            is_correct=True,
                            response_time=1.0,
                            created_at=progress.first_learned_date + timedelta(days=i)
                        )
            
            migrated_progress += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'迁移完成: {migrated_goals}个目标, {migrated_sessions}个会话, {migrated_progress}个进度记录'
            )
        )

    def merge_duplicate_learning_goals(self):
        """合并重复的学习目标"""
        self.stdout.write('正在合并重复的学习目标...')
        
        # 查找重复的学习目标
        from django.db.models import Count
        duplicates = TeachingLearningGoal.objects.values('user', 'name').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        merged_count = 0
        for duplicate in duplicates:
            user_goals = TeachingLearningGoal.objects.filter(
                user_id=duplicate['user'],
                name=duplicate['name']
            ).order_by('created_at')
            
            # 保留最早创建的目标
            primary_goal = user_goals.first()
            duplicate_goals = user_goals[1:]
            
            self.stdout.write(f'合并目标: {primary_goal.name} (保留) + {len(duplicate_goals)}个重复')
            
            if not self.dry_run:
                with transaction.atomic():
                    for dup_goal in duplicate_goals:
                        # 迁移目标单词
                        GoalWord.objects.filter(goal=dup_goal).update(goal=primary_goal)
                        
                        # 迁移学习会话
                        TeachingLearningSession.objects.filter(goal=dup_goal).update(goal=primary_goal)
                        
                        # 迁移学习记录
                        TeachingWordLearningRecord.objects.filter(goal=dup_goal).update(goal=primary_goal)
                        
                        # 迁移学习计划
                        TeachingLearningPlan.objects.filter(goal=dup_goal).update(goal=primary_goal)
                        
                        # 删除重复目标
                        dup_goal.delete()
            
            merged_count += len(duplicate_goals)
        
        self.stdout.write(
            self.style.SUCCESS(f'合并完成: 处理了{merged_count}个重复目标')
        )

    def create_unified_models(self):
        """创建统一模型数据"""
        self.stdout.write('正在创建统一模型数据...')
        
        created_goals = 0
        created_sessions = 0
        created_progress = 0
        
        # 创建统一学习目标
        teaching_goals = TeachingLearningGoal.objects.all()
        for goal in teaching_goals:
            existing_unified = UnifiedLearningGoal.objects.filter(
                user=goal.user,
                name=goal.name
            ).first()
            
            if existing_unified:
                continue
            
            if not self.dry_run:
                unified_goal = UnifiedLearningGoal.objects.create(
                    user=goal.user,
                    name=goal.name,
                    description=goal.description,
                    goal_type='custom',
                    target_words_count=goal.target_words_count,
                    start_date=goal.start_date,
                    end_date=goal.end_date,
                    is_active=goal.is_active,
                    is_current=goal.is_active,  # 简化处理
                    created_at=goal.created_at,
                    updated_at=goal.updated_at
                )
                
                # 关联单词集和词汇表
                unified_goal.word_sets.set(goal.word_sets.all())
                unified_goal.vocabulary_lists.set(goal.vocabulary_lists.all())
                
                # 创建目标单词关联
                goal_words = GoalWord.objects.filter(goal=goal)
                for goal_word in goal_words:
                    UnifiedGoalWord.objects.get_or_create(
                        goal=unified_goal,
                        word=goal_word.word,
                        defaults={'added_at': goal_word.added_at}
                    )
                
                # 创建学习会话
                sessions = TeachingLearningSession.objects.filter(goal=goal)
                for session in sessions:
                    UnifiedLearningSession.objects.create(
                        user=session.user,
                        goal=unified_goal,
                        start_time=session.start_time,
                        end_time=session.end_time,
                        words_studied=session.words_studied,
                        correct_answers=session.correct_answers,
                        total_answers=session.total_answers
                    )
                    created_sessions += 1
                
                # 创建单词学习进度
                records = TeachingWordLearningRecord.objects.filter(goal=goal)
                word_progress = {}
                
                for record in records:
                    word_id = record.word.id
                    if word_id not in word_progress:
                        word_progress[word_id] = {
                            'word': record.word,
                            'review_count': 0,
                            'last_review': None,
                            'is_correct_count': 0
                        }
                    
                    word_progress[word_id]['review_count'] += 1
                    if record.is_correct:
                        word_progress[word_id]['is_correct_count'] += 1
                        word_progress[word_id]['last_review'] = record.created_at
                
                for word_id, progress_data in word_progress.items():
                    is_mastered = progress_data['is_correct_count'] >= 6
                    UnifiedWordProgress.objects.create(
                        user=goal.user,
                        goal=unified_goal,
                        word=progress_data['word'],
                        review_count=progress_data['is_correct_count'],
                        last_review_date=progress_data['last_review'],
                        is_mastered=is_mastered,
                        mastered_date=progress_data['last_review'] if is_mastered else None
                    )
                    created_progress += 1
            
            created_goals += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'统一模型创建完成: {created_goals}个目标, {created_sessions}个会话, {created_progress}个进度记录'
            )
        )