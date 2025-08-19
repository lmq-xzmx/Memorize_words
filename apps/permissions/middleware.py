from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from guardian.shortcuts import get_objects_for_user
from django.apps import apps
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.urls import resolve
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .utils import RolePermissionChecker
import logging
import time
from typing import Optional, Dict, Any

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
    class TokenAuthMiddleware(BaseMiddleware):
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
                    # 允许匿名连接，特别是对于 /ws/permissions/anonymous 路径
                    scope['user'] = self.get_anonymous_user()
                    logger.info("WebSocket匿名连接已允许")
            
            return await self.inner(scope, receive, send)
        
        def get_anonymous_user(self):
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()
        
        @database_sync_to_async
        def get_user_from_token(self, token):
            """
            从token获取用户
            支持Django REST Framework Token认证
            """
            try:
                # 首先尝试Django REST Framework Token认证
                from rest_framework.authtoken.models import Token as DRFToken
                try:
                    token_obj = DRFToken.objects.get(key=token)
                    user = token_obj.user
                    if user.is_active:
                        logger.info(f"WebSocket DRF token认证成功: 用户 {user.username} (ID: {user.id})")
                        return user
                    else:
                        logger.warning(f"WebSocket token认证失败: 用户 {user.username} 已被禁用")
                        from django.contrib.auth.models import AnonymousUser
                        return AnonymousUser()
                except DRFToken.DoesNotExist:
                    logger.info("DRF Token不存在，尝试JWT认证")
                
                # 备用方案：JWT token认证
                import jwt
                from django.conf import settings
                
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                
                if user_id:
                    user = User.objects.get(id=user_id)
                    if user.is_active:
                        logger.info(f"WebSocket JWT token认证成功: 用户 {user.username} (ID: {user.id})")
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


class PermissionAuditMiddleware(MiddlewareMixin):
    """权限审计中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # 配置选项
        self.enabled = getattr(settings, 'PERMISSION_AUDIT_ENABLED', True)
        self.excluded_paths = getattr(settings, 'PERMISSION_AUDIT_EXCLUDED_PATHS', [
            '/static/',
            '/media/',
            '/favicon.ico',
            '/health/',
            '/ping/'
        ])
        self.excluded_users = getattr(settings, 'PERMISSION_AUDIT_EXCLUDED_USERS', [])
        self.log_anonymous = getattr(settings, 'PERMISSION_AUDIT_LOG_ANONYMOUS', False)
    
    def __call__(self, request):
        # 请求开始时间
        start_time = time.time()
        
        # 预处理
        self.process_request(request)
        
        # 处理请求
        response = self.get_response(request)
        
        # 后处理
        self.process_response(request, response, start_time)
        
        return response
    
    def process_request(self, request):
        """处理请求"""
        if not self.enabled or self._should_skip_audit(request):
            return None
        
        try:
            # 记录请求开始
            request._audit_start_time = timezone.now()
            request._audit_data = {
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
                'content_type': request.META.get('CONTENT_TYPE', ''),
                'content_length': request.META.get('CONTENT_LENGTH', 0)
            }
            
            # 如果用户已认证，记录用户信息
            if hasattr(request, 'user') and request.user.is_authenticated:
                request._audit_data.update({
                    'user_id': request.user.id,
                    'username': request.user.username,
                    'user_role': getattr(request.user, 'role', None)
                })
            
        except Exception as e:
            logger.error(f"权限审计中间件预处理失败: {str(e)}")
        
        return None
    
    def process_response(self, request, response, start_time):
        """处理响应"""
        if not self.enabled or self._should_skip_audit(request):
            return response
        
        try:
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 获取审计数据
            audit_data = getattr(request, '_audit_data', {})
            audit_data.update({
                'status_code': response.status_code,
                'processing_time': processing_time,
                'response_size': len(response.content) if hasattr(response, 'content') else 0
            })
            
            # 记录审计日志
            try:
                from .audit import audit_service, AuditActionType, AuditResult
                
                # 确定操作类型和结果
                action_type = self._determine_action_type(request, response)
                result = self._determine_result(response)
                
                user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                
                audit_service.log_permission_action(
                    action_type=action_type,
                    user=user,
                    resource=self._get_resource_name(request),
                    action=request.method.lower(),
                    result=result,
                    description=f"{request.method} {request.path}",
                    details=audit_data,
                    request=request
                )
            except ImportError:
                logger.warning("无法导入审计服务，跳过审计记录")
            
        except Exception as e:
            logger.error(f"权限审计中间件后处理失败: {str(e)}")
        
        return response
    
    def _should_skip_audit(self, request):
        """判断是否跳过审计"""
        # 检查路径排除列表
        for excluded_path in self.excluded_paths:
            if request.path.startswith(excluded_path):
                return True
        
        # 检查用户排除列表
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            request.user.username in self.excluded_users):
            return True
        
        # 检查是否记录匿名用户
        if (not self.log_anonymous and 
            (not hasattr(request, 'user') or not request.user.is_authenticated)):
            return True
        
        return False
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _get_resource_name(self, request):
        """获取资源名称"""
        try:
            # 尝试从URL解析获取视图名称
            resolver_match = resolve(request.path)
            if resolver_match.view_name:
                return resolver_match.view_name
            elif resolver_match.func:
                return f"{resolver_match.func.__module__}.{resolver_match.func.__name__}"
        except Exception:
            pass
        
        # 回退到路径
        return request.path
    
    def _determine_action_type(self, request, response):
        """确定操作类型"""
        # 根据HTTP方法和状态码确定操作类型
        method = request.method.upper()
        status_code = response.status_code
        
        if status_code == 401:
            return 'login_failure'
        elif status_code == 403:
            return 'security_violation'
        elif method == 'POST':
            return 'permission_check'
        elif method in ['PUT', 'PATCH']:
            return 'permission_check'
        elif method == 'DELETE':
            return 'permission_check'
        else:
            return 'permission_check'
    
    def _determine_result(self, response):
        """确定操作结果"""
        status_code = response.status_code
        
        if 200 <= status_code < 300:
            return 'success'
        elif status_code == 401:
            return 'denied'
        elif status_code == 403:
            return 'denied'
        elif 400 <= status_code < 500:
            return 'failure'
        elif 500 <= status_code < 600:
            return 'error'
        else:
            return 'failure'


class SecurityValidationMiddleware(MiddlewareMixin):
    """安全验证中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # 配置选项
        self.enabled = getattr(settings, 'SECURITY_VALIDATION_ENABLED', True)
        self.excluded_paths = getattr(settings, 'SECURITY_VALIDATION_EXCLUDED_PATHS', [
            '/static/',
            '/media/',
            '/favicon.ico',
            '/health/',
            '/ping/',
            '/admin/login/',
            '/accounts/login/'
        ])
        self.strict_mode = getattr(settings, 'SECURITY_VALIDATION_STRICT_MODE', False)
    
    def __call__(self, request):
        # 安全验证
        security_response = self.process_request(request)
        if security_response:
            return security_response
        
        # 处理请求
        response = self.get_response(request)
        
        return response
    
    def process_request(self, request):
        """处理请求安全验证"""
        if not self.enabled or self._should_skip_validation(request):
            return None
        
        try:
            # 只对已认证用户进行验证
            if not (hasattr(request, 'user') and request.user.is_authenticated):
                return None
            
            # 导入验证器（避免循环导入）
            try:
                from .validators import permission_validator
            except ImportError:
                logger.warning("无法导入权限验证器，跳过安全验证")
                return None
            
            # 获取资源和操作信息
            resource_type = self._get_resource_type(request)
            action = request.method.lower()
            
            # 执行权限验证
            is_valid, message, violations, rule_results = permission_validator.validate_user_access(
                user=request.user,
                resource_type=resource_type,
                action=action,
                request=request
            )
            
            # 如果验证失败，返回错误响应
            if not is_valid:
                logger.warning(
                    f"用户 {request.user.username} 访问 {resource_type} 被拒绝: {message}"
                )
                
                if self.strict_mode:
                    # 严格模式：返回403错误
                    return JsonResponse({
                        'error': 'Access Denied',
                        'message': message,
                        'violations': violations
                    }, status=403)
                else:
                    # 宽松模式：仅记录日志
                    logger.warning(f"安全验证失败（宽松模式）: {message}")
            
            # 将验证结果添加到请求中，供后续使用
            request._security_validation = {
                'is_valid': is_valid,
                'message': message,
                'violations': violations,
                'rule_results': rule_results
            }
            
        except Exception as e:
            logger.error(f"安全验证中间件处理失败: {str(e)}")
            
            if self.strict_mode:
                return JsonResponse({
                    'error': 'Security Validation Error',
                    'message': 'An error occurred during security validation'
                }, status=500)
        
        return None
    
    def _should_skip_validation(self, request):
        """判断是否跳过验证"""
        # 检查路径排除列表
        for excluded_path in self.excluded_paths:
            if request.path.startswith(excluded_path):
                return True
        
        return False
    
    def _get_resource_type(self, request):
        """获取资源类型"""
        try:
            # 尝试从URL解析获取资源类型
            resolver_match = resolve(request.path)
            if resolver_match.app_name:
                return resolver_match.app_name
            elif resolver_match.namespace:
                return resolver_match.namespace
        except Exception:
            pass
        
        # 从路径推断资源类型
        path_parts = request.path.strip('/').split('/')
        if path_parts and path_parts[0]:
            return path_parts[0]
        
        return 'unknown'


class RateLimitMiddleware(MiddlewareMixin):
    """频率限制中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # 配置选项
        self.enabled = getattr(settings, 'RATE_LIMIT_ENABLED', True)
        self.default_limit = getattr(settings, 'RATE_LIMIT_DEFAULT', 1000)  # 每小时请求数
        self.time_window = getattr(settings, 'RATE_LIMIT_WINDOW', 3600)  # 时间窗口（秒）
        self.excluded_paths = getattr(settings, 'RATE_LIMIT_EXCLUDED_PATHS', [
            '/static/',
            '/media/',
            '/favicon.ico'
        ])
        
        # 内存缓存（生产环境应使用Redis等）
        self._request_cache = {}
    
    def __call__(self, request):
        # 频率限制检查
        rate_limit_response = self.process_request(request)
        if rate_limit_response:
            return rate_limit_response
        
        # 处理请求
        response = self.get_response(request)
        
        return response
    
    def process_request(self, request):
        """处理频率限制"""
        if not self.enabled or self._should_skip_rate_limit(request):
            return None
        
        try:
            # 获取客户端标识
            client_id = self._get_client_id(request)
            
            # 检查频率限制
            if self._is_rate_limited(client_id):
                logger.warning(f"客户端 {client_id} 超过频率限制")
                
                # 记录违规日志
                try:
                    from .audit import audit_service, AuditRiskLevel
                    user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                    audit_service.log_security_violation(
                        user=user,
                        violation_type='rate_limit',
                        severity='medium',
                        description=f"客户端 {client_id} 超过频率限制",
                        details={
                            'client_id': client_id,
                            'path': request.path,
                            'method': request.method
                        },
                        request=request
                    )
                except ImportError:
                    logger.warning("无法导入审计服务，跳过违规记录")
                
                return JsonResponse({
                    'error': 'Rate Limit Exceeded',
                    'message': 'Too many requests. Please try again later.'
                }, status=429)
            
            # 记录请求
            self._record_request(client_id)
            
        except Exception as e:
            logger.error(f"频率限制中间件处理失败: {str(e)}")
        
        return None
    
    def _should_skip_rate_limit(self, request):
        """判断是否跳过频率限制"""
        # 检查路径排除列表
        for excluded_path in self.excluded_paths:
            if request.path.startswith(excluded_path):
                return True
        
        return False
    
    def _get_client_id(self, request):
        """获取客户端标识"""
        # 优先使用用户ID
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user_{request.user.id}"
        
        # 使用IP地址
        ip_address = self._get_client_ip(request)
        return f"ip_{ip_address}"
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _is_rate_limited(self, client_id):
        """检查是否超过频率限制"""
        now = time.time()
        
        # 清理过期记录
        if client_id in self._request_cache:
            self._request_cache[client_id] = [
                timestamp for timestamp in self._request_cache[client_id]
                if now - timestamp < self.time_window
            ]
        
        # 检查请求数量
        request_count = len(self._request_cache.get(client_id, []))
        return request_count >= self.default_limit
    
    def _record_request(self, client_id):
        """记录请求"""
        now = time.time()
        
        if client_id not in self._request_cache:
            self._request_cache[client_id] = []
        
        self._request_cache[client_id].append(now)
        
        # 限制缓存大小
        if len(self._request_cache[client_id]) > self.default_limit * 2:
            self._request_cache[client_id] = self._request_cache[client_id][-self.default_limit:]