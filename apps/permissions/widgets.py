from django import forms
from django.utils.html import format_html
from django.urls import reverse
from apps.accounts.models import UserRole
from apps.accounts.services.role_service import RoleService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import RoleManagement
else:
    try:
        from .models import RoleManagement
    except ImportError:
        RoleManagement = None


class StandardRoleSelectWidget(forms.Select):
    """标准角色选择器Widget - 使用统一数据源"""
    
    def __init__(self, attrs=None, choices=(), include_inactive=False):
        self.include_inactive = include_inactive
        default_attrs = {
            'id': 'id_role',
            'class': 'form-control standard-role-selector'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, choices)
    
    def get_role_choices(self):
        """获取角色选择项 - 使用统一服务"""
        return RoleService.get_role_choices(include_inactive=self.include_inactive)
    
    def render(self, name, value, attrs=None, renderer=None):
        """渲染Widget"""
        # 更新选择项
        self.choices = self.get_role_choices()
        
        # 渲染基础选择器
        html = super().render(name, value, attrs, renderer)
        
        # 返回基础HTML，移除JavaScript支持
        return html
    
    class Media:
        css = {
            'all': ('admin/css/unified_admin_styles.css',)
        }
        js = ('admin/js/unified_role_selector.js',)


class StandardRoleChoiceField(forms.ChoiceField):
    """标准角色选择字段 - 使用统一数据源"""
    
    def __init__(self, *args, include_inactive=False, **kwargs):
        self.include_inactive = include_inactive
        
        # 设置默认widget
        if 'widget' not in kwargs:
            kwargs['widget'] = StandardRoleSelectWidget(include_inactive=include_inactive)
        
        # 设置选择项
        if 'choices' not in kwargs:
            kwargs['choices'] = self.get_role_choices()
        
        super().__init__(*args, **kwargs)
    
    def get_role_choices(self):
        """获取角色选择项 - 使用统一服务"""
        return RoleService.get_role_choices(include_inactive=self.include_inactive)
    
    def validate(self, value):
        """验证角色值"""
        super().validate(value)
        if value and value != '':
            role_info = RoleService.get_role_info(value)
            if not role_info:
                raise forms.ValidationError(f'无效的角色代码: {value}')
            if not self.include_inactive and not role_info['is_active']:
                raise forms.ValidationError(f'角色 {value} 已被禁用')


class RoleTextInputWidget(forms.TextInput):
    """角色文本输入Widget - 用于创建新角色"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'id': 'id_role',
            'class': 'form-control role-text-input',
            'placeholder': '请输入新角色标识（如：custom_role）',
            'pattern': '[a-z_][a-z0-9_]*',  # 角色代码格式验证
            'title': '角色代码只能包含小写字母、数字和下划线，且必须以字母或下划线开头'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        """渲染Widget"""
        html = super().render(name, value, attrs, renderer)
        return html
    
    class Media:
        css = {
            'all': ('admin/css/unified_admin_styles.css',)
        }
        js = ('admin/js/role_text_input_validator.js',)