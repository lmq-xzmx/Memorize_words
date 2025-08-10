from django.core.cache import cache
from django.db.models import Prefetch, Count, Q
from django.utils import timezone
from datetime import timedelta
import hashlib
import json


class UserQueryOptimizer:
    """
    用户查询优化器
    提供高效的用户数据查询方法
    """
    
    @staticmethod
    def get_users_with_extensions(role=None, active_only=True):
        """
        获取用户及其增项数据（优化版）
        """
        from .models import CustomUser, UserExtensionData
        
        queryset = CustomUser.objects.select_related(
            'learning_profile'
        ).prefetch_related(
            Prefetch(
                'userextensiondata_set',
                queryset=UserExtensionData.objects.select_related('role_extension')
            )
        )
        
        if role:
            queryset = queryset.filter(role=role)
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('date_joined')
    
    @staticmethod
    def get_user_statistics(use_cache=True):
        """
        获取用户统计信息（带缓存）
        """
        cache_key = 'user_statistics'
        
        if use_cache:
            stats = cache.get(cache_key)
            if stats:
                return stats
        
        from .models import CustomUser, UserRole
        
        # 使用聚合查询优化性能
        stats = {}
        for role_value, role_label in UserRole.choices:
            stats[role_value] = {
                'label': role_label,
                'total': CustomUser.objects.filter(role=role_value).count(),
                'active': CustomUser.objects.filter(role=role_value, is_active=True).count(),
                'recent': CustomUser.objects.filter(
                    role=role_value,
                    date_joined__gte=timezone.now() - timedelta(days=30)
                ).count()
            }
        
        # 缓存5分钟
        if use_cache:
            cache.set(cache_key, stats, 300)
        
        return stats
    
    @staticmethod
    def search_users_optimized(search_term, role=None, limit=50):
        """
        优化的用户搜索
        """
        from .models import CustomUser
        
        queryset = CustomUser.objects.filter(
            Q(username__icontains=search_term) |
            Q(real_name__icontains=search_term) |
            Q(email__icontains=search_term)
        ).select_related('learning_profile')
        
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset.filter(is_active=True)[:limit]


class RoleExtensionCacheManager:
    """
    角色增项缓存管理器
    """
    
    @staticmethod
    def get_role_extension_config(role, use_cache=True):
        """
        获取角色增项配置（带缓存）
        """
        cache_key = f'role_extension_config_{role}'
        
        if use_cache:
            config = cache.get(cache_key)
            if config:
                return config
        
        from .models import RoleExtension
        
        try:
            role_extension = RoleExtension.objects.get(role=role, is_active=True)
            config = {
                'id': role_extension.pk,
                'role': role_extension.role,
                'fields': getattr(role_extension, 'fields', {}),
                'required_fields': getattr(role_extension, 'required_fields', []),
                'field_order': getattr(role_extension, 'field_order', [])
            }
            
            # 缓存30分钟
            if use_cache:
                cache.set(cache_key, config, 1800)
            
            return config
        except RoleExtension.DoesNotExist:
            return None
    
    @staticmethod
    def invalidate_role_extension_cache(role):
        """
        清除角色增项缓存
        """
        cache_key = f'role_extension_config_{role}'
        cache.delete(cache_key)
    
    @staticmethod
    def get_user_extension_data(user_id, use_cache=True):
        """
        获取用户增项数据（带缓存）
        """
        cache_key = f'user_extension_data_{user_id}'
        
        if use_cache:
            data = cache.get(cache_key)
            if data:
                return data
        
        from .models import UserExtensionData
        
        extensions = UserExtensionData.objects.filter(
            user_id=user_id
        ).select_related('role_extension').values(
            'role_extension__role',
            'data',
            'updated_at'
        )
        
        data = {}
        for ext in extensions:
            role = ext['role_extension__role']
            data[role] = {
                'data': ext['data'],
                'updated_at': ext['updated_at'].isoformat() if ext['updated_at'] else None
            }
        
        # 缓存10分钟
        if use_cache:
            cache.set(cache_key, data, 600)
        
        return data
    
    @staticmethod
    def invalidate_user_extension_cache(user_id):
        """
        清除用户增项数据缓存
        """
        cache_key = f'user_extension_data_{user_id}'
        cache.delete(cache_key)


class QueryCacheManager:
    """
    查询缓存管理器
    """
    
    @staticmethod
    def generate_cache_key(prefix, **kwargs):
        """
        生成缓存键
        """
        # 将参数排序并序列化
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        
        # 生成哈希
        hash_obj = hashlib.md5(params_str.encode('utf-8'))
        hash_str = hash_obj.hexdigest()[:16]
        
        return f'{prefix}_{hash_str}'
    
    @staticmethod
    def cached_query(cache_key, query_func, timeout=300):
        """
        缓存查询结果
        """
        result = cache.get(cache_key)
        if result is None:
            result = query_func()
            cache.set(cache_key, result, timeout)
        return result
    
    @staticmethod
    def invalidate_pattern(pattern):
        """
        清除匹配模式的缓存
        """
        # 注意：这需要Redis支持，Django默认缓存不支持模式删除
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(f'*{pattern}*')
            if keys:
                redis_conn.delete(*keys)
        except ImportError:
            # 如果没有Redis，跳过模式删除
            pass


class BulkOperationOptimizer:
    """
    批量操作优化器
    """
    
    @staticmethod
    def bulk_create_users(users_data, batch_size=100):
        """
        批量创建用户（优化版）
        """
        from .models import CustomUser
        
        users_to_create = []
        for user_data in users_data:
            user = CustomUser(
                username=user_data['username'],
                real_name=user_data.get('real_name', ''),
                email=user_data.get('email', ''),
                phone=user_data.get('phone', ''),
                role=user_data['role'],
                grade=user_data.get('grade', ''),
                is_active=True
            )
            users_to_create.append(user)
        
        # 分批创建
        created_users = []
        for i in range(0, len(users_to_create), batch_size):
            batch = users_to_create[i:i + batch_size]
            created_batch = CustomUser.objects.bulk_create(batch)
            created_users.extend(created_batch)
        
        return created_users
    
    @staticmethod
    def bulk_update_user_extensions(updates_data, batch_size=100):
        """
        批量更新用户增项数据（优化版）
        """
        from .models import UserExtensionData
        
        # 分批处理更新
        updated_count = 0
        for i in range(0, len(updates_data), batch_size):
            batch = updates_data[i:i + batch_size]
            
            # 构建批量更新
            for update_data in batch:
                UserExtensionData.objects.filter(
                    user_id=update_data['user_id'],
                    role_extension_id=update_data['role_extension_id']
                ).update(
                    data=update_data['data'],
                    updated_at=timezone.now()
                )
                updated_count += 1
        
        return updated_count
    
    @staticmethod
    def bulk_assign_roles(assignments_data, batch_size=100):
        """
        批量分配角色（优化版）
        """
        from .models import CustomUser
        
        updated_count = 0
        for i in range(0, len(assignments_data), batch_size):
            batch = assignments_data[i:i + batch_size]
            
            # 构建批量更新
            user_ids = [item['user_id'] for item in batch]
            role_mapping = {item['user_id']: item['role'] for item in batch}
            
            users = CustomUser.objects.filter(pk__in=user_ids)
            for user in users:
                if user.pk in role_mapping:
                    user.role = role_mapping[user.pk]
            
            # 批量更新
            CustomUser.objects.bulk_update(users, ['role'])
            updated_count += len(users)
        
        return updated_count