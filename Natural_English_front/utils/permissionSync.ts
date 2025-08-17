// 权限同步管理器
import { getCurrentUser } from './permission';
import { fetchUserMenuPermissions } from './dynamicPermission';

// 类型定义
type PermissionSyncEventType = 'userPermissions' | 'authCleared';
type PermissionSyncCallback = (type: PermissionSyncEventType, data: any) => void;

interface PermissionData {
  success: boolean;
  [key: string]: any;
}

interface User {
  id?: string | number;
  username?: string;
  [key: string]: any;
}

// 权限同步管理器类
class PermissionSyncManager {
  private listeners: PermissionSyncCallback[];
  private isAutoSyncEnabled: boolean;
  private syncInterval: NodeJS.Timeout | null;
  private syncIntervalTime: number;

  constructor() {
    this.listeners = [];
    this.isAutoSyncEnabled = false;
    this.syncInterval = null;
    this.syncIntervalTime = 5 * 60 * 1000; // 5分钟
  }

  // 添加权限变更监听器
  addListener(callback: PermissionSyncCallback): void {
    this.listeners.push(callback);
  }

  // 移除权限变更监听器
  removeListener(callback: PermissionSyncCallback): void {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  // 通知所有监听器
  notifyListeners(type: PermissionSyncEventType, data: any): void {
    this.listeners.forEach(callback => {
      try {
        callback(type, data);
      } catch (error) {
        console.error('权限同步监听器执行失败:', error);
      }
    });
  }

  // 启动自动同步
  startAutoSync(): void {
    if (this.isAutoSyncEnabled) {
      return;
    }

    this.isAutoSyncEnabled = true;
    this.syncInterval = setInterval(async () => {
      try {
        await this.syncUserPermissions();
      } catch (error) {
        console.error('自动权限同步失败:', error);
      }
    }, this.syncIntervalTime);

    console.log('权限自动同步已启动');
  }

  // 停止自动同步
  stopAutoSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    this.isAutoSyncEnabled = false;
    console.log('权限自动同步已停止');
  }

  // 同步用户权限
  async syncUserPermissions(): Promise<PermissionData | null> {
    try {
      const user: User | null = getCurrentUser();
      if (!user) {
        console.log('用户未登录，跳过权限同步');
        return null;
      }

      const permissionData: any = await fetchUserMenuPermissions();
      if (permissionData && permissionData.success) {
        console.log('权限同步成功:', permissionData);
        this.notifyListeners('userPermissions', permissionData);
        return permissionData;
      } else {
        console.warn('权限同步失败:', permissionData);
        return null;
      }
    } catch (error) {
      console.error('权限同步异常:', error);
      return null;
    }
  }

  // 清除认证信息
  clearAuth(): void {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    this.notifyListeners('authCleared', null);
    console.log('认证信息已清除');
  }
}

// 创建全局实例
const permissionSyncManager = new PermissionSyncManager();

// 导出便捷函数
export async function syncUserPermissions(): Promise<PermissionData | null> {
  return await permissionSyncManager.syncUserPermissions();
}

export function startAutoSync(): void {
  permissionSyncManager.startAutoSync();
}

export function stopAutoSync(): void {
  permissionSyncManager.stopAutoSync();
}

export function addPermissionListener(callback: PermissionSyncCallback): void {
  permissionSyncManager.addListener(callback);
}

export function removePermissionListener(callback: PermissionSyncCallback): void {
  permissionSyncManager.removeListener(callback);
}

export function clearAuth(): void {
  permissionSyncManager.clearAuth();
}

// 默认导出管理器实例
export default permissionSyncManager;

// 导出类型
export type {
  PermissionSyncEventType,
  PermissionSyncCallback,
  PermissionData,
  User
};