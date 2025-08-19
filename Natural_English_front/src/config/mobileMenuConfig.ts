import type { MenuItem } from '@/composables/usePermission'
import type { ToolItem } from '@/composables/useMenuManager'

/**
 * 移动端底部导航菜单配置
 */
export const mobileBottomMenuConfig: MenuItem[] = [
  {
    id: 'learning',
    name: '学习中心',
    path: '/learning',
    icon: '学',
    meta: {
      title: '学习中心',
      requiresAuth: true,
      permissions: ['learning:access'],
      order: 1
    }
  },
  {
    id: 'tools',
    name: '工具中心',
    path: '/tools',
    icon: '工',
    meta: {
      title: '工具中心',
      requiresAuth: true,
      permissions: ['tools:access'],
      order: 2
    }
  },
  {
    id: 'words',
    name: '词汇管理',
    path: '/words',
    icon: '词',
    meta: {
      title: '词汇管理',
      requiresAuth: true,
      permissions: ['words:access'],
      order: 3
    },
    children: [
      {
        id: 'words-vocabulary',
        name: '词汇管理',
        path: '/words/vocabulary',
        icon: '📚',
        meta: {
          title: '词汇管理',
          requiresAuth: true,
          permissions: ['words:manage']
        }
      },
      {
        id: 'words-practice',
        name: '练习模式',
        path: '/words/practice',
        icon: '✍️',
        meta: {
          title: '练习模式',
          requiresAuth: true,
          permissions: ['words:practice']
        }
      },
      {
        id: 'words-review',
        name: '复习中心',
        path: '/words/review',
        icon: '🔄',
        meta: {
          title: '复习中心',
          requiresAuth: true,
          permissions: ['words:review']
        }
      },
      {
        id: 'words-statistics',
        name: '学习统计',
        path: '/words/statistics',
        icon: '📊',
        meta: {
          title: '学习统计',
          requiresAuth: true,
          permissions: ['words:statistics']
        }
      }
    ]
  },
  {
    id: 'profile',
    name: '个人中心',
    path: '/profile',
    icon: '👤',
    meta: {
      title: '个人中心',
      requiresAuth: true,
      order: 4
    }
  }
]

/**
 * 开发工具配置
 */
export const developmentToolsConfig: ToolItem[] = [
  {
    id: 'word-reading',
    name: '单词阅读',
    title: '单词阅读',
    description: '支持音频播放和进度跟踪的单词阅读功能',
    path: '/words/reading',
    icon: '📖',
    enabled: false,
    category: 'words',
    order: 1
  },
  {
    id: 'word-learning',
    name: '单词学习',
    title: '单词学习',
    description: '展示单词详情和多种释义的学习页面',
    path: '/words/learning',
    icon: '📚',
    enabled: false,
    category: 'words',
    order: 2
  },
  {
    id: 'word-spelling',
    name: '拼写练习',
    title: '拼写练习',
    description: '听音拼写练习，提升单词记忆效果',
    path: '/words/spelling',
    icon: '✍️',
    enabled: false,
    category: 'words',
    order: 3
  },
  {
    id: 'grammar-check',
    name: '语法检查',
    title: '语法检查',
    description: '智能语法检查和纠错功能',
    path: '/tools/grammar',
    icon: '📝',
    enabled: false,
    category: 'tools',
    order: 4
  },
  {
    id: 'pronunciation-practice',
    name: '发音练习',
    title: '发音练习',
    description: 'AI语音识别，纠正发音问题',
    path: '/tools/pronunciation',
    icon: '🎤',
    enabled: false,
    category: 'tools',
    order: 5
  },
  {
    id: 'translation-tool',
    name: '翻译工具',
    title: '翻译工具',
    description: '多语言翻译，支持语音和文本',
    path: '/tools/translation',
    icon: '🌐',
    enabled: false,
    category: 'tools',
    order: 6
  },
  {
    id: 'study-plan',
    name: '学习计划',
    title: '学习计划',
    description: '个性化学习计划制定和跟踪',
    path: '/learning/plan',
    icon: '📅',
    enabled: false,
    category: 'learning',
    order: 7
  },
  {
    id: 'progress-tracking',
    name: '进度跟踪',
    title: '进度跟踪',
    description: '详细的学习进度分析和报告',
    path: '/learning/progress',
    icon: '📈',
    enabled: false,
    category: 'learning',
    order: 8
  }
]

/**
 * 权限映射配置
 */
export const permissionMapping = {
  // 学习模块权限
  learning: {
    access: 'learning:access',
    view: 'learning:view',
    create: 'learning:create',
    edit: 'learning:edit',
    delete: 'learning:delete'
  },
  
  // 工具模块权限
  tools: {
    access: 'tools:access',
    use: 'tools:use',
    configure: 'tools:configure',
    manage: 'tools:manage'
  },
  
  // 词汇模块权限
  words: {
    access: 'words:access',
    view: 'words:view',
    manage: 'words:manage',
    practice: 'words:practice',
    review: 'words:review',
    statistics: 'words:statistics',
    import: 'words:import',
    export: 'words:export'
  },
  
  // 用户模块权限
  user: {
    profile: 'user:profile',
    settings: 'user:settings',
    security: 'user:security'
  }
}

/**
 * 角色显示名称映射
 */
export const roleDisplayNames = {
  super_admin: '超级管理员',
  admin: '管理员',
  teacher: '教师',
  student: '学生',
  guest: '访客'
}

/**
 * 获取用户可访问的菜单项
 */
export function getUserAccessibleMenus(
  userPermissions: string[],
  userRoles: string[]
): MenuItem[] {
  return mobileBottomMenuConfig.filter(menu => {
    // 检查菜单权限
    if (menu.meta?.permissions) {
      const hasPermission = menu.meta.permissions.some(permission => 
        userPermissions.includes(permission)
      )
      if (!hasPermission) return false
    }
    
    // 检查角色权限
    if (menu.meta?.roles) {
      const hasRole = menu.meta.roles.some(role => 
        userRoles.includes(role)
      )
      if (!hasRole) return false
    }
    
    // 过滤子菜单
    if (menu.children) {
      menu.children = menu.children.filter(child => {
        if (child.meta?.permissions) {
          return child.meta.permissions.some(permission => 
            userPermissions.includes(permission)
          )
        }
        if (child.meta?.roles) {
          return child.meta.roles.some(role => 
            userRoles.includes(role)
          )
        }
        return true
      })
    }
    
    return true
  })
}

/**
 * 获取用户可用的开发工具
 */
export function getUserAccessibleTools(
  userPermissions: string[],
  userRoles: string[]
): ToolItem[] {
  // 超级管理员和管理员可以访问所有工具
  if (userRoles.includes('super_admin') || userRoles.includes('admin')) {
    return developmentToolsConfig
  }
  
  // 根据权限过滤工具
  return developmentToolsConfig.filter(tool => {
    const categoryPermission = `${tool.category}:use`
    return userPermissions.includes(categoryPermission) || 
           userPermissions.includes('tools:manage')
  })
}

/**
 * 菜单配置验证
 */
export function validateMenuConfig(config: MenuItem[]): boolean {
  try {
    for (const menu of config) {
      if (!menu.id || !menu.name || !menu.path) {
        console.error('菜单配置缺少必要字段:', menu)
        return false
      }
      
      if (menu.children) {
        if (!validateMenuConfig(menu.children)) {
          return false
        }
      }
    }
    return true
  } catch (error) {
    console.error('菜单配置验证失败:', error)
    return false
  }
}

/**
 * 工具配置验证
 */
export function validateToolsConfig(config: ToolItem[]): boolean {
  try {
    for (const tool of config) {
      if (!tool.id || !tool.name || !tool.path) {
        console.error('工具配置缺少必要字段:', tool)
        return false
      }
    }
    return true
  } catch (error) {
    console.error('工具配置验证失败:', error)
    return false
  }
}

export default {
  mobileBottomMenuConfig,
  developmentToolsConfig,
  permissionMapping,
  roleDisplayNames,
  getUserAccessibleMenus,
  getUserAccessibleTools,
  validateMenuConfig,
  validateToolsConfig
}