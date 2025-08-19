import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { permissionChecker } from '@/utils/permissions'
import type { RouteLocationNormalized } from 'vue-router'

// 权限类型定义
export interface Permission {
  id: string
  name: string
  code: string
  module: string
  description?: string
}

export interface Role {
  id: string
  name: string
  code: string
  permissions: Permission[]
}

export interface User {
  id: string
  username: string
  roles: Role[]
  permissions: Permission[]
}

// 菜单项类型定义
export interface MenuItem {
  id: string
  name: string
  path: string
  icon?: string
  component?: string
  meta?: {
    title?: string
    requiresAuth?: boolean
    permissions?: string[]
    roles?: string[]
  }
  children?: MenuItem[]
}

export function usePermission() {
  const store = useStore()
  
  // 当前用户信息
  const currentUser = computed<User | null>(() => store.getters['user/currentUser'])
  
  // 获取当前用户权限
  const userPermissions = computed(() => {
    return store.getters['user/permissions'] || []
  })
  
  // 用户角色列表
  const userRoles = computed<Role[]>(() => {
    if (!currentUser.value) return []
    return currentUser.value.roles || []
  })
  
  // 权限代码列表
  const permissionCodes = computed<string[]>(() => {
    return userPermissions.value.map((p: any) => p.code || p)
  })
  
  // 角色代码列表
  const roleCodes = computed<string[]>(() => {
    return userRoles.value.map(r => r.code)
  })
  
  // 检查单个权限
  const hasPermission = (permission: string | string[], requireAll = false): boolean => {
    if (typeof permission === 'string') {
      return permissionChecker.check(permission)
    }
    
    if (requireAll) {
      return permissionChecker.checkAll(permission)
    } else {
      return permissionChecker.checkAny(permission)
    }
  }
  
  // 检查多个权限（任一）
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissionChecker.checkAny(permissions)
  }
  
  // 检查多个权限（全部）
  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissionChecker.checkAll(permissions)
  }
  
  // 检查用户角色
  const hasRole = (role: string | string[], requireAll = false): boolean => {
    const userRole = store.getters['user/role']
    
    if (typeof role === 'string') {
      return userRole === role
    }
    
    if (requireAll) {
      return role.every(r => roleCodes.value.includes(r))
    } else {
      return role.some(r => roleCodes.value.includes(r))
    }
  }
  
  // 检查多个角色（任一）
  const hasAnyRole = (roles: string[]): boolean => {
    const userRole = store.getters['user/role']
    return roles.includes(userRole)
  }
  
  // 检查是否为超级管理员
  const isSuperAdmin = computed<boolean>(() => {
    return hasRole(['super_admin', 'admin'])
  })
  
  // 检查路由权限
  const hasRoutePermission = (route: RouteLocationNormalized): boolean => {
    if (!route.meta?.requiresAuth) return true
    if (!currentUser.value) return false
    if (isSuperAdmin.value) return true
    
    if (route.meta?.roles && route.meta.roles.length > 0) {
      if (!hasRole(route.meta.roles)) return false
    }
    
    if (route.meta?.permissions && route.meta.permissions.length > 0) {
      if (!hasPermission(route.meta.permissions)) return false
    }
    
    return true
  }
  
  // 过滤用户可访问的菜单项
  const filterMenuItems = (menuItems: MenuItem[]): MenuItem[] => {
    return menuItems.filter(item => {
      const hasCurrentPermission = checkMenuItemPermission(item)
      
      if (!hasCurrentPermission) return false
      
      if (item.children && item.children.length > 0) {
        item.children = filterMenuItems(item.children)
      }
      
      return true
    })
  }
  
  // 检查单个菜单项权限
  const checkMenuItemPermission = (menuItem: MenuItem): boolean => {
    if (!menuItem.meta?.requiresAuth) return true
    if (!currentUser.value) return false
    if (isSuperAdmin.value) return true
    
    if (menuItem.meta?.roles && menuItem.meta.roles.length > 0) {
      if (!hasRole(menuItem.meta.roles)) return false
    }
    
    if (menuItem.meta?.permissions && menuItem.meta.permissions.length > 0) {
      if (!hasPermission(menuItem.meta.permissions)) return false
    }
    
    return true
  }
  
  // 刷新用户权限信息
  const refreshPermissions = async (): Promise<void> => {
    try {
      await store.dispatch('user/fetchUserInfo')
    } catch (error) {
      console.error('刷新用户权限失败:', error)
      throw error
    }
  }
  
  return {
    // 原有功能保持兼容
    userPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    
    // 新增功能
    currentUser,
    userRoles,
    permissionCodes,
    roleCodes,
    isSuperAdmin,
    hasRoutePermission,
    filterMenuItems,
    checkMenuItemPermission,
    refreshPermissions
  }
}

// 权限指令相关函数
export function usePermissionDirective() {
  const { hasPermission, hasRole, isSuperAdmin } = usePermission()
  
  const checkElementPermission = (value: any): boolean => {
    if (!value) return true
    if (isSuperAdmin.value) return true
    
    if (typeof value === 'string') {
      return hasPermission(value)
    }
    
    if (Array.isArray(value)) {
      return hasPermission(value)
    }
    
    if (typeof value === 'object') {
      const { permissions, roles, requireAll = false } = value
      
      let hasRequiredPermission = true
      let hasRequiredRole = true
      
      if (permissions) {
        hasRequiredPermission = hasPermission(permissions, requireAll)
      }
      
      if (roles) {
        hasRequiredRole = hasRole(roles, requireAll)
      }
      
      return hasRequiredPermission && hasRequiredRole
    }
    
    return false
  }
  
  return {
    checkElementPermission
  }
}

// 导出类型
export type { Permission, Role, User, MenuItem }