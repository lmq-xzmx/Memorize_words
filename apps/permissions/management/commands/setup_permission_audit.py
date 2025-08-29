from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Permission, Group
from apps.permissions.models import RoleManagement, MenuModuleConfig
from apps.permissions.models_optimized import PermissionSyncLog, AutoSyncConfig
from apps.accounts.models import CustomUser, UserRole
from datetime import datetime, timedelta
import json


class Command(BaseCommand):
    help = '设置和管理权限审计监控机制'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['setup', 'audit', 'report', 'cleanup'],
            default='setup',
            help='执行的操作类型',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='审计报告的天数范围',
        )
        parser.add_argument(
            '--role',
            type=str,
            help='指定角色进行审计',
        )

    def handle(self, *args, **options):
        action = options.get('action')
        days = options.get('days')
        role = options.get('role')
        
        if action == 'setup':
            self.setup_audit_system()
        elif action == 'audit':
            self.perform_permission_audit(role)
        elif action == 'report':
            self.generate_audit_report(days)
        elif action == 'cleanup':
            self.cleanup_old_logs(days)
        
        self.stdout.write(self.style.SUCCESS('权限审计操作完成！'))

    def setup_audit_system(self):
        """设置权限审计系统"""
        self.stdout.write('设置权限审计系统...')
        
        with transaction.atomic():
            # 创建或更新自动同步配置
            config, created = AutoSyncConfig.objects.get_or_create(
                defaults={
                    'enable_auto_sync': True,
                    'sync_on_user_create': True,
                    'sync_on_user_update': True,
                    'sync_on_role_change': True,
                    'sync_on_permission_change': True,
                    'auto_sync_interval_minutes': 60,
                    'batch_sync_size': 100,
                    'max_retry_attempts': 3,
                    'retry_delay_seconds': 30,
                    'notify_on_sync_failure': True,
                    'notification_emails': ['admin@example.com']
                }
            )
            
            if created:
                self.stdout.write('  创建自动同步配置')
            else:
                self.stdout.write('  更新自动同步配置')
            
            # 记录审计系统设置日志
            PermissionSyncLog.log_sync_operation(
                sync_type='manual_sync',
                target_type='system',
                target_id='audit_system',
                operation='create',
                result='权限审计系统设置完成',
                is_success=True
            )
            
            self.stdout.write('权限审计系统设置完成')

    def perform_permission_audit(self, specific_role=None):
        """执行权限审计"""
        self.stdout.write('执行权限审计检查...')
        
        audit_results = {
            'role_consistency': [],
            'permission_conflicts': [],
            'orphaned_permissions': [],
            'missing_permissions': [],
            'menu_access_issues': []
        }
        
        # 检查角色一致性
        self.check_role_consistency(audit_results, specific_role)
        
        # 检查权限冲突
        self.check_permission_conflicts(audit_results, specific_role)
        
        # 检查孤立权限
        self.check_orphaned_permissions(audit_results)
        
        # 检查缺失权限
        self.check_missing_permissions(audit_results, specific_role)
        
        # 检查菜单访问问题
        self.check_menu_access_issues(audit_results, specific_role)
        
        # 生成审计报告
        self.display_audit_results(audit_results)
        
        # 记录审计日志
        PermissionSyncLog.log_sync_operation(
            sync_type='manual_sync',
            target_type='system',
            target_id=specific_role or 'all_roles',
            operation='sync',
            result=f'权限审计完成，发现 {self.count_issues(audit_results)} 个问题',
            is_success=True,
            extra_data=audit_results
        )

    def check_role_consistency(self, audit_results, specific_role):
        """检查角色一致性"""
        self.stdout.write('  检查角色一致性...')
        
        # 获取所有角色管理记录
        role_managements = RoleManagement.objects.all()
        if specific_role:
            role_managements = role_managements.filter(role=specific_role)
        
        for role_mgmt in role_managements:
            # 检查角色是否在UserRole枚举中定义
            valid_roles = [choice[0] for choice in UserRole.choices]
            if role_mgmt.role not in valid_roles:
                audit_results['role_consistency'].append({
                    'type': 'invalid_role',
                    'role': role_mgmt.role,
                    'message': f'角色 {role_mgmt.role} 不在有效角色列表中'
                })
            
            # 检查角色层级关系
            if role_mgmt.parent:
                if role_mgmt.parent.role == role_mgmt.role:
                    audit_results['role_consistency'].append({
                        'type': 'circular_reference',
                        'role': role_mgmt.role,
                        'message': f'角色 {role_mgmt.role} 存在循环引用'
                    })

    def check_permission_conflicts(self, audit_results, specific_role):
        """检查权限冲突"""
        self.stdout.write('  检查权限冲突...')
        
        # 检查用户是否有冲突的角色分配
        users = CustomUser.objects.all()
        if specific_role:
            users = users.filter(role=specific_role)
        
        for user in users:
            # 检查用户组分配是否与角色一致
            user_groups = user.groups.all()
            expected_group_name = f'{user.role}_group'
            
            has_correct_group = any(group.name == expected_group_name for group in user_groups)
            if not has_correct_group and user_groups.exists():
                audit_results['permission_conflicts'].append({
                    'type': 'group_mismatch',
                    'user': user.username,
                    'role': user.role,
                    'groups': [group.name for group in user_groups],
                    'message': f'用户 {user.username} 的组分配与角色不匹配'
                })

    def check_orphaned_permissions(self, audit_results):
        """检查孤立权限"""
        self.stdout.write('  检查孤立权限...')
        
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        # 请使用 MenuValidity 和 RoleMenuAssignment 替代
        pass

    def check_missing_permissions(self, audit_results, specific_role):
        """检查缺失权限"""
        self.stdout.write('  检查缺失权限...')
        
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        # 请使用 MenuValidity 和 RoleMenuAssignment 替代
        pass

    def check_menu_access_issues(self, audit_results, specific_role):
        """检查菜单访问问题"""
        self.stdout.write('  检查菜单访问问题...')
        
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        # 请使用 MenuValidity 和 RoleMenuAssignment 替代
        pass

    def should_have_menu_access(self, role, menu_key):
        """判断角色是否应该有特定菜单的访问权限"""
        # 所有角色都应该有的基本菜单
        basic_menus = ['dashboard', 'profile_management', 'profile_edit', 'password_change']
        if menu_key in basic_menus:
            return True
        
        # 管理员应该有所有菜单权限
        if role == UserRole.ADMIN.value:
            return True
        
        return False

    def display_audit_results(self, audit_results):
        """显示审计结果"""
        self.stdout.write('\n=== 权限审计结果 ===')
        
        total_issues = self.count_issues(audit_results)
        if total_issues == 0:
            self.stdout.write(self.style.SUCCESS('✓ 未发现权限问题'))
            return
        
        self.stdout.write(f'发现 {total_issues} 个权限问题：\n')
        
        for category, issues in audit_results.items():
            if issues:
                category_name = {
                    'role_consistency': '角色一致性问题',
                    'permission_conflicts': '权限冲突问题',
                    'orphaned_permissions': '孤立权限问题',
                    'missing_permissions': '缺失权限问题',
                    'menu_access_issues': '菜单访问问题'
                }.get(category, category)
                
                self.stdout.write(f'{category_name} ({len(issues)} 个):')
                for issue in issues:
                    self.stdout.write(f'  - {issue["message"]}')
                self.stdout.write('')

    def count_issues(self, audit_results):
        """统计问题总数"""
        return sum(len(issues) for issues in audit_results.values())

    def generate_audit_report(self, days):
        """生成审计报告"""
        self.stdout.write(f'生成最近 {days} 天的审计报告...')
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 获取同步日志
        logs = PermissionSyncLog.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('-created_at')
        
        # 统计信息
        total_logs = logs.count()
        success_logs = logs.filter(is_success=True).count()
        failed_logs = logs.filter(is_success=False).count()
        
        self.stdout.write(f'\n=== 审计报告 ({start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}) ===')
        self.stdout.write(f'总操作数: {total_logs}')
        self.stdout.write(f'成功操作: {success_logs}')
        self.stdout.write(f'失败操作: {failed_logs}')
        
        if failed_logs > 0:
            self.stdout.write(f'\n失败操作详情:')
            failed_log_list = logs.filter(is_success=False)[:10]
            for log in failed_log_list:
                self.stdout.write(f'  - {log.created_at.strftime("%Y-%m-%d %H:%M")} | {log.get_sync_type_display_name()} | {log.result}')
        
        # 按同步类型统计
        sync_type_stats = {}
        for log in logs:
            sync_type = log.get_sync_type_display_name()
            if sync_type not in sync_type_stats:
                sync_type_stats[sync_type] = {'total': 0, 'success': 0, 'failed': 0}
            sync_type_stats[sync_type]['total'] += 1
            if log.is_success:
                sync_type_stats[sync_type]['success'] += 1
            else:
                sync_type_stats[sync_type]['failed'] += 1
        
        if sync_type_stats:
            self.stdout.write(f'\n按类型统计:')
            for sync_type, stats in sync_type_stats.items():
                self.stdout.write(f'  {sync_type}: {stats["total"]} 次 (成功: {stats["success"]}, 失败: {stats["failed"]})')

    def cleanup_old_logs(self, days):
        """清理旧日志"""
        self.stdout.write(f'清理 {days} 天前的审计日志...')
        
        cutoff_date = datetime.now() - timedelta(days=days)
        old_logs = PermissionSyncLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()
        
        if count > 0:
            old_logs.delete()
            self.stdout.write(f'已清理 {count} 条旧日志')
        else:
            self.stdout.write('没有需要清理的旧日志')