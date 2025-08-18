from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.management.color import Style
from apps.accounts.models import RoleTemplate, UserRole


class Command(BaseCommand):
    help = '为7种角色创建对应的RoleTemplate实例'
    
    def handle(self, *args, **options):
        """创建角色模板"""
        
        # 定义7种角色的模板配置
        role_templates = [
            {
                'role': UserRole.ADMIN,
                'template_name': '系统管理员模板',
                'description': '系统管理员角色模板，包含系统管理、用户管理、权限管理等功能配置',
                'version': '1.0.0'
            },
            {
                'role': UserRole.DEAN,
                'template_name': '教导主任模板',
                'description': '教导主任角色模板，包含教学管理、教师管理、教学监督等功能配置',
                'version': '1.0.0'
            },
            {
                'role': UserRole.ACADEMIC_DIRECTOR,
                'template_name': '教务主任模板',
                'description': '教务主任角色模板，包含课程管理、教学计划、资源配置等功能配置',
                'version': '1.0.0'
            },
            {
                'role': UserRole.RESEARCH_LEADER,
                'template_name': '教研组长模板',
                'description': '教研组长角色模板，包含教研活动、方法研究、质量评估等功能配置',
                'version': '1.0.0'
            },
            {
                'role': UserRole.TEACHER,
                'template_name': '教师模板',
                'description': '教师角色模板，包含课程教学、学生管理、成绩录入等功能配置',
                'version': '1.0.0'
            },
            {
                'role': UserRole.PARENT,
                'template_name': '家长模板',
                'description': '家长角色模板，包含学生信息查看、学习进度监控、沟通交流等功能配置',
                'version': '1.0.0'
            },
            {
                'role': UserRole.STUDENT,
                'template_name': '学生模板',
                'description': '学生角色模板，包含课程学习、练习测试、个人中心等功能配置',
                'version': '1.0.0'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for template_data in role_templates:
                template, created = RoleTemplate.objects.get_or_create(
                    role=template_data['role'],
                    defaults={
                        'template_name': template_data['template_name'],
                        'description': template_data['description'],
                        'version': template_data['version'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ 创建角色模板: {template.template_name} ({template.role})'
                        )
                    )
                else:
                    # 更新现有模板
                    template.template_name = template_data['template_name']
                    template.description = template_data['description']
                    template.version = template_data['version']
                    template.is_active = True
                    template.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ 更新角色模板: {template.template_name} ({template.role})'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n角色模板创建完成！\n'
                f'新建: {created_count} 个\n'
                f'更新: {updated_count} 个\n'
                f'总计: {created_count + updated_count} 个角色模板'
            )
        )
        
        # 显示所有角色模板状态
        self.stdout.write('\n当前角色模板状态:')
        for template in RoleTemplate.objects.all().order_by('role'):
            user_count = template.get_user_count()
            field_count = template.get_field_count()
            status = '✓ 启用' if template.is_active else '✗ 禁用'
            self.stdout.write(
                f'  {template.template_name}: {status}, '
                f'用户数: {user_count}, 字段数: {field_count}'
            )