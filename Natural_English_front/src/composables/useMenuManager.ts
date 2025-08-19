import { ref, computed, reactive, watch } from 'vue'
import { useStore } from 'vuex'
import { usePermission } from './usePermission'
import { menuService } from '@/services/menuService'
import { menuAdapter } from '@/services/menuAdapter'
import type { RouteLocationNormalized } from 'vue-router'

// 菜单状态类型
export interface MenuState {
  activeMenu: string | null
  expandedMenus: string[]
  selectedTool: string | null
  showDevCenter: boolean
  menuVersion: number
  lastUpdated: number
}

// 工具项类型
export interface ToolItem {
  id: string
  name: string
  title: string
  description: string
  path: string
  icon: string
  enabled: boolean
  category?: string
  order?: number
}

// 菜单配置类型
export interface MenuItem {
  id: string
  name: string
  path: string
  icon?: string
  component?: string
  meta?: {
    title?: string
    requiresAuth?: boolean
    permissions?: string[]
    roles?: string[]
    hideInMenu?: boolean
    order?: number
    isMobileNav?: boolean
  }
  children?: MenuItem[]
}

export interface MenuConfig {
  id: string
  name: string
  path: string
  icon?: string
  component?: string
  meta?: {
    title?: string
    requiresAuth?: boolean
    permissions?: string[]
    roles?: string[]
    hideInMenu?: boolean
    order?: number
  }
  children?: MenuConfig[]
}

/**
 * 菜单管理器组合式函数
 */
export function useMenuManager() {
  const store = useStore()
  const { hasPermission, hasRole, filterMenuItems, checkMenuItemPermission } = usePermission()
  
  // 菜单状态
  const menuState = reactive<MenuState>({
    activeMenu: null,
    expandedMenus: [],
    selectedTool: null,
    showDevCenter: false,
    menuVersion: 0,
    lastUpdated: Date.now()
  })
  
  // 原始菜单配置
  const rawMenuConfig = ref<MenuConfig[]>([])
  
  // 工具配置
  const toolsConfig = ref<ToolItem[]>([])
  
  // 加载状态
  const loading = ref({
    menuConfig: false,
    toolsConfig: false,
    updating: false
  })
  
  // 错误状态
  const error = ref({
    menuConfig: null as string | null,
    toolsConfig: null as string | null,
    updating: null as string | null
  })
  
  // 过滤后的菜单
  const filteredMenus = computed<MenuItem[]>(() => {
    const menus = convertConfigToMenuItem(rawMenuConfig.value)
    return filterMenuItems(menus)
  })
  
  // 启用的工具
  const enabledTools = computed<ToolItem[]>(() => {
    return toolsConfig.value.filter(tool => tool.enabled)
  })
  
  // 底部导航菜单
  const bottomNavMenus = computed<MenuItem[]>(() => {
    return filteredMenus.value.filter(menu => 
      !menu.meta?.hideInMenu && 
      (menu.meta?.order || 0) >= 0
    ).sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0))
  })
  
  // 侧边栏菜单
  const sidebarMenus = computed<MenuItem[]>(() => {
    return filteredMenus.value.filter(menu => 
      !menu.meta?.hideInMenu
    )
  })
  
  /**
   * 转换配置为菜单项
   */
  const convertConfigToMenuItem = (configs: MenuConfig[]): MenuItem[] => {
    return configs.map(config => ({
      id: config.id,
      name: config.name,
      path: config.path,
      icon: config.icon,
      component: config.component,
      meta: config.meta,
      children: config.children ? convertConfigToMenuItem(config.children) : undefined
    }))
  }
  
  /**
   * 加载菜单配置
   */
  const loadMenuConfig = async (): Promise<void> => {
    loading.value.menuConfig = true
    error.value.menuConfig = null
    
    try {
      const response = await menuService.getUserMenuConfig()
      
      if (response.success && response.data) {
        rawMenuConfig.value = response.data.menuItems
        
        menuState.menuVersion++
        menuState.lastUpdated = Date.now()
        
        // 保存到本地存储
        saveMenuState()
        
        console.log('菜单配置加载成功:', response.message)
      } else {
        throw new Error(response.message || '加载菜单配置失败')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误'
      error.value.menuConfig = errorMessage
      console.error('加载菜单配置失败:', errorMessage)
      
      // 降级处理：使用默认菜单
      const userRole = store.getters['user/role'] || 'student'
      rawMenuConfig.value = menuAdapter.getDefaultMenuByRole(userRole)
    } finally {
      loading.value.menuConfig = false
    }
  }
  
  /**
   * 加载工具配置
   */
  const loadToolsConfig = async (): Promise<void> => {
    loading.value.toolsConfig = true
    error.value.toolsConfig = null
    
    try {
      const response = await menuService.getToolsConfig()
      
      if (response.success && response.data) {
        toolsConfig.value = response.data
        
        // 保存到本地存储
        saveMenuState()
        
        console.log('工具配置加载成功:', response.message)
      } else {
        throw new Error(response.message || '加载工具配置失败')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误'
      error.value.toolsConfig = errorMessage
      console.error('加载工具配置失败:', errorMessage)
      
      // 降级处理：清空工具配置
      toolsConfig.value = []
    } finally {
      loading.value.toolsConfig = false
    }
  }
  
  /**
   * 切换菜单状态
   */
  const toggleMenu = (menuId: string): void => {
    if (menuState.activeMenu === menuId) {
      menuState.activeMenu = null
      menuState.showDevCenter = false
    } else {
      menuState.activeMenu = menuId
      menuState.showDevCenter = false
    }
  }
  
  /**
   * 展开/收起菜单
   */
  const toggleMenuExpansion = (menuId: string): void => {
    const index = menuState.expandedMenus.indexOf(menuId)
    if (index > -1) {
      menuState.expandedMenus.splice(index, 1)
    } else {
      menuState.expandedMenus.push(menuId)
    }
  }
  
  /**
   * 检查菜单是否展开
   */
  const isMenuExpanded = (menuId: string): boolean => {
    return menuState.expandedMenus.includes(menuId)
  }
  
  /**
   * 设置活动菜单
   */
  const setActiveMenu = (menuId: string | null): void => {
    menuState.activeMenu = menuId
  }
  
  /**
   * 关闭所有菜单
   */
  const closeAllMenus = (): void => {
    menuState.activeMenu = null
    menuState.showDevCenter = false
  }
  
  /**
   * 切换开发中心
   */
  const toggleDevCenter = (): void => {
    menuState.showDevCenter = !menuState.showDevCenter
  }
  
  /**
   * 选择工具
   */
  const selectTool = (toolId: string): void => {
    menuState.selectedTool = toolId
  }
  
  /**
   * 切换工具启用状态
   */
  const toggleTool = async (toolId: string): Promise<void> => {
    const tool = toolsConfig.value.find(t => t.id === toolId)
    if (tool) {
      tool.enabled = !tool.enabled
      
      try {
        await store.dispatch('menu/updateToolStatus', {
          toolId,
          enabled: tool.enabled
        })
      } catch (error) {
        // 回滚状态
        tool.enabled = !tool.enabled
        console.error('更新工具状态失败:', error)
        throw error
      }
    }
  }
  
  /**
   * 根据路由设置活动菜单
   */
  const setActiveMenuByRoute = (route: RouteLocationNormalized): void => {
    const findActiveMenu = (menus: MenuItem[], path: string): string | null => {
      for (const menu of menus) {
        if (menu.path === path) {
          return menu.id
        }
        if (menu.children) {
          const childActive = findActiveMenu(menu.children, path)
          if (childActive) {
            // 展开父菜单
            if (!menuState.expandedMenus.includes(menu.id)) {
              menuState.expandedMenus.push(menu.id)
            }
            return childActive
          }
        }
      }
      return null
    }
    
    const activeMenuId = findActiveMenu(filteredMenus.value, route.path)
    if (activeMenuId) {
      setActiveMenu(activeMenuId)
    }
  }
  
  /**
   * 获取面包屑导航
   */
  const getBreadcrumbs = (route: RouteLocationNormalized): MenuItem[] => {
    const breadcrumbs: MenuItem[] = []
    
    const findBreadcrumbs = (menus: MenuItem[], path: string, parents: MenuItem[] = []): boolean => {
      for (const menu of menus) {
        const currentPath = [...parents, menu]
        
        if (menu.path === path) {
          breadcrumbs.push(...currentPath)
          return true
        }
        
        if (menu.children) {
          if (findBreadcrumbs(menu.children, path, currentPath)) {
            return true
          }
        }
      }
      return false
    }
    
    findBreadcrumbs(filteredMenus.value, route.path)
    return breadcrumbs
  }
  
  /**
   * 刷新菜单配置
   */
  const refreshMenuConfig = async (): Promise<void> => {
    await Promise.all([
      loadMenuConfig(),
      loadToolsConfig()
    ])
  }
  
  /**
   * 检查菜单更新
   */
  const checkMenuUpdates = async (): Promise<boolean> => {
    try {
      const response = await store.dispatch('menu/checkMenuVersion')
      const serverVersion = response.data?.version || 0
      
      if (serverVersion > menuState.menuVersion) {
        await refreshMenuConfig()
        return true
      }
      
      return false
    } catch (error) {
      console.error('检查菜单更新失败:', error)
      return false
    }
  }
  
  /**
   * 保存菜单状态到本地存储
   */
  const saveMenuState = (): void => {
    try {
      const stateToSave = {
        expandedMenus: menuState.expandedMenus,
        selectedTool: menuState.selectedTool,
        menuVersion: menuState.menuVersion
      }
      localStorage.setItem('menuState', JSON.stringify(stateToSave))
    } catch (error) {
      console.error('保存菜单状态失败:', error)
    }
  }
  
  /**
   * 从本地存储恢复菜单状态
   */
  const restoreMenuState = (): void => {
    try {
      const savedState = localStorage.getItem('menuState')
      if (savedState) {
        const state = JSON.parse(savedState)
        menuState.expandedMenus = state.expandedMenus || []
        menuState.selectedTool = state.selectedTool || null
        
        // 如果版本不匹配，清除状态
        if (state.menuVersion !== menuState.menuVersion) {
          menuState.expandedMenus = []
          menuState.selectedTool = null
        }
      }
    } catch (error) {
      console.error('恢复菜单状态失败:', error)
    }
  }
  
  // 监听菜单状态变化，自动保存
  watch(
    () => [menuState.expandedMenus, menuState.selectedTool],
    () => {
      saveMenuState()
    },
    { deep: true }
  )
  
  return {
    // 状态
    menuState,
    rawMenuConfig,
    toolsConfig,
    filteredMenus,
    enabledTools,
    bottomNavMenus,
    sidebarMenus,
    
    // 方法
    loadMenuConfig,
    loadToolsConfig,
    toggleMenu,
    toggleMenuExpansion,
    isMenuExpanded,
    setActiveMenu,
    closeAllMenus,
    toggleDevCenter,
    selectTool,
    toggleTool,
    setActiveMenuByRoute,
    getBreadcrumbs,
    refreshMenuConfig,
    checkMenuUpdates,
    saveMenuState,
    restoreMenuState
  }
}

// 导出类型
export type { MenuState, ToolItem, MenuConfig }