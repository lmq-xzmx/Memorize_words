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
import { createPermissionChecker, hasPermission as optimizedHasPermission } from '../utils/permissionUtils.js'

export default {
  data() {
    return {
      currentUser: null,
      userRole: null,
      isUserAuthenticated: false,
      permissionChecker: null
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
     * 优化后的权限检查器实例
     */
    optimizedPermissionChecker() {
      return this.currentUser ? createPermissionChecker(this.currentUser) : null
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
     * 权限检查方法
     * @param {string} permission 权限标识
     * @returns {boolean}
     */
    $hasPermission(permission) {
      return hasPermission(this.userRole, permission)
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
      this.userRole = this.currentUser?.role
      this.isUserAuthenticated = isAuthenticated()
      // 更新权限检查器
      this.permissionChecker = this.currentUser ? createPermissionChecker(this.currentUser) : null
    },
    
    /**
     * 清除权限缓存
     */
    $clearPermissionCache() {
      if (this.optimizedPermissionChecker) {
        this.optimizedPermissionChecker.clearUserCache()
      }
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