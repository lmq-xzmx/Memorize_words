from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from .models import UserLoginLog
import logging

logger = logging.getLogger(__name__)


class ForceHTTPMiddleware(MiddlewareMixin):
    """强制HTTP中间件（开发环境使用）"""
    
    def process_request(self, request):
        # 在开发环境下可以添加一些HTTP相关的处理
        return None


class RolePermissionMiddleware(MiddlewareMixin):
    """角色权限中间件"""
    
    def process_request(self, request):
        """处理请求前的权限检查"""
        # 如果用户已登录但账号被禁用
        if request.user.is_authenticated:
            if hasattr(request.user, 'is_active_account') and not request.user.is_active_account:
                logout(request)
                messages.error(request, '您的账号已被禁用，请联系管理员。')
                return redirect('accounts:login')
        
        return None


class AdminUnifiedLoginMiddleware(MiddlewareMixin):
    """Admin统一登录中间件"""
    
    def process_request(self, request):
        """处理Admin登录重定向"""
        # 如果访问admin登录页面，重定向到统一登录页面
        if request.path == '/admin/login/' and not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:login') + '?next=' + request.GET.get('next', '/admin/'))
        
        return None


class UserActivityMiddleware(MiddlewareMixin):
    """用户活动记录中间件"""
    
    def process_request(self, request):
        """记录用户活动"""
        if request.user.is_authenticated:
            # 可以在这里记录用户的最后活动时间等信息
            pass
        
        return None