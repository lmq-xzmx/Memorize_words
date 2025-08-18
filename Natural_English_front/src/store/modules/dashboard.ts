import type { RootState } from '../index'

interface DashboardState {
  stats: {
    learningDays: number
    masteredWords: number
    completedExercises: number
    totalPoints: number
  }
  progress: {
    wordMastery: number
    grammarPractice: number
    listeningTraining: number
  }
  recentActivities: Array<{
    id: string
    icon: string
    text: string
    time: string
  }>
  loading: boolean
}

const state: DashboardState = {
  stats: {
    learningDays: 0,
    masteredWords: 0,
    completedExercises: 0,
    totalPoints: 0
  },
  progress: {
    wordMastery: 0,
    grammarPractice: 0,
    listeningTraining: 0
  },
  recentActivities: [],
  loading: false
}

const mutations = {
  SET_STATS(state: DashboardState, stats: any) {
    state.stats = { ...state.stats, ...stats }
  },
  
  SET_PROGRESS(state: DashboardState, progress: any) {
    state.progress = { ...state.progress, ...progress }
  },
  
  SET_RECENT_ACTIVITIES(state: DashboardState, activities: any[]) {
    state.recentActivities = activities
  },
  
  SET_LOADING(state: DashboardState, loading: boolean) {
    state.loading = loading
  }
}

const actions = {
  async getStats({ commit }: any) {
    commit('SET_LOADING', true)
    try {
      // 模拟API调用
      const mockStats = {
        learningDays: 45,
        masteredWords: 1250,
        completedExercises: 89,
        totalPoints: 3420
      }
      
      // 在实际项目中，这里应该是真实的API调用
      // const response = await api.get('/dashboard/stats')
      // const stats = response.data
      
      commit('SET_STATS', mockStats)
      return mockStats
    } catch (error) {
      console.error('获取统计数据失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async getProgress({ commit }: any) {
    commit('SET_LOADING', true)
    try {
      // 模拟API调用
      const mockProgress = {
        wordMastery: 75,
        grammarPractice: 60,
        listeningTraining: 45
      }
      
      // 在实际项目中，这里应该是真实的API调用
      // const response = await api.get('/dashboard/progress')
      // const progress = response.data
      
      commit('SET_PROGRESS', mockProgress)
      return mockProgress
    } catch (error) {
      console.error('获取进度数据失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async getRecentActivities({ commit }: any) {
    commit('SET_LOADING', true)
    try {
      // 模拟API调用
      const mockActivities = [
        {
          id: '1',
          icon: 'el-icon-document',
          text: '完成了单词学习：Technology相关词汇',
          time: '2小时前'
        },
        {
          id: '2',
          icon: 'el-icon-edit-outline',
          text: '完成了语法练习：现在完成时',
          time: '4小时前'
        },
        {
          id: '3',
          icon: 'el-icon-trophy',
          text: '获得成就：连续学习7天',
          time: '1天前'
        },
        {
          id: '4',
          icon: 'el-icon-star-on',
          text: '掌握了新单词：artificial intelligence',
          time: '2天前'
        }
      ]
      
      // 在实际项目中，这里应该是真实的API调用
      // const response = await api.get('/dashboard/activities')
      // const activities = response.data
      
      commit('SET_RECENT_ACTIVITIES', mockActivities)
      return mockActivities
    } catch (error) {
      console.error('获取最近活动失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  stats: (state: DashboardState) => state.stats,
  progress: (state: DashboardState) => state.progress,
  recentActivities: (state: DashboardState) => state.recentActivities,
  loading: (state: DashboardState) => state.loading
}

const dashboard = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

export default dashboard