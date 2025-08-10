from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Count
from django.db import transaction
from django.core.exceptions import ValidationError
from .validators import RoleExtensionValidator, BulkOperationValidator
from .performance import RoleExtensionCacheManager, BulkOperationOptimizer

from .models import (
    CustomUser, UserRole, RoleTemplate, RoleExtension, 
    UserExtensionData, RoleLevel, RoleUser, UserExtension
)
from .serializers import (
    UserSerializer, UserExtensionDataSerializer, RoleExtensionSerializer
)


class RoleTemplateSerializer(serializers.ModelSerializer):
    """角色模板序列化器"""
    field_count = serializers.ReadOnlyField(source='get_field_count')
    user_count = serializers.ReadOnlyField(source='get_user_count')
    
    class Meta:
        model = RoleTemplate
        fields = [
            'id', 'role', 'template_name', 'description', 'version',
            'is_active', 'created_at', 'updated_at', 'field_count', 'user_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'field_count', 'user_count']


class RoleTemplateDetailSerializer(serializers.ModelSerializer):
    """角色模板详细序列化器"""
    template_fields = RoleExtensionSerializer(many=True, read_only=True)
    field_count = serializers.ReadOnlyField(source='get_field_count')
    user_count = serializers.ReadOnlyField(source='get_user_count')
    
    class Meta:
        model = RoleTemplate
        fields = [
            'id', 'role', 'template_name', 'description', 'version',
            'is_active', 'created_at', 'updated_at', 'template_fields',
            'field_count', 'user_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'template_fields', 'field_count', 'user_count']


class BatchUserExtensionSerializer(serializers.Serializer):
    """批量用户增项操作序列化器"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='用户ID列表',
        required=True
    )
    extension_data = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        help_text='增项数据字典，格式：{"field_name": "value"}',
        required=True
    )
    operation = serializers.ChoiceField(
        choices=['create', 'update', 'delete'],
        default='update',
        help_text='操作类型：create-创建，update-更新，delete-删除'
    )


class RoleTemplateViewSet(viewsets.ModelViewSet):
    """角色模板管理视图集"""
    queryset = RoleTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    ordering_fields = ['role', 'created_at', 'updated_at']
    ordering = ['role']
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        from rest_framework.serializers import BaseSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return RoleTemplateDetailSerializer
        return RoleTemplateSerializer
    
    def get_permissions(self):
        """根据动作设置权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 只有管理员可以修改模板
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """创建模板时设置创建者"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def clone_template(self, request, pk=None):
        """克隆模板"""
        template = self.get_object()
        new_role = request.data.get('new_role') if hasattr(request.data, 'get') else None
        new_name = request.data.get('new_name') if hasattr(request.data, 'get') else None
        
        if not new_role or not new_name:
            return Response(
                {'error': '请提供新角色和模板名称'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查新角色是否已有模板
        if RoleTemplate.objects.filter(role=new_role).exists():
            return Response(
                {'error': '该角色已存在模板'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # 创建新模板
            new_template = RoleTemplate.objects.create(
                role=new_role,
                template_name=new_name,
                description=f'从{template.template_name}克隆',
                version='1.0.0',
                created_by=request.user
            )
            
            # 复制字段配置
            template_fields = RoleExtension.objects.filter(role_template=template)
            for field in template_fields:
                RoleExtension.objects.create(
                    role_template=new_template,
                    role=new_role,
                    field_name=field.field_name,
                    field_label=field.field_label,
                    field_type=field.field_type,
                    field_choices=field.field_choices,
                    is_required=field.is_required,
                    help_text=field.help_text,
                    default_value=field.default_value,
                    show_in_frontend_register=field.show_in_frontend_register,
                    show_in_backend_admin=field.show_in_backend_admin,
                    show_in_profile=field.show_in_profile,
                    validation_rules=field.validation_rules,
                    sort_order=field.sort_order
                )
        
        serializer = RoleTemplateDetailSerializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def apply_to_users(self, request, pk=None):
        """将模板应用到用户"""
        template = self.get_object()
        user_ids = request.data.get('user_ids', []) if hasattr(request.data, 'get') else []
        
        if not user_ids:
            # 应用到该角色的所有用户
            users = CustomUser.objects.filter(role=template.role, is_active=True)
        else:
            users = CustomUser.objects.filter(id__in=user_ids, role=template.role, is_active=True)
        
        applied_count = 0
        with transaction.atomic():
            for user in users:
                template_fields = RoleExtension.objects.filter(role_template=template, is_active=True)
                for field in template_fields:
                    # 创建或更新用户增项数据
                    data_obj, created = UserExtensionData.objects.update_or_create(
                        user=user,
                        role_extension=field,
                        defaults={'field_value': field.default_value or ''}
                    )
                    if created:
                        applied_count += 1
        
        return Response({
            'message': f'模板已应用到 {users.count()} 个用户',
            'applied_count': applied_count,
            'user_count': users.count()
        })


class EnhancedUserExtensionDataViewSet(viewsets.ModelViewSet):
    """增强的用户增项数据视图集"""
    serializer_class = UserExtensionDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role_extension__role', 'role_extension__field_type']
    
    def get_queryset(self):
        """根据用户角色过滤查询集"""
        from django.db.models import QuerySet
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return UserExtensionData.objects.all()
        if getattr(user, 'role', None) == UserRole.ADMIN:
            return UserExtensionData.objects.all()
        else:
            # 普通用户只能查看自己的扩展数据
            return UserExtensionData.objects.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """批量创建用户增项数据（优化版）"""
        serializer = BatchUserExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data.get('user_ids', [])
        extension_data = serializer.validated_data.get('extension_data', {})
        
        # 验证用户权限
        if not (getattr(request.user, 'role', None) == UserRole.ADMIN):
            # 非管理员只能操作自己的数据
            if len(user_ids) > 1 or (user_ids and user_ids[0] != request.user.id):
                return Response(
                    {'error': '权限不足'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 使用增强验证器
        try:
            for user_id in user_ids:
                user = CustomUser.objects.get(id=user_id)
                for field_name, value in extension_data.items():
                    extension = RoleExtension.objects.get(
                        role=user.role,
                        field_name=field_name,
                        is_active=True
                    )
                    RoleExtensionValidator.validate_extension_data({field_name: value}, extension)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except (CustomUser.DoesNotExist, RoleExtension.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        created_count = 0
        errors = []
        
        with transaction.atomic():
            # 使用优化的批量操作
            updates_data = []
            for user_id in user_ids:
                try:
                    user = CustomUser.objects.get(id=user_id)
                    for field_name, value in extension_data.items():
                        try:
                            extension = RoleExtension.objects.get(
                                role=user.role,
                                field_name=field_name,
                                is_active=True
                            )
                            
                            updates_data.append({
                                'user_id': user_id,
                                'role_extension_id': extension.pk,
                                'field_value': value
                            })
                            
                        except RoleExtension.DoesNotExist:
                            errors.append(f'用户{user.username}的角色{user.role}不存在字段{field_name}')
                            
                except CustomUser.DoesNotExist:
                    errors.append(f'用户ID {user_id} 不存在')
            
            # 执行批量更新
            if updates_data:
                created_count = BulkOperationOptimizer.bulk_update_user_extensions(updates_data)
                
                # 清除相关缓存
                for user_id in user_ids:
                    RoleExtensionCacheManager.invalidate_user_extension_cache(user_id)
        
        return Response({
            'message': f'批量创建完成，成功创建 {created_count} 条记录',
            'created_count': created_count,
            'errors': errors
        })
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """批量更新用户增项数据"""
        serializer = BatchUserExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data.get('user_ids', [])
        extension_data = serializer.validated_data.get('extension_data', {})
        
        # 验证用户权限
        if not (getattr(request.user, 'role', None) == UserRole.ADMIN):
            # 非管理员只能操作自己的数据
            if len(user_ids) > 1 or (user_ids and user_ids[0] != request.user.id):
                return Response(
                    {'error': '权限不足'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for user_id in user_ids:
                try:
                    user = CustomUser.objects.get(id=user_id)
                    for field_name, value in extension_data.items():
                        try:
                            extension = RoleExtension.objects.get(
                                role=user.role,
                                field_name=field_name,
                                is_active=True
                            )
                            
                            data_obj, created = UserExtensionData.objects.update_or_create(
                                user=user,
                                role_extension=extension,
                                defaults={'field_value': value}
                            )
                            
                            updated_count += 1
                            
                        except RoleExtension.DoesNotExist:
                            errors.append(f'用户{user.username}的角色{user.role}不存在字段{field_name}')
                            
                except CustomUser.DoesNotExist:
                    errors.append(f'用户ID {user_id} 不存在')
        
        return Response({
            'message': f'批量更新完成，成功更新 {updated_count} 条记录',
            'updated_count': updated_count,
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def template_statistics(self, request):
        """模板使用统计"""
        if not (getattr(request.user, 'role', None) == UserRole.ADMIN):
            return Response(
                {'error': '权限不足'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = []
        for template in RoleTemplate.objects.filter(is_active=True):
            # 统计该模板的使用情况
            total_users = CustomUser.objects.filter(role=template.role, is_active=True).count()
            users_with_data = UserExtensionData.objects.filter(
                role_extension__role=template.role
            ).values('user').distinct().count()
            
            field_stats = []
            template_fields = RoleExtension.objects.filter(role_template=template, is_active=True)
            for field in template_fields:
                filled_count = UserExtensionData.objects.filter(
                    role_extension=field
                ).exclude(field_value='').count()
                
                field_stats.append({
                    'field_name': field.field_name,
                    'field_label': field.field_label,
                    'total_users': total_users,
                    'filled_count': filled_count,
                    'fill_rate': round(filled_count / total_users * 100, 2) if total_users > 0 else 0
                })
            
            stats.append({
                'template_id': template.pk,
                'template_name': template.template_name,
                'role': template.role,
                'total_users': total_users,
                'users_with_data': users_with_data,
                'coverage_rate': round(users_with_data / total_users * 100, 2) if total_users > 0 else 0,
                'field_statistics': field_stats
            })
        
        return Response({
            'template_statistics': stats,
            'summary': {
                'total_templates': len(stats),
                'total_users': sum(s['total_users'] for s in stats),
                'total_users_with_data': sum(s['users_with_data'] for s in stats)
            }
        })