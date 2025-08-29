from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from typing import List, Dict, Optional, Tuple, Any
import logging

from apps.permissions.models import RoleManagement, RoleGroupMapping, GroupRoleIdentifier
from apps.permissions.models_optimized import PermissionSyncLog
from apps.accounts.models import UserRole

logger = logging.getLogger(__name__)


class GroupConsistencyChecker:
    """Django组与角色映射一致性检查器"""
    
    def __init__(self):
        self.issues = []
        self.stats = {
            'total_groups': 0,
            'role_linked_groups': 0,
            'orphaned_groups': 0,
            'missing_mappings': 0,
            'permission_mismatches': 0,
            'identifier_issues': 0
        }
    
    def check_all_consistency(self) -> Dict[str, Any]:
        """执行完整的一致性检查"""
        logger.info("开始执行Django组与角色映射一致性检查")
        
        self.issues = []
        self._reset_stats()
        
        # 检查各种一致性问题
        self._check_orphaned_groups()
        self._check_missing_mappings()
        self._check_identifier_consistency()
        self._check_permission_sync()
        
        # 生成检查报告
        report = {
            'timestamp': timezone.now(),
            'stats': self.stats,
            'issues': self.issues,
            'has_issues': len(self.issues) > 0
        }
        
        logger.info(f"一致性检查完成，发现 {len(self.issues)} 个问题")
        return report
    
    def _reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_groups': Group.objects.count(),
            'role_linked_groups': 0,
            'orphaned_groups': 0,
            'missing_mappings': 0,
            'permission_mismatches': 0,
            'identifier_issues': 0
        }
    
    def _check_orphaned_groups(self) -> List[Dict[str, Any]]:
        """检查孤立的Django组（没有对应角色映射的组）"""
        orphaned_issues = []
        
        # 获取所有已映射的组ID
        mapped_group_ids = set(
            RoleGroupMapping.objects.filter(is_active=True)
            .values_list('group_id', flat=True)
        )
        
        # 查找孤立组
        all_groups = Group.objects.all()
        for group in all_groups:
            if group.id not in mapped_group_ids:
                try:
                    identifier = GroupRoleIdentifier.objects.get(group=group)
                    if identifier.status != 'orphaned':
                        # 标记为孤立状态
                        identifier.mark_as_orphaned()
                        orphaned_issues.append({
                            'type': 'orphaned_group',
                            'group_id': group.id,
                            'group_name': group.name,
                            'description': f'组 "{group.name}" 没有对应的角色映射',
                            'auto_fixable': True
                        })
                        self.stats['orphaned_groups'] += 1
                except GroupRoleIdentifier.DoesNotExist:
                    # 创建标识符并标记为孤立
                    identifier = GroupRoleIdentifier.objects.create(
                        group=group,
                        status='orphaned',
                        sync_status='disabled'
                    )
                    orphaned_issues.append({
                        'type': 'orphaned_group',
                        'group_id': group.id,
                        'group_name': group.name,
                        'description': f'组 "{group.name}" 没有对应的角色映射和标识符',
                        'auto_fixable': True
                    })
                    self.stats['orphaned_groups'] += 1
        
        self.issues.extend(orphaned_issues)
        return orphaned_issues
    
    def _check_missing_mappings(self) -> List[Dict[str, Any]]:
        """检查缺失的角色映射"""
        missing_issues = []
        
        # 检查所有角色是否都有对应的组映射
        for role_mgmt in RoleManagement.objects.filter(is_active=True):
            try:
                mapping = RoleGroupMapping.objects.get(role=role_mgmt.role, is_active=True)
                # 检查组标识符
                try:
                    identifier = GroupRoleIdentifier.objects.get(group=mapping.group)
                    if identifier.role_identifier != role_mgmt.role:
                        identifier.mark_as_role_linked(role_mgmt.role)
                        self.stats['role_linked_groups'] += 1
                except GroupRoleIdentifier.DoesNotExist:
                    # 创建缺失的标识符
                    GroupRoleIdentifier.objects.create(
                        group=mapping.group,
                        status='role_linked',
                        role_identifier=role_mgmt.role,
                        sync_status='synced'
                    )
                    self.stats['role_linked_groups'] += 1
            except RoleGroupMapping.DoesNotExist:
                missing_issues.append({
                    'type': 'missing_mapping',
                    'role': role_mgmt.role,
                    'role_display': role_mgmt.display_name,
                    'description': f'角色 "{role_mgmt.display_name}" 缺少组映射',
                    'auto_fixable': True
                })
                self.stats['missing_mappings'] += 1
        
        self.issues.extend(missing_issues)
        return missing_issues
    
    def _check_identifier_consistency(self) -> List[Dict[str, Any]]:
        """检查组标识符一致性"""
        identifier_issues = []
        
        for mapping in RoleGroupMapping.objects.filter(is_active=True):
            try:
                identifier = GroupRoleIdentifier.objects.get(group=mapping.group)
                
                # 检查角色标识符是否一致
                if identifier.role_identifier != mapping.role:
                    identifier_issues.append({
                        'type': 'identifier_mismatch',
                        'mapping_id': mapping.id,
                        'group_name': mapping.group.name,
                        'expected_role': mapping.role,
                        'actual_role': identifier.role_identifier,
                        'description': f'组 "{mapping.group.name}" 的角色标识符不一致',
                        'auto_fixable': True
                    })
                    self.stats['identifier_issues'] += 1
                
                # 检查状态是否正确
                if identifier.status != 'role_linked':
                    identifier_issues.append({
                        'type': 'status_mismatch',
                        'mapping_id': mapping.id,
                        'group_name': mapping.group.name,
                        'expected_status': 'role_linked',
                        'actual_status': identifier.status,
                        'description': f'组 "{mapping.group.name}" 的状态标识不正确',
                        'auto_fixable': True
                    })
                    self.stats['identifier_issues'] += 1
                    
            except GroupRoleIdentifier.DoesNotExist:
                identifier_issues.append({
                    'type': 'missing_identifier',
                    'mapping_id': mapping.id,
                    'group_name': mapping.group.name,
                    'role': mapping.role,
                    'description': f'组 "{mapping.group.name}" 缺少角色标识符',
                    'auto_fixable': True
                })
                self.stats['identifier_issues'] += 1
        
        self.issues.extend(identifier_issues)
        return identifier_issues
    
    def _check_permission_sync(self) -> List[Dict[str, Any]]:
        """检查权限同步状态"""
        permission_issues = []
        
        for mapping in RoleGroupMapping.objects.filter(is_active=True):
            try:
                # 获取角色应有的权限
                expected_permissions = set()
                
                # 从RoleManagement获取权限
                try:
                    role_mgmt = RoleManagement.objects.get(role=mapping.role)
                    expected_permissions.update(role_mgmt.get_all_permissions())
                except RoleManagement.DoesNotExist:
                    # 如果是预定义角色，可能需要其他逻辑
                    pass
                
                # 获取组当前权限
                current_permissions = set(mapping.group.permissions.all())
                
                # 比较权限差异
                missing_permissions = expected_permissions - current_permissions
                extra_permissions = current_permissions - expected_permissions
                
                if missing_permissions or extra_permissions:
                    permission_issues.append({
                        'type': 'permission_mismatch',
                        'mapping_id': mapping.id,
                        'group_name': mapping.group.name,
                        'role': mapping.role,
                        'missing_permissions': [p.codename for p in missing_permissions],
                        'extra_permissions': [p.codename for p in extra_permissions],
                        'description': f'组 "{mapping.group.name}" 的权限与角色不同步',
                        'auto_fixable': True
                    })
                    self.stats['permission_mismatches'] += 1
                    
            except Exception as e:
                permission_issues.append({
                    'type': 'permission_check_error',
                    'mapping_id': mapping.id,
                    'group_name': mapping.group.name,
                    'error': str(e),
                    'description': f'检查组 "{mapping.group.name}" 权限时发生错误',
                    'auto_fixable': False
                })
        
        self.issues.extend(permission_issues)
        return permission_issues
    
    def auto_fix_issues(self, issue_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """自动修复检测到的问题"""
        if issue_types is None:
            issue_types = ['orphaned_group', 'missing_mapping', 'identifier_mismatch', 
                          'status_mismatch', 'missing_identifier', 'permission_mismatch']
        
        fixed_count = 0
        failed_count = 0
        fix_results = []
        
        with transaction.atomic():
            for issue in self.issues:
                if issue['type'] in issue_types and issue.get('auto_fixable', False):
                    try:
                        success = self._fix_single_issue(issue)
                        if success:
                            fixed_count += 1
                            fix_results.append({
                                'issue_type': issue['type'],
                                'description': issue['description'],
                                'status': 'fixed'
                            })
                        else:
                            failed_count += 1
                            fix_results.append({
                                'issue_type': issue['type'],
                                'description': issue['description'],
                                'status': 'failed'
                            })
                    except Exception as e:
                        failed_count += 1
                        fix_results.append({
                            'issue_type': issue['type'],
                            'description': issue['description'],
                            'status': 'error',
                            'error': str(e)
                        })
                        logger.error(f"修复问题失败: {e}")
        
        # 记录修复日志
        PermissionSyncLog.objects.create(
            sync_type='manual_sync',
            target_type='system',
            target_id='consistency_check',
            operation='sync',
            result=f'自动修复完成: 成功 {fixed_count} 个，失败 {failed_count} 个',
            is_success=failed_count == 0
        )
        
        return {
            'fixed_count': fixed_count,
            'failed_count': failed_count,
            'results': fix_results
        }
    
    def _fix_single_issue(self, issue: Dict[str, Any]) -> bool:
        """修复单个问题"""
        try:
            if issue['type'] == 'missing_mapping':
                return self._fix_missing_mapping(issue)
            elif issue['type'] == 'missing_identifier':
                return self._fix_missing_identifier(issue)
            elif issue['type'] == 'identifier_mismatch':
                return self._fix_identifier_mismatch(issue)
            elif issue['type'] == 'status_mismatch':
                return self._fix_status_mismatch(issue)
            elif issue['type'] == 'permission_mismatch':
                return self._fix_permission_mismatch(issue)
            else:
                return False
        except Exception as e:
            logger.error(f"修复问题 {issue['type']} 失败: {e}")
            return False
    
    def _fix_missing_mapping(self, issue: Dict[str, Any]) -> bool:
        """修复缺失的角色映射"""
        role = issue['role']
        group_name = f"role_{role}"
        
        # 创建或获取组
        group, created = Group.objects.get_or_create(name=group_name)
        
        # 创建映射
        mapping = RoleGroupMapping.objects.create(
            role=role,
            group=group,
            is_active=True
        )
        
        # 同步组标识符
        mapping.sync_group_identifier()
        
        return True
    
    def _fix_missing_identifier(self, issue: Dict[str, Any]) -> bool:
        """修复缺失的组标识符"""
        mapping = RoleGroupMapping.objects.get(id=issue['mapping_id'])
        
        GroupRoleIdentifier.objects.create(
            group=mapping.group,
            status='role_linked',
            role_identifier=mapping.role,
            sync_status='synced'
        )
        
        return True
    
    def _fix_identifier_mismatch(self, issue: Dict[str, Any]) -> bool:
        """修复角色标识符不匹配"""
        mapping = RoleGroupMapping.objects.get(id=issue['mapping_id'])
        identifier = GroupRoleIdentifier.objects.get(group=mapping.group)
        
        identifier.mark_as_role_linked(mapping.role)
        
        return True
    
    def _fix_status_mismatch(self, issue: Dict[str, Any]) -> bool:
        """修复状态不匹配"""
        mapping = RoleGroupMapping.objects.get(id=issue['mapping_id'])
        identifier = GroupRoleIdentifier.objects.get(group=mapping.group)
        
        identifier.status = 'role_linked'
        identifier.save()
        
        return True
    
    def _fix_permission_mismatch(self, issue: Dict[str, Any]) -> bool:
        """修复权限不匹配"""
        mapping = RoleGroupMapping.objects.get(id=issue['mapping_id'])
        
        try:
            role_mgmt = RoleManagement.objects.get(role=mapping.role)
            expected_permissions = role_mgmt.get_all_permissions()
            
            # 同步权限
            mapping.group.permissions.set(expected_permissions)
            
            return True
        except RoleManagement.DoesNotExist:
            return False