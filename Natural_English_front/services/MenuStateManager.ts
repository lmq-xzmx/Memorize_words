/**
 * 菜单状态管理器
 * 统一管理菜单状态、权限检查、位置计算等逻辑
 */

import { reactive, ref, computed } from 'vue'
import type { Ref } from 'vue'
import { bottomNavMenus, toolMenus, fashionMenus, adminMenus } from '../config/menuConfig'
import { getCurrentUser, isAuthenticated } from '../utils/permission'
import type { User } from '../types'

// 菜单项接口
interface MenuItem {
  id: string
  name: string
  icon?: string
  path?: string
  permission?: string
  children?: MenuItem[]
}

// 菜单状态接口
interface MenuStateType {
  // 底部导航状态
  bottomMenuVisible: boolean
  activeBottomMenu: string | null
  
  // 菜单数据
  bottomMenus: MenuItem[]
  toolMenus: MenuItem[]
  fashionMenus: MenuItem[]
  adminMenus: MenuItem[]
  
  // 用户状态
  currentUser: User | null
  isAuthenticated: boolean
  
  // 菜单显示状态
  showMoreMenu: boolean
  showToolsMenu: boolean
  showFashionMenu: boolean
}

// 权限检查函数类型
type PermissionCheckFn = (permission: string) => boolean

// 菜单状态
export const menuState: MenuStateType = reactive({
  // 底部导航状态
  bottomMenuVisible: true,
  activeBottomMenu: null,
  
  // 菜单数据
  bottomMenus: bottomNavMenus,
  toolMenus: toolMenus,
  fashionMenus: fashionMenus,
  adminMenus: adminMenus,
  
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
  public state: MenuStateType
  private clickOutsideHandler?: (event: Event) => void
  
  constructor() {
    this.state = menuState
    this.init()
  }
  
  // 初始化
  private init(): void {
    this.updateUserState()
    this.setupEventListeners()
  }
  
  // 更新用户状态
  public updateUserState(): void {
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
  public setActiveBottomMenu(menuId: string | null): void {
    this.state.activeBottomMenu = menuId
  }
  
  // 切换底部菜单可见性
  public toggleBottomMenuVisible(): void {
    this.state.bottomMenuVisible = !this.state.bottomMenuVisible
  }
  
  // 显示更多菜单
  public showMoreMenu(): void {
    this.state.showMoreMenu = true
  }
  
  // 隐藏更多菜单
  public hideMoreMenu(): void {
    this.state.showMoreMenu = false
  }
  
  // 切换更多菜单
  public toggleMoreMenu(): void {
    this.state.showMoreMenu = !this.state.showMoreMenu
  }
  
  // 显示工具菜单
  public showToolsMenu(): void {
    this.state.showToolsMenu = true
    this.state.showFashionMenu = false
  }
  
  // 显示时尚菜单
  public showFashionMenu(): void {
    this.state.showFashionMenu = true
    this.state.showToolsMenu = false
  }
  
  // 隐藏所有子菜单
  public hideAllSubMenus(): void {
    this.state.showToolsMenu = false
    this.state.showFashionMenu = false
  }
  
  // 获取可访问的底部菜单
  public getAccessibleBottomMenus(hasPermissionFn: PermissionCheckFn): MenuItem[] {
    return this.state.bottomMenus.filter(menu => 
      !menu.permission || hasPermissionFn(menu.permission)
    )
  }
  
  // 获取可访问的工具菜单
  public getAccessibleToolMenus(hasPermissionFn: PermissionCheckFn): MenuItem[] {
    return this.state.toolMenus.filter(menu => 
      !menu.permission || hasPermissionFn(menu.permission)
    )
  }
  
  // 获取可访问的时尚菜单
  public getAccessibleFashionMenus(hasPermissionFn: PermissionCheckFn): MenuItem[] {
    return this.state.fashionMenus.filter(menu => 
      !menu.permission || hasPermissionFn(menu.permission)
    )
  }
  
  // 设置事件监听器
  private setupEventListeners(): void {
    // 点击外部关闭菜单
    this.clickOutsideHandler = (event: Event) => {
      const target = event.target as HTMLElement
      if (!target.closest('.menu-container')) {
        this.hideAllSubMenus()
        this.hideMoreMenu()
      }
    }
    
    if (typeof document !== 'undefined') {
      document.addEventListener('click', this.clickOutsideHandler)
    }
  }
  
  // 销毁管理器
  public destroy(): void {
    if (this.clickOutsideHandler && typeof document !== 'undefined') {
      document.removeEventListener('click', this.clickOutsideHandler)
    }
  }
}

// 创建单例实例
const menuStateManager = new MenuStateManager()

// 导出
export default menuStateManager
export { MenuStateManager }
export type { MenuItem, MenuStateType, PermissionCheckFn }