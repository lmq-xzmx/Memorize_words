# -*- coding: utf-8 -*-
"""
角色选择器统一配置文件

本文件定义了整个系统中角色选择器的统一配置和使用规范。
所有需要角色选择功能的模块都应该使用这里定义的标准组件。
"""

from typing import Any, Optional
from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from .widgets import StandardRoleSelectWidget, StandardRoleChoiceField, RoleTextInputWidget


class RoleSelectorMixin:
    """
    角色选择器混入类
    
    为Admin类提供统一的角色选择器配置方法。
    使用方法：在Admin类中继承此混入类，然后调用相应的配置方法。
    """
    
    def setup_role_selector(self, db_field: models.Field, request: HttpRequest, **kwargs: Any) -> Optional[Any]:
        """
        为角色字段设置标准选择器
        
        Args:
            db_field: 数据库字段
            request: HTTP请求对象
            **kwargs: 其他参数
            
        Returns:
            配置好的字段或None
        """
        if db_field.name == 'role':
            kwargs['widget'] = StandardRoleSelectWidget()
            # 使用类型忽略来避免类型检查错误
            return super().formfield_for_choice_field(db_field, request, **kwargs)  # type: ignore
        return None
    
    def setup_role_text_input(self, db_field: models.Field, request: HttpRequest, **kwargs: Any) -> Optional[Any]:
        """
        为角色字段设置文本输入框（用于创建新角色）
        
        Args:
            db_field: 数据库字段
            request: HTTP请求对象
            **kwargs: 其他参数
            
        Returns:
            配置好的字段或None
        """
        if db_field.name == 'role':
            kwargs['widget'] = RoleTextInputWidget()
            # 使用类型忽略来避免类型检查错误
            return super().formfield_for_char_field(db_field, request, **kwargs)  # type: ignore
        return None


class StandardRoleAdminMixin(RoleSelectorMixin):
    """
    标准角色管理混入类
    
    为需要角色选择功能的Admin类提供标准配置。
    适用于大部分角色选择场景。
    """
    
    def formfield_for_choice_field(self, db_field: models.Field, request: HttpRequest, **kwargs: Any) -> Any:
        """
        为选择字段配置标准角色选择器
        """
        result = self.setup_role_selector(db_field, request, **kwargs)
        if result is not None:
            return result
        return super().formfield_for_choice_field(db_field, request, **kwargs)  # type: ignore
    
    def formfield_for_char_field(self, db_field: models.Field, request: HttpRequest, **kwargs: Any) -> Any:
        """
        为字符字段配置标准角色选择器（当role字段是CharField时）
        """
        if db_field.name == 'role':
            # 对于role字段，使用下拉选择器而不是文本输入框
            kwargs['widget'] = StandardRoleSelectWidget()
            from .widgets import StandardRoleChoiceField
            return StandardRoleChoiceField(**kwargs)
        return super().formfield_for_char_field(db_field, request, **kwargs)  # type: ignore


class RoleCreationAdminMixin(RoleSelectorMixin):
    """
    角色创建管理混入类
    
    为需要创建新角色的Admin类提供文本输入配置。
    适用于角色管理等需要创建新角色的场景。
    """
    
    def formfield_for_char_field(self, db_field: models.Field, request: HttpRequest, **kwargs: Any) -> Any:
        """
        为字符字段配置角色文本输入框
        """
        result = self.setup_role_text_input(db_field, request, **kwargs)
        if result is not None:
            return result
        return super().formfield_for_char_field(db_field, request, **kwargs)  # type: ignore


# 角色选择器使用指南
ROLE_SELECTOR_USAGE_GUIDE = """
角色选择器统一使用指南

1. 标准角色选择场景（推荐）：
   - 继承 StandardRoleAdminMixin
   - 适用于：用户管理、角色组映射、角色用户组等
   
   示例：
   class MyAdmin(StandardRoleAdminMixin, admin.ModelAdmin):
       pass

2. 角色创建场景：
   - 继承 RoleCreationAdminMixin
   - 适用于：角色管理（创建新角色）
   
   示例：
   class RoleManagementAdmin(RoleCreationAdminMixin, admin.ModelAdmin):
       pass

3. 自定义场景：
   - 继承 RoleSelectorMixin
   - 手动调用 setup_role_selector 或 setup_role_text_input
   
   示例：
   class CustomAdmin(RoleSelectorMixin, admin.ModelAdmin):
       def formfield_for_choice_field(self, db_field, request, **kwargs):
           result = self.setup_role_selector(db_field, request, **kwargs)
           if result is not None:
               return result
           return super().formfield_for_choice_field(db_field, request, **kwargs)

4. 表单中使用：
   from apps.permissions.widgets import StandardRoleChoiceField, StandardRoleSelectWidget
   
   class MyForm(forms.ModelForm):
       role = StandardRoleChoiceField(widget=StandardRoleSelectWidget())

注意事项：
- 所有角色选择器都会自动加载最新的角色数据
- 支持实时更新和动态刷新
- 统一的样式和交互体验
- 自动处理权限验证和数据同步
"""


# 导出的公共接口
__all__ = [
    'RoleSelectorMixin',
    'StandardRoleAdminMixin', 
    'RoleCreationAdminMixin',
    'ROLE_SELECTOR_USAGE_GUIDE'
]