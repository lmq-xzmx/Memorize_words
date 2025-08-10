"""
角色所辖用户增项的级联视图

提供三级级联的视图：角色 -> 用户 -> 增项
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from typing import Any

from .models import RoleLevel, RoleUser, UserExtension
from .models import RoleExtension, UserRole
import json
from apps.accounts.services.role_service import RoleService

User = get_user_model()


@staff_member_required
def role_hierarchy_index(request):
    """角色级别列表页面 - 第一级"""
    # 获取所有角色级别
    role_levels = RoleLevel.objects.annotate(
        user_count=Count('role_users', filter=Q(role_users__is_active=True)),
        extension_count=Count('role_users__user_extensions', filter=Q(role_users__user_extensions__is_active=True))
    ).order_by('sort_order', 'role')
    
    # 统计信息
    total_roles = role_levels.count()
    total_users = RoleUser.objects.filter(is_active=True).count()
    total_extensions = UserExtension.objects.filter(is_active=True).count()
    
    context = {
        'role_levels': role_levels,
        'total_roles': total_roles,
        'total_users': total_users,
        'total_extensions': total_extensions,
        'title': '角色所辖用户增项管理',
        'breadcrumbs': [
            {'name': '首页', 'url': reverse('admin:index')},
            {'name': '角色所辖用户增项', 'url': None},
        ]
    }
    
    return render(request, 'admin/accounts/role_hierarchy/index.html', context)


@staff_member_required
def role_users_list(request, role_level_id):
    """角色用户列表页面 - 第二级"""
    role_level = get_object_or_404(RoleLevel, id=role_level_id)
    
    # 获取该角色下的用户
    role_users_query = RoleUser.objects.filter(
        role_level=role_level,
        is_active=True
    ).select_related('user').annotate(
        extension_count=Count('user_extensions', filter=Q(user_extensions__is_active=True))
    ).order_by('user__username')
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        role_users_query = role_users_query.filter(
            Q(user__username__icontains=search_query) |
            Q(user__real_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # 分页
    paginator = Paginator(role_users_query, 20)
    page_number = request.GET.get('page')
    role_users = paginator.get_page(page_number)
    
    # 获取该角色的增项配置
    role_extensions = RoleExtension.objects.filter(
        role=role_level.role,
        is_active=True
    ).order_by('sort_order')
    
    context = {
        'role_level': role_level,
        'role_users': role_users,
        'role_extensions': role_extensions,
        'search_query': search_query,
        'title': f'{role_level.role_name} - 用户列表',
        'breadcrumbs': [
            {'name': '首页', 'url': reverse('admin:index')},
            {'name': '角色所辖用户增项', 'url': reverse('accounts:role_hierarchy_index')},
            {'name': role_level.role_name, 'url': None},
        ]
    }
    
    return render(request, 'admin/accounts/role_hierarchy/role_users.html', context)


@staff_member_required
def user_extensions_detail(request, role_user_id):
    """用户增项详情页面 - 第三级"""
    role_user = get_object_or_404(RoleUser, id=role_user_id)
    
    # 获取该用户的所有增项
    user_extensions = UserExtension.objects.filter(
        role_user=role_user,
        is_active=True
    ).select_related('role_extension').order_by('role_extension__sort_order')
    
    # 获取该角色的所有增项配置
    role_extensions = RoleExtension.objects.filter(
        role=role_user.role_level.role,
        is_active=True
    ).order_by('sort_order')
    
    # 创建增项数据字典，方便模板使用
    extension_data = {}
    for ext in user_extensions:
        extension_data[ext.role_extension.id] = ext
    
    context = {
        'role_user': role_user,
        'user_extensions': user_extensions,
        'role_extensions': role_extensions,
        'extension_data': extension_data,
        'title': f'{role_user.user.username} - 增项详情',
        'breadcrumbs': [
            {'name': '首页', 'url': reverse('admin:index')},
            {'name': '角色所辖用户增项', 'url': reverse('accounts:role_hierarchy_index')},
            {'name': role_user.role_level.role_name, 'url': reverse('accounts:role_users_list', args=[getattr(role_user.role_level, 'id')])},
            {'name': role_user.user.username, 'url': None},
        ]
    }
    
    return render(request, 'admin/accounts/role_hierarchy/user_extensions.html', context)


@staff_member_required
def update_user_extensions(request, role_user_id):
    """更新用户增项"""
    role_user = get_object_or_404(RoleUser, id=role_user_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 获取该角色的所有增项配置
                role_extensions = RoleExtension.objects.filter(
                    role=role_user.role_level.role,
                    is_active=True
                )
                
                for role_ext in role_extensions:
                    field_name = f'extension_{getattr(role_ext, "id")}'
                    field_value = request.POST.get(field_name, '')
                    
                    if field_value:
                        # 更新或创建增项数据
                        user_ext, created = UserExtension.objects.get_or_create(
                            role_user=role_user,
                            role_extension=role_ext,
                            defaults={
                                'field_value': field_value,
                                'created_by': request.user
                            }
                        )
                        
                        if not created and user_ext.field_value != field_value:
                            user_ext.field_value = field_value
                            user_ext.save()
                    else:
                        # 如果值为空，删除现有的增项数据
                        UserExtension.objects.filter(
                            role_user=role_user,
                            role_extension=role_ext
                        ).delete()
                
                messages.success(request, f'用户 {role_user.user.username} 的增项信息已更新')
                
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
    
    return redirect('accounts:user_extensions_detail', role_user_id=role_user_id)


@staff_member_required
def sync_role_data(request):
    """同步角色数据"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 同步角色级别
                for role_choice in RoleService.get_role_choices(include_empty=False):
                    role_code, role_name = role_choice
                    RoleLevel.objects.get_or_create(
                        role=role_code,
                        defaults={
                            'role_name': role_name,
                            'description': f'{role_name}角色',
                            'is_active': True,
                            'sort_order': 0
                        }
                    )
                
                # 同步用户数据
                users = User.objects.filter(is_active=True)
                synced_count = 0
                
                for user in users:
                    if hasattr(user, 'role') and getattr(user, 'role', None):
                        role_level = RoleLevel.objects.get(role=getattr(user, 'role'))
                        role_user, created = RoleUser.objects.get_or_create(
                            user=user,
                            defaults={
                                'role_level': role_level,
                                'is_active': user.is_active
                            }
                        )
                        
                        if not created:
                            # 更新现有记录
                            if role_user.role_level != role_level:
                                role_user.role_level = role_level
                                role_user.save()
                        
                        synced_count += 1
                
                messages.success(request, f'成功同步 {synced_count} 个用户的角色数据')
                
        except Exception as e:
            messages.error(request, f'同步失败: {str(e)}')
    
    return redirect('accounts:role_hierarchy_index')


@staff_member_required
def role_statistics_api(request, role_level_id):
    """角色统计API"""
    role_level = get_object_or_404(RoleLevel, id=role_level_id)
    
    # 统计数据
    total_users = RoleUser.objects.filter(role_level=role_level, is_active=True).count()
    total_extensions = UserExtension.objects.filter(
        role_user__role_level=role_level,
        is_active=True
    ).count()
    
    # 按增项类型统计
    extension_stats = {}
    role_extensions = RoleExtension.objects.filter(role=role_level.role, is_active=True)
    
    for role_ext in role_extensions:
        count = UserExtension.objects.filter(
            role_user__role_level=role_level,
            role_extension=role_ext,
            is_active=True
        ).count()
        extension_stats[role_ext.field_label] = count
    
    data = {
        'role_name': role_level.role_name,
        'total_users': total_users,
        'total_extensions': total_extensions,
        'extension_stats': extension_stats
    }
    
    return JsonResponse(data)


@staff_member_required
def batch_update_extensions(request):
    """批量更新增项"""
    if request.method == 'POST':
        try:
            role_user_ids = request.POST.getlist('role_user_ids')
            extension_id = request.POST.get('extension_id')
            field_value = request.POST.get('field_value')
            
            if not all([role_user_ids, extension_id, field_value]):
                messages.error(request, '参数不完整')
                return redirect('accounts:role_hierarchy_index')
            
            role_extension = get_object_or_404(RoleExtension, id=extension_id)
            
            with transaction.atomic():
                updated_count = 0
                for role_user_id in role_user_ids:
                    role_user = get_object_or_404(RoleUser, id=role_user_id)
                    
                    user_ext, created = UserExtension.objects.get_or_create(
                        role_user=role_user,
                        role_extension=role_extension,
                        defaults={
                            'field_value': field_value,
                            'created_by': request.user
                        }
                    )
                    
                    if not created:
                        user_ext.field_value = field_value
                        user_ext.save()
                    
                    updated_count += 1
                
                messages.success(request, f'成功批量更新 {updated_count} 个用户的增项信息')
                
        except Exception as e:
            messages.error(request, f'批量更新失败: {str(e)}')
    
    return redirect('accounts:role_hierarchy_index')