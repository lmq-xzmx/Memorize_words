from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.words.models import (
    Word, WordResource, VocabularySource, VocabularyList,
    ImportedVocabulary
)
from apps.vocabulary_manager.models import UserStreak, StudySession

User = get_user_model()


class WordResourceModelTest(TestCase):
    """单词资源模型测试"""
    
    def setUp(self):
        self.resource_data = {
            'name': '测试音频',
            'resource_type': 'audio',
            'description': '测试音频文件'
        }
    
    def test_create_url_resource(self):
        """测试创建URL资源"""
        resource = WordResource.objects.create(
            name='测试链接',
            resource_type='url',
            url='https://example.com',
            description='测试链接资源'
        )
        self.assertEqual(resource.name, '测试链接')
        self.assertEqual(resource.resource_type, 'url')
        self.assertEqual(resource.url, 'https://example.com')
    
    def test_resource_str_representation(self):
        """测试资源字符串表示"""
        resource = WordResource.objects.create(**self.resource_data)
        self.assertEqual(str(resource), '测试音频')


class WordModelTest(TestCase):
    """单词模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.word_data = {
            'user': self.user,
            'word': 'hello',
            'phonetic': '/həˈloʊ/',
            'definition': '你好；问候',
            'part_of_speech': '感叹词',
            'example': 'Hello, how are you?',
            'difficulty_level': 1
        }
    
    def test_create_word(self):
        """测试创建单词"""
        word = Word.objects.create(**self.word_data)
        self.assertEqual(word.word, 'hello')
        self.assertEqual(word.user, self.user)
        self.assertFalse(word.is_learned)
        self.assertEqual(word.mastery_level, 0)
    
    def test_word_str_representation(self):
        """测试单词字符串表示"""
        word = Word.objects.create(**self.word_data)
        expected = f"hello ({self.user.username})"
        self.assertEqual(str(word), expected)
    
    def test_mark_word_as_learned(self):
        """测试标记单词为已学习"""
        word = Word.objects.create(**self.word_data)
        word.is_learned = True
        word.save()
        
        word.refresh_from_db()
        self.assertTrue(word.is_learned)
        self.assertIsNotNone(word.learned_at)
    
    def test_tag_operations(self):
        """测试标签操作"""
        word = Word.objects.create(**self.word_data)
        
        # 添加标签
        word.add_tag('基础词汇')
        self.assertIn('基础词汇', word.tag_list)
        
        word.add_tag('常用词')
        self.assertIn('常用词', word.tag_list)
        self.assertEqual(len(word.tag_list), 2)
        
        # 移除标签
        word.remove_tag('基础词汇')
        self.assertNotIn('基础词汇', word.tag_list)
        self.assertIn('常用词', word.tag_list)
    
    def test_unique_constraint(self):
        """测试用户-单词唯一约束"""
        Word.objects.create(**self.word_data)
        
        # 尝试创建重复的单词
        with self.assertRaises(Exception):
            Word.objects.create(**self.word_data)
    
    def test_word_with_resources(self):
        """测试单词绑定资源"""
        word = Word.objects.create(**self.word_data)
        
        # 创建资源
        resource1 = WordResource.objects.create(
            name='音频1',
            resource_type='audio',
            url='https://example.com/audio1.mp3'
        )
        resource2 = WordResource.objects.create(
            name='图片1',
            resource_type='image',
            url='https://example.com/image1.jpg'
        )
        
        # 绑定资源
        word.resources.add(resource1, resource2)
        
        self.assertEqual(word.resources.count(), 2)
        self.assertIn(resource1, word.resources.all())
        self.assertIn(resource2, word.resources.all())


class VocabularySourceModelTest(TestCase):
    """词库来源模型测试"""
    
    def test_create_vocabulary_source(self):
        """测试创建词库来源"""
        source = VocabularySource.objects.create(
            name='牛津词典',
            description='牛津英语词典'
        )
        self.assertEqual(source.name, '牛津词典')
        self.assertEqual(str(source), '牛津词典')


class VocabularyListModelTest(TestCase):
    """词库列表模型测试"""
    
    def setUp(self):
        self.source = VocabularySource.objects.create(
            name='测试来源',
            description='测试词库来源'
        )
    
    def test_create_vocabulary_list(self):
        """测试创建词库列表"""
        vocab_list = VocabularyList.objects.create(
            source=self.source,
            name='初级词汇',
            description='初级英语词汇列表'
        )
        self.assertEqual(vocab_list.name, '初级词汇')
        self.assertEqual(vocab_list.source, self.source)
        self.assertTrue(vocab_list.is_active)
        self.assertEqual(vocab_list.word_count, 0)
    
    def test_update_word_count(self):
        """测试更新单词数量"""
        vocab_list = VocabularyList.objects.create(
            source=self.source,
            name='测试列表'
        )
        
        # 添加导入单词
        ImportedVocabulary.objects.create(
            vocabulary_list=vocab_list,
            word='test1'
        )
        ImportedVocabulary.objects.create(
            vocabulary_list=vocab_list,
            word='test2'
        )
        
        # 更新单词数量
        count = vocab_list.update_word_count()
        self.assertEqual(count, 2)
        
        vocab_list.refresh_from_db()
        self.assertEqual(vocab_list.word_count, 2)


class ImportedVocabularyModelTest(TestCase):
    """导入词汇模型测试"""
    
    def setUp(self):
        self.source = VocabularySource.objects.create(name='测试来源')
        self.vocab_list = VocabularyList.objects.create(
            source=self.source,
            name='测试列表'
        )
    
    def test_create_imported_vocabulary(self):
        """测试创建导入词汇"""
        imported_word = ImportedVocabulary.objects.create(
            vocabulary_list=self.vocab_list,
            word='example',
            phonetic='/ɪɡˈzæmpəl/',
            definition='例子',
            part_of_speech='名词',
            grade='3'
        )
        
        self.assertEqual(imported_word.word, 'example')
        self.assertEqual(imported_word.vocabulary_list, self.vocab_list)
        self.assertFalse(imported_word.has_conflict)
        self.assertFalse(imported_word.conflict_resolved)
    
    def test_imported_vocabulary_str_representation(self):
        """测试导入词汇字符串表示"""
        imported_word = ImportedVocabulary.objects.create(
            vocabulary_list=self.vocab_list,
            word='test'
        )
        expected = f"test ({self.vocab_list.name})"
        self.assertEqual(str(imported_word), expected)


class UserStreakModelTest(TestCase):
    """用户学习记录模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_streak(self):
        """测试创建用户学习记录"""
        streak = UserStreak.objects.create(user=self.user)
        self.assertEqual(streak.user, self.user)
        self.assertEqual(streak.current_streak, 0)
        self.assertEqual(streak.longest_streak, 0)
        self.assertEqual(streak.total_words_learned, 0)
    
    def test_update_streak_continuous(self):
        """测试连续学习更新"""
        streak = UserStreak.objects.create(user=self.user)
        
        # 模拟昨天的学习
        yesterday = timezone.now().date() - timedelta(days=1)
        streak.last_activity_date = yesterday
        streak.current_streak = 1
        streak.save()
        
        # 今天学习
        streak.update_streak()
        
        self.assertEqual(streak.current_streak, 2)
        self.assertEqual(streak.longest_streak, 2)
    
    def test_update_streak_broken(self):
        """测试中断学习记录"""
        streak = UserStreak.objects.create(user=self.user)
        
        # 模拟前天的学习
        two_days_ago = timezone.now().date() - timedelta(days=2)
        streak.last_activity_date = two_days_ago
        streak.current_streak = 5
        streak.longest_streak = 5
        streak.save()
        
        # 今天学习（中断了昨天）
        streak.update_streak()
        
        self.assertEqual(streak.current_streak, 1)
        self.assertEqual(streak.longest_streak, 5)  # 最长记录保持不变


class StudySessionModelTest(TestCase):
    """学习会话模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_study_session(self):
        """测试创建学习会话"""
        session = StudySession.objects.create(user=self.user)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.words_count, 0)
        self.assertEqual(session.accuracy_rate, 0.0)
        self.assertIsNone(session.completed_at)
    
    def test_complete_session(self):
        """测试完成学习会话"""
        session = StudySession.objects.create(user=self.user)
        
        # 添加学习的单词
        word1 = Word.objects.create(user=self.user, word='test1')
        word2 = Word.objects.create(user=self.user, word='test2')
        session.words_studied.add(word1, word2)
        
        # 完成会话
        session.complete_session()
        
        session.refresh_from_db()
        self.assertIsNotNone(session.completed_at)
        self.assertEqual(session.words_count, 2)
    
    def test_session_str_representation(self):
        """测试学习会话字符串表示"""
        session = StudySession.objects.create(user=self.user)
        expected = f"{self.user.username} - {session.created_at.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(session), expected)