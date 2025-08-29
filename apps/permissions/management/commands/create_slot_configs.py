from django.core.management.base import BaseCommand
from django.db import transaction
from apps.permissions.models import SlotConfig
from apps.accounts.services.role_service import RoleService


class Command(BaseCommand):
    help = '为所有角色创建4个和5个槽位的配置'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，不实际创建配置',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建已存在的配置',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('预览模式：以下是将要创建的槽位配置'))
        else:
            self.stdout.write('开始创建槽位配置...')
            
        # 获取所有角色
        roles = RoleService.get_all_roles()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'找到 {len(roles)} 个角色'))
        
        created_count = 0
        skipped_count = 0
        
        if not dry_run:
            with transaction.atomic():
                for role_data in roles:
                    role_code = role_data['code']
                    role_name = role_data['display_name']
                    
                    # 为每个角色创建4个和5个槽位的配置
                    for slot_count in [4, 5]:
                        # 实际创建配置
                        existing = SlotConfig.objects.filter(
                            role=role_code, 
                            slot_count=slot_count
                        ).first()
                        
                        if existing and not force:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'跳过 {role_name} ({role_code}) - {slot_count}个槽位 (已存在)'
                                )
                            )
                            skipped_count += 1
                        else:
                            if existing and force:
                                existing.delete()
                                
                            SlotConfig.objects.create(
                                role=role_code,
                                slot_count=slot_count,
                                is_active=(slot_count == 4)  # 4个槽位的配置默认激活
                            )
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'创建 {role_name} ({role_code}) - {slot_count}个槽位 '
                                    f'(激活: {"是" if slot_count == 4 else "否"})'
                                )
                            )
                            created_count += 1
        else:
            # 预览模式
            for role_data in roles:
                role_code = role_data['code']
                role_name = role_data['display_name']
                
                # 为每个角色创建4个和5个槽位的配置
                for slot_count in [4, 5]:
                    # 检查是否已存在
                    existing = SlotConfig.objects.filter(
                        role=role_code, 
                        slot_count=slot_count
                    ).first()
                    
                    if existing and not force:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  跳过 {role_name} ({role_code}) - {slot_count}个槽位 (已存在)'
                            )
                        )
                        skipped_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  将创建 {role_name} ({role_code}) - {slot_count}个槽位 '
                                f'(激活: {"是" if slot_count == 4 else "否"})'
                            )
                        )
                        created_count += 1
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n预览完成！'))
            self.stdout.write(self.style.SUCCESS(f'将创建 {created_count} 个配置'))
        else:
            self.stdout.write('\n创建完成！')
            self.stdout.write(self.style.SUCCESS(f'成功创建 {created_count} 个配置'))
            
        self.stdout.write(self.style.WARNING(f'跳过 {skipped_count} 个已存在的配置'))