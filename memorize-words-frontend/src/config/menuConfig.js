/**
 * 菜单配置中心
 * 统一管理所有菜单配置，避免硬编码分散
 * 参考废弃代码重新设计，支持多层级菜单和权限控制
 */

// 基础权限组定义
const BASE_PERMISSIONS = {
  // 基础权限
  BASIC: ['view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help'],
  
  // 学习权限
  LEARNING: [
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory'
  ],
  
  // 社交权限
  SOCIAL: ['access_community', 'access_fashion_content', 'discover_content'],
  
  // 管理权限
  MANAGEMENT: [
    'view_analytics', 'manage_resource_auth', 'manage_subscriptions', 'share_resources'
  ],
  
  // 开发权限
  DEVELOPMENT: ['access_dev_tools'],
  
  // 高级管理权限
  ADMIN: ['manage_users', 'manage_academic', 'manage_curriculum', 'manage_research']
}

// 角色权限继承配置
export const ROLE_PERMISSION_INHERITANCE = {
  'student': [...BASE_PERMISSIONS.BASIC, ...BASE_PERMISSIONS.LEARNING, ...BASE_PERMISSIONS.SOCIAL, 'change_own_profile'],
  'parent': [...BASE_PERMISSIONS.BASIC, 'view_student', 'view_own_children', 'view_child_progress'],
  'teacher': [...BASE_PERMISSIONS.BASIC, ...BASE_PERMISSIONS.LEARNING, ...BASE_PERMISSIONS.SOCIAL, ...BASE_PERMISSIONS.MANAGEMENT, ...BASE_PERMISSIONS.DEVELOPMENT],
  'admin': ['*'] // 管理员拥有所有权限
}

// Uni-App 菜单项配置
export const MENU_ITEMS = {
  // 🎯 主要底部导航菜单 (BOTTOM_MENUS)
  BOTTOM_MENUS: [
    {
      id: 'word-slash',
      title: '斩词',
      path: '/word-learning',
      icon: '⚔️',
      permission: 'view_word_learning',
      category: 'bottom',
      sortOrder: 1,
      description: '单词学习主入口'
    },
    {
      id: 'tools',
      title: '工具',
      icon: '🛠️',
      permission: 'access_dev_tools',
      category: 'bottom',
      isDropdown: true,
      children: 'TOOL_MENUS',
      sortOrder: 2,
      description: '下拉菜单，指向工具菜单'
    },
    {
      id: 'fashion',
      title: '时尚',
      icon: '✨',
      permission: 'access_fashion_content',
      category: 'bottom',
      isDropdown: true,
      children: 'FASHION_MENUS',
      sortOrder: 3,
      description: '下拉菜单，指向时尚菜单'
    },
    {
      id: 'profile',
      title: '我的',
      path: '/profile',
      icon: '👤',
      permission: 'view_own_profile',
      category: 'bottom',
      sortOrder: 4,
      description: '个人资料页面'
    }
  ],
  
  // 🔧 工具菜单 (TOOL_MENUS) - 一级目录
  TOOL_MENUS: [
    {
      id: 'dev-center',
      title: '开发中心',
      icon: '💻',
      permission: 'access_dev_tools',
      category: 'tool',
      isExpandable: true,
      children: 'DEV_TOOLS',
      description: '可展开菜单，包含开发工具'
    }
  ],

  // 🛠️ 开发工具子菜单 (DEV_TOOLS) - 二级目录
  DEV_TOOLS: [
    {
      id: 'api-test',
      title: 'API测试',
      path: '/pages/test-api/index',
      icon: '🔧',
      permission: 'access_dev_tools',
      enabled: true
    },
    {
      id: 'position-test',
      title: '位置测试',
      path: '/pages/position-test/index',
      icon: '📍',
      permission: 'access_dev_tools',
      enabled: false
    },
    {
      id: 'performance-monitor',
      title: '性能监控',
      path: '/pages/performance/index',
      icon: '📊',
      permission: 'view_analytics',
      enabled: false
    }
  ],

  // ✨ 时尚菜单 (FASHION_MENUS) - 一级目录
  FASHION_MENUS: [
    {
      id: 'discover',
      title: '发现',
      path: '/discover',
      icon: '🔍',
      permission: 'discover_content',
      category: 'fashion',
      description: '内容发现页面'
    },
    {
      id: 'trends',
      title: '趋势',
      path: '/trends',
      icon: '📈',
      permission: 'access_fashion_content',
      category: 'fashion',
      description: '趋势内容展示'
    },
    {
      id: 'community-fashion',
      title: '社区',
      path: '/community',
      icon: '👥',
      permission: 'access_community',
      category: 'fashion',
      description: '社区交流平台'
    }
  ]
}

// 页面权限映射
export const PAGE_PERMISSIONS = {
  '/': 'view_word_learning',
  '/word-learning': 'view_word_learning',
  '/pages/word-learning/index': 'view_word_learning',
  '/pages/challenge/index': 'participate_challenge',
  '/pages/review/index': 'review_words',
  '/pages/statistics/index': 'view_analytics',
  '/profile': 'view_own_profile',
  '/pages/profile/index': 'view_own_profile',
  '/pages/test-api/index': 'access_dev_tools',
  '/pages/position-test/index': 'access_dev_tools',
  '/pages/performance/index': 'view_analytics',
  '/discover': 'discover_content',
  '/pages/discover/index': 'discover_content',
  '/trends': 'access_fashion_content',
  '/pages/trends/index': 'access_fashion_content',
  '/community': 'access_community',
  '/pages/community/index': 'access_community'
}

// 角色显示名称
export const ROLE_DISPLAY_NAMES = {
  'admin': '管理员',
  'dean': '教导主任',
  'academic_director': '教务主任',
  'research_leader': '教研组长',
  'teacher': '自由老师',
  'parent': '家长',
  'student': '学生'
}

// Uni-App 平台配置
export const PLATFORM_CONFIG = {
  // H5平台配置
  'h5': {
    supportTabBar: true,
    supportSideMenu: true,
    supportPopup: true
  },
  // 微信小程序配置
  'mp-weixin': {
    supportTabBar: true,
    supportSideMenu: false,
    supportPopup: true,
    maxTabBarItems: 5
  },
  // APP配置
  'app': {
    supportTabBar: true,
    supportSideMenu: true,
    supportPopup: true,
    supportDrawer: true
  }
}

// 缓存配置
export const CACHE_CONFIG = {
  MENU_CACHE_DURATION: 5 * 60 * 1000, // 5分钟
  PERMISSION_CACHE_DURATION: 10 * 60 * 1000, // 10分钟
  USER_CACHE_DURATION: 30 * 60 * 1000 // 30分钟
}

// 权限检查函数
export function hasPermission(permission, userRole = 'student') {
  if (!permission) return true
  
  const rolePermissions = ROLE_PERMISSION_INHERITANCE[userRole] || []
  
  // 管理员拥有所有权限
  if (rolePermissions.includes('*')) return true
  
  return rolePermissions.includes(permission)
}

// 获取当前用户角色
export function getCurrentUserRole() {
  // 这里可以从本地存储或全局状态获取用户角色
  // 暂时返回默认角色
  return uni.getStorageSync('userRole') || 'student'
}

// 获取用户权限列表
export function getUserPermissions(userRole = 'student') {
  return ROLE_PERMISSION_INHERITANCE[userRole] || []
}

// 检查页面访问权限
export function checkPagePermission(path, userRole = 'student') {
  const requiredPermission = PAGE_PERMISSIONS[path]
  return hasPermission(requiredPermission, userRole)
}

export default {
  ROLE_PERMISSION_INHERITANCE,
  MENU_ITEMS,
  PAGE_PERMISSIONS,
  ROLE_DISPLAY_NAMES,
  PLATFORM_CONFIG,
  CACHE_CONFIG,
  hasPermission,
  getCurrentUserRole,
  getUserPermissions,
  checkPagePermission
}