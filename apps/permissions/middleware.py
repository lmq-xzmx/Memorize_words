from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from guardian.shortcuts import get_objects_for_user
from .models import RoleManagement
from .utils import RolePermissionChecker
import logging

logger = logging.getLogger(__name__)


class EnhancedRBACMiddleware:
    """
    增强的RBAC中间件 - 支持角色继承和对象级权限
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 不需要权限检查的路径
        self.exempt_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/admin/login/',
            '/admin/logout/',
            '/static/',
            '/media/',
            '/api/auth/',
            '/api/accounts/api/auth/',
            '/accounts/api/auth/',
            '/accounts/api/users/',  # 添加用户API路径
            '/accounts/api/',  # 添加所有accounts API路径
            '/api/teaching/learning-goals/',  # 允许匿名访问学习目标列表
        ]
        
        # 需要特殊处理的路径模式
        self.special_patterns = {
            '/admin/': self.check_admin_access,
            '/api/': self.check_api_access,
            '/teaching/': self.check_teaching_access,
        }
    
    def __call__(self, request):
        # 检查是否需要权限验证
        if self.should_exempt(request):
            return self.get_response(request)
        
        # 检查用户是否已登录
        if isinstance(request.user, AnonymousUser):
            return redirect('accounts:login')
        
        # 执行权限检查
        if not self.check_permissions(request):
            logger.warning(f"Access denied for user {request.user.username} to {request.path}")
            return HttpResponseForbidden("您没有访问此页面的权限")
        
        response = self.get_response(request)
        return response
    
    def should_exempt(self, request):
        """检查是否应该跳过权限检查"""
        path = request.path
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    def check_permissions(self, request):
        """主要权限检查逻辑"""
        path = request.path
        user = request.user
        
        # 超级用户直接通过
        if user.is_superuser:
            return True
        
        # 检查特殊路径模式
        for pattern, checker in self.special_patterns.items():
            if path.startswith(pattern):
                return checker(request)
        
        # 默认权限检查
        return self.check_default_access(request)
    
    def check_admin_access(self, request):
        """检查Django Admin访问权限"""
        user = request.user
        
        # 检查是否有admin访问权限
        if not (user.is_staff or user.is_superuser):
            return False
        
        # 获取用户角色管理对象
        try:
            role_mgmt = RoleManagement.objects.get(role=user.role)
            if not role_mgmt.is_active:
                return False
            
            # 检查是否有admin相关权限
            all_permissions = role_mgmt.get_all_permissions()
            admin_permissions = [p for p in all_permissions if 'admin' in p.codename.lower()]
            
            return len(admin_permissions) > 0
        except RoleManagement.DoesNotExist:
            return user.is_staff
    
    def check_api_access(self, request):
        """检查API访问权限"""
        user = request.user
        
        # API访问需要有效的角色
        try:
            role_mgmt = RoleManagement.objects.get(role=user.role)
            return role_mgmt.is_active
        except RoleManagement.DoesNotExist:
            return False
    
    def check_teaching_access(self, request):
        """检查教学模块访问权限"""
        user = request.user
        
        # 教师和管理员可以访问教学模块
        allowed_roles = ['teacher', 'admin']
        
        if user.role in allowed_roles:
            try:
                role_mgmt = RoleManagement.objects.get(role=user.role)
                return role_mgmt.is_active
            except RoleManagement.DoesNotExist:
                return False
        
        return False
    
    def check_default_access(self, request):
        """默认权限检查"""
        user = request.user
        
        # 检查用户角色是否激活
        try:
            role_mgmt = RoleManagement.objects.get(role=user.role)
            return role_mgmt.is_active
        except RoleManagement.DoesNotExist:
            return True  # 如果没有角色管理配置，默认允许访问


class ObjectPermissionMiddleware:
    """
    对象级权限中间件 - 与django-guardian集成
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 在请求中添加对象权限检查器
        request.object_permission_checker = ObjectPermissionChecker(request.user)
        
        response = self.get_response(request)
        return response


class ObjectPermissionChecker:
    """
    对象权限检查器
    """
    
    def __init__(self, user):
        self.user = user
    
    def has_perm(self, perm, obj=None):
        """检查用户是否对特定对象有权限"""
        if self.user.is_superuser:
            return True
        
        if obj is None:
            return self.user.has_perm(perm)
        
        # 使用guardian检查对象级权限
        from guardian.shortcuts import get_perms
        user_perms = get_perms(self.user, obj)
        
        return perm in user_perms
    
    def get_objects_with_perm(self, perm, klass):
        """获取用户有权限的对象列表"""
        if self.user.is_superuser:
            return klass.objects.all()
        
        return get_objects_for_user(self.user, perm, klass)