from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.accounts.models import UserRole
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    help = '创建默认学生用户用于文章预览'

    def handle(self, *args, **options):
        self.stdout.write('创建默认学生用户...')
        
        try:
            with transaction.atomic():
                # 创建默认学生
                default_student, created = User.objects.get_or_create(
                    username='default_student',
                    defaults={
                        'email': 'default_student@example.com',
                        'real_name': '张小明',
                        'nickname': '小明同学',
                        'phone': '13800138000',
                        'role': UserRole.STUDENT,
                        'grade_level': '小学四年级',
                        'english_level': 'elementary',
                        'is_active': True,
                        'admin_approval_status': 'approved'
                    }
                )
                
                if created:
                    default_student.set_password('student123')
                    default_student.save()
                    Token.objects.get_or_create(user=default_student)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'成功创建默认学生: {default_student.real_name} ({default_student.username})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'默认学生已存在: {default_student.real_name} ({default_student.username})'
                        )
                    )
                
                # 创建几个额外的测试学生
                test_students = [
                    {
                        'username': 'student_test1',
                        'email': 'test1@example.com',
                        'real_name': '李小红',
                        'nickname': '小红',
                        'phone': '13800138001',
                        'grade_level': '小学三年级',
                        'english_level': 'beginner'
                    },
                    {
                        'username': 'student_test2',
                        'email': 'test2@example.com',
                        'real_name': '王小华',
                        'nickname': '小华',
                        'phone': '13800138002',
                        'grade_level': '小学五年级',
                        'english_level': 'intermediate'
                    },
                    {
                        'username': 'student_test3',
                        'email': 'test3@example.com',
                        'real_name': '赵小刚',
                        'nickname': '小刚',
                        'phone': '13800138003',
                        'grade_level': '初中一年级',
                        'english_level': 'intermediate'
                    }
                ]
                
                for student_data in test_students:
                    student_data['role'] = UserRole.STUDENT
                    student_data['is_active'] = True
                    student_data['admin_approval_status'] = 'approved'
                    
                    student, created = User.objects.get_or_create(
                        username=student_data['username'],
                        defaults=student_data
                    )
                    
                    if created:
                        student.set_password('student123')
                        student.save()
                        Token.objects.get_or_create(user=student)
                        self.stdout.write(
                            f'创建测试学生: {student.real_name} ({student.username})'
                        )
                    else:
                        self.stdout.write(
                            f'测试学生已存在: {student.real_name} ({student.username})'
                        )
                
                self.stdout.write(
                    self.style.SUCCESS('\n默认学生创建完成！')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建默认学生时出错: {str(e)}')
            )
            import traceback
            traceback.print_exc()