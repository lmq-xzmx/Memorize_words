// 菜单配置文件
// 定义应用的菜单结构和权限控制

// 菜单类型定义
export const MENU_TYPES = {
  ROOT: 'root',           // 根菜单（TabBar）
  PRIMARY: 'primary',     // 一级菜单
  SECONDARY: 'secondary', // 二级菜单
  ACTION: 'action'        // 操作菜单
}

// 菜单状态定义
export const MENU_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  DISABLED: 'disabled',
  HIDDEN: 'hidden'
}

// 根菜单配置（TabBar菜单）
export const ROOT_MENUS = {
  WORD_CHALLENGE: {
    id: 'word_challenge',
    title: '斩词',
    icon: 'sword',
    path: '/word-challenge',
    permission: 'word_challenge_access',
    category: 'learning',
    order: 1
  },
  TOOLS: {
    id: 'tools',
    title: '工具',
    icon: 'tools',
    path: '/tools',
    permission: 'tools_access',
    category: 'utility',
    order: 2
  },
  FASHION: {
    id: 'fashion',
    title: '时尚',
    icon: 'fashion',
    path: '/fashion',
    permission: 'fashion_access',
    category: 'social',
    order: 3
  },
  PROFILE: {
    id: 'profile',
    title: '我的',
    icon: 'user',
    path: '/profile',
    permission: 'basic_access',
    category: 'personal',
    order: 4
  }
}

// 一级菜单配置
export const PRIMARY_MENUS = {
  // 斩词模块
  WORD_LEARNING: {
    id: 'word_learning',
    title: '单词学习',
    icon: 'book',
    path: '/word-challenge/learning',
    permission: 'word_learning_access',
    parent: 'word_challenge',
    children: ['word_spelling', 'flashcard_practice']
  },
  WORD_CHALLENGE_GAME: {
    id: 'word_challenge_game',
    title: '单词挑战',
    icon: 'game',
    path: '/word-challenge/game',
    permission: 'word_challenge_access',
    parent: 'word_challenge'
  },
  WORD_REVIEW: {
    id: 'word_review',
    title: '单词复习',
    icon: 'review',
    path: '/word-challenge/review',
    permission: 'word_review_access',
    parent: 'word_challenge'
  },
  READING_COMPREHENSION: {
    id: 'reading_comprehension',
    title: '阅读理解',
    icon: 'reading',
    path: '/word-challenge/reading',
    permission: 'reading_access',
    parent: 'word_challenge'
  },
  LISTENING_PRACTICE: {
    id: 'listening_practice',
    title: '听力练习',
    icon: 'listening',
    path: '/word-challenge/listening',
    permission: 'listening_access',
    parent: 'word_challenge'
  },

  // 工具模块
  CLASS_MANAGEMENT: {
    id: 'class_management',
    title: '班级管理',
    icon: 'class',
    path: '/tools/class',
    permission: 'class_management_access',
    parent: 'tools'
  },
  STUDENT_PROGRESS: {
    id: 'student_progress',
    title: '学生进度',
    icon: 'progress',
    path: '/tools/progress',
    permission: 'student_progress_access',
    parent: 'tools'
  },
  TEACHING_RESOURCES: {
    id: 'teaching_resources',
    title: '教学资源',
    icon: 'resources',
    path: '/tools/resources',
    permission: 'teaching_resources_access',
    parent: 'tools'
  },
  DATA_ANALYSIS: {
    id: 'data_analysis',
    title: '数据分析',
    icon: 'analytics',
    path: '/tools/analytics',
    permission: 'data_analysis_access',
    parent: 'tools'
  },

  // 时尚模块
  DISCOVER: {
    id: 'discover',
    title: '发现',
    icon: 'discover',
    path: '/fashion/discover',
    permission: 'discover_access',
    parent: 'fashion'
  },
  TRENDS: {
    id: 'trends',
    title: '趋势',
    icon: 'trends',
    path: '/fashion/trends',
    permission: 'trends_access',
    parent: 'fashion'
  },
  COMMUNITY: {
    id: 'community',
    title: '社区',
    icon: 'community',
    path: '/fashion/community',
    permission: 'community_access',
    parent: 'fashion'
  },

  // 个人中心模块
  PERSONAL_INFO: {
    id: 'personal_info',
    title: '个人信息',
    icon: 'info',
    path: '/profile/info',
    permission: 'basic_access',
    parent: 'profile'
  },
  LEARNING_STATS: {
    id: 'learning_stats',
    title: '学习统计',
    icon: 'stats',
    path: '/profile/stats',
    permission: 'learning_stats_access',
    parent: 'profile'
  },
  SETTINGS: {
    id: 'settings',
    title: '设置',
    icon: 'settings',
    path: '/profile/settings',
    permission: 'basic_access',
    parent: 'profile'
  }
}

// 二级菜单配置
export const SECONDARY_MENUS = {
  WORD_SPELLING: {
    id: 'word_spelling',
    title: '单词拼写',
    icon: 'spelling',
    path: '/word-challenge/learning/spelling',
    permission: 'word_spelling_access',
    parent: 'word_learning'
  },
  FLASHCARD_PRACTICE: {
    id: 'flashcard_practice',
    title: '闪卡练习',
    icon: 'flashcard',
    path: '/word-challenge/learning/flashcard',
    permission: 'flashcard_access',
    parent: 'word_learning'
  }
}

// 页面权限映射
export const PAGE_PERMISSIONS = {
  '/word-challenge': 'word_challenge_access',
  '/word-challenge/learning': 'word_learning_access',
  '/word-challenge/game': 'word_challenge_access',
  '/word-challenge/review': 'word_review_access',
  '/word-challenge/reading': 'reading_access',
  '/word-challenge/listening': 'listening_access',
  '/tools': 'tools_access',
  '/tools/class': 'class_management_access',
  '/tools/progress': 'student_progress_access',
  '/tools/resources': 'teaching_resources_access',
  '/tools/analytics': 'data_analysis_access',
  '/fashion': 'fashion_access',
  '/fashion/discover': 'discover_access',
  '/fashion/trends': 'trends_access',
  '/fashion/community': 'community_access',
  '/profile': 'basic_access',
  '/profile/info': 'basic_access',
  '/profile/stats': 'learning_stats_access',
  '/profile/settings': 'basic_access'
}

// 角色显示名称
export const ROLE_DISPLAY_NAMES = {
  student: '学生',
  parent: '家长',
  teacher: '教师',
  academic_leader: '教研组长',
  academic_director: '教务主任',
  dean: '教导主任',
  admin: '管理员'
}

// 缓存配置
export const CACHE_CONFIG = {
  MENU_CACHE_KEY: 'user_menu_cache',
  PERMISSION_CACHE_KEY: 'user_permission_cache',
  CACHE_DURATION: 30 * 60 * 1000, // 30分钟
  MAX_CACHE_SIZE: 100
}

// 菜单工具函数
export const MenuUtils = {
  // 根据角色获取菜单
  getMenuByRole(role) {
    const roleMenuMap = {
      student: [ROOT_MENUS.WORD_CHALLENGE, ROOT_MENUS.FASHION, ROOT_MENUS.PROFILE],
      teacher: [ROOT_MENUS.WORD_CHALLENGE, ROOT_MENUS.TOOLS, ROOT_MENUS.FASHION, ROOT_MENUS.PROFILE],
      admin: Object.values(ROOT_MENUS)
    }
    return roleMenuMap[role] || []
  },

  // 检查菜单权限
  hasMenuPermission(menuId, userPermissions) {
    const menu = this.findMenuById(menuId)
    if (!menu || !menu.permission) return true
    return userPermissions.includes(menu.permission)
  },

  // 根据ID查找菜单
  findMenuById(menuId) {
    const allMenus = { ...ROOT_MENUS, ...PRIMARY_MENUS, ...SECONDARY_MENUS }
    return allMenus[menuId] || null
  },

  // 过滤有权限的菜单
  filterMenusByPermissions(menus, userPermissions) {
    return menus.filter(menu => this.hasMenuPermission(menu.id, userPermissions))
  },

  // 构建菜单树
  buildMenuTree(menus) {
    const menuMap = new Map()
    const rootMenus = []

    // 创建菜单映射
    menus.forEach(menu => {
      menuMap.set(menu.id, { ...menu, children: [] })
    })

    // 构建树结构
    menus.forEach(menu => {
      if (menu.parent) {
        const parent = menuMap.get(menu.parent)
        if (parent) {
          parent.children.push(menuMap.get(menu.id))
        }
      } else {
        rootMenus.push(menuMap.get(menu.id))
      }
    })

    return rootMenus
  }
}

export default {
  MENU_TYPES,
  MENU_STATUS,
  ROOT_MENUS,
  PRIMARY_MENUS,
  SECONDARY_MENUS,
  PAGE_PERMISSIONS,
  ROLE_DISPLAY_NAMES,
  CACHE_CONFIG,
  MenuUtils
}