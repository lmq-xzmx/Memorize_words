import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import CustomUser, UserRole, LearningProfile
from apps.teaching.models import LearningGoal, LearningSession, WordLearningRecord, GoalWord
from apps.words.models import Word


class Command(BaseCommand):
    help = '为现有学生创建模拟学习数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有学习数据',
        )
        parser.add_argument(
            '--students',
            type=int,
            default=10,
            help='处理的学生数量（默认10个）',
        )

    def handle(self, *args, **options):
        # 获取单词数据
        words = list(Word.objects.all()[:100])  # 获取前100个单词
        if not words:
            self.stdout.write(
                self.style.ERROR('没有找到单词数据，请先导入单词数据')
            )
            return

        with transaction.atomic():
            if options['clear']:
                self.clear_existing_data()

            # 获取学生用户
            students = CustomUser.objects.filter(
                role=UserRole.STUDENT
            )[:options['students']]

            if not students:
                self.stdout.write(
                    self.style.ERROR('没有找到学生用户')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(f'开始为 {len(students)} 个学生创建学习数据...')
            )

            for student in students:
                self.create_student_data(student, words)

            self.stdout.write(
                self.style.SUCCESS('学习数据创建完成！')
            )

    def clear_existing_data(self):
        """清除现有学习数据"""
        self.stdout.write('清除现有学习数据...')
        LearningProfile.objects.all().delete()
        LearningGoal.objects.all().delete()
        LearningSession.objects.all().delete()
        WordLearningRecord.objects.all().delete()

    def create_student_data(self, student, words):
        """为单个学生创建学习数据"""
        # 1. 创建学习档案
        self.create_learning_profile(student)
        
        # 2. 创建学习目标
        goals = self.create_learning_goals(student, words)
        
        # 3. 创建学习会话
        self.create_learning_sessions(student, goals, words)
        
        self.stdout.write(f'  - 为学生 {student.username} 创建了学习档案、目标和会话数据')
    
    def create_learning_profile(self, student):
        """创建学习档案"""
        profile, created = LearningProfile.objects.get_or_create(
            user=student,
            defaults={
                'total_study_time': random.randint(300, 3600),  # 5分钟到1小时
                'completed_lessons': random.randint(1, 50),
                'current_streak': random.randint(0, 30),
                'max_streak': random.randint(5, 60),
                'last_study_date': timezone.now() - timedelta(days=random.randint(0, 7))
            }
        )
        return profile
    
    def create_learning_goals(self, student, words):
        """创建学习目标"""
        goals = []
        
        # 创建1-3个学习目标
        for i in range(random.randint(1, 3)):
            goal = LearningGoal.objects.create(
                user=student,
                name=f'学生{student.username}的词汇学习目标{i+1}',
                description=f'为学生{student.username}创建的词汇学习目标',
                goal_type='vocabulary',
                target_words_count=random.randint(20, 100),
                learned_words=random.randint(0, 50),
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timedelta(days=random.randint(7, 30))).date(),
                is_active=True
            )
            
            # 为目标添加单词
            goal_words = random.sample(words, min(goal.target_words_count, len(words)))
            for word in goal_words:
                GoalWord.objects.create(
                     goal=goal,
                     word=word
                 )
            
            goals.append(goal)
        
        return goals
    
    def create_learning_sessions(self, student, goals, words):
        """创建学习会话"""
        # 创建5-15个学习会话
        for i in range(random.randint(5, 15)):
            start_time = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            session = LearningSession.objects.create(
                user=student,
                goal=random.choice(goals) if goals else None,
                start_time=start_time,
                end_time=start_time + timedelta(minutes=random.randint(5, 60)),
                words_studied=random.randint(5, 30),
                correct_answers=random.randint(3, 25),
                total_answers=random.randint(10, 40)
            )
            
            # 为会话创建单词学习记录
            session_words = random.sample(words, min(session.words_studied, len(words)))
            for word in session_words:
                WordLearningRecord.objects.create(
                     session=session,
                     goal=session.goal,
                     word=word,
                     user_answer=word.word if random.choice([True, False]) else 'wrong_answer',
                     is_correct=random.choice([True, False]),
                     response_time=random.randint(5, 30)  # 秒
                 )