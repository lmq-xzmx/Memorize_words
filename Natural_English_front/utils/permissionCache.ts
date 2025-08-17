/**
 * 权限缓存管理器
 * 提供权限数据的本地缓存、同步和实时更新功能
 * 根据《用户权限管理系统规范》文档实现
 */

// 声明模块类型
declare const permissionApi: any
declare const permission: any
declare const roleDefinitions: any

import { PermissionAPI } from './permissionApi'
import { getCurrentUser } from './permission'
import { getRolePermissions } from './roleDefinitions'

// 类型定义
interface CacheKeys {
  USER_PERMISSIONS: string
  ROLE_PERMISSIONS: string
  MENU_PERMISSIONS: string
  PAGE_PERMISSIONS: string
  CACHE_TIMESTAMP: string
  CACHE_VERSION: string
}

interface CacheExpiry {
  USER_PERMISSIONS: number
  ROLE_PERMISSIONS: number
  MENU_PERMISSIONS: number
  PAGE_PERMISSIONS: number
}

interface RetryConfig {
  MAX_RETRIES: number
  RETRY_DELAY: number
  BACKOFF_MULTIPLIER: number
}

interface CacheConfig {
  CACHE_KEYS: CacheKeys
  CACHE_EXPIRY: CacheExpiry
  CURRENT_VERSION: string
  SYNC_INTERVAL: number
  RETRY_CONFIG: RetryConfig
}

interface CacheData {
  data: any
  timestamp: number
  version: string
  accessCount: number
  lastAccess: number
  priority: 'high' | 'normal' | 'low'
  persistent: boolean
  expireTime?: number | null
}

interface OfflineCacheItem {
  data: any
  timestamp: number
  expireTime: number
}

interface PerformanceStats {
  hits: number
  misses: number
  sets: number
  deletes: number
  cleanups: number
  totalRequestTime: number
  requestCount: number
  cacheEfficiency: number
}

interface CacheStrategies {
  LRU: string
  LFU: string
  PRIORITY: string
}

interface WarmupConfig {
  enabled: boolean
  commonPermissions: string[]
  preloadRoles: string[]
}

interface RetryQueueItem {
  operation: string
  params: Record<string, any>
  retries: number
  timestamp: number
}

interface GetOptions {
  fallbackToOffline?: boolean
  recordStats?: boolean
}

interface SetOptions {
  customExpireTime?: number | null
  priority?: 'high' | 'normal' | 'low'
  persistent?: boolean
  recordStats?: boolean
}

interface CacheItemInfo {
  key: string
  size: number
  timestamp: number
  expired: boolean
  accessCount: number
  lastAccess: number
  priority: string
  persistent: boolean
}

interface CacheStats {
  totalItems: number
  offlineItems: number
  memoryUsage: number
  storageUsage: number
  expiredItems: number
  items: CacheItemInfo[]
  performance: {
    hits: number
    misses: number
    hitRate: string
    avgRequestTime: string
    cacheEfficiency: string
    sets: number
    deletes: number
    cleanups: number
  }
  strategy: string
  isOnline: boolean
}

type CacheListener = (event: string, data: any) => void

/**
 * 权限缓存配置
 */
const CACHE_CONFIG: CacheConfig = {
  // 缓存键名
  CACHE_KEYS: {
    USER_PERMISSIONS: 'user_permissions',
    ROLE_PERMISSIONS: 'role_permissions',
    MENU_PERMISSIONS: 'menu_permissions',
    PAGE_PERMISSIONS: 'page_permissions',
    CACHE_TIMESTAMP: 'permissions_cache_timestamp',
    CACHE_VERSION: 'permissions_cache_version'
  },
  
  // 缓存过期时间（毫秒）
  CACHE_EXPIRY: {
    USER_PERMISSIONS: 30 * 60 * 1000, // 30分钟
    ROLE_PERMISSIONS: 60 * 60 * 1000, // 1小时
    MENU_PERMISSIONS: 15 * 60 * 1000, // 15分钟
    PAGE_PERMISSIONS: 15 * 60 * 1000  // 15分钟
  },
  
  // 缓存版本
  CURRENT_VERSION: '1.0.0',
  
  // 同步间隔
  SYNC_INTERVAL: 5 * 60 * 1000, // 5分钟
  
  // 重试配置
  RETRY_CONFIG: {
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000, // 1秒
    BACKOFF_MULTIPLIER: 2
  }
}

/**
 * 增强的权限缓存管理器类
 * 提供智能缓存、性能监控和离线权限验证功能
 */
class PermissionCacheManager {
  private cache: Map<string, CacheData>
  private offlineCache: Map<string, OfflineCacheItem>
  private listeners: Set<CacheListener>
  private syncTimer: number | null
  private isOnline: boolean
  private retryQueue: RetryQueueItem[]
  private performanceStats: PerformanceStats
  private cacheStrategies: CacheStrategies
  private currentStrategy: string
  private warmupConfig: WarmupConfig

  constructor() {
    this.cache = new Map()
    this.offlineCache = new Map() // 离线权限缓存
    this.listeners = new Set()
    this.syncTimer = null
    this.isOnline = navigator.onLine
    this.retryQueue = []
    
    // 性能监控数据
    this.performanceStats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      cleanups: 0,
      totalRequestTime: 0,
      requestCount: 0,
      cacheEfficiency: 0
    }
    
    // 智能缓存策略配置
    this.cacheStrategies = {
      LRU: 'lru', // 最近最少使用
      LFU: 'lfu', // 最少使用频率
      PRIORITY: 'priority' // 优先级策略
    }
    this.currentStrategy = this.cacheStrategies.LRU
    
    // 缓存预热配置
    this.warmupConfig = {
      enabled: true,
      commonPermissions: ['read', 'write', 'admin'],
      preloadRoles: ['user', 'admin', 'guest']
    }
    
    // 初始化
    this.init()
  }
  
  /**
   * 初始化缓存管理器
   */
  private init(): void {
    // 检查缓存版本
    this.checkCacheVersion()
    
    // 加载本地缓存
    this.loadFromLocalStorage()
    
    // 监听网络状态
    this.setupNetworkListeners()
    
    // 监听存储变化
    this.setupStorageListeners()
    
    console.log('权限缓存管理器初始化完成')
  }
  
  /**
   * 检查缓存版本
   */
  private checkCacheVersion(): void {
    const cachedVersion = localStorage.getItem(CACHE_CONFIG.CACHE_KEYS.CACHE_VERSION)
    
    if (cachedVersion !== CACHE_CONFIG.CURRENT_VERSION) {
      console.log('缓存版本不匹配，清除旧缓存')
      this.clearAllCache()
      localStorage.setItem(CACHE_CONFIG.CACHE_KEYS.CACHE_VERSION, CACHE_CONFIG.CURRENT_VERSION)
    }
  }
  
  /**
   * 从localStorage加载缓存
   */
  private loadFromLocalStorage(): void {
    Object.values(CACHE_CONFIG.CACHE_KEYS).forEach(key => {
      if (key === CACHE_CONFIG.CACHE_KEYS.CACHE_VERSION) return
      
      try {
        const cached = localStorage.getItem(key)
        if (cached) {
          const data = JSON.parse(cached)
          this.cache.set(key, data)
        }
      } catch (error) {
        console.error(`加载缓存失败 ${key}:`, error)
        localStorage.removeItem(key)
      }
    })
  }
  
  /**
   * 设置网络状态监听
   */
  private setupNetworkListeners(): void {
    window.addEventListener('online', () => {
      this.isOnline = true
      console.log('网络已连接，开始处理重试队列')
      this.processRetryQueue()
    })
    
    window.addEventListener('offline', () => {
      this.isOnline = false
      console.log('网络已断开，进入离线模式')
    })
  }
  
  /**
   * 设置存储变化监听
   */
  private setupStorageListeners(): void {
    window.addEventListener('storage', (event) => {
      if (event.key && Object.values(CACHE_CONFIG.CACHE_KEYS).includes(event.key)) {
        console.log('检测到权限缓存变化:', event.key)
        this.handleStorageChange(event)
      }
    })
  }
  
  /**
   * 处理存储变化
   */
  private handleStorageChange(event: StorageEvent): void {
    try {
      if (event.key && event.newValue) {
        const data = JSON.parse(event.newValue)
        this.cache.set(event.key, data)
        this.notifyListeners('cacheUpdated', { key: event.key, data })
      } else if (event.key) {
        this.cache.delete(event.key)
        this.notifyListeners('cacheCleared', { key: event.key })
      }
    } catch (error) {
      console.error('处理存储变化失败:', error)
    }
  }
  
  /**
   * 获取缓存数据（增强版）
   */
  get(key: string, options: GetOptions = {}): any {
    const { fallbackToOffline = true, recordStats = true } = options
    const startTime = performance.now()
    
    const cached = this.cache.get(key)
    
    if (!cached) {
      if (recordStats) this.performanceStats.misses++
      
      // 尝试从离线缓存获取
      if (fallbackToOffline) {
        const offlineValue = this.getOfflineCache(key)
        if (offlineValue) {
          // 将离线缓存重新加载到内存缓存
          this.set(key, offlineValue, { persistent: true, recordStats: false })
          this.recordRequestTime(startTime)
          return offlineValue
        }
      }
      
      this.recordRequestTime(startTime)
      return null
    }
    
    // 检查缓存是否过期
    if (this.isCacheExpired(key, cached.timestamp)) {
      console.log(`缓存已过期: ${key}`)
      this.delete(key)
      
      if (recordStats) this.performanceStats.misses++
      
      // 尝试从离线缓存获取
      if (fallbackToOffline) {
        const offlineValue = this.getOfflineCache(key)
        if (offlineValue) {
          this.set(key, offlineValue, { persistent: true, recordStats: false })
          this.recordRequestTime(startTime)
          return offlineValue
        }
      }
      
      this.recordRequestTime(startTime)
      return null
    }
    
    // 更新访问统计
    if (cached.accessCount !== undefined) {
      cached.accessCount++
      cached.lastAccess = Date.now()
    }
    
    if (recordStats) this.performanceStats.hits++
    this.recordRequestTime(startTime)
    
    return cached.data
  }
  
  /**
   * 设置缓存数据（增强版）
   */
  set(key: string, data: any, options: SetOptions = {}): void {
    const {
      customExpireTime = null,
      priority = 'normal',
      persistent = false,
      recordStats = true
    } = options
    
    const cacheData: CacheData = {
      data,
      timestamp: Date.now(),
      version: CACHE_CONFIG.CURRENT_VERSION,
      accessCount: 0,
      lastAccess: Date.now(),
      priority,
      persistent,
      expireTime: customExpireTime ? Date.now() + customExpireTime : null
    }
    
    // 内存缓存
    this.cache.set(key, cacheData)
    
    if (recordStats) this.performanceStats.sets++
    
    // 如果是持久化缓存，同时存储到离线缓存
    if (persistent) {
      this.setOfflineCache(key, data)
    }
    
    // 持久化缓存
    try {
      localStorage.setItem(key, JSON.stringify(cacheData))
      localStorage.setItem(CACHE_CONFIG.CACHE_KEYS.CACHE_TIMESTAMP, Date.now().toString())
    } catch (error) {
      console.error('保存缓存失败:', error)
      // 如果localStorage满了，使用智能清除策略
      this.intelligentCacheEviction()
      try {
        localStorage.setItem(key, JSON.stringify(cacheData))
      } catch (retryError) {
        console.error('重试保存缓存失败:', retryError)
      }
    }
    
    // 检查缓存大小并执行智能清理
    this.checkCacheSizeAndEvict()
    
    this.notifyListeners('cacheSet', { key, data })
  }
  
  /**
   * 删除缓存数据
   */
  delete(key: string): void {
    this.cache.delete(key)
    localStorage.removeItem(key)
    this.notifyListeners('cacheDeleted', { key })
  }
  
  /**
   * 检查缓存是否过期
   */
  private isCacheExpired(key: string, timestamp: number): boolean {
    if (!timestamp) return true
    
    const expiry = (CACHE_CONFIG.CACHE_EXPIRY as any)[key.toUpperCase()] || CACHE_CONFIG.CACHE_EXPIRY.USER_PERMISSIONS
    return Date.now() - timestamp > expiry
  }
  
  /**
   * 智能缓存驱逐策略
   */
  private intelligentCacheEviction(): void {
    const entries = Array.from(this.cache.entries())
    const maxSize = 1000 // 最大缓存条目数
    
    if (entries.length <= maxSize * 0.8) {
      return // 缓存使用率未达到80%，无需清理
    }
    
    const deleteCount = Math.floor(maxSize * 0.2) // 删除20%
    let sortedEntries: [string, CacheData][]
    
    switch (this.currentStrategy) {
      case this.cacheStrategies.LRU:
        // 按最后访问时间排序
        sortedEntries = entries.sort((a, b) => 
          (a[1].lastAccess || a[1].timestamp) - (b[1].lastAccess || b[1].timestamp)
        )
        break
      case this.cacheStrategies.LFU:
        // 按访问次数排序
        sortedEntries = entries.sort((a, b) => 
          (a[1].accessCount || 0) - (b[1].accessCount || 0)
        )
        break
      case this.cacheStrategies.PRIORITY:
        // 按优先级和访问时间排序
        sortedEntries = entries.sort((a, b) => {
          const priorityOrder: Record<string, number> = { high: 3, normal: 2, low: 1 }
          const aPriority = priorityOrder[a[1].priority] || 2
          const bPriority = priorityOrder[b[1].priority] || 2
          
          if (aPriority !== bPriority) {
            return aPriority - bPriority
          }
          return (a[1].lastAccess || a[1].timestamp) - (b[1].lastAccess || b[1].timestamp)
        })
        break
      default:
        // 默认按时间戳排序
        sortedEntries = entries.sort((a, b) => a[1].timestamp - b[1].timestamp)
    }
    
    // 保护高优先级和持久化缓存
    const lowPriorityEntries = sortedEntries.filter(([key, item]) => 
      item.priority !== 'high' && !item.persistent
    )
    
    const entriesToDelete = lowPriorityEntries.slice(0, Math.min(deleteCount, lowPriorityEntries.length))
    
    entriesToDelete.forEach(([key]) => {
      this.delete(key)
    })
    
    console.log(`智能缓存清理: 删除了 ${entriesToDelete.length} 个缓存项，策略: ${this.currentStrategy}`)
  }
  
  /**
   * 检查缓存大小并执行驱逐
   */
  private checkCacheSizeAndEvict(): void {
    const maxSize = 1000
    if (this.cache.size > maxSize) {
      this.intelligentCacheEviction()
    }
  }
  
  /**
   * 设置离线缓存
   */
  private setOfflineCache(key: string, data: any): void {
    try {
      const item: OfflineCacheItem = {
        data,
        timestamp: Date.now(),
        expireTime: Date.now() + (24 * 60 * 60 * 1000) // 24小时过期
      }
      
      localStorage.setItem(`offline_permission_${key}`, JSON.stringify(item))
      this.offlineCache.set(key, item)
    } catch (error) {
      console.warn('离线缓存存储失败:', error)
    }
  }
  
  /**
   * 获取离线缓存
   */
  private getOfflineCache(key: string): any {
    try {
      // 先从内存中获取
      let item = this.offlineCache.get(key)
      
      // 如果内存中没有，从localStorage获取
      if (!item) {
        const stored = localStorage.getItem(`offline_permission_${key}`)
        if (stored) {
          item = JSON.parse(stored)
          if (item) {
            this.offlineCache.set(key, item)
          }
        }
      }
      
      if (!item) {
        return null
      }
      
      // 检查是否过期
      if (Date.now() > item.expireTime) {
        this.clearOfflineCache(key)
        return null
      }
      
      return item.data
    } catch (error) {
      console.warn('离线缓存读取失败:', error)
      return null
    }
  }
  
  /**
   * 清除离线缓存
   */
  private clearOfflineCache(key: string): void {
    this.offlineCache.delete(key)
    localStorage.removeItem(`offline_permission_${key}`)
  }
  
  /**
   * 记录请求时间
   */
  private recordRequestTime(startTime: number): void {
    const duration = performance.now() - startTime
    this.performanceStats.totalRequestTime += duration
    this.performanceStats.requestCount++
    
    // 计算缓存效率
    if (this.performanceStats.requestCount > 0) {
      this.performanceStats.cacheEfficiency = 
        (this.performanceStats.hits / this.performanceStats.requestCount * 100)
    }
  }
  
  /**
   * 清除所有缓存
   */
  clearAllCache(): void {
    this.cache.clear()
    Object.values(CACHE_CONFIG.CACHE_KEYS).forEach(key => {
      localStorage.removeItem(key)
    })
    this.notifyListeners('allCacheCleared', {})
    console.log('所有权限缓存已清除')
  }
  
  /**
   * 获取用户权限（带缓存）
   */
  async getUserPermissions(userId: string, forceRefresh: boolean = false): Promise<any> {
    const cacheKey = `${CACHE_CONFIG.CACHE_KEYS.USER_PERMISSIONS}_${userId}`
    
    if (!forceRefresh) {
      const cached = this.get(cacheKey)
      if (cached) {
        return cached
      }
    }
    
    try {
      const result = await (PermissionAPI as any).getUserPermissions()
      if (result && result.success) {
        this.set(cacheKey, result.data)
        return result.data
      }
    } catch (error) {
      console.error('获取用户权限失败:', error)
      if (!this.isOnline) {
        // 离线时返回缓存数据（即使过期）
        const cached = this.cache.get(cacheKey)
        return cached?.data || null
      }
    }
    
    return null
  }
  
  /**
   * 获取角色权限（带缓存）
   */
  async getRolePermissions(role: string, forceRefresh: boolean = false): Promise<any> {
    const cacheKey = `${CACHE_CONFIG.CACHE_KEYS.ROLE_PERMISSIONS}_${role}`
    
    if (!forceRefresh) {
      const cached = this.get(cacheKey)
      if (cached) {
        return cached
      }
    }
    
    try {
      // 从本地角色定义获取权限
      const permissions = getRolePermissions(role)
      this.set(cacheKey, permissions)
      return permissions
    } catch (error) {
      console.error('获取角色权限失败:', error)
      return []
    }
  }
  
  /**
   * 同步权限数据
   */
  async syncPermissions(): Promise<boolean> {
    if (!this.isOnline) {
      console.log('离线状态，跳过权限同步')
      return false
    }
    
    try {
      const user = getCurrentUser()
      if (!user || !user.id) {
        console.log('用户未登录，跳过权限同步')
        return false
      }
      
      // 同步用户权限
      await this.getUserPermissions(user.id, true)
      
      // 同步角色权限
      if (user.role) {
        await this.getRolePermissions(user.role, true)
      }
      
      this.notifyListeners('permissionsSynced', { userId: user.id, role: user.role })
      console.log('权限同步完成')
      return true
    } catch (error) {
      console.error('权限同步失败:', error)
      this.addToRetryQueue('syncPermissions')
      return false
    }
  }
  
  /**
   * 添加到重试队列
   */
  private addToRetryQueue(operation: string, params: Record<string, any> = {}): void {
    this.retryQueue.push({
      operation,
      params,
      retries: 0,
      timestamp: Date.now()
    })
  }
  
  /**
   * 处理重试队列
   */
  private async processRetryQueue(): Promise<void> {
    if (!this.isOnline || this.retryQueue.length === 0) {
      return
    }
    
    const queue = [...this.retryQueue]
    this.retryQueue = []
    
    for (const item of queue) {
      try {
        if (item.operation === 'syncPermissions') {
          await this.syncPermissions()
        }
        console.log(`重试操作成功: ${item.operation}`)
      } catch (error) {
        console.error(`重试操作失败: ${item.operation}`, error)
        
        if (item.retries < CACHE_CONFIG.RETRY_CONFIG.MAX_RETRIES) {
          item.retries++
          setTimeout(() => {
            this.retryQueue.push(item)
          }, CACHE_CONFIG.RETRY_CONFIG.RETRY_DELAY * Math.pow(CACHE_CONFIG.RETRY_CONFIG.BACKOFF_MULTIPLIER, item.retries))
        }
      }
    }
  }
  
  /**
   * 启动自动同步
   */
  startAutoSync(): void {
    if (this.syncTimer) {
      return
    }
    
    this.syncTimer = setInterval(() => {
      this.syncPermissions()
    }, CACHE_CONFIG.SYNC_INTERVAL)
    
    console.log('权限自动同步已启动')
  }
  
  /**
   * 停止自动同步
   */
  stopAutoSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer)
      this.syncTimer = null
      console.log('权限自动同步已停止')
    }
  }
  
  /**
   * 添加监听器
   */
  addListener(callback: CacheListener): void {
    this.listeners.add(callback)
  }
  
  /**
   * 移除监听器
   */
  removeListener(callback: CacheListener): void {
    this.listeners.delete(callback)
  }
  
  /**
   * 通知监听器
   */
  private notifyListeners(event: string, data: any): void {
    this.listeners.forEach(callback => {
      try {
        callback(event, data)
      } catch (error) {
        console.error('权限缓存监听器执行失败:', error)
      }
    })
  }
  
  /**
   * 获取增强的缓存统计信息
   */
  getCacheStats(): CacheStats {
    const stats: CacheStats = {
      totalItems: this.cache.size,
      offlineItems: this.offlineCache.size,
      memoryUsage: 0,
      storageUsage: 0,
      expiredItems: 0,
      items: [],
      performance: {
        hits: this.performanceStats.hits,
        misses: this.performanceStats.misses,
        hitRate: this.performanceStats.requestCount > 0 
          ? `${(this.performanceStats.hits / this.performanceStats.requestCount * 100).toFixed(2)}%`
          : '0%',
        avgRequestTime: this.performanceStats.requestCount > 0
          ? `${(this.performanceStats.totalRequestTime / this.performanceStats.requestCount).toFixed(2)}ms`
          : '0ms',
        cacheEfficiency: `${this.performanceStats.cacheEfficiency.toFixed(2)}%`,
        sets: this.performanceStats.sets,
        deletes: this.performanceStats.deletes,
        cleanups: this.performanceStats.cleanups
      },
      strategy: this.currentStrategy,
      isOnline: this.isOnline
    }
    
    this.cache.forEach((value, key) => {
      const itemSize = JSON.stringify(value).length
      stats.memoryUsage += itemSize
      
      const isExpired = this.isCacheExpired(key, value.timestamp)
      if (isExpired) {
        stats.expiredItems++
      }
      
      stats.items.push({
        key,
        size: itemSize,
        timestamp: value.timestamp,
        expired: isExpired,
        accessCount: value.accessCount || 0,
        lastAccess: value.lastAccess,
        priority: value.priority || 'normal',
        persistent: value.persistent || false
      })
    })
    
    // 计算localStorage使用量
    try {
      Object.values(CACHE_CONFIG.CACHE_KEYS).forEach(key => {
        const item = localStorage.getItem(key)
        if (item) {
          stats.storageUsage += item.length
        }
      })
      
      // 计算离线缓存使用量
      const offlineKeys = Object.keys(localStorage).filter(key => 
        key.startsWith('offline_permission_')
      )
      offlineKeys.forEach(key => {
        const item = localStorage.getItem(key)
        if (item) {
          stats.storageUsage += item.length
        }
      })
    } catch (error) {
      console.error('计算存储使用量失败:', error)
    }
    
    return stats
  }
  
  /**
   * 设置缓存策略
   */
  setCacheStrategy(strategy: string): void {
    if (Object.values(this.cacheStrategies).includes(strategy)) {
      this.currentStrategy = strategy
      console.log(`缓存策略已设置为: ${strategy}`)
      this.notifyListeners('strategyChanged', { strategy })
    } else {
      console.warn(`无效的缓存策略: ${strategy}`)
    }
  }
  
  /**
   * 缓存预热
   */
  async warmupCache(): Promise<void> {
    if (!this.warmupConfig.enabled) {
      return
    }
    
    console.log('开始缓存预热...')
    
    try {
      const user = getCurrentUser()
      if (!user || !user.id) {
        console.log('用户未登录，跳过缓存预热')
        return
      }
      
      // 预热用户权限
      await this.getUserPermissions(user.id, false)
      
      // 预热角色权限
      if (user.role && this.warmupConfig.preloadRoles.includes(user.role)) {
        await this.getRolePermissions(user.role, false)
      }
      
      // 预热常用权限
      for (const permission of this.warmupConfig.commonPermissions) {
        const cacheKey = `permission_check_${user.id}_${permission}`
        // 这里可以预加载常用权限检查结果
      }
      
      console.log('缓存预热完成')
      this.notifyListeners('warmupCompleted', { userId: user.id })
    } catch (error) {
      console.error('缓存预热失败:', error)
    }
  }
  
  /**
   * 清除用户相关缓存
   */
  clearUserCache(userId: string): void {
    const keysToDelete: string[] = []
    
    for (const key of this.cache.keys()) {
      if (key.includes(`_${userId}`) || key.includes(`user_${userId}`)) {
        keysToDelete.push(key)
      }
    }
    
    keysToDelete.forEach(key => this.delete(key))
    console.log(`清除用户 ${userId} 的 ${keysToDelete.length} 个缓存项`)
    
    this.notifyListeners('userCacheCleared', { userId, count: keysToDelete.length })
  }
  
  /**
   * 清除角色相关缓存
   */
  clearRoleCache(role: string): void {
    const keysToDelete: string[] = []
    
    for (const key of this.cache.keys()) {
      if (key.includes(`_${role}`) || key.includes(`role_${role}`)) {
        keysToDelete.push(key)
      }
    }
    
    keysToDelete.forEach(key => this.delete(key))
    console.log(`清除角色 ${role} 的 ${keysToDelete.length} 个缓存项`)
    
    this.notifyListeners('roleCacheCleared', { role, count: keysToDelete.length })
  }
}

// 创建全局实例
const permissionCacheManager = new PermissionCacheManager()

// 导出便捷函数
export async function getUserPermissions(userId: string, forceRefresh: boolean = false): Promise<any> {
  return await permissionCacheManager.getUserPermissions(userId, forceRefresh)
}

export async function getRolePermissionsFromCache(role: string, forceRefresh: boolean = false): Promise<any> {
  return await permissionCacheManager.getRolePermissions(role, forceRefresh)
}

export async function syncPermissions(): Promise<boolean> {
  return await permissionCacheManager.syncPermissions()
}

export function clearPermissionCache(): void {
  permissionCacheManager.clearAllCache()
}

export function startPermissionSync(): void {
  permissionCacheManager.startAutoSync()
}

export function stopPermissionSync(): void {
  permissionCacheManager.stopAutoSync()
}

export function addPermissionCacheListener(callback: CacheListener): void {
  permissionCacheManager.addListener(callback)
}

export function removePermissionCacheListener(callback: CacheListener): void {
  permissionCacheManager.removeListener(callback)
}

export function getPermissionCacheStats(): CacheStats {
  return permissionCacheManager.getCacheStats()
}

export function getCacheStats(): CacheStats {
  return permissionCacheManager.getCacheStats()
}

export function cleanExpiredCache(): void {
  return (permissionCacheManager as any).intelligentCacheEviction()
}

export function getPermissionCache(): PermissionCacheManager {
  return permissionCacheManager
}

export function setPermissionCache(key: string, value: any, options: SetOptions = {}): void {
  return permissionCacheManager.set(key, value, options)
}

export default permissionCacheManager