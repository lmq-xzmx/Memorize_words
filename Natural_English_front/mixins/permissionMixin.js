/**
 * 权限检查混入
 * 为Vue组件提供权限检查功能
 * 根据《用户权限管理系统规范》文档实现
 */

import {
  ROLE_PERMISSIONS,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  PAGE_PERMISSIONS,
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
} from '@/utils/permission'

import {
  getPermissionCache,
  setPermissionCache,
  cleanExpiredCache,
  getCacheStats
} from '@/utils/permissionCache'

import {
  ROLES,
  ROLE_DISPLAY_NAMES,
  getRolePermissions,
  roleHasPermission,
  isRoleHigher,
  getManageableRoles
} from '@/utils/roleDefinitions'

import {
  ALL_PERMISSIONS,
  PERMISSION_CATEGORIES,
  PERMISSION_DISPLAY_NAMES,
  LEARNING_PERMISSIONS,
  CONTENT_PERMISSIONS,
  SOCIAL_PERMISSIONS,
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS,
  ADVANCED_PERMISSIONS,
  PERMISSION_CONSTANTS
} from '@/utils/permissionConstants'

import {
  LEARNING_MODE_PERMISSIONS,
  getAccessibleLearningModes,
  pageRequiresAuth
} from '@/utils/learningModePermissions'

import {
  PermissionChecker,
  OPTIMIZED_ROLE_PERMISSIONS,
  createPermissionChecker,
  hasPermission as optimizedHasPermission
} from '@/utils/permissionUtils'

import {
  getDynamicPermissions,
  refreshDynamicPermissions,
  hasPermission as hasDynamicPermission
} from '@/utils/dynamicPermission'

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
      // 权限同步间隔（毫秒）
      permissionSyncInterval: 5 * 60 * 1000, // 5分钟
      // 权限加载状态
      isPermissionLoading: false,
      // 权限错误列表
      permissionErrors: [],
      // 缓存统计信息
      cacheStats: {
        hits: 0,
        misses: 0,
        totalChecks: 0
      }
    }
  },
  
  computed: {
    // 用户认证状态
    isAuthenticated() {
      return !!this.currentUser && !!this.currentUser.id
    },

    // 角色显示名称
    roleDisplayName() {
      if (!this.userRole) return '未知角色'
      return ROLE_DISPLAY_NAMES[this.userRole] || this.userRole
    },
    
    // 可访问的菜单项
    accessibleMenus() {
      if (!this.userRole || !this.permissionChecker) return []
      return this.permissionChecker.getAccessibleMenus()
    },
    
    // 可访问的页面列表
    accessiblePages() {
      if (!this.userRole) return []
      return getAccessiblePages(this.userRole)
    },
    
    // 可访问的学习模式
    accessibleLearningModes() {
      if (!this.userRole) return []
      return getAccessibleLearningModes(this.userRole)
    },

    // 权限同步状态
    permissionSyncStatus() {
      return {
        lastSync: this.permissionCacheStatus.lastUpdate,
        isLoading: this.isPermissionLoading,
        hasErrors: this.permissionErrors.length > 0,
        errors: this.permissionErrors
      }
    },

    // 缓存统计信息
    permissionCacheStats() {
      return getCacheStats()
    },
    
    // 角色层级检查
    isAdmin() {
      return this.userRole === ROLES.ADMIN
    },
    
    isDean() {
      return this.userRole === ROLES.DEAN
    },
    
    isAcademicSupervisor() {
      return this.userRole === ROLES.ACADEMIC_SUPERVISOR
    },
    
    isResearchManager() {
      return this.userRole === ROLES.RESEARCH_MANAGER
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
    
    /**
     * 优化后的权限检查器实例
     */
    optimizedPermissionChecker() {
      return this.currentUser ? createPermissionChecker(this.currentUser) : null
    },
    
    /**
     * 检查是否为教师角色（包括各级教师）
     */
    isTeacherRole() {
      return ['teacher', 'teaching_director', 'academic_director', 'research_group_leader'].includes(this.userRole)
    },
    
    /**
     * 检查是否为教导主任
     */
    isTeachingDirector() {
      return this.userRole === 'teaching_director'
    },
    
    /**
     * 检查是否为教务主任
     */
    isAcademicDirector() {
      return this.userRole === 'academic_director'
    },
    
    /**
      * 检查是否为教研组长
      */
     isResearchGroupLeader() {
       return this.userRole === 'research_group_leader'
     }
  },
  
  methods: {
    /**
     * 同步权限数据
     * @param {boolean} force - 是否强制同步
     * @returns {Promise<boolean>} 同步是否成功
     */
    async $syncPermissions(force = false) {
      if (this.permissionCacheStatus.syncing && !force) {
        return false
      }
      
      this.permissionCacheStatus.syncing = true
      
      try {
        const result = await syncPermissions(force)
        
        if (result) {
          // 重新获取用户权限
          await this.$updateUserInfo()
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
     * @param {string} permission - 权限代码
     * @returns {string} 权限显示名称
     */
    $getPermissionDisplayName(permission) {
      return getPermissionDisplayName(permission)
    },
    
    /**
     * 获取权限分类显示名称
     * @param {string} category - 权限分类
     * @returns {string} 分类显示名称
     */
    $getCategoryDisplayName(category) {
      return getCategoryDisplayName(category)
    },

    /**
     * 检查用户是否拥有指定权限
     * @param {string|Array} permission - 权限名称或权限数组
     * @param {object} context - 权限检查上下文
     * @returns {boolean}
     */
    $hasPermission(permission, context = {}) {
      if (!this.permissionChecker) {
        // 修复：使用用户角色而不是权限数组调用hasPermission
        if (this.userRole && this.userPermissions && this.userPermissions.length > 0) {
          // 如果有权限数组，直接检查
          return this.userPermissions.includes(permission) || this.userPermissions.includes('*')
        } else if (this.userRole) {
          // 如果只有角色，使用角色检查权限
          return hasPermission(this.userRole, permission)
        }
        return false
      }
      return this.permissionChecker.hasBasicPermission(permission)
    },
    
    /**
     * 检查用户是否拥有任一权限
     * @param {Array} permissions - 权限数组
     * @param {object} context - 权限检查上下文
     * @returns {boolean}
     */
    $hasAnyPermission(permissions, context = {}) {
      if (!permissions || !Array.isArray(permissions)) {
        return false
      }
      return permissions.some(permission => this.$hasPermission(permission, context))
    },
    
    /**
     * 检查用户是否拥有所有权限
     * @param {Array} permissions - 权限数组
     * @param {object} context - 权限检查上下文
     * @returns {boolean}
     */
    $hasAllPermissions(permissions, context = {}) {
      if (!permissions || !Array.isArray(permissions)) {
        return true
      }
      return permissions.every(permission => this.$hasPermission(permission, context))
    },
    
    /**
     * 批量权限检查
     * @param {Array} permissionChecks - 权限检查配置数组
     * @returns {object} 权限检查结果对象
     */
    $hasBatchPermissions(permissionChecks) {
      const results = {}
      permissionChecks.forEach(({ key, permission, context = {} }) => {
        results[key] = this.$hasPermission(permission, context)
      })
      return results
    },
    
    /**
     * 优化后的权限检查方法
     * @param {string} resource 资源类型
     * @param {string} action 操作类型
     * @param {object} context 上下文信息
     * @returns {boolean}
     */
    $hasOptimizedPermission(resource, action, context = {}) {
      return this.optimizedPermissionChecker ? 
        optimizedHasPermission(this.currentUser, resource, action, context) : false
    },
    
    /**
     * 检查菜单访问权限
     * @param {string} menuId 菜单ID
     * @returns {boolean}
     */
    $canAccessMenu(menuId) {
      return this.optimizedPermissionChecker ? 
        this.optimizedPermissionChecker.canAccessMenu(menuId) : false
    },
    
    /**
     * 检查学习目标权限
     * @param {string} action 操作类型
     * @param {object} context 上下文信息
     * @returns {boolean}
     */
    $canManageLearningGoal(action, context = {}) {
      return this.optimizedPermissionChecker ? 
        this.optimizedPermissionChecker.hasLearningGoalPermission(action, context) : false
    },
    
    /**
     * 检查学习计划权限
     * @param {string} action 操作类型
     * @param {object} context 上下文信息
     * @returns {boolean}
     */
    $canManageLearningPlan(action, context = {}) {
      return this.optimizedPermissionChecker ? 
        this.optimizedPermissionChecker.hasLearningPlanPermission(action, context) : false
    },
    
    /**
     * 检查用户是否可以访问指定页面
     * @param {string} path - 页面路径
     * @returns {boolean} 是否可以访问
     */
    $canAccessPage(path) {
      return canAccessPage(this.userPermissions, path)
    },
    
    /**
     * 检查学习目标权限
     * @param {string} action - 操作类型
     * @param {object} context - 上下文信息
     * @returns {boolean}
     */
    $hasLearningGoalPermission(action, context = {}) {
      if (!this.permissionChecker) return false
      return this.permissionChecker.hasLearningGoalPermission(action, context)
    },
    
    /**
     * 检查学习计划权限
     * @param {string} action - 操作类型
     * @param {object} context - 上下文信息
     * @returns {boolean}
     */
    $hasLearningPlanPermission(action, context = {}) {
      if (!this.permissionChecker) return false
      return this.permissionChecker.hasLearningPlanPermission(action, context)
    },
    
    /**
     * 检查角色是否拥有指定权限
     * @param {string} role - 角色名称
     * @param {string} permission - 权限名称
     * @returns {boolean}
     */
    $roleHasPermission(role, permission) {
      return roleHasPermission(role, permission)
    },
    
    /**
     * 检查当前角色是否高于指定角色
     * @param {string} targetRole - 目标角色
     * @returns {boolean}
     */
    $isRoleHigher(targetRole) {
      return isRoleHigher(this.userRole, targetRole)
    },
    
    /**
     * 检查用户是否已认证
     * @returns {boolean} 是否已认证
     */
    $isAuthenticated() {
      return isAuthenticated()
    },

    /**
     * 动态权限检查方法（从API获取最新权限）
     * @param {string} permission 权限标识
     * @returns {Promise<boolean>}
     */
    async $hasDynamicPermission(permission) {
      try {
        return await hasDynamicPermission(permission)
      } catch (error) {
        console.error('动态权限检查失败:', error)
        return false
      }
    },
    
    /**
     * 权限检查装饰器方法
     * @param {string} permission - 权限名称
     * @param {Function} callback - 回调函数
     * @param {string} errorMessage - 错误提示信息
     */
    $withPermission(permission, callback, errorMessage = '权限不足') {
      if (this.$hasPermission(permission)) {
        return callback()
      } else {
        this.$showError(errorMessage)
        return false
      }
    },
    
    /**
     * 显示错误信息
     * @param {string} message - 错误信息
     */
    $showError(message) {
      console.error(message)
      // 这里可以集成具体的UI组件库的提示组件
      alert(message) // 临时使用alert，实际项目中应该使用更好的UI组件
    },
    
    /**
     * 显示成功信息
     * @param {string} message - 成功信息
     */
    $showSuccess(message) {
      console.log(message)
      // 这里可以集成具体的UI组件库的提示组件
    },
    
    /**
     * 更新用户信息和权限
     */
    async $updateUserInfo() {
      try {
        const user = await getCurrentUser()
        if (user) {
          this.currentUser = user
          this.userRole = user.role
          
          // 修复：确保权限数据正确设置
          if (user.permissions && Array.isArray(user.permissions)) {
            this.userPermissions = user.permissions
          } else if (user.role) {
            // 如果没有权限数组，根据角色获取权限
            const rolePermissions = getRolePermissions(user.role)
            this.userPermissions = rolePermissions || []
          } else {
            // 使用新的权限缓存管理器获取权限
            this.userPermissions = await fetchUserPermissions(user.id || user.username, user.role)
          }
          this.isUserAuthenticated = true
          
          // 更新权限缓存状态
          this.permissionCacheStatus.loaded = true
          this.permissionCacheStatus.lastUpdate = new Date()
          this.permissionCacheStatus.syncing = false
          
          // 初始化权限检查器
          if (user) {
            this.permissionChecker = new PermissionChecker(user)
          } else {
            this.permissionChecker = null
          }
        } else {
          this.currentUser = null
          this.userRole = null
          this.userPermissions = []
          this.isUserAuthenticated = false
          this.permissionCacheStatus.loaded = false
          this.permissionChecker = null
        }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        this.currentUser = null
        this.userRole = null
        this.userPermissions = []
        this.isUserAuthenticated = false
        this.permissionCacheStatus.loaded = false
        this.permissionChecker = null
      }
    },
    
    /**
     * 清除权限缓存
     */
    $clearPermissionCache() {
      clearCache()
      this.permissionCacheStatus.loaded = false
      this.permissionCacheStatus.lastUpdate = null
      this.permissionCacheStatus.syncing = false
      this.permissionCacheStatus = {
        loaded: false,
        lastUpdate: null,
        syncing: false
      }
      
      // 重新获取用户信息
      this.$updateUserInfo()
    },
    
    /**
     * 同步权限配置
     */
    async $syncPermissions() {
      this.permissionCacheStatus.syncing = true
      try {
        await permissionSyncManager.syncPermissions()
        await this.$updateUserInfo()
      } catch (error) {
        console.error('权限同步失败:', error)
      } finally {
        this.permissionCacheStatus.syncing = false
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
     * 导航到指定页面（带权限检查）
     * @param {string} path - 页面路径
     * @param {Object} params - 路由参数
     */
    $navigateWithPermission(path, params = {}) {
      if (this.$canAccessPage(path)) {
        this.$router.push({ path, ...params })
      } else {
        console.warn(`没有权限访问页面: ${path}`)
        // 重定向到用户默认页面
        const defaultPage = this.userDefaultPage || '/dashboard'
        this.$router.push(defaultPage)
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
      let hasRequiredPermission = false
      
      if (Array.isArray(permission)) {
        hasRequiredPermission = mode === 'all' 
          ? this.$hasAllPermissions(permission)
          : this.$hasAnyPermission(permission)
      } else {
        hasRequiredPermission = this.$hasPermission(permission)
      }
      
      if (hasRequiredPermission) {
        try {
          return action()
        } catch (error) {
          console.error(`执行${feature}时发生错误:`, error)
          this.$showError(`执行${feature}时发生错误`)
        }
      } else {
        console.warn(`权限不足，无法执行操作: ${permission}`)
        this.$showError(`您没有权限使用${feature}`)
      }
    }
  },
  
  async created() {
    // 初始化用户信息
    await this.$updateUserInfo()
    
    // 初始化权限检查器
    if (this.currentUser) {
      this.permissionChecker = new PermissionChecker(this.currentUser)
    }
    
    // 设置权限变更监听
    this.permissionListener = () => {
      this.$updateUserInfo()
    }
    
    // 监听权限变更
    permissionSyncManager.addListener(this.$onPermissionChange)
    
    // 启动权限同步管理器
    if (permissionSyncManager && this.isUserAuthenticated) {
      permissionSyncManager.start()
      // 启动权限缓存管理器的自动同步
      await this.$syncPermissions()
    }
  },
  
  beforeUnmount() {
    // 清理权限变更监听器
    permissionSyncManager.removeListener(this.$onPermissionChange)
    
    // 停止权限同步管理器
    if (permissionSyncManager) {
      permissionSyncManager.stop()
    }
  }
}

/**
 * 权限指令
 * 用法：v-permission="'permission_name'"
 */
export const permissionDirective = {
  mounted(el, binding) {
    const user = getCurrentUser()
    const permission = binding.value
    
    if (!user || !hasPermission(user.role, permission)) {
      // 隐藏元素
      el.style.display = 'none'
      // 或者移除元素
      // el.parentNode && el.parentNode.removeChild(el)
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

/**
 * 角色指令
 * 用法：v-role="'admin'" 或 v-role="['admin', 'teacher']"
 */
export const roleDirective = {
  mounted(el, binding) {
    const user = getCurrentUser()
    const requiredRoles = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (!user || !requiredRoles.includes(user.role)) {
      el.style.display = 'none'
    }
  },
  
  updated(el, binding) {
    const user = getCurrentUser()
    const requiredRoles = Array.isArray(binding.value) ? binding.value : [binding.value]
    
    if (!user || !requiredRoles.includes(user.role)) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}