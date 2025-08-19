import type { RootState } from '../index'
import { getRolePermissions } from '@/config/permissions'
import { permissionChecker } from '@/utils/permissions'
import api from '@/utils/api'
import type { ActionContext } from 'vuex'

export interface UserState {
  profile: {
    id: number | null
    username: string
    email: string
    role: string
    avatar?: string
    created_at?: string
  }
  permissions: string[]
  roles: string[]
}

const user = {
  namespaced: true,
  
  state: (): UserState => ({
    profile: {
      id: null,
      username: '',
      email: '',
      role: '',
      avatar: '',
      created_at: ''
    },
    permissions: [],
    roles: []
  }),
  
  mutations: {
    SET_USER_PROFILE(state: UserState, profile: Partial<UserState['profile']>) {
      state.profile = { ...state.profile, ...profile }
      // 更新权限检查器
      if (profile.role) {
        const rolePermissions = getRolePermissions(profile.role)
        state.permissions = rolePermissions
        permissionChecker.updatePermissions(rolePermissions, profile.role)
      }
    },
    
    SET_USER_PERMISSIONS(state: UserState, permissions: string[]) {
      state.permissions = permissions
      permissionChecker.updatePermissions(permissions, state.profile.role)
    },
    
    SET_USER_ROLES(state: UserState, roles: string[]) {
      state.roles = roles
    },
    
    CLEAR_USER_DATA(state: UserState) {
      state.profile = {
        id: null,
        username: '',
        email: '',
        role: '',
        avatar: '',
        created_at: ''
      }
      state.permissions = []
      state.roles = []
      permissionChecker.updatePermissions([], '')
    }
  },
  
  actions: {
    // 设置用户信息
    setUserProfile({ commit }: ActionContext<UserState, RootState>, profile: Partial<UserState['profile']>) {
      commit('SET_USER_PROFILE', profile)
    },
    
    // 设置用户权限
    setUserPermissions({ commit }: ActionContext<UserState, RootState>, permissions: string[]) {
      commit('SET_USER_PERMISSIONS', permissions)
    },
    
    // 设置用户角色
    setUserRoles({ commit }: ActionContext<UserState, RootState>, roles: string[]) {
      commit('SET_USER_ROLES', roles)
    },
    
    // 清除用户数据
    clearUserData({ commit }: ActionContext<UserState, RootState>) {
      commit('CLEAR_USER_DATA')
    },
    
    // 获取用户信息
    async fetchUserInfo({ commit }: ActionContext<UserState, RootState>) {
      try {
        const response = await api.get('/api/auth/user/')
        
        // 后端返回的数据结构是 {success: true, user: {...}}
        const userData = response.data.user || response.data
        
        // 确保用户数据包含id字段（路由守卫需要）
        const userInfo = {
          ...userData,
          id: userData.id || userData.user_id
        }
        
        commit('SET_USER_PROFILE', userInfo)
        commit('SET_USER_ROLES', [userInfo.role])
        
        return userInfo
      } catch (error) {
        console.error('获取用户信息失败:', error)
        
        // 如果获取失败，使用模拟数据（开发环境）
        if (process.env.NODE_ENV === 'development') {
          const mockUserData = {
            id: 1,
            username: 'testuser',
            email: 'test@example.com',
            role: 'student',
            avatar: '',
            created_at: new Date().toISOString()
          }
          
          commit('SET_USER_PROFILE', mockUserData)
          commit('SET_USER_ROLES', [mockUserData.role])
          
          return mockUserData
        }
        
        throw error
      }
    }
  },
  
  getters: {
    // 获取用户信息
    userProfile: (state: UserState) => state.profile,
    
    // 获取用户权限
    userPermissions: (state: UserState) => state.permissions,
    
    // 获取用户角色
    userRoles: (state: UserState) => state.roles,
    
    // 检查是否有特定权限
    hasPermission: (state: UserState) => (permission: string) => {
      return state.permissions.includes(permission)
    },
    
    // 检查是否有任意权限
    hasAnyPermission: (state: UserState) => (permissions: string[]) => {
      return permissions.some(permission => state.permissions.includes(permission))
    },
    
    // 检查是否有所有权限
    hasAllPermissions: (state: UserState) => (permissions: string[]) => {
      return permissions.every(permission => state.permissions.includes(permission))
    },
    
    // 检查是否有特定角色
    hasRole: (state: UserState) => (role: string) => {
      return state.roles.includes(role)
    },
    
    // 检查是否为管理员
    isAdmin: (state: UserState) => {
      return state.profile.role === 'admin' || state.roles.includes('admin')
    },
    
    // 检查是否为教师
    isTeacher: (state: UserState) => {
      return state.profile.role === 'teacher' || state.roles.includes('teacher')
    },
    
    // 检查是否为学生
    isStudent: (state: UserState) => {
      return state.profile.role === 'student' || state.roles.includes('student')
    },
    
    // 获取当前用户（兼容性getter）
    currentUser: (state: UserState) => state.profile,
    
    // 获取用户资料（别名）
    profile: (state: UserState) => state.profile
  }
}

export default user