from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import UserLoginLog
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomUserBackend(ModelBackend):
    """自定义用户认证后端"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """认证用户"""
        if username is None or password is None:
            return None
        
        try:
            # 支持用户名、邮箱、手机号登录
            user = User.objects.get(
                Q(username=username) | 
                Q(email=username) | 
                Q(phone=username)
            )
        except User.DoesNotExist:
            # 记录登录失败日志
            self._log_login_attempt(request, username, False)
            return None
        except User.MultipleObjectsReturned:
            # 如果有多个用户匹配，返回None
            logger.warning(f"Multiple users found for identifier: {username}")
            return None
        
        # 检查密码
        if user.check_password(password):
            # 检查账号是否激活
            if hasattr(user, 'is_active_account') and not user.is_active_account:
                logger.warning(f"Inactive account login attempt: {username}")
                self._log_login_attempt(request, username, False, user)
                return None
            
            # 记录登录成功日志
            self._log_login_attempt(request, username, True, user)
            return user
        else:
            # 记录登录失败日志
            self._log_login_attempt(request, username, False, user)
            return None
    
    def _log_login_attempt(self, request, username, success, user=None):
        """记录登录尝试"""
        try:
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            UserLoginLog.objects.create(
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_success=success
            )
        except Exception as e:
            logger.error(f"Failed to log login attempt: {e}")
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '未知'
    
    def get_user(self, user_id):
        """根据用户ID获取用户"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None