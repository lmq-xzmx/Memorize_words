from django.core.management.base import BaseCommand
from django.db import transaction
from apps.permissions.models import (
    RoleSlotMenuAssignment, 
    SlotConfig, 
    MenuModuleConfig
)
from apps.accounts.services.role_service import RoleService


class Command(BaseCommand):
    help = '初始化角色槽位菜单分配 - 为所有角色创建基础的槽位菜单配置'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--preview',
            action='store_true',
            help='预览模式，只显示将要创建的配置，不实际创建'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重建，删除现有配置并重新创建'
        )
        
        parser.add_argument(
            '--role',
            type=str,
            help='只为指定角色创建配置'
        )
    
    def handle(self, *args, **options):
        preview_mode = options['preview']
        force_rebuild = options['force']
        target_role = options['role']
        
        if preview_mode:
            self.stdout.write(
                self.style.WARNING('🔍 预览模式 - 不会实际创建数据')
            )
        
        if force_rebuild:
            self.stdout.write(
                self.style.WARNING('⚠️  强制重建模式 - 将删除现有配置')
            )
        
        try:
            with transaction.atomic():
                # 获取所有角色
                all_roles_data = RoleService.get_all_roles(include_inactive=False)
                all_roles = [(role['code'], role['display_name']) for role in all_roles_data]
                
                if target_role:
                    # 验证指定角色是否存在
                    role_codes = [role[0] for role in all_roles]
                    if target_role not in role_codes:
                        self.stdout.write(
                            self.style.ERROR(f'❌ 角色 "{target_role}" 不存在')
                        )
                        return
                    roles_to_process = [(target_role, dict(all_roles)[target_role])]
                else:
                    roles_to_process = all_roles
                
                # 获取所有根菜单
                root_menus = MenuModuleConfig.objects.filter(
                    parent__isnull=True,
                    is_active=True
                ).order_by('sort_order', 'name')
                
                if not root_menus.exists():
                    self.stdout.write(
                        self.style.ERROR('❌ 没有找到可用的根菜单，请先创建根菜单')
                    )
                    return
                
                total_created = 0
                total_updated = 0
                total_deleted = 0
                
                for role_code, role_name in roles_to_process:
                    self.stdout.write(f'\n📋 处理角色: {role_name} ({role_code})')
                    
                    # 获取该角色的槽位配置
                    slot_configs = SlotConfig.objects.filter(role=role_code)
                    
                    if not slot_configs.exists():
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  角色 {role_name} 没有槽位配置，跳过')
                        )
                        continue
                    
                    # 如果是强制重建，删除现有配置
                    if force_rebuild and not preview_mode:
                        deleted_count = RoleSlotMenuAssignment.objects.filter(
                            role=role_code
                        ).delete()[0]
                        total_deleted += deleted_count
                        if deleted_count > 0:
                            self.stdout.write(
                                self.style.WARNING(f'🗑️  删除了 {deleted_count} 个现有配置')
                            )
                    
                    # 为每个槽位配置创建菜单分配
                    for slot_config in slot_configs:
                        slot_count = slot_config.slot_count
                        
                        self.stdout.write(
                            f'  📊 槽位数量: {slot_count}'
                        )
                        
                        # 为每个槽位位置创建配置
                        for position in range(1, slot_count + 1):
                            # 检查是否已存在
                            existing = RoleSlotMenuAssignment.objects.filter(
                                role=role_code,
                                slot_position=position
                            ).first()
                            
                            if existing and not force_rebuild:
                                self.stdout.write(
                                    f'    ⏭️  槽位 {position} 已存在，跳过'
                                )
                                continue
                            
                            # 选择根菜单（循环分配）
                            menu_index = (position - 1) % root_menus.count()
                            selected_menu = root_menus[menu_index]
                            
                            # 确定菜单状态
                            if position <= min(2, slot_count):  # 前2个槽位为激活状态
                                menu_status = 'active'
                            else:
                                menu_status = 'backup'
                            
                            assignment_data = {
                                'role': role_code,
                                'slot_position': position,
                                'root_menu': selected_menu,
                                'menu_status': menu_status,
                                'is_active': True,
                                'sort_order': position
                            }
                            
                            if preview_mode:
                                self.stdout.write(
                                    f'    🔍 预览槽位 {position}: {selected_menu.name} ({menu_status})'
                                )
                            else:
                                if existing:
                                    # 更新现有记录
                                    for key, value in assignment_data.items():
                                        setattr(existing, key, value)
                                    existing.save()
                                    total_updated += 1
                                    self.stdout.write(
                                        f'    ✅ 更新槽位 {position}: {selected_menu.name} ({menu_status})'
                                    )
                                else:
                                    # 创建新记录
                                    RoleSlotMenuAssignment.objects.create(**assignment_data)
                                    total_created += 1
                                    self.stdout.write(
                                        f'    ✅ 创建槽位 {position}: {selected_menu.name} ({menu_status})'
                                    )
                
                # 显示统计信息
                self.stdout.write('\n' + '='*50)
                if preview_mode:
                    self.stdout.write(
                        self.style.SUCCESS('🔍 预览完成！以上是将要创建的配置')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ 初始化完成！'
                            f'创建: {total_created}, '
                            f'更新: {total_updated}, '
                            f'删除: {total_deleted}'
                        )
                    )
                    
                    if total_created > 0 or total_updated > 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'🎉 角色槽位菜单分配已成功初始化！'
                                f'\n   可以访问 /admin/permissions/roleslotmenuassignment/ 查看和管理配置'
                            )
                        )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 初始化失败: {str(e)}')
            )
            raise