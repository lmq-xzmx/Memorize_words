from django.core.management.base import BaseCommand
from apps.permissions.models import RoleManagement, MenuModuleConfig
from apps.accounts.models import CustomUser, UserRole
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '基础权限检查命令'

    def handle(self, *args, **options):
        self.stdout.write('开始权限检查...')
        
        # 执行权限检查
        issues = self.check_permissions()
        
        # 统计问题
        total_issues = sum(len(category_issues) for category_issues in issues.values())
        
        if total_issues == 0:
            self.stdout.write('✓ 权限检查通过，未发现问题')
            return
        
        self.stdout.write(f'发现 {total_issues} 个权限问题')
        
        # 显示问题详情
        for category, category_issues in issues.items():
            if category_issues:
                self.stdout.write(f'  {category}: {len(category_issues)} 个问题')
        
        self.stdout.write('权限检查完成')

    def check_permissions(self):
        """检查权限问题"""
        issues = {
            'missing_admin_permissions': [],
            'orphaned_permissions': [],
            'user_role_mismatches': [],
            'inactive_menu_permissions': []
        }
        
        # 检查管理员缺失的权限
        self.check_admin_missing_permissions(issues)
        
        # 检查孤立权限
        self.check_orphaned_permissions(issues)
        
        # 检查用户角色不匹配
        self.check_user_role_mismatches(issues)
        
        # 检查非活跃菜单权限
        self.check_inactive_menu_permissions(issues)
        
        return issues

    def check_admin_missing_permissions(self, issues):
        """检查管理员缺失的权限"""
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        pass

    def check_orphaned_permissions(self, issues):
        """检查孤立权限"""
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        pass

    def check_user_role_mismatches(self, issues):
        """检查用户角色不匹配"""
        users = CustomUser.objects.all()
        
        for user in users:
            # 检查用户组分配是否与角色一致
            user_groups = user.groups.all()
            expected_group_name = f'{user.role}_group'
            
            has_correct_group = any(group.name == expected_group_name for group in user_groups)
            
            if user_groups.exists() and not has_correct_group:
                issues['user_role_mismatches'].append({
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'groups': [group.name for group in user_groups],
                    'expected_group': expected_group_name,
                    'message': f'用户 {user.username} 的组分配与角色不匹配'
                })

    def check_inactive_menu_permissions(self, issues):
        """检查非活跃菜单权限"""
        # RoleMenuPermission 已被废弃，此功能暂时跳过
        pass