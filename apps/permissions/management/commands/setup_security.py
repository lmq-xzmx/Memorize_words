# -*- coding: utf-8 -*-
"""
安全系统设置管理命令
用于初始化安全规则、权限验证和审计系统
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.core.management.color import Style

from ...validators import create_default_security_rules, setup_validation_system
from ...audit import setup_audit_system
from ...models import UserRole

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '设置和管理权限安全系统'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = Style()
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--init-security',
            action='store_true',
            help='初始化安全规则系统'
        )
        
        parser.add_argument(
            '--init-audit',
            action='store_true',
            help='初始化审计系统'
        )
        
        parser.add_argument(
            '--create-rules',
            action='store_true',
            help='创建默认安全规则'
        )
        
        parser.add_argument(
            '--validate-users',
            action='store_true',
            help='验证所有用户权限一致性'
        )
        
        parser.add_argument(
            '--user-id',
            type=int,
            help='指定用户ID进行权限验证'
        )
        
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='生成安全报告'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='报告时间范围（天数）'
        )
        
        parser.add_argument(
            '--test-validation',
            action='store_true',
            help='测试权限验证功能'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行操作，跳过确认'
        )
    
    def handle(self, *args, **options):
        try:
            if options['init_security']:
                self.init_security_system(options)
            
            elif options['init_audit']:
                self.init_audit_system(options)
            
            elif options['create_rules']:
                self.create_security_rules(options)
            
            elif options['validate_users']:
                self.validate_users(options)
            
            elif options['user_id']:
                self.validate_single_user(options['user_id'], options)
            
            elif options['generate_report']:
                self.generate_security_report(options)
            
            elif options['test_validation']:
                self.test_validation_system(options)
            
            else:
                self.print_help('manage.py', 'setup_security')
                
        except Exception as e:
            logger.error(f"命令执行失败: {str(e)}")
            raise CommandError(f"命令执行失败: {str(e)}")
    
    def init_security_system(self, options):
        """初始化安全系统"""
        self.stdout.write(self.style.SUCCESS("开始初始化安全系统..."))
        
        try:
            with transaction.atomic():
                # 设置验证系统
                setup_validation_system()
                
                # 设置审计系统
                setup_audit_system()
                
                self.stdout.write(
                    self.style.SUCCESS("✓ 安全系统初始化完成")
                )
                
        except Exception as e:
            logger.error(f"初始化安全系统失败: {str(e)}")
            raise CommandError(f"初始化安全系统失败: {str(e)}")
    
    def init_audit_system(self, options):
        """初始化审计系统"""
        self.stdout.write(self.style.SUCCESS("开始初始化审计系统..."))
        
        try:
            setup_audit_system()
            
            self.stdout.write(
                self.style.SUCCESS("✓ 审计系统初始化完成")
            )
            
        except Exception as e:
            logger.error(f"初始化审计系统失败: {str(e)}")
            raise CommandError(f"初始化审计系统失败: {str(e)}")
    
    def create_security_rules(self, options):
        """创建安全规则"""
        self.stdout.write(self.style.SUCCESS("开始创建默认安全规则..."))
        
        try:
            create_default_security_rules()
            
            self.stdout.write(
                self.style.SUCCESS("✓ 默认安全规则创建完成")
            )
            
        except Exception as e:
            logger.error(f"创建安全规则失败: {str(e)}")
            raise CommandError(f"创建安全规则失败: {str(e)}")
    
    def validate_users(self, options):
        """验证所有用户权限一致性"""
        self.stdout.write(self.style.SUCCESS("开始验证用户权限一致性..."))
        
        try:
            from ...validators import permission_validator
            
            users = User.objects.all()
            total_users = users.count()
            issues_found = 0
            
            self.stdout.write(f"共需验证 {total_users} 个用户")
            
            for i, user in enumerate(users, 1):
                self.stdout.write(f"验证用户 {i}/{total_users}: {user.username}")
                
                report = permission_validator.check_permission_consistency(user)
                
                if 'error' in report:
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ 验证失败: {report['error']}")
                    )
                    continue
                
                if report['issues']:
                    issues_found += 1
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ 发现 {len(report['issues'])} 个问题")
                    )
                    
                    for issue in report['issues']:
                        self.stdout.write(
                            f"    - {issue['type']}: {issue['description']} ({issue['count']} 项)"
                        )
                else:
                    self.stdout.write(
                        self.style.SUCCESS("  ✓ 权限一致性正常")
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n权限验证完成，共发现 {issues_found} 个用户存在权限问题"
                )
            )
            
        except Exception as e:
            logger.error(f"用户权限验证失败: {str(e)}")
            raise CommandError(f"用户权限验证失败: {str(e)}")
    
    def validate_single_user(self, user_id, options):
        """验证单个用户权限"""
        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(
                self.style.SUCCESS(f"验证用户: {user.username} (ID: {user_id})")
            )
            
            from ...validators import permission_validator
            
            report = permission_validator.check_permission_consistency(user)
            
            if 'error' in report:
                self.stdout.write(
                    self.style.ERROR(f"验证失败: {report['error']}")
                )
                return
            
            # 显示统计信息
            stats = report['statistics']
            self.stdout.write("\n=== 权限统计 ===")
            self.stdout.write(f"所属组数量: {stats['total_groups']}")
            self.stdout.write(f"组权限数量: {stats['group_permissions']}")
            self.stdout.write(f"直接权限数量: {stats['direct_permissions']}")
            self.stdout.write(f"总权限数量: {stats['total_permissions']}")
            
            # 显示问题
            if report['issues']:
                self.stdout.write("\n=== 发现的问题 ===")
                for issue in report['issues']:
                    severity_style = {
                        'low': self.style.WARNING,
                        'medium': self.style.ERROR,
                        'high': self.style.ERROR
                    }.get(issue['severity'], self.style.WARNING)
                    
                    self.stdout.write(
                        severity_style(
                            f"[{issue['severity'].upper()}] {issue['description']} ({issue['count']} 项)"
                        )
                    )
                    
                    # 显示详细信息（限制显示数量）
                    for detail in issue['details'][:5]:
                        self.stdout.write(f"  - {detail['codename']} ({detail['content_type']})")
                    
                    if len(issue['details']) > 5:
                        self.stdout.write(f"  ... 还有 {len(issue['details']) - 5} 项")
            else:
                self.stdout.write(
                    self.style.SUCCESS("\n✓ 未发现权限问题")
                )
            
            # 显示建议
            if report['recommendations']:
                self.stdout.write("\n=== 建议 ===")
                for recommendation in report['recommendations']:
                    self.stdout.write(f"• {recommendation}")
            
        except User.DoesNotExist:
            raise CommandError(f"用户 ID {user_id} 不存在")
        except Exception as e:
            logger.error(f"验证用户 {user_id} 失败: {str(e)}")
            raise CommandError(f"验证用户失败: {str(e)}")
    
    def generate_security_report(self, options):
        """生成安全报告"""
        days = options['days']
        self.stdout.write(
            self.style.SUCCESS(f"生成过去 {days} 天的安全报告...")
        )
        
        try:
            from ...validators import permission_validator
            
            report = permission_validator.generate_security_report(days)
            
            if 'error' in report:
                self.stdout.write(
                    self.style.ERROR(f"生成报告失败: {report['error']}")
                )
                return
            
            # 显示报告摘要
            summary = report['summary']
            self.stdout.write("\n=== 安全报告摘要 ===")
            self.stdout.write(f"报告期间: {report['period']['start'][:10]} 至 {report['period']['end'][:10]}")
            self.stdout.write(f"总事件数: {summary['total_events']}")
            self.stdout.write(f"失败事件: {summary['failed_events']}")
            self.stdout.write(f"拒绝事件: {summary['denied_events']}")
            self.stdout.write(f"可疑事件: {summary['suspicious_events']}")
            self.stdout.write(f"涉及用户: {summary['unique_users']}")
            self.stdout.write(f"涉及资源: {summary['unique_resources']}")
            
            # 显示按操作类型统计
            if report['by_action']:
                self.stdout.write("\n=== 按操作类型统计 ===")
                for action, count in sorted(report['by_action'].items(), key=lambda x: x[1], reverse=True)[:10]:
                    self.stdout.write(f"{action}: {count}")
            
            # 显示按风险等级统计
            if report['by_risk_level']:
                self.stdout.write("\n=== 按风险等级统计 ===")
                for risk, count in report['by_risk_level'].items():
                    style_func = {
                        'critical': self.style.ERROR,
                        'high': self.style.ERROR,
                        'medium': self.style.WARNING,
                        'low': self.style.SUCCESS
                    }.get(risk, self.style.SUCCESS)
                    
                    self.stdout.write(style_func(f"{risk}: {count}"))
            
            # 显示活跃用户
            if report['by_user']:
                self.stdout.write("\n=== 活跃用户 (前5名) ===")
                for username, stats in list(report['by_user'].items())[:5]:
                    success_rate = stats['success_rate']
                    style_func = self.style.SUCCESS if success_rate > 90 else self.style.WARNING
                    
                    self.stdout.write(
                        style_func(
                            f"{username}: {stats['total']} 次操作，成功率 {success_rate}%"
                        )
                    )
            
            # 显示安全事件
            if report['security_incidents']:
                self.stdout.write("\n=== 高风险安全事件 (最近5个) ===")
                for incident in report['security_incidents'][:5]:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[{incident['timestamp'][:19]}] {incident['user']}: "
                            f"{incident['action_type']} - {incident['description']}"
                        )
                    )
            
            # 显示规则违规
            if report['rule_violations']:
                self.stdout.write("\n=== 规则违规事件 (最近5个) ===")
                for violation in report['rule_violations'][:5]:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[{violation['timestamp'][:19]}] {violation['user']}: "
                            f"{violation['description']}"
                        )
                    )
            
            # 显示建议
            if report['recommendations']:
                self.stdout.write("\n=== 安全建议 ===")
                for recommendation in report['recommendations']:
                    self.stdout.write(
                        self.style.WARNING(f"• {recommendation}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS("\n安全报告生成完成")
            )
            
        except Exception as e:
            logger.error(f"生成安全报告失败: {str(e)}")
            raise CommandError(f"生成安全报告失败: {str(e)}")
    
    def test_validation_system(self, options):
        """测试权限验证系统"""
        self.stdout.write(self.style.SUCCESS("测试权限验证系统..."))
        
        try:
            from ...validators import permission_validator
            
            # 获取测试用户
            test_user = User.objects.first()
            if not test_user:
                self.stdout.write(
                    self.style.WARNING("没有找到测试用户，跳过验证测试")
                )
                return
            
            self.stdout.write(f"使用测试用户: {test_user.username}")
            
            # 测试不同的访问场景
            test_cases = [
                {
                    'resource_type': 'user_management',
                    'action': 'view',
                    'description': '查看用户管理'
                },
                {
                    'resource_type': 'user_management',
                    'action': 'create',
                    'description': '创建用户'
                },
                {
                    'resource_type': 'role_management',
                    'action': 'update',
                    'description': '更新角色'
                },
                {
                    'resource_type': 'system_config',
                    'action': 'delete',
                    'description': '删除系统配置'
                }
            ]
            
            self.stdout.write("\n=== 权限验证测试结果 ===")
            
            for test_case in test_cases:
                is_valid, message, violations, rule_results = permission_validator.validate_user_access(
                    user=test_user,
                    resource_type=test_case['resource_type'],
                    action=test_case['action'],
                    ip_address='127.0.0.1',
                    user_agent='Test Agent'
                )
                
                status_style = self.style.SUCCESS if is_valid else self.style.ERROR
                status_text = "✓ 允许" if is_valid else "✗ 拒绝"
                
                self.stdout.write(
                    status_style(
                        f"{test_case['description']}: {status_text} - {message}"
                    )
                )
                
                if violations:
                    for violation in violations:
                        self.stdout.write(f"  违规: {violation}")
                
                # 显示规则验证结果
                if rule_results:
                    passed_rules = sum(1 for r in rule_results.values() if r['valid'])
                    total_rules = len(rule_results)
                    self.stdout.write(
                        f"  规则验证: {passed_rules}/{total_rules} 通过"
                    )
            
            self.stdout.write(
                self.style.SUCCESS("\n权限验证系统测试完成")
            )
            
        except Exception as e:
            logger.error(f"测试权限验证系统失败: {str(e)}")
            raise CommandError(f"测试权限验证系统失败: {str(e)}")
    
    def print_status(self, message, success=True):
        """打印状态信息"""
        if success:
            self.stdout.write(self.style.SUCCESS(f"✓ {message}"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ {message}"))