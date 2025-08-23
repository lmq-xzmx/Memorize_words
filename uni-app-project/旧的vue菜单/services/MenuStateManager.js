/**
 * 菜单状态管理器
 * 负责菜单状态的统一管理和持久化
 */

import { reactive, watch } from 'vue'
import permissionService from './PermissionService.js'
import menuDataService from './MenuDataService.js'

class MenuStateManager {
  constructor() {
    // 响应式状态
    this.state = reactive({
      // 用户信息
      currentUser: null,
      userRole: null,
      isAuthenticated: false,
      
      // 菜单状态
      activeMenu: null,
      expandedMenus: new Set(),
      enabledDevTools: new Set(),
      
      // UI状态
      sidebarCollapsed: false,
      bottomMenuVisible: true,
      activeBottomMenu: null,
      
      // 菜单数据
      mainMenus: [],
      bottomMenus: [],
      toolMenus: [],
      fashionMenus: [],
      devToolMenus: [],
      
      // 加载状态
      isLoading: false,
      pageLoading: false,
      error: null,
      
      // 通知状态
      notifications: []
    })

    // 初始化
    this.init()
  }

  /**
   * 初始化状态管理器
   */
  async init() {
    try {
      // 恢复持久化状态
      this.restorePersistedState()
      
      // 更新用户信息
      await this.updateUserInfo()
      
      // 加载菜单数据
      await this.loadMenus()
      
      // 监听权限变更
      permissionService.addPermissionListener(this.handlePermissionChange.bind(this))
      
      // 监听菜单更新
      menuDataService.addMenuUpdateListener(this.handleMenuUpdate.bind(this))
      
      // 设置状态持久化监听
      this.setupStatePersistence()
      
    } catch (error) {
      console.error('菜单状态管理器初始化失败:', error)
      this.state.error = error.message
    }
  }

  /**
   * 初始化用户相关状态
   * @param {Object} user - 用户信息
   */
  async initializeUser(user) {
    try {
      console.log('🔄 初始化用户菜单状态...', user?.username)
      
      this.state.currentUser = user
      this.state.userRole = user?.role || null
      this.state.isAuthenticated = true
      
      // 加载用户菜单数据
      await this.loadMenus()
      
      console.log('✅ 用户菜单状态初始化完成')
    } catch (error) {
      console.error('❌ 用户菜单状态初始化失败:', error)
      this.state.error = error.message
      throw error
    }
  }

  /**
   * 更新用户信息
   */
  async updateUserInfo() {
    const user = permissionService.getCurrentUser()
    const isAuthenticated = permissionService.isAuthenticated()
    
    this.state.currentUser = user
    this.state.userRole = user?.role || null
    this.state.isAuthenticated = isAuthenticated
    
    if (!isAuthenticated) {
      this.clearMenuData()
    }
  }

  /**
   * 加载菜单数据
   */
  async loadMenus() {
    if (!this.state.userRole) {
      this.clearMenuData()
      return
    }

    this.state.isLoading = true
    this.state.error = null

    try {
      // 并行加载各类菜单
      const [mainMenus, bottomMenus, toolMenus, fashionMenus, devToolMenus] = await Promise.all([
        menuDataService.getMenusByType('main', this.state.userRole),
        menuDataService.getMenusByType('bottom', this.state.userRole),
        menuDataService.getMenusByType('tools', this.state.userRole),
        menuDataService.getMenusByType('fashion', this.state.userRole),
        menuDataService.getDevToolMenus(this.state.userRole)
      ])

      this.state.mainMenus = mainMenus
      this.state.bottomMenus = bottomMenus
      this.state.toolMenus = toolMenus
      this.state.fashionMenus = fashionMenus
      this.state.devToolMenus = devToolMenus

    } catch (error) {
      console.error('加载菜单数据失败:', error)
      this.state.error = error.message
    } finally {
      this.state.isLoading = false
    }
  }

  /**
   * 清除菜单数据
   */
  clearMenuData() {
    this.state.mainMenus = []
    this.state.bottomMenus = []
    this.state.toolMenus = []
    this.state.fashionMenus = []
    this.state.devToolMenus = []
  }

  /**
   * 设置活动菜单
   * @param {string} menuId - 菜单ID
   */
  setActiveMenu(menuId) {
    this.state.activeMenu = menuId
  }

  /**
   * 设置活动底部菜单
   * @param {string} menuId - 菜单ID
   */
  setActiveBottomMenu(menuId) {
    this.state.activeBottomMenu = menuId
  }

  /**
   * 切换菜单展开状态
   * @param {string} menuId - 菜单ID
   */
  toggleMenuExpanded(menuId) {
    if (this.state.expandedMenus.has(menuId)) {
      this.state.expandedMenus.delete(menuId)
    } else {
      this.state.expandedMenus.add(menuId)
    }
  }

  /**
   * 设置菜单展开状态
   * @param {string} menuId - 菜单ID
   * @param {boolean} expanded - 是否展开
   */
  setMenuExpanded(menuId, expanded) {
    if (expanded) {
      this.state.expandedMenus.add(menuId)
    } else {
      this.state.expandedMenus.delete(menuId)
    }
  }

  /**
   * 检查菜单是否展开
   * @param {string} menuId - 菜单ID
   * @returns {boolean} 是否展开
   */
  isMenuExpanded(menuId) {
    return this.state.expandedMenus.has(menuId)
  }

  /**
   * 切换开发工具启用状态
   * @param {string} toolId - 工具ID
   */
  toggleDevTool(toolId) {
    if (this.state.enabledDevTools.has(toolId)) {
      this.state.enabledDevTools.delete(toolId)
    } else {
      this.state.enabledDevTools.add(toolId)
    }
    
    // 更新菜单状态
    menuDataService.updateMenuStatus(toolId, {
      enabled: this.state.enabledDevTools.has(toolId)
    })
  }

  /**
   * 设置开发工具启用状态
   * @param {string} toolId - 工具ID
   * @param {boolean} enabled - 是否启用
   */
  setDevToolEnabled(toolId, enabled) {
    if (enabled) {
      this.state.enabledDevTools.add(toolId)
    } else {
      this.state.enabledDevTools.delete(toolId)
    }
    
    menuDataService.updateMenuStatus(toolId, { enabled })
  }

  /**
   * 检查开发工具是否启用
   * @param {string} toolId - 工具ID
   * @returns {boolean} 是否启用
   */
  isDevToolEnabled(toolId) {
    return this.state.enabledDevTools.has(toolId)
  }

  /**
   * 切换侧边栏折叠状态
   */
  toggleSidebar() {
    this.state.sidebarCollapsed = !this.state.sidebarCollapsed
  }

  /**
   * 设置侧边栏折叠状态
   * @param {boolean} collapsed - 是否折叠
   */
  setSidebarCollapsed(collapsed) {
    this.state.sidebarCollapsed = collapsed
  }

  /**
   * 设置底部菜单可见性
   * @param {boolean} visible - 是否可见
   */
  setBottomMenuVisible(visible) {
    this.state.bottomMenuVisible = visible
  }

  /**
   * 根据路径设置活动菜单
   * @param {string} path - 当前路径
   */
  setActiveMenuByPath(path) {
    // 在主菜单中查找匹配的菜单项
    const findMenuByPath = (menus, targetPath) => {
      for (const menu of menus) {
        if (menu.path === targetPath || targetPath.startsWith(menu.path + '/')) {
          return menu.id
        }
        if (menu.children && Array.isArray(menu.children)) {
          const childMatch = findMenuByPath(menu.children, targetPath)
          if (childMatch) return childMatch
        }
      }
      return null
    }

    const activeMenuId = findMenuByPath(this.state.mainMenus, path) || 
                        findMenuByPath(this.state.bottomMenus, path)
    
    if (activeMenuId) {
      this.setActiveMenu(activeMenuId)
    }
  }

  /**
   * 处理权限变更
   * @param {Object} user - 用户信息
   */
  async handlePermissionChange(user) {
    await this.updateUserInfo()
    await this.loadMenus()
  }

  /**
   * 处理菜单更新
   * @param {string} menuId - 菜单ID
   * @param {Object} updates - 更新内容
   */
  handleMenuUpdate(menuId, updates) {
    // 重新加载相关菜单数据
    this.loadMenus()
  }

  /**
   * 恢复持久化状态
   */
  restorePersistedState() {
    try {
      const savedState = localStorage.getItem('menuState')
      if (savedState) {
        const parsed = JSON.parse(savedState)
        
        // 恢复可持久化的状态
        this.state.sidebarCollapsed = parsed.sidebarCollapsed || false
        this.state.expandedMenus = new Set(parsed.expandedMenus || [])
        this.state.enabledDevTools = new Set(parsed.enabledDevTools || [])
        this.state.activeMenu = parsed.activeMenu || null
        this.state.activeBottomMenu = parsed.activeBottomMenu || null
      }
    } catch (error) {
      console.warn('恢复菜单状态失败:', error)
    }
  }

  /**
   * 持久化状态
   */
  persistState() {
    try {
      const stateToSave = {
        sidebarCollapsed: this.state.sidebarCollapsed,
        expandedMenus: Array.from(this.state.expandedMenus),
        enabledDevTools: Array.from(this.state.enabledDevTools),
        activeMenu: this.state.activeMenu,
        activeBottomMenu: this.state.activeBottomMenu
      }
      
      localStorage.setItem('menuState', JSON.stringify(stateToSave))
    } catch (error) {
      console.warn('持久化菜单状态失败:', error)
    }
  }

  /**
   * 设置状态持久化监听
   */
  setupStatePersistence() {
    // 监听需要持久化的状态变化
    watch(
      () => ({
        sidebarCollapsed: this.state.sidebarCollapsed,
        expandedMenus: this.state.expandedMenus,
        enabledDevTools: this.state.enabledDevTools,
        activeMenu: this.state.activeMenu,
        activeBottomMenu: this.state.activeBottomMenu
      }),
      () => {
        this.persistState()
      },
      { deep: true }
    )
  }

  /**
   * 清除持久化状态
   */
  clearPersistedState() {
    localStorage.removeItem('menuState')
  }

  /**
   * 设置页面加载状态
   */
  setPageLoading(loading) {
    this.state.pageLoading = loading
  }

  /**
   * 添加通知
   */
  addNotification(notification) {
    const id = Date.now() + Math.random()
    const notificationWithId = {
      id,
      type: 'info',
      duration: 3000,
      ...notification
    }
    
    this.state.notifications.push(notificationWithId)
    
    // 自动移除通知
    if (notificationWithId.duration > 0) {
      setTimeout(() => {
        this.removeNotification(id)
      }, notificationWithId.duration)
    }
    
    return id
  }

  /**
   * 移除通知
   */
  removeNotification(id) {
    const index = this.state.notifications.findIndex(n => n.id === id)
    if (index > -1) {
      this.state.notifications.splice(index, 1)
    }
  }

  /**
   * 清空所有通知
   */
  clearNotifications() {
    this.state.notifications = []
  }

  /**
   * 重置状态
   */
  reset() {
    this.state.activeMenu = null
    this.state.expandedMenus.clear()
    this.state.enabledDevTools.clear()
    this.state.sidebarCollapsed = false
    this.state.bottomMenuVisible = true
    this.state.activeBottomMenu = null
    this.clearMenuData()
    this.clearPersistedState()
  }

  /**
   * 获取状态快照
   * @returns {Object} 状态快照
   */
  getStateSnapshot() {
    return {
      currentUser: this.state.currentUser,
      userRole: this.state.userRole,
      isAuthenticated: this.state.isAuthenticated,
      activeMenu: this.state.activeMenu,
      expandedMenus: Array.from(this.state.expandedMenus),
      enabledDevTools: Array.from(this.state.enabledDevTools),
      sidebarCollapsed: this.state.sidebarCollapsed,
      bottomMenuVisible: this.state.bottomMenuVisible,
      activeBottomMenu: this.state.activeBottomMenu,
      menuCounts: {
        main: this.state.mainMenus.length,
        bottom: this.state.bottomMenus.length,
        tools: this.state.toolMenus.length,
        fashion: this.state.fashionMenus.length,
        devTools: this.state.devToolMenus.length
      },
      isLoading: this.state.isLoading,
      error: this.state.error
    }
  }
}

// 创建单例实例
const menuStateManager = new MenuStateManager()

// 将状态管理器暴露到全局
if (typeof window !== 'undefined') {
  window.menuStateManager = menuStateManager
}

export default menuStateManager

// 导出状态和常用方法
export const menuState = menuStateManager.state
export const {
  setActiveMenu,
  setActiveBottomMenu,
  toggleMenuExpanded,
  setMenuExpanded,
  isMenuExpanded,
  toggleDevTool,
  setDevToolEnabled,
  isDevToolEnabled,
  toggleSidebar,
  setSidebarCollapsed,
  setBottomMenuVisible,
  setActiveMenuByPath,
  setPageLoading,
  addNotification,
  removeNotification,
  clearNotifications,
  reset,
  getStateSnapshot
} = menuStateManager