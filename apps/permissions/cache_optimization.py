# -*- coding: utf-8 -*-
"""
权限API性能优化 - 缓存策略实现
提供多层缓存、智能预加载和性能监控
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from functools import wraps
from collections import defaultdict
import threading
import time

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

User = get_user_model()
logger = logging.getLogger(__name__)


class CacheLevel:
    """缓存级别常量"""
    L1_MEMORY = 'l1_memory'  # 内存缓存（最快）
    L2_REDIS = 'l2_redis'    # Redis缓存（中等）
    L3_DATABASE = 'l3_db'    # 数据库缓存（最慢）


class CacheStrategy:
    """缓存策略常量"""
    LRU = 'lru'              # 最近最少使用
    LFU = 'lfu'              # 最少使用频率
    TTL = 'ttl'              # 时间过期
    PRIORITY = 'priority'     # 优先级
    ADAPTIVE = 'adaptive'     # 自适应


class PermissionCacheManager:
    """权限缓存管理器"""
    
    def __init__(self):
        self.l1_cache = {}  # 内存缓存
        self.cache_stats = defaultdict(int)
        self.access_times = defaultdict(list)
        self.cache_priorities = defaultdict(int)
        self.lock = threading.RLock()
        
        # 配置参数
        self.l1_max_size = getattr(settings, 'PERMISSION_L1_CACHE_SIZE', 1000)
        self.l2_timeout = getattr(settings, 'PERMISSION_L2_CACHE_TIMEOUT', 3600)
        self.l3_timeout = getattr(settings, 'PERMISSION_L3_CACHE_TIMEOUT', 86400)
        
        # 性能监控
        self.performance_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time': 0,
            'slow_queries': [],
            'hot_keys': defaultdict(int)
        }
        
        # 预加载配置
        self.preload_patterns = [
            'user_permissions_{user_id}',
            'role_permissions_{role_id}',
            'menu_permissions_{user_id}',
            'user_roles_{user_id}'
        ]
    
    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 构建键值字符串
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        
        # 添加关键字参数
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend(f"{k}:{v}" for k, v in sorted_kwargs)
        
        # 生成最终键值
        key_string = "_".join(key_parts)
        
        # 如果键值过长，使用哈希
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}_{key_hash}"
        
        return key_string
    
    def get_multi_level(self, key: str, fetch_func: Callable = None, 
                       timeout: int = None, priority: int = 1) -> Any:
        """多级缓存获取"""
        start_time = time.time()
        
        try:
            with self.lock:
                self.performance_stats['total_requests'] += 1
                self.performance_stats['hot_keys'][key] += 1
            
            # L1缓存检查（内存）
            l1_value = self._get_l1_cache(key)
            if l1_value is not None:
                self._record_cache_hit('l1', time.time() - start_time)
                self._update_access_time(key)
                return l1_value
            
            # L2缓存检查（Redis）
            l2_value = self._get_l2_cache(key)
            if l2_value is not None:
                self._record_cache_hit('l2', time.time() - start_time)
                # 回填L1缓存
                self._set_l1_cache(key, l2_value, priority)
                return l2_value
            
            # L3缓存检查（数据库缓存表）
            l3_value = self._get_l3_cache(key)
            if l3_value is not None:
                self._record_cache_hit('l3', time.time() - start_time)
                # 回填L2和L1缓存
                self._set_l2_cache(key, l3_value, timeout)
                self._set_l1_cache(key, l3_value, priority)
                return l3_value
            
            # 缓存未命中，执行获取函数
            if fetch_func:
                value = fetch_func()
                if value is not None:
                    # 设置所有级别的缓存
                    self._set_all_levels(key, value, timeout, priority)
                
                self._record_cache_miss(time.time() - start_time)
                return value
            
            self._record_cache_miss(time.time() - start_time)
            return None
            
        except Exception as e:
            logger.error(f"多级缓存获取失败 {key}: {e}")
            # 降级到直接执行获取函数
            if fetch_func:
                return fetch_func()
            return None
    
    def set_multi_level(self, key: str, value: Any, timeout: int = None, 
                       priority: int = 1):
        """多级缓存设置"""
        try:
            self._set_all_levels(key, value, timeout, priority)
        except Exception as e:
            logger.error(f"多级缓存设置失败 {key}: {e}")
    
    def delete_multi_level(self, key: str):
        """多级缓存删除"""
        try:
            # 删除L1缓存
            with self.lock:
                self.l1_cache.pop(key, None)
                self.access_times.pop(key, None)
                self.cache_priorities.pop(key, None)
            
            # 删除L2缓存
            cache.delete(key)
            
            # 删除L3缓存
            self._delete_l3_cache(key)
            
        except Exception as e:
            logger.error(f"多级缓存删除失败 {key}: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """按模式失效缓存"""
        try:
            # L1缓存模式匹配删除
            with self.lock:
                keys_to_delete = [k for k in self.l1_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    self.l1_cache.pop(key, None)
                    self.access_times.pop(key, None)
                    self.cache_priorities.pop(key, None)
            
            # L2缓存模式删除（Redis支持）
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(f"*{pattern}*")
            
            # L3缓存模式删除
            self._delete_l3_pattern(pattern)
            
            logger.info(f"缓存模式失效完成: {pattern}")
            
        except Exception as e:
            logger.error(f"缓存模式失效失败 {pattern}: {e}")
    
    def invalidate_user_cache(self, user_id: int):
        """失效用户相关缓存"""
        patterns = [
            f"user_permissions_{user_id}",
            f"user_roles_{user_id}",
            f"menu_permissions_{user_id}",
            f"user_menu_access_{user_id}",
            f"user_role_permissions_{user_id}"
        ]
        
        for pattern in patterns:
            self.invalidate_pattern(pattern)
    
    def invalidate_role_cache(self, role_id: int):
        """失效角色相关缓存"""
        patterns = [
            f"role_permissions_{role_id}",
            f"role_users_{role_id}",
            f"role_menu_access_{role_id}"
        ]
        
        for pattern in patterns:
            self.invalidate_pattern(pattern)
    
    def preload_user_permissions(self, user_id: int):
        """预加载用户权限"""
        try:
            # from .models import RoleMenuPermission  # 已废弃，使用 MenuValidity 和 RoleMenuAssignment 替代
            from django.contrib.auth.models import Permission
            
            # 预加载用户角色
            user_roles_key = self.get_cache_key('user_roles', user_id)
            if not self._check_cache_exists(user_roles_key):
                user = User.objects.select_related().get(id=user_id)
                roles = list(user.groups.values_list('id', 'name'))
                self.set_multi_level(user_roles_key, roles, priority=3)
            
            # 预加载用户权限
            user_perms_key = self.get_cache_key('user_permissions', user_id)
            if not self._check_cache_exists(user_perms_key):
                user = User.objects.get(id=user_id)
                perms = list(user.get_all_permissions())
                self.set_multi_level(user_perms_key, perms, priority=3)
            
            # 预加载菜单权限
            menu_perms_key = self.get_cache_key('menu_permissions', user_id)
            if not self._check_cache_exists(menu_perms_key):
                # TODO: 使用 MenuValidity 和 RoleMenuAssignment 替代 RoleMenuPermission
                menu_perms = []  # 暂时返回空列表
                self.set_multi_level(menu_perms_key, menu_perms, priority=3)
            
            logger.info(f"用户权限预加载完成: {user_id}")
            
        except Exception as e:
            logger.error(f"用户权限预加载失败 {user_id}: {e}")
    
    def batch_preload(self, user_ids: List[int]):
        """批量预加载"""
        for user_id in user_ids:
            self.preload_user_permissions(user_id)
    
    def _get_l1_cache(self, key: str) -> Any:
        """获取L1缓存"""
        with self.lock:
            return self.l1_cache.get(key)
    
    def _set_l1_cache(self, key: str, value: Any, priority: int = 1):
        """设置L1缓存"""
        with self.lock:
            # 检查缓存大小限制
            if len(self.l1_cache) >= self.l1_max_size:
                self._evict_l1_cache()
            
            self.l1_cache[key] = value
            self.cache_priorities[key] = priority
            self._update_access_time(key)
    
    def _evict_l1_cache(self):
        """L1缓存淘汰策略"""
        if not self.l1_cache:
            return
        
        # 使用LRU + 优先级策略
        current_time = time.time()
        
        # 计算每个键的得分（优先级 + 最近访问时间）
        scores = {}
        for key in self.l1_cache.keys():
            priority = self.cache_priorities.get(key, 1)
            last_access = max(self.access_times.get(key, [0]))
            time_score = (current_time - last_access) / 3600  # 小时为单位
            scores[key] = priority - time_score
        
        # 删除得分最低的25%
        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k])
        keys_to_remove = sorted_keys[:len(sorted_keys) // 4]
        
        for key in keys_to_remove:
            self.l1_cache.pop(key, None)
            self.access_times.pop(key, None)
            self.cache_priorities.pop(key, None)
    
    def _get_l2_cache(self, key: str) -> Any:
        """获取L2缓存（Redis）"""
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"L2缓存获取失败 {key}: {e}")
            return None
    
    def _set_l2_cache(self, key: str, value: Any, timeout: int = None):
        """设置L2缓存（Redis）"""
        try:
            timeout = timeout or self.l2_timeout
            cache.set(key, value, timeout)
        except Exception as e:
            logger.error(f"L2缓存设置失败 {key}: {e}")
    
    def _get_l3_cache(self, key: str) -> Any:
        """获取L3缓存（数据库）"""
        try:
            from .models import PermissionCache
            cache_obj = PermissionCache.objects.filter(
                cache_key=key,
                expires_at__gt=timezone.now()
            ).first()
            
            if cache_obj:
                return json.loads(cache_obj.cache_value)
            return None
            
        except Exception as e:
            logger.error(f"L3缓存获取失败 {key}: {e}")
            return None
    
    def _set_l3_cache(self, key: str, value: Any, timeout: int = None):
        """设置L3缓存（数据库）"""
        try:
            from .models import PermissionCache
            
            timeout = timeout or self.l3_timeout
            expires_at = timezone.now() + timedelta(seconds=timeout)
            
            PermissionCache.objects.update_or_create(
                cache_key=key,
                defaults={
                    'cache_value': json.dumps(value, cls=DjangoJSONEncoder),
                    'expires_at': expires_at,
                    'created_at': timezone.now()
                }
            )
            
        except Exception as e:
            logger.error(f"L3缓存设置失败 {key}: {e}")
    
    def _delete_l3_cache(self, key: str):
        """删除L3缓存"""
        try:
            from .models import PermissionCache
            PermissionCache.objects.filter(cache_key=key).delete()
        except Exception as e:
            logger.error(f"L3缓存删除失败 {key}: {e}")
    
    def _delete_l3_pattern(self, pattern: str):
        """按模式删除L3缓存"""
        try:
            from .models import PermissionCache
            PermissionCache.objects.filter(cache_key__contains=pattern).delete()
        except Exception as e:
            logger.error(f"L3缓存模式删除失败 {pattern}: {e}")
    
    def _set_all_levels(self, key: str, value: Any, timeout: int = None, 
                       priority: int = 1):
        """设置所有级别缓存"""
        self._set_l1_cache(key, value, priority)
        self._set_l2_cache(key, value, timeout)
        self._set_l3_cache(key, value, timeout)
    
    def _check_cache_exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return (self._get_l1_cache(key) is not None or 
                self._get_l2_cache(key) is not None or 
                self._get_l3_cache(key) is not None)
    
    def _update_access_time(self, key: str):
        """更新访问时间"""
        current_time = time.time()
        if key not in self.access_times:
            self.access_times[key] = []
        
        self.access_times[key].append(current_time)
        
        # 只保留最近10次访问时间
        if len(self.access_times[key]) > 10:
            self.access_times[key] = self.access_times[key][-10:]
    
    def _record_cache_hit(self, level: str, response_time: float):
        """记录缓存命中"""
        with self.lock:
            self.performance_stats['cache_hits'] += 1
            self._update_avg_response_time(response_time)
            self.cache_stats[f'{level}_hits'] += 1
    
    def _record_cache_miss(self, response_time: float):
        """记录缓存未命中"""
        with self.lock:
            self.performance_stats['cache_misses'] += 1
            self._update_avg_response_time(response_time)
            
            # 记录慢查询
            if response_time > 1.0:  # 超过1秒的查询
                self.performance_stats['slow_queries'].append({
                    'timestamp': timezone.now().isoformat(),
                    'response_time': response_time
                })
                
                # 只保留最近100个慢查询
                if len(self.performance_stats['slow_queries']) > 100:
                    self.performance_stats['slow_queries'] = \
                        self.performance_stats['slow_queries'][-100:]
    
    def _update_avg_response_time(self, response_time: float):
        """更新平均响应时间"""
        total_requests = self.performance_stats['total_requests']
        current_avg = self.performance_stats['avg_response_time']
        
        # 计算新的平均响应时间
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        self.performance_stats['avg_response_time'] = new_avg
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        with self.lock:
            total_requests = self.performance_stats['total_requests']
            cache_hits = self.performance_stats['cache_hits']
            
            hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'cache_hits': cache_hits,
                'cache_misses': self.performance_stats['cache_misses'],
                'hit_rate': round(hit_rate, 2),
                'avg_response_time': round(self.performance_stats['avg_response_time'], 4),
                'l1_cache_size': len(self.l1_cache),
                'l1_max_size': self.l1_max_size,
                'slow_queries_count': len(self.performance_stats['slow_queries']),
                'hot_keys': dict(sorted(
                    self.performance_stats['hot_keys'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),
                'cache_level_stats': dict(self.cache_stats)
            }
    
    def cleanup_expired_cache(self):
        """清理过期缓存"""
        try:
            from .models import PermissionCache
            
            # 清理L3过期缓存
            expired_count = PermissionCache.objects.filter(
                expires_at__lt=timezone.now()
            ).delete()[0]
            
            logger.info(f"清理了 {expired_count} 个过期的L3缓存")
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
    
    def warm_up_cache(self, user_ids: List[int] = None):
        """缓存预热"""
        try:
            if not user_ids:
                # 获取活跃用户ID
                recent_time = timezone.now() - timedelta(days=7)
                user_ids = User.objects.filter(
                    last_login__gte=recent_time
                ).values_list('id', flat=True)[:100]
            
            logger.info(f"开始缓存预热，用户数量: {len(user_ids)}")
            
            # 批量预加载
            self.batch_preload(list(user_ids))
            
            logger.info("缓存预热完成")
            
        except Exception as e:
            logger.error(f"缓存预热失败: {e}")


# 全局缓存管理器实例
cache_manager = PermissionCacheManager()


# 缓存装饰器
def cached_permission_check(timeout: int = 3600, priority: int = 1):
    """权限检查缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_manager.get_cache_key(
                f'perm_check_{func.__name__}',
                *args,
                **kwargs
            )
            
            # 尝试从缓存获取
            def fetch_func():
                return func(*args, **kwargs)
            
            return cache_manager.get_multi_level(
                cache_key,
                fetch_func,
                timeout,
                priority
            )
        
        return wrapper
    return decorator


def cached_user_permissions(timeout: int = 3600):
    """用户权限缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            cache_key = cache_manager.get_cache_key(
                'user_permissions',
                user_id,
                *args,
                **kwargs
            )
            
            def fetch_func():
                return func(user_id, *args, **kwargs)
            
            return cache_manager.get_multi_level(
                cache_key,
                fetch_func,
                timeout,
                priority=3  # 用户权限高优先级
            )
        
        return wrapper
    return decorator


def invalidate_user_cache_on_change(user_field: str = 'user_id'):
    """用户变更时失效缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 提取用户ID
            user_id = None
            if user_field in kwargs:
                user_id = kwargs[user_field]
            elif args and len(args) > 0:
                # 假设第一个参数是用户ID
                user_id = args[0]
            
            # 失效用户缓存
            if user_id:
                cache_manager.invalidate_user_cache(user_id)
            
            return result
        
        return wrapper
    return decorator


# 数据库查询优化
class QueryOptimizer:
    """查询优化器"""
    
    @staticmethod
    def optimize_user_permissions_query(user_id: int):
        """优化用户权限查询"""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        # 使用select_related和prefetch_related优化查询
        user = User.objects.select_related().prefetch_related(
            'groups__permissions',
            'user_permissions'
        ).get(id=user_id)
        
        # 获取所有权限（用户直接权限 + 组权限）
        permissions = set()
        
        # 用户直接权限
        for perm in user.user_permissions.select_related('content_type'):
            permissions.add(f"{perm.content_type.app_label}.{perm.codename}")
        
        # 组权限
        for group in user.groups.prefetch_related('permissions__content_type'):
            for perm in group.permissions.all():
                permissions.add(f"{perm.content_type.app_label}.{perm.codename}")
        
        return list(permissions)
    
    @staticmethod
    def optimize_role_permissions_query(role_id: int):
        """优化角色权限查询"""
        from django.contrib.auth.models import Group
        
        role = Group.objects.prefetch_related(
            'permissions__content_type'
        ).get(id=role_id)
        
        permissions = []
        for perm in role.permissions.all():
            permissions.append({
                'id': perm.id,
                'name': perm.name,
                'codename': perm.codename,
                'content_type': perm.content_type.app_label
            })
        
        return permissions
    
    @staticmethod
    def optimize_menu_permissions_query(user_id: int):
        """优化菜单权限查询"""
        # TODO: 使用 MenuValidity 和 RoleMenuAssignment 替代 RoleMenuPermission
        # 暂时返回所有活跃菜单
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT
                    mmc.id,
                    mmc.name,
                    mmc.path,
                    mmc.icon,
                    mmc.sort_order,
                    mmc.parent_id,
                    true as can_view,
                    true as can_add,
                    true as can_edit,
                    true as can_delete
                FROM permissions_menumoduleconfig mmc
                WHERE mmc.is_active = true
                ORDER BY mmc.sort_order
            """, [])
            
            columns = [col[0] for col in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results


# 性能监控中间件
class PermissionCacheMiddleware:
    """权限缓存中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 请求开始时间
        start_time = time.time()
        
        # 处理请求
        response = self.get_response(request)
        
        # 记录性能数据
        end_time = time.time()
        response_time = end_time - start_time
        
        # 如果是权限相关的请求，记录统计信息
        if '/api/permissions/' in request.path:
            cache_manager.performance_stats['total_requests'] += 1
            cache_manager._update_avg_response_time(response_time)
        
        return response