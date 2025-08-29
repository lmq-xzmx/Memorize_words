from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import UserRole
from apps.permissions.models import RoleManagement, RoleMapping
from apps.permissions.services import RoleMappingService


class Command(BaseCommand):
    help = '初始化角色映射数据，为现有的UserRole创建对应的RoleMapping记录'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建所有映射，即使已存在'
        )
        parser.add_argument(
            '--role',
            type=str,
            help='只初始化指定的角色（使用角色代码）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，不实际创建数据'
        )
    
    def handle(self, *args, **options):
        force = options['force']
        target_role = options['role']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('开始初始化角色映射数据...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('预览模式：不会实际创建数据'))
        
        # 获取所有UserRole选择项
        user_roles = UserRole.choices
        if target_role:
            user_roles = [(code, name) for code, name in user_roles if code == target_role]
            if not user_roles:
                self.stdout.write(self.style.ERROR(f'未找到角色代码: {target_role}'))
                return
        
        total_created = 0
        total_skipped = 0
        total_errors = 0
        
        with transaction.atomic():
            for role_code, role_name in user_roles:
                try:
                    self.stdout.write(f'\n处理角色: {role_name} ({role_code})')
                    
                    # 检查是否已存在映射
                    existing_mapping = RoleMapping.objects.filter(user_role=role_code).first()
                    if existing_mapping and not force:
                        self.stdout.write(f'  跳过: 映射已存在 -> {existing_mapping.role_management.display_name}')
                        total_skipped += 1
                        continue
                    
                    # 查找对应的RoleManagement
                    role_management = self._find_matching_role_management(role_code, role_name)
                    
                    if not role_management:
                        self.stdout.write(self.style.WARNING(f'  警告: 未找到匹配的RoleManagement，将创建默认映射'))
                        role_management = self._create_default_role_management(role_code, role_name, dry_run)
                        if not role_management:
                            total_errors += 1
                            continue
                    
                    # 创建或更新映射
                    if not dry_run:
                        if existing_mapping and force:
                            existing_mapping.role_management = role_management
                            existing_mapping.is_active = True
                            existing_mapping.auto_sync = True
                            existing_mapping.description = f'自动映射: {role_name}'
                            existing_mapping.save()
                            self.stdout.write(f'  更新: {role_name} -> {role_management.display_name}')
                        else:
                            mapping = RoleMapping.objects.create(
                                user_role=role_code,
                                role_management=role_management,
                                is_active=True,
                                auto_sync=True,
                                description=f'自动映射: {role_name}'
                            )
                            self.stdout.write(f'  创建: {role_name} -> {role_management.display_name}')
                        total_created += 1
                    else:
                        self.stdout.write(f'  [预览] 将创建: {role_name} -> {role_management.display_name}')
                        total_created += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  错误: {str(e)}'))
                    total_errors += 1
        
        # 输出统计信息
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'初始化完成!'))
        self.stdout.write(f'创建/更新: {total_created}')
        self.stdout.write(f'跳过: {total_skipped}')
        self.stdout.write(f'错误: {total_errors}')
        
        if not dry_run and total_created > 0:
            self.stdout.write('\n正在验证映射一致性...')
            try:
                issues = RoleMappingService.validate_mapping_consistency()
                total_issues = sum(len(issue_list) for issue_list in issues.values())
                if total_issues == 0:
                    self.stdout.write(self.style.SUCCESS('映射一致性验证通过'))
                else:
                    self.stdout.write(self.style.WARNING(f'发现 {total_issues} 个一致性问题'))
                    for issue_type, issue_list in issues.items():
                        if issue_list:
                            self.stdout.write(f'  {issue_type}: {len(issue_list)} 个')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'一致性验证失败: {str(e)}'))
    
    def _find_matching_role_management(self, role_code, role_name):
        """查找匹配的RoleManagement"""
        # 1. 首先尝试精确匹配role字段
        role_management = RoleManagement.objects.filter(
            role=role_code,
            is_active=True
        ).first()
        
        if role_management:
            return role_management
        
        # 2. 尝试通过display_name匹配
        role_management = RoleManagement.objects.filter(
            display_name__icontains=role_name,
            is_active=True
        ).first()
        
        if role_management:
            return role_management
        
        # 3. 尝试模糊匹配
        keywords = role_name.split()
        for keyword in keywords:
            if len(keyword) > 1:  # 忽略单字符
                role_management = RoleManagement.objects.filter(
                    display_name__icontains=keyword,
                    is_active=True
                ).first()
                if role_management:
                    return role_management
        
        return None
    
    def _create_default_role_management(self, role_code, role_name, dry_run=False):
        """创建默认的RoleManagement"""
        try:
            if dry_run:
                self.stdout.write(f'  [预览] 将创建默认RoleManagement: {role_name}')
                # 返回一个模拟对象用于预览
                class MockRoleManagement:
                    display_name = f'默认-{role_name}'
                return MockRoleManagement()
            
            # 检查是否已存在相同的role
            existing = RoleManagement.objects.filter(role=role_code).first()
            if existing:
                return existing
            
            role_management = RoleManagement.objects.create(
                role=role_code,
                display_name=f'默认-{role_name}',
                description=f'自动创建的默认角色管理: {role_name}',
                is_active=True,
                sort_order=999  # 默认排序靠后
            )
            
            self.stdout.write(f'  创建默认RoleManagement: {role_management.display_name}')
            return role_management
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  创建默认RoleManagement失败: {str(e)}'))
            return None