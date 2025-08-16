/**
 * 菜单配置文件
 * 统一管理底部导航和其他菜单的配置
 */

// 底部导航主菜单配置 - 符合文档规范的层级结构
export const bottomNavMenus = [
  {
    id: 'word',
    key: 'word',
    name: '斩词',
    level: 'root',
    icon: '斩',
    iconType: 'chinese',
    url: '/',
    sort_order: 1,
    permissions: ['view_word_learning'],
    roles: ['student', 'teacher', 'parent', 'admin'],
    description: '单词学习主页面'
  },
  {
    id: 'tools',
    key: 'tools',
    name: '工具',
    level: 'level1',
    icon: '新',
    iconType: 'chinese',
    sort_order: 2,
    requiresAuth: true,
    permissions: ['access_dev_tools'],
    roles: ['admin', 'dean', 'academic_director', 'research_leader', 'teacher'],
    description: '开发工具集合',
    children: []
  },
  {
    id: 'fashion',
    key: 'fashion',
    name: '时尚',
    level: 'level1',
    icon: '榜',
    iconType: 'chinese',
    sort_order: 3,
    permissions: ['access_fashion_content'],
    roles: ['student', 'teacher', 'parent', 'admin'],
    description: '时尚内容和社区功能',
    children: []
  },
  {
    id: 'profile',
    key: 'profile',
    name: '我的',
    level: 'root',
    icon: '👤',
    iconType: 'emoji',
    url: '/profile',
    sort_order: 4,
    requiresAuth: true,
    permissions: ['view_own_profile'],
    roles: ['student', 'teacher', 'parent', 'admin'],
    description: '个人资料和设置'
  }
]

// 工具菜单配置 - 转换为层级结构的子菜单
export const toolsMenuConfig = {
  key: 'tools',
  name: '开发工具',
  level: 'level1',
  icon: 'fas fa-tools',
  sort_order: 2,
  permissions: ['access_dev_tools'],
  roles: ['admin', 'dean', 'academic_director', 'research_leader', 'teacher'],
  children: [
    {
      id: 'word-reading',
      key: 'word-reading',
      name: '单词阅读',
      level: 'level2',
      description: 'H5版单词阅读页面，支持音频播放和进度跟踪',
      url: '/word-reading',
      icon: '📖',
      sort_order: 1,
      permissions: ['practice_reading'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'word-learning',
      key: 'word-learning',
      name: '单词学习',
      level: 'level2',
      description: 'H5版单词学习页面，展示单词详情和多种释义',
      url: '/word-learning',
      icon: '📚',
      sort_order: 2,
      permissions: ['view_word_learning'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'word-spelling',
      key: 'word-spelling',
      name: '拼写练习',
      level: 'level2',
      description: '听音拼写练习页面，提升单词记忆',
      url: '/word-learning/spelling',
      icon: '✍️',
      sort_order: 3,
      permissions: ['practice_spelling'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'word-flashcard',
      key: 'word-flashcard',
      name: '闪卡学习',
      level: 'level2',
      description: '翻转卡片学习单词页面',
      url: '/word-learning/flashcard',
      icon: '🃏',
      sort_order: 4,
      permissions: ['use_flashcard'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'word-detail',
      key: 'word-detail',
      name: '单词详情',
      level: 'level2',
      description: '单词详情页面，包含音标、释义、例句、词根词缀等完整信息',
      url: '/word-detail/institution',
      icon: '📝',
      sort_order: 5,
      permissions: ['view_word_detail'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'word-root-analysis',
      key: 'word-root-analysis',
      name: '词根分解',
      level: 'level2',
      description: '词根拆解展示页面，支持词根分析和学习进度管理',
      url: '/word-root-analysis',
      icon: '🌱',
      sort_order: 6,
      permissions: ['analyze_word_roots'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'pattern-memory',
      key: 'pattern-memory',
      name: '模式匹配记忆',
      level: 'level2',
      description: '三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式',
      url: '/pattern-memory',
      icon: '🧠',
      sort_order: 7,
      permissions: ['use_pattern_memory'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'story-reading',
      key: 'story-reading',
      name: '故事阅读',
      level: 'level2',
      description: '交互式故事阅读页面，支持词性标注和生词收集功能',
      url: '/story-reading',
      icon: '📚',
      sort_order: 8,
      permissions: ['practice_story_reading'],
      roles: ['student', 'teacher'],
      enabled: false
    },
    {
      id: 'word-challenge',
      key: 'word-challenge',
      name: '单词挑战',
      level: 'level2',
      description: '单词挑战游戏页面',
      url: '/word-challenge',
      icon: '⚔️',
      sort_order: 9,
      permissions: ['participate_challenge'],
      roles: ['student', 'teacher'],
      enabled: false
    }
  ]
}

// 时尚菜单配置 - 转换为层级结构
export const fashionMenuConfig = {
  key: 'fashion',
  name: '时尚内容',
  level: 'level1',
  icon: 'fas fa-star',
  sort_order: 3,
  permissions: ['access_fashion_content'],
  roles: ['student', 'teacher', 'parent', 'admin'],
  children: [
    {
      id: 'listening',
      key: 'listening',
      name: '听说训练中心',
      level: 'level2',
      url: '/listening',
      icon: '🎧',
      sort_order: 1,
      permissions: ['practice_listening'],
      roles: ['student', 'teacher'],
      description: '听力和口语训练'
    },
    {
      id: 'community',
      key: 'community',
      name: '社区互动',
      level: 'level2',
      url: '/community',
      icon: '👥',
      sort_order: 2,
      permissions: ['access_community'],
      roles: ['student', 'teacher', 'parent'],
      description: '用户社区交流'
    },
    {
      id: 'learning-modes',
      key: 'learning-modes',
      name: '词汇阅读中心',
      level: 'level2',
      url: '/learning-modes',
      icon: '📚',
      sort_order: 3,
      permissions: ['view_word_learning'],
      roles: ['student', 'teacher'],
      description: '多种学习模式选择'
    },
    {
      id: 'fashion-trends',
      key: 'fashion-trends',
      name: '时尚趋势',
      level: 'level2',
      url: '/fashion',
      icon: '🌟',
      sort_order: 4,
      permissions: ['access_fashion_content'],
      roles: ['student', 'teacher', 'parent'],
      description: '最新时尚内容'
    },
    {
      id: 'discover',
      key: 'discover',
      name: '发现',
      level: 'level2',
      url: '/dev-index',
      icon: '🔍',
      sort_order: 5,
      permissions: ['discover_content'],
      roles: ['student', 'teacher', 'parent'],
      description: '发现新内容'
    }
  ]
}

// 管理功能菜单配置 - 转换为层级结构
export const adminMenuConfig = {
  key: 'admin',
  name: '管理功能',
  level: 'level1',
  icon: 'fas fa-cog',
  sort_order: 4,
  permissions: ['admin_access'],
  roles: ['admin', 'teacher'],
  children: [
    {
      id: 'admin-dev-index',
      key: 'admin-dev-index',
      name: '管理开发期首页',
      level: 'level2',
      url: '/admin/dev-index',
      icon: '⚙️',
      sort_order: 1,
      permissions: ['admin'],
      roles: ['admin'],
      description: '管理员开发期首页设置'
    },
    {
      id: 'user-management',
      key: 'user-management',
      name: '用户管理',
      level: 'level2',
      url: '/admin/users',
      icon: '👥',
      sort_order: 2,
      permissions: ['manage_users'],
      roles: ['admin'],
      description: '管理系统用户'
    },
    {
      id: 'content-management',
      key: 'content-management',
      name: '内容管理',
      level: 'level2',
      url: '/admin/content',
      icon: '📝',
      sort_order: 3,
      permissions: ['manage_content'],
      roles: ['admin', 'teacher'],
      description: '管理学习内容'
    },
    {
      id: 'system-settings',
      key: 'system-settings',
      name: '系统设置',
      level: 'level2',
      url: '/admin/settings',
      icon: '⚙️',
      sort_order: 4,
      permissions: ['manage_system'],
      roles: ['admin'],
      description: '系统配置管理'
    },
    {
      id: 'analytics',
      key: 'analytics',
      name: '数据分析',
      level: 'level2',
      url: '/admin/analytics',
      icon: '📊',
      sort_order: 5,
      permissions: ['view_analytics'],
      roles: ['admin', 'teacher'],
      description: '查看系统分析数据'
    }
  ]
}

// 菜单权限映射 - 适配新的层级结构
export const menuPermissions = {
  // 一级菜单权限
  'word': ['view_word_learning'],
  'tools': ['access_dev_tools'],
  'fashion': ['access_fashion_content'],
  'profile': ['view_own_profile'],
  'admin': ['admin_access'],
  
  // 二级菜单权限
  'word-reading': ['practice_reading'],
  'word-learning': ['view_word_learning'],
  'word-spelling': ['practice_spelling'],
  'word-flashcard': ['use_flashcard'],
  'word-detail': ['view_word_detail'],
  'word-root-analysis': ['analyze_word_roots'],
  'pattern-memory': ['use_pattern_memory'],
  'story-reading': ['practice_story_reading'],
  'word-challenge': ['participate_challenge'],
  'listening': ['practice_listening'],
  'community': ['access_community'],
  'learning-modes': ['view_word_learning'],
  'fashion-trends': ['access_fashion_content'],
  'discover': ['discover_content'],
  'admin-dev-index': ['admin_access'],
  'user-management': ['manage_users'],
  'content-management': ['manage_content'],
  'system-settings': ['manage_system'],
  'analytics': ['view_analytics']
}

// 角色显示名称映射
export const roleDisplayNames = {
  'admin': '管理员',
  'dean': '院长',
  'academic_director': '学术主任',
  'research_leader': '研究负责人',
  'teacher': '教师',
  'parent': '家长',
  'student': '学生'
}

// 获取用户可访问的菜单项 - 适配层级结构
export function getAccessibleMenuItems(userRole, hasPermissionFn) {
  const accessibleItems = []
  
  // 检查底部导航菜单
  bottomNavMenus.forEach(item => {
    if (!item.roles || item.roles.includes(userRole)) {
      if (!item.permissions || item.permissions.some(perm => hasPermissionFn(perm))) {
        accessibleItems.push({
          ...item,
          category: 'bottom-nav'
        })
      }
    }
  })
  
  // 检查工具菜单的子项
  if (toolsMenuConfig.roles.includes(userRole) && 
      toolsMenuConfig.permissions.some(perm => hasPermissionFn(perm))) {
    toolsMenuConfig.children.forEach(item => {
      if (item.roles.includes(userRole) && 
          item.permissions.some(perm => hasPermissionFn(perm))) {
        accessibleItems.push({
          ...item,
          category: 'tools'
        })
      }
    })
  }
  
  // 检查时尚菜单的子项
  if (fashionMenuConfig.roles.includes(userRole) && 
      fashionMenuConfig.permissions.some(perm => hasPermissionFn(perm))) {
    fashionMenuConfig.children.forEach(item => {
      if (item.roles.includes(userRole) && 
          item.permissions.some(perm => hasPermissionFn(perm))) {
        accessibleItems.push({
          ...item,
          category: 'fashion'
        })
      }
    })
  }
  
  // 检查管理员菜单的子项
  if (adminMenuConfig.roles.includes(userRole) && 
      adminMenuConfig.permissions.some(perm => hasPermissionFn(perm))) {
    adminMenuConfig.children.forEach(item => {
      if (item.roles.includes(userRole) && 
          item.permissions.some(perm => hasPermissionFn(perm))) {
        accessibleItems.push({
          ...item,
          category: 'admin'
        })
      }
    })
  }
  
  return accessibleItems
}

// 检查菜单项权限 - 适配层级结构
export function checkMenuPermission(menuId, userRole, hasPermissionFn) {
  // 查找菜单项
  const allMenuItems = [
    ...bottomNavMenus,
    ...toolsMenuConfig.children,
    ...fashionMenuConfig.children,
    ...adminMenuConfig.children
  ]
  
  const menuItem = allMenuItems.find(item => item.id === menuId || item.key === menuId)
  if (!menuItem) {
    return false
  }
  
  // 检查角色权限
  if (menuItem.roles && !menuItem.roles.includes(userRole)) {
    return false
  }
  
  // 检查功能权限
  if (!menuItem.permissions || menuItem.permissions.length === 0) {
    return true
  }
  
  return menuItem.permissions.some(perm => hasPermissionFn(perm))
}

export default {
  bottomNavMenus,
  toolsMenuConfig,
  fashionMenuConfig,
  adminMenuConfig,
  menuPermissions,
  roleDisplayNames,
  getAccessibleMenuItems,
  checkMenuPermission
}