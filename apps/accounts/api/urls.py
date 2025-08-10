from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleAPIViewSet, role_choices_api, role_validate_api

# DRF路由器
router = DefaultRouter()
router.register(r'roles', RoleAPIViewSet, basename='role')

# URL配置
urlpatterns = [
    # DRF API路由
    path('api/', include(router.urls)),
    
    # 兼容性API路由（非DRF）
    path('api/role-choices/', role_choices_api, name='role_choices_api'),
    path('api/role-validate/<str:role_code>/', role_validate_api, name='role_validate_api'),
]

# 导出路由器供主URL配置使用
__all__ = ['router', 'urlpatterns']