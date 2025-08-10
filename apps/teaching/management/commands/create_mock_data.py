from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.teaching.models import LearningGoal, GoalWord, LearningSession, WordLearningRecord, LearningPlan
from apps.accounts.models import LearningProfile
from apps.words.models import Word
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string

User = get_user_model()

class Command(BaseCommand):
    help = '创建模拟学员和成长中心数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=20,
            help='要创建的学员数量（默认20）'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有的模拟数据'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.clear_mock_data()
        
        student_count = options['students']
        self.stdout.write(f'开始创建 {student_count} 个模拟学员的数据...')
        
        # 确保有足够的单词数据
        self.ensure_words()
        
        # 创建学员
        students = self.create_students(student_count)
        
        # 为每个学员创建学习数据
        for student in students:
            self.create_learning_data(student)
        
        self.stdout.write(
            self.style.SUCCESS(f'成功创建了 {student_count} 个学员的完整学习数据！')
        )
    
    def clear_mock_data(self):
        """清除模拟数据"""
        self.stdout.write('清除现有模拟数据...')
        
        # 删除测试用户（用户名以test_开头的）
        test_users = User.objects.filter(username__startswith='test_')
        user_count = test_users.count()
        
        if user_count > 0:
            # 删除相关的学习数据
            LearningGoal.objects.filter(user__in=test_users).delete()
            LearningSession.objects.filter(user__in=test_users).delete()
            LearningProfile.objects.filter(user__in=test_users).delete()
            
            # 删除用户
            test_users.delete()
            
            self.stdout.write(self.style.SUCCESS(f'清除了 {user_count} 个测试用户的数据'))
        else:
            self.stdout.write('没有找到需要清除的测试数据')
    
    def ensure_words(self):
        """确保有足够的单词数据"""
        word_count = Word.objects.count()
        if word_count < 100:
            self.stdout.write('创建基础单词数据...')
            # 创建一些基础单词
            basic_words = [
                ('apple', '苹果', 'noun'),
                ('book', '书', 'noun'),
                ('cat', '猫', 'noun'),
                ('dog', '狗', 'noun'),
                ('eat', '吃', 'verb'),
                ('run', '跑', 'verb'),
                ('happy', '快乐的', 'adjective'),
                ('big', '大的', 'adjective'),
                ('small', '小的', 'adjective'),
                ('good', '好的', 'adjective'),
                ('water', '水', 'noun'),
                ('house', '房子', 'noun'),
                ('car', '汽车', 'noun'),
                ('tree', '树', 'noun'),
                ('flower', '花', 'noun'),
                ('sun', '太阳', 'noun'),
                ('moon', '月亮', 'noun'),
                ('star', '星星', 'noun'),
                ('love', '爱', 'verb'),
                ('learn', '学习', 'verb'),
            ]
            
            for word, meaning, pos in basic_words:
                Word.objects.get_or_create(
                    word=word,
                    defaults={
                        'meaning': meaning,
                        'part_of_speech': pos,
                        'frequency': random.randint(1, 1000),
                        'difficulty_level': random.choice(['beginner', 'intermediate', 'advanced'])
                    }
                )
    
    def create_students(self, count):
        """创建学员"""
        students = []
        grades = ['小学一年级', '小学二年级', '小学三年级', '小学四年级', '小学五年级', '小学六年级',
                 '初中一年级', '初中二年级', '初中三年级', '高中一年级', '高中二年级', '高中三年级']
        english_levels = ['beginner', 'elementary', 'intermediate', 'upper_intermediate', 'advanced']
        
        for i in range(count):
            username = f'test_student_{i+1:03d}'
            email = f'{username}@example.com'
            
            # 创建用户
            user = User.objects.create(
                username=username,
                email=email,
                first_name=f'学员{i+1:03d}',
                last_name='测试',
                role='student',
                grade_level=random.choice(grades),
                english_level=random.choice(english_levels),
                phone=f'138{random.randint(10000000, 99999999)}',
                real_name=f'测试学员{i+1:03d}'
            )
            user.set_password('testpass123')
            user.save()
            
            # 创建学习档案
            profile, created = LearningProfile.objects.get_or_create(
                user=user,
                defaults={
                    'total_study_time': random.randint(100, 5000),  # 100-5000分钟
                    'completed_lessons': random.randint(0, 20),
                    'current_streak': random.randint(0, 100),
                    'max_streak': random.randint(0, 150),
                    'last_study_date': timezone.now().date() - timedelta(days=random.randint(0, 30))
                }
            )
            
            students.append(user)
            
        self.stdout.write(f'创建了 {count} 个学员账户')
        return students
    
    def create_learning_data(self, student):
        """为学员创建学习数据"""
        # 创建1-3个学习目标
        goal_count = random.randint(1, 3)
        goals = []
        
        for i in range(goal_count):
            start_date = timezone.now().date() - timedelta(days=random.randint(30, 180))
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            goal = LearningGoal.objects.create(
                user=student,
                name=f'{student.first_name}的学习目标{i+1}',
                description=f'这是{student.first_name}的第{i+1}个学习目标，专注于提升英语词汇量。',
                target_words_count=random.randint(50, 200),
                start_date=start_date,
                end_date=end_date,
                is_active=random.choice([True, True, True, False])  # 75%概率激活
            )
            goals.append(goal)
            
            # 为目标添加单词
            words = Word.objects.order_by('?')[:goal.target_words_count]
            for word in words:
                GoalWord.objects.create(goal=goal, word=word)
            
            # 创建学习计划
            LearningPlan.objects.create(
                goal=goal,
                plan_type=random.choice(['daily', 'weekly', 'custom']),
                words_per_day=random.randint(5, 20),
                review_interval=random.randint(1, 7)
            )
        
        # 创建学习会话和记录
        for goal in goals:
            session_count = random.randint(5, 30)
            
            for _ in range(session_count):
                session_start = timezone.now() - timedelta(
                    days=random.randint(0, 60),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                session_end = session_start + timedelta(minutes=random.randint(10, 60))
                
                session = LearningSession.objects.create(
                    user=student,
                    goal=goal,
                    start_time=session_start,
                    end_time=session_end,
                    words_studied=random.randint(5, 20),
                    correct_answers=0,  # 将在创建记录时更新
                    total_answers=0     # 将在创建记录时更新
                )
                
                # 为会话创建单词学习记录
                goal_words = list(goal.goal_words.all())
                study_words = random.sample(goal_words, min(session.words_studied, len(goal_words)))
                
                correct_count = 0
                total_count = 0
                
                for goal_word in study_words:
                    # 每个单词可能有多次练习
                    practice_count = random.randint(1, 3)
                    
                    for _ in range(practice_count):
                        is_correct = random.choice([True, True, True, False])  # 75%正确率
                        
                        WordLearningRecord.objects.create(
                            session=session,
                            goal=goal,
                            word=goal_word.word,
                            user_answer=goal_word.word.word if is_correct else 'wrong_answer',
                            is_correct=is_correct,
                            response_time=random.uniform(1.0, 10.0),
                            created_at=session_start + timedelta(minutes=random.randint(0, 30))
                        )
                        
                        if is_correct:
                            correct_count += 1
                        total_count += 1
                
                # 更新会话统计
                session.correct_answers = correct_count
                session.total_answers = total_count
                session.save()
        
        self.stdout.write(f'为学员 {student.username} 创建了学习数据')