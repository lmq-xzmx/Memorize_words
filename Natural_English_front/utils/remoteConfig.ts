// 远程配置管理
import { getBackendHost } from '../config/apiConfig';

// 配置接口定义
export interface RemoteConfigData {
  apiBaseUrl: string;
  features: {
    darkMode: boolean;
    notifications: boolean;
    analytics: boolean;
  };
  ui: {
    theme: string;
    language: string;
  };
  learning: {
    dailyGoal: number;
    reminderEnabled: boolean;
  };
}

class RemoteConfig {
  private cache: Map<string, any>;
  private lastFetchTime: number;
  private cacheTimeout: number;

  constructor() {
    this.cache = new Map();
    this.lastFetchTime = 0;
    this.cacheTimeout = 5 * 60 * 1000; // 5分钟缓存
  }

  async fetchConfig(): Promise<RemoteConfigData> {
    const now = Date.now();
    
    // 检查缓存是否有效
    if (now - this.lastFetchTime < this.cacheTimeout && this.cache.size > 0) {
      console.log('No new values fetched. Using cached values.');
      return this.getCachedConfig();
    }

    try {
      // 模拟从远程获取配置
      const config = await this.fetchFromRemote();
      
      // 更新缓存
      this.updateCache(config);
      this.lastFetchTime = now;
      
      console.log('New configuration fetched successfully.');
      return config;
    } catch (error) {
      console.warn('Failed to fetch remote config, using cached values:', error);
      return this.getCachedConfig();
    }
  }

  private async fetchFromRemote(): Promise<RemoteConfigData> {
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 返回默认配置
    return {
      apiBaseUrl: getBackendHost(),
      features: {
        darkMode: true,
        notifications: true,
        analytics: false
      },
      ui: {
        theme: 'default',
        language: 'zh-CN'
      },
      learning: {
        dailyGoal: 20,
        reminderEnabled: true
      }
    };
  }

  private updateCache(config: RemoteConfigData): void {
    this.cache.clear();
    Object.entries(config).forEach(([key, value]) => {
      this.cache.set(key, value);
    });
  }

  private getCachedConfig(): RemoteConfigData {
    const config: any = {};
    this.cache.forEach((value, key) => {
      config[key] = value;
    });
    return config as RemoteConfigData;
  }

  getValue<T = any>(key: string, defaultValue: T | null = null): T | null {
    return this.cache.get(key) || defaultValue;
  }

  setValue(key: string, value: any): void {
    this.cache.set(key, value);
  }

  clearCache(): void {
    this.cache.clear();
    this.lastFetchTime = 0;
  }
}

// 创建单例实例
const remoteConfig = new RemoteConfig();

// 初始化配置
remoteConfig.fetchConfig().catch(console.error);

export default remoteConfig;