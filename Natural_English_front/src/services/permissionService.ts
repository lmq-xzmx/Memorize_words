// 权限管理服务 - 支持新的权限验证和审计功能
import axios from 'axios'
import type { AxiosResponse } from 'axios'

// 权限相关接口定义
export interface Permission {
  id: string
  name: string
  description: string
  category: string
  codename?: string
  content_type?: string
}

export interface UserPermissions {
  userId: number
  username: string
  role: string
  permissions: string[]
  groups: string[]
  isActive: boolean
  lastUpdated: string
}

export interface PermissionCheck {
  permission: string
  hasPermission: boolean
  reason?: string
  source?: 'role' | 'direct' | 'group'
}

export interface PermissionValidationResult {
  isValid: boolean
  issues: {
    type: 'missing' | 'conflict' | 'deprecated'
    permission: string
    description: string
    severity: 'low' | 'medium' | 'high'
  }[]
  recommendations: string[]
}

export interface SecurityReport {
  id: string
  generatedAt: string
  summary: {
    totalUsers: number
    totalRoles: number
    totalPermissions: number
    securityIssues: number
    riskLevel: 'low' | 'medium' | 'high'
  }
  details: {
    userPermissionIssues: number
    roleConfigurationIssues: number
    securityViolations: number
    auditLogAlerts: number
  }
  recommendations: string[]
  downloadUrl?: string
}

// API响应接口
interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

class PermissionService {
  private baseURL = '/api/permissions'
  private unifiedURL = '/api/permissions'

  // 权限检查 API
  async checkPermission(permission: string, userId?: number): Promise<PermissionCheck> {
    try {
      const params = userId ? { userId } : {}
      const response: AxiosResponse<ApiResponse<PermissionCheck>> = 
        await axios.get(`${this.unifiedURL}/check/`, { params: { permission, ...params } })
      return response.data.data || { permission, hasPermission: false }
    } catch (error) {
      console.error('权限检查失败:', error)
      return { permission, hasPermission: false, reason: '检查失败' }
    }
  }

  async batchCheckPermissions(permissions: string[], userId?: number): Promise<PermissionCheck[]> {
    try {
      const response: AxiosResponse<ApiResponse<PermissionCheck[]>> = 
        await axios.post(`${this.unifiedURL}/batch/check/`, { permissions, userId })
      return response.data.data || []
    } catch (error) {
      console.error('批量权限检查失败:', error)
      return permissions.map(permission => ({ permission, hasPermission: false, reason: '检查失败' }))
    }
  }

  async getUserPermissions(userId?: number): Promise<UserPermissions> {
    try {
      const params = userId ? { userId } : {}
      const response: AxiosResponse<ApiResponse<any>> = 
        await axios.get(`${this.baseURL}/user-permissions/`, { params })
      const data = response.data.data
      if (data) {
        // 适配后端返回的数据格式
        return {
          userId: data.user_id || data.userId || 0,
          username: data.username || '',
          role: data.role || '',
          permissions: data.permissions || [],
          groups: data.groups || [],
          isActive: data.isActive !== undefined ? data.isActive : true,
          lastUpdated: data.lastUpdated || new Date().toISOString()
        }
      }
      return {
        userId: 0,
        username: '',
        role: '',
        permissions: [],
        groups: [],
        isActive: false,
        lastUpdated: ''
      }
    } catch (error) {
      console.error('获取用户权限失败:', error)
      throw error
    }
  }

  async getUserRole(userId?: number): Promise<{ role: string, displayName: string, permissions: string[] }> {
    try {
      const params = userId ? { userId } : {}
      const response: AxiosResponse<ApiResponse<{ role: string, displayName: string, permissions: string[] }>> = 
        await axios.get(`${this.unifiedURL}/user/role/`, { params })
      return response.data.data || { role: '', displayName: '', permissions: [] }
    } catch (error) {
      console.error('获取用户角色失败:', error)
      throw error
    }
  }

  // 权限配置 API
  async getAllPermissions(): Promise<Permission[]> {
    try {
      const response: AxiosResponse<ApiResponse<Permission[]>> = 
        await axios.get(`${this.baseURL}/permissions/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取权限列表失败:', error)
      throw error
    }
  }

  async getPermissionsByCategory(category: string): Promise<Permission[]> {
    try {
      const response: AxiosResponse<ApiResponse<Permission[]>> = 
        await axios.get(`${this.baseURL}/permissions/`, { params: { category } })
      return response.data.data || []
    } catch (error) {
      console.error('获取分类权限失败:', error)
      throw error
    }
  }

  async getRolePermissions(role: string): Promise<string[]> {
    try {
      const response: AxiosResponse<ApiResponse<string[]>> = 
        await axios.get(`${this.unifiedURL}/role/permissions/`, { params: { role } })
      return response.data.data || []
    } catch (error) {
      console.error('获取角色权限失败:', error)
      throw error
    }
  }

  async updateRolePermissions(role: string, permissions: string[]): Promise<void> {
    try {
      await axios.post(`${this.unifiedURL}/role/permissions/`, { role, permissions })
    } catch (error) {
      console.error('更新角色权限失败:', error)
      throw error
    }
  }

  // 菜单权限 API
  async getRoleMenus(role?: string): Promise<any[]> {
    try {
      const params = role ? { role } : {}
      const response: AxiosResponse<ApiResponse<any[]>> = 
        await axios.get(`${this.unifiedURL}/role/menus/`, { params })
      return response.data.data || []
    } catch (error) {
      console.error('获取角色菜单失败:', error)
      throw error
    }
  }

  async updateRoleMenus(role: string, menuIds: string[]): Promise<void> {
    try {
      await axios.post(`${this.unifiedURL}/role/menus/`, { role, menuIds })
    } catch (error) {
      console.error('更新角色菜单失败:', error)
      throw error
    }
  }

  // 权限验证 API
  async validateUserPermissions(userId: number): Promise<PermissionValidationResult> {
    try {
      const response: AxiosResponse<ApiResponse<PermissionValidationResult>> = 
        await axios.post(`${this.baseURL}/validate-permissions/`, { userId })
      return response.data.data || { isValid: false, issues: [], recommendations: [] }
    } catch (error) {
      console.error('验证用户权限失败:', error)
      throw error
    }
  }

  async validateRoleConfiguration(role: string): Promise<PermissionValidationResult> {
    try {
      const response: AxiosResponse<ApiResponse<PermissionValidationResult>> = 
        await axios.post(`${this.baseURL}/validate-role/`, { role })
      return response.data.data || { isValid: false, issues: [], recommendations: [] }
    } catch (error) {
      console.error('验证角色配置失败:', error)
      throw error
    }
  }

  async validateSystemPermissions(): Promise<PermissionValidationResult> {
    try {
      const response: AxiosResponse<ApiResponse<PermissionValidationResult>> = 
        await axios.post(`${this.baseURL}/validate-system/`)
      return response.data.data || { isValid: false, issues: [], recommendations: [] }
    } catch (error) {
      console.error('验证系统权限失败:', error)
      throw error
    }
  }

  // 安全报告 API
  async generateSecurityReport(): Promise<SecurityReport> {
    try {
      const response: AxiosResponse<ApiResponse<SecurityReport>> = 
        await axios.post(`${this.baseURL}/security-report/`)
      return response.data.data || {
        id: '',
        generatedAt: '',
        summary: { totalUsers: 0, totalRoles: 0, totalPermissions: 0, securityIssues: 0, riskLevel: 'low' },
        details: { userPermissionIssues: 0, roleConfigurationIssues: 0, securityViolations: 0, auditLogAlerts: 0 },
        recommendations: []
      }
    } catch (error) {
      console.error('生成安全报告失败:', error)
      throw error
    }
  }

  async getSecurityReports(params?: {
    page?: number
    pageSize?: number
    startDate?: string
    endDate?: string
  }): Promise<{ reports: SecurityReport[], total: number }> {
    try {
      const response: AxiosResponse<ApiResponse<{ reports: SecurityReport[], total: number }>> = 
        await axios.get(`${this.baseURL}/security-reports/`, { params })
      return response.data.data || { reports: [], total: 0 }
    } catch (error) {
      console.error('获取安全报告失败:', error)
      throw error
    }
  }

  async downloadSecurityReport(reportId: string, format: 'pdf' | 'excel' | 'csv' = 'pdf'): Promise<Blob> {
    try {
      const response = await axios.get(`${this.baseURL}/security-reports/${reportId}/download/`, {
        params: { format },
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('下载安全报告失败:', error)
      throw error
    }
  }

  // 缓存管理 API
  async clearPermissionCache(userId?: number): Promise<void> {
    try {
      const params = userId ? { userId } : {}
      await axios.post(`${this.unifiedURL}/cache/clear/`, params)
    } catch (error) {
      console.error('清除权限缓存失败:', error)
      throw error
    }
  }

  async getCacheStats(): Promise<{
    totalCacheSize: number
    userCacheCount: number
    roleCacheCount: number
    hitRate: number
    lastClearTime: string
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        totalCacheSize: number
        userCacheCount: number
        roleCacheCount: number
        hitRate: number
        lastClearTime: string
      }>> = await axios.get(`${this.unifiedURL}/cache/stats/`)
      return response.data.data || {
        totalCacheSize: 0,
        userCacheCount: 0,
        roleCacheCount: 0,
        hitRate: 0,
        lastClearTime: ''
      }
    } catch (error) {
      console.error('获取缓存统计失败:', error)
      throw error
    }
  }

  // 权限统计 API
  async getPermissionStats(): Promise<{
    totalPermissions: number
    activePermissions: number
    unusedPermissions: number
    mostUsedPermissions: { permission: string, count: number }[]
    leastUsedPermissions: { permission: string, count: number }[]
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        totalPermissions: number
        activePermissions: number
        unusedPermissions: number
        mostUsedPermissions: { permission: string, count: number }[]
        leastUsedPermissions: { permission: string, count: number }[]
      }>> = await axios.get(`${this.unifiedURL}/stats/overview/`)
      return response.data.data || {
        totalPermissions: 0,
        activePermissions: 0,
        unusedPermissions: 0,
        mostUsedPermissions: [],
        leastUsedPermissions: []
      }
    } catch (error) {
      console.error('获取权限统计失败:', error)
      throw error
    }
  }

  async getPermissionUsage(params?: {
    startDate?: string
    endDate?: string
    permission?: string
    userId?: number
  }): Promise<{
    usage: { date: string, count: number }[]
    topUsers: { userId: number, username: string, count: number }[]
    topPermissions: { permission: string, count: number }[]
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        usage: { date: string, count: number }[]
        topUsers: { userId: number, username: string, count: number }[]
        topPermissions: { permission: string, count: number }[]
      }>> = await axios.get(`${this.unifiedURL}/stats/usage/`, { params })
      return response.data.data || {
        usage: [],
        topUsers: [],
        topPermissions: []
      }
    } catch (error) {
      console.error('获取权限使用统计失败:', error)
      throw error
    }
  }

  // 前端权限同步 API
  async syncFrontendPermissions(): Promise<{
    synced: number
    failed: number
    errors: string[]
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        synced: number
        failed: number
        errors: string[]
      }>> = await axios.post(`${this.unifiedURL}/sync/frontend/`)
      return response.data.data || { synced: 0, failed: 0, errors: [] }
    } catch (error) {
      console.error('同步前端权限失败:', error)
      throw error
    }
  }

  async getSyncStatus(): Promise<{
    lastSyncTime: string
    syncStatus: 'success' | 'failed' | 'pending'
    frontendVersion: string
    backendVersion: string
    differences: string[]
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        lastSyncTime: string
        syncStatus: 'success' | 'failed' | 'pending'
        frontendVersion: string
        backendVersion: string
        differences: string[]
      }>> = await axios.get(`${this.unifiedURL}/sync/status/`)
      return response.data.data || {
        lastSyncTime: '',
        syncStatus: 'pending',
        frontendVersion: '',
        backendVersion: '',
        differences: []
      }
    } catch (error) {
      console.error('获取同步状态失败:', error)
      throw error
    }
  }
}

export default new PermissionService()