// 远程配置管理
import { getBackendHost } from '../config/apiConfig.js'

class RemoteConfig {
  constructor() {
    this.cache = new Map()
    this.lastFetchTime = 0
    this.cacheTimeout = 5 * 60 * 1000 // 5分钟缓存
  }

  async fetchConfig() {
    const now = Date.now()
    
    // 检查缓存是否有效
    if (now - this.lastFetchTime < this.cacheTimeout && this.cache.size > 0) {
      console.log('No new values fetched. Using cached values.')
      return this.getCachedConfig()
    }

    try {
      // 模拟从远程获取配置
      const config = await this.fetchFromRemote()
      
      // 更新缓存
      this.updateCache(config)
      this.lastFetchTime = now
      
      console.log('New configuration fetched successfully.')
      return config
    } catch (error) {
      console.warn('Failed to fetch remote config, using cached values:', error)
      return this.getCachedConfig()
    }
  }

  async fetchFromRemote() {
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 100))
    
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
    }
  }

  updateCache(config) {
    this.cache.clear()
    Object.entries(config).forEach(([key, value]) => {
      this.cache.set(key, value)
    })
  }

  getCachedConfig() {
    const config = {}
    this.cache.forEach((value, key) => {
      config[key] = value
    })
    return config
  }

  getValue(key, defaultValue = null) {
    return this.cache.get(key) || defaultValue
  }

  setValue(key, value) {
    this.cache.set(key, value)
  }

  clearCache() {
    this.cache.clear()
    this.lastFetchTime = 0
  }
}

// 创建单例实例
const remoteConfig = new RemoteConfig()

// 初始化配置
remoteConfig.fetchConfig().catch(console.error)

export default remoteConfig