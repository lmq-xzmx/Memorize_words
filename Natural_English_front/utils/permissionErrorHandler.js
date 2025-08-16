/**
 * 权限错误处理器
 * 提供API调用失败时的降级策略、离线权限支持和错误恢复机制
 */

import { PermissionCache } from './permissionCache.js';
import { performanceMonitor } from './permissionPerformanceMonitor.js';

class PermissionErrorHandler {
    constructor() {
        this.cache = new PermissionCache();
        this.fallbackStrategies = {
            CACHE_FALLBACK: 'cache_fallback',
            DEFAULT_PERMISSIONS: 'default_permissions',
            OFFLINE_MODE: 'offline_mode',
            RETRY_WITH_BACKOFF: 'retry_with_backoff',
            GRACEFUL_DEGRADATION: 'graceful_degradation'
        };
        
        this.errorTypes = {
            NETWORK_ERROR: 'network_error',
            TIMEOUT_ERROR: 'timeout_error',
            AUTH_ERROR: 'auth_error',
            SERVER_ERROR: 'server_error',
            PERMISSION_DENIED: 'permission_denied',
            RATE_LIMIT: 'rate_limit',
            UNKNOWN_ERROR: 'unknown_error'
        };
        
        this.retryConfig = {
            maxRetries: 3,
            baseDelay: 1000, // 1秒
            maxDelay: 10000, // 10秒
            backoffMultiplier: 2,
            jitterRange: 0.1 // 10%的随机抖动
        };
        
        this.circuitBreaker = {
            failureThreshold: 5,
            resetTimeout: 30000, // 30秒
            state: 'CLOSED', // CLOSED, OPEN, HALF_OPEN
            failureCount: 0,
            lastFailureTime: null,
            successCount: 0
        };
        
        this.offlineMode = {
            enabled: false,
            detectedAt: null,
            fallbackPermissions: new Map(),
            gracePeriod: 5 * 60 * 1000 // 5分钟宽限期
        };
        
        this.errorHistory = [];
        this.maxErrorHistory = 100;
        this.listeners = new Set();
        
        this.init();
    }

    /**
     * 初始化错误处理器
     */
    init() {
        this.setupNetworkListeners();
        this.loadOfflinePermissions();
        this.startHealthCheck();
    }

    /**
     * 处理权限检查错误
     */
    async handlePermissionError(error, context = {}) {
        const errorType = this.classifyError(error);
        const errorRecord = {
            type: errorType,
            error,
            context,
            timestamp: Date.now(),
            handled: false
        };
        
        this.recordError(errorRecord);
        
        // 更新熔断器状态
        this.updateCircuitBreaker(false);
        
        // 记录性能监控
        performanceMonitor.recordApiResponse(context.requestData, { error: true });
        
        console.warn('[PermissionErrorHandler] 处理权限错误:', errorRecord);
        
        // 根据错误类型选择处理策略
        const strategy = this.selectFallbackStrategy(errorType, context);
        const result = await this.executeFallbackStrategy(strategy, errorRecord, context);
        
        errorRecord.handled = true;
        errorRecord.fallbackStrategy = strategy;
        errorRecord.result = result;
        
        // 通知监听器
        this.notifyListeners('errorHandled', errorRecord);
        
        return result;
    }

    /**
     * 分类错误类型
     */
    classifyError(error) {
        if (!error) return this.errorTypes.UNKNOWN_ERROR;
        
        // 网络错误
        if (error.name === 'NetworkError' || error.message?.includes('fetch')) {
            return this.errorTypes.NETWORK_ERROR;
        }
        
        // 超时错误
        if (error.name === 'TimeoutError' || error.code === 'TIMEOUT') {
            return this.errorTypes.TIMEOUT_ERROR;
        }
        
        // HTTP状态码错误
        if (error.status) {
            if (error.status === 401 || error.status === 403) {
                return this.errorTypes.AUTH_ERROR;
            }
            if (error.status === 429) {
                return this.errorTypes.RATE_LIMIT;
            }
            if (error.status >= 500) {
                return this.errorTypes.SERVER_ERROR;
            }
        }
        
        // 权限拒绝
        if (error.message?.includes('permission') || error.message?.includes('denied')) {
            return this.errorTypes.PERMISSION_DENIED;
        }
        
        return this.errorTypes.UNKNOWN_ERROR;
    }

    /**
     * 选择降级策略
     */
    selectFallbackStrategy(errorType, context) {
        // 检查熔断器状态
        if (this.circuitBreaker.state === 'OPEN') {
            return this.fallbackStrategies.OFFLINE_MODE;
        }
        
        // 根据错误类型选择策略
        switch (errorType) {
            case this.errorTypes.NETWORK_ERROR:
                return this.isOnline() 
                    ? this.fallbackStrategies.RETRY_WITH_BACKOFF 
                    : this.fallbackStrategies.OFFLINE_MODE;
            
            case this.errorTypes.TIMEOUT_ERROR:
                return this.fallbackStrategies.CACHE_FALLBACK;
            
            case this.errorTypes.AUTH_ERROR:
                return this.fallbackStrategies.DEFAULT_PERMISSIONS;
            
            case this.errorTypes.SERVER_ERROR:
                return this.fallbackStrategies.RETRY_WITH_BACKOFF;
            
            case this.errorTypes.RATE_LIMIT:
                return this.fallbackStrategies.CACHE_FALLBACK;
            
            case this.errorTypes.PERMISSION_DENIED:
                return this.fallbackStrategies.GRACEFUL_DEGRADATION;
            
            default:
                return this.fallbackStrategies.CACHE_FALLBACK;
        }
    }

    /**
     * 执行降级策略
     */
    async executeFallbackStrategy(strategy, errorRecord, context) {
        console.log(`[PermissionErrorHandler] 执行降级策略: ${strategy}`);
        
        switch (strategy) {
            case this.fallbackStrategies.CACHE_FALLBACK:
                return await this.executeCacheFallback(context);
            
            case this.fallbackStrategies.DEFAULT_PERMISSIONS:
                return await this.executeDefaultPermissions(context);
            
            case this.fallbackStrategies.OFFLINE_MODE:
                return await this.executeOfflineMode(context);
            
            case this.fallbackStrategies.RETRY_WITH_BACKOFF:
                return await this.executeRetryWithBackoff(context, errorRecord);
            
            case this.fallbackStrategies.GRACEFUL_DEGRADATION:
                return await this.executeGracefulDegradation(context);
            
            default:
                return this.getDefaultResult(context);
        }
    }

    /**
     * 缓存降级策略
     */
    async executeCacheFallback(context) {
        const { permissionKey, userId, resource } = context;
        
        // 尝试从缓存获取权限
        const cachedPermission = this.cache.get(permissionKey, { fallbackToOffline: true });
        
        if (cachedPermission) {
            console.log('[PermissionErrorHandler] 使用缓存权限:', permissionKey);
            return {
                success: true,
                permission: cachedPermission,
                source: 'cache',
                fallback: true,
                message: '使用缓存权限数据'
            };
        }
        
        // 缓存中没有，尝试其他策略
        return await this.executeDefaultPermissions(context);
    }

    /**
     * 默认权限策略
     */
    async executeDefaultPermissions(context) {
        const { userId, resource, action } = context;
        
        // 获取用户的默认权限
        const defaultPermissions = this.getDefaultPermissions(userId);
        
        const hasPermission = this.checkDefaultPermission(defaultPermissions, resource, action);
        
        console.log('[PermissionErrorHandler] 使用默认权限:', { resource, action, hasPermission });
        
        return {
            success: true,
            permission: hasPermission,
            source: 'default',
            fallback: true,
            message: '使用默认权限配置'
        };
    }

    /**
     * 离线模式策略
     */
    async executeOfflineMode(context) {
        if (!this.offlineMode.enabled) {
            this.enableOfflineMode();
        }
        
        const { permissionKey, userId, resource, action } = context;
        
        // 尝试从离线缓存获取
        const offlinePermission = this.cache.getOfflineCache(permissionKey);
        
        if (offlinePermission) {
            console.log('[PermissionErrorHandler] 使用离线权限:', permissionKey);
            return {
                success: true,
                permission: offlinePermission,
                source: 'offline',
                fallback: true,
                message: '离线模式：使用本地权限数据'
            };
        }
        
        // 使用离线默认权限
        const offlineDefault = this.getOfflineDefaultPermission(userId, resource, action);
        
        return {
            success: true,
            permission: offlineDefault,
            source: 'offline_default',
            fallback: true,
            message: '离线模式：使用默认权限'
        };
    }

    /**
     * 重试策略
     */
    async executeRetryWithBackoff(context, errorRecord) {
        const { originalRequest, retryCount = 0 } = context;
        
        if (retryCount >= this.retryConfig.maxRetries) {
            console.log('[PermissionErrorHandler] 重试次数已达上限，使用缓存降级');
            return await this.executeCacheFallback(context);
        }
        
        const delay = this.calculateBackoffDelay(retryCount);
        
        console.log(`[PermissionErrorHandler] ${delay}ms后进行第${retryCount + 1}次重试`);
        
        await this.sleep(delay);
        
        try {
            // 重新执行原始请求
            const result = await originalRequest();
            
            // 重试成功，更新熔断器
            this.updateCircuitBreaker(true);
            
            return {
                success: true,
                permission: result,
                source: 'retry',
                retryCount: retryCount + 1,
                message: `重试成功（第${retryCount + 1}次）`
            };
        } catch (retryError) {
            // 重试失败，递归重试或降级
            return await this.executeRetryWithBackoff(
                { ...context, retryCount: retryCount + 1 },
                errorRecord
            );
        }
    }

    /**
     * 优雅降级策略
     */
    async executeGracefulDegradation(context) {
        const { resource, action, userId } = context;
        
        // 提供有限的权限，允许基本操作
        const limitedPermissions = this.getLimitedPermissions(userId, resource);
        
        const hasLimitedPermission = limitedPermissions.includes(action) || 
                                   this.isBasicAction(action);
        
        console.log('[PermissionErrorHandler] 优雅降级:', { resource, action, hasLimitedPermission });
        
        return {
            success: true,
            permission: hasLimitedPermission,
            source: 'degraded',
            fallback: true,
            limited: true,
            message: '功能受限：仅提供基本权限'
        };
    }

    /**
     * 计算退避延迟
     */
    calculateBackoffDelay(retryCount) {
        const baseDelay = this.retryConfig.baseDelay;
        const multiplier = this.retryConfig.backoffMultiplier;
        const maxDelay = this.retryConfig.maxDelay;
        const jitterRange = this.retryConfig.jitterRange;
        
        let delay = Math.min(baseDelay * Math.pow(multiplier, retryCount), maxDelay);
        
        // 添加随机抖动
        const jitter = delay * jitterRange * (Math.random() * 2 - 1);
        delay += jitter;
        
        return Math.max(delay, 0);
    }

    /**
     * 更新熔断器状态
     */
    updateCircuitBreaker(success) {
        const now = Date.now();
        
        if (success) {
            this.circuitBreaker.successCount++;
            
            if (this.circuitBreaker.state === 'HALF_OPEN') {
                // 半开状态下成功，重置熔断器
                this.circuitBreaker.state = 'CLOSED';
                this.circuitBreaker.failureCount = 0;
                console.log('[PermissionErrorHandler] 熔断器已重置为CLOSED状态');
            }
        } else {
            this.circuitBreaker.failureCount++;
            this.circuitBreaker.lastFailureTime = now;
            
            if (this.circuitBreaker.state === 'CLOSED' && 
                this.circuitBreaker.failureCount >= this.circuitBreaker.failureThreshold) {
                // 失败次数达到阈值，打开熔断器
                this.circuitBreaker.state = 'OPEN';
                console.log('[PermissionErrorHandler] 熔断器已打开');
                this.notifyListeners('circuitBreakerOpened', this.circuitBreaker);
            }
        }
        
        // 检查是否可以从OPEN状态转为HALF_OPEN
        if (this.circuitBreaker.state === 'OPEN' && 
            now - this.circuitBreaker.lastFailureTime > this.circuitBreaker.resetTimeout) {
            this.circuitBreaker.state = 'HALF_OPEN';
            console.log('[PermissionErrorHandler] 熔断器转为HALF_OPEN状态');
        }
    }

    /**
     * 启用离线模式
     */
    enableOfflineMode() {
        this.offlineMode.enabled = true;
        this.offlineMode.detectedAt = Date.now();
        
        console.log('[PermissionErrorHandler] 离线模式已启用');
        this.notifyListeners('offlineModeEnabled', this.offlineMode);
        
        // 显示用户通知
        this.showOfflineNotification();
    }

    /**
     * 禁用离线模式
     */
    disableOfflineMode() {
        this.offlineMode.enabled = false;
        this.offlineMode.detectedAt = null;
        
        console.log('[PermissionErrorHandler] 离线模式已禁用');
        this.notifyListeners('offlineModeDisabled', this.offlineMode);
    }

    /**
     * 获取默认权限
     */
    getDefaultPermissions(userId) {
        // 根据用户类型返回默认权限
        const userType = this.getUserType(userId);
        
        const defaultPermissions = {
            guest: ['read'],
            user: ['read', 'write'],
            admin: ['read', 'write', 'delete', 'admin']
        };
        
        return defaultPermissions[userType] || defaultPermissions.guest;
    }

    /**
     * 检查默认权限
     */
    checkDefaultPermission(permissions, resource, action) {
        // 基本权限检查逻辑
        if (permissions.includes('admin')) {
            return true;
        }
        
        if (action === 'read' && permissions.includes('read')) {
            return true;
        }
        
        if (action === 'write' && permissions.includes('write')) {
            return true;
        }
        
        return false;
    }

    /**
     * 获取离线默认权限
     */
    getOfflineDefaultPermission(userId, resource, action) {
        // 离线模式下的保守权限策略
        const userType = this.getUserType(userId);
        
        // 在离线模式下，只允许基本的读取操作
        if (action === 'read') {
            return true;
        }
        
        // 管理员在离线模式下有更多权限
        if (userType === 'admin' && ['read', 'write'].includes(action)) {
            return true;
        }
        
        return false;
    }

    /**
     * 获取有限权限
     */
    getLimitedPermissions(userId, resource) {
        const userType = this.getUserType(userId);
        
        const limitedPermissions = {
            guest: ['read'],
            user: ['read'],
            admin: ['read', 'write']
        };
        
        return limitedPermissions[userType] || ['read'];
    }

    /**
     * 检查是否为基本操作
     */
    isBasicAction(action) {
        const basicActions = ['read', 'view', 'list', 'get'];
        return basicActions.includes(action.toLowerCase());
    }

    /**
     * 获取用户类型
     */
    getUserType(userId) {
        // 从缓存或本地存储获取用户信息
        try {
            const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
            return userInfo.role || 'guest';
        } catch {
            return 'guest';
        }
    }

    /**
     * 获取默认结果
     */
    getDefaultResult(context) {
        return {
            success: false,
            permission: false,
            source: 'default',
            fallback: true,
            message: '权限检查失败，拒绝访问'
        };
    }

    /**
     * 记录错误
     */
    recordError(errorRecord) {
        this.errorHistory.push(errorRecord);
        
        // 保持错误历史大小
        if (this.errorHistory.length > this.maxErrorHistory) {
            this.errorHistory.shift();
        }
    }

    /**
     * 设置网络监听器
     */
    setupNetworkListeners() {
        if (typeof window !== 'undefined') {
            window.addEventListener('online', () => {
                console.log('[PermissionErrorHandler] 网络已连接');
                this.disableOfflineMode();
                this.resetCircuitBreaker();
            });
            
            window.addEventListener('offline', () => {
                console.log('[PermissionErrorHandler] 网络已断开');
                this.enableOfflineMode();
            });
        }
    }

    /**
     * 加载离线权限
     */
    loadOfflinePermissions() {
        try {
            const stored = localStorage.getItem('offline_permissions');
            if (stored) {
                const permissions = JSON.parse(stored);
                this.offlineMode.fallbackPermissions = new Map(permissions);
                console.log('[PermissionErrorHandler] 离线权限已加载');
            }
        } catch (error) {
            console.warn('[PermissionErrorHandler] 加载离线权限失败:', error);
        }
    }

    /**
     * 保存离线权限
     */
    saveOfflinePermissions() {
        try {
            const permissions = Array.from(this.offlineMode.fallbackPermissions.entries());
            localStorage.setItem('offline_permissions', JSON.stringify(permissions));
        } catch (error) {
            console.warn('[PermissionErrorHandler] 保存离线权限失败:', error);
        }
    }

    /**
     * 开始健康检查
     */
    startHealthCheck() {
        setInterval(() => {
            this.performHealthCheck();
        }, 30000); // 每30秒检查一次
    }

    /**
     * 执行健康检查
     */
    async performHealthCheck() {
        if (!this.isOnline()) {
            return;
        }
        
        try {
            // 简单的健康检查请求
            const response = await fetch('/api/health', {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                this.updateCircuitBreaker(true);
                
                if (this.offlineMode.enabled) {
                    this.disableOfflineMode();
                }
            }
        } catch (error) {
            console.log('[PermissionErrorHandler] 健康检查失败:', error.message);
        }
    }

    /**
     * 重置熔断器
     */
    resetCircuitBreaker() {
        this.circuitBreaker.state = 'CLOSED';
        this.circuitBreaker.failureCount = 0;
        this.circuitBreaker.successCount = 0;
        this.circuitBreaker.lastFailureTime = null;
        
        console.log('[PermissionErrorHandler] 熔断器已重置');
    }

    /**
     * 显示离线通知
     */
    showOfflineNotification() {
        const message = '网络连接不稳定，已切换到离线模式。部分功能可能受限。';
        
        // 触发应用内通知
        window.dispatchEvent(new CustomEvent('showNotification', {
            detail: {
                type: 'warning',
                message: message,
                duration: 8000,
                persistent: true
            }
        }));
    }

    /**
     * 检查是否在线
     */
    isOnline() {
        return typeof navigator !== 'undefined' ? navigator.onLine : true;
    }

    /**
     * 睡眠函数
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 添加监听器
     */
    addListener(listener) {
        this.listeners.add(listener);
    }

    /**
     * 移除监听器
     */
    removeListener(listener) {
        this.listeners.delete(listener);
    }

    /**
     * 通知监听器
     */
    notifyListeners(event, data) {
        this.listeners.forEach(listener => {
            try {
                listener(event, data);
            } catch (error) {
                console.error('[PermissionErrorHandler] 监听器错误:', error);
            }
        });
    }

    /**
     * 获取错误统计
     */
    getErrorStats() {
        const stats = {
            total: this.errorHistory.length,
            byType: {},
            recentErrors: this.errorHistory.slice(-10),
            circuitBreaker: { ...this.circuitBreaker },
            offlineMode: { ...this.offlineMode }
        };
        
        // 按类型统计错误
        this.errorHistory.forEach(error => {
            stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;
        });
        
        return stats;
    }

    /**
     * 清除错误历史
     */
    clearErrorHistory() {
        this.errorHistory = [];
        console.log('[PermissionErrorHandler] 错误历史已清除');
    }
}

// 创建全局错误处理器实例
const errorHandler = new PermissionErrorHandler();

export { errorHandler, PermissionErrorHandler };
export default errorHandler;