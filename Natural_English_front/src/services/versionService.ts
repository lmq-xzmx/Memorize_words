import { cacheService } from './cacheService'
import type { MenuItem, ToolItem } from '@/composables/useMenuManager'
import { getApiBaseUrl } from '../../config/apiconfig'

// 版本信息接口
export interface VersionInfo {
  version: number
  timestamp: number
  checksum?: string
  changes?: ChangeRecord[]
  author?: string
  description?: string
}

// 变更记录接口
export interface ChangeRecord {
  type: 'create' | 'update' | 'delete'
  target: 'menu' | 'tool' | 'permission'
  targetId: string
  targetName?: string
  oldValue?: any
  newValue?: any
  timestamp: number
  author?: string
  reason?: string
}

// 版本比较结果
export interface VersionComparison {
  needsUpdate: boolean
  localVersion: number
  serverVersion: number
  changes: ChangeRecord[]
  conflictCount: number
}

// 同步结果
export interface SyncResult {
  success: boolean
  message: string
  updatedItems: {
    menus: MenuItem[]
    tools: ToolItem[]
  }
  conflicts: ConflictInfo[]
  version: VersionInfo
}

// 冲突信息
export interface ConflictInfo {
  type: 'menu' | 'tool'
  id: string
  name: string
  localValue: any
  serverValue: any
  resolution?: 'local' | 'server' | 'merge'
}

// 版本控制配置
interface VersionConfig {
  enableAutoSync: boolean
  syncInterval: number // 毫秒
  maxVersionHistory: number
  enableConflictResolution: boolean
  backupBeforeSync: boolean
}

const defaultVersionConfig: VersionConfig = {
  enableAutoSync: true,
  syncInterval: 5 * 60 * 1000, // 5分钟
  maxVersionHistory: 50,
  enableConflictResolution: true,
  backupBeforeSync: true
}

class VersionService {
  private config: VersionConfig
  private syncTimer: number | null = null
  private eventListeners: Map<string, Function[]> = new Map()

  constructor(config: Partial<VersionConfig> = {}) {
    this.config = { ...defaultVersionConfig, ...config }
    
    if (this.config.enableAutoSync) {
      this.startAutoSync()
    }
  }

  // 获取本地版本信息
  getLocalVersion(): VersionInfo | null {
    return cacheService.getMenuVersion()
  }

  // 获取服务器版本信息
  async getServerVersion(): Promise<VersionInfo> {
    try {
      const response = await fetch('/api/menu/version')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('获取服务器版本失败:', error)
      throw error
    }
  }

  // 比较版本
  async compareVersions(): Promise<VersionComparison> {
    const localVersion = this.getLocalVersion()
    const serverVersion = await this.getServerVersion()
    
    const needsUpdate = !localVersion || localVersion.version < serverVersion.version
    const changes = serverVersion.changes || []
    
    // 检查冲突
    const conflictCount = this.detectConflicts(localVersion, serverVersion)
    
    return {
      needsUpdate,
      localVersion: localVersion?.version || 0,
      serverVersion: serverVersion.version,
      changes,
      conflictCount
    }
  }

  // 检测冲突
  private detectConflicts(localVersion: VersionInfo | null, serverVersion: VersionInfo): number {
    if (!localVersion || !localVersion.changes || !serverVersion.changes) {
      return 0
    }
    
    let conflictCount = 0
    const localChanges = new Map(localVersion.changes.map(c => [c.targetId, c]))
    
    for (const serverChange of serverVersion.changes) {
      const localChange = localChanges.get(serverChange.targetId)
      if (localChange && this.isConflicting(localChange, serverChange)) {
        conflictCount++
      }
    }
    
    return conflictCount
  }

  // 判断是否冲突
  private isConflicting(localChange: ChangeRecord, serverChange: ChangeRecord): boolean {
    return localChange.targetId === serverChange.targetId && 
           localChange.target === serverChange.target &&
           localChange.type !== 'create' && 
           serverChange.type !== 'create'
  }

  // 智能合并策略
  private async smartMerge(localChanges: ChangeRecord[], serverChanges: ChangeRecord[]): Promise<ChangeRecord[]> {
    const mergedChanges: ChangeRecord[] = []
    const processedIds = new Set<string>()

    // 处理服务器变更（优先级更高）
    for (const serverChange of serverChanges) {
      const conflictingLocal = localChanges.find(local => 
        this.isConflicting(local, serverChange)
      )

      if (conflictingLocal) {
        // 冲突解决策略
        const resolvedChange = await this.resolveConflict(conflictingLocal, serverChange)
        mergedChanges.push(resolvedChange)
        processedIds.add(serverChange.targetId)
      } else {
        mergedChanges.push(serverChange)
        processedIds.add(serverChange.targetId)
      }
    }

    // 添加非冲突的本地变更
    for (const localChange of localChanges) {
      if (!processedIds.has(localChange.targetId)) {
        mergedChanges.push(localChange)
      }
    }

    return mergedChanges
  }

  // 解决单个冲突
  private async resolveConflict(localChange: ChangeRecord, serverChange: ChangeRecord): Promise<ChangeRecord> {
    // 基于时间戳的策略：较新的变更优先
    if (serverChange.timestamp > localChange.timestamp) {
      return {
        ...serverChange,
        reason: `自动解决冲突：服务器版本更新 (${new Date(serverChange.timestamp).toLocaleString()})`
      }
    }

    // 基于变更类型的策略
    if (serverChange.type === 'delete' && localChange.type === 'update') {
      return {
        ...serverChange,
        reason: '自动解决冲突：删除操作优先于更新操作'
      }
    }

    // 默认使用服务器版本
    return {
      ...serverChange,
      reason: '自动解决冲突：使用服务器版本'
    }
  }

  // 生成变更摘要
  generateChangeSummary(changes: ChangeRecord[]): string {
    const summary = {
      created: changes.filter(c => c.type === 'create').length,
      updated: changes.filter(c => c.type === 'update').length,
      deleted: changes.filter(c => c.type === 'delete').length
    }

    const parts = []
    if (summary.created > 0) parts.push(`新增 ${summary.created} 项`)
    if (summary.updated > 0) parts.push(`更新 ${summary.updated} 项`)
    if (summary.deleted > 0) parts.push(`删除 ${summary.deleted} 项`)

    return parts.length > 0 ? parts.join('，') : '无变更'
  }

  // 同步菜单配置
  async syncMenuConfig(): Promise<SyncResult> {
    try {
      const comparison = await this.compareVersions()
      
      if (!comparison.needsUpdate) {
        return {
          success: true,
          message: '菜单配置已是最新版本',
          updatedItems: { menus: [], tools: [] },
          conflicts: [],
          version: await this.getServerVersion()
        }
      }

      // 备份当前配置
      if (this.config.backupBeforeSync) {
        await this.createBackup()
      }

      // 获取最新配置
      const [menusResponse, toolsResponse] = await Promise.all([
        fetch(`${getApiBaseUrl()}/permissions/frontend-menu-config/`),
        fetch(`${getApiBaseUrl()}/permissions/frontend-menu-config/`)
      ])

      if (!menusResponse.ok || !toolsResponse.ok) {
        throw new Error('获取最新配置失败')
      }

      const menusData = await menusResponse.json()
      const toolsData = await toolsResponse.json()
      const serverVersion = await this.getServerVersion()

      // 智能合并变更
      const localVersion = this.getLocalVersion()
      let mergedChanges: ChangeRecord[] = []
      
      if (localVersion?.changes && serverVersion.changes) {
        mergedChanges = await this.smartMerge(localVersion.changes, serverVersion.changes)
        
        // 更新服务器版本的变更记录
        serverVersion.changes = mergedChanges
      }

      // 检测并解决冲突
      const conflicts = await this.resolveConflicts(menusData.menus, toolsData.tools)

      // 更新缓存
      cacheService.cacheMenuConfig(menusData.menus, serverVersion.version)
      cacheService.cacheToolsConfig(toolsData.tools, serverVersion.version)
      cacheService.setMenuVersion(serverVersion.version, mergedChanges)

      // 生成变更摘要
      const changeSummary = this.generateChangeSummary(mergedChanges)

      // 触发同步完成事件
      this.emit('syncCompleted', {
        version: serverVersion,
        conflicts: conflicts.length,
        changeSummary,
        mergedChanges: mergedChanges.length
      })

      return {
        success: true,
        message: `菜单配置已同步到版本 ${serverVersion.version}${changeSummary ? ` (${changeSummary})` : ''}`,
        updatedItems: {
          menus: menusData.menus,
          tools: toolsData.tools
        },
        conflicts,
        version: serverVersion
      }
    } catch (error: any) {
      console.error('同步菜单配置失败:', error)
      
      this.emit('syncFailed', { error: error.message })
      
      return {
        success: false,
        message: error.message || '同步失败',
        updatedItems: { menus: [], tools: [] },
        conflicts: [],
        version: { version: 0, timestamp: Date.now() }
      }
    }
  }

  // 解决冲突
  private async resolveConflicts(menus: MenuItem[], tools: ToolItem[]): Promise<ConflictInfo[]> {
    const conflicts: ConflictInfo[] = []
    
    if (!this.config.enableConflictResolution) {
      return conflicts
    }

    // 这里可以实现具体的冲突解决逻辑
    // 例如：比较本地和服务器的配置，找出差异并提供解决方案
    
    return conflicts
  }

  // 创建备份
  private async createBackup(): Promise<void> {
    const localMenus = cacheService.getCachedMenuConfig()
    const localTools = cacheService.getCachedToolsConfig()
    const localVersion = this.getLocalVersion()
    
    if (localMenus || localTools || localVersion) {
      const backup = {
        menus: localMenus,
        tools: localTools,
        version: localVersion,
        timestamp: Date.now()
      }
      
      const backupKey = `backup_${Date.now()}`
      cacheService.set(backupKey, backup, 7 * 24 * 60 * 60 * 1000) // 保存7天
      
      // 清理旧备份
      this.cleanupOldBackups()
    }
  }

  // 清理旧备份
  private cleanupOldBackups(): void {
    const stats = cacheService.getStats()
    const backupKeys = stats.keys.filter(key => key.includes('backup_'))
    
    if (backupKeys.length > this.config.maxVersionHistory) {
      // 按时间戳排序，删除最旧的备份
      const sortedKeys = backupKeys.sort((a, b) => {
        const timestampA = parseInt(a.split('_')[1])
        const timestampB = parseInt(b.split('_')[1])
        return timestampA - timestampB
      })
      
      const keysToDelete = sortedKeys.slice(0, backupKeys.length - this.config.maxVersionHistory)
      keysToDelete.forEach(key => cacheService.delete(key.replace('menu_cache_', '')))
    }
  }

  // 恢复备份
  async restoreBackup(backupTimestamp: number): Promise<boolean> {
    try {
      const backupKey = `backup_${backupTimestamp}`
      const backup = cacheService.get(backupKey)
      
      if (!backup) {
        throw new Error('备份不存在')
      }
      
      if (backup.menus) {
        cacheService.cacheMenuConfig(backup.menus, backup.version?.version)
      }
      
      if (backup.tools) {
        cacheService.cacheToolsConfig(backup.tools, backup.version?.version)
      }
      
      if (backup.version) {
        cacheService.setMenuVersion(backup.version.version, backup.version.changes)
      }
      
      this.emit('backupRestored', { timestamp: backupTimestamp })
      
      return true
    } catch (error) {
      console.error('恢复备份失败:', error)
      return false
    }
  }

  // 获取备份列表
  getBackupList(): Array<{ timestamp: number; version?: number; size: number }> {
    const stats = cacheService.getStats()
    const backupKeys = stats.keys.filter(key => key.includes('backup_'))
    
    return backupKeys.map(key => {
      const timestamp = parseInt(key.split('_')[1])
      const backup = cacheService.get(key.replace('menu_cache_', ''))
      
      return {
        timestamp,
        version: backup?.version?.version,
        size: JSON.stringify(backup).length
      }
    }).sort((a, b) => b.timestamp - a.timestamp)
  }

  // 强制同步
  async forceSync(): Promise<SyncResult> {
    // 清除本地缓存，强制从服务器获取最新配置
    cacheService.delete('menu_config')
    cacheService.delete('tools_config')
    
    return await this.syncMenuConfig()
  }

  // 启动自动同步
  startAutoSync(): void {
    if (this.syncTimer) {
      return
    }
    
    this.syncTimer = window.setInterval(async () => {
      try {
        const comparison = await this.compareVersions()
        if (comparison.needsUpdate) {
          console.log('检测到菜单配置更新，开始自动同步...')
          await this.syncMenuConfig()
        }
      } catch (error) {
        console.error('自动同步检查失败:', error)
      }
    }, this.config.syncInterval)
  }

  // 停止自动同步
  stopAutoSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer)
      this.syncTimer = null
    }
  }

  // 事件监听
  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event)!.push(callback)
  }

  // 移除事件监听
  off(event: string, callback?: Function): void {
    if (!this.eventListeners.has(event)) {
      return
    }
    
    if (callback) {
      const listeners = this.eventListeners.get(event)!
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    } else {
      this.eventListeners.delete(event)
    }
  }

  // 触发事件
  private emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`事件监听器执行失败 (${event}):`, error)
        }
      })
    }
  }

  // 获取同步状态
  getSyncStatus(): {
    autoSyncEnabled: boolean
    lastSyncTime: number | null
    nextSyncTime: number | null
  } {
    const lastSyncTime = this.getLocalVersion()?.timestamp || null
    const nextSyncTime = this.syncTimer && lastSyncTime 
      ? lastSyncTime + this.config.syncInterval 
      : null
    
    return {
      autoSyncEnabled: !!this.syncTimer,
      lastSyncTime,
      nextSyncTime
    }
  }

  // 销毁服务
  destroy(): void {
    this.stopAutoSync()
    this.eventListeners.clear()
  }
}

// 创建全局版本服务实例
export const versionService = new VersionService()

export default versionService
export type { VersionConfig }