/**
 * API配置文件
 * 统一管理前端与后端的连接配置
 */

// 获取后端基础URL
export function getApiBaseUrl() {
  return import.meta.env.MODE === 'production' ? '/api' : 'http://127.0.0.1:8000/api'
}

// 获取后端完整地址（不包含/api路径）
export function getBaseUrl() {
  return import.meta.env.MODE === 'production' ? '' : 'http://127.0.0.1:8000'
}

// 获取后端主机地址（兼容性方法）
export function getBackendHost() {
  return import.meta.env.MODE === 'production' ? '' : 'http://127.0.0.1:8000'
}

// 获取后端基础URL（兼容性方法）
export function getBackendBaseURL() {
  return import.meta.env.MODE === 'production' ? '/api' : 'http://127.0.0.1:8000/api'
}

// API端点配置
export const API_ENDPOINTS = {
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
  
  // 资源授权
  RESOURCE_AUTH: {
    BASE: '/api/resource-auth'
  },
  
  // 分析统计
  ANALYTICS: {
    BASE: '/analytics'
  }
}

// 构建完整的API URL
export function buildApiUrl(endpoint) {
  const baseURL = getBackendBaseURL()
  return `${baseURL}${endpoint}`
}

// 构建完整的页面URL（用于页面跳转）
export function buildPageUrl(path) {
  const host = getBackendHost()
  return `${host}${path}`
}

// WebSocket配置
export function getWebSocketUrl() {
  const host = getBackendHost()
  const wsProtocol = host.startsWith('https') ? 'wss' : 'ws'
  const wsHost = host.replace(/^https?:\/\//, '')
  return `${wsProtocol}://${wsHost}/ws/permissions/`
}

// 兼容性方法 - 为websocketManager提供getBaseUrl方法
export const apiConfig = {
  getBaseUrl: getBackendHost,
  getBackendBaseURL,
  getBackendHost,
  getWebSocketUrl,
  API_ENDPOINTS,
  buildApiUrl,
  buildPageUrl
}

// 默认导出配置对象
export default {
  getBackendBaseURL,
  getBackendHost,
  getWebSocketUrl,
  API_ENDPOINTS,
  buildApiUrl,
  buildPageUrl
}