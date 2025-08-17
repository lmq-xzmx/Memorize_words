// JavaScript模块的类型声明
declare module '../utils/permission.js' {
  import type { User } from './utils'
  
  export function hasPermission(permissions: string[], permission: string): boolean
  export function hasAnyPermission(permissions: string[], permissionList: string[]): boolean
  export function hasAllPermissions(permissions: string[], permissionList: string[]): boolean
  export function canAccessPage(permissions: string[], pagePath: string): boolean
  export function getAccessiblePages(permissions: string[]): string[]
  export function isAuthenticated(): boolean
  export function getCurrentUser(): Promise<User | null>
  export function getRoleDisplayName(role: string): string
  export function getPermissionDisplayName(permission: string): string
  export function getCategoryDisplayName(category: string): string
  export function getAccessibleMenus(permissions: string[]): any[]
  export function getDefaultPageForRole(role: string): string
  export function clearAuth(): void
  export function clearPermissionCache(): void
  export function getCachedPermissions(): string[]
  export function setCachedPermissions(permissions: string[]): void
  export const permissionSyncManager: any
}

declare module '../utils/roleDefinitions.js' {
  export const ROLES: {
    ADMIN: string
    DEAN: string
    ACADEMIC_DIRECTOR: string
    RESEARCH_LEADER: string
    TEACHER: string
    PARENT: string
    STUDENT: string
  }
  export const ROLE_DISPLAY_NAMES: Record<string, string>
  export function getRolePermissions(role: string): string[]
  export function roleHasPermission(role: string, permission: string): boolean
  export function isRoleHigher(userRole: string, targetRole: string): boolean
  export function getManageableRoles(role: string): string[]
}

declare module '../utils/permissionConstants.js' {
  export const ALL_PERMISSIONS: string[]
  export const PERMISSION_CATEGORIES: Record<string, string[]>
  export const PERMISSION_DISPLAY_NAMES: Record<string, string>
  export const LEARNING_PERMISSIONS: string[]
  export const CONTENT_PERMISSIONS: string[]
  export const SOCIAL_PERMISSIONS: string[]
  export const MANAGEMENT_PERMISSIONS: string[]
  export const SYSTEM_PERMISSIONS: string[]
  export const ADVANCED_PERMISSIONS: string[]
}

declare module '../utils/learningModePermissions.js' {
  export const PAGE_PERMISSIONS: Record<string, string[]>
  export function getAccessibleLearningModes(permissions: string[]): string[]
  export function pageRequiresAuth(pagePath: string): boolean
}

// 通用模块声明，处理没有.js扩展名的导入
declare module '../utils/permission' {
  export * from '../utils/permission'
}

declare module '../utils/roleDefinitions' {
  export * from '../utils/roleDefinitions'
}

declare module '../utils/permissionConstants' {
  export * from '../utils/permissionConstants'
}

declare module '../utils/learningModePermissions' {
  export * from '../utils/learningModePermissions'
}