from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta, datetime
from django.utils import timezone

from apps.accounts.models import CustomUser, UserRole, LearningProfile
from apps.teaching.models import (
    LearningSession as StudySession, UserStreak, LearningGoal, LearningPlan, DailyStudyRecord
)
from apps.words.models import (
    Word, VocabularyList, VocabularySource, WordResource, PART_OF_SPEECH_CHOICES
)

User = get_user_model()

class Command(BaseCommand):
    help = '创建测试数据 - 模拟成长中心相关数据'

    def handle(self, *args, **options):
        self.stdout.write("开始创建测试数据...")
        
        try:
            # 创建用户
            students = self.create_test_users()
            
            # 创建词汇数据
            vocab_list, words = self.create_vocabulary_data()
            
            # 创建学习数据
            self.create_learning_data(students, vocab_list, words)
            
            self.stdout.write(self.style.SUCCESS("\n测试数据创建完成！"))
            self.stdout.write(f"创建了 {len(students)} 个学生用户")
            self.stdout.write(f"创建了 {len(words)} 个单词")
            self.stdout.write("\n可以访问以下管理页面查看数据:")
            self.stdout.write("- 用户管理: http://localhost:8001/admin/accounts/customuser/")
            self.stdout.write("- 词汇管理: http://localhost:8001/admin/words/word/")
            self.stdout.write("- 学习目标: http://localhost:8001/admin/vocabulary_manager/learninggoal/")
            self.stdout.write("- 学习计划: http://localhost:8001/admin/vocabulary_manager/learningplan/")
            self.stdout.write("- 学习会话: http://localhost:8001/admin/vocabulary_manager/studysession/")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"创建测试数据时出错: {e}"))
            import traceback
            traceback.print_exc()

    def create_test_users(self):
        """创建测试用户"""
        self.stdout.write("创建测试用户...")
        
        # 创建学生用户
        students = [
            {
                'username': 'student1',
                'email': 'student1@test.com',
                'real_name': '张小明',
                'role': UserRole.STUDENT,
                'grade_level': '小学三年级',
                'english_level': 'beginner'
            },
            {
                'username': 'student2', 
                'email': 'student2@test.com',
                'real_name': '李小红',
                'role': UserRole.STUDENT,
                'grade_level': '小学四年级',
                'english_level': 'elementary'
            },
            {
                'username': 'student3',
                'email': 'student3@test.com', 
                'real_name': '王小华',
                'role': UserRole.STUDENT,
                'grade_level': '初中一年级',
                'english_level': 'intermediate'
            }
        ]
        
        created_students = []
        for student_data in students:
            user, created = CustomUser.objects.get_or_create(
                username=student_data['username'],
                defaults=student_data
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f"创建学生用户: {user.real_name} ({user.username})")
            created_students.append(user)
        
        return created_students

    def create_vocabulary_data(self):
        """创建词汇数据"""
        self.stdout.write("创建词汇数据...")
        
        # 创建词库来源
        source, created = VocabularySource.objects.get_or_create(
            name='小学英语教材',
            defaults={'description': '小学英语基础词汇'}
        )
        
        # 创建词库列表
        vocab_list, created = VocabularyList.objects.get_or_create(
            name='小学三年级上册',
            defaults={
                'source': source,
                'description': '小学三年级上册英语单词',
                'is_active': True
            }
        )
        
        # 创建测试单词
        test_words = [
            {'word': 'apple', 'phonetic': '/ˈæpl/', 'definition': '苹果', 'part_of_speech': '名词', 'example': 'I like to eat apples.'},
            {'word': 'book', 'phonetic': '/bʊk/', 'definition': '书', 'part_of_speech': '名词', 'example': 'This is my book.'},
            {'word': 'cat', 'phonetic': '/kæt/', 'definition': '猫', 'part_of_speech': '名词', 'example': 'The cat is sleeping.'},
            {'word': 'dog', 'phonetic': '/dɔːɡ/', 'definition': '狗', 'part_of_speech': '名词', 'example': 'I have a dog.'},
            {'word': 'eat', 'phonetic': '/iːt/', 'definition': '吃', 'part_of_speech': '动词', 'example': 'I eat breakfast every morning.'},
            {'word': 'fish', 'phonetic': '/fɪʃ/', 'definition': '鱼', 'part_of_speech': '名词', 'example': 'Fish live in water.'},
            {'word': 'good', 'phonetic': '/ɡʊd/', 'definition': '好的', 'part_of_speech': '形容词', 'example': 'This is a good book.'},
            {'word': 'happy', 'phonetic': '/ˈhæpi/', 'definition': '快乐的', 'part_of_speech': '形容词', 'example': 'I am happy today.'},
            {'word': 'run', 'phonetic': '/rʌn/', 'definition': '跑', 'part_of_speech': '动词', 'example': 'I like to run in the park.'},
            {'word': 'water', 'phonetic': '/ˈwɔːtər/', 'definition': '水', 'part_of_speech': '名词', 'example': 'Please drink more water.'}
        ]
        
        created_words = []
        for word_data in test_words:
            word, created = Word.objects.get_or_create(
                word=word_data['word'],
                vocabulary_list=vocab_list,
                defaults=word_data
            )
            if created:
                self.stdout.write(f"创建单词: {word.word}")
            created_words.append(word)
        
        # 更新词库单词数量
        vocab_list.update_word_count()
        
        return vocab_list, created_words

    def create_learning_data(self, students, vocab_list, words):
        """创建学习数据"""
        self.stdout.write("创建学习数据...")
        
        for student in students:
            # 创建学习档案
            profile, created = LearningProfile.objects.get_or_create(
                user=student,
                defaults={
                    'total_study_time': 120,  # 120分钟
                    'completed_lessons': 5,
                    'current_streak': 3,
                    'max_streak': 7,
                    'last_study_date': date.today() - timedelta(days=1)
                }
            )
            
            # 创建连续学习记录
            streak, created = UserStreak.objects.get_or_create(
                user=student,
                defaults={
                    'current_streak': 3,
                    'longest_streak': 7,
                    'last_study_date': date.today() - timedelta(days=1),
                    'total_study_days': 15
                }
            )
            
            # 创建学习目标
            goal, created = LearningGoal.objects.get_or_create(
                user=student,
                name=f'{student.real_name}的词汇学习目标',
                defaults={
                    'description': '掌握小学三年级上册词汇',
                    'goal_type': 'vocabulary_list',
                    'vocabulary_list': vocab_list,
                    'is_current': True,
                    'total_words': len(words),
                    'learned_words': 3
                }
            )
            
            # 创建学习计划
            plan, created = LearningPlan.objects.get_or_create(
                user=student,
                learning_goal=goal,
                name=f'{student.real_name}的学习计划',
                defaults={
                    'plan_mode': 'daily_progress',
                    'start_date': date.today() - timedelta(days=7),
                    'end_date': date.today() + timedelta(days=23),
                    'total_words': len(words),
                    'daily_target': 2,
                    'status': 'active'
                }
            )
            
            # 创建学习会话
            for i in range(3):
                session_date = date.today() - timedelta(days=i+1)
                session, created = StudySession.objects.get_or_create(
                    user=student,
                    learning_goal=goal,
                    start_time=timezone.make_aware(
                        datetime.combine(session_date, datetime.min.time())
                    ),
                    defaults={
                        'end_time': timezone.make_aware(
                            datetime.combine(session_date, datetime.min.time()) + timedelta(minutes=30)
                        ),
                        'duration': timedelta(minutes=30),
                        'words_studied': 5,
                        'words_learned': 3
                    }
                )
            
            # 创建每日学习记录
            for i in range(7):
                record_date = date.today() - timedelta(days=i)
                record, created = DailyStudyRecord.objects.get_or_create(
                    user=student,
                    learning_plan=plan,
                    study_date=record_date,
                    defaults={
                        'target_words': 2,
                        'completed_words': 2 if i < 3 else 1,
                        'study_duration': timedelta(minutes=25)
                    }
                )
            
            # 为学生创建个人单词学习记录
            for i, word in enumerate(words[:5]):
                personal_word, created = Word.objects.get_or_create(
                    word=word.word,
                    user=student,
                    defaults={
                        'phonetic': word.phonetic,
                        'definition': word.definition,
                        'part_of_speech': word.part_of_speech,
                        'example': word.example,
                        'is_learned': i < 3,  # 前3个单词标记为已学
                        'mastery_level': 80 if i < 3 else 20,
                        'difficulty_level': 2
                    }
                )
                if created and i < 3:
                    personal_word.learned_at = timezone.now() - timedelta(days=i+1)
                    personal_word.save()
            
            self.stdout.write(f"为用户 {student.real_name} 创建学习数据")