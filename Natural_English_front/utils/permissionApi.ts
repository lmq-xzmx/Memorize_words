/**
 * 优化后的权限检查API工具
 * 提供与后端权限检查接口的交互功能
 */

import * as axiosModule from 'axios'
import { type AxiosInstance, type AxiosResponse, type AxiosError } from 'axios'

// 获取axios实例
const axios = (axiosModule as any).default || axiosModule

// 权限检查相关类型定义
interface PermissionCheckRequest {
  resource_type: string;
  action: string;
  context: Record<string, any>;
}

interface PermissionCheckResponse {
  success: boolean;
  has_permission: boolean;
  error?: string;
  message?: string;
}

interface UserPermissionsResponse {
  success: boolean;
  permissions?: string[];
  roles?: string[];
  error?: string;
}

interface MenuPermissionRequest {
  menu_id: string;
}

interface LearningGoalPermissionRequest {
  action: string;
  goal_id?: number;
  context: Record<string, any>;
}

interface LearningPlanPermissionRequest {
  action: string;
  plan_id?: number;
  context: Record<string, any>;
}

interface PermissionStatsResponse {
  success: boolean;
  stats?: {
    total_checks: number;
    cache_hits: number;
    cache_misses: number;
    hit_rate: string;
  };
  error?: string;
}

interface LearningGoal {
  id: number;
  is_own?: boolean;
  is_personal?: boolean;
  is_class_goal?: boolean;
}

interface LearningPlan {
  id: number;
  is_own?: boolean;
  is_personal?: boolean;
  is_class_plan?: boolean;
}

interface PermissionItem {
  resource: string;
  action: string;
  context?: Record<string, any>;
}

interface PermissionCheckResult extends PermissionItem {
  has_permission: boolean;
  success: boolean;
  error?: string;
}

// API基础URL - 使用优化后的权限接口
const API_BASE_URL = '/permissions/optimized/api'

// 创建axios实例
const permissionApi: AxiosInstance = axios.create({
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
      config.headers!.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理通用错误
permissionApi.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error: AxiosError) => {
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
   */
  static async checkPermission(
    resourceType: string, 
    action: string, 
    context: Record<string, any> = {}
  ): Promise<PermissionCheckResponse> {
    try {
      const response = await permissionApi.post('/check/', {
        resource_type: resourceType,
        action: action,
        context: context
      })
      return response.data
    } catch (error: any) {
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
   */
  static async getUserPermissions(): Promise<UserPermissionsResponse> {
    try {
      const response = await permissionApi.get('/user-permissions/')
      return response.data
    } catch (error: any) {
      console.error('获取用户权限失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
  
  /**
   * 检查菜单权限
   */
  static async checkMenuPermission(menuId: string): Promise<PermissionCheckResponse> {
    try {
      const response = await permissionApi.post('/check-menu/', {
        menu_id: menuId
      })
      return response.data
    } catch (error: any) {
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
   */
  static async checkLearningGoalPermission(
    action: string, 
    goalId: number | null = null, 
    context: Record<string, any> = {}
  ): Promise<PermissionCheckResponse> {
    try {
      const data: LearningGoalPermissionRequest = {
        action: action,
        context: context
      }
      
      if (goalId) {
        data.goal_id = goalId
      }
      
      const response = await permissionApi.post('/check-learning-goal/', data)
      return response.data
    } catch (error: any) {
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
   */
  static async checkLearningPlanPermission(
    action: string, 
    planId: number | null = null, 
    context: Record<string, any> = {}
  ): Promise<PermissionCheckResponse> {
    try {
      const data: LearningPlanPermissionRequest = {
        action: action,
        context: context
      }
      
      if (planId) {
        data.plan_id = planId
      }
      
      const response = await permissionApi.post('/check-learning-plan/', data)
      return response.data
    } catch (error: any) {
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
   */
  static async clearPermissionCache(): Promise<PermissionCheckResponse> {
    try {
      const response = await permissionApi.post('/clear-cache/')
      return response.data
    } catch (error: any) {
      console.error('清除权限缓存失败:', error)
      return {
        success: false,
        has_permission: false,
        error: error.message
      }
    }
  }
  
  /**
   * 获取权限统计信息（仅管理员）
   */
  static async getPermissionStats(): Promise<PermissionStatsResponse> {
    try {
      const response = await permissionApi.get('/stats/')
      return response.data
    } catch (error: any) {
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
 */
export async function canAccessMenu(menuId: string): Promise<boolean> {
  const result = await PermissionAPI.checkMenuPermission(menuId)
  return result.success && result.has_permission
}

/**
 * 检查学习目标权限
 */
export async function canManageLearningGoal(action: string, goal: LearningGoal | null = null): Promise<boolean> {
  const context: Record<string, any> = {}
  let goalId: number | null = null
  
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
 */
export async function canManageLearningPlan(action: string, plan: LearningPlan | null = null): Promise<boolean> {
  const context: Record<string, any> = {}
  let planId: number | null = null
  
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
 */
export async function checkMultiplePermissions(permissions: PermissionItem[]): Promise<PermissionCheckResult[]> {
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
  } catch (error: any) {
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
 */
export function requirePermission(
  resource: string, 
  action: string, 
  context: Record<string, any> = {}
): (target: any, propertyKey: string, descriptor: PropertyDescriptor) => PropertyDescriptor {
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor): PropertyDescriptor {
    const originalMethod = descriptor.value
    
    descriptor.value = async function(...args: any[]) {
      const result = await PermissionAPI.checkPermission(resource, action, context)
      
      if (!result.success || !result.has_permission) {
        throw new Error(`权限不足：无法执行 ${action} 操作`)
      }
      
      return originalMethod.apply(this, args)
    }
    
    return descriptor
  }
}

export type {
  PermissionCheckRequest,
  PermissionCheckResponse,
  UserPermissionsResponse,
  MenuPermissionRequest,
  LearningGoalPermissionRequest,
  LearningPlanPermissionRequest,
  PermissionStatsResponse,
  LearningGoal,
  LearningPlan,
  PermissionItem,
  PermissionCheckResult
}

export default PermissionAPI
export { PermissionAPI }