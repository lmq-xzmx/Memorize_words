from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from typing import Optional, List, Dict, Any
import sys

from ...models import RoleGroupMapping, GroupRoleIdentifier
from ...services.group_consistency_checker import GroupConsistencyChecker
from ...services.sync_monitor import SyncMonitor
from ...models_optimized import PermissionSyncLog


class Command(BaseCommand):
    help = '管理Django组的角色标识符和同步状态'
    
    def add_arguments(self, parser):
        """添加命令行参数"""
        subparsers = parser.add_subparsers(
            dest='action',
            help='可用的操作'
        )
        
        # 创建标识符
        create_parser = subparsers.add_parser(
            'create-identifier',
            help='为组创建角色标识符'
        )
        create_parser.add_argument(
            '--group-id',
            type=int,
            help='组ID'
        )
        create_parser.add_argument(
            '--group-name',
            type=str,
            help='组名称'
        )
        create_parser.add_argument(
            '--role-identifier',
            type=str,
            required=True,
            help='角色标识符'
        )
        create_parser.add_argument(
            '--status',
            type=str,
            choices=['role_linked', 'orphaned', 'inactive', 'error'],
            default='role_linked',
            help='组状态'
        )
        
        # 批量同步
        sync_parser = subparsers.add_parser(
            'batch-sync',
            help='批量同步组和角色映射'
        )
        sync_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要执行的操作，不实际执行'
        )
        sync_parser.add_argument(
            '--force',
            action='store_true',
            help='强制同步，即使组状态正常'
        )
        
        # 一致性检查
        check_parser = subparsers.add_parser(
            'check-consistency',
            help='检查组和角色映射的一致性'
        )
        check_parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复发现的问题'
        )
        check_parser.add_argument(
            '--group-id',
            type=int,
            help='检查特定组的一致性'
        )
        
        # 清理孤立组
        cleanup_parser = subparsers.add_parser(
            'cleanup-orphaned',
            help='清理孤立的组标识符'
        )
        cleanup_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要删除的标识符，不实际删除'
        )
        
        # 统计信息
        stats_parser = subparsers.add_parser(
            'stats',
            help='显示组和角色映射的统计信息'
        )
        stats_parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='统计天数（默认7天）'
        )
        
        # 监控健康状态
        monitor_parser = subparsers.add_parser(
            'monitor',
            help='检查同步系统健康状态'
        )
        monitor_parser.add_argument(
            '--send-alerts',
            action='store_true',
            help='发送告警邮件'
        )
        
        # 清理日志
        cleanup_logs_parser = subparsers.add_parser(
            'cleanup-logs',
            help='清理旧的同步日志'
        )
        cleanup_logs_parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='保留天数（默认30天）'
        )
    
    def handle(self, *args, **options):
        """处理命令"""
        action = options.get('action')
        
        if not action:
            self.print_help('manage.py', 'manage_group_identifiers')
            return
        
        try:
            if action == 'create-identifier':
                self.create_identifier(options)
            elif action == 'batch-sync':
                self.batch_sync(options)
            elif action == 'check-consistency':
                self.check_consistency(options)
            elif action == 'cleanup-orphaned':
                self.cleanup_orphaned(options)
            elif action == 'stats':
                self.show_stats(options)
            elif action == 'monitor':
                self.monitor_health(options)
            elif action == 'cleanup-logs':
                self.cleanup_logs(options)
            else:
                raise CommandError(f'未知的操作: {action}')
                
        except Exception as e:
            raise CommandError(f'执行操作时发生错误: {str(e)}')
    
    def create_identifier(self, options: Dict[str, Any]):
        """创建组角色标识符"""
        group_id = options.get('group_id')
        group_name = options.get('group_name')
        role_identifier = options['role_identifier']
        status = options['status']
        
        # 获取组对象
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                raise CommandError(f'组ID {group_id} 不存在')
        elif group_name:
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                raise CommandError(f'组名称 "{group_name}" 不存在')
        else:
            raise CommandError('必须指定 --group-id 或 --group-name')
        
        # 检查是否已存在标识符
        try:
            existing = getattr(group, 'grouproleidentifier', None)
            if existing:
                self.stdout.write(
                    self.style.WARNING(
                        f'组 "{group.name}" 已存在角色标识符: {getattr(existing, "role_identifier", "未知")}'
                    )
                )
                return
        except Exception:
            pass
        
        # 创建标识符
        with transaction.atomic():
            identifier = GroupRoleIdentifier.objects.create(
                group=group,
                role_identifier=role_identifier,
                status=status,
                sync_status='pending',
                last_sync_at=timezone.now()
            )
            
            # 记录日志
            PermissionSyncLog.objects.create(
                action='create_identifier',
                target_type='group',
                target_id=str(group.id),
                details={
                    'group_name': group.name,
                    'role_identifier': role_identifier,
                    'status': status
                },
                status='success'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功为组 "{group.name}" 创建角色标识符: {role_identifier}'
            )
        )
    
    def batch_sync(self, options: Dict[str, Any]):
        """批量同步组和角色映射"""
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        self.stdout.write('开始批量同步组和角色映射...')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('这是一次试运行，不会实际执行同步操作'))
        
        checker = GroupConsistencyChecker()
        
        # 获取所有需要同步的组
        if force:
            groups = Group.objects.all()
        else:
            try:
                groups = Group.objects.filter(
                    grouproleidentifier__sync_status__in=['pending', 'failed']
                )
            except Exception:
                groups = Group.objects.all()
        
        total_groups = groups.count()
        success_count = 0
        error_count = 0
        errors = []
        
        self.stdout.write(f'找到 {total_groups} 个需要同步的组')
        
        for i, group in enumerate(groups, 1):
            self.stdout.write(f'[{i}/{total_groups}] 同步组: {group.name}', ending='')
            
            if dry_run:
                self.stdout.write(' (试运行)')
                continue
            
            try:
                with transaction.atomic():
                    try:
                        result = getattr(checker, 'sync_group_to_role', lambda x: {'success': False, 'error': '方法不存在'})(group)
                        if result.get('success', False):
                            success_count += 1
                            self.stdout.write(' ✓')
                        else:
                            error_count += 1
                            error_msg = result.get('error', '未知错误')
                            errors.append(f'{group.name}: {error_msg}')
                            self.stdout.write(f' ✗ ({error_msg})')
                    except AttributeError:
                        error_count += 1
                        errors.append(f'{group.name}: 同步方法不可用')
                        self.stdout.write(' ✗ (同步方法不可用)')
            except Exception as e:
                error_count += 1
                errors.append(f'{group.name}: {str(e)}')
                self.stdout.write(f' ✗ ({str(e)})')
        
        if not dry_run:
            self.stdout.write('\n批量同步完成:')
            self.stdout.write(f'  成功: {success_count}')
            self.stdout.write(f'  失败: {error_count}')
            
            if errors:
                self.stdout.write('\n错误详情:')
                for error in errors[:10]:  # 最多显示10个错误
                    self.stdout.write(f'  - {error}')
                if len(errors) > 10:
                    self.stdout.write(f'  ... 还有 {len(errors) - 10} 个错误')
    
    def check_consistency(self, options: Dict[str, Any]):
        """检查一致性"""
        fix = options.get('fix', False)
        group_id = options.get('group_id')
        
        checker = GroupConsistencyChecker()
        
        if group_id:
            # 检查特定组
            try:
                group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                raise CommandError(f'组ID {group_id} 不存在')
            
            self.stdout.write(f'检查组 "{group.name}" 的一致性...')
            result = checker.check_group_consistency(group)
            
            if result['is_consistent']:
                self.stdout.write(self.style.SUCCESS('✓ 组状态一致'))
            else:
                self.stdout.write(self.style.WARNING('⚠ 发现不一致问题:'))
                for issue in result.get('issues', []):
                    self.stdout.write(f'  - {issue}')
                
                if fix:
                    self.stdout.write('正在修复问题...')
                    fix_result = checker.fix_group_issues(group)
                    if fix_result.get('success', False):
                        self.stdout.write(self.style.SUCCESS('✓ 问题修复完成'))
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ 修复失败: {fix_result.get("error", "未知错误")}'
                            )
                        )
        else:
            # 检查所有组
            self.stdout.write('检查所有组的一致性...')
            result = checker.check_all_groups_consistency()
            
            total_groups = result['total_groups']
            consistent_groups = result['consistent_groups']
            inconsistent_groups = result['inconsistent_groups']
            
            self.stdout.write(f'总组数: {total_groups}')
            self.stdout.write(f'一致的组: {consistent_groups}')
            self.stdout.write(f'不一致的组: {inconsistent_groups}')
            
            if inconsistent_groups > 0:
                self.stdout.write('\n不一致的组详情:')
                for group_info in result.get('inconsistent_details', [])[:10]:
                    self.stdout.write(f'  - {group_info["group_name"]}: {group_info["issues"]}')
                
                if fix:
                    self.stdout.write('\n正在修复所有问题...')
                    fix_result = checker.fix_all_issues()
                    self.stdout.write(f'修复结果: 成功 {fix_result["success_count"]}, 失败 {fix_result["error_count"]}')
    
    def cleanup_orphaned(self, options: Dict[str, Any]):
        """清理孤立的组标识符"""
        dry_run = options.get('dry_run', False)
        
        # 查找孤立的标识符（对应的组不存在）
        orphaned_identifiers = GroupRoleIdentifier.objects.filter(
            group__isnull=True
        )
        
        count = orphaned_identifiers.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('没有发现孤立的组标识符'))
            return
        
        self.stdout.write(f'发现 {count} 个孤立的组标识符')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('这是一次试运行，不会实际删除'))
            for identifier in orphaned_identifiers[:10]:
                self.stdout.write(f'  - ID: {identifier.id}, 角色标识: {identifier.role_identifier}')
            if count > 10:
                self.stdout.write(f'  ... 还有 {count - 10} 个')
        else:
            orphaned_identifiers.delete()
            self.stdout.write(self.style.SUCCESS(f'成功删除 {count} 个孤立的组标识符'))
    
    def show_stats(self, options: Dict[str, Any]):
        """显示统计信息"""
        days = options.get('days', 7)
        
        monitor = SyncMonitor()
        stats = monitor.get_sync_statistics(days)
        
        self.stdout.write(f'\n=== 最近 {days} 天的同步统计 ===')
        self.stdout.write(f'总日志数: {stats["total_logs"]}')
        self.stdout.write(f'成功率: {stats["success_rate"]:.1f}%')
        
        self.stdout.write('\n按操作类型统计:')
        for action_stat in stats['action_stats']:
            self.stdout.write(f'  {action_stat["action"]}: {action_stat["count"]}')
        
        self.stdout.write('\n按目标类型统计:')
        for target_stat in stats['target_stats']:
            self.stdout.write(f'  {target_stat["target_type"]}: {target_stat["count"]}')
        
        self.stdout.write('\n最活跃用户:')
        for user_stat in stats['user_stats']:
            self.stdout.write(f'  {user_stat["created_by__username"]}: {user_stat["count"]}')
    
    def monitor_health(self, options: Dict[str, Any]):
        """监控健康状态"""
        send_alerts = options.get('send_alerts', False)
        
        monitor = SyncMonitor()
        health_report = monitor.check_sync_health()
        
        self.stdout.write('\n=== 同步系统健康状态 ===')
        self.stdout.write(f'健康分数: {health_report["health_score"]}%')
        self.stdout.write(f'检查时间: {health_report["timestamp"]}')
        self.stdout.write(f'总日志数: {health_report["total_logs"]}')
        
        # 显示状态分布
        self.stdout.write('\n状态分布:')
        for status, count in health_report['status_distribution'].items():
            self.stdout.write(f'  {status}: {count}')
        
        # 显示告警
        alerts = health_report.get('alerts', [])
        if alerts:
            self.stdout.write(f'\n发现 {len(alerts)} 个告警:')
            for alert in alerts:
                severity_color = {
                    'high': self.style.ERROR,
                    'medium': self.style.WARNING,
                    'low': self.style.SUCCESS
                }.get(alert['severity'], self.style.NOTICE)
                
                self.stdout.write(
                    severity_color(f'  [{alert["severity"].upper()}] {alert["message"]}')
                )
            
            if send_alerts:
                self.stdout.write('\n发送告警邮件...')
                if monitor.send_alert_email(alerts):
                    self.stdout.write(self.style.SUCCESS('告警邮件发送成功'))
                else:
                    self.stdout.write(self.style.ERROR('告警邮件发送失败'))
        else:
            self.stdout.write(self.style.SUCCESS('\n没有发现告警'))
    
    def cleanup_logs(self, options: Dict[str, Any]):
        """清理旧日志"""
        days = options.get('days', 30)
        
        monitor = SyncMonitor()
        deleted_count = monitor.cleanup_old_logs(days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功清理了 {deleted_count} 条超过 {days} 天的同步日志'
            )
        )