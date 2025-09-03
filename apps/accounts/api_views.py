from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.db.models import Q, Count, QuerySet
from django.utils import timezone
from datetime import timedelta
from typing import Type, Union, Any, Dict
from rest_framework.serializers import BaseSerializer
from django.core.exceptions import ValidationError
from .validators import EnhancedUserValidator, RoleExtensionValidator
from .performance import UserQueryOptimizer, RoleExtensionCacheManager

from .models import CustomUser, UserRole, LearningProfile, UserLoginLog, RoleExtension, UserExtensionData
from .services.role_service import RoleService
from .serializers import (
    UserSerializer, UserProfileSerializer, UserListSerializer,
    LoginSerializer, ChangePasswordSerializer, LearningProfileSerializer,
    UserLoginLogSerializer, RegisterSerializer, RoleExtensionSerializer,
    UserExtensionDataSerializer, RoleExtensionListSerializer, RegisterWithExtensionSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class CustomAuthToken(ObtainAuthToken):
    """自定义认证Token视图"""
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # 记录登录日志
        UserLoginLog.objects.create(
            username=user.username,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '') or '',
            login_success=True
        )
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'real_name': user.real_name,
            'role': user.role,
            'email': user.email
        })
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or ''


class RegisterViewSet(viewsets.GenericViewSet):
    """用户注册视图集"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request):
        """用户注册"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 创建Token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': '注册成功',
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'real_name': user.real_name,
            'role': user.role
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def roles(self, request):
        """获取角色列表"""
        try:
            roles = RoleService.get_role_choices()
            return Response({
                'roles': roles,
                'message': '角色列表获取成功'
            })
        except Exception as e:
            return Response(
                {'error': f'获取角色列表失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def role_extensions(self, request):
        """获取角色增项配置"""
        role = request.query_params.get('role')
        if not role:
            return Response({'error': '请提供角色参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        extensions = RoleExtension.objects.filter(
            role=role,
            is_active=True,
            show_in_frontend_register=True
        ).order_by('sort_order', 'field_name')
        
        extension_data = []
        for ext in extensions:
            data = {
                'field_name': ext.field_name,
                'field_label': ext.field_label,
                'field_type': ext.field_type,
                'is_required': ext.is_required,
                'help_text': ext.help_text,
                'default_value': ext.default_value,
                'validation_rules': ext.get_validation_rules()
            }
            
            # 如果是选择字段，添加选择项
            if ext.field_type == 'choice':
                data['choices'] = ext.get_choices_list()
            
            extension_data.append(data)
        
        return Response({
            'role': role,
            'extensions': extension_data
        })
    
    @action(detail=False, methods=['post'])
    def register_with_extensions(self, request):
        """带增项的用户注册"""
        from .serializers import DynamicRegisterSerializer
        
        serializer = DynamicRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 创建Token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': '注册成功'
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'grade_level']
    search_fields = ['username', 'real_name', 'email', 'phone']
    ordering_fields = ['date_joined', 'last_login', 'username']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return UserProfileSerializer
        return UserSerializer
    
    def get_permissions(self):
        """根据动作设置权限"""
        if self.action in ['create', 'destroy', 'list']:
            # 只有管理员可以创建、删除用户和查看用户列表
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """创建用户时进行额外验证"""
        # 使用增强验证器
        user_data = request.data
        try:
            EnhancedUserValidator.validate_username(user_data.get('username'))
            EnhancedUserValidator.validate_real_name(user_data.get('real_name'))
            EnhancedUserValidator.validate_email(user_data.get('email'))
            EnhancedUserValidator.validate_phone(user_data.get('phone'))
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 检查权限
        user_role = getattr(request.user, 'role', None)
        is_superuser = getattr(request.user, 'is_superuser', False)
        if not (is_superuser or user_role == UserRole.ADMIN):
            return Response(
                {'error': '权限不足'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        """根据用户角色过滤查询集"""
        user = self.request.user
        is_superuser = getattr(user, 'is_superuser', False)
        if is_superuser:
            return CustomUser.objects.all()
        user_role = getattr(user, 'role', None)
        if user_role == UserRole.ADMIN:
            return CustomUser.objects.all()
        else:
            # 非管理员只能查看自己的信息
            user_id = getattr(user, 'id', None)
            if user_id is not None:
                return CustomUser.objects.filter(id=user_id)
            return CustomUser.objects.none()
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """获取或更新当前用户个人资料"""
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        else:
            serializer = UserProfileSerializer(
                request.user, 
                data=request.data, 
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': '密码修改成功'})
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出"""
        try:
            # 删除用户的Token
            request.user.auth_token.delete()
        except Token.DoesNotExist:
            pass
        
        return Response({'message': '登出成功'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """用户统计信息（使用缓存优化）"""
        user_role = getattr(request.user, 'role', None)
        if user_role != UserRole.ADMIN:
            return Response(
                {'error': '权限不足'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 使用优化的统计查询
        stats = UserQueryOptimizer.get_user_statistics()
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def students(self, request):
        """获取学生列表（用于选择器等场景）"""
        # 基础查询：只获取学生角色的用户
        queryset = CustomUser.objects.filter(
            role=UserRole.STUDENT,
            is_active=True
        ).select_related().order_by('real_name', 'username')
        
        # 搜索过滤
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(real_name__icontains=search)
            )
        
        # 年级过滤
        grade = request.query_params.get('grade')
        if grade:
            queryset = queryset.filter(grade_level=grade)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 格式化数据
            students_data = []
            for student in page:
                students_data.append({
                    'id': student.pk,
                    'username': student.username,
                    'real_name': student.real_name or student.username,
                    'grade': getattr(student, 'grade_level', '') or '',
                    'display_name': f"{student.real_name or student.username} ({student.username})"
                })
            
            return self.get_paginated_response(students_data)
        
        # 无分页情况
        students_data = []
        for student in queryset:
            students_data.append({
                'id': student.pk,
                'username': student.username,
                'real_name': student.real_name or student.username,
                'grade': getattr(student, 'grade', '') or '',
                'display_name': f"{student.real_name or student.username} ({student.username})"
            })
        
        return Response(students_data)


class LearningProfileViewSet(viewsets.ModelViewSet):
    """学习档案视图集"""
    serializer_class = LearningProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的学习档案"""
        user = self.request.user
        is_superuser = getattr(user, 'is_superuser', False)
        if is_superuser:
            return LearningProfile.objects.all()
        user_role = getattr(user, 'role', None)
        if user_role == UserRole.ADMIN:
            return LearningProfile.objects.all()
        return LearningProfile.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """创建学习档案时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post', 'put', 'patch'])
    def my_profile(self, request):
        """获取或更新我的学习档案"""
        try:
            profile = LearningProfile.objects.get(user=request.user)
            if request.method == 'GET':
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            else:
                serializer = self.get_serializer(
                    profile,
                    data=request.data,
                    partial=request.method in ['PATCH', 'PUT']
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        except LearningProfile.DoesNotExist:
            if request.method == 'GET':
                return Response(
                    {'error': '学习档案不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                # 创建新的学习档案
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserLoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """用户登录日志视图集"""
    serializer_class = UserLoginLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_successful']
    ordering_fields = ['login_time']
    ordering = ['-login_time']
    
    def get_queryset(self):
        """根据用户角色过滤查询集"""
        user = self.request.user
        is_superuser = getattr(user, 'is_superuser', False)
        if is_superuser:
            return UserLoginLog.objects.all()
        user_role = getattr(user, 'role', None)
        if user_role == UserRole.ADMIN:
            return UserLoginLog.objects.all()
        else:
            # 普通用户只能查看自己的登录日志
            return UserLoginLog.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """获取我的登录日志"""
        logs = UserLoginLog.objects.filter(user=request.user).order_by('-login_time')[:10]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class StudentListViewSet(viewsets.ReadOnlyModelViewSet):
    """学生列表视图集 - 用于获取学生数据"""
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]  # 允许匿名访问
    authentication_classes = []  # 不需要认证
    
    def get_queryset(self):
        """获取所有学生用户"""
        return CustomUser.objects.filter(role=UserRole.STUDENT, is_active=True).order_by('real_name', 'username')
    
    @action(detail=False, methods=['get'])
    def for_select(self, request):
        """获取用于选择器的学生数据"""
        try:
            students = self.get_queryset()
            data = []
            
            for student in students:
                # 确保所有字段都有默认值
                student_data = {
                    'id': getattr(student, 'id', None),
                    'username': student.username or '',
                    'real_name': student.real_name or student.username or '',
                    'display_name': f"{student.real_name or student.username} ({student.username})",
                    'english_level': getattr(student, 'english_level', '') or '',
                    'grade': getattr(student, 'grade', '') or ''
                }
                data.append(student_data)
            
            # 添加调试信息
            print(f"StudentListViewSet.for_select: 返回 {len(data)} 名学生")
            
            return Response(data)
            
        except Exception as e:
            print(f"StudentListViewSet.for_select 错误: {str(e)}")
            return Response(
                {'error': '获取学生数据失败', 'detail': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RoleExtensionViewSet(viewsets.ModelViewSet):
    """角色增项视图集"""
    serializer_class = RoleExtensionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['role', 'field_type', 'is_active', 'show_in_frontend_register', 'show_in_backend_admin']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', 'created_at']
    
    def get_queryset(self):
        """根据用户角色过滤查询集"""
        user = self.request.user
        is_superuser = getattr(user, 'is_superuser', False)
        if is_superuser:
            return RoleExtension.objects.all()
        user_role = getattr(user, 'role', None)
        if user_role == UserRole.ADMIN:
            return RoleExtension.objects.all()
        else:
            # 普通用户只能查看激活的扩展字段
            return RoleExtension.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'list':
            return RoleExtensionListSerializer
        return RoleExtensionSerializer
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """根据角色获取扩展字段"""
        role = request.query_params.get('role')
        if not role:
            return Response(
                {'error': '请提供角色参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        extensions = RoleExtension.objects.filter(
            role=role,
            is_active=True
        ).order_by('sort_order')
        
        serializer = RoleExtensionListSerializer(extensions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def for_register(self, request):
        """获取用于注册的扩展字段"""
        role = request.query_params.get('role', 'student')
        
        extensions = RoleExtension.objects.filter(
            role=role,
            is_active=True,
            show_in_frontend_register=True
        ).order_by('sort_order')
        
        serializer = RoleExtensionListSerializer(extensions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def for_admin(self, request):
        """获取用于后台管理的扩展字段"""
        user_role = getattr(request.user, 'role', None)
        if user_role != UserRole.ADMIN:
            return Response(
                {'error': '权限不足'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        role = request.query_params.get('role')
        if not role:
            return Response(
                {'error': '请提供角色参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        extensions = RoleExtension.objects.filter(
            role=role,
            is_active=True,
            show_in_backend_admin=True
        ).order_by('sort_order')
        
        serializer = RoleExtensionListSerializer(extensions, many=True)
        return Response(serializer.data)


class UserExtensionDataViewSet(viewsets.ModelViewSet):
    """用户扩展数据视图集"""
    serializer_class = UserExtensionDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['extension__role', 'extension__field_type']
    
    def get_queryset(self):
        """根据用户角色过滤查询集"""
        user = self.request.user
        is_superuser = getattr(user, 'is_superuser', False)
        if is_superuser:
            return UserExtensionData.objects.all()
        user_role = getattr(user, 'role', None)
        if user_role == UserRole.ADMIN:
            return UserExtensionData.objects.all()
        else:
            # 普通用户只能查看自己的扩展数据
            return UserExtensionData.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """创建扩展数据时设置用户"""
        # 如果不是管理员，只能为自己创建数据
        user_role = getattr(self.request.user, 'role', None)
        if user_role != UserRole.ADMIN:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_data(self, request):
        """获取我的扩展数据"""
        user = request.user
        user_id = getattr(user, 'id', None)
        if user_id is not None:
            data = UserExtensionData.objects.filter(user=user)
        else:
            data = UserExtensionData.objects.none()
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """批量更新扩展数据"""
        extension_data = request.data.get('extension_data', {})
        user = request.user
        
        # 如果是管理员且指定了用户ID，可以更新其他用户的数据
        user_role = getattr(user, 'role', None)
        if user_role == UserRole.ADMIN:
            user_id = request.data.get('user_id')
            if user_id:
                try:
                    user = CustomUser.objects.get(id=user_id)
                except CustomUser.DoesNotExist:
                    return Response(
                        {'error': '用户不存在'},
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        updated_data = []
        for field_name, value in extension_data.items():
            try:
                extension = RoleExtension.objects.get(
                    role=user.role,
                    field_name=field_name,
                    is_active=True
                )
                
                data_obj, created = UserExtensionData.objects.update_or_create(
                    user=user,
                    extension=extension,
                    defaults={'value': value}
                )
                
                updated_data.append({
                    'field_name': field_name,
                    'value': value,
                    'created': created
                })
                
            except RoleExtension.DoesNotExist:
                continue
        
        return Response({
            'message': '扩展数据更新成功',
            'updated_data': updated_data
        })