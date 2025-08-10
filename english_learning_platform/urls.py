from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.views.generic import RedirectView

# 自定义登出视图
def custom_logout(request):
    """自定义登出视图"""
    from django.contrib.auth import logout
    from django.contrib import messages
    logout(request)
    messages.success(request, '您已成功退出登录。')
    return redirect('accounts:login')

# Admin登出视图
def admin_logout(request):
    """Admin登出视图"""
    from django.contrib.auth import logout
    from django.contrib import messages
    logout(request)
    messages.success(request, '您已成功退出管理后台。')
    return redirect('accounts:login')

# Favicon处理
def favicon_view(request):
    """处理favicon请求"""
    return HttpResponse(status=204)  # No Content

urlpatterns = [
    # Admin相关
    path('admin/logout/', admin_logout, name='admin_logout'),
    path('admin/login/', RedirectView.as_view(url='/accounts/login/?next=/admin/', permanent=False)),
    
    # 旧的 Proxy 模型重定向到统一用户管理
    path('admin/accounts/studentuserproxy/', RedirectView.as_view(url='/admin/accounts/customuser/?role=student', permanent=True)),
    path('admin/accounts/teacheruserproxy/', RedirectView.as_view(url='/admin/accounts/customuser/?role=teacher', permanent=True)),
    path('admin/accounts/parentuserproxy/', RedirectView.as_view(url='/admin/accounts/customuser/?role=parent', permanent=True)),
    path('admin/accounts/adminuserproxy/', RedirectView.as_view(url='/admin/accounts/customuser/?role=admin', permanent=True)),
    
    path('admin/', admin.site.urls),
    
    # 认证相关
    path('logout/', custom_logout, name='logout'),
    
    # 应用URL
    path('accounts/', include('apps.accounts.urls')),
    path('permissions/', include('apps.permissions.urls')),
    path('organization/', include('apps.organization.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('courses/', include('apps.courses.urls')),
    path('teaching/', include('apps.teaching.urls')),
    path('words/', include('apps.words.urls')),
    path('vocabulary-manager/', include('apps.vocabulary_manager.urls')),
    path('nlp-engine/', include('apps.nlp_engine.urls')),  # NLP引擎API
    path('article-factory/', include('apps.article_factory.urls')),
    path('reports/', include('apps.reports.urls')),
    path('api/resource-auth/', include('apps.resource_authorization.urls')),  # 资源授权系统API
    
    # 根路径重定向
    path('', RedirectView.as_view(url='/teaching/', permanent=False)),
    
    # Favicon
    path('favicon.ico', favicon_view),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 自定义Admin站点信息
admin.site.site_header = 'Natural English 管理后台'
admin.site.site_title = 'Natural English Admin'
admin.site.index_title = '欢迎使用 Natural English 管理系统'
