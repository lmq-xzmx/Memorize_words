/**
 * 角色定义和权限管理
 * 定义系统中的角色层级和权限关系
 */

// 角色层级定义（数字越大权限越高）
export const ROLE_HIERARCHY = {
  'student': 1,
  'parent': 2,
  'teacher': 3,
  'research_leader': 4,
  'academic_director': 5,
  'dean': 6,
  'admin': 7
} as const

// 角色权限映射
export const ROLE_PERMISSIONS: Record<string, string[]> = {
  'student': [
    'learning.view',
    'learning.practice',
    'content.view',
    'social.interact'
  ],
  'parent': [
    'learning.view',
    'learning.monitor',
    'content.view',
    'social.view'
  ],
  'teacher': [
    'learning.view',
    'learning.manage',
    'content.view',
    'content.create',
    'content.edit',
    'social.moderate',
    'management.class'
  ],
  'research_leader': [
    'learning.view',
    'learning.manage',
    'content.view',
    'content.create',
    'content.edit',
    'content.delete',
    'social.moderate',
    'management.research',
    'advanced.analytics'
  ],
  'academic_director': [
    'learning.view',
    'learning.manage',
    'content.view',
    'content.create',
    'content.edit',
    'content.delete',
    'social.moderate',
    'management.academic',
    'management.curriculum',
    'advanced.analytics',
    'advanced.reports'
  ],
  'dean': [
    'learning.view',
    'learning.manage',
    'content.view',
    'content.create',
    'content.edit',
    'content.delete',
    'social.moderate',
    'management.academic',
    'management.curriculum',
    'management.faculty',
    'advanced.analytics',
    'advanced.reports',
    'system.monitor'
  ],
  'admin': [
    'learning.view',
    'learning.manage',
    'content.view',
    'content.create',
    'content.edit',
    'content.delete',
    'social.moderate',
    'management.academic',
    'management.curriculum',
    'management.faculty',
    'management.system',
    'advanced.analytics',
    'advanced.reports',
    'system.monitor',
    'system.configure',
    'system.backup'
  ]
}

/**
 * 获取用户可管理的角色列表
 * @param userRole 用户当前角色
 * @returns 可管理的角色列表
 */
export function getManageableRoles(userRole: string): string[] {
  const userLevel = ROLE_HIERARCHY[userRole as keyof typeof ROLE_HIERARCHY] || 0
  
  return Object.keys(ROLE_HIERARCHY).filter(role => {
    const roleLevel = ROLE_HIERARCHY[role as keyof typeof ROLE_HIERARCHY]
    return roleLevel < userLevel
  })
}

/**
 * 检查角色是否拥有特定权限
 * @param role 角色名称
 * @param permission 权限名称
 * @returns 是否拥有权限
 */
export function roleHasPermission(role: string, permission: string): boolean {
  const rolePermissions = ROLE_PERMISSIONS[role]
  return rolePermissions ? rolePermissions.includes(permission) : false
}

/**
 * 检查目标角色是否比当前用户角色级别更高
 * @param currentUserRole 当前用户角色
 * @param targetRole 目标角色
 * @returns 目标角色是否更高级
 */
export function isRoleHigher(currentUserRole: string, targetRole: string): boolean {
  const currentLevel = ROLE_HIERARCHY[currentUserRole as keyof typeof ROLE_HIERARCHY] || 0
  const targetLevel = ROLE_HIERARCHY[targetRole as keyof typeof ROLE_HIERARCHY] || 0
  
  return targetLevel > currentLevel
}

/**
 * 获取角色的显示名称
 * @param role 角色名称
 * @returns 角色显示名称
 */
export function getRoleDisplayName(role: string): string {
  const roleNames: Record<string, string> = {
    'student': '学生',
    'parent': '家长',
    'teacher': '教师',
    'research_leader': '研究负责人',
    'academic_director': '学术主任',
    'dean': '院长',
    'admin': '系统管理员'
  }
  
  return roleNames[role] || role
}

/**
 * 获取角色的权限列表
 * @param role 角色名称
 * @returns 权限列表
 */
export function getRolePermissions(role: string): string[] {
  return ROLE_PERMISSIONS[role] || []
}

/**
 * 检查用户是否可以分配特定角色
 * @param userRole 用户角色
 * @param targetRole 目标角色
 * @returns 是否可以分配
 */
export function canAssignRole(userRole: string, targetRole: string): boolean {
  const manageableRoles = getManageableRoles(userRole)
  return manageableRoles.includes(targetRole)
}

/**
 * 获取所有角色列表
 * @returns 角色列表
 */
export function getAllRoles(): string[] {
  return Object.keys(ROLE_HIERARCHY)
}

/**
 * 获取角色层级数值
 * @param role 角色名称
 * @returns 层级数值
 */
export function getRoleLevel(role: string): number {
  return ROLE_HIERARCHY[role as keyof typeof ROLE_HIERARCHY] || 0
}

export type RoleType = keyof typeof ROLE_HIERARCHY
export type PermissionType = string