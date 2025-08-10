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

// 创建axios实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/accounts/api',
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
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
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
  baseURL: 'http://127.0.0.1:8000/words/api',
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
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
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
  baseURL: 'http://127.0.0.1:8000/api/resource-auth',
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
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
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

export default api