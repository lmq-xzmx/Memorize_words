/**
 * 统一认证状态管理服务
 * 整合分散的认证逻辑，提供统一的认证状态管理
 */

import api from '../utils/api.js'
import permissionService from './PermissionService.js'
import menuDataService from './MenuDataService.js'
import configSyncService from './ConfigSyncService.js'

class AuthStateManager {
  constructor() {
    this.authState = {
      isAuthenticated: false,
      user: null,
      token: null,
      loginTime: null,
      lastActivity: null,
      sessionTimeout: 30 * 60 * 1000, // 30分钟
      refreshTokenTimeout: null
    }
    
    this.authListeners = []
    this.sessionCheckInterval = null
    
    // 初始化认证状态
    this.initializeAuthState()
  }

  /**
   * 初始化服务
   */
  async init() {
    console.log('🔐 初始化认证状态管理服务...')
    this.initializeAuthState()
    this.startSessionCheck()
    console.log('✅ 认证状态管理服务初始化完成')
  }

  /**
   * 初始化认证状态
   */
  initializeAuthState() {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    const loginTime = localStorage.getItem('loginTime')
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr)
        this.authState = {
          ...this.authState,
          isAuthenticated: true,
          user,
          token,
          loginTime: loginTime ? parseInt(loginTime) : Date.now(),
          lastActivity: Date.now()
        }
        
        // 验证token有效性
        this.verifyToken()
        
        // 启动会话检查
        this.startSessionCheck()
        
      } catch (error) {
        console.error('初始化认证状态失败:', error)
        this.clearAuthState()
      }
    }
  }

  /**
   * 用户登录
   */
  async login(credentials) {
    try {
      const response = await api.post('/accounts/auth/login/', credentials)
      const { token, user, expires_in } = response
      
      if (!token || !user) {
        throw new Error('登录响应数据不完整')
      }
      
      // 更新认证状态
      const loginTime = Date.now()
      this.authState = {
        ...this.authState,
        isAuthenticated: true,
        user,
        token,
        loginTime,
        lastActivity: loginTime
      }
      
      // 持久化存储
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('loginTime', loginTime.toString())
      
      // 设置token过期时间
      if (expires_in) {
        this.scheduleTokenRefresh(expires_in * 1000)
      }
      
      // 更新权限服务
      await permissionService.updateUserInfo(user, token)
      
      // 启动配置同步
      configSyncService.startSync()
      
      // 启动会话检查
      this.startSessionCheck()
      
      // 通知监听器
      this.notifyAuthChange('login', user)
      
      console.log('用户登录成功:', user.username)
      return { success: true, user, token }
      
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  /**
   * 用户登出
   */
  async logout() {
    try {
      // 调用后端登出接口
      if (this.authState.token) {
        await api.post('/accounts/auth/logout/')
      }
    } catch (error) {
      console.error('后端登出失败:', error)
      // 即使后端登出失败，也要清除本地状态
    } finally {
      this.clearAuthState()
      this.notifyAuthChange('logout', null)
      console.log('用户已登出')
    }
  }

  /**
   * 清除认证状态
   */
  clearAuthState() {
    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('loginTime')
    
    // 重置状态
    this.authState = {
      isAuthenticated: false,
      user: null,
      token: null,
      loginTime: null,
      lastActivity: null,
      sessionTimeout: 30 * 60 * 1000,
      refreshTokenTimeout: null
    }
    
    // 清除定时器
    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval)
      this.sessionCheckInterval = null
    }
    
    if (this.authState.refreshTokenTimeout) {
      clearTimeout(this.authState.refreshTokenTimeout)
      this.authState.refreshTokenTimeout = null
    }
    
    // 清除权限服务状态
    permissionService.clearAuth()
    
    // 清除菜单缓存
    menuDataService.clearAllCache()
  }

  /**
   * 验证token有效性
   */
  async verifyToken() {
    if (!this.authState.token) {
      return false
    }
    
    try {
      const response = await api.post('/accounts/auth/verify-token/')
      
      // 处理响应拦截器返回的数据格式
      const data = response.data || response
      if (data && data.valid) {
        this.updateLastActivity()
        return true
      } else {
        console.warn('Token验证失败')
        this.clearAuthState()
        return false
      }
    } catch (error) {
      console.error('Token验证请求失败:', error)
      
      // 如果是401错误，清除认证状态
      if (error.response?.status === 401) {
        this.clearAuthState()
      }
      
      return false
    }
  }

  /**
   * 刷新token
   */
  async refreshToken() {
    try {
      const response = await api.post('/accounts/auth/refresh-token/')
      const { token, expires_in } = response.data
      
      if (token) {
        this.authState.token = token
        localStorage.setItem('token', token)
        
        // 重新调度token刷新
        if (expires_in) {
          this.scheduleTokenRefresh(expires_in * 1000)
        }
        
        console.log('Token刷新成功')
        return true
      }
      
      return false
    } catch (error) {
      console.error('Token刷新失败:', error)
      this.clearAuthState()
      return false
    }
  }

  /**
   * 调度token刷新
   */
  scheduleTokenRefresh(expiresIn) {
    // 在token过期前5分钟刷新
    const refreshTime = Math.max(expiresIn - 5 * 60 * 1000, 60 * 1000)
    
    if (this.authState.refreshTokenTimeout) {
      clearTimeout(this.authState.refreshTokenTimeout)
    }
    
    this.authState.refreshTokenTimeout = setTimeout(() => {
      this.refreshToken()
    }, refreshTime)
  }

  /**
   * 启动会话检查
   */
  startSessionCheck() {
    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval)
    }
    
    this.sessionCheckInterval = setInterval(() => {
      this.checkSession()
    }, 60 * 1000) // 每分钟检查一次
  }

  /**
   * 检查会话状态
   */
  checkSession() {
    if (!this.authState.isAuthenticated) {
      return
    }
    
    const now = Date.now()
    const timeSinceLastActivity = now - this.authState.lastActivity
    
    // 检查会话是否超时
    if (timeSinceLastActivity > this.authState.sessionTimeout) {
      console.warn('会话超时，自动登出')
      this.logout()
      
      // 显示会话超时提示
      this.notifyAuthChange('session_timeout', null)
    }
  }

  /**
   * 更新最后活动时间
   */
  updateLastActivity() {
    this.authState.lastActivity = Date.now()
  }

  /**
   * 获取认证状态
   */
  getAuthState() {
    return { ...this.authState }
  }

  /**
   * 检查是否已认证
   */
  isAuthenticated() {
    return this.authState.isAuthenticated && this.authState.token && this.authState.user
  }

  /**
   * 获取当前用户
   */
  getCurrentUser() {
    return this.authState.user
  }

  /**
   * 获取当前token
   */
  getToken() {
    return this.authState.token
  }

  /**
   * 添加认证状态监听器
   */
  addAuthListener(callback) {
    if (typeof callback === 'function') {
      this.authListeners.push(callback)
    }
  }

  /**
   * 移除认证状态监听器
   */
  removeAuthListener(callback) {
    const index = this.authListeners.indexOf(callback)
    if (index > -1) {
      this.authListeners.splice(index, 1)
    }
  }

  /**
   * 通知认证状态变化
   */
  notifyAuthChange(event, user) {
    this.authListeners.forEach(callback => {
      try {
        callback(event, user, this.authState)
      } catch (error) {
        console.error('认证状态监听器执行失败:', error)
      }
    })
  }

  /**
   * 设置会话超时时间
   */
  setSessionTimeout(timeout) {
    this.authState.sessionTimeout = timeout
  }

  /**
   * 获取会话剩余时间
   */
  getSessionRemainingTime() {
    if (!this.authState.isAuthenticated) {
      return 0
    }
    
    const elapsed = Date.now() - this.authState.lastActivity
    return Math.max(this.authState.sessionTimeout - elapsed, 0)
  }

  /**
   * 延长会话
   */
  extendSession() {
    if (this.authState.isAuthenticated) {
      this.updateLastActivity()
      console.log('会话已延长')
    }
  }
}

const authStateManager = new AuthStateManager()

// 全局暴露
if (typeof window !== 'undefined') {
  window.authStateManager = authStateManager
  
  // 监听页面活动，更新最后活动时间
  const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
  
  activityEvents.forEach(event => {
    document.addEventListener(event, () => {
      authStateManager.updateLastActivity()
    }, { passive: true })
  })
  
  // 监听页面可见性变化
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && authStateManager.isAuthenticated()) {
      // 页面重新可见时验证token
      authStateManager.verifyToken()
    }
  })
}

export default authStateManager

export const {
  login,
  logout,
  isAuthenticated,
  getCurrentUser,
  getToken,
  addAuthListener,
  removeAuthListener,
  extendSession,
  getSessionRemainingTime
} = authStateManager