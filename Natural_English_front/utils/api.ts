import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import type { User, Word, LearningProgress, StudySession } from '../types'

// Extend Window interface for global properties
declare global {
  interface Window {
    globalErrorHandler?: {
      handleAPIError: (error: any, context?: any) => void;
    };
    permissionWatcher?: {
      notifyChange: (data: any) => void;
    };
  }
}

// Simplified API enhancer
const apiInterceptorEnhancer = {
  enhance: (axiosInstance: AxiosInstance, options: any = {}) => {
    // Simplified enhancer for now - will be properly implemented later
    return axiosInstance;
  }
};

// 定义响应数据的基础接口
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  success?: boolean
}

// 定义请求配置接口
interface RequestConfig {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  data?: any
  params?: any
  headers?: Record<string, string>
  timeout?: number
}

// 定义错误响应接口
interface ErrorResponse {
  code: number
  message: string
  data?: any
}

// 请求状态枚举
enum RequestStatus {
  PENDING = 'pending',
  SUCCESS = 'success',
  ERROR = 'error'
}

// 请求重试配置
interface RetryConfig {
  retries: number
  retryDelay: number
  retryCondition?: (error: any) => boolean
}

// 默认重试配置
const DEFAULT_RETRY_CONFIG: RetryConfig = {
  retries: 3,
  retryDelay: 1000,
  retryCondition: (error) => {
    return error.code === 'NETWORK_ERROR' || error.response?.status >= 500
  }
}

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  confirmPassword?: string;
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  createdAt: string;
}

interface WordData {
  id: number;
  word: string;
  pronunciation: string;
  definition: string;
  example: string;
  difficulty: number;
}

interface WordSearchParams {
  query?: string;
  page?: number;
  limit?: number;
  difficulty?: string;
  category?: string;
}

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.MODE === 'production' ? '/api' : 'http://127.0.0.1:8001/api',
  timeout: 15000, // 增加超时时间
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error: AxiosError) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    // 处理认证错误
    if (error.response?.status === 401) {
      // 清除本地存储的认证信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      ElMessage.error('登录已过期，请重新登录')
    }
    
    // 处理其他HTTP错误
    const message = (error.response?.data as any)?.message || error.message || '请求失败'
    ElMessage.error(message)
    
    return Promise.reject(error)
  }
)

// 认证相关API
export const authAPI = {
  // 登录
  login(username: string, password: string) {
    return api.post('/accounts/api/auth/login/', { username, password })
  },
  
  // 注册
  register(userData: RegisterData) {
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
  login(credentials: LoginCredentials) {
    return api.post('/accounts/api/auth/login/', credentials)
  },
  
  // 注册
  register(userData: RegisterData) {
    return api.post('/accounts/api/auth/register/', userData)
  },
  
  // 获取用户信息
  getProfile() {
    return api.get('/accounts/api/users/profile/')
  },
  
  // 更新用户信息
  updateProfile(data: Partial<User>) {
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
  getWords(params: WordSearchParams = {}) {
    return api.get('/words/', { params })
  },
  
  // 获取单词详情
  getWordDetail(id: string | number) {
    return api.get(`/words/${id}/`)
  },
  
  // 搜索单词
  searchWords(query: string, params: WordSearchParams = {}) {
    return api.get('/words/search/', { 
      params: { q: query, ...params } 
    })
  },
  
  // 获取单词例句
  getWordExamples(params: any = {}) {
    return api.get('/words/examples/', { params })
  },
  
  // 添加学习记录
  addLearningRecord(data: any) {
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
  getLearningGoals(params: any = {}) {
    return api.get('/teaching/goals/', { params })
  },
  
  // 获取当前学习目标
  getCurrentLearningGoal() {
    return api.get('/teaching/goals/current/')
  },
  
  // 创建学习目标
  createLearningGoal(data: any) {
    return api.post('/teaching/goals/', data)
  },
  
  // 更新学习目标
  updateLearningGoal(id: string | number, data: any) {
    return api.put(`/teaching/goals/${id}/`, data)
  },
  
  // 删除学习目标
  deleteLearningGoal(id: string | number) {
    return api.delete(`/teaching/goals/${id}/`)
  },
  
  // 获取练习单词
  getPracticeWords(params: any = {}) {
    return api.get('/teaching/practice-words/', { params })
  },
  
  // 创建学习会话
  createLearningSession(data: any) {
    return api.post('/teaching/learning-sessions/', data)
  },
  
  // 结束学习会话
  endLearningSession(sessionId: string | number) {
    return api.put(`/teaching/learning-sessions/${sessionId}/end/`)
  },
  
  // 创建单词学习记录
  createWordLearningRecord(data: any) {
    return api.post('/teaching/word-learning-records/', data)
  },
  
  // 获取学习进度
  getLearningProgress() {
    return api.get('/analytics/learning-progress/')
  },

  // 学习计划相关API
  // 获取学习计划
  getLearningPlans(params: any = {}) {
    return api.get('/teaching/learning-plans/', { params })
  },

  // 创建学习计划
  createLearningPlan(data: any) {
    return api.post('/teaching/learning-plans/', data)
  },

  // 更新学习计划
  updateLearningPlan(id: string | number, data: any) {
    return api.put(`/teaching/learning-plans/${id}/`, data)
  },

  // 删除学习计划
  deleteLearningPlan(id: string | number) {
    return api.delete(`/teaching/learning-plans/${id}/`)
  },

  // 获取学习目标的关联学习计划
  getGoalPlans(goalId: string | number) {
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
  updateResourceAuth(data: any) {
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
  getMyAuthorizations(params: any = {}) {
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
  subscribe(featureId: string | number) {
    return api.post('/subscriptions/subscribe/', { feature_id: featureId })
  },
  
  // 分享资源
  shareResource(resourceId: string | number, shareData: any) {
    return api.post('/shares/', { resource_id: resourceId, ...shareData })
  },
  
  // 撤销分享
  revokeShare(shareId: string | number) {
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
  subscribeToFeature(featureId: string | number) {
    return api.post('/subscriptions/subscribe/', { feature_id: featureId })
  },
  
  // 续订
  renewSubscription(subscriptionId: string | number) {
    return api.post(`/subscriptions/${subscriptionId}/renew/`)
  },
  
  // 取消订阅功能
  unsubscribeFromFeature(featureId: string | number) {
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
  revokeResourceShare(shareId: string | number) {
    return api.delete(`/shares/${shareId}/`)
  },
  
  // 获取分享链接
  getShareLink(shareId: string | number) {
    return api.get(`/shares/${shareId}/link/`)
  },
  
  // 创建订阅
  createSubscription(data: any) {
    return api.post('/subscriptions/', data)
  },
  
  // 取消订阅
  cancelSubscription(id: string | number) {
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
  getCourseDetail(id: string | number) {
    return api.get(`/teaching/courses/${id}/`)
  },
  
  // 创建课程
  createCourse(data: any) {
    return api.post('/teaching/courses/', data)
  },
  
  // 更新课程
  updateCourse(id: string | number, data: any) {
    return api.put(`/teaching/courses/${id}/`, data)
  }
}

// 默认导出
export default api