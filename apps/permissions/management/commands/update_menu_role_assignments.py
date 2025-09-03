from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.termcolors import make_style
from apps.permissions.models import MenuModuleConfig, RoleSlotMenuAssignment, MenuValidity
from apps.accounts.services.role_service import RoleService
import logging
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    # 为Django模型添加类型注释以解决linter错误
    MenuModuleConfig.objects = MenuModuleConfig.objects  # type: ignore
    RoleSlotMenuAssignment.objects = RoleSlotMenuAssignment.objects  # type: ignore
    MenuValidity.objects = MenuValidity.objects  # type: ignore

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    更新菜单模块的角色分配机制
    
    基于RoleSlotMenuAssignment的槽位分配，自动推荐和更新MenuModuleConfig的关联角色
    """
    
    help = '根据槽位分配更新菜单角色关联，优化关联角色推荐机制'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_success = make_style(opts=('bold',), fg='green')
        self.style_warning = make_style(opts=('bold',), fg='yellow')
        self.style_error = make_style(opts=('bold',), fg='red')
        self.style_info = make_style(opts=('bold',), fg='blue')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--preview',
            action='store_true',
            help='预览模式，只显示推荐结果不实际更新'
        )
        parser.add_argument(
            '--auto-create',
            action='store_true',
            help='自动创建缺失的角色分配关系'
        )
        parser.add_argument(
            '--menu-key',
            type=str,
            help='指定特定菜单key进行更新'
        )
        parser.add_argument(
            '--role',
            type=str,
            help='指定特定角色进行更新'
        )
    
    def handle(self, *args, **options):
        preview_mode = options['preview']
        auto_create = options['auto_create']
        specific_menu = options.get('menu_key')
        specific_role = options.get('role')
        
        self.stdout.write(self.style_info('=' * 80))
        self.stdout.write(self.style_info('菜单角色分配更新工具'))
        self.stdout.write(self.style_info('=' * 80))
        
        if preview_mode:
            self.stdout.write(self.style_warning('🔍 预览模式 - 不会实际修改数据'))
        
        try:
            # 获取所有角色信息
            all_roles = {role['code']: role['display_name'] for role in RoleService.get_all_roles()}
            self.stdout.write(f"📋 发现 {len(all_roles)} 个角色")
            
            # 分析菜单配置
            menu_filters = {}
            if specific_menu:
                menu_filters['key'] = specific_menu
            
            menus = MenuModuleConfig.objects.filter(**menu_filters).order_by('menu_level', 'sort_order')  # type: ignore
            
            total_processed = 0
            total_recommendations = 0
            total_created = 0
            
            with transaction.atomic():  # type: ignore
                for menu in menus:
                    result = self._analyze_menu_roles(menu, all_roles, specific_role)
                    
                    if result['has_recommendations'] or result['current_roles']:
                        self._display_menu_analysis(menu, result)
                        total_processed += 1
                        total_recommendations += len(result['recommended_roles'])
                        
                        # 如果不是预览模式且启用自动创建
                        if not preview_mode and auto_create:
                            created_count = self._create_missing_assignments(menu, result['missing_roles'])
                            total_created += created_count
                            if created_count > 0:
                                self.stdout.write(self.style_success(f"  ✅ 创建了 {created_count} 个角色分配"))
            
            # 显示统计信息
            self.stdout.write(self.style_info('\n' + '=' * 80))
            self.stdout.write(self.style_info('📊 处理统计'))
            self.stdout.write(f"处理菜单数: {total_processed}")
            self.stdout.write(f"推荐关联数: {total_recommendations}")
            if auto_create and not preview_mode:
                self.stdout.write(f"创建分配数: {total_created}")
            
            if preview_mode:
                self.stdout.write(self.style_warning('\n💡 使用 --auto-create 参数可自动创建缺失的角色分配'))
            
            self.stdout.write(self.style_success('\n✅ 菜单角色分配分析完成'))
            
        except Exception as e:
            self.stdout.write(self.style_error(f'❌ 处理失败: {str(e)}'))
            logger.error(f"菜单角色分配更新失败: {str(e)}", exc_info=True)
            raise
    
    def _analyze_menu_roles(self, menu, all_roles, specific_role=None):
        """分析菜单的角色分配情况"""
        # 获取当前通过MenuValidity关联的角色
        current_roles = set(MenuValidity.objects.filter(  # type: ignore
            menu_module=menu,
            is_valid=True
        ).values_list('role', flat=True).distinct())
        
        # 根据RoleSlotMenuAssignment获取推荐角色
        recommended_roles = set()
        if menu.menu_level == 'root':
            # 查找在槽位分配中使用此菜单的角色
            slot_roles = set(RoleSlotMenuAssignment.objects.filter(  # type: ignore
                root_menu=menu,
                is_active=True
            ).values_list('role', flat=True).distinct())
            recommended_roles = slot_roles
        elif menu.menu_level in ['level1', 'level2']:
            # 对于子菜单，MenuModuleConfig没有parent字段，跳过父菜单角色查找
            pass
        
        # 如果指定了特定角色，只处理该角色
        if specific_role:
            current_roles = current_roles & {specific_role}
            recommended_roles = recommended_roles & {specific_role}
        
        # 计算缺失的推荐角色
        missing_roles = recommended_roles - current_roles
        
        return {
            'current_roles': current_roles,
            'recommended_roles': recommended_roles,
            'missing_roles': missing_roles,
            'has_recommendations': bool(recommended_roles),
            'all_roles': all_roles
        }
    
    def _display_menu_analysis(self, menu, result):
        """显示菜单分析结果"""
        self.stdout.write(f"\n📋 {menu.name} ({menu.key}) - {menu.get_menu_level_display()}")
        
        # 显示当前关联角色
        if result['current_roles']:
            role_names = [result['all_roles'].get(role, role) for role in result['current_roles']]
            self.stdout.write(f"  当前关联: {', '.join(role_names)}")
        else:
            self.stdout.write("  当前关联: 无")
        
        # 显示推荐角色
        if result['recommended_roles']:
            role_names = [result['all_roles'].get(role, role) for role in result['recommended_roles']]
            self.stdout.write(f"  推荐关联: {', '.join(role_names)}")
        
        # 显示缺失的推荐角色
        if result['missing_roles']:
            role_names = [result['all_roles'].get(role, role) for role in result['missing_roles']]
            self.stdout.write(self.style_warning(f"  ⚠️  缺失关联: {', '.join(role_names)}"))
    
    def _create_missing_assignments(self, menu, missing_roles):
        """创建缺失的角色分配"""
        created_count = 0
        
        for role in missing_roles:
            try:
                assignment, created = MenuValidity.objects.get_or_create(  # type: ignore
                    menu_module=menu,
                    role=role,
                    defaults={
                        'is_valid': True
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"    ✅ 创建角色分配: {role}")
                else:
                    self.stdout.write(f"    ℹ️  角色分配已存在: {role}")
            except Exception as e:
                self.stdout.write(self.style_error(f"    ❌ 创建角色分配失败 {role}: {str(e)}"))
        
        return created_count