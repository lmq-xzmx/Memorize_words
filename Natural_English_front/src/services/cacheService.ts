import type { MenuItem, ToolItem } from '@/composables/useMenuManager'

// 缓存键前缀
const CACHE_PREFIX = 'menu_cache_'
const VERSION_KEY = 'menu_version'
const LAST_UPDATE_KEY = 'menu_last_update'

// 缓存配置
interface CacheConfig {
  ttl: number // 生存时间（毫秒）
  maxSize: number // 最大缓存大小
  enableCompression: boolean // 是否启用压缩
  enableEncryption: boolean // 是否启用加密
}

// 默认缓存配置
const defaultCacheConfig: CacheConfig = {
  ttl: 30 * 60 * 1000, // 30分钟
  maxSize: 100, // 最多100个缓存项
  enableCompression: true,
  enableEncryption: false
}

// 缓存项接口
interface CacheItem<T = any> {
  key: string
  data: T
  timestamp: number
  ttl: number
  version?: number
  compressed?: boolean
  encrypted?: boolean
}

// 缓存统计信息
interface CacheStats {
  size: number
  keys: string[]
  hitRate: number
  missRate: number
  totalHits: number
  totalMisses: number
  lastCleanup: number
}

// 版本信息
interface VersionInfo {
  version: number
  timestamp: number
  checksum?: string
  changes?: string[]
}

class CacheService {
  private config: CacheConfig
  private cache: Map<string, CacheItem>
  private stats: CacheStats
  private cleanupTimer: number | null = null

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = { ...defaultCacheConfig, ...config }
    this.cache = new Map()
    this.stats = {
      size: 0,
      keys: [],
      hitRate: 0,
      missRate: 0,
      totalHits: 0,
      totalMisses: 0,
      lastCleanup: Date.now()
    }
    
    // 启动定期清理
    this.startCleanupTimer()
    
    // 从 localStorage 恢复缓存
    this.restoreFromStorage()
  }

  // 设置缓存项
  set<T>(key: string, data: T, ttl?: number, version?: number): void {
    const fullKey = this.getFullKey(key)
    const item: CacheItem<T> = {
      key: fullKey,
      data: this.processData(data),
      timestamp: Date.now(),
      ttl: ttl || this.config.ttl,
      version,
      compressed: this.config.enableCompression,
      encrypted: this.config.enableEncryption
    }

    // 检查缓存大小限制
    if (this.cache.size >= this.config.maxSize) {
      this.evictOldest()
    }

    this.cache.set(fullKey, item)
    this.updateStats()
    this.saveToStorage(fullKey, item)
  }

  // 获取缓存项
  get<T>(key: string): T | null {
    const fullKey = this.getFullKey(key)
    const item = this.cache.get(fullKey)

    if (!item) {
      this.stats.totalMisses++
      this.updateHitRate()
      return null
    }

    // 检查是否过期
    if (this.isExpired(item)) {
      this.delete(key)
      this.stats.totalMisses++
      this.updateHitRate()
      return null
    }

    this.stats.totalHits++
    this.updateHitRate()
    return this.restoreData(item.data)
  }

  // 删除缓存项
  delete(key: string): boolean {
    const fullKey = this.getFullKey(key)
    const deleted = this.cache.delete(fullKey)
    
    if (deleted) {
      this.updateStats()
      this.removeFromStorage(fullKey)
    }
    
    return deleted
  }

  // 检查缓存项是否存在且未过期
  has(key: string): boolean {
    const fullKey = this.getFullKey(key)
    const item = this.cache.get(fullKey)
    
    if (!item) return false
    
    if (this.isExpired(item)) {
      this.delete(key)
      return false
    }
    
    return true
  }

  // 清空所有缓存
  clear(): void {
    this.cache.clear()
    this.updateStats()
    this.clearStorage()
  }

  // 获取缓存统计信息
  getStats(): CacheStats {
    return { ...this.stats }
  }

  // 设置菜单版本
  setMenuVersion(version: number, changes?: string[]): void {
    const versionInfo: VersionInfo = {
      version,
      timestamp: Date.now(),
      changes
    }
    
    this.set(VERSION_KEY, versionInfo)
    localStorage.setItem(CACHE_PREFIX + VERSION_KEY, JSON.stringify(versionInfo))
  }

  // 获取菜单版本
  getMenuVersion(): VersionInfo | null {
    const cached = this.get<VersionInfo>(VERSION_KEY)
    if (cached) return cached
    
    // 从 localStorage 获取
    const stored = localStorage.getItem(CACHE_PREFIX + VERSION_KEY)
    if (stored) {
      try {
        return JSON.parse(stored)
      } catch (error) {
        console.error('解析版本信息失败:', error)
      }
    }
    
    return null
  }

  // 检查版本是否需要更新
  needsUpdate(serverVersion: number): boolean {
    const localVersion = this.getMenuVersion()
    return !localVersion || localVersion.version < serverVersion
  }

  // 缓存菜单配置
  cacheMenuConfig(menus: MenuItem[], version?: number): void {
    this.set('menu_config', menus, undefined, version)
  }

  // 获取缓存的菜单配置
  getCachedMenuConfig(): MenuItem[] | null {
    return this.get<MenuItem[]>('menu_config')
  }

  // 缓存工具配置
  cacheToolsConfig(tools: ToolItem[], version?: number): void {
    this.set('tools_config', tools, undefined, version)
  }

  // 获取缓存的工具配置
  getCachedToolsConfig(): ToolItem[] | null {
    return this.get<ToolItem[]>('tools_config')
  }

  // 缓存用户权限
  cacheUserPermissions(userId: string, permissions: string[], roles: string[]): void {
    const key = `user_permissions_${userId}`
    this.set(key, { permissions, roles }, 15 * 60 * 1000) // 15分钟过期
  }

  // 获取缓存的用户权限
  getCachedUserPermissions(userId: string): { permissions: string[]; roles: string[] } | null {
    const key = `user_permissions_${userId}`
    return this.get(key)
  }

  // 清除用户权限缓存
  clearUserPermissions(userId: string): void {
    const key = `user_permissions_${userId}`
    this.delete(key)
  }

  // 智能缓存更新策略
  async smartUpdate<T>(key: string, fetchFn: () => Promise<T>, options?: {
    forceUpdate?: boolean
    compareChecksum?: boolean
    version?: number
  }): Promise<T> {
    const fullKey = this.getFullKey(key)
    const cached = this.cache.get(fullKey)
    
    // 强制更新
    if (options?.forceUpdate) {
      const data = await fetchFn()
      this.set(key, data, undefined, options.version)
      return data
    }
    
    // 检查缓存是否存在且未过期
    if (cached && !this.isExpired(cached)) {
      // 版本检查
      if (options?.version && cached.version && cached.version >= options.version) {
        this.stats.totalHits++
        this.updateHitRate()
        return this.restoreData(cached.data)
      }
    }
    
    // 获取新数据
    const data = await fetchFn()
    this.set(key, data, undefined, options?.version)
    return data
  }

  // 增量缓存更新
  async incrementalUpdate<T extends { id: string }>(
    key: string, 
    updates: Array<{ action: 'create' | 'update' | 'delete', item: T }>,
    version?: number
  ): Promise<T[]> {
    const cached = this.get<T[]>(key) || []
    let updatedData = [...cached]
    
    for (const update of updates) {
      const index = updatedData.findIndex(item => item.id === update.item.id)
      
      switch (update.action) {
        case 'create':
          if (index === -1) {
            updatedData.push(update.item)
          }
          break
        case 'update':
          if (index !== -1) {
            updatedData[index] = { ...updatedData[index], ...update.item }
          }
          break
        case 'delete':
          if (index !== -1) {
            updatedData.splice(index, 1)
          }
          break
      }
    }
    
    this.set(key, updatedData, undefined, version)
    return updatedData
  }

  // 批量缓存失效
  invalidateByPattern(pattern: string): number {
    let invalidatedCount = 0
    const regex = new RegExp(pattern)
    
    for (const [key] of this.cache) {
      if (regex.test(key)) {
        this.cache.delete(key)
        this.removeFromStorage(key)
        invalidatedCount++
      }
    }
    
    this.updateStats()
    return invalidatedCount
  }

  // 预热缓存
  async warmupCache(warmupConfig: Array<{
    key: string
    fetchFn: () => Promise<any>
    priority: 'high' | 'medium' | 'low'
  }>): Promise<void> {
    // 按优先级排序
    const sortedConfig = warmupConfig.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 }
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    })
    
    const promises = sortedConfig.map(async config => {
      try {
        const data = await config.fetchFn()
        this.set(config.key, data)
        console.log(`缓存预热完成: ${config.key}`)
      } catch (error) {
        console.error(`缓存预热失败: ${config.key}`, error)
      }
    })
    
    await Promise.allSettled(promises)
  }

  // 批量设置缓存
  setBatch(items: Array<{ key: string; data: any; ttl?: number; version?: number }>): void {
    items.forEach(item => {
      this.set(item.key, item.data, item.ttl, item.version)
    })
  }

  // 批量获取缓存
  getBatch<T>(keys: string[]): Record<string, T | null> {
    const result: Record<string, T | null> = {}
    keys.forEach(key => {
      result[key] = this.get<T>(key)
    })
    return result
  }

  // 获取完整键名
  private getFullKey(key: string): string {
    return CACHE_PREFIX + key
  }

  // 检查缓存项是否过期
  private isExpired(item: CacheItem): boolean {
    return Date.now() - item.timestamp > item.ttl
  }

  // 处理数据（压缩/加密）
  private processData<T>(data: T): T {
    let processed = data
    
    if (this.config.enableCompression) {
      // 简单的JSON压缩（实际项目中可使用更好的压缩算法）
      processed = JSON.parse(JSON.stringify(processed)) as T
    }
    
    if (this.config.enableEncryption) {
      // 这里可以添加加密逻辑
      // processed = encrypt(processed)
    }
    
    return processed
  }

  // 恢复数据（解压缩/解密）
  private restoreData<T>(data: T): T {
    let restored = data
    
    if (this.config.enableEncryption) {
      // 这里可以添加解密逻辑
      // restored = decrypt(restored)
    }
    
    if (this.config.enableCompression) {
      // 解压缩逻辑
      restored = JSON.parse(JSON.stringify(restored)) as T
    }
    
    return restored
  }

  // 淘汰最旧的缓存项
  private evictOldest(): void {
    let oldestKey = ''
    let oldestTime = Date.now()
    
    for (const [key, item] of this.cache) {
      if (item.timestamp < oldestTime) {
        oldestTime = item.timestamp
        oldestKey = key
      }
    }
    
    if (oldestKey) {
      this.cache.delete(oldestKey)
      this.removeFromStorage(oldestKey)
    }
  }

  // 更新统计信息
  private updateStats(): void {
    this.stats.size = this.cache.size
    this.stats.keys = Array.from(this.cache.keys())
  }

  // 更新命中率
  private updateHitRate(): void {
    const total = this.stats.totalHits + this.stats.totalMisses
    if (total > 0) {
      this.stats.hitRate = this.stats.totalHits / total
      this.stats.missRate = this.stats.totalMisses / total
    }
  }

  // 启动清理定时器
  private startCleanupTimer(): void {
    this.cleanupTimer = window.setInterval(() => {
      this.cleanup()
    }, 5 * 60 * 1000) // 每5分钟清理一次
  }

  // 清理过期缓存
  private cleanup(): void {
    const now = Date.now()
    const expiredKeys: string[] = []
    
    for (const [key, item] of this.cache) {
      if (this.isExpired(item)) {
        expiredKeys.push(key)
      }
    }
    
    expiredKeys.forEach(key => {
      this.cache.delete(key)
      this.removeFromStorage(key)
    })
    
    this.stats.lastCleanup = now
    this.updateStats()
  }

  // 保存到 localStorage
  private saveToStorage(key: string, item: CacheItem): void {
    try {
      localStorage.setItem(key, JSON.stringify(item))
    } catch (error) {
      console.warn('保存缓存到localStorage失败:', error)
    }
  }

  // 从 localStorage 删除
  private removeFromStorage(key: string): void {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.warn('从localStorage删除缓存失败:', error)
    }
  }

  // 清空 localStorage 中的缓存
  private clearStorage(): void {
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith(CACHE_PREFIX)) {
          localStorage.removeItem(key)
        }
      })
    } catch (error) {
      console.warn('清空localStorage缓存失败:', error)
    }
  }

  // 从 localStorage 恢复缓存
  private restoreFromStorage(): void {
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith(CACHE_PREFIX)) {
          const stored = localStorage.getItem(key)
          if (stored) {
            try {
              const item: CacheItem = JSON.parse(stored)
              if (!this.isExpired(item)) {
                this.cache.set(key, item)
              } else {
                localStorage.removeItem(key)
              }
            } catch (error) {
              console.warn('恢复缓存项失败:', key, error)
              localStorage.removeItem(key)
            }
          }
        }
      })
      this.updateStats()
    } catch (error) {
      console.warn('从localStorage恢复缓存失败:', error)
    }
  }

  // 销毁缓存服务
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer)
      this.cleanupTimer = null
    }
    this.clear()
  }
}

// 创建全局缓存服务实例
const cacheService = new CacheService()

// 菜单缓存管理器
class MenuCacheManager {
  private cacheService: CacheService

  constructor(cacheService: CacheService) {
    this.cacheService = cacheService
  }

  // 智能同步菜单配置
  async syncMenuConfig(serverVersion: number, fetchMenuConfig: () => Promise<MenuItem[]>, options?: {
    forceUpdate?: boolean
    incremental?: boolean
  }): Promise<MenuItem[]> {
    return await this.cacheService.smartUpdate(
      'menu_config',
      fetchMenuConfig,
      {
        forceUpdate: options?.forceUpdate,
        version: serverVersion
      }
    )
  }

  // 智能同步工具配置
  async syncToolsConfig(serverVersion: number, fetchToolsConfig: () => Promise<ToolItem[]>, options?: {
    forceUpdate?: boolean
    incremental?: boolean
  }): Promise<ToolItem[]> {
    return await this.cacheService.smartUpdate(
      'tools_config',
      fetchToolsConfig,
      {
        forceUpdate: options?.forceUpdate,
        version: serverVersion
      }
    )
  }

  // 增量更新菜单项
  async incrementalUpdateMenus(updates: Array<{
    action: 'create' | 'update' | 'delete'
    item: MenuItem
  }>, version?: number): Promise<MenuItem[]> {
    return await this.cacheService.incrementalUpdate('menu_config', updates, version)
  }

  // 增量更新工具项
  async incrementalUpdateTools(updates: Array<{
    action: 'create' | 'update' | 'delete'
    item: ToolItem
  }>, version?: number): Promise<ToolItem[]> {
    return await this.cacheService.incrementalUpdate('tools_config', updates, version)
  }

  // 处理WebSocket菜单更新消息
  async handleMenuUpdate(updateData: {
    type: 'menu' | 'tool'
    action: 'create' | 'update' | 'delete'
    items: (MenuItem | ToolItem)[]
    version?: number
  }): Promise<void> {
    const updates = updateData.items.map(item => ({
      action: updateData.action,
      item
    }))

    if (updateData.type === 'menu') {
      await this.incrementalUpdateMenus(updates as any, updateData.version)
    } else {
      await this.incrementalUpdateTools(updates as any, updateData.version)
    }

    // 更新版本信息
    if (updateData.version) {
      this.cacheService.setMenuVersion(updateData.version)
    }

    console.log(`${updateData.type}缓存已更新:`, {
      action: updateData.action,
      count: updateData.items.length,
      version: updateData.version
    })
  }

  // 预热菜单缓存
  async warmupMenuCache(fetchFunctions: {
    fetchMenuConfig: () => Promise<MenuItem[]>
    fetchToolsConfig: () => Promise<ToolItem[]>
    fetchUserPermissions?: () => Promise<any>
  }): Promise<void> {
    const warmupConfig = [
      {
        key: 'menu_config',
        fetchFn: fetchFunctions.fetchMenuConfig,
        priority: 'high' as const
      },
      {
        key: 'tools_config',
        fetchFn: fetchFunctions.fetchToolsConfig,
        priority: 'high' as const
      }
    ]

    if (fetchFunctions.fetchUserPermissions) {
      warmupConfig.push({
        key: 'user_permissions',
        fetchFn: fetchFunctions.fetchUserPermissions,
        priority: 'high' as const
      })
    }

    await this.cacheService.warmupCache(warmupConfig)
  }

  // 清除所有菜单相关缓存
  clearMenuCache(): void {
    this.cacheService.delete('menu_config')
    this.cacheService.delete('tools_config')
    this.cacheService.delete(VERSION_KEY)
  }

  // 清除过期缓存
  clearExpiredCache(): number {
    return this.cacheService.invalidateByPattern('.*')
  }

  // 获取缓存统计
  getCacheStats(): CacheStats {
    return this.cacheService.getStats()
  }

  // 获取缓存健康状态
  getCacheHealth(): {
    isHealthy: boolean
    hitRate: number
    cacheSize: number
    issues: string[]
  } {
    const stats = this.cacheService.getStats()
    const issues: string[] = []
    
    if (stats.hitRate < 0.8) {
      issues.push('缓存命中率过低')
    }
    
    if (stats.size > this.cacheService['config'].maxSize * 0.9) {
      issues.push('缓存使用率过高')
    }
    
    return {
      isHealthy: issues.length === 0,
      hitRate: stats.hitRate,
      cacheSize: stats.size,
      issues
    }
  }
}

// 创建全局菜单缓存管理器实例
const menuCacheManager = new MenuCacheManager(cacheService)

// 统一导出
export { CacheService, MenuCacheManager }
export { cacheService, menuCacheManager }
export default cacheService
export type { CacheConfig, CacheItem, CacheStats, VersionInfo }