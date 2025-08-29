/**
 * Uni-App 菜单管理器
 * 适配多端平台的菜单配置和权限控制
 */

import { MENU_ITEMS, PAGE_PERMISSIONS, ROLE_PERMISSION_INHERITANCE, PLATFORM_CONFIG } from '@/config/menuConfig.js'
import { menuApiService } from '@/utils/apiService.js'

class MenuManager {
  constructor() {
    this.cacheExpiry = 5 * 60 * 1000 // 5分钟缓存
    this.version = '1.0.0'
    this.currentPlatform = this.getCurrentPlatform()
    this.useBackendApi = true // 是否使用后端API
    this.fallbackToLocal = true // API失败时是否回退到本地配置
  }

  /**
   * 获取当前运行平台
   */
  getCurrentPlatform() {
    // #ifdef H5
    return 'h5'
    // #endif
    
    // #ifdef MP-WEIXIN
    return 'mp-weixin'
    // #endif
    
    // #ifdef APP-PLUS
    return 'app'
    // #endif
    
    // #ifdef MP-ALIPAY
    return 'mp-alipay'
    // #endif
    
    return 'h5' // 默认H5
  }

  /**
   * 清除菜单相关缓存
   */
  clearCache() {
    try {
      uni.removeStorageSync('menu_cache')
      uni.removeStorageSync('permission_cache')
      uni.removeStorageSync('user_menus_cache')
    } catch (e) {
      console.error('清除缓存失败:', e)
    }
  }

  /**
   * 设置缓存
   */
  setCache(key, data, expiry = this.cacheExpiry) {
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
        expiry,
        version: this.version
      }
      uni.setStorageSync(key, cacheData)
    } catch (e) {
      console.error('设置缓存失败:', e)
    }
  }

  /**
   * 获取缓存
   */
  getCache(key) {
    try {
      const cacheData = uni.getStorageSync(key)
      if (!cacheData) return null
      
      const { data, timestamp, expiry, version } = cacheData
      
      // 检查版本
      if (version !== this.version) {
        uni.removeStorageSync(key)
        return null
      }
      
      // 检查过期时间
      if (Date.now() - timestamp > expiry) {
        uni.removeStorageSync(key)
        return null
      }
      
      return data
    } catch (e) {
      console.error('获取缓存失败:', e)
      return null
    }
  }

  /**
   * 获取当前用户信息
   */
  getCurrentUser() {
    try {
      return uni.getStorageSync('user_info') || null
    } catch (e) {
      console.error('获取用户信息失败:', e)
      return null
    }
  }

  /**
   * 检查用户是否已认证
   */
  isAuthenticated() {
    const user = this.getCurrentUser()
    const token = uni.getStorageSync('access_token')
    return !!(user && token)
  }

  /**
   * 获取用户角色
   */
  getUserRole() {
    const user = this.getCurrentUser()
    return user?.role || 'student'
  }

  /**
   * 获取用户权限列表
   */
  getUserPermissions() {
    const role = this.getUserRole()
    const permissions = ROLE_PERMISSION_INHERITANCE[role] || []
    
    // 处理权限继承
    const expandedPermissions = new Set()
    
    permissions.forEach(permission => {
      if (permission === '*') {
        // 管理员拥有所有权限
        Object.values(ROLE_PERMISSION_INHERITANCE).forEach(rolePerms => {
          rolePerms.forEach(perm => {
            if (perm !== '*') expandedPermissions.add(perm)
          })
        })
      } else if (ROLE_PERMISSION_INHERITANCE[permission]) {
        // 角色继承
        ROLE_PERMISSION_INHERITANCE[permission].forEach(perm => {
          expandedPermissions.add(perm)
        })
      } else {
        expandedPermissions.add(permission)
      }
    })
    
    return Array.from(expandedPermissions)
  }

  /**
   * 检查用户是否有指定权限
   */
  hasPermission(permission) {
    if (!this.isAuthenticated()) return false
    
    const userPermissions = this.getUserPermissions()
    return userPermissions.includes(permission)
  }

  /**
   * 检查页面访问权限
   */
  checkPagePermission(path) {
    const permission = PAGE_PERMISSIONS[path]
    if (!permission) return true // 没有配置权限要求的页面默认允许访问
    
    return this.hasPermission(permission)
  }

  /**
   * 过滤菜单项（根据权限和平台）
   */
  filterMenuItems(menuItems) {
    if (!Array.isArray(menuItems)) return []
    
    return menuItems.filter(menu => {
      // 检查权限
      if (menu.permission && !this.hasPermission(menu.permission)) {
        return false
      }
      
      // 检查平台支持
      if (menu.platforms && !menu.platforms.includes(this.currentPlatform)) {
        return false
      }
      
      return true
    }).sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
  }

  /**
   * 获取主菜单
   */
  async getMainMenus() {
    const cacheKey = 'main_menus_cache'
    const cached = this.getCache(cacheKey)
    if (cached) return cached
    
    let mainMenus = []
    
    if (this.useBackendApi && this.isAuthenticated()) {
      try {
        const user = this.getCurrentUser()
        const backendMenus = await this.getBackendMenusByPosition('main')
        mainMenus = this.transformBackendMenus(backendMenus)
      } catch (error) {
        console.warn('获取后端主菜单失败，使用本地配置:', error)
        if (this.fallbackToLocal) {
          mainMenus = this.filterMenuItems(MENU_ITEMS.MAIN_MENUS)
        }
      }
    } else {
      mainMenus = this.filterMenuItems(MENU_ITEMS.MAIN_MENUS)
    }
    
    this.setCache(cacheKey, mainMenus)
    return mainMenus
  }

  /**
   * 获取底部导航菜单
   */
  async getBottomMenus() {
    const cacheKey = 'bottom_menus_cache'
    const cached = this.getCache(cacheKey)
    if (cached) return cached
    
    let bottomMenus = []
    
    if (this.useBackendApi && this.isAuthenticated()) {
      try {
        const backendMenus = await this.getBackendMenusByPosition('bottom')
        bottomMenus = this.transformBackendMenus(backendMenus)
      } catch (error) {
        console.warn('获取后端底部菜单失败，使用本地配置:', error)
        if (this.fallbackToLocal) {
          bottomMenus = this.filterMenuItems(MENU_ITEMS.BOTTOM_MENUS)
        }
      }
    } else {
      bottomMenus = this.filterMenuItems(MENU_ITEMS.BOTTOM_MENUS)
    }
    
    // 根据平台限制底部导航数量
    const platformConfig = PLATFORM_CONFIG[this.currentPlatform]
    if (platformConfig?.maxTabBarItems) {
      bottomMenus = bottomMenus.slice(0, platformConfig.maxTabBarItems)
    }
    
    this.setCache(cacheKey, bottomMenus)
    return bottomMenus
  }

  /**
   * 获取工具菜单
   */
  getToolMenus() {
    const cacheKey = 'tool_menus_cache'
    const cached = this.getCache(cacheKey)
    if (cached) return cached
    
    const toolMenus = this.filterMenuItems(MENU_ITEMS.TOOL_MENUS)
    this.setCache(cacheKey, toolMenus)
    
    return toolMenus
  }

  /**
   * 获取时尚菜单
   */
  getFashionMenus() {
    const cacheKey = 'fashion_menus_cache'
    const cached = this.getCache(cacheKey)
    if (cached) return cached
    
    const fashionMenus = this.filterMenuItems(MENU_ITEMS.FASHION_MENUS)
    this.setCache(cacheKey, fashionMenus)
    
    return fashionMenus
  }

  /**
   * 获取开发工具菜单
   */
  getDevTools() {
    const cacheKey = 'dev_tools_cache'
    const cached = this.getCache(cacheKey)
    if (cached) return cached
    
    const devTools = this.filterMenuItems(MENU_ITEMS.DEV_TOOLS)
    this.setCache(cacheKey, devTools)
    
    return devTools
  }

  /**
   * 生成Uni-App tabBar配置
   */
  generateTabBarConfig() {
    const bottomMenus = this.getBottomMenus()
    
    return {
      color: '#7A7E83',
      selectedColor: '#007AFF',
      borderStyle: 'black',
      backgroundColor: '#ffffff',
      list: bottomMenus.map(menu => ({
        pagePath: menu.path.replace(/^\//, ''), // 移除开头的斜杠
        iconPath: `/static/icons/${menu.icon}.png`,
        selectedIconPath: `/static/icons/${menu.selectedIcon || menu.icon}-active.png`,
        text: menu.title
      }))
    }
  }

  /**
   * 导航到指定页面
   */
  navigateTo(path, params = {}) {
    // 检查页面权限
    if (!this.checkPagePermission(path)) {
      uni.showToast({
        title: '没有访问权限',
        icon: 'none'
      })
      return false
    }
    
    // 构建URL
    let url = path
    if (Object.keys(params).length > 0) {
      const query = Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')
      url += `?${query}`
    }
    
    // 判断是否为tabBar页面
    const bottomMenus = this.getBottomMenus()
    const isTabBarPage = bottomMenus.some(menu => menu.path === path)
    
    if (isTabBarPage) {
      uni.switchTab({ url })
    } else {
      uni.navigateTo({ url })
    }
    
    return true
  }

  /**
   * 获取当前页面菜单信息
   */
  getCurrentPageMenu() {
    const pages = getCurrentPages()
    if (pages.length === 0) return null
    
    const currentPage = pages[pages.length - 1]
    const currentPath = `/${currentPage.route}`
    
    const allMenus = [
      ...this.getMainMenus(),
      ...this.getBottomMenus(),
      ...this.getToolMenus(),
      ...this.getFashionMenus(),
      ...this.getDevTools()
    ]
    
    return allMenus.find(menu => menu.path === currentPath) || null
  }

  /**
   * 从后端API获取指定位置的菜单
   */
  async getBackendMenusByPosition(position) {
    try {
      const response = await menuApiService.getMenuByPosition(position)
      return response.data || []
    } catch (error) {
      console.error('获取后端菜单失败:', error)
      throw error
    }
  }

  /**
   * 获取用户的所有前台菜单
   */
  async getUserFrontendMenus() {
    try {
      const user = this.getCurrentUser()
      if (!user?.id) {
        throw new Error('用户信息不完整')
      }
      
      const response = await menuApiService.getFrontendMenusForUser(user.id)
      return response.data || []
    } catch (error) {
      console.error('获取用户前台菜单失败:', error)
      throw error
    }
  }

  /**
   * 检查用户对菜单的访问权限
   */
  async checkBackendMenuAccess(menuId) {
    try {
      const user = this.getCurrentUser()
      if (!user?.id) {
        return false
      }
      
      const response = await menuApiService.checkMenuAccess(user.id, menuId)
      return response.has_access || false
    } catch (error) {
      console.error('检查菜单访问权限失败:', error)
      return false
    }
  }

  /**
   * 转换后端菜单数据格式为前端格式
   */
  transformBackendMenus(backendMenus) {
    if (!Array.isArray(backendMenus)) return []
    
    return backendMenus.map(menu => ({
      id: menu.id,
      title: menu.title,
      path: menu.url || menu.path,
      icon: menu.icon || 'default',
      selectedIcon: menu.selected_icon || menu.icon || 'default',
      permission: menu.permission_code,
      sortOrder: menu.sort_order || 0,
      platforms: menu.platforms ? menu.platforms.split(',') : ['h5', 'mp-weixin', 'app'],
      isActive: menu.is_active !== false,
      description: menu.description,
      // 处理子菜单
      children: menu.children ? this.transformBackendMenus(menu.children) : [],
      // 后端特有字段
      menuType: menu.menu_type,
      position: menu.position,
      startTime: menu.start_time,
      endTime: menu.end_time
    })).filter(menu => menu.isActive)
      .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
  }

  /**
   * 刷新菜单缓存
   */
  async refreshMenus() {
    this.clearCache()
    // 重新获取菜单数据
    try {
      await Promise.all([
        this.getMainMenus(),
        this.getBottomMenus(),
        this.getToolMenus(),
        this.getFashionMenus(),
        this.getDevTools()
      ])
    } catch (error) {
      console.error('刷新菜单失败:', error)
    }
  }

  /**
   * 设置API使用模式
   */
  setApiMode(useBackendApi, fallbackToLocal = true) {
    this.useBackendApi = useBackendApi
    this.fallbackToLocal = fallbackToLocal
    this.clearCache() // 清除缓存以重新获取数据
  }
}

// 创建单例实例
const menuManager = new MenuManager()

export default menuManager

// 导出常用方法
export const {
  hasPermission,
  checkPagePermission,
  getMainMenus,
  getBottomMenus,
  getToolMenus,
  getFashionMenus,
  getDevTools,
  navigateTo,
  getCurrentPageMenu,
  generateTabBarConfig,
  refreshMenus,
  getUserFrontendMenus,
  checkBackendMenuAccess,
  setApiMode
} = menuManager