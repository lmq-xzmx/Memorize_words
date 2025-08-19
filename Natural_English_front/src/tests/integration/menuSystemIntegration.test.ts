/**
 * 菜单系统集成测试
 * 测试实时推送、版本控制和缓存同步的协同工作
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createStore } from 'vuex'
import menuModule from '@/store/modules/menu'
import versionService from '@/services/versionService'
import { CacheService, MenuCacheManager } from '@/services/cacheService'
import { menuWebSocketService } from '@/services/menuService'

// Mock cacheService module
vi.mock('@/services/cacheService', () => {
  const mockCacheService = {
    get: vi.fn(),
    set: vi.fn(),
    delete: vi.fn(),
    clear: vi.fn(),
    has: vi.fn()
  }
  
  const mockMenuCacheManager = {
    syncMenuConfig: vi.fn(),
    syncToolsConfig: vi.fn(),
    incrementalUpdateMenus: vi.fn(),
    handleMenuUpdate: vi.fn(),
    getCacheStats: vi.fn(),
    getCacheHealth: vi.fn(),
    clearExpiredCache: vi.fn()
  }
  
  return {
    CacheService: vi.fn(() => mockCacheService),
    MenuCacheManager: vi.fn(() => mockMenuCacheManager)
  }
})

// Mock fetch API
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: vi.fn().mockResolvedValue({ version: 1, timestamp: Date.now() })
})

// Mock WebSocket
vi.mock('@/services/menuService', () => {
  const mockWebSocket = {
    connect: vi.fn(),
    disconnect: vi.fn(),
    on: vi.fn(),
    emit: vi.fn(),
    send: vi.fn()
  }
  
  return {
    menuService: {
      getUserMenuConfig: vi.fn(),
      getToolsConfig: vi.fn(),
      getMenuVersion: vi.fn(),
      updateToolStatus: vi.fn(),
      recordMenuUsage: vi.fn()
    },
    menuWebSocketService: mockWebSocket
  }
})

describe('菜单系统集成测试', () => {
  let store: any
  let mockWebSocketService: any
  let mockMenuCacheManager: any

  beforeEach(async () => {
    // 获取mock的服务
    const { menuWebSocketService } = await import('@/services/menuService')
    const { MenuCacheManager } = await import('@/services/cacheService')
    
    mockWebSocketService = menuWebSocketService
    mockMenuCacheManager = new MenuCacheManager()
    
    // 重置 mock 调用记录
    vi.clearAllMocks()
    mockWebSocketService.on.mockClear()

    // 创建测试store
    store = createStore({
      modules: {
        menu: menuModule,
        user: {
          namespaced: true,
          state: {
            currentUser: { id: 'test-user' },
            permissions: ['read', 'write'],
            roles: ['admin']
          }
        }
      }
    })

    // 清除所有mock
    vi.clearAllMocks()
  })

  afterEach(() => {
    // 清理
    store = null
  })

  describe('实时推送机制测试', () => {
    it('应该正确处理WebSocket连接状态', async () => {
      // 初始化WebSocket
      await store.dispatch('menu/initializeWebSocket', 'test-user')

      // 验证连接事件监听器已设置
      expect(mockWebSocketService.on).toHaveBeenCalledWith('connected', expect.any(Function))
      expect(mockWebSocketService.on).toHaveBeenCalledWith('disconnected', expect.any(Function))
      expect(mockWebSocketService.on).toHaveBeenCalledWith('menuUpdated', expect.any(Function))
      expect(mockWebSocketService.on).toHaveBeenCalledWith('toolStatusChanged', expect.any(Function))

      // 验证连接已建立
      expect(mockWebSocketService.connect).toHaveBeenCalledWith('test-user')
    })

    it('应该正确处理菜单更新推送', async () => {
      // 初始化WebSocket以注册事件监听器
      await store.dispatch('menu/initializeWebSocket', 'test-user')
      
      const mockMenuUpdates = [
        {
          id: 'menu-1',
          name: '更新的菜单',
          path: '/updated',
          enabled: true
        }
      ]

      // 模拟接收到菜单更新推送
      const updateData = {
        incremental: true,
        action: 'update',
        updates: mockMenuUpdates,
        version: 2
      }

      // 获取menuUpdated事件处理器
      const menuUpdatedHandler = mockWebSocketService.on.mock.calls
        .find(call => call[0] === 'menuUpdated')?.[1]

      expect(menuUpdatedHandler).toBeDefined()

      // 模拟处理菜单更新
      if (menuUpdatedHandler) {
        await menuUpdatedHandler(updateData)
      }

      // 验证增量更新被调用
      // 注意：这里需要mock相关的dispatch调用
    })

    it('应该正确处理工具状态变更推送', async () => {
      // 初始化WebSocket以注册事件监听器
      await store.dispatch('menu/initializeWebSocket', 'test-user')
      
      const mockToolUpdate = {
        toolId: 'tool-1',
        enabled: false,
        incremental: false
      }

      // 获取toolStatusChanged事件处理器
      const toolStatusHandler = mockWebSocketService.on.mock.calls
        .find(call => call[0] === 'toolStatusChanged')?.[1]

      expect(toolStatusHandler).toBeDefined()

      if (toolStatusHandler) {
        await toolStatusHandler(mockToolUpdate)
      }

      // 验证工具状态已更新
      // 这里需要检查store状态的变化
    })
  })

  describe('版本控制机制测试', () => {
    it('应该正确检测版本冲突', async () => {
      // Mock版本服务返回冲突
      const mockVersionInfo = {
        current: 1,
        server: 3,
        hasConflicts: true,
        conflictItems: ['menu-1']
      }

      vi.spyOn(versionService, 'getServerVersion').mockResolvedValue({
        version: 3,
        timestamp: Date.now()
      })

      vi.spyOn(versionService, 'syncMenuConfig').mockResolvedValue({
        success: false,
        hasConflicts: true,
        conflicts: mockVersionInfo.conflictItems,
        menuUpdates: [],
        toolUpdates: []
      })

      // 执行版本同步
      await store.dispatch('menu/syncMenuVersion')

      // 验证冲突状态被正确设置
      const state = store.state.menu
      expect(state.versionInfo.hasConflicts).toBe(true)
    })

    it('应该正确处理版本同步', async () => {
      const mockSyncResult = {
        success: true,
        hasConflicts: false,
        menuUpdates: [
          {
            action: 'update' as const,
            item: {
              id: 'menu-1',
              name: '同步的菜单',
              path: '/synced'
            }
          }
        ],
        toolUpdates: []
      }

      vi.spyOn(versionService, 'getServerVersion').mockResolvedValue({
        version: 2,
        timestamp: Date.now()
      })

      vi.spyOn(versionService, 'syncMenuConfig').mockResolvedValue(mockSyncResult)

      // 执行版本同步
      await store.dispatch('menu/syncMenuVersion')

      // 验证版本信息已更新
      const state = store.state.menu
      expect(state.versionInfo.current).toBe(2)
      expect(state.versionInfo.hasConflicts).toBe(false)
    })
  })

  describe('缓存同步机制测试', () => {
    it('应该正确执行智能缓存更新', async () => {
      const mockMenuConfig = [
        { id: 'menu-1', name: '菜单1', path: '/menu1' },
        { id: 'menu-2', name: '菜单2', path: '/menu2' }
      ]

      // Mock缓存服务
      vi.spyOn(mockMenuCacheManager, 'syncMenuConfig').mockResolvedValue(mockMenuConfig)

      // 执行菜单配置获取
      const result = await store.dispatch('menu/fetchMenuConfig')

      // 验证智能缓存被使用
      expect(mockMenuCacheManager.syncMenuConfig).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })

    it('应该正确处理增量缓存更新', async () => {
      const mockUpdates = [
        {
          action: 'update' as const,
          item: { id: 'menu-1', name: '更新的菜单', path: '/updated' }
        }
      ]

      const mockResult = [
        { id: 'menu-1', name: '更新的菜单', path: '/updated' },
        { id: 'menu-2', name: '菜单2', path: '/menu2' }
      ]

      vi.spyOn(mockMenuCacheManager, 'incrementalUpdateMenus').mockResolvedValue(mockResult)

      // 执行增量更新
      const result = await store.dispatch('menu/incrementalUpdateMenus', mockUpdates)

      // 验证增量更新被正确执行
      expect(mockMenuCacheManager.incrementalUpdateMenus).toHaveBeenCalledWith(mockUpdates)
      expect(result).toEqual(mockResult)
    })

    it('应该正确监控缓存健康状态', () => {
      const mockCacheStats = {
        size: 10,
        items: { 'menu_config': {}, 'tools_config': {} },
        hitRate: 0.85,
        missCount: 3,
        hitCount: 17
      }

      const mockCacheHealth = {
        isHealthy: true,
        hitRate: 0.85,
        cacheSize: 10,
        issues: []
      }

      vi.spyOn(mockMenuCacheManager, 'getCacheStats').mockReturnValue(mockCacheStats)
      vi.spyOn(mockMenuCacheManager, 'getCacheHealth').mockReturnValue(mockCacheHealth)

      // 更新缓存统计
      store.dispatch('menu/updateCacheStats')

      // 验证缓存统计被正确更新
      const state = store.state.menu
      expect(state.cacheStats.hitRate).toBe(0.85)
      expect(state.cacheStats.isHealthy).toBe(true)
    })
  })

  describe('系统协同工作测试', () => {
    // 存储事件处理器
    const eventHandlers: Record<string, Function> = {}
    
    beforeEach(() => {
      // 重置事件处理器
      Object.keys(eventHandlers).forEach(key => delete eventHandlers[key])
      
      // 重新设置 mock 实现
      mockWebSocketService.on.mockImplementation((event: string, handler: Function) => {
        eventHandlers[event] = handler
      })
    })
    
    it('应该正确处理完整的菜单更新流程', async () => {
      // 定义事件处理器别名
      const toolStatusHandler = () => eventHandlers['toolStatusChanged']
      const cacheInvalidatedHandler = () => eventHandlers['cacheInvalidated']
      const permissionChangedHandler = () => eventHandlers['permissionChanged']
      // 1. 模拟WebSocket推送菜单更新
      const updateData = {
        incremental: true,
        action: 'update',
        updates: [
          { id: 'menu-1', name: '协同更新菜单', path: '/collaborative' }
        ],
        version: 3
      }

      // 2. Mock相关服务
      vi.spyOn(versionService, 'getServerVersion').mockResolvedValue({
        version: 3,
        timestamp: Date.now()
      })

      vi.spyOn(mockMenuCacheManager, 'handleMenuUpdate').mockResolvedValue()
      vi.spyOn(mockMenuCacheManager, 'incrementalUpdateMenus').mockResolvedValue([
        { id: 'menu-1', name: '协同更新菜单', path: '/collaborative' }
      ])

      // 3. 初始化WebSocket并获取事件处理器
      await store.dispatch('menu/initializeWebSocket', 'test-user')
      const menuUpdatedHandler = mockWebSocketService.on.mock.calls
        .find(call => call[0] === 'menuUpdated')?.[1]

      // 4. 模拟接收推送并处理
      if (menuUpdatedHandler) {
        await menuUpdatedHandler(updateData)
      }

      // 5. 验证整个流程
      expect(mockMenuCacheManager.handleMenuUpdate).toHaveBeenCalledWith({
        type: 'menu',
        action: 'update',
        items: updateData.updates,
        version: updateData.version
      })
    })

    it('应该正确处理缓存失效和重新加载', async () => {
      // 定义事件处理器别名
      const toolStatusHandler = () => eventHandlers['toolStatusChanged']
      const cacheInvalidatedHandler = () => eventHandlers['cacheInvalidated']
      const permissionChangedHandler = () => eventHandlers['permissionChanged']
      
      // 1. 初始化WebSocket以注册事件监听器
      await store.dispatch('menu/initializeWebSocket', 'test-user')
      
      // 2. 获取缓存失效处理器
      const handler = cacheInvalidatedHandler()
      expect(handler).toBeDefined()

      // 3. Mock缓存清理
      vi.spyOn(mockMenuCacheManager, 'clearExpiredCache').mockReturnValue(5)

      // 4. 处理缓存失效
      if (handler) {
        handler({ pattern: '.*menu.*' })
      }

      // 5. 验证缓存被清理
      expect(mockMenuCacheManager.clearExpiredCache).toHaveBeenCalled()
    })

    it('应该正确处理权限变更影响的菜单重载', async () => {
      // 定义事件处理器别名
      const toolStatusHandler = () => eventHandlers['toolStatusChanged']
      const cacheInvalidatedHandler = () => eventHandlers['cacheInvalidated']
      const permissionChangedHandler = () => eventHandlers['permissionChanged']
      
      // 1. Mock store dispatch来跟踪调用
      const dispatchSpy = vi.spyOn(store, 'dispatch')
      
      // 2. 初始化WebSocket以注册事件监听器
      await store.dispatch('menu/initializeWebSocket', 'test-user')
      
      // 3. 清除之前的dispatch调用记录
      dispatchSpy.mockClear()
      
      // 4. 获取权限变更处理器
      const handler = permissionChangedHandler()
      expect(handler).toBeDefined()

      // 5. 处理权限变更
        if (handler) {
          await handler({ userId: 'test-user', permissions: ['read'] })
        }

      // 6. 验证菜单配置被重新获取
      expect(store.dispatch).toHaveBeenCalledWith('menu/refreshMenuConfig', undefined)
      expect(store.dispatch).toHaveBeenCalledWith('menu/fetchMenuConfig', undefined)
      expect(store.dispatch).toHaveBeenCalledWith('menu/fetchToolsConfig', undefined)
      expect(store.dispatch).toHaveBeenCalledWith('menu/clearExpiredCache', undefined)
      expect(store.dispatch).toHaveBeenCalledWith('menu/updateCacheStats', undefined)
    })
  })

  describe('错误处理和降级机制测试', () => {
    it('应该在WebSocket推送处理失败时降级到全量更新', async () => {
      // 1. Mock增量更新失败
      vi.spyOn(mockMenuCacheManager, 'handleMenuUpdate').mockRejectedValue(
        new Error('增量更新失败')
      )

      // 2. Mock store dispatch来跟踪调用
      const dispatchSpy = vi.spyOn(store, 'dispatch')
      
      // 3. 初始化WebSocket以注册事件监听器
      await store.dispatch('menu/initializeWebSocket', 'test-user')
      
      // 4. 清除之前的dispatch调用记录
      dispatchSpy.mockClear()

      // 5. 获取菜单更新处理器
      const menuUpdatedHandler = mockWebSocketService.on.mock.calls
        .find(call => call[0] === 'menuUpdated')?.[1]

      // 6. 模拟处理失败的增量更新
      if (menuUpdatedHandler) {
        await menuUpdatedHandler({
          incremental: true,
          action: 'update',
          updates: [{ id: 'menu-1' }],
          version: 2
        })
      }

      // 7. 验证降级到全量更新
      expect(store.dispatch).toHaveBeenCalledWith('menu/refreshMenuConfig', undefined)
      expect(store.dispatch).toHaveBeenCalledWith('menu/fetchMenuConfig', undefined)
      expect(store.dispatch).toHaveBeenCalledWith('menu/fetchToolsConfig', undefined)
    })

    it('应该在版本同步失败时继续正常工作', async () => {
      // Mock版本同步失败
      vi.spyOn(versionService, 'syncMenuConfig').mockRejectedValue(
        new Error('版本同步失败')
      )

      // 执行版本同步（应该不抛出错误）
      await expect(store.dispatch('menu/syncMenuVersion')).rejects.toThrow('版本同步失败')

      // 验证错误状态被设置
      const state = store.state.menu
      expect(state.error.syncing).toBe('版本同步失败')
    })
  })
})