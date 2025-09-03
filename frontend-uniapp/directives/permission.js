/**
 * 权限指令
 * 用于在模板中控制元素的显示和隐藏
 */

import store from '@/store'

/**
 * 检查权限
 * @param {string|Array} value 权限值
 * @param {string} type 权限类型 (permission|role|menu)
 * @returns {boolean} 是否有权限
 */
function checkPermission(value, type = 'permission') {
  const userInfo = store.state.user?.userInfo
  const isLoggedIn = store.state.user?.isLoggedIn
  const currentRole = store.state.permission?.currentRole
  const userMenuPermissions = store.state.permission?.userMenuPermissions
  
  // 未登录用户没有权限
  if (!isLoggedIn) {
    return false
  }
  
  switch (type) {
    case 'role':
      return checkRole(value, currentRole)
    case 'menu':
      return checkMenuPermission(value, userMenuPermissions)
    case 'permission':
    default:
      return checkUserPermission(value, userMenuPermissions)
  }
}

/**
 * 检查角色权限
 * @param {string|Array} roles 角色
 * @param {string} currentRole 当前角色
 * @returns {boolean} 是否有权限
 */
function checkRole(roles, currentRole) {
  if (!currentRole) {
    return false
  }
  
  if (Array.isArray(roles)) {
    return roles.includes(currentRole)
  }
  
  return currentRole === roles
}

/**
 * 检查用户权限
 * @param {string|Array} permissions 权限
 * @param {Array} userPermissions 用户权限列表
 * @returns {boolean} 是否有权限
 */
function checkUserPermission(permissions, userPermissions) {
  if (!userPermissions || userPermissions.length === 0) {
    return false
  }
  
  const permissionList = Array.isArray(permissions) ? permissions : [permissions]
  
  return permissionList.some(permission => 
    userPermissions.some(p => 
      p.permission === permission || p.code === permission
    )
  )
}

/**
 * 检查菜单权限
 * @param {string|Array} menuIds 菜单ID
 * @param {Array} userPermissions 用户权限列表
 * @returns {boolean} 是否有权限
 */
function checkMenuPermission(menuIds, userPermissions) {
  if (!userPermissions || userPermissions.length === 0) {
    return false
  }
  
  const menuList = Array.isArray(menuIds) ? menuIds : [menuIds]
  
  return menuList.some(menuId => 
    userPermissions.some(p => p.menu_id === menuId)
  )
}

/**
 * 权限指令定义
 */
const permissionDirective = {
  // Vue 3 指令生命周期
  mounted(el, binding) {
    checkAndToggleElement(el, binding)
  },
  
  updated(el, binding) {
    checkAndToggleElement(el, binding)
  },
  
  // Vue 2 兼容
  bind(el, binding) {
    checkAndToggleElement(el, binding)
  },
  
  update(el, binding) {
    checkAndToggleElement(el, binding)
  }
}

/**
 * 检查权限并切换元素显示状态
 * @param {Element} el DOM元素
 * @param {Object} binding 指令绑定对象
 */
function checkAndToggleElement(el, binding) {
  const { value, arg, modifiers } = binding
  
  // 确定权限类型
  const type = arg || 'permission'
  
  // 检查权限
  const hasPermission = checkPermission(value, type)
  
  // 根据权限控制元素
  if (modifiers.hide) {
    // 使用 v-permission.hide 时，有权限则隐藏
    toggleElement(el, !hasPermission)
  } else {
    // 默认行为，有权限则显示
    toggleElement(el, hasPermission)
  }
}

/**
 * 切换元素显示状态
 * @param {Element} el DOM元素
 * @param {boolean} show 是否显示
 */
function toggleElement(el, show) {
  if (show) {
    // 显示元素
    el.style.display = el._originalDisplay || ''
    el.style.visibility = 'visible'
  } else {
    // 隐藏元素
    if (!el._originalDisplay) {
      el._originalDisplay = el.style.display || ''
    }
    el.style.display = 'none'
    el.style.visibility = 'hidden'
  }
}

/**
 * 角色指令
 */
const roleDirective = {
  mounted(el, binding) {
    const hasRole = checkRole(binding.value, store.state.permission?.currentRole)
    toggleElement(el, hasRole)
  },
  
  updated(el, binding) {
    const hasRole = checkRole(binding.value, store.state.permission?.currentRole)
    toggleElement(el, hasRole)
  },
  
  // Vue 2 兼容
  bind(el, binding) {
    const hasRole = checkRole(binding.value, store.state.permission?.currentRole)
    toggleElement(el, hasRole)
  },
  
  update(el, binding) {
    const hasRole = checkRole(binding.value, store.state.permission?.currentRole)
    toggleElement(el, hasRole)
  }
}

/**
 * 注册权限指令
 * @param {Object} app Vue应用实例
 */
export function registerPermissionDirectives(app) {
  // 权限指令
  app.directive('permission', permissionDirective)
  
  // 角色指令
  app.directive('role', roleDirective)
  
  // 管理员指令
  app.directive('admin', {
    mounted(el, binding) {
      const isAdmin = checkRole(['admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isAdmin)
    },
    updated(el, binding) {
      const isAdmin = checkRole(['admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isAdmin)
    },
    // Vue 2 兼容
    bind(el, binding) {
      const isAdmin = checkRole(['admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isAdmin)
    },
    update(el, binding) {
      const isAdmin = checkRole(['admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isAdmin)
    }
  })
  
  // 教师指令
  app.directive('teacher', {
    mounted(el, binding) {
      const isTeacher = checkRole(['teacher', 'admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isTeacher)
    },
    updated(el, binding) {
      const isTeacher = checkRole(['teacher', 'admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isTeacher)
    },
    // Vue 2 兼容
    bind(el, binding) {
      const isTeacher = checkRole(['teacher', 'admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isTeacher)
    },
    update(el, binding) {
      const isTeacher = checkRole(['teacher', 'admin', 'super_admin'], store.state.permission?.currentRole)
      toggleElement(el, isTeacher)
    }
  })
  
  // 学生指令
  app.directive('student', {
    mounted(el, binding) {
      const isStudent = checkRole('student', store.state.permission?.currentRole)
      toggleElement(el, isStudent)
    },
    updated(el, binding) {
      const isStudent = checkRole('student', store.state.permission?.currentRole)
      toggleElement(el, isStudent)
    },
    // Vue 2 兼容
    bind(el, binding) {
      const isStudent = checkRole('student', store.state.permission?.currentRole)
      toggleElement(el, isStudent)
    },
    update(el, binding) {
      const isStudent = checkRole('student', store.state.permission?.currentRole)
      toggleElement(el, isStudent)
    }
  })
}

/**
 * 导出权限检查函数
 */
export {
  checkPermission,
  checkRole,
  checkUserPermission,
  checkMenuPermission
}

/**
 * 默认导出
 */
export default {
  install: registerPermissionDirectives
}