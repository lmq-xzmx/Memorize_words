import axios from 'axios'
import type { MenuItem, ToolItem } from '@/composables/useMenuManager'
import { cacheService, menuCacheManager } from './cacheService'
import { 
  getWebSocketConfig, 
  WebSocketMessageType, 
  WebSocketStatus,
  type WebSocketMessage,
  type MenuUpdateData,
  type ToolStatusChangeData,
  type PermissionUpdateData,
  validateWebSocketMessage,
  createWebSocketMessage
} from '@/config/websocketConfig'
import { menuAdapter, type BackendMenuConfig } from './menuAdapter'
import { getApiBaseUrl } from '../../config/apiconfig'

// API 响应类型
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  success: boolean
}

// 菜单版本信息
interface MenuVersion {
  version: number
  lastUpdated: string
  checksum?: string
}

// 用户菜单权限
interface UserMenuPermission {
  userId: string
  menuId: string
  permissions: string[]
  roles: string[]
  enabled: boolean
}

// 工具状态更新
interface ToolStatusUpdate {
  toolId: string
  enabled: boolean
  userId?: string
}

/**
 * 菜单服务类
 */
class MenuService {
  private baseURL = '/api/menu'
  private cache = new Map<string, any>()
  private cacheTimeout = 5 * 60 * 1000 // 5分钟缓存

  /**
   * 获取用户菜单配置
   */
  async getUserMenuConfig(userId?: string): Promise<ApiResponse<{menuItems: MenuItem[], toolItems: ToolItem[]}>> {
    const cacheKey = `menu_config_${userId || 'current'}`
    
    // 检查缓存
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey)
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data
      }
    }

    try {
      const response = await fetch(`${getApiBaseUrl()}/permissions/frontend-menu-config/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        console.warn(`菜单配置API请求失败 (${response.status})，使用默认配置`)
        return this.getDefaultMenuConfig()
      }
      
      const backendData = await response.json()
      
      if (backendData.success) {
        // 使用适配器转换数据格式
        const transformedData = menuAdapter.transformMenuConfig(backendData.data as BackendMenuConfig)
        
        // 根据权限过滤菜单和工具
        const filteredMenuItems = menuAdapter.filterMenuByPermissions(transformedData.menuItems)
        const filteredToolItems = menuAdapter.filterToolsByPermissions(transformedData.toolItems)
        
        const finalData = {
          menuItems: filteredMenuItems,
          toolItems: filteredToolItems
        }
        
        const result = {
          code: 200,
          success: true,
          data: finalData,
          message: '获取菜单配置成功'
        }
        
        // 缓存结果
        this.cache.set(cacheKey, {
          data: result,
          timestamp: Date.now()
        })
        
        return result
      }
      
      return backendData
    } catch (error) {
      console.error('获取用户菜单配置失败:', error)
      console.warn('使用默认菜单配置')
      
      // 返回默认配置
      return this.getDefaultMenuConfig()
    }
  }

  /**
   * 获取工具配置
   */
  async getToolsConfig(userId?: string): Promise<ApiResponse<ToolItem[]>> {
    const cacheKey = `tools_config_${userId || 'current'}`
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey)
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data
      }
    }

    try {
      const response = await fetch(`${getApiBaseUrl()}/permissions/frontend-menu-config/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        console.warn(`工具配置API请求失败 (${response.status})，使用默认配置`)
        return this.getDefaultToolsConfig()
      }
      
      const backendData = await response.json()
      
      if (backendData.success && backendData.data.toolsMenuConfig?.items) {
        // 使用适配器转换工具配置
        const transformedTools = backendData.data.toolsMenuConfig.items.map(
          (tool: any) => menuAdapter.transformToolItem(tool)
        )
        
        // 根据权限过滤工具
        const filteredTools = menuAdapter.filterToolsByPermissions(transformedTools)
        
        const result = {
          code: 200,
          success: true,
          data: filteredTools,
          message: '获取工具配置成功'
        }
        
        this.cache.set(cacheKey, {
          data: result,
          timestamp: Date.now()
        })
        
        return result
      }
      
      return {
        code: 404,
        success: false,
        data: [],
        message: '工具配置为空'
      }
    } catch (error) {
      console.error('获取工具配置失败:', error)
      console.warn('使用默认工具配置')
      
      // 返回默认配置
      return this.getDefaultToolsConfig()
    }
  }

  /**
   * 获取菜单版本信息
   */
  async getMenuVersion(): Promise<ApiResponse<MenuVersion>> {
    try {
      const response = await axios.get<ApiResponse<MenuVersion>>(
        `${this.baseURL}/version`
      )
      return response.data
    } catch (error) {
      console.error('获取菜单版本失败:', error)
      throw error
    }
  }

  /**
   * 检查菜单更新
   */
  async checkMenuUpdates(currentVersion: number): Promise<ApiResponse<{ hasUpdate: boolean; version: MenuVersion }>> {
    try {
      const response = await axios.get<ApiResponse<{ hasUpdate: boolean; version: MenuVersion }>>(
        `${this.baseURL}/check-updates`,
        {
          params: { currentVersion }
        }
      )
      return response.data
    } catch (error) {
      console.error('检查菜单更新失败:', error)
      throw error
    }
  }

  /**
   * 更新工具状态
   */
  async updateToolStatus(update: ToolStatusUpdate): Promise<ApiResponse<boolean>> {
    try {
      const response = await axios.post<ApiResponse<boolean>>(
        `${this.baseURL}/tool-status`,
        update
      )

      // 清除相关缓存
      this.clearToolsCache(update.userId)

      return response.data
    } catch (error) {
      console.error('更新工具状态失败:', error)
      throw error
    }
  }

  /**
   * 批量更新工具状态
   */
  async batchUpdateToolStatus(updates: ToolStatusUpdate[]): Promise<ApiResponse<boolean>> {
    try {
      const response = await axios.post<ApiResponse<boolean>>(
        `${this.baseURL}/batch-tool-status`,
        { updates }
      )

      // 清除所有工具缓存
      this.clearAllToolsCache()

      return response.data
    } catch (error) {
      console.error('批量更新工具状态失败:', error)
      throw error
    }
  }

  /**
   * 获取用户菜单权限
   */
  async getUserMenuPermissions(userId?: string): Promise<ApiResponse<UserMenuPermission[]>> {
    try {
      const response = await axios.get<ApiResponse<UserMenuPermission[]>>(
        `${this.baseURL}/user-permissions`,
        {
          params: { userId }
        }
      )
      return response.data
    } catch (error) {
      console.error('获取用户菜单权限失败:', error)
      throw error
    }
  }

  /**
   * 刷新菜单缓存
   */
  async refreshMenuCache(userId?: string): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/refresh-cache`, {
        userId
      })

      // 清除本地缓存
      this.clearCache(userId)
    } catch (error) {
      console.error('刷新菜单缓存失败:', error)
      throw error
    }
  }

  /**
   * 记录菜单使用统计
   */
  async recordMenuUsage(menuId: string, action: string = 'click'): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/usage-stats`, {
        menuId,
        action,
        timestamp: Date.now()
      })
    } catch (error) {
      // 统计失败不影响主要功能
      console.warn('记录菜单使用统计失败:', error)
    }
  }

  /**
   * 获取菜单使用统计
   */
  async getMenuUsageStats(timeRange?: { start: string; end: string }): Promise<ApiResponse<any>> {
    try {
      const response = await axios.get<ApiResponse<any>>(
        `${this.baseURL}/usage-stats`,
        {
          params: timeRange
        }
      )
      return response.data
    } catch (error) {
      console.error('获取菜单使用统计失败:', error)
      throw error
    }
  }

  /**
   * 清除指定用户的缓存
   */
  private clearCache(userId?: string): void {
    const userKey = userId || 'current'
    const keysToDelete = Array.from(this.cache.keys()).filter(key => 
      key.includes(userKey)
    )
    
    keysToDelete.forEach(key => {
      this.cache.delete(key)
    })
  }

  /**
   * 清除工具缓存
   */
  private clearToolsCache(userId?: string): void {
    const userKey = userId || 'current'
    const cacheKey = `tools_config_${userKey}`
    this.cache.delete(cacheKey)
  }

  /**
   * 清除所有工具缓存
   */
  private clearAllToolsCache(): void {
    const keysToDelete = Array.from(this.cache.keys()).filter(key => 
      key.startsWith('tools_config_')
    )
    
    keysToDelete.forEach(key => {
      this.cache.delete(key)
    })
  }

  /**
   * 清除所有缓存
   */
  clearAllCache(): void {
    this.cache.clear()
  }

  /**
   * 获取缓存统计信息
   */
  getCacheStats(): { size: number; keys: string[] } {
    return cacheService.getStats()
  }
  
  /**
   * 使用缓存管理器同步菜单配置
   */
  async syncMenuConfig(serverVersion: number): Promise<ApiResponse<MenuItem[]>> {
    try {
      const menuConfig = await menuCacheManager.syncMenuConfig(
        serverVersion,
        () => this.fetchMenuConfigFromServer()
      )
      
      return {
        code: 200,
        success: true,
        data: menuConfig,
        message: '菜单配置同步成功'
      }
    } catch (error: any) {
      return {
        code: 500,
        success: false,
        data: [],
        message: error.message || '菜单配置同步失败'
      }
    }
  }
  
  /**
   * 从服务器获取菜单配置
   */
  private async fetchMenuConfigFromServer(): Promise<MenuItem[]> {
    const response = await fetch(`${getApiBaseUrl()}/permissions/frontend-menu-config/`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return data.success ? data.data.bottomNavMenus || [] : []
  }
  
  /**
   * 获取认证令牌
   */
  private getAuthToken(): string {
    const token = localStorage.getItem('token')
    if (!token) {
      console.warn('未找到认证token，请先登录或设置token')
      // 提供一个临时的测试token（仅用于开发测试）
      const testToken = 'test-token-for-development'
      console.log('使用临时测试token:', testToken)
      return testToken
    }
    return token
  }
  
  /**
   * 获取默认菜单配置
   */
  private getDefaultMenuConfig(): ApiResponse<{menuItems: MenuItem[], toolItems: ToolItem[]}> {
    const userRole = this.getCurrentUserRole()
    const defaultMenuItems = menuAdapter.getDefaultMenuByRole(userRole)
    
    return {
      code: 200,
      success: true,
      data: {
        menuItems: defaultMenuItems,
        toolItems: []
      },
      message: '使用默认菜单配置'
    }
  }
  
  /**
   * 获取默认工具配置
   */
  private getDefaultToolsConfig(): ApiResponse<ToolItem[]> {
    const userRole = this.getCurrentUserRole()
    const defaultTools = menuAdapter.getDefaultToolsByRole(userRole)
    
    return {
      code: 200,
      success: true,
      data: defaultTools,
      message: '使用默认工具配置'
    }
  }
  
  /**
   * 获取当前用户角色
   */
  private getCurrentUserRole(): string {
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      try {
        const user = JSON.parse(userInfo)
        return user.role || 'student'
      } catch (error) {
        console.error('解析用户信息失败:', error)
      }
    }
    return 'student'
  }
}

// 创建单例实例
const menuService = new MenuService()

// WebSocket 连接用于实时更新
class MenuWebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private config = getWebSocketConfig()
  private heartbeatInterval: number | null = null
  private listeners = new Map<string, Function[]>()
  private status: WebSocketStatus = WebSocketStatus.DISCONNECTED
  private userId?: string
  private sessionId?: string

  /**
   * 连接 WebSocket
   */
  connect(userId?: string): void {
    // 如果已有连接，先关闭
    if (this.ws) {
      console.log('关闭现有WebSocket连接，状态:', this.ws.readyState)
      this.ws.close()
      this.ws = null
    }

    this.userId = userId
    this.status = WebSocketStatus.CONNECTING
    this.emit('statusChanged', this.status)
    
    console.log('开始建立WebSocket连接，用户ID:', userId)

    // 构建WebSocket URL，确保与后端路由匹配
    const baseUrl = this.config.url.endsWith('/') ? this.config.url.slice(0, -1) : this.config.url
    // 检查userId是否为有效的数字ID，如果不是则使用匿名路径
    const isValidUserId = userId && /^\d+$/.test(userId.toString())
    let wsUrl = isValidUserId ? `${baseUrl}/${userId}/` : `${baseUrl}/anonymous/`
    
    console.log('WebSocket URL构建详情:', {
      originalConfigUrl: this.config.url,
      baseUrl,
      userId,
      isValidUserId,
      finalUrl: wsUrl
    })
    
    // 如果是认证用户，添加token参数
    if (isValidUserId) {
      const token = localStorage.getItem('token')
      if (token) {
        wsUrl += `?token=${encodeURIComponent(token)}`
        console.log('WebSocket URL包含token认证')
      } else {
        console.warn('用户已认证但未找到token，使用匿名连接')
        wsUrl = `${baseUrl}/anonymous/`
      }
    }
    
    try {
      // 暂时移除protocols参数，避免协议不匹配问题
      this.ws = new WebSocket(wsUrl)
      console.log('WebSocket创建成功，URL:', wsUrl)
      
      // 连接超时处理
      const connectionTimeout = setTimeout(() => {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
          this.ws.close()
          this.handleConnectionError(new Error('连接超时'))
        }
      }, this.config.connectionTimeout)
      
      this.ws.onopen = () => {
        clearTimeout(connectionTimeout)
        console.log('菜单 WebSocket 连接已建立，URL:', wsUrl)
        console.log('WebSocket readyState:', this.ws?.readyState)
        // 不要立即设置为CONNECTED，等待连接确认消息
        this.status = WebSocketStatus.CONNECTING
        this.reconnectAttempts = 0
        this.emit('statusChanged', this.status)
        
        // 发送连接消息给后端 - 直接发送，不通过sendMessage方法
        const connectMessage = {
          type: 'connect',
          data: {
            userId: this.userId || null,
            client_info: 'menu-websocket-client'
          },
          timestamp: Date.now()
        }
        
        console.log('发送连接消息:', connectMessage)
        const messageStr = JSON.stringify(connectMessage)
        console.log('消息字符串:', messageStr)
        
        // 直接发送，确保在onopen事件中立即发送
        if (this.ws) {
          this.ws.send(messageStr)
          console.log('连接消息已直接发送到WebSocket')
        }
        
        console.log('WebSocket连接已建立，已发送连接消息，等待后端连接确认')
      }
      
      this.ws.onmessage = (event) => {
        try {
          console.log('收到原始WebSocket消息:', event.data)
          const message = JSON.parse(event.data)
          console.log('解析后的WebSocket消息:', message)
          console.log('消息类型:', message.type)
          console.log('WebSocket连接状态:', this.ws?.readyState)
          
          // 直接处理消息，跳过验证
          this.handleMessage(message)
          
          console.log('消息处理完成，WebSocket连接状态:', this.ws?.readyState)
          
          // 原来的验证逻辑（暂时注释）
          // if (validateWebSocketMessage(message)) {
          //   this.handleMessage(message)
          // } else {
          //   console.warn('收到无效的WebSocket消息:', message)
          // }
        } catch (error) {
          console.error('解析 WebSocket 消息失败:', error, '原始数据:', event.data)
          // 不要抛出错误，避免导致连接断开
        }
      }
      
      this.ws.onclose = (event) => {
        clearTimeout(connectionTimeout)
        console.log('菜单 WebSocket 连接已关闭，代码:', event.code, '原因:', event.reason, '用户ID:', this.userId)
        this.status = WebSocketStatus.DISCONNECTED
        this.stopHeartbeat()
        this.emit('disconnected', { code: event.code, reason: event.reason })
        this.emit('statusChanged', this.status)
        
        if (event.code !== 1000 && event.code !== 1001) {
          console.log('连接异常关闭，准备重连')
          this.attemptReconnect()
        }
      }
      
      this.ws.onerror = (error) => {
        clearTimeout(connectionTimeout)
        console.error('菜单 WebSocket 错误:', error)
        this.handleConnectionError(error)
      }
    } catch (error) {
      console.error('创建 WebSocket 连接失败:', error)
      this.handleConnectionError(error)
    }
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 处理 WebSocket 消息
   */
  private handleMessage(message: WebSocketMessage): void {
    try {
      console.log('处理WebSocket消息:', message.type, message)
      switch (message.type) {
        case WebSocketMessageType.CONNECTION_CONFIRMED:
          try {
            console.log('收到连接确认消息:', message)
            // 后端发送的消息格式：{ type: 'connection_confirmed', data: { ... }, timestamp: ... }
            const messageData = message.data || {}
            this.sessionId = messageData.sessionId || `session_${Date.now()}`
            console.log('设置sessionId:', this.sessionId)
            console.log('连接确认数据:', messageData)
            
            // 更新连接状态
            this.status = WebSocketStatus.CONNECTED
            console.log('更新连接状态为CONNECTED')
            
            this.emit('connectionConfirmed', messageData)
            console.log('触发connectionConfirmed事件')
            this.emit('statusChanged', this.status)
            console.log('触发statusChanged事件')
            
            // 重置重连计数
            this.reconnectAttempts = 0
            console.log('重置重连计数为0')
            
            // 连接确认后延迟启动心跳机制，确保连接完全稳定
            console.log('连接确认完成，延迟启动心跳机制')
            setTimeout(() => {
              console.log('延迟后启动心跳机制')
              this.startHeartbeat()
            }, 1000) // 延迟1秒启动心跳
          } catch (error) {
            console.error('处理CONNECTION_CONFIRMED消息时出错:', error)
            // 不要抛出错误，避免导致连接断开
          }
          break
      case WebSocketMessageType.MENU_UPDATED:
        this.handleMenuUpdate(message.data as MenuUpdateData)
        break
      case WebSocketMessageType.TOOL_STATUS_CHANGED:
        this.handleToolStatusChange(message.data as ToolStatusChangeData)
        break
      case WebSocketMessageType.PERMISSION_UPDATED:
        this.handlePermissionUpdate(message.data as PermissionUpdateData)
        break
      case WebSocketMessageType.HEARTBEAT:
      case WebSocketMessageType.HEARTBEAT_RESPONSE:
        // 心跳响应，无需处理
        console.log('收到心跳响应:', message.data)
        break
      case WebSocketMessageType.ERROR:
        console.error('服务器错误:', message.data)
        this.emit('error', message.data)
        break
      default:
        console.warn('未知的 WebSocket 消息类型:', message.type)
    }
    } catch (error) {
      console.error('处理WebSocket消息时发生错误:', error, message)
      // 不要抛出错误，避免导致连接断开
    }
  }
  
  /**
   * 处理菜单更新
   */
  private handleMenuUpdate(data: MenuUpdateData): void {
    console.log('菜单更新:', data)
    
    // 清除相关缓存
    if (data.action === 'update' || data.action === 'delete') {
      cacheService.delete('menu_config')
    }
    
    this.emit('menuUpdated', data)
  }
  
  /**
   * 处理工具状态变更
   */
  private handleToolStatusChange(data: ToolStatusChangeData): void {
    console.log('工具状态变更:', data)
    this.emit('toolStatusChanged', data)
  }
  
  /**
   * 处理权限更新
   */
  private handlePermissionUpdate(data: PermissionUpdateData): void {
    console.log('权限更新:', data)
    
    // 清除用户权限缓存
    cacheService.clearUserPermissions(data.userId)
    
    this.emit('permissionChanged', data)
  }
  
  /**
   * 开始心跳
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        // 使用简化的心跳消息格式，与测试脚本保持一致
        const heartbeatMessage = {
          type: 'heartbeat',
          timestamp: Date.now()
        }
        this.ws.send(JSON.stringify(heartbeatMessage))
      }
    }, this.config.heartbeatInterval)
  }
  
  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }
  
  /**
   * 发送消息
   */
  private sendMessage(message: any): void {
    console.log('尝试发送WebSocket消息:', message)
    console.log('WebSocket状态:', this.ws?.readyState)
    console.log('WebSocket.OPEN常量:', WebSocket.OPEN)
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const messageStr = JSON.stringify(message)
      console.log('发送消息字符串:', messageStr)
      this.ws.send(messageStr)
      console.log('消息已发送到WebSocket')
    } else {
      console.warn('WebSocket未连接，无法发送消息，当前状态:', this.ws?.readyState)
    }
  }
  
  /**
   * 获取连接状态
   */
  getStatus(): WebSocketStatus {
    return this.status
  }
  
  /**
   * 获取连接信息
   */
  getConnectionInfo(): { status: WebSocketStatus; reconnectAttempts: number; userId?: string } {
    return {
      status: this.status,
      reconnectAttempts: this.reconnectAttempts,
      userId: this.userId
    }
  }

  /**
   * 尝试重连
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('WebSocket 重连次数已达上限')
      this.status = WebSocketStatus.ERROR
      this.emit('reconnectFailed')
      this.emit('statusChanged', this.status)
      return
    }

    this.reconnectAttempts++
    this.status = WebSocketStatus.RECONNECTING
    this.emit('statusChanged', this.status)
    
    const delay = this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1)
    
    setTimeout(() => {
      console.log(`尝试第 ${this.reconnectAttempts} 次重连...`)
      this.connect(this.userId)
    }, delay)
  }
  
  /**
   * 处理连接错误
   */
  private handleConnectionError(error: any): void {
    this.status = WebSocketStatus.ERROR
    this.emit('error', error)
    this.emit('statusChanged', this.status)
    
    // 尝试重连
    this.attemptReconnect()
  }

  /**
   * 添加事件监听器
   */
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(callback)
  }

  /**
   * 移除事件监听器
   */
  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * 触发事件
   */
  private emit(event: string, data?: any): void {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('WebSocket 事件回调执行失败:', error)
        }
      })
    }
  }
}

// 创建 WebSocket 服务实例
const menuWebSocketService = new MenuWebSocketService()

export {
  menuService,
  menuWebSocketService,
  MenuService,
  MenuWebSocketService
}

export type {
  ApiResponse,
  MenuVersion,
  UserMenuPermission,
  ToolStatusUpdate
}

export default menuService