from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.models import Permission
from typing import List, Dict, Optional, Set
from .models import RoleMapping, RoleManagement
from apps.accounts.models import UserRole, CustomUser
import logging

logger = logging.getLogger(__name__)


class RoleMappingService:
    """角色映射服务类，提供角色映射的业务逻辑"""
    
    @staticmethod
    def create_mapping(user_role: str, role_management_id: int, 
                      description: str = '', auto_sync: bool = True) -> RoleMapping:
        """创建角色映射关系"""
        try:
            # 验证user_role是否有效
            valid_roles = [choice[0] for choice in UserRole.choices]
            if user_role not in valid_roles:
                raise ValidationError(f'无效的用户角色: {user_role}')
            
            # 验证role_management是否存在
            role_management = RoleManagement.objects.get(id=role_management_id)
            
            # 检查是否已存在映射
            if RoleMapping.objects.filter(user_role=user_role).exists():
                raise ValidationError(f'角色 {user_role} 已存在映射关系')
            
            # 创建映射
            mapping = RoleMapping.objects.create(
                user_role=user_role,
                role_management=role_management,
                description=description,
                auto_sync=auto_sync
            )
            
            logger.info(f'创建角色映射: {user_role} -> {role_management.display_name}')
            return mapping
            
        except RoleManagement.DoesNotExist:
            raise ValidationError(f'角色管理ID {role_management_id} 不存在')
        except Exception as e:
            logger.error(f'创建角色映射失败: {str(e)}')
            raise
    
    @staticmethod
    def get_mapping_by_user_role(user_role: str) -> Optional[RoleMapping]:
        """根据用户角色获取映射关系"""
        try:
            return RoleMapping.objects.select_related('role_management').get(
                user_role=user_role,
                is_active=True
            )
        except RoleMapping.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_permissions(user: CustomUser) -> Set[str]:
        """获取用户的所有权限（通过映射机制）"""
        permissions = set()
        
        try:
            # 获取用户角色对应的映射
            mapping = RoleMappingService.get_mapping_by_user_role(user.role)
            
            if mapping and mapping.role_management:
                # 获取角色管理中的权限
                role_permissions = mapping.role_management.get_all_permissions()
                permissions.update([perm.codename for perm in role_permissions])
                
                logger.debug(f'用户 {user.username} 通过映射获取权限: {len(permissions)} 个')
            else:
                logger.warning(f'用户 {user.username} 的角色 {user.role} 未找到映射关系')
                
        except Exception as e:
            logger.error(f'获取用户权限失败: {str(e)}')
            
        return permissions
    
    @staticmethod
    def sync_role_permissions(user_role: str) -> bool:
        """同步角色权限（当RoleManagement权限变更时）"""
        try:
            mapping = RoleMappingService.get_mapping_by_user_role(user_role)
            
            if not mapping or not mapping.auto_sync:
                return False
            
            # 获取该角色的所有用户
            users = CustomUser.objects.filter(role=user_role)
            
            # 这里可以添加具体的权限同步逻辑
            # 例如：清除用户缓存、发送权限变更通知等
            
            logger.info(f'同步角色 {user_role} 的权限，影响用户数: {users.count()}')
            return True
            
        except Exception as e:
            logger.error(f'同步角色权限失败: {str(e)}')
            return False
    
    @staticmethod
    def update_mapping(user_role: str, **kwargs) -> bool:
        """更新角色映射关系"""
        try:
            mapping = RoleMapping.objects.get(user_role=user_role)
            
            # 更新允许的字段
            allowed_fields = ['role_management', 'is_active', 'auto_sync', 'description']
            updated = False
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(mapping, field):
                    setattr(mapping, field, value)
                    updated = True
            
            if updated:
                mapping.save()
                logger.info(f'更新角色映射: {user_role}')
                
                # 如果启用了自动同步，触发权限同步
                if mapping.auto_sync:
                    RoleMappingService.sync_role_permissions(user_role)
            
            return updated
            
        except RoleMapping.DoesNotExist:
            logger.error(f'角色映射不存在: {user_role}')
            return False
        except Exception as e:
            logger.error(f'更新角色映射失败: {str(e)}')
            return False
    
    @staticmethod
    def delete_mapping(user_role: str) -> bool:
        """删除角色映射关系"""
        try:
            mapping = RoleMapping.objects.get(user_role=user_role)
            mapping.delete()
            
            logger.info(f'删除角色映射: {user_role}')
            return True
            
        except RoleMapping.DoesNotExist:
            logger.error(f'角色映射不存在: {user_role}')
            return False
        except Exception as e:
            logger.error(f'删除角色映射失败: {str(e)}')
            return False
    
    @staticmethod
    def get_all_mappings() -> List[RoleMapping]:
        """获取所有角色映射关系"""
        return RoleMapping.objects.select_related('role_management').all()
    
    @staticmethod
    def get_active_mappings() -> List[RoleMapping]:
        """获取所有启用的角色映射关系"""
        return RoleMapping.objects.select_related('role_management').filter(is_active=True)
    
    @staticmethod
    def initialize_default_mappings() -> Dict[str, bool]:
        """初始化默认的角色映射关系"""
        results = {}
        
        try:
            # 获取所有UserRole选择项
            user_roles = [choice[0] for choice in UserRole.choices]
            
            for role in user_roles:
                try:
                    # 检查是否已存在映射
                    if RoleMapping.objects.filter(user_role=role).exists():
                        results[role] = True  # 已存在
                        continue
                    
                    # 尝试找到对应的RoleManagement
                    # 这里可以根据实际业务逻辑来匹配
                    role_management = None
                    
                    # 示例：根据角色名称匹配
                    role_display = dict(UserRole.choices).get(role, role)
                    try:
                        role_management = RoleManagement.objects.filter(
                            display_name__icontains=role_display
                        ).first()
                    except:
                        pass
                    
                    if role_management:
                        RoleMapping.objects.create(
                            user_role=role,
                            role_management=role_management,
                            description=f'系统自动创建的 {role_display} 角色映射',
                            auto_sync=True
                        )
                        results[role] = True
                        logger.info(f'创建默认映射: {role} -> {role_management.display_name}')
                    else:
                        results[role] = False
                        logger.warning(f'未找到角色 {role} 对应的RoleManagement')
                        
                except Exception as e:
                    results[role] = False
                    logger.error(f'初始化角色 {role} 映射失败: {str(e)}')
            
        except Exception as e:
            logger.error(f'初始化默认映射失败: {str(e)}')
        
        return results
    
    @staticmethod
    def validate_mapping_consistency() -> Dict[str, List[str]]:
        """验证映射关系的一致性"""
        issues = {
            'missing_mappings': [],
            'invalid_roles': [],
            'inactive_role_management': []
        }
        
        try:
            # 检查是否有UserRole没有对应的映射
            user_roles = [choice[0] for choice in UserRole.choices]
            existing_mappings = set(RoleMapping.objects.values_list('user_role', flat=True))
            
            for role in user_roles:
                if role not in existing_mappings:
                    issues['missing_mappings'].append(role)
            
            # 检查是否有映射指向无效的角色
            all_mappings = RoleMapping.objects.all()
            for mapping in all_mappings:
                if mapping.user_role not in user_roles:
                    issues['invalid_roles'].append(mapping.user_role)
                
                # 检查关联的RoleManagement是否启用
                if not mapping.role_management.is_active:
                    issues['inactive_role_management'].append(mapping.user_role)
        
        except Exception as e:
            logger.error(f'验证映射一致性失败: {str(e)}')
        
        return issues