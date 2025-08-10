"""
统一学习管理功能的单元测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import patch

from apps.teaching.services import UnifiedLearningService, DataMigrationService, LearningProgressService
from apps.teaching.unified_models import (
    UnifiedLearningGoal,
    UnifiedGoalWord,
    UnifiedLearningSession,
    UnifiedWordProgress,
    UnifiedLearningPlan
)
from apps.teaching.models import (
    LearningGoal as TeachingLearningGoal,
    GoalWord,
    LearningSession as TeachingLearningSession,
    WordLearningRecord as TeachingWordLearningRecord
)
from apps.vocabulary_manager.models import (
    LearningGoal as VocabLearningGoal,
    StudySession,
    WordLearningProgress
)
from apps.words.models import Word, WordSet, VocabularyList

User = get_user_model()


class UnifiedLearningServiceTest(TestCase):
    """统一学习服务测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = UnifiedLearningService(self.user)
        
        # 创建测试单词
        self.word1 = Word.objects.create(
            word='test1',
            definition='测试单词1',
            user=self.user
        )
        self.word2 = Word.objects.create(
            word='test2',
            definition='测试单词2',
            user=self.user
        )
        
        # 创建测试单词集
        self.word_set = WordSet.objects.create(
            name='测试单词集',
            description='测试用单词集',
            user=self.user
        )
        self.word_set.words.add(self.word1, self.word2)
    
    def test_create_unified_learning_goal(self):
        """测试创建统一学习目标"""
        goal = self.service.create_unified_learning_goal(
            name='测试目标',
            description='测试描述',
            target_words_count=50,
            word_sets=[self.word_set.id]
        )
        
        self.assertEqual(goal.name, '测试目标')
        self.assertEqual(goal.description, '测试描述')
        self.assertEqual(goal.target_words_count, 50)
        self.assertEqual(goal.user, self.user)
        self.assertTrue(goal.is_active)
        
        # 检查单词集关联
        self.assertIn(self.word_set, goal.word_sets.all())
        
        # 检查单词同步
        goal_words = GoalWord.objects.filter(goal=goal)
        self.assertEqual(goal_words.count(), 2)
    
    def test_get_learning_goals(self):
        """测试获取学习目标列表"""
        # 创建测试目标
        goal1 = TeachingLearningGoal.objects.create(
            user=self.user,
            name='目标1',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_active=True
        )
        goal2 = TeachingLearningGoal.objects.create(
            user=self.user,
            name='目标2',
            target_words_count=50,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_active=False
        )
        
        # 测试获取所有目标
        all_goals = self.service.get_learning_goals()
        self.assertEqual(len(all_goals), 2)
        
        # 测试只获取活跃目标
        active_goals = self.service.get_learning_goals(active_only=True)
        self.assertEqual(len(active_goals), 1)
        self.assertEqual(active_goals[0].name, '目标1')
    
    def test_start_learning_session(self):
        """测试开始学习会话"""
        goal = TeachingLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        session = self.service.start_learning_session(goal.id)
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.goal, goal)
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.end_time)
    
    def test_end_learning_session(self):
        """测试结束学习会话"""
        goal = TeachingLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        session = TeachingLearningSession.objects.create(
            user=self.user,
            goal=goal
        )
        
        ended_session = self.service.end_learning_session(session.id)
        
        self.assertIsNotNone(ended_session.end_time)
    
    def test_record_word_learning(self):
        """测试记录单词学习"""
        goal = TeachingLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        session = TeachingLearningSession.objects.create(
            user=self.user,
            goal=goal
        )
        
        record = self.service.record_word_learning(
            session_id=session.id,
            word_id=self.word1.id,
            user_answer='test answer',
            is_correct=True,
            response_time=2.5
        )
        
        self.assertEqual(record.session, session)
        self.assertEqual(record.goal, goal)
        self.assertEqual(record.word, self.word1)
        self.assertEqual(record.user_answer, 'test answer')
        self.assertTrue(record.is_correct)
        self.assertEqual(record.response_time, 2.5)
        
        # 检查会话统计更新
        session.refresh_from_db()
        self.assertEqual(session.total_answers, 1)
        self.assertEqual(session.correct_answers, 1)
    
    def test_get_learning_statistics(self):
        """测试获取学习统计"""
        # 创建测试数据
        goal = TeachingLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_active=True
        )
        
        session = TeachingLearningSession.objects.create(
            user=self.user,
            goal=goal,
            end_time=timezone.now()
        )
        
        TeachingWordLearningRecord.objects.create(
            session=session,
            goal=goal,
            word=self.word1,
            user_answer='test',
            is_correct=True,
            response_time=1.0
        )
        
        stats = self.service.get_learning_statistics()
        
        self.assertEqual(stats['total_goals'], 1)
        self.assertEqual(stats['active_goals'], 1)
        self.assertEqual(stats['total_sessions'], 1)
        self.assertEqual(stats['completed_sessions'], 1)
        self.assertEqual(stats['total_records'], 1)
        self.assertEqual(stats['correct_records'], 1)
        self.assertEqual(stats['accuracy_rate'], 100.0)


class DataMigrationServiceTest(TestCase):
    """数据迁移服务测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试单词集
        self.word_set = WordSet.objects.create(
            name='测试单词集',
            description='测试用单词集',
            user=self.user
        )
    
    @patch('apps.vocabulary_manager.models.VocabularyList')
    def test_migrate_vocabulary_manager_to_teaching(self, mock_vocab_list):
        """测试从Vocabulary_Manager迁移数据到Teaching"""
        # 创建Vocabulary_Manager测试数据
        vocab_goal = VocabLearningGoal.objects.create(
            user=self.user,
            name='词汇目标',
            description='测试词汇目标',
            goal_type='word_set',
            word_set=self.word_set,
            is_current=True,
            total_words=10
        )
        
        # 执行迁移
        migrated_count = DataMigrationService.migrate_vocabulary_manager_to_teaching()
        
        # 验证迁移结果
        self.assertGreaterEqual(migrated_count, 1)
        
        teaching_goal = TeachingLearningGoal.objects.filter(
            user=self.user,
            name='词汇目标'
        ).first()
        
        self.assertIsNotNone(teaching_goal)
        self.assertEqual(teaching_goal.description, '测试词汇目标')
        self.assertTrue(teaching_goal.is_active)
    
    def test_merge_duplicate_learning_data(self):
        """测试合并重复学习数据"""
        # 创建重复的学习目标
        goal1 = TeachingLearningGoal.objects.create(
            user=self.user,
            name='重复目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        goal2 = TeachingLearningGoal.objects.create(
            user=self.user,
            name='重复目标',
            target_words_count=50,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        # 为第二个目标创建一些数据
        word = Word.objects.create(
            word='test',
            definition='测试',
            user=self.user
        )
        
        GoalWord.objects.create(goal=goal2, word=word)
        
        # 执行合并
        duplicates = DataMigrationService.merge_duplicate_learning_data()
        
        # 验证合并结果
        remaining_goals = TeachingLearningGoal.objects.filter(
            user=self.user,
            name='重复目标'
        )
        self.assertEqual(remaining_goals.count(), 1)
        
        # 验证数据已迁移到保留的目标
        remaining_goal = remaining_goals.first()
        self.assertEqual(remaining_goal.id, goal1.id)  # 应该保留最早创建的
        
        # 验证关联数据已迁移
        goal_words = GoalWord.objects.filter(goal=remaining_goal)
        self.assertEqual(goal_words.count(), 1)


class LearningProgressServiceTest(TestCase):
    """学习进度服务测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = LearningProgressService(self.user)
        
        self.goal = TeachingLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.word = Word.objects.create(
            word='test',
            definition='测试单词',
            user=self.user
        )
    
    @patch('apps.vocabulary_manager.models.WordLearningProgress')
    def test_update_word_progress_with_existing_progress(self, mock_progress_model):
        """测试更新已存在的单词学习进度"""
        # 模拟已存在的进度记录
        mock_progress = mock_progress_model.objects.get.return_value
        mock_progress.review_count = 3
        mock_progress.is_mastered = False
        mock_progress.is_forgotten = False
        mock_progress.last_review_date = timezone.now()
        
        # 测试添加复习
        result = self.service.update_word_progress(
            goal_id=self.goal.id,
            word_id=self.word.id,
            action='review'
        )
        
        # 验证调用了add_review方法
        mock_progress.add_review.assert_called_once()
    
    def test_update_word_progress_without_existing_progress(self):
        """测试更新不存在进度记录的单词"""
        # 创建一些学习记录来模拟进度
        session = TeachingLearningSession.objects.create(
            user=self.user,
            goal=self.goal
        )
        
        # 创建正确的学习记录
        for i in range(3):
            TeachingWordLearningRecord.objects.create(
                session=session,
                goal=self.goal,
                word=self.word,
                user_answer='correct',
                is_correct=True,
                response_time=1.0
            )
        
        # 创建错误的学习记录
        TeachingWordLearningRecord.objects.create(
            session=session,
            goal=self.goal,
            word=self.word,
            user_answer='wrong',
            is_correct=False,
            response_time=2.0
        )
        
        result = self.service.update_word_progress(
            goal_id=self.goal.id,
            word_id=self.word.id,
            action='review'
        )
        
        # 验证返回的进度数据
        self.assertEqual(result['review_count'], 3)
        self.assertFalse(result['is_mastered'])
        self.assertFalse(result['is_forgotten'])
        self.assertEqual(result['status'], 'review_3')


class UnifiedModelsTest(TestCase):
    """统一模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.word = Word.objects.create(
            word='test',
            definition='测试单词',
            user=self.user
        )
    
    def test_unified_learning_goal_creation(self):
        """测试统一学习目标创建"""
        goal = UnifiedLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            description='测试描述',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_current=True
        )
        
        self.assertEqual(goal.name, '测试目标')
        self.assertEqual(goal.user, self.user)
        self.assertTrue(goal.is_current)
        self.assertTrue(goal.is_active)
    
    def test_unified_learning_goal_current_exclusivity(self):
        """测试统一学习目标的当前状态互斥性"""
        goal1 = UnifiedLearningGoal.objects.create(
            user=self.user,
            name='目标1',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_current=True
        )
        
        goal2 = UnifiedLearningGoal.objects.create(
            user=self.user,
            name='目标2',
            target_words_count=50,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_current=True
        )
        
        # 刷新第一个目标
        goal1.refresh_from_db()
        
        # 验证只有最新设置的目标是当前目标
        self.assertFalse(goal1.is_current)
        self.assertTrue(goal2.is_current)
    
    def test_unified_word_progress_status(self):
        """测试统一单词进度状态"""
        goal = UnifiedLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        progress = UnifiedWordProgress.objects.create(
            user=self.user,
            goal=goal,
            word=self.word,
            review_count=3
        )
        
        self.assertEqual(progress.status, 'review_3')
        
        # 测试掌握状态
        progress.is_mastered = True
        progress.save()
        self.assertEqual(progress.status, 'mastered')
        
        # 测试遗忘状态
        progress.is_mastered = False
        progress.is_forgotten = True
        progress.save()
        self.assertEqual(progress.status, 'forgotten')
    
    def test_unified_learning_session_properties(self):
        """测试统一学习会话属性"""
        goal = UnifiedLearningGoal.objects.create(
            user=self.user,
            name='测试目标',
            target_words_count=100,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        session = UnifiedLearningSession.objects.create(
            user=self.user,
            goal=goal,
            words_studied=10,
            words_learned=8,
            correct_answers=15,
            total_answers=20
        )
        
        # 测试正确率
        self.assertEqual(session.accuracy_rate, 75.0)
        
        # 测试学习效率
        self.assertEqual(session.learning_efficiency, 80.0)
        
        # 测试时长（未结束会话）
        self.assertEqual(session.duration, 0)
        
        # 结束会话并测试时长
        session.end_session()
        self.assertGreater(session.duration, 0)