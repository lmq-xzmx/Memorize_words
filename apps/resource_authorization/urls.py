from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'authorizations', views.ResourceAuthorizationViewSet, basename='authorization')
router.register(r'shares', views.ResourceShareViewSet, basename='share')
router.register(r'categories', views.ResourceCategoryViewSet, basename='category')
router.register(r'subscriptions', views.UserSubscriptionViewSet, basename='subscription')

app_name = 'resource_authorization'

urlpatterns = [
    path('api/', include(router.urls)),
]