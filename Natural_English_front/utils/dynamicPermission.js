// 动态权限管理 - 从后端API获取权限数据
import { syncAuthState } from './authSync.js'

// 权限缓存
let permissionCache = {
  userMenus: null,
  allPermissions: null,
  userRole: null,
  lastUpdate: null,
  cacheTimeout: 5 * 60 * 1000 // 5分钟缓存
}

/**
 * 获取API基础URL
 */
function getApiBaseUrl() {
  return 'http://localhost:8001'
}

/**
 * 发送API请求
 */
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('token')
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  }
  
  const response = await fetch(`${getApiBaseUrl()}${url}`, {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  })
  
  if (!response.ok) {
    throw new Error(`API请求失败: ${response.status} ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 从后端获取用户菜单权限
 */
export async function fetchUserMenuPermissions() {
  try {
    const data = await apiRequest('/permissions/api/user-menu-permissions/')
    
    if (data.success) {
      // 更新缓存
      permissionCache.userMenus = data.menus
      permissionCache.allPermissions = data.all_permissions
      permissionCache.userRole = data.user_role
      permissionCache.lastUpdate = Date.now()
      
      console.log('成功获取用户菜单权限:', data)
      return data
    } else {
      console.error('获取菜单权限失败:', data.message)
      return null
    }
  } catch (error) {
    console.error('获取菜单权限API调用失败:', error)
    return null
  }
}

/**
 * 检查特定菜单权限
 */
export async function checkMenuPermission(menuKey) {
  try {
    const data = await apiRequest('/permissions/api/check-menu-permission/', {
      method: 'POST',
      body: JSON.stringify({ menu_key: menuKey })
    })
    
    return data.success ? data.has_permission : false
  } catch (error) {
    console.error('检查菜单权限失败:', error)
    return false
  }
}

/**
 * 获取角色显示名称
 */
export async function fetchRoleDisplayName() {
  try {
    const data = await apiRequest('/permissions/api/role-display-name/')
    return data.success ? data : null
  } catch (error) {
    console.error('获取角色显示名称失败:', error)
    return null
  }
}

/**
 * 获取菜单层级结构
 */
export async function fetchMenuHierarchy() {
  try {
    const data = await apiRequest('/permissions/api/menu-hierarchy/')
    return data.success ? data.menu_hierarchy : null
  } catch (error) {
    console.error('获取菜单层级失败:', error)
    return null
  }
}

/**
 * 检查缓存是否有效
 */
function isCacheValid() {
  if (!permissionCache.lastUpdate) return false
  return (Date.now() - permissionCache.lastUpdate) < permissionCache.cacheTimeout
}

/**
 * 获取用户可访问的菜单（带缓存）
 */
export async function getAccessibleMenus(forceRefresh = false) {
  // 检查缓存
  if (!forceRefresh && isCacheValid() && permissionCache.userMenus) {
    console.log('使用缓存的菜单数据')
    return permissionCache.userMenus
  }
  
  // 从API获取最新数据
  const permissionData = await fetchUserMenuPermissions()
  if (permissionData && permissionData.menus) {
    return permissionData.menus
  }
  
  // 如果API失败，返回缓存数据（如果有）
  if (permissionCache.userMenus) {
    console.warn('API获取失败，使用缓存数据')
    return permissionCache.userMenus
  }
  
  return []
}

/**
 * 检查用户是否有特定权限（带缓存）
 */
export async function hasPermission(permission, forceRefresh = false) {
  // 检查缓存
  if (!forceRefresh && isCacheValid() && permissionCache.allPermissions) {
    return permissionCache.allPermissions[permission] || false
  }
  
  // 从API获取最新数据
  const permissionData = await fetchUserMenuPermissions()
  if (permissionData && permissionData.all_permissions) {
    return permissionData.all_permissions[permission] || false
  }
  
  // 如果API失败，返回缓存数据（如果有）
  if (permissionCache.allPermissions) {
    console.warn('API获取失败，使用缓存数据检查权限')
    return permissionCache.allPermissions[permission] || false
  }
  
  return false
}

/**
 * 检查页面访问权限
 */
export async function canAccessPage(path) {
  // 页面到权限的映射
  const pagePermissionMap = {
    '/': 'dashboard',
    '/dashboard': 'dashboard',
    '/learning': 'learning',
    '/learning/practice': 'learning_practice',
    '/learning/progress': 'learning_progress',
    '/teaching': 'teaching',
    '/teaching/plans': 'teaching_plans',
    '/teaching/goals': 'teaching_goals',
    '/words': 'words',
    '/words/vocabulary': 'words_vocabulary',
    '/words/management': 'words_management',
    '/accounts': 'accounts',
    '/accounts/users': 'accounts_users',
    '/accounts/roles': 'accounts_roles',
    '/permissions': 'permissions',
    '/permissions/menu': 'permissions_menu',
    '/permissions/role': 'permissions_role'
  }
  
  const permission = pagePermissionMap[path]
  if (!permission) {
    // 如果没有映射，默认允许访问
    return true
  }
  
  return await hasPermission(permission)
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  try {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null
    
    // 检查是否是HTML内容
    if (userStr.trim().startsWith('<!DOCTYPE') || userStr.trim().startsWith('<html')) {
      console.warn('检测到localStorage中存储的是HTML内容，清除无效数据')
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      return null
    }
    
    const user = JSON.parse(userStr)
    // 验证用户对象的有效性
    if (user && typeof user === 'object' && !Array.isArray(user) && user.role) {
      return user
    }
    
    console.warn('用户数据格式无效，清除数据')
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    return null
  } catch (error) {
    console.error('解析用户信息失败:', error)
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    return null
  }
}

/**
 * 检查用户是否已认证
 */
export async function isAuthenticated() {
  const token = localStorage.getItem('token')
  const user = getCurrentUser()
  
  // 如果前端没有登录信息，尝试同步后端状态
  if (!token || !user) {
    console.log('前端无登录信息，尝试同步后端状态...')
    const syncResult = await syncAuthState()
    if (syncResult.success && syncResult.authenticated) {
      console.log('同步成功，用户已登录')
      return true
    }
    return false
  }
  
  return true
}

/**
 * 获取用户角色显示名称
 */
export function getRoleDisplayName(role) {
  const roleNames = {
    'admin': '管理员',
    'dean': '教导主任',
    'academic_director': '教务主任',
    'research_leader': '教研组长',
    'teacher': '自由老师',
    'parent': '家长',
    'student': '学生'
  }
  return roleNames[role] || role
}

/**
 * 清除认证信息和权限缓存
 */
export function clearAuth() {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  
  // 清除权限缓存
  permissionCache = {
    userMenus: null,
    allPermissions: null,
    userRole: null,
    lastUpdate: null,
    cacheTimeout: 5 * 60 * 1000
  }
  
  console.log('已清除认证信息和权限缓存')
}

/**
 * 路由权限检查
 */
export async function checkRoutePermission(to, from, next) {
  const isAuth = await isAuthenticated()
  
  if (!isAuth) {
    console.log('用户未认证，重定向到登录页')
    next('/login')
    return
  }
  
  const canAccess = await canAccessPage(to.path)
  if (!canAccess) {
    console.log(`用户无权访问页面: ${to.path}`)
    next('/403') // 重定向到无权限页面
    return
  }
  
  next()
}

/**
 * 权限变化监听器
 */
class PermissionWatcher {
  constructor() {
    this.listeners = []
  }
  
  addListener(callback) {
    this.listeners.push(callback)
  }
  
  removeListener(callback) {
    const index = this.listeners.indexOf(callback)
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }
  
  notifyChange(user) {
    this.listeners.forEach(callback => {
      try {
        callback(user)
      } catch (error) {
        console.error('权限变化监听器执行失败:', error)
      }
    })
  }
}

export const permissionWatcher = new PermissionWatcher()

// 监听localStorage变化
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key === 'user') {
      const user = getCurrentUser()
      permissionWatcher.notifyChange(user)
    }
  })
  
  // 暴露到全局对象供调试使用
  window.dynamicPermissionUtils = {
    hasPermission,
    canAccessPage,
    getAccessibleMenus,
    getCurrentUser,
    isAuthenticated,
    getRoleDisplayName,
    clearAuth,
    fetchUserMenuPermissions,
    checkMenuPermission,
    fetchRoleDisplayName,
    fetchMenuHierarchy,
    permissionCache
  }
}

export default {
  hasPermission,
  canAccessPage,
  getAccessibleMenus,
  getCurrentUser,
  isAuthenticated,
  getRoleDisplayName,
  checkRoutePermission,
  clearAuth,
  fetchUserMenuPermissions,
  checkMenuPermission,
  fetchRoleDisplayName,
  fetchMenuHierarchy,
  permissionWatcher
}