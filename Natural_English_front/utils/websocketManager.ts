/**
 * WebSocket连接管理器 - 重构版本
 * 提供稳定的WebSocket连接、自动重连机制和权限变更通知
 */

import { ConnectionManager, ConnectionStatus, ConnectionListener, MessageHandler as CMMessageHandler } from './websocket/connectionManager.ts'
import { HeartbeatManager } from './websocket/heartbeatManager.ts'
import { ReconnectManager } from './websocket/reconnectManager.ts'
import { PermissionHandler } from './websocket/permissionHandler.ts';

// 类型定义
interface WebSocketMessage {
    type: string;
    data?: any;
    timestamp?: number;
}

interface ReconnectStatus {
    isReconnecting: boolean;
    attempts: number;
    nextAttemptAt?: number;
    maxAttempts: number;
}

interface ConnectionQuality {
    latency: number;
    isStable: boolean;
    lastPingAt?: number;
    lastPongAt?: number;
}

interface WebSocketStatus {
    isConnected: boolean;
    url?: string;
    readyState?: number;
    lastConnectedAt?: number;
    lastDisconnectedAt?: number;
    reconnect: ReconnectStatus;
    connectionQuality: ConnectionQuality;
}

type MessageHandler = (data: WebSocketMessage) => void;

class WebSocketManager {
    private connectionManager: ConnectionManager;
    private heartbeatManager: HeartbeatManager;
    private reconnectManager: ReconnectManager;
    private permissionHandler: PermissionHandler;
    private messageHandlers: Map<string, MessageHandler>;

    constructor() {
        // 初始化各个管理模块
        this.connectionManager = new ConnectionManager();
        this.heartbeatManager = new HeartbeatManager(this.connectionManager);
        this.reconnectManager = new ReconnectManager(this.connectionManager);
        this.permissionHandler = new PermissionHandler(this.connectionManager);
        
        // 消息处理器
        this.messageHandlers = new Map();
        
        // 设置模块间的回调
        this.setupModuleCallbacks();
    }

    /**
     * 设置模块间的回调关系
     */
    private setupModuleCallbacks(): void {
        // 连接管理器回调
        this.connectionManager.onMessageReceived = (data: WebSocketMessage) => {
            this.handleMessage(data);
        };
        
        this.connectionManager.onReconnectNeeded = () => {
            this.reconnectManager.scheduleReconnect();
        };
        
        // 连接状态监听
        this.connectionManager.onConnection((status: string, data?: any) => {
            if (status === 'connected') {
                this.reconnectManager.reset();
                this.heartbeatManager.start();
                this.permissionHandler.authenticate();
            } else if (status === 'disconnected') {
                this.heartbeatManager.stop();
            }
        });
    }

    /**
     * 建立WebSocket连接
     */
    connect(): void {
        this.connectionManager.connect();
    }

    /**
     * 处理接收到的消息
     */
    private handleMessage(data: WebSocketMessage): void {
        const { type } = data;
        
        // 处理特殊消息类型
        switch (type) {
            case 'pong':
                this.heartbeatManager.handlePong(data);
                break;
            case 'permission_change':
                this.permissionHandler.handlePermissionChange(data.data || data);
                break;
            default:
                // 调用注册的消息处理器
                if (this.messageHandlers.has(type)) {
                    const handler = this.messageHandlers.get(type);
                    try {
                        if (handler) {
                            handler(data);
                        }
                    } catch (error) {
                        console.error(`[WebSocket] 消息处理器执行失败 (${type}):`, error);
                    }
                }
                break;
        }
    }

    /**
     * 发送消息
     */
    send(data: WebSocketMessage): boolean {
        return this.connectionManager.send(data);
    }

    /**
     * 注册消息处理器
     */
    onMessage(type: string, handler: MessageHandler): void {
        if (typeof handler === 'function') {
            this.messageHandlers.set(type, handler);
        }
    }

    /**
     * 移除消息处理器
     */
    offMessage(type: string): void {
        this.messageHandlers.delete(type);
    }

    /**
     * 添加连接状态监听器
     */
    onConnection(listener: ConnectionListener): void {
        this.connectionManager.onConnection(listener);
    }

    /**
     * 移除连接状态监听器
     */
    offConnection(listener: ConnectionListener): void {
        this.connectionManager.offConnection(listener);
    }

    /**
     * 断开连接
     */
    disconnect(): void {
        this.heartbeatManager.stop();
        this.reconnectManager.stop();
        this.connectionManager.disconnect();
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus(): WebSocketStatus {
        const connectionStatus = this.connectionManager.getConnectionStatus();
        const reconnectStatus = this.reconnectManager.getReconnectStatus();
        const connectionQuality = this.heartbeatManager.getConnectionQuality();
        
        return {
            ...connectionStatus,
            reconnect: reconnectStatus,
            connectionQuality
        };
    }

    /**
     * 添加监听器（兼容旧API）
     */
    addListener(type: string, handler: MessageHandler): void {
        this.onMessage(type, handler);
    }

    /**
     * 移除监听器（兼容旧API）
     */
    removeListener(type: string): void {
        this.offMessage(type);
    }

    /**
     * 清理资源
     */
    destroy(): void {
        this.heartbeatManager.destroy();
        this.reconnectManager.destroy();
        this.permissionHandler.destroy();
        this.connectionManager.destroy();
        
        // 清理消息处理器
        this.messageHandlers.clear();
    }
}

// 创建单例实例
const webSocketManager = new WebSocketManager();

// 兼容旧的导出名称
const websocketManager = webSocketManager;

export { webSocketManager, websocketManager, WebSocketManager };
export default webSocketManager;

// 导出类型
export type {
    WebSocketMessage,
    ReconnectStatus,
    ConnectionQuality,
    WebSocketStatus,
    MessageHandler
};

// 重新导出从connectionManager导入的类型
export type { ConnectionStatus, ConnectionListener } from './websocket/connectionManager.ts';