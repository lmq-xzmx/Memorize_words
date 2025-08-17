/**
 * API配置文件
 * 统一管理前端与后端的连接配置
 */

// 环境类型
type Environment = 'development' | 'production'

// API端点接口
interface ApiEndpoints {
  AUTH: {
    LOGIN: string
    REGISTER: string
    VERIFY: string
    LOGOUT: string
    REFRESH: string
    ROLES: string
    ROLE_EXTENSIONS: string
    REGISTER_WITH_EXTENSIONS: string
    USER_CURRENT: string
    USER_INFO: string
  }
  PERMISSIONS: {
    USER_MENU: string
    OPTIMIZED_USER_MENU: string
    CHECK_MENU_PERMISSION: string
    ROLE_DISPLAY_NAME: string
    MENU_HIERARCHY: string
  }
  TEACHING: {
    LEARNING_GOALS: string
    LEARNING_DASHBOARD: string
    GOALS_MANAGEMENT: string
  }
  WORDS: {
    BASE: string
  }
  RESOURCE_AUTH: {
    BASE: string
  }
  ANALYTICS: {
    BASE: string
  }
}

// API配置接口
interface ApiConfig {
  getBaseUrl: () => string
  getBackendBaseURL: () => string
  getBackendHost: () => string
  getWebSocketUrl: () => string
  API_ENDPOINTS: ApiEndpoints
  buildApiUrl: (endpoint: string) => string
  buildPageUrl: (path: string) => string
}

// 获取后端基础URL
export function getApiBaseUrl(): string {
  return (import.meta as any).env.MODE === 'production' ? '/api' : 'http://127.0.0.1:8001/api'
}

// 获取后端完整地址（不包含/api路径）
export function getBaseUrl(): string {
  return (import.meta as any).env.MODE === 'production' ? '' : 'http://127.0.0.1:8001'
}

// 获取后端主机地址（兼容性方法）
export function getBackendHost(): string {
  return (import.meta as any).env.MODE === 'production' ? '' : 'http://127.0.0.1:8001'
}

// 获取后端基础URL（兼容性方法）
export function getBackendBaseURL(): string {
  return (import.meta as any).env.MODE === 'production' ? '/api' : 'http://127.0.0.1:8001/api'
}

// API端点配置
export const API_ENDPOINTS: ApiEndpoints = {
  // 认证相关
  AUTH: {
    LOGIN: '/accounts/api/auth/login/',
    REGISTER: '/accounts/api/auth/register/',
    VERIFY: '/accounts/api/auth/verify/',
    LOGOUT: '/accounts/api/auth/logout/',
    REFRESH: '/accounts/api/auth/refresh/',
    ROLES: '/accounts/api/auth/roles/',
    ROLE_EXTENSIONS: '/accounts/api/auth/role-extensions/',
    REGISTER_WITH_EXTENSIONS: '/accounts/api/auth/register-with-extensions/',
    USER_CURRENT: '/accounts/api/users/current/',
    USER_INFO: '/accounts/api/auth/user/'
  },
  
  // 权限相关
  PERMISSIONS: {
    USER_MENU: '/permissions/api/user-menu-permissions/',
    OPTIMIZED_USER_MENU: '/permissions/optimized/api/user-menu-permissions/',
    CHECK_MENU_PERMISSION: '/permissions/api/check-menu-permission/',
    ROLE_DISPLAY_NAME: '/permissions/api/role-display-name/',
    MENU_HIERARCHY: '/permissions/api/menu-hierarchy/'
  },
  
  // 教学相关
  TEACHING: {
    LEARNING_GOALS: '/teaching/api/learning-goals/',
    LEARNING_DASHBOARD: '/teaching/learning-dashboard/',
    GOALS_MANAGEMENT: '/teaching/goals/'
  },
  
  // 单词相关
  WORDS: {
    BASE: '/words/api'
  },
  
  // 资源认证
  RESOURCE_AUTH: {
    BASE: '/api/resource-auth'
  },
  
  // 分析相关
  ANALYTICS: {
    BASE: '/analytics'
  }
}

// 构建API URL
export function buildApiUrl(endpoint: string): string {
  return `${getApiBaseUrl()}${endpoint}`
}

// 构建页面URL
export function buildPageUrl(path: string): string {
  return `${getBaseUrl()}${path}`
}

// 获取WebSocket URL
export function getWebSocketUrl(): string {
  const protocol = (import.meta as any).env.MODE === 'production' ? 'wss:' : 'ws:'
  const host = (import.meta as any).env.MODE === 'production' ? window.location.host : '127.0.0.1:8001'
  return `${protocol}//${host}/ws/`
}

// API配置对象
export const apiConfig: ApiConfig = {
  getBaseUrl: getBackendHost,
  getBackendBaseURL,
  getBackendHost,
  getWebSocketUrl,
  API_ENDPOINTS,
  buildApiUrl,
  buildPageUrl
}

// 默认导出
const defaultConfig = {
  getBackendBaseURL,
  getBackendHost,
  getWebSocketUrl,
  API_ENDPOINTS,
  buildApiUrl,
  buildPageUrl
}

export default defaultConfig

// 导出类型
export type { ApiEndpoints, ApiConfig, Environment }