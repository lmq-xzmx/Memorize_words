// WebSocket 配置
export interface WebSocketConfig {
  url: string
  reconnectInterval: number
  maxReconnectAttempts: number
  heartbeatInterval: number
  connectionTimeout: number
  protocols?: string[]
}

// 默认 WebSocket 配置
export const defaultWebSocketConfig: WebSocketConfig = {
  url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/permissions/',
  reconnectInterval: 3000, // 3秒
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000, // 30秒
  connectionTimeout: 10000, // 10秒
  protocols: ['menu-protocol']
}

// 消息类型定义
export enum WebSocketMessageType {
  // 连接相关
  CONNECT = 'connect',
  CONNECTION_CONFIRMED = 'connection_confirmed',
  DISCONNECT = 'disconnect',
  HEARTBEAT = 'heartbeat',
  HEARTBEAT_RESPONSE = 'heartbeat_response',
  
  // 菜单相关
  MENU_UPDATED = 'menu_updated',
  MENU_CONFIG_CHANGED = 'menu_config_changed',
  MENU_PERMISSION_CHANGED = 'menu_permission_changed',
  
  // 工具相关
  TOOL_STATUS_CHANGED = 'tool_status_changed',
  TOOL_CONFIG_UPDATED = 'tool_config_updated',
  
  // 权限相关
  PERMISSION_UPDATED = 'permission_updated',
  ROLE_CHANGED = 'role_changed',
  
  // 用户相关
  USER_STATUS_CHANGED = 'user_status_changed',
  
  // 系统相关
  SYSTEM_NOTIFICATION = 'system_notification',
  ERROR = 'error'
}

// WebSocket 消息接口
export interface WebSocketMessage {
  type: WebSocketMessageType
  data?: any
  timestamp?: number
  userId?: string
  sessionId?: string
}

// 菜单更新消息数据
export interface MenuUpdateData {
  menuId: string
  action: 'create' | 'update' | 'delete'
  menuData?: any
  version: number
  affectedUsers?: string[]
}

// 工具状态变更消息数据
export interface ToolStatusChangeData {
  toolId: string
  enabled: boolean
  userId?: string
  config?: any
}

// 权限更新消息数据
export interface PermissionUpdateData {
  userId: string
  permissions: string[]
  roles: string[]
  action: 'grant' | 'revoke' | 'update'
}

// 系统通知消息数据
export interface SystemNotificationData {
  title: string
  message: string
  type: 'info' | 'warning' | 'error' | 'success'
  duration?: number
  actions?: Array<{
    text: string
    action: string
  }>
}

// WebSocket 连接状态
export enum WebSocketStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTING = 'disconnecting',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

// WebSocket 事件类型
export enum WebSocketEventType {
  OPEN = 'open',
  CLOSE = 'close',
  ERROR = 'error',
  MESSAGE = 'message',
  RECONNECT = 'reconnect',
  RECONNECT_FAILED = 'reconnect_failed'
}

// 环境配置
export const getWebSocketConfig = (): WebSocketConfig => {
  const env = import.meta.env.MODE || 'development'
  
  const configs: Record<string, Partial<WebSocketConfig>> = {
    development: {
      url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/permissions/',
      reconnectInterval: 3000,
      maxReconnectAttempts: 10
    },
    production: {
      url: import.meta.env.VITE_WS_URL || 'wss://api.example.com/ws/permissions/',
      reconnectInterval: 5000,
      maxReconnectAttempts: 5
    },
    test: {
      url: 'ws://localhost:8001/ws/permissions/',
      reconnectInterval: 1000,
      maxReconnectAttempts: 3
    }
  }
  
  return {
    ...defaultWebSocketConfig,
    ...configs[env]
  }
}

// 消息验证函数
export function validateWebSocketMessage(message: any): message is WebSocketMessage {
  if (!message || typeof message !== 'object') {
    return false
  }
  
  if (!message.type || !Object.values(WebSocketMessageType).includes(message.type)) {
    return false
  }
  
  return true
}

// 创建 WebSocket 消息
export function createWebSocketMessage(
  type: WebSocketMessageType,
  data?: any,
  userId?: string
): WebSocketMessage {
  return {
    type,
    data,
    timestamp: Date.now(),
    userId,
    sessionId: generateSessionId()
  }
}

// 生成会话ID
function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15)
}

// 错误处理配置
export const errorHandlingConfig = {
  // 是否自动重连
  autoReconnect: true,
  
  // 错误重试策略
  retryStrategy: {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffFactor: 2
  },
  
  // 错误日志配置
  logging: {
    enabled: true,
    level: 'error',
    includeStack: import.meta.env.DEV
  }
}

// 性能监控配置
export const performanceConfig = {
  // 是否启用性能监控
  enabled: import.meta.env.DEV,
  
  // 监控指标
  metrics: {
    connectionTime: true,
    messageLatency: true,
    reconnectCount: true,
    errorRate: true
  },
  
  // 报告间隔（毫秒）
  reportInterval: 60000
}

export default {
  defaultWebSocketConfig,
  getWebSocketConfig,
  WebSocketMessageType,
  WebSocketStatus,
  WebSocketEventType,
  validateWebSocketMessage,
  createWebSocketMessage,
  errorHandlingConfig,
  performanceConfig
}