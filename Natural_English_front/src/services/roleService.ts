// 角色管理服务 - 适配新的3层架构设计
import axios from 'axios'
import type { AxiosResponse } from 'axios'

// 角色相关接口定义
export interface Role {
  id: number
  role: string
  display_name: string
  description: string
  is_active: boolean
  parent?: number
  sort_order: number
  permissions: string[]
  user_count: number
  created_at: string
  updated_at: string
}

export interface RoleTemplate {
  id: number
  role: string
  template_name: string
  description: string
  is_active: boolean
  auto_assign: boolean
  permissions: string[]
  menu_permissions: string[]
  created_at: string
}

export interface RoleGroupMapping {
  id: number
  role: string
  django_group: string
  is_active: boolean
  auto_sync: boolean
  created_at: string
}

export interface PermissionAuditLog {
  id: number
  action_type: string
  result: string
  risk_level: string
  user: string
  target_user?: string
  resource?: string
  permission?: string
  role?: string
  description: string
  ip_address: string
  created_at: string
}

export interface SecurityRule {
  id: number
  rule_type: string
  name: string
  description: string
  is_active: boolean
  rule_config: Record<string, any>
  created_at: string
}

// API响应接口
interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

class RoleService {
  private baseURL = '/api/permissions'
  private accountsURL = '/api/accounts'

  // 核心管理层 API
  async getRoles(): Promise<Role[]> {
    try {
      const response: AxiosResponse<ApiResponse<Role[]>> = await axios.get(`${this.baseURL}/roles/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取角色列表失败:', error)
      throw error
    }
  }

  async createRole(roleData: Partial<Role>): Promise<Role> {
    try {
      const response: AxiosResponse<ApiResponse<Role>> = await axios.post(`${this.baseURL}/roles/`, roleData)
      return response.data.data!
    } catch (error) {
      console.error('创建角色失败:', error)
      throw error
    }
  }

  async updateRole(id: number, roleData: Partial<Role>): Promise<Role> {
    try {
      const response: AxiosResponse<ApiResponse<Role>> = await axios.put(`${this.baseURL}/roles/${id}/`, roleData)
      return response.data.data!
    } catch (error) {
      console.error('更新角色失败:', error)
      throw error
    }
  }

  async deleteRole(id: number): Promise<void> {
    try {
      await axios.delete(`${this.baseURL}/roles/${id}/`)
    } catch (error) {
      console.error('删除角色失败:', error)
      throw error
    }
  }

  async getRolePermissions(roleId: number): Promise<string[]> {
    try {
      const response: AxiosResponse<ApiResponse<string[]>> = await axios.get(`${this.baseURL}/roles/${roleId}/permissions/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取角色权限失败:', error)
      throw error
    }
  }

  async updateRolePermissions(roleId: number, permissions: string[]): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/roles/${roleId}/permissions/`, { permissions })
    } catch (error) {
      console.error('更新角色权限失败:', error)
      throw error
    }
  }

  // 注册配置层 API
  async getRoleTemplates(): Promise<RoleTemplate[]> {
    try {
      const response: AxiosResponse<ApiResponse<RoleTemplate[]>> = await axios.get(`${this.accountsURL}/role-templates/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取角色模板失败:', error)
      throw error
    }
  }

  async createRoleTemplate(templateData: Partial<RoleTemplate>): Promise<RoleTemplate> {
    try {
      const response: AxiosResponse<ApiResponse<RoleTemplate>> = await axios.post(`${this.accountsURL}/role-templates/`, templateData)
      return response.data.data!
    } catch (error) {
      console.error('创建角色模板失败:', error)
      throw error
    }
  }

  async updateRoleTemplate(id: number, templateData: Partial<RoleTemplate>): Promise<RoleTemplate> {
    try {
      const response: AxiosResponse<ApiResponse<RoleTemplate>> = await axios.put(`${this.accountsURL}/role-templates/${id}/`, templateData)
      return response.data.data!
    } catch (error) {
      console.error('更新角色模板失败:', error)
      throw error
    }
  }

  async deleteRoleTemplate(id: number): Promise<void> {
    try {
      await axios.delete(`${this.accountsURL}/role-templates/${id}/`)
    } catch (error) {
      console.error('删除角色模板失败:', error)
      throw error
    }
  }

  // 权限同步层 API
  async getRoleGroupMappings(): Promise<RoleGroupMapping[]> {
    try {
      const response: AxiosResponse<ApiResponse<RoleGroupMapping[]>> = await axios.get(`${this.baseURL}/role-group-mappings/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取角色组映射失败:', error)
      throw error
    }
  }

  async syncRoleToGroup(role: string): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/sync-role-to-group/`, { role })
    } catch (error) {
      console.error('同步角色到组失败:', error)
      throw error
    }
  }

  async syncAllRolesToGroups(): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/sync-all-roles-to-groups/`)
    } catch (error) {
      console.error('同步所有角色到组失败:', error)
      throw error
    }
  }

  // 权限审计 API
  async getAuditLogs(params?: {
    page?: number
    pageSize?: number
    actionType?: string
    riskLevel?: string
    startDate?: string
    endDate?: string
  }): Promise<{ logs: PermissionAuditLog[], total: number }> {
    try {
      const response: AxiosResponse<ApiResponse<{ logs: PermissionAuditLog[], total: number }>> = 
        await axios.get(`${this.baseURL}/audit-logs/`, { params })
      return response.data.data || { logs: [], total: 0 }
    } catch (error) {
      console.error('获取审计日志失败:', error)
      throw error
    }
  }

  async getSecurityRules(): Promise<SecurityRule[]> {
    try {
      const response: AxiosResponse<ApiResponse<SecurityRule[]>> = await axios.get(`${this.baseURL}/security-rules/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取安全规则失败:', error)
      throw error
    }
  }

  async createSecurityRule(ruleData: Partial<SecurityRule>): Promise<SecurityRule> {
    try {
      const response: AxiosResponse<ApiResponse<SecurityRule>> = await axios.post(`${this.baseURL}/security-rules/`, ruleData)
      return response.data.data!
    } catch (error) {
      console.error('创建安全规则失败:', error)
      throw error
    }
  }

  async updateSecurityRule(id: number, ruleData: Partial<SecurityRule>): Promise<SecurityRule> {
    try {
      const response: AxiosResponse<ApiResponse<SecurityRule>> = await axios.put(`${this.baseURL}/security-rules/${id}/`, ruleData)
      return response.data.data!
    } catch (error) {
      console.error('更新安全规则失败:', error)
      throw error
    }
  }

  async deleteSecurityRule(id: number): Promise<void> {
    try {
      await axios.delete(`${this.baseURL}/security-rules/${id}/`)
    } catch (error) {
      console.error('删除安全规则失败:', error)
      throw error
    }
  }

  // 权限验证 API
  async validateUserPermissions(userId: number): Promise<{ isValid: boolean, issues: string[] }> {
    try {
      const response: AxiosResponse<ApiResponse<{ isValid: boolean, issues: string[] }>> = 
        await axios.post(`${this.baseURL}/validate-user-permissions/`, { userId })
      return response.data.data || { isValid: false, issues: [] }
    } catch (error) {
      console.error('验证用户权限失败:', error)
      throw error
    }
  }

  async generateSecurityReport(): Promise<{ reportUrl: string }> {
    try {
      const response: AxiosResponse<ApiResponse<{ reportUrl: string }>> = 
        await axios.post(`${this.baseURL}/generate-security-report/`)
      return response.data.data || { reportUrl: '' }
    } catch (error) {
      console.error('生成安全报告失败:', error)
      throw error
    }
  }

  // 统计信息 API
  async getRoleStats(): Promise<{
    totalRoles: number
    activeRoles: number
    totalUsers: number
    totalPermissions: number
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        totalRoles: number
        activeRoles: number
        totalUsers: number
        totalPermissions: number
      }>> = await axios.get(`${this.baseURL}/stats/`)
      return response.data.data || { totalRoles: 0, activeRoles: 0, totalUsers: 0, totalPermissions: 0 }
    } catch (error) {
      console.error('获取角色统计失败:', error)
      throw error
    }
  }

  // 批量操作 API
  async batchUpdateRoles(operations: {
    action: 'activate' | 'deactivate' | 'delete'
    roleIds: number[]
  }): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/batch-update-roles/`, operations)
    } catch (error) {
      console.error('批量更新角色失败:', error)
      throw error
    }
  }

  async exportRoles(format: 'json' | 'csv' | 'excel' = 'json'): Promise<Blob> {
    try {
      const response = await axios.get(`${this.baseURL}/export-roles/`, {
        params: { format },
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('导出角色失败:', error)
      throw error
    }
  }

  async importRoles(file: File): Promise<{ success: number, failed: number, errors: string[] }> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response: AxiosResponse<ApiResponse<{ success: number, failed: number, errors: string[] }>> = 
        await axios.post(`${this.baseURL}/import-roles/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      return response.data.data || { success: 0, failed: 0, errors: [] }
    } catch (error) {
      console.error('导入角色失败:', error)
      throw error
    }
  }
}

export default new RoleService()