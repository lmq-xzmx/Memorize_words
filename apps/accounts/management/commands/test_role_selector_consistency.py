from django.core.management.base import BaseCommand
from django.contrib import admin
from django.apps import apps
from apps.accounts.services.role_service import RoleService
from apps.permissions.role_selector_config import StandardRoleAdminMixin
import inspect


class Command(BaseCommand):
    help = '测试角色选择器的一致性'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='显示详细信息'
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write(self.style.SUCCESS('开始角色选择器一致性测试...'))
        
        # 获取所有注册的Admin类
        admin_classes = self._get_admin_classes_with_role_fields()
        
        if verbose:
            self.stdout.write(f'\n找到 {len(admin_classes)} 个包含角色字段的Admin类:')
            for admin_class, model_class in admin_classes:
                admin_name = admin_class.__class__.__name__
                model_name = model_class.__name__
                self.stdout.write(f'  - {admin_name} ({model_name})')
        
        # 测试统一性
        self._test_role_selector_consistency(admin_classes, verbose)
        
        # 测试数据源一致性
        self._test_data_source_consistency(verbose)
        
        self.stdout.write(self.style.SUCCESS('\n角色选择器一致性测试完成！'))
    
    def _get_admin_classes_with_role_fields(self):
        """获取包含角色字段的Admin类"""
        admin_classes = []
        
        for model, admin_class in admin.site._registry.items():
            # 检查模型是否有role字段
            if hasattr(model, 'role'):
                admin_classes.append((admin_class, model))
        
        return admin_classes
    
    def _test_role_selector_consistency(self, admin_classes, verbose):
        """测试角色选择器一致性"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('角色选择器一致性测试')
        self.stdout.write('='*50)
        
        consistent_count = 0
        total_count = len(admin_classes)
        
        for admin_class, model_class in admin_classes:
            is_consistent = self._check_admin_consistency(admin_class, model_class, verbose)
            if is_consistent:
                consistent_count += 1
        
        self.stdout.write(f'\n一致性测试结果:')
        self.stdout.write(f'  总Admin类数: {total_count}')
        self.stdout.write(f'  使用统一选择器: {consistent_count}')
        self.stdout.write(f'  一致性比例: {consistent_count/total_count*100:.1f}%')
        
        if consistent_count == total_count:
            self.stdout.write(self.style.SUCCESS('  ✓ 所有Admin类都使用了统一的角色选择器'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 有 {total_count - consistent_count} 个Admin类未使用统一选择器'))
    
    def _check_admin_consistency(self, admin_class, model_class, verbose):
        """检查单个Admin类的一致性"""
        class_name = admin_class.__class__.__name__
        model_name = model_class.__name__
        
        # 检查是否继承了StandardRoleAdminMixin
        admin_class_type = admin_class.__class__
        uses_mixin = issubclass(admin_class_type, StandardRoleAdminMixin)
        
        # 检查MRO中是否包含StandardRoleAdminMixin
        mixin_in_mro = any(cls.__name__ == 'StandardRoleAdminMixin' for cls in admin_class_type.__mro__)
        
        is_consistent = uses_mixin or mixin_in_mro
        
        if verbose:
            status = '✓' if is_consistent else '✗'
            self.stdout.write(f'  {status} {class_name} ({model_name})')
            if not is_consistent:
                self.stdout.write(f'    - 未继承StandardRoleAdminMixin')
        
        return is_consistent
    
    def _test_data_source_consistency(self, verbose):
        """测试数据源一致性"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('数据源一致性测试')
        self.stdout.write('='*50)
        
        try:
            # 获取角色服务的数据
            service_roles = RoleService.get_role_choices(include_empty=False)
            service_role_codes = {role[0] for role in service_roles}
            
            # 获取预定义角色
            from apps.accounts.models import UserRole
            predefined_roles = {choice[0] for choice in UserRole.choices}
            
            # 获取角色管理中的角色
            try:
                from apps.permissions.models import RoleManagement
                management_roles = set(RoleManagement.objects.filter(
                    is_active=True
                ).values_list('role', flat=True))
            except ImportError:
                management_roles = set()
            
            if verbose:
                self.stdout.write(f'\n数据源详情:')
                self.stdout.write(f'  预定义角色: {sorted(predefined_roles)}')
                self.stdout.write(f'  管理角色: {sorted(management_roles)}')
                self.stdout.write(f'  服务层角色: {sorted(service_role_codes)}')
            
            # 检查一致性
            expected_roles = predefined_roles | management_roles
            missing_in_service = expected_roles - service_role_codes
            extra_in_service = service_role_codes - expected_roles
            
            self.stdout.write(f'\n数据源一致性结果:')
            self.stdout.write(f'  预定义角色数: {len(predefined_roles)}')
            self.stdout.write(f'  管理角色数: {len(management_roles)}')
            self.stdout.write(f'  服务层角色数: {len(service_role_codes)}')
            
            if not missing_in_service and not extra_in_service:
                self.stdout.write(self.style.SUCCESS('  ✓ 数据源完全一致'))
            else:
                if missing_in_service:
                    self.stdout.write(self.style.WARNING(f'  ⚠ 服务层缺失角色: {missing_in_service}'))
                if extra_in_service:
                    self.stdout.write(self.style.WARNING(f'  ⚠ 服务层多余角色: {extra_in_service}'))
            
            # 测试缓存一致性
            self._test_cache_consistency(verbose)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'数据源测试失败: {e}'))
    
    def _test_cache_consistency(self, verbose):
        """测试缓存一致性"""
        self.stdout.write(f'\n缓存一致性测试:')
        
        try:
            # 清除缓存
            RoleService.clear_cache()
            
            # 第一次调用（写入缓存）
            roles1 = RoleService.get_role_choices(include_empty=False)
            
            # 第二次调用（从缓存读取）
            roles2 = RoleService.get_role_choices(include_empty=False)
            
            # 比较结果
            if roles1 == roles2:
                self.stdout.write(self.style.SUCCESS('  ✓ 缓存数据一致'))
            else:
                self.stdout.write(self.style.ERROR('  ✗ 缓存数据不一致'))
                if verbose:
                    self.stdout.write(f'    第一次: {len(roles1)} 个角色')
                    self.stdout.write(f'    第二次: {len(roles2)} 个角色')
            
            # 测试缓存刷新
            RoleService.refresh_cache()
            roles3 = RoleService.get_role_choices(include_empty=False)
            
            if roles1 == roles3:
                self.stdout.write(self.style.SUCCESS('  ✓ 缓存刷新正常'))
            else:
                self.stdout.write(self.style.ERROR('  ✗ 缓存刷新异常'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  缓存测试失败: {e}'))