/**
 * 菜单数据服务
 * 负责菜单数据的获取、缓存和管理
 */

import { MENU_ITEMS, CACHE_CONFIG } from '../config/menuConfig.js'
import permissionService from './PermissionService.js'
import api from '../utils/api.js'

class MenuDataService {
  constructor() {
    this.menuCache = new Map()
    this.cacheTimestamps = new Map()
    this.isLoading = false
    this.initialized = false
  }

  /**
   * 初始化菜单数据服务
   */
  async init() {
    if (this.initialized) {
      console.log('菜单数据服务已初始化')
      return
    }

    try {
      console.log('🍽️ 初始化菜单数据服务...')
      
      // 清理过期缓存
      this.clearExpiredCache()
      
      this.initialized = true
      console.log('✅ 菜单数据服务初始化完成')
    } catch (error) {
      console.error('❌ 菜单数据服务初始化失败:', error)
      this.initialized = false
      throw error
    }
  }

  /**
   * 清理过期缓存
   */
  clearExpiredCache() {
    const now = Date.now()
    for (const [key, timestamp] of this.cacheTimestamps.entries()) {
      if (now - timestamp > CACHE_CONFIG.MENU_CACHE_DURATION) {
        this.menuCache.delete(key)
        this.cacheTimestamps.delete(key)
      }
    }
  }

  /**
   * 获取用户可访问的菜单
   * @param {string} userRole - 用户角色
   * @param {string} category - 菜单分类（可选）
   * @returns {Promise<Array>} 菜单列表
   */
  async getUserMenus(userRole, category = null) {
    const cacheKey = `user_menus_${userRole}_${category || 'all'}`
    
    // 检查缓存
    if (this.isCacheValid(cacheKey)) {
      return this.menuCache.get(cacheKey)
    }

    try {
      // 尝试从后端获取菜单数据
      const backendMenus = await this.fetchMenusFromBackend(userRole)
      
      if (backendMenus && backendMenus.length > 0) {
        const filteredMenus = this.filterMenusByCategory(backendMenus, category)
        this.cacheMenus(cacheKey, filteredMenus)
        return filteredMenus
      }
    } catch (error) {
      console.warn('从后端获取菜单失败，使用本地配置:', error)
    }

    // 后端获取失败，使用本地配置
    const localMenus = this.getLocalMenus(userRole, category)
    this.cacheMenus(cacheKey, localMenus)
    return localMenus
  }

  /**
   * 从后端获取菜单数据
   * @param {string} userRole - 用户角色
   * @returns {Promise<Array>} 菜单数据
   */
  async fetchMenusFromBackend(userRole) {
    if (this.isLoading) {
      // 避免重复请求
      await this.waitForLoading()
      return this.menuCache.get(`backend_menus_${userRole}`)
    }

    this.isLoading = true
    
    try {
      const user = permissionService.getCurrentUser()
      if (!user || !permissionService.isAuthenticated()) {
        throw new Error('用户未认证')
      }

      const response = await api.get('/accounts/menus/')

      // 处理响应拦截器返回的数据格式
      const data = response.data || response
      if (data && Array.isArray(data)) {
        const cacheKey = `backend_menus_${userRole}`
        this.cacheMenus(cacheKey, data)
        return data
      }
      
      throw new Error('后端返回的菜单数据格式无效')
    } catch (error) {
      console.error('获取后端菜单数据失败:', error)
      throw error
    } finally {
      this.isLoading = false
    }
  }

  /**
   * 等待加载完成
   * @returns {Promise}
   */
  async waitForLoading() {
    return new Promise((resolve) => {
      const checkLoading = () => {
        if (!this.isLoading) {
          resolve()
        } else {
          setTimeout(checkLoading, 100)
        }
      }
      checkLoading()
    })
  }

  /**
   * 获取本地菜单配置
   * @param {string} userRole - 用户角色
   * @param {string} category - 菜单分类
   * @returns {Array} 菜单列表
   */
  getLocalMenus(userRole, category) {
    let menus = []
    
    if (category) {
      menus = MENU_ITEMS[category.toUpperCase() + '_MENUS'] || []
    } else {
      // 获取所有菜单
      menus = [
        ...MENU_ITEMS.MAIN_MENUS,
        ...MENU_ITEMS.BOTTOM_MENUS
      ]
    }

    // 根据权限过滤菜单
    return this.filterMenusByPermission(menus, userRole)
  }

  /**
   * 根据分类过滤菜单
   * @param {Array} menus - 菜单列表
   * @param {string} category - 分类
   * @returns {Array} 过滤后的菜单
   */
  filterMenusByCategory(menus, category) {
    if (!category) return menus
    return menus.filter(menu => menu.category === category)
  }

  /**
   * 根据权限过滤菜单
   * @param {Array} menus - 菜单列表
   * @param {string} userRole - 用户角色
   * @returns {Array} 过滤后的菜单
   */
  filterMenusByPermission(menus, userRole) {
    return menus.filter(menu => {
      if (!menu.permission) return true
      return permissionService.hasPermission(userRole, menu.permission)
    }).map(menu => {
      // 处理子菜单
      if (menu.children && typeof menu.children === 'string') {
        const childMenus = MENU_ITEMS[menu.children] || []
        menu.children = this.filterMenusByPermission(childMenus, userRole)
      }
      return menu
    })
  }

  /**
   * 构建菜单树结构
   * @param {Array} menus - 菜单列表
   * @returns {Array} 菜单树
   */
  buildMenuTree(menus) {
    const menuMap = new Map()
    const rootMenus = []

    // 创建菜单映射
    menus.forEach(menu => {
      menuMap.set(menu.id, { ...menu, children: [] })
    })

    // 构建树结构
    menus.forEach(menu => {
      const menuItem = menuMap.get(menu.id)
      
      if (menu.parentId && menuMap.has(menu.parentId)) {
        menuMap.get(menu.parentId).children.push(menuItem)
      } else {
        rootMenus.push(menuItem)
      }
    })

    // 按排序字段排序
    return this.sortMenus(rootMenus)
  }

  /**
   * 菜单排序
   * @param {Array} menus - 菜单列表
   * @returns {Array} 排序后的菜单
   */
  sortMenus(menus) {
    return menus.sort((a, b) => {
      const orderA = a.sortOrder || 999
      const orderB = b.sortOrder || 999
      return orderA - orderB
    }).map(menu => {
      if (menu.children && menu.children.length > 0) {
        menu.children = this.sortMenus(menu.children)
      }
      return menu
    })
  }

  /**
   * 获取特定类型的菜单
   * @param {string} menuType - 菜单类型
   * @param {string} userRole - 用户角色
   * @returns {Array} 菜单列表
   */
  async getMenusByType(menuType, userRole) {
    const cacheKey = `${menuType}_menus_${userRole}`
    
    if (this.isCacheValid(cacheKey)) {
      return this.menuCache.get(cacheKey)
    }

    let menus = []
    
    switch (menuType) {
      case 'bottom':
        menus = await this.getUserMenus(userRole, 'bottom')
        break
      case 'main':
        menus = await this.getUserMenus(userRole, 'main')
        break
      case 'tools':
        menus = this.getLocalMenus(userRole, 'tool')
        break
      case 'fashion':
        menus = this.getLocalMenus(userRole, 'fashion')
        break
      case 'dev':
        menus = this.getLocalMenus(userRole, 'dev')
        break
      default:
        menus = await this.getUserMenus(userRole)
    }

    this.cacheMenus(cacheKey, menus)
    return menus
  }

  /**
   * 获取开发工具菜单
   * @param {string} userRole - 用户角色
   * @returns {Array} 开发工具菜单
   */
  getDevToolMenus(userRole) {
    const devTools = MENU_ITEMS.DEV_TOOLS || []
    return this.filterMenusByPermission(devTools, userRole)
  }

  /**
   * 更新菜单项状态
   * @param {string} menuId - 菜单ID
   * @param {Object} updates - 更新内容
   */
  updateMenuStatus(menuId, updates) {
    // 清除相关缓存
    this.clearCacheByPattern(`*${menuId}*`)
    
    // 触发菜单更新事件
    this.notifyMenuUpdate(menuId, updates)
  }

  /**
   * 缓存菜单数据
   * @param {string} key - 缓存键
   * @param {Array} menus - 菜单数据
   */
  cacheMenus(key, menus) {
    this.menuCache.set(key, menus)
    this.cacheTimestamps.set(key, Date.now())
  }

  /**
   * 检查缓存是否有效
   * @param {string} key - 缓存键
   * @returns {boolean} 是否有效
   */
  isCacheValid(key) {
    const timestamp = this.cacheTimestamps.get(key)
    if (!timestamp) return false
    
    return Date.now() - timestamp < CACHE_CONFIG.MENU_CACHE_DURATION
  }

  /**
   * 清除缓存
   * @param {string} pattern - 缓存键模式
   */
  clearCacheByPattern(pattern) {
    const regex = new RegExp(pattern.replace(/\*/g, '.*'))
    
    for (const key of this.menuCache.keys()) {
      if (regex.test(key)) {
        this.menuCache.delete(key)
        this.cacheTimestamps.delete(key)
      }
    }
  }

  /**
   * 清除所有缓存
   */
  clearAllCache() {
    this.menuCache.clear()
    this.cacheTimestamps.clear()
  }

  /**
   * 菜单更新监听器
   */
  menuUpdateListeners = []

  /**
   * 添加菜单更新监听器
   * @param {Function} callback - 回调函数
   */
  addMenuUpdateListener(callback) {
    this.menuUpdateListeners.push(callback)
  }

  /**
   * 移除菜单更新监听器
   * @param {Function} callback - 回调函数
   */
  removeMenuUpdateListener(callback) {
    const index = this.menuUpdateListeners.indexOf(callback)
    if (index > -1) {
      this.menuUpdateListeners.splice(index, 1)
    }
  }

  /**
   * 通知菜单更新
   * @param {string} menuId - 菜单ID
   * @param {Object} updates - 更新内容
   */
  notifyMenuUpdate(menuId, updates) {
    this.menuUpdateListeners.forEach(callback => {
      try {
        callback(menuId, updates)
      } catch (error) {
        console.error('菜单更新监听器执行失败:', error)
      }
    })
  }
}

// 创建单例实例
const menuDataService = new MenuDataService()

// 监听权限变更，清除菜单缓存
if (typeof window !== 'undefined') {
  permissionService.addPermissionListener(() => {
    menuDataService.clearAllCache()
  })

  // 将菜单数据服务暴露到全局
  window.menuDataService = menuDataService
}

export default menuDataService

// 导出常用方法
export const {
  getUserMenus,
  getMenusByType,
  getDevToolMenus,
  updateMenuStatus,
  addMenuUpdateListener,
  removeMenuUpdateListener
} = menuDataService