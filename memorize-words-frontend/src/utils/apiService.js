/**
 * API 服务模块
 * 统一管理与后端的API交互
 */

class ApiService {
  constructor() {
    // 根据环境配置API基础URL
    this.baseURL = this.getBaseURL()
    this.timeout = 10000 // 10秒超时
  }

  /**
   * 获取API基础URL
   */
  getBaseURL() {
    // #ifdef H5
    return 'http://127.0.0.1:8001/api'
    // #endif
    
    // #ifdef MP-WEIXIN || MP-ALIPAY
    return 'https://your-domain.com/api'
    // #endif
    
    // #ifdef APP-PLUS
    return 'https://your-domain.com/api'
    // #endif
    
    return 'http://127.0.0.1:8001/api' // 默认开发环境
  }

  /**
   * 通用请求方法
   */
  async request(options) {
    const {
      url,
      method = 'GET',
      data = {},
      header = {},
      showLoading = false
    } = options

    if (showLoading) {
      uni.showLoading({ title: '加载中...' })
    }

    try {
      const token = uni.getStorageSync('access_token')
      const defaultHeader = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }

      const response = await new Promise((resolve, reject) => {
        uni.request({
          url: `${this.baseURL}${url}`,
          method,
          data,
          header: { ...defaultHeader, ...header },
          timeout: this.timeout,
          success: resolve,
          fail: reject
        })
      })

      if (showLoading) {
        uni.hideLoading()
      }

      // 处理响应
      if (response.statusCode === 200) {
        return response.data
      } else if (response.statusCode === 401) {
        // Token过期，清除本地存储并跳转登录
        this.handleUnauthorized()
        throw new Error('登录已过期，请重新登录')
      } else {
        throw new Error(response.data?.message || `请求失败: ${response.statusCode}`)
      }
    } catch (error) {
      if (showLoading) {
        uni.hideLoading()
      }
      console.error('API请求错误:', error)
      throw error
    }
  }

  /**
   * 处理未授权情况
   */
  handleUnauthorized() {
    uni.removeStorageSync('access_token')
    uni.removeStorageSync('user_info')
    uni.removeStorageSync('menu_cache')
    
    // 跳转到登录页面
    uni.reLaunch({
      url: '/pages/auth/login'
    })
  }

  /**
   * GET请求
   */
  get(url, params = {}, options = {}) {
    const queryString = Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&')
    
    const fullUrl = queryString ? `${url}?${queryString}` : url
    
    return this.request({
      url: fullUrl,
      method: 'GET',
      ...options
    })
  }

  /**
   * POST请求
   */
  post(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'POST',
      data,
      ...options
    })
  }

  /**
   * PUT请求
   */
  put(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'PUT',
      data,
      ...options
    })
  }

  /**
   * DELETE请求
   */
  delete(url, options = {}) {
    return this.request({
      url,
      method: 'DELETE',
      ...options
    })
  }
}

// 菜单相关API
class MenuApiService extends ApiService {
  /**
   * 获取用户可访问的前台菜单列表
   */
  async getFrontendMenusForUser(userId) {
    try {
      const response = await this.get('/permissions/get_frontend_menus_for_user/', {
        user_id: userId
      })
      return response
    } catch (error) {
      console.error('获取用户菜单失败:', error)
      throw error
    }
  }

  /**
   * 根据位置获取菜单
   */
  async getMenuByPosition(position) {
    try {
      const response = await this.get('/permissions/get_menu_by_position/', {
        position
      })
      return response
    } catch (error) {
      console.error('根据位置获取菜单失败:', error)
      throw error
    }
  }

  /**
   * 检查用户对特定菜单的访问权限
   */
  async checkMenuAccess(userId, menuId) {
    try {
      const response = await this.get('/permissions/check_menu_access/', {
        user_id: userId,
        menu_id: menuId
      })
      return response
    } catch (error) {
      console.error('检查菜单访问权限失败:', error)
      throw error
    }
  }

  /**
   * 获取用户菜单配置（兼容旧接口）
   */
  async getUserMenus(userId) {
    try {
      const response = await this.get('/permissions/menu-modules/user_menus/', {
        user_id: userId
      })
      return response
    } catch (error) {
      console.error('获取用户菜单配置失败:', error)
      throw error
    }
  }
}

// 创建实例
const apiService = new ApiService()
const menuApiService = new MenuApiService()

export default apiService
export { menuApiService }

// 导出常用方法
export const {
  get,
  post,
  put,
  delete: deleteRequest
} = apiService