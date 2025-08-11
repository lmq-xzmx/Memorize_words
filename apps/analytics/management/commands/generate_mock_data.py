from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
import random
from decimal import Decimal

from apps.analytics.models import (
    UserEngagementMetrics, UserRetentionData, ABTestExperiment, ABTestParticipant,
    UserBehaviorPattern, GameElementEffectiveness
)
from apps.teaching.models import LearningSession, WordLearningRecord
from apps.words.models import Word

User = get_user_model()

class Command(BaseCommand):
    help = '生成模拟的用户参与度数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='要生成数据的用户数量'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='生成数据的天数'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        days_count = options['days']
        
        self.stdout.write(f'开始为 {users_count} 个用户生成 {days_count} 天的模拟数据...')
        
        # 获取用户
        users = User.objects.all()[:users_count]
        if not users:
            self.stdout.write(self.style.ERROR('没有找到用户，请先创建用户'))
            return
        
        # 生成用户参与度指标
        self.generate_engagement_metrics(users)
        
        # 生成用户行为模式
        self.generate_behavior_patterns(users)
        
        # 生成游戏化元素效果数据
        self.generate_game_element_effectiveness()
        
        # 生成A/B测试数据
        self.generate_ab_test_data(users)
        
        # 生成用户留存数据
        self.generate_retention_data(users, days_count)
        
        self.stdout.write(self.style.SUCCESS('模拟数据生成完成！'))
    
    def generate_engagement_metrics(self, users):
        """生成用户参与度指标"""
        self.stdout.write('生成用户参与度指标...')
        
        for user in users:
            # 删除已存在的数据
            UserEngagementMetrics.objects.filter(user=user).delete()
            
            # 为最近30天生成数据
            for i in range(30):
                date = timezone.now().date() - timedelta(days=i)
                
                # 创建新的参与度指标
                UserEngagementMetrics.objects.create(
                    user=user,
                    date=date,
                    session_count=random.randint(1, 5),
                    total_session_duration=random.randint(900, 3600),  # 15-60分钟
                    avg_session_duration=random.randint(900, 2700),  # 15-45分钟
                    peak_activity_hour=random.randint(8, 22),
                    words_practiced=random.randint(10, 50),
                    correct_answers=random.randint(8, 45),
                    total_answers=random.randint(10, 50),
                    accuracy_rate=round(random.uniform(0.6, 0.95), 2),
                    exp_gained=random.randint(50, 200),
                    coins_earned=random.randint(20, 100),
                    achievements_unlocked=random.randint(0, 3),
                    streak_count=random.randint(0, 15),
                    battles_participated=random.randint(0, 5),
                    battles_won=random.randint(0, 3),
                    social_interactions=random.randint(0, 10)
                )
    
    def generate_behavior_patterns(self, users):
        """生成用户行为模式"""
        self.stdout.write('生成用户行为模式...')
        
        study_times = ['早晨', '上午', '下午', '晚上', '深夜']
        difficulties = ['简单', '中等', '困难']
        engagement_types = ['学习型', '竞争型', '社交型', '探索型']
        learning_styles = ['视觉型', '听觉型', '动觉型', '混合型']
        
        for user in users:
            # 删除已存在的数据
            UserBehaviorPattern.objects.filter(user=user).delete()
            
            # 创建新的行为模式
            UserBehaviorPattern.objects.create(
                user=user,
                preferred_study_time=random.choice(study_times),
                avg_session_length=random.randint(15, 60),
                preferred_difficulty=random.choice(difficulties),
                engagement_type=random.choice(engagement_types),
                motivation_factors=['成就感', '进步', '竞争', '社交'][0:random.randint(1, 3)],
                social_activity_level=random.choice(['低', '中等', '高']),
                competitive_tendency=round(random.uniform(0.2, 0.9), 2),
                learning_style=random.choice(learning_styles),
                retention_rate=round(random.uniform(0.5, 0.95), 2),
                churn_risk_score=round(random.uniform(0.05, 0.3), 2),
                engagement_score=round(random.uniform(60, 95), 1)
            )
    
    def generate_game_element_effectiveness(self):
        """生成游戏化元素效果数据"""
        self.stdout.write('生成游戏化元素效果数据...')
        
        # 删除已存在的数据
        GameElementEffectiveness.objects.all().delete()
        
        game_elements = [
            ('积分系统', '奖励机制'),
            ('徽章奖励', '成就系统'),
            ('排行榜', '竞争机制'),
            ('连续学习', '习惯养成'),
            ('挑战任务', '目标导向'),
            ('社交分享', '社交功能'),
            ('个人成就', '成就系统'),
            ('团队竞赛', '竞争机制'),
            ('每日签到', '习惯养成'),
            ('学习路径', '进度追踪')
        ]
        
        for element_name, element_type in game_elements:
            start_date = timezone.now() - timedelta(days=30)
            end_date = timezone.now()
            
            GameElementEffectiveness.objects.create(
                element_name=element_name,
                element_type=element_type,
                engagement_impact=round(random.uniform(0.1, 0.4), 2),
                retention_impact=round(random.uniform(0.05, 0.25), 2),
                learning_efficiency_impact=round(random.uniform(0.05, 0.3), 2),
                total_interactions=random.randint(500, 2000),
                unique_users=random.randint(50, 200),
                avg_interaction_frequency=round(random.uniform(0.3, 0.9), 2),
                measurement_period_start=start_date,
                measurement_period_end=end_date
            )
    
    def generate_ab_test_data(self, users):
        """生成A/B测试数据"""
        self.stdout.write('生成A/B测试数据...')
        
        # 删除已存在的数据
        ABTestExperiment.objects.all().delete()
        ABTestParticipant.objects.all().delete()
        
        experiments = [
            {
                'name': '新手引导优化测试',
                'description': '测试新的用户引导流程对用户留存的影响',
                'target_metric': '7日留存率',
                'success_criteria': '实验组留存率比对照组提高10%以上'
            },
            {
                'name': '积分奖励机制测试',
                'description': '测试不同积分奖励策略对用户参与度的影响',
                'target_metric': '日均学习时长',
                'success_criteria': '实验组学习时长比对照组提高15%以上'
            },
            {
                'name': '学习提醒推送测试',
                'description': '测试个性化学习提醒对用户活跃度的影响',
                'target_metric': '日活跃用户数',
                'success_criteria': '实验组DAU比对照组提高20%以上'
            }
        ]
        
        for exp_data in experiments:
            # 创建实验
            start_date = timezone.now() - timedelta(days=random.randint(10, 30))
            end_date = timezone.now() + timedelta(days=random.randint(5, 15))
            
            experiment = ABTestExperiment.objects.create(
                name=exp_data['name'],
                description=exp_data['description'],
                start_date=start_date,
                end_date=end_date,
                is_active=random.choice([True, False]),
                control_group_ratio=0.5,
                experiment_config={'version': 'v1', 'feature_enabled': True},
                target_metric=exp_data['target_metric'],
                success_criteria=exp_data['success_criteria']
            )
            
            # 为实验分配参与者
            selected_users = random.sample(list(users), min(len(users), 20))
            for user in selected_users:
                conversion_achieved = random.choice([True, False])
                ABTestParticipant.objects.create(
                    experiment=experiment,
                    user=user,
                    group=random.choice(['control', 'experiment']),
                    conversion_achieved=conversion_achieved,
                    conversion_date=timezone.now() if conversion_achieved else None,
                    metric_value=round(random.uniform(10, 100), 2),
                    additional_data={'engagement_score': random.randint(60, 95)}
                )
    
    def generate_retention_data(self, users, days_count):
        """生成用户留存数据"""
        self.stdout.write('生成用户留存数据...')
        
        # 删除已存在的数据
        UserRetentionData.objects.all().delete()
        
        for user in users:
            # 为每个用户创建一条留存记录
            registration_date = user.date_joined.date() if hasattr(user, 'date_joined') else timezone.now().date() - timedelta(days=random.randint(30, 365))
            
            UserRetentionData.objects.create(
                user=user,
                registration_date=registration_date,
                day_1_retention=random.choice([True, False]),
                day_3_retention=random.choice([True, False]),
                day_7_retention=random.choice([True, False]),
                day_14_retention=random.choice([True, False]),
                day_30_retention=random.choice([True, False]),
                total_active_days=random.randint(5, 50),
                consecutive_active_days=random.randint(1, 15),
                last_active_date=timezone.now().date() - timedelta(days=random.randint(0, 7)),
                total_sessions=random.randint(10, 200),
                total_study_time=random.randint(300, 3000),  # 分钟
                total_words_learned=random.randint(50, 500)
            )