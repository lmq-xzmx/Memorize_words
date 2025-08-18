// 权限配置
export interface Permission {
  id: string
  name: string
  description: string
  category: string
}

// 权限类别
export const PERMISSION_CATEGORIES = {
  DASHBOARD: 'dashboard',
  LEARNING: 'learning',
  PROGRESS: 'progress',
  PROFILE: 'profile',
  ADMIN: 'admin',
  TEACHER: 'teacher'
} as const

// 基础权限定义
export const PERMISSIONS: Permission[] = [
  // 仪表板权限
  {
    id: 'dashboard.view',
    name: '查看仪表板',
    description: '允许用户查看仪表板页面',
    category: PERMISSION_CATEGORIES.DASHBOARD
  },
  
  // 学习中心权限
  {
    id: 'learning.view',
    name: '访问学习中心',
    description: '允许用户访问学习中心',
    category: PERMISSION_CATEGORIES.LEARNING
  },
  {
    id: 'learning.words.view',
    name: '查看单词学习',
    description: '允许用户查看单词学习模块',
    category: PERMISSION_CATEGORIES.LEARNING
  },
  {
    id: 'learning.words.practice',
    name: '练习单词',
    description: '允许用户进行单词练习',
    category: PERMISSION_CATEGORIES.LEARNING
  },
  {
    id: 'learning.sentences.view',
    name: '查看句子学习',
    description: '允许用户查看句子学习模块',
    category: PERMISSION_CATEGORIES.LEARNING
  },
  {
    id: 'learning.sentences.practice',
    name: '练习句子',
    description: '允许用户进行句子练习',
    category: PERMISSION_CATEGORIES.LEARNING
  },
  {
    id: 'learning.practice.view',
    name: '查看练习测试',
    description: '允许用户查看练习测试模块',
    category: PERMISSION_CATEGORIES.LEARNING
  },
  {
    id: 'learning.practice.take',
    name: '参加测试',
    description: '允许用户参加练习测试',
    category: PERMISSION_CATEGORIES.LEARNING
  },
  
  // 学习进度权限
  {
    id: 'progress.view',
    name: '查看学习进度',
    description: '允许用户查看学习进度',
    category: PERMISSION_CATEGORIES.PROGRESS
  },
  {
    id: 'progress.statistics.view',
    name: '查看学习统计',
    description: '允许用户查看学习统计数据',
    category: PERMISSION_CATEGORIES.PROGRESS
  },
  {
    id: 'progress.achievements.view',
    name: '查看成就徽章',
    description: '允许用户查看成就徽章',
    category: PERMISSION_CATEGORIES.PROGRESS
  },
  
  // 个人中心权限
  {
    id: 'profile.view',
    name: '查看个人中心',
    description: '允许用户查看个人中心',
    category: PERMISSION_CATEGORIES.PROFILE
  },
  {
    id: 'profile.settings.view',
    name: '查看个人设置',
    description: '允许用户查看个人设置',
    category: PERMISSION_CATEGORIES.PROFILE
  },
  {
    id: 'profile.settings.edit',
    name: '编辑个人设置',
    description: '允许用户编辑个人设置',
    category: PERMISSION_CATEGORIES.PROFILE
  },
  {
    id: 'profile.history.view',
    name: '查看学习历史',
    description: '允许用户查看学习历史',
    category: PERMISSION_CATEGORIES.PROFILE
  },
  
  // 管理员权限
  {
    id: 'admin.dashboard.view',
    name: '查看管理仪表板',
    description: '允许管理员查看管理仪表板',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.users.view',
    name: '查看用户管理',
    description: '允许管理员查看用户管理模块',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.users.list.view',
    name: '查看用户列表',
    description: '允许管理员查看用户列表',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.users.create',
    name: '创建用户',
    description: '允许管理员创建新用户',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.users.edit',
    name: '编辑用户',
    description: '允许管理员编辑用户信息',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.users.delete',
    name: '删除用户',
    description: '允许管理员删除用户',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.users.roles.view',
    name: '查看角色管理',
    description: '允许管理员查看角色管理',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.users.roles.edit',
    name: '编辑用户角色',
    description: '允许管理员编辑用户角色',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.view',
    name: '查看内容管理',
    description: '允许管理员查看内容管理模块',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.words.view',
    name: '查看单词管理',
    description: '允许管理员查看单词管理',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.words.create',
    name: '创建单词',
    description: '允许管理员创建新单词',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.words.edit',
    name: '编辑单词',
    description: '允许管理员编辑单词',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.words.delete',
    name: '删除单词',
    description: '允许管理员删除单词',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.sentences.view',
    name: '查看句子管理',
    description: '允许管理员查看句子管理',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.sentences.create',
    name: '创建句子',
    description: '允许管理员创建新句子',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.sentences.edit',
    name: '编辑句子',
    description: '允许管理员编辑句子',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.content.sentences.delete',
    name: '删除句子',
    description: '允许管理员删除句子',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.system.view',
    name: '查看系统设置',
    description: '允许管理员查看系统设置',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.system.config.view',
    name: '查看系统配置',
    description: '允许管理员查看系统配置',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.system.config.edit',
    name: '编辑系统配置',
    description: '允许管理员编辑系统配置',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  {
    id: 'admin.system.logs.view',
    name: '查看系统日志',
    description: '允许管理员查看系统日志',
    category: PERMISSION_CATEGORIES.ADMIN
  },
  
  // 教师权限
  {
    id: 'teacher.dashboard.view',
    name: '查看教师仪表板',
    description: '允许教师查看教师仪表板',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.classes.view',
    name: '查看班级管理',
    description: '允许教师查看班级管理模块',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.classes.list.view',
    name: '查看班级列表',
    description: '允许教师查看班级列表',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.classes.create',
    name: '创建班级',
    description: '允许教师创建新班级',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.classes.edit',
    name: '编辑班级',
    description: '允许教师编辑班级信息',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.classes.progress.view',
    name: '查看学生进度',
    description: '允许教师查看学生学习进度',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.courses.view',
    name: '查看课程管理',
    description: '允许教师查看课程管理模块',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.courses.create',
    name: '创建课程',
    description: '允许教师创建新课程',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.courses.list.view',
    name: '查看课程列表',
    description: '允许教师查看课程列表',
    category: PERMISSION_CATEGORIES.TEACHER
  },
  {
    id: 'teacher.courses.edit',
    name: '编辑课程',
    description: '允许教师编辑课程内容',
    category: PERMISSION_CATEGORIES.TEACHER
  }
]

// 学生权限
const STUDENT_PERMISSIONS = [
  'dashboard.view',
  'learning.view',
  'learning.words.view',
  'learning.words.practice',
  'learning.sentences.view',
  'learning.sentences.practice',
  'learning.practice.view',
  'learning.practice.take',
  'progress.view',
  'progress.statistics.view',
  'progress.achievements.view',
  'profile.view',
  'profile.settings.view',
  'profile.settings.edit',
  'profile.history.view'
]

// 教师特有权限
const TEACHER_SPECIFIC_PERMISSIONS = [
  'teacher.dashboard.view',
  'teacher.classes.view',
  'teacher.classes.list.view',
  'teacher.classes.create',
  'teacher.classes.edit',
  'teacher.classes.progress.view',
  'teacher.courses.view',
  'teacher.courses.create',
  'teacher.courses.list.view',
  'teacher.courses.edit'
]

// 角色权限映射
export const ROLE_PERMISSIONS = {
  student: STUDENT_PERMISSIONS,
  teacher: [...STUDENT_PERMISSIONS, ...TEACHER_SPECIFIC_PERMISSIONS],
  admin: PERMISSIONS.map(p => p.id)
}

// 获取角色权限
export const getRolePermissions = (role: string): string[] => {
  return ROLE_PERMISSIONS[role as keyof typeof ROLE_PERMISSIONS] || ROLE_PERMISSIONS.student
}

// 检查权限是否存在
export const isValidPermission = (permission: string): boolean => {
  return PERMISSIONS.some(p => p.id === permission)
}

// 根据类别获取权限
export const getPermissionsByCategory = (category: string): Permission[] => {
  return PERMISSIONS.filter(p => p.category === category)
}

// 权限检查函数
export const hasPermission = (userPermissions: string[], requiredPermission: string): boolean => {
  return userPermissions.includes(requiredPermission)
}

export const hasAnyPermission = (userPermissions: string[], requiredPermissions: string[]): boolean => {
  return requiredPermissions.some(permission => userPermissions.includes(permission))
}

export const hasAllPermissions = (userPermissions: string[], requiredPermissions: string[]): boolean => {
  return requiredPermissions.every(permission => userPermissions.includes(permission))
}