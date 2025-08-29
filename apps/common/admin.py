# -*- coding: utf-8 -*-
"""
统一的ModelAdmin基类
提供通用的管理功能，替代前端JavaScript逻辑
"""

from django.contrib import admin
from django.forms import ModelForm
from django.core.cache import cache
from django import forms
from django.db import models
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.forms.widgets import Select, TextInput
from django.core.exceptions import ValidationError
import json
import re


class EnhancedModelAdmin(admin.ModelAdmin):
    """
    增强的ModelAdmin基类
    替代原有的JavaScript功能，使用Django原生实现
    """
    
    class Media:
        css = {
            'all': (
                'admin/css/unified_admin_styles.css',
            )
        }
        js = (
            'admin/js/unified_role_selector.js',
            'admin/js/xpath_optimizer.js',
            'admin/js/role_management_auto_fill.js',
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        统一的外键字段处理
        替代dynamic_role_selector.js的功能
        """
        if db_field.name == 'role':
            kwargs['widget'] = forms.Select(attrs={
                'class': 'unified-role-selector',
                'data-field-type': 'role'
            })
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        统一的多对多字段处理
        替代role_user_group_admin.js的用户过滤功能
        """
        if db_field.name == 'users':
            # 根据角色过滤用户
            role_id = request.GET.get('role')
            if role_id:
                from apps.accounts.models import CustomUser
                kwargs['queryset'] = CustomUser.objects.filter(
                    role_id=role_id,
                    is_active=True
                ).order_by('real_name', 'username')
            
            # 使用增强的多选组件
            kwargs['widget'] = FilteredSelectMultiple(
                verbose_name=db_field.verbose_name,
                is_stacked=False,
                attrs={
                    'class': 'enhanced-user-selector',
                    'data-role-dependent': 'true'
                }
            )
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        获取表单时的统一处理
        """
        form = super().get_form(request, obj, change, **kwargs)
        
        # 添加动态帮助文本
        self._add_dynamic_help_text(form)
        
        # 设置字段依赖关系
        self._setup_field_dependencies(form)
        
        return form
    
    def _add_dynamic_help_text(self, form):
        """
        添加动态帮助文本
        """
        if 'users' in form.base_fields:
            form.base_fields['users'].help_text = (
                '选择角色后，用户列表将自动过滤显示该角色下的激活用户。'
                '可以按住Ctrl键进行多选。'
            )
        
        if 'role' in form.base_fields:
            form.base_fields['role'].help_text = (
                '选择角色将影响其他相关字段的可选项。'
            )
    
    def _setup_field_dependencies(self, form):
        """
        设置字段依赖关系
        """
        # 为有依赖关系的字段添加特殊属性
        dependent_fields = {
            'users': 'role',  # users字段依赖role字段
            'groups': 'role',  # groups字段依赖role字段
        }
        
        for field_name, depends_on in dependent_fields.items():
            if field_name in form.base_fields and depends_on in form.base_fields:
                form.base_fields[field_name].widget.attrs.update({
                    'data-depends-on': depends_on,
                    'data-auto-filter': 'true'
                })


class ConflictResolutionAdminMixin(admin.ModelAdmin):
    """
    冲突解决管理混入类
    替代conflict_resolution.js的字段同步功能
    """
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        
        # 为冲突解决字段添加自动同步逻辑
        if hasattr(self, 'model'):
            model = self.model
            if hasattr(model, 'word') and hasattr(model, 'conflicting_word'):
                self._setup_conflict_resolution_fields(form)
        
        return form
    
    def _setup_conflict_resolution_fields(self, form):
        """
        设置冲突解决字段的自动同步
        """
        if 'word' in form.base_fields:
            form.base_fields['word'].widget.attrs.update({
                'data-sync-target': 'conflicting_word',
                'data-sync-condition': 'empty'
            })
        
        if 'conflicting_word' in form.base_fields:
            form.base_fields['conflicting_word'].help_text = (
                '如果不填写，将自动使用word字段的值'
            )
            form.base_fields['conflicting_word'].widget.attrs.update({
                'data-auto-sync': 'true'
            })


class RoleBasedFilterAdminMixin(admin.ModelAdmin):
    """
    基于角色的过滤管理混入类
    替代role_user_group_admin.js的过滤功能
    """
    
    def get_urls(self):
        """
        添加AJAX端点用于动态过滤
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'filter-users-by-role/',
                self.admin_site.admin_view(self.filter_users_by_role),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_filter_users'
            ),
        ]
        return custom_urls + urls
    
    def filter_users_by_role(self, request):
        """
        根据角色过滤用户的AJAX端点
        """
        role_id = request.GET.get('role_id')
        
        if not role_id:
            return JsonResponse({'users': []})
        
        try:
            from apps.accounts.models import CustomUser
            users = CustomUser.objects.filter(
                role_id=role_id,
                is_active=True
            ).order_by('real_name', 'username').values(
                'id', 'username', 'real_name', 'role__name'
            )
            
            user_list = []
            for user in users:
                display_name = user['real_name'] or user['username']
                role_display = user['role__name'] or ''
                user_list.append({
                    'id': user['id'],
                    'text': f"{display_name} ({user['username']})" + 
                           (f" [{role_display}]" if role_display else "")
                })
            
            return JsonResponse({'users': user_list})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class EnhancedRoleForm(forms.ModelForm):
    """
    增强的角色表单，提供自动填充功能
    替代 role_management_auto_fill.js 的功能
    """
    # 中英文角色映射表
    ROLE_MAPPING = {
        '管理员': 'admin',
        '教师': 'teacher', 
        '学生': 'student',
        '超级管理员': 'superadmin',
        '系统管理员': 'sysadmin',
        '课程管理员': 'courseadmin',
        '班级管理员': 'classadmin',
        '助教': 'assistant',
        '访客': 'guest',
        '审核员': 'reviewer'
    }
    
    class Meta:
        abstract = True
    
    def clean_role_name(self):
        """自动转换中文角色名到英文"""
        role_name = self.cleaned_data.get('role_name', '')
        if role_name in self.ROLE_MAPPING:
            return self.ROLE_MAPPING[role_name]
        return role_name
    
    def clean_role_code(self):
        """自动生成角色代码"""
        role_code = self.cleaned_data.get('role_code', '')
        role_name = self.cleaned_data.get('role_name', '')
        
        if not role_code and role_name:
            # 自动生成角色代码
            if role_name in self.ROLE_MAPPING:
                role_code = self.ROLE_MAPPING[role_name]
            else:
                # 简单的拼音转换
                role_code = self.chinese_to_pinyin(role_name)
        
        return role_code
    
    def chinese_to_pinyin(self, text):
        """简单的中文转拼音实现"""
        if not text:
            return ''
            
        pinyin_map = {
            '管': 'guan', '理': 'li', '员': 'yuan',
            '教': 'jiao', '师': 'shi', '学': 'xue', '生': 'sheng',
            '超': 'chao', '级': 'ji', '系': 'xi', '统': 'tong',
            '课': 'ke', '程': 'cheng', '班': 'ban',
            '助': 'zhu', '访': 'fang', '客': 'ke',
            '审': 'shen', '核': 'he'
        }
        
        result = ''
        for char in str(text):
            result += pinyin_map.get(char, char)
        
        return result.lower()


class DynamicLearningPlanAdminMixin(admin.ModelAdmin):
    """
    动态学习计划Admin混入类
    替代 learning_plan_admin.js 的功能
    """
    
    # 计划类型字段配置
    PLAN_TYPE_FIELD_CONFIG = {
        'mechanical': {
            'required_fields': ['words_per_day', 'review_interval'],
            'hidden_fields': ['daily_target', 'start_date', 'end_date', 'weekend_settings'],
            'readonly_fields': []
        },
        'daily_progress': {
            'required_fields': ['daily_target', 'start_date'],
            'hidden_fields': ['words_per_day', 'review_interval', 'weekend_settings'],
            'readonly_fields': []
        },
        'workday': {
            'required_fields': ['words_per_day', 'start_date', 'end_date'],
            'hidden_fields': ['weekend_settings'],
            'readonly_fields': []
        },
        'weekend': {
            'required_fields': ['weekend_settings', 'words_per_day'],
            'hidden_fields': ['daily_target'],
            'readonly_fields': []
        },
        'weekly': {
            'required_fields': ['weekly_target', 'start_date'],
            'hidden_fields': ['daily_target', 'words_per_day'],
            'readonly_fields': []
        },
        'custom': {
            'required_fields': ['custom_settings'],
            'hidden_fields': [],
            'readonly_fields': []
        }
    }
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        """根据计划类型动态调整表单字段"""
        form = super().get_form(request, obj, change, **kwargs)
        
        if obj and hasattr(obj, 'plan_type') and obj.plan_type:
            self.adjust_fields_by_plan_type(form, obj.plan_type)
        
        return form
    
    def adjust_fields_by_plan_type(self, form, plan_type):
        """根据计划类型调整字段显示"""
        config = self.PLAN_TYPE_FIELD_CONFIG.get(plan_type, {})
        
        # 隐藏不需要的字段
        for field_name in config.get('hidden_fields', []):
            if field_name in form.base_fields:
                form.base_fields[field_name].widget = forms.HiddenInput()
                form.base_fields[field_name].required = False
        
        # 设置必填字段
        for field_name in config.get('required_fields', []):
            if field_name in form.base_fields:
                form.base_fields[field_name].required = True
        
        # 设置只读字段
        for field_name in config.get('readonly_fields', []):
            if field_name in form.base_fields:
                form.base_fields[field_name].widget.attrs['readonly'] = True
    
    def get_readonly_fields(self, request, obj=None):
        """动态设置只读字段"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        if obj and hasattr(obj, 'plan_type') and obj.plan_type:
            config = self.PLAN_TYPE_FIELD_CONFIG.get(obj.plan_type, {})
            readonly_fields.extend(config.get('readonly_fields', []))
        
        return tuple(readonly_fields)


class EnhancedRoleAdminMixin(admin.ModelAdmin):
    """
    增强的角色Admin混入类
    替代 unified_role_selector.js 的部分功能
    """
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义外键字段，优化角色选择"""
        if db_field.name == "role":
            # 根据用户权限过滤角色选项
            kwargs["queryset"] = self.get_role_queryset(request)
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_role_queryset(self, request):
        """获取角色查询集，带缓存优化"""
        cache_key = f'role_choices_{request.user.id}_{request.user.groups.count()}'
        queryset = cache.get(cache_key)
        
        if queryset is None:
            # 根据用户权限过滤角色
            if request.user.is_superuser:
                queryset = self.get_all_roles()
            else:
                queryset = self.get_user_accessible_roles(request.user)
            
            # 缓存5分钟
            cache.set(cache_key, queryset, 300)
        
        return queryset
    
    def get_all_roles(self):
        """获取所有角色"""
        from django.contrib.auth.models import Group
        return Group.objects.filter(name__icontains='role').order_by('name')
    
    def get_user_accessible_roles(self, user):
        """获取用户可访问的角色"""
        from django.contrib.auth.models import Group
        user_groups = user.groups.all()
        
        # 基于用户组权限过滤角色
        accessible_roles = Group.objects.filter(
            name__icontains='role'
        ).exclude(
            name__in=['superadmin', 'sysadmin']
        ).order_by('name')
        
        return accessible_roles


class UnifiedAdminForm(forms.ModelForm):
    """
    统一的管理表单基类
    替代JavaScript的字段处理逻辑
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_field_enhancements()
    
    def _setup_field_enhancements(self):
        """
        设置字段增强功能
        """
        # 自动同步字段逻辑
        if 'word' in self.fields and 'conflicting_word' in self.fields:
            self.fields['conflicting_word'].required = False
    
    def clean(self):
        """
        统一的数据清理逻辑
        替代JavaScript的字段同步功能
        """
        cleaned_data = super().clean()
        
        # 自动同步word和conflicting_word字段
        word = cleaned_data.get('word')
        conflicting_word = cleaned_data.get('conflicting_word')
        
        if word and not conflicting_word:
            cleaned_data['conflicting_word'] = word
        
        return cleaned_data
    
    def clean_conflicting_word(self):
        """
        冲突词字段的特殊清理逻辑
        """
        conflicting_word = self.cleaned_data.get('conflicting_word')
        word = self.cleaned_data.get('word')
        
        # 如果conflicting_word为空，使用word的值
        if not conflicting_word and word:
            return word
        
        return conflicting_word


# 导出的管理类，供其他应用使用
__all__ = [
    'EnhancedModelAdmin',
    'ConflictResolutionAdminMixin',
    'RoleBasedFilterAdminMixin',
    'EnhancedRoleForm',
    'DynamicLearningPlanAdminMixin',
    'EnhancedRoleAdminMixin',
    'UnifiedAdminForm',
]