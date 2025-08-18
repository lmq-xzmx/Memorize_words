from django.db import transaction
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from apps.accounts.models import CustomUser, UserRole, RoleTemplate, RoleExtension, UserExtensionData
from apps.permissions.models import RoleManagement, RoleGroupMapping
from typing import Dict, List, Any, Optional
import json


class RegistrationService:
    """用户注册自动分配服务"""
    
    @classmethod
    def get_role_registration_form_fields(cls, role: str) -> List[Dict[str, Any]]:
        """获取角色注册表单字段配置"""
        try:
            # 获取角色模板
            role_template = RoleTemplate.objects.get(role=role, is_active=True)
            
            # 获取角色增项字段
            extensions = RoleExtension.objects.filter(
                role_template=role_template,
                is_active=True,
                show_in_frontend_register=True
            ).order_by('sort_order', 'field_name')
            
            form_fields = []
            for extension in extensions:
                field_config = {
                    'field_name': extension.field_name,
                    'field_label': extension.field_label,
                    'field_type': extension.field_type,
                    'is_required': extension.is_required,
                    'help_text': extension.help_text,
                    'default_value': extension.default_value,
                    'validation_rules': extension.get_validation_rules(),
                }
                
                # 如果是选择字段，添加选择项
                if extension.field_type == 'choice':
                    field_config['choices'] = extension.get_choices_list()
                
                form_fields.append(field_config)
            
            return form_fields
            
        except RoleTemplate.DoesNotExist:
            return []
    
    @classmethod
    def validate_registration_data(cls, role: str, extension_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证注册数据"""
        errors = {}
        
        try:
            role_template = RoleTemplate.objects.get(role=role, is_active=True)
            extensions = RoleExtension.objects.filter(
                role_template=role_template,
                is_active=True,
                show_in_frontend_register=True
            )
            
            for extension in extensions:
                field_name = extension.field_name
                field_value = extension_data.get(field_name, '')
                field_errors = []
                
                # 必填字段验证
                if extension.is_required and not field_value:
                    field_errors.append(f'{extension.field_label}为必填字段')
                
                # 字段类型验证
                if field_value:
                    field_errors.extend(cls._validate_field_value(extension, field_value))
                
                if field_errors:
                    errors[field_name] = field_errors
            
        except RoleTemplate.DoesNotExist:
            errors['role'] = ['无效的角色类型']
        
        return errors
    
    @classmethod
    def _validate_field_value(cls, extension: RoleExtension, value: str) -> List[str]:
        """验证字段值"""
        errors = []
        
        # 数字字段验证
        if extension.field_type == 'number':
            try:
                float(value)
            except ValueError:
                errors.append(f'{extension.field_label}必须是有效的数字')
        
        # 邮箱字段验证
        elif extension.field_type == 'email':
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                errors.append(f'{extension.field_label}必须是有效的邮箱地址')
        
        # 电话字段验证
        elif extension.field_type == 'phone':
            import re
            phone_pattern = r'^[\d\-\+\(\)\s]+$'
            if not re.match(phone_pattern, value):
                errors.append(f'{extension.field_label}必须是有效的电话号码')
        
        # URL字段验证
        elif extension.field_type == 'url':
            import re
            url_pattern = r'^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$'
            if not re.match(url_pattern, value):
                errors.append(f'{extension.field_label}必须是有效的URL地址')
        
        # 选择字段验证
        elif extension.field_type == 'choice':
            valid_choices = [choice[0] for choice in extension.get_choices_list()]
            if value not in valid_choices:
                errors.append(f'{extension.field_label}的值无效')
        
        # 自定义验证规则
        validation_rules = extension.get_validation_rules()
        if validation_rules:
            # 长度验证
            if 'min_length' in validation_rules and len(value) < validation_rules['min_length']:
                errors.append(f'{extension.field_label}长度不能少于{validation_rules["min_length"]}个字符')
            
            if 'max_length' in validation_rules and len(value) > validation_rules['max_length']:
                errors.append(f'{extension.field_label}长度不能超过{validation_rules["max_length"]}个字符')
            
            # 正则表达式验证
            if 'pattern' in validation_rules:
                import re
                if not re.match(validation_rules['pattern'], value):
                    error_msg = validation_rules.get('pattern_error', f'{extension.field_label}格式不正确')
                    errors.append(error_msg)
        
        return errors
    
    @classmethod
    def create_user_with_role_assignment(cls, user_data: Dict[str, Any], role: str, extension_data: Dict[str, Any]) -> CustomUser:
        """创建用户并自动分配角色权限"""
        with transaction.atomic():
            # 1. 验证注册数据
            validation_errors = cls.validate_registration_data(role, extension_data)
            if validation_errors:
                raise ValidationError(validation_errors)
            
            # 2. 创建用户
            user = CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data.get('email', ''),
                password=user_data['password'],
                role=role,
                phone=user_data.get('phone', ''),
                real_name=user_data.get('real_name', ''),
                nickname=user_data.get('nickname', ''),
                notes=user_data.get('notes', ''),
                grade_level=user_data.get('grade_level', ''),
                english_level=user_data.get('english_level', ''),
            )
            
            # 3. 保存角色增项数据
            cls._save_user_extension_data(user, role, extension_data)
            
            # 4. 自动分配角色权限
            cls._assign_role_permissions(user, role)
            
            # 5. 自动分配到角色组
            cls._assign_user_to_role_group(user, role)
            
            return user
    
    @classmethod
    def _save_user_extension_data(cls, user: CustomUser, role: str, extension_data: Dict[str, Any]):
        """保存用户角色增项数据"""
        try:
            role_template = RoleTemplate.objects.get(role=role, is_active=True)
            extensions = RoleExtension.objects.filter(
                role_template=role_template,
                is_active=True
            )
            
            for extension in extensions:
                field_name = extension.field_name
                field_value = extension_data.get(field_name, extension.default_value)
                
                if field_value:
                    UserExtensionData.objects.create(
                        user=user,
                        role_extension=extension,
                        field_value=str(field_value)
                    )
        
        except RoleTemplate.DoesNotExist:
            pass
    
    @classmethod
    def _assign_role_permissions(cls, user: CustomUser, role: str):
        """自动分配角色权限"""
        try:
            # 获取角色管理配置
            role_mgmt = RoleManagement.objects.get(role=role, is_active=True)
            
            # 获取所有权限（包括继承的权限）
            permissions = role_mgmt.get_all_permissions()
            
            # 为用户分配权限
            user.user_permissions.set(permissions)
            
        except RoleManagement.DoesNotExist:
            pass
    
    @classmethod
    def _assign_user_to_role_group(cls, user: CustomUser, role: str):
        """自动分配用户到角色组"""
        try:
            # 获取角色组映射
            role_mapping = RoleGroupMapping.objects.get(role=role, auto_sync=True)
            
            # 将用户添加到对应的Django组
            user.groups.add(role_mapping.group)
            
        except RoleGroupMapping.DoesNotExist:
            pass
    
    @classmethod
    def update_user_role_assignment(cls, user: CustomUser, new_role: str, extension_data: Optional[Dict[str, Any]] = None):
        """更新用户角色分配"""
        with transaction.atomic():
            old_role = user.role
            
            # 1. 验证新角色数据
            if extension_data:
                validation_errors = cls.validate_registration_data(new_role, extension_data)
                if validation_errors:
                    raise ValidationError(validation_errors)
            
            # 2. 更新用户角色
            user.role = new_role
            user.save()
            
            # 3. 清除旧的角色增项数据
            cls._clear_user_extension_data(user, old_role)
            
            # 4. 保存新的角色增项数据
            if extension_data:
                cls._save_user_extension_data(user, new_role, extension_data)
            
            # 5. 重新分配角色权限
            cls._reassign_role_permissions(user, old_role, new_role)
            
            # 6. 重新分配角色组
            cls._reassign_user_role_group(user, old_role, new_role)
    
    @classmethod
    def _clear_user_extension_data(cls, user: CustomUser, role: str):
        """清除用户角色增项数据"""
        try:
            role_template = RoleTemplate.objects.get(role=role, is_active=True)
            extensions = RoleExtension.objects.filter(role_template=role_template)
            
            UserExtensionData.objects.filter(
                user=user,
                role_extension__in=extensions
            ).delete()
            
        except RoleTemplate.DoesNotExist:
            pass
    
    @classmethod
    def _reassign_role_permissions(cls, user: CustomUser, old_role: str, new_role: str):
        """重新分配角色权限"""
        # 清除旧权限
        user.user_permissions.clear()
        
        # 分配新权限
        cls._assign_role_permissions(user, new_role)
    
    @classmethod
    def _reassign_user_role_group(cls, user: CustomUser, old_role: str, new_role: str):
        """重新分配用户角色组"""
        # 从旧角色组中移除
        try:
            old_mapping = RoleGroupMapping.objects.get(role=old_role, auto_sync=True)
            user.groups.remove(old_mapping.group)
        except RoleGroupMapping.DoesNotExist:
            pass
        
        # 添加到新角色组
        cls._assign_user_to_role_group(user, new_role)
    
    @classmethod
    def get_user_extension_data(cls, user: CustomUser) -> Dict[str, Any]:
        """获取用户角色增项数据"""
        extension_data = {}
        
        user_extensions = UserExtensionData.objects.filter(user=user).select_related('role_extension')
        
        for user_ext in user_extensions:
            field_name = user_ext.role_extension.field_name
            field_value = user_ext.field_value
            
            # 根据字段类型转换值
            if user_ext.role_extension.field_type == 'boolean':
                field_value = field_value.lower() in ('true', '1', 'yes')
            elif user_ext.role_extension.field_type == 'number':
                try:
                    field_value = float(field_value) if '.' in field_value else int(field_value)
                except ValueError:
                    pass
            
            extension_data[field_name] = field_value
        
        return extension_data
    
    @classmethod
    def get_available_roles_for_registration(cls) -> List[Dict[str, Any]]:
        """获取可用于注册的角色列表"""
        available_roles = []
        
        # 获取所有启用的角色模板
        role_templates = RoleTemplate.objects.filter(is_active=True).order_by('role')
        
        for template in role_templates:
            role_info = {
                'role': template.role,
                'display_name': template.template_name,
                'description': template.description,
                'field_count': template.get_field_count(),
                'has_approval': template.role in [UserRole.ADMIN, UserRole.DEAN],  # 需要审批的角色
            }
            available_roles.append(role_info)
        
        return available_roles