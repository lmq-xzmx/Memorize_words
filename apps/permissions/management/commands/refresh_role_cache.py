from django.core.management.base import BaseCommand
from apps.accounts.services.role_service import RoleService


class Command(BaseCommand):
    help = '手动刷新角色缓存'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-only',
            action='store_true',
            help='仅清除缓存，不预热',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('=== 开始刷新角色缓存 ===')
        
        try:
            if options['clear_only']:
                # 仅清除缓存
                RoleService.clear_cache()
                self.stdout.write(
                    self.style.SUCCESS('✅ 角色缓存已清除')
                )
            else:
                # 刷新缓存（清除+预热）
                RoleService.refresh_cache()
                self.stdout.write(
                    self.style.SUCCESS('✅ 角色缓存已刷新并预热')
                )
            
            # 显示缓存状态
            self.stdout.write('\n=== 缓存状态检查 ===')
            
            # 获取角色数据验证缓存
            roles = RoleService.get_all_roles()
            self.stdout.write(f'📊 当前系统中共有 {len(roles)} 个角色')
            
            active_roles = [r for r in roles if r.get('is_active', True)]
            self.stdout.write(f'🟢 其中 {len(active_roles)} 个角色处于激活状态')
            
            # 显示角色选择项
            choices = RoleService.get_role_choices()
            self.stdout.write(f'📋 角色选择项共 {len(choices)} 个')
            
            self.stdout.write('\n=== 角色缓存刷新完成 ===')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 刷新角色缓存失败: {str(e)}')
            )
            raise e