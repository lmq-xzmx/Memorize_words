from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import (
    CustomUser, UserRole, RoleExtension, UserExtensionData,
    LearningProfile, UserLoginLog
)
from .serializers import UserSerializer
from rest_framework import serializers
import csv
import json
import io
from datetime import datetime, timedelta
from apps.accounts.services.role_service import RoleService


class UserImportSerializer(serializers.Serializer):
    """用户导入序列化器"""
    username = serializers.CharField(max_length=150)
    real_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=RoleService.get_role_choices(include_empty=False))
    password = serializers.CharField(max_length=128, required=False)
    is_active = serializers.BooleanField(default=True)
    extensions = serializers.DictField(child=serializers.CharField(), required=False)


class UserExportSerializer(serializers.ModelSerializer):
    """用户导出序列化器"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    extensions = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'real_name', 'email', 'phone', 
            'role', 'role_display', 'is_active', 'date_joined', 
            'last_login', 'extensions'
        ]
    
    def get_extensions(self, obj):
        """获取用户增项数据"""
        extensions = UserExtensionData.objects.filter(user=obj).select_related('role_extension')
        return {
            ext.role_extension.field_name: {
                'label': ext.role_extension.field_label,
                'value': ext.field_value,
                'type': ext.role_extension.field_type
            }
            for ext in extensions
        }


class UserRoleTransferSerializer(serializers.Serializer):
    """用户角色转换序列化器"""
    user_ids = serializers.ListField(child=serializers.IntegerField())
    source_role = serializers.ChoiceField(choices=RoleService.get_role_choices(include_empty=False))
    target_role = serializers.ChoiceField(choices=RoleService.get_role_choices(include_empty=False))
    transfer_extensions = serializers.BooleanField(default=True)
    backup_data = serializers.BooleanField(default=True)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)


class UserMergeSerializer(serializers.Serializer):
    """用户账号合并序列化器"""
    primary_user_id = serializers.IntegerField()
    secondary_user_ids = serializers.ListField(child=serializers.IntegerField())
    merge_extensions = serializers.BooleanField(default=True)
    merge_learning_profile = serializers.BooleanField(default=True)
    merge_login_logs = serializers.BooleanField(default=False)
    keep_secondary_accounts = serializers.BooleanField(default=False)


class EnhancedUserManagementViewSet(viewsets.ModelViewSet):
    """增强用户管理API - 实现通用用户信息统一管理"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        # 超级用户和管理员可以查看所有用户
        if user.is_superuser or user.role == UserRole.ADMIN:
            return CustomUser.objects.all()
        
        # 教师可以查看学生
        elif user.role == UserRole.TEACHER:
            return CustomUser.objects.filter(
                Q(role=UserRole.STUDENT) | Q(pk=user.pk)
            )
        
        # 家长可以查看自己和关联的学生
        elif user.role == UserRole.PARENT:
            # 这里可以根据实际业务逻辑调整
            return CustomUser.objects.filter(pk=user.pk)
        
        # 学生只能查看自己
        else:
            return CustomUser.objects.filter(pk=user.pk)
    
    def check_user_management_permission(self, request, target_user=None, action_type='view'):
        """检查用户管理权限"""
        if not request.user.is_authenticated:
            return False
        
        # 超级用户拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 管理员可以管理所有用户
        if request.user.role == UserRole.ADMIN:
            return True
        
        # 检查具体操作权限
        if target_user:
            # 用户可以管理自己的信息（除了角色变更）
            if target_user == request.user and action_type in ['view', 'update']:
                return True
            
            # 教师可以查看和部分管理学生
            if (request.user.role == UserRole.TEACHER and 
                target_user.role == UserRole.STUDENT and 
                action_type in ['view', 'update']):
                return True
        
        return False
    
    @action(detail=False, methods=['post'])
    def batch_import(self, request):
        """批量导入用户"""
        if not (request.user.is_superuser or request.user.role == UserRole.ADMIN):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以批量导入用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 支持CSV文件上传和JSON数据两种方式
        if 'file' in request.FILES:
            return self._import_from_csv(request)
        else:
            return self._import_from_json(request)
    
    def _import_from_csv(self, request):
        """从CSV文件导入用户"""
        csv_file = request.FILES['file']
        
        if not csv_file.name.endswith('.csv'):
            return Response({
                'success': False,
                'message': '请上传CSV格式文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 读取CSV文件
            file_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_data))
            
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # 处理增项数据
                        extensions = {}
                        user_data = {}
                        
                        for key, value in row.items():
                            if key.startswith('ext_'):
                                extensions[key[4:]] = value  # 移除'ext_'前缀
                            else:
                                user_data[key] = value
                        
                        # 验证用户数据
                        serializer = UserImportSerializer(data={
                            **user_data,
                            'extensions': extensions
                        })
                        
                        if serializer.is_valid():
                            # 创建用户
                            user = self._create_user_with_extensions(
                                serializer.validated_data
                            )
                            success_count += 1
                        else:
                            errors.append(f'第{row_num}行：{serializer.errors}')
                            error_count += 1
                    
                    except Exception as e:
                        errors.append(f'第{row_num}行：{str(e)}')
                        error_count += 1
            
            return Response({
                'success': True,
                'message': f'导入完成：成功{success_count}个，失败{error_count}个',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10]  # 只返回前10个错误
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'文件处理失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _import_from_json(self, request):
        """从JSON数据导入用户"""
        users_data = request.data.get('users', [])
        
        if not users_data:
            return Response({
                'success': False,
                'message': '请提供用户数据'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for index, user_data in enumerate(users_data):
                    try:
                        serializer = UserImportSerializer(data=user_data)
                        
                        if serializer.is_valid():
                            user = self._create_user_with_extensions(
                                serializer.validated_data
                            )
                            success_count += 1
                        else:
                            errors.append(f'用户{index + 1}：{serializer.errors}')
                            error_count += 1
                    
                    except Exception as e:
                        errors.append(f'用户{index + 1}：{str(e)}')
                        error_count += 1
            
            return Response({
                'success': True,
                'message': f'导入完成：成功{success_count}个，失败{error_count}个',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'导入失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_user_with_extensions(self, validated_data):
        """创建用户并设置增项数据"""
        extensions = validated_data.pop('extensions', {})
        
        # 创建用户
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data.get('password', 'temp123456'),
            real_name=validated_data.get('real_name', ''),
            phone=validated_data.get('phone', ''),
            role=validated_data['role'],
            is_active=validated_data.get('is_active', True)
        )
        
        # 设置增项数据
        if extensions:
            for field_name, field_value in extensions.items():
                try:
                    role_extension = RoleExtension.objects.get(
                        role=user.role,
                        field_name=field_name,
                        is_active=True
                    )
                    
                    UserExtensionData.objects.create(
                        user=user,
                        role_extension=role_extension,
                        field_value=field_value
                    )
                except RoleExtension.DoesNotExist:
                    pass  # 忽略不存在的增项字段
        
        return user
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出用户数据"""
        if not (request.user.is_superuser or request.user.role == UserRole.ADMIN):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以导出用户数据'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取查询参数
        role = request.query_params.get('role')
        format_type = request.query_params.get('format', 'json')  # json 或 csv
        include_extensions = request.query_params.get('include_extensions', 'true').lower() == 'true'
        
        # 构建查询集
        queryset = self.get_queryset()
        if role:
            queryset = queryset.filter(role=role)
        
        queryset = queryset.filter(is_active=True).order_by('role', 'username')
        
        if format_type == 'csv':
            return self._export_to_csv(queryset, include_extensions)
        else:
            return self._export_to_json(queryset, include_extensions)
    
    def _export_to_csv(self, queryset, include_extensions):
        """导出为CSV格式"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # 写入表头
        headers = ['用户名', '真实姓名', '邮箱', '手机', '角色', '状态', '注册时间', '最后登录']
        
        if include_extensions:
            # 获取所有可能的增项字段
            all_extensions = set()
            for user in queryset:
                extensions = UserExtensionData.objects.filter(user=user).select_related('role_extension')
                for ext in extensions:
                    all_extensions.add(f'ext_{ext.role_extension.field_name}')
            
            headers.extend(sorted(all_extensions))
        
        writer.writerow(headers)
        
        # 写入数据
        for user in queryset:
            row = [
                user.username,
                user.real_name,
                user.email,
                user.phone,
                user.get_role_display(),
                '激活' if user.is_active else '禁用',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
            ]
            
            if include_extensions:
                # 获取用户增项数据
                extensions = UserExtensionData.objects.filter(user=user).select_related('role_extension')
                extension_dict = {f'ext_{ext.role_extension.field_name}': ext.field_value for ext in extensions}
                
                for header in headers[8:]:  # 从增项字段开始
                    row.append(extension_dict.get(header, ''))
            
            writer.writerow(row)
        
        return response
    
    def _export_to_json(self, queryset, include_extensions):
        """导出为JSON格式"""
        serializer = UserExportSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'total': queryset.count(),
            'export_time': datetime.now().isoformat(),
            'include_extensions': include_extensions
        })
    
    @action(detail=False, methods=['post'])
    def role_transfer(self, request):
        """用户角色转换"""
        if not (request.user.is_superuser or request.user.role == UserRole.ADMIN):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以进行角色转换'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserRoleTransferSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '数据验证失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            with transaction.atomic():
                users = CustomUser.objects.filter(
                    id__in=validated_data['user_ids'],
                    role=validated_data['source_role'],
                    is_active=True
                )
                
                if not users.exists():
                    return Response({
                        'success': False,
                        'message': '未找到符合条件的用户'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                transfer_results = []
                
                for user in users:
                    result = self._transfer_user_role(
                        user,
                        validated_data['target_role'],
                        validated_data.get('transfer_extensions', True),
                        validated_data.get('backup_data', True)
                    )
                    transfer_results.append(result)
                
                success_count = sum(1 for r in transfer_results if r['success'])
                
                return Response({
                    'success': True,
                    'message': f'角色转换完成：成功{success_count}个，失败{len(transfer_results) - success_count}个',
                    'results': transfer_results
                })
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'角色转换失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _transfer_user_role(self, user, target_role, transfer_extensions, backup_data):
        """转换单个用户的角色"""
        try:
            old_role = user.role
            
            # 备份原始数据
            if backup_data:
                backup_data = {
                    'old_role': old_role,
                    'transfer_time': datetime.now().isoformat(),
                    'extensions': {}
                }
                
                if transfer_extensions:
                    extensions = UserExtensionData.objects.filter(user=user)
                    for ext in extensions:
                        backup_data['extensions'][ext.role_extension.field_name] = {
                            'value': ext.field_value,
                            'field_label': ext.role_extension.field_label
                        }
                
                # 可以将备份数据存储到用户的notes字段或单独的备份表
                user.notes = f"{user.notes}\n[角色转换备份] {json.dumps(backup_data, ensure_ascii=False)}"
            
            # 更新用户角色
            user.role = target_role
            user.save()
            
            # 处理增项数据
            if transfer_extensions:
                # 删除旧角色的增项数据
                UserExtensionData.objects.filter(user=user).delete()
                
                # 为新角色创建默认增项数据
                new_role_extensions = RoleExtension.objects.filter(
                    role=target_role,
                    is_active=True
                )
                
                for role_ext in new_role_extensions:
                    if role_ext.default_value:
                        UserExtensionData.objects.create(
                            user=user,
                            role_extension=role_ext,
                            field_value=role_ext.default_value
                        )
            
            return {
                'success': True,
                'user_id': user.pk,
                'username': user.username,
                'old_role': old_role,
                'new_role': target_role,
                'message': '角色转换成功'
            }
        
        except Exception as e:
            return {
                'success': False,
                'user_id': user.pk,
                'username': user.username,
                'message': f'角色转换失败：{str(e)}'
            }
    
    @action(detail=False, methods=['post'])
    def merge_accounts(self, request):
        """合并用户账号"""
        if not (request.user.is_superuser or request.user.role == UserRole.ADMIN):
            return Response({
                'success': False,
                'message': '权限不足，只有管理员可以合并用户账号'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserMergeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '数据验证失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # 获取主账号
                primary_user = CustomUser.objects.get(
                    id=validated_data['primary_user_id'],
                    is_active=True
                )
                
                # 获取待合并账号
                secondary_users = CustomUser.objects.filter(
                    id__in=validated_data['secondary_user_ids'],
                    is_active=True
                ).exclude(id=primary_user.pk)
                
                if not secondary_users.exists():
                    return Response({
                        'success': False,
                        'message': '未找到有效的待合并账号'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                merge_results = []
                
                for secondary_user in secondary_users:
                    result = self._merge_user_account(
                        primary_user,
                        secondary_user,
                        validated_data
                    )
                    merge_results.append(result)
                
                success_count = sum(1 for r in merge_results if r['success'])
                
                return Response({
                    'success': True,
                    'message': f'账号合并完成：成功{success_count}个，失败{len(merge_results) - success_count}个',
                    'primary_user': {
                        'id': primary_user.pk,
                        'username': primary_user.username,
                        'real_name': primary_user.real_name
                    },
                    'results': merge_results
                })
        
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': '主账号不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'账号合并失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _merge_user_account(self, primary_user, secondary_user, options):
        """合并单个用户账号"""
        try:
            # 合并增项数据
            if options.get('merge_extensions', True):
                secondary_extensions = UserExtensionData.objects.filter(user=secondary_user)
                for ext in secondary_extensions:
                    # 检查主账号是否已有相同增项
                    existing_ext = UserExtensionData.objects.filter(
                        user=primary_user,
                        role_extension=ext.role_extension
                    ).first()
                    
                    if not existing_ext:
                        # 转移增项数据到主账号
                        ext.user = primary_user
                        ext.save()
                    else:
                        # 如果主账号已有数据，可以选择保留或合并
                        if not existing_ext.field_value and ext.field_value:
                            existing_ext.field_value = ext.field_value
                            existing_ext.save()
            
            # 合并学习档案
            if options.get('merge_learning_profile', True):
                try:
                    secondary_profile = LearningProfile.objects.get(user=secondary_user)
                    primary_profile, created = LearningProfile.objects.get_or_create(
                        user=primary_user,
                        defaults={
                            'total_study_time': 0,
                            'completed_lessons': 0,
                            'current_streak': 0,
                            'max_streak': 0
                        }
                    )
                    
                    # 合并学习数据
                    primary_profile.total_study_time += secondary_profile.total_study_time
                    primary_profile.completed_lessons += secondary_profile.completed_lessons
                    primary_profile.max_streak = max(primary_profile.max_streak, secondary_profile.max_streak)
                    primary_profile.save()
                    
                except LearningProfile.DoesNotExist:
                    pass
            
            # 合并登录日志
            if options.get('merge_login_logs', False):
                UserLoginLog.objects.filter(username=secondary_user.username).update(
                    username=primary_user.username
                )
            
            # 处理次要账号
            if not options.get('keep_secondary_accounts', False):
                # 删除次要账号
                secondary_user.delete()
            else:
                # 禁用次要账号
                secondary_user.is_active = False
                secondary_user.username = f"{secondary_user.username}_merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                secondary_user.save()
            
            return {
                'success': True,
                'secondary_user_id': secondary_user.pk,
                'secondary_username': secondary_user.username,
                'message': '账号合并成功'
            }
        
        except Exception as e:
            return {
                'success': False,
                'secondary_user_id': secondary_user.pk,
                'secondary_username': secondary_user.username,
                'message': f'账号合并失败：{str(e)}'
            }
    
    @action(detail=False, methods=['get'])
    def advanced_statistics(self, request):
        """高级用户统计"""
        # 基础统计
        total_users = CustomUser.objects.filter(is_active=True).count()
        
        # 角色分布
        role_distribution = {}
        for role_code, role_name in RoleService.get_role_choices(include_empty=False):
            count = CustomUser.objects.filter(role=role_code, is_active=True).count()
            role_distribution[role_code] = {
                'name': role_name,
                'count': count,
                'percentage': round((count / max(total_users, 1)) * 100, 2)
            }
        
        # 注册趋势（最近30天）
        registration_trend = []
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            count = CustomUser.objects.filter(
                date_joined__date=date,
                is_active=True
            ).count()
            registration_trend.append({
                'date': date.isoformat(),
                'count': count
            })
        
        # 活跃度统计
        active_users_7d = CustomUser.objects.filter(
            last_login__gte=datetime.now() - timedelta(days=7),
            is_active=True
        ).count()
        
        active_users_30d = CustomUser.objects.filter(
            last_login__gte=datetime.now() - timedelta(days=30),
            is_active=True
        ).count()
        
        # 增项完整度统计
        extension_completeness = {}
        for role_code, role_name in RoleService.get_role_choices(include_empty=False):
            users_with_role = CustomUser.objects.filter(role=role_code, is_active=True)
            if users_with_role.exists():
                total_extensions = RoleExtension.objects.filter(role=role_code, is_active=True).count()
                if total_extensions > 0:
                    users_with_complete_extensions = 0
                    for user in users_with_role:
                        user_extensions = UserExtensionData.objects.filter(user=user).count()
                        if user_extensions >= total_extensions:
                            users_with_complete_extensions += 1
                    
                    completeness_rate = round((users_with_complete_extensions / users_with_role.count()) * 100, 2)
                else:
                    completeness_rate = 100
                
                extension_completeness[role_code] = {
                    'name': role_name,
                    'total_users': users_with_role.count(),
                    'complete_users': users_with_complete_extensions if total_extensions > 0 else users_with_role.count(),
                    'completeness_rate': completeness_rate
                }
        
        return Response({
            'success': True,
            'data': {
                'overview': {
                    'total_users': total_users,
                    'active_users_7d': active_users_7d,
                    'active_users_30d': active_users_30d,
                    'activity_rate_7d': round((active_users_7d / max(total_users, 1)) * 100, 2),
                    'activity_rate_30d': round((active_users_30d / max(total_users, 1)) * 100, 2)
                },
                'role_distribution': role_distribution,
                'registration_trend': list(reversed(registration_trend)),
                'extension_completeness': extension_completeness
            }
        })