/**
 * API权限拦截器
 * 在请求层面验证权限并处理错误
 */

import axios from 'axios'
import type { AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { PermissionCache } from '@/services/permissionCacheService'
import { ElMessage, ElMessageBox } from 'element-plus'
import router from '@/router'

// API权限配置接口
interface ApiPermissionConfig {
  permission?: string | string[]
  requiredRole?: string
  skipPermissionCheck?: boolean
  fallbackBehavior?: 'redirect' | 'message' | 'silent'
  customErrorHandler?: (error: any) => void
}

// 权限错误类
class PermissionError extends Error {
  constructor(
    message: string,
    public code: string = 'PERMISSION_DENIED',
    public statusCode: number = 403
  ) {
    super(message)
    this.name = 'PermissionError'
  }
}

// 获取用户信息的辅助函数
function getUserInfo(): { id: string; role: string } | null {
  try {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const id = (userInfo.id || userInfo.user_id)?.toString()
    const role = userInfo.role || userInfo.user_role
    
    if (id && role) {
      return { id, role }
    }
    return null
  } catch {
    return null
  }
}

// API权限映射配置
const API_PERMISSION_MAP: Record<string, ApiPermissionConfig> = {
  // 用户管理相关
  'GET:/api/users': { permission: 'user.list.view' },
  'POST:/api/users': { permission: 'user.create' },
  'PUT:/api/users': { permission: 'user.update' },
  'DELETE:/api/users': { permission: 'user.delete' },
  
  // 角色管理相关
  'GET:/api/roles': { permission: 'role.list.view' },
  'POST:/api/roles': { permission: 'role.create' },
  'PUT:/api/roles': { permission: 'role.update' },
  'DELETE:/api/roles': { permission: 'role.delete' },
  
  // 权限管理相关
  'GET:/api/permissions': { permission: 'permission.list.view' },
  'POST:/api/permissions': { permission: 'permission.create' },
  'PUT:/api/permissions': { permission: 'permission.update' },
  'DELETE:/api/permissions': { permission: 'permission.delete' },
  
  // 学生相关
  'GET:/api/students': { permission: 'student.list.view' },
  'POST:/api/students': { permission: 'student.create' },
  'PUT:/api/students': { permission: 'student.update' },
  'DELETE:/api/students': { permission: 'student.delete' },
  
  // 教师相关
  'GET:/api/teachers': { permission: 'teacher.list.view' },
  'POST:/api/teachers': { permission: 'teacher.create' },
  'PUT:/api/teachers': { permission: 'teacher.update' },
  'DELETE:/api/teachers': { permission: 'teacher.delete' },
  
  // 班级管理
  'GET:/api/classes': { permission: 'class.list.view' },
  'POST:/api/classes': { permission: 'class.create' },
  'PUT:/api/classes': { permission: 'class.update' },
  'DELETE:/api/classes': { permission: 'class.delete' },
  
  // 管理员专用接口
  'GET:/api/admin': { requiredRole: 'admin' },
  'POST:/api/admin': { requiredRole: 'admin' },
  
  // 公开接口（跳过权限检查）
  'POST:/api/auth/login': { skipPermissionCheck: true },
  'POST:/api/auth/register': { skipPermissionCheck: true },
  'POST:/api/auth/logout': { skipPermissionCheck: true },
  'GET:/api/public': { skipPermissionCheck: true }
}

// 生成API权限键
function getApiPermissionKey(method: string, url: string): string {
  // 移除查询参数和片段
  const cleanUrl = url.split('?')[0].split('#')[0]
  return `${method.toUpperCase()}:${cleanUrl}`
}

// 检查API权限
async function checkApiPermission(
  config: AxiosRequestConfig,
  permissionConfig: ApiPermissionConfig
): Promise<boolean> {
  const userInfo = getUserInfo()
  
  if (!userInfo) {
    console.warn('[ApiInterceptor] 无法获取用户信息')
    return false
  }
  
  const { id: userId, role: userRole } = userInfo
  
  // 检查角色权限
  if (permissionConfig.requiredRole) {
    if (userRole !== permissionConfig.requiredRole) {
      console.warn(`[ApiInterceptor] 角色权限不足: 需要 ${permissionConfig.requiredRole}, 当前 ${userRole}`)
      return false
    }
  }
  
  // 检查具体权限
  if (permissionConfig.permission) {
    const permissions = Array.isArray(permissionConfig.permission) 
      ? permissionConfig.permission 
      : [permissionConfig.permission]
    
    try {
      const results = await Promise.all(
        permissions.map(permission => 
          PermissionCache.checkComponent(permission, userId)
        )
      )
      
      // 默认需要所有权限都满足
      const hasPermission = results.every(result => result)
      
      if (!hasPermission) {
        console.warn(`[ApiInterceptor] API权限不足: ${permissions.join(', ')}`)
        return false
      }
    } catch (error: any) {
      console.error('[ApiInterceptor] 权限检查失败:', error)
      return false
    }
  }
  
  return true
}

// 处理权限错误
function handlePermissionError(
  error: PermissionError,
  config: AxiosRequestConfig,
  permissionConfig?: ApiPermissionConfig
): void {
  const fallbackBehavior = permissionConfig?.fallbackBehavior || 'message'
  
  // 自定义错误处理器优先
  if (permissionConfig?.customErrorHandler) {
    permissionConfig.customErrorHandler(error)
    return
  }
  
  switch (fallbackBehavior) {
    case 'redirect':
      ElMessage.error('权限不足，即将跳转到登录页')
      setTimeout(() => {
        router.push('/login')
      }, 1500)
      break
      
    case 'message':
      ElMessage.error(error.message || '权限不足，无法执行此操作')
      break
      
    case 'silent':
      console.warn('[ApiInterceptor] 权限不足（静默处理）:', error.message)
      break
      
    default:
      ElMessage.error('权限不足，无法执行此操作')
  }
}

// 请求拦截器
const requestInterceptor = async (config: InternalAxiosRequestConfig): Promise<InternalAxiosRequestConfig> => {
  const method = config.method || 'GET'
  const url = config.url || ''
  
  // 跳过非API请求
  if (!url.startsWith('/api/')) {
    return config
  }
  
  const apiKey = getApiPermissionKey(method, url)
  const permissionConfig = API_PERMISSION_MAP[apiKey]
  
  // 如果没有配置权限要求，允许通过
  if (!permissionConfig) {
    return config
  }
  
  // 跳过权限检查的接口
  if (permissionConfig.skipPermissionCheck) {
    return config
  }
  
  // 检查权限
  try {
    const hasPermission = await checkApiPermission(config, permissionConfig)
    
    if (!hasPermission) {
      const error = new PermissionError(
        `API权限不足: ${method} ${url}`,
        'API_PERMISSION_DENIED',
        403
      )
      
      // 处理权限错误
      handlePermissionError(error, config, permissionConfig)
      
      // 抛出错误以阻止请求
      throw error
    }
    
    // 添加权限检查标记
    if (!config.headers) {
      config.headers = {} as any
    }
    config.headers['X-Permission-Checked'] = 'true'
    config.headers['X-User-Id'] = getUserInfo()?.id || ''
    config.headers['X-User-Role'] = getUserInfo()?.role || ''
    
    console.log(`[ApiInterceptor] 权限检查通过: ${method} ${url}`)
    
  } catch (error) {
    if (error instanceof PermissionError) {
      throw error
    }
    
    console.error('[ApiInterceptor] 权限检查异常:', error)
    const errorData = (error as any).response?.data || {}
    const errorMessage = errorData.message || errorData.error || (error as any).message || '未知错误'
    throw new PermissionError(
      `权限检查失败: ${errorMessage}`,
      'PERMISSION_CHECK_FAILED',
      500
    )
  }
  
  return config
}

// 响应拦截器
const responseInterceptor = {
  success: (response: AxiosResponse): AxiosResponse => {
    // 检查响应中的权限更新信息
    const permissionUpdate = response.headers['x-permission-update']
    if (permissionUpdate) {
      try {
        const updateInfo = JSON.parse(permissionUpdate)
        console.log('[ApiInterceptor] 检测到权限更新:', updateInfo)
        
        // 触发权限缓存刷新
        const userInfo = getUserInfo()
        if (userInfo) {
          PermissionCache.refreshUser(userInfo.id)
        }
      } catch (error) {
        console.warn('[ApiInterceptor] 解析权限更新信息失败:', error)
      }
    }
    
    return response
  },
  
  error: (error: AxiosError): Promise<AxiosError> => {
    // 处理权限相关的HTTP错误
    if (error.response?.status === 403) {
      const errorData = error.response.data as any || {}
      const message = errorData.message || '权限不足'
      ElMessage.error(message)
      
      // 如果是权限不足，可能需要刷新权限缓存
      const userInfo = getUserInfo()
      if (userInfo) {
        PermissionCache.refreshUser(userInfo.id)
      }
    } else if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      
      // 清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      PermissionCache.clear()
      
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    }
    
    return Promise.reject(error)
  }
}

// API权限拦截器类
export class ApiPermissionInterceptor {
  private static instance: ApiPermissionInterceptor
  private isInstalled = false
  private requestInterceptorId?: number
  private responseInterceptorId?: number
  
  private constructor() {}
  
  static getInstance(): ApiPermissionInterceptor {
    if (!ApiPermissionInterceptor.instance) {
      ApiPermissionInterceptor.instance = new ApiPermissionInterceptor()
    }
    return ApiPermissionInterceptor.instance
  }
  
  /**
   * 安装拦截器
   */
  install(axiosInstance = axios): void {
    if (this.isInstalled) {
      console.warn('[ApiPermissionInterceptor] 拦截器已安装')
      return
    }
    
    // 安装请求拦截器
    this.requestInterceptorId = axiosInstance.interceptors.request.use(
      requestInterceptor,
      (error) => Promise.reject(error)
    )
    
    // 安装响应拦截器
    this.responseInterceptorId = axiosInstance.interceptors.response.use(
      responseInterceptor.success,
      responseInterceptor.error
    )
    
    this.isInstalled = true
    console.log('[ApiPermissionInterceptor] 拦截器安装完成')
  }
  
  /**
   * 卸载拦截器
   */
  uninstall(axiosInstance = axios): void {
    if (!this.isInstalled) {
      return
    }
    
    if (this.requestInterceptorId !== undefined) {
      axiosInstance.interceptors.request.eject(this.requestInterceptorId)
    }
    
    if (this.responseInterceptorId !== undefined) {
      axiosInstance.interceptors.response.eject(this.responseInterceptorId)
    }
    
    this.isInstalled = false
    this.requestInterceptorId = undefined
    this.responseInterceptorId = undefined
    
    console.log('[ApiPermissionInterceptor] 拦截器卸载完成')
  }
  
  /**
   * 添加API权限配置
   */
  addPermissionConfig(apiKey: string, config: ApiPermissionConfig): void {
    API_PERMISSION_MAP[apiKey] = config
    console.log(`[ApiPermissionInterceptor] 添加权限配置: ${apiKey}`, config)
  }
  
  /**
   * 批量添加API权限配置
   */
  addPermissionConfigs(configs: Record<string, ApiPermissionConfig>): void {
    Object.assign(API_PERMISSION_MAP, configs)
    console.log('[ApiPermissionInterceptor] 批量添加权限配置:', Object.keys(configs))
  }
  
  /**
   * 移除API权限配置
   */
  removePermissionConfig(apiKey: string): void {
    delete API_PERMISSION_MAP[apiKey]
    console.log(`[ApiPermissionInterceptor] 移除权限配置: ${apiKey}`)
  }
  
  /**
   * 获取当前权限配置
   */
  getPermissionConfigs(): Record<string, ApiPermissionConfig> {
    return { ...API_PERMISSION_MAP }
  }
  
  /**
   * 手动检查API权限
   */
  async checkPermission(method: string, url: string): Promise<boolean> {
    const apiKey = getApiPermissionKey(method, url)
    const permissionConfig = API_PERMISSION_MAP[apiKey]
    
    if (!permissionConfig || permissionConfig.skipPermissionCheck) {
      return true
    }
    
    return await checkApiPermission({ method, url }, permissionConfig)
  }
}

// 创建单例实例
export const apiPermissionInterceptor = ApiPermissionInterceptor.getInstance()

// 便捷安装函数
export function installApiPermissionInterceptor(axiosInstance = axios): void {
  apiPermissionInterceptor.install(axiosInstance)
}

// 便捷卸载函数
export function uninstallApiPermissionInterceptor(axiosInstance = axios): void {
  apiPermissionInterceptor.uninstall(axiosInstance)
}

// 在开发环境下暴露到全局对象
if (process.env.NODE_ENV === 'development') {
  const globalWindow = window as any
  globalWindow.apiPermissionInterceptor = apiPermissionInterceptor
  globalWindow.ApiPermissionInterceptor = ApiPermissionInterceptor
  globalWindow.installApiPermissionInterceptor = installApiPermissionInterceptor
  globalWindow.uninstallApiPermissionInterceptor = uninstallApiPermissionInterceptor
}

// 导出类型
export type { ApiPermissionConfig, PermissionError }

// 默认导出
export default apiPermissionInterceptor