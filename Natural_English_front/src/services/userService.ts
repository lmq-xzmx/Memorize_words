// 用户管理服务 - 支持新的3层架构设计
import axios from 'axios'
import type { AxiosResponse } from 'axios'

// 用户相关接口定义
export interface User {
  id: number
  username: string
  email: string
  firstName?: string
  lastName?: string
  displayName?: string
  avatar?: string
  role: string
  roleDisplayName?: string
  groups: string[]
  permissions: string[]
  isActive: boolean
  isStaff: boolean
  isSuperuser: boolean
  dateJoined: string
  lastLogin?: string
  profile?: UserProfile
  learningProgress?: LearningProgress
}

export interface UserProfile {
  id: number
  userId: number
  phone?: string
  address?: string
  birthDate?: string
  gender?: 'M' | 'F' | 'O'
  bio?: string
  preferences: {
    language: string
    theme: 'light' | 'dark' | 'auto'
    notifications: {
      email: boolean
      push: boolean
      sms: boolean
    }
    privacy: {
      showProfile: boolean
      showProgress: boolean
      allowMessages: boolean
    }
  }
  createdAt: string
  updatedAt: string
}

export interface LearningProgress {
  id: number
  userId: number
  totalWords: number
  masteredWords: number
  studyDays: number
  totalStudyTime: number
  currentLevel: string
  achievements: string[]
  weeklyGoal: number
  weeklyProgress: number
  lastStudyDate?: string
  streakDays: number
  updatedAt: string
}

export interface UserCreateRequest {
  username: string
  email: string
  password: string
  firstName?: string
  lastName?: string
  role?: string
  groups?: string[]
  permissions?: string[]
  isActive?: boolean
  profile?: Partial<UserProfile>
}

export interface UserUpdateRequest {
  username?: string
  email?: string
  firstName?: string
  lastName?: string
  role?: string
  groups?: string[]
  permissions?: string[]
  isActive?: boolean
  profile?: Partial<UserProfile>
}

export interface UserListParams {
  page?: number
  pageSize?: number
  search?: string
  role?: string
  group?: string
  isActive?: boolean
  orderBy?: string
  orderDirection?: 'asc' | 'desc'
  dateFrom?: string
  dateTo?: string
}

export interface UserListResponse {
  users: User[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface UserStats {
  totalUsers: number
  activeUsers: number
  newUsersThisMonth: number
  usersByRole: { role: string, count: number }[]
  usersByGroup: { group: string, count: number }[]
  recentRegistrations: User[]
  topLearners: User[]
}

export interface BatchOperation {
  action: 'activate' | 'deactivate' | 'delete' | 'updateRole' | 'addToGroup' | 'removeFromGroup'
  userIds: number[]
  params?: {
    role?: string
    group?: string
    reason?: string
  }
}

export interface BatchOperationResult {
  success: number
  failed: number
  errors: {
    userId: number
    error: string
  }[]
  details: string
}

// API响应接口
interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

class UserService {
  private baseURL = '/api/accounts'
  private unifiedURL = '/api/accounts/unified'

  // 用户基础 API
  async getUsers(params?: UserListParams): Promise<UserListResponse> {
    try {
      const response: AxiosResponse<ApiResponse<UserListResponse>> = 
        await axios.get(`${this.baseURL}/users/`, { params })
      return response.data.data || { users: [], total: 0, page: 1, pageSize: 10, totalPages: 0 }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      throw error
    }
  }

  async getUser(userId: number): Promise<User> {
    try {
      const response: AxiosResponse<ApiResponse<User>> = 
        await axios.get(`${this.baseURL}/users/${userId}/`)
      return response.data.data!
    } catch (error) {
      console.error('获取用户详情失败:', error)
      throw error
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response: AxiosResponse<ApiResponse<User>> = 
        await axios.get(`${this.baseURL}/users/me/`)
      return response.data.data!
    } catch (error) {
      console.error('获取当前用户信息失败:', error)
      throw error
    }
  }

  async createUser(userData: UserCreateRequest): Promise<User> {
    try {
      const response: AxiosResponse<ApiResponse<User>> = 
        await axios.post(`${this.baseURL}/users/`, userData)
      return response.data.data!
    } catch (error) {
      console.error('创建用户失败:', error)
      throw error
    }
  }

  async updateUser(userId: number, userData: UserUpdateRequest): Promise<User> {
    try {
      const response: AxiosResponse<ApiResponse<User>> = 
        await axios.patch(`${this.baseURL}/users/${userId}/`, userData)
      return response.data.data!
    } catch (error) {
      console.error('更新用户失败:', error)
      throw error
    }
  }

  async deleteUser(userId: number): Promise<void> {
    try {
      await axios.delete(`${this.baseURL}/users/${userId}/`)
    } catch (error) {
      console.error('删除用户失败:', error)
      throw error
    }
  }

  async activateUser(userId: number): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/activate/`)
    } catch (error) {
      console.error('激活用户失败:', error)
      throw error
    }
  }

  async deactivateUser(userId: number, reason?: string): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/deactivate/`, { reason })
    } catch (error) {
      console.error('停用用户失败:', error)
      throw error
    }
  }

  // 用户角色管理 API
  async getUsersByRole(role: string, params?: Omit<UserListParams, 'role'>): Promise<UserListResponse> {
    try {
      const response: AxiosResponse<ApiResponse<UserListResponse>> = 
        await axios.get(`${this.unifiedURL}/roles/${role}/users/`, { params })
      return response.data.data || { users: [], total: 0, page: 1, pageSize: 10, totalPages: 0 }
    } catch (error) {
      console.error('获取角色用户失败:', error)
      throw error
    }
  }

  async updateUserRole(userId: number, role: string): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/role/`, { role })
    } catch (error) {
      console.error('更新用户角色失败:', error)
      throw error
    }
  }

  async getUserRoleHistory(userId: number): Promise<{
    id: number
    userId: number
    oldRole: string
    newRole: string
    changedBy: string
    changedAt: string
    reason?: string
  }[]> {
    try {
      const response: AxiosResponse<ApiResponse<{
        id: number
        userId: number
        oldRole: string
        newRole: string
        changedBy: string
        changedAt: string
        reason?: string
      }[]>> = await axios.get(`${this.baseURL}/users/${userId}/role-history/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取用户角色历史失败:', error)
      throw error
    }
  }

  // 用户组管理 API
  async addUserToGroup(userId: number, group: string): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/groups/`, { group })
    } catch (error) {
      console.error('添加用户到组失败:', error)
      throw error
    }
  }

  async removeUserFromGroup(userId: number, group: string): Promise<void> {
    try {
      await axios.delete(`${this.baseURL}/users/${userId}/groups/${group}/`)
    } catch (error) {
      console.error('从组中移除用户失败:', error)
      throw error
    }
  }

  async getUserGroups(userId: number): Promise<string[]> {
    try {
      const response: AxiosResponse<ApiResponse<string[]>> = 
        await axios.get(`${this.baseURL}/users/${userId}/groups/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取用户组失败:', error)
      throw error
    }
  }

  // 用户权限管理 API
  async getUserPermissions(userId: number): Promise<string[]> {
    try {
      const response: AxiosResponse<ApiResponse<string[]>> = 
        await axios.get(`${this.baseURL}/users/${userId}/permissions/`)
      return response.data.data || []
    } catch (error) {
      console.error('获取用户权限失败:', error)
      throw error
    }
  }

  async updateUserPermissions(userId: number, permissions: string[]): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/permissions/`, { permissions })
    } catch (error) {
      console.error('更新用户权限失败:', error)
      throw error
    }
  }

  async addUserPermission(userId: number, permission: string): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/permissions/add/`, { permission })
    } catch (error) {
      console.error('添加用户权限失败:', error)
      throw error
    }
  }

  async removeUserPermission(userId: number, permission: string): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/permissions/remove/`, { permission })
    } catch (error) {
      console.error('移除用户权限失败:', error)
      throw error
    }
  }

  // 用户档案管理 API
  async getUserProfile(userId: number): Promise<UserProfile> {
    try {
      const response: AxiosResponse<ApiResponse<UserProfile>> = 
        await axios.get(`${this.baseURL}/users/${userId}/profile/`)
      return response.data.data!
    } catch (error) {
      console.error('获取用户档案失败:', error)
      throw error
    }
  }

  async updateUserProfile(userId: number, profileData: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const response: AxiosResponse<ApiResponse<UserProfile>> = 
        await axios.patch(`${this.baseURL}/users/${userId}/profile/`, profileData)
      return response.data.data!
    } catch (error) {
      console.error('更新用户档案失败:', error)
      throw error
    }
  }

  async uploadUserAvatar(userId: number, file: File): Promise<{ avatarUrl: string }> {
    try {
      const formData = new FormData()
      formData.append('avatar', file)
      const response: AxiosResponse<ApiResponse<{ avatarUrl: string }>> = 
        await axios.post(`${this.baseURL}/users/${userId}/avatar/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      return response.data.data!
    } catch (error) {
      console.error('上传用户头像失败:', error)
      throw error
    }
  }

  // 学习进度管理 API
  async getUserLearningProgress(userId: number): Promise<LearningProgress> {
    try {
      const response: AxiosResponse<ApiResponse<LearningProgress>> = 
        await axios.get(`${this.baseURL}/users/${userId}/learning-progress/`)
      return response.data.data!
    } catch (error) {
      console.error('获取学习进度失败:', error)
      throw error
    }
  }

  async updateLearningProgress(userId: number, progressData: Partial<LearningProgress>): Promise<LearningProgress> {
    try {
      const response: AxiosResponse<ApiResponse<LearningProgress>> = 
        await axios.patch(`${this.baseURL}/users/${userId}/learning-progress/`, progressData)
      return response.data.data!
    } catch (error) {
      console.error('更新学习进度失败:', error)
      throw error
    }
  }

  async resetLearningProgress(userId: number): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/users/${userId}/learning-progress/reset/`)
    } catch (error) {
      console.error('重置学习进度失败:', error)
      throw error
    }
  }

  // 用户统计 API
  async getUserStats(): Promise<UserStats> {
    try {
      const response: AxiosResponse<ApiResponse<UserStats>> = 
        await axios.get(`${this.baseURL}/stats/overview/`)
      return response.data.data || {
        totalUsers: 0,
        activeUsers: 0,
        newUsersThisMonth: 0,
        usersByRole: [],
        usersByGroup: [],
        recentRegistrations: [],
        topLearners: []
      }
    } catch (error) {
      console.error('获取用户统计失败:', error)
      throw error
    }
  }

  async getUserActivity(userId: number, params?: {
    startDate?: string
    endDate?: string
    activityType?: string
  }): Promise<{
    activities: {
      id: number
      type: string
      description: string
      timestamp: string
      metadata?: any
    }[]
    summary: {
      totalActivities: number
      lastActivity: string
      mostActiveDay: string
      activityTypes: { type: string, count: number }[]
    }
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        activities: {
          id: number
          type: string
          description: string
          timestamp: string
          metadata?: any
        }[]
        summary: {
          totalActivities: number
          lastActivity: string
          mostActiveDay: string
          activityTypes: { type: string, count: number }[]
        }
      }>> = await axios.get(`${this.baseURL}/users/${userId}/activity/`, { params })
      return response.data.data || {
        activities: [],
        summary: {
          totalActivities: 0,
          lastActivity: '',
          mostActiveDay: '',
          activityTypes: []
        }
      }
    } catch (error) {
      console.error('获取用户活动失败:', error)
      throw error
    }
  }

  // 批量操作 API
  async batchOperation(operation: BatchOperation): Promise<BatchOperationResult> {
    try {
      const response: AxiosResponse<ApiResponse<BatchOperationResult>> = 
        await axios.post(`${this.baseURL}/users/batch/`, operation)
      return response.data.data || { success: 0, failed: 0, errors: [], details: '' }
    } catch (error) {
      console.error('批量操作失败:', error)
      throw error
    }
  }

  async exportUsers(params?: {
    format?: 'csv' | 'excel' | 'json'
    filters?: UserListParams
    fields?: string[]
  }): Promise<Blob> {
    try {
      const response = await axios.post(`${this.baseURL}/users/export/`, params, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('导出用户失败:', error)
      throw error
    }
  }

  async importUsers(file: File, options?: {
    skipDuplicates?: boolean
    updateExisting?: boolean
    defaultRole?: string
  }): Promise<{
    imported: number
    skipped: number
    errors: { row: number, error: string }[]
    summary: string
  }> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (options) {
        formData.append('options', JSON.stringify(options))
      }
      const response: AxiosResponse<ApiResponse<{
        imported: number
        skipped: number
        errors: { row: number, error: string }[]
        summary: string
      }>> = await axios.post(`${this.baseURL}/users/import/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data.data || { imported: 0, skipped: 0, errors: [], summary: '' }
    } catch (error) {
      console.error('导入用户失败:', error)
      throw error
    }
  }

  // 搜索和过滤 API
  async searchUsers(query: string, filters?: {
    role?: string
    group?: string
    isActive?: boolean
    fields?: string[]
  }): Promise<User[]> {
    try {
      const response: AxiosResponse<ApiResponse<User[]>> = 
        await axios.get(`${this.baseURL}/users/search/`, {
          params: { q: query, ...filters }
        })
      return response.data.data || []
    } catch (error) {
      console.error('搜索用户失败:', error)
      throw error
    }
  }

  async getAdvancedFilters(): Promise<{
    roles: { value: string, label: string, count: number }[]
    groups: { value: string, label: string, count: number }[]
    registrationDateRange: { min: string, max: string }
    lastLoginDateRange: { min: string, max: string }
  }> {
    try {
      const response: AxiosResponse<ApiResponse<{
        roles: { value: string, label: string, count: number }[]
        groups: { value: string, label: string, count: number }[]
        registrationDateRange: { min: string, max: string }
        lastLoginDateRange: { min: string, max: string }
      }>> = await axios.get(`${this.baseURL}/users/filters/`)
      return response.data.data || {
        roles: [],
        groups: [],
        registrationDateRange: { min: '', max: '' },
        lastLoginDateRange: { min: '', max: '' }
      }
    } catch (error) {
      console.error('获取高级过滤器失败:', error)
      throw error
    }
  }
}

export default new UserService()