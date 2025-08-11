/**
 * 权限控制混入
 * 为Vue组件提供权限检查功能
 */

import { 
  hasPermission, 
  canAccessPage, 
  getCurrentUser, 
  isAuthenticated,
  getRoleDisplayName,
  getAccessibleMenus,
  permissionWatcher
} from '../utils/permission.js'

export default {
  data() {
    return {
      currentUser: null,
      userRole: null,
      isUserAuthenticated: false
    }
  },
  
  computed: {
    /**
     * 获取用户角色显示名称
     */
    roleDisplayName() {
      return this.userRole ? getRoleDisplayName(this.userRole) : '未知角色'
    },
    
    /**
     * 获取用户可访问的菜单
     */
    accessibleMenus() {
      return this.userRole ? getAccessibleMenus(this.userRole) : []
    },
    
    /**
     * 检查是否为管理员
     */
    isAdmin() {
      return this.userRole === 'admin'
    },
    
    /**
     * 检查是否为教师角色（包括各级教师）
     */
    isTeacher() {
      return ['teacher', 'dean', 'academic_director', 'research_leader'].includes(this.userRole)
    },
    
    /**
     * 检查是否为学生
     */
    isStudent() {
      return this.userRole === 'student'
    },
    
    /**
     * 检查是否为家长
     */
    isParent() {
      return this.userRole === 'parent'
    }
  },
  
  methods: {
    /**
     * 检查用户是否拥有指定权限
     * @param {string} permission - 权限名称
     * @returns {boolean} 是否拥有权限
     */
    $hasPermission(permission) {
      return hasPermission(this.userRole, permission)
    },
    
    /**
     * 检查用户是否可以访问指定页面
     * @param {string} path - 页面路径
     * @returns {boolean} 是否可以访问
     */
    $canAccessPage(path) {
      return canAccessPage(this.userRole, path)
    },
    
    /**
     * 检查用户是否已认证
     * @returns {boolean} 是否已认证
     */
    $isAuthenticated() {
      return isAuthenticated()
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
      // 这里可以集成具体的UI组件库的提示组件
      console.error(message)
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
     * 更新用户信息
     */
    $updateUserInfo() {
      this.currentUser = getCurrentUser()
      this.userRole = this.currentUser?.role || null
      this.isUserAuthenticated = isAuthenticated()
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
     * 导航到指定页面（带权限检查）
     * @param {string} path - 页面路径
     * @param {Object} params - 路由参数
     */
    $navigateWithPermission(path, params = {}) {
      if (this.$canAccessPage(path)) {
        this.$router.push({ path, ...params })
      } else {
        this.$showError(`您没有权限访问页面：${path}`)
      }
    },
    
    /**
     * 检查功能权限并执行操作
     * @param {string} permission - 权限名称
     * @param {Function} action - 要执行的操作
     * @param {string} feature - 功能名称（用于错误提示）
     */
    $executeWithPermission(permission, action, feature = '此功能') {
      if (this.$hasPermission(permission)) {
        try {
          return action()
        } catch (error) {
          console.error(`执行${feature}时发生错误:`, error)
          this.$showError(`执行${feature}时发生错误`)
        }
      } else {
        this.$showError(`您没有权限使用${feature}`)
      }
    }
  },
  
  created() {
    // 初始化用户信息
    this.$updateUserInfo()
    
    // 监听权限变更
    permissionWatcher.addListener(this.$onPermissionChange)
  },
  
  beforeUnmount() {
    // 清理权限变更监听器
    permissionWatcher.removeListener(this.$onPermissionChange)
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