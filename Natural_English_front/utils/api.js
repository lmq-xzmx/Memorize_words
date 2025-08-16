import axios from 'axios'
import apiEnhancer from './apiInterceptorEnhancer.js'

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.MODE === 'production' ? '/api' : 'http://127.0.0.1:8000/api',
  timeout: 15000, // 增加超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 应用性能增强
apiEnhancer.enhance(api, {
  enableCache: true,
  enableBatch: false,
  cacheableMethods: ['GET', 'HEAD'],
  cachableEndpoints: [
    '/api/words',
    '/api/learning-goals',
    '/api/user/profile',
    '/api/analytics'
  ]
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 使用全局错误处理器处理API错误
    if (window.globalErrorHandler) {
      window.globalErrorHandler.handleAPIError(error, {
        url: error.config?.url,
        method: error.config?.method
      })
    }
    
    if (error.response?.status === 401) {
      // 清除token并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 清除权限缓存
      if (window.permissionWatcher) {
        window.permissionWatcher.notifyChange(null)
      }
      
      // 避免在登录页重复跳转
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// 认证相关API
export const authAPI = {
  // 登录
  login(username, password) {
    return api.post('/accounts/api/auth/login/', { username, password })
  },
  
  // 注册
  register(userData) {
    return api.post('/accounts/api/auth/register/', userData)
  },
  
  // 登出
  logout() {
    return api.post('/accounts/api/users/logout/', {})
  },
  
  // 刷新token
  refreshToken() {
    return api.post('/accounts/api/auth/refresh-token/')
  },
  
  // 验证token
  verifyToken() {
    return api.post('/accounts/api/auth/verify-token/')
  }
}

// 用户相关API
export const userAPI = {
  // 登录
  login(credentials) {
    return api.post('/accounts/api/auth/login/', credentials)
  },
  
  // 注册
  register(userData) {
    return api.post('/accounts/api/auth/register/', userData)
  },
  
  // 获取用户信息
  getProfile() {
    return api.get('/accounts/api/users/profile/')
  },
  
  // 更新用户信息
  updateProfile(data) {
    return api.put('/accounts/api/users/profile/', data)
  },
  
  // 登出
  logout() {
    return api.post('/accounts/api/users/logout/', {})
  }
}

// 单词相关API
export const wordAPI = {
  // 获取单词列表
  getWords(params = {}) {
    return api.get('/words/', { params })
  },
  
  // 获取单词详情
  getWordDetail(id) {
    return api.get(`/words/${id}/`)
  },
  
  // 搜索单词
  searchWords(query, params = {}) {
    return api.get('/words/search/', { 
      params: { q: query, ...params } 
    })
  },
  
  // 获取单词例句
  getWordExamples(params = {}) {
    return api.get('/words/examples/', { params })
  },
  
  // 添加学习记录
  addLearningRecord(data) {
    return api.post('/words/learning-records/', data)
  },
  
  // 获取学习统计
  getLearningStats() {
    return api.get('/words/learning-stats/')
  }
}

// 学习相关API
export const learningAPI = {
  // 获取学习目标
  getLearningGoals(params = {}) {
    return api.get('/teaching/goals/', { params })
  },
  
  // 获取当前学习目标
  getCurrentLearningGoal() {
    return api.get('/teaching/goals/current/')
  },
  
  // 创建学习目标
  createLearningGoal(data) {
    return api.post('/teaching/goals/', data)
  },
  
  // 更新学习目标
  updateLearningGoal(id, data) {
    return api.put(`/teaching/goals/${id}/`, data)
  },
  
  // 删除学习目标
  deleteLearningGoal(id) {
    return api.delete(`/teaching/goals/${id}/`)
  },
  
  // 获取练习单词
  getPracticeWords(params = {}) {
    return api.get('/teaching/practice-words/', { params })
  },
  
  // 创建学习会话
  createLearningSession(data) {
    return api.post('/teaching/learning-sessions/', data)
  },
  
  // 结束学习会话
  endLearningSession(sessionId) {
    return api.put(`/teaching/learning-sessions/${sessionId}/end/`)
  },
  
  // 创建单词学习记录
  createWordLearningRecord(data) {
    return api.post('/teaching/word-learning-records/', data)
  },
  
  // 获取学习进度
  getLearningProgress() {
    return api.get('/analytics/learning-progress/')
  },

  // 学习计划相关API
  // 获取学习计划
  getLearningPlans(params = {}) {
    return api.get('/teaching/learning-plans/', { params })
  },

  // 创建学习计划
  createLearningPlan(data) {
    return api.post('/teaching/learning-plans/', data)
  },

  // 更新学习计划
  updateLearningPlan(id, data) {
    return api.put(`/teaching/learning-plans/${id}/`, data)
  },

  // 删除学习计划
  deleteLearningPlan(id) {
    return api.delete(`/teaching/learning-plans/${id}/`)
  },

  // 获取学习目标的关联学习计划
  getGoalPlans(goalId) {
    return api.get(`/teaching/learning-goals/${goalId}/plans/`)
  }
}

// 资源授权相关API
export const resourceAuthAPI = {
  // 获取资源授权信息
  getResourceAuth() {
    return api.get('/resource-auth/')
  },
  
  // 更新资源授权
  updateResourceAuth(data) {
    return api.put('/resource-auth/', data)
  },
  
  // 获取订阅信息
  getSubscriptions() {
    return api.get('/subscriptions/')
  },
  
  // 获取当前订阅
  getMySubscription() {
    return api.get('/subscriptions/current/')
  },
  
  // 获取我的授权
  getMyAuthorizations(params = {}) {
    return api.get('/authorizations/', { params })
  },
  
  // 获取我的分享
  getMyShares() {
    return api.get('/shares/')
  },
  
  // 获取分类
  getCategories() {
    return api.get('/categories/')
  },
  
  // 获取订阅功能
  getSubscriptionFeatures() {
    return api.get('/subscriptions/features/')
  },
  
  // 订阅功能
  subscribe(featureId) {
    return api.post('/subscriptions/subscribe/', { feature_id: featureId })
  },
  
  // 分享资源
  shareResource(resourceId, shareData) {
    return api.post('/shares/', { resource_id: resourceId, ...shareData })
  },
  
  // 撤销分享
  revokeShare(shareId) {
    return api.delete(`/shares/${shareId}/`)
  },
  
  // 获取订阅信息
  getSubscriptionInfo() {
    return api.get('/subscriptions/info/')
  },
  
  // 获取订阅历史
  getSubscriptionHistory() {
    return api.get('/subscriptions/history/')
  },
  
  // 订阅功能
  subscribeToFeature(featureId) {
    return api.post('/subscriptions/subscribe/', { feature_id: featureId })
  },
  
  // 续订
  renewSubscription(subscriptionId) {
    return api.post(`/subscriptions/${subscriptionId}/renew/`)
  },
  
  // 取消订阅功能
  unsubscribeFromFeature(featureId) {
    return api.post('/subscriptions/unsubscribe/', { feature_id: featureId })
  },
  
  // 获取资源分享
  getResourceShares() {
    return api.get('/shares/')
  },
  
  // 获取授权统计
  getAuthorizationStats() {
    return api.get('/authorizations/stats/')
  },
  
  // 撤销资源分享
  revokeResourceShare(shareId) {
    return api.delete(`/shares/${shareId}/`)
  },
  
  // 获取分享链接
  getShareLink(shareId) {
    return api.get(`/shares/${shareId}/link/`)
  },
  
  // 创建订阅
  createSubscription(data) {
    return api.post('/subscriptions/', data)
  },
  
  // 取消订阅
  cancelSubscription(id) {
    return api.delete(`/subscriptions/${id}/`)
  }
}

// 教学相关API
export const teachingAPI = {
  // 获取教学内容
  getTeachingContent() {
    return api.get('/teaching/content/')
  },
  
  // 获取课程列表
  getCourses() {
    return api.get('/teaching/courses/')
  },
  
  // 获取课程详情
  getCourseDetail(id) {
    return api.get(`/teaching/courses/${id}/`)
  },
  
  // 创建课程
  createCourse(data) {
    return api.post('/teaching/courses/', data)
  },
  
  // 更新课程
  updateCourse(id, data) {
    return api.put(`/teaching/courses/${id}/`, data)
  }
}

// 默认导出
export default api