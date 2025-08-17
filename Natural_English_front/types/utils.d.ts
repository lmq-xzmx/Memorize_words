// 用户接口定义
export interface User {
  id: string | number
  username: string
  role: string
  email?: string
  [key: string]: any
}

// 权限缓存状态接口
export interface PermissionCacheStatus {
  loaded: boolean
  lastUpdate: Date | null
  syncing: boolean
}

// 权限工具函数类型定义
export declare function hasPermission(permissions: string[], permission: string): boolean
export declare function hasAnyPermission(permissions: string[], permissionList: string[]): boolean
export declare function hasAllPermissions(permissions: string[], permissionList: string[]): boolean
export declare function canAccessPage(permissions: string[], pagePath: string): boolean
export declare function getAccessiblePages(permissions: string[]): string[]
export declare function isAuthenticated(): boolean
export declare function getCurrentUser(): Promise<User | null>
export declare function getRoleDisplayName(role: string): string
export declare function getPermissionDisplayName(permission: string): string
export declare function getCategoryDisplayName(category: string): string
export declare function getAccessibleMenus(permissions: string[]): any[]
export declare function getDefaultPageForRole(role: string): string
export declare function clearAuth(): void
export declare function clearPermissionCache(): void
export declare function getCachedPermissions(): string[]
export declare function setCachedPermissions(permissions: string[]): void

// 角色常量类型定义
export declare const ROLES: {
  ADMIN: string
  DEAN: string
  ACADEMIC_DIRECTOR: string
  RESEARCH_LEADER: string
  TEACHER: string
  PARENT: string
  STUDENT: string
}

export declare const ROLE_DISPLAY_NAMES: Record<string, string>
export declare function getRolePermissions(role: string): string[]
export declare function roleHasPermission(role: string, permission: string): boolean
export declare function isRoleHigher(userRole: string, targetRole: string): boolean
export declare function getManageableRoles(role: string): string[]

// 权限常量类型定义
export declare const ALL_PERMISSIONS: string[]
export declare const PERMISSION_CATEGORIES: Record<string, string[]>
export declare const PERMISSION_DISPLAY_NAMES: Record<string, string>
export declare const LEARNING_PERMISSIONS: string[]
export declare const CONTENT_PERMISSIONS: string[]
export declare const SOCIAL_PERMISSIONS: string[]
export declare const MANAGEMENT_PERMISSIONS: string[]
export declare const SYSTEM_PERMISSIONS: string[]
export declare const ADVANCED_PERMISSIONS: string[]

// 学习模式权限类型定义
export declare const PAGE_PERMISSIONS: Record<string, string[]>
export declare function getAccessibleLearningModes(permissions: string[]): string[]
export declare function pageRequiresAuth(pagePath: string): boolean