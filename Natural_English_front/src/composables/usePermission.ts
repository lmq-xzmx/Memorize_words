import { computed } from 'vue'
import { useStore } from 'vuex'
import { permissionChecker } from '@/utils/permissions'

export function usePermission() {
  const store = useStore()
  
  // 获取当前用户权限
  const userPermissions = computed(() => {
    return store.getters['user/permissions'] || []
  })
  
  // 检查单个权限
  const hasPermission = (permission: string): boolean => {
    return permissionChecker.check(permission)
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
  const hasRole = (role: string): boolean => {
    const userRole = store.getters['user/role']
    return userRole === role
  }
  
  // 检查多个角色（任一）
  const hasAnyRole = (roles: string[]): boolean => {
    const userRole = store.getters['user/role']
    return roles.includes(userRole)
  }
  
  return {
    userPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole
  }
}