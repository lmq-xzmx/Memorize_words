/**
 * 统一配置管理器
 * 整合环境配置、API配置、应用配置等，支持动态配置加载
 */

import { apiConfig } from '../config/apiConfig.js';

class ConfigManager {
    constructor() {
        this.configs = new Map();
        this.watchers = new Map();
        this.remoteConfigCache = new Map();
        this.lastRemoteFetch = 0;
        this.remoteCacheTimeout = 5 * 60 * 1000; // 5分钟缓存
        this.initialized = false;
        
        // 默认配置
        this.defaultConfigs = {
            app: {
                name: 'Natural English Learning',
                version: '1.0.0',
                environment: import.meta.env.MODE || 'development',
                debug: import.meta.env.MODE === 'development'
            },
            api: {
                timeout: 15000,
                retryAttempts: 3,
                retryDelay: 1000,
                enableCache: true,
                enableBatch: false
            },
            websocket: {
                maxReconnectAttempts: 8,
                reconnectInterval: 1000,
                maxReconnectInterval: 60000,
                heartbeatInterval: 25000,
                enableQualityMonitoring: true
            },
            ui: {
                theme: 'light',
                language: 'zh-CN',
                pageSize: 20,
                animationDuration: 300,
                showNotifications: true
            },
            performance: {
                enableMetrics: true,
                metricsInterval: 30000,
                maxCacheSize: 100,
                enableLazyLoading: true
            },
            security: {
                tokenRefreshThreshold: 5 * 60 * 1000, // 5分钟
                maxLoginAttempts: 5,
                sessionTimeout: 30 * 60 * 1000, // 30分钟
                enableCSRF: true
            }
        };
        
        this.init();
    }

    /**
     * 初始化配置管理器
     */
    async init() {
        if (this.initialized) {
            return;
        }
        
        try {
            // 加载默认配置
            this.loadDefaultConfigs();
            
            // 加载环境配置
            this.loadEnvironmentConfigs();
            
            // 加载本地存储配置
            this.loadLocalStorageConfigs();
            
            // 尝试加载远程配置
            await this.loadRemoteConfigs();
            
            this.initialized = true;
            console.log('[配置管理器] 初始化完成');
        } catch (error) {
            console.error('[配置管理器] 初始化失败:', error);
            // 即使远程配置加载失败，也要标记为已初始化
            this.initialized = true;
        }
    }

    /**
     * 加载默认配置
     */
    loadDefaultConfigs() {
        Object.entries(this.defaultConfigs).forEach(([key, config]) => {
            this.configs.set(key, { ...config });
        });
    }

    /**
     * 加载环境配置
     */
    loadEnvironmentConfigs() {
        // 从环境变量加载配置
        const envConfigs = {
            app: {
                environment: import.meta.env.MODE,
                debug: import.meta.env.MODE === 'development',
                apiBaseUrl: import.meta.env.VITE_API_BASE_URL
            },
            api: {
                baseUrl: apiConfig.getBackendBaseURL(),
                wsUrl: apiConfig.getWebSocketUrl()
            }
        };
        
        // 合并环境配置
        Object.entries(envConfigs).forEach(([key, config]) => {
            const existing = this.configs.get(key) || {};
            this.configs.set(key, { ...existing, ...config });
        });
    }

    /**
     * 加载本地存储配置
     */
    loadLocalStorageConfigs() {
        try {
            const savedConfigs = localStorage.getItem('app_configs');
            if (savedConfigs) {
                const parsed = JSON.parse(savedConfigs);
                Object.entries(parsed).forEach(([key, config]) => {
                    const existing = this.configs.get(key) || {};
                    this.configs.set(key, { ...existing, ...config });
                });
            }
        } catch (error) {
            console.warn('[配置管理器] 加载本地配置失败:', error);
        }
    }

    /**
     * 加载远程配置
     */
    async loadRemoteConfigs() {
        const now = Date.now();
        
        // 检查缓存是否有效
        if (now - this.lastRemoteFetch < this.remoteCacheTimeout && this.remoteConfigCache.size > 0) {
            this.applyRemoteConfigs();
            return;
        }
        
        try {
            const response = await fetch(`${apiConfig.getBackendBaseURL()}/config/frontend/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${localStorage.getItem('token') || ''}`
                }
            });
            
            if (response.ok) {
                const remoteConfigs = await response.json();
                this.remoteConfigCache.clear();
                Object.entries(remoteConfigs).forEach(([key, config]) => {
                    this.remoteConfigCache.set(key, config);
                });
                
                this.applyRemoteConfigs();
                this.lastRemoteFetch = now;
                console.log('[配置管理器] 远程配置加载成功');
            }
        } catch (error) {
            console.warn('[配置管理器] 远程配置加载失败:', error);
        }
    }

    /**
     * 应用远程配置
     */
    applyRemoteConfigs() {
        this.remoteConfigCache.forEach((config, key) => {
            const existing = this.configs.get(key) || {};
            this.configs.set(key, { ...existing, ...config });
        });
    }

    /**
     * 获取配置
     */
    get(category, key = null, defaultValue = null) {
        const categoryConfig = this.configs.get(category);
        
        if (!categoryConfig) {
            return defaultValue;
        }
        
        if (key === null) {
            return categoryConfig;
        }
        
        return categoryConfig[key] !== undefined ? categoryConfig[key] : defaultValue;
    }

    /**
     * 设置配置
     */
    set(category, key, value) {
        const existing = this.configs.get(category) || {};
        
        if (typeof key === 'object') {
            // 批量设置
            this.configs.set(category, { ...existing, ...key });
        } else {
            // 单个设置
            existing[key] = value;
            this.configs.set(category, existing);
        }
        
        // 触发监听器
        this.notifyWatchers(category, key, value);
        
        // 保存到本地存储
        this.saveToLocalStorage();
    }

    /**
     * 监听配置变化
     */
    watch(category, callback) {
        if (!this.watchers.has(category)) {
            this.watchers.set(category, []);
        }
        
        this.watchers.get(category).push(callback);
        
        // 返回取消监听的函数
        return () => {
            const callbacks = this.watchers.get(category);
            if (callbacks) {
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
            }
        };
    }

    /**
     * 通知监听器
     */
    notifyWatchers(category, key, value) {
        const callbacks = this.watchers.get(category);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(key, value, this.configs.get(category));
                } catch (error) {
                    console.error('[配置管理器] 监听器执行失败:', error);
                }
            });
        }
    }

    /**
     * 保存到本地存储
     */
    saveToLocalStorage() {
        try {
            const configsToSave = {};
            this.configs.forEach((config, key) => {
                // 只保存用户可配置的项目
                if (['ui', 'performance'].includes(key)) {
                    configsToSave[key] = config;
                }
            });
            
            localStorage.setItem('app_configs', JSON.stringify(configsToSave));
        } catch (error) {
            console.warn('[配置管理器] 保存本地配置失败:', error);
        }
    }

    /**
     * 重置配置
     */
    reset(category = null) {
        if (category) {
            // 重置特定分类
            if (this.defaultConfigs[category]) {
                this.configs.set(category, { ...this.defaultConfigs[category] });
                this.notifyWatchers(category, null, this.configs.get(category));
            }
        } else {
            // 重置所有配置
            this.configs.clear();
            this.loadDefaultConfigs();
            this.loadEnvironmentConfigs();
            
            // 通知所有监听器
            this.watchers.forEach((callbacks, category) => {
                this.notifyWatchers(category, null, this.configs.get(category));
            });
        }
        
        this.saveToLocalStorage();
    }

    /**
     * 刷新远程配置
     */
    async refreshRemoteConfigs() {
        this.lastRemoteFetch = 0; // 强制重新获取
        await this.loadRemoteConfigs();
    }

    /**
     * 获取所有配置
     */
    getAllConfigs() {
        const result = {};
        this.configs.forEach((config, key) => {
            result[key] = { ...config };
        });
        return result;
    }

    /**
     * 导出配置
     */
    exportConfigs() {
        return JSON.stringify(this.getAllConfigs(), null, 2);
    }

    /**
     * 导入配置
     */
    importConfigs(configString) {
        try {
            const configs = JSON.parse(configString);
            Object.entries(configs).forEach(([category, config]) => {
                this.set(category, config);
            });
            return true;
        } catch (error) {
            console.error('[配置管理器] 导入配置失败:', error);
            return false;
        }
    }

    /**
     * 获取配置状态
     */
    getStatus() {
        return {
            initialized: this.initialized,
            configCount: this.configs.size,
            watcherCount: Array.from(this.watchers.values()).reduce((sum, arr) => sum + arr.length, 0),
            lastRemoteFetch: this.lastRemoteFetch,
            hasRemoteCache: this.remoteConfigCache.size > 0
        };
    }
}

// 创建全局实例
const configManager = new ConfigManager();

// 便捷方法
export const getConfig = (category, key, defaultValue) => {
    return configManager.get(category, key, defaultValue);
};

export const setConfig = (category, key, value) => {
    return configManager.set(category, key, value);
};

export const watchConfig = (category, callback) => {
    return configManager.watch(category, callback);
};

export { ConfigManager, configManager };
export default configManager;