/**
 * 优化后的权限检查混入
 * 为Vue组件提供高性能的权限检查功能
 * 集成缓存机制和批量权限检查
 */

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
  getDefaultPageForRole,
  clearAuth,
  clearCache,
  getCachedPermissions,
  setCachedPermissions,
  fetchUserPermissions,
  syncPermissions,
  permissionSyncManager,
  permissionWatcher
} from '../utils/permission.js'

import {
  createPermissionChecker,
  hasPermission as optimizedHasPermission,
  clearAllPermissionCache,
  getCacheStats
} from '../utils/permissionUtils.js'

import permissionCacheManager from '../utils/permissionCache.js'

import {
  ROLES,
  ROLE_DISPLAY_NAMES,
  getRolePermissions,
  roleHasPermission,
  isRoleHigher,
  getManageableRoles
} from '../utils/roleDefinitions.js'

import {
  ALL_PERMISSIONS,
  PERMISSION_CATEGORIES,
  PERMISSION_DISPLAY_NAMES,
  LEARNING_PERMISSIONS,
  CONTENT_PERMISSIONS,
  SOCIAL_PERMISSIONS,
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS,
  ADVANCED_PERMISSIONS
} from '../utils/permissionConstants.js'

import {
  PAGE_PERMISSIONS,
  getAccessibleLearningModes,
  pageRequiresAuth
} from '../utils/learningModePermissions.js'

// 权限检查性能监控
class PermissionPerformanceMonitor {
  constructor() {
    this.metrics = {
      totalChecks: 0,
      cacheHits: 0,
      cacheMisses: 0,
      averageCheckTime: 0,
      slowQueries: []
    }
  }

  recordCheck(duration, fromCache = false) {
    this.metrics.totalChecks++
    if (fromCache) {
      this.metrics.cacheHits++
    } else {
      this.metrics.cacheMisses++
    }
    
    // 更新平均检查时间
    this.metrics.averageCheckTime = 
      (this.metrics.averageCheckTime * (this.metrics.totalChecks - 1) + duration) / this.metrics.totalChecks
    
    // 记录慢查询（超过10ms）
    if (duration > 10 && !fromCache) {
      this.metrics.slowQueries.push({
        duration,
        timestamp: Date.now()
      })
      
      // 只保留最近100个慢查询
      if (this.metrics.slowQueries.length > 100) {
        this.metrics.slowQueries.shift()
      }
    }
  }

  getReport() {
    const cacheHitRate = this.metrics.totalChecks > 0 
      ? this.metrics.cacheHits / this.metrics.totalChecks 
      : 0
    
    return {
      ...this.metrics,
      cacheHitRate: Math.round(cacheHitRate * 100) / 100
    }
  }

  reset() {
    this.metrics = {
      totalChecks: 0,
      cacheHits: 0,
      cacheMisses: 0,
      averageCheckTime: 0,
      slowQueries: []
    }
  }
}

const performanceMonitor = new PermissionPerformanceMonitor()

export default {
  data() {
    return {
      // 当前用户信息
      currentUser: null,
      // 用户角色
      userRole: null,
      // 用户权限列表
      userPermissions: [],
      // 用户认证状态
      isUserAuthenticated: false,
      // 权限检查器实例
      permissionChecker: null,
      // 权限变更监听器
      permissionListener: null,
      // 权限缓存状态
      permissionCacheStatus: {
        loaded: false,
        lastUpdate: null,
        syncing: false
      },
      // 批量权限检查缓存
      batchPermissionCache: new Map(),
      // 性能监控开关
      enablePerformanceMonitoring: process.env.NODE_ENV === 'development'
    }
  },
  
  computed: {
    // 角色显示名称
    roleDisplayName() {
      return this.userRole ? getRoleDisplayName(this.userRole) : '未知角色'
    },
    
    // 可访问的菜单项
    accessibleMenus() {
      return this.permissionChecker ? this.permissionChecker.getAccessibleMenus() : []
    },
    
    // 可访问的页面列表
    accessiblePages() {
      return getAccessiblePages(this.userPermissions)
    },
    
    // 可访问的学习模式
    accessibleLearningModes() {
      return getAccessibleLearningModes(this.userPermissions)
    },
    
    // 角色检查计算属性
    isAdmin() {
      return this.userRole === ROLES.ADMIN
    },
    
    isDean() {
      return this.userRole === ROLES.DEAN
    },
    
    isAcademicDirector() {
      return this.userRole === ROLES.ACADEMIC_DIRECTOR
    },
    
    isResearchLeader() {
      return this.userRole === ROLES.RESEARCH_LEADER
    },
    
    isTeacher() {
      return this.userRole === ROLES.TEACHER
    },
    
    isParent() {
      return this.userRole === ROLES.PARENT
    },
    
    isStudent() {
      return this.userRole === ROLES.STUDENT
    },
    
    // 权限分类检查
    hasLearningPermissions() {
      return hasAnyPermission(this.userPermissions, LEARNING_PERMISSIONS)
    },
    
    hasContentPermissions() {
      return hasAnyPermission(this.userPermissions, CONTENT_PERMISSIONS)
    },
    
    hasSocialPermissions() {
      return hasAnyPermission(this.userPermissions, SOCIAL_PERMISSIONS)
    },
    
    hasManagementPermissions() {
      return hasAnyPermission(this.userPermissions, MANAGEMENT_PERMISSIONS)
    },
    
    hasSystemPermissions() {
      return hasAnyPermission(this.userPermissions, SYSTEM_PERMISSIONS)
    },
    
    hasAdvancedPermissions() {
      return hasAnyPermission(this.userPermissions, ADVANCED_PERMISSIONS)
    },
    
    // 可管理的角色列表
    manageableRoles() {
      return getManageableRoles(this.userRole)
    },
    
    // 用户默认页面
    userDefaultPage() {
      return getDefaultPageForRole(this.userRole)
    },
    
    // 性能监控报告
    performanceReport() {
      return this.enablePerformanceMonitoring ? performanceMonitor.getReport() : null
    }
  },
  
  methods: {
    /**
     * 优化后的权限检查方法（带性能监控）
     * @param {string} permission - 权限名称
     * @returns {boolean}
     */
    $hasPermission(permission) {
      const startTime = performance.now()
      
      try {
        if (!permission) {
          return true
        }
        
        if (!this.isUserAuthenticated || !this.userRole) {
          return false
        }
        
        const result = hasPermission(this.userRole, permission)
        
        if (this.enablePerformanceMonitoring) {
          const duration = performance.now() - startTime
          performanceMonitor.recordCheck(duration, false)
        }
        
        return result
      } catch (error) {
        console.error('权限检查失败:', error)
        return false
      }
    },
    
    /**
     * 批量权限检查（优化性能）
     * @param {Array} permissions - 权限数组
     * @param {string} mode - 检查模式: 'any' 或 'all'
     * @returns {boolean}
     */
    $hasBatchPermissions(permissions, mode = 'any') {
      if (!permissions || !Array.isArray(permissions)) {
        return true
      }
      
      const cacheKey = `${permissions.join(',')}_${mode}`
      
      // 检查批量缓存
      if (this.batchPermissionCache.has(cacheKey)) {
        const cached = this.batchPermissionCache.get(cacheKey)
        if (Date.now() - cached.timestamp < 60000) { // 1分钟缓存
          return cached.result
        }
        this.batchPermissionCache.delete(cacheKey)
      }
      
      const startTime = performance.now()
      let result
      
      if (mode === 'all') {
        result = permissions.every(permission => this.$hasPermission(permission))
      } else {
        result = permissions.some(permission => this.$hasPermission(permission))
      }
      
      // 缓存结果
      this.batchPermissionCache.set(cacheKey, {
        result,
        timestamp: Date.now()
      })
      
      if (this.enablePerformanceMonitoring) {
        const duration = performance.now() - startTime
        performanceMonitor.recordCheck(duration, false)
      }
      
      return result
    },
    
    /**
     * 检查用户是否拥有任一权限
     * @param {Array} permissions - 权限数组
     * @returns {boolean}
     */
    $hasAnyPermission(permissions) {
      return this.$hasBatchPermissions(permissions, 'any')
    },
    
    /**
     * 检查用户是否拥有所有权限
     * @param {Array} permissions - 权限数组
     * @returns {boolean}
     */
    $hasAllPermissions(permissions) {
      return this.$hasBatchPermissions(permissions, 'all')
    },
    
    /**
     * 优化后的权限检查方法（使用权限检查器）
     * @param {string} resource 资源类型
     * @param {string} action 操作类型
     * @param {object} context 上下文信息
     * @returns {boolean}
     */
    $hasOptimizedPermission(resource, action, context = {}) {
      if (!this.permissionChecker) {
        return false
      }
      
      const startTime = performance.now()
      const result = optimizedHasPermission(this.currentUser, resource, action, context)
      
      if (this.enablePerformanceMonitoring) {
        const duration = performance.now() - startTime
        performanceMonitor.recordCheck(duration, true) // 假设使用了缓存
      }
      
      return result
    },
    
    /**
     * 检查菜单访问权限
     * @param {string} menuId 菜单ID
     * @returns {boolean}
     */
    $canAccessMenu(menuId) {
      return this.permissionChecker ? this.permissionChecker.canAccessMenu(menuId) : false
    },
    
    /**
     * 检查学习目标权限
     * @param {string} action 操作类型
     * @param {object} context 上下文信息
     * @returns {boolean}
     */
    $canManageLearningGoal(action, context = {}) {
      return this.permissionChecker ? 
        this.permissionChecker.hasLearningGoalPermission(action, context) : false
    },
    
    /**
     * 检查学习计划权限
     * @param {string} action 操作类型
     * @param {object} context 上下文信息
     * @returns {boolean}
     */
    $canManageLearningPlan(action, context = {}) {
      return this.permissionChecker ? 
        this.permissionChecker.hasLearningPlanPermission(action, context) : false
    },
    
    /**
     * 检查页面访问权限
     * @param {string} path 页面路径
     * @returns {boolean}
     */
    $canAccessPage(path) {
      return canAccessPage(this.userRole, path)
    },
    
    /**
     * 检查角色权限
     * @param {string} role 角色名称
     * @param {string} permission 权限名称
     * @returns {boolean}
     */
    $roleHasPermission(role, permission) {
      return roleHasPermission(role, permission)
    },
    
    /**
     * 检查角色层级
     * @param {string} targetRole 目标角色
     * @returns {boolean}
     */
    $isRoleHigher(targetRole) {
      return isRoleHigher(this.userRole, targetRole)
    },
    
    /**
     * 检查用户认证状态
     * @returns {boolean}
     */
    $isAuthenticated() {
      return this.isUserAuthenticated
    },
    
    /**
     * 权限检查装饰器方法
     * @param {string|Array} permission - 权限名称或权限数组
     * @param {Function} callback - 回调函数
     * @param {string} errorMessage - 错误提示信息
     * @param {string} mode - 权限检查模式
     */
    $withPermission(permission, callback, errorMessage = '权限不足', mode = 'any') {
      let hasRequiredPermission = false
      
      if (Array.isArray(permission)) {
        hasRequiredPermission = this.$hasBatchPermissions(permission, mode)
      } else {
        hasRequiredPermission = this.$hasPermission(permission)
      }
      
      if (hasRequiredPermission) {
        return callback()
      } else {
        this.$showError(errorMessage)
        return false
      }
    },
    
    /**
     * 显示错误信息
     * @param {string} message 错误信息
     */
    $showError(message) {
      if (this.$message) {
        this.$message.error(message)
      } else {
        console.error(message)
      }
    },
    
    /**
     * 显示成功信息
     * @param {string} message 成功信息
     */
    $showSuccess(message) {
      if (this.$message) {
        this.$message.success(message)
      }
    },
    
    /**
     * 更新用户信息和权限
     */
    async $updateUserInfo() {
      try {
        const user = getCurrentUser()
        
        if (user) {
          this.currentUser = user
          this.userRole = user.role
          this.userPermissions = getRolePermissions(user.role) || []
          this.isUserAuthenticated = await isAuthenticated()
          
          // 创建优化的权限检查器
          this.permissionChecker = createPermissionChecker(user)
          
          this.permissionCacheStatus.loaded = true
          this.permissionCacheStatus.lastUpdate = new Date()
        } else {
          this.currentUser = null
          this.userRole = null
          this.userPermissions = []
          this.isUserAuthenticated = false
          this.permissionChecker = null
          
          this.permissionCacheStatus.loaded = false
          this.permissionCacheStatus.lastUpdate = null
        }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        this.isUserAuthenticated = false
      }
    },
    
    /**
     * 清理权限缓存
     */
    $clearPermissionCache() {
      try {
        clearCache()
        clearAllPermissionCache()
        this.batchPermissionCache.clear()
        
        if (this.permissionChecker) {
          this.permissionChecker.clearUserCache()
        }
        
        if (this.enablePerformanceMonitoring) {
          performanceMonitor.reset()
        }
        
        this.permissionCacheStatus.loaded = false
        this.permissionCacheStatus.lastUpdate = null
      } catch (error) {
        console.error('清理权限缓存失败:', error)
      }
    },
    
    /**
     * 同步权限配置
     * @param {boolean} force 是否强制同步
     */
    async $syncPermissions(force = false) {
      if (this.permissionCacheStatus.syncing && !force) {
        return false
      }
      
      this.permissionCacheStatus.syncing = true
      
      try {
        const result = await syncPermissions(force)
        
        if (result) {
          await this.$updateUserInfo()
          this.$clearPermissionCache()
        }
        
        this.permissionCacheStatus.syncing = false
        return result
      } catch (error) {
        console.error('权限同步失败:', error)
        this.permissionCacheStatus.syncing = false
        return false
      }
    },
    
    /**
     * 获取权限显示名称
     * @param {string} permission - 权限名称
     * @returns {string}
     */
    $getPermissionDisplayName(permission) {
      return getPermissionDisplayName(permission)
    },
    
    /**
     * 获取权限分类显示名称
     * @param {string} category - 权限分类
     * @returns {string}
     */
    $getCategoryDisplayName(category) {
      return getCategoryDisplayName(category)
    },
    
    /**
     * 权限变更处理
     * @param {Object} user - 用户信息
     */
    $onPermissionChange(user) {
      this.$updateUserInfo()
      // 子组件可以重写此方法来处理权限变更
    },
    
    /**
     * 权限变更监听
     * @param {Function} callback - 回调函数
     */
    $addPermissionListener(callback) {
      if (permissionSyncManager) {
        permissionSyncManager.addListener(callback)
      }
    },
    
    /**
     * 移除权限变更监听
     * @param {Function} callback - 回调函数
     */
    $removePermissionListener(callback) {
      if (permissionSyncManager) {
        permissionSyncManager.removeListener(callback)
      }
    },
    
    /**
     * 带权限检查的导航
     * @param {string} path - 目标路径
     * @param {object} params - 路由参数
     */
    $navigateWithPermission(path, params = {}) {
      if (this.$canAccessPage(path)) {
        this.$router.push({ path, ...params })
      } else {
        this.$showError('您没有权限访问该页面')
      }
    },
    
    /**
     * 检查页面是否需要认证
     * @param {string} path - 页面路径
     * @returns {boolean}
     */
    $pageRequiresAuth(path) {
      return pageRequiresAuth(path)
    },
    
    /**
     * 获取角色权限列表
     * @param {string} role - 角色名称
     * @returns {Array}
     */
    $getRolePermissions(role) {
      return getRolePermissions(role)
    },
    
    /**
     * 检查功能权限并执行操作
     * @param {string|Array} permission - 权限名称或权限数组
     * @param {Function} action - 要执行的操作
     * @param {string} feature - 功能名称（用于错误提示）
     * @param {string} mode - 权限检查模式: 'any' 或 'all'
     */
    $executeWithPermission(permission, action, feature = '此功能', mode = 'any') {
      return this.$withPermission(permission, action, `您没有权限使用${feature}`, mode)
    },
    
    /**
     * 获取性能监控报告
     * @returns {Object|null}
     */
    $getPerformanceReport() {
      return this.performanceReport
    },
    
    /**
     * 获取缓存统计信息
     * @returns {Object}
     */
    $getCacheStats() {
      return {
        permissionUtils: getCacheStats(),
        batchCache: {
          size: this.batchPermissionCache.size,
          maxSize: 1000
        },
        performance: this.performanceReport
      }
    }
  },
  
  async created() {
    // 初始化用户信息
    await this.$updateUserInfo()
    
    // 设置权限变更监听
    this.permissionListener = () => {
      this.$updateUserInfo()
    }
    
    // 监听权限变更
    if (permissionSyncManager) {
      permissionSyncManager.addListener(this.$onPermissionChange)
      
      // 启动权限同步管理器
      if (this.isUserAuthenticated) {
        permissionSyncManager.start()
        await this.$syncPermissions()
      }
    }
  },
  
  beforeUnmount() {
    // 清理权限变更监听
    if (permissionSyncManager && this.permissionListener) {
      permissionSyncManager.removeListener(this.$onPermissionChange)
    }
    
    // 清理批量权限缓存
    this.batchPermissionCache.clear()
  }
}

// 导出权限指令
export const permissionDirective = {
  mounted(el, binding) {
    const user = getCurrentUser()
    const permission = binding.value
    
    if (!user || !hasPermission(user.role, permission)) {
      el.style.display = 'none'
    }
  },
  
  updated(el, binding) {
    const user = getCurrentUser()
    const permission = binding.value
    
    if (!user || !hasPermission(user.role, permission)) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}

// 导出角色指令
export const roleDirective = {
  mounted(el, binding) {
    const user = getCurrentUser()
    const roles = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (!user || !roles.includes(user.role)) {
      el.style.display = 'none'
    }
  },
  
  updated(el, binding) {
    const user = getCurrentUser()
    const roles = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (!user || !roles.includes(user.role)) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}