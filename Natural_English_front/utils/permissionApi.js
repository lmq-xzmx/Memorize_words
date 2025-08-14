/**
 * 优化后的权限检查API工具
 * 提供与后端权限检查接口的交互功能
 */

import axios from 'axios'

// API基础URL - 使用优化后的权限接口
const API_BASE_URL = '/permissions/optimized/api'

// 创建axios实例
const permissionApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
permissionApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理通用错误
permissionApi.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('权限API请求失败:', error)
    
    // 处理认证失败
    if (error.response?.status === 401) {
      // 清除本地存储的认证信息
      localStorage.removeItem('auth_token')
      sessionStorage.removeItem('auth_token')
      
      // 跳转到登录页面
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

/**
 * 权限检查API类
 */
class PermissionAPI {
  /**
   * 统一权限检查
   * @param {string} resourceType 资源类型 (menu, learning_goal, learning_plan)
   * @param {string} action 操作类型
   * @param {object} context 上下文信息
   * @returns {Promise<object>}
   */
  static async checkPermission(resourceType, action, context = {}) {
    try {
      const response = await permissionApi.post('/check/', {
        resource_type: resourceType,
        action: action,
        context: context
      })
      return response
    } catch (error) {
      console.error('权限检查失败:', error)
      return {
        success: false,
        has_permission: false,
        error: error.message
      }
    }
  }
  
  /**
   * 获取用户权限信息
   * @returns {Promise<object>}
   */
  static async getUserPermissions() {
    try {
      const response = await permissionApi.get('/user-permissions/')
      return response
    } catch (error) {
      console.error('获取用户权限失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
  
  /**
   * 检查菜单权限
   * @param {string} menuId 菜单ID
   * @returns {Promise<object>}
   */
  static async checkMenuPermission(menuId) {
    try {
      const response = await permissionApi.post('/check-menu/', {
        menu_id: menuId
      })
      return response
    } catch (error) {
      console.error('菜单权限检查失败:', error)
      return {
        success: false,
        has_permission: false,
        error: error.message
      }
    }
  }
  
  /**
   * 检查学习目标权限
   * @param {string} action 操作类型
   * @param {number} goalId 学习目标ID（可选）
   * @param {object} context 上下文信息
   * @returns {Promise<object>}
   */
  static async checkLearningGoalPermission(action, goalId = null, context = {}) {
    try {
      const data = {
        action: action,
        context: context
      }
      
      if (goalId) {
        data.goal_id = goalId
      }
      
      const response = await permissionApi.post('/check-learning-goal/', data)
      return response
    } catch (error) {
      console.error('学习目标权限检查失败:', error)
      return {
        success: false,
        has_permission: false,
        error: error.message
      }
    }
  }
  
  /**
   * 检查学习计划权限
   * @param {string} action 操作类型
   * @param {number} planId 学习计划ID（可选）
   * @param {object} context 上下文信息
   * @returns {Promise<object>}
   */
  static async checkLearningPlanPermission(action, planId = null, context = {}) {
    try {
      const data = {
        action: action,
        context: context
      }
      
      if (planId) {
        data.plan_id = planId
      }
      
      const response = await permissionApi.post('/check-learning-plan/', data)
      return response
    } catch (error) {
      console.error('学习计划权限检查失败:', error)
      return {
        success: false,
        has_permission: false,
        error: error.message
      }
    }
  }
  
  /**
   * 清除权限缓存
   * @returns {Promise<object>}
   */
  static async clearPermissionCache() {
    try {
      const response = await permissionApi.post('/clear-cache/')
      return response
    } catch (error) {
      console.error('清除权限缓存失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
  
  /**
   * 获取权限统计信息（仅管理员）
   * @returns {Promise<object>}
   */
  static async getPermissionStats() {
    try {
      const response = await permissionApi.get('/stats/')
      return response
    } catch (error) {
      console.error('获取权限统计失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
}

/**
 * 便捷的权限检查函数
 */

/**
 * 检查是否可以访问菜单
 * @param {string} menuId 菜单ID
 * @returns {Promise<boolean>}
 */
export async function canAccessMenu(menuId) {
  const result = await PermissionAPI.checkMenuPermission(menuId)
  return result.success && result.has_permission
}

/**
 * 检查学习目标权限
 * @param {string} action 操作类型
 * @param {object} goal 学习目标对象（可选）
 * @returns {Promise<boolean>}
 */
export async function canManageLearningGoal(action, goal = null) {
  const context = {}
  let goalId = null
  
  if (goal) {
    goalId = goal.id
    context.is_own = goal.is_own || false
    context.is_personal = goal.is_personal || false
    context.is_class_goal = goal.is_class_goal || false
  }
  
  const result = await PermissionAPI.checkLearningGoalPermission(action, goalId, context)
  return result.success && result.has_permission
}

/**
 * 检查学习计划权限
 * @param {string} action 操作类型
 * @param {object} plan 学习计划对象（可选）
 * @returns {Promise<boolean>}
 */
export async function canManageLearningPlan(action, plan = null) {
  const context = {}
  let planId = null
  
  if (plan) {
    planId = plan.id
    context.is_own = plan.is_own || false
    context.is_personal = plan.is_personal || false
    context.is_class_plan = plan.is_class_plan || false
  }
  
  const result = await PermissionAPI.checkLearningPlanPermission(action, planId, context)
  return result.success && result.has_permission
}

/**
 * 批量检查权限
 * @param {Array} permissions 权限数组 [{resource, action, context}]
 * @returns {Promise<Array>} 权限检查结果数组
 */
export async function checkMultiplePermissions(permissions) {
  const promises = permissions.map(perm => 
    PermissionAPI.checkPermission(perm.resource, perm.action, perm.context || {})
  )
  
  try {
    const results = await Promise.all(promises)
    return results.map((result, index) => ({
      ...permissions[index],
      has_permission: result.success && result.has_permission,
      success: result.success,
      error: result.error
    }))
  } catch (error) {
    console.error('批量权限检查失败:', error)
    return permissions.map(perm => ({
      ...perm,
      has_permission: false,
      success: false,
      error: error.message
    }))
  }
}

/**
 * 权限检查装饰器函数
 * @param {string} resource 资源类型
 * @param {string} action 操作类型
 * @param {object} context 上下文信息
 * @returns {Function} 装饰器函数
 */
export function requirePermission(resource, action, context = {}) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value
    
    descriptor.value = async function(...args) {
      const result = await PermissionAPI.checkPermission(resource, action, context)
      
      if (!result.success || !result.has_permission) {
        throw new Error(`权限不足：无法执行 ${action} 操作`)
      }
      
      return originalMethod.apply(this, args)
    }
    
    return descriptor
  }
}

export default PermissionAPI
export { PermissionAPI }