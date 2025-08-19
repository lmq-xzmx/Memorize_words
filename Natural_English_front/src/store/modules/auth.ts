import type { RootState } from '../index'
import api from '@/utils/api';
import type { ActionContext } from 'vuex'

export interface AuthState {
  token: string | null
  isAuthenticated: boolean
  loading: boolean
}

const auth = {
  namespaced: true,
  
  state: {
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false
  },
  
  mutations: {
    SET_TOKEN(state: AuthState, token: string) {
      state.token = token
      state.isAuthenticated = true
      localStorage.setItem('token', token)
    },
    
    CLEAR_TOKEN(state: AuthState) {
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    },
    
    SET_LOADING(state: AuthState, loading: boolean) {
      state.loading = loading
    }
  },
  
  actions: {
    async login({ commit }: ActionContext<AuthState, RootState>, credentials: { username: string; password: string }) {
      try {
        commit('SET_LOADING', true)
        const response = await api.post('/api/auth/login/', credentials)
        const { token } = response.data
        commit('SET_TOKEN', token)
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          message: error.response?.data?.message || '登录失败' 
        }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async register({ commit }: ActionContext<AuthState, RootState>, userData: any) {
      try {
        commit('SET_LOADING', true)
        const response = await api.post('/api/auth/register/', userData)
        return { success: true, data: response.data }
      } catch (error: any) {
        return { 
          success: false, 
          message: error.response?.data?.message || '注册失败' 
        }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    logout({ commit }: ActionContext<AuthState, RootState>) {
      commit('CLEAR_TOKEN')
      // 清除用户信息
      localStorage.removeItem('userInfo')
    }
  },
  
  getters: {
    isAuthenticated: (state: AuthState) => state.isAuthenticated,
    token: (state: AuthState) => state.token,
    loading: (state: AuthState) => state.loading
  }
}

export default auth