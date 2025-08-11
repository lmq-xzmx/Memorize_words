from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from apps.resource_authorization.models import (
    ResourceAuthorization,
    ResourceCategory,
    SubscriptionFeature,
    UserSubscription
)
from apps.teaching.models import LearningGoal
from apps.teaching.models import LearningGoal as VocabLearningGoal
from apps.words.models import Word, WordSet

User = get_user_model()


class Command(BaseCommand):
    help = '初始化资源授权系统的基础数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-categories',
            action='store_true',
            help='创建默认资源分类',
        )
        parser.add_argument(
            '--create-features',
            action='store_true',
            help='创建默认订阅功能',
        )
        parser.add_argument(
            '--migrate-existing',
            action='store_true',
            help='为现有资源创建授权记录',
        )
        parser.add_argument(
            '--create-demo-subscriptions',
            action='store_true',
            help='为现有用户创建演示订阅',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('开始初始化资源授权系统...')
        )
        
        if options['create_categories']:
            self.create_default_categories()
        
        if options['create_features']:
            self.create_default_features()
        
        if options['migrate_existing']:
            self.migrate_existing_resources()
        
        if options['create_demo_subscriptions']:
            self.create_demo_subscriptions()
        
        self.stdout.write(
            self.style.SUCCESS('资源授权系统初始化完成！')
        )
    
    def create_default_categories(self):
        """创建默认资源分类"""
        self.stdout.write('创建默认资源分类...')
        
        categories = [
            {
                'name': '学习目标',
                'description': '用户创建的学习目标和计划',
                'is_public': True,
                'sort_order': 1
            },
            {
                'name': '词汇管理',
                'description': '单词、词汇表和学习资源',
                'is_public': True,
                'sort_order': 2
            },
            {
                'name': '学习记录',
                'description': '学习会话和进度记录',
                'is_public': False,
                'sort_order': 3
            },
            {
                'name': '共享资源',
                'description': '用户间分享的学习资源',
                'is_public': True,
                'sort_order': 4
            }
        ]
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('未找到管理员用户，跳过分类创建')
            )
            return
        
        for cat_data in categories:
            category, created = ResourceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'created_by': admin_user,
                    'is_public': cat_data['is_public'],
                    'sort_order': cat_data['sort_order']
                }
            )
            
            if created:
                self.stdout.write(
                    f'  ✓ 创建分类: {category.name}'
                )
            else:
                self.stdout.write(
                    f'  - 分类已存在: {category.name}'
                )
    
    def create_default_features(self):
        """创建默认订阅功能"""
        self.stdout.write('创建默认订阅功能...')
        
        features = [
            {
                'name': '基础学习',
                'code': 'basic_learning',
                'description': '基础的单词学习功能',
                'subscription_types': ['free', 'basic', 'premium'],
                'usage_limit': 100,
                'daily_limit': 20
            },
            {
                'name': '高级学习',
                'code': 'advanced_learning',
                'description': '高级学习功能和个性化推荐',
                'subscription_types': ['basic', 'premium'],
                'usage_limit': 500,
                'daily_limit': 100
            },
            {
                'name': '无限学习',
                'code': 'unlimited_learning',
                'description': '无限制学习功能',
                'subscription_types': ['premium'],
                'usage_limit': None,
                'daily_limit': None
            },
            {
                'name': '资源分享',
                'code': 'resource_sharing',
                'description': '与其他用户分享学习资源',
                'subscription_types': ['basic', 'premium'],
                'usage_limit': 50,
                'daily_limit': 10
            },
            {
                'name': '高级分析',
                'code': 'advanced_analytics',
                'description': '详细的学习分析和报告',
                'subscription_types': ['premium'],
                'usage_limit': None,
                'daily_limit': None
            }
        ]
        
        for feature_data in features:
            feature, created = SubscriptionFeature.objects.get_or_create(
                code=feature_data['code'],
                defaults={
                    'name': feature_data['name'],
                    'description': feature_data['description'],
                    'subscription_types': feature_data['subscription_types'],
                    'usage_limit': feature_data['usage_limit'],
                    'daily_limit': feature_data['daily_limit'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    f'  ✓ 创建功能: {feature.name}'
                )
            else:
                self.stdout.write(
                    f'  - 功能已存在: {feature.name}'
                )
    
    @transaction.atomic
    def migrate_existing_resources(self):
        """为现有资源创建授权记录"""
        self.stdout.write('为现有资源创建授权记录...')
        
        # 迁移学习目标
        learning_goals = LearningGoal.objects.all()
        for goal in learning_goals:
            auth, created = ResourceAuthorization.objects.get_or_create(
                resource_type='learning_goal',
                resource_id=str(goal.pk),
                defaults={
                    'created_by': goal.user,
                    'access_level': 'owner',
                    'is_active': True,
                    'is_public': False,
                    'metadata': {
                        'migrated': True,
                        'source': 'teaching_app'
                    }
                }
            )
            if created:
                self.stdout.write(f'  ✓ 学习目标授权: {goal.pk}')
        
        # 迁移词汇学习目标
        vocab_goals = VocabLearningGoal.objects.all()
        for goal in vocab_goals:
            auth, created = ResourceAuthorization.objects.get_or_create(
                resource_type='vocab_learning_goal',
                resource_id=str(goal.pk),
                defaults={
                    'created_by': goal.user,
                    'access_level': 'owner',
                    'is_active': True,
                    'is_public': False,
                    'metadata': {
                        'migrated': True,
                        'source': 'vocabulary_manager_app'
                    }
                }
            )
            if created:
                self.stdout.write(f'  ✓ 词汇目标授权: {goal.pk}')
        
        # 迁移单词集
        word_sets = WordSet.objects.filter(created_by__isnull=False)
        for word_set in word_sets:
            auth, created = ResourceAuthorization.objects.get_or_create(
                resource_type='word_set',
                resource_id=str(word_set.pk),
                defaults={
                    'created_by': word_set.created_by,
                    'access_level': 'owner',
                    'is_active': True,
                    'is_public': False,
                    'metadata': {
                        'migrated': True,
                        'source': 'words_app'
                    }
                }
            )
            if created:
                self.stdout.write(f'  ✓ 单词集授权: {word_set.pk}')
        
        self.stdout.write(
            self.style.SUCCESS('现有资源迁移完成')
        )
    
    def create_demo_subscriptions(self):
        """为现有用户创建演示订阅"""
        self.stdout.write('为用户创建演示订阅...')
        
        # 获取基础功能
        basic_features = SubscriptionFeature.objects.filter(
            code__in=['basic_learning', 'resource_sharing']
        )
        
        # 为前10个用户创建基础订阅
        users = User.objects.filter(is_active=True)[:10]
        for user in users:
            subscription, created = UserSubscription.objects.get_or_create(
                user=user,
                defaults={
                    'subscription_type': 'basic',
                    'status': 'active',
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date() + timedelta(days=30),
                    'metadata': {
                        'demo': True,
                        'created_by_init': True
                    }
                }
            )
            
            if created:
                subscription.features.set(basic_features)
                self.stdout.write(
                    f'  ✓ 为用户 {user.username} 创建基础订阅'
                )
            else:
                self.stdout.write(
                    f'  - 用户 {user.username} 已有订阅'
                )
        
        self.stdout.write(
            self.style.SUCCESS('演示订阅创建完成')
        )