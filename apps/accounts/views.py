from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.core.paginator import Paginator
from django import forms
from .models import CustomUser, UserRole, LearningProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm, ProfileForm
import json
from apps.accounts.services.role_service import RoleService


class CustomLoginView(LoginView):
    """自定义登录视图"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """登录成功后的重定向URL"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        # 统一重定向到前端应用，避免跳转到后台管理页面
        # 前端应用会根据用户角色和权限进行相应的页面展示
        return 'http://localhost:3004/'
    
    def form_valid(self, form):
        """表单验证成功"""
        messages.success(self.request, f'欢迎回来，{form.get_user().real_name or form.get_user().username}！')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """表单验证失败"""
        messages.error(self.request, '用户名或密码错误，请重试。')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """自定义登出视图"""
    next_page = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, '您已成功退出登录。')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """用户注册视图"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """表单验证成功"""
        response = super().form_valid(form)
        messages.success(self.request, '注册成功！请登录。')
        return response
    
    def form_invalid(self, form):
        """表单验证失败"""
        messages.error(self.request, '注册失败，请检查输入信息。')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """用户个人资料视图"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # 如果是学生，获取学习档案
        if self.request.user.role == UserRole.STUDENT:
            try:
                context['learning_profile'] = LearningProfile.objects.get(user=self.request.user)  # type: ignore
            except LearningProfile.DoesNotExist:  # type: ignore
                context['learning_profile'] = None
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """编辑个人资料视图"""
    model = CustomUser
    form_class = ProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        """获取当前用户的学习档案"""
        if queryset is None:
            queryset = self.get_queryset()
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, '个人资料更新成功！')
        return super().form_valid(form)


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    """修改密码视图"""
    template_name = 'accounts/change_password.html'
    
    def post(self, request, *args, **kwargs):
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, '原密码错误。')
            return self.get(request, *args, **kwargs)
        
        if new_password != confirm_password:
            messages.error(request, '两次输入的新密码不一致。')
            return self.get(request, *args, **kwargs)
        
        if len(new_password) < 6:
            messages.error(request, '密码长度至少6位。')
            return self.get(request, *args, **kwargs)
        
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, '密码修改成功！请重新登录。')
        logout(request)
        return redirect('accounts:login')


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """用户列表视图（管理员功能）"""
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role == UserRole.ADMIN
    
    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by('-date_joined')
        
        # 搜索功能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |  # type: ignore
                Q(real_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # 角色过滤
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = RoleService.get_role_choices(include_empty=False)
        context['search'] = self.request.GET.get('search', '')
        context['selected_role'] = self.request.GET.get('role', '')
        return context


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """用户详情视图"""
    model = CustomUser
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'
    
    def test_func(self):
        return self.request.user.role == UserRole.ADMIN


class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """编辑用户视图"""
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_edit.html'
    
    def test_func(self):
        return self.request.user.role == UserRole.ADMIN
    
    def get_success_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '用户信息更新成功！')
        return super().form_valid(form)


class RoleManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """角色管理视图"""
    template_name = 'accounts/role_management.html'
    
    def test_func(self):
        return self.request.user.role == UserRole.ADMIN
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = RoleService.get_role_choices(include_empty=False)
        context['role_stats'] = {
            role[0]: CustomUser.objects.filter(role=role[0]).count()
            for role in RoleService.get_role_choices(include_empty=False)
        }
        return context


# AJAX视图
@login_required
def check_username_ajax(request):
    """检查用户名是否可用"""
    username = request.GET.get('username')
    if not username:
        return JsonResponse({'available': False, 'message': '用户名不能为空'})
    
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({
        'available': not exists,
        'message': '用户名已存在' if exists else '用户名可用'
    })


@login_required
def get_user_info_ajax(request, user_id):
    """获取用户信息（AJAX）"""
    try:
        user = CustomUser.objects.get(id=user_id)
        data = {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'email': user.email,
            'phone': user.phone,
            'role': user.get_role_display(),
            'english_level': user.english_level,
            'is_active': user.is_active_account,
        }
        return JsonResponse({'success': True, 'data': data})
    except CustomUser.DoesNotExist:  # type: ignore
        return JsonResponse({'success': False, 'message': '用户不存在'})


def dev_login_view(request):
    """开发期快捷登录页面"""
    return render(request, 'dev_login.html')