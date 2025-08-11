from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    CustomAuthToken, RegisterViewSet, UserViewSet,
    LearningProfileViewSet, UserLoginLogViewSet,
    RoleExtensionViewSet, StudentListViewSet
)
from .template_api_views import (
    RoleTemplateViewSet, EnhancedUserExtensionDataViewSet
)
from .bulk_api_views import BulkOperationsViewSet

app_name = 'accounts'

# 创建API路由器
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'students', StudentListViewSet, basename='student')
router.register(r'learning-profiles', LearningProfileViewSet, basename='learningprofile')
router.register(r'login-logs', UserLoginLogViewSet, basename='userloginlog')
router.register(r'role-extensions', RoleExtensionViewSet, basename='roleextension')
router.register(r'user-extensions', EnhancedUserExtensionDataViewSet, basename='userextensions')
router.register(r'role-templates', RoleTemplateViewSet, basename='roletemplate')
router.register(r'bulk-operations', BulkOperationsViewSet, basename='bulkoperations')

urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    path('api/auth/login/', CustomAuthToken.as_view(), name='api_login'),
    path('api/auth/register/', RegisterViewSet.as_view({'post': 'create'}), name='api_register'),
    path('api/auth/roles/', RegisterViewSet.as_view({'get': 'roles'}), name='api_roles'),
    path('api/auth/role-extensions/', RegisterViewSet.as_view({'get': 'role_extensions'}), name='api_role_extensions'),
    path('api/auth/register-with-extensions/', RegisterViewSet.as_view({'post': 'register_with_extensions'}), name='api_register_with_extensions'),
    
    # 传统Web视图（保留用于管理后台）
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # 用户管理
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # 用户列表（管理员功能）
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    
    # 角色管理
    path('roles/', views.RoleManagementView.as_view(), name='role_management'),
    
    # AJAX接口
    path('ajax/check-username/', views.check_username_ajax, name='check_username_ajax'),
    path('ajax/user-info/<int:user_id>/', views.get_user_info_ajax, name='user_info_ajax'),
    
    # 开发期快捷登录
    path('dev-login/', views.dev_login_view, name='dev_login'),
    
    # 角色所辖用户增项管理已整合到主要视图中
]