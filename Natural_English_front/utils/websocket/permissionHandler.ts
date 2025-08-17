/**
 * WebSocket权限处理模块
 * 负责权限变更通知和认证处理
 */

// 接口定义
interface PermissionChangeData {
  action: string;
  resource_type: string;
  resource_name?: string;
  resource_id?: string;
  user_name?: string;
  user_id?: string;
  [key: string]: any;
}

interface ConnectionManager {
  isConnected: boolean;
  send(data: any): boolean;
}

interface PermissionCache {
  clearUserCache(userId: string): void;
  clearResourceCache(resourceType: string, resourceId: string): void;
  clear(): void;
}

export class PermissionHandler {
  private connectionManager: ConnectionManager;
  private permissionCache: PermissionCache;

  constructor(connectionManager: ConnectionManager) {
    this.connectionManager = connectionManager;
    // 使用 any 类型来处理模块导入问题
    this.permissionCache = {} as any;
  }

  /**
   * 发送认证信息
   */
  authenticate(): void {
    const token = localStorage.getItem('token');
    if (token && this.connectionManager.isConnected) {
      const authMessage = {
        type: 'auth',
        token: token,
        timestamp: Date.now()
      };
      
      const success = this.connectionManager.send(authMessage);
      if (success) {
        console.log('[WebSocket] 认证信息已发送');
      } else {
        console.error('[WebSocket] 认证信息发送失败');
      }
    }
  }

  /**
   * 处理权限变更通知
   */
  handlePermissionChange(data: PermissionChangeData): void {
    console.log('[WebSocket] 收到权限变更通知:', data);
    
    try {
      // 清除相关缓存
      if (data.user_id) {
        this.permissionCache.clearUserCache(data.user_id);
      }
      
      if (data.resource_type && data.resource_id) {
        this.permissionCache.clearResourceCache(data.resource_type, data.resource_id);
      }
      
      // 触发权限变更事件
      this.triggerPermissionChangeEvent(data);
      
      // 显示通知
      this.showPermissionChangeNotification(data);
      
    } catch (error) {
      console.error('[WebSocket] 处理权限变更失败:', error);
    }
  }

  /**
   * 触发权限变更事件
   */
  private triggerPermissionChangeEvent(data: PermissionChangeData): void {
    const event = new CustomEvent('permissionChanged', {
      detail: data
    });
    window.dispatchEvent(event);
  }

  /**
   * 显示权限变更通知
   */
  private showPermissionChangeNotification(data: PermissionChangeData): void {
    const message = this.getPermissionChangeMessage(data);
    
    // 创建通知
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('权限变更通知', {
        body: message,
        icon: '/favicon.ico'
      });
    } else {
      // 降级到控制台通知
      console.info('[权限通知]', message);
    }
  }

  /**
   * 获取权限变更消息
   */
  private getPermissionChangeMessage(data: PermissionChangeData): string {
    const { action, resource_type, resource_name, user_name } = data;
    
    const actionMap: Record<string, string> = {
      'granted': '获得了',
      'revoked': '失去了',
      'updated': '更新了'
    };
    
    const resourceMap: Record<string, string> = {
      'course': '课程',
      'lesson': '课时',
      'exercise': '练习',
      'exam': '考试'
    };
    
    const actionText = actionMap[action] || action;
    const resourceText = resourceMap[resource_type] || resource_type;
    const resourceNameText = resource_name || '未知资源';
    const userText = user_name || '用户';
    
    return `${userText}${actionText}对${resourceText}「${resourceNameText}」的访问权限`;
  }

  /**
   * 清理资源
   */
  destroy(): void {
    // 清理权限缓存
    this.permissionCache.clear();
  }
}

export type { PermissionChangeData };