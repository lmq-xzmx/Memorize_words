from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    ResourceAuthorization,
    ResourceShare,
    ResourceCategory,
    ResourceUsageAnalytics,
    UserSubscription,
    SubscriptionFeature
)

User = get_user_model()


class ResourceAuthorizationSerializer(serializers.ModelSerializer):
    """资源授权序列化器"""
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    access_level_display = serializers.CharField(source='get_access_level_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceAuthorization
        fields = [
            'id', 'resource_type', 'resource_type_display', 'resource_id',
            'access_level', 'access_level_display', 'created_by', 'created_by_username',
            'is_active', 'is_public', 'requires_subscription',
            'valid_from', 'valid_until', 'is_expired',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_expired(self, obj):
        """检查是否已过期"""
        if obj.valid_until:
            return timezone.now() > obj.valid_until
        return False
    
    def validate(self, attrs):
        """验证数据"""
        valid_from = attrs.get('valid_from')
        valid_until = attrs.get('valid_until')
        
        if valid_from and valid_until and valid_from >= valid_until:
            raise serializers.ValidationError("有效开始时间必须早于结束时间")
        
        return attrs


class ResourceShareSerializer(serializers.ModelSerializer):
    """资源分享序列化器"""
    authorization_info = ResourceAuthorizationSerializer(source='authorization', read_only=True)
    shared_by_username = serializers.CharField(source='shared_by.username', read_only=True)
    shared_with_usernames = serializers.SerializerMethodField()
    share_type_display = serializers.CharField(source='get_share_type_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceShare
        fields = [
            'id', 'authorization', 'authorization_info', 'shared_by', 'shared_by_username',
            'shared_with', 'shared_with_usernames', 'share_type', 'share_type_display',
            'is_active', 'allow_reshare', 'expires_at', 'is_expired',
            'share_message', 'metadata', 'shared_at'
        ]
        read_only_fields = ['shared_at']
    
    def get_shared_with_usernames(self, obj):
        """获取分享对象用户名列表"""
        return [user.username for user in obj.shared_with.all()]
    
    def get_is_expired(self, obj):
        """检查分享是否已过期"""
        if obj.expires_at:
            return timezone.now() > obj.expires_at
        return False
    
    def validate(self, attrs):
        """验证分享数据"""
        expires_at = attrs.get('expires_at')
        
        if expires_at and expires_at <= timezone.now():
            raise serializers.ValidationError("过期时间必须是未来时间")
        
        return attrs


class ResourceCategorySerializer(serializers.ModelSerializer):
    """资源分类序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    children = serializers.SerializerMethodField()
    resource_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceCategory
        fields = [
            'id', 'name', 'description', 'parent', 'parent_name',
            'created_by', 'created_by_username', 'is_public', 'sort_order',
            'children', 'resource_count', 'authorizations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_children(self, obj):
        """获取子分类"""
        children = obj.children.filter(is_public=True) if hasattr(obj, 'children') else []
        return ResourceCategorySerializer(children, many=True, context=self.context).data
    
    def get_resource_count(self, obj):
        """获取资源数量"""
        return obj.get_resource_count()
    
    def validate_parent(self, value):
        """验证父分类"""
        if value and self.instance and value == self.instance:
            raise serializers.ValidationError("分类不能设置自己为父分类")
        
        # 检查循环引用
        if value and self.instance:
            current = value
            while current:
                if current == self.instance:
                    raise serializers.ValidationError("不能创建循环引用")
                current = current.parent
        
        return value


class ResourceUsageAnalyticsSerializer(serializers.ModelSerializer):
    """资源使用分析序列化器"""
    authorization_info = ResourceAuthorizationSerializer(source='authorization', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = ResourceUsageAnalytics
        fields = [
            'id', 'authorization', 'authorization_info', 'user', 'user_username',
            'action', 'action_display', 'platform', 'platform_display',
            'session_id', 'user_agent', 'ip_address',
            'metadata', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class SubscriptionFeatureSerializer(serializers.ModelSerializer):
    """订阅功能序列化器"""
    
    class Meta:
        model = SubscriptionFeature
        fields = [
            'id', 'name', 'code', 'description', 'is_active',
            'subscription_types', 'usage_limit', 'daily_limit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_code(self, value):
        """验证功能代码唯一性"""
        if self.instance:
            # 更新时排除自身
            if SubscriptionFeature.objects.exclude(id=self.instance.id).filter(code=value).exists():
                raise serializers.ValidationError("功能代码已存在")
        else:
            # 创建时检查唯一性
            if SubscriptionFeature.objects.filter(code=value).exists():
                raise serializers.ValidationError("功能代码已存在")
        return value


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """用户订阅序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    subscription_type_display = serializers.CharField(source='get_subscription_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    features_info = SubscriptionFeatureSerializer(source='features', many=True, read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'user_username', 'subscription_type', 'subscription_type_display',
            'status', 'status_display', 'start_date', 'end_date',
            'is_active', 'remaining_days', 'features', 'features_info',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_active(self, obj):
        """获取激活状态"""
        return obj.is_active()
    
    def get_remaining_days(self, obj):
        """获取剩余天数"""
        return obj.get_remaining_days()
    
    def validate(self, attrs):
        """验证订阅数据"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("开始日期必须早于结束日期")
        
        return attrs


class ResourceAuthorizationCreateSerializer(serializers.ModelSerializer):
    """资源授权创建序列化器"""
    
    class Meta:
        model = ResourceAuthorization
        fields = [
            'resource_type', 'resource_id', 'access_level',
            'is_active', 'is_public', 'requires_subscription',
            'valid_from', 'valid_until', 'metadata'
        ]
    
    def create(self, validated_data):
        """创建资源授权"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ResourceShareCreateSerializer(serializers.ModelSerializer):
    """资源分享创建序列化器"""
    
    class Meta:
        model = ResourceShare
        fields = [
            'authorization', 'shared_with', 'share_type',
            'is_active', 'allow_reshare', 'expires_at',
            'share_message', 'metadata'
        ]
    
    def create(self, validated_data):
        """创建资源分享"""
        validated_data['shared_by'] = self.context['request'].user
        return super().create(validated_data)


class ResourceCategoryCreateSerializer(serializers.ModelSerializer):
    """资源分类创建序列化器"""
    
    class Meta:
        model = ResourceCategory
        fields = [
            'name', 'description', 'parent',
            'is_public', 'sort_order', 'authorizations'
        ]
    
    def create(self, validated_data):
        """创建资源分类"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)