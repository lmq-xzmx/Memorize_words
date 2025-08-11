/**
 * 浏览器缓存清除工具
 * 用于清除可能影响前端代码生效的浏览器存储
 */

export class BrowserCacheManager {
  /**
   * 清除所有浏览器存储
   */
  static clearAllStorage() {
    try {
      // 清除 localStorage
      if (typeof localStorage !== 'undefined') {
        const localStorageKeys = Object.keys(localStorage);
        console.log('清除 localStorage 项目:', localStorageKeys);
        localStorage.clear();
      }
      
      // 清除 sessionStorage
      if (typeof sessionStorage !== 'undefined') {
        const sessionStorageKeys = Object.keys(sessionStorage);
        console.log('清除 sessionStorage 项目:', sessionStorageKeys);
        sessionStorage.clear();
      }
      
      console.log('✅ 浏览器存储已清除');
      return true;
    } catch (error) {
      console.error('❌ 清除浏览器存储失败:', error);
      return false;
    }
  }
  
  /**
   * 清除特定前缀的存储项
   * @param {string} prefix - 前缀
   */
  static clearStorageByPrefix(prefix) {
    try {
      // 清除 localStorage 中的特定项
      if (typeof localStorage !== 'undefined') {
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && key.startsWith(prefix)) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach(key => {
          localStorage.removeItem(key);
          console.log(`清除 localStorage: ${key}`);
        });
      }
      
      // 清除 sessionStorage 中的特定项
      if (typeof sessionStorage !== 'undefined') {
        const keysToRemove = [];
        for (let i = 0; i < sessionStorage.length; i++) {
          const key = sessionStorage.key(i);
          if (key && key.startsWith(prefix)) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach(key => {
          sessionStorage.removeItem(key);
          console.log(`清除 sessionStorage: ${key}`);
        });
      }
      
      console.log(`✅ 已清除前缀为 "${prefix}" 的存储项`);
      return true;
    } catch (error) {
      console.error(`❌ 清除前缀为 "${prefix}" 的存储项失败:`, error);
      return false;
    }
  }
  
  /**
   * 清除用户个性化相关的缓存
   */
  static clearPersonalizationCache() {
    const prefixes = [
      'element_',
      'user_',
      'personalization_',
      'config_',
      'settings_'
    ];
    
    prefixes.forEach(prefix => {
      this.clearStorageByPrefix(prefix);
    });
  }
  
  /**
   * 强制刷新页面（清除内存缓存）
   */
  static forceRefresh() {
    try {
      // 先清除存储
      this.clearAllStorage();
      
      // 强制刷新页面
      if (typeof window !== 'undefined') {
        window.location.reload(true);
      }
    } catch (error) {
      console.error('❌ 强制刷新失败:', error);
    }
  }
  
  /**
   * 检查是否有缓存数据
   */
  static checkCacheStatus() {
    const status = {
      localStorage: 0,
      sessionStorage: 0,
      total: 0
    };
    
    try {
      if (typeof localStorage !== 'undefined') {
        status.localStorage = localStorage.length;
      }
      
      if (typeof sessionStorage !== 'undefined') {
        status.sessionStorage = sessionStorage.length;
      }
      
      status.total = status.localStorage + status.sessionStorage;
      
      console.log('缓存状态:', status);
      return status;
    } catch (error) {
      console.error('❌ 检查缓存状态失败:', error);
      return status;
    }
  }
}

// 全局方法，方便在控制台调用
if (typeof window !== 'undefined') {
  window.clearBrowserCache = BrowserCacheManager.clearAllStorage;
  window.clearPersonalizationCache = BrowserCacheManager.clearPersonalizationCache;
  window.forceRefresh = BrowserCacheManager.forceRefresh;
  window.checkCacheStatus = BrowserCacheManager.checkCacheStatus;
}

export default BrowserCacheManager;