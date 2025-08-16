/**
 * 优化后的前端权限检查工具
 * 基于用户权限管理系统规范实现
 * 提供高性能的权限验证和缓存机制
 */

import { ROLES } from './roleDefinitions.js'
import { ALL_PERMISSIONS } from './unifiedPermissionConstants.js'

// 权限缓存机制
const permissionCache = new Map()
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存
const MAX_CACHE_SIZE = 1000 // 最大缓存条目数

// 缓存统计信息
const cacheStats = {
  hits: 0,
  misses: 0,
  evictions: 0,
  totalChecks: 0
}

/**
 * 生成缓存键
 */
function getCacheKey(userId, resource, action, context = {}) {
  const contextStr = context ? JSON.stringify(context) : ''
  return `${userId}_${resource}_${action}_${contextStr}`
}

/**
 * 检查缓存是否有效
 */
function isCacheValid(cacheEntry) {
  return cacheEntry && (Date.now() - cacheEntry.timestamp) < CACHE_DURATION
}

/**
 * 设置权限缓存（带LRU淘汰策略）
 */
function setPermissionCache(key, result) {
  // 如果缓存已满，删除最旧的条目
  if (permissionCache.size >= MAX_CACHE_SIZE) {
    const firstKey = permissionCache.keys().next().value
    permissionCache.delete(firstKey)
    cacheStats.evictions++
  }
  
  permissionCache.set(key, {
    result,
    timestamp: Date.now(),
    accessCount: 1
  })
}

/**
 * 获取权限缓存
 */
function getPermissionCache(key) {
  const cacheEntry = permissionCache.get(key)
  if (isCacheValid(cacheEntry)) {
    cacheEntry.accessCount++
    cacheStats.hits++
    return cacheEntry.result
  }
  
  cacheStats.misses++
  return null
}

/**
 * 清理过期缓存
 */
function cleanExpiredCache() {
  const now = Date.now()
  for (const [key, entry] of permissionCache.entries()) {
    if (now - entry.timestamp >= CACHE_DURATION) {
      permissionCache.delete(key)
    }
  }
}

// 定期清理过期缓存
setInterval(cleanExpiredCache, CACHE_DURATION)

// 基于权限管理系统规范的角色权限配置
const OPTIMIZED_ROLE_PERMISSIONS = {
  'admin': {
    menus: ['*'], // 管理员拥有所有权限
    learning_goals: ['view', 'create', 'edit', 'delete', 'manage_all'],
    learning_plans: ['view', 'create', 'edit', 'delete', 'manage_all'],
    permissions: ['*'] // 所有权限
  },
  'dean': {
    menus: [
      'dashboard', 'word_learning', 'spelling_practice', 'flashcard_practice',
      'reading_practice', 'word_detail', 'word_examples', 'story_reading',
      'listening_practice', 'word_challenge', 'word_selection', 'word_review',
      'word_root_analysis', 'pattern_memory', 'community', 'fashion_content',
      'discover_content', 'dev_tools', 'analytics', 'resource_management',
      'subscription_management', 'resource_sharing', 'academic_management',
      'teaching_management', 'reports', 'user_management'
    ],
    learning_goals: ['view', 'create', 'edit', 'delete', 'manage_all'],
    learning_plans: ['view', 'create', 'edit', 'delete', 'manage_all'],
    permissions: [
      'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
      'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
      'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
      'participate_challenge', 'practice_word_selection', 'review_words',
      'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
      'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
      'manage_subscriptions', 'share_resources', 'manage_academic', 'manage_teaching',
      'view_reports', 'manage_users'
    ]
  },
  'academic_director': {
    menus: [
      'dashboard', 'word_learning', 'spelling_practice', 'flashcard_practice',
      'reading_practice', 'word_detail', 'word_examples', 'story_reading',
      'listening_practice', 'word_challenge', 'word_selection', 'word_review',
      'word_root_analysis', 'pattern_memory', 'community', 'fashion_content',
      'discover_content', 'dev_tools', 'analytics', 'resource_management',
      'subscription_management', 'resource_sharing', 'curriculum_management',
      'teaching_management', 'academic_reports'
    ],
    learning_goals: ['view', 'create', 'edit', 'delete', 'manage_class'],
    learning_plans: ['view', 'create', 'edit', 'delete', 'manage_class'],
    permissions: [
      'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
      'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
      'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
      'participate_challenge', 'practice_word_selection', 'review_words',
      'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
      'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
      'manage_subscriptions', 'share_resources', 'manage_curriculum', 'manage_teaching',
      'view_academic_reports'
    ]
  },
  'research_leader': {
    menus: [
      'dashboard', 'word_learning', 'spelling_practice', 'flashcard_practice',
      'reading_practice', 'word_detail', 'word_examples', 'story_reading',
      'listening_practice', 'word_challenge', 'word_selection', 'word_review',
      'word_root_analysis', 'pattern_memory', 'community', 'fashion_content',
      'discover_content', 'dev_tools', 'analytics', 'resource_management',
      'subscription_management', 'resource_sharing', 'research_management',
      'teaching_methods', 'research_reports'
    ],
    learning_goals: ['view', 'create', 'edit', 'manage_group'],
    learning_plans: ['view', 'create', 'edit', 'manage_group'],
    permissions: [
      'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
      'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
      'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
      'participate_challenge', 'practice_word_selection', 'review_words',
      'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
      'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
      'manage_subscriptions', 'share_resources', 'manage_research', 'manage_teaching_methods',
      'view_research_reports'
    ]
  },
  'teacher': {
    menus: [
      'dashboard', 'word_learning', 'spelling_practice', 'flashcard_practice',
      'reading_practice', 'word_detail', 'word_examples', 'story_reading',
      'listening_practice', 'word_challenge', 'word_selection', 'word_review',
      'word_root_analysis', 'pattern_memory', 'community', 'fashion_content',
      'discover_content', 'dev_tools', 'analytics', 'resource_management',
      'subscription_management', 'resource_sharing', 'teaching_management',
      'student_management'
    ],
    learning_goals: ['view', 'create', 'edit_own', 'manage_own'],
    learning_plans: ['view', 'create', 'edit_own', 'manage_own'],
    permissions: [
      'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
      'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
      'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
      'participate_challenge', 'practice_word_selection', 'review_words',
      'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
      'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
      'manage_subscriptions', 'share_resources', 'manage_teaching', 'view_student',
      'change_student'
    ]
  },
  'parent': {
    menus: ['dashboard', 'child_progress', 'child_reports', 'teacher_communication'],
    learning_goals: ['view_child'],
    learning_plans: ['view_child'],
    permissions: [
      'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
      'view_student', 'view_own_children', 'view_child_progress', 'view_child_reports',
      'communicate_with_teacher'
    ]
  },
  'student': {
    menus: [
      'dashboard', 'word_learning', 'spelling_practice', 'flashcard_practice',
      'reading_practice', 'word_detail', 'word_examples', 'story_reading',
      'listening_practice', 'word_challenge', 'word_selection', 'word_review',
      'word_root_analysis', 'pattern_memory', 'community', 'fashion_content',
      'discover_content', 'my_learning', 'personal_goals', 'personal_plans'
    ],
    learning_goals: ['view_own', 'create_personal'],
    learning_plans: ['view_own', 'create_personal'],
    permissions: [
      'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
      'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
      'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
      'participate_challenge', 'practice_word_selection', 'review_words',
      'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
      'discover_content', 'change_own_profile'
    ]
  }
}

/**
 * 优化后的权限检查类
 * 基于用户权限管理系统规范实现
 */
class PermissionChecker {
  constructor(user) {
    this.user = user;
    this.userRole = user?.role || 'guest';
    this.userId = user?.id;
    this.userCache = new Map();
  }

  /**
   * 检查用户是否拥有指定权限
   * @param {string} resource 资源类型
   * @param {string} action 操作类型
   * @param {object} context 上下文信息
   * @returns {boolean}
   */
  hasPermission(resource, action, context = {}) {
    if (!this.user || !this.user.role) {
      return false;
    }

    cacheStats.totalChecks++;
    const cacheKey = getCacheKey(this.userId, resource, action, context);
    
    // 检查缓存
    const cachedResult = getPermissionCache(cacheKey);
    if (cachedResult !== null) {
      return cachedResult;
    }

    // 执行权限检查逻辑
    const result = this._checkPermission(resource, action, context);
    
    // 缓存结果
    setPermissionCache(cacheKey, result);
    
    return result;
  }

  /**
   * 内部权限检查逻辑
   * @private
   */
  _checkPermission(resource, action, context) {
    const userRole = this.user.role;
    const rolePermissions = OPTIMIZED_ROLE_PERMISSIONS[userRole];
    
    if (!rolePermissions) {
      return false;
    }

    // 管理员拥有所有权限
    if (rolePermissions.permissions && rolePermissions.permissions.includes('*')) {
      return true;
    }

    // 检查具体权限
    switch (resource) {
      case 'menu':
        return this._checkMenuPermission(action, rolePermissions, context);
      case 'learning_goal':
        return this._checkLearningGoalPermission(action, rolePermissions, context);
      case 'learning_plan':
        return this._checkLearningPlanPermission(action, rolePermissions, context);
      case 'permission':
        return this._checkBasicPermission(action, rolePermissions, context);
      default:
        return false;
    }
  }

  /**
   * 检查基础权限
   * @private
   */
  _checkBasicPermission(permission, rolePermissions, context) {
    return rolePermissions.permissions && 
           (rolePermissions.permissions.includes('*') || 
            rolePermissions.permissions.includes(permission));
  }

  /**
   * 检查菜单权限
   * @private
   */
  _checkMenuPermission(menuId, rolePermissions, context) {
    return rolePermissions.menus.includes(menuId) || rolePermissions.menus.includes('*');
  }

  /**
   * 检查学习目标权限
   * @private
   */
  _checkLearningGoalPermission(action, rolePermissions, context) {
    const permissions = rolePermissions.learning_goals || [];
    
    // 检查基本权限
    if (permissions.includes(action)) {
      return true;
    }

    // 检查上下文相关权限
    if (context.goalId && context.ownerId) {
      // 检查是否是自己的目标
      if (context.ownerId === this.user.id && permissions.includes('manage_own')) {
        return true;
      }
      
      // 检查是否是同班级的目标
      if (context.classId === this.user.classId && permissions.includes('manage_class')) {
        return true;
      }
      
      // 检查是否是同组的目标
      if (context.groupId === this.user.groupId && permissions.includes('manage_group')) {
        return true;
      }
    }

    return false;
  }

  /**
   * 检查学习计划权限
   * @private
   */
  _checkLearningPlanPermission(action, rolePermissions, context) {
    const permissions = rolePermissions.learning_plans || [];
    
    // 检查基本权限
    if (permissions.includes(action)) {
      return true;
    }

    // 检查上下文相关权限
    if (context.planId && context.ownerId) {
      // 检查是否是自己的计划
      if (context.ownerId === this.user.id && permissions.includes('manage_own')) {
        return true;
      }
      
      // 检查是否是同班级的计划
      if (context.classId === this.user.classId && permissions.includes('manage_class')) {
        return true;
      }
      
      // 检查是否是同组的计划
      if (context.groupId === this.user.groupId && permissions.includes('manage_group')) {
        return true;
      }
    }

    return false;
  }

  /**
   * 检查菜单访问权限
   */
  canAccessMenu(menuId) {
    return this.hasPermission('menu', menuId);
  }

  /**
   * 检查学习目标权限
   */
  hasLearningGoalPermission(action, context = {}) {
    return this.hasPermission('learning_goal', action, context);
  }

  /**
   * 检查学习计划权限
   */
  hasLearningPlanPermission(action, context = {}) {
    return this.hasPermission('learning_plan', action, context);
  }

  /**
   * 检查基础权限
   * @param {string} permission 权限名称
   * @returns {boolean}
   */
  hasBasicPermission(permission) {
    return this.hasPermission('permission', permission);
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
function createPermissionChecker(user) {
  return new PermissionChecker(user);
}

/**
 * 便捷的权限检查函数
 */
function hasPermission(user, resource, action, context = {}) {
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
 * 清理所有权限缓存
 */
function clearAllPermissionCache() {
  permissionCache.clear()
}

/**
 * 获取缓存统计信息
 */
function getCacheStats() {
  return {
    ...cacheStats,
    size: permissionCache.size,
    hitRate: cacheStats.totalChecks > 0 ? (cacheStats.hits / cacheStats.totalChecks * 100).toFixed(2) + '%' : '0%',
    keys: Array.from(permissionCache.keys())
  };
}

export {
  OPTIMIZED_ROLE_PERMISSIONS,
  PermissionChecker,
  createPermissionChecker,
  hasPermission,
  clearAllPermissionCache,
  getCacheStats
}

export default {
  OPTIMIZED_ROLE_PERMISSIONS,
  createPermissionChecker,
  hasPermission,
  clearAllPermissionCache,
  getCacheStats,
  PermissionChecker
};