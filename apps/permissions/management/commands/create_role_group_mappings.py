from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.permissions.models import RoleGroupMapping
from apps.accounts.models import UserRole
from django.db import transaction
from apps.accounts.services.role_service import RoleService


class Command(BaseCommand):
    help = '创建缺失的角色组映射'
    
    def handle(self, *args, **options):
        """创建角色组映射"""
        
        self.stdout.write("🔧 创建角色组映射...")
        
        # 角色到组名的映射
        role_group_mapping = {
            UserRole.ADMIN: '管理员组',
            UserRole.TEACHER: '自由老师',
            UserRole.PARENT: '家长组',
            UserRole.STUDENT: '学生组',
        }
        
        with transaction.atomic():
            for role, group_name in role_group_mapping.items():
                try:
                    # 创建或获取Django组
                    group, group_created = Group.objects.get_or_create(name=group_name)
                    group_status = "新建" if group_created else "已存在"
                    self.stdout.write(f"  📁 Django组 '{group_name}': {group_status}")
                    
                    # 创建或获取角色组映射
                    mapping, mapping_created = RoleGroupMapping.objects.get_or_create(
                        role=role,
                        defaults={
                            'group': group,
                            'auto_sync': True
                        }
                    )
                    
                    if mapping_created:
                        role_display = dict(RoleService.get_role_choices(include_empty=False)).get(role, role)
                        self.stdout.write(
                            f"  ✅ 创建角色映射: {role_display} -> {group_name}"
                        )
                    else:
                        # 如果映射已存在但组不同，更新映射
                        if mapping.group != group:
                            old_group = mapping.group.name
                            mapping.group = group
                            mapping.save()
                            role_display = dict(RoleService.get_role_choices(include_empty=False)).get(role, role)
                            self.stdout.write(
                                f"  🔄 更新角色映射: {role_display} {old_group} -> {group_name}"
                            )
                        else:
                            role_display = dict(RoleService.get_role_choices(include_empty=False)).get(role, role)
                            self.stdout.write(
                                f"  ℹ️  角色映射已存在: {role_display} -> {group_name}"
                            )
                            
                except Exception as e:
                    role_display = dict(RoleService.get_role_choices(include_empty=False)).get(role, role)
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ❌ 创建 {role_display} 映射失败: {e}"
                        )
                    )
        
        # 验证映射完整性
        self.stdout.write("\n🔍 验证映射完整性...")
        existing_roles = set(RoleGroupMapping.objects.values_list('role', flat=True))
        all_roles = set([choice[0] for choice in RoleService.get_role_choices(include_empty=False)])
        missing_roles = all_roles - existing_roles
        
        if missing_roles:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠️  仍有缺失的角色映射: {', '.join(missing_roles)}"
                )
            )
        else:
            self.stdout.write("  ✅ 所有角色都有对应的组映射")
        
        self.stdout.write("\n🎉 角色组映射创建完成！")
        
        # 显示最终状态
        self.stdout.write("\n📊 最终映射状态:")
        for mapping in RoleGroupMapping.objects.all().order_by('role'):
            status = "🟢 活跃" if mapping.auto_sync else "🔴 非活跃"
            self.stdout.write(
                f"  {mapping.get_role_display()} -> {mapping.group.name} ({status})"
            )