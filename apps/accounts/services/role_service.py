from django.core.cache import cache
from django.db.models import Q
from typing import List, Dict, Tuple, Optional
from apps.accounts.models import UserRole
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

# 动态导入，避免循环导入
try:
    from apps.permissions.models import RoleManagement
except ImportError:
    RoleManagement = None

# RoleExtension在同一个app中，使用字符串引用避免循环导入


class RoleService:
    """统一的角色数据服务"""
    
    CACHE_KEY_ALL_ROLES = 'role_service:all_roles'
    CACHE_KEY_ROLE_CHOICES = 'role_service:role_choices'
    CACHE_KEY_ROLE_HIERARCHY = 'role_service:role_hierarchy'
    CACHE_TIMEOUT = 300  # 5分钟缓存
    
    @classmethod
    def get_all_roles(cls, include_inactive: bool = False) -> List[Dict]:
        """获取所有角色的统一接口"""
        cache_key = f"{cls.CACHE_KEY_ALL_ROLES}:{include_inactive}"
        roles = cache.get(cache_key)
        
        if roles is None:
            roles = []
            
            # 1. 添加预定义角色
            predefined_roles = {choice[0]: choice[1] for choice in UserRole.choices}
            
            # 2. 获取角色管理数据
            role_management_data = []
            if RoleManagement and hasattr(RoleManagement, 'objects'):
                try:
                    queryset = RoleManagement.objects.all()
                    if not include_inactive:
                        queryset = queryset.filter(is_active=True)
                    
                    role_management_data = list(queryset.values(
                        'role', 'display_name', 'description', 'is_active', 'sort_order'
                    ))
                except Exception as e:
                    logger.error(f"获取角色管理数据失败: {e}")
                    role_management_data = []
            
            # 3. 合并角色数据
            processed_roles = set()
            
            for rm_data in role_management_data:
                role_code = rm_data['role']
                if role_code and role_code not in processed_roles:
                    roles.append({
                        'code': role_code,
                        'display_name': rm_data['display_name'] or predefined_roles.get(role_code, role_code),
                        'description': rm_data['description'] or '',
                        'is_predefined': role_code in predefined_roles,
                        'is_active': rm_data['is_active'],
                        'sort_order': rm_data['sort_order'] or 999
                    })
                    processed_roles.add(role_code)
            
            # 4. 添加未在角色管理中的预定义角色
            for role_code, role_name in UserRole.choices:
                if role_code not in processed_roles:
                    roles.append({
                        'code': role_code,
                        'display_name': role_name,
                        'description': f'系统预定义角色：{role_name}',
                        'is_predefined': True,
                        'is_active': True,
                        'sort_order': 0
                    })
            
            # 5. 排序
            roles.sort(key=lambda x: (x['sort_order'], x['code']))
            
            cache.set(cache_key, roles, cls.CACHE_TIMEOUT)
        
        return roles
    
    @classmethod
    def get_role_choices(cls, include_inactive: bool = False, include_empty: bool = True) -> List[Tuple[str, str]]:
        """获取角色选择项的统一接口"""
        cache_key = f"{cls.CACHE_KEY_ROLE_CHOICES}:{include_inactive}:{include_empty}"
        choices = cache.get(cache_key)
        
        if choices is None:
            choices = []
            
            if include_empty:
                choices.append(('', '---------'))  # 空选项
            
            roles = cls.get_all_roles(include_inactive=include_inactive)
            for role in roles:
                if include_inactive or role['is_active']:
                    choices.append((role['code'], role['display_name']))
            
            cache.set(cache_key, choices, cls.CACHE_TIMEOUT)
        
        return choices
    
    @classmethod
    def get_role_hierarchy(cls) -> Dict[str, List[str]]:
        """获取角色层级关系"""
        hierarchy = cache.get(cls.CACHE_KEY_ROLE_HIERARCHY)
        
        if hierarchy is None:
            hierarchy = {}
            
            # 从RoleManagement获取父子关系（暂时禁用以避免异步上下文问题）
            # TODO: 重新启用RoleManagement层级查询，需要解决异步上下文问题
            # 使用默认层级结构
            hierarchy = cls._get_default_hierarchy()
            
            cache.set(cls.CACHE_KEY_ROLE_HIERARCHY, hierarchy, cls.CACHE_TIMEOUT)
        
        return hierarchy
    
    @classmethod
    def _get_default_hierarchy(cls) -> Dict[str, List[str]]:
        """获取默认角色层级关系"""
        return {
            'super_admin': ['admin', 'teacher', 'student', 'parent'],
            'admin': ['teacher', 'student', 'parent'],
            'teacher': ['student'],
        }
    
    @classmethod
    def get_role_info(cls, role_code: str) -> Optional[Dict]:
        """获取单个角色的详细信息"""
        roles = cls.get_all_roles(include_inactive=True)
        for role in roles:
            if role['code'] == role_code:
                return role
        return None
    
    @classmethod
    def clear_cache(cls):
        """清除角色相关缓存"""
        cache.delete_many([
            f"{cls.CACHE_KEY_ALL_ROLES}:True",
            f"{cls.CACHE_KEY_ALL_ROLES}:False",
            f"{cls.CACHE_KEY_ROLE_CHOICES}:True:True",
            f"{cls.CACHE_KEY_ROLE_CHOICES}:True:False",
            f"{cls.CACHE_KEY_ROLE_CHOICES}:False:True",
            f"{cls.CACHE_KEY_ROLE_CHOICES}:False:False",
            cls.CACHE_KEY_ROLE_HIERARCHY
        ])
    
    @classmethod
    def refresh_cache(cls):
        """刷新角色缓存"""
        cls.clear_cache()
        # 预热缓存
        cls.get_all_roles(include_inactive=False)
        cls.get_all_roles(include_inactive=True)
        cls.get_role_choices(include_inactive=False, include_empty=True)
        cls.get_role_choices(include_inactive=False, include_empty=False)
        cls.get_role_choices(include_inactive=True, include_empty=True)
        cls.get_role_choices(include_inactive=True, include_empty=False)
        cls.get_role_hierarchy()
        print("角色缓存已刷新")
    
    @classmethod
    def validate_role(cls, role_code: str, include_inactive: bool = False) -> bool:
        """验证角色代码是否有效"""
        if not role_code:
            return False
        
        role_info = cls.get_role_info(role_code)
        if not role_info:
            return False
        
        if not include_inactive and not role_info['is_active']:
            return False
        
        return True
    
    @classmethod
    def get_role_display_name(cls, role_code: str) -> str:
        """获取角色显示名称"""
        role_info = cls.get_role_info(role_code)
        if role_info:
            return role_info['display_name']
        return role_code or '未知角色'
    
    @classmethod
    def get_role_fields(cls, role_code: str) -> List[Dict]:
        """获取角色字段配置 - 从数据库获取角色增项"""
        try:
            # 使用Django的apps.get_model来避免循环导入
            from django.apps import apps
            RoleExtension = apps.get_model('accounts', 'RoleExtension')
            
            # 获取角色增项字段
            extensions = RoleExtension.objects.filter(
                role=role_code,
                is_active=True,
                show_in_frontend_register=True
            ).order_by('sort_order', 'field_name')
            
            fields = []
            for extension in extensions:
                field_config = {
                    'name': extension.field_name,
                    'label': extension.field_label,
                    'type': extension.field_type,
                    'required': extension.is_required,
                    'placeholder': extension.help_text or f'请输入{extension.field_label}'
                }
                
                # 如果是选择字段，添加选择项
                if extension.field_type == 'choice':
                    try:
                        choices = extension.get_choices_list()
                        field_config['options'] = [
                            {'value': choice[0], 'label': choice[1]} 
                            for choice in choices
                        ]
                    except Exception:
                        field_config['options'] = []
                
                # 添加验证规则
                if hasattr(extension, 'get_validation_rules'):
                    validation_rules = extension.get_validation_rules()
                    if validation_rules:
                        field_config['validation'] = validation_rules
                
                fields.append(field_config)
            
            return fields
            
        except Exception as e:
            # 如果获取失败，返回空列表并记录错误
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取角色 {role_code} 的字段配置失败: {str(e)}")
            return []