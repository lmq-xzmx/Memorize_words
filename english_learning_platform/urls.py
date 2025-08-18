from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import JsonResponse

from apps.accounts.views import dev_login_view

# 简单的健康检查视图
def health_check(request):
    """简单的健康检查端点"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Service is healthy'
    })

urlpatterns = [
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
    # path('', include('gamification.urls')),  # 临时禁用
    path('dev_login.html', dev_login_view, name='dev_login'),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
]

# 开发环境下提供静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)