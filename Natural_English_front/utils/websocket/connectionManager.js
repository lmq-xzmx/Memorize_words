/**
 * WebSocket连接管理模块
 * 负责WebSocket连接的建立、断开和状态管理
 */

import { getWebSocketUrl } from '../../config/apiConfig.js';
import globalErrorHandler from '../globalErrorHandler.js';
import performanceMonitor from '../performanceMonitor.js';

export class ConnectionManager {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.connectionListeners = [];
        
        // 网络状态监听
        this.isOnline = navigator.onLine;
        this.setupNetworkListeners();
        
        // 绑定方法上下文
        this.handleOpen = this.handleOpen.bind(this);
        this.handleMessage = this.handleMessage.bind(this);
        this.handleError = this.handleError.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.handleOnline = this.handleOnline.bind(this);
        this.handleOffline = this.handleOffline.bind(this);
    }

    /**
     * 设置网络状态监听器
     */
    setupNetworkListeners() {
        window.addEventListener('online', this.handleOnline);
        window.addEventListener('offline', this.handleOffline);
    }

    /**
     * 处理网络恢复
     */
    handleOnline() {
        this.isOnline = true;
        if (!this.isConnected) {
            this.connect();
        }
    }

    /**
     * 处理网络断开
     */
    handleOffline() {
        this.isOnline = false;
    }

    /**
     * 建立WebSocket连接
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            return;
        }

        try {
            const wsUrl = this.getWebSocketUrl();
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = this.handleOpen;
            this.ws.onmessage = this.handleMessage;
            this.ws.onerror = this.handleError;
            this.ws.onclose = this.handleClose;
        } catch (error) {
            console.error('[WebSocket] 连接创建失败:', error);
            globalErrorHandler.handleWebSocketError(error);
        }
    }

    /**
     * 获取WebSocket URL
     */
    getWebSocketUrl() {
        try {
            return getWebSocketUrl();
        } catch (error) {
            console.error('[WebSocket] 获取WebSocket URL失败:', error);
            throw error;
        }
    }

    /**
     * 处理连接打开事件
     */
    handleOpen(event) {
        console.log('[WebSocket] 连接已建立');
        this.isConnected = true;
        
        // 记录连接事件
        performanceMonitor.recordWebSocketEvent('connect');
        
        // 通知连接监听器
        this.notifyConnectionListeners('connected');
    }

    /**
     * 处理消息接收事件
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            // 记录消息接收事件
            performanceMonitor.recordWebSocketEvent('message_received');
            
            console.log('[WebSocket] 收到消息:', data);
            
            // 触发消息处理事件
            this.onMessageReceived?.(data);
        } catch (error) {
            console.error('[WebSocket] 消息解析失败:', error);
            globalErrorHandler.handleWebSocketError(error);
        }
    }

    /**
     * 处理连接错误事件
     */
    handleError(event) {
        console.error('[WebSocket] 连接错误:', event);
        
        const error = new Error(`WebSocket连接错误: ${event.type}`);
        error.originalEvent = event;
        
        globalErrorHandler.handleWebSocketError(error);
        
        // 通知连接监听器
        this.notifyConnectionListeners('error', error);
    }

    /**
     * 处理连接关闭事件
     */
    handleClose(event) {
        console.log('[WebSocket] 连接已关闭:', event.code, event.reason);
        this.isConnected = false;
        
        // 通知连接监听器
        this.notifyConnectionListeners('disconnected', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
        });
        
        // 如果不是正常关闭，触发重连
        if (event.code !== 1000) {
            this.onReconnectNeeded?.();
            
            // 记录重连事件
            performanceMonitor.recordWebSocketEvent('reconnect');
        }
    }

    /**
     * 发送消息
     */
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(data));
                
                // 记录消息发送事件
                performanceMonitor.recordWebSocketEvent('message_sent');
                
                return true;
            } catch (error) {
                console.error('[WebSocket] 发送消息失败:', error);
                globalErrorHandler.handleWebSocketError(error);
                return false;
            }
        }
        return false;
    }

    /**
     * 断开连接
     */
    disconnect() {
        if (this.ws) {
            this.ws.close(1000, '正常关闭');
            this.ws = null;
        }
        this.isConnected = false;
    }

    /**
     * 添加连接状态监听器
     */
    onConnection(listener) {
        if (typeof listener === 'function') {
            this.connectionListeners.push(listener);
        }
    }

    /**
     * 移除连接状态监听器
     */
    offConnection(listener) {
        const index = this.connectionListeners.indexOf(listener);
        if (index > -1) {
            this.connectionListeners.splice(index, 1);
        }
    }

    /**
     * 通知连接状态监听器
     */
    notifyConnectionListeners(status, data = null) {
        this.connectionListeners.forEach(listener => {
            try {
                listener(status, data);
            } catch (error) {
                console.error('[WebSocket] 连接监听器执行失败:', error);
            }
        });
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            readyState: this.ws?.readyState,
            isOnline: this.isOnline
        };
    }

    /**
     * 清理资源
     */
    destroy() {
        this.disconnect();
        
        // 移除网络状态监听器
        window.removeEventListener('online', this.handleOnline);
        window.removeEventListener('offline', this.handleOffline);
        
        // 清理连接监听器
        this.connectionListeners = [];
    }
}