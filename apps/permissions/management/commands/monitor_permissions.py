from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from apps.permissions.models import RoleManagement, RoleMenuPermission, MenuModuleConfig
from apps.permissions.models_optimized import PermissionSyncLog, AutoSyncConfig
from apps.accounts.models import CustomUser, UserRole
from datetime import datetime, timedelta
import json
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '权限监控和自动修复命令'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-fix',
            action='store_true',
            help='自动修复发现的权限问题',
        )
        parser.add_argument(
            '--notify',
            action='store_true',
            help='发送通知邮件',
        )
        parser.add_argument(
            '--check-interval',
            type=int,
            default=60,
            help='检查间隔（分钟）',
        )

    def handle(self, *args, **options):
        auto_fix = options.get('auto_fix')
        notify = options.get('notify')
        check_interval = options.get('check_interval')
        
        self.stdout.write('开始权限监控检查...')
        
        # 获取自动同步配置
        try:
            config = AutoSyncConfig.objects.get()
        except Exception:
            self.stdout.write(self.style.WARNING('未找到自动同步配置，请先运行 setup_permission_audit --action=setup'))
            return
        
        if not config.enable_auto_sync:
            self.stdout.write('自动同步已禁用，跳过监控')
            return
        
        # 执行权限检查
        issues = self.check_permissions()
        
        # 统计问题
        total_issues = sum(len(category_issues) for category_issues in issues.values())
        
        if total_issues == 0:
            self.stdout.write(self.style.SUCCESS('✓ 权限检查通过，未发现问题'))
            self.log_monitoring_result('success', '权限检查通过', {})
            return
        
        self.stdout.write(f'发现 {total_issues} 个权限问题')
        
        # 自动修复
        if auto_fix:
            fixed_count = self.auto_fix_issues(issues)
            self.stdout.write(f'已自动修复 {fixed_count} 个问题')
        
        # 发送通知
        if notify and config.notify_on_sync_failure:
            self.send_notification(issues, auto_fix)
        
        # 记录监控结果
        self.log_monitoring_result('issues_found', f'发现 {total_issues} 个问题', issues)
        
        self.stdout.write('权限监控检查完成')

    def check_permissions(self):
        """检查权限问题"""
        issues = {
            'missing_admin_permissions': [],
            'orphaned_permissions': [],
            'user_role_mismatches': [],
            'inactive_menu_permissions': []
        }
        
        # 检查管理员缺失的权限
        self.check_admin_missing_permissions(issues)
        
        # 检查孤立权限
        self.check_orphaned_permissions(issues)
        
        # 检查用户角色不匹配
        self.check_user_role_mismatches(issues)
        
        # 检查非活跃菜单权限
        self.check_inactive_menu_permissions(issues)
        
        return issues

    def check_admin_missing_permissions(self, issues):
        """检查管理员缺失的权限"""
        admin_role = UserRole.ADMIN.value
        
        # 获取所有活跃的菜单模块
        active_menus = MenuModuleConfig.objects.filter(is_active=True)
        
        for menu in active_menus:
            # 检查管理员是否有此菜单的权限
            if not RoleMenuPermission.objects.filter(
                role=admin_role,
                menu_module=menu
            ).exists():
                issues['missing_admin_permissions'].append({
                    'menu_id': menu.id,
                    'menu_name': menu.name,
                    'menu_key': menu.key,
                    'message': f'管理员缺少菜单 {menu.name} 的访问权限'
                })

    def check_orphaned_permissions(self, issues):
        """检查孤立权限"""
        valid_roles = [choice[0] for choice in UserRole.choices]
        
        # 检查角色菜单权限中的无效角色
        orphaned_permissions = RoleMenuPermission.objects.exclude(
            role__in=valid_roles
        )
        
        for perm in orphaned_permissions:
            issues['orphaned_permissions'].append({
                'permission_id': perm.id,
                'role': perm.role,
                'menu_name': perm.menu_module.name,
                'message': f'权限记录关联了无效角色 {perm.role}'
            })

    def check_user_role_mismatches(self, issues):
        """检查用户角色不匹配"""
        users = CustomUser.objects.all()
        
        for user in users:
            # 检查用户组分配是否与角色一致
            user_groups = user.groups.all()
            expected_group_name = f'{user.role}_group'
            
            has_correct_group = any(group.name == expected_group_name for group in user_groups)
            
            if user_groups.exists() and not has_correct_group:
                issues['user_role_mismatches'].append({
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'groups': [group.name for group in user_groups],
                    'expected_group': expected_group_name,
                    'message': f'用户 {user.username} 的组分配与角色不匹配'
                })

    def check_inactive_menu_permissions(self, issues):
        """检查非活跃菜单权限"""
        # 查找关联到非活跃菜单的权限
        inactive_permissions = RoleMenuPermission.objects.filter(
            menu_module__is_active=False
        )
        
        for perm in inactive_permissions:
            issues['inactive_menu_permissions'].append({
                'permission_id': perm.id,
                'role': perm.role,
                'menu_name': perm.menu_module.name,
                'message': f'角色 {perm.role} 关联了非活跃菜单 {perm.menu_module.name}'
            })

    def auto_fix_issues(self, issues):
        """自动修复权限问题"""
        fixed_count = 0
        
        with transaction.atomic():
            # 修复管理员缺失的权限
            fixed_count += self.fix_admin_missing_permissions(issues['missing_admin_permissions'])
            
            # 清理孤立权限
            fixed_count += self.fix_orphaned_permissions(issues['orphaned_permissions'])
            
            # 清理非活跃菜单权限
            fixed_count += self.fix_inactive_menu_permissions(issues['inactive_menu_permissions'])
        
        return fixed_count

    def fix_admin_missing_permissions(self, missing_permissions):
        """修复管理员缺失的权限"""
        fixed_count = 0
        admin_role = UserRole.ADMIN.value
        
        for issue in missing_permissions:
            try:
                menu_module = MenuModuleConfig.objects.get(id=issue['menu_id'])
                
                # 创建管理员权限
                RoleMenuPermission.objects.get_or_create(
                    role=admin_role,
                    menu_module=menu_module,
                    defaults={
                        'can_access': True
                    }
                )
                
                fixed_count += 1
                self.stdout.write(f'  ✓ 已为管理员添加菜单 {menu_module.name} 的访问权限')
                
            except Exception:
                self.stdout.write(f'  ✗ 菜单模块 {issue["menu_id"]} 不存在，跳过修复')
        
        return fixed_count

    def fix_orphaned_permissions(self, orphaned_permissions):
        """清理孤立权限"""
        fixed_count = 0
        
        for issue in orphaned_permissions:
            try:
                permission = RoleMenuPermission.objects.get(id=issue['permission_id'])
                permission.delete()
                fixed_count += 1
                self.stdout.write(f'  ✓ 已删除孤立权限记录 (角色: {issue["role"]}, 菜单: {issue["menu_name"]})')
                
            except Exception:
                self.stdout.write(f'  ✗ 权限记录 {issue["permission_id"]} 不存在，跳过删除')
        
        return fixed_count

    def fix_inactive_menu_permissions(self, inactive_permissions):
        """清理非活跃菜单权限"""
        fixed_count = 0
        
        for issue in inactive_permissions:
            try:
                permission = RoleMenuPermission.objects.get(id=issue['permission_id'])
                permission.delete()
                fixed_count += 1
                self.stdout.write(f'  ✓ 已删除非活跃菜单权限 (角色: {issue["role"]}, 菜单: {issue["menu_name"]})')
                
            except Exception:
                self.stdout.write(f'  ✗ 权限记录 {issue["permission_id"]} 不存在，跳过删除')
        
        return fixed_count

    def send_notification(self, issues, auto_fix):
        """发送通知邮件"""
        try:
            config = AutoSyncConfig.objects.get()
            
            if not config.notification_emails:
                return
            
            total_issues = sum(len(category_issues) for category_issues in issues.values())
            
            subject = f'权限监控报告 - 发现 {total_issues} 个问题'
            
            message_parts = [
                f'权限监控检查完成，发现 {total_issues} 个问题：\n'
            ]
            
            for category, category_issues in issues.items():
                if category_issues:
                    category_name = {
                        'missing_admin_permissions': '管理员缺失权限',
                        'orphaned_permissions': '孤立权限',
                        'user_role_mismatches': '用户角色不匹配',
                        'inactive_menu_permissions': '非活跃菜单权限'
                    }.get(category, category)
                    
                    message_parts.append(f'\n{category_name} ({len(category_issues)} 个):')
                    for issue in category_issues[:5]:  # 只显示前5个
                        message_parts.append(f'  - {issue["message"]}')
                    
                    if len(category_issues) > 5:
                        message_parts.append(f'  ... 还有 {len(category_issues) - 5} 个问题')
            
            if auto_fix:
                message_parts.append('\n已启用自动修复功能。')
            else:
                message_parts.append('\n请手动检查和修复这些问题，或使用 --auto-fix 参数启用自动修复。')
            
            message = '\n'.join(message_parts)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=config.notification_emails,
                fail_silently=True
            )
            
            self.stdout.write('已发送通知邮件')
            
        except Exception as e:
            self.stdout.write(f'发送通知邮件失败: {e}')

    def log_monitoring_result(self, status, message, issues_data):
        """记录监控结果"""
        try:
            PermissionSyncLog.log_sync_operation(
                sync_type='auto_sync',
                target_type='system',
                target_id='permission_monitor',
                operation='monitor',
                result=message,
                is_success=(status == 'success'),
                extra_data=issues_data
            )
        except Exception as e:
            logger.error(f'记录监控结果失败: {e}')