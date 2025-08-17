/**
 * 学习模式权限映射
 * 根据《用户权限管理系统规范》文档定义的学习模式与权限对应关系
 */

import { LEARNING_PERMISSIONS, CONTENT_PERMISSIONS, SOCIAL_PERMISSIONS } from './unifiedPermissionConstants';

// 页面权限配置接口
export interface PagePermissionConfig {
  required: string[];
  category: string;
  description: string;
  requiresAuth?: boolean;
}

// 权限分类类型
export type PermissionCategory = 
  | 'public'
  | 'auth'
  | 'user'
  | 'learning'
  | 'social_learning'
  | 'content'
  | 'social'
  | 'assessment'
  | 'development';

// 可访问页面信息接口
export interface AccessiblePageInfo extends PagePermissionConfig {
  path: string;
}

// 学习模式页面路径与权限映射
export const LEARNING_MODE_PERMISSIONS: Record<string, PagePermissionConfig> = {
  // 基础学习模式
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
  
  // 高级学习模式
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
    description: '模式记忆训练'
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
  
  // 挑战模式
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
  
  // 竞技模式
  '/word-selection-practice': {
    required: [LEARNING_PERMISSIONS.COMPETITION_MODE],
    category: 'learning',
    description: '竞技练习模式'
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
  
  // 社交学习模式
  '/word-selection-practice2': {
    required: [LEARNING_PERMISSIONS.WORD_SELECTION, SOCIAL_PERMISSIONS.TEACHER_STUDENT_INTERACTION],
    category: 'social_learning',
    description: '师生互动练习'
  },
  
  // 学习模式选择
  '/learning-mode': {
    required: [LEARNING_PERMISSIONS.WORD_LEARNING],
    category: 'learning',
    description: '学习模式选择器'
  },
  
  '/learning-modes': {
    required: [LEARNING_PERMISSIONS.WORD_LEARNING],
    category: 'learning',
    description: '学习模式列表'
  },
  
  // 组合学习模式
  '/word-learning/spelling': {
    required: [LEARNING_PERMISSIONS.WORD_LEARNING, LEARNING_PERMISSIONS.WORD_SPELLING],
    category: 'learning',
    description: '单词学习-拼写练习'
  },
  
  '/word-learning/flashcard': {
    required: [LEARNING_PERMISSIONS.WORD_LEARNING, LEARNING_PERMISSIONS.WORD_FLASHCARD],
    category: 'learning',
    description: '单词学习-闪卡模式'
  },
  
  // 测试模式
  '/position-test': {
    required: [LEARNING_PERMISSIONS.POSITION_TEST],
    category: 'assessment',
    description: '位置测试'
  }
};

// 所有页面权限配置
export const PAGE_PERMISSIONS: Record<string, PagePermissionConfig> = {
  // 学习模式页面
  ...LEARNING_MODE_PERMISSIONS,
  
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
  
  // 内容页面
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
  
  // 社交页面
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
  
  // 开发页面
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
  },
  
  '/auth-test': {
    required: [],
    category: 'development',
    description: '认证测试'
  },
  
  '/login-test': {
    required: [],
    category: 'development',
    description: '登录测试'
  }
};

// 权限分类对应的页面
export const PERMISSION_CATEGORY_PAGES: Record<PermissionCategory, string[]> = {
  public: [],
  auth: [],
  user: [],
  learning: [],
  social_learning: [],
  content: [],
  social: [],
  assessment: [],
  development: []
};

// 初始化分类页面映射
Object.entries(PAGE_PERMISSIONS).forEach(([path, config]) => {
  const category = config.category as PermissionCategory || 'public';
  if (!PERMISSION_CATEGORY_PAGES[category]) {
    PERMISSION_CATEGORY_PAGES[category] = [];
  }
  PERMISSION_CATEGORY_PAGES[category].push(path);
});

/**
 * 检查用户是否可以访问指定页面
 * @param userPermissions - 用户权限列表
 * @param path - 页面路径
 * @returns 是否可以访问
 */
export function canAccessPage(userPermissions: string[], path: string): boolean {
  const pageConfig = PAGE_PERMISSIONS[path];
  
  if (!pageConfig) {
    // 如果页面未配置权限，默认允许访问
    return true;
  }
  
  const requiredPermissions = pageConfig.required || [];
  
  // 如果页面不需要特殊权限，允许访问
  if (requiredPermissions.length === 0) {
    return true;
  }
  
  // 检查用户是否拥有所有必需权限
  return requiredPermissions.every(permission => 
    userPermissions.includes(permission)
  );
}

/**
 * 获取用户可访问的学习模式页面
 * @param userPermissions - 用户权限列表
 * @returns 可访问的页面列表
 */
export function getAccessibleLearningModes(userPermissions: string[]): AccessiblePageInfo[] {
  return Object.entries(LEARNING_MODE_PERMISSIONS)
    .filter(([path, config]) => canAccessPage(userPermissions, path))
    .map(([path, config]) => ({
      path,
      ...config
    }));
}

/**
 * 获取页面权限配置
 * @param path - 页面路径
 * @returns 权限配置
 */
export function getPagePermissionConfig(path: string): PagePermissionConfig | null {
  return PAGE_PERMISSIONS[path] || null;
}

/**
 * 检查页面是否需要认证
 * @param path - 页面路径
 * @returns 是否需要认证
 */
export function pageRequiresAuth(path: string): boolean {
  const config = PAGE_PERMISSIONS[path];
  return config?.requiresAuth === true;
}

/**
 * 获取指定分类的所有页面
 * @param category - 权限分类
 * @returns 页面路径列表
 */
export function getPagesByCategory(category: PermissionCategory): string[] {
  return PERMISSION_CATEGORY_PAGES[category] || [];
}

/**
 * 获取用户可访问的所有页面
 * @param userPermissions - 用户权限列表
 * @returns 可访问的页面配置列表
 */
export function getAllAccessiblePages(userPermissions: string[]): AccessiblePageInfo[] {
  return Object.entries(PAGE_PERMISSIONS)
    .filter(([path, config]) => canAccessPage(userPermissions, path))
    .map(([path, config]) => ({
      path,
      ...config
    }));
}