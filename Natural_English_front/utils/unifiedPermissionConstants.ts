/**
 * 统一权限常量文件
 * 整合所有权限相关的常量定义，避免重复和不一致
 * 根据《用户权限管理系统规范》文档统一管理
 */

// ==================== 类型定义 ====================
export interface PermissionCategories {
  LEARNING: string
  CONTENT: string
  SOCIAL: string
  MANAGEMENT: string
  SYSTEM: string
  ADVANCED: string
}

export interface LearningPermissions {
  WORD_LEARNING: string
  WORD_FLASHCARD: string
  WORD_SPELLING: string
  WORD_READING: string
  WORD_SELECTION: string
  STORY_READING: string
  LISTENING: string
  PATTERN_MEMORY: string
  WORD_ROOT_ANALYSIS: string
  WORD_EXAMPLES: string
  WORD_CHALLENGE: string
  WORD_REVIEW: string
  COMPETITION_MODE: string
  QUICK_BRUSH: string
  POSITION_TEST: string
  PROGRESS_TRACKING: string
}

export interface ContentPermissions {
  VIEW_CONTENT: string
  DOWNLOAD_CONTENT: string
  SHARE_CONTENT: string
  CREATE_CONTENT: string
  EDIT_CONTENT: string
  DELETE_CONTENT: string
  PUBLISH_CONTENT: string
  RESOURCE_AUTH: string
  RESOURCE_SHARING: string
  SUBSCRIPTION_MANAGEMENT: string
}

export interface SocialPermissions {
  VIEW_COMMUNITY: string
  POST_COMMUNITY: string
  COMMENT_COMMUNITY: string
  LIKE_COMMUNITY: string
  PEER_INTERACTION: string
  GROUP_STUDY: string
  TEACHER_STUDENT_INTERACTION: string
  VIEW_FASHION: string
  PARTICIPATE_FASHION: string
}

export interface ManagementPermissions {
  VIEW_USERS: string
  CREATE_USERS: string
  EDIT_USERS: string
  DELETE_USERS: string
  VIEW_ROLES: string
  ASSIGN_ROLES: string
  MODIFY_ROLES: string
  VIEW_PERMISSIONS: string
  ASSIGN_PERMISSIONS: string
  MODIFY_PERMISSIONS: string
  ACADEMIC_SUPERVISION: string
  RESEARCH_MANAGEMENT: string
  CURRICULUM_MANAGEMENT: string
}

export interface SystemPermissions {
  SYSTEM_CONFIG: string
  SYSTEM_MONITORING: string
  SYSTEM_BACKUP: string
  DATA_EXPORT: string
  DATA_IMPORT: string
  DATA_ANALYSIS: string
  SECURITY_CONFIG: string
  AUDIT_LOG: string
  ACCESS_CONTROL: string
}

export interface AdvancedPermissions {
  DEV_ACCESS: string
  API_ACCESS: string
  DEBUG_MODE: string
  ADVANCED_ANALYTICS: string
  CUSTOM_FEATURES: string
  EXPERIMENTAL_FEATURES: string
}

export interface Roles {
  STUDENT: string
  TEACHER: string
  PARENT: string
  ACADEMIC_DIRECTOR: string
  ACADEMIC_SUPERVISOR: string
  RESEARCH_LEADER: string
  RESEARCH_MANAGER: string
  DEAN: string
  ADMIN: string
}

export interface PagePermissionConfig {
  required: string[]
  category: string
  description: string
  requiresAuth?: boolean
}

export interface PagePermissions {
  [path: string]: PagePermissionConfig
}

export interface RoleHierarchy {
  [role: string]: number
}

export interface RoleInheritance {
  [role: string]: string[]
}

export interface PermissionDisplayNames {
  [permission: string]: string
}

export interface RoleDisplayNames {
  [role: string]: string
}

export interface PermissionCategoryMap {
  [category: string]: any
}

export interface LegacyPagePermissions {
  [path: string]: string
}

export interface LegacyRolePermissions {
  [role: string]: string[]
}

export interface AccessiblePage {
  path: string
  required: string[]
  category: string
  description: string
  requiresAuth?: boolean
}

// ==================== 权限分类枚举 ====================
export const PERMISSION_CATEGORIES: PermissionCategories = {
  LEARNING: 'learning',           // 学习权限
  CONTENT: 'content',            // 内容权限
  SOCIAL: 'social',              // 社交权限
  MANAGEMENT: 'management',      // 管理权限
  SYSTEM: 'system',              // 系统权限
  ADVANCED: 'advanced'           // 高级权限
}

// ==================== 学习权限 ====================
export const LEARNING_PERMISSIONS: LearningPermissions = {
  // 基础学习
  WORD_LEARNING: 'learning.word_learning',
  WORD_FLASHCARD: 'learning.word_flashcard',
  WORD_SPELLING: 'learning.word_spelling',
  WORD_READING: 'learning.word_reading',
  WORD_SELECTION: 'learning.word_selection',
  
  // 高级学习
  STORY_READING: 'learning.story_reading',
  LISTENING: 'learning.listening',
  PATTERN_MEMORY: 'learning.pattern_memory',
  WORD_ROOT_ANALYSIS: 'learning.word_root_analysis',
  WORD_EXAMPLES: 'learning.word_examples',
  
  // 练习模式
  WORD_CHALLENGE: 'learning.word_challenge',
  WORD_REVIEW: 'learning.word_review',
  COMPETITION_MODE: 'learning.competition_mode',
  QUICK_BRUSH: 'learning.quick_brush',
  
  // 测试评估
  POSITION_TEST: 'learning.position_test',
  PROGRESS_TRACKING: 'learning.progress_tracking'
}

// ==================== 内容权限 ====================
export const CONTENT_PERMISSIONS: ContentPermissions = {
  // 内容访问
  VIEW_CONTENT: 'content.view_content',
  DOWNLOAD_CONTENT: 'content.download_content',
  SHARE_CONTENT: 'content.share_content',
  
  // 内容管理
  CREATE_CONTENT: 'content.create_content',
  EDIT_CONTENT: 'content.edit_content',
  DELETE_CONTENT: 'content.delete_content',
  PUBLISH_CONTENT: 'content.publish_content',
  
  // 资源管理
  RESOURCE_AUTH: 'content.resource_auth',
  RESOURCE_SHARING: 'content.resource_sharing',
  SUBSCRIPTION_MANAGEMENT: 'content.subscription_management'
}

// ==================== 社交权限 ====================
export const SOCIAL_PERMISSIONS: SocialPermissions = {
  // 社区功能
  VIEW_COMMUNITY: 'social.view_community',
  POST_COMMUNITY: 'social.post_community',
  COMMENT_COMMUNITY: 'social.comment_community',
  LIKE_COMMUNITY: 'social.like_community',
  
  // 互动功能
  PEER_INTERACTION: 'social.peer_interaction',
  GROUP_STUDY: 'social.group_study',
  TEACHER_STUDENT_INTERACTION: 'social.teacher_student_interaction',
  
  // 时尚功能
  VIEW_FASHION: 'social.view_fashion',
  PARTICIPATE_FASHION: 'social.participate_fashion'
}

// ==================== 管理权限 ====================
export const MANAGEMENT_PERMISSIONS: ManagementPermissions = {
  // 用户管理
  VIEW_USERS: 'management.view_users',
  CREATE_USERS: 'management.create_users',
  EDIT_USERS: 'management.edit_users',
  DELETE_USERS: 'management.delete_users',
  
  // 角色管理
  VIEW_ROLES: 'management.view_roles',
  ASSIGN_ROLES: 'management.assign_roles',
  MODIFY_ROLES: 'management.modify_roles',
  
  // 权限管理
  VIEW_PERMISSIONS: 'management.view_permissions',
  ASSIGN_PERMISSIONS: 'management.assign_permissions',
  MODIFY_PERMISSIONS: 'management.modify_permissions',
  
  // 学术管理
  ACADEMIC_SUPERVISION: 'management.academic_supervision',
  RESEARCH_MANAGEMENT: 'management.research_management',
  CURRICULUM_MANAGEMENT: 'management.curriculum_management'
}

// ==================== 系统权限 ====================
export const SYSTEM_PERMISSIONS: SystemPermissions = {
  // 系统配置
  SYSTEM_CONFIG: 'system.system_config',
  SYSTEM_MONITORING: 'system.system_monitoring',
  SYSTEM_BACKUP: 'system.system_backup',
  
  // 数据管理
  DATA_EXPORT: 'system.data_export',
  DATA_IMPORT: 'system.data_import',
  DATA_ANALYSIS: 'system.data_analysis',
  
  // 安全管理
  SECURITY_CONFIG: 'system.security_config',
  AUDIT_LOG: 'system.audit_log',
  ACCESS_CONTROL: 'system.access_control'
}

// ==================== 高级权限 ====================
export const ADVANCED_PERMISSIONS: AdvancedPermissions = {
  // 开发权限
  DEV_ACCESS: 'advanced.dev_access',
  API_ACCESS: 'advanced.api_access',
  DEBUG_MODE: 'advanced.debug_mode',
  
  // 高级功能
  ADVANCED_ANALYTICS: 'advanced.advanced_analytics',
  CUSTOM_FEATURES: 'advanced.custom_features',
  EXPERIMENTAL_FEATURES: 'advanced.experimental_features'
}

// ==================== 角色定义 ====================
export const ROLES: Roles = {
  STUDENT: 'student',                    // 学生
  TEACHER: 'teacher',                    // 自由老师
  PARENT: 'parent',                      // 家长
  ACADEMIC_DIRECTOR: 'academic_director', // 教务主任
  ACADEMIC_SUPERVISOR: 'academic_supervisor', // 学术监督
  RESEARCH_LEADER: 'research_leader',    // 教研组长
  RESEARCH_MANAGER: 'research_manager',  // 研究管理员
  DEAN: 'dean',                         // 教导主任
  ADMIN: 'admin'                        // 管理员
}

// ==================== 角色显示名称 ====================
export const ROLE_DISPLAY_NAMES: RoleDisplayNames = {
  [ROLES.STUDENT]: '学生',
  [ROLES.TEACHER]: '自由老师',
  [ROLES.PARENT]: '家长',
  [ROLES.ACADEMIC_DIRECTOR]: '教务主任',
  [ROLES.ACADEMIC_SUPERVISOR]: '学术监督',
  [ROLES.RESEARCH_LEADER]: '教研组长',
  [ROLES.RESEARCH_MANAGER]: '研究管理员',
  [ROLES.DEAN]: '教导主任',
  [ROLES.ADMIN]: '管理员'
}

// ==================== 角色层级 ====================
export const ROLE_HIERARCHY: RoleHierarchy = {
  [ROLES.STUDENT]: 1,
  [ROLES.PARENT]: 1,
  [ROLES.TEACHER]: 2,
  [ROLES.ACADEMIC_DIRECTOR]: 3,
  [ROLES.ACADEMIC_SUPERVISOR]: 3,
  [ROLES.RESEARCH_LEADER]: 4,
  [ROLES.RESEARCH_MANAGER]: 4,
  [ROLES.DEAN]: 5,
  [ROLES.ADMIN]: 6
}

// ==================== 角色继承关系 ====================
export const ROLE_INHERITANCE: RoleInheritance = {
  [ROLES.TEACHER]: [ROLES.STUDENT],
  [ROLES.ACADEMIC_DIRECTOR]: [ROLES.TEACHER],
  [ROLES.ACADEMIC_SUPERVISOR]: [ROLES.TEACHER],
  [ROLES.RESEARCH_LEADER]: [ROLES.TEACHER],
  [ROLES.RESEARCH_MANAGER]: [ROLES.TEACHER],
  [ROLES.DEAN]: [ROLES.ACADEMIC_DIRECTOR, ROLES.RESEARCH_LEADER],
  [ROLES.ADMIN]: [ROLES.DEAN]
}

// ==================== 所有权限集合 ====================
export const ALL_PERMISSIONS = {
  ...LEARNING_PERMISSIONS,
  ...CONTENT_PERMISSIONS,
  ...SOCIAL_PERMISSIONS,
  ...MANAGEMENT_PERMISSIONS,
  ...SYSTEM_PERMISSIONS,
  ...ADVANCED_PERMISSIONS
}

// ==================== 权限分类映射 ====================
export const PERMISSION_CATEGORY_MAP: PermissionCategoryMap = {
  [PERMISSION_CATEGORIES.LEARNING]: LEARNING_PERMISSIONS,
  [PERMISSION_CATEGORIES.CONTENT]: CONTENT_PERMISSIONS,
  [PERMISSION_CATEGORIES.SOCIAL]: SOCIAL_PERMISSIONS,
  [PERMISSION_CATEGORIES.MANAGEMENT]: MANAGEMENT_PERMISSIONS,
  [PERMISSION_CATEGORIES.SYSTEM]: SYSTEM_PERMISSIONS,
  [PERMISSION_CATEGORIES.ADVANCED]: ADVANCED_PERMISSIONS
}

// ==================== 权限显示名称映射 ====================
export const PERMISSION_DISPLAY_NAMES: PermissionDisplayNames = {
  // 学习权限
  [LEARNING_PERMISSIONS.WORD_LEARNING]: '单词学习',
  [LEARNING_PERMISSIONS.WORD_FLASHCARD]: '闪卡学习',
  [LEARNING_PERMISSIONS.WORD_SPELLING]: '拼写练习',
  [LEARNING_PERMISSIONS.WORD_READING]: '单词阅读',
  [LEARNING_PERMISSIONS.WORD_SELECTION]: '单词选择',
  [LEARNING_PERMISSIONS.STORY_READING]: '故事阅读',
  [LEARNING_PERMISSIONS.LISTENING]: '听力练习',
  [LEARNING_PERMISSIONS.PATTERN_MEMORY]: '模式记忆',
  [LEARNING_PERMISSIONS.WORD_ROOT_ANALYSIS]: '词根分析',
  [LEARNING_PERMISSIONS.WORD_EXAMPLES]: '单词例句',
  [LEARNING_PERMISSIONS.WORD_CHALLENGE]: '单词挑战',
  [LEARNING_PERMISSIONS.WORD_REVIEW]: '单词复习',
  [LEARNING_PERMISSIONS.COMPETITION_MODE]: '竞技模式',
  [LEARNING_PERMISSIONS.QUICK_BRUSH]: '快刷模式',
  [LEARNING_PERMISSIONS.POSITION_TEST]: '位置测试',
  [LEARNING_PERMISSIONS.PROGRESS_TRACKING]: '进度跟踪',
  
  // 内容权限
  [CONTENT_PERMISSIONS.VIEW_CONTENT]: '查看内容',
  [CONTENT_PERMISSIONS.DOWNLOAD_CONTENT]: '下载内容',
  [CONTENT_PERMISSIONS.SHARE_CONTENT]: '分享内容',
  [CONTENT_PERMISSIONS.CREATE_CONTENT]: '创建内容',
  [CONTENT_PERMISSIONS.EDIT_CONTENT]: '编辑内容',
  [CONTENT_PERMISSIONS.DELETE_CONTENT]: '删除内容',
  [CONTENT_PERMISSIONS.PUBLISH_CONTENT]: '发布内容',
  [CONTENT_PERMISSIONS.RESOURCE_AUTH]: '资源授权',
  [CONTENT_PERMISSIONS.RESOURCE_SHARING]: '资源共享',
  [CONTENT_PERMISSIONS.SUBSCRIPTION_MANAGEMENT]: '订阅管理',
  
  // 社交权限
  [SOCIAL_PERMISSIONS.VIEW_COMMUNITY]: '查看社区',
  [SOCIAL_PERMISSIONS.POST_COMMUNITY]: '发布社区内容',
  [SOCIAL_PERMISSIONS.COMMENT_COMMUNITY]: '评论社区',
  [SOCIAL_PERMISSIONS.LIKE_COMMUNITY]: '点赞社区',
  [SOCIAL_PERMISSIONS.PEER_INTERACTION]: '同伴互动',
  [SOCIAL_PERMISSIONS.GROUP_STUDY]: '小组学习',
  [SOCIAL_PERMISSIONS.TEACHER_STUDENT_INTERACTION]: '师生互动',
  [SOCIAL_PERMISSIONS.VIEW_FASHION]: '查看时尚',
  [SOCIAL_PERMISSIONS.PARTICIPATE_FASHION]: '参与时尚',
  
  // 管理权限
  [MANAGEMENT_PERMISSIONS.VIEW_USERS]: '查看用户',
  [MANAGEMENT_PERMISSIONS.CREATE_USERS]: '创建用户',
  [MANAGEMENT_PERMISSIONS.EDIT_USERS]: '编辑用户',
  [MANAGEMENT_PERMISSIONS.DELETE_USERS]: '删除用户',
  [MANAGEMENT_PERMISSIONS.VIEW_ROLES]: '查看角色',
  [MANAGEMENT_PERMISSIONS.ASSIGN_ROLES]: '分配角色',
  [MANAGEMENT_PERMISSIONS.MODIFY_ROLES]: '修改角色',
  [MANAGEMENT_PERMISSIONS.VIEW_PERMISSIONS]: '查看权限',
  [MANAGEMENT_PERMISSIONS.ASSIGN_PERMISSIONS]: '分配权限',
  [MANAGEMENT_PERMISSIONS.MODIFY_PERMISSIONS]: '修改权限',
  [MANAGEMENT_PERMISSIONS.ACADEMIC_SUPERVISION]: '学术监督',
  [MANAGEMENT_PERMISSIONS.RESEARCH_MANAGEMENT]: '研究管理',
  [MANAGEMENT_PERMISSIONS.CURRICULUM_MANAGEMENT]: '课程管理',
  
  // 系统权限
  [SYSTEM_PERMISSIONS.SYSTEM_CONFIG]: '系统配置',
  [SYSTEM_PERMISSIONS.SYSTEM_MONITORING]: '系统监控',
  [SYSTEM_PERMISSIONS.SYSTEM_BACKUP]: '系统备份',
  [SYSTEM_PERMISSIONS.DATA_EXPORT]: '数据导出',
  [SYSTEM_PERMISSIONS.DATA_IMPORT]: '数据导入',
  [SYSTEM_PERMISSIONS.DATA_ANALYSIS]: '数据分析',
  [SYSTEM_PERMISSIONS.SECURITY_CONFIG]: '安全配置',
  [SYSTEM_PERMISSIONS.AUDIT_LOG]: '审计日志',
  [SYSTEM_PERMISSIONS.ACCESS_CONTROL]: '访问控制',
  
  // 高级权限
  [ADVANCED_PERMISSIONS.DEV_ACCESS]: '开发访问',
  [ADVANCED_PERMISSIONS.API_ACCESS]: 'API访问',
  [ADVANCED_PERMISSIONS.DEBUG_MODE]: '调试模式',
  [ADVANCED_PERMISSIONS.ADVANCED_ANALYTICS]: '高级分析',
  [ADVANCED_PERMISSIONS.CUSTOM_FEATURES]: '自定义功能',
  [ADVANCED_PERMISSIONS.EXPERIMENTAL_FEATURES]: '实验性功能'
}

// ==================== 权限分类显示名称 ====================
export const PERMISSION_CATEGORY_DISPLAY_NAMES: PermissionDisplayNames = {
  [PERMISSION_CATEGORIES.LEARNING]: '学习权限',
  [PERMISSION_CATEGORIES.CONTENT]: '内容权限',
  [PERMISSION_CATEGORIES.SOCIAL]: '社交权限',
  [PERMISSION_CATEGORIES.MANAGEMENT]: '管理权限',
  [PERMISSION_CATEGORIES.SYSTEM]: '系统权限',
  [PERMISSION_CATEGORIES.ADVANCED]: '高级权限'
}

// ==================== 页面权限映射 ====================
export const PAGE_PERMISSIONS: PagePermissions = {
  // 基础页面
  '/': {
    required: [],
    category: 'public',
    description: '首页'
  },
  '/login': {
    required: [],
    category: 'auth',
    description: '登录页面'
  },
  '/register': {
    required: [],
    category: 'auth',
    description: '注册页面'
  },
  '/dashboard': {
    required: [],
    category: 'user',
    description: '用户仪表板',
    requiresAuth: true
  },
  '/profile': {
    required: [],
    category: 'user',
    description: '个人资料',
    requiresAuth: true
  },
  '/settings': {
    required: [],
    category: 'user',
    description: '设置页面',
    requiresAuth: true
  },
  
  // 学习模式页面
  '/word-learning': {
    required: [LEARNING_PERMISSIONS.WORD_LEARNING],
    category: 'learning',
    description: '单词学习基础功能'
  },
  '/word-flashcard': {
    required: [LEARNING_PERMISSIONS.WORD_FLASHCARD],
    category: 'learning',
    description: '闪卡学习模式'
  },
  '/word-spelling': {
    required: [LEARNING_PERMISSIONS.WORD_SPELLING],
    category: 'learning',
    description: '拼写练习模式'
  },
  '/word-reading': {
    required: [LEARNING_PERMISSIONS.WORD_READING],
    category: 'learning',
    description: '单词阅读模式'
  },
  '/word-selection': {
    required: [LEARNING_PERMISSIONS.WORD_SELECTION],
    category: 'learning',
    description: '单词选择练习'
  },
  '/story-reading': {
    required: [LEARNING_PERMISSIONS.STORY_READING],
    category: 'learning',
    description: '故事阅读模式'
  },
  '/listening': {
    required: [LEARNING_PERMISSIONS.LISTENING],
    category: 'learning',
    description: '听力练习模式'
  },
  '/pattern-memory': {
    required: [LEARNING_PERMISSIONS.PATTERN_MEMORY],
    category: 'learning',
    description: '模式记忆练习'
  },
  '/word-root-analysis': {
    required: [LEARNING_PERMISSIONS.WORD_ROOT_ANALYSIS],
    category: 'learning',
    description: '词根分析学习'
  },
  '/word-examples': {
    required: [LEARNING_PERMISSIONS.WORD_EXAMPLES],
    category: 'learning',
    description: '单词例句学习'
  },
  '/word-challenge': {
    required: [LEARNING_PERMISSIONS.WORD_CHALLENGE],
    category: 'learning',
    description: '单词挑战模式'
  },
  '/word-review': {
    required: [LEARNING_PERMISSIONS.WORD_REVIEW],
    category: 'learning',
    description: '单词复习模式'
  },
  '/competition': {
    required: [LEARNING_PERMISSIONS.COMPETITION_MODE],
    category: 'learning',
    description: '竞技模式'
  },
  '/quick-brush': {
    required: [LEARNING_PERMISSIONS.QUICK_BRUSH],
    category: 'learning',
    description: '快刷模式'
  },
  '/position-test': {
    required: [LEARNING_PERMISSIONS.POSITION_TEST],
    category: 'assessment',
    description: '位置测试'
  },
  
  // 内容相关页面
  '/discover': {
    required: [CONTENT_PERMISSIONS.VIEW_CONTENT],
    category: 'content',
    description: '发现页面'
  },
  '/resource-auth': {
    required: [CONTENT_PERMISSIONS.RESOURCE_AUTH],
    category: 'content',
    description: '资源授权'
  },
  '/resource-sharing': {
    required: [CONTENT_PERMISSIONS.RESOURCE_SHARING],
    category: 'content',
    description: '资源共享'
  },
  '/subscription': {
    required: [CONTENT_PERMISSIONS.SUBSCRIPTION_MANAGEMENT],
    category: 'content',
    description: '订阅管理'
  },
  
  // 社交功能页面
  '/community': {
    required: [SOCIAL_PERMISSIONS.VIEW_COMMUNITY],
    category: 'social',
    description: '社区页面'
  },
  '/fashion': {
    required: [SOCIAL_PERMISSIONS.VIEW_FASHION],
    category: 'social',
    description: '时尚页面'
  },
  
  // 开发和测试页面
  '/dev-index': {
    required: [],
    category: 'development',
    description: '开发中心'
  },
  '/admin/dev-index': {
    required: [],
    category: 'development',
    description: '管理员开发中心',
    requiresAuth: true
  },
  '/test-api': {
    required: [],
    category: 'development',
    description: 'API测试'
  }
}

// ==================== 旧版权限映射（兼容性） ====================
export const LEGACY_PAGE_PERMISSIONS: LegacyPagePermissions = {
  '/': 'view_word_learning',
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
  '/word-review': 'review_words',
  '/word-root-analysis': 'analyze_word_roots',
  '/pattern-memory': 'use_pattern_memory',
  '/community': 'access_community',
  '/fashion': 'access_fashion_content',
  '/dev-index': 'access_dev_tools',
  '/analytics': 'view_analytics',
  '/resource-auth': 'manage_resource_auth',
  '/subscription-management': 'manage_subscriptions',
  '/resource-sharing': 'share_resources',
  '/discover': 'discover_content'
}

// ==================== 角色权限映射（旧版兼容） ====================
export const LEGACY_ROLE_PERMISSIONS: LegacyRolePermissions = {
  'admin': ['*'], // 管理员拥有所有权限
  'dean': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_academic', 'manage_teaching',
    'view_reports', 'manage_users'
  ],
  'academic_director': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_curriculum', 'manage_teaching',
    'view_academic_reports'
  ],
  'research_leader': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_research', 'manage_teaching_methods',
    'view_research_reports'
  ],
  'teacher': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'access_dev_tools', 'view_analytics', 'manage_resource_auth',
    'manage_subscriptions', 'share_resources', 'manage_teaching', 'view_student',
    'change_student'
  ],
  'parent': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_student', 'view_own_children', 'view_child_progress', 'view_child_reports',
    'communicate_with_teacher'
  ],
  'student': [
    'view_dashboard', 'view_own_profile', 'change_own_settings', 'view_help',
    'view_word_learning', 'practice_spelling', 'use_flashcard', 'practice_reading',
    'view_word_detail', 'view_word_examples', 'practice_story_reading', 'practice_listening',
    'participate_challenge', 'practice_word_selection', 'review_words',
    'analyze_word_roots', 'use_pattern_memory', 'access_community', 'access_fashion_content',
    'discover_content', 'change_own_profile'
  ]
}

// ==================== 工具函数 ====================

/**
 * 检查用户是否可以访问指定页面
 * @param userPermissions - 用户权限列表
 * @param path - 页面路径
 * @returns 是否可以访问
 */
export function canAccessPage(userPermissions: string[], path: string): boolean {
  const pageConfig = PAGE_PERMISSIONS[path]
  
  if (!pageConfig) {
    // 如果页面未配置权限，默认允许访问
    return true
  }
  
  const requiredPermissions = pageConfig.required || []
  
  // 如果页面不需要特殊权限，允许访问
  if (requiredPermissions.length === 0) {
    return true
  }
  
  // 检查用户是否拥有所有必需权限
  return requiredPermissions.every(permission => 
    userPermissions.includes(permission)
  )
}

/**
 * 获取页面权限配置
 * @param path - 页面路径
 * @returns 权限配置
 */
export function getPagePermissionConfig(path: string): PagePermissionConfig | null {
  return PAGE_PERMISSIONS[path] || null
}

/**
 * 检查页面是否需要认证
 * @param path - 页面路径
 * @returns 是否需要认证
 */
export function pageRequiresAuth(path: string): boolean {
  const config = PAGE_PERMISSIONS[path]
  return config?.requiresAuth === true
}

/**
 * 获取用户可访问的学习模式页面
 * @param userPermissions - 用户权限列表
 * @returns 可访问的页面列表
 */
export function getAccessibleLearningModes(userPermissions: string[]): AccessiblePage[] {
  return Object.entries(PAGE_PERMISSIONS)
    .filter(([path, config]) => {
      return config.category === 'learning' && canAccessPage(userPermissions, path)
    })
    .map(([path, config]) => ({
      path,
      ...config
    }))
}

/**
 * 获取用户可访问的所有页面
 * @param userPermissions - 用户权限列表
 * @returns 可访问的页面配置列表
 */
export function getAllAccessiblePages(userPermissions: string[]): AccessiblePage[] {
  return Object.entries(PAGE_PERMISSIONS)
    .filter(([path, _config]) => canAccessPage(userPermissions, path))
    .map(([path, config]) => ({
      path,
      ...config
    }))
}

/**
 * 检查角色是否比另一个角色级别更高
 * @param role1 - 角色1
 * @param role2 - 角色2
 * @returns role1是否比role2级别更高
 */
export function isRoleHigher(role1: string, role2: string): boolean {
  return (ROLE_HIERARCHY[role1] || 0) > (ROLE_HIERARCHY[role2] || 0)
}

/**
 * 获取角色可以管理的其他角色
 * @param role - 当前角色
 * @returns 可管理的角色列表
 */
export function getManageableRoles(role: string): string[] {
  const currentLevel = ROLE_HIERARCHY[role] || 0
  return Object.keys(ROLE_HIERARCHY).filter(r => 
    ROLE_HIERARCHY[r] < currentLevel
  )
}

// ==================== 默认导出 ====================
export default {
  // 权限分类
  PERMISSION_CATEGORIES,
  PERMISSION_CATEGORY_DISPLAY_NAMES,
  
  // 权限定义
  LEARNING_PERMISSIONS,
  CONTENT_PERMISSIONS,
  SOCIAL_PERMISSIONS,
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS,
  ADVANCED_PERMISSIONS,
  ALL_PERMISSIONS,
  
  // 角色定义
  ROLES,
  ROLE_DISPLAY_NAMES,
  ROLE_HIERARCHY,
  ROLE_INHERITANCE,
  
  // 权限映射
  PERMISSION_CATEGORY_MAP,
  PERMISSION_DISPLAY_NAMES,
  PAGE_PERMISSIONS,
  
  // 兼容性
  LEGACY_PAGE_PERMISSIONS,
  LEGACY_ROLE_PERMISSIONS,
  
  // 工具函数
  canAccessPage,
  getPagePermissionConfig,
  pageRequiresAuth,
  getAccessibleLearningModes,
  getAllAccessiblePages,
  isRoleHigher,
  getManageableRoles
}