from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.accounts.models import UserRole, CustomUser
from apps.permissions.models_optimized import OptimizedRoleGroupMapping, PermissionSyncLog
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '同步权限到Django组和用户'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            help='只同步指定角色的权限',
        )
        parser.add_argument(
            '--users',
            action='store_true',
            help='同步用户到对应的角色组',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，不实际执行同步',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('开始同步权限...')
        
        target_role = options.get('role')
        sync_users = options.get('users', False)
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write('*** 预览模式 - 不会实际执行同步 ***')
        
        # 获取要同步的角色组映射
        if target_role:
            if target_role not in dict(UserRole.choices):
                self.stdout.write(f'无效的角色: {target_role}')
                return
            mappings = OptimizedRoleGroupMapping.objects.filter(role=target_role, auto_sync=True)
        else:
            mappings = OptimizedRoleGroupMapping.objects.filter(auto_sync=True)
        
        if not mappings.exists():
            self.stdout.write('没有找到需要同步的角色组映射')
            return
        
        self.stdout.write(f'找到 {mappings.count()} 个角色组映射需要同步')
        
        # 同步角色组权限
        success_count = 0
        error_count = 0
        
        for mapping in mappings:
            try:
                self.stdout.write(f'\n同步角色: {mapping.role} -> {mapping.group.name}')
                
                if not dry_run:
                    sync_success, sync_message = mapping.sync_to_django_group()
                    if sync_success:
                        self.stdout.write(f'  ✓ {sync_message}')
                        success_count += 1
                    else:
                        self.stdout.write(f'  ✗ {sync_message}')
                        error_count += 1
                else:
                    # 预览模式：显示将要同步的权限
                    all_perms = mapping.get_all_permissions()
                    enabled_perms = [perm for perm, enabled in all_perms.items() if enabled]
                    self.stdout.write(f'  将同步 {len(enabled_perms)} 个权限:')
                    for perm in enabled_perms:
                        self.stdout.write(f'    - {perm}')
                    success_count += 1
                
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                self.stdout.write(f'  ✗ 同步失败: {error_msg}')
                logger.error(f'同步角色 {mapping.role} 权限失败: {error_msg}')
        
        # 同步用户到角色组
        if sync_users and not dry_run:
            self.stdout.write('\n开始同步用户到角色组...')
            user_success_count = 0
            user_error_count = 0
            
            # 获取要同步的用户
            if target_role:
                users = CustomUser.objects.filter(role=target_role, is_active=True)
            else:
                users = CustomUser.objects.filter(is_active=True)
            
            self.stdout.write(f'找到 {users.count()} 个用户需要同步')
            
            for user in users:
                try:
                    from apps.permissions.models_optimized import sync_user_to_role_group
                    sync_success, sync_message = sync_user_to_role_group(user)
                    if sync_success:
                        self.stdout.write(f'  ✓ 用户 {user.username}: {sync_message}')
                        user_success_count += 1
                    else:
                        self.stdout.write(f'  ✗ 用户 {user.username}: {sync_message}')
                        user_error_count += 1
                        
                except Exception as e:
                    user_error_count += 1
                    error_msg = str(e)
                    self.stdout.write(f'  ✗ 用户 {user.username}: {error_msg}')
                    logger.error(f'同步用户 {user.username} 失败: {error_msg}')
            
            self.stdout.write(f'\n用户同步结果: 成功 {user_success_count}, 失败 {user_error_count}')
        
        elif sync_users and dry_run:
            self.stdout.write('\n预览用户同步...')
            if target_role:
                users = CustomUser.objects.filter(role=target_role, is_active=True)
            else:
                users = CustomUser.objects.filter(is_active=True)
            
            self.stdout.write(f'将同步 {users.count()} 个用户到对应角色组')
            for user in users:
                try:
                    mapping = OptimizedRoleGroupMapping.objects.get(role=user.role)
                    self.stdout.write(f'  用户 {user.username} -> 组 {mapping.group.name}')
                except OptimizedRoleGroupMapping.DoesNotExist:
                    self.stdout.write(f'  用户 {user.username} -> 无对应组映射')
        
        # 显示统计信息
        self.stdout.write('\n' + '='*50)
        if not dry_run:
            self.stdout.write(f'权限同步完成:')
            self.stdout.write(f'  成功: {success_count} 个角色组')
            self.stdout.write(f'  失败: {error_count} 个角色组')
            
            if error_count == 0:
                self.stdout.write('所有权限同步成功！')
            else:
                self.stdout.write('部分权限同步失败，请检查日志。')
        else:
            self.stdout.write(f'预览完成: 将同步 {success_count} 个角色组')
            self.stdout.write('使用 --dry-run=false 执行实际同步')
        
        # 显示最近的同步日志
        if not dry_run:
            self.stdout.write('\n最近的同步日志:')
            recent_logs = PermissionSyncLog.objects.filter(
                sync_type='role_group_sync'
            ).order_by('-created_at')[:5]
            
            for log in recent_logs:
                status = '✓' if log.is_success else '✗'
                self.stdout.write(f'  {status} {log.result}')