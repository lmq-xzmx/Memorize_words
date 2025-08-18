from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import RoleTemplate, RoleExtension, UserRole
import json


class Command(BaseCommand):
    help = '为各角色创建特定的注册增项字段配置'
    
    def handle(self, *args, **options):
        """创建角色增项字段配置"""
        
        # 基础增项（所有角色共有）
        base_extensions = [
            {
                'field_name': 'real_name',
                'field_label': '真实姓名',
                'field_type': 'text',
                'is_required': True,
                'help_text': '请输入您的真实姓名',
                'sort_order': 1
            },
            {
                'field_name': 'phone',
                'field_label': '联系电话',
                'field_type': 'phone',
                'is_required': True,
                'help_text': '请输入有效的手机号码',
                'sort_order': 2
            },
            {
                'field_name': 'notes',
                'field_label': '备注信息',
                'field_type': 'textarea',
                'is_required': False,
                'help_text': '其他需要说明的信息（选填）',
                'sort_order': 99
            }
        ]
        
        # 角色特定增项配置
        role_specific_extensions = {
            UserRole.STUDENT: [
                {
                    'field_name': 'grade_level',
                    'field_label': '年级信息',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['primary_1', '小学一年级'],
                        ['primary_2', '小学二年级'],
                        ['primary_3', '小学三年级'],
                        ['primary_4', '小学四年级'],
                        ['primary_5', '小学五年级'],
                        ['primary_6', '小学六年级'],
                        ['junior_1', '初中一年级'],
                        ['junior_2', '初中二年级'],
                        ['junior_3', '初中三年级'],
                        ['senior_1', '高中一年级'],
                        ['senior_2', '高中二年级'],
                        ['senior_3', '高中三年级'],
                        ['other', '其他']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您当前的年级',
                    'sort_order': 10
                },
                {
                    'field_name': 'english_level',
                    'field_label': '英语水平',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['beginner', '初级'],
                        ['elementary', '基础'],
                        ['intermediate', '中级'],
                        ['advanced', '高级']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您的英语水平',
                    'sort_order': 11
                },
                {
                    'field_name': 'learning_goal',
                    'field_label': '学习目标',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['exam_prep', '考试准备'],
                        ['daily_communication', '日常交流'],
                        ['academic_english', '学术英语'],
                        ['business_english', '商务英语'],
                        ['interest_hobby', '兴趣爱好'],
                        ['other', '其他']
                    ]),
                    'is_required': False,
                    'help_text': '请选择您的主要学习目标',
                    'sort_order': 12
                }
            ],
            UserRole.PARENT: [
                {
                    'field_name': 'related_student',
                    'field_label': '关联学生',
                    'field_type': 'text',
                    'is_required': True,
                    'help_text': '请输入您孩子的姓名或学号',
                    'sort_order': 10
                },
                {
                    'field_name': 'home_address',
                    'field_label': '家庭地址',
                    'field_type': 'textarea',
                    'is_required': False,
                    'help_text': '请输入详细的家庭地址（选填）',
                    'sort_order': 11
                }
            ],
            UserRole.TEACHER: [
                {
                    'field_name': 'teaching_subject',
                    'field_label': '教学科目',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['english', '英语'],
                        ['chinese', '语文'],
                        ['math', '数学'],
                        ['science', '科学'],
                        ['other', '其他']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您的主要教学科目',
                    'sort_order': 10
                },
                {
                    'field_name': 'teaching_experience',
                    'field_label': '教学经验',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['0-1', '1年以下'],
                        ['1-3', '1-3年'],
                        ['3-5', '3-5年'],
                        ['5-10', '5-10年'],
                        ['10+', '10年以上']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您的教学经验年限',
                    'sort_order': 11
                },
                {
                    'field_name': 'qualification_certificate',
                    'field_label': '资格证书',
                    'field_type': 'text',
                    'is_required': False,
                    'help_text': '请输入您的教师资格证书编号（选填）',
                    'sort_order': 12
                },
                {
                    'field_name': 'specialty_field',
                    'field_label': '专业领域',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['primary_education', '小学教育'],
                        ['junior_education', '初中教育'],
                        ['senior_education', '高中教育'],
                        ['language_training', '语言培训'],
                        ['exam_coaching', '考试辅导'],
                        ['other', '其他']
                    ]),
                    'is_required': False,
                    'help_text': '请选择您的专业领域',
                    'sort_order': 13
                }
            ],
            # 管理角色（管理员、教导主任、教务主任、教研组长）
            UserRole.ADMIN: [
                {
                    'field_name': 'management_scope',
                    'field_label': '管理范围',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['system_admin', '系统管理'],
                        ['user_management', '用户管理'],
                        ['content_management', '内容管理'],
                        ['full_management', '全面管理']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您的主要管理范围',
                    'sort_order': 10
                },
                {
                    'field_name': 'work_experience',
                    'field_label': '工作经验',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['0-2', '2年以下'],
                        ['2-5', '2-5年'],
                        ['5-10', '5-10年'],
                        ['10+', '10年以上']
                    ]),
                    'is_required': False,
                    'help_text': '请选择您的相关工作经验',
                    'sort_order': 11
                }
            ],
            UserRole.DEAN: [
                {
                    'field_name': 'management_scope',
                    'field_label': '管理范围',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['teaching_management', '教学管理'],
                        ['teacher_management', '教师管理'],
                        ['curriculum_supervision', '课程监督'],
                        ['quality_control', '质量控制']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您的主要管理范围',
                    'sort_order': 10
                },
                {
                    'field_name': 'work_experience',
                    'field_label': '工作经验',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['0-2', '2年以下'],
                        ['2-5', '2-5年'],
                        ['5-10', '5-10年'],
                        ['10+', '10年以上']
                    ]),
                    'is_required': False,
                    'help_text': '请选择您的相关工作经验',
                    'sort_order': 11
                }
            ],
            UserRole.ACADEMIC_DIRECTOR: [
                {
                    'field_name': 'management_scope',
                    'field_label': '管理范围',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['course_management', '课程管理'],
                        ['teaching_plan', '教学计划'],
                        ['resource_allocation', '资源配置'],
                        ['academic_affairs', '教务事务']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您的主要管理范围',
                    'sort_order': 10
                },
                {
                    'field_name': 'work_experience',
                    'field_label': '工作经验',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['0-2', '2年以下'],
                        ['2-5', '2-5年'],
                        ['5-10', '5-10年'],
                        ['10+', '10年以上']
                    ]),
                    'is_required': False,
                    'help_text': '请选择您的相关工作经验',
                    'sort_order': 11
                }
            ],
            UserRole.RESEARCH_LEADER: [
                {
                    'field_name': 'management_scope',
                    'field_label': '管理范围',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['research_activities', '教研活动'],
                        ['method_research', '方法研究'],
                        ['quality_assessment', '质量评估'],
                        ['teacher_training', '教师培训']
                    ]),
                    'is_required': True,
                    'help_text': '请选择您的主要管理范围',
                    'sort_order': 10
                },
                {
                    'field_name': 'work_experience',
                    'field_label': '工作经验',
                    'field_type': 'choice',
                    'field_choices': json.dumps([
                        ['0-2', '2年以下'],
                        ['2-5', '2-5年'],
                        ['5-10', '5-10年'],
                        ['10+', '10年以上']
                    ]),
                    'is_required': False,
                    'help_text': '请选择您的相关工作经验',
                    'sort_order': 11
                }
            ]
        }
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            # 为每个角色创建增项字段
            for role in UserRole.choices:
                role_value = role[0]
                role_name = role[1]
                
                try:
                    role_template = RoleTemplate.objects.get(role=role_value)
                except RoleTemplate.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'角色模板不存在: {role_name} ({role_value})')
                    )
                    continue
                
                # 创建基础增项字段
                for ext_data in base_extensions:
                    extension, created = RoleExtension.objects.get_or_create(
                        role_template=role_template,
                        role=role_value,
                        field_name=ext_data['field_name'],
                        defaults={
                            'field_label': ext_data['field_label'],
                            'field_type': ext_data['field_type'],
                            'is_required': ext_data['is_required'],
                            'help_text': ext_data['help_text'],
                            'sort_order': ext_data['sort_order'],
                            'show_in_frontend_register': True,
                            'show_in_backend_admin': True,
                            'show_in_profile': True,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            f'  ✓ 创建基础字段: {role_name} - {ext_data["field_label"]}'
                        )
                    else:
                        updated_count += 1
                
                # 创建角色特定增项字段
                if role_value in role_specific_extensions:
                    for ext_data in role_specific_extensions[role_value]:
                        extension, created = RoleExtension.objects.get_or_create(
                            role_template=role_template,
                            role=role_value,
                            field_name=ext_data['field_name'],
                            defaults={
                                'field_label': ext_data['field_label'],
                                'field_type': ext_data['field_type'],
                                'field_choices': ext_data.get('field_choices', ''),
                                'is_required': ext_data['is_required'],
                                'help_text': ext_data['help_text'],
                                'sort_order': ext_data['sort_order'],
                                'show_in_frontend_register': True,
                                'show_in_backend_admin': True,
                                'show_in_profile': True,
                                'is_active': True
                            }
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(
                                f'  ✓ 创建特定字段: {role_name} - {ext_data["field_label"]}'
                            )
                        else:
                            updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n角色增项字段配置完成！\n'
                f'新建: {created_count} 个\n'
                f'更新: {updated_count} 个\n'
                f'总计: {created_count + updated_count} 个字段配置'
            )
        )
        
        # 显示各角色的字段统计
        self.stdout.write('\n各角色字段统计:')
        for template in RoleTemplate.objects.all().order_by('role'):
            field_count = template.get_field_count()
            role_name = dict(UserRole.choices)[template.role]
            self.stdout.write(
                f'  {role_name}: {field_count} 个字段'
            )