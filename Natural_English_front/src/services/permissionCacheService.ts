/**
 * 权限缓存服务
 * 集成LRU缓存管理器到权限系统中
 */

import { permissionCacheManager, PermissionCacheUtils } from '@/utils/permissionCacheManager'
import permissionService from './permissionService'
import roleService from './roleService'
import { ElMessage } from 'element-plus'

// 权限数据接口
interface UserPermissions {
  permissions: string[]
  roles: string[]
  menus: any[]
  lastUpdate: number
}

interface RolePermissions {
  permissions: string[]
  menus: string[]
  actions: string[]
  lastUpdate: number
}

/**
 * 权限缓存服务类
 */
export class PermissionCacheService {
  private static instance: PermissionCacheService
  private isInitialized = false

  private constructor() {}

  static getInstance(): PermissionCacheService {
    if (!PermissionCacheService.instance) {
      PermissionCacheService.instance = new PermissionCacheService()
    }
    return PermissionCacheService.instance
  }

  /**
   * 初始化缓存服务
   */
  async initialize(userId?: string, role?: string): Promise<void> {
    if (this.isInitialized) return

    try {
      // 预热缓存
      if (userId && role) {
        await permissionCacheManager.warmup(userId, role)
      }

      this.isInitialized = true
      console.log('[PermissionCache] 权限缓存服务初始化完成')
    } catch (error) {
      console.error('[PermissionCache] 初始化失败:', error)
    }
  }

  /**
   * 获取用户权限（带缓存）
   */
  async getUserPermissions(userId: string, forceRefresh = false): Promise<UserPermissions | null> {
    const cacheKey = PermissionCacheUtils.getUserPermissionKey(userId)
    
    // 如果不强制刷新，先尝试从缓存获取
    if (!forceRefresh) {
      const cached = permissionCacheManager.get<UserPermissions>(cacheKey)
      if (cached) {
        console.log(`[PermissionCache] 从缓存获取用户权限: ${userId}`)
        return cached
      }
    }

    try {
      // 从API获取最新数据
      console.log(`[PermissionCache] 从API获取用户权限: ${userId}`)
      const response = await permissionService.getUserPermissions(parseInt(userId))
      
      const permissions: UserPermissions = {
        permissions: response.permissions || [],
        roles: response.role ? [response.role] : [],
        menus: [], // 菜单数据需要单独获取
        lastUpdate: Date.now()
      }

      // 缓存数据（高优先级，因为是用户特定数据）
      permissionCacheManager.set(cacheKey, permissions, undefined, 3)
      
      return permissions
    } catch (error) {
      console.error(`[PermissionCache] 获取用户权限失败: ${userId}`, error)
      
      // 如果API失败，尝试返回缓存的数据
      const cached = permissionCacheManager.get<UserPermissions>(cacheKey)
      if (cached) {
        ElMessage.warning('网络异常，使用缓存数据')
        return cached
      }
      
      return null
    }
  }

  /**
   * 获取角色权限（带缓存）
   */
  async getRolePermissions(roleId: string, forceRefresh = false): Promise<RolePermissions | null> {
    const cacheKey = PermissionCacheUtils.getRolePermissionKey(roleId)
    
    if (!forceRefresh) {
      const cached = permissionCacheManager.get<RolePermissions>(cacheKey)
      if (cached) {
        console.log(`[PermissionCache] 从缓存获取角色权限: ${roleId}`)
        return cached
      }
    }

    try {
      console.log(`[PermissionCache] 从API获取角色权限: ${roleId}`)
      const response = await roleService.getRolePermissions(parseInt(roleId))
      
      const permissions: RolePermissions = {
        permissions: response || [],
        menus: [], // 菜单数据需要单独获取
        actions: [], // 操作权限需要单独获取
        lastUpdate: Date.now()
      }

      // 缓存数据（中等优先级）
      permissionCacheManager.set(cacheKey, permissions, undefined, 2)
      
      return permissions
    } catch (error) {
      console.error(`[PermissionCache] 获取角色权限失败: ${roleId}`, error)
      
      const cached = permissionCacheManager.get<RolePermissions>(cacheKey)
      if (cached) {
        ElMessage.warning('网络异常，使用缓存数据')
        return cached
      }
      
      return null
    }
  }

  /**
   * 获取用户菜单权限（带缓存）
   */
  async getUserMenus(userId: string, forceRefresh = false): Promise<any[] | null> {
    const cacheKey = PermissionCacheUtils.getMenuPermissionKey(userId)
    
    if (!forceRefresh) {
      const cached = permissionCacheManager.get<any[]>(cacheKey)
      if (cached) {
        console.log(`[PermissionCache] 从缓存获取用户菜单: ${userId}`)
        return cached
      }
    }

    try {
      console.log(`[PermissionCache] 从API获取用户菜单: ${userId}`)
      const userPermissions = await permissionService.getUserPermissions(parseInt(userId))
      const menuData = userPermissions.role ? await permissionService.getRoleMenus(userPermissions.role) : []
      
      // 缓存菜单数据（高优先级）
      permissionCacheManager.set(cacheKey, menuData, undefined, 3)
      
      return menuData
    } catch (error) {
      console.error(`[PermissionCache] 获取用户菜单失败: ${userId}`, error)
      
      const cached = permissionCacheManager.get<any[]>(cacheKey)
      if (cached) {
        ElMessage.warning('网络异常，使用缓存菜单')
        return cached
      }
      
      return null
    }
  }

  /**
   * 检查路由权限（带缓存）
   */
  async checkRoutePermission(route: string, userId: string, forceRefresh = false): Promise<boolean> {
    const cacheKey = PermissionCacheUtils.getRoutePermissionKey(route, userId)
    
    if (!forceRefresh) {
      const cached = permissionCacheManager.get<boolean>(cacheKey)
      if (cached !== null) {
        return cached
      }
    }

    try {
      // 获取用户权限
      const userPermissions = await this.getUserPermissions(userId)
      if (!userPermissions) {
        return false
      }

      // 检查路由权限逻辑（这里需要根据实际业务逻辑实现）
      const hasPermission = this.checkPermissionLogic(route, userPermissions.permissions)
      
      // 缓存结果（短期缓存，因为路由权限检查频繁）
      permissionCacheManager.set(cacheKey, hasPermission, 2 * 60 * 1000, 2) // 2分钟缓存
      
      return hasPermission
    } catch (error) {
      console.error(`[PermissionCache] 检查路由权限失败: ${route}`, error)
      return false
    }
  }

  /**
   * 检查组件权限（带缓存）
   */
  async checkComponentPermission(component: string, userId: string, forceRefresh = false): Promise<boolean> {
    const cacheKey = PermissionCacheUtils.getComponentPermissionKey(component, userId)
    
    if (!forceRefresh) {
      const cached = permissionCacheManager.get<boolean>(cacheKey)
      if (cached !== null) {
        return cached
      }
    }

    try {
      const userPermissions = await this.getUserPermissions(userId)
      if (!userPermissions) {
        return false
      }

      const hasPermission = this.checkPermissionLogic(component, userPermissions.permissions)
      
      // 缓存结果
      permissionCacheManager.set(cacheKey, hasPermission, 5 * 60 * 1000, 1) // 5分钟缓存
      
      return hasPermission
    } catch (error) {
      console.error(`[PermissionCache] 检查组件权限失败: ${component}`, error)
      return false
    }
  }

  /**
   * 批量预加载权限数据
   */
  async preloadPermissions(userId: string, routes: string[] = [], components: string[] = []): Promise<void> {
    try {
      // 预加载用户基础权限
      await this.getUserPermissions(userId)
      await this.getUserMenus(userId)

      // 预加载路由权限
      const routePromises = routes.map(route => 
        this.checkRoutePermission(route, userId)
      )

      // 预加载组件权限
      const componentPromises = components.map(component => 
        this.checkComponentPermission(component, userId)
      )

      await Promise.allSettled([...routePromises, ...componentPromises])
      
      console.log(`[PermissionCache] 预加载完成: ${routes.length} 个路由, ${components.length} 个组件`)
    } catch (error) {
      console.error('[PermissionCache] 预加载权限失败:', error)
    }
  }

  /**
   * 刷新用户相关的所有缓存
   */
  async refreshUserCache(userId: string): Promise<void> {
    try {
      // 清除用户相关缓存
      const clearedCount = PermissionCacheUtils.clearUserCache(userId, permissionCacheManager)
      console.log(`[PermissionCache] 清除用户缓存: ${clearedCount} 项`)

      // 重新加载用户权限数据
      await this.getUserPermissions(userId, true)
      await this.getUserMenus(userId, true)
      
      ElMessage.success('权限缓存已刷新')
    } catch (error) {
      console.error('[PermissionCache] 刷新用户缓存失败:', error)
      ElMessage.error('刷新权限缓存失败')
    }
  }

  /**
   * 刷新角色相关的所有缓存
   */
  async refreshRoleCache(roleId: string): Promise<void> {
    try {
      const clearedCount = PermissionCacheUtils.clearRoleCache(roleId, permissionCacheManager)
      console.log(`[PermissionCache] 清除角色缓存: ${clearedCount} 项`)

      await this.getRolePermissions(roleId, true)
      
      ElMessage.success('角色权限缓存已刷新')
    } catch (error) {
      console.error('[PermissionCache] 刷新角色缓存失败:', error)
      ElMessage.error('刷新角色权限缓存失败')
    }
  }

  /**
   * 清除所有缓存
   */
  clearAllCache(): void {
    permissionCacheManager.clear()
    ElMessage.success('所有权限缓存已清除')
    console.log('[PermissionCache] 所有缓存已清除')
  }

  /**
   * 获取缓存统计信息
   */
  getCacheStats(): any {
    return {
      metrics: permissionCacheManager.getMetrics(),
      size: permissionCacheManager.size(),
      hotKeys: permissionCacheManager.getHotKeys(10)
    }
  }

  /**
   * 显示缓存统计（开发环境）
   */
  showCacheStats(): void {
    if (process.env.NODE_ENV === 'development') {
      PermissionCacheUtils.showCacheStats(permissionCacheManager)
    }
  }

  // 私有方法

  /**
   * 权限检查逻辑
   */
  private checkPermissionLogic(resource: string, permissions: string[]): boolean {
    // 这里实现具体的权限检查逻辑
    // 可以根据资源名称和权限列表进行匹配
    
    // 简单的包含检查
    if (permissions.includes(resource)) {
      return true
    }

    // 通配符检查
    for (const permission of permissions) {
      if (permission.includes('*')) {
        const pattern = permission.replace('*', '.*')
        const regex = new RegExp(`^${pattern}$`)
        if (regex.test(resource)) {
          return true
        }
      }
    }

    // 层级权限检查（例如：admin.* 包含 admin.users）
    for (const permission of permissions) {
      if (permission.endsWith('.*')) {
        const prefix = permission.slice(0, -2)
        if (resource.startsWith(prefix + '.')) {
          return true
        }
      }
    }

    return false
  }
}

// 创建单例实例
export const permissionCacheService = PermissionCacheService.getInstance()

// 导出便捷方法
export const PermissionCache = {
  /**
   * 初始化权限缓存
   */
  init: (userId?: string, role?: string) => permissionCacheService.initialize(userId, role),
  
  /**
   * 获取用户权限
   */
  getUserPermissions: (userId: string, forceRefresh = false) => 
    permissionCacheService.getUserPermissions(userId, forceRefresh),
  
  /**
   * 获取用户菜单
   */
  getUserMenus: (userId: string, forceRefresh = false) => 
    permissionCacheService.getUserMenus(userId, forceRefresh),
  
  /**
   * 检查路由权限
   */
  checkRoute: (route: string, userId: string, forceRefresh = false) => 
    permissionCacheService.checkRoutePermission(route, userId, forceRefresh),
  
  /**
   * 检查组件权限
   */
  checkComponent: (component: string, userId: string, forceRefresh = false) => 
    permissionCacheService.checkComponentPermission(component, userId, forceRefresh),
  
  /**
   * 预加载权限
   */
  preload: (userId: string, routes?: string[], components?: string[]) => 
    permissionCacheService.preloadPermissions(userId, routes, components),
  
  /**
   * 刷新用户缓存
   */
  refreshUser: (userId: string) => permissionCacheService.refreshUserCache(userId),
  
  /**
   * 清除所有缓存
   */
  clear: () => permissionCacheService.clearAllCache(),
  
  /**
   * 获取统计信息
   */
  getStats: () => permissionCacheService.getCacheStats(),
  
  /**
   * 显示统计信息
   */
  showStats: () => permissionCacheService.showCacheStats()
}

// 在开发环境下暴露到全局对象
if (process.env.NODE_ENV === 'development') {
  // 临时注释掉，避免与其他代码冲突
  // (window as any).PermissionCache = PermissionCache
  (window as any).permissionCacheService = permissionCacheService
}