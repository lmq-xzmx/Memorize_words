/**
 * 权限指令
 * 提供v-permission、v-role、v-auth等指令用于模板权限控制
 * 根据《用户权限管理系统规范》文档实现
 */

import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  canAccessPage,
  isAuthenticated,
  getCurrentUser
} from '../utils/permission.js'

import {
  getRolePermissions,
  roleHasPermission
} from '../utils/roleDefinitions.js'

/**
 * 获取当前用户权限
 * @returns {Promise<Array>} 用户权限列表
 */
async function getCurrentUserPermissions() {
  try {
    const user = await getCurrentUser()
    if (user && user.role) {
      return getRolePermissions(user.role)
    }
    return []
  } catch (error) {
    console.error('获取用户权限失败:', error)
    return []
  }
}

/**
 * 获取当前用户角色
 * @returns {Promise<string|null>} 用户角色
 */
async function getCurrentUserRole() {
  try {
    const user = await getCurrentUser()
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
function hideElement(el, reason) {
  el.style.display = 'none'
  el.setAttribute(`data-${reason}-hidden`, 'true')
  el.setAttribute('aria-hidden', 'true')
}

/**
 * 显示元素的通用方法
 * @param {HTMLElement} el - DOM元素
 * @param {string} reason - 隐藏原因
 */
function showElement(el, reason) {
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
  async mounted(el, binding) {
    const { value, modifiers } = binding
    
    try {
      let hasRequiredPermission = false
      
      if (modifiers.page) {
        // 页面访问权限检查
        const userPermissions = await getCurrentUserPermissions()
        hasRequiredPermission = canAccessPage(userPermissions, value)
      } else {
        // 功能权限检查
        const userPermissions = await getCurrentUserPermissions()
        
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
  
  async updated(el, binding) {
    const { value, modifiers } = binding
    
    try {
      let hasRequiredPermission = false
      
      if (modifiers.page) {
        // 页面访问权限检查
        const userPermissions = await getCurrentUserPermissions()
        hasRequiredPermission = canAccessPage(userPermissions, value)
      } else {
        // 功能权限检查
        const userPermissions = await getCurrentUserPermissions()
        
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
  async mounted(el, binding) {
    const { value, modifiers } = binding
    
    try {
      const userRole = await getCurrentUserRole()
      let hasRequiredRole = false
      
      if (modifiers.higher) {
        // 检查角色层级
        const { isRoleHigher } = await import('../utils/roleDefinitions.js')
        hasRequiredRole = isRoleHigher(userRole, value)
      } else {
        // 检查角色匹配
        if (Array.isArray(value)) {
          hasRequiredRole = value.includes(userRole)
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
  
  async updated(el, binding) {
    const { value, modifiers } = binding
    
    try {
      const userRole = await getCurrentUserRole()
      let hasRequiredRole = false
      
      if (modifiers.higher) {
        // 检查角色层级
        const { isRoleHigher } = await import('../utils/roleDefinitions.js')
        hasRequiredRole = isRoleHigher(userRole, value)
      } else {
        // 检查角色匹配
        if (Array.isArray(value)) {
          hasRequiredRole = value.includes(userRole)
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
  async mounted(el, binding) {
    const { modifiers } = binding
    
    try {
      const authenticated = await isAuthenticated()
      
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
  
  async updated(el, binding) {
    const { modifiers } = binding
    
    try {
      const authenticated = await isAuthenticated()
      
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
  async mounted(el, binding) {
    const { value } = binding
    
    try {
      const userPermissions = await getCurrentUserPermissions()
      
      let hasRequiredLevel = false
      
      switch (value) {
        case 'basic':
          // 基础级别：有任何权限即可
          hasRequiredLevel = userPermissions.length > 0
          break
        case 'advanced':
          // 高级级别：需要管理或系统权限
          const { MANAGEMENT_PERMISSIONS, SYSTEM_PERMISSIONS } = await import('../utils/permissionConstants.js')
          hasRequiredLevel = hasAnyPermission(userPermissions, [...MANAGEMENT_PERMISSIONS, ...SYSTEM_PERMISSIONS])
          break
        case 'admin':
          // 管理员级别：需要系统权限
          const { SYSTEM_PERMISSIONS: SYS_PERMS } = await import('../utils/permissionConstants.js')
          hasRequiredLevel = hasAnyPermission(userPermissions, SYS_PERMS)
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
  
  async updated(el, binding) {
    const { value } = binding
    
    try {
      const userPermissions = await getCurrentUserPermissions()
      
      let hasRequiredLevel = false
      
      switch (value) {
        case 'basic':
          hasRequiredLevel = userPermissions.length > 0
          break
        case 'advanced':
          const { MANAGEMENT_PERMISSIONS, SYSTEM_PERMISSIONS } = await import('../utils/permissionConstants.js')
          hasRequiredLevel = hasAnyPermission(userPermissions, [...MANAGEMENT_PERMISSIONS, ...SYSTEM_PERMISSIONS])
          break
        case 'admin':
          const { SYSTEM_PERMISSIONS: SYS_PERMS } = await import('../utils/permissionConstants.js')
          hasRequiredLevel = hasAnyPermission(userPermissions, SYS_PERMS)
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
 * @param {Object} app - Vue应用实例
 */
export function installPermissionDirectives(app) {
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