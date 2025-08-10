from django.core.management.base import BaseCommand
from apps.permissions.models import RoleManagement
from apps.accounts.models import UserRole
from django.db import transaction


class Command(BaseCommand):
    help = '设置角色继承层级关系'
    
    def handle(self, *args, **options):
        """设置角色继承关系"""
        
        # 如果指定了reset参数，先重置继承关系
        if options.get('reset'):
            self.reset_hierarchy()
            return
        
        with transaction.atomic():
            try:
                # 获取所有角色
                admin_role = RoleManagement.objects.get(role=UserRole.ADMIN)
                teacher_role = RoleManagement.objects.get(role=UserRole.TEACHER)
                parent_role = RoleManagement.objects.get(role=UserRole.PARENT)
                student_role = RoleManagement.objects.get(role=UserRole.STUDENT)
                
                # 设置继承关系：管理员 -> 教师 -> 家长 -> 学生
                # 管理员是根角色，不设置父角色
                admin_role.parent = None
                admin_role.save()
                self.stdout.write(f"✅ 设置 {admin_role.display_name} 为根角色")
                
                # 教师继承管理员权限
                teacher_role.parent = admin_role
                teacher_role.save()
                self.stdout.write(f"✅ 设置 {teacher_role.display_name} 继承 {admin_role.display_name}")
                
                # 家长继承教师权限（部分）
                parent_role.parent = teacher_role
                parent_role.save()
                self.stdout.write(f"✅ 设置 {parent_role.display_name} 继承 {teacher_role.display_name}")
                
                # 学生继承家长权限（基础权限）
                student_role.parent = parent_role
                student_role.save()
                self.stdout.write(f"✅ 设置 {student_role.display_name} 继承 {parent_role.display_name}")
                
                # 显示继承层级
                self.stdout.write("\n📊 角色继承层级：")
                for role in [admin_role, teacher_role, parent_role, student_role]:
                    level = role.get_hierarchy_level()
                    indent = "  " * level
                    direct_perms = role.permissions.count()
                    total_perms = len(role.get_all_permissions())
                    inherited_perms = total_perms - direct_perms
                    
                    self.stdout.write(
                        f"{indent}📁 {role.display_name} (层级: {level}, "
                        f"直接权限: {direct_perms}, 继承权限: {inherited_perms}, 总权限: {total_perms})"
                    )
                
                # 同步权限到Django组
                from apps.permissions.utils import PermissionUtils
                
                self.stdout.write("\n🔄 同步权限到Django组...")
                for role in [admin_role, teacher_role, parent_role, student_role]:
                    success = PermissionUtils.sync_role_permissions(role)
                    status = "成功" if success else "失败"
                    self.stdout.write(f"  {role.display_name}: {status}")
                
                self.stdout.write("\n🎉 角色继承层级设置完成！")
                
            except RoleManagement.DoesNotExist as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ 角色不存在: {e}")
                )
                self.stdout.write(
                    self.style.WARNING("请先运行 'python manage.py create_default_roles' 创建默认角色")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ 设置角色继承时发生错误: {e}")
                )
                raise
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有角色的继承关系',
        )
    
    def reset_hierarchy(self):
        """重置角色继承关系"""
        self.stdout.write("🔄 重置角色继承关系...")
        
        roles = RoleManagement.objects.all()
        for role in roles:
            role.parent = None
            role.save()
            self.stdout.write(f"  ✅ 重置 {role.display_name}")
        
        self.stdout.write("✅ 角色继承关系已重置")