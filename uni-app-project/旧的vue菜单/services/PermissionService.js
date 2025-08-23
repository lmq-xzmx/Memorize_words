/**
 * 权限服务
 * 提供权限计算、缓存和验证功能
 */

import { ROLE_PERMISSION_INHERITANCE, PAGE_PERMISSIONS, ROLE_DISPLAY_NAMES, CACHE_CONFIG } from '../config/menuConfig.js'

class PermissionService {
  constructor() {
    this.permissionCache = new Map()
    this.userCache = new Map()
    this.cacheTimestamps = new Map()
    this.initialized = false
  }

  /**
   * 初始化权限服务
   * @returns {Promise<void>}
   */
  async init() {
    if (this.initialized) {
      return
    }

    try {
      console.log('🔐 正在初始化权限服务...')
      
      // 清理过期缓存
      this.clearExpiredCache()
      
      // 验证当前用户认证状态
      const user = this.getCurrentUser()
      if (user) {
        console.log('✅ 用户认证状态有效:', user.username)
      } else {
        console.log('ℹ️ 用户未登录')
      }
      
      this.initialized = true
      console.log('✅ 权限服务初始化完成')
      
    } catch (error) {
      console.error('❌ 权限服务初始化失败:', error)
      throw error
    }
  }

  /**
   * 更新用户信息
   * @param {Object} user - 用户信息
   * @param {string} token - 认证令牌
   * @returns {Promise<void>}
   */
  async updateUserInfo(user, token) {
    try {
      console.log('🔄 正在更新用户权限信息...', user.username)
      
      // 清理旧的缓存
      this.clearUserCache()
      
      // 存储用户信息到localStorage
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('token', token)
      
      // 更新用户缓存
      this.userCache.set('current_user', user)
      this.cacheTimestamps.set('current_user', Date.now())
      
      // 计算并缓存用户权限
      const permissions = this.calculateRolePermissions(user.role)
      this.permissionCache.set(user.role, permissions)
      this.cacheTimestamps.set(user.role, Date.now())
      
      // 通知权限变更
      this.notifyPermissionChange(user)
      
      console.log('✅ 用户权限信息更新完成')
      
    } catch (error) {
      console.error('❌ 更新用户权限信息失败:', error)
      throw error
    }
  }

  /**
   * 清理过期缓存
   */
  clearExpiredCache() {
    const now = Date.now()
    for (const [key, timestamp] of this.cacheTimestamps.entries()) {
      if (now - timestamp > CACHE_CONFIG.PERMISSION_CACHE_DURATION) {
        this.permissionCache.delete(key)
        this.userCache.delete(key)
        this.cacheTimestamps.delete(key)
      }
    }
  }

  /**
   * 计算角色的所有权限（支持继承）
   * @param {string} role - 角色名称
   * @returns {Array} 权限列表
   */
  calculateRolePermissions(role) {
    const cacheKey = `role_permissions_${role}`
    
    // 检查缓存
    if (this.isCacheValid(cacheKey, CACHE_CONFIG.PERMISSION_CACHE_DURATION)) {
      return this.permissionCache.get(cacheKey)
    }

    const permissions = new Set()
    const visited = new Set()

    const collectPermissions = (currentRole) => {
      if (visited.has(currentRole)) {
        console.warn(`检测到权限继承循环: ${currentRole}`)
        return
      }
      visited.add(currentRole)

      const roleConfig = ROLE_PERMISSION_INHERITANCE[currentRole]
      if (!roleConfig) {
        console.warn(`未找到角色配置: ${currentRole}`)
        // 为未知角色提供基础权限
        permissions.add('view_dashboard')
        permissions.add('view_own_profile')
        return
      }

      // 管理员拥有所有权限
      if (roleConfig.includes('*')) {
        permissions.add('*')
        return
      }

      roleConfig.forEach(item => {
        if (ROLE_PERMISSION_INHERITANCE[item]) {
          // 这是一个角色继承
          collectPermissions(item)
        } else {
          // 这是一个具体权限
          permissions.add(item)
        }
      })
    }

    collectPermissions(role)
    const result = Array.from(permissions)
    
    // 缓存结果
    this.permissionCache.set(cacheKey, result)
    this.cacheTimestamps.set(cacheKey, Date.now())
    
    return result
  }

  /**
   * 检查用户是否拥有指定权限
   * @param {string} userRole - 用户角色
   * @param {string} permission - 权限名称
   * @returns {boolean} 是否拥有权限
   */
  hasPermission(userRole, permission) {
    if (!userRole || !permission) {
      return false
    }

    const permissions = this.calculateRolePermissions(userRole)
    return permissions.includes('*') || permissions.includes(permission)
  }

  /**
   * 检查用户是否可以访问指定页面
   * @param {string} userRole - 用户角色
   * @param {string} path - 页面路径
   * @returns {boolean} 是否可以访问
   */
  canAccessPage(userRole, path) {
    // 处理动态路由参数
    const normalizedPath = this.normalizePath(path)
    const permission = PAGE_PERMISSIONS[normalizedPath] || PAGE_PERMISSIONS[path]
    
    if (!permission) {
      // 如果页面没有定义权限要求，默认允许访问
      return true
    }
    
    return this.hasPermission(userRole, permission)
  }

  /**
   * 标准化路径（处理动态参数）
   * @param {string} path - 原始路径
   * @returns {string} 标准化后的路径
   */
  normalizePath(path) {
    return path
      .replace(/\/\d+$/, '') // 移除末尾的数字ID
      .replace(/\/[^/]*$/, '') // 移除末尾的动态参数
  }

  /**
   * 获取当前用户信息（带缓存）
   * @returns {Object|null} 用户信息对象
   */
  getCurrentUser() {
    const cacheKey = 'current_user'
    
    // 检查缓存
    if (this.isCacheValid(cacheKey, CACHE_CONFIG.USER_CACHE_DURATION)) {
      return this.userCache.get(cacheKey)
    }

    try {
      const userStr = localStorage.getItem('user')
      if (!userStr) {
        this.clearUserCache()
        return null
      }
      
      // 检查是否是HTML内容
      if (userStr.trim().startsWith('<!DOCTYPE') || userStr.trim().startsWith('<html')) {
        console.warn('检测到localStorage中存储的是HTML内容，清除无效数据')
        this.clearAuth()
        return null
      }
      
      const user = JSON.parse(userStr)
      
      // 验证用户对象的有效性
      if (user && typeof user === 'object' && !Array.isArray(user) && user.role) {
        // 缓存用户信息
        this.userCache.set(cacheKey, user)
        this.cacheTimestamps.set(cacheKey, Date.now())
        return user
      }
      
      console.warn('用户数据格式无效，清除数据')
      this.clearAuth()
      return null
    } catch (error) {
      console.error('解析用户信息失败:', error)
      this.clearAuth()
      return null
    }
  }

  /**
   * 检查用户是否已认证
   * @returns {boolean} 是否已认证
   */
  isAuthenticated() {
    const token = localStorage.getItem('token')
    const user = this.getCurrentUser()
    return !!(token && user)
  }

  /**
   * 获取用户角色显示名称
   * @param {string} role - 角色代码
   * @returns {string} 角色显示名称
   */
  getRoleDisplayName(role) {
    return ROLE_DISPLAY_NAMES[role] || role
  }

  /**
   * 清除认证信息
   */
  clearAuth() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('userSettings')
    this.clearAllCache()
    
    // 触发权限变更事件
    this.notifyPermissionChange(null)
  }

  /**
   * 清除用户缓存
   */
  clearUserCache() {
    this.userCache.delete('current_user')
    this.cacheTimestamps.delete('current_user')
  }

  /**
   * 清除所有缓存
   */
  clearAllCache() {
    this.permissionCache.clear()
    this.userCache.clear()
    this.cacheTimestamps.clear()
  }

  /**
   * 检查缓存是否有效
   * @param {string} key - 缓存键
   * @param {number} duration - 缓存持续时间（毫秒）
   * @returns {boolean} 缓存是否有效
   */
  isCacheValid(key, duration) {
    const timestamp = this.cacheTimestamps.get(key)
    if (!timestamp) return false
    
    return Date.now() - timestamp < duration
  }

  /**
   * 权限变更监听器列表
   */
  permissionListeners = []

  /**
   * 添加权限变更监听器
   * @param {Function} callback - 回调函数
   */
  addPermissionListener(callback) {
    this.permissionListeners.push(callback)
  }

  /**
   * 移除权限变更监听器
   * @param {Function} callback - 回调函数
   */
  removePermissionListener(callback) {
    const index = this.permissionListeners.indexOf(callback)
    if (index > -1) {
      this.permissionListeners.splice(index, 1)
    }
  }

  /**
   * 通知权限变更
   * @param {Object} user - 用户信息
   */
  notifyPermissionChange(user) {
    this.permissionListeners.forEach(callback => {
      try {
        callback(user)
      } catch (error) {
        console.error('权限变更监听器执行失败:', error)
      }
    })
  }

  /**
   * 批量检查权限
   * @param {string} userRole - 用户角色
   * @param {Array} permissions - 权限列表
   * @returns {Object} 权限检查结果
   */
  batchCheckPermissions(userRole, permissions) {
    const result = {}
    const userPermissions = this.calculateRolePermissions(userRole)
    const hasAllPermissions = userPermissions.includes('*')
    
    permissions.forEach(permission => {
      result[permission] = hasAllPermissions || userPermissions.includes(permission)
    })
    
    return result
  }

  /**
   * 获取用户可访问的权限列表
   * @param {string} userRole - 用户角色
   * @returns {Array} 可访问的权限列表
   */
  getUserPermissions(userRole) {
    return this.calculateRolePermissions(userRole)
  }
}

// 创建单例实例
const permissionService = new PermissionService()

// 监听localStorage变化，自动更新权限状态
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key === 'user' || event.key === 'token') {
      permissionService.clearUserCache()
      const user = permissionService.getCurrentUser()
      permissionService.notifyPermissionChange(user)
    }
  })

  // 将权限服务暴露到全局
  window.permissionService = permissionService
}

export default permissionService

// 导出常用方法
export const {
  hasPermission,
  canAccessPage,
  getCurrentUser,
  isAuthenticated,
  getRoleDisplayName,
  clearAuth,
  addPermissionListener,
  removePermissionListener,
  batchCheckPermissions,
  getUserPermissions,
  updateUserInfo
} = permissionService