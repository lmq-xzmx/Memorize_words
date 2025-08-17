from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from guardian.shortcuts import get_objects_for_user
from django.apps import apps
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
        # 跳过WebSocket请求 - WebSocket请求由ASGI处理，不应该被HTTP中间件拦截
        if hasattr(request, 'META') and request.META.get('HTTP_UPGRADE') == 'websocket':
            return self.get_response(request)
        
        # 检查是否需要权限验证
        if self.should_exempt(request):
            return self.get_response(request)
        
        # 对于API请求，让DRF处理认证和权限
        if request.path.startswith('/api/') or request.path.startswith('/permissions/api/') or request.path.startswith('/permissions/optimized/api/'):
            return self.get_response(request)
        
        # 检查用户是否已登录
        if isinstance(request.user, AnonymousUser):
            return redirect('accounts:login')
        
        # 执行权限检查
        if not self.check_permissions(request):
            logger.warning(f"Access denied for user {request.user.username} to {request.path}")
            return HttpResponseForbidden("您没有访问此页面的权限".encode('utf-8'))
        
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
            RoleManagement = apps.get_model('permissions', 'RoleManagement')
            role_mgmt = RoleManagement.objects.get(role=user.role)
            if not role_mgmt.is_active:
                return False
            
            # 检查是否有admin相关权限
            all_permissions = role_mgmt.get_all_permissions()
            admin_permissions = [p for p in all_permissions if 'admin' in p.codename.lower()]
            
            return len(admin_permissions) > 0
        except Exception as e:
            if 'DoesNotExist' in str(type(e)):
                return user.is_staff
            logger.error(f"检查管理员权限时出错: {e}")
            return user.is_staff
    
    def check_api_access(self, request):
        """检查API访问权限"""
        user = request.user
        
        # API访问需要有效的角色
        try:
            RoleManagement = apps.get_model('permissions', 'RoleManagement')
            role_mgmt = RoleManagement.objects.get(role=user.role)
            return role_mgmt.is_active
        except Exception as e:
            if 'DoesNotExist' in str(type(e)):
                return False
            logger.error(f"检查API权限时出错: {e}")
            return False
    
    def check_teaching_access(self, request):
        """检查教学模块访问权限"""
        user = request.user
        
        # 教师和管理员可以访问教学模块
        allowed_roles = ['teacher', 'admin']
        
        if user.role in allowed_roles:
            try:
                RoleManagement = apps.get_model('permissions', 'RoleManagement')
                role_mgmt = RoleManagement.objects.get(role=user.role)
                return role_mgmt.is_active
            except Exception as e:
                if 'DoesNotExist' in str(type(e)):
                    return False
                logger.error(f"检查教学权限时出错: {e}")
                return False
        
        return False
    
    def check_default_access(self, request):
        """默认权限检查"""
        user = request.user
        
        # 检查用户角色是否激活
        try:
            RoleManagement = apps.get_model('permissions', 'RoleManagement')
            role_mgmt = RoleManagement.objects.get(role=user.role)
            return role_mgmt.is_active
        except Exception as e:
            if 'DoesNotExist' in str(type(e)):
                return True  # 如果没有角色管理配置，默认允许访问
            logger.error(f"检查默认权限时出错: {e}")
            return True


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


# WebSocket认证中间件
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
try:
    from channels.middleware import BaseMiddleware
    from channels.db import database_sync_to_async
    from rest_framework_simplejwt.tokens import UntypedToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    import jwt
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    BaseMiddleware = object
    database_sync_to_async = lambda f: f

from django.conf import settings

User = get_user_model()


if WEBSOCKET_AVAILABLE:
    class TokenAuthMiddleware:
        """
        WebSocket Token认证中间件
        从URL查询参数中获取token并验证用户身份
        """
        
        def __init__(self, inner):
            super().__init__(inner)
        
        async def __call__(self, scope, receive, send):
            # 只处理WebSocket连接
            if scope['type'] == 'websocket':
                # 从查询字符串中获取token
                query_string = scope.get('query_string', b'').decode()
                query_params = parse_qs(query_string)
                token = query_params.get('token', [None])[0]
                
                if token:
                    user = await self.get_user_from_token(token)
                    scope['user'] = user
                else:
                    scope['user'] = self.get_anonymous_user()
            
            return await self.inner(scope, receive, send)
        
        def get_anonymous_user(self):
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()
        
        @database_sync_to_async
        def get_user_from_token(self, token):
            """
            从token获取用户
            """
            try:
                # 简单的token验证
                import jwt
                from django.conf import settings
                
                # 解码token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                
                if user_id:
                    user = User.objects.get(id=user_id)
                    if user.is_active:
                        logger.info(f"WebSocket token认证成功: 用户 {user.username}")
                        return user
                    else:
                        logger.warning(f"WebSocket token认证失败: 用户 {user.username} 已被禁用")
                
            except Exception as e:
                logger.warning(f"WebSocket token认证失败: {e}")
            
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()
else:
    class TokenAuthMiddleware:
        def __init__(self, inner):
            self.inner = inner
        
        def __call__(self, scope, receive, send):
            return self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    """
    Token认证中间件栈
    """
    return TokenAuthMiddleware(inner)