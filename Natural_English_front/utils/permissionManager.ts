// 权限管理器 - 包含路由检查、缓存管理和同步功能

// 导入依赖
import * as authSync from './authSync';
import * as permissionCache from './permissionCache';
import * as unifiedPermissionConstants from './unifiedPermissionConstants';
import * as roleDefinitions from './roleDefinitions';

// 从其他模块导入
const { ROLES } = unifiedPermissionConstants;
const { isRoleHigher } = roleDefinitions;
const {
  default: permissionCacheManager,
  clearPermissionCache,
  getUserPermissions: getCachedUserPermissions,
  syncPermissions: syncCachedPermissions
} = permissionCache;

// 导入基础权限函数
import { getCurrentUser, canAccessPage, getRolePermissions } from './permission';

// 类型定义
interface User {
  id?: string;
  user_id?: string;
  username: string;
  role: string;
  [key: string]: any;
}

interface RouteObject {
  path: string;
  meta?: {
    requiresAuth?: boolean;
    [key: string]: any;
  };
}

interface PermissionSyncConfig {
  apiEndpoint: string;
  websocketEndpoint?: string;
  syncInterval: number;
  retryAttempts: number;
  retryDelay: number;
  maxRetryDelay: number;
}

interface PermissionCacheStatus {
  lastSync: number;
  syncing: boolean;
  version: string;
}

interface ConnectionStatus {
  status: string;
  retryCount: number;
  websocketState: number | null;
  lastSyncTime: number;
}

// 权限缓存状态
let permissionCacheStatus: PermissionCacheStatus = {
  lastSync: 0,
  syncing: false,
  version: '1.0.0'
};

// 权限同步配置
const PERMISSION_SYNC_CONFIG: PermissionSyncConfig = {
  apiEndpoint: '/api/permissions/sync',
  websocketEndpoint: 'ws://localhost:8001/ws/permissions/',
  syncInterval: 30 * 1000, // 30秒同步间隔
  retryAttempts: 5,
  retryDelay: 2000,
  maxRetryDelay: 30000
};

/**
 * 路由权限检查函数
 * @param to - 目标路由
 * @param from - 来源路由
 * @param next - 路由继续函数
 */
export async function checkRoutePermission(
  to: RouteObject, 
  from: RouteObject, 
  next: (path?: string) => void
): Promise<void> {
  // 确保路由对象有 meta 属性
  if (!to.meta) {
    to.meta = {};
  }
  
  const authenticated = await isAuthenticated();
  const user = getCurrentUser();
  
  // 如果路由需要认证但用户未登录
  if (to.meta.requiresAuth && !authenticated) {
    next('/login');
    return;
  }
  
  // 如果用户已登录但访问登录页，重定向到首页
  if (authenticated && to.path === '/login') {
    next('/');
    return;
  }
  
  // 检查页面权限
  if (user && !canAccessPage(user.role, to.path)) {
    // 记录访问被拒绝的日志
    console.warn(`访问被拒绝: 用户 ${user.username} (${user.role}) 尝试访问 ${to.path}`);
    
    // 重定向到用户有权限的默认页面
    const defaultPage = getDefaultPageForRole(user.role);
    next(defaultPage);
    return;
  }
  
  // 特殊页面处理
  if (to.path.startsWith('/admin') && user && !isRoleHigher(user.role, ROLES.TEACHER)) {
    next('/dashboard');
    return;
  }
  
  next();
}

/**
 * 获取角色的默认页面
 * @param role - 用户角色
 * @returns 默认页面路径
 */
export function getDefaultPageForRole(role: string): string {
  const defaultPages: Record<string, string> = {
    [ROLES.ADMIN]: '/admin/dashboard',
    [ROLES.DEAN]: '/management/overview',
    [ROLES.ACADEMIC_SUPERVISOR]: '/academic/dashboard',
    [ROLES.RESEARCH_MANAGER]: '/research/dashboard',
    [ROLES.TEACHER]: '/teacher/dashboard',
    [ROLES.PARENT]: '/parent/dashboard',
    [ROLES.STUDENT]: '/dashboard'
  };
  
  return defaultPages[role] || '/dashboard';
}

/**
 * 清除权限缓存
 */
export function clearCache(): void {
  clearPermissionCache();
  permissionCacheStatus.lastSync = 0;
  permissionCacheStatus.syncing = false;
}

/**
 * 获取用户权限（使用缓存管理器）
 * @param userId - 用户ID
 * @param role - 用户角色
 * @returns 用户权限列表
 */
export async function fetchUserPermissions(userId: string, role: string): Promise<string[]> {
  try {
    // 优先从缓存获取
    const cachedPermissions = await getCachedUserPermissions(userId);
    if (cachedPermissions) {
      return cachedPermissions;
    }
    
    // 从角色定义获取基础权限
    const rolePermissions = getRolePermissions(role);
    
    // 缓存权限数据
    await permissionCacheManager.set(`user_permissions_${userId}`, rolePermissions);
    
    return rolePermissions;
  } catch (error) {
    console.error('获取用户权限失败:', error);
    // 降级到角色权限
    return getRolePermissions(role);
  }
}

/**
 * 同步权限数据
 * @param force - 是否强制同步
 * @returns 同步是否成功
 */
export async function syncPermissions(force: boolean = false): Promise<boolean> {
  if (permissionCacheStatus.syncing && !force) {
    return false;
  }
  
  permissionCacheStatus.syncing = true;
  
  try {
    const result = await syncCachedPermissions();
    permissionCacheStatus.lastSync = Date.now();
    permissionCacheStatus.syncing = false;
    
    // 通知权限变更
    permissionSyncManager.notifyListeners('permissions_synced', {
      success: result,
      timestamp: permissionCacheStatus.lastSync
    });
    
    return result;
  } catch (error) {
    console.error('权限同步失败:', error);
    permissionCacheStatus.syncing = false;
    return false;
  }
}

/**
 * 获取缓存的权限数据
 * @param key - 缓存键
 * @returns 缓存的数据
 */
export function getCachedPermissions(key: string): any {
  // 使用新的缓存管理器
  return permissionCacheManager.get(key);
}

/**
 * 设置权限缓存
 * @param key - 缓存键
 * @param value - 缓存值
 */
export function setCachedPermissions(key: string, value: any): void {
  // 使用新的缓存管理器
  return permissionCacheManager.set(key, value);
}

/**
 * 清除认证缓存
 */
export function clearAuthCache(): void {
  // 这个函数需要访问permission.ts中的authCache，暂时通过全局对象实现
  if (typeof window !== 'undefined' && (window as any).permissionUtils) {
    (window as any).permissionUtils.clearAuthCache?.();
  }
  clearPermissionCache();
}

/**
 * 清除用户认证信息
 */
export function clearAuth(): void {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('userSettings');
  
  // 清除认证缓存
  clearAuthCache();
  
  // 触发权限变更事件
  if (typeof window !== 'undefined' && (window as any).permissionWatcher) {
    (window as any).permissionWatcher.notifyChange();
  }
}

/**
 * 权限同步管理器
 */
class PermissionSyncManager {
  private websocket: WebSocket | null = null;
  private syncInterval: any = null;
  private retryCount: number = 0;
  private listeners: Array<(event: string, data?: any) => void> = [];
  private connectionStatus: string = 'disconnected';
  private lastSyncTime: number = 0;
  private isDestroyed: boolean = false;
  
  constructor() {
    // 初始化状态
  }
  
  init(): void {
    // 监听localStorage变化
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', (e) => {
        if (e.key === 'user' || e.key === 'token' || e.key === 'permissionCache') {
          this.notifyListeners('permission_changed', {
            key: e.key,
            oldValue: e.oldValue,
            newValue: e.newValue
          });
          
          // 清除缓存，强制重新获取权限
          if (e.key === 'user') {
            clearPermissionCache();
          }
        }
      });
    }
    
    // 启动定期同步
    this.startPeriodicSync();
  }
  
  /**
   * 启动定期权限同步
   */
  startPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    
    this.syncInterval = setInterval(() => {
      this.syncPermissions();
    }, PERMISSION_SYNC_CONFIG.syncInterval);
  }
  
  /**
   * 停止定期同步
   */
  stopPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }
  
  /**
   * 同步权限数据
   */
  async syncPermissions(): Promise<void> {
    const user = getCurrentUser();
    if (!user) {
      return;
    }
    
    try {
      // 使用新的权限缓存管理器进行同步
      const syncResult = await syncCachedPermissions();
      
      if (syncResult) {
        this.retryCount = 0;
        this.notifyListeners('permissions_synced', {
          success: true,
          timestamp: Date.now()
        });
      } else {
        throw new Error('权限同步失败');
      }
    } catch (error) {
      console.warn('权限同步错误:', error);
      this.handleSyncError();
    }
  }
  
  /**
   * 处理同步错误
   */
  handleSyncError(): void {
    this.retryCount++;
    if (this.retryCount < PERMISSION_SYNC_CONFIG.retryAttempts) {
      setTimeout(() => {
        this.syncPermissions();
      }, PERMISSION_SYNC_CONFIG.retryDelay * this.retryCount);
    } else {
      console.error('权限同步重试次数已达上限');
      this.notifyListeners('sync_failed', { retryCount: this.retryCount });
    }
  }
  
  /**
   * 更新权限数据
   */
  async updatePermissions(permissionData: any): Promise<void> {
    try {
      if (permissionData.userPermissions) {
        await permissionCacheManager.set('userPermissions', permissionData.userPermissions);
      }
      
      if (permissionData.rolePermissions) {
        await permissionCacheManager.set('rolePermissions', permissionData.rolePermissions);
      }
      
      // 更新缓存状态
      permissionCacheStatus.lastSync = Date.now();
      
      this.notifyListeners('permissions_updated', permissionData);
    } catch (error) {
      console.error('更新权限数据失败:', error);
      this.notifyListeners('permissions_update_failed', { error });
    }
  }
  
  /**
   * 建立WebSocket连接进行实时同步
   */
  connectWebSocket(): void {
    const user = getCurrentUser();
    const token = localStorage.getItem('token');
    if (!user || !token) {
      console.warn('权限WebSocket连接失败：缺少用户信息或令牌');
      return;
    }
    
    // 如果已有连接且状态正常，不重复连接
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      console.log('权限WebSocket已连接，跳过重复连接');
      return;
    }
    
    // 关闭现有连接
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    try {
      // 构建WebSocket URL，添加用户ID参数
      const wsUrl = `${PERMISSION_SYNC_CONFIG.websocketEndpoint}?token=${encodeURIComponent(token)}&userId=${user.id || user.user_id}`;
      console.log('正在连接权限WebSocket:', wsUrl.replace(/token=[^&]+/, 'token=***'));
      
      this.websocket = new WebSocket(wsUrl);
      
      // 设置连接超时
      const connectionTimeout = setTimeout(() => {
        if (this.websocket && this.websocket.readyState === WebSocket.CONNECTING) {
          console.error('权限WebSocket连接超时');
          this.websocket.close();
        }
      }, 10000);
      
      this.websocket.onopen = () => {
        clearTimeout(connectionTimeout);
        console.log('权限WebSocket连接已建立');
        this.retryCount = 0;
        this.connectionStatus = 'connected';
        
        // 发送认证确认
        if (this.websocket) {
          this.websocket.send(JSON.stringify({
            type: 'auth_confirm',
            userId: user.id || user.user_id,
            timestamp: Date.now()
          }));
        }
      };
      
      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('收到权限WebSocket消息:', data);
          
          if (data.type === 'permission_update' || data.type === 'permission_changed') {
            this.updatePermissions(data.payload || data.data);
          } else if (data.type === 'auth_success') {
            console.log('权限WebSocket认证成功');
            this.connectionStatus = 'authenticated';
          } else if (data.type === 'heartbeat') {
            // 响应心跳
            if (this.websocket) {
              this.websocket.send(JSON.stringify({ type: 'heartbeat_response' }));
            }
          }
        } catch (error: any) {
        console.error('WebSocket消息解析错误:', error);
        }
      };
      
      this.websocket.onclose = (event) => {
        clearTimeout(connectionTimeout);
        this.connectionStatus = 'disconnected';
        
        console.log(`权限WebSocket连接已关闭，代码: ${event.code}, 原因: ${event.reason || '未知'}`);
        
        // 根据关闭代码决定是否重连
        if (event.code !== 1000 && event.code !== 1001) { // 非正常关闭
          this.scheduleReconnect();
        }
      };
      
      this.websocket.onerror = (error) => {
        clearTimeout(connectionTimeout);
        this.connectionStatus = 'error';
        
        console.error('权限WebSocket错误:', {
          error: error,
          readyState: this.websocket ? this.websocket.readyState : 'null',
          url: wsUrl.replace(/token=[^&]+/, 'token=***'),
          retryCount: this.retryCount
        });
        
        // 触发WebSocket诊断
        if (typeof window !== 'undefined' && (window as any).websocketDiagnostics) {
          (window as any).websocketDiagnostics.handleWebSocketError('权限WebSocket', error.toString());
        }
        
        // 检查是否是网络错误
        if (typeof navigator !== 'undefined' && !navigator.onLine) {
          console.warn('网络连接断开，等待网络恢复后重连');
          if (typeof window !== 'undefined') {
            window.addEventListener('online', () => {
              console.log('网络已恢复，尝试重连WebSocket');
              this.connectWebSocket();
            }, { once: true });
          }
        }
      };
    } catch (error) {
      console.error('WebSocket连接失败:', error);
      this.connectionStatus = 'error';
      
      // 触发WebSocket诊断
      if (typeof window !== 'undefined' && (window as any).websocketDiagnostics) {
        (window as any).websocketDiagnostics.handleWebSocketError('WebSocket连接失败', error.toString());
      }
      
      this.scheduleReconnect();
    }
  }
  
  /**
   * 安排重连
   */
  scheduleReconnect(): void {
    if (this.retryCount >= PERMISSION_SYNC_CONFIG.retryAttempts) {
      console.error(`权限WebSocket重连失败，已达到最大重试次数 ${PERMISSION_SYNC_CONFIG.retryAttempts}`);
      return;
    }
    
    const delay = Math.min(
      PERMISSION_SYNC_CONFIG.retryDelay * Math.pow(2, this.retryCount),
      PERMISSION_SYNC_CONFIG.maxRetryDelay
    );
    
    console.log(`${delay / 1000}秒后尝试重连权限WebSocket (第${this.retryCount + 1}次)`);
    
    setTimeout(() => {
      this.retryCount++;
      this.connectWebSocket();
    }, delay);
  }
  
  /**
   * 断开WebSocket连接
   */
  disconnectWebSocket(): void {
    if (this.websocket) {
      console.log('主动断开权限WebSocket连接');
      this.websocket.close(1000, '主动断开'); // 正常关闭
      this.websocket = null;
    }
    this.connectionStatus = 'disconnected';
    this.retryCount = 0;
  }
  
  /**
   * 获取连接状态
   */
  getConnectionStatus(): ConnectionStatus {
    return {
      status: this.connectionStatus,
      retryCount: this.retryCount,
      websocketState: this.websocket ? this.websocket.readyState : null,
      lastSyncTime: this.lastSyncTime
    };
  }
  
  /**
   * 检查连接是否健康
   */
  isConnectionHealthy(): boolean {
    return this.websocket !== null && 
           this.websocket.readyState === WebSocket.OPEN && 
           this.connectionStatus === 'authenticated';
  }
  
  /**
   * 添加权限变更监听器
   */
  addListener(callback: (event: string, data?: any) => void): void {
    this.listeners.push(callback);
  }
  
  /**
   * 移除权限变更监听器
   */
  removeListener(callback: (event: string, data?: any) => void): void {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  /**
   * 通知所有监听器
   */
  notifyListeners(event: string, data?: any): void {
    this.listeners.forEach(callback => {
      try {
        callback(event, data);
      } catch (error) {
        console.error('权限监听器执行错误:', error);
      }
    });
  }
  
  /**
   * 通知权限变更（兼容性方法）
   * @param user - 用户信息
   */
  notifyChange(user?: User): void {
    this.notifyListeners('permission_changed', user);
  }
  
  /**
   * 启动同步管理器
   */
  start(): void {
    this.startPeriodicSync();
    this.connectWebSocket();
  }

  /**
   * 停止同步管理器（兼容性方法）
   */
  stop(): void {
    this.destroy();
  }
  
  /**
   * 销毁同步管理器
   */
  destroy(): void {
    this.stopPeriodicSync();
    this.disconnectWebSocket();
    this.listeners = [];
  }
}

// 创建全局权限同步管理器实例
export const permissionSyncManager = new PermissionSyncManager();

// 兼容性导出
export const permissionWatcher = permissionSyncManager;

// 监听localStorage变化，自动更新权限状态
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key === 'user' || event.key === 'token') {
      const user = getCurrentUser();
      permissionWatcher.notifyChange(user || undefined);
    }
  });
}

// 导入isAuthenticated函数
import { isAuthenticated } from './permission';

// 默认导出
export default {
  checkRoutePermission,
  getDefaultPageForRole,
  clearCache,
  fetchUserPermissions,
  syncPermissions,
  getCachedPermissions,
  setCachedPermissions,
  clearAuthCache,
  clearAuth,
  permissionSyncManager,
  permissionWatcher
};