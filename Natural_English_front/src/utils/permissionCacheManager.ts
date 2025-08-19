import { ElMessage } from 'element-plus'

// 缓存项接口
interface CacheItem<T> {
  value: T
  timestamp: number
  accessCount: number
  lastAccess: number
  priority: number
}

// 缓存配置接口
interface CacheConfig {
  maxSize: number
  defaultTTL: number
  cleanupInterval: number
  enableMetrics: boolean
}

// 缓存指标接口
interface CacheMetrics {
  hits: number
  misses: number
  evictions: number
  totalRequests: number
  hitRate: number
  avgAccessTime: number
}

// 权限缓存键类型
type PermissionCacheKey = 
  | `user_permissions_${string}`
  | `role_permissions_${string}`
  | `menu_permissions_${string}`
  | `user_roles_${string}`
  | `route_permissions_${string}`
  | `component_permissions_${string}`

/**
 * 权限缓存管理器
 * 实现LRU缓存算法，支持TTL、优先级和性能指标
 */
export class PermissionCacheManager {
  private cache = new Map<string, CacheItem<any>>()
  private accessOrder = new Map<string, number>() // 访问顺序
  private config: CacheConfig
  private metrics: CacheMetrics
  private cleanupTimer: NodeJS.Timeout | null = null
  private accessCounter = 0
  private isInitialized = false

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: config.maxSize || 500,
      defaultTTL: config.defaultTTL || 5 * 60 * 1000, // 5分钟
      cleanupInterval: config.cleanupInterval || 60 * 1000, // 1分钟
      enableMetrics: config.enableMetrics !== false
    }

    this.metrics = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalRequests: 0,
      hitRate: 0,
      avgAccessTime: 0
    }
  }

  /**
   * 初始化缓存管理器
   */
  init(): void {
    if (!this.isInitialized) {
      this.startCleanupTimer()
      this.isInitialized = true
    }
  }

  /**
   * 设置缓存项
   */
  set<T>(key: PermissionCacheKey, value: T, ttl?: number, priority = 1): void {
    if (!this.isInitialized) {
      this.init()
    }

    // 如果缓存已满，执行LRU淘汰
    if (this.cache.size >= this.config.maxSize && !this.cache.has(key)) {
      this.evictLRU()
    }

    const now = Date.now()
    const item: CacheItem<T> = {
      value,
      timestamp: now,
      accessCount: 1,
      lastAccess: now,
      priority
    }

    this.cache.set(key, item)
    this.updateAccessOrder(key)
  }

  /**
   * 获取缓存项
   */
  get<T>(key: PermissionCacheKey): T | null {
    const startTime = Date.now()
    
    if (!this.isInitialized) {
      this.init()
    }

    const item = this.cache.get(key)
    
    if (this.config.enableMetrics) {
      this.metrics.totalRequests++
      if (item && !this.isExpired(item)) {
        this.metrics.hits++
      } else {
        this.metrics.misses++
      }
      this.updateMetrics(startTime)
    }

    if (!item || this.isExpired(item)) {
      if (item) {
        this.cache.delete(key)
        this.accessOrder.delete(key)
      }
      return null
    }

    // 更新访问信息
    item.accessCount++
    item.lastAccess = Date.now()
    this.updateAccessOrder(key)

    return item.value as T
  }

  /**
   * 检查缓存项是否存在
   */
  has(key: PermissionCacheKey): boolean {
    if (!this.isInitialized) {
      this.init()
    }
    
    const item = this.cache.get(key)
    if (!item || this.isExpired(item)) {
      if (item) {
        this.cache.delete(key)
        this.accessOrder.delete(key)
      }
      return false
    }
    return true
  }

  /**
   * 删除缓存项
   */
  delete(key: PermissionCacheKey): boolean {
    this.accessOrder.delete(key)
    return this.cache.delete(key)
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
    this.accessOrder.clear()
    this.resetMetrics()
  }

  /**
   * 批量设置缓存项
   */
  setMultiple<T>(entries: Array<[PermissionCacheKey, T]>, ttl?: number, priority = 1): void {
    entries.forEach(([key, value]) => {
      this.set(key, value, ttl, priority)
    })
  }

  /**
   * 批量获取缓存项
   */
  getMultiple<T>(keys: PermissionCacheKey[]): Map<PermissionCacheKey, T | null> {
    const result = new Map<PermissionCacheKey, T | null>()
    keys.forEach(key => {
      result.set(key, this.get<T>(key))
    })
    return result
  }

  /**
   * 根据模式删除缓存项
   */
  deleteByPattern(pattern: string): number {
    let deletedCount = 0
    const regex = new RegExp(pattern)
    
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.delete(key as PermissionCacheKey)
        deletedCount++
      }
    }
    
    return deletedCount
  }

  /**
   * 获取缓存指标
   */
  getMetrics(): CacheMetrics {
    return { ...this.metrics }
  }

  /**
   * 获取缓存大小
   */
  size(): number {
    return this.cache.size
  }

  /**
   * 获取热点数据
   */
  getHotKeys(limit = 10): Array<{ key: string; accessCount: number; lastAccess: number }> {
    return Array.from(this.cache.entries())
      .map(([key, item]) => ({
        key,
        accessCount: item.accessCount,
        lastAccess: item.lastAccess
      }))
      .sort((a, b) => b.accessCount - a.accessCount)
      .slice(0, limit)
  }

  /**
   * 预热缓存
   */
  async warmup(userId: string, role: string): Promise<void> {
    try {
      // 这里可以预加载一些常用的权限数据
      console.log(`缓存预热开始: 用户${userId}, 角色${role}`)
      
      // 预设一些常用的缓存键
      const commonKeys = [
        `user_permissions_${userId}`,
        `user_roles_${userId}`,
        `role_permissions_${role}`,
        `menu_permissions_${userId}`
      ]
      
      // 这里可以调用实际的数据加载逻辑
      console.log('预热缓存键:', commonKeys)
    } catch (error) {
      console.error('缓存预热失败:', error)
    }
  }

  /**
   * 导出缓存数据
   */
  exportCache(): Record<string, any> {
    const exported: Record<string, any> = {}
    for (const [key, item] of this.cache.entries()) {
      if (!this.isExpired(item)) {
        exported[key] = {
          value: item.value,
          timestamp: item.timestamp,
          accessCount: item.accessCount,
          lastAccess: item.lastAccess,
          priority: item.priority
        }
      }
    }
    return exported
  }

  /**
   * 销毁缓存管理器
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer)
      this.cleanupTimer = null
    }
    this.clear()
    this.isInitialized = false
  }

  // 私有方法
  private isExpired(item: CacheItem<any>): boolean {
    return Date.now() - item.timestamp > this.config.defaultTTL
  }

  private updateAccessOrder(key: string): void {
    this.accessOrder.set(key, ++this.accessCounter)
  }

  private evictLRU(): void {
    let oldestKey = ''
    let oldestAccess = Infinity
    let lowestPriority = Infinity

    for (const [key, accessTime] of this.accessOrder.entries()) {
      const item = this.cache.get(key)
      if (item) {
        // 优先淘汰低优先级的项目
        if (item.priority < lowestPriority || 
           (item.priority === lowestPriority && accessTime < oldestAccess)) {
          oldestKey = key
          oldestAccess = accessTime
          lowestPriority = item.priority
        }
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey)
      this.accessOrder.delete(oldestKey)
      if (this.config.enableMetrics) {
        this.metrics.evictions++
      }
    }
  }

  private updateMetrics(startTime: number): void {
    const accessTime = Date.now() - startTime
    this.metrics.avgAccessTime = 
      (this.metrics.avgAccessTime * (this.metrics.totalRequests - 1) + accessTime) / 
      this.metrics.totalRequests
    
    this.metrics.hitRate = this.metrics.hits / this.metrics.totalRequests
  }

  private resetMetrics(): void {
    this.metrics = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalRequests: 0,
      hitRate: 0,
      avgAccessTime: 0
    }
  }

  private startCleanupTimer(): void {
    if (this.cleanupTimer) return
    
    this.cleanupTimer = setInterval(() => {
      this.cleanup()
    }, this.config.cleanupInterval)
  }

  private cleanup(): void {
    const now = Date.now()
    const expiredKeys: string[] = []
    
    for (const [key, item] of this.cache.entries()) {
      if (this.isExpired(item)) {
        expiredKeys.push(key)
      }
    }
    
    expiredKeys.forEach(key => {
      this.cache.delete(key)
      this.accessOrder.delete(key)
    })
    
    if (expiredKeys.length > 0) {
      console.log(`清理了 ${expiredKeys.length} 个过期缓存项`)
    }
  }
}

// 创建缓存管理器实例
const cacheManager = new PermissionCacheManager({
  maxSize: 1000,
  defaultTTL: 5 * 60 * 1000, // 5分钟
  cleanupInterval: 60 * 1000, // 1分钟清理一次
  enableMetrics: true
})

// 导出缓存管理器实例
export const permissionCacheManager = cacheManager

/**
 * 权限缓存工具类
 */
export const PermissionCacheUtils = {
  /**
   * 生成用户权限缓存键
   */
  getUserPermissionKey(userId: string): PermissionCacheKey {
    return `user_permissions_${userId}`
  },

  /**
   * 生成角色权限缓存键
   */
  getRolePermissionKey(roleId: string): PermissionCacheKey {
    return `role_permissions_${roleId}`
  },

  /**
   * 生成菜单权限缓存键
   */
  getMenuPermissionKey(userId: string): PermissionCacheKey {
    return `menu_permissions_${userId}`
  },

  /**
   * 生成用户角色缓存键
   */
  getUserRoleKey(userId: string): PermissionCacheKey {
    return `user_roles_${userId}`
  },

  /**
   * 生成路由权限缓存键
   */
  getRoutePermissionKey(route: string, userId: string): PermissionCacheKey {
    return `route_permissions_${route}_${userId}`
  },

  /**
   * 生成组件权限缓存键
   */
  getComponentPermissionKey(component: string, userId: string): PermissionCacheKey {
    return `component_permissions_${component}_${userId}`
  },

  /**
   * 清理用户相关缓存
   */
  clearUserCache(userId: string, cacheManager: PermissionCacheManager): number {
    let clearedCount = 0
    
    // 直接删除特定键
    const userKeys = [
      `user_permissions_${userId}`,
      `user_roles_${userId}`,
      `menu_permissions_${userId}`
    ]
    
    userKeys.forEach(key => {
      if (cacheManager.delete(key as PermissionCacheKey)) {
        clearedCount++
      }
    })
    
    // 删除路由和组件权限（使用模式匹配）
    clearedCount += cacheManager.deleteByPattern(`route_permissions_.*_${userId}`)
    clearedCount += cacheManager.deleteByPattern(`component_permissions_.*_${userId}`)
    
    return clearedCount
  },

  /**
   * 清理角色相关缓存
   */
  clearRoleCache(roleId: string, cacheManager: PermissionCacheManager): number {
    return cacheManager.deleteByPattern(`role_permissions_${roleId}`)
  },

  /**
   * 显示缓存统计信息
   */
  showCacheStats(cacheManager: PermissionCacheManager): void {
    const metrics = cacheManager.getMetrics()
    const hotKeys = cacheManager.getHotKeys(5)
    
    console.group('权限缓存统计')
    console.log('缓存大小:', cacheManager.size())
    console.log('命中率:', `${(metrics.hitRate * 100).toFixed(2)}%`)
    console.log('总请求数:', metrics.totalRequests)
    console.log('命中次数:', metrics.hits)
    console.log('未命中次数:', metrics.misses)
    console.log('淘汰次数:', metrics.evictions)
    console.log('平均访问时间:', `${metrics.avgAccessTime.toFixed(2)}ms`)
    console.log('热点数据:', hotKeys)
    console.groupEnd()
    
    ElMessage.success('缓存统计信息已输出到控制台')
  }
}

// 延迟初始化，避免循环引用
setTimeout(() => {
  cacheManager.init()
}, 0)

// 在开发环境下暴露到全局对象，便于调试
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  ;(window as any).permissionCacheManager = permissionCacheManager
  ;(window as any).PermissionCacheUtils = PermissionCacheUtils
}