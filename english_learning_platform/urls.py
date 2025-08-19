from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
import os

from apps.accounts.views import dev_login_view
from apps.permissions.api_views import get_menu_version

# 简单的健康检查视图
def health_check(request):
    """简单的健康检查端点"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Service is healthy'
    })

# 测试文件服务视图
def serve_test_file(request, filename):
    """提供测试文件服务"""
    file_path = os.path.join(settings.BASE_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    else:
        return HttpResponse('File not found', status=404)

urlpatterns = [
    path('admin/', include('massadmin.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('api/', include(('apps.accounts.urls', 'accounts'), namespace='api_accounts')),  # 修正API路由映射
    path('api/words/', include('apps.words.urls')),
    path('api/teaching/', include('apps.teaching.urls')),
    path('api/vocabulary/', include('apps.vocabulary_manager.urls')),
    path('api/permissions/', include(('apps.permissions.urls', 'permissions'), namespace='api_permissions')),  # 添加permissions应用API路由
    path('permissions/', include(('apps.permissions.urls', 'permissions'), namespace='permissions_web')),  # 添加permissions应用URL
    # 健康检查端点
    path('api/health-check', health_check, name='health_check'),
    path('api/health', health_check, name='health_check_alt'),
    
    # 菜单版本API（直接路由，避免嵌套路径问题）
    path('api/menu/version/', get_menu_version, name='menu_version'),
    # path('', include('gamification.urls')),  # 临时禁用
    path('dev_login.html', dev_login_view, name='dev_login'),
    
    # 测试文件路由
    path('test-websocket-minimal.html', lambda request: serve_test_file(request, 'test-websocket-minimal.html'), name='test_websocket_minimal'),
    path('test-websocket-no-heartbeat.html', lambda request: serve_test_file(request, 'test-websocket-no-heartbeat.html'), name='test_websocket_no_heartbeat'),
    
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
]

# 开发环境下提供静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)