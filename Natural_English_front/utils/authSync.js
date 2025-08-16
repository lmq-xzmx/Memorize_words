/**
 * 前后端登录状态同步工具
 * 解决前端权限验证与后端登录状态不一致的问题
 */

// 导入清除认证缓存函数
import { clearAuthCache } from './permission.js'
// 导入统一的API配置
import { buildApiUrl, API_ENDPOINTS } from '../config/apiConfig.js'

// 获取CSRF Token
function getCsrfToken() {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrftoken') {
      return value
    }
  }
  return null
}

/**
 * 验证后端登录状态
 * @returns {Promise<boolean>} 是否已在后端登录
 */
export async function verifyBackendAuth() {
  try {
    const url = buildApiUrl(API_ENDPOINTS.AUTH.VERIFY)
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include', // 包含cookies
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken() || ''
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      return data.authenticated === true
    }
    
    return false
  } catch (error) {
    console.error('验证后端登录状态失败:', error)
    return false
  }
}

/**
 * 从后端获取用户信息
 * @returns {Promise<Object|null>} 用户信息或null
 */
export async function fetchUserFromBackend() {
  try {
    const url = buildApiUrl(API_ENDPOINTS.AUTH.USER_CURRENT)
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken() || ''
      }
    })
    
    if (response.ok) {
      const userData = await response.json()
      return {
        id: userData.id,
        username: userData.username,
        real_name: userData.real_name || userData.username,
        role: userData.role,
        email: userData.email
      }
    }
    
    return null
  } catch (error) {
    console.error('获取后端用户信息失败:', error)
    return null
  }
}

/**
 * 同步前后端登录状态
 * @returns {Promise<Object>} 同步结果
 */
export async function syncAuthState() {
  try {
    // 检查前端localStorage中的登录状态
    const frontendToken = localStorage.getItem('token')
    const frontendUser = localStorage.getItem('user')
    
    // 验证后端登录状态
    const backendAuthenticated = await verifyBackendAuth()
    
    console.log('登录状态同步检查:', {
      frontendToken: !!frontendToken,
      frontendUser: !!frontendUser,
      backendAuthenticated
    })
    
    if (backendAuthenticated) {
      // 后端已登录，获取用户信息
      const backendUser = await fetchUserFromBackend()
      
      if (backendUser) {
        // 更新前端localStorage
        if (!frontendToken) {
          // 生成临时token（实际项目中应该从后端获取）
          const tempToken = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
          localStorage.setItem('token', tempToken)
        }
        
        localStorage.setItem('user', JSON.stringify(backendUser))
        
        // 清除认证缓存
        clearAuthCache()
        
        // 触发权限变更事件
        if (window.permissionWatcher) {
          window.permissionWatcher.notifyChange(backendUser)
        }
        
        return {
          success: true,
          authenticated: true,
          user: backendUser,
          message: '登录状态已同步'
        }
      }
    } else {
      // 后端未登录，清除前端状态
      if (frontendToken || frontendUser) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        // 清除认证缓存
        clearAuthCache()
        
        // 触发权限变更事件
        if (window.permissionWatcher) {
          window.permissionWatcher.notifyChange(null)
        }
        
        return {
          success: true,
          authenticated: false,
          user: null,
          message: '前端登录状态已清除，与后端保持一致'
        }
      }
    }
    
    return {
      success: true,
      authenticated: backendAuthenticated,
      user: backendAuthenticated ? JSON.parse(frontendUser || '{}') : null,
      message: '登录状态已同步'
    }
    
  } catch (error) {
    console.error('同步登录状态失败:', error)
    return {
      success: false,
      authenticated: false,
      user: null,
      message: `同步失败: ${error.message}`
    }
  }
}

/**
 * 初始化登录状态同步
 * 在应用启动时调用
 */
export async function initAuthSync() {
  console.log('初始化登录状态同步...')
  const result = await syncAuthState()
  console.log('登录状态同步结果:', result)
  return result
}

/**
 * 定期同步登录状态
 * @param {number} interval 同步间隔（毫秒），默认5分钟
 */
export function startAuthSyncInterval(interval = 5 * 60 * 1000) {
  return setInterval(async () => {
    console.log('定期同步登录状态...')
    await syncAuthState()
  }, interval)
}

/**
 * 手动触发登录状态同步
 * 在用户操作后调用
 */
export async function manualSyncAuth() {
  console.log('手动同步登录状态...')
  const result = await syncAuthState()
  
  if (result.success && result.authenticated) {
    console.log('登录状态同步成功，用户已登录')
  } else if (result.success && !result.authenticated) {
    console.log('登录状态同步成功，用户未登录')
  } else {
    console.error('登录状态同步失败:', result.message)
  }
  
  return result
}

export default {
  verifyBackendAuth,
  fetchUserFromBackend,
  syncAuthState,
  initAuthSync,
  startAuthSyncInterval,
  manualSyncAuth
}