/**
 * usePermission 组合式API
 * 为Vue 3 Composition API提供权限控制功能
 * 根据《用户权限管理系统规范》文档实现
 */

import { ref, computed, onMounted, onUnmounted, watch, Ref } from 'vue'
import type { User, PermissionCacheStatus } from '../types/utils'

interface UsePermissionReturn {
  currentUser: Ref<User | null>
  userRole: Ref<string | null>
  userPermissions: Ref<string[]>
  isUserAuthenticated: Ref<boolean>
  permissionCacheStatus: Ref<PermissionCacheStatus>
  roleDisplayName: Ref<string>
  accessibleMenus: Ref<any[]>
  accessiblePages: Ref<string[]>
  accessibleLearningModes: Ref<string[]>
  isAdmin: Ref<boolean>
  isDean: Ref<boolean>
  isAcademicDirector: Ref<boolean>
  isResearchLeader: Ref<boolean>
  isTeacher: Ref<boolean>
  isParent: Ref<boolean>
  isStudent: Ref<boolean>
  hasLearningPermissions: Ref<boolean>
  hasContentPermissions: Ref<boolean>
  hasSocialPermissions: Ref<boolean>
  hasManagementPermissions: Ref<boolean>
  hasSystemPermissions: Ref<boolean>
  hasAdvancedPermissions: Ref<boolean>
  defaultPage: Ref<string>
  checkPermission: (permission: string) => boolean
  checkAnyPermission: (permissions: string[]) => boolean
  checkAllPermissions: (permissions: string[]) => boolean
  checkPageAccess: (pagePath: string) => boolean
  checkAuthentication: () => boolean
  checkRolePermission: (role: string, permission: string) => boolean
  checkRoleHierarchy: (targetRole: string) => boolean
  updateUserInfo: () => Promise<void>
  logout: () => Promise<void>
  refreshPermissions: () => Promise<void>
  syncPermissions: () => Promise<void>
  getPermissionDisplayName: (permission: string) => string
  getCategoryDisplayName: (category: string) => string
  getManageableRoles: () => string[]
  navigateToDefaultPage: () => Promise<void>
  cleanup: () => void
}

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
} from '../utils/permission'

import {
  ROLES,
  ROLE_DISPLAY_NAMES,
  getRolePermissions,
  roleHasPermission,
  isRoleHigher,
  getManageableRoles
} from '../utils/roleDefinitions'

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
} from '../utils/permissionConstants'

import {
  PAGE_PERMISSIONS,
  getAccessibleLearningModes,
  pageRequiresAuth
} from '../utils/learningModePermissions'

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
  const checkPermission = (permission: string) => {
    return hasPermission(userPermissions.value, permission)
  }
  
  const checkAnyPermission = (permissions: string[]) => {
    return hasAnyPermission(userPermissions.value, permissions)
  }
  
  const checkAllPermissions = (permissions: string[]) => {
    return hasAllPermissions(userPermissions.value, permissions)
  }
  
  const checkPageAccess = (pagePath: string) => {
    return canAccessPage(userPermissions.value, pagePath)
  }
  
  const checkAuthentication = () => {
    return isAuthenticated()
  }
  
  const checkRolePermission = (role: string, permission: string) => {
    return roleHasPermission(role, permission)
  }
  
  const checkRoleHierarchy = (targetRole: string) => {
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
  const navigateWithPermission = (path: string, options = {}) => {
    if (checkPageAccess(path)) {
      router.push({ path, ...options })
    } else {
      console.warn(`没有权限访问页面: ${path}`)
      const defaultPage = userDefaultPage.value || '/dashboard'
      router.push(defaultPage)
    }
  }
  
  const executeWithPermission = (permission: string | string[], action: () => any, fallback: (() => any) | null = null, mode = 'any') => {
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
  const getPermissionName = (permission: string) => {
    return getPermissionDisplayName(permission)
  }
  
  const getCategoryName = (category: string) => {
    return getCategoryDisplayName(category)
  }
  
  const getRolePermissionList = (role: string) => {
    return getRolePermissions(role)
  }
  
  const checkPageAuth = (path: string) => {
    return pageRequiresAuth(path)
  }
  
  // 权限变更监听
  let permissionListener: any = null
  
  const addPermissionListener = (callback: (user: any) => void) => {
    if (permissionSyncManager) {
      permissionSyncManager.addListener(callback)
    }
  }
  
  const removePermissionListener = (callback: (user: any) => void) => {
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