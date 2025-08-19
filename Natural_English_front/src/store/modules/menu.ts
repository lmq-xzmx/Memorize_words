import type { Module } from 'vuex'
import { menuService, menuWebSocketService } from '@/services/menuService'
import { menuAdapter } from '@/services/menuAdapter'
import { versionService } from '@/services/versionService'
import { cacheService, MenuCacheManager } from '@/services/cacheService'
import type { MenuItem, ToolItem, MenuState } from '@/composables/useMenuManager'
import type { ApiResponse, MenuVersion, ToolStatusUpdate } from '@/services/menuService'

// 初始化服务实例
const menuCacheManager = new MenuCacheManager(cacheService)

// 菜单模块状态类型
interface MenuModuleState {
  // 菜单配置
  menuConfig: MenuItem[]
  toolsConfig: ToolItem[]
  
  // 菜单状态
  activeMenu: string | null
  expandedMenus: string[]
  selectedTool: string | null
  showDevCenter: boolean
  
  // 版本控制
  menuVersion: number
  lastUpdated: number
  versionInfo: {
    current: number
    server: number
    hasConflicts: boolean
    lastSync: number
  }
  
  // 加载状态
  loading: {
    menuConfig: boolean
    toolsConfig: boolean
    updating: boolean
    syncing: boolean
  }
  
  // 错误状态
  error: {
    menuConfig: string | null
    toolsConfig: string | null
    updating: string | null
    syncing: string | null
  }
  
  // WebSocket 连接状态
  wsConnected: boolean
  
  // 缓存状态
  cacheEnabled: boolean
  cacheStats: {
    size: number
    keys: string[]
    hitRate: number
    isHealthy: boolean
  }
}

// 根状态类型（简化版）
interface RootState {
  user: {
    currentUser: any
    permissions: string[]
    roles: string[]
  }
}

const menuModule: Module<MenuModuleState, RootState> = {
  namespaced: true,
  
  state: (): MenuModuleState => ({
    // 菜单配置
    menuConfig: [],
    toolsConfig: [],
    
    // 菜单状态
    activeMenu: null,
    expandedMenus: [],
    selectedTool: null,
    showDevCenter: false,
    
    // 版本控制
    menuVersion: 0,
    lastUpdated: 0,
    versionInfo: {
      current: 0,
      server: 0,
      hasConflicts: false,
      lastSync: 0
    },
    
    // 加载状态
    loading: {
      menuConfig: false,
      toolsConfig: false,
      updating: false,
      syncing: false
    },
    
    // 错误状态
    error: {
      menuConfig: null,
      toolsConfig: null,
      updating: null,
      syncing: null
    },
    
    // WebSocket 连接状态
    wsConnected: false,
    
    // 缓存状态
    cacheEnabled: true,
    cacheStats: {
      size: 0,
      keys: [],
      hitRate: 0,
      isHealthy: true
    }
  }),
  
  getters: {
    // 获取过滤后的菜单
    filteredMenus: (state, getters, rootState) => {
      const userPermissions = rootState.user.permissions || []
      const userRoles = rootState.user.roles || []
      
      return menuAdapter.filterMenuByPermissions(state.menuConfig)
    },
    
    // 获取启用的工具
    enabledTools: (state, getters, rootState) => {
      return menuAdapter.filterToolsByPermissions(state.toolsConfig.filter(tool => tool.enabled))
    },
    
    // 获取底部导航菜单
    bottomNavMenus: (state, getters) => {
      const filteredMenus = getters.filteredMenus
      return menuAdapter.transformToMobileNav(filteredMenus)
    },
    
    // 获取侧边栏菜单
    sidebarMenus: (state, getters) => {
      return getters.filteredMenus.filter((menu: MenuItem) => !menu.meta?.hideInMenu)
    },
    
    // 检查是否有菜单更新
    hasMenuUpdates: (state) => {
      const now = Date.now()
      const updateInterval = 30 * 60 * 1000 // 30分钟
      return now - state.lastUpdated > updateInterval
    },
    
    // 获取菜单加载状态
    isLoading: (state) => {
      return state.loading.menuConfig || state.loading.toolsConfig || state.loading.updating
    },
    
    // 获取错误信息
    hasError: (state) => {
      return !!(state.error.menuConfig || state.error.toolsConfig || state.error.updating)
    }
  },
  
  mutations: {
    // 设置菜单配置
    SET_MENU_CONFIG(state, config: MenuItem[]) {
      state.menuConfig = config
      state.error.menuConfig = null
    },
    
    // 设置工具配置
    SET_TOOLS_CONFIG(state, config: ToolItem[]) {
      state.toolsConfig = config
      state.error.toolsConfig = null
    },
    
    // 设置活动菜单
    SET_ACTIVE_MENU(state, menuId: string | null) {
      state.activeMenu = menuId
    },
    
    // 切换菜单展开状态
    TOGGLE_MENU_EXPANSION(state, menuId: string) {
      const index = state.expandedMenus.indexOf(menuId)
      if (index > -1) {
        state.expandedMenus.splice(index, 1)
      } else {
        state.expandedMenus.push(menuId)
      }
    },
    
    // 设置选中的工具
    SET_SELECTED_TOOL(state, toolId: string | null) {
      state.selectedTool = toolId
    },
    
    // 切换开发中心显示状态
    TOGGLE_DEV_CENTER(state) {
      state.showDevCenter = !state.showDevCenter
    },
    
    // 关闭所有菜单
    CLOSE_ALL_MENUS(state) {
      state.activeMenu = null
      state.showDevCenter = false
    },
    
    // 更新工具状态
    UPDATE_TOOL_STATUS(state, { toolId, enabled }: { toolId: string; enabled: boolean }) {
      const tool = state.toolsConfig.find(t => t.id === toolId)
      if (tool) {
        tool.enabled = enabled
      }
    },
    
    // 设置菜单版本
    SET_MENU_VERSION(state, version: number) {
      state.menuVersion = version
      state.lastUpdated = Date.now()
    },
    
    // 设置加载状态
    SET_LOADING(state, { type, loading }: { type: keyof MenuModuleState['loading']; loading: boolean }) {
      state.loading[type] = loading
    },
    
    // 设置错误状态
    SET_ERROR(state, { type, error }: { type: keyof MenuModuleState['error']; error: string | null }) {
      state.error[type] = error
    },
    
    // 设置 WebSocket 连接状态
    SET_WS_CONNECTED(state, connected: boolean) {
      state.wsConnected = connected
    },
    
    // 设置缓存状态
    SET_CACHE_ENABLED(state, enabled: boolean) {
      state.cacheEnabled = enabled
    },
    
    // 更新缓存统计
    UPDATE_CACHE_STATS(state, stats: { size: number; keys: string[]; hitRate: number; isHealthy: boolean }) {
      state.cacheStats = stats
    },
    
    // 版本控制相关mutations
    SET_VERSION_INFO(state, versionInfo: MenuModuleState['versionInfo']) {
      state.versionInfo = versionInfo
    },
    
    UPDATE_VERSION_CONFLICT(state, hasConflicts: boolean) {
      state.versionInfo.hasConflicts = hasConflicts
    },
    
    SET_LAST_SYNC_TIME(state, timestamp: number) {
      state.versionInfo.lastSync = timestamp
    },
    
    // 增量更新菜单项
    INCREMENTAL_UPDATE_MENU(state, updates: Array<{
      action: 'create' | 'update' | 'delete'
      item: MenuItem
    }>) {
      updates.forEach(update => {
        const index = state.menuConfig.findIndex(item => item.id === update.item.id)
        
        switch (update.action) {
          case 'create':
            if (index === -1) {
              state.menuConfig.push(update.item)
            }
            break
          case 'update':
            if (index !== -1) {
              state.menuConfig[index] = { ...state.menuConfig[index], ...update.item }
            }
            break
          case 'delete':
            if (index !== -1) {
              state.menuConfig.splice(index, 1)
            }
            break
        }
      })
    },
    
    // 增量更新工具项
    INCREMENTAL_UPDATE_TOOLS(state, updates: Array<{
      action: 'create' | 'update' | 'delete'
      item: ToolItem
    }>) {
      updates.forEach(update => {
        const index = state.toolsConfig.findIndex(item => item.id === update.item.id)
        
        switch (update.action) {
          case 'create':
            if (index === -1) {
              state.toolsConfig.push(update.item)
            }
            break
          case 'update':
            if (index !== -1) {
              state.toolsConfig[index] = { ...state.toolsConfig[index], ...update.item }
            }
            break
          case 'delete':
            if (index !== -1) {
              state.toolsConfig.splice(index, 1)
            }
            break
        }
      })
    },
    
    // 重置菜单状态
    RESET_MENU_STATE(state) {
      state.activeMenu = null
      state.expandedMenus = []
      state.selectedTool = null
      state.showDevCenter = false
    }
  },
  
  actions: {
    // 智能获取菜单配置
    async fetchMenuConfig({ commit, state, rootState }, options?: { forceUpdate?: boolean }) {
      commit('SET_LOADING', { type: 'menuConfig', loading: true })
      commit('SET_ERROR', { type: 'menuConfig', error: null })
      
      try {
        const userId = rootState.user.currentUser?.id
        
        // 获取服务器版本信息
        const versionResponse = await versionService.getServerVersion()
        const serverVersion = versionResponse.version
        
        // 使用智能缓存同步
        const menuConfig = await menuCacheManager.syncMenuConfig(
          serverVersion,
          async () => {
            const response = await menuService.getUserMenuConfig(userId)
            if (!response.success || !response.data) {
              throw new Error(response.message)
            }
            
            // 使用适配器过滤菜单
            const filteredMenuItems = menuAdapter.filterMenuByPermissions(response.data.menuItems)
            return filteredMenuItems
          },
          { forceUpdate: options?.forceUpdate }
        )
        
        commit('SET_MENU_CONFIG', menuConfig)
        commit('SET_MENU_VERSION', serverVersion)
        
        // 更新版本信息
        commit('SET_VERSION_INFO', {
          current: serverVersion,
          server: serverVersion,
          hasConflicts: false,
          lastSync: Date.now()
        })
        
        return { success: true, data: menuConfig }
      } catch (error: any) {
        const errorMessage = error.message || '获取菜单配置失败'
        commit('SET_ERROR', { type: 'menuConfig', error: errorMessage })
        
        // 降级处理：使用默认菜单
        const userRole = rootState.user?.roles?.[0] || 'student'
        const defaultMenuItems = menuAdapter.getDefaultMenuByRole(userRole)
        commit('SET_MENU_CONFIG', defaultMenuItems)
        
        throw error
      } finally {
        commit('SET_LOADING', { type: 'menuConfig', loading: false })
      }
    },
    
    // 智能获取工具配置
    async fetchToolsConfig({ commit, rootState }, options?: { forceUpdate?: boolean }) {
      commit('SET_LOADING', { type: 'toolsConfig', loading: true })
      commit('SET_ERROR', { type: 'toolsConfig', error: null })
      
      try {
        const userId = rootState.user.currentUser?.id
        
        // 获取服务器版本信息
        const versionResponse = await versionService.getServerVersion()
        const serverVersion = versionResponse.version
        
        // 使用智能缓存同步
        const toolsConfig = await menuCacheManager.syncToolsConfig(
          serverVersion,
          async () => {
            const response = await menuService.getToolsConfig(userId)
            if (!response.success || !response.data) {
              throw new Error(response.message)
            }
            
            // 使用适配器过滤工具
            const filteredToolItems = menuAdapter.filterToolsByPermissions(response.data)
            return filteredToolItems
          },
          { forceUpdate: options?.forceUpdate }
        )
        
        commit('SET_TOOLS_CONFIG', toolsConfig)
        
        return { success: true, data: toolsConfig }
      } catch (error: any) {
        const errorMessage = error.message || '获取工具配置失败'
        commit('SET_ERROR', { type: 'toolsConfig', error: errorMessage })
        
        // 降级处理：清空工具配置
        commit('SET_TOOLS_CONFIG', [])
        
        throw error
      } finally {
        commit('SET_LOADING', { type: 'toolsConfig', loading: false })
      }
    },
    
    // 检查菜单版本
    async checkMenuVersion({ commit }) {
      try {
        const response = await menuService.getMenuVersion()
        if (response.success) {
          commit('SET_MENU_VERSION', response.data.version)
          return response
        }
        throw new Error(response.message)
      } catch (error) {
        console.error('检查菜单版本失败:', error)
        throw error
      }
    },
    
    // 更新工具状态
    async updateToolStatus({ commit, rootState }, { toolId, enabled }: ToolStatusUpdate) {
      commit('SET_LOADING', { type: 'updating', loading: true })
      commit('SET_ERROR', { type: 'updating', error: null })
      
      try {
        const userId = rootState.user.currentUser?.id
        const response = await menuService.updateToolStatus({ toolId, enabled, userId })
        
        if (response.success) {
          commit('UPDATE_TOOL_STATUS', { toolId, enabled })
          return response
        } else {
          throw new Error(response.message)
        }
      } catch (error: any) {
        const errorMessage = error.message || '更新工具状态失败'
        commit('SET_ERROR', { type: 'updating', error: errorMessage })
        throw error
      } finally {
        commit('SET_LOADING', { type: 'updating', loading: false })
      }
    },
    
    // 刷新菜单配置
    async refreshMenuConfig({ dispatch }) {
      await Promise.all([
        dispatch('fetchMenuConfig'),
        dispatch('fetchToolsConfig')
      ])
    },
    
    // 初始化菜单模块
    async initializeMenu({ dispatch, commit, rootState }) {
      try {
        console.log('开始初始化菜单模块...')
        
        // 1. 预热缓存（异步执行，不阻塞主流程）
        dispatch('warmupCache').catch(error => {
          console.warn('缓存预热失败:', error)
        })
        
        // 2. 获取菜单配置（使用智能缓存）
        await dispatch('refreshMenuConfig')
        
        // 3. 同步菜单版本
        await dispatch('syncMenuVersion').catch(error => {
          console.warn('版本同步失败:', error)
        })
        
        // 4. 初始化 WebSocket 连接
        const userId = rootState.user.currentUser?.id
        dispatch('initializeWebSocket', userId)
        
        // 5. 更新缓存统计
        dispatch('updateCacheStats')
        
        // 6. 定期清理过期缓存（每5分钟）
        setInterval(() => {
          dispatch('clearExpiredCache')
        }, 5 * 60 * 1000)
        
        console.log('菜单模块初始化完成')
      } catch (error) {
        console.error('初始化菜单模块失败:', error)
        throw error
      }
    },
    
    // 初始化 WebSocket
    initializeWebSocket({ commit, dispatch }, userId?: string) {
      // 设置事件监听器
      menuWebSocketService.on('connected', () => {
        commit('SET_WS_CONNECTED', true)
        console.log('WebSocket连接已建立')
      })
      
      menuWebSocketService.on('disconnected', () => {
        commit('SET_WS_CONNECTED', false)
        console.log('WebSocket连接已断开')
      })
      
      // 实际建立WebSocket连接
      menuWebSocketService.connect(userId)
      
      // 处理菜单更新通知（支持增量更新）
      menuWebSocketService.on('menuUpdated', async (data) => {
        console.log('收到菜单更新通知:', data)
        
        try {
          if (data.incremental && data.updates) {
            // 增量更新 - 先更新缓存
            await menuCacheManager.handleMenuUpdate({
              type: 'menu',
              action: data.action || 'update',
              items: data.updates,
              version: data.version
            })
            
            // 缓存更新成功后，更新store状态
            if (data.action === 'update' || data.action === 'create') {
              await dispatch('incrementalUpdateMenus', data.updates.map((item: MenuItem) => ({
                action: data.action,
                item
              })))
            }
            
            // 同步版本信息
            if (data.version) {
              await dispatch('syncMenuVersion')
            }
          } else {
            // 全量更新
            await dispatch('refreshMenuConfig')
          }
        } catch (error) {
          console.error('处理菜单更新失败:', error)
          // 降级到全量更新
          await dispatch('refreshMenuConfig')
        }
      })
      
      // 处理工具状态变更通知
      menuWebSocketService.on('toolStatusChanged', async (data) => {
        console.log('收到工具状态变更通知:', data)
        
        try {
          if (data.incremental && data.updates) {
            // 增量更新工具
            await menuCacheManager.handleMenuUpdate({
              type: 'tool',
              action: data.action || 'update',
              items: data.updates,
              version: data.version
            })
            
            await dispatch('incrementalUpdateTools', data.updates.map((item: ToolItem) => ({
              action: data.action,
              item
            })))
          } else {
            // 单个工具状态更新
            commit('UPDATE_TOOL_STATUS', data)
          }
        } catch (error) {
          console.error('处理工具状态变更失败:', error)
          // 降级处理
          commit('UPDATE_TOOL_STATUS', data)
        }
      })
      
      // 处理权限变更通知
      menuWebSocketService.on('permissionChanged', async (data) => {
        console.log('收到权限变更通知:', data)
        
        try {
          // 权限变更可能影响菜单显示，需要重新获取配置
          await dispatch('refreshMenuConfig')
          
          // 清除相关缓存
          dispatch('clearExpiredCache')
        } catch (error) {
          console.error('处理权限变更失败:', error)
        }
      })
      
      // 处理缓存失效通知
      menuWebSocketService.on('cacheInvalidated', (data) => {
        console.log('收到缓存失效通知:', data)
        
        if (data.pattern) {
          // 按模式清除缓存
          menuCacheManager.clearExpiredCache()
        } else {
          // 清除所有缓存
          dispatch('clearCache')
        }
        
        dispatch('updateCacheStats')
      })
      
      // WebSocket连接已在上面建立，无需重复连接
    },
    
    // 断开 WebSocket
    disconnectWebSocket({ commit }) {
      menuWebSocketService.disconnect()
      commit('SET_WS_CONNECTED', false)
    },
    
    // 增量更新菜单
    async incrementalUpdateMenus({ commit }, updates: Array<{
      action: 'create' | 'update' | 'delete'
      item: MenuItem
    }>) {
      try {
        const result = await menuCacheManager.incrementalUpdateMenus(updates)
        commit('INCREMENTAL_UPDATE_MENU', updates)
        commit('SET_MENU_CONFIG', result)
        
        console.log('菜单增量更新完成:', updates.length, '项')
        return result
      } catch (error) {
        console.error('菜单增量更新失败:', error)
        throw error
      }
    },
    
    // 增量更新工具
    async incrementalUpdateTools({ commit }, updates: Array<{
      action: 'create' | 'update' | 'delete'
      item: ToolItem
    }>) {
      try {
        const result = await menuCacheManager.incrementalUpdateTools(updates)
        commit('INCREMENTAL_UPDATE_TOOLS', updates)
        commit('SET_TOOLS_CONFIG', result)
        
        console.log('工具增量更新完成:', updates.length, '项')
        return result
      } catch (error) {
        console.error('工具增量更新失败:', error)
        throw error
      }
    },
    
    // 同步菜单版本
    async syncMenuVersion({ commit, state, dispatch }) {
      commit('SET_LOADING', { type: 'syncing', loading: true })
      commit('SET_ERROR', { type: 'syncing', error: null })
      
      try {
        // 获取服务器版本
        const serverVersionResponse = await versionService.getServerVersion()
        const serverVersion = serverVersionResponse.version
        
        // 检查是否需要同步
        if (serverVersion > state.versionInfo.current) {
          console.log('检测到版本更新，开始同步...', {
            current: state.versionInfo.current,
            server: serverVersion
          })
          
          // 同步菜单配置
          const syncResult = await versionService.syncMenuConfig(
            state.versionInfo.current,
            serverVersion
          )
          
          if (syncResult.hasConflicts) {
            commit('UPDATE_VERSION_CONFLICT', true)
            console.warn('版本同步存在冲突，需要手动解决')
          } else {
            // 应用同步结果
            if (syncResult.menuUpdates && syncResult.menuUpdates.length > 0) {
              await dispatch('incrementalUpdateMenus', syncResult.menuUpdates)
            }
            
            if (syncResult.toolUpdates && syncResult.toolUpdates.length > 0) {
              await dispatch('incrementalUpdateTools', syncResult.toolUpdates)
            }
            
            // 更新版本信息
            commit('SET_VERSION_INFO', {
              current: serverVersion,
              server: serverVersion,
              hasConflicts: false,
              lastSync: Date.now()
            })
          }
        }
        
        return { success: true, version: serverVersion }
      } catch (error: any) {
        const errorMessage = error.message || '版本同步失败'
        commit('SET_ERROR', { type: 'syncing', error: errorMessage })
        throw error
      } finally {
        commit('SET_LOADING', { type: 'syncing', loading: false })
      }
    },
    
    // 预热缓存
    async warmupCache({ rootState }) {
      try {
        const userId = rootState.user.currentUser?.id
        
        await menuCacheManager.warmupMenuCache({
          fetchMenuConfig: () => menuService.getUserMenuConfig(userId).then(r => r.data?.menuItems || []),
          fetchToolsConfig: () => menuService.getToolsConfig(userId).then(r => r.data || []),
          fetchUserPermissions: () => Promise.resolve(rootState.user.permissions)
        })
        
        console.log('缓存预热完成')
      } catch (error) {
        console.warn('缓存预热失败:', error)
      }
    },
    
    // 更新缓存统计
    updateCacheStats({ commit }) {
      const stats = menuCacheManager.getCacheStats()
      const health = menuCacheManager.getCacheHealth()
      
      commit('UPDATE_CACHE_STATS', {
        size: stats.size,
        keys: Object.keys(stats.items),
        hitRate: health.hitRate,
        isHealthy: health.isHealthy
      })
    },
    
    // 清除缓存
    clearCache({ dispatch }) {
      menuCacheManager.clearMenuCache()
      dispatch('updateCacheStats')
    },
    
    // 清除过期缓存
    clearExpiredCache({ dispatch }) {
      const clearedCount = menuCacheManager.clearExpiredCache()
      dispatch('updateCacheStats')
      console.log(`清除了 ${clearedCount} 个过期缓存项`)
    },
    
    // 切换缓存状态
    toggleCache({ commit, state, dispatch }) {
      const enabled = !state.cacheEnabled
      commit('SET_CACHE_ENABLED', enabled)
      
      if (!enabled) {
        dispatch('clearCache')
      }
    },
    
    // 记录菜单使用
    recordMenuUsage({ }, { menuId, action = 'click' }) {
      // 异步记录，不影响主流程
      menuService.recordMenuUsage(menuId, action).catch(error => {
        console.warn('记录菜单使用失败:', error)
      })
    }
  }
}

export default menuModule
export type { MenuModuleState }