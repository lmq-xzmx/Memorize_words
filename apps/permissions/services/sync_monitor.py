from django.utils import timezone
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from typing import Dict, List, Optional, Any
from datetime import timedelta
import logging

from ..models_optimized import PermissionSyncLog
from ..models import GroupRoleIdentifier, RoleGroupMapping

logger = logging.getLogger(__name__)


class SyncMonitor:
    """同步状态监控服务
    
    负责监控权限同步状态，检测异常情况并发送告警
    """
    
    def __init__(self):
        self.alert_threshold = getattr(settings, 'SYNC_ALERT_THRESHOLD', 5)  # 失败次数阈值
        self.check_interval = getattr(settings, 'SYNC_CHECK_INTERVAL', 60)  # 检查间隔（分钟）
        self.admin_emails = getattr(settings, 'SYNC_ADMIN_EMAILS', [])
    
    def check_sync_health(self) -> Dict[str, Any]:
        """检查同步健康状态
        
        Returns:
            Dict: 健康状态报告
        """
        now = timezone.now()
        check_time = now - timedelta(minutes=self.check_interval)
        
        # 获取最近的同步日志
        recent_logs = PermissionSyncLog.objects.filter(
            created_at__gte=check_time
        )
        
        # 统计各种状态
        status_stats = recent_logs.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # 获取失败的同步
        failed_syncs = recent_logs.filter(status='error')
        
        # 获取长时间未同步的组
        stale_groups = self._get_stale_groups()
        
        # 获取同步频率异常的组
        frequent_sync_groups = self._get_frequent_sync_groups()
        
        # 构建健康报告
        health_report = {
            'timestamp': now,
            'check_interval_minutes': self.check_interval,
            'total_logs': recent_logs.count(),
            'status_distribution': {item['status']: item['count'] for item in status_stats},
            'failed_syncs': {
                'count': failed_syncs.count(),
                'details': list(failed_syncs.values(
                    'id', 'action', 'target_type', 'target_id', 
                    'details', 'created_at', 'created_by__username'
                ).exclude(created_by__isnull=True)[:10])  # 最近10个失败记录
            },
            'stale_groups': {
                'count': len(stale_groups),
                'details': stale_groups[:10]  # 最多显示10个
            },
            'frequent_sync_groups': {
                'count': len(frequent_sync_groups),
                'details': frequent_sync_groups[:10]
            },
            'alerts': []
        }
        
        # 检查是否需要告警
        alerts = self._check_alerts(health_report)
        health_report['alerts'] = alerts
        
        # 计算健康分数
        health_report['health_score'] = self._calculate_health_score(health_report)
        
        return health_report
    
    def _get_stale_groups(self) -> List[Dict[str, Any]]:
        """获取长时间未同步的组
        
        Returns:
            List: 长时间未同步的组列表
        """
        stale_threshold = timezone.now() - timedelta(days=7)  # 7天未同步
        
        try:
            stale_identifiers = GroupRoleIdentifier.objects.filter(
                Q(last_sync_at__lt=stale_threshold) | Q(last_sync_at__isnull=True),
                status='role_linked'
            ).select_related('group')
        except Exception as e:
            logger.error(f"获取长时间未同步的组时出错: {str(e)}")
            return []
        
        result = []
        for identifier in stale_identifiers:
            try:
                result.append({
                    'group_id': getattr(identifier.group, 'id', None) if identifier.group else None,
                    'group_name': getattr(identifier.group, 'name', '未知组') if identifier.group else '未知组',
                    'role_identifier': getattr(identifier, 'role_identifier', ''),
                    'last_sync_at': getattr(identifier, 'last_sync_at', None),
                    'sync_status': getattr(identifier, 'sync_status', '')
                })
            except Exception as e:
                logger.warning(f"处理组标识符时出错: {str(e)}")
                continue
        return result
    
    def _get_frequent_sync_groups(self) -> List[Dict[str, Any]]:
        """获取同步频率异常的组
        
        Returns:
            List: 同步频率异常的组列表
        """
        recent_time = timezone.now() - timedelta(hours=1)  # 1小时内
        frequent_threshold = 10  # 1小时内超过10次同步认为异常
        
        frequent_logs = PermissionSyncLog.objects.filter(
            created_at__gte=recent_time,
            target_type='group'
        ).values('target_id').annotate(
            sync_count=Count('id')
        ).filter(
            sync_count__gt=frequent_threshold
        ).order_by('-sync_count')
        
        result = []
        for log_data in frequent_logs:
            try:
                from django.contrib.auth.models import Group
                group = Group.objects.get(id=log_data['target_id'])
                result.append({
                    'group_id': getattr(group, 'id', None),
                    'group_name': getattr(group, 'name', '未知组'),
                    'sync_count': log_data.get('sync_count', 0),
                    'time_period': '1小时'
                })
            except (Group.DoesNotExist, Exception) as e:
                logger.warning(f"处理频繁同步组时出错: {str(e)}")
                continue
        
        return result
    
    def _check_alerts(self, health_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查是否需要发送告警
        
        Args:
            health_report: 健康状态报告
            
        Returns:
            List: 告警列表
        """
        alerts = []
        
        # 检查失败同步数量
        failed_count = health_report['failed_syncs']['count']
        if failed_count >= self.alert_threshold:
            alerts.append({
                'type': 'high_failure_rate',
                'severity': 'high',
                'message': f'最近{self.check_interval}分钟内有{failed_count}次同步失败',
                'details': health_report['failed_syncs']['details']
            })
        
        # 检查长时间未同步的组
        stale_count = health_report['stale_groups']['count']
        if stale_count > 0:
            severity = 'high' if stale_count > 10 else 'medium'
            alerts.append({
                'type': 'stale_groups',
                'severity': severity,
                'message': f'发现{stale_count}个组超过7天未同步',
                'details': health_report['stale_groups']['details']
            })
        
        # 检查频繁同步的组
        frequent_count = health_report['frequent_sync_groups']['count']
        if frequent_count > 0:
            alerts.append({
                'type': 'frequent_sync',
                'severity': 'medium',
                'message': f'发现{frequent_count}个组在1小时内频繁同步',
                'details': health_report['frequent_sync_groups']['details']
            })
        
        # 检查健康分数
        health_score = health_report.get('health_score', 100)
        if health_score < 70:
            severity = 'high' if health_score < 50 else 'medium'
            alerts.append({
                'type': 'low_health_score',
                'severity': severity,
                'message': f'系统健康分数较低: {health_score}%',
                'details': {'health_score': health_score}
            })
        
        return alerts
    
    def _calculate_health_score(self, health_report: Dict[str, Any]) -> int:
        """计算健康分数
        
        Args:
            health_report: 健康状态报告
            
        Returns:
            int: 健康分数 (0-100)
        """
        score = 100
        
        # 根据失败率扣分
        total_logs = health_report['total_logs']
        if total_logs > 0:
            failed_count = health_report['failed_syncs']['count']
            failure_rate = failed_count / total_logs
            score -= int(failure_rate * 50)  # 失败率最多扣50分
        
        # 根据长时间未同步的组扣分
        stale_count = health_report['stale_groups']['count']
        if stale_count > 0:
            score -= min(stale_count * 2, 30)  # 每个长时间未同步的组扣2分，最多扣30分
        
        # 根据频繁同步扣分
        frequent_count = health_report['frequent_sync_groups']['count']
        if frequent_count > 0:
            score -= min(frequent_count * 3, 20)  # 每个频繁同步的组扣3分，最多扣20分
        
        return max(0, score)
    
    def send_alert_email(self, alerts: List[Dict[str, Any]]) -> bool:
        """发送告警邮件
        
        Args:
            alerts: 告警列表
            
        Returns:
            bool: 是否发送成功
        """
        if not alerts or not self.admin_emails:
            return False
        
        try:
            # 构建邮件内容
            subject = f'权限同步系统告警 - {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
            
            message_lines = [
                '权限同步系统检测到以下问题：\n'
            ]
            
            for alert in alerts:
                severity_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(alert['severity'], '⚪')
                
                message_lines.append(
                    f"{severity_emoji} [{alert['severity'].upper()}] {alert['message']}"
                )
                
                if alert.get('details'):
                    message_lines.append('详细信息:')
                    if isinstance(alert['details'], list):
                        for detail in alert['details'][:5]:  # 最多显示5个详细信息
                            message_lines.append(f"  - {detail}")
                    else:
                        message_lines.append(f"  {alert['details']}")
                
                message_lines.append('')  # 空行分隔
            
            message_lines.extend([
                '请及时检查和处理相关问题。',
                '',
                '此邮件由权限同步监控系统自动发送。'
            ])
            
            message = '\n'.join(message_lines)
            
            # 发送邮件
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=self.admin_emails,
                fail_silently=False
            )
            
            logger.info(f"告警邮件发送成功，收件人: {self.admin_emails}")
            return True
            
        except Exception as e:
            logger.error(f"发送告警邮件失败: {str(e)}", exc_info=True)
            return False
    
    def get_sync_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取同步统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            Dict: 统计信息
        """
        start_time = timezone.now() - timedelta(days=days)
        
        logs = PermissionSyncLog.objects.filter(
            created_at__gte=start_time
        )
        
        # 按日期统计
        daily_stats = {}
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            day_logs = logs.filter(created_at__date=date)
            
            daily_stats[str(date)] = {
                'total': day_logs.count(),
                'success': day_logs.filter(status='success').count(),
                'warning': day_logs.filter(status='warning').count(),
                'error': day_logs.filter(status='error').count()
            }
        
        # 按操作类型统计
        action_stats = logs.values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按目标类型统计
        target_stats = logs.values('target_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 最活跃的用户
        try:
            user_stats = logs.filter(
                created_by__isnull=False
            ).values(
                'created_by__username'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        except Exception as e:
            logger.warning(f"获取用户统计时出错: {str(e)}")
            user_stats = []
        
        return {
            'period_days': days,
            'total_logs': logs.count(),
            'daily_stats': daily_stats,
            'action_stats': list(action_stats),
            'target_stats': list(target_stats),
            'user_stats': list(user_stats),
            'success_rate': (
                logs.filter(status='success').count() / logs.count() * 100
                if logs.count() > 0 else 0
            )
        }
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """清理旧的同步日志
        
        Args:
            days: 保留天数
            
        Returns:
            int: 删除的日志数量
        """
        cutoff_time = timezone.now() - timedelta(days=days)
        
        old_logs = PermissionSyncLog.objects.filter(
            created_at__lt=cutoff_time
        )
        
        count = old_logs.count()
        old_logs.delete()
        
        logger.info(f"清理了{count}条超过{days}天的同步日志")
        return count