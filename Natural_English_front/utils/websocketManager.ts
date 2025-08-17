/**
 * WebSocket连接管理器 - 简化版本
 * 提供基本的WebSocket连接和消息处理功能
 */

// 类型定义
type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'
type ConnectionListener = (status: ConnectionStatus) => void

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
    private ws: WebSocket | null = null;
    private messageHandlers: Map<string, MessageHandler>;
    private connectionListeners: Set<ConnectionListener> = new Set();
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 1000;
    private isReconnecting = false;
    private url = '';

    constructor() {
        this.messageHandlers = new Map();
    }

    // 连接WebSocket
    connect(url?: string): void {
        if (url) this.url = url;
        if (!this.url) return;

        try {
            this.ws = new WebSocket(this.url);
            this.setupEventListeners();
            this.notifyConnectionListeners('connecting');
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.notifyConnectionListeners('error');
        }
    }

    // 设置事件监听器
    private setupEventListeners(): void {
        if (!this.ws) return;

        this.ws.onopen = () => {
            this.reconnectAttempts = 0;
            this.isReconnecting = false;
            this.notifyConnectionListeners('connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const message: WebSocketMessage = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('消息解析失败:', error);
            }
        };

        this.ws.onclose = () => {
            this.notifyConnectionListeners('disconnected');
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket错误:', error);
            this.notifyConnectionListeners('error');
        };
    }

    // 处理消息
    private handleMessage(message: WebSocketMessage): void {
        const handler = this.messageHandlers.get(message.type);
        if (handler) {
            handler(message);
        }
    }

    // 发送消息
    send(data: WebSocketMessage): boolean {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
            return true;
        }
        return false;
    }

    // 注册消息处理器
    onMessage(type: string, handler: MessageHandler): void {
        this.messageHandlers.set(type, handler);
    }

    // 移除消息处理器
    offMessage(type: string): void {
        this.messageHandlers.delete(type);
    }

    // 注册连接状态监听器
    onConnection(listener: ConnectionListener): void {
        this.connectionListeners.add(listener);
    }

    // 移除连接状态监听器
    offConnection(listener: ConnectionListener): void {
        this.connectionListeners.delete(listener);
    }

    // 通知连接状态变化
    private notifyConnectionListeners(status: ConnectionStatus): void {
        this.connectionListeners.forEach(listener => listener(status));
    }

    // 尝试重连
    private attemptReconnect(): void {
        if (this.isReconnecting || this.reconnectAttempts >= this.maxReconnectAttempts) {
            return;
        }

        this.isReconnecting = true;
        this.reconnectAttempts++;

        setTimeout(() => {
            this.connect();
        }, this.reconnectDelay * this.reconnectAttempts);
    }

    // 断开连接
    disconnect(): void {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isReconnecting = false;
        this.reconnectAttempts = 0;
    }

    // 获取连接状态
    getConnectionStatus(): WebSocketStatus {
        return {
            isConnected: this.ws?.readyState === WebSocket.OPEN,
            url: this.url,
            readyState: this.ws?.readyState,
            reconnect: {
                isReconnecting: this.isReconnecting,
                attempts: this.reconnectAttempts,
                maxAttempts: this.maxReconnectAttempts
            },
            connectionQuality: {
                latency: 0,
                isStable: this.ws?.readyState === WebSocket.OPEN
            }
        };
    }

    // 销毁实例
    destroy(): void {
        this.disconnect();
        this.messageHandlers.clear();
        this.connectionListeners.clear();
    }
}

// 创建单例实例
const webSocketManager = new WebSocketManager();
const websocketManager = webSocketManager;

export { webSocketManager, websocketManager, WebSocketManager };
export default webSocketManager;

// 导出类型
export type {
    WebSocketMessage,
    ReconnectStatus,
    ConnectionQuality,
    WebSocketStatus,
    MessageHandler,
    ConnectionStatus,
    ConnectionListener
};