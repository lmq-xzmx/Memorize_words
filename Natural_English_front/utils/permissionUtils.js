/**
 * 优化后的前端权限检查工具
 * 提供统一的权限检查接口，支持缓存和性能优化
 */

// 权限缓存
const permissionCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5分钟缓存

// 优化后的角色权限配置
const OPTIMIZED_ROLE_PERMISSIONS = {
  'admin': {
    menus: ['*'], // 管理员拥有所有权限
    learning_goals: ['view', 'create', 'edit', 'delete', 'manage_all'],
    learning_plans: ['view', 'create', 'edit', 'delete', 'manage_all']
  },
  'teaching_director': {
    menus: [
      'dashboard', 'teaching_management', 'learning_goals', 'learning_plans',
      'student_management', 'teacher_management', 'data_analysis', 'reports'
    ],
    learning_goals: ['view', 'create', 'edit', 'delete', 'manage_class'],
    learning_plans: ['view', 'create', 'edit', 'delete', 'manage_class']
  },
  'academic_director': {
    menus: [
      'dashboard', 'teaching_management', 'learning_goals', 'learning_plans',
      'curriculum_management', 'data_analysis', 'reports'
    ],
    learning_goals: ['view', 'create', 'edit', 'delete', 'manage_class'],
    learning_plans: ['view', 'create', 'edit', 'delete', 'manage_class']
  },
  'research_group_leader': {
    menus: [
      'dashboard', 'teaching_management', 'learning_goals', 'learning_plans',
      'research_management', 'data_analysis'
    ],
    learning_goals: ['view', 'create', 'edit', 'manage_group'],
    learning_plans: ['view', 'create', 'edit', 'manage_group']
  },
  'teacher': {
    menus: [
      'dashboard', 'teaching_management', 'learning_goals', 'learning_plans',
      'student_progress', 'my_classes'
    ],
    learning_goals: ['view', 'create', 'edit_own', 'manage_own'],
    learning_plans: ['view', 'create', 'edit_own', 'manage_own']
  },
  'parent': {
    menus: ['dashboard', 'child_progress', 'learning_goals', 'learning_plans'],
    learning_goals: ['view_child'],
    learning_plans: ['view_child']
  },
  'student': {
    menus: ['dashboard', 'my_learning', 'learning_goals', 'learning_plans'],
    learning_goals: ['view_own', 'create_personal'],
    learning_plans: ['view_own', 'create_personal']
  }
};

/**
 * 获取缓存键
 */
function getCacheKey(userId, resource, action, context = {}) {
  const contextStr = Object.keys(context).sort().map(k => `${k}:${context[k]}`).join(',');
  return `${userId}_${resource}_${action}_${contextStr}`;
}

/**
 * 检查缓存是否有效
 */
function isCacheValid(cacheEntry) {
  return cacheEntry && (Date.now() - cacheEntry.timestamp) < CACHE_DURATION;
}

/**
 * 设置权限缓存
 */
function setPermissionCache(key, result) {
  permissionCache.set(key, {
    result,
    timestamp: Date.now()
  });
}

/**
 * 获取权限缓存
 */
function getPermissionCache(key) {
  const cacheEntry = permissionCache.get(key);
  if (isCacheValid(cacheEntry)) {
    return cacheEntry.result;
  }
  permissionCache.delete(key);
  return null;
}

/**
 * 清理过期缓存
 */
function cleanExpiredCache() {
  const now = Date.now();
  for (const [key, entry] of permissionCache.entries()) {
    if (now - entry.timestamp >= CACHE_DURATION) {
      permissionCache.delete(key);
    }
  }
}

// 定期清理缓存
setInterval(cleanExpiredCache, 60000); // 每分钟清理一次

/**
 * 优化后的权限检查类
 */
class PermissionChecker {
  constructor(user) {
    this.user = user;
    this.userRole = user?.role || 'guest';
    this.userId = user?.id;
  }

  /**
   * 检查菜单访问权限
   */
  canAccessMenu(menuId) {
    const cacheKey = getCacheKey(this.userId, 'menu', menuId);
    const cached = getPermissionCache(cacheKey);
    if (cached !== null) {
      return cached;
    }

    const rolePermissions = OPTIMIZED_ROLE_PERMISSIONS[this.userRole];
    if (!rolePermissions) {
      setPermissionCache(cacheKey, false);
      return false;
    }

    const hasAccess = rolePermissions.menus.includes('*') || 
                     rolePermissions.menus.includes(menuId);
    
    setPermissionCache(cacheKey, hasAccess);
    return hasAccess;
  }

  /**
   * 检查学习目标权限
   */
  hasLearningGoalPermission(action, context = {}) {
    const cacheKey = getCacheKey(this.userId, 'learning_goal', action, context);
    const cached = getPermissionCache(cacheKey);
    if (cached !== null) {
      return cached;
    }

    const rolePermissions = OPTIMIZED_ROLE_PERMISSIONS[this.userRole];
    if (!rolePermissions) {
      setPermissionCache(cacheKey, false);
      return false;
    }

    const permissions = rolePermissions.learning_goals;
    let hasPermission = false;

    switch (action) {
      case 'view':
        hasPermission = permissions.includes('view') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('view_own') && context.isOwn) ||
                       (permissions.includes('view_child') && context.isChild);
        break;
      
      case 'create':
        hasPermission = permissions.includes('create') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('create_personal') && context.isPersonal);
        break;
      
      case 'edit':
        hasPermission = permissions.includes('edit') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('edit_own') && context.isOwn) ||
                       (permissions.includes('manage_own') && context.isOwn) ||
                       (permissions.includes('manage_class') && context.isClassGoal) ||
                       (permissions.includes('manage_group') && context.isGroupGoal);
        break;
      
      case 'delete':
        hasPermission = permissions.includes('delete') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('manage_own') && context.isOwn) ||
                       (permissions.includes('manage_class') && context.isClassGoal) ||
                       (permissions.includes('manage_group') && context.isGroupGoal);
        break;
    }

    setPermissionCache(cacheKey, hasPermission);
    return hasPermission;
  }

  /**
   * 检查学习计划权限
   */
  hasLearningPlanPermission(action, context = {}) {
    const cacheKey = getCacheKey(this.userId, 'learning_plan', action, context);
    const cached = getPermissionCache(cacheKey);
    if (cached !== null) {
      return cached;
    }

    const rolePermissions = OPTIMIZED_ROLE_PERMISSIONS[this.userRole];
    if (!rolePermissions) {
      setPermissionCache(cacheKey, false);
      return false;
    }

    const permissions = rolePermissions.learning_plans;
    let hasPermission = false;

    switch (action) {
      case 'view':
        hasPermission = permissions.includes('view') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('view_own') && context.isOwn) ||
                       (permissions.includes('view_child') && context.isChild);
        break;
      
      case 'create':
        hasPermission = permissions.includes('create') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('create_personal') && context.isPersonal);
        break;
      
      case 'edit':
        hasPermission = permissions.includes('edit') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('edit_own') && context.isOwn) ||
                       (permissions.includes('manage_own') && context.isOwn) ||
                       (permissions.includes('manage_class') && context.isClassPlan) ||
                       (permissions.includes('manage_group') && context.isGroupPlan);
        break;
      
      case 'delete':
        hasPermission = permissions.includes('delete') || 
                       permissions.includes('manage_all') ||
                       (permissions.includes('manage_own') && context.isOwn) ||
                       (permissions.includes('manage_class') && context.isClassPlan) ||
                       (permissions.includes('manage_group') && context.isGroupPlan);
        break;
    }

    setPermissionCache(cacheKey, hasPermission);
    return hasPermission;
  }

  /**
   * 获取可访问的菜单列表
   */
  getAccessibleMenus() {
    const cacheKey = getCacheKey(this.userId, 'accessible_menus', 'all');
    const cached = getPermissionCache(cacheKey);
    if (cached !== null) {
      return cached;
    }

    const rolePermissions = OPTIMIZED_ROLE_PERMISSIONS[this.userRole];
    if (!rolePermissions) {
      setPermissionCache(cacheKey, []);
      return [];
    }

    const menus = rolePermissions.menus.includes('*') ? 
      Object.keys(OPTIMIZED_ROLE_PERMISSIONS.admin.menus) : 
      rolePermissions.menus;
    
    setPermissionCache(cacheKey, menus);
    return menus;
  }

  /**
   * 清除用户权限缓存
   */
  clearUserCache() {
    for (const key of permissionCache.keys()) {
      if (key.startsWith(`${this.userId}_`)) {
        permissionCache.delete(key);
      }
    }
  }
}

/**
 * 创建权限检查器实例
 */
export function createPermissionChecker(user) {
  return new PermissionChecker(user);
}

/**
 * 便捷的权限检查函数
 */
export function hasPermission(user, resource, action, context = {}) {
  const checker = new PermissionChecker(user);
  
  switch (resource) {
    case 'menu':
      return checker.canAccessMenu(action);
    case 'learning_goal':
      return checker.hasLearningGoalPermission(action, context);
    case 'learning_plan':
      return checker.hasLearningPlanPermission(action, context);
    default:
      return false;
  }
}

/**
 * 清除所有权限缓存
 */
export function clearAllPermissionCache() {
  permissionCache.clear();
}

/**
 * 获取缓存统计信息
 */
export function getCacheStats() {
  return {
    size: permissionCache.size,
    keys: Array.from(permissionCache.keys())
  };
}

export default {
  createPermissionChecker,
  hasPermission,
  clearAllPermissionCache,
  getCacheStats,
  PermissionChecker
};