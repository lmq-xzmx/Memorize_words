from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import (
    CustomUser, UserRole, RoleExtension, UserExtensionData, LearningProfile,
    RoleTemplate, RoleLevel, RoleUser, UserExtension, RoleUserGroup
)
from rest_framework.authtoken.models import Token
import random
import json
from datetime import date, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = '创建全面的测试数据 - 包含多个角色和完整的用户信息'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有测试数据后重新创建',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.clear_existing_data()
        
        self.stdout.write(self.style.SUCCESS('开始创建全面测试数据...'))
        
        # 创建角色模板和扩展字段
        self.create_role_templates_and_extensions()
        
        # 创建管理员用户
        self.create_admin_users()
        
        # 创建教师用户
        self.create_teacher_users()
        
        # 创建学生用户
        self.create_student_users()
        
        # 创建家长用户
        self.create_parent_users()
        
        # 创建角色用户组
        self.create_role_user_groups()
        
        # 为用户填充扩展数据
        self.populate_user_extension_data()
        
        # 创建学习档案
        self.create_learning_profiles()
        
        self.stdout.write(self.style.SUCCESS('\n全面测试数据创建完成!'))
        self.print_login_info()

    def clear_existing_data(self):
        """清除现有测试数据"""
        self.stdout.write('清除现有测试数据...')
        
        # 删除测试用户（保留真实用户）
        test_usernames = [
            'admin', 'admin2', 'admin3',
            'teacher1', 'teacher2', 'teacher3', 'teacher4', 'teacher5',
            'student1', 'student2', 'student3', 'student4', 'student5', 
            'student6', 'student7', 'student8', 'student9', 'student10',
            'parent1', 'parent2', 'parent3', 'parent4', 'parent5'
        ]
        
        CustomUser.objects.filter(username__in=test_usernames).delete()
        
        # 清除角色相关数据
        RoleUserGroup.objects.all().delete()
        UserExtension.objects.all().delete()
        RoleUser.objects.all().delete()
        UserExtensionData.objects.all().delete()
        
        self.stdout.write('测试数据清除完成')

    def create_role_templates_and_extensions(self):
        """创建角色模板和扩展字段"""
        self.stdout.write('创建角色模板和扩展字段...')
        
        # 角色模板配置
        role_templates = [
            {
                'role': UserRole.ADMIN,
                'template_name': '管理员模板',
                'description': '系统管理员角色模板，包含系统管理相关字段',
                'extensions': [
                    {
                        'field_name': 'department',
                        'field_label': '所属部门',
                        'field_type': 'choice',
                        'field_choices': json.dumps([['tech', '技术部'], ['edu', '教育部'], ['admin', '行政部'], ['hr', '人事部']]),
                        'is_required': True,
                        'sort_order': 1
                    },
                    {
                        'field_name': 'employee_id',
                        'field_label': '员工编号',
                        'field_type': 'text',
                        'is_required': True,
                        'sort_order': 2
                    },
                    {
                        'field_name': 'access_level',
                        'field_label': '权限级别',
                        'field_type': 'choice',
                        'field_choices': json.dumps([['super', '超级管理员'], ['admin', '普通管理员'], ['operator', '操作员']]),
                        'is_required': True,
                        'sort_order': 3
                    }
                ]
            },
            {
                'role': UserRole.TEACHER,
                'template_name': '教师模板',
                'description': '教师角色模板，包含教学相关字段',
                'extensions': [
                    {
                        'field_name': 'subject',
                        'field_label': '教学科目',
                        'field_type': 'choice',
                        'field_choices': json.dumps([['english', '英语'], ['math', '数学'], ['chinese', '语文'], ['science', '科学']]),
                        'is_required': True,
                        'sort_order': 1
                    },
                    {
                        'field_name': 'teaching_experience',
                        'field_label': '教学经验(年)',
                        'field_type': 'number',
                        'is_required': False,
                        'sort_order': 2
                    },
                    {
                        'field_name': 'qualification',
                        'field_label': '教师资格证',
                        'field_type': 'text',
                        'is_required': False,
                        'sort_order': 3
                    },
                    {
                        'field_name': 'specialization',
                        'field_label': '专业特长',
                        'field_type': 'textarea',
                        'is_required': False,
                        'sort_order': 4
                    }
                ]
            },
            {
                'role': UserRole.STUDENT,
                'template_name': '学生模板',
                'description': '学生角色模板，包含学习相关字段',
                'extensions': [
                    {
                        'field_name': 'school',
                        'field_label': '就读学校',
                        'field_type': 'text',
                        'is_required': False,
                        'sort_order': 1
                    },
                    {
                        'field_name': 'class_name',
                        'field_label': '班级',
                        'field_type': 'text',
                        'is_required': False,
                        'sort_order': 2
                    },
                    {
                        'field_name': 'learning_goals',
                        'field_label': '学习目标',
                        'field_type': 'textarea',
                        'is_required': False,
                        'sort_order': 3
                    },
                    {
                        'field_name': 'interests',
                        'field_label': '兴趣爱好',
                        'field_type': 'textarea',
                        'is_required': False,
                        'sort_order': 4
                    },
                    {
                        'field_name': 'parent_contact',
                        'field_label': '家长联系方式',
                        'field_type': 'phone',
                        'is_required': False,
                        'sort_order': 5
                    }
                ]
            },
            {
                'role': UserRole.PARENT,
                'template_name': '家长模板',
                'description': '家长角色模板，包含家庭相关字段',
                'extensions': [
                    {
                        'field_name': 'occupation',
                        'field_label': '职业',
                        'field_type': 'text',
                        'is_required': False,
                        'sort_order': 1
                    },
                    {
                        'field_name': 'children_count',
                        'field_label': '孩子数量',
                        'field_type': 'number',
                        'is_required': False,
                        'sort_order': 2
                    },
                    {
                        'field_name': 'education_background',
                        'field_label': '教育背景',
                        'field_type': 'choice',
                        'field_choices': json.dumps([['high_school', '高中'], ['college', '大专'], ['bachelor', '本科'], ['master', '硕士'], ['phd', '博士']]),
                        'is_required': False,
                        'sort_order': 3
                    },
                    {
                        'field_name': 'expectations',
                        'field_label': '对孩子的期望',
                        'field_type': 'textarea',
                        'is_required': False,
                        'sort_order': 4
                    }
                ]
            }
        ]
        
        for template_data in role_templates:
            # 创建角色模板
            template, created = RoleTemplate.objects.get_or_create(
                role=template_data['role'],
                defaults={
                    'template_name': template_data['template_name'],
                    'description': template_data['description'],
                    'version': '1.0.0',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'创建角色模板: {template.template_name}')
            
            # 创建扩展字段
            for ext_data in template_data['extensions']:
                extension, created = RoleExtension.objects.get_or_create(
                    role_template=template,
                    role=template_data['role'],
                    field_name=ext_data['field_name'],
                    defaults={
                        'field_label': ext_data['field_label'],
                        'field_type': ext_data['field_type'],
                        'field_choices': ext_data.get('field_choices', ''),
                        'is_required': ext_data.get('is_required', False),
                        'sort_order': ext_data.get('sort_order', 0),
                        'show_in_frontend_register': True,
                        'show_in_backend_admin': True,
                        'show_in_profile': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  创建扩展字段: {ext_data["field_label"]}')

    def create_admin_users(self):
        """创建管理员用户"""
        self.stdout.write('创建管理员用户...')
        
        admin_users = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'real_name': '系统管理员',
                'nickname': '超级管理员',
                'phone': '13800138000',
                'is_staff': True,
                'is_superuser': True,
                'password': 'admin123'
            },
            {
                'username': 'admin2',
                'email': 'admin2@example.com',
                'real_name': '张管理',
                'nickname': '技术管理员',
                'phone': '13800138001',
                'is_staff': True,
                'is_superuser': False,
                'password': 'admin123'
            },
            {
                'username': 'admin3',
                'email': 'admin3@example.com',
                'real_name': '李管理',
                'nickname': '教育管理员',
                'phone': '13800138002',
                'is_staff': True,
                'is_superuser': False,
                'password': 'admin123'
            }
        ]
        
        for admin_data in admin_users:
            admin_user, created = CustomUser.objects.get_or_create(
                username=admin_data['username'],
                defaults={
                    'email': admin_data['email'],
                    'real_name': admin_data['real_name'],
                    'nickname': admin_data['nickname'],
                    'phone': admin_data['phone'],
                    'role': UserRole.ADMIN,
                    'is_staff': admin_data['is_staff'],
                    'is_superuser': admin_data['is_superuser'],
                    'is_active': True,
                    'admin_approval_status': 'approved'
                }
            )
            
            if created:
                admin_user.set_password(admin_data['password'])
                admin_user.save()
                Token.objects.get_or_create(user=admin_user)
                self.stdout.write(f'创建管理员: {admin_user.username} / {admin_data["password"]}')
            else:
                self.stdout.write(f'管理员已存在: {admin_user.username}')

    def create_teacher_users(self):
        """创建教师用户"""
        self.stdout.write('创建教师用户...')
        
        teacher_users = [
            {
                'username': 'teacher1',
                'email': 'teacher1@example.com',
                'real_name': '张老师',
                'nickname': '英语张老师',
                'phone': '13900139001'
            },
            {
                'username': 'teacher2',
                'email': 'teacher2@example.com',
                'real_name': '李老师',
                'nickname': '数学李老师',
                'phone': '13900139002'
            },
            {
                'username': 'teacher3',
                'email': 'teacher3@example.com',
                'real_name': '王老师',
                'nickname': '语文王老师',
                'phone': '13900139003'
            },
            {
                'username': 'teacher4',
                'email': 'teacher4@example.com',
                'real_name': '赵老师',
                'nickname': '科学赵老师',
                'phone': '13900139004'
            },
            {
                'username': 'teacher5',
                'email': 'teacher5@example.com',
                'real_name': '刘老师',
                'nickname': '英语刘老师',
                'phone': '13900139005'
            }
        ]
        
        for teacher_data in teacher_users:
            teacher, created = CustomUser.objects.get_or_create(
                username=teacher_data['username'],
                defaults={
                    'email': teacher_data['email'],
                    'real_name': teacher_data['real_name'],
                    'nickname': teacher_data['nickname'],
                    'phone': teacher_data['phone'],
                    'role': UserRole.TEACHER,
                    'is_active': True,
                    'admin_approval_status': 'approved'
                }
            )
            
            if created:
                teacher.set_password('teacher123')
                teacher.save()
                Token.objects.get_or_create(user=teacher)
                self.stdout.write(f'创建教师: {teacher.username} / teacher123')
            else:
                self.stdout.write(f'教师已存在: {teacher.username}')

    def create_student_users(self):
        """创建学生用户"""
        self.stdout.write('创建学生用户...')
        
        student_users = [
            {
                'username': 'student1',
                'email': 'student1@example.com',
                'real_name': '张小明',
                'nickname': '小明',
                'phone': '13700137001',
                'grade_level': '小学三年级',
                'english_level': 'beginner'
            },
            {
                'username': 'student2',
                'email': 'student2@example.com',
                'real_name': '李小红',
                'nickname': '小红',
                'phone': '13700137002',
                'grade_level': '小学四年级',
                'english_level': 'elementary'
            },
            {
                'username': 'student3',
                'email': 'student3@example.com',
                'real_name': '王小刚',
                'nickname': '小刚',
                'phone': '13700137003',
                'grade_level': '小学五年级',
                'english_level': 'intermediate'
            },
            {
                'username': 'student4',
                'email': 'student4@example.com',
                'real_name': '赵小丽',
                'nickname': '小丽',
                'phone': '13700137004',
                'grade_level': '小学六年级',
                'english_level': 'intermediate'
            },
            {
                'username': 'student5',
                'email': 'student5@example.com',
                'real_name': '刘小华',
                'nickname': '小华',
                'phone': '13700137005',
                'grade_level': '小学三年级',
                'english_level': 'beginner'
            },
            {
                'username': 'student6',
                'email': 'student6@example.com',
                'real_name': '陈小军',
                'nickname': '小军',
                'phone': '13700137006',
                'grade_level': '小学四年级',
                'english_level': 'elementary'
            },
            {
                'username': 'student7',
                'email': 'student7@example.com',
                'real_name': '周小芳',
                'nickname': '小芳',
                'phone': '13700137007',
                'grade_level': '小学五年级',
                'english_level': 'intermediate'
            },
            {
                'username': 'student8',
                'email': 'student8@example.com',
                'real_name': '吴小强',
                'nickname': '小强',
                'phone': '13700137008',
                'grade_level': '小学六年级',
                'english_level': 'advanced'
            },
            {
                'username': 'student9',
                'email': 'student9@example.com',
                'real_name': '郑小美',
                'nickname': '小美',
                'phone': '13700137009',
                'grade_level': '小学三年级',
                'english_level': 'beginner'
            },
            {
                'username': 'student10',
                'email': 'student10@example.com',
                'real_name': '孙小亮',
                'nickname': '小亮',
                'phone': '13700137010',
                'grade_level': '小学四年级',
                'english_level': 'elementary'
            }
        ]
        
        for student_data in student_users:
            student, created = CustomUser.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'real_name': student_data['real_name'],
                    'nickname': student_data['nickname'],
                    'phone': student_data['phone'],
                    'role': UserRole.STUDENT,
                    'is_active': True,
                    'grade_level': student_data['grade_level'],
                    'english_level': student_data['english_level'],
                    'admin_approval_status': 'approved'
                }
            )
            
            if created:
                student.set_password('student123')
                student.save()
                Token.objects.get_or_create(user=student)
                self.stdout.write(f'创建学生: {student.username} / student123')
            else:
                self.stdout.write(f'学生已存在: {student.username}')

    def create_parent_users(self):
        """创建家长用户"""
        self.stdout.write('创建家长用户...')
        
        parent_users = [
            {
                'username': 'parent1',
                'email': 'parent1@example.com',
                'real_name': '张家长',
                'nickname': '小明爸爸',
                'phone': '13600136001'
            },
            {
                'username': 'parent2',
                'email': 'parent2@example.com',
                'real_name': '李家长',
                'nickname': '小红妈妈',
                'phone': '13600136002'
            },
            {
                'username': 'parent3',
                'email': 'parent3@example.com',
                'real_name': '王家长',
                'nickname': '小刚爸爸',
                'phone': '13600136003'
            },
            {
                'username': 'parent4',
                'email': 'parent4@example.com',
                'real_name': '赵家长',
                'nickname': '小丽妈妈',
                'phone': '13600136004'
            },
            {
                'username': 'parent5',
                'email': 'parent5@example.com',
                'real_name': '刘家长',
                'nickname': '小华爸爸',
                'phone': '13600136005'
            }
        ]
        
        for parent_data in parent_users:
            parent, created = CustomUser.objects.get_or_create(
                username=parent_data['username'],
                defaults={
                    'email': parent_data['email'],
                    'real_name': parent_data['real_name'],
                    'nickname': parent_data['nickname'],
                    'phone': parent_data['phone'],
                    'role': UserRole.PARENT,
                    'is_active': True,
                    'admin_approval_status': 'approved'
                }
            )
            
            if created:
                parent.set_password('parent123')
                parent.save()
                Token.objects.get_or_create(user=parent)
                self.stdout.write(f'创建家长: {parent.username} / parent123')
            else:
                self.stdout.write(f'家长已存在: {parent.username}')

    def create_role_user_groups(self):
        """创建角色用户组"""
        self.stdout.write('创建角色用户组...')
        
        # 教师组
        teacher_group, created = RoleUserGroup.objects.get_or_create(
            name='英语教师组',
            role=UserRole.TEACHER,
            defaults={
                'description': '专门负责英语教学的教师组',
                'is_active': True
            }
        )
        if created:
            # 添加英语教师
            english_teachers = CustomUser.objects.filter(
                role=UserRole.TEACHER,
                username__in=['teacher1', 'teacher5']
            )
            teacher_group.users.set(english_teachers)
            self.stdout.write('创建英语教师组')
        
        # 学生组
        student_groups = [
            {
                'name': '三年级学生组',
                'description': '小学三年级学生组',
                'grade': '小学三年级'
            },
            {
                'name': '四年级学生组',
                'description': '小学四年级学生组',
                'grade': '小学四年级'
            },
            {
                'name': '五年级学生组',
                'description': '小学五年级学生组',
                'grade': '小学五年级'
            },
            {
                'name': '六年级学生组',
                'description': '小学六年级学生组',
                'grade': '小学六年级'
            }
        ]
        
        for group_data in student_groups:
            group, created = RoleUserGroup.objects.get_or_create(
                name=group_data['name'],
                role=UserRole.STUDENT,
                defaults={
                    'description': group_data['description'],
                    'is_active': True
                }
            )
            if created:
                # 添加对应年级的学生
                students = CustomUser.objects.filter(
                    role=UserRole.STUDENT,
                    grade_level=group_data['grade']
                )
                group.users.set(students)
                self.stdout.write(f'创建{group_data["name"]}')

    def populate_user_extension_data(self):
        """为用户填充扩展数据"""
        self.stdout.write('填充用户扩展数据...')
        
        # 管理员扩展数据
        admin_extension_data = {
            'admin': {'department': 'admin', 'employee_id': 'A001', 'access_level': 'super'},
            'admin2': {'department': 'tech', 'employee_id': 'A002', 'access_level': 'admin'},
            'admin3': {'department': 'edu', 'employee_id': 'A003', 'access_level': 'admin'}
        }
        
        # 教师扩展数据
        teacher_extension_data = {
            'teacher1': {'subject': 'english', 'teaching_experience': '5', 'qualification': 'TEM-8', 'specialization': '少儿英语教学，口语训练'},
            'teacher2': {'subject': 'math', 'teaching_experience': '8', 'qualification': '数学教师资格证', 'specialization': '小学数学基础教学'},
            'teacher3': {'subject': 'chinese', 'teaching_experience': '10', 'qualification': '语文教师资格证', 'specialization': '阅读理解，作文指导'},
            'teacher4': {'subject': 'science', 'teaching_experience': '3', 'qualification': '科学教师资格证', 'specialization': '实验教学，科学启蒙'},
            'teacher5': {'subject': 'english', 'teaching_experience': '7', 'qualification': 'TESOL', 'specialization': '英语语法，听力训练'}
        }
        
        # 学生扩展数据
        student_extension_data = {
            'student1': {'school': '实验小学', 'class_name': '三年级一班', 'learning_goals': '提高英语口语能力', 'interests': '画画，唱歌', 'parent_contact': '13600136001'},
            'student2': {'school': '实验小学', 'class_name': '四年级二班', 'learning_goals': '英语考试成绩提升', 'interests': '跳舞，阅读', 'parent_contact': '13600136002'},
            'student3': {'school': '育才小学', 'class_name': '五年级一班', 'learning_goals': '英语写作能力提升', 'interests': '足球，编程', 'parent_contact': '13600136003'},
            'student4': {'school': '育才小学', 'class_name': '六年级三班', 'learning_goals': '准备中学英语', 'interests': '钢琴，书法', 'parent_contact': '13600136004'},
            'student5': {'school': '实验小学', 'class_name': '三年级二班', 'learning_goals': '英语基础打牢', 'interests': '游泳，画画', 'parent_contact': '13600136005'},
            'student6': {'school': '明德小学', 'class_name': '四年级一班', 'learning_goals': '英语听力提升', 'interests': '篮球，音乐', 'parent_contact': '13600136001'},
            'student7': {'school': '明德小学', 'class_name': '五年级二班', 'learning_goals': '英语综合能力', 'interests': '舞蹈，手工', 'parent_contact': '13600136002'},
            'student8': {'school': '育才小学', 'class_name': '六年级一班', 'learning_goals': '英语竞赛准备', 'interests': '围棋，阅读', 'parent_contact': '13600136003'},
            'student9': {'school': '实验小学', 'class_name': '三年级三班', 'learning_goals': '英语兴趣培养', 'interests': '唱歌，跳绳', 'parent_contact': '13600136004'},
            'student10': {'school': '明德小学', 'class_name': '四年级三班', 'learning_goals': '英语词汇积累', 'interests': '乒乓球，绘画', 'parent_contact': '13600136005'}
        }
        
        # 家长扩展数据
        parent_extension_data = {
            'parent1': {'occupation': '软件工程师', 'children_count': '1', 'education_background': 'bachelor', 'expectations': '希望孩子能够流利地用英语交流'},
            'parent2': {'occupation': '教师', 'children_count': '1', 'education_background': 'master', 'expectations': '培养孩子的英语学习兴趣和习惯'},
            'parent3': {'occupation': '医生', 'children_count': '2', 'education_background': 'master', 'expectations': '提高孩子的英语成绩和综合能力'},
            'parent4': {'occupation': '会计师', 'children_count': '1', 'education_background': 'bachelor', 'expectations': '为孩子升学做好英语准备'},
            'parent5': {'occupation': '销售经理', 'children_count': '1', 'education_background': 'college', 'expectations': '让孩子在英语方面有所突破'}
        }
        
        # 填充数据
        all_extension_data = {
            **admin_extension_data,
            **teacher_extension_data,
            **student_extension_data,
            **parent_extension_data
        }
        
        for username, data in all_extension_data.items():
            try:
                user = CustomUser.objects.get(username=username)
                role_extensions = RoleExtension.objects.filter(role=user.role)
                
                for extension in role_extensions:
                    if extension.field_name in data:
                        extension_data, created = UserExtensionData.objects.get_or_create(
                            user=user,
                            role_extension=extension,
                            defaults={'field_value': data[extension.field_name]}
                        )
                        if created:
                            self.stdout.write(f'  {username}: {extension.field_label} = {data[extension.field_name]}')
            except CustomUser.DoesNotExist:
                continue

    def create_learning_profiles(self):
        """创建学习档案"""
        self.stdout.write('创建学习档案...')
        
        students = CustomUser.objects.filter(role=UserRole.STUDENT)
        for student in students:
            profile, created = LearningProfile.objects.get_or_create(
                user=student,
                defaults={
                    'total_study_time': random.randint(100, 1000),
                    'completed_lessons': random.randint(10, 100),
                    'current_streak': random.randint(0, 30),
                    'max_streak': random.randint(5, 50),
                    'last_study_date': timezone.now().date() - timedelta(days=random.randint(0, 7))
                }
            )
            if created:
                self.stdout.write(f'创建学习档案: {student.username}')

    def print_login_info(self):
        """打印登录信息"""
        self.stdout.write('\n=== 测试账号登录信息 ===')
        self.stdout.write('\n管理员账号:')
        self.stdout.write('  admin / admin123 (超级管理员)')
        self.stdout.write('  admin2 / admin123 (技术管理员)')
        self.stdout.write('  admin3 / admin123 (教育管理员)')
        
        self.stdout.write('\n教师账号:')
        for i in range(1, 6):
            self.stdout.write(f'  teacher{i} / teacher123')
        
        self.stdout.write('\n学生账号:')
        for i in range(1, 11):
            self.stdout.write(f'  student{i} / student123')
        
        self.stdout.write('\n家长账号:')
        for i in range(1, 6):
            self.stdout.write(f'  parent{i} / parent123')
        
        self.stdout.write('\n=== 数据统计 ===')
        self.stdout.write(f'管理员: {CustomUser.objects.filter(role=UserRole.ADMIN).count()} 人')
        self.stdout.write(f'教师: {CustomUser.objects.filter(role=UserRole.TEACHER).count()} 人')
        self.stdout.write(f'学生: {CustomUser.objects.filter(role=UserRole.STUDENT).count()} 人')
        self.stdout.write(f'家长: {CustomUser.objects.filter(role=UserRole.PARENT).count()} 人')
        self.stdout.write(f'角色模板: {RoleTemplate.objects.count()} 个')
        self.stdout.write(f'扩展字段: {RoleExtension.objects.count()} 个')
        self.stdout.write(f'用户组: {RoleUserGroup.objects.count()} 个')
        self.stdout.write(f'学习档案: {LearningProfile.objects.count()} 个')