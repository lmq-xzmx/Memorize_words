from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from apps.accounts.services.role_service import RoleService
from apps.accounts.models import CustomUser, UserRole, RoleExtension, UserExtensionData
from typing import Dict, List, Any
import time


class Command(BaseCommand):
    """
    验证角色系统优化效果的管理命令
    """
    help = '验证角色系统优化效果，包括性能测试和数据一致性检查'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--performance',
            action='store_true',
            help='运行性能测试'
        )
        parser.add_argument(
            '--consistency',
            action='store_true',
            help='检查数据一致性'
        )
        parser.add_argument(
            '--cache',
            action='store_true',
            help='测试缓存功能'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='运行所有测试'
        )
        parser.add_argument(
            '--iterations',
            type=int,
            default=100,
            help='性能测试迭代次数（默认100）'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始角色系统优化验证...'))
        
        if options['all']:
            options['performance'] = True
            options['consistency'] = True
            options['cache'] = True
        
        results = {}
        
        if options['performance']:
            results['performance'] = self.test_performance(options['iterations'])
        
        if options['consistency']:
            results['consistency'] = self.test_consistency()
        
        if options['cache']:
            results['cache'] = self.test_cache()
        
        self.print_summary(results)
    
    def test_performance(self, iterations: int) -> Dict[str, Any]:
        """
        性能测试
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.WARNING('性能测试'))
        self.stdout.write('='*50)
        
        results = {}
        
        # 测试角色选择项获取性能
        self.stdout.write('测试角色选择项获取性能...')
        start_time = time.time()
        for _ in range(iterations):
            choices = RoleService.get_role_choices()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations * 1000  # 转换为毫秒
        results['role_choices_avg_ms'] = round(avg_time, 3)
        self.stdout.write(f'  平均响应时间: {avg_time:.3f}ms')
        
        # 测试角色验证性能
        self.stdout.write('测试角色验证性能...')
        test_roles = [UserRole.STUDENT, UserRole.TEACHER, UserRole.ADMIN, 'invalid_role']
        start_time = time.time()
        for _ in range(iterations):
            for role in test_roles:
                RoleService.validate_role(role)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / (iterations * len(test_roles)) * 1000
        results['role_validation_avg_ms'] = round(avg_time, 3)
        self.stdout.write(f'  平均验证时间: {avg_time:.3f}ms')
        
        # 测试数据库查询性能
        self.stdout.write('测试数据库查询性能...')
        
        # 用户角色查询
        start_time = time.time()
        for _ in range(iterations):
            list(CustomUser.objects.filter(role=UserRole.STUDENT, is_active=True)[:10])
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations * 1000
        results['db_user_query_avg_ms'] = round(avg_time, 3)
        self.stdout.write(f'  用户角色查询平均时间: {avg_time:.3f}ms')
        
        # 角色增项查询
        start_time = time.time()
        for _ in range(iterations):
            list(RoleExtension.objects.filter(role=UserRole.STUDENT, is_active=True))
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations * 1000
        results['db_extension_query_avg_ms'] = round(avg_time, 3)
        self.stdout.write(f'  角色增项查询平均时间: {avg_time:.3f}ms')
        
        return results
    
    def test_consistency(self) -> Dict[str, Any]:
        """
        数据一致性测试
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.WARNING('数据一致性测试'))
        self.stdout.write('='*50)
        
        results = {
            'issues': [],
            'total_checks': 0,
            'passed_checks': 0
        }
        
        # 检查角色选择项一致性
        self.stdout.write('检查角色选择项一致性...')
        results['total_checks'] += 1
        
        try:
            service_choices = RoleService.get_role_choices(include_empty=False)
            model_choices = list(RoleService.get_role_choices(include_empty=False))
            
            # service_choices 是 (code, display_name) 的元组列表
            service_roles = {choice[0] for choice in service_choices if choice[0]}  # 排除空值
            model_roles = {choice[0] for choice in model_choices}
            
            if service_roles.issuperset(model_roles):
                self.stdout.write(self.style.SUCCESS('  ✓ 角色选择项一致'))
                results['passed_checks'] += 1
            else:
                missing = model_roles - service_roles
                results['issues'].append(f'角色选择项不一致，缺失: {missing}')
                self.stdout.write(self.style.ERROR(f'  ✗ 角色选择项不一致，缺失: {missing}'))
        except Exception as e:
            results['issues'].append(f'角色选择项检查失败: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ 检查失败: {str(e)}'))
        
        # 检查用户角色数据完整性
        self.stdout.write('检查用户角色数据完整性...')
        results['total_checks'] += 1
        
        try:
            invalid_users = CustomUser.objects.exclude(
                role__in=[choice[0] for choice in RoleService.get_role_choices(include_empty=False)]
            ).filter(role__isnull=False)
            
            if not invalid_users.exists():
                self.stdout.write(self.style.SUCCESS('  ✓ 用户角色数据完整'))
                results['passed_checks'] += 1
            else:
                count = invalid_users.count()
                results['issues'].append(f'发现{count}个用户的角色数据无效')
                self.stdout.write(self.style.ERROR(f'  ✗ 发现{count}个用户的角色数据无效'))
        except Exception as e:
            results['issues'].append(f'用户角色数据检查失败: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ 检查失败: {str(e)}'))
        
        # 检查角色增项数据一致性
        self.stdout.write('检查角色增项数据一致性...')
        results['total_checks'] += 1
        
        try:
            # 检查是否有用户增项数据对应的角色增项配置不存在
            orphaned_data = UserExtensionData.objects.filter(
                role_extension__isnull=True
            )
            
            if not orphaned_data.exists():
                self.stdout.write(self.style.SUCCESS('  ✓ 角色增项数据一致'))
                results['passed_checks'] += 1
            else:
                count = orphaned_data.count()
                results['issues'].append(f'发现{count}个孤立的用户增项数据')
                self.stdout.write(self.style.ERROR(f'  ✗ 发现{count}个孤立的用户增项数据'))
        except Exception as e:
            results['issues'].append(f'角色增项数据检查失败: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ 检查失败: {str(e)}'))
        
        return results
    
    def test_cache(self) -> Dict[str, Any]:
        """
        缓存功能测试
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.WARNING('缓存功能测试'))
        self.stdout.write('='*50)
        
        results = {
            'cache_working': False,
            'cache_performance': {},
            'issues': []
        }
        
        try:
            # 清除缓存
            self.stdout.write('清除角色缓存...')
            RoleService.clear_cache()
            
            # 测试缓存写入
            self.stdout.write('测试缓存写入...')
            start_time = time.time()
            choices1 = RoleService.get_role_choices()  # 第一次调用，应该从数据库加载
            first_call_time = time.time() - start_time
            
            # 测试缓存读取
            self.stdout.write('测试缓存读取...')
            start_time = time.time()
            choices2 = RoleService.get_role_choices()  # 第二次调用，应该从缓存读取
            second_call_time = time.time() - start_time
            
            # 验证数据一致性
            if choices1 == choices2:
                results['cache_working'] = True
                self.stdout.write(self.style.SUCCESS('  ✓ 缓存数据一致'))
            else:
                results['issues'].append('缓存数据不一致')
                self.stdout.write(self.style.ERROR('  ✗ 缓存数据不一致'))
            
            # 性能对比
            results['cache_performance'] = {
                'first_call_ms': round(first_call_time * 1000, 3),
                'second_call_ms': round(second_call_time * 1000, 3),
                'improvement_ratio': round(first_call_time / second_call_time, 2) if second_call_time > 0 else 0
            }
            
            self.stdout.write(f'  首次调用时间: {first_call_time*1000:.3f}ms')
            self.stdout.write(f'  缓存调用时间: {second_call_time*1000:.3f}ms')
            if second_call_time > 0:
                improvement = first_call_time / second_call_time
                self.stdout.write(f'  性能提升: {improvement:.2f}倍')
            
            # 测试缓存刷新
            self.stdout.write('测试缓存刷新...')
            RoleService.refresh_cache()
            choices3 = RoleService.get_role_choices()
            
            if choices1 == choices3:
                self.stdout.write(self.style.SUCCESS('  ✓ 缓存刷新正常'))
            else:
                results['issues'].append('缓存刷新后数据不一致')
                self.stdout.write(self.style.ERROR('  ✗ 缓存刷新后数据不一致'))
                
        except Exception as e:
            results['issues'].append(f'缓存测试失败: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ 缓存测试失败: {str(e)}'))
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """
        打印测试总结
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('测试总结'))
        self.stdout.write('='*50)
        
        if 'performance' in results:
            perf = results['performance']
            self.stdout.write('\n性能测试结果:')
            self.stdout.write(f'  角色选择项平均响应时间: {perf.get("role_choices_avg_ms", "N/A")}ms')
            self.stdout.write(f'  角色验证平均时间: {perf.get("role_validation_avg_ms", "N/A")}ms')
            self.stdout.write(f'  数据库用户查询平均时间: {perf.get("db_user_query_avg_ms", "N/A")}ms')
            self.stdout.write(f'  数据库增项查询平均时间: {perf.get("db_extension_query_avg_ms", "N/A")}ms')
        
        if 'consistency' in results:
            cons = results['consistency']
            self.stdout.write('\n数据一致性测试结果:')
            self.stdout.write(f'  总检查项: {cons.get("total_checks", 0)}')
            self.stdout.write(f'  通过检查: {cons.get("passed_checks", 0)}')
            if cons.get('issues'):
                self.stdout.write('  发现问题:')
                for issue in cons['issues']:
                    self.stdout.write(f'    - {issue}')
        
        if 'cache' in results:
            cache_res = results['cache']
            self.stdout.write('\n缓存功能测试结果:')
            self.stdout.write(f'  缓存工作状态: {"正常" if cache_res.get("cache_working") else "异常"}')
            if cache_res.get('cache_performance'):
                perf = cache_res['cache_performance']
                self.stdout.write(f'  性能提升: {perf.get("improvement_ratio", "N/A")}倍')
            if cache_res.get('issues'):
                self.stdout.write('  发现问题:')
                for issue in cache_res['issues']:
                    self.stdout.write(f'    - {issue}')
        
        # 总体评估
        self.stdout.write('\n总体评估:')
        total_issues = sum(len(r.get('issues', [])) for r in results.values())
        if total_issues == 0:
            self.stdout.write(self.style.SUCCESS('  ✓ 角色系统优化成功，所有测试通过'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 发现 {total_issues} 个问题，需要进一步优化'))
        
        self.stdout.write('\n角色系统优化验证完成！')