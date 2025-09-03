import { login, getUserInfo, logout } from '@/services/userService'

const state = {
  token: uni.getStorageSync('token') || '',
  userInfo: uni.getStorageSync('userInfo') || {},
  isLoggedIn: !!uni.getStorageSync('token'),
  roles: uni.getStorageSync('roles') || [],
  permissions: uni.getStorageSync('permissions') || []
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    state.isLoggedIn = !!token
    if (token) {
      uni.setStorageSync('token', token)
    } else {
      uni.removeStorageSync('token')
    }
  },
  
  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo
    uni.setStorageSync('userInfo', userInfo)
  },
  
  SET_ROLES(state, roles) {
    state.roles = roles
    uni.setStorageSync('roles', roles)
  },
  
  SET_PERMISSIONS(state, permissions) {
    state.permissions = permissions
    uni.setStorageSync('permissions', permissions)
  },
  
  CLEAR_USER_DATA(state) {
    state.token = ''
    state.userInfo = {}
    state.isLoggedIn = false
    state.roles = []
    state.permissions = []
    
    // 清除本地存储
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
    uni.removeStorageSync('roles')
    uni.removeStorageSync('permissions')
  }
}

const actions = {
  // 用户登录
  async login({ commit }, loginForm) {
    try {
      const response = await login(loginForm)
      const { token, user, roles, permissions } = response.data
      
      commit('SET_TOKEN', token)
      commit('SET_USER_INFO', user)
      commit('SET_ROLES', roles || [])
      commit('SET_PERMISSIONS', permissions || [])
      
      return Promise.resolve(response)
    } catch (error) {
      return Promise.reject(error)
    }
  },
  
  // 获取用户信息
  async getUserInfo({ commit, state }) {
    try {
      if (!state.token) {
        throw new Error('未登录')
      }
      
      const response = await getUserInfo()
      const { user, roles, permissions } = response.data
      
      commit('SET_USER_INFO', user)
      commit('SET_ROLES', roles || [])
      commit('SET_PERMISSIONS', permissions || [])
      
      return Promise.resolve(response)
    } catch (error) {
      // 如果获取用户信息失败，清除登录状态
      commit('CLEAR_USER_DATA')
      return Promise.reject(error)
    }
  },
  
  // 用户登出
  async logout({ commit }) {
    try {
      await logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      commit('CLEAR_USER_DATA')
    }
  },
  
  // 检查登录状态
  checkLoginStatus({ commit, state, dispatch }) {
    return new Promise(async (resolve) => {
      if (state.token) {
        try {
          // 验证token是否有效
          await dispatch('getUserInfo')
          resolve(true)
        } catch (error) {
          console.error('Token验证失败:', error)
          commit('CLEAR_USER_DATA')
          resolve(false)
        }
      } else {
        resolve(false)
      }
    })
  },
  
  // 更新用户信息
  updateUserInfo({ commit }, userInfo) {
    commit('SET_USER_INFO', userInfo)
  },
  
  // 刷新token
  refreshToken({ commit }, token) {
    commit('SET_TOKEN', token)
  }
}

const getters = {
  token: state => state.token,
  userInfo: state => state.userInfo,
  isLoggedIn: state => state.isLoggedIn,
  roles: state => state.roles,
  permissions: state => state.permissions,
  userId: state => state.userInfo.id,
  username: state => state.userInfo.username,
  nickname: state => state.userInfo.nickname || state.userInfo.username,
  avatar: state => state.userInfo.avatar,
  email: state => state.userInfo.email,
  phone: state => state.userInfo.phone,
  
  // 检查是否有特定角色
  hasRole: (state) => (role) => {
    return state.roles.includes(role)
  },
  
  // 检查是否有特定权限
  hasPermission: (state) => (permission) => {
    return state.permissions.includes(permission)
  },
  
  // 检查是否有任一角色
  hasAnyRole: (state) => (roles) => {
    return roles.some(role => state.roles.includes(role))
  },
  
  // 检查是否有任一权限
  hasAnyPermission: (state) => (permissions) => {
    return permissions.some(permission => state.permissions.includes(permission))
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}