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

from .models import MenuModuleConfig, RoleMenuPermission, RoleGroupMapping
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
            'role_permissions_count': RoleMenuPermission.objects.count(),
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
        if search:
            queryset = queryset.filter(
                Q(module_name__icontains=search) |
                Q(display_name__icontains=search)
            )
        return queryset.order_by('module_name')


class MenuModuleCreateView(LoginRequiredMixin, RolePermissionMixin, CreateView):
    """创建菜单模块"""
    model = MenuModuleConfig
    template_name = 'permissions/menu_module_form.html'
    fields = ['module_name', 'display_name', 'icon', 'url_pattern', 'parent_module', 
              'sort_order', 'is_active', 'description']
    success_url = reverse_lazy('permissions:menu_module_list')
    required_roles = [UserRole.ADMIN]
    
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
    fields = ['module_name', 'display_name', 'icon', 'url_pattern', 'parent_module', 
              'sort_order', 'is_active', 'description']
    success_url = reverse_lazy('permissions:menu_module_list')
    required_roles = [UserRole.ADMIN]
    
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


class RoleMenuPermissionListView(LoginRequiredMixin, RolePermissionMixin, ListView):
    """角色菜单权限列表"""
    model = RoleMenuPermission
    template_name = 'permissions/role_menu_permission_list.html'
    context_object_name = 'role_permissions'
    paginate_by = 20
    required_roles = [UserRole.ADMIN]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('menu_module')
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset.order_by('role', 'menu_module__module_name')


class RoleMenuPermissionCreateView(LoginRequiredMixin, RolePermissionMixin, CreateView):
    """创建角色菜单权限"""
    model = RoleMenuPermission
    template_name = 'permissions/role_menu_permission_form.html'
    fields = ['role', 'menu_module', 'can_view', 'can_add', 'can_change', 'can_delete']
    success_url = reverse_lazy('permissions:role_menu_permission_list')
    required_roles = [UserRole.ADMIN]
    
    def form_valid(self, form):
        messages.success(self.request, '角色菜单权限创建成功！')
        return super().form_valid(form)


class RoleMenuPermissionDetailView(LoginRequiredMixin, RolePermissionMixin, DetailView):
    """角色菜单权限详情"""
    model = RoleMenuPermission
    template_name = 'permissions/role_menu_permission_detail.html'
    context_object_name = 'role_permission'
    required_roles = [UserRole.ADMIN]


class RoleMenuPermissionUpdateView(LoginRequiredMixin, RolePermissionMixin, UpdateView):
    """更新角色菜单权限"""
    model = RoleMenuPermission
    template_name = 'permissions/role_menu_permission_form.html'
    fields = ['role', 'menu_module', 'can_view', 'can_add', 'can_change', 'can_delete']
    success_url = reverse_lazy('permissions:role_menu_permission_list')
    required_roles = [UserRole.ADMIN]
    
    def form_valid(self, form):
        messages.success(self.request, '角色菜单权限更新成功！')
        return super().form_valid(form)


class RoleMenuPermissionDeleteView(LoginRequiredMixin, RolePermissionMixin, DeleteView):
    """删除角色菜单权限"""
    model = RoleMenuPermission
    template_name = 'permissions/role_menu_permission_confirm_delete.html'
    success_url = reverse_lazy('permissions:role_menu_permission_list')
    required_roles = [UserRole.ADMIN]
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '角色菜单权限删除成功！')
        return super().delete(request, *args, **kwargs)


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


class BatchAssignPermissionsView(LoginRequiredMixin, RolePermissionMixin, TemplateView):
    """批量分配权限"""
    template_name = 'permissions/batch_assign_permissions.html'
    required_roles = [UserRole.ADMIN]
    
    def post(self, request, *args, **kwargs):
        role = request.POST.get('role')
        module_ids = request.POST.getlist('module_ids')
        permissions = {
            'can_view': request.POST.get('can_view') == 'on',
            'can_add': request.POST.get('can_add') == 'on',
            'can_change': request.POST.get('can_change') == 'on',
            'can_delete': request.POST.get('can_delete') == 'on',
        }
        
        try:
            for module_id in module_ids:
                module = get_object_or_404(MenuModuleConfig, id=module_id)
                role_permission, created = RoleMenuPermission.objects.get_or_create(
                    role=role,
                    menu_module=module,
                    defaults=permissions
                )
                if not created:
                    for key, value in permissions.items():
                        setattr(role_permission, key, value)
                    role_permission.save()
            
            messages.success(request, f'成功为角色 {role} 批量分配了 {len(module_ids)} 个模块的权限！')
        except Exception as e:
            messages.error(request, f'批量分配权限失败：{str(e)}')
        
        return redirect('permissions:role_menu_permission_list')


class BatchRemovePermissionsView(LoginRequiredMixin, RolePermissionMixin, TemplateView):
    """批量移除权限"""
    template_name = 'permissions/batch_remove_permissions.html'
    required_roles = [UserRole.ADMIN]
    
    def post(self, request, *args, **kwargs):
        permission_ids = request.POST.getlist('permission_ids')
        
        try:
            deleted_count = RoleMenuPermission.objects.filter(
                id__in=permission_ids
            ).delete()[0]
            
            messages.success(request, f'成功删除了 {deleted_count} 个权限配置！')
        except Exception as e:
            messages.error(request, f'批量删除权限失败：{str(e)}')
        
        return redirect('permissions:role_menu_permission_list')


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
def check_permission_ajax(request):
    """检查权限AJAX接口"""
    role = request.GET.get('role')
    module_name = request.GET.get('module_name')
    permission_type = request.GET.get('permission_type', 'can_view')
    
    if not all([role, module_name]):
        return JsonResponse({'success': False, 'message': '参数不完整'})
    
    try:
        module = MenuModuleConfig.objects.get(module_name=module_name)
        role_permission = RoleMenuPermission.objects.filter(
            role=role,
            menu_module=module
        ).first()
        
        has_permission = False
        if role_permission:
            has_permission = getattr(role_permission, permission_type, False)
        
        return JsonResponse({
            'success': True,
            'has_permission': has_permission,
            'role': role,
            'module_name': module_name,
            'permission_type': permission_type
        })
    except MenuModuleConfig.DoesNotExist:
        return JsonResponse({'success': False, 'message': '菜单模块不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def get_role_permissions_ajax(request):
    """获取角色权限AJAX接口"""
    role = request.GET.get('role')
    
    if not role:
        return JsonResponse({'success': False, 'message': '角色参数缺失'})
    
    try:
        permissions = RoleMenuPermission.objects.filter(
            role=role
        ).select_related('menu_module').values(
            'menu_module__module_name',
            'menu_module__display_name',
            'can_view',
            'can_add',
            'can_change',
            'can_delete'
        )
        
        return JsonResponse({
            'success': True,
            'permissions': list(permissions),
            'role': role
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})