/**
 * usePermission 组合式API
 * 为Vue 3 Composition API提供权限控制功能
 * 根据《用户权限管理系统规范》文档实现
 */

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
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
  clearPermissionCache,
  getCachedPermissions,
  setCachedPermissions,
  permissionSyncManager
} from '../utils/permission.js'

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

/**
 * 权限管理组合式API
 * @returns {Object} 权限相关的响应式数据和方法
 */
export function usePermission() {
  const router = useRouter()
  
  // 响应式数据
  const currentUser = ref(null)
  const userRole = ref(null)
  const userPermissions = ref([])
  const isUserAuthenticated = ref(false)
  const permissionCacheStatus = ref({
    loaded: false,
    lastUpdate: null,
    syncing: false
  })
  
  // 计算属性
  const roleDisplayName = computed(() => {
    return userRole.value ? getRoleDisplayName(userRole.value) : '未知角色'
  })
  
  const accessibleMenus = computed(() => {
    return getAccessibleMenus(userPermissions.value)
  })
  
  const accessiblePages = computed(() => {
    return getAccessiblePages(userPermissions.value)
  })
  
  const accessibleLearningModes = computed(() => {
    return getAccessibleLearningModes(userPermissions.value)
  })
  
  // 角色层级检查
  const isAdmin = computed(() => userRole.value === ROLES.ADMIN)
  const isDean = computed(() => userRole.value === ROLES.DEAN)
  const isAcademicDirector = computed(() => userRole.value === ROLES.ACADEMIC_DIRECTOR)
  const isResearchLeader = computed(() => userRole.value === ROLES.RESEARCH_LEADER)
  const isTeacher = computed(() => userRole.value === ROLES.TEACHER)
  const isParent = computed(() => userRole.value === ROLES.PARENT)
  const isStudent = computed(() => userRole.value === ROLES.STUDENT)
  
  // 权限分类检查
  const hasLearningPermissions = computed(() => {
    return hasAnyPermission(userPermissions.value, LEARNING_PERMISSIONS)
  })
  
  const hasContentPermissions = computed(() => {
    return hasAnyPermission(userPermissions.value, CONTENT_PERMISSIONS)
  })
  
  const hasSocialPermissions = computed(() => {
    return hasAnyPermission(userPermissions.value, SOCIAL_PERMISSIONS)
  })
  
  const hasManagementPermissions = computed(() => {
    return hasAnyPermission(userPermissions.value, MANAGEMENT_PERMISSIONS)
  })
  
  const hasSystemPermissions = computed(() => {
    return hasAnyPermission(userPermissions.value, SYSTEM_PERMISSIONS)
  })
  
  const hasAdvancedPermissions = computed(() => {
    return hasAnyPermission(userPermissions.value, ADVANCED_PERMISSIONS)
  })
  
  const manageableRoles = computed(() => {
    return getManageableRoles(userRole.value)
  })
  
  const userDefaultPage = computed(() => {
    return getDefaultPageForRole(userRole.value)
  })
  
  // 权限检查方法
  const checkPermission = (permission) => {
    return hasPermission(userPermissions.value, permission)
  }
  
  const checkAnyPermission = (permissions) => {
    return hasAnyPermission(userPermissions.value, permissions)
  }
  
  const checkAllPermissions = (permissions) => {
    return hasAllPermissions(userPermissions.value, permissions)
  }
  
  const checkPageAccess = (pagePath) => {
    return canAccessPage(userPermissions.value, pagePath)
  }
  
  const checkAuthentication = () => {
    return isAuthenticated()
  }
  
  const checkRolePermission = (role, permission) => {
    return roleHasPermission(role, permission)
  }
  
  const checkRoleHierarchy = (targetRole) => {
    return isRoleHigher(userRole.value, targetRole)
  }
  
  // 用户信息管理
  const updateUserInfo = async () => {
    try {
      const user = await getCurrentUser()
      if (user) {
        currentUser.value = user
        userRole.value = user.role
        userPermissions.value = getRolePermissions(user.role)
        isUserAuthenticated.value = true
        
        // 更新权限缓存状态
        permissionCacheStatus.value.loaded = true
        permissionCacheStatus.value.lastUpdate = new Date()
      } else {
        currentUser.value = null
        userRole.value = null
        userPermissions.value = []
        isUserAuthenticated.value = false
        permissionCacheStatus.value.loaded = false
      }
    } catch (error) {
      console.error('更新用户信息失败:', error)
      currentUser.value = null
      userRole.value = null
      userPermissions.value = []
      isUserAuthenticated.value = false
      permissionCacheStatus.value.loaded = false
    }
  }
  
  // 权限缓存管理
  const clearCache = () => {
    clearPermissionCache()
    permissionCacheStatus.value = {
      loaded: false,
      lastUpdate: null,
      syncing: false
    }
    updateUserInfo()
  }
  
  const syncPermissions = async () => {
    permissionCacheStatus.value.syncing = true
    try {
      await permissionSyncManager.syncPermissions()
      await updateUserInfo()
    } catch (error) {
      console.error('权限同步失败:', error)
    } finally {
      permissionCacheStatus.value.syncing = false
    }
  }
  
  // 导航和操作
  const navigateWithPermission = (path, options = {}) => {
    if (checkPageAccess(path)) {
      router.push({ path, ...options })
    } else {
      console.warn(`没有权限访问页面: ${path}`)
      const defaultPage = userDefaultPage.value || '/dashboard'
      router.push(defaultPage)
    }
  }
  
  const executeWithPermission = (permission, action, fallback = null, mode = 'any') => {
    let hasRequiredPermission = false
    
    if (Array.isArray(permission)) {
      hasRequiredPermission = mode === 'all' 
        ? checkAllPermissions(permission)
        : checkAnyPermission(permission)
    } else {
      hasRequiredPermission = checkPermission(permission)
    }
    
    if (hasRequiredPermission) {
      return action()
    } else {
      console.warn(`权限不足，无法执行操作: ${permission}`)
      if (fallback) {
        return fallback()
      }
    }
  }
  
  // 工具方法
  const getPermissionName = (permission) => {
    return getPermissionDisplayName(permission)
  }
  
  const getCategoryName = (category) => {
    return getCategoryDisplayName(category)
  }
  
  const getRolePermissionList = (role) => {
    return getRolePermissions(role)
  }
  
  const checkPageAuth = (path) => {
    return pageRequiresAuth(path)
  }
  
  // 权限变更监听
  let permissionListener = null
  
  const addPermissionListener = (callback) => {
    if (permissionSyncManager) {
      permissionSyncManager.addListener(callback)
    }
  }
  
  const removePermissionListener = (callback) => {
    if (permissionSyncManager) {
      permissionSyncManager.removeListener(callback)
    }
  }
  
  // 生命周期管理
  onMounted(async () => {
    // 初始化用户信息
    await updateUserInfo()
    
    // 设置权限变更监听
    permissionListener = () => {
      updateUserInfo()
    }
    addPermissionListener(permissionListener)
    
    // 启动权限同步管理器
    if (permissionSyncManager && isUserAuthenticated.value) {
      permissionSyncManager.start()
    }
  })
  
  onUnmounted(() => {
    // 清理权限变更监听
    if (permissionListener) {
      removePermissionListener(permissionListener)
    }
    
    // 停止权限同步管理器
    if (permissionSyncManager) {
      permissionSyncManager.stop()
    }
  })
  
  // 监听用户认证状态变化
  watch(isUserAuthenticated, (newValue) => {
    if (newValue && permissionSyncManager) {
      permissionSyncManager.start()
    } else if (!newValue && permissionSyncManager) {
      permissionSyncManager.stop()
    }
  })
  
  return {
    // 响应式数据
    currentUser,
    userRole,
    userPermissions,
    isUserAuthenticated,
    permissionCacheStatus,
    
    // 计算属性
    roleDisplayName,
    accessibleMenus,
    accessiblePages,
    accessibleLearningModes,
    isAdmin,
    isDean,
    isAcademicDirector,
    isResearchLeader,
    isTeacher,
    isParent,
    isStudent,
    hasLearningPermissions,
    hasContentPermissions,
    hasSocialPermissions,
    hasManagementPermissions,
    hasSystemPermissions,
    hasAdvancedPermissions,
    manageableRoles,
    userDefaultPage,
    
    // 权限检查方法
    checkPermission,
    checkAnyPermission,
    checkAllPermissions,
    checkPageAccess,
    checkAuthentication,
    checkRolePermission,
    checkRoleHierarchy,
    
    // 用户信息管理
    updateUserInfo,
    
    // 权限缓存管理
    clearCache,
    syncPermissions,
    
    // 导航和操作
    navigateWithPermission,
    executeWithPermission,
    
    // 工具方法
    getPermissionName,
    getCategoryName,
    getRolePermissionList,
    checkPageAuth,
    
    // 权限变更监听
    addPermissionListener,
    removePermissionListener
  }
}

/**
 * 简化的权限检查组合式API
 * 只提供基本的权限检查功能，适用于简单场景
 */
export function useSimplePermission() {
  const { 
    userPermissions, 
    userRole, 
    isUserAuthenticated,
    checkPermission,
    checkPageAccess,
    updateUserInfo
  } = usePermission()
  
  return {
    userPermissions,
    userRole,
    isUserAuthenticated,
    hasPermission: checkPermission,
    canAccessPage: checkPageAccess,
    updateUserInfo
  }
}

/**
 * 角色检查组合式API
 * 专门用于角色相关的权限检查
 */
export function useRolePermission() {
  const {
    userRole,
    isAdmin,
    isDean,
    isAcademicDirector,
    isResearchLeader,
    isTeacher,
    isParent,
    isStudent,
    manageableRoles,
    checkRolePermission,
    checkRoleHierarchy
  } = usePermission()
  
  return {
    userRole,
    isAdmin,
    isDean,
    isAcademicDirector,
    isResearchLeader,
    isTeacher,
    isParent,
    isStudent,
    manageableRoles,
    checkRolePermission,
    checkRoleHierarchy
  }
}