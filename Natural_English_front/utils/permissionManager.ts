// 权限管理器 - 包含路由检查、缓存管理和同步功能

// 声明require函数
declare const require: any;

// 导入依赖
import { PermissionCache } from '../src/services/permissionCacheService'
import { webSocketManager } from './websocketManager'

// 权限常量定义
const ROLES = {
  ADMIN: 'admin',
  TEACHER: 'teacher', 
  STUDENT: 'student',
  DEAN: 'dean',
  ACADEMIC_SUPERVISOR: 'academic_supervisor',
  RESEARCH_MANAGER: 'research_manager',
  PARENT: 'parent'
};

// 角色层级检查函数
function isRoleHigher(role1: string, role2: string): boolean {
  const hierarchy = ['admin', 'teacher', 'student'];
  return hierarchy.indexOf(role1) < hierarchy.indexOf(role2);
}

// 权限缓存管理函数
function clearPermissionCache(): void {
  PermissionCache.clear();
}

function getCachedUserPermissions(userId: string): Promise<any> {
  return PermissionCache.getUserPermissions(userId);
}

function syncCachedPermissions(): Promise<boolean> {
  // 这里可以实现具体的同步逻辑
  return Promise.resolve(true);
}

// 基础权限函数（临时实现）
function getCurrentUser(): any {
  try {
    return JSON.parse(localStorage.getItem('userInfo') || '{}');
  } catch {
    return null;
  }
}

function canAccessPage(role: string, page: string): boolean {
  return true; // 临时实现
}

function getRolePermissions(role: string): string[] {
  return []; // 临时实现
}

function isAuthenticated(): boolean {
  return !!localStorage.getItem('token');
}

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
  // 使用新的权限缓存服务
  PermissionCache.clear();
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
    // 使用新的权限缓存服务
    const permissions = await PermissionCache.getUserPermissions(userId);
    if (permissions) {
      return permissions.permissions || [];
    }
    
    // 从角色定义获取基础权限
    const rolePermissions = getRolePermissions(role);
    
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
  // 使用新的权限缓存服务 - 临时返回null
  return null;
}

/**
 * 设置权限缓存
 * @param key - 缓存键
 * @param value - 缓存值
 */
export function setCachedPermissions(key: string, value: any): void {
  // 使用新的权限缓存服务 - 临时实现
  console.log('设置缓存:', key, value);
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
 * 基于统一的WebSocket管理器实现权限同步
 */
class PermissionSyncManager {
  private syncInterval: any = null;
  private listeners: Array<(event: string, data?: any) => void> = [];
  private lastSyncTime: number = 0;
  private isDestroyed: boolean = false;
  private isInitialized: boolean = false;
  
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
    const wsStatus = webSocketManager.getStatus();
    const currentRetryCount = wsStatus.reconnectCount + 1;
    if (currentRetryCount < PERMISSION_SYNC_CONFIG.retryAttempts) {
      setTimeout(() => {
        this.syncPermissions();
      }, PERMISSION_SYNC_CONFIG.retryDelay * currentRetryCount);
    } else {
      console.error('权限同步重试次数已达上限');
      this.notifyListeners('sync_failed', { retryCount: currentRetryCount });
    }
  }
  
  /**
   * 更新权限数据
   */
  async updatePermissions(permissionData: any): Promise<void> {
    try {
        if (permissionData.userPermissions) {
          // 使用新的权限缓存服务 - 临时实现
          console.log('更新用户权限:', permissionData.userPermissions);
        }
        
        if (permissionData.rolePermissions) {
          // 使用新的权限缓存服务 - 临时实现
          console.log('更新角色权限:', permissionData.rolePermissions);
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
   * 初始化WebSocket连接监听器
   */
  private initializeWebSocketListeners(): void {
    if (this.isInitialized) {
      return;
    }

    // 监听权限变更消息
    webSocketManager.addListener('permission_update', (data) => {
      this.updatePermissions(data);
    });

    webSocketManager.addListener('permission_changed', (data) => {
      this.updatePermissions(data);
    });

    // 监听连接状态变化
    webSocketManager.addConnectionListener((status) => {
      console.log('[PermissionSyncManager] WebSocket状态变化:', status);
      this.lastSyncTime = status.lastConnectTime || Date.now();
    });

    this.isInitialized = true;
    console.log('[PermissionSyncManager] WebSocket监听器已初始化');
  }

  /**
   * 建立WebSocket连接进行实时同步
   */
  async connectWebSocket(): Promise<void> {
    const user = getCurrentUser();
    const token = localStorage.getItem('token');
    if (!user || !token) {
      console.warn('[PermissionSyncManager] 权限WebSocket连接失败：缺少用户信息或令牌');
      return;
    }

    // 初始化监听器
    this.initializeWebSocketListeners();

    // 使用统一的WebSocket管理器建立连接
    try {
      const connected = await webSocketManager.connect();
      if (connected) {
        console.log('[PermissionSyncManager] 权限WebSocket连接已建立');
      } else {
        console.warn('[PermissionSyncManager] 权限WebSocket连接失败');
      }
    } catch (error) {
      console.error('[PermissionSyncManager] WebSocket连接异常:', error);
    }
  }
  
  /**
   * 安排重连（委托给WebSocket管理器）
   */
  scheduleReconnect(): void {
    console.log('[PermissionSyncManager] 请求重连权限WebSocket');
    this.connectWebSocket();
  }
  
  /**
   * 断开WebSocket连接
   */
  disconnectWebSocket(): void {
    console.log('[PermissionSyncManager] 断开权限WebSocket连接');
    webSocketManager.disconnect();
  }
  
  /**
   * 获取连接状态
   */
  getConnectionStatus(): ConnectionStatus {
    const wsStatus = webSocketManager.getStatus();
    return {
      status: wsStatus.isConnected ? 'connected' : 'disconnected',
      retryCount: wsStatus.reconnectCount,
      websocketState: wsStatus.readyState,
      lastSyncTime: this.lastSyncTime
    };
  }
  
  /**
   * 检查连接是否健康
   */
  isConnectionHealthy(): boolean {
    return webSocketManager.isConnected;
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

// isAuthenticated 函数已在上面定义

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