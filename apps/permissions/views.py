from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import MenuModuleConfig, RoleGroupMapping
# RoleMenuPermission 模型已废弃，请使用 MenuValidity 和 RoleMenuAssignment 替代
from .models_optimized import PermissionSyncLog
from apps.accounts.models import CustomUser, UserRole


class RolePermissionMixin(View):
    """角色权限混入类"""
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if self.required_roles and request.user.role not in self.required_roles:
            messages.error(request, '您没有权限访问此页面')
            return redirect('accounts:profile')
        
        return super().dispatch(request, *args, **kwargs)


class PermissionIndexView(LoginRequiredMixin, RolePermissionMixin, TemplateView):
    """权限管理主页"""
    template_name = 'permissions/index.html'
    required_roles = [UserRole.ADMIN, UserRole.TEACHER]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'menu_modules_count': MenuModuleConfig.objects.count(),
            'role_mappings_count': RoleGroupMapping.objects.count(),
            'sync_logs_count': PermissionSyncLog.objects.count(),
            'recent_logs': PermissionSyncLog.objects.order_by('-created_at')[:5],
        })
        return context


class MenuModuleListView(LoginRequiredMixin, RolePermissionMixin, ListView):
    """菜单模块列表"""
    model = MenuModuleConfig
    template_name = 'permissions/menu_module_list.html'
    context_object_name = 'menu_modules'
    paginate_by = 20
    required_roles = [UserRole.ADMIN]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        role_filter = self.request.GET.get('role')
        menu_level = self.request.GET.get('menu_level')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(key__icontains=search) |
                Q(description__icontains=search)
            )
        
        if role_filter:
            # 筛选指定角色可访问的菜单
            queryset = queryset.filter(
                menuvalidity__role=role_filter,
                menuvalidity__is_valid=True
            ).distinct()
        
        if menu_level:
            queryset = queryset.filter(menu_level=menu_level)
            
        return queryset.order_by('menu_level', 'sort_order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加筛选选项
        from .models import MenuValidity
        context['available_roles'] = MenuValidity.objects.values_list('role', flat=True).distinct()
        context['menu_level_choices'] = MenuModuleConfig.MENU_LEVEL_CHOICES
        context['current_role'] = self.request.GET.get('role', '')
        context['current_menu_level'] = self.request.GET.get('menu_level', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class MenuModuleCreateView(LoginRequiredMixin, RolePermissionMixin, CreateView):
    """创建菜单模块"""
    model = MenuModuleConfig
    template_name = 'permissions/menu_module_form.html'
    fields = ['name', 'key', 'menu_level', 'icon', 'url', 'sort_order', 'is_active', 'description']
    success_url = reverse_lazy('permissions:menu_module_list')
    required_roles = [UserRole.ADMIN]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '创建菜单模块'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '菜单模块创建成功！')
        return super().form_valid(form)


class MenuModuleDetailView(LoginRequiredMixin, RolePermissionMixin, DetailView):
    """菜单模块详情"""
    model = MenuModuleConfig
    template_name = 'permissions/menu_module_detail.html'
    context_object_name = 'menu_module'
    required_roles = [UserRole.ADMIN]


class MenuModuleUpdateView(LoginRequiredMixin, RolePermissionMixin, UpdateView):
    """更新菜单模块"""
    model = MenuModuleConfig
    template_name = 'permissions/menu_module_form.html'
    fields = ['name', 'key', 'menu_level', 'icon', 'url', 'sort_order', 'is_active', 'description']
    success_url = reverse_lazy('permissions:menu_module_list')
    required_roles = [UserRole.ADMIN]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '编辑菜单模块'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '菜单模块更新成功！')
        return super().form_valid(form)


class MenuModuleDeleteView(LoginRequiredMixin, RolePermissionMixin, DeleteView):
    """删除菜单模块"""
    model = MenuModuleConfig
    template_name = 'permissions/menu_module_confirm_delete.html'
    success_url = reverse_lazy('permissions:menu_module_list')
    required_roles = [UserRole.ADMIN]
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '菜单模块删除成功！')
        return super().delete(request, *args, **kwargs)


# RoleMenuPermissionListView 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


# RoleMenuPermissionCreateView 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


# RoleMenuPermissionDetailView 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


# RoleMenuPermissionUpdateView 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


# RoleMenuPermissionDeleteView 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


class RoleGroupMappingListView(LoginRequiredMixin, RolePermissionMixin, ListView):
    """角色组映射列表"""
    model = RoleGroupMapping
    template_name = 'permissions/role_group_mapping_list.html'
    context_object_name = 'role_mappings'
    paginate_by = 20
    required_roles = [UserRole.ADMIN]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('group')
        return queryset.order_by('role', 'group__name')


class RoleGroupMappingCreateView(LoginRequiredMixin, RolePermissionMixin, CreateView):
    """创建角色组映射"""
    model = RoleGroupMapping
    template_name = 'permissions/role_group_mapping_form.html'
    fields = ['role', 'group', 'is_active']
    success_url = reverse_lazy('permissions:role_group_mapping_list')
    required_roles = [UserRole.ADMIN]
    
    def form_valid(self, form):
        messages.success(self.request, '角色组映射创建成功！')
        return super().form_valid(form)


class RoleGroupMappingDetailView(LoginRequiredMixin, RolePermissionMixin, DetailView):
    """角色组映射详情"""
    model = RoleGroupMapping
    template_name = 'permissions/role_group_mapping_detail.html'
    context_object_name = 'role_mapping'
    required_roles = [UserRole.ADMIN]


class RoleGroupMappingUpdateView(LoginRequiredMixin, RolePermissionMixin, UpdateView):
    """更新角色组映射"""
    model = RoleGroupMapping
    template_name = 'permissions/role_group_mapping_form.html'
    fields = ['role', 'group', 'is_active']
    success_url = reverse_lazy('permissions:role_group_mapping_list')
    required_roles = [UserRole.ADMIN]
    
    def form_valid(self, form):
        messages.success(self.request, '角色组映射更新成功！')
        return super().form_valid(form)


class RoleGroupMappingDeleteView(LoginRequiredMixin, RolePermissionMixin, DeleteView):
    """删除角色组映射"""
    model = RoleGroupMapping
    template_name = 'permissions/role_group_mapping_confirm_delete.html'
    success_url = reverse_lazy('permissions:role_group_mapping_list')
    required_roles = [UserRole.ADMIN]
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '角色组映射删除成功！')
        return super().delete(request, *args, **kwargs)


class PermissionSyncLogListView(LoginRequiredMixin, RolePermissionMixin, ListView):
    """权限同步日志列表"""
    model = PermissionSyncLog
    template_name = 'permissions/permission_sync_log_list.html'
    context_object_name = 'sync_logs'
    paginate_by = 20
    required_roles = [UserRole.ADMIN]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')


class PermissionSyncLogDetailView(LoginRequiredMixin, RolePermissionMixin, DetailView):
    """权限同步日志详情"""
    model = PermissionSyncLog
    template_name = 'permissions/permission_sync_log_detail.html'
    context_object_name = 'sync_log'
    required_roles = [UserRole.ADMIN]


# BatchAssignPermissionsView 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


# BatchRemovePermissionsView 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


# AJAX视图
@login_required
@require_http_methods(["POST"])
def sync_permissions_ajax(request):
    """同步权限AJAX接口"""
    if not request.user.role == UserRole.ADMIN:
        return JsonResponse({'success': False, 'message': '权限不足'})
    
    try:
        from .signals import sync_all_permissions
        sync_all_permissions()
        return JsonResponse({'success': True, 'message': '权限同步成功！'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'权限同步失败：{str(e)}'})


@login_required
@require_http_methods(["GET"])
def get_menus_by_role_ajax(request):
    """AJAX获取指定角色的菜单列表"""
    role = request.GET.get('role')
    if not role:
        return JsonResponse({'success': False, 'message': '角色参数缺失'}, status=400)
    
    try:
        from .models import MenuValidity
        # 获取该角色有效的菜单
        valid_menus = MenuValidity.objects.filter(
            role=role, 
            is_valid=True
        ).select_related('menu_module')
        
        menus_data = []
        for validity in valid_menus:
            menu = validity.menu_module
            menus_data.append({
                'id': menu.id,
                'name': menu.name,
                'key': menu.key,
                'menu_level': menu.menu_level,
                'menu_level_display': menu.get_menu_level_display(),
                'icon': menu.icon,
                'url': menu.url,
                'sort_order': menu.sort_order,
                'is_active': menu.is_active
            })
        
        return JsonResponse({
            'success': True,
            'menus': menus_data,
            'count': len(menus_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取菜单失败：{str(e)}'
        }, status=500)


# check_permission_ajax 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代


# get_role_permissions_ajax 已被移除，因为依赖于已废弃的 RoleMenuPermission 模型
# 请使用 MenuValidity 和 RoleMenuAssignment 替代