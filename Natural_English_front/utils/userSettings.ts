/**
 * 用户个性化设置管理工具
 * 提供基于用户ID的个性化设置存储和管理功能
 */

// 类型定义
interface UserInfo {
  id?: string;
  user_id?: string;
  [key: string]: any;
}

interface UserSettings {
  [key: string]: any;
}

/**
 * 获取当前用户ID
 * @returns 用户ID，如果获取失败则返回'default'
 */
export function getCurrentUserId(): string {
  try {
    const userInfo = localStorage.getItem('user');
    if (userInfo) {
      const user: UserInfo = JSON.parse(userInfo);
      return user.id || user.user_id || 'default';
    }
    return 'default';
  } catch (error) {
    console.error('获取用户ID失败:', error);
    return 'default';
  }
}

/**
 * 保存用户个性化设置
 * @param settingKey - 设置键名
 * @param value - 设置值
 * @param userId - 用户ID，可选，默认使用当前用户ID
 */
export function saveUserSetting(settingKey: string, value: any, userId: string | null = null): void {
  try {
    const currentUserId = userId || getCurrentUserId();
    const storageKey = `${settingKey}_${currentUserId}`;
    localStorage.setItem(storageKey, JSON.stringify(value));
    console.log(`用户设置已保存: ${storageKey}`, value);
  } catch (error) {
    console.error('保存用户设置失败:', error);
  }
}

/**
 * 获取用户个性化设置
 * @param settingKey - 设置键名
 * @param defaultValue - 默认值
 * @param userId - 用户ID，可选，默认使用当前用户ID
 * @returns 设置值
 */
export function getUserSetting<T = any>(settingKey: string, defaultValue: T | null = null, userId: string | null = null): T | null {
  try {
    const currentUserId = userId || getCurrentUserId();
    const storageKey = `${settingKey}_${currentUserId}`;
    const savedValue = localStorage.getItem(storageKey);
    
    if (savedValue !== null) {
      return JSON.parse(savedValue) as T;
    }
    return defaultValue;
  } catch (error) {
    console.error('获取用户设置失败:', error);
    return defaultValue;
  }
}

/**
 * 删除用户个性化设置
 * @param settingKey - 设置键名
 * @param userId - 用户ID，可选，默认使用当前用户ID
 */
export function removeUserSetting(settingKey: string, userId: string | null = null): void {
  try {
    const currentUserId = userId || getCurrentUserId();
    const storageKey = `${settingKey}_${currentUserId}`;
    localStorage.removeItem(storageKey);
    console.log(`用户设置已删除: ${storageKey}`);
  } catch (error) {
    console.error('删除用户设置失败:', error);
  }
}

/**
 * 获取所有用户设置
 * @param userId - 用户ID，可选，默认使用当前用户ID
 * @returns 所有用户设置
 */
export function getAllUserSettings(userId: string | null = null): UserSettings {
  try {
    const currentUserId = userId || getCurrentUserId();
    const userSettings: UserSettings = {};
    
    // 遍历localStorage中所有以用户ID结尾的键
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.endsWith(`_${currentUserId}`)) {
        const settingKey = key.replace(`_${currentUserId}`, '');
        const value = localStorage.getItem(key);
        try {
          userSettings[settingKey] = JSON.parse(value!);
        } catch {
          userSettings[settingKey] = value;
        }
      }
    }
    
    return userSettings;
  } catch (error) {
    console.error('获取所有用户设置失败:', error);
    return {};
  }
}

/**
 * 清除所有用户设置
 * @param userId - 用户ID，可选，默认使用当前用户ID
 */
export function clearAllUserSettings(userId: string | null = null): void {
  try {
    const currentUserId = userId || getCurrentUserId();
    const keysToRemove: string[] = [];
    
    // 收集所有需要删除的键
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.endsWith(`_${currentUserId}`)) {
        keysToRemove.push(key);
      }
    }
    
    // 删除所有用户设置
    keysToRemove.forEach(key => {
      localStorage.removeItem(key);
    });
    
    console.log(`已清除用户 ${currentUserId} 的所有设置，共 ${keysToRemove.length} 项`);
  } catch (error) {
    console.error('清除所有用户设置失败:', error);
  }
}

/**
 * 用户设置管理类
 */
export class UserSettingsManager {
  private userId: string;

  constructor(userId: string | null = null) {
    this.userId = userId || getCurrentUserId();
  }
  
  /**
   * 保存设置
   * @param key - 设置键名
   * @param value - 设置值
   */
  save(key: string, value: any): void {
    return saveUserSetting(key, value, this.userId);
  }
  
  /**
   * 获取设置
   * @param key - 设置键名
   * @param defaultValue - 默认值
   * @returns 设置值
   */
  get<T = any>(key: string, defaultValue: T | null = null): T | null {
    return getUserSetting<T>(key, defaultValue, this.userId);
  }
  
  /**
   * 删除设置
   * @param key - 设置键名
   */
  remove(key: string): void {
    return removeUserSetting(key, this.userId);
  }
  
  /**
   * 获取所有设置
   * @returns 所有用户设置
   */
  getAll(): UserSettings {
    return getAllUserSettings(this.userId);
  }
  
  /**
   * 清除所有设置
   */
  clearAll(): void {
    return clearAllUserSettings(this.userId);
  }
  
  /**
   * 更新用户ID
   * @param newUserId - 新的用户ID
   */
  updateUserId(newUserId: string | null): void {
    this.userId = newUserId || getCurrentUserId();
  }
}

// 默认导出一个全局实例
export default new UserSettingsManager();

// 导出类型
export type {
  UserInfo,
  UserSettings
};