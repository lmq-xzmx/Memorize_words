from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import logging

from accounts.models_optimized import OptimizedRoleTemplate, RegistrationConfig, RegistrationLog
from accounts.models import UserRole
from permissions.models_optimized import OptimizedRoleGroupMapping

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = '设置和管理用户注册流程配置'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--init-templates',
            action='store_true',
            help='初始化默认角色模板'
        )
        
        parser.add_argument(
            '--init-config',
            action='store_true',
            help='初始化注册配置'
        )
        
        parser.add_argument(
            '--role',
            type=str,
            help='指定角色创建模板'
        )
        
        parser.add_argument(
            '--enable-auto-assign',
            action='store_true',
            help='启用自动角色分配'
        )
        
        parser.add_argument(
            '--list-templates',
            action='store_true',
            help='列出所有角色模板'
        )
        
        parser.add_argument(
            '--test-registration',
            type=str,
            help='测试注册流程（提供用户名）'
        )
    
    def handle(self, *args, **options):
        try:
            if options['init_templates']:
                self.init_role_templates()
            
            if options['init_config']:
                self.init_registration_config()
            
            if options['role']:
                self.create_role_template(options['role'])
            
            if options['enable_auto_assign']:
                self.enable_auto_assignment()
            
            if options['list_templates']:
                self.list_templates()
            
            if options['test_registration']:
                self.test_registration_flow(options['test_registration'])
                
        except Exception as e:
            logger.error(f"命令执行失败: {str(e)}")
            raise CommandError(f"命令执行失败: {str(e)}")
    
    def init_role_templates(self):
        """初始化默认角色模板"""
        self.stdout.write("初始化默认角色模板...")
        
        templates_config = {
            UserRole.STUDENT: {
                'template_name': '学生注册模板',
                'description': '学生用户注册时的默认配置',
                'registration_type': 'self_register',
                'permission_strategy': 'template_based',
                'form_config': {
                    'required_fields': ['username', 'email', 'password'],
                    'optional_fields': ['first_name', 'last_name'],
                    'custom_fields': ['student_id', 'grade', 'major']
                },
                'auto_config': {
                    'auto_activate': True,
                    'auto_assign_role': True,
                    'auto_send_email': True,
                    'auto_create_profile': True
                }
            },
            UserRole.TEACHER: {
                'template_name': '教师注册模板',
                'description': '教师用户注册时的默认配置',
                'registration_type': 'admin_approve',
                'permission_strategy': 'role_based',
                'form_config': {
                    'required_fields': ['username', 'email', 'password', 'first_name', 'last_name'],
                    'optional_fields': ['phone'],
                    'custom_fields': ['employee_id', 'department', 'title']
                },
                'auto_config': {
                    'auto_activate': False,
                    'auto_assign_role': True,
                    'auto_send_email': True,
                    'auto_create_profile': True
                }
            },
            UserRole.ADMIN: {
                'template_name': '管理员注册模板',
                'description': '管理员用户注册时的默认配置',
                'registration_type': 'admin_only',
                'permission_strategy': 'full_access',
                'form_config': {
                    'required_fields': ['username', 'email', 'password', 'first_name', 'last_name'],
                    'optional_fields': ['phone'],
                    'custom_fields': ['admin_level', 'department']
                },
                'auto_config': {
                    'auto_activate': True,
                    'auto_assign_role': True,
                    'auto_send_email': True,
                    'auto_create_profile': True
                }
            }
        }
        
        created_count = 0
        for role, config in templates_config.items():
            template, created = OptimizedRoleTemplate.objects.get_or_create(
                role=role,
                defaults={
                    'template_name': config['template_name'],
                    'description': config['description'],
                    'registration_type': config['registration_type'],
                    'permission_strategy': config['permission_strategy'],
                    'form_config': config['form_config'],
                    'auto_config': config['auto_config'],
                    'is_active': True,
                    'version': '1.0'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"创建角色模板: {template.template_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"角色模板已存在: {template.template_name}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"初始化完成，创建了 {created_count} 个角色模板")
        )
    
    def init_registration_config(self):
        """初始化注册配置"""
        self.stdout.write("初始化注册配置...")
        
        config, created = RegistrationConfig.objects.get_or_create(
            defaults={
                'enable_registration': True,
                'default_role': UserRole.STUDENT,
                'require_email_verification': True,
                'require_admin_approval': False,
                'auto_assign_permissions': True,
                'registration_limit_per_day': 100,
                'allowed_email_domains': ['@student.edu', '@teacher.edu'],
                'blocked_email_domains': ['@temp.com'],
                'custom_validation_rules': {
                    'password_min_length': 8,
                    'require_special_chars': True,
                    'require_numbers': True
                },
                'notification_settings': {
                    'notify_admin_on_registration': True,
                    'send_welcome_email': True,
                    'admin_notification_emails': ['admin@example.com']
                }
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS("创建默认注册配置")
            )
        else:
            self.stdout.write(
                self.style.WARNING("注册配置已存在")
            )
    
    def create_role_template(self, role):
        """为指定角色创建模板"""
        self.stdout.write(f"为角色 {role} 创建模板...")
        
        if role not in [choice[0] for choice in UserRole.choices]:
            raise CommandError(f"无效的角色: {role}")
        
        template_name = f"{role}注册模板"
        template, created = OptimizedRoleTemplate.objects.get_or_create(
            role=role,
            defaults={
                'template_name': template_name,
                'description': f'{role}用户注册时的配置模板',
                'registration_type': 'self_register',
                'permission_strategy': 'role_based',
                'form_config': {
                    'required_fields': ['username', 'email', 'password'],
                    'optional_fields': ['first_name', 'last_name'],
                    'custom_fields': []
                },
                'auto_config': {
                    'auto_activate': True,
                    'auto_assign_role': True,
                    'auto_send_email': True,
                    'auto_create_profile': True
                },
                'is_active': True,
                'version': '1.0'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"创建角色模板: {template_name}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"角色模板已存在: {template_name}")
            )
    
    def enable_auto_assignment(self):
        """启用自动角色分配"""
        self.stdout.write("启用自动角色分配...")
        
        config = RegistrationConfig.objects.first()
        if config:
            config.auto_assign_permissions = True
            config.save()
            self.stdout.write(
                self.style.SUCCESS("已启用自动角色分配")
            )
        else:
            self.stdout.write(
                self.style.ERROR("未找到注册配置，请先运行 --init-config")
            )
    
    def list_templates(self):
        """列出所有角色模板"""
        self.stdout.write("当前角色模板:")
        
        templates = OptimizedRoleTemplate.objects.all()
        if not templates.exists():
            self.stdout.write(
                self.style.WARNING("未找到任何角色模板")
            )
            return
        
        for template in templates:
            status = "启用" if template.is_active else "禁用"
            self.stdout.write(
                f"- {template.template_name} ({template.role}) - {status} - v{template.version}"
            )
            self.stdout.write(f"  描述: {template.description}")
            self.stdout.write(f"  注册类型: {template.registration_type}")
            self.stdout.write(f"  权限策略: {template.permission_strategy}")
            self.stdout.write("")
    
    def test_registration_flow(self, username):
        """测试注册流程"""
        self.stdout.write(f"测试用户 {username} 的注册流程...")
        
        # 检查用户是否已存在
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"用户 {username} 已存在")
            )
            return
        
        # 获取注册配置
        config = RegistrationConfig.objects.first()
        if not config:
            raise CommandError("未找到注册配置，请先运行 --init-config")
        
        # 获取默认角色模板
        template = OptimizedRoleTemplate.objects.filter(
            role=config.default_role,
            is_active=True
        ).first()
        
        if not template:
            raise CommandError(f"未找到角色 {config.default_role} 的活跃模板")
        
        self.stdout.write(f"使用模板: {template.template_name}")
        self.stdout.write(f"默认角色: {config.default_role}")
        self.stdout.write(f"自动分配权限: {'是' if config.auto_assign_permissions else '否'}")
        self.stdout.write(f"需要邮箱验证: {'是' if config.require_email_verification else '否'}")
        self.stdout.write(f"需要管理员审批: {'是' if config.require_admin_approval else '否'}")
        
        # 模拟创建用户（不实际创建）
        self.stdout.write("\n模拟注册流程:")
        self.stdout.write("1. 验证用户输入")
        self.stdout.write("2. 创建用户账户")
        self.stdout.write("3. 分配默认角色")
        
        if config.auto_assign_permissions:
            self.stdout.write("4. 自动分配权限")
            
            # 检查角色组映射
            mapping = OptimizedRoleGroupMapping.objects.filter(
                role=config.default_role
            ).first()
            
            if mapping:
                self.stdout.write(f"   - 添加到组: {mapping.group.name}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"   - 警告: 未找到角色 {config.default_role} 的组映射")
                )
        
        if template.auto_config.get('auto_create_profile', False):
            self.stdout.write("5. 创建用户档案")
        
        if template.auto_config.get('auto_send_email', False):
            self.stdout.write("6. 发送欢迎邮件")
        
        self.stdout.write(
            self.style.SUCCESS("注册流程测试完成")
        )


def auto_register_user(username, email, password, role=None, **extra_fields):
    """自动化用户注册函数"""
    try:
        with transaction.atomic():
            # 获取注册配置
            config = RegistrationConfig.objects.first()
            if not config or not config.enable_registration:
                return False, "注册功能已禁用"
            
            # 确定用户角色
            user_role = role or config.default_role
            
            # 获取角色模板
            template = OptimizedRoleTemplate.objects.filter(
                role=user_role,
                is_active=True
            ).first()
            
            if not template:
                return False, f"未找到角色 {user_role} 的活跃模板"
            
            # 创建用户
            user_data = {
                'username': username,
                'email': email,
                'role': user_role,
                'is_active': template.auto_config.get('auto_activate', True),
                **extra_fields
            }
            
            user = User.objects.create_user(password=password, **user_data)
            
            # 记录注册日志
            RegistrationLog.objects.create(
                user=user,
                template=template,
                registration_data={
                    'username': username,
                    'email': email,
                    'role': user_role,
                    'template_used': template.template_name,
                    'auto_config': template.auto_config
                },
                status='success',
                created_at=timezone.now()
            )
            
            logger.info(f"用户注册成功: {username} - 角色: {user_role}")
            return True, f"用户 {username} 注册成功"
            
    except Exception as e:
        logger.error(f"用户注册失败: {username} - {str(e)}")
        
        # 记录失败日志
        try:
            RegistrationLog.objects.create(
                registration_data={
                    'username': username,
                    'email': email,
                    'role': user_role,
                    'error': str(e)
                },
                status='failed',
                error_message=str(e),
                created_at=timezone.now()
            )
        except:
            pass
        
        return False, f"注册失败: {str(e)}"