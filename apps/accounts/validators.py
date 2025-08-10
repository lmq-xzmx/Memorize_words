from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re


class EnhancedUserValidator:
    """
    增强的用户数据验证器
    提供更严格的用户数据验证规则
    """
    
    @staticmethod
    def validate_username(username):
        """
        验证用户名
        - 长度3-20字符
        - 只能包含字母、数字、下划线
        - 不能以数字开头
        """
        if not username:
            raise ValidationError(_('用户名不能为空'))
        
        if len(username) < 3 or len(username) > 20:
            raise ValidationError(_('用户名长度必须在3-20字符之间'))
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
            raise ValidationError(_('用户名只能包含字母、数字、下划线，且不能以数字开头'))
        
        # 检查保留用户名
        reserved_names = ['admin', 'root', 'system', 'test', 'guest']
        if username.lower() in reserved_names:
            raise ValidationError(_('该用户名为系统保留，请选择其他用户名'))
    
    @staticmethod
    def validate_real_name(real_name):
        """
        验证真实姓名
        - 长度2-10字符
        - 只能包含中文、英文字母
        """
        if not real_name:
            return  # 真实姓名可以为空
        
        if len(real_name) < 2 or len(real_name) > 10:
            raise ValidationError(_('真实姓名长度必须在2-10字符之间'))
        
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s]+$', real_name):
            raise ValidationError(_('真实姓名只能包含中文、英文字母和空格'))
    
    @staticmethod
    def validate_phone(phone):
        """
        验证手机号码
        - 支持中国大陆手机号格式
        """
        if not phone:
            return  # 手机号可以为空
        
        # 中国大陆手机号正则
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            raise ValidationError(_('请输入有效的手机号码'))
    
    @staticmethod
    def validate_email(email):
        """
        验证邮箱地址
        """
        if not email:
            return  # 邮箱可以为空
        
        # 基本邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(_('请输入有效的邮箱地址'))
    
    @staticmethod
    def validate_password_strength(password):
        """
        验证密码强度
        - 长度至少8位
        - 包含大小写字母、数字
        """
        if not password:
            raise ValidationError(_('密码不能为空'))
        
        if len(password) < 8:
            raise ValidationError(_('密码长度至少8位'))
        
        if len(password) > 128:
            raise ValidationError(_('密码长度不能超过128位'))
        
        # 检查是否包含大写字母
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_('密码必须包含至少一个大写字母'))
        
        # 检查是否包含小写字母
        if not re.search(r'[a-z]', password):
            raise ValidationError(_('密码必须包含至少一个小写字母'))
        
        # 检查是否包含数字
        if not re.search(r'\d', password):
            raise ValidationError(_('密码必须包含至少一个数字'))
        
        # 检查常见弱密码
        weak_passwords = [
            '12345678', 'password', 'Password123', 
            'qwerty123', 'abc123456', '123456789'
        ]
        if password in weak_passwords:
            raise ValidationError(_('密码过于简单，请选择更复杂的密码'))


class RoleExtensionValidator:
    """
    角色增项数据验证器
    """
    
    @staticmethod
    def validate_extension_data(extension_data, role_extension):
        """
        验证增项数据
        """
        if not extension_data:
            return
        
        # 验证必填字段
        required_fields = role_extension.get_required_fields()
        for field in required_fields:
            if field not in extension_data or not extension_data[field]:
                raise ValidationError(_(f'字段 {field} 为必填项'))
        
        # 验证字段类型和格式
        field_configs = role_extension.get_field_configs()
        for field_name, value in extension_data.items():
            if field_name in field_configs:
                config = field_configs[field_name]
                RoleExtensionValidator._validate_field_value(field_name, value, config)
    
    @staticmethod
    def _validate_field_value(field_name, value, config):
        """
        验证单个字段值
        """
        field_type = config.get('type', 'text')
        
        if field_type == 'number':
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValidationError(_(f'字段 {field_name} 必须是数字'))
        
        elif field_type == 'email':
            EnhancedUserValidator.validate_email(value)
        
        elif field_type == 'phone':
            EnhancedUserValidator.validate_phone(value)
        
        elif field_type == 'text':
            max_length = config.get('max_length', 255)
            if len(str(value)) > max_length:
                raise ValidationError(_(f'字段 {field_name} 长度不能超过 {max_length} 字符'))
        
        # 验证选择字段
        choices = config.get('choices')
        if choices and value not in [choice['value'] for choice in choices]:
            raise ValidationError(_(f'字段 {field_name} 的值不在允许的选项中'))


class BulkOperationValidator:
    """
    批量操作数据验证器
    """
    
    @staticmethod
    def validate_bulk_user_data(users_data):
        """
        验证批量用户数据
        """
        if not users_data:
            raise ValidationError(_('用户数据不能为空'))
        
        if not isinstance(users_data, list):
            raise ValidationError(_('用户数据必须是列表格式'))
        
        if len(users_data) > 100:
            raise ValidationError(_('单次批量操作不能超过100个用户'))
        
        # 验证每个用户数据
        usernames = set()
        for i, user_data in enumerate(users_data):
            try:
                BulkOperationValidator._validate_single_user_data(user_data)
                
                # 检查用户名重复
                username = user_data.get('username')
                if username in usernames:
                    raise ValidationError(_(f'用户名 {username} 重复'))
                usernames.add(username)
                
            except ValidationError as e:
                raise ValidationError(_(f'第 {i+1} 个用户数据错误: {str(e)}'))
    
    @staticmethod
    def _validate_single_user_data(user_data):
        """
        验证单个用户数据
        """
        required_fields = ['username', 'role']
        for field in required_fields:
            if field not in user_data:
                raise ValidationError(_(f'缺少必填字段: {field}'))
        
        # 验证用户名
        EnhancedUserValidator.validate_username(user_data['username'])
        
        # 验证真实姓名
        if 'real_name' in user_data:
            EnhancedUserValidator.validate_real_name(user_data['real_name'])
        
        # 验证邮箱
        if 'email' in user_data:
            EnhancedUserValidator.validate_email(user_data['email'])
        
        # 验证手机号
        if 'phone' in user_data:
            EnhancedUserValidator.validate_phone(user_data['phone'])
    
    @staticmethod
    def validate_bulk_role_assignment(assignments_data):
        """
        验证批量角色分配数据
        """
        if not assignments_data:
            raise ValidationError(_('角色分配数据不能为空'))
        
        if not isinstance(assignments_data, list):
            raise ValidationError(_('角色分配数据必须是列表格式'))
        
        if len(assignments_data) > 200:
            raise ValidationError(_('单次批量角色分配不能超过200个'))
        
        # 验证每个分配数据
        for i, assignment in enumerate(assignments_data):
            if 'user_id' not in assignment or 'role' not in assignment:
                raise ValidationError(_(f'第 {i+1} 个分配数据缺少必填字段'))