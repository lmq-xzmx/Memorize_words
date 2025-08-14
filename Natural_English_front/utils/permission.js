/**
 * 前端权限控制工具
 * 基于角色的访问控制(RBAC)实现
 */

import { syncAuthState, manualSyncAuth } from './authSync.js'

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

// 页面权限映射表
const PAGE_PERMISSIONS = {
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
 * @param {string} userRole - 用户角色
 * @param {string} permission - 权限名称
 * @returns {boolean} 是否拥有权限
 */
export function hasPermission(userRole, permission) {
  if (!userRole || !permission) {
    return false
  }
  
  const permissions = ROLE_PERMISSIONS[userRole] || []
  return permissions.includes('*') || permissions.includes(permission)
}

/**
 * 检查用户是否可以访问指定页面
 * @param {string} userRole - 用户角色
 * @param {string} path - 页面路径
 * @returns {boolean} 是否可以访问
 */
export function canAccessPage(userRole, path) {
  // 处理动态路由参数
  const normalizedPath = path.replace(/\/\d+$/, '').replace(/\/[^/]*$/, '')
  const permission = PAGE_PERMISSIONS[normalizedPath] || PAGE_PERMISSIONS[path]
  
  if (!permission) {
    // 如果页面没有定义权限要求，默认允许访问
    return true
  }
  
  return hasPermission(userRole, permission)
}

/**
 * 获取用户可访问的菜单项
 * @param {string} userRole - 用户角色
 * @returns {Array} 可访问的菜单项
 */
export function getAccessibleMenus(userRole) {
  const allMenus = [
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
  
  return allMenus.filter(menu => hasPermission(userRole, menu.permission))
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

/**
 * 检查用户是否已认证
 * @returns {boolean} 是否已认证
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
 * @param {string} role - 角色代码
 * @returns {string} 角色显示名称
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
 * 权限检查装饰器（用于Vue组件方法）
 * @param {string} permission - 权限名称
 * @returns {Function} 装饰器函数
 */
export function requirePermission(permission) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value
    
    descriptor.value = function(...args) {
      const user = getCurrentUser()
      if (!user || !hasPermission(user.role, permission)) {
        console.warn(`权限不足：需要 ${permission} 权限`)
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
  // 检查认证状态
  if (to.meta.requiresAuth) {
    const authenticated = await isAuthenticated()
    if (!authenticated) {
      next('/login')
      return
    }
  }
  
  // 检查页面权限
  const user = getCurrentUser()
  if (user && !canAccessPage(user.role, to.path)) {
    console.warn(`用户 ${user.username}(${user.role}) 无权访问页面 ${to.path}`)
    next('/dashboard') // 重定向到仪表板
    return
  }
  
  next()
}

/**
 * 清除用户认证信息
 */
export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('userSettings')
  
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
 * 权限变更监听器
 */
class PermissionWatcher {
  constructor() {
    this.listeners = []
  }
  
  /**
   * 添加权限变更监听器
   * @param {Function} callback - 回调函数
   */
  addListener(callback) {
    this.listeners.push(callback)
  }
  
  /**
   * 移除权限变更监听器
   * @param {Function} callback - 回调函数
   */
  removeListener(callback) {
    const index = this.listeners.indexOf(callback)
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }
  
  /**
   * 通知权限变更
   * @param {Object} user - 用户信息
   */
  notifyChange(user) {
    this.listeners.forEach(callback => {
      try {
        callback(user)
      } catch (error) {
        console.error('权限变更监听器执行失败:', error)
      }
    })
  }
}

export const permissionWatcher = new PermissionWatcher()

// 监听localStorage变化，自动更新权限状态
window.addEventListener('storage', (event) => {
  if (event.key === 'user' || event.key === 'token') {
    const user = getCurrentUser()
    permissionWatcher.notifyChange(user)
  }
})

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
  permissionWatcher
}