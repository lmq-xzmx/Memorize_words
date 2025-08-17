/**
 * 优化后的权限检查混入
 * 为Vue组件提供高性能的权限检查功能
 * 集成缓存机制和批量权限检查
 */

import { defineComponent } from 'vue'
import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  canAccessPage,
  getAccessiblePages,
  isAuthenticated,
  getCurrentUser,
  getRoleDisplayName,
  getPermissionDisplayName,
  getCategoryDisplayName,
  getAccessibleMenus,
  getRolePermissions,
  permissionSyncManager
} from '../utils/permission'
import {
  LEARNING_PERMISSIONS,
  CONTENT_PERMISSIONS,
  SOCIAL_PERMISSIONS,
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS,
  ADVANCED_PERMISSIONS
} from '../utils/permissionConstants'
import {
  getManageableRoles,
  roleHasPermission,
  isRoleHigher
} from '../utils/roleDefinitions'
import {
  getAccessibleLearningModes,
  pageRequiresAuth
} from '../utils/learningModePermissions'
import {
  createPermissionChecker,
  clearAllPermissionCache
} from '../utils/permissionUtils'



// 性能监控接口
interface PerformanceStats {
  totalChecks: number
  cacheHits: number
  averageTime: number
  slowChecks: number
}

// 权限检查结果接口
interface PermissionCheckResult {
  hasPermission: boolean
  fromCache: boolean
  duration: number
}

// 批量权限检查接口
interface BatchPermissionCheck {
  permission: string
  context?: Record<string, any>
}

// 用户信息接口
interface UserInfo {
  id: string
  username: string
  roles: string[]
  permissions: string[]
}

// 性能监控类
class PermissionPerformanceMonitor {
  private stats: PerformanceStats
  
  constructor() {
    this.stats = {
      totalChecks: 0,
      cacheHits: 0,
      averageTime: 0,
      slowChecks: 0
    }
  }

  recordCheck(duration: number, fromCache: boolean = false): void {
    this.stats.totalChecks++
    if (fromCache) {
      this.stats.cacheHits++
    }
    
    // 更新平均时间
    this.stats.averageTime = (
      (this.stats.averageTime * (this.stats.totalChecks - 1) + duration) / 
      this.stats.totalChecks
    )
    
    // 记录慢查询（超过10ms）
    if (duration > 10) {
      this.stats.slowChecks++
    }
  }

  getReport(): PerformanceStats {
    return {
      ...this.stats,
      cacheHitRate: this.stats.totalChecks > 0 ? 
        (this.stats.cacheHits / this.stats.totalChecks * 100) : 0
    } as PerformanceStats & { cacheHitRate: number }
  }

  reset(): void {
    this.stats = {
      totalChecks: 0,
      cacheHits: 0,
      averageTime: 0,
      slowChecks: 0
    }
  }
}

const performanceMonitor = new PermissionPerformanceMonitor()

export default defineComponent({
  name: 'OptimizedPermissionMixin',
  
  data() {
    return {
      permissionCache: new Map<string, any>(),
      permissionListeners: [] as Array<(user: UserInfo) => void>,
      lastSyncTime: 0,
      syncInProgress: false,
      batchCheckQueue: [] as BatchPermissionCheck[],
      performanceMode: true,
      cacheEnabled: true,
      debugMode: false,
      permissionWatcherActive: false,
      optimizedChecker: null as any,
      userInfo: null as UserInfo | null,
      permissionSyncStatus: {
        lastSync: null as Date | null,
        isOnline: true,
        pendingChanges: 0
      }
    }
  },
  
  computed: {
    // 角色显示名称
    roleDisplayName(): string {
      return getRoleDisplayName(this.userInfo?.roles?.[0] || '')
    },
    
    // 可访问的菜单
    accessibleMenus(): any[] {
      return getAccessibleMenus(this.userInfo?.permissions || [])
    },
    
    // 可访问的页面
    accessiblePages(): Array<{path: string, permission: string}> {
      return getAccessiblePages(this.userInfo?.permissions || [])
    },
    
    // 可访问的学习模式
    accessibleLearningModes(): string[] {
      return []
    },
    
    // 是否为管理员
    isAdmin(): boolean {
      return this.userInfo?.roles?.includes('admin') || false
    },

    isDean(): boolean {
      return this.userInfo?.roles?.includes('dean') || false
    },

    isAcademicDirector(): boolean {
      return this.userInfo?.roles?.includes('academic_director') || false
    },

    isResearchLeader(): boolean {
      return this.userInfo?.roles?.includes('research_leader') || false
    },

    isTeacher(): boolean {
      return this.userInfo?.roles?.includes('teacher') || false
    },

    isParent(): boolean {
      return this.userInfo?.roles?.includes('parent') || false
    },

    isStudent(): boolean {
      return this.userInfo?.roles?.includes('student') || false
    },
    
    // 权限类别检查
    hasLearningPermissions(): boolean {
      return hasAnyPermission(LEARNING_PERMISSIONS, this.userInfo?.permissions || [])
    },

    hasContentPermissions(): boolean {
      return hasAnyPermission(CONTENT_PERMISSIONS, this.userInfo?.permissions || [])
    },

    hasSocialPermissions(): boolean {
      return hasAnyPermission(SOCIAL_PERMISSIONS, this.userInfo?.permissions || [])
    },

    hasManagementPermissions(): boolean {
      return hasAnyPermission(MANAGEMENT_PERMISSIONS, this.userInfo?.permissions || [])
    },

    hasSystemPermissions(): boolean {
      return hasAnyPermission(SYSTEM_PERMISSIONS, this.userInfo?.permissions || [])
    },

    hasAdvancedPermissions(): boolean {
      return hasAnyPermission(ADVANCED_PERMISSIONS, this.userInfo?.permissions || [])
    },
    
    // 可管理的角色
    manageableRoles(): string[] {
      return getManageableRoles(this.userInfo?.roles?.[0] || '')
    },
    
    // 用户默认页面
    userDefaultPage(): string {
      const role = this.userInfo?.roles?.[0] || ''
      const defaultPages: Record<string, string> = {
        'admin': '/admin',
        'teacher': '/dashboard',
        'student': '/word-learning',
        'parent': '/dashboard'
      }
      return defaultPages[role] || '/'
    },
    
    // 性能报告
    performanceReport(): any {
      return performanceMonitor.getReport()
    }
  },
  
  methods: {
    /**
     * 检查权限（优化版本）
     * @param permission - 权限名称
     * @param context - 上下文信息
     */
    $hasPermission(permission: string, context: Record<string, any> = {}): boolean {
      const startTime = performance.now()
      
      try {
        // 检查缓存
        const cacheKey = `${permission}_${JSON.stringify(context)}`
        if (this.cacheEnabled && this.permissionCache.has(cacheKey)) {
          const result = this.permissionCache.get(cacheKey)
          const duration = performance.now() - startTime
          performanceMonitor.recordCheck(duration, true)
          return result
        }
        
        // 执行权限检查
        const result = hasPermission(permission, this.userInfo?.permissions || [])
        
        // 缓存结果
        if (this.cacheEnabled) {
          this.permissionCache.set(cacheKey, result)
        }
        
        const duration = performance.now() - startTime
        performanceMonitor.recordCheck(duration, false)
        
        return result
      } catch (error) {
        console.error('权限检查失败:', error)
        return false
      }
    },
    
    /**
     * 批量权限检查
     * @param permissions - 权限列表
     * @param mode - 检查模式：'any' 或 'all'
     */
    $hasBatchPermissions(permissions: string[], mode: 'any' | 'all' = 'any'): boolean {
      const startTime = performance.now()
      
      try {
        const results = permissions.map(permission => 
          this.$hasPermission(permission)
        )
        
        const result = mode === 'any' ? 
          results.some(r => r) : 
          results.every(r => r)
        
        const duration = performance.now() - startTime
        performanceMonitor.recordCheck(duration, false)
        
        return result
      } catch (error) {
        console.error('批量权限检查失败:', error)
        return false
      }
    },
    
    /**
     * 检查是否有任一权限
     * @param permissions - 权限列表
     */
    $hasAnyPermission(permissions: string[]): boolean {
      return this.$hasBatchPermissions(permissions, 'any')
    },
    
    /**
     * 检查是否有所有权限
     * @param permissions - 权限列表
     */
    $hasAllPermissions(permissions: string[]): boolean {
      return this.$hasBatchPermissions(permissions, 'all')
    },
    
    /**
     * 优化的权限检查
     * @param resource - 资源
     * @param action - 操作
     * @param context - 上下文
     */
    $hasOptimizedPermission(resource: string, action: string, context: Record<string, any> = {}): boolean {
      const permission = `${resource}:${action}`
      return hasPermission(permission, this.userInfo?.permissions || [])
    },
    
    /**
     * 检查菜单访问权限
     * @param menuId - 菜单ID
     */
    $canAccessMenu(menuId: string): boolean {
      return this.$hasPermission(`menu.${menuId}.view`)
    },
    
    /**
     * 检查学习目标管理权限
     * @param action - 操作类型
     * @param context - 上下文
     */
    $canManageLearningGoal(action: string, context: Record<string, any> = {}): boolean {
      return this.$hasOptimizedPermission('learning_goal', action, context)
    },
    
    /**
     * 检查学习计划管理权限
     * @param action - 操作类型
     * @param context - 上下文
     */
    $canManageLearningPlan(action: string, context: Record<string, any> = {}): boolean {
      return this.$hasOptimizedPermission('learning_plan', action, context)
    },
    
    /**
     * 检查页面访问权限
     * @param path - 页面路径
     */
    $canAccessPage(path: string): boolean {
      return canAccessPage(path, this.userInfo?.permissions || [])
    },
    
    /**
     * 检查角色权限
     * @param role - 角色
     * @param permission - 权限
     */
    $roleHasPermission(role: string, permission: string): boolean {
      return roleHasPermission(role, permission)
    },
    
    /**
     * 检查角色等级
     * @param targetRole - 目标角色
     */
    $isRoleHigher(targetRole: string): boolean {
      return isRoleHigher(this.userInfo?.roles?.[0] || '', targetRole)
    },
    
    /**
     * 检查是否已认证
     */
    async $isAuthenticated(): Promise<boolean> {
      return await isAuthenticated()
    },
    
    /**
     * 带权限执行操作
     * @param permission - 权限
     * @param callback - 回调函数
     * @param errorMessage - 错误消息
     * @param mode - 检查模式
     */
    $withPermission(
      permission: string | string[], 
      callback: () => void, 
      errorMessage: string = '权限不足', 
      mode: 'any' | 'all' = 'any'
    ): void {
      const hasAccess = Array.isArray(permission) ? 
        this.$hasBatchPermissions(permission, mode) : 
        this.$hasPermission(permission)
      
      if (hasAccess) {
        callback()
      } else {
        this.$showError(errorMessage)
      }
    },
    
    /**
     * 显示错误消息
     * @param message - 错误消息
     */
    $showError(message: string): void {
      // 这里可以集成具体的消息提示组件
      console.error(message)
    },
    
    /**
     * 显示成功消息
     * @param message - 成功消息
     */
    $showSuccess(message: string): void {
      console.log(message)
    },
    
    /**
     * 更新用户信息
     */
    async $updateUserInfo(): Promise<void> {
      try {
        const user = await getCurrentUser()
        if (user) {
          this.userInfo = {
            id: user.id || user.user_id || '',
            username: user.username,
            roles: user.role ? [user.role] : [],
            permissions: []
          }
          
          // 清除权限缓存
          this.permissionCache.clear()
          
          // 通知权限变更
          this.permissionListeners.forEach(listener => {
            if (this.userInfo) {
              listener(this.userInfo)
            }
          })
          
          console.log('用户信息已更新')
        }
      } catch (error) {
        console.error('更新用户信息失败:', error)
      }
    },
    
    /**
     * 清除权限缓存
     */
    $clearPermissionCache(): void {
      this.permissionCache.clear()
      clearAllPermissionCache()
      
      // 重置性能监控
      performanceMonitor.reset()
      
      console.log('权限缓存已清除')
    },
    
    /**
     * 同步权限
     * @param force - 是否强制同步
     */
    async $syncPermissions(force: boolean = false): Promise<void> {
      if (this.syncInProgress && !force) {
        return
      }
      
      try {
        this.syncInProgress = true
        
        if (permissionSyncManager && permissionSyncManager.sync) {
          await permissionSyncManager.sync(force)
        }
        
        await this.$updateUserInfo()
        
        this.permissionSyncStatus.lastSync = new Date()
        this.permissionSyncStatus.pendingChanges = 0
        
        console.log('权限同步完成')
      } catch (error) {
        console.error('权限同步失败:', error)
      } finally {
        this.syncInProgress = false
      }
    },
    
    /**
     * 获取权限显示名称
     * @param permission - 权限
     */
    $getPermissionDisplayName(permission: string): string {
      return getPermissionDisplayName(permission)
    },
    
    /**
     * 获取分类显示名称
     * @param category - 分类
     */
    $getCategoryDisplayName(category: string): string {
      return getCategoryDisplayName(category)
    },
    
    /**
     * 权限变更回调
     * @param user - 用户信息
     */
    $onPermissionChange(user: UserInfo): void {
      this.userInfo = user
    },
    
    /**
     * 添加权限监听器
     * @param callback - 回调函数
     */
    $addPermissionListener(callback: (user: UserInfo) => void): void {
      this.permissionListeners.push(callback)
    },
    
    /**
     * 移除权限监听器
     * @param callback - 回调函数
     */
    $removePermissionListener(callback: (user: UserInfo) => void): void {
      const index = this.permissionListeners.indexOf(callback)
      if (index > -1) {
        this.permissionListeners.splice(index, 1)
      }
    },
    
    /**
     * 带权限导航
     * @param path - 路径
     * @param params - 参数
     */
    $navigateWithPermission(path: string, params: Record<string, any> = {}): void {
      if (this.$canAccessPage(path)) {
        // 使用Vue Router进行导航
        const router = (this as any).$router
        if (router) {
          router.push({ path, ...params })
        }
      } else {
        this.$showError('您没有访问该页面的权限')
      }
    },
    
    /**
     * 检查页面是否需要认证
     * @param path - 页面路径
     */
    $pageRequiresAuth(path: string): boolean {
      return pageRequiresAuth(path)
    },
    
    /**
     * 获取角色权限
     * @param role - 角色
     */
    $getRolePermissions(role: string): string[] {
      return getRolePermissions(role) || []
    },
    
    /**
     * 带权限执行操作
     * @param permission - 权限
     * @param action - 操作
     * @param feature - 功能名称
     * @param mode - 检查模式
     */
    $executeWithPermission(
      permission: string | string[], 
      action: () => void, 
      feature: string = '此功能', 
      mode: 'any' | 'all' = 'any'
    ): void {
      this.$withPermission(permission, action, `您没有使用${feature}的权限`, mode)
    },
    
    /**
     * 获取性能报告
     */
    $getPerformanceReport(): PerformanceStats & { cacheHitRate: number } {
      return this.performanceReport
    },
    
    /**
     * 获取缓存统计
     */
    $getCacheStats(): any {
      return {
        localCacheSize: this.permissionCache.size,
        globalCacheStats: {},
        performanceStats: this.performanceReport
      }
    }
  },
  
  async created() {
    try {
      // 初始化用户信息
      await this.$updateUserInfo()
      
      // 添加权限变更监听
      this.$addPermissionListener(this.$onPermissionChange)
      
    } catch (error) {
      console.error('权限混入初始化失败:', error)
    }
  },
  
  beforeUnmount() {
    // 移除权限变更监听
    this.$removePermissionListener(this.$onPermissionChange)
  }
})

// 权限指令
export const permissionDirective = {
  mounted(el: HTMLElement, binding: any) {
    const { value, modifiers } = binding
    const hasAccess = hasPermission(value, [])
    
    if (!hasAccess) {
      el.style.display = 'none'
    }
  },
  
  updated(el: HTMLElement, binding: any) {
    const { value } = binding
    const hasAccess = hasPermission(value, [])
    
    el.style.display = hasAccess ? '' : 'none'
  }
}

// 角色指令
export const roleDirective = {
  mounted(el: HTMLElement, binding: any) {
    const { value } = binding
    const user = getCurrentUser()
    const hasRole = user?.role === value
    
    if (!hasRole) {
      el.style.display = 'none'
    }
  },
  
  updated(el: HTMLElement, binding: any) {
    const { value } = binding
    const user = getCurrentUser()
    const hasRole = user?.role === value
    
    el.style.display = hasRole ? '' : 'none'
  }
}

// 导出类型
export type {
  PerformanceStats,
  PermissionCheckResult,
  BatchPermissionCheck,
  UserInfo
}