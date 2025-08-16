/**
 * 菜单状态管理器
 * 统一管理菜单状态、权限检查、位置计算等逻辑
 */

import { reactive, ref, computed } from 'vue'
import { bottomNavMenus, toolsMenuConfig, fashionMenuConfig, adminMenuConfig } from '../config/menuConfig.js'
import { getCurrentUser, isAuthenticated } from '../utils/permission.js'

// 菜单状态
export const menuState = reactive({
  // 底部导航状态
  bottomMenuVisible: true,
  activeBottomMenu: null,
  
  // 菜单数据
  bottomMenus: bottomNavMenus,
  toolMenus: toolsMenuConfig.items,
  fashionMenus: fashionMenuConfig.items,
  adminMenus: adminMenuConfig.items,
  
  // 用户状态
  currentUser: null,
  isAuthenticated: false,
  
  // 菜单显示状态
  showMoreMenu: false,
  showToolsMenu: false,
  showFashionMenu: false
})

// 菜单状态管理器类
class MenuStateManager {
  constructor() {
    this.state = menuState
    this.init()
  }
  
  // 初始化
  init() {
    this.updateUserState()
    this.setupEventListeners()
  }
  
  // 更新用户状态
  updateUserState() {
    try {
      this.state.currentUser = getCurrentUser()
      this.state.isAuthenticated = isAuthenticated()
    } catch (error) {
      console.error('更新用户状态失败:', error)
      this.state.currentUser = null
      this.state.isAuthenticated = false
    }
  }
  
  // 设置活动底部菜单
  setActiveBottomMenu(menuId) {
    this.state.activeBottomMenu = menuId
  }
  
  // 切换底部菜单可见性
  toggleBottomMenuVisible() {
    this.state.bottomMenuVisible = !this.state.bottomMenuVisible
  }
  
  // 显示更多菜单
  showMoreMenu() {
    this.state.showMoreMenu = true
  }
  
  // 隐藏更多菜单
  hideMoreMenu() {
    this.state.showMoreMenu = false
  }
  
  // 切换更多菜单
  toggleMoreMenu() {
    this.state.showMoreMenu = !this.state.showMoreMenu
  }
  
  // 显示工具菜单
  showToolsMenu() {
    this.state.showToolsMenu = true
    this.state.showFashionMenu = false
  }
  
  // 显示时尚菜单
  showFashionMenu() {
    this.state.showFashionMenu = true
    this.state.showToolsMenu = false
  }
  
  // 隐藏所有子菜单
  hideAllSubMenus() {
    this.state.showToolsMenu = false
    this.state.showFashionMenu = false
  }
  
  // 获取可访问的底部菜单
  getAccessibleBottomMenus(hasPermissionFn) {
    return this.state.bottomMenus.filter(menu => {
      if (!menu.requiresAuth) return true
      if (!this.state.isAuthenticated) return false
      return !menu.permission || hasPermissionFn(menu.permission)
    })
  }
  
  // 获取可访问的工具菜单
  getAccessibleToolMenus(hasPermissionFn) {
    return this.state.toolMenus.filter(tool => {
      return !tool.permission || hasPermissionFn(tool.permission)
    })
  }
  
  // 获取可访问的时尚菜单
  getAccessibleFashionMenus(hasPermissionFn) {
    return this.state.fashionMenus.filter(menu => {
      return !menu.permission || hasPermissionFn(menu.permission)
    })
  }
  
  // 设置事件监听器
  setupEventListeners() {
    // 监听存储变化
    window.addEventListener('storage', (event) => {
      if (event.key === 'user' || event.key === 'token') {
        this.updateUserState()
      }
    })
    
    // 监听权限变更
    if (window.permissionWatcher) {
      window.permissionWatcher.addListener(() => {
        this.updateUserState()
      })
    }
  }
  
  // 清理资源
  destroy() {
    // 清理事件监听器
    if (window.permissionWatcher) {
      window.permissionWatcher.removeListener(this.updateUserState)
    }
  }
}

// 创建单例实例
const menuStateManager = new MenuStateManager()

// 导出状态和管理器
export default menuStateManager
export { MenuStateManager }