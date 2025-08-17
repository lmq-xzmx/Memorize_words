// 前端权限控制工具 - TypeScript版本
// 实现基于角色的访问控制 (RBAC)

// 导入依赖模块
import * as authSync from './authSync';
import * as unifiedPermissionConstants from './unifiedPermissionConstants';
import * as roleDefinitions from './roleDefinitions';
import * as learningModePermissions from './learningModePermissions';
import * as permissionCache from './permissionCache';
import * as permissionManager from './permissionManager';

// 从统一权限常量中导入
const {
  ALL_PERMISSIONS,
  PERMISSION_CATEGORIES,
  PERMISSION_DISPLAY_NAMES,
  LEARNING_PERMISSIONS,
  CONTENT_PERMISSIONS,
  SOCIAL_PERMISSIONS,
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS,
  ADVANCED_PERMISSIONS,
  ROLES,
  ROLE_DISPLAY_NAMES
} = unifiedPermissionConstants;

// 从角色定义中导入
const {
  ROLE_PERMISSIONS,
  getRolePermissions,
  roleHasPermission,
  isRoleHigher,
  getManageableRoles
} = roleDefinitions;

// 从统一权限常量中导入页面权限相关
const {
  PAGE_PERMISSIONS,
  canAccessPage: canAccessPageByPermissions,
  pageRequiresAuth,
  getAccessibleLearningModes,
  getAllAccessiblePages
} = unifiedPermissionConstants;

// 从权限缓存中导入
const {
  // permissionCacheManager,
  // clearPermissionCache,
  // getCachedUserPermissions,
  // syncCachedPermissions
} = permissionCache;

// 类型定义
interface User {
  id?: string;
  user_id?: string;
  username: string;
  role: string;
  [key: string]: any;
}

interface MenuItem {
  id: string;
  title: string;
  path: string;
  icon: string;
  permission?: string | string[];
  children?: MenuItem[];
}

interface PermissionSyncConfig {
  apiEndpoint: string;
  websocketEndpoint?: string;
  syncInterval: number;
  retryAttempts: number;
  retryDelay: number;
  maxRetryDelay: number;
}

interface AuthCache {
  lastCheck: number;
  result: boolean | null;
  syncing: boolean;
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
  websocketEndpoint: 'ws://localhost:8000/ws/permissions/',
  syncInterval: 30 * 1000, // 30秒同步间隔
  retryAttempts: 5,
  retryDelay: 2000,
  maxRetryDelay: 30000
};

// 旧版页面权限映射（向后兼容）
const PAGE_PERMISSIONS_LEGACY: Record<string, string> = {
  // '/': 'view_word_learning', // 首页不需要权限，允许所有用户访问
  '/dashboard': 'view_dashboard',
  '/profile': 'view_own_profile',
  '/settings': 'change_own_settings',
  '/help': 'view_help',
  '/word-learning': 'view_word_learning',
  '/word-learning/spelling': 'practice_spelling',
  '/word-learning/flashcard': 'use_flashcard',
  '/word-reading': 'practice_reading',
  '/word-detail': 'view_word_detail',
  '/word-examples': 'view_word_examples',
  '/story-reading': 'practice_story_reading',
  '/listening': 'practice_listening',
  '/word-challenge': 'participate_challenge',
  '/word-selection': 'practice_word_selection',
  '/word-selection-practice': 'practice_word_selection',
  '/word-selection-practice2': 'practice_word_selection',
  '/word-review': 'review_words',
  '/word-root-analysis': 'analyze_word_roots',
  '/pattern-memory': 'use_pattern_memory',
  '/community': 'access_community',
  '/fashion': 'access_fashion_content',
  '/dev': 'access_dev_tools',
  '/dev-index': 'access_dev_tools',
  '/admin/dev-index': 'access_dev_tools',
  '/analytics': 'view_analytics',
  '/resource-auth': 'manage_resource_auth',
  '/subscription-management': 'manage_subscriptions',
  '/resource-sharing': 'share_resources',
  '/test': 'access_test_features',
  '/learning-modes': 'view_word_learning',
  '/competition': 'participate_challenge',
  '/quick-brush': 'review_words',
  '/discover': 'discover_content'
};

/**
 * 检查用户是否拥有指定权限
 * @param userRole - 用户角色或权限列表
 * @param permission - 权限名称
 * @returns 是否拥有权限
 */
export function hasPermission(userRole: string | string[], permission: string): boolean {
  if (!permission) {
    return false;
  }
  
  // 如果传入的是权限数组，直接检查
  if (Array.isArray(userRole)) {
    return userRole.includes(permission);
  }
  
  // 如果传入的是角色，获取角色权限
  if (typeof userRole === 'string') {
    const permissions = getRolePermissions(userRole) || [];
    return permissions.includes('*') || permissions.includes(permission);
  }
  
  return false;
}

/**
 * 检查用户是否拥有多个权限中的任意一个
 * @param userRole - 用户角色或权限列表
 * @param permissions - 权限列表
 * @returns 是否拥有任意权限
 */
export function hasAnyPermission(userRole: string | string[], permissions: string[]): boolean {
  if (!permissions || !Array.isArray(permissions)) {
    return false;
  }
  
  return permissions.some(permission => hasPermission(userRole, permission));
}

/**
 * 检查用户是否拥有所有指定权限
 * @param userRole - 用户角色或权限列表
 * @param permissions - 权限列表
 * @returns 是否拥有所有权限
 */
export function hasAllPermissions(userRole: string | string[], permissions: string[]): boolean {
  if (!permissions || !Array.isArray(permissions)) {
    return true;
  }
  
  return permissions.every(permission => hasPermission(userRole, permission));
}

/**
 * 检查用户是否可以访问指定页面
 * @param userRole - 用户角色或权限列表
 * @param path - 页面路径
 * @returns 是否可以访问
 */
export function canAccessPage(userRole: string | string[], path: string): boolean {
  if (!path) {
    return false;
  }
  
  // 获取用户权限列表
  let userPermissions: string[] = [];
  if (Array.isArray(userRole)) {
    userPermissions = userRole;
  } else if (typeof userRole === 'string') {
    userPermissions = getRolePermissions(userRole) || [];
  }
  
  // 处理动态路由参数
  const normalizedPath = path.replace(/\/\d+$/, '').replace(/\/[^/]*$/, '');
  const permission = PAGE_PERMISSIONS_LEGACY[normalizedPath] || PAGE_PERMISSIONS_LEGACY[path];
  
  if (!permission) {
    // 如果页面没有定义权限要求，默认允许访问
    return true;
  }
  
  return userPermissions.includes('*') || userPermissions.includes(permission);
}

/**
 * 获取用户可访问的页面列表
 * @param userRole - 用户角色或权限列表
 * @returns 可访问的页面配置列表
 */
export function getAccessiblePages(userRole: string | string[]): Array<{path: string, permission: string}> {
  let userPermissions: string[] = [];
  if (Array.isArray(userRole)) {
    userPermissions = userRole;
  } else if (typeof userRole === 'string') {
    userPermissions = getRolePermissions(userRole) || [];
  }
  
  const accessiblePages: Array<{path: string, permission: string}> = [];
  for (const [path, permission] of Object.entries(PAGE_PERMISSIONS_LEGACY)) {
    if (userPermissions.includes('*') || userPermissions.includes(permission)) {
      accessiblePages.push({ path, permission });
    }
  }
  
  return accessiblePages;
}

/**
 * 获取用户可访问的菜单项
 * @param userRole - 用户角色或权限列表
 * @param menuItems - 菜单项列表
 * @returns 过滤后的菜单项
 */
export function getAccessibleMenus(userRole: string | string[], menuItems?: MenuItem[]): MenuItem[] {
  // 如果没有传入菜单项，使用默认菜单
  const defaultMenus: MenuItem[] = [
    {
      id: 'dashboard',
      title: '仪表板',
      path: '/dashboard',
      icon: '📊',
      permission: 'view_dashboard'
    },
    {
      id: 'word-learning',
      title: '单词学习',
      path: '/word-learning',
      icon: '📚',
      permission: 'view_word_learning'
    },
    {
      id: 'word-challenge',
      title: '单词挑战',
      path: '/word-challenge',
      icon: '🎯',
      permission: 'participate_challenge'
    },
    {
      id: 'word-review',
      title: '单词复习',
      path: '/word-review',
      icon: '🔄',
      permission: 'review_words'
    },
    {
      id: 'community',
      title: '学习社区',
      path: '/community',
      icon: '👥',
      permission: 'access_community'
    },
    {
      id: 'analytics',
      title: '数据分析',
      path: '/analytics',
      icon: '📈',
      permission: 'view_analytics'
    },
    {
      id: 'resource-auth',
      title: '资源管理',
      path: '/resource-auth',
      icon: '🔐',
      permission: 'manage_resource_auth'
    },
    {
      id: 'dev-index',
      title: '开发工具',
      path: '/dev-index',
      icon: '🛠️',
      permission: 'access_dev_tools'
    },
    {
      id: 'profile',
      title: '个人资料',
      path: '/profile',
      icon: '👤',
      permission: 'view_own_profile'
    },
    {
      id: 'settings',
      title: '设置',
      path: '/settings',
      icon: '⚙️',
      permission: 'change_own_settings'
    }
  ];
  
  const menus = menuItems || defaultMenus;
  
  if (!menus) {
    return [];
  }
  
  let userPermissions: string[] = [];
  if (Array.isArray(userRole)) {
    userPermissions = userRole;
  } else if (typeof userRole === 'string') {
    userPermissions = getRolePermissions(userRole);
  }
  
  return menus.filter(item => {
    // 如果菜单项没有权限要求，默认可访问
    if (!item.permission) {
      return true;
    }
    
    // 支持多权限检查
    if (Array.isArray(item.permission)) {
      return hasAnyPermission(userPermissions, item.permission);
    }
    
    // 单权限检查
    return hasPermission(userPermissions, item.permission);
  }).map(item => {
    // 递归过滤子菜单
    if (item.children && item.children.length > 0) {
      return {
        ...item,
        children: getAccessibleMenus(userRole, item.children)
      };
    }
    return item;
  });
}

/**
 * 获取当前用户信息
 * @returns 用户信息对象
 */
export async function getCurrentUser(): Promise<User | null> {
  try {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    // 检查是否是HTML内容
    if (userStr.trim().startsWith('<!DOCTYPE') || userStr.trim().startsWith('<html')) {
      console.warn('检测到localStorage中存储的是HTML内容，清除无效数据');
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      return null;
    }
    
    const user = JSON.parse(userStr);
    // 验证用户对象的有效性
    if (user && typeof user === 'object' && !Array.isArray(user) && user.role) {
      return Promise.resolve(user);
    }
    
    console.warn('用户数据格式无效，清除数据');
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    return Promise.resolve(null);
  } catch (error) {
    console.error('解析用户信息失败:', error);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    return Promise.resolve(null);
  }
}

// 认证状态缓存
let authCache: AuthCache = {
  lastCheck: 0,
  result: null,
  syncing: false
};

// 缓存有效期（5分钟）
const AUTH_CACHE_DURATION = 5 * 60 * 1000;

/**
 * 检查用户是否已认证
 * @returns 是否已认证
 */
export async function isAuthenticated(): Promise<boolean> {
  const token = localStorage.getItem('token');
  const user = await getCurrentUser();
  
  // 如果前端有完整的登录信息，直接返回true
  if (token && user) {
    return true;
  }
  
  // 检查缓存是否有效
  const now = Date.now();
  if (authCache.lastCheck && (now - authCache.lastCheck) < AUTH_CACHE_DURATION && authCache.result !== null) {
    return authCache.result || false;
  }
  
  // 如果正在同步中，等待同步完成
  if (authCache.syncing) {
    // 等待最多3秒
    let waitTime = 0;
    while (authCache.syncing && waitTime < 3000) {
      await new Promise(resolve => setTimeout(resolve, 100));
      waitTime += 100;
    }
    return authCache.result ?? false;
  }
  
  // 开始同步后端状态
  authCache.syncing = true;
  try {
    console.log('前端无登录信息，尝试同步后端状态...');
    const syncResult = await authSync.syncAuthState();
    
    authCache.lastCheck = now;
    authCache.result = syncResult.success && syncResult.authenticated;
    
    if (authCache.result) {
      console.log('同步成功，用户已登录');
    } else {
      console.log('同步完成，用户未登录');
    }
    
    return authCache.result || false;
  } catch (error) {
    console.error('认证状态同步失败:', error);
    authCache.lastCheck = now;
    authCache.result = false;
    return false;
  } finally {
    authCache.syncing = false;
  }
}

/**
 * 获取用户角色显示名称
 * @param role - 角色代码
 * @returns 角色显示名称
 */
export function getRoleDisplayName(role: string): string {
  return ROLE_DISPLAY_NAMES[role] || role;
}

/**
 * 获取权限显示名称
 * @param permission - 权限代码
 * @returns 权限显示名称
 */
export function getPermissionDisplayName(permission: string): string {
  return PERMISSION_DISPLAY_NAMES[permission] || permission;
}

/**
 * 获取权限分类显示名称
 * @param category - 权限分类
 * @returns 分类显示名称
 */
export function getCategoryDisplayName(category: string): string {
  const categoryNames: Record<string, string> = {
    learning: '学习功能',
    content: '内容管理',
    social: '社交功能',
    management: '管理功能',
    system: '系统管理',
    advanced: '高级功能'
  };
  return categoryNames[category] || category;
}

/**
 * 权限检查装饰器（用于Vue组件方法）
 * @param permissions - 所需权限
 * @param mode - 权限检查模式: 'any' | 'all'
 * @returns 装饰器函数
 */
export function requirePermission(permissions: string | string[], mode: 'any' | 'all' = 'any') {
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function(...args: any[]) {
      const user = await getCurrentUser();
      if (!user) {
        console.warn('用户未登录');
        return;
      }
      
      const userPermissions = getRolePermissions(user.role);
      let hasRequiredPermission = false;
      
      if (Array.isArray(permissions)) {
        hasRequiredPermission = mode === 'all' 
          ? hasAllPermissions(userPermissions, permissions)
          : hasAnyPermission(userPermissions, permissions);
      } else {
        hasRequiredPermission = hasPermission(userPermissions, permissions);
      }
      
      if (!hasRequiredPermission) {
        console.warn(`权限不足: 需要 ${Array.isArray(permissions) ? permissions.join(', ') : permissions} 权限`);
        return;
      }
      
      return originalMethod.apply(this, args);
    };
    
    return descriptor;
  };
}

// 导出其他必要的函数和常量
export { getRolePermissions, PAGE_PERMISSIONS };
export const { permissionSyncManager } = permissionManager;

// 默认导出
export default {
  hasPermission,
  canAccessPage,
  getAccessibleMenus,
  getCurrentUser,
  isAuthenticated,
  getRoleDisplayName,
  requirePermission,
  getRolePermissions,
  PAGE_PERMISSIONS
};