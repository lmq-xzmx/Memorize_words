import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export function useAuth() {
  const store = useStore()
  const router = useRouter()
  
  // 用户认证状态
  const isAuthenticated = computed(() => {
    return store.getters['auth/isAuthenticated']
  })
  
  // 用户信息
  const userProfile = computed(() => {
    return store.getters['user/profile'] || {}
  })
  
  // 用户角色
  const userRole = computed(() => {
    return store.getters['user/role'] || 'student'
  })
  
  // 用户权限
  const userPermissions = computed(() => {
    return store.getters['user/permissions'] || []
  })
  
  // 登录
  const login = async (credentials: { username: string; password: string }) => {
    try {
      await store.dispatch('auth/login', credentials)
      await store.dispatch('user/fetchUserInfo')
      return true
    } catch (error) {
      throw error
    }
  }
  
  // 注册
  const register = async (userData: any) => {
    try {
      await store.dispatch('auth/register', userData)
      return true
    } catch (error) {
      throw error
    }
  }
  
  // 退出登录
  const logout = async () => {
    try {
      await store.dispatch('auth/logout')
      await router.push('/login')
    } catch (error) {
      throw error
    }
  }
  
  // 刷新用户信息
  const refreshUserInfo = async () => {
    try {
      await store.dispatch('user/fetchUserInfo')
    } catch (error) {
      console.error('刷新用户信息失败:', error)
    }
  }
  
  return {
    isAuthenticated,
    userProfile,
    userRole,
    userPermissions,
    login,
    register,
    logout,
    refreshUserInfo
  }
}