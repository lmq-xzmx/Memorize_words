from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import UserRole, RoleExtension, UserExtensionData, LearningProfile
from rest_framework.authtoken.models import Token
import random

User = get_user_model()

class Command(BaseCommand):
    help = '创建开发环境测试用户'

    def handle(self, *args, **options):
        # 创建超级管理员
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'real_name': '系统管理员',
                'role': UserRole.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            Token.objects.get_or_create(user=admin_user)
            self.stdout.write(f'创建管理员: {getattr(admin_user, "username", "unknown")} / admin123')
        else:
            self.stdout.write(f'管理员已存在: {getattr(admin_user, "username", "unknown")}')

        # 创建教师用户
        teachers_data = [
            {'username': 'teacher1', 'real_name': '张老师', 'email': 'teacher1@example.com'},
            {'username': 'teacher2', 'real_name': '李老师', 'email': 'teacher2@example.com'},
            {'username': 'teacher3', 'real_name': '王老师', 'email': 'teacher3@example.com'},
        ]
        
        for teacher_data in teachers_data:
            teacher, created = User.objects.get_or_create(
                username=teacher_data['username'],
                defaults={
                    'email': teacher_data['email'],
                    'real_name': teacher_data['real_name'],
                    'role': UserRole.TEACHER,
                    'is_active': True,
                }
            )
            if created:
                teacher.set_password('teacher123')
                teacher.save()
                Token.objects.get_or_create(user=teacher)
                self.stdout.write(f'创建教师: {getattr(teacher, "username", "unknown")} / teacher123')
            else:
                self.stdout.write(f'教师已存在: {getattr(teacher, "username", "unknown")}')

        # 创建学生用户
        students_data = [
            {'username': 'student1', 'real_name': '小明', 'email': 'student1@example.com', 'grade_level': '小学三年级'},
            {'username': 'student2', 'real_name': '小红', 'email': 'student2@example.com', 'grade_level': '小学四年级'},
            {'username': 'student3', 'real_name': '小刚', 'email': 'student3@example.com', 'grade_level': '小学五年级'},
            {'username': 'student4', 'real_name': '小丽', 'email': 'student4@example.com', 'grade_level': '小学六年级'},
            {'username': 'student5', 'real_name': '小华', 'email': 'student5@example.com', 'grade_level': '小学三年级'},
        ]
        
        for student_data in students_data:
            student, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'real_name': student_data['real_name'],
                    'role': UserRole.STUDENT,
                    'is_active': True,
                    'grade_level': student_data['grade_level'],
                    'english_level': random.choice(['beginner', 'elementary', 'intermediate', 'advanced']),
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                Token.objects.get_or_create(user=student)
                
                # 学习档案将在用户首次登录时自动创建
                
                self.stdout.write(f'创建学生: {getattr(student, "username", "unknown")} / student123')
            else:
                self.stdout.write(f'学生已存在: {getattr(student, "username", "unknown")}')

        # 创建家长用户
        parents_data = [
            {'username': 'parent1', 'real_name': '张家长', 'email': 'parent1@example.com'},
            {'username': 'parent2', 'real_name': '李家长', 'email': 'parent2@example.com'},
        ]
        
        for parent_data in parents_data:
            parent, created = User.objects.get_or_create(
                username=parent_data['username'],
                defaults={
                    'email': parent_data['email'],
                    'real_name': parent_data['real_name'],
                    'role': UserRole.PARENT,
                    'is_active': True,
                }
            )
            if created:
                parent.set_password('parent123')
                parent.save()
                Token.objects.get_or_create(user=parent)
                self.stdout.write(f'创建家长: {getattr(parent, "username", "unknown")} / parent123')
            else:
                self.stdout.write(f'家长已存在: {getattr(parent, "username", "unknown")}')

        # 创建角色扩展字段示例
        self.create_role_extensions()
        
        self.stdout.write(self.style.SUCCESS('\n开发环境用户创建完成!'))
        self.stdout.write('\n快捷登录信息:')
        self.stdout.write('管理员: admin / admin123')
        self.stdout.write('教师: teacher1 / teacher123')
        self.stdout.write('学生: student1 / student123')
        self.stdout.write('家长: parent1 / parent123')

    def create_role_extensions(self):
        """创建角色扩展字段示例"""
        extensions = [
            {
                'role': UserRole.STUDENT,
                'field_name': 'english_level',
                'field_label': '英语水平',
                'field_type': 'choice',
                'choices': 'beginner:初级,intermediate:中级,advanced:高级',
                'is_required': True,
                'show_in_frontend_register': True,
                'show_in_backend_admin': True,
                'sort_order': 1,
            },
            {
                'role': UserRole.STUDENT,
                'field_name': 'grade',
                'field_label': '年级',
                'field_type': 'choice',
                'choices': '一年级,二年级,三年级,四年级,五年级,六年级',
                'is_required': True,
                'show_in_frontend_register': True,
                'show_in_backend_admin': True,
                'sort_order': 2,
            },
            {
                'role': UserRole.TEACHER,
                'field_name': 'subject',
                'field_label': '教学科目',
                'field_type': 'text',
                'is_required': False,
                'show_in_frontend_register': True,
                'show_in_backend_admin': True,
                'sort_order': 1,
            },
            {
                'role': UserRole.PARENT,
                'field_name': 'children_info',
                'field_label': '孩子信息',
                'field_type': 'textarea',
                'is_required': False,
                'show_in_frontend_register': True,
                'show_in_backend_admin': True,
                'sort_order': 1,
            },
        ]
        
        for ext_data in extensions:
            extension, created = RoleExtension.objects.get_or_create(
                role=ext_data['role'],
                field_name=ext_data['field_name'],
                defaults=ext_data
            )
            if created:
                self.stdout.write(f'创建角色扩展字段: {ext_data["role"]} - {ext_data["field_name"]}')