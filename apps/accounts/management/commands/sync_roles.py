from django.core.management.base import BaseCommand
from apps.accounts.models import UserRole
from apps.permissions.models import RoleManagement


class Command(BaseCommand):
    help = '同步UserRole枚举到RoleManagement数据库'
    
    def handle(self, *args, **options):
        self.stdout.write('=== 开始同步角色数据 ===')
        
        # 显示当前UserRole枚举
        self.stdout.write('\n当前UserRole枚举中的角色:')
        for choice in UserRole.choices:
            self.stdout.write(f'  - {choice[0]}: {choice[1]}')
        
        # 显示当前RoleManagement数据库中的角色
        self.stdout.write('\n当前RoleManagement数据库中的角色:')
        existing_roles = RoleManagement.objects.all().order_by('sort_order')
        if existing_roles.exists():
            for role in existing_roles:
                self.stdout.write(f'  - {role.role}: {role.display_name} (活跃: {role.is_active})')
        else:
            self.stdout.write('  数据库中暂无角色数据')
        
        # 同步角色数据
        self.stdout.write('\n开始同步角色数据...')
        created_count = 0
        updated_count = 0
        
        for i, (role_code, role_name) in enumerate(UserRole.choices):
            role_obj, created = RoleManagement.objects.get_or_create(
                role=role_code,
                defaults={
                    'display_name': role_name,
                    'description': f'系统预定义角色：{role_name}',
                    'is_active': True,
                    'sort_order': i * 10  # 给排序留出空间
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ 创建角色: {role_code} - {role_name}')
            else:
                # 更新显示名称（如果需要）
                if role_obj.display_name != role_name:
                    role_obj.display_name = role_name
                    role_obj.save()
                    updated_count += 1
                    self.stdout.write(f'  ↻ 更新角色: {role_code} - {role_name}')
                else:
                    self.stdout.write(f'  - 角色已存在: {role_code} - {role_name}')
        
        self.stdout.write(f'\n=== 同步完成 ===')
        self.stdout.write(f'创建角色数量: {created_count}')
        self.stdout.write(f'更新角色数量: {updated_count}')
        self.stdout.write(f'总角色数量: {RoleManagement.objects.count()}')
        
        # 清除角色服务缓存
        try:
            from apps.accounts.services.role_service import RoleService
            RoleService.clear_cache()
            self.stdout.write('✓ 已清除角色服务缓存')
        except Exception as e:
            self.stdout.write(f'⚠ 清除缓存失败: {e}')