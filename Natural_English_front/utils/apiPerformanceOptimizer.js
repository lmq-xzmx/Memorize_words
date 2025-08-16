/**
 * API性能优化器
 * 提供请求缓存、批量处理、响应压缩等功能
 */

class APIPerformanceOptimizer {
    constructor() {
        this.cache = new Map();
        this.batchQueue = new Map();
        this.batchTimer = null;
        this.batchDelay = 100; // 批量处理延迟100ms
        this.cacheExpiry = 5 * 60 * 1000; // 缓存5分钟
        this.maxCacheSize = 100; // 最大缓存条目数
        this.compressionThreshold = 1024; // 1KB以上启用压缩
        
        // 性能监控
        this.metrics = {
            cacheHits: 0,
            cacheMisses: 0,
            batchedRequests: 0,
            totalRequests: 0,
            averageResponseTime: 0
        };
    }

    /**
     * 生成缓存键
     */
    generateCacheKey(url, method, params, data) {
        const key = {
            url,
            method: method.toLowerCase(),
            params: params || {},
            data: data || {}
        };
        return JSON.stringify(key);
    }

    /**
     * 检查缓存
     */
    checkCache(cacheKey) {
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
            this.metrics.cacheHits++;
            return cached.data;
        }
        
        if (cached) {
            this.cache.delete(cacheKey);
        }
        
        this.metrics.cacheMisses++;
        return null;
    }

    /**
     * 设置缓存
     */
    setCache(cacheKey, data) {
        // 检查缓存大小限制
        if (this.cache.size >= this.maxCacheSize) {
            // 删除最旧的缓存项
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(cacheKey, {
            data,
            timestamp: Date.now()
        });
    }

    /**
     * 清除缓存
     */
    clearCache(pattern = null) {
        if (pattern) {
            // 清除匹配模式的缓存
            for (const [key] of this.cache) {
                if (key.includes(pattern)) {
                    this.cache.delete(key);
                }
            }
        } else {
            // 清除所有缓存
            this.cache.clear();
        }
    }

    /**
     * 批量处理请求
     */
    batchRequest(requestConfig) {
        return new Promise((resolve, reject) => {
            const batchKey = `${requestConfig.method}_${requestConfig.url}`;
            
            if (!this.batchQueue.has(batchKey)) {
                this.batchQueue.set(batchKey, []);
            }
            
            this.batchQueue.get(batchKey).push({
                config: requestConfig,
                resolve,
                reject
            });
            
            // 设置批量处理定时器
            if (this.batchTimer) {
                clearTimeout(this.batchTimer);
            }
            
            this.batchTimer = setTimeout(() => {
                this.processBatchQueue();
            }, this.batchDelay);
        });
    }

    /**
     * 处理批量队列
     */
    async processBatchQueue() {
        const batches = new Map(this.batchQueue);
        this.batchQueue.clear();
        this.batchTimer = null;
        
        for (const [batchKey, requests] of batches) {
            if (requests.length === 1) {
                // 单个请求直接处理
                const { config, resolve, reject } = requests[0];
                try {
                    const response = await this.executeRequest(config);
                    resolve(response);
                } catch (error) {
                    reject(error);
                }
            } else {
                // 多个请求批量处理
                this.metrics.batchedRequests += requests.length;
                await this.executeBatchRequests(requests);
            }
        }
    }

    /**
     * 执行批量请求
     */
    async executeBatchRequests(requests) {
        try {
            // 构建批量请求数据
            const batchData = requests.map(req => ({
                id: Math.random().toString(36).substr(2, 9),
                method: req.config.method,
                url: req.config.url,
                data: req.config.data,
                params: req.config.params
            }));
            
            // 发送批量请求
            const batchResponse = await this.executeRequest({
                method: 'POST',
                url: '/api/batch',
                data: { requests: batchData }
            });
            
            // 分发响应
            batchResponse.responses.forEach((response, index) => {
                const { resolve, reject } = requests[index];
                if (response.error) {
                    reject(new Error(response.error));
                } else {
                    resolve(response.data);
                }
            });
            
        } catch (error) {
            // 批量请求失败，回退到单个请求
            console.warn('[API优化器] 批量请求失败，回退到单个请求:', error);
            for (const { config, resolve, reject } of requests) {
                try {
                    const response = await this.executeRequest(config);
                    resolve(response);
                } catch (err) {
                    reject(err);
                }
            }
        }
    }

    /**
     * 执行单个请求
     */
    async executeRequest(config) {
        const startTime = Date.now();
        
        try {
            // 这里应该调用实际的axios实例
            // 为了演示，我们返回一个模拟响应
            const response = await fetch(config.url, {
                method: config.method,
                headers: {
                    'Content-Type': 'application/json',
                    ...config.headers
                },
                body: config.data ? JSON.stringify(config.data) : undefined
            });
            
            const data = await response.json();
            
            // 更新性能指标
            const responseTime = Date.now() - startTime;
            this.updateMetrics(responseTime);
            
            return data;
            
        } catch (error) {
            const responseTime = Date.now() - startTime;
            this.updateMetrics(responseTime);
            throw error;
        }
    }

    /**
     * 更新性能指标
     */
    updateMetrics(responseTime) {
        this.metrics.totalRequests++;
        this.metrics.averageResponseTime = 
            (this.metrics.averageResponseTime * (this.metrics.totalRequests - 1) + responseTime) / 
            this.metrics.totalRequests;
    }

    /**
     * 优化请求配置
     */
    optimizeRequest(config) {
        const optimizedConfig = { ...config };
        
        // 添加压缩头
        if (!optimizedConfig.headers) {
            optimizedConfig.headers = {};
        }
        
        optimizedConfig.headers['Accept-Encoding'] = 'gzip, deflate, br';
        
        // 对于GET请求，添加缓存控制
        if (config.method?.toLowerCase() === 'get') {
            optimizedConfig.headers['Cache-Control'] = 'max-age=300'; // 5分钟缓存
        }
        
        return optimizedConfig;
    }

    /**
     * 获取性能指标
     */
    getMetrics() {
        const cacheHitRate = this.metrics.totalRequests > 0 ? 
            (this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses)) * 100 : 0;
        
        return {
            ...this.metrics,
            cacheHitRate: Math.round(cacheHitRate * 100) / 100,
            cacheSize: this.cache.size
        };
    }

    /**
     * 重置指标
     */
    resetMetrics() {
        this.metrics = {
            cacheHits: 0,
            cacheMisses: 0,
            batchedRequests: 0,
            totalRequests: 0,
            averageResponseTime: 0
        };
    }

    /**
     * 销毁优化器
     */
    destroy() {
        if (this.batchTimer) {
            clearTimeout(this.batchTimer);
        }
        this.cache.clear();
        this.batchQueue.clear();
    }
}

// 创建全局实例
const apiOptimizer = new APIPerformanceOptimizer();

export { APIPerformanceOptimizer, apiOptimizer };
export default apiOptimizer;