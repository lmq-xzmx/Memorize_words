from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import UserRole
from apps.permissions.models_optimized import OptimizedRoleGroupMapping, PermissionSyncLog
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '初始化权限系统：创建角色组映射和基础权限配置'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建所有映射（会删除现有数据）',
        )
        parser.add_argument(
            '--role',
            type=str,
            help='只初始化指定角色的权限',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='初始化后立即同步到Django组',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化权限系统...'))
        
        force = options.get('force', False)
        target_role = options.get('role')
        auto_sync = options.get('sync', False)
        
        # 获取要处理的角色列表
        if target_role:
            if target_role not in dict(UserRole.choices):
                self.stdout.write(self.style.ERROR(f'无效的角色: {target_role}'))
                return
            roles_to_process = [target_role]
        else:
            roles_to_process = [choice[0] for choice in UserRole.choices]
        
        self.stdout.write(f'将处理以下角色: {", ".join(roles_to_process)}')
        
        # 如果强制模式，删除现有映射
        if force:
            self.stdout.write(self.style.WARNING('强制模式：删除现有角色组映射...'))
            if target_role:
                OptimizedRoleGroupMapping.objects.filter(role=target_role).delete()
            else:
                OptimizedRoleGroupMapping.objects.all().delete()
        
        # 初始化每个角色
        success_count = 0
        error_count = 0
        
        for role in roles_to_process:
            try:
                self.stdout.write(f'\n处理角色: {role}')
                
                # 创建角色组映射
                mapping, created = OptimizedRoleGroupMapping.create_for_role(role)
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ 创建新的角色组映射: {mapping}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  - 角色组映射已存在: {mapping}')
                    )
                
                # 显示配置的权限
                base_perms = mapping.get_base_permissions_dict()
                menu_perms = mapping.get_menu_permissions_list()
                
                self.stdout.write(f'  基础权限: {len(base_perms)} 项')
                for perm, enabled in base_perms.items():
                    status = '✓' if enabled else '✗'
                    self.stdout.write(f'    {status} {perm}')
                
                self.stdout.write(f'  菜单权限: {len(menu_perms)} 项')
                for menu in menu_perms:
                    self.stdout.write(f'    ✓ {menu}')
                
                # 如果启用自动同步
                if auto_sync:
                    self.stdout.write('  执行权限同步...')
                    sync_success, sync_message = mapping.sync_to_django_group()
                    if sync_success:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ 同步成功: {sync_message}')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'  ✗ 同步失败: {sync_message}')
                        )
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                self.stdout.write(
                    self.style.ERROR(f'  ✗ 处理角色 {role} 时出错: {error_msg}')
                )
                logger.error(f'初始化角色 {role} 权限失败: {error_msg}')
        
        # 显示统计信息
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'初始化完成:')
        self.stdout.write(f'  成功: {success_count} 个角色')
        self.stdout.write(f'  失败: {error_count} 个角色')
        
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('所有角色权限初始化成功！'))
        else:
            self.stdout.write(self.style.WARNING('部分角色权限初始化失败，请检查日志。'))
        
        # 显示下一步建议
        if not auto_sync and success_count > 0:
            self.stdout.write('\n建议执行以下命令同步权限到Django组:')
            self.stdout.write('  python manage.py sync_permissions')
    
    def create_basic_permissions(self):
        """创建基础权限（如果不存在）"""
        self.stdout.write('检查基础权限...')
        
        # 定义基础权限
        basic_permissions = [
            ('view_own_profile', '查看个人资料'),
            ('change_own_profile', '修改个人资料'),
            ('view_learning_progress', '查看学习进度'),
            ('add_learning_record', '添加学习记录'),
            ('view_child_progress', '查看子女进度'),
            ('view_learning_reports', '查看学习报告'),
            ('view_student_progress', '查看学生进度'),
            ('add_teaching_plan', '添加教学计划'),
            ('change_teaching_plan', '修改教学计划'),
            ('view_vocabulary', '查看词汇'),
            ('add_vocabulary', '添加词汇'),
            ('change_vocabulary', '修改词汇'),
            ('view_all', '查看所有'),
            ('add_all', '添加所有'),
            ('change_all', '修改所有'),
            ('delete_all', '删除所有'),
        ]
        
        # 获取或创建内容类型
        from apps.accounts.models import CustomUser
        content_type = ContentType.objects.get_for_model(CustomUser)
        
        created_count = 0
        for codename, name in basic_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ 创建权限: {name} ({codename})')
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'创建了 {created_count} 个基础权限'))
        else:
            self.stdout.write('所有基础权限已存在')