/**
 * 菜单配置中心
 * 统一管理所有菜单配置，避免硬编码分散
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
  
  // 教学权限
  TEACHING: ['manage_teaching', 'view_student', 'change_student'],
  
  // 高级管理权限
  ADMIN: ['manage_users', 'manage_academic', 'manage_curriculum', 'manage_research']
}

// 角色权限继承配置
export const ROLE_PERMISSION_INHERITANCE = {
  'student': [...BASE_PERMISSIONS.BASIC, ...BASE_PERMISSIONS.LEARNING, ...BASE_PERMISSIONS.SOCIAL, 'change_own_profile'],
  'parent': [...BASE_PERMISSIONS.BASIC, 'view_student', 'view_own_children', 'view_child_progress', 'view_child_reports', 'communicate_with_teacher'],
  'teacher': [...BASE_PERMISSIONS.BASIC, ...BASE_PERMISSIONS.LEARNING, ...BASE_PERMISSIONS.SOCIAL, ...BASE_PERMISSIONS.MANAGEMENT, ...BASE_PERMISSIONS.TEACHING, 'access_dev_tools'],
  'research_leader': ['teacher', 'manage_research', 'manage_teaching_methods', 'view_research_reports'],
  'academic_director': ['research_leader', 'manage_curriculum', 'view_academic_reports'],
  'dean': ['academic_director', ...BASE_PERMISSIONS.ADMIN, 'view_reports'],
  'admin': ['*'] // 管理员拥有所有权限
}

// 菜单项配置
export const MENU_ITEMS = {
  // 主菜单
  MAIN_MENUS: [
    {
      id: 'dashboard',
      title: '仪表板',
      path: '/dashboard',
      icon: '📊',
      permission: 'view_dashboard',
      category: 'main',
      sortOrder: 1
    },
    {
      id: 'word-learning',
      title: '单词学习',
      path: '/word-learning',
      icon: '📚',
      permission: 'view_word_learning',
      category: 'learning',
      sortOrder: 2
    },
    {
      id: 'word-challenge',
      title: '单词挑战',
      path: '/word-challenge',
      icon: '🎯',
      permission: 'participate_challenge',
      category: 'learning',
      sortOrder: 3
    },
    {
      id: 'word-review',
      title: '单词复习',
      path: '/word-review',
      icon: '🔄',
      permission: 'review_words',
      category: 'learning',
      sortOrder: 4
    },
    {
      id: 'community',
      title: '学习社区',
      path: '/community',
      icon: '👥',
      permission: 'access_community',
      category: 'social',
      sortOrder: 5
    },
    {
      id: 'analytics',
      title: '数据分析',
      path: '/analytics',
      icon: '📈',
      permission: 'view_analytics',
      category: 'management',
      sortOrder: 6
    },
    {
      id: 'resource-auth',
      title: '资源管理',
      path: '/resource-auth',
      icon: '🔐',
      permission: 'manage_resource_auth',
      category: 'management',
      sortOrder: 7
    },
    {
      id: 'dev',
      title: '开发工具',
      path: '/dev',
      icon: '🛠️',
      permission: 'access_dev_tools',
      category: 'development',
      sortOrder: 8
    },
    {
      id: 'profile',
      title: '个人资料',
      path: '/profile',
      icon: '👤',
      permission: 'view_own_profile',
      category: 'user',
      sortOrder: 9
    },
    {
      id: 'settings',
      title: '设置',
      path: '/settings',
      icon: '⚙️',
      permission: 'change_own_settings',
      category: 'user',
      sortOrder: 10
    }
  ],
  
  // 底部导航菜单
  BOTTOM_MENUS: [
    {
      id: 'word-slash',
      title: '斩词',
      path: '/word-learning',
      icon: '⚔️',
      permission: 'view_word_learning',
      category: 'bottom'
    },
    {
      id: 'tools',
      title: '工具',
      icon: '🛠️',
      permission: 'access_dev_tools',
      category: 'bottom',
      isDropdown: true,
      children: 'TOOL_MENUS'
    },
    {
      id: 'fashion',
      title: '时尚',
      icon: '✨',
      permission: 'access_fashion_content',
      category: 'bottom',
      isDropdown: true,
      children: 'FASHION_MENUS'
    },
    {
      id: 'profile',
      title: '我的',
      path: '/profile',
      icon: '👤',
      permission: 'view_own_profile',
      category: 'bottom'
    }
  ],
  
  // 工具菜单
  TOOL_MENUS: [
    {
      id: 'dev-center',
      title: '开发中心',
      icon: '💻',
      permission: 'access_dev_tools',
      isExpandable: true,
      children: 'DEV_TOOLS'
    }
  ],
  
  // 开发工具
  DEV_TOOLS: [
    {
      id: 'api-test',
      title: 'API测试',
      path: '/test-api',
      icon: '🔧',
      permission: 'access_dev_tools',
      enabled: true
    },
    {
      id: 'position-test',
      title: '位置测试',
      path: '/position-test',
      icon: '📍',
      permission: 'access_dev_tools',
      enabled: false
    },
    {
      id: 'performance-monitor',
      title: '性能监控',
      path: '/performance',
      icon: '📊',
      permission: 'view_analytics',
      enabled: false
    }
  ],
  
  // 时尚菜单
  FASHION_MENUS: [
    {
      id: 'discover',
      title: '发现',
      path: '/discover',
      icon: '🔍',
      permission: 'discover_content'
    },
    {
      id: 'trends',
      title: '趋势',
      path: '/trends',
      icon: '📈',
      permission: 'access_fashion_content'
    },
    {
      id: 'community-fashion',
      title: '社区',
      path: '/community',
      icon: '👥',
      permission: 'access_community'
    }
  ]
}

// 页面权限映射
export const PAGE_PERMISSIONS = {
  '/': 'view_word_learning',
  '/dashboard': 'view_dashboard',
  '/profile': 'view_own_profile',
  '/settings': 'change_own_settings',
  '/help': 'view_help',
  '/learning-mode': 'view_word_learning',
  '/word-learning': 'view_word_learning',
  '/word-spelling': 'practice_spelling',
  '/word-flashcard': 'use_flashcard',
  '/word-reading': 'practice_reading',
  '/word-detail': 'view_word_detail',
  '/word-examples': 'view_word_examples',
  '/story-reading': 'practice_story_reading',
  '/listening': 'practice_listening',
  '/word-challenge': 'participate_challenge',
  '/word-selection': 'practice_word_selection',
  '/word-review': 'review_words',
  '/word-root-analysis': 'analyze_word_roots',
  '/pattern-memory': 'use_pattern_memory',
  '/community': 'access_community',
  '/fashion': 'access_fashion_content',
  '/dev': 'access_dev_tools',
  '/analytics': 'view_analytics',
  '/resource-auth': 'manage_resource_auth',
  '/subscription': 'manage_subscriptions',
  '/resource-sharing': 'share_resources'
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

// 缓存配置
export const CACHE_CONFIG = {
  MENU_CACHE_DURATION: 5 * 60 * 1000, // 5分钟
  PERMISSION_CACHE_DURATION: 10 * 60 * 1000, // 10分钟
  USER_CACHE_DURATION: 30 * 60 * 1000 // 30分钟
}

export default {
  ROLE_PERMISSION_INHERITANCE,
  MENU_ITEMS,
  PAGE_PERMISSIONS,
  ROLE_DISPLAY_NAMES,
  CACHE_CONFIG
}