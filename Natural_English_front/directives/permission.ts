/**
 * 权限指令
 * 提供v-permission、v-role、v-auth等指令用于模板权限控制
 * 根据《用户权限管理系统规范》文档实现
 */

import type { App, DirectiveBinding } from 'vue'

// 导入权限常量和角色定义
import unifiedPermissionConstants from '../utils/unifiedPermissionConstants'
import * as roleDefinitions from '../utils/roleDefinitions'

// 解构权限常量
const {
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS
} = unifiedPermissionConstants

// 解构角色定义函数
const {
  getRolePermissions,
  roleHasPermission
} = roleDefinitions

// 用户信息接口
interface UserInfo {
  id: string
  username: string
  role: string
  permissions?: string[]
}

// 指令绑定值类型
type PermissionValue = string | string[]
type RoleValue = string | string[]
type PermissionLevel = 'basic' | 'advanced' | 'admin'

// 指令修饰符接口
interface PermissionModifiers {
  all?: boolean
  page?: boolean
}

interface RoleModifiers {
  higher?: boolean
}

interface AuthModifiers {
  guest?: boolean
}

// 简化的权限检查函数，避免循环依赖
function hasAnyPermission(userPermissions: string[], permissions: string[]): boolean {
  if (!userPermissions || !Array.isArray(userPermissions)) return false
  if (!permissions || !Array.isArray(permissions)) return false
  return permissions.some(permission => userPermissions.includes(permission))
}

function hasPermission(userPermissions: string[], permission: string): boolean {
  if (!userPermissions || !Array.isArray(userPermissions)) return false
  return userPermissions.includes(permission)
}

function hasAllPermissions(userPermissions: string[], permissions: string[]): boolean {
  if (!userPermissions || !Array.isArray(userPermissions)) return false
  if (!permissions || !Array.isArray(permissions)) return false
  return permissions.every(permission => userPermissions.includes(permission))
}

function canAccessPage(userPermissions: string[], path: string): boolean {
  // 简化的页面权限检查
  return true // 暂时允许所有页面访问
}

function getCurrentUser(): UserInfo | null {
  try {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  } catch (error) {
    console.error('获取用户信息失败:', error)
    return null
  }
}

function isAuthenticated(): boolean {
  const user = getCurrentUser()
  return !!(user && user.id)
}

/**
 * 获取当前用户权限
 * @returns {string[]} 用户权限列表
 */
function getCurrentUserPermissions(): string[] {
  try {
    const user = getCurrentUser()
    if (user && user.role) {
      return getRolePermissions(user.role) || []
    }
    return []
  } catch (error) {
    console.error('获取用户权限失败:', error)
    return []
  }
}

/**
 * 获取当前用户角色
 * @returns {string|null} 用户角色
 */
function getCurrentUserRole(): string | null {
  try {
    const user = getCurrentUser()
    return user?.role || null
  } catch (error) {
    console.error('获取用户角色失败:', error)
    return null
  }
}

/**
 * 隐藏元素的通用方法
 * @param {HTMLElement} el - DOM元素
 * @param {string} reason - 隐藏原因
 */
function hideElement(el: HTMLElement, reason: string): void {
  el.style.display = 'none'
  el.setAttribute(`data-${reason}-hidden`, 'true')
  el.setAttribute('aria-hidden', 'true')
}

/**
 * 显示元素的通用方法
 * @param {HTMLElement} el - DOM元素
 * @param {string} reason - 隐藏原因
 */
function showElement(el: HTMLElement, reason: string): void {
  el.style.display = ''
  el.removeAttribute(`data-${reason}-hidden`)
  el.removeAttribute('aria-hidden')
}

/**
 * v-permission 指令
 * 用法:
 * v-permission="'user.read'" - 检查单个权限
 * v-permission="['user.read', 'user.write']" - 检查多个权限（任一）
 * v-permission.all="['user.read', 'user.write']" - 检查多个权限（全部）
 * v-permission.page="'/dashboard'" - 检查页面访问权限
 */
export const permissionDirective = {
  mounted(el: HTMLElement, binding: DirectiveBinding<PermissionValue>) {
    const { value, modifiers } = binding as DirectiveBinding<PermissionValue> & { modifiers: PermissionModifiers }
    
    try {
      let hasRequiredPermission = false
      
      if (modifiers.page) {
        // 页面访问权限检查
        const userPermissions = getCurrentUserPermissions()
        hasRequiredPermission = canAccessPage(userPermissions, value as string)
      } else {
        // 功能权限检查
        const userPermissions = getCurrentUserPermissions()
        
        if (Array.isArray(value)) {
          if (modifiers.all) {
            hasRequiredPermission = hasAllPermissions(userPermissions, value)
          } else {
            hasRequiredPermission = hasAnyPermission(userPermissions, value)
          }
        } else {
          hasRequiredPermission = hasPermission(userPermissions, value)
        }
      }
      
      if (!hasRequiredPermission) {
        hideElement(el, 'permission')
      }
    } catch (error) {
      console.error('权限指令检查失败:', error)
      // 安全起见，权限检查失败时隐藏元素
      hideElement(el, 'permission')
    }
  },
  
  updated(el: HTMLElement, binding: DirectiveBinding<PermissionValue>) {
    const { value, modifiers } = binding as DirectiveBinding<PermissionValue> & { modifiers: PermissionModifiers }
    
    try {
      let hasRequiredPermission = false
      
      if (modifiers.page) {
        // 页面访问权限检查
        const userPermissions = getCurrentUserPermissions()
        hasRequiredPermission = canAccessPage(userPermissions, value as string)
      } else {
        // 功能权限检查
        const userPermissions = getCurrentUserPermissions()
        
        if (Array.isArray(value)) {
          if (modifiers.all) {
            hasRequiredPermission = hasAllPermissions(userPermissions, value)
          } else {
            hasRequiredPermission = hasAnyPermission(userPermissions, value)
          }
        } else {
          hasRequiredPermission = hasPermission(userPermissions, value)
        }
      }
      
      if (!hasRequiredPermission) {
        hideElement(el, 'permission')
      } else {
        showElement(el, 'permission')
      }
    } catch (error) {
      console.error('权限指令更新失败:', error)
      hideElement(el, 'permission')
    }
  }
}

/**
 * v-role 指令
 * 用法:
 * v-role="'admin'" - 检查单个角色
 * v-role="['admin', 'teacher']" - 检查多个角色
 * v-role.higher="'student'" - 检查是否高于指定角色
 */
export const roleDirective = {
  mounted(el: HTMLElement, binding: DirectiveBinding<RoleValue>) {
    const { value, modifiers } = binding as DirectiveBinding<RoleValue> & { modifiers: RoleModifiers }
    
    try {
      const userRole = getCurrentUserRole()
      let hasRequiredRole = false
      
      if (modifiers.higher) {
        // 检查角色层级 - 暂时简化处理
        hasRequiredRole = false
      } else {
        // 检查角色匹配
        if (Array.isArray(value)) {
          hasRequiredRole = value.includes(userRole!)
        } else {
          hasRequiredRole = userRole === value
        }
      }
      
      if (!hasRequiredRole) {
        hideElement(el, 'role')
      }
    } catch (error) {
      console.error('角色指令检查失败:', error)
      hideElement(el, 'role')
    }
  },
  
  updated(el: HTMLElement, binding: DirectiveBinding<RoleValue>) {
    const { value, modifiers } = binding as DirectiveBinding<RoleValue> & { modifiers: RoleModifiers }
    
    try {
      const userRole = getCurrentUserRole()
      let hasRequiredRole = false
      
      if (modifiers.higher) {
        // 检查角色层级 - 暂时简化处理
        hasRequiredRole = false
      } else {
        // 检查角色匹配
        if (Array.isArray(value)) {
          hasRequiredRole = value.includes(userRole!)
        } else {
          hasRequiredRole = userRole === value
        }
      }
      
      if (!hasRequiredRole) {
        hideElement(el, 'role')
      } else {
        showElement(el, 'role')
      }
    } catch (error) {
      console.error('角色指令更新失败:', error)
      hideElement(el, 'role')
    }
  }
}

/**
 * v-auth 指令
 * 用法:
 * v-auth - 检查用户是否已认证
 * v-auth.guest - 检查用户是否为访客（未认证）
 */
export const authDirective = {
  mounted(el: HTMLElement, binding: DirectiveBinding<any>) {
    const { modifiers } = binding as DirectiveBinding<any> & { modifiers: AuthModifiers }
    
    try {
      const authenticated = isAuthenticated()
      
      let shouldShow = false
      if (modifiers.guest) {
        // 访客模式：未认证时显示
        shouldShow = !authenticated
      } else {
        // 认证模式：已认证时显示
        shouldShow = authenticated
      }
      
      if (!shouldShow) {
        hideElement(el, 'auth')
      }
    } catch (error) {
      console.error('认证指令检查失败:', error)
      hideElement(el, 'auth')
    }
  },
  
  updated(el: HTMLElement, binding: DirectiveBinding<any>) {
    const { modifiers } = binding as DirectiveBinding<any> & { modifiers: AuthModifiers }
    
    try {
      const authenticated = isAuthenticated()
      
      let shouldShow = false
      if (modifiers.guest) {
        // 访客模式：未认证时显示
        shouldShow = !authenticated
      } else {
        // 认证模式：已认证时显示
        shouldShow = authenticated
      }
      
      if (!shouldShow) {
        hideElement(el, 'auth')
      } else {
        showElement(el, 'auth')
      }
    } catch (error) {
      console.error('认证指令更新失败:', error)
      hideElement(el, 'auth')
    }
  }
}

/**
 * v-permission-level 指令
 * 根据权限级别控制元素显示
 * 用法:
 * v-permission-level="'basic'" - 基础权限级别
 * v-permission-level="'advanced'" - 高级权限级别
 */
export const permissionLevelDirective = {
  mounted(el: HTMLElement, binding: DirectiveBinding<PermissionLevel>) {
    const { value } = binding
    
    try {
      const userPermissions = getCurrentUserPermissions()
      
      let hasRequiredLevel = false
      
      switch (value) {
        case 'basic':
          // 基础级别：有任何权限即可
          hasRequiredLevel = userPermissions.length > 0
          break
        case 'advanced':
          // 高级级别：需要管理或系统权限
          hasRequiredLevel = hasAnyPermission(userPermissions, [...Object.values(MANAGEMENT_PERMISSIONS) as string[], ...Object.values(SYSTEM_PERMISSIONS) as string[]])
          break
        case 'admin':
          // 管理员级别：需要系统权限
          hasRequiredLevel = hasAnyPermission(userPermissions, Object.values(SYSTEM_PERMISSIONS) as string[])
          break
        default:
          hasRequiredLevel = false
      }
      
      if (!hasRequiredLevel) {
        hideElement(el, 'permission-level')
      }
    } catch (error) {
      console.error('权限级别指令检查失败:', error)
      hideElement(el, 'permission-level')
    }
  },
  
  updated(el: HTMLElement, binding: DirectiveBinding<PermissionLevel>) {
    const { value } = binding
    
    try {
      const userPermissions = getCurrentUserPermissions()
      
      let hasRequiredLevel = false
      
      switch (value) {
        case 'basic':
          hasRequiredLevel = userPermissions.length > 0
          break
        case 'advanced':
          hasRequiredLevel = hasAnyPermission(userPermissions, [...Object.values(MANAGEMENT_PERMISSIONS) as string[], ...Object.values(SYSTEM_PERMISSIONS) as string[]])
          break
        case 'admin':
          hasRequiredLevel = hasAnyPermission(userPermissions, Object.values(SYSTEM_PERMISSIONS) as string[])
          break
        default:
          hasRequiredLevel = false
      }
      
      if (!hasRequiredLevel) {
        hideElement(el, 'permission-level')
      } else {
        showElement(el, 'permission-level')
      }
    } catch (error) {
      console.error('权限级别指令更新失败:', error)
      hideElement(el, 'permission-level')
    }
  }
}

/**
 * 权限指令安装函数
 * @param {App} app - Vue应用实例
 */
export function installPermissionDirectives(app: App): void {
  app.directive('permission', permissionDirective)
  app.directive('role', roleDirective)
  app.directive('auth', authDirective)
  app.directive('permission-level', permissionLevelDirective)
}

/**
 * 默认导出所有指令
 */
export default {
  permission: permissionDirective,
  role: roleDirective,
  auth: authDirective,
  'permission-level': permissionLevelDirective,
  install: installPermissionDirectives
}

// 导出类型
export type {
  UserInfo,
  PermissionValue,
  RoleValue,
  PermissionLevel,
  PermissionModifiers,
  RoleModifiers,
  AuthModifiers
}