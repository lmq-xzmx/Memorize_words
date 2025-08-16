/**
 * WebSocket连接管理器 - 重构版本
 * 提供稳定的WebSocket连接、自动重连机制和权限变更通知
 */

import { ConnectionManager } from './websocket/connectionManager.js';
import { HeartbeatManager } from './websocket/heartbeatManager.js';
import { ReconnectManager } from './websocket/reconnectManager.js';
import { PermissionHandler } from './websocket/permissionHandler.js';

class WebSocketManager {
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
    setupModuleCallbacks() {
        // 连接管理器回调
        this.connectionManager.onMessageReceived = (data) => {
            this.handleMessage(data);
        };
        
        this.connectionManager.onReconnectNeeded = () => {
            this.reconnectManager.scheduleReconnect();
        };
        
        // 连接状态监听
        this.connectionManager.onConnection((status, data) => {
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
    connect() {
        this.connectionManager.connect();
    }

    /**
     * 处理接收到的消息
     */
    handleMessage(data) {
        const { type } = data;
        
        // 处理特殊消息类型
        switch (type) {
            case 'pong':
                this.heartbeatManager.handlePong(data);
                break;
            case 'permission_change':
                this.permissionHandler.handlePermissionChange(data);
                break;
            default:
                // 调用注册的消息处理器
                if (this.messageHandlers.has(type)) {
                    const handler = this.messageHandlers.get(type);
                    try {
                        handler(data);
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
    send(data) {
        return this.connectionManager.send(data);
    }

    /**
     * 注册消息处理器
     */
    onMessage(type, handler) {
        if (typeof handler === 'function') {
            this.messageHandlers.set(type, handler);
        }
    }

    /**
     * 移除消息处理器
     */
    offMessage(type) {
        this.messageHandlers.delete(type);
    }

    /**
     * 添加连接状态监听器
     */
    onConnection(listener) {
        this.connectionManager.onConnection(listener);
    }

    /**
     * 移除连接状态监听器
     */
    offConnection(listener) {
        this.connectionManager.offConnection(listener);
    }

    /**
     * 断开连接
     */
    disconnect() {
        this.heartbeatManager.stop();
        this.reconnectManager.stop();
        this.connectionManager.disconnect();
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
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
     * 清理资源
     */
    destroy() {
        this.heartbeatManager.destroy();
        this.reconnectManager.destroy();
        this.permissionHandler.destroy();
        this.connectionManager.destroy();
        
        // 清理消息处理器
        this.messageHandlers.clear();
    }
}

// 创建单例实例
const websocketManager = new WebSocketManager();

export { websocketManager, WebSocketManager };
export default websocketManager;