/**
 * API拦截器增强模块
 * 将性能优化功能集成到axios实例中
 */

import apiOptimizer from './apiPerformanceOptimizer.js';
import globalErrorHandler from './globalErrorHandler.js';
import performanceMonitor from './performanceMonitor.js';

class APIInterceptorEnhancer {
    constructor() {
        this.enableCache = true;
        this.enableBatch = false; // 默认关闭批量处理，需要后端支持
        this.cacheableMethods = ['GET', 'HEAD'];
        this.cachableEndpoints = [
            '/api/words',
            '/api/learning-goals',
            '/api/user/profile',
            '/api/resource-auth/categories',
            '/api/analytics'
        ];
    }

    /**
     * 增强axios实例
     */
    enhance(axiosInstance, options = {}) {
        const config = {
            enableCache: options.enableCache ?? this.enableCache,
            enableBatch: options.enableBatch ?? this.enableBatch,
            cacheableMethods: options.cacheableMethods ?? this.cacheableMethods,
            cachableEndpoints: options.cachableEndpoints ?? this.cachableEndpoints
        };

        // 请求拦截器
        axiosInstance.interceptors.request.use(
            (requestConfig) => {
                return this.handleRequest(requestConfig, config);
            },
            (error) => {
                console.error('[API增强器] 请求拦截器错误:', error);
                return Promise.reject(error);
            }
        );

        // 响应拦截器
        axiosInstance.interceptors.response.use(
            (response) => {
                return this.handleResponse(response, config);
            },
            (error) => {
                return this.handleError(error, config);
            }
        );

        return axiosInstance;
    }

    /**
     * 处理请求
     */
    handleRequest(config, enhancerConfig) {
        // 优化请求配置
        const optimizedConfig = apiOptimizer.optimizeRequest(config);
        
        // 检查是否可缓存
        if (this.isCacheable(config, enhancerConfig)) {
            const cacheKey = apiOptimizer.generateCacheKey(
                config.url,
                config.method,
                config.params,
                config.data
            );
            
            const cachedData = apiOptimizer.checkCache(cacheKey);
            if (cachedData) {
                // 返回缓存的Promise
                return Promise.resolve({
                    ...config,
                    adapter: () => Promise.resolve({
                        data: cachedData,
                        status: 200,
                        statusText: 'OK',
                        headers: {},
                        config,
                        request: {}
                    })
                });
            }
            
            // 标记为需要缓存
            optimizedConfig._shouldCache = true;
            optimizedConfig._cacheKey = cacheKey;
        }
        
        // 添加性能监控标记
        optimizedConfig._startTime = Date.now();
        
        return optimizedConfig;
    }

    /**
     * 处理响应
     */
    handleResponse(response, enhancerConfig) {
        const config = response.config;
        
        // 更新性能指标
        if (config._startTime) {
            const responseTime = Date.now() - config._startTime;
            apiOptimizer.updateMetrics(responseTime);
            
            // 记录到性能监控器
            performanceMonitor.recordAPIRequest(
                config.url,
                config.method,
                responseTime,
                true
            );
        }
        
        // 缓存响应数据
        if (config._shouldCache && config._cacheKey) {
            apiOptimizer.setCache(config._cacheKey, response.data);
        }
        
        return response;
    }

    /**
     * 处理错误
     */
    handleError(error, enhancerConfig) {
        const config = error.config;
        
        // 更新性能指标
        if (config && config._startTime) {
            const responseTime = Date.now() - config._startTime;
            apiOptimizer.updateMetrics(responseTime);
            
            // 记录到性能监控器
            performanceMonitor.recordAPIRequest(
                config.url,
                config.method,
                responseTime,
                false
            );
        }
        
        // 使用全局错误处理器处理API错误
        const errorContext = {
            url: config?.url,
            method: config?.method,
            enhancerConfig
        };
        
        globalErrorHandler.handleAPIError(error, errorContext);
        
        return Promise.reject(error);
    }

    /**
     * 检查请求是否可缓存
     */
    isCacheable(config, enhancerConfig) {
        if (!enhancerConfig.enableCache) {
            return false;
        }
        
        // 检查HTTP方法
        if (!enhancerConfig.cacheableMethods.includes(config.method?.toUpperCase())) {
            return false;
        }
        
        // 检查端点
        const url = config.url || '';
        return enhancerConfig.cachableEndpoints.some(endpoint => 
            url.includes(endpoint)
        );
    }

    /**
     * 清除特定端点的缓存
     */
    clearEndpointCache(endpoint) {
        apiOptimizer.clearCache(endpoint);
    }

    /**
     * 获取性能指标
     */
    getPerformanceMetrics() {
        return apiOptimizer.getMetrics();
    }

    /**
     * 重置性能指标
     */
    resetMetrics() {
        apiOptimizer.resetMetrics();
    }
}

// 创建全局实例
const apiEnhancer = new APIInterceptorEnhancer();

export { APIInterceptorEnhancer, apiEnhancer };
export default apiEnhancer;