// 菜单配置
export interface MenuItem {
  id: string
  title: string
  path: string
  icon?: string
  permission?: string
  children?: MenuItem[]
}

// 主菜单配置
export const MAIN_MENU_ITEMS: MenuItem[] = [
  {
    id: 'dashboard',
    title: '仪表板',
    path: '/dashboard',
    icon: 'el-icon-s-home',
    permission: 'dashboard.view'
  },
  {
    id: 'learning',
    title: '学习中心',
    path: '/learning',
    icon: 'el-icon-reading',
    permission: 'learning.view',
    children: [
      {
        id: 'word-learning',
        title: '单词学习',
        path: '/learning/words',
        icon: 'el-icon-document',
        permission: 'learning.words.view'
      },
      {
        id: 'sentence-learning',
        title: '句子学习',
        path: '/learning/sentences',
        icon: 'el-icon-chat-line-square',
        permission: 'learning.sentences.view'
      },
      {
        id: 'practice',
        title: '练习测试',
        path: '/learning/practice',
        icon: 'el-icon-edit-outline',
        permission: 'learning.practice.view'
      }
    ]
  },
  {
    id: 'progress',
    title: '学习进度',
    path: '/progress',
    icon: 'el-icon-data-line',
    permission: 'progress.view',
    children: [
      {
        id: 'statistics',
        title: '学习统计',
        path: '/progress/statistics',
        icon: 'el-icon-pie-chart',
        permission: 'progress.statistics.view'
      },
      {
        id: 'achievements',
        title: '成就徽章',
        path: '/progress/achievements',
        icon: 'el-icon-trophy',
        permission: 'progress.achievements.view'
      }
    ]
  },
  {
    id: 'profile',
    title: '个人中心',
    path: '/profile',
    icon: 'el-icon-user',
    permission: 'profile.view',
    children: [
      {
        id: 'settings',
        title: '个人设置',
        path: '/profile/settings',
        icon: 'el-icon-setting',
        permission: 'profile.settings.view'
      },
      {
        id: 'history',
        title: '学习历史',
        path: '/profile/history',
        icon: 'el-icon-time',
        permission: 'profile.history.view'
      }
    ]
  }
]

// 管理员菜单配置
export const ADMIN_MENU_ITEMS: MenuItem[] = [
  {
    id: 'admin-dashboard',
    title: '管理仪表板',
    path: '/admin/dashboard',
    icon: 'el-icon-s-platform',
    permission: 'admin.dashboard.view'
  },
  {
    id: 'user-management',
    title: '用户管理',
    path: '/admin/users',
    icon: 'el-icon-user-solid',
    permission: 'admin.users.view',
    children: [
      {
        id: 'user-list',
        title: '用户列表',
        path: '/admin/users/list',
        icon: 'el-icon-s-custom',
        permission: 'admin.users.list.view'
      },
      {
        id: 'user-roles',
        title: '角色管理',
        path: '/admin/users/roles',
        icon: 'el-icon-s-check',
        permission: 'admin.users.roles.view'
      }
    ]
  },
  {
    id: 'content-management',
    title: '内容管理',
    path: '/admin/content',
    icon: 'el-icon-document-copy',
    permission: 'admin.content.view',
    children: [
      {
        id: 'word-management',
        title: '单词管理',
        path: '/admin/content/words',
        icon: 'el-icon-collection',
        permission: 'admin.content.words.view'
      },
      {
        id: 'sentence-management',
        title: '句子管理',
        path: '/admin/content/sentences',
        icon: 'el-icon-chat-dot-square',
        permission: 'admin.content.sentences.view'
      }
    ]
  },
  {
    id: 'system-settings',
    title: '系统设置',
    path: '/admin/system',
    icon: 'el-icon-s-tools',
    permission: 'admin.system.view',
    children: [
      {
        id: 'system-config',
        title: '系统配置',
        path: '/admin/system/config',
        icon: 'el-icon-s-operation',
        permission: 'admin.system.config.view'
      },
      {
        id: 'system-logs',
        title: '系统日志',
        path: '/admin/system/logs',
        icon: 'el-icon-document',
        permission: 'admin.system.logs.view'
      }
    ]
  }
]

// 教师菜单配置
export const TEACHER_MENU_ITEMS: MenuItem[] = [
  {
    id: 'teacher-dashboard',
    title: '教师仪表板',
    path: '/teacher/dashboard',
    icon: 'el-icon-s-home',
    permission: 'teacher.dashboard.view'
  },
  {
    id: 'class-management',
    title: '班级管理',
    path: '/teacher/classes',
    icon: 'el-icon-s-custom',
    permission: 'teacher.classes.view',
    children: [
      {
        id: 'class-list',
        title: '班级列表',
        path: '/teacher/classes/list',
        icon: 'el-icon-menu',
        permission: 'teacher.classes.list.view'
      },
      {
        id: 'student-progress',
        title: '学生进度',
        path: '/teacher/classes/progress',
        icon: 'el-icon-data-analysis',
        permission: 'teacher.classes.progress.view'
      }
    ]
  },
  {
    id: 'course-management',
    title: '课程管理',
    path: '/teacher/courses',
    icon: 'el-icon-reading',
    permission: 'teacher.courses.view',
    children: [
      {
        id: 'course-create',
        title: '创建课程',
        path: '/teacher/courses/create',
        icon: 'el-icon-circle-plus',
        permission: 'teacher.courses.create'
      },
      {
        id: 'course-list',
        title: '课程列表',
        path: '/teacher/courses/list',
        icon: 'el-icon-collection',
        permission: 'teacher.courses.list.view'
      }
    ]
  }
]

// 根据用户角色获取菜单
export const getMenuByRole = (role: string): MenuItem[] => {
  switch (role) {
    case 'admin':
      return [...MAIN_MENU_ITEMS, ...ADMIN_MENU_ITEMS]
    case 'teacher':
      return [...MAIN_MENU_ITEMS, ...TEACHER_MENU_ITEMS]
    case 'student':
    default:
      return MAIN_MENU_ITEMS
  }
}

// 获取扁平化的菜单项（用于权限检查）
export const getFlatMenuItems = (menuItems: MenuItem[]): MenuItem[] => {
  const flatItems: MenuItem[] = []
  
  const flatten = (items: MenuItem[]) => {
    items.forEach(item => {
      flatItems.push(item)
      if (item.children) {
        flatten(item.children)
      }
    })
  }
  
  flatten(menuItems)
  return flatItems
}

// 根据路径查找菜单项
export const findMenuItemByPath = (menuItems: MenuItem[], path: string): MenuItem | null => {
  for (const item of menuItems) {
    if (item.path === path) {
      return item
    }
    if (item.children) {
      const found = findMenuItemByPath(item.children, path)
      if (found) return found
    }
  }
  return null
}

// 根据权限过滤菜单项
export const filterMenuByPermissions = (menuItems: MenuItem[], userPermissions: string[]): MenuItem[] => {
  return menuItems.filter(item => {
    // 如果没有权限要求，则显示
    if (!item.permission) {
      // 如果有子菜单，递归过滤
      if (item.children) {
        const filteredChildren = filterMenuByPermissions(item.children, userPermissions)
        return filteredChildren.length > 0 ? { ...item, children: filteredChildren } : false
      }
      return true
    }
    
    // 检查用户是否有该权限
    const hasPermission = userPermissions.includes(item.permission)
    if (!hasPermission) {
      return false
    }
    
    // 如果有子菜单，递归过滤
    if (item.children) {
      const filteredChildren = filterMenuByPermissions(item.children, userPermissions)
      return { ...item, children: filteredChildren }
    }
    
    return true
  }).filter(Boolean) as MenuItem[]
}