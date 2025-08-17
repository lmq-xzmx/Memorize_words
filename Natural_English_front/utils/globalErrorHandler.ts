/**
 * 全局错误处理器 - TypeScript版本
 * 统一处理API错误、WebSocket错误和应用程序错误
 */

// 环境变量类型声明
// 使用any类型处理import.meta以避免TypeScript声明问题
const importMeta: any = {
  env: {
    MODE: process.env.NODE_ENV || 'development'
  }
};

// 类型定义
interface ErrorInfo {
  type: string;
  error: any;
  context?: Record<string, any>;
  timestamp: string;
  userMessage?: string;
  severity?: 'critical' | 'error' | 'warning' | 'info';
}

interface APIError {
  response?: {
    status?: number;
    statusText?: string;
    data?: any;
  };
  config?: {
    url?: string;
    method?: string;
  };
  message: string;
}

interface WebSocketError {
  message?: string;
  code?: number;
  reason?: string;
}

interface ErrorStats {
  total: number;
  byType: Record<string, number>;
  bySeverity: Record<string, number>;
  recent: ErrorInfo[];
}

type ErrorListener = (errorInfo: ErrorInfo) => void;
type ErrorSeverity = 'critical' | 'error' | 'warning' | 'info';

class GlobalErrorHandler {
    private errorQueue: ErrorInfo[] = [];
    private maxQueueSize: number = 50;
    private errorListeners: ErrorListener[] = [];

    constructor() {
        this.setupGlobalHandlers();
    }

    /**
     * 设置全局错误处理器
     */
    private setupGlobalHandlers(): void {
        // 捕获未处理的Promise拒绝
        window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
            this.handleError({
                type: 'unhandled_promise_rejection',
                error: event.reason,
                timestamp: new Date().toISOString()
            });
        });

        // 捕获JavaScript运行时错误
        window.addEventListener('error', (event: ErrorEvent) => {
            this.handleError({
                type: 'javascript_error',
                error: {
                    message: event.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    stack: event.error?.stack
                },
                timestamp: new Date().toISOString()
            });
        });
    }

    /**
     * 处理错误
     */
    handleError(errorInfo: ErrorInfo): void {
        // 添加到错误队列
        this.addToQueue(errorInfo);
        
        // 分类处理错误
        const processedError = this.processError(errorInfo);
        
        // 通知错误监听器
        this.notifyListeners(processedError);
        
        // 显示用户友好的错误提示
        this.showUserFriendlyError(processedError);
        
        // 记录错误日志
        this.logError(processedError);
    }

    /**
     * 处理API错误
     */
    handleAPIError(error: APIError, context: Record<string, any> = {}): ErrorInfo {
        const errorInfo: ErrorInfo = {
            type: 'api_error',
            error: {
                status: error.response?.status,
                statusText: error.response?.statusText,
                message: error.message,
                url: error.config?.url,
                method: error.config?.method,
                data: error.response?.data
            },
            context,
            timestamp: new Date().toISOString()
        };
        
        this.handleError(errorInfo);
        return errorInfo;
    }

    /**
     * 处理WebSocket错误
     */
    handleWebSocketError(error: WebSocketError, context: Record<string, any> = {}): ErrorInfo {
        const errorInfo: ErrorInfo = {
            type: 'websocket_error',
            error: {
                message: error.message || 'WebSocket连接错误',
                code: error.code,
                reason: error.reason
            },
            context,
            timestamp: new Date().toISOString()
        };
        
        this.handleError(errorInfo);
        return errorInfo;
    }

    /**
     * 处理业务逻辑错误
     */
    handleBusinessError(message: string, code: string | number | null = null, context: Record<string, any> = {}): ErrorInfo {
        const errorInfo: ErrorInfo = {
            type: 'business_error',
            error: {
                message,
                code
            },
            context,
            timestamp: new Date().toISOString()
        };
        
        this.handleError(errorInfo);
        return errorInfo;
    }

    /**
     * 处理错误信息
     */
    private processError(errorInfo: ErrorInfo): ErrorInfo {
        const processed = { ...errorInfo };
        
        // 根据错误类型进行特殊处理
        switch (errorInfo.type) {
            case 'api_error':
                processed.userMessage = this.getAPIErrorMessage(errorInfo.error);
                processed.severity = this.getAPIErrorSeverity(errorInfo.error);
                break;
                
            case 'websocket_error':
                processed.userMessage = this.getWebSocketErrorMessage(errorInfo.error);
                processed.severity = 'warning';
                break;
                
            case 'business_error':
                processed.userMessage = errorInfo.error.message;
                processed.severity = 'info';
                break;
                
            default:
                processed.userMessage = '系统发生未知错误，请稍后重试';
                processed.severity = 'error';
        }
        
        return processed;
    }

    /**
     * 获取API错误消息
     */
    private getAPIErrorMessage(error: any): string {
        const status = error.status;
        
        switch (status) {
            case 400:
                return '请求参数错误，请检查输入信息';
            case 401:
                return '登录已过期，请重新登录';
            case 403:
                return '没有权限执行此操作';
            case 404:
                return '请求的资源不存在';
            case 429:
                return '请求过于频繁，请稍后重试';
            case 500:
                return '服务器内部错误，请稍后重试';
            case 502:
            case 503:
            case 504:
                return '服务暂时不可用，请稍后重试';
            default:
                if (status >= 500) {
                    return '服务器错误，请稍后重试';
                } else if (status >= 400) {
                    return '请求错误，请检查输入信息';
                } else {
                    return '网络连接异常，请检查网络设置';
                }
        }
    }

    /**
     * 获取WebSocket错误消息
     */
    private getWebSocketErrorMessage(error: any): string {
        if (error.code === 1006) {
            return '连接异常断开，正在尝试重新连接...';
        } else if (error.code === 1000) {
            return '连接正常关闭';
        } else {
            return '实时连接出现问题，部分功能可能受影响';
        }
    }

    /**
     * 获取API错误严重程度
     */
    private getAPIErrorSeverity(error: any): ErrorSeverity {
        const status = error.status;
        
        if (status === 401) {
            return 'critical'; // 需要重新登录
        } else if (status >= 500) {
            return 'error'; // 服务器错误
        } else if (status >= 400) {
            return 'warning'; // 客户端错误
        } else {
            return 'info';
        }
    }

    /**
     * 显示用户友好的错误提示
     */
    private showUserFriendlyError(errorInfo: ErrorInfo): void {
        // 避免重复显示相同错误
        if (this.isDuplicateError(errorInfo)) {
            return;
        }
        
        // 根据严重程度选择显示方式
        switch (errorInfo.severity) {
            case 'critical':
                this.showCriticalError(errorInfo.userMessage!);
                break;
            case 'error':
                this.showError(errorInfo.userMessage!);
                break;
            case 'warning':
                this.showWarning(errorInfo.userMessage!);
                break;
            case 'info':
                this.showInfo(errorInfo.userMessage!);
                break;
        }
    }

    /**
     * 显示关键错误（如需要重新登录）
     */
    private showCriticalError(message: string): void {
        // 可以集成到现有的通知系统
        console.error('[关键错误]', message);
        
        // 如果是认证错误，可以触发重新登录
        if (message.includes('登录')) {
            this.triggerReauth();
        }
    }

    /**
     * 显示普通错误
     */
    private showError(message: string): void {
        console.error('[错误]', message);
        // 可以显示toast通知
    }

    /**
     * 显示警告
     */
    private showWarning(message: string): void {
        console.warn('[警告]', message);
        // 可以显示toast通知
    }

    /**
     * 显示信息
     */
    private showInfo(message: string): void {
        console.info('[信息]', message);
        // 可以显示toast通知
    }

    /**
     * 触发重新认证
     */
    private triggerReauth(): void {
        // 清除本地存储的认证信息
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // 重定向到登录页面
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }

    /**
     * 检查是否为重复错误
     */
    private isDuplicateError(errorInfo: ErrorInfo): boolean {
        const recent = this.errorQueue.slice(-5); // 检查最近5个错误
        return recent.some(error => 
            error.type === errorInfo.type &&
            error.userMessage === errorInfo.userMessage &&
            (Date.now() - new Date(error.timestamp).getTime()) < 5000 // 5秒内
        );
    }

    /**
     * 添加到错误队列
     */
    private addToQueue(errorInfo: ErrorInfo): void {
        this.errorQueue.push(errorInfo);
        
        // 保持队列大小
        if (this.errorQueue.length > this.maxQueueSize) {
            this.errorQueue.shift();
        }
    }

    /**
     * 通知错误监听器
     */
    private notifyListeners(errorInfo: ErrorInfo): void {
        this.errorListeners.forEach(listener => {
            try {
                listener(errorInfo);
            } catch (e) {
                console.error('错误监听器执行失败:', e);
            }
        });
    }

    /**
     * 记录错误日志
     */
    private logError(errorInfo: ErrorInfo): void {
        // 开发环境下详细记录
        if (importMeta?.env?.MODE === 'development') {
            console.group(`[${errorInfo.type}] ${errorInfo.timestamp}`);
            console.error('错误信息:', errorInfo.error);
            console.log('上下文:', errorInfo.context);
            console.log('用户消息:', errorInfo.userMessage);
            console.groupEnd();
        }
        
        // 生产环境下可以发送到错误监控服务
        // this.sendToErrorService(errorInfo);
    }

    /**
     * 添加错误监听器
     */
    addErrorListener(listener: ErrorListener): void {
        this.errorListeners.push(listener);
    }

    /**
     * 移除错误监听器
     */
    removeErrorListener(listener: ErrorListener): void {
        const index = this.errorListeners.indexOf(listener);
        if (index > -1) {
            this.errorListeners.splice(index, 1);
        }
    }

    /**
     * 获取错误统计
     */
    getErrorStats(): ErrorStats {
        const stats: ErrorStats = {
            total: this.errorQueue.length,
            byType: {},
            bySeverity: {},
            recent: this.errorQueue.slice(-10)
        };
        
        this.errorQueue.forEach(error => {
            stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;
            if (error.severity) {
                stats.bySeverity[error.severity] = (stats.bySeverity[error.severity] || 0) + 1;
            }
        });
        
        return stats;
    }

    /**
     * 清除错误队列
     */
    clearErrors(): void {
        this.errorQueue = [];
    }
}

// 创建全局实例
const globalErrorHandler = new GlobalErrorHandler();

export { GlobalErrorHandler, globalErrorHandler };
export type { ErrorInfo, APIError, WebSocketError, ErrorStats, ErrorListener, ErrorSeverity };
export default globalErrorHandler;