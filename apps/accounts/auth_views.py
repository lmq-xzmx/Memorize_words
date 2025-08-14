from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
import json

User = get_user_model()

class AuthVerifyView(APIView):
    """
    验证用户登录状态的API视图
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = []
    
    def get(self, request):
        """
        验证当前用户是否已登录
        """
        try:
            # 检查用户是否已认证
            if request.user.is_authenticated:
                return Response({
                    'authenticated': True,
                    'user_id': request.user.id,
                    'username': request.user.username,
                    'message': '用户已登录'
                })
            else:
                return Response({
                    'authenticated': False,
                    'message': '用户未登录'
                })
        except Exception as e:
            return Response({
                'authenticated': False,
                'error': str(e),
                'message': '验证登录状态时发生错误'
            }, status=500)

class CurrentUserView(APIView):
    """
    获取当前登录用户信息的API视图
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取当前登录用户的详细信息
        """
        try:
            user = request.user
            
            # 获取用户角色
            role = 'user'  # 默认角色
            if user.is_superuser:
                role = 'admin'
            elif user.is_staff:
                role = 'staff'
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'real_name': getattr(user, 'real_name', user.username),
                'email': user.email,
                'role': role,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            
            return Response({
                'success': True,
                'user': user_data,
                'message': '获取用户信息成功'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': '获取用户信息时发生错误'
            }, status=500)

class AuthSyncView(View):
    """
    前后端登录状态同步API视图
    """
    
    def get(self, request):
        """
        获取完整的登录状态信息，用于前后端同步
        """
        try:
            if request.user.is_authenticated:
                user = request.user
                
                # 获取用户角色
                role = 'user'
                if user.is_superuser:
                    role = 'admin'
                elif user.is_staff:
                    role = 'staff'
                
                return JsonResponse({
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'real_name': getattr(user, 'real_name', user.username),
                        'email': user.email,
                        'role': role,
                        'is_active': user.is_active,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser
                    },
                    'session_key': request.session.session_key,
                    'message': '用户已登录，状态同步成功'
                })
            else:
                return JsonResponse({
                    'authenticated': False,
                    'user': None,
                    'message': '用户未登录'
                })
                
        except Exception as e:
            return JsonResponse({
                'authenticated': False,
                'user': None,
                'error': str(e),
                'message': '同步登录状态时发生错误'
            }, status=500)

# 函数式视图（兼容性）
@require_http_methods(["GET"])
def auth_verify(request):
    """
    验证用户登录状态（函数式视图）
    """
    view = AuthVerifyView()
    return view.get(request)

@require_http_methods(["GET"])
def current_user(request):
    """
    获取当前用户信息（函数式视图）
    """
    view = CurrentUserView()
    return view.get(request)

@require_http_methods(["GET"])
def auth_sync(request):
    """
    前后端登录状态同步（函数式视图）
    """
    view = AuthSyncView()
    return view.get(request)