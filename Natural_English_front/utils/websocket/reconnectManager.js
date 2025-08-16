/**
 * WebSocket重连管理模块
 * 负责自动重连策略和重连逻辑
 */

export class ReconnectManager {
    constructor(connectionManager) {
        this.connectionManager = connectionManager;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 8; // 最大重连次数
        this.reconnectInterval = 1000; // 初始重连间隔1秒
        this.maxReconnectInterval = 60000; // 最大重连间隔60秒
        this.reconnectTimer = null;
    }

    /**
     * 安排重连
     */
    scheduleReconnect() {
        // 检查网络状态
        if (!this.connectionManager.isOnline) {
            console.log('[WebSocket] 网络离线，暂停重连');
            return;
        }

        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[WebSocket] 已达到最大重连次数，停止重连');
            return;
        }

        // 计算重连延迟（指数退避 + 随机抖动）
        const baseDelay = Math.min(
            this.reconnectInterval * Math.pow(2, this.reconnectAttempts),
            this.maxReconnectInterval
        );
        
        // 添加随机抖动（±25%）
        const jitter = baseDelay * 0.25 * (Math.random() - 0.5);
        const delay = Math.max(1000, baseDelay + jitter);

        console.log(`[WebSocket] 将在 ${delay}ms 后进行第 ${this.reconnectAttempts + 1} 次重连`);

        this.reconnectTimer = setTimeout(() => {
            this.reconnectAttempts++;
            console.log(`[WebSocket] 开始第 ${this.reconnectAttempts} 次重连`);
            this.connectionManager.connect();
        }, delay);
    }

    /**
     * 重置重连状态
     */
    reset() {
        this.reconnectAttempts = 0;
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    /**
     * 停止重连
     */
    stop() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    /**
     * 获取重连状态
     */
    getReconnectStatus() {
        return {
            attempts: this.reconnectAttempts,
            maxAttempts: this.maxReconnectAttempts,
            isScheduled: !!this.reconnectTimer
        };
    }

    /**
     * 清理资源
     */
    destroy() {
        this.stop();
        this.reset();
    }
}