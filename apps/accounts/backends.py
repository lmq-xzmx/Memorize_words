from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
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
            user = User.objects.filter(
                Q(username=username) | 
                Q(email=username) | 
                Q(phone=username)
            ).first()
        except Exception as e:
            logger.warning(f"User lookup failed for identifier: {username}, error: {e}")
            return None
        
        if not user:
            return None
        
        # 检查密码
        if user.check_password(password):
            # 检查账号是否激活
            if not user.is_active:
                logger.warning(f"Inactive account login attempt: {username}")
                return None
            
            return user
        else:
            return None
    
    def get_user(self, user_id):
        """根据用户ID获取用户"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None