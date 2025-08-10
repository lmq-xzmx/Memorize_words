from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.db.models import Count, Q
from .models import (
    CustomUser, UserRole, RoleTemplate, RoleExtension, 
    UserExtensionData, RoleLevel, RoleUser, UserExtension
)
from apps.permissions.models import RoleMenuPermission, RoleGroupMapping
from .serializers import UserSerializer
from rest_framework import serializers
import json
from apps.accounts.services.role_service import RoleService


class UnifiedRoleManagementSerializer(serializers.Serializer):
    """统一角色管理序列化器"""
    role = serializers.ChoiceField(choices=RoleService.get_role_choices(include_empty=False))
    display_name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    user_count = serializers.IntegerField(read_only=True)
    extension_count = serializers.IntegerField(read_only=True)
    permissions = serializers.ListField(child=serializers.CharField(), read_only=True)
    hierarchy_level = serializers.IntegerField(read_only=True)
    can_manage_roles = serializers.ListField(child=serializers.CharField(), read_only=True)


class RoleExtensionConfigSerializer(serializers.ModelSerializer):
    """角色增项配置序列化器"""
    choices_list = serializers.SerializerMethodField()
    validation_rules_dict = serializers.SerializerMethodField()
    
    class Meta:
        model = RoleExtension
        fields = '__all__'
    
    def get_choices_list(self, obj):
        return obj.get_choices_list()
    
    def get_validation_rules_dict(self, obj):
        return obj.get_validation_rules()


class UserExtensionManagementSerializer(serializers.Serializer):
    """用户增项管理序列化器"""
    user_id = serializers.IntegerField()
    username = serializers.CharField(read_only=True)
    real_name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    extensions = serializers.DictField(child=serializers.CharField(), required=False)
    

class UnifiedRoleManagementViewSet(viewsets.ViewSet):
    """统一角色管理API - 实现通用用户信息统一管理和角色关联增项配置"""
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action in ['create', 'update', 'destroy', 'batch_operations']:
            # 只有管理员可以进行角色管理操作
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def check_role_management_permission(self, request, target_role=None):
        """检查角色管理权限"""
        if not request.user.is_authenticated:
            return False
        
        # 超级用户拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 管理员可以管理所有角色
        if request.user.role == UserRole.ADMIN:
            return True
        
        # 检查是否可以管理指定角色
        if target_role:
            return UserRole.can_manage_role(request.user.role, target_role)
        
        return False
    
    @action(detail=False, methods=['get'])
    def list_roles(self, request):
        """获取所有角色列表及统计信息"""
        roles_data = []
        
        for role_choice in RoleService.get_role_choices(include_empty=False):
            role_code, role_name = role_choice
            
            # 获取角色统计信息
            user_count = CustomUser.objects.filter(role=role_code, is_active=True).count()
            extension_count = RoleExtension.objects.filter(role=role_code, is_active=True).count()
            
            # 获取角色层级信息
            hierarchy = UserRole.get_role_hierarchy()
            role_enum = UserRole(role_code) if role_code in [choice[0] for choice in RoleService.get_role_choices(include_empty=False)] else None
            role_info = hierarchy.get(role_enum, {}) if role_enum else {}
            
            # 获取可管理的角色
            can_manage_roles = []
            for target_role, _ in RoleService.get_role_choices(include_empty=False):
                if UserRole.can_manage_role(role_code, target_role):
                    can_manage_roles.append(target_role)
            
            roles_data.append({
                'role': role_code,
                'display_name': role_name,
                'description': f'{role_name}角色，负责相关功能管理',
                'user_count': user_count,
                'extension_count': extension_count,
                'permissions': UserRole.get_role_permissions(role_code),
                'hierarchy_level': role_info.get('level', 0),
                'can_manage_roles': can_manage_roles
            })
        
        return Response({
            'success': True,
            'data': roles_data,
            'total': len(roles_data)
        })
    
    @action(detail=False, methods=['get'])
    def role_hierarchy(self, request):
        """获取角色层级关系"""
        hierarchy = UserRole.get_role_hierarchy()
        
        # 构建层级树结构
        hierarchy_tree = []
        for role_code, role_name in RoleService.get_role_choices(include_empty=False):
            role_enum = UserRole(role_code)
            role_info = hierarchy.get(role_enum, {})
            hierarchy_tree.append({
                'role': role_code,
                'name': role_name,
                'level': role_info.get('level', 0),
                'parent': role_info.get('parent'),
                'children': role_info.get('children', []),
                'user_count': CustomUser.objects.filter(role=role_code, is_active=True).count()
            })
        
        # 按层级排序
        hierarchy_tree.sort(key=lambda x: (x['level'], x['role']))
        
        return Response({
            'success': True,
            'data': hierarchy_tree
        })
    
    @action(detail=False, methods=['get'])
    def role_extensions(self, request):
        """获取角色增项配置"""
        role = request.query_params.get('role')
        
        if role and role not in [choice[0] for choice in RoleService.get_role_choices(include_empty=False)]:
            return Response({
                'success': False,
                'message': '无效的角色类型'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 构建查询条件
        queryset = RoleExtension.objects.filter(is_active=True)
        if role:
            queryset = queryset.filter(role=role)
        
        extensions = queryset.order_by('role', 'sort_order')
        serializer = RoleExtensionConfigSerializer(extensions, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'total': extensions.count()
        })
    
    @action(detail=False, methods=['post'])
    def create_role_extension(self, request):
        """创建角色增项配置"""
        if not self.check_role_management_permission(request):
            return Response({
                'success': False,
                'message': '权限不足，无法创建角色增项配置'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoleExtensionConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '角色增项配置创建成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def users_by_role(self, request):
        """按角色获取用户列表"""
        role = request.query_params.get('role')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        if not role:
            return Response({
                'success': False,
                'message': '请指定角色类型'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查权限
        if not self.check_role_management_permission(request, role):
            return Response({
                'success': False,
                'message': '权限不足，无法查看该角色用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取用户列表
        users = CustomUser.objects.filter(role=role, is_active=True).order_by('username')
        total = users.count()
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        users_page = users[start:end]
        
        # 序列化用户数据
        users_data = []
        for user in users_page:
            # 获取用户增项数据
            extensions = UserExtensionData.objects.filter(user=user).select_related('role_extension')
            extension_data = {}
            for ext in extensions:
                extension_data[ext.role_extension.field_name] = {
                    'label': ext.role_extension.field_label,
                    'value': ext.field_value,
                    'type': ext.role_extension.field_type
                }
            
            users_data.append({
                'id': user.pk,
                'username': user.username,
                'real_name': user.real_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'extensions': extension_data
            })
        
        return Response({
            'success': True,
            'data': users_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'pages': (total + page_size - 1) // page_size
            }
        })
    
    @action(detail=False, methods=['post'])
    def batch_assign_role(self, request):
        """批量分配用户角色"""
        if not self.check_role_management_permission(request):
            return Response({
                'success': False,
                'message': '权限不足，无法进行批量角色分配'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_ids = request.data.get('user_ids', [])
        target_role = request.data.get('target_role')
        
        if not user_ids or not target_role:
            return Response({
                'success': False,
                'message': '请提供用户ID列表和目标角色'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if target_role not in [choice[0] for choice in RoleService.get_role_choices(include_empty=False)]:
            return Response({
                'success': False,
                'message': '无效的角色类型'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否有权限管理目标角色
        if not self.check_role_management_permission(request, target_role):
            return Response({
                'success': False,
                'message': f'权限不足，无法分配{target_role}角色'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            with transaction.atomic():
                updated_users = CustomUser.objects.filter(
                    id__in=user_ids, 
                    is_active=True
                ).update(role=target_role)
                
                # 触发信号，自动分配组和同步角色数据
                for user in CustomUser.objects.filter(id__in=user_ids):
                    user.auto_assign_group()
                
                return Response({
                    'success': True,
                    'message': f'成功为{updated_users}个用户分配{target_role}角色',
                    'updated_count': updated_users
                })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'批量分配角色失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_update_extensions(self, request):
        """批量更新用户增项数据"""
        if not self.check_role_management_permission(request):
            return Response({
                'success': False,
                'message': '权限不足，无法进行批量增项更新'
            }, status=status.HTTP_403_FORBIDDEN)
        
        updates = request.data.get('updates', [])
        
        if not updates:
            return Response({
                'success': False,
                'message': '请提供更新数据'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for update_data in updates:
                    user_id = update_data.get('user_id')
                    extensions = update_data.get('extensions', {})
                    
                    try:
                        user = CustomUser.objects.get(id=user_id, is_active=True)
                        
                        # 检查是否有权限管理该用户的角色
                        if not self.check_role_management_permission(request, user.role):
                            errors.append(f'用户{user.username}：权限不足')
                            error_count += 1
                            continue
                        
                        # 更新增项数据
                        for field_name, field_value in extensions.items():
                            try:
                                role_extension = RoleExtension.objects.get(
                                    role=user.role,
                                    field_name=field_name,
                                    is_active=True
                                )
                                
                                UserExtensionData.objects.update_or_create(
                                    user=user,
                                    role_extension=role_extension,
                                    defaults={'field_value': field_value}
                                )
                            except RoleExtension.DoesNotExist:
                                errors.append(f'用户{user.username}：增项字段{field_name}不存在')
                                continue
                        
                        success_count += 1
                    
                    except CustomUser.DoesNotExist:
                        errors.append(f'用户ID{user_id}：用户不存在')
                        error_count += 1
                    except Exception as e:
                        errors.append(f'用户ID{user_id}：{str(e)}')
                        error_count += 1
                
                return Response({
                    'success': True,
                    'message': f'批量更新完成：成功{success_count}个，失败{error_count}个',
                    'success_count': success_count,
                    'error_count': error_count,
                    'errors': errors
                })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'批量更新失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def system_statistics(self, request):
        """获取系统统计信息"""
        # 用户统计
        total_users = CustomUser.objects.filter(is_active=True).count()
        role_stats = {}
        for role_code, role_name in RoleService.get_role_choices(include_empty=False):
            role_stats[role_code] = {
                'name': role_name,
                'count': CustomUser.objects.filter(role=role_code, is_active=True).count()
            }
        
        # 增项配置统计
        extension_stats = {}
        for role_code, role_name in RoleService.get_role_choices(include_empty=False):
            extension_count = RoleExtension.objects.filter(role=role_code, is_active=True).count()
            extension_stats[role_code] = {
                'name': role_name,
                'extension_count': extension_count
            }
        
        # 增项数据统计
        extension_data_count = UserExtensionData.objects.count()
        
        return Response({
            'success': True,
            'data': {
                'total_users': total_users,
                'role_statistics': role_stats,
                'extension_statistics': extension_stats,
                'total_extension_data': extension_data_count,
                'system_health': {
                    'roles_configured': len([r for r in role_stats.values() if r['count'] > 0]),
                    'extensions_configured': sum(e['extension_count'] for e in extension_stats.values()),
                    'data_completeness': round((extension_data_count / max(total_users, 1)) * 100, 2)
                }
            }
        })