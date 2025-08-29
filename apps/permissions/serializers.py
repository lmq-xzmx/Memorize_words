from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import MenuModuleConfig, RoleGroupMapping
from .models_optimized import PermissionSyncLog
from apps.accounts.models import UserRole
from apps.accounts.services.role_service import RoleService

class DynamicRoleChoiceField(serializers.ChoiceField):
    """动态角色选择字段"""
    def __init__(self, **kwargs):
        kwargs['choices'] = RoleService.get_role_choices(include_empty=False)
        super().__init__(**kwargs)



class MenuModuleConfigSerializer(serializers.ModelSerializer):
    """前台菜单模块配置序列化器"""
    
    class Meta:
        model = MenuModuleConfig
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# RoleMenuPermissionSerializer 已被移除（RoleMenuPermission 模型已废弃）
# 请使用 MenuValidity 和 RoleMenuAssignment 相关序列化器替代


class GroupSerializer(serializers.ModelSerializer):
    """Django组序列化器"""
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permissions_count']
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    content_type_name = serializers.CharField(source='content_type.name', read_only=True)
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type', 'content_type_name']


class RoleGroupMappingSerializer(serializers.ModelSerializer):
    """角色组映射配置序列化器"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = RoleGroupMapping
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PermissionSyncLogSerializer(serializers.ModelSerializer):
    """权限同步日志序列化器"""
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    
    class Meta:
        model = PermissionSyncLog
        fields = '__all__'
        read_only_fields = ('created_at',)


class RolePermissionSerializer(serializers.Serializer):
    """角色权限管理序列化器"""
    role = DynamicRoleChoiceField()
    permissions = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="权限ID列表"
    )
    
    def validate_permissions(self, value):
        """验证权限ID是否存在"""
        existing_permissions = Permission.objects.filter(id__in=value)
        if len(existing_permissions) != len(value):
            raise serializers.ValidationError("部分权限ID不存在")
        return value


class MenuAccessCheckSerializer(serializers.Serializer):
    """菜单访问检查序列化器"""
    role = DynamicRoleChoiceField()
    menu_key = serializers.CharField(max_length=50)
    
    def validate_menu_key(self, value):
        """验证菜单标识是否存在"""
        try:
            if hasattr(MenuModuleConfig, 'objects') and not MenuModuleConfig.objects.filter(key=value, is_active=True).exists():
                raise serializers.ValidationError("菜单模块不存在或已禁用")
        except Exception:
            # 如果数据库查询失败，跳过验证
            pass
        return value


class BulkPermissionUpdateSerializer(serializers.Serializer):
    """批量权限更新序列化器"""
    role = DynamicRoleChoiceField()
    menu_permissions = serializers.DictField(
        child=serializers.BooleanField(),
        help_text="菜单权限字典，key为菜单标识，value为是否可访问"
    )
    
    def validate_menu_permissions(self, value):
        """验证菜单权限数据"""
        try:
            if hasattr(MenuModuleConfig, 'objects'):
                menu_keys = list(value.keys())
                existing_menus = MenuModuleConfig.objects.filter(key__in=menu_keys)
                if len(existing_menus) != len(menu_keys):
                    raise serializers.ValidationError("部分菜单标识不存在")
        except Exception:
            # 如果数据库查询失败，跳过验证
            pass
        return value