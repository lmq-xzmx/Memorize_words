/**
 * 角色定义和权限继承机制
 * 根据《用户权限管理系统规范》文档定义的角色体系
 */
// 从统一权限常量文件导入权限定义
import {
  LEARNING_PERMISSIONS,
  CONTENT_PERMISSIONS,
  SOCIAL_PERMISSIONS,
  MANAGEMENT_PERMISSIONS,
  SYSTEM_PERMISSIONS,
  ADVANCED_PERMISSIONS,
  ROLES,
  ROLE_DISPLAY_NAMES,
  ROLE_HIERARCHY,
  ROLE_INHERITANCE
} from './unifiedPermissionConstants.js'

// 角色定义已从统一权限常量文件导入
// 为了向后兼容，重新导出角色相关常量
export { ROLES, ROLE_DISPLAY_NAMES, ROLE_HIERARCHY, ROLE_INHERITANCE }

// 基础角色权限定义（不包含继承）
const BASE_ROLE_PERMISSIONS = {
  // 学生权限
  [ROLES.STUDENT]: [
    // 基础学习权限
    LEARNING_PERMISSIONS.WORD_LEARNING,
    LEARNING_PERMISSIONS.WORD_FLASHCARD,
    LEARNING_PERMISSIONS.WORD_SPELLING,
    LEARNING_PERMISSIONS.WORD_READING,
    LEARNING_PERMISSIONS.WORD_SELECTION,
    LEARNING_PERMISSIONS.STORY_READING,
    LEARNING_PERMISSIONS.LISTENING,
    LEARNING_PERMISSIONS.PATTERN_MEMORY,
    LEARNING_PERMISSIONS.WORD_ROOT_ANALYSIS,
    LEARNING_PERMISSIONS.WORD_EXAMPLES,
    LEARNING_PERMISSIONS.WORD_CHALLENGE,
    LEARNING_PERMISSIONS.WORD_REVIEW,
    LEARNING_PERMISSIONS.COMPETITION_MODE,
    LEARNING_PERMISSIONS.QUICK_BRUSH,
    LEARNING_PERMISSIONS.POSITION_TEST,
    LEARNING_PERMISSIONS.PROGRESS_TRACKING,
    
    // 基础内容权限
    CONTENT_PERMISSIONS.VIEW_CONTENT,
    CONTENT_PERMISSIONS.DOWNLOAD_CONTENT,
    CONTENT_PERMISSIONS.SHARE_CONTENT,
    
    // 基础社交权限
    SOCIAL_PERMISSIONS.VIEW_COMMUNITY,
    SOCIAL_PERMISSIONS.POST_COMMUNITY,
    SOCIAL_PERMISSIONS.COMMENT_COMMUNITY,
    SOCIAL_PERMISSIONS.LIKE_COMMUNITY,
    SOCIAL_PERMISSIONS.PEER_INTERACTION,
    SOCIAL_PERMISSIONS.GROUP_STUDY,
    SOCIAL_PERMISSIONS.VIEW_FASHION,
    SOCIAL_PERMISSIONS.PARTICIPATE_FASHION
  ],
  
  // 教师特有权限
  [ROLES.TEACHER]: [
    // 教师特有权限
    SOCIAL_PERMISSIONS.TEACHER_STUDENT_INTERACTION,
    
    // 内容管理权限
    CONTENT_PERMISSIONS.CREATE_CONTENT,
    CONTENT_PERMISSIONS.EDIT_CONTENT,
    CONTENT_PERMISSIONS.PUBLISH_CONTENT,
    
    // 基础管理权限
    MANAGEMENT_PERMISSIONS.VIEW_USERS,
    MANAGEMENT_PERMISSIONS.ACADEMIC_SUPERVISION
  ],
  
  // 家长权限
  [ROLES.PARENT]: [
    // 查看权限
    CONTENT_PERMISSIONS.VIEW_CONTENT,
    LEARNING_PERMISSIONS.PROGRESS_TRACKING,
    
    // 社交权限
    SOCIAL_PERMISSIONS.VIEW_COMMUNITY,
    SOCIAL_PERMISSIONS.TEACHER_STUDENT_INTERACTION
  ],
  
  // 教务主任特有权限
  [ROLES.ACADEMIC_DIRECTOR]: [
    // 学术管理权限
    MANAGEMENT_PERMISSIONS.CURRICULUM_MANAGEMENT,
    MANAGEMENT_PERMISSIONS.VIEW_ROLES,
    MANAGEMENT_PERMISSIONS.ASSIGN_ROLES,
    
    // 高级内容权限
    CONTENT_PERMISSIONS.DELETE_CONTENT,
    CONTENT_PERMISSIONS.RESOURCE_AUTH,
    
    // 数据分析权限
    SYSTEM_PERMISSIONS.DATA_ANALYSIS
  ],
  
  // 教研组长特有权限
  [ROLES.RESEARCH_LEADER]: [
    // 研究管理权限
    MANAGEMENT_PERMISSIONS.RESEARCH_MANAGEMENT,
    
    // 高级分析权限
    ADVANCED_PERMISSIONS.ADVANCED_ANALYTICS,
    SYSTEM_PERMISSIONS.DATA_EXPORT,
    SYSTEM_PERMISSIONS.DATA_IMPORT
  ],
  
  // 教导主任特有权限
  [ROLES.DEAN]: [
    // 高级管理权限
    MANAGEMENT_PERMISSIONS.CREATE_USERS,
    MANAGEMENT_PERMISSIONS.EDIT_USERS,
    MANAGEMENT_PERMISSIONS.DELETE_USERS,
    MANAGEMENT_PERMISSIONS.MODIFY_ROLES,
    MANAGEMENT_PERMISSIONS.VIEW_PERMISSIONS,
    MANAGEMENT_PERMISSIONS.ASSIGN_PERMISSIONS,
    
    // 系统权限
    SYSTEM_PERMISSIONS.SYSTEM_MONITORING,
    SYSTEM_PERMISSIONS.AUDIT_LOG,
    
    // 高级功能
    ADVANCED_PERMISSIONS.CUSTOM_FEATURES
  ],
  
  // 管理员特有权限
  [ROLES.ADMIN]: [
    // 系统管理权限
    SYSTEM_PERMISSIONS.SYSTEM_CONFIG,
    SYSTEM_PERMISSIONS.SYSTEM_BACKUP,
    SYSTEM_PERMISSIONS.SECURITY_CONFIG,
    SYSTEM_PERMISSIONS.ACCESS_CONTROL,
    
    // 权限管理
    MANAGEMENT_PERMISSIONS.MODIFY_PERMISSIONS,
    
    // 高级权限
    ADVANCED_PERMISSIONS.DEV_ACCESS,
    ADVANCED_PERMISSIONS.API_ACCESS,
    ADVANCED_PERMISSIONS.DEBUG_MODE,
    ADVANCED_PERMISSIONS.EXPERIMENTAL_FEATURES
  ]
}

// 构建完整的角色权限映射（包含继承）
function buildRolePermissions() {
  const rolePermissions = {}
  
  // 首先设置基础权限
  Object.keys(BASE_ROLE_PERMISSIONS).forEach(role => {
    rolePermissions[role] = [...BASE_ROLE_PERMISSIONS[role]]
  })
  
  // 然后处理继承关系
  rolePermissions[ROLES.TEACHER] = [
    ...rolePermissions[ROLES.STUDENT],
    ...BASE_ROLE_PERMISSIONS[ROLES.TEACHER]
  ]
  
  rolePermissions[ROLES.ACADEMIC_DIRECTOR] = [
    ...rolePermissions[ROLES.TEACHER],
    ...BASE_ROLE_PERMISSIONS[ROLES.ACADEMIC_DIRECTOR]
  ]
  
  rolePermissions[ROLES.RESEARCH_LEADER] = [
    ...rolePermissions[ROLES.ACADEMIC_DIRECTOR],
    ...BASE_ROLE_PERMISSIONS[ROLES.RESEARCH_LEADER]
  ]
  
  rolePermissions[ROLES.DEAN] = [
    ...rolePermissions[ROLES.RESEARCH_LEADER],
    ...BASE_ROLE_PERMISSIONS[ROLES.DEAN]
  ]
  
  rolePermissions[ROLES.ADMIN] = [
    ...rolePermissions[ROLES.DEAN],
    ...BASE_ROLE_PERMISSIONS[ROLES.ADMIN]
  ]
  
  return rolePermissions
}

// 角色权限定义（包含继承）
export const ROLE_PERMISSIONS = buildRolePermissions()

// 角色继承关系
export const ROLE_INHERITANCE = {
  [ROLES.TEACHER]: [ROLES.STUDENT],
  [ROLES.ACADEMIC_DIRECTOR]: [ROLES.TEACHER, ROLES.STUDENT],
  [ROLES.RESEARCH_LEADER]: [ROLES.ACADEMIC_DIRECTOR, ROLES.TEACHER, ROLES.STUDENT],
  [ROLES.DEAN]: [ROLES.RESEARCH_LEADER, ROLES.ACADEMIC_DIRECTOR, ROLES.TEACHER, ROLES.STUDENT],
  [ROLES.ADMIN]: [ROLES.DEAN, ROLES.RESEARCH_LEADER, ROLES.ACADEMIC_DIRECTOR, ROLES.TEACHER, ROLES.STUDENT]
}

// 角色层级（数字越大权限越高）
export const ROLE_HIERARCHY = {
  [ROLES.STUDENT]: 1,
  [ROLES.PARENT]: 1,
  [ROLES.TEACHER]: 2,
  [ROLES.ACADEMIC_DIRECTOR]: 3,
  [ROLES.RESEARCH_LEADER]: 4,
  [ROLES.DEAN]: 5,
  [ROLES.ADMIN]: 6
}

// 角色注册方式
export const ROLE_REGISTRATION_METHODS = {
  [ROLES.STUDENT]: 'self_register',      // 自主注册
  [ROLES.TEACHER]: 'admin_assign',       // 管理员分配
  [ROLES.PARENT]: 'invitation',          // 邀请注册
  [ROLES.ACADEMIC_DIRECTOR]: 'admin_assign', // 管理员分配
  [ROLES.RESEARCH_LEADER]: 'admin_assign',    // 管理员分配
  [ROLES.DEAN]: 'admin_assign',          // 管理员分配
  [ROLES.ADMIN]: 'system_assign'         // 系统分配
}

// 角色描述
export const ROLE_DESCRIPTIONS = {
  [ROLES.STUDENT]: '学习系统的主要用户，拥有完整的学习功能权限',
  [ROLES.TEACHER]: '自由教师，拥有教学管理和内容创建权限',
  [ROLES.PARENT]: '学生家长，可以查看学生学习进度和参与互动',
  [ROLES.ACADEMIC_DIRECTOR]: '教务主任，负责课程和教学质量管理',
  [ROLES.RESEARCH_LEADER]: '教研组长，负责教学研究和数据分析',
  [ROLES.DEAN]: '教导主任，拥有高级管理权限',
  [ROLES.ADMIN]: '系统管理员，拥有最高权限'
}

/**
 * 获取角色的所有权限（包括继承的权限）
 * @param {string} role - 角色名称
 * @returns {Array} 权限列表
 */
export function getRolePermissions(role) {
  if (!role || !ROLE_PERMISSIONS[role]) {
    return []
  }
  
  const permissions = new Set(ROLE_PERMISSIONS[role])
  
  // 添加继承的权限
  const inheritedRoles = ROLE_INHERITANCE[role] || []
  inheritedRoles.forEach(inheritedRole => {
    if (ROLE_PERMISSIONS[inheritedRole]) {
      ROLE_PERMISSIONS[inheritedRole].forEach(permission => {
        permissions.add(permission)
      })
    }
  })
  
  return Array.from(permissions)
}

/**
 * 检查角色是否有指定权限
 * @param {string} role - 角色名称
 * @param {string} permission - 权限名称
 * @returns {boolean} 是否有权限
 */
export function roleHasPermission(role, permission) {
  const permissions = getRolePermissions(role)
  return permissions.includes(permission)
}

/**
 * 检查角色是否高于另一个角色
 * @param {string} role1 - 角色1
 * @param {string} role2 - 角色2
 * @returns {boolean} role1是否高于role2
 */
export function isRoleHigher(role1, role2) {
  const hierarchy1 = ROLE_HIERARCHY[role1] || 0
  const hierarchy2 = ROLE_HIERARCHY[role2] || 0
  return hierarchy1 > hierarchy2
}

/**
 * 获取角色可以管理的下级角色
 * @param {string} role - 角色名称
 * @returns {Array} 可管理的角色列表
 */
export function getManageableRoles(role) {
  const currentHierarchy = ROLE_HIERARCHY[role] || 0
  return Object.keys(ROLE_HIERARCHY).filter(r => 
    ROLE_HIERARCHY[r] < currentHierarchy
  )
}