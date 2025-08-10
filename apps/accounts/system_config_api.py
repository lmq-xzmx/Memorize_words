from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
from .models import (
    CustomUser, UserRole, RoleExtension, RoleTemplate,
    UserExtensionData
)
from rest_framework import serializers
import json
from datetime import datetime
from apps.accounts.services.role_service import RoleService


class SystemConfigSerializer(serializers.Serializer):
    """系统配置序列化器"""
    config_key = serializers.CharField(max_length=100)
    config_value = serializers.CharField()
    config_type = serializers.ChoiceField(choices=[
        ('string', '字符串'),
        ('integer', '整数'),
        ('boolean', '布尔值'),
        ('json', 'JSON对象')
    ])
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    is_public = serializers.BooleanField(default=False)


class RoleTemplateSerializer(serializers.ModelSerializer):
    """角色模板序列化器"""
    class Meta:
        model = RoleTemplate
        fields = '__all__'


class RoleExtensionConfigSerializer(serializers.Serializer):
    """角色增项配置序列化器"""
    role = serializers.ChoiceField(choices=RoleService.get_role_choices(include_empty=False))
    extensions = serializers.ListField(
        child=serializers.DictField(),
        help_text="增项字段配置列表"
    )


class SystemConfigManagementViewSet(viewsets.ViewSet):
    """系统配置管理API - 实现系统级配置统一管理"""
    permission_classes = [IsAuthenticated]
    
    def check_admin_permission(self, request):
        """检查管理员权限"""
        return (request.user.is_authenticated and 
                (request.user.is_superuser or 
                 getattr(request.user, 'role', None) == UserRole.ADMIN))
    
    @action(detail=False, methods=['get'])
    def system_overview(self, request):
        """系统概览"""
        if not self.check_admin_permission(request):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以查看系统概览'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 用户统计
        user_stats = {}
        for role_code, role_name in RoleService.get_role_choices(include_empty=False):
            count = CustomUser.objects.filter(role=role_code, is_active=True).count()
            user_stats[role_code] = {
                'name': role_name,
                'count': count
            }
        
        # 角色增项统计
        extension_stats = {}
        for role_code, role_name in RoleService.get_role_choices(include_empty=False):
            extension_count = RoleExtension.objects.filter(
                role=role_code, 
                is_active=True
            ).count()
            extension_stats[role_code] = {
                'name': role_name,
                'extension_count': extension_count
            }
        
        # 系统配置统计
        config_stats = {
            'total_configs': self._get_system_configs_count(),
            'public_configs': self._get_public_configs_count(),
            'cache_status': self._get_cache_status()
        }
        
        return Response({
            'success': True,
            'data': {
                'user_statistics': user_stats,
                'extension_statistics': extension_stats,
                'config_statistics': config_stats,
                'system_info': {
                    'version': getattr(settings, 'VERSION', '1.0.0'),
                    'debug_mode': settings.DEBUG,
                    'database_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
                    'cache_backend': getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'unknown').split('.')[-1]
                }
            }
        })
    
    def _get_system_configs_count(self):
        """获取系统配置数量"""
        # 这里可以从数据库或配置文件中获取
        # 暂时返回模拟数据
        return len(getattr(settings, 'SYSTEM_CONFIGS', {}))
    
    def _get_public_configs_count(self):
        """获取公开配置数量"""
        # 这里可以从数据库或配置文件中获取
        return 5  # 模拟数据
    
    def _get_cache_status(self):
        """获取缓存状态"""
        try:
            cache.set('test_key', 'test_value', 10)
            test_value = cache.get('test_key')
            return 'active' if test_value == 'test_value' else 'inactive'
        except Exception:
            return 'error'
    
    @action(detail=False, methods=['get', 'post'])
    def role_templates(self, request):
        """角色模板管理"""
        if not self.check_admin_permission(request):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以管理角色模板'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            return self._get_role_templates(request)
        else:
            return self._create_role_template(request)
    
    def _get_role_templates(self, request):
        """获取角色模板列表"""
        role = request.query_params.get('role')
        
        queryset = RoleTemplate.objects.all()
        if role:
            queryset = queryset.filter(role=role)
        
        queryset = queryset.order_by('role', 'template_name')
        
        templates_data = []
        for template in queryset:
            template_data = {
                'id': template.pk,
                'role': template.role,
                'role_display': template.get_role_display(),
                'template_name': template.template_name,
                'description': template.description,
                'is_default': template.is_default,
                'is_active': template.is_active,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'template_fields': []
            }
            
            # 获取模板字段（这里需要根据实际的RoleTemplate模型结构调整）
            try:
                if hasattr(template, 'template_fields') and template.template_fields:
                    if isinstance(template.template_fields, str):
                        template_data['template_fields'] = json.loads(template.template_fields)
                    else:
                        template_data['template_fields'] = template.template_fields
            except (json.JSONDecodeError, AttributeError):
                template_data['template_fields'] = []
            
            templates_data.append(template_data)
        
        return Response({
            'success': True,
            'data': templates_data,
            'total': queryset.count()
        })
    
    def _create_role_template(self, request):
        """创建角色模板"""
        serializer = RoleTemplateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '数据验证失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                template = serializer.save()
                
                # 如果设置为默认模板，取消其他默认模板
                if template.is_default:
                    RoleTemplate.objects.filter(
                        role=template.role
                    ).exclude(pk=template.pk).update(is_default=False)
                
                return Response({
                    'success': True,
                    'message': '角色模板创建成功',
                    'data': {
                        'id': template.pk,
                        'template_name': template.template_name,
                        'role': template.role
                    }
                })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'角色模板创建失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get', 'post', 'put'])
    def role_extensions(self, request):
        """角色增项配置管理"""
        if not self.check_admin_permission(request):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以管理角色增项配置'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            return self._get_role_extensions(request)
        elif request.method == 'POST':
            return self._create_role_extension(request)
        else:
            return self._update_role_extensions(request)
    
    def _get_role_extensions(self, request):
        """获取角色增项配置"""
        role = request.query_params.get('role')
        include_inactive = request.query_params.get('include_inactive', 'false').lower() == 'true'
        
        queryset = RoleExtension.objects.all()
        if role:
            queryset = queryset.filter(role=role)
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        queryset = queryset.order_by('role', 'sort_order', 'field_name')
        
        extensions_data = []
        for extension in queryset:
            extension_data = {
                'id': extension.pk,
                'role': extension.role,
                'role_display': extension.get_role_display(),
                'field_name': extension.field_name,
                'field_label': extension.field_label,
                'field_type': extension.field_type,
                'field_options': extension.field_options,
                'default_value': extension.default_value,
                'is_required': extension.is_required,
                'is_active': extension.is_active,
                'sort_order': extension.sort_order,
                'help_text': extension.help_text,
                'validation_rules': extension.validation_rules
            }
            
            # 获取使用此增项的用户数量
            usage_count = UserExtensionData.objects.filter(
                role_extension=extension
            ).count()
            extension_data['usage_count'] = usage_count
            
            extensions_data.append(extension_data)
        
        # 按角色分组
        grouped_data = {}
        for ext in extensions_data:
            role_key = ext['role']
            if role_key not in grouped_data:
                grouped_data[role_key] = {
                    'role': role_key,
                    'role_display': ext['role_display'],
                    'extensions': []
                }
            grouped_data[role_key]['extensions'].append(ext)
        
        return Response({
            'success': True,
            'data': {
                'by_role': list(grouped_data.values()),
                'all_extensions': extensions_data
            },
            'total': len(extensions_data)
        })
    
    def _create_role_extension(self, request):
        """创建角色增项配置"""
        try:
            with transaction.atomic():
                extension_data = request.data
                
                # 验证必要字段
                required_fields = ['role', 'field_name', 'field_label', 'field_type']
                for field in required_fields:
                    if field not in extension_data:
                        return Response({
                            'success': False,
                            'message': f'缺少必要字段：{field}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # 检查字段名是否已存在
                existing = RoleExtension.objects.filter(
                    role=extension_data['role'],
                    field_name=extension_data['field_name']
                ).exists()
                
                if existing:
                    return Response({
                        'success': False,
                        'message': '该角色下已存在相同的字段名'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 创建增项配置
                extension = RoleExtension.objects.create(
                    role=extension_data['role'],
                    field_name=extension_data['field_name'],
                    field_label=extension_data['field_label'],
                    field_type=extension_data['field_type'],
                    field_options=extension_data.get('field_options', ''),
                    default_value=extension_data.get('default_value', ''),
                    is_required=extension_data.get('is_required', False),
                    is_active=extension_data.get('is_active', True),
                    sort_order=extension_data.get('sort_order', 0),
                    help_text=extension_data.get('help_text', ''),
                    validation_rules=extension_data.get('validation_rules', '')
                )
                
                return Response({
                    'success': True,
                    'message': '角色增项配置创建成功',
                    'data': {
                        'id': extension.pk,
                        'field_name': extension.field_name,
                        'field_label': extension.field_label,
                        'role': extension.role
                    }
                })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'创建失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_role_extensions(self, request):
        """批量更新角色增项配置"""
        serializer = RoleExtensionConfigSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '数据验证失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            with transaction.atomic():
                role = validated_data['role']
                extensions_config = validated_data['extensions']
                
                # 获取现有的增项配置
                existing_extensions = {ext.field_name: ext for ext in 
                                     RoleExtension.objects.filter(role=role)}
                
                updated_count = 0
                created_count = 0
                
                for ext_config in extensions_config:
                    field_name = ext_config.get('field_name')
                    
                    if field_name in existing_extensions:
                        # 更新现有配置
                        extension = existing_extensions[field_name]
                        for key, value in ext_config.items():
                            if hasattr(extension, key):
                                setattr(extension, key, value)
                        extension.save()
                        updated_count += 1
                    else:
                        # 创建新配置
                        RoleExtension.objects.create(
                            role=role,
                            **ext_config
                        )
                        created_count += 1
                
                return Response({
                    'success': True,
                    'message': f'配置更新完成：更新{updated_count}个，新增{created_count}个',
                    'updated_count': updated_count,
                    'created_count': created_count
                })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'配置更新失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def sync_role_extensions(self, request):
        """同步角色增项配置到用户"""
        if not self.check_admin_permission(request):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以同步角色增项配置'
            }, status=status.HTTP_403_FORBIDDEN)
        
        role = request.data.get('role')
        force_update = request.data.get('force_update', False)
        
        if not role:
            return Response({
                'success': False,
                'message': '请指定要同步的角色'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # 获取该角色的所有用户
                users = CustomUser.objects.filter(role=role, is_active=True)
                
                # 获取该角色的增项配置
                role_extensions = RoleExtension.objects.filter(
                    role=role, 
                    is_active=True
                )
                
                sync_results = []
                
                for user in users:
                    user_result = {
                        'user_id': user.pk,
                        'username': user.username,
                        'synced_extensions': [],
                        'skipped_extensions': []
                    }
                    
                    for role_ext in role_extensions:
                        # 检查用户是否已有此增项数据
                        existing_data = UserExtensionData.objects.filter(
                            user=user,
                            role_extension=role_ext
                        ).first()
                        
                        if not existing_data or force_update:
                            if existing_data and force_update:
                                # 更新现有数据
                                if role_ext.default_value:
                                    existing_data.field_value = role_ext.default_value
                                    existing_data.save()
                                    user_result['synced_extensions'].append({
                                        'field_name': role_ext.field_name,
                                        'action': 'updated'
                                    })
                            else:
                                # 创建新数据
                                UserExtensionData.objects.create(
                                    user=user,
                                    role_extension=role_ext,
                                    field_value=role_ext.default_value or ''
                                )
                                user_result['synced_extensions'].append({
                                    'field_name': role_ext.field_name,
                                    'action': 'created'
                                })
                        else:
                            user_result['skipped_extensions'].append({
                                'field_name': role_ext.field_name,
                                'reason': 'already_exists'
                            })
                    
                    sync_results.append(user_result)
                
                total_synced = sum(len(r['synced_extensions']) for r in sync_results)
                total_skipped = sum(len(r['skipped_extensions']) for r in sync_results)
                
                return Response({
                    'success': True,
                    'message': f'同步完成：处理{len(sync_results)}个用户，同步{total_synced}个增项，跳过{total_skipped}个',
                    'data': {
                        'role': role,
                        'processed_users': len(sync_results),
                        'total_synced': total_synced,
                        'total_skipped': total_skipped,
                        'details': sync_results
                    }
                })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'同步失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def system_health(self, request):
        """系统健康检查"""
        health_data = {
            'database': self._check_database_health(),
            'cache': self._check_cache_health(),
            'user_data_integrity': self._check_user_data_integrity(),
            'extension_data_integrity': self._check_extension_data_integrity()
        }
        
        overall_status = 'healthy' if all(
            check['status'] == 'ok' for check in health_data.values()
        ) else 'warning'
        
        return Response({
            'success': True,
            'overall_status': overall_status,
            'checks': health_data,
            'check_time': datetime.now().isoformat()
        })
    
    def _check_database_health(self):
        """检查数据库健康状态"""
        try:
            CustomUser.objects.count()
            return {'status': 'ok', 'message': '数据库连接正常'}
        except Exception as e:
            return {'status': 'error', 'message': f'数据库连接异常：{str(e)}'}
    
    def _check_cache_health(self):
        """检查缓存健康状态"""
        try:
            test_key = 'health_check_test'
            cache.set(test_key, 'test_value', 10)
            value = cache.get(test_key)
            if value == 'test_value':
                cache.delete(test_key)
                return {'status': 'ok', 'message': '缓存工作正常'}
            else:
                return {'status': 'warning', 'message': '缓存读写异常'}
        except Exception as e:
            return {'status': 'error', 'message': f'缓存连接异常：{str(e)}'}
    
    def _check_user_data_integrity(self):
        """检查用户数据完整性"""
        try:
            # 检查是否有用户没有对应的角色增项数据
            issues = []
            
            for role_code, role_name in RoleService.get_role_choices(include_empty=False):
                users_count = CustomUser.objects.filter(role=role_code, is_active=True).count()
                required_extensions = RoleExtension.objects.filter(
                    role=role_code, 
                    is_required=True, 
                    is_active=True
                ).count()
                
                if users_count > 0 and required_extensions > 0:
                    # 检查有多少用户缺少必需的增项数据
                    users_with_incomplete_data = 0
                    for user in CustomUser.objects.filter(role=role_code, is_active=True):
                        user_extensions = UserExtensionData.objects.filter(
                            user=user,
                            role_extension__is_required=True,
                            role_extension__is_active=True
                        ).count()
                        
                        if user_extensions < required_extensions:
                            users_with_incomplete_data += 1
                    
                    if users_with_incomplete_data > 0:
                        issues.append(f'{role_name}角色有{users_with_incomplete_data}个用户缺少必需的增项数据')
            
            if issues:
                return {
                    'status': 'warning',
                    'message': '发现数据完整性问题',
                    'issues': issues
                }
            else:
                return {'status': 'ok', 'message': '用户数据完整性正常'}
        
        except Exception as e:
            return {'status': 'error', 'message': f'数据完整性检查失败：{str(e)}'}
    
    def _check_extension_data_integrity(self):
        """检查增项数据完整性"""
        try:
            # 检查是否有孤立的增项数据（对应的用户或增项配置已删除）
            orphaned_data = UserExtensionData.objects.filter(
                user__isnull=True
            ).count()
            
            inactive_extension_data = UserExtensionData.objects.filter(
                role_extension__is_active=False
            ).count()
            
            issues = []
            if orphaned_data > 0:
                issues.append(f'发现{orphaned_data}条孤立的增项数据')
            
            if inactive_extension_data > 0:
                issues.append(f'发现{inactive_extension_data}条关联到已禁用增项配置的数据')
            
            if issues:
                return {
                    'status': 'warning',
                    'message': '发现增项数据问题',
                    'issues': issues
                }
            else:
                return {'status': 'ok', 'message': '增项数据完整性正常'}
        
        except Exception as e:
            return {'status': 'error', 'message': f'增项数据完整性检查失败：{str(e)}'}