/**
 * 前端权限控制工具
 * 实现基于角色的访问控制 (RBAC)
 * 根据《用户权限管理系统规范》文档实现
 */

import { syncAuthState, manualSyncAuth } from './authSync.js'

// 从统一权限常量文件导入所有权限和角色定义
import {
  ALL_PERMISSIONS,
  PERMISSION_CATEGORIES,
  PERMISSION_DISPLAY_NAMES,
  LEARNING_PERMISSIONS,
  CONTENT_PERMISSIONS,
  SOCIAL_PERMISSIONS,
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS,
  ADVANCED_PERMISSIONS,
  ROLES,
  ROLE_DISPLAY_NAMES,
  BASE_ROLE_PERMISSIONS,
  getRolePermissions,
  roleHasPermission,
  isRoleHigher,
  getManageableRoles
} from './unifiedPermissionConstants.js'

import {
  PAGE_PERMISSIONS,
  canAccessPage as canAccessPageByPermissions,
  pageRequiresAuth,
  getAccessibleLearningModes,
  getAllAccessiblePages
} from './learningModePermissions.js'

import permissionCacheManager, { getUserPermissions as getCachedUserPermissions, syncPermissions as syncCachedPermissions, clearPermissionCache } from './permissionCache.js'

// 角色权限映射表
const ROLE_PERMISSIONS = {
  'admin': ['*'], // 管理员拥有所有权限
  'dean': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_academic', 'manage_teaching',
    'view_reports', 'manage_users'
  ],
  'academic_director': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_curriculum', 'manage_teaching',
    'view_academic_reports'
  ],
  'research_leader': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_research', 'manage_teaching_methods',
    'view_research_reports'
  ],
  'teacher': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_teaching', 'view_student',
    'change_student'
  ],
  'parent': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_student', 'view_own_children', 'view_child_progress', 'view_child_reports',
    'communicate_with_teacher'
  ],
  'student': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'change_own_profile'
  ]
}

// 权限缓存状态（使用新的缓存管理器）
let permissionCacheStatus = {
  lastSync: 0,
  syncing: false,
  version: '1.0.0'
}

// 权限同步配置
const PERMISSION_SYNC_CONFIG = {
  apiEndpoint: '/api/permissions/sync',
  websocketEndpoint: import.meta.env.MODE === 'production' ? '/ws/permissions/' : 'ws://127.0.0.1:8000/ws/permissions/',
  syncInterval: 30 * 1000, // 30秒同步间隔
  retryAttempts: 5,
  retryDelay: 2000,
  maxRetryDelay: 30000
}

// 页面权限映射表
const PAGE_PERMISSIONS_LEGACY = {
  '/': 'view_word_learning',
  '/dashboard': 'view_dashboard',
  '/profile': 'view_own_profile',
  '/settings': 'change_own_settings',
  '/help': 'view_help',
  '/word-learning': 'view_word_learning',
  '/word-learning/spelling': 'practice_spelling',
  '/word-learning/flashcard': 'use_flashcard',
  '/word-reading': 'practice_reading',
  '/word-detail': 'view_word_detail',
  '/word-examples': 'view_word_examples',
  '/story-reading': 'practice_story_reading',
  '/listening': 'practice_listening',
  '/word-challenge': 'participate_challenge',
  '/word-selection': 'practice_word_selection',
  '/word-selection-practice': 'practice_word_selection',
  '/word-selection-practice2': 'practice_word_selection',
  '/word-review': 'review_words',
  '/word-root-analysis': 'analyze_word_roots',
  '/pattern-memory': 'use_pattern_memory',
  '/community': 'access_community',
  '/fashion': 'access_fashion_content',
  '/dev': 'access_dev_tools',
  '/dev-index': 'access_dev_tools',
  '/admin/dev-index': 'access_dev_tools',
  '/analytics': 'view_analytics',
  '/resource-auth': 'manage_resource_auth',
  '/subscription-management': 'manage_subscriptions',
  '/resource-sharing': 'share_resources',
  // 补充缺失的页面权限映射
  '/learning-modes': 'view_word_learning',
  '/competition': 'participate_challenge',
  '/quick-brush': 'review_words',
  '/discover': 'discover_content'
}

/**
 * 检查用户是否拥有指定权限
 * @param {string|Array} userRole - 用户角色或权限列表
 * @param {string} permission - 权限名称
 * @returns {boolean} 是否拥有权限
 */
export function hasPermission(userRole, permission) {
  if (!permission) {
    return false
  }
  
  // 如果传入的是权限数组，直接检查
  if (Array.isArray(userRole)) {
    return userRole.includes(permission)
  }
  
  // 如果传入的是角色，获取角色权限
  if (typeof userRole === 'string') {
    const permissions = ROLE_PERMISSIONS[userRole] || []
    return permissions.includes('*') || permissions.includes(permission)
  }
  
  return false
}

/**
 * 检查用户是否拥有多个权限中的任意一个
 * @param {string|Array} userRole - 用户角色或权限列表
 * @param {Array} permissions - 权限列表
 * @returns {boolean} 是否拥有任意权限
 */
export function hasAnyPermission(userRole, permissions) {
  if (!permissions || !Array.isArray(permissions)) {
    return false
  }
  
  return permissions.some(permission => hasPermission(userRole, permission))
}

/**
 * 检查用户是否拥有所有指定权限
 * @param {string|Array} userRole - 用户角色或权限列表
 * @param {Array} permissions - 权限列表
 * @returns {boolean} 是否拥有所有权限
 */
export function hasAllPermissions(userRole, permissions) {
  if (!permissions || !Array.isArray(permissions)) {
    return true
  }
  
  return permissions.every(permission => hasPermission(userRole, permission))
}

/**
 * 检查用户是否可以访问指定页面
 * @param {string|Array} userRole - 用户角色或权限列表
 * @param {string} path - 页面路径
 * @returns {boolean} 是否可以访问
 */
export function canAccessPage(userRole, path) {
  if (!path) {
    return false
  }
  
  // 获取用户权限列表
  let userPermissions = []
  if (Array.isArray(userRole)) {
    userPermissions = userRole
  } else if (typeof userRole === 'string') {
    userPermissions = ROLE_PERMISSIONS[userRole] || []
  }
  
  // 处理动态路由参数
  const normalizedPath = path.replace(/\/\d+$/, '').replace(/\/[^/]*$/, '')
  const permission = PAGE_PERMISSIONS_LEGACY[normalizedPath] || PAGE_PERMISSIONS_LEGACY[path]
  
  if (!permission) {
    // 如果页面没有定义权限要求，默认允许访问
    return true
  }
  
  return userPermissions.includes('*') || userPermissions.includes(permission)
}

/**
 * 获取用户可访问的页面列表
 * @param {string|Array} userRole - 用户角色或权限列表
 * @returns {Array} 可访问的页面配置列表
 */
export function getAccessiblePages(userRole) {
  let userPermissions = []
  if (Array.isArray(userRole)) {
    userPermissions = userRole
  } else if (typeof userRole === 'string') {
    userPermissions = ROLE_PERMISSIONS[userRole] || []
  }
  
  const accessiblePages = []
  for (const [path, permission] of Object.entries(PAGE_PERMISSIONS_LEGACY)) {
    if (userPermissions.includes('*') || userPermissions.includes(permission)) {
      accessiblePages.push({ path, permission })
    }
  }
  
  return accessiblePages
}

/**
 * 获取用户可访问的菜单项
 * @param {string|Array} userRole - 用户角色或权限列表
 * @param {Array} menuItems - 菜单项列表
 * @returns {Array} 过滤后的菜单项
 */
export function getAccessibleMenus(userRole, menuItems) {
  // 如果没有传入菜单项，使用默认菜单
  const defaultMenus = [
    {
      id: 'dashboard',
      title: '仪表板',
      path: '/dashboard',
      icon: '📊',
      permission: 'view_dashboard'
    },
    {
      id: 'word-learning',
      title: '单词学习',
      path: '/word-learning',
      icon: '📚',
      permission: 'view_word_learning'
    },
    {
      id: 'word-challenge',
      title: '单词挑战',
      path: '/word-challenge',
      icon: '🎯',
      permission: 'participate_challenge'
    },
    {
      id: 'word-review',
      title: '单词复习',
      path: '/word-review',
      icon: '🔄',
      permission: 'review_words'
    },
    {
      id: 'community',
      title: '学习社区',
      path: '/community',
      icon: '👥',
      permission: 'access_community'
    },
    {
      id: 'analytics',
      title: '数据分析',
      path: '/analytics',
      icon: '📈',
      permission: 'view_analytics'
    },
    {
      id: 'resource-auth',
      title: '资源管理',
      path: '/resource-auth',
      icon: '🔐',
      permission: 'manage_resource_auth'
    },
    {
      id: 'dev-index',
      title: '开发工具',
      path: '/dev-index',
      icon: '🛠️',
      permission: 'access_dev_tools'
    },
    {
      id: 'profile',
      title: '个人资料',
      path: '/profile',
      icon: '👤',
      permission: 'view_own_profile'
    },
    {
      id: 'settings',
      title: '设置',
      path: '/settings',
      icon: '⚙️',
      permission: 'change_own_settings'
    }
  ]
  
  const menus = menuItems || defaultMenus
  
  if (!menus) {
    return []
  }
  
  let userPermissions = []
  if (Array.isArray(userRole)) {
    userPermissions = userRole
  } else if (typeof userRole === 'string') {
    userPermissions = getRolePermissions(userRole)
  }
  
  return menus.filter(item => {
    // 如果菜单项没有权限要求，默认可访问
    if (!item.permission) {
      return true
    }
    
    // 支持多权限检查
    if (Array.isArray(item.permission)) {
      return hasAnyPermission(userPermissions, item.permission)
    }
    
    // 单权限检查
    return hasPermission(userPermissions, item.permission)
  }).map(item => {
    // 递归过滤子菜单
    if (item.children && item.children.length > 0) {
      return {
        ...item,
        children: getAccessibleMenus(userRole, item.children)
      }
    }
    return item
  })
}

/**
 * 获取当前用户信息
 * @returns {Object} 用户信息对象
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

// 认证状态缓存
let authCache = {
  lastCheck: 0,
  result: null,
  syncing: false
}

// 缓存有效期（5分钟）
const AUTH_CACHE_DURATION = 5 * 60 * 1000

/**
 * 检查用户是否已认证
 * @returns {boolean} 是否已认证
 */
export async function isAuthenticated() {
  const token = localStorage.getItem('token')
  const user = getCurrentUser()
  
  // 如果前端有完整的登录信息，直接返回true
  if (token && user) {
    return true
  }
  
  // 检查缓存是否有效
  const now = Date.now()
  if (authCache.lastCheck && (now - authCache.lastCheck) < AUTH_CACHE_DURATION && authCache.result !== null) {
    return authCache.result
  }
  
  // 如果正在同步中，等待同步完成
  if (authCache.syncing) {
    // 等待最多3秒
    let waitTime = 0
    while (authCache.syncing && waitTime < 3000) {
      await new Promise(resolve => setTimeout(resolve, 100))
      waitTime += 100
    }
    return authCache.result || false
  }
  
  // 开始同步后端状态
  authCache.syncing = true
  try {
    console.log('前端无登录信息，尝试同步后端状态...')
    const syncResult = await syncAuthState()
    
    authCache.lastCheck = now
    authCache.result = syncResult.success && syncResult.authenticated
    
    if (authCache.result) {
      console.log('同步成功，用户已登录')
    } else {
      console.log('同步完成，用户未登录')
    }
    
    return authCache.result
  } catch (error) {
    console.error('认证状态同步失败:', error)
    authCache.lastCheck = now
    authCache.result = false
    return false
  } finally {
    authCache.syncing = false
  }
}

/**
 * 获取用户角色显示名称
 * @param {string} role - 角色代码
 * @returns {string} 角色显示名称
 */
export function getRoleDisplayName(role) {
  return ROLE_DISPLAY_NAMES[role] || role
}

/**
 * 获取权限显示名称
 * @param {string} permission - 权限代码
 * @returns {string} 权限显示名称
 */
export function getPermissionDisplayName(permission) {
  return PERMISSION_DISPLAY_NAMES[permission] || permission
}

/**
 * 获取权限分类显示名称
 * @param {string} category - 权限分类
 * @returns {string} 分类显示名称
 */
export function getCategoryDisplayName(category) {
  const categoryNames = {
    learning: '学习功能',
    content: '内容管理',
    social: '社交功能',
    management: '管理功能',
    system: '系统管理',
    advanced: '高级功能'
  }
  return categoryNames[category] || category
}

/**
 * 权限检查装饰器（用于Vue组件方法）
 * @param {string|Array} permissions - 所需权限
 * @param {string} mode - 权限检查模式: 'any' | 'all'
 * @returns {Function} 装饰器函数
 */
export function requirePermission(permissions, mode = 'any') {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value
    
    descriptor.value = function(...args) {
      const user = getCurrentUser()
      if (!user) {
        console.warn('用户未登录')
        return
      }
      
      const userPermissions = getRolePermissions(user.role)
      let hasRequiredPermission = false
      
      if (Array.isArray(permissions)) {
        hasRequiredPermission = mode === 'all' 
          ? hasAllPermissions(userPermissions, permissions)
          : hasAnyPermission(userPermissions, permissions)
      } else {
        hasRequiredPermission = hasPermission(userPermissions, permissions)
      }
      
      if (!hasRequiredPermission) {
        console.warn(`权限不足: 需要 ${Array.isArray(permissions) ? permissions.join(', ') : permissions} 权限`)
        return
      }
      
      return originalMethod.apply(this, args)
    }
    
    return descriptor
  }
}

/**
 * 路由权限检查函数
 * @param {Object} to - 目标路由
 * @param {Object} from - 来源路由
 * @param {Function} next - 路由继续函数
 */
export async function checkRoutePermission(to, from, next) {
  // 确保路由对象有 meta 属性
  if (!to.meta) {
    to.meta = {}
  }
  
  const authenticated = await isAuthenticated()
  const user = getCurrentUser()
  
  // 如果路由需要认证但用户未登录
  if (to.meta.requiresAuth && !authenticated) {
    next('/login')
    return
  }
  
  // 如果用户已登录但访问登录页，重定向到首页
  if (authenticated && to.path === '/login') {
    next('/')
    return
  }
  
  // 检查页面权限
  if (user && !canAccessPage(user.role, to.path)) {
    // 记录访问被拒绝的日志
    console.warn(`访问被拒绝: 用户 ${user.username} (${user.role}) 尝试访问 ${to.path}`)
    
    // 重定向到用户有权限的默认页面
    const defaultPage = getDefaultPageForRole(user.role)
    next(defaultPage)
    return
  }
  
  // 特殊页面处理
  if (to.path.startsWith('/admin') && user && !isRoleHigher(user.role, ROLES.TEACHER)) {
    next('/dashboard')
    return
  }
  
  next()
}

/**
 * 获取角色的默认页面
 * @param {string} role - 用户角色
 * @returns {string} 默认页面路径
 */
export function getDefaultPageForRole(role) {
  const defaultPages = {
    [ROLES.ADMIN]: '/admin/dashboard',
    [ROLES.DEAN]: '/management/overview',
    [ROLES.ACADEMIC_SUPERVISOR]: '/academic/dashboard',
    [ROLES.RESEARCH_MANAGER]: '/research/dashboard',
    [ROLES.TEACHER]: '/teacher/dashboard',
    [ROLES.PARENT]: '/parent/dashboard',
    [ROLES.STUDENT]: '/dashboard'
  }
  
  return defaultPages[role] || '/dashboard'
}

/**
 * 清除权限缓存
 */
export function clearCache() {
  clearPermissionCache()
  permissionCacheStatus.lastSync = 0
  permissionCacheStatus.syncing = false
}

/**
 * 获取用户权限（使用缓存管理器）
 * @param {string} userId - 用户ID
 * @param {string} role - 用户角色
 * @returns {Promise<Array>} 用户权限列表
 */
export async function fetchUserPermissions(userId, role) {
  try {
    // 优先从缓存获取
    const cachedPermissions = await getCachedUserPermissions(userId)
    if (cachedPermissions) {
      return cachedPermissions
    }
    
    // 从角色定义获取基础权限
    const rolePermissions = getRolePermissions(role)
    
    // 缓存权限数据
    await permissionCacheManager.set(`user_permissions_${userId}`, rolePermissions)
    
    return rolePermissions
  } catch (error) {
    console.error('获取用户权限失败:', error)
    // 降级到角色权限
    return getRolePermissions(role)
  }
}

/**
 * 同步权限数据
 * @param {boolean} force - 是否强制同步
 * @returns {Promise<boolean>} 同步是否成功
 */
export async function syncPermissions(force = false) {
  if (permissionCacheStatus.syncing && !force) {
    return false
  }
  
  permissionCacheStatus.syncing = true
  
  try {
    const result = await syncCachedPermissions()
    permissionCacheStatus.lastSync = Date.now()
    permissionCacheStatus.syncing = false
    
    // 通知权限变更
    permissionSyncManager.notifyListeners('permissions_synced', {
      success: result,
      timestamp: permissionCacheStatus.lastSync
    })
    
    return result
  } catch (error) {
    console.error('权限同步失败:', error)
    permissionCacheStatus.syncing = false
    return false
  }
}

/**
 * 获取缓存的权限数据
 * @param {string} key - 缓存键
 * @returns {any} 缓存的数据
 */
export function getCachedPermissions(key) {
  // 使用新的缓存管理器
  return permissionCacheManager.get(key)
}

/**
 * 设置权限缓存
 * @param {string} key - 缓存键
 * @param {any} value - 缓存值
 */
export function setCachedPermissions(key, value) {
  // 使用新的缓存管理器
  return permissionCacheManager.set(key, value)
}

/**
 * 清除认证缓存
 */
export function clearAuthCache() {
  authCache.lastCheck = 0
  authCache.result = null
  authCache.syncing = false
  clearPermissionCache()
}

/**
 * 清除用户认证信息
 */
export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('userSettings')
  
  // 清除认证缓存
  clearAuthCache()
  
  // 触发权限变更事件
  if (typeof window !== 'undefined' && window.permissionWatcher) {
    window.permissionWatcher.notifyChange()
  }
}

// 将权限工具函数暴露到全局window对象
if (typeof window !== 'undefined') {
  window.permissionUtils = {
    hasPermission,
    canAccessPage,
    getCurrentUser,
    isAuthenticated,
    getRoleDisplayName,
    clearAuth,
    getAccessibleMenus
  }
}

/**
 * 权限同步管理器
 */
class PermissionSyncManager {
  constructor() {
    this.websocket = null
    this.syncInterval = null
    this.retryCount = 0
    this.listeners = []
    this.connectionStatus = 'disconnected' // disconnected, connecting, connected, authenticated, error
    this.lastSyncTime = 0
    this.isDestroyed = false
  }
  
  init() {
    // 监听localStorage变化
    window.addEventListener('storage', (e) => {
      if (e.key === 'user' || e.key === 'token' || e.key === 'permissionCache') {
        this.notifyListeners('permission_changed', {
          key: e.key,
          oldValue: e.oldValue,
          newValue: e.newValue
        })
        
        // 清除缓存，强制重新获取权限
        if (e.key === 'user') {
          clearPermissionCache()
        }
      }
    })
    
    // 启动定期同步
    this.startPeriodicSync()
  }
  
  /**
   * 启动定期权限同步
   */
  startPeriodicSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
    }
    
    this.syncInterval = setInterval(() => {
      this.syncPermissions()
    }, PERMISSION_SYNC_CONFIG.syncInterval)
  }
  
  /**
   * 停止定期同步
   */
  stopPeriodicSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
  }
  
  /**
   * 同步权限数据
   */
  async syncPermissions() {
    const user = getCurrentUser()
    if (!user) {
      return
    }
    
    try {
      // 使用新的权限缓存管理器进行同步
      const syncResult = await syncCachedPermissions()
      
      if (syncResult) {
        this.retryCount = 0
        this.notifyListeners('permissions_synced', {
          success: true,
          timestamp: Date.now()
        })
      } else {
        throw new Error('权限同步失败')
      }
    } catch (error) {
      console.warn('权限同步错误:', error)
      this.handleSyncError()
    }
  }
  
  /**
   * 处理同步错误
   */
  handleSyncError() {
    this.retryCount++
    if (this.retryCount < PERMISSION_SYNC_CONFIG.retryAttempts) {
      setTimeout(() => {
        this.syncPermissions()
      }, PERMISSION_SYNC_CONFIG.retryDelay * this.retryCount)
    } else {
      console.error('权限同步重试次数已达上限')
      this.notifyListeners('sync_failed', { retryCount: this.retryCount })
    }
  }
  
  /**
   * 更新权限数据
   */
  async updatePermissions(permissionData) {
    try {
      if (permissionData.userPermissions) {
        await permissionCacheManager.set('userPermissions', permissionData.userPermissions)
      }
      
      if (permissionData.rolePermissions) {
        await permissionCacheManager.set('rolePermissions', permissionData.rolePermissions)
      }
      
      // 更新缓存状态
      permissionCacheStatus.lastSync = Date.now()
      
      this.notifyListeners('permissions_updated', permissionData)
    } catch (error) {
      console.error('更新权限数据失败:', error)
      this.notifyListeners('permissions_update_failed', { error })
    }
  }
  
  /**
   * 建立WebSocket连接进行实时同步
   */
  connectWebSocket() {
    const user = getCurrentUser()
    const token = localStorage.getItem('token')
    if (!user || !token) {
      console.warn('权限WebSocket连接失败：缺少用户信息或令牌')
      return
    }
    
    // 如果已有连接且状态正常，不重复连接
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      console.log('权限WebSocket已连接，跳过重复连接')
      return
    }
    
    // 关闭现有连接
    if (this.websocket) {
      this.websocket.close()
      this.websocket = null
    }
    
    try {
      // 构建WebSocket URL，添加用户ID参数
      const wsUrl = `${PERMISSION_SYNC_CONFIG.websocketEndpoint}?token=${encodeURIComponent(token)}&userId=${user.id || user.user_id}`
      console.log('正在连接权限WebSocket:', wsUrl.replace(/token=[^&]+/, 'token=***'))
      
      this.websocket = new WebSocket(wsUrl)
      
      // 设置连接超时
      const connectionTimeout = setTimeout(() => {
        if (this.websocket && this.websocket.readyState === WebSocket.CONNECTING) {
          console.error('权限WebSocket连接超时')
          this.websocket.close()
        }
      }, 10000)
      
      this.websocket.onopen = () => {
        clearTimeout(connectionTimeout)
        console.log('权限WebSocket连接已建立')
        this.retryCount = 0
        this.connectionStatus = 'connected'
        
        // 发送认证确认
        this.websocket.send(JSON.stringify({
          type: 'auth_confirm',
          userId: user.id || user.user_id,
          timestamp: Date.now()
        }))
      }
      
      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('收到权限WebSocket消息:', data)
          
          if (data.type === 'permission_update' || data.type === 'permission_changed') {
            this.updatePermissions(data.payload || data.data)
          } else if (data.type === 'auth_success') {
            console.log('权限WebSocket认证成功')
            this.connectionStatus = 'authenticated'
          } else if (data.type === 'heartbeat') {
            // 响应心跳
            this.websocket.send(JSON.stringify({ type: 'heartbeat_response' }))
          }
        } catch (error) {
          console.error('WebSocket消息解析错误:', error)
        }
      }
      
      this.websocket.onclose = (event) => {
        clearTimeout(connectionTimeout)
        this.connectionStatus = 'disconnected'
        
        console.log(`权限WebSocket连接已关闭，代码: ${event.code}, 原因: ${event.reason || '未知'}`)
        
        // 根据关闭代码决定是否重连
        if (event.code !== 1000 && event.code !== 1001) { // 非正常关闭
          this.scheduleReconnect()
        }
      }
      
      this.websocket.onerror = (error) => {
        clearTimeout(connectionTimeout)
        this.connectionStatus = 'error'
        
        console.error('权限WebSocket错误:', {
          error: error,
          readyState: this.websocket ? this.websocket.readyState : 'null',
          url: wsUrl.replace(/token=[^&]+/, 'token=***'),
          retryCount: this.retryCount
        })
        
        // 触发WebSocket诊断
        if (window.websocketDiagnostics) {
          window.websocketDiagnostics.handleWebSocketError('权限WebSocket', error.toString())
        }
        
        // 检查是否是网络错误
        if (!navigator.onLine) {
          console.warn('网络连接断开，等待网络恢复后重连')
          window.addEventListener('online', () => {
            console.log('网络已恢复，尝试重连WebSocket')
            this.connectWebSocket()
          }, { once: true })
        }
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      this.connectionStatus = 'error'
      
      // 触发WebSocket诊断
      if (window.websocketDiagnostics) {
        window.websocketDiagnostics.handleWebSocketError('WebSocket连接失败', error.toString())
      }
      
      this.scheduleReconnect()
    }
  }
  
  /**
   * 安排重连
   */
  scheduleReconnect() {
    if (this.retryCount >= PERMISSION_SYNC_CONFIG.retryAttempts) {
      console.error(`权限WebSocket重连失败，已达到最大重试次数 ${PERMISSION_SYNC_CONFIG.retryAttempts}`)
      return
    }
    
    const delay = Math.min(
      PERMISSION_SYNC_CONFIG.retryDelay * Math.pow(2, this.retryCount),
      PERMISSION_SYNC_CONFIG.maxRetryDelay
    )
    
    console.log(`${delay / 1000}秒后尝试重连权限WebSocket (第${this.retryCount + 1}次)`)
    
    setTimeout(() => {
      this.retryCount++
      this.connectWebSocket()
    }, delay)
  }
  
  /**
   * 断开WebSocket连接
   */
  disconnectWebSocket() {
    if (this.websocket) {
      console.log('主动断开权限WebSocket连接')
      this.websocket.close(1000, '主动断开') // 正常关闭
      this.websocket = null
    }
    this.connectionStatus = 'disconnected'
    this.retryCount = 0
  }
  
  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      status: this.connectionStatus,
      retryCount: this.retryCount,
      websocketState: this.websocket ? this.websocket.readyState : null,
      lastSyncTime: this.lastSyncTime
    }
  }
  
  /**
   * 检查连接是否健康
   */
  isConnectionHealthy() {
    return this.websocket && 
           this.websocket.readyState === WebSocket.OPEN && 
           this.connectionStatus === 'authenticated'
  }
  
  /**
   * 添加权限变更监听器
   */
  addListener(callback) {
    this.listeners.push(callback)
  }
  
  /**
   * 移除权限变更监听器
   */
  removeListener(callback) {
    const index = this.listeners.indexOf(callback)
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }
  
  /**
   * 通知所有监听器
   */
  notifyListeners(event, data) {
    this.listeners.forEach(callback => {
      try {
        callback(event, data)
      } catch (error) {
        console.error('权限监听器执行错误:', error)
      }
    })
  }
  
  /**
   * 通知权限变更（兼容性方法）
   * @param {Object} user - 用户信息
   */
  notifyChange(user) {
    this.notifyListeners('permission_changed', user)
  }
  
  /**
   * 启动同步管理器
   */
  start() {
    this.startPeriodicSync()
    this.connectWebSocket()
  }

  /**
   * 停止同步管理器（兼容性方法）
   */
  stop() {
    this.destroy()
  }
  
  /**
   * 销毁同步管理器
   */
  destroy() {
    this.stopPeriodicSync()
    this.disconnectWebSocket()
    this.listeners = []
  }
}

// 创建全局权限同步管理器实例
export const permissionSyncManager = new PermissionSyncManager()

// 兼容性导出
export const permissionWatcher = permissionSyncManager

// 监听localStorage变化，自动更新权限状态
window.addEventListener('storage', (event) => {
  if (event.key === 'user' || event.key === 'token') {
    const user = getCurrentUser()
    permissionWatcher.notifyChange(user)
  }
})

// 导出 getRolePermissions 函数、PAGE_PERMISSIONS 和 ROLE_PERMISSIONS
export { getRolePermissions, PAGE_PERMISSIONS, ROLE_PERMISSIONS }

export default {
  hasPermission,
  canAccessPage,
  getAccessibleMenus,
  getCurrentUser,
  isAuthenticated,
  getRoleDisplayName,
  requirePermission,
  checkRoutePermission,
  clearAuth,
  permissionWatcher,
  getRolePermissions,
  PAGE_PERMISSIONS,
  ROLE_PERMISSIONS
}