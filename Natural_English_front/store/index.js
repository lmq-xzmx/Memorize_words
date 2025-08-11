import { createStore } from 'vuex'
import api from '../utils/api'

// 状态管理
const store = createStore({
  state: {
    // 用户相关状态
    user: {
      isAuthenticated: false,
      profile: null,
      token: localStorage.getItem('token') || null
    },
    
    // 学习相关状态
    learning: {
      currentWord: null,
      learningProgress: {},
      studySession: null
    },
    
    // 应用状态
    app: {
      loading: false,
      error: null,
      theme: localStorage.getItem('theme') || 'light',
      language: localStorage.getItem('language') || 'zh-CN'
    },
    
    // 单词相关状态
    words: {
      currentWordList: [],
      selectedWords: [],
      searchResults: [],
      favorites: []
    }
  },
  
  mutations: {
    // 用户相关mutations
    SET_USER_AUTHENTICATED(state, status) {
      state.user.isAuthenticated = status
    },
    
    SET_USER_PROFILE(state, profile) {
      state.user.profile = profile
    },
    
    SET_USER_TOKEN(state, token) {
      state.user.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    
    // 学习相关mutations
    SET_CURRENT_WORD(state, word) {
      state.learning.currentWord = word
    },
    
    SET_LEARNING_PROGRESS(state, progress) {
      state.learning.learningProgress = progress
    },
    
    SET_STUDY_SESSION(state, session) {
      state.learning.studySession = session
    },
    
    // 应用状态mutations
    SET_LOADING(state, status) {
      state.app.loading = status
    },
    
    SET_ERROR(state, error) {
      state.app.error = error
    },
    
    SET_THEME(state, theme) {
      state.app.theme = theme
      localStorage.setItem('theme', theme)
    },
    
    SET_LANGUAGE(state, language) {
      state.app.language = language
      localStorage.setItem('language', language)
    },
    
    // 单词相关mutations
    SET_WORD_LIST(state, words) {
      state.words.currentWordList = words
    },
    
    SET_SELECTED_WORDS(state, words) {
      state.words.selectedWords = words
    },
    
    SET_SEARCH_RESULTS(state, results) {
      state.words.searchResults = results
    },
    
    ADD_TO_FAVORITES(state, word) {
      if (!state.words.favorites.find(w => w.id === word.id)) {
        state.words.favorites.push(word)
      }
    },
    
    REMOVE_FROM_FAVORITES(state, wordId) {
      state.words.favorites = state.words.favorites.filter(w => w.id !== wordId)
    }
  },
  
  actions: {
    // 用户认证actions
    async login({ commit }, credentials) {
      try {
        commit('SET_LOADING', true)
        const response = await api.post('/auth/login/', credentials)
        const { token, user } = response.data
        
        commit('SET_USER_TOKEN', token)
        commit('SET_USER_PROFILE', user)
        commit('SET_USER_AUTHENTICATED', true)
        commit('SET_ERROR', null)
        
        return { success: true, data: response.data }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || '登录失败')
        return { success: false, error: error.response?.data }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async logout({ commit }) {
      try {
        await api.post('/auth/logout/')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        commit('SET_USER_TOKEN', null)
        commit('SET_USER_PROFILE', null)
        commit('SET_USER_AUTHENTICATED', false)
      }
    },
    
    async register({ commit }, userData) {
      try {
        commit('SET_LOADING', true)
        const response = await api.post('/auth/register/', userData)
        commit('SET_ERROR', null)
        return { success: true, data: response.data }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || '注册失败')
        return { success: false, error: error.response?.data }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 获取用户信息
    async fetchUserProfile({ commit }) {
      try {
        const response = await api.get('/auth/profile/')
        commit('SET_USER_PROFILE', response.data)
        return { success: true, data: response.data }
      } catch (error) {
        console.error('Fetch profile error:', error)
        return { success: false, error: error.response?.data }
      }
    },
    
    // 学习相关actions
    async fetchWordList({ commit }, params = {}) {
      try {
        commit('SET_LOADING', true)
        const response = await api.get('/words/', { params })
        commit('SET_WORD_LIST', response.data.results || response.data)
        return { success: true, data: response.data }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || '获取单词列表失败')
        return { success: false, error: error.response?.data }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async searchWords({ commit }, query) {
      try {
        const response = await api.get('/words/search/', { params: { q: query } })
        commit('SET_SEARCH_RESULTS', response.data.results || response.data)
        return { success: true, data: response.data }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || '搜索失败')
        return { success: false, error: error.response?.data }
      }
    },
    
    // 初始化应用
    async initializeApp({ commit, dispatch }) {
      const token = localStorage.getItem('token')
      if (token) {
        commit('SET_USER_TOKEN', token)
        commit('SET_USER_AUTHENTICATED', true)
        await dispatch('fetchUserProfile')
      }
    }
  },
  
  getters: {
    // 用户相关getters
    isAuthenticated: state => state.user.isAuthenticated,
    userProfile: state => state.user.profile,
    userToken: state => state.user.token,
    
    // 应用状态getters
    isLoading: state => state.app.loading,
    appError: state => state.app.error,
    currentTheme: state => state.app.theme,
    currentLanguage: state => state.app.language,
    
    // 学习相关getters
    currentWord: state => state.learning.currentWord,
    learningProgress: state => state.learning.learningProgress,
    studySession: state => state.learning.studySession,
    
    // 单词相关getters
    wordList: state => state.words.currentWordList,
    selectedWords: state => state.words.selectedWords,
    searchResults: state => state.words.searchResults,
    favoriteWords: state => state.words.favorites,
    
    // 计算属性
    selectedWordCount: state => state.words.selectedWords.length,
    hasSearchResults: state => state.words.searchResults.length > 0
  }
})

export default store