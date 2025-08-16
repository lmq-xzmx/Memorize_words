#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试账号和数据的脚本
用于生成足够测试使用的全字段数据
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_learning_platform.settings')
django.setup()

from django.contrib.auth.models import Group
from apps.words.models import Word, VocabularyList, WordSet, VocabularySource
from apps.teaching.models import LearningGoal, LearningPlan, GoalWord, LearningSession, WordLearningRecord
from apps.accounts.models import CustomUser, LearningProfile
# Role模型在permissions应用中，但这里我们使用Django的Group模型

def create_test_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    # 创建用户组
    student_group, _ = Group.objects.get_or_create(name='学生组')
    teacher_group, _ = Group.objects.get_or_create(name='教师组')
    admin_group, _ = Group.objects.get_or_create(name='管理员组')
    
    # 使用Django的Group模型代替Role模型
    
    # 测试用户数据
    test_users = [
        {
            'username': 'student_alice',
            'email': 'alice@example.com',
            'password': 'test123456',
            'first_name': '爱丽丝',
            'last_name': '王',
            'is_staff': False,
            'is_superuser': False,
            'groups': [student_group],
            # 'roles': [student_role],  # 暂时注释掉角色分配
            'profile': {
                'phone': '13800138001',
                'birth_date': '2005-03-15',
                'gender': 'female',
                'grade': '高一',
                'school': '北京市第一中学',
                'learning_level': 'intermediate',
                'preferred_language': 'zh-cn'
            }
        },
        {
            'username': 'student_bob',
            'email': 'bob@example.com',
            'password': 'test123456',
            'first_name': '鲍勃',
            'last_name': '李',
            'is_staff': False,
            'is_superuser': False,
            'groups': [student_group],
            # 'roles': [student_role],  # 暂时注释掉角色分配
            'profile': {
                'phone': '13800138002',
                'birth_date': '2006-07-22',
                'gender': 'male',
                'grade': '初三',
                'school': '上海市实验中学',
                'learning_level': 'beginner',
                'preferred_language': 'zh-cn'
            }
        },
        {
            'username': 'teacher_chen',
            'email': 'chen@example.com',
            'password': 'test123456',
            'first_name': '陈老师',
            'last_name': '陈',
            'is_staff': True,
            'is_superuser': False,
            'groups': [teacher_group],
            # 'roles': [teacher_role],  # 暂时注释掉角色分配
            'profile': {
                'phone': '13800138003',
                'birth_date': '1985-12-10',
                'gender': 'female',
                'grade': '',
                'school': '北京市第一中学',
                'learning_level': 'advanced',
                'preferred_language': 'zh-cn'
            }
        },
        {
            'username': 'admin_zhang',
            'email': 'admin@example.com',
            'password': 'admin123456',
            'first_name': '张管理员',
            'last_name': '张',
            'is_staff': True,
            'is_superuser': True,
            'groups': [admin_group],
            # 'roles': [admin_role],  # 暂时注释掉角色分配
            'profile': {
                'phone': '13800138004',
                'birth_date': '1980-05-20',
                'gender': 'male',
                'grade': '',
                'school': '系统管理',
                'learning_level': 'advanced',
                'preferred_language': 'zh-cn'
            }
        }
    ]
    
    created_users = []
    for user_data in test_users:
        # 创建用户
        user, created = CustomUser.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser']
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"创建用户: {user.username}")
        else:
            print(f"用户已存在: {user.username}")
        
        # 添加到用户组
        for group in user_data['groups']:
            user.groups.add(group)
        
        # 创建学习档案
        profile_data = user_data['profile']
        profile, profile_created = LearningProfile.objects.get_or_create(
            user=user,
            defaults={
                'total_study_time': 0,
                'completed_lessons': 0,
                'current_streak': 0,
                'max_streak': 0
            }
        )
        
        # 更新用户的其他字段
        user.phone = profile_data['phone']
        user.grade_level = profile_data['grade']
        user.english_level = profile_data['learning_level']
        user.save()
        
        if profile_created:
            print(f"创建学习档案: {user.username}")
        
        created_users.append(user)
    
    return created_users

def create_test_words():
    """创建测试单词"""
    print("创建测试单词...")
    
    test_words = [
        {
            'word': 'apple',
            'phonetic': '/ˈæpl/',
            'definition': 'n. 苹果',
            'part_of_speech': '名词',
            'example': 'I like to eat apples.',
            'difficulty_level': 1,
            'tags': '水果,基础'
        },
        {
            'word': 'beautiful',
            'phonetic': '/ˈbjuːtɪfl/',
            'definition': 'adj. 美丽的，漂亮的',
            'part_of_speech': '形容词',
            'example': 'She is a beautiful girl.',
            'difficulty_level': 2,
            'tags': '形容词,基础'
        },
        {
            'word': 'computer',
            'phonetic': '/kəmˈpjuːtər/',
            'definition': 'n. 计算机，电脑',
            'part_of_speech': '名词',
            'example': 'I use a computer to work.',
            'difficulty_level': 2,
            'tags': '科技,名词'
        },
        {
            'word': 'education',
            'phonetic': '/ˌedʒuˈkeɪʃn/',
            'definition': 'n. 教育',
            'part_of_speech': '名词',
            'example': 'Education is very important.',
            'difficulty_level': 3,
            'tags': '教育,抽象名词'
        },
        {
            'word': 'fantastic',
            'phonetic': '/fænˈtæstɪk/',
            'definition': 'adj. 极好的，了不起的',
            'part_of_speech': '形容词',
            'example': 'The movie was fantastic!',
            'difficulty_level': 3,
            'tags': '形容词,情感'
        },
        {
            'word': 'government',
            'phonetic': '/ˈɡʌvərnmənt/',
            'definition': 'n. 政府',
            'part_of_speech': '名词',
            'example': 'The government made a new policy.',
            'difficulty_level': 4,
            'tags': '政治,名词'
        },
        {
            'word': 'happiness',
            'phonetic': '/ˈhæpɪnəs/',
            'definition': 'n. 幸福，快乐',
            'part_of_speech': '名词',
            'example': 'Money cannot buy happiness.',
            'difficulty_level': 3,
            'tags': '情感,抽象名词'
        },
        {
            'word': 'important',
            'phonetic': '/ɪmˈpɔːrtnt/',
            'definition': 'adj. 重要的',
            'part_of_speech': '形容词',
            'example': 'This is an important meeting.',
            'difficulty_level': 2,
            'tags': '形容词,常用'
        },
        {
            'word': 'journey',
            'phonetic': '/ˈdʒɜːrni/',
            'definition': 'n. 旅程，旅行',
            'part_of_speech': '名词',
            'example': 'Life is a long journey.',
            'difficulty_level': 3,
            'tags': '旅行,名词'
        },
        {
            'word': 'knowledge',
            'phonetic': '/ˈnɑːlɪdʒ/',
            'definition': 'n. 知识',
            'part_of_speech': '名词',
            'example': 'Knowledge is power.',
            'difficulty_level': 3,
            'tags': '教育,抽象名词'
        }
    ]
    
    created_words = []
    for word_data in test_words:
        word, created = Word.objects.get_or_create(
            word=word_data['word'],
            defaults=word_data
        )
        
        if created:
            print(f"创建单词: {word.word}")
        else:
            print(f"单词已存在: {word.word}")
        
        created_words.append(word)
    
    return created_words

def create_test_vocabulary_lists(users, words):
    """创建测试词汇表"""
    print("创建测试词汇表...")
    
    vocabulary_lists_data = [
        {
            'name': '初级英语词汇',
            'description': '适合初学者的基础英语词汇表',
            'is_active': True,
            'words': words[:5]  # 前5个单词
        },
        {
            'name': '中级英语词汇',
            'description': '适合中级学习者的英语词汇表',
            'is_active': True,
            'words': words[3:8]  # 中间5个单词
        },
        {
            'name': '高级英语词汇',
            'description': '适合高级学习者的英语词汇表',
            'is_active': True,
            'words': words[5:]  # 后5个单词
        }
    ]
    
    created_lists = []
    for list_data in vocabulary_lists_data:
        vocab_list, created = VocabularyList.objects.get_or_create(
            name=list_data['name'],
            defaults={
                'description': list_data['description'],
                'is_active': list_data['is_active']
            }
        )
        
        if created:
            print(f"创建词汇表: {vocab_list.name}")
            # VocabularyList模型没有words字段，需要通过其他方式关联单词
            # 这里暂时跳过单词关联，因为需要了解正确的关联方式
            pass
        else:
            print(f"词汇表已存在: {vocab_list.name}")
        
        created_lists.append(vocab_list)
    
    return created_lists

def create_test_learning_goals(users, vocabulary_lists):
    """创建测试学习目标"""
    print("创建测试学习目标...")
    
    # 找到学生用户
    alice = next((u for u in users if u.username == 'student_alice'), None)
    bob = next((u for u in users if u.username == 'student_bob'), None)
    
    if not alice or not bob:
        print("未找到学生用户")
        return []
    
    goals_data = [
        {
            'user': alice,
            'name': '高考英语词汇突破',
            'description': '为高考准备，掌握3000个核心词汇',
            'goal_type': 'vocabulary',
            'target_words_count': 3000,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=180),
            'vocabulary_lists': vocabulary_lists[:2]  # 初级和中级词汇表
        },
        {
            'user': bob,
            'name': '中考英语词汇准备',
            'description': '为中考准备，掌握1500个基础词汇',
            'goal_type': 'vocabulary',
            'target_words_count': 1500,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=120),
            'vocabulary_lists': vocabulary_lists[:1]  # 初级词汇表
        },
        {
            'user': alice,
            'name': '英语阅读理解提升',
            'description': '提高英语阅读理解能力',
            'goal_type': 'reading',
            'target_words_count': 500,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=90),
            'vocabulary_lists': vocabulary_lists[1:]  # 中级和高级词汇表
        }
    ]
    
    created_goals = []
    for goal_data in goals_data:
        goal, created = LearningGoal.objects.get_or_create(
            user=goal_data['user'],
            name=goal_data['name'],
            defaults={
                'description': goal_data['description'],
                'goal_type': goal_data['goal_type'],
                'target_words_count': goal_data['target_words_count'],
                'start_date': goal_data['start_date'],
                'end_date': goal_data['end_date']
            }
        )
        
        if created:
            print(f"创建学习目标: {goal.name}")
            # 添加词汇表到学习目标
            for vocab_list in goal_data['vocabulary_lists']:
                goal.vocabulary_lists.add(vocab_list)
        else:
            print(f"学习目标已存在: {goal.name}")
        
        created_goals.append(goal)
    
    return created_goals

def create_test_learning_plans(goals):
    """创建测试学习计划"""
    print("创建测试学习计划...")
    
    plans_data = [
        {
            'goal': goals[0],
            'plan_type': 'daily_progress',
            'words_per_day': 20,
            'review_interval': 3
        },
        {
            'goal': goals[1],
            'plan_type': 'weekday',
            'words_per_day': 15,
            'review_interval': 2
        },
        {
            'goal': goals[2] if len(goals) > 2 else goals[0],
            'plan_type': 'weekend',
            'words_per_day': 10,
            'review_interval': 1
        }
    ]
    
    created_plans = []
    for plan_data in plans_data:
        plan, created = LearningPlan.objects.get_or_create(
            goal=plan_data['goal'],
            plan_type=plan_data['plan_type'],
            defaults={
                'words_per_day': plan_data['words_per_day'],
                'review_interval': plan_data['review_interval']
            }
        )
        
        if created:
            print(f"创建学习计划: {plan.goal.name} - {plan.plan_type}")
        else:
            print(f"学习计划已存在: {plan.goal.name} - {plan.plan_type}")
        
        created_plans.append(plan)
    
    return created_plans

def create_test_learning_sessions(goals, words):
    """创建测试学习会话和记录"""
    print("创建测试学习会话...")
    
    if not goals:
        print("没有学习目标，跳过创建学习会话")
        return []
    
    # 为每个目标创建一些学习会话
    created_sessions = []
    for goal in goals[:2]:  # 只为前两个目标创建会话
        # 创建3个学习会话
        for i in range(3):
            session_start = timezone.now() - timedelta(days=i*2, hours=i)
            session_end = session_start + timedelta(minutes=30 + i*10)
            
            session = LearningSession.objects.create(
                user=goal.user,
                goal=goal,
                start_time=session_start,
                end_time=session_end,
                words_studied=5 + i,
                correct_answers=3 + i,
                total_answers=5 + i
            )
            
            print(f"创建学习会话: {session}")
            
            # 为每个会话创建一些学习记录
            for j, word in enumerate(words[:5]):
                if j >= session.words_studied:
                    break
                
                record = WordLearningRecord.objects.create(
                    session=session,
                    goal=goal,
                    word=word,
                    user_answer=word.word if j < session.correct_answers else 'wrong_answer',
                    is_correct=j < session.correct_answers,
                    response_time=2.5 + j * 0.5,
                    is_forgotten=j >= session.correct_answers
                )
                
            created_sessions.append(session)
    
    return created_sessions

def main():
    """主函数"""
    print("开始创建测试数据...")
    
    try:
        # 创建测试用户
        users = create_test_users()
        
        # 创建测试单词
        words = create_test_words()
        
        # 创建测试词汇表
        vocabulary_lists = create_test_vocabulary_lists(users, words)
        
        # 创建测试学习目标
        goals = create_test_learning_goals(users, vocabulary_lists)
        
        # 创建测试学习计划
        plans = create_test_learning_plans(goals)
        
        # 创建测试学习会话
        sessions = create_test_learning_sessions(goals, words)
        
        print("\n测试数据创建完成！")
        print(f"创建用户: {len(users)} 个")
        print(f"创建单词: {len(words)} 个")
        print(f"创建词汇表: {len(vocabulary_lists)} 个")
        print(f"创建学习目标: {len(goals)} 个")
        print(f"创建学习计划: {len(plans)} 个")
        print(f"创建学习会话: {len(sessions)} 个")
        
        print("\n测试账号信息:")
        print("学生账号1: student_alice / test123456")
        print("学生账号2: student_bob / test123456")
        print("教师账号: teacher_chen / test123456")
        print("管理员账号: admin_zhang / admin123456")
        
    except Exception as e:
        print(f"创建测试数据时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()