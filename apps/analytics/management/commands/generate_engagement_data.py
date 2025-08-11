from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from apps.analytics.models import (
    UserEngagementMetrics, UserRetentionData, ABTestExperiment,
    ABTestParticipant, UserBehaviorPattern, GameElementEffectiveness
)

User = get_user_model()


class Command(BaseCommand):
    help = '生成用户粘性游戏化系统的示例数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=100,
            help='生成数据的用户数量'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='生成数据的天数'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('清除现有数据...')
            UserEngagementMetrics.objects.all().delete()
            UserRetentionData.objects.all().delete()
            ABTestExperiment.objects.all().delete()
            ABTestParticipant.objects.all().delete()
            UserBehaviorPattern.objects.all().delete()
            GameElementEffectiveness.objects.all().delete()

        users_count = options['users']
        days_count = options['days']
        
        self.stdout.write(f'开始生成 {users_count} 个用户 {days_count} 天的数据...')
        
        # 获取或创建用户
        users = self.get_or_create_users(users_count)
        
        # 生成用户粘性指标数据
        self.generate_engagement_metrics(users, days_count)
        
        # 生成用户留存数据
        self.generate_retention_data(users)
        
        # 生成用户行为模式数据
        self.generate_behavior_patterns(users)
        
        # 生成游戏化元素效果数据
        self.generate_game_element_effectiveness(users, days_count)
        
        # 生成A/B测试数据
        self.generate_ab_test_data(users)
        
        self.stdout.write(
            self.style.SUCCESS(f'成功生成了 {users_count} 个用户的数据')
        )

    def get_or_create_users(self, count):
        """获取或创建用户"""
        existing_users = list(User.objects.all()[:count])
        
        if len(existing_users) < count:
            needed = count - len(existing_users)
            self.stdout.write(f'创建 {needed} 个新用户...')
            
            for i in range(needed):
                user = User.objects.create(
                    username=f'test_user_{len(existing_users) + i + 1}',
                    email=f'test{len(existing_users) + i + 1}@example.com'
                )
                user.set_password('testpass123')
                user.save()
                
                # 确保学习档案存在
                from apps.accounts.models import LearningProfile
                LearningProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'total_study_time': 0,
                        'completed_lessons': 0,
                        'current_streak': 0,
                        'max_streak': 0
                    }
                )
                
                existing_users.append(user)
        
        return existing_users[:count]

    def generate_engagement_metrics(self, users, days):
        """生成用户粘性指标数据"""
        self.stdout.write('生成用户粘性指标数据...')
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        for user in users:
            # 为每个用户生成不同的学习模式
            user_type = random.choice(['active', 'moderate', 'casual', 'declining'])
            
            current_date = start_date
            streak = 0
            
            while current_date <= end_date:
                # 根据用户类型决定是否学习
                study_probability = self.get_study_probability(user_type, streak)
                
                if random.random() < study_probability:
                    # 生成学习数据
                    session_count = random.randint(1, 5)
                    avg_duration = random.uniform(300, 3600)  # 5分钟到1小时
                    words_count = random.randint(5, 50)
                    accuracy = random.uniform(0.6, 0.95)
                    peak_hour = random.randint(6, 23)
                    
                    # 计算粘性评分
                    engagement_score = self.calculate_engagement_score(
                        session_count, avg_duration, accuracy, streak
                    )
                    
                    UserEngagementMetrics.objects.get_or_create(
                        user=user,
                        date=current_date,
                        defaults={
                            'session_count': session_count,
                            'total_session_duration': int(avg_duration * session_count),
                            'avg_session_duration': avg_duration,
                            'words_practiced': words_count,
                            'correct_answers': int(words_count * accuracy),
                            'total_answers': words_count,
                            'accuracy_rate': accuracy,
                            'peak_activity_hour': peak_hour,
                            'exp_gained': random.randint(10, 100),
                            'coins_earned': random.randint(5, 50),
                            'achievements_unlocked': random.randint(0, 3),
                            'streak_count': streak
                        }
                    )
                    
                    streak += 1
                else:
                    streak = 0
                
                current_date += timedelta(days=1)

    def get_study_probability(self, user_type, streak):
        """根据用户类型和连续天数获取学习概率"""
        base_probabilities = {
            'active': 0.9,
            'moderate': 0.6,
            'casual': 0.3,
            'declining': 0.8 - (streak * 0.05)  # 递减型用户
        }
        
        prob = base_probabilities[user_type]
        
        # 连续学习会增加概率（习惯形成）
        if user_type != 'declining' and streak > 0:
            prob = min(0.95, prob + (streak * 0.02))
        
        return max(0.05, prob)

    def calculate_engagement_score(self, sessions, duration, accuracy, streak):
        """计算粘性评分"""
        session_score = min(sessions * 10, 40)  # 最多40分
        duration_score = min(duration / 60, 30)  # 最多30分
        accuracy_score = accuracy * 20  # 最多20分
        streak_score = min(streak, 10)  # 最多10分
        
        return min(100, session_score + duration_score + accuracy_score + streak_score)

    def generate_retention_data(self, users):
        """生成用户留存数据"""
        self.stdout.write('生成用户留存数据...')
        
        for user in users:
            # 模拟注册时间
            reg_date = timezone.now().date() - timedelta(
                days=random.randint(1, 90)
            )
            
            UserRetentionData.objects.get_or_create(
                user=user,
                registration_date=reg_date,
                defaults={
                    'day_1_retention': random.choice([True, False]),
                    'day_3_retention': random.choice([True, False]),
                    'day_7_retention': random.choice([True, False]),
                    'day_30_retention': random.choice([True, False]),
                    'total_active_days': random.randint(1, 30),
                    'consecutive_active_days': random.randint(0, 10),
                    'last_active_date': timezone.now().date() - timedelta(
                        days=random.randint(0, 7)
                    ),
                    'total_sessions': random.randint(5, 100),
                    'total_study_time': random.randint(60, 1800),
                    'total_words_learned': random.randint(10, 500)
                }
            )

    def generate_behavior_patterns(self, users):
        """生成用户行为模式数据"""
        self.stdout.write('生成用户行为模式数据...')
        
        learning_styles = ['visual', 'auditory', 'kinesthetic', 'mixed']
        difficulty_preferences = ['easy', 'medium', 'hard', 'adaptive']
        
        for user in users:
            UserBehaviorPattern.objects.create(
                user=user,
                preferred_study_time=random.choice(['morning', 'afternoon', 'evening', 'night']),
                avg_session_length=random.randint(10, 60),
                preferred_difficulty=random.choice(difficulty_preferences),
                engagement_type=random.choice(['achievement', 'social', 'mastery', 'competition']),
                motivation_factors=['streaks', 'badges', 'leaderboard', 'progress'],
                social_activity_level=random.choice(['low', 'medium', 'high']),
                competitive_tendency=random.uniform(0.0, 1.0),
                learning_style=random.choice(learning_styles),
                retention_rate=random.uniform(0.6, 0.95),
                churn_risk_score=random.uniform(0, 100),
                engagement_score=random.uniform(60, 95)
            )

    def generate_game_element_effectiveness(self, users, days):
        """生成游戏化元素效果数据"""
        self.stdout.write('生成游戏化元素效果数据...')
        
        game_elements = [
            ('badge', '成就徽章'),
            ('streak', '连续学习'),
            ('leaderboard', '排行榜'),
            ('points', '积分系统'),
            ('level', '等级系统'),
            ('challenge', '挑战任务'),
            ('social', '社交功能'),
            ('reward', '奖励机制')
        ]
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 为每个元素生成效果数据
        for element_type, element_name in game_elements:
            current_date = start_date
            
            while current_date <= end_date:
                # 随机选择一些用户使用该元素
                element_users = random.sample(users, random.randint(10, len(users) // 2))
                
                # 为每个元素创建一条效果记录（不是按用户）
                GameElementEffectiveness.objects.create(
                    element_name=element_name,
                    element_type=element_type,
                    engagement_impact=random.uniform(0.1, 0.8),
                    retention_impact=random.uniform(-0.1, 0.3),
                    learning_efficiency_impact=random.uniform(0.0, 0.5),
                    total_interactions=random.randint(50, 500),
                    unique_users=len(element_users),
                    avg_interaction_frequency=random.uniform(1.0, 10.0),
                    measurement_period_start=timezone.make_aware(datetime.combine(current_date, datetime.min.time())),
                    measurement_period_end=timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
                )
                
                current_date += timedelta(days=1)

    def generate_ab_test_data(self, users):
        """生成A/B测试数据"""
        self.stdout.write('生成A/B测试数据...')
        
        # 创建几个测试实验
        experiments = [
            {
                'name': '新手引导优化',
                'description': '测试新的用户引导流程对留存率的影响',
                'experiment_type': 'ui_design',
                'target_metric': 'retention_rate'
            },
            {
                'name': '积分系统改进',
                'description': '测试新的积分奖励机制对用户参与度的影响',
                'experiment_type': 'gamification',
                'target_metric': 'engagement_score'
            },
            {
                'name': '学习提醒优化',
                'description': '测试个性化学习提醒对学习频率的影响',
                'experiment_type': 'notification',
                'target_metric': 'study_duration'
            }
        ]
        
        for exp_data in experiments:
            # 创建实验
            start_date = timezone.now().date() - timedelta(days=20)
            end_date = timezone.now().date() - timedelta(days=5)
            
            experiment, created = ABTestExperiment.objects.get_or_create(
                name=exp_data['name'],
                defaults={
                    'description': exp_data['description'],
                    'target_metric': exp_data['target_metric'],
                    'start_date': timezone.make_aware(datetime.combine(start_date, datetime.min.time())),
                    'end_date': timezone.make_aware(datetime.combine(end_date, datetime.max.time())),
                    'is_active': False,
                    'control_group_ratio': 0.5,
                    'experiment_config': {'type': exp_data['experiment_type']},
                    'success_criteria': '提升目标指标10%以上'
                }
            )
            
            # 为实验分配参与者
            test_users = random.sample(users, random.randint(50, len(users)))
            
            for user in test_users:
                group = random.choice(['control', 'test'])
                converted = random.choice([True, False])
                
                # 实验组的转化率稍高
                if group == 'test':
                    converted = random.random() < 0.65
                else:
                    converted = random.random() < 0.55
                
                ABTestParticipant.objects.create(
                    experiment=experiment,
                    user=user,
                    group=group,
                    conversion_achieved=converted,
                    conversion_date=start_date + timedelta(
                        days=random.randint(1, 15)
                    ) if converted else None,
                    metric_value=random.uniform(50, 100),
                    additional_data={'session_count': random.randint(1, 20), 'time_spent': random.randint(300, 3600)}
                )

        self.stdout.write(f'创建了 {len(experiments)} 个A/B测试实验')