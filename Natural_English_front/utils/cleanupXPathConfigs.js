import axios from 'axios'

// 获取CSRF token的函数
function getCsrfToken() {
  const name = 'csrftoken'
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// 创建API实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8001/accounts/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// 请求拦截器 - 自动添加Token和CSRF token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    // 添加CSRF token
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  response => {
    // 检查响应是否为HTML内容（通常表示被重定向到登录页）
    if (typeof response.data === 'string' && 
        (response.data.trim().startsWith('<!DOCTYPE') || response.data.trim().startsWith('<html'))) {
      console.warn('API返回HTML内容，可能是未认证被重定向到登录页')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 标记需要重新登录，让路由守卫处理跳转
      if (window.location.pathname !== '/login') {
        // 延迟执行，避免在API调用过程中立即跳转
        setTimeout(() => {
          if (window.VueRouter) {
            window.VueRouter.push('/login')
          } else {
            window.location.href = '/login'
          }
        }, 100)
      }
      return Promise.reject(new Error('未认证，请重新登录'))
    }
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        // 延迟执行，避免在API调用过程中立即跳转
        setTimeout(() => {
           if (window.VueRouter) {
             window.VueRouter.push('/login')
           } else {
             window.location.href = '/login'
           }
         }, 100)
      }
    }
    // 检查错误响应是否为HTML内容
    if (error.response?.data && typeof error.response.data === 'string' &&
        (error.response.data.trim().startsWith('<!DOCTYPE') || error.response.data.trim().startsWith('<html'))) {
      console.warn('错误响应包含HTML内容，清除认证信息')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        // 延迟执行，避免在API调用过程中立即跳转
        setTimeout(() => {
           if (window.VueRouter) {
             window.VueRouter.push('/login')
           } else {
             window.location.href = '/login'
           }
         }, 100)
      }
      return Promise.reject(new Error('认证失效，请重新登录'))
    }
    return Promise.reject(error.response?.data || error.message)
  }
)

// 用户认证相关API
export const authAPI = {
  // 用户注册
  register(userData) {
    return api.post('/auth/register/', userData)
  },
  
  // 用户登录
  login(username, password) {
    return api.post('/auth/login/', { username, password })
  },
  
  // 用户登出
  logout() {
    return api.post('/users/logout/')
  }
}

// 用户信息相关API
export const userAPI = {
  // 获取用户信息
  getProfile() {
    return api.get('/users/profile/')
  },
  
  // 更新用户信息
  updateProfile(userData) {
    return api.put('/users/profile/', userData)
  },
  
  // 修改密码
  changePassword(passwordData) {
    return api.post('/users/change_password/', passwordData)
  }
}

// 学习档案相关API
export const learningAPI = {
  // 获取学习档案
  getProfiles() {
    return api.get('/learning-profiles/')
  },
  
  // 创建学习档案
  createProfile(profileData) {
    return api.post('/learning-profiles/', profileData)
  }
}

// 创建单词API实例
const wordApi = axios.create({
  baseURL: 'http://127.0.0.1:8001/words/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// 单词API请求拦截器
wordApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 单词API响应拦截器
wordApi.interceptors.response.use(
  response => {
    // 检查响应是否为HTML内容
    if (typeof response.data === 'string' && 
        (response.data.trim().startsWith('<!DOCTYPE') || response.data.trim().startsWith('<html'))) {
      console.warn('单词API返回HTML内容，可能是未认证被重定向到登录页')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
          if (window.VueRouter) {
            window.VueRouter.push('/login')
          } else {
            window.location.href = '/login'
          }
        }, 100)
      }
      return Promise.reject(new Error('未认证，请重新登录'))
    }
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
           if (window.VueRouter) {
             window.VueRouter.push('/login')
           } else {
             window.location.href = '/login'
           }
         }, 100)
      }
    }
    // 检查错误响应是否为HTML内容
    if (error.response?.data && typeof error.response.data === 'string' &&
        (error.response.data.trim().startsWith('<!DOCTYPE') || error.response.data.trim().startsWith('<html'))) {
      console.warn('单词API错误响应包含HTML内容，清除认证信息')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
           if (window.VueRouter) {
             window.VueRouter.push('/login')
           } else {
             window.location.href = '/login'
           }
         }, 100)
      }
      return Promise.reject(new Error('认证失效，请重新登录'))
    }
    return Promise.reject(error.response?.data || error.message)
  }
)

// 单词相关API
export const wordAPI = {
  // 获取单词列表
  getWords(params = {}) {
    return wordApi.get('/words/', { params })
  },
  
  // 获取单词例句
  getWordExamples(params = {}) {
    return wordApi.get('/word-examples/', { params })
  },
  
  // 标记单词为已学习
  markAsLearned(wordId) {
    return wordApi.post(`/words/${wordId}/mark_learned/`)
  },
  
  // 更新单词掌握程度
  updateMastery(wordId, masteryLevel) {
    return wordApi.post(`/words/${wordId}/update_mastery/`, { mastery_level: masteryLevel })
  }
}

// 创建资源授权API实例
const resourceAuthApi = axios.create({
  baseURL: 'http://127.0.0.1:8001/api/resource-auth',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// 资源授权API请求拦截器
resourceAuthApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 资源授权API响应拦截器
resourceAuthApi.interceptors.response.use(
  response => {
    // 检查响应是否为HTML内容
    if (typeof response.data === 'string' && 
        (response.data.trim().startsWith('<!DOCTYPE') || response.data.trim().startsWith('<html'))) {
      console.warn('资源授权API返回HTML内容，可能是未认证被重定向到登录页')
      
      // 使用权限系统的清理方法
      if (window.permissionUtils && window.permissionUtils.clearAuth) {
        window.permissionUtils.clearAuth()
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
      
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
          if (window.VueRouter) {
            window.VueRouter.push('/login')
          } else {
            window.location.href = '/login'
          }
        }, 100)
      }
      return Promise.reject(new Error('未认证，请重新登录'))
    }
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      // 使用权限系统的清理方法
      if (window.permissionUtils && window.permissionUtils.clearAuth) {
        window.permissionUtils.clearAuth()
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
      
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
          if (window.VueRouter) {
            window.VueRouter.push('/login')
          } else {
            window.location.href = '/login'
          }
        }, 100)
      }
    }
    // 检查错误响应是否为HTML内容
    if (error.response?.data && typeof error.response.data === 'string' &&
        (error.response.data.trim().startsWith('<!DOCTYPE') || error.response.data.trim().startsWith('<html'))) {
      console.warn('资源授权API错误响应包含HTML内容，清除认证信息')
      
      // 使用权限系统的清理方法
      if (window.permissionUtils && window.permissionUtils.clearAuth) {
        window.permissionUtils.clearAuth()
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
      
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
          if (window.VueRouter) {
            window.VueRouter.push('/login')
          } else {
            window.location.href = '/login'
          }
        }, 100)
      }
      return Promise.reject(new Error('认证失效，请重新登录'))
    }
    return Promise.reject(error.response?.data || error.message)
  }
)

// 资源授权相关API
export const resourceAuthAPI = {
  // 订阅管理
  getSubscriptionInfo() {
    return resourceAuthApi.get('/subscriptions/current/')
  },
  
  getSubscriptionFeatures() {
    return resourceAuthApi.get('/subscriptions/features/')
  },
  
  subscribeToFeature(featureId) {
    return resourceAuthApi.post('/subscriptions/subscribe/', { feature_id: featureId })
  },
  
  unsubscribeFromFeature(featureId) {
    return resourceAuthApi.post('/subscriptions/unsubscribe/', { feature_id: featureId })
  },
  
  getSubscriptionHistory() {
    return resourceAuthApi.get('/subscriptions/history/')
  },
  
  renewSubscription(subscriptionId) {
    return resourceAuthApi.post(`/subscriptions/${subscriptionId}/renew/`)
  },
  
  // 资源授权管理
  getResourceAuthorizations() {
    return resourceAuthApi.get('/authorizations/')
  },
  
  getResourceCategories() {
    return resourceAuthApi.get('/categories/')
  },
  
  checkResourceAccess(resourceId) {
    return resourceAuthApi.get(`/authorizations/check-access/${resourceId}/`)
  },
  
  requestResourceAccess(resourceId) {
    return resourceAuthApi.post('/authorizations/request-access/', { resource_id: resourceId })
  },
  
  grantResourceAccess(resourceId, userId) {
    return resourceAuthApi.post('/authorizations/grant-access/', { 
      resource_id: resourceId, 
      user_id: userId 
    })
  },
  
  revokeResourceAccess(authorizationId) {
    return resourceAuthApi.delete(`/authorizations/${authorizationId}/`)
  },
  
  // 资源分享管理
  getResourceShares() {
    return resourceAuthApi.get('/shares/')
  },
  
  shareResource(resourceId, shareData) {
    return resourceAuthApi.post('/shares/', {
      resource_id: resourceId,
      ...shareData
    })
  },
  
  revokeResourceShare(shareId) {
    return resourceAuthApi.delete(`/shares/${shareId}/`)
  },
  
  getShareLink(shareId) {
    return resourceAuthApi.get(`/shares/${shareId}/link/`)
  },
  
  // 统计信息
  getAuthorizationStats() {
    return resourceAuthApi.get('/authorizations/stats/')
  }
}

// 创建analytics API实例
const analyticsApi = axios.create({
  baseURL: 'http://127.0.0.1:8001/analytics',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// Analytics API请求拦截器
analyticsApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Analytics API响应拦截器
analyticsApi.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
          if (window.VueRouter) {
            window.VueRouter.push('/login')
          } else {
            window.location.href = '/login'
          }
        }, 100)
      }
    }
    return Promise.reject(error.response?.data || error.message)
  }
)

// Analytics相关API
export const analyticsAPI = {
  // 获取用户参与度指标
  getUserEngagementMetrics() {
    return analyticsApi.get('/user-engagement-metrics/')
  },
  
  // 获取行为分析数据
  getBehaviorAnalysis() {
    return analyticsApi.get('/behavior-analysis/')
  },
  
  // 获取游戏元素效果数据
  getGameElementEffectiveness() {
    return analyticsApi.get('/game-element-effectiveness/')
  },
  
  // 获取学习概览
  getOverview() {
    return analyticsApi.get('/overview/')
  },
  
  // 获取每日活动数据
  getDailyActivity() {
    return analyticsApi.get('/daily-activity/')
  },
  
  // 获取每周进度数据
  getWeeklyProgress() {
    return analyticsApi.get('/weekly-progress/')
  },
  
  // 获取综合分析数据
  getComprehensive() {
    return analyticsApi.get('/comprehensive/')
  },
  
  // 导出数据
  exportData(dataType, format = 'json') {
    return analyticsApi.get('/export-data/', {
      params: { type: dataType, format: format }
    })
  }
}

// 创建teaching API实例
const teachingApi = axios.create({
  baseURL: 'http://127.0.0.1:8001/api/teaching',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// Teaching API请求拦截器
teachingApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Teaching API响应拦截器
teachingApi.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        setTimeout(() => {
          if (window.VueRouter) {
            window.VueRouter.push('/login')
          } else {
            window.location.href = '/login'
          }
        }, 100)
      }
    }
    return Promise.reject(error.response?.data || error.message)
  }
)

// Teaching相关API
export const teachingAPI = {
  // 学习目标管理
  getLearningGoals(params = {}) {
    return teachingApi.get('/learning-goals/', { params })
  },
  
  createLearningGoal(data) {
    return teachingApi.post('/learning-goals/', data)
  },
  
  updateLearningGoal(id, data) {
    return teachingApi.put(`/learning-goals/${id}/`, data)
  },
  
  deleteLearningGoal(id) {
    return teachingApi.delete(`/learning-goals/${id}/`)
  },
  
  getLearningGoalProgress(id) {
    return teachingApi.get(`/learning-goals/${id}/progress/`)
  },
  
  addWordsToGoal(id, wordIds) {
    return teachingApi.post(`/learning-goals/${id}/add_words/`, { word_ids: wordIds })
  },
  
  removeWordsFromGoal(id, wordIds) {
    return teachingApi.post(`/learning-goals/${id}/remove_words/`, { word_ids: wordIds })
  },
  
  getCurrentLearningGoal() {
    return teachingApi.get('/learning-goals/current/')
  },
  
  // 学习会话管理
  createLearningSession(data) {
    return teachingApi.post('/learning-sessions/', data)
  },
  
  endLearningSession(id) {
    return teachingApi.post(`/learning-sessions/${id}/end_session/`)
  },
  
  getLearningSessionRecords(id) {
    return teachingApi.get(`/learning-sessions/${id}/records/`)
  },
  
  // 学习记录管理
  createWordLearningRecord(data) {
    return teachingApi.post('/word-learning-records/', data)
  },
  
  getWordLearningRecords(params = {}) {
    return teachingApi.get('/word-learning-records/', { params })
  },
  
  getWordLearningStatistics() {
    return teachingApi.get('/word-learning-records/statistics/')
  },
  
  // 练习单词获取
  getPracticeWords(params = {}) {
    return teachingApi.get('/practice-words/', { params })
  }
}

export default api