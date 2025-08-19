/**
 * WebSocket管理器 - 统一的WebSocket连接管理
 * 提供连接管理、消息路由、监听器管理和错误处理
 */

import { getWebSocketUrl } from '../config/apiconfig';
import { globalErrorHandler } from './globalerrorhandler';

// 类型定义
interface WebSocketMessage {
  type: string;
  data?: any;
  payload?: any;
  timestamp?: number;
  userId?: string;
}

interface ConnectionConfig {
  url: string;
  protocols?: string[];
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
  connectionTimeout: number;
}

interface ConnectionStatus {
  isConnected: boolean;
  isConnecting: boolean;
  reconnectCount: number;
  lastConnectTime: number;
  lastDisconnectTime: number;
  readyState: number;
}

type MessageListener = (data: any) => void;
type ConnectionListener = (status: ConnectionStatus) => void;

/**
 * WebSocket管理器类
 */
class WebSocketManager {
  private websocket: WebSocket | null = null;
  private config: ConnectionConfig;
  private status: ConnectionStatus;
  private messageListeners: Map<string, Set<MessageListener>>;
  private connectionListeners: Set<ConnectionListener>;
  private heartbeatTimer: any = null;
  private reconnectTimer: any = null;
  private connectionTimer: any = null;
  private isDestroyed: boolean = false;

  constructor(config?: Partial<ConnectionConfig>) {
    this.config = {
      url: getWebSocketUrl(),
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      connectionTimeout: 10000,
      ...config
    };

    this.status = {
      isConnected: false,
      isConnecting: false,
      reconnectCount: 0,
      lastConnectTime: 0,
      lastDisconnectTime: 0,
      readyState: WebSocket.CLOSED
    };

    this.messageListeners = new Map();
    this.connectionListeners = new Set();

    // 监听网络状态变化
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => {
        console.log('[WebSocketManager] 网络已恢复，尝试重连');
        this.connect();
      });

      window.addEventListener('offline', () => {
        console.log('[WebSocketManager] 网络断开');
        this.disconnect();
      });
    }
  }

  /**
   * 建立WebSocket连接
   */
  async connect(): Promise<boolean> {
    if (this.isDestroyed) {
      console.warn('[WebSocketManager] 管理器已销毁，无法连接');
      return false;
    }

    if (this.status.isConnecting || this.status.isConnected) {
      console.log('[WebSocketManager] 连接已存在或正在连接中');
      return this.status.isConnected;
    }

    // 检查网络状态
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      console.warn('[WebSocketManager] 网络不可用，跳过连接');
      return false;
    }

    this.status.isConnecting = true;
    this.notifyConnectionListeners();

    try {
      // 构建WebSocket URL
      const token = localStorage.getItem('token');
      const user = this.getCurrentUser();
      
      if (!token || !user) {
        console.warn('[WebSocketManager] 缺少认证信息，无法建立连接');
        this.status.isConnecting = false;
        return false;
      }

      const wsUrl = `${this.config.url}permissions/?token=${encodeURIComponent(token)}&userId=${user.id || user.user_id}`;
      console.log('[WebSocketManager] 正在连接:', wsUrl.replace(/token=[^&]+/, 'token=***'));

      // 创建WebSocket连接
      this.websocket = new WebSocket(wsUrl, this.config.protocols);

      // 设置连接超时
      this.connectionTimer = setTimeout(() => {
        if (this.websocket && this.websocket.readyState === WebSocket.CONNECTING) {
          console.error('[WebSocketManager] 连接超时');
          this.websocket.close();
        }
      }, this.config.connectionTimeout);

      // 设置事件处理器
      this.setupEventHandlers();

      return new Promise((resolve) => {
        const checkConnection = () => {
          if (this.status.isConnected) {
            resolve(true);
          } else if (!this.status.isConnecting) {
            resolve(false);
          } else {
            setTimeout(checkConnection, 100);
          }
        };
        checkConnection();
      });

    } catch (error) {
      console.error('[WebSocketManager] 连接失败:', error);
      this.status.isConnecting = false;
      this.handleConnectionError(error);
      return false;
    }
  }

  /**
   * 设置WebSocket事件处理器
   */
  private setupEventHandlers(): void {
    if (!this.websocket) return;

    this.websocket.onopen = () => {
      if (this.connectionTimer) {
        clearTimeout(this.connectionTimer);
        this.connectionTimer = null;
      }

      console.log('[WebSocketManager] 连接已建立');
      this.status.isConnected = true;
      this.status.isConnecting = false;
      this.status.reconnectCount = 0;
      this.status.lastConnectTime = Date.now();
      this.status.readyState = WebSocket.OPEN;

      // 发送认证信息
      this.sendAuthMessage();

      // 启动心跳
      this.startHeartbeat();

      // 通知连接状态变化
      this.notifyConnectionListeners();
    };

    this.websocket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('[WebSocketManager] 收到消息:', message);
        this.handleMessage(message);
      } catch (error) {
        console.error('[WebSocketManager] 消息解析失败:', error);
      }
    };

    this.websocket.onclose = (event) => {
      if (this.connectionTimer) {
        clearTimeout(this.connectionTimer);
        this.connectionTimer = null;
      }

      console.log(`[WebSocketManager] 连接已关闭，代码: ${event.code}, 原因: ${event.reason || '未知'}`);
      
      this.status.isConnected = false;
      this.status.isConnecting = false;
      this.status.lastDisconnectTime = Date.now();
      this.status.readyState = WebSocket.CLOSED;

      // 停止心跳
      this.stopHeartbeat();

      // 通知连接状态变化
      this.notifyConnectionListeners();

      // 根据关闭代码决定是否重连
      if (event.code !== 1000 && event.code !== 1001 && !this.isDestroyed) {
        this.scheduleReconnect();
      }
    };

    this.websocket.onerror = (error) => {
      console.error('[WebSocketManager] WebSocket错误:', error);
      this.handleConnectionError(error);
    };
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage): void {
    const { type, data, payload } = message;
    const messageData = data || payload;

    // 处理特殊消息类型
    switch (type) {
      case 'auth_success':
        console.log('[WebSocketManager] 认证成功');
        break;
      case 'heartbeat':
        this.handleHeartbeat();
        break;
      case 'permission_update':
      case 'permission_changed':
        this.notifyListeners('permissionChanged', messageData);
        break;
      case 'role_updated':
        this.notifyListeners('roleUpdated', messageData);
        break;
      case 'menu_access_changed':
        this.notifyListeners('menuAccessChanged', messageData);
        break;
      case 'system_notification':
        this.notifyListeners('systemNotification', messageData);
        break;
      default:
        // 通知对应类型的监听器
        this.notifyListeners(type, messageData);
        break;
    }
  }

  /**
   * 发送认证消息
   */
  private sendAuthMessage(): void {
    const token = localStorage.getItem('token');
    const user = this.getCurrentUser();
    
    if (token && user) {
      this.send({
        type: 'auth_confirm',
        userId: user.id || user.user_id,
        timestamp: Date.now()
      });
    }
  }

  /**
   * 处理心跳消息
   */
  private handleHeartbeat(): void {
    this.send({ type: 'heartbeat_response', timestamp: Date.now() });
  }

  /**
   * 启动心跳机制
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.status.isConnected) {
        this.send({ type: 'ping', timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * 停止心跳机制
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * 安排重连
   */
  private scheduleReconnect(): void {
    if (this.status.reconnectCount >= this.config.maxReconnectAttempts) {
      console.error(`[WebSocketManager] 已达到最大重连次数 ${this.config.maxReconnectAttempts}`);
      return;
    }

    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(2, this.status.reconnectCount),
      30000
    );

    console.log(`[WebSocketManager] ${delay / 1000}秒后尝试重连 (第${this.status.reconnectCount + 1}次)`);

    this.reconnectTimer = setTimeout(() => {
      this.status.reconnectCount++;
      this.connect();
    }, delay);
  }

  /**
   * 处理连接错误
   */
  private handleConnectionError(error: any): void {
    globalErrorHandler.handleWebSocketError({
      message: error.message || 'WebSocket连接错误',
      code: error.code
    }, {
      url: this.config.url,
      reconnectCount: this.status.reconnectCount
    });
  }

  /**
   * 发送消息
   */
  send(message: any): boolean {
    if (!this.status.isConnected || !this.websocket) {
      console.warn('[WebSocketManager] 连接未建立，无法发送消息');
      return false;
    }

    try {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
      this.websocket.send(messageStr);
      return true;
    } catch (error) {
      console.error('[WebSocketManager] 发送消息失败:', error);
      return false;
    }
  }

  /**
   * 添加消息监听器
   */
  addListener(type: string, listener: MessageListener): void {
    if (!this.messageListeners.has(type)) {
      this.messageListeners.set(type, new Set());
    }
    this.messageListeners.get(type)!.add(listener);
  }

  /**
   * 移除消息监听器
   */
  removeListener(type: string, listener: MessageListener): void {
    const listeners = this.messageListeners.get(type);
    if (listeners) {
      listeners.delete(listener);
      if (listeners.size === 0) {
        this.messageListeners.delete(type);
      }
    }
  }

  /**
   * 添加连接状态监听器
   */
  addConnectionListener(listener: ConnectionListener): void {
    this.connectionListeners.add(listener);
  }

  /**
   * 移除连接状态监听器
   */
  removeConnectionListener(listener: ConnectionListener): void {
    this.connectionListeners.delete(listener);
  }

  /**
   * 通知消息监听器
   */
  private notifyListeners(type: string, data: any): void {
    const listeners = this.messageListeners.get(type);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error(`[WebSocketManager] 监听器执行失败 (${type}):`, error);
        }
      });
    }
  }

  /**
   * 通知连接状态监听器
   */
  private notifyConnectionListeners(): void {
    this.connectionListeners.forEach(listener => {
      try {
        listener({ ...this.status });
      } catch (error) {
        console.error('[WebSocketManager] 连接状态监听器执行失败:', error);
      }
    });
  }

  /**
   * 获取当前用户信息
   */
  private getCurrentUser(): any {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('[WebSocketManager] 获取用户信息失败:', error);
      return null;
    }
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.websocket) {
      console.log('[WebSocketManager] 主动断开连接');
      this.websocket.close(1000, '主动断开');
      this.websocket = null;
    }

    this.stopHeartbeat();
    this.status.isConnected = false;
    this.status.isConnecting = false;
  }

  /**
   * 销毁管理器
   */
  destroy(): void {
    this.isDestroyed = true;
    this.disconnect();
    this.messageListeners.clear();
    this.connectionListeners.clear();
    
    if (this.connectionTimer) {
      clearTimeout(this.connectionTimer);
      this.connectionTimer = null;
    }
  }

  /**
   * 获取连接状态
   */
  getStatus(): ConnectionStatus {
    return { ...this.status };
  }

  /**
   * 检查是否已连接
   */
  get isConnected(): boolean {
    return this.status.isConnected;
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<ConnectionConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// 创建全局WebSocket管理器实例
export const webSocketManager = new WebSocketManager();

// 默认导出
export default webSocketManager;

// 兼容性导出
export { WebSocketManager };