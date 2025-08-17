/**
 * API拦截器增强模块
 * 将性能优化功能集成到axios实例中
 */

import { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import apiOptimizer from './apiPerformanceOptimizer';
import globalErrorHandler from './globalErrorHandler';

interface EnhancerOptions {
  enableCache?: boolean;
  enableBatch?: boolean;
  cacheableMethods?: string[];
  cachableEndpoints?: string[];
}

interface EnhancerConfig {
  enableCache: boolean;
  enableBatch: boolean;
  cacheableMethods: string[];
  cachableEndpoints: string[];
}

interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  _shouldCache?: boolean;
  _cacheKey?: string;
  _startTime?: number;
}

interface ErrorContext {
  url?: string;
  method?: string;
  enhancerConfig: EnhancerConfig;
}

class APIInterceptorEnhancer {
    private enableCache: boolean;
    private enableBatch: boolean;
    private cacheableMethods: string[];
    private cachableEndpoints: string[];

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
    enhance(axiosInstance: AxiosInstance, options: EnhancerOptions = {}): AxiosInstance {
        const config: EnhancerConfig = {
            enableCache: options.enableCache ?? this.enableCache,
            enableBatch: options.enableBatch ?? this.enableBatch,
            cacheableMethods: options.cacheableMethods ?? this.cacheableMethods,
            cachableEndpoints: options.cachableEndpoints ?? this.cachableEndpoints
        };

        // 请求拦截器
        axiosInstance.interceptors.request.use(
            (requestConfig: InternalAxiosRequestConfig) => {
                return this.handleRequest(requestConfig, config);
            },
            (error: any) => {
                console.error('[API增强器] 请求拦截器错误:', error);
                return Promise.reject(error);
            }
        );

        // 响应拦截器
        axiosInstance.interceptors.response.use(
            (response: AxiosResponse) => {
                return this.handleResponse(response, config);
            },
            (error: AxiosError) => {
                return this.handleError(error, config);
            }
        );

        return axiosInstance;
    }

    /**
     * 处理请求
     */
    private handleRequest(config: InternalAxiosRequestConfig, enhancerConfig: EnhancerConfig): Promise<InternalAxiosRequestConfig> | InternalAxiosRequestConfig {
        // 优化请求配置
        const optimizedConfig = apiOptimizer.optimizeRequest({
            url: config.url || '',
            method: config.method || 'GET',
            params: config.params,
            data: config.data
        }) as any;
        
        // 合并配置
        const extendedConfig = { ...config, ...optimizedConfig } as ExtendedAxiosRequestConfig;
        
        // 检查是否可缓存
        if (this.isCacheable(config, enhancerConfig)) {
            const cacheKey = apiOptimizer.generateCacheKey(
                config.url || '',
                config.method || 'GET',
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
                    } as AxiosResponse)
                });
            }
            
            // 标记为需要缓存
            extendedConfig._shouldCache = true;
            extendedConfig._cacheKey = cacheKey;
        }
        
        // 添加性能监控标记
        extendedConfig._startTime = Date.now();
        
        return extendedConfig;
    }

    /**
     * 处理响应
     */
    private handleResponse(response: AxiosResponse, enhancerConfig: EnhancerConfig): AxiosResponse {
        const config = response.config as ExtendedAxiosRequestConfig;
        
        // 更新性能指标
        if (config._startTime) {
            const responseTime = Date.now() - config._startTime;
            // 注意：updateMetrics是私有方法，这里暂时注释掉
            // apiOptimizer.updateMetrics(responseTime);
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
    private handleError(error: AxiosError, enhancerConfig: EnhancerConfig): Promise<never> {
        const config = error.config as ExtendedAxiosRequestConfig;
        
        // 更新性能指标
        if (config && config._startTime) {
            const responseTime = Date.now() - config._startTime;
            // 注意：updateMetrics是私有方法，这里暂时注释掉
            // apiOptimizer.updateMetrics(responseTime);
        }
        
        // 使用全局错误处理器处理API错误
        const errorContext: ErrorContext = {
            url: config?.url,
            method: config?.method,
            enhancerConfig
        };
        
        if (globalErrorHandler && typeof globalErrorHandler.handleAPIError === 'function') {
            globalErrorHandler.handleAPIError(error, errorContext);
        }
        
        return Promise.reject(error);
    }

    /**
     * 检查请求是否可缓存
     */
    private isCacheable(config: InternalAxiosRequestConfig, enhancerConfig: EnhancerConfig): boolean {
        if (!enhancerConfig.enableCache) {
            return false;
        }
        
        // 检查HTTP方法
        if (!enhancerConfig.cacheableMethods.includes(config.method?.toUpperCase() || 'GET')) {
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
    clearEndpointCache(endpoint: string): void {
        if (apiOptimizer && typeof apiOptimizer.clearCache === 'function') {
            apiOptimizer.clearCache(endpoint);
        }
    }

    /**
     * 获取性能指标
     */
    getPerformanceMetrics(): any {
        if (apiOptimizer && typeof apiOptimizer.getMetrics === 'function') {
            return apiOptimizer.getMetrics();
        }
        return {};
    }

    /**
     * 重置性能指标
     */
    resetMetrics(): void {
        if (apiOptimizer && typeof apiOptimizer.resetMetrics === 'function') {
            apiOptimizer.resetMetrics();
        }
    }
}

// 创建全局实例
const apiEnhancer = new APIInterceptorEnhancer();

export { APIInterceptorEnhancer, apiEnhancer };
export default apiEnhancer;