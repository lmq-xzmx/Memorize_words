import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import apiEnhancer from './apiInterceptorEnhancer';

// 类型定义
interface UserData {
  username: string;
  email: string;
  password: string;
  [key: string]: any;
}

interface LoginCredentials {
  username: string;
  password: string;
}

interface PasswordData {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

interface ProfileData {
  [key: string]: any;
}

interface WordParams {
  page?: number;
  limit?: number;
  difficulty?: string;
  category?: string;
  [key: string]: any;
}

interface ShareData {
  user_id: number;
  permissions: string[];
  expires_at?: string;
  [key: string]: any;
}

interface LearningGoalData {
  title: string;
  description?: string;
  target_words: number;
  deadline?: string;
  [key: string]: any;
}

interface LearningSessionData {
  goal_id: number;
  start_time: string;
  [key: string]: any;
}

interface WordLearningRecordData {
  session_id: number;
  word_id: number;
  result: string;
  time_spent: number;
  [key: string]: any;
}

// 获取CSRF token的函数
function getCsrfToken(): string | null {
  const name = 'csrftoken';
  let cookieValue: string | null = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 创建API实例
const api: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/accounts/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

// 应用性能增强到主API实例
apiEnhancer.enhance(api, {
  enableCache: true,
  cachableEndpoints: ['/accounts/api']
});

// 请求拦截器 - 自动添加Token和CSRF token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // 添加CSRF token
    const csrfToken = getCsrfToken();
    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理token过期
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 检查响应中是否有新的token
    const newToken = response.headers['authorization'];
    if (newToken) {
      localStorage.setItem('token', newToken.replace('Token ', ''));
    }
    
    // 检查是否有权限相关的响应头
    const permissionUpdate = response.headers['x-permission-update'];
    if (permissionUpdate) {
      try {
        const permissions = JSON.parse(permissionUpdate);
        // 触发权限更新事件
        window.dispatchEvent(new CustomEvent('permissionUpdate', {
          detail: permissions
        }));
      } catch (e) {
        console.warn('Failed to parse permission update:', e);
      }
    }
    
    return response;
  },
  error => {
    if (error.response) {
      // 处理401未授权错误
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        // 触发登出事件
        window.dispatchEvent(new CustomEvent('authLogout'));
        
        // 如果不是登录页面，重定向到登录页面
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
      
      // 处理403权限不足错误
      if (error.response.status === 403) {
        // 触发权限不足事件
        window.dispatchEvent(new CustomEvent('permissionDenied', {
          detail: {
            url: error.config?.url,
            method: error.config?.method,
            message: error.response.data?.message || 'Permission denied'
          }
        }));
      }
    }
    
    return Promise.reject(error);
  }
);

// 认证相关API
export const authAPI = {
  // 用户注册
  register(userData: UserData) {
    return api.post('/register/', userData);
  },
  
  // 用户登录
  login(username: string, password: string) {
    return api.post('/login/', { username, password });
  },
  
  // 用户登出
  logout() {
    return api.post('/logout/');
  }
};

// 用户相关API
export const userAPI = {
  // 获取用户资料
  getProfile() {
    return api.get('/profile/');
  },
  
  // 更新用户资料
  updateProfile(userData: ProfileData) {
    return api.put('/profile/', userData);
  },
  
  // 修改密码
  changePassword(passwordData: PasswordData) {
    return api.post('/change-password/', passwordData);
  }
};

// 学习相关API
export const learningAPI = {
  // 获取学习档案
  getProfiles() {
    return api.get('/learning-profiles/');
  },
  
  // 创建学习档案
  createProfile(profileData: ProfileData) {
    return api.post('/learning-profiles/', profileData);
  }
};

// 单词API实例
const wordApi: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/words/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

// 应用性能增强到单词API实例
apiEnhancer.enhance(wordApi, {
  enableCache: true,
  cachableEndpoints: ['/words/api']
});

// 单词API请求拦截器
wordApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    const csrfToken = getCsrfToken();
    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 单词API响应拦截器
wordApi.interceptors.response.use(
  (response: AxiosResponse) => {
    // 检查是否有学习进度更新
    const progressUpdate = response.headers['x-learning-progress'];
    if (progressUpdate) {
      try {
        const progress = JSON.parse(progressUpdate);
        window.dispatchEvent(new CustomEvent('learningProgressUpdate', {
          detail: progress
        }));
      } catch (e) {
        console.warn('Failed to parse learning progress:', e);
      }
    }
    
    return response;
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.dispatchEvent(new CustomEvent('authLogout'));
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    // 处理单词相关的特殊错误
    if (error.response?.status === 429) {
      window.dispatchEvent(new CustomEvent('rateLimitExceeded', {
        detail: {
          message: 'Too many requests. Please slow down.',
          retryAfter: error.response.headers['retry-after']
        }
      }));
    }
    
    return Promise.reject(error);
  }
);

// 单词相关API
export const wordAPI = {
  // 获取单词列表
  getWords(params: WordParams = {}) {
    return wordApi.get('/words/', { params });
  },
  
  // 获取单词例句
  getWordExamples(params: WordParams = {}) {
    return wordApi.get('/word-examples/', { params });
  },
  
  // 标记单词为已学习
  markAsLearned(wordId: number) {
    return wordApi.post(`/words/${wordId}/mark-learned/`);
  },
  
  // 更新单词掌握度
  updateMastery(wordId: number, masteryLevel: number) {
    return wordApi.put(`/words/${wordId}/mastery/`, { mastery_level: masteryLevel });
  }
};

// 资源授权API实例
const resourceAuthApi: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/resource-auth',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

// 应用性能增强到资源授权API实例
apiEnhancer.enhance(resourceAuthApi, {
  enableCache: true,
  cachableEndpoints: ['/api/resource-auth']
});

// 资源授权API请求拦截器
resourceAuthApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    const csrfToken = getCsrfToken();
    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 资源授权API响应拦截器
resourceAuthApi.interceptors.response.use(
  (response: AxiosResponse) => {
    // 检查是否有订阅状态更新
    const subscriptionUpdate = response.headers['x-subscription-update'];
    if (subscriptionUpdate) {
      try {
        const subscription = JSON.parse(subscriptionUpdate);
        window.dispatchEvent(new CustomEvent('subscriptionUpdate', {
          detail: subscription
        }));
      } catch (e) {
        console.warn('Failed to parse subscription update:', e);
      }
    }
    
    // 检查是否有资源访问权限更新
    const accessUpdate = response.headers['x-access-update'];
    if (accessUpdate) {
      try {
        const access = JSON.parse(accessUpdate);
        window.dispatchEvent(new CustomEvent('resourceAccessUpdate', {
          detail: access
        }));
      } catch (e) {
        console.warn('Failed to parse access update:', e);
      }
    }
    
    return response;
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.dispatchEvent(new CustomEvent('authLogout'));
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    // 处理订阅相关错误
    if (error.response?.status === 402) {
      window.dispatchEvent(new CustomEvent('paymentRequired', {
        detail: {
          message: 'Payment required to access this resource',
          resource: error.config?.url
        }
      }));
    }
    
    // 处理资源访问限制
    if (error.response?.status === 403) {
      const errorData = error.response.data;
      if (errorData?.code === 'SUBSCRIPTION_REQUIRED') {
        window.dispatchEvent(new CustomEvent('subscriptionRequired', {
          detail: {
            message: errorData.message,
            feature: errorData.feature
          }
        }));
      } else if (errorData?.code === 'RESOURCE_ACCESS_DENIED') {
        window.dispatchEvent(new CustomEvent('resourceAccessDenied', {
          detail: {
            message: errorData.message,
            resource: errorData.resource
          }
        }));
      }
    }
    
    return Promise.reject(error);
  }
);

// 资源授权相关API
export const resourceAuthAPI = {
  // 订阅管理
  getSubscriptionInfo() {
    return resourceAuthApi.get('/subscriptions/');
  },
  
  getSubscriptionFeatures() {
    return resourceAuthApi.get('/subscription-features/');
  },
  
  subscribeToFeature(featureId: number) {
    return resourceAuthApi.post(`/subscribe/${featureId}/`);
  },
  
  unsubscribeFromFeature(featureId: number) {
    return resourceAuthApi.post(`/unsubscribe/${featureId}/`);
  },
  
  getSubscriptionHistory() {
    return resourceAuthApi.get('/subscription-history/');
  },
  
  renewSubscription(subscriptionId: number) {
    return resourceAuthApi.post(`/subscriptions/${subscriptionId}/renew/`);
  },
  
  // 资源授权管理
  getResourceAuthorizations() {
    return resourceAuthApi.get('/authorizations/');
  },
  
  getResourceCategories() {
    return resourceAuthApi.get('/resource-categories/');
  },
  
  checkResourceAccess(resourceId: number) {
    return resourceAuthApi.get(`/resources/${resourceId}/access/`);
  },
  
  requestResourceAccess(resourceId: number) {
    return resourceAuthApi.post(`/resources/${resourceId}/request-access/`);
  },
  
  grantResourceAccess(resourceId: number, userId: number) {
    return resourceAuthApi.post(`/resources/${resourceId}/grant-access/`, {
      user_id: userId
    });
  },
  
  revokeResourceAccess(authorizationId: number) {
    return resourceAuthApi.delete(`/authorizations/${authorizationId}/`);
  },
  
  // 资源分享
  getResourceShares() {
    return resourceAuthApi.get('/shares/');
  },
  
  shareResource(resourceId: number, shareData: ShareData) {
    return resourceAuthApi.post(`/resources/${resourceId}/share/`, {
      ...shareData,
      resource_id: resourceId
    });
  },
  
  revokeResourceShare(shareId: number) {
    return resourceAuthApi.delete(`/shares/${shareId}/`);
  },
  
  getShareLink(shareId: number) {
    return resourceAuthApi.get(`/shares/${shareId}/link/`);
  },
  
  // 统计和分析
  getAuthorizationStats() {
    return resourceAuthApi.get('/stats/authorizations/');
  }
};

// 分析API实例
const analyticsApi: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/analytics',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

// 应用性能增强到分析API实例
apiEnhancer.enhance(analyticsApi, {
  enableCache: true,
  cachableEndpoints: ['/analytics']
});

// 分析API请求拦截器
analyticsApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    const csrfToken = getCsrfToken();
    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 分析API响应拦截器
analyticsApi.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.dispatchEvent(new CustomEvent('authLogout'));
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    // 处理分析数据访问限制
    if (error.response?.status === 403) {
      window.dispatchEvent(new CustomEvent('analyticsAccessDenied', {
        detail: {
          message: 'Analytics access denied',
          endpoint: error.config?.url
        }
      }));
    }
    
    return Promise.reject(error);
  }
);

// 分析相关API
export const analyticsAPI = {
  // 用户参与度指标
  getUserEngagementMetrics() {
    return analyticsApi.get('/user-engagement/');
  },
  
  // 行为分析
  getBehaviorAnalysis() {
    return analyticsApi.get('/behavior-analysis/');
  },
  
  // 游戏元素效果分析
  getGameElementEffectiveness() {
    return analyticsApi.get('/game-element-effectiveness/');
  },
  
  // 概览数据
  getOverview() {
    return analyticsApi.get('/overview/');
  },
  
  // 每日活动数据
  getDailyActivity() {
    return analyticsApi.get('/daily-activity/');
  },
  
  // 每周进度数据
  getWeeklyProgress() {
    return analyticsApi.get('/weekly-progress/');
  },
  
  // 综合分析数据
  getComprehensive() {
    return analyticsApi.get('/comprehensive/');
  },
  
  // 导出数据
  exportData(dataType: string, format: string = 'json') {
    return analyticsApi.get(`/export/${dataType}/`, {
      params: { format },
      responseType: format === 'csv' ? 'blob' : 'json'
    });
  }
};

// 教学API实例
const teachingApi: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/teaching',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

// 应用性能增强到教学API实例
apiEnhancer.enhance(teachingApi, {
  enableCache: true,
  cachableEndpoints: ['/api/teaching']
});

// 教学API请求拦截器
teachingApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    const csrfToken = getCsrfToken();
    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 教学API响应拦截器
teachingApi.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.dispatchEvent(new CustomEvent('authLogout'));
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    // 处理教学功能访问限制
    if (error.response?.status === 403) {
      window.dispatchEvent(new CustomEvent('teachingAccessDenied', {
        detail: {
          message: 'Teaching feature access denied',
          endpoint: error.config?.url
        }
      }));
    }
    
    return Promise.reject(error);
  }
);

// 教学相关API
export const teachingAPI = {
  // 学习目标管理
  getLearningGoals(params: WordParams = {}) {
    return teachingApi.get('/learning-goals/', { params });
  },
  
  createLearningGoal(data: LearningGoalData) {
    return teachingApi.post('/learning-goals/', data);
  },
  
  updateLearningGoal(id: number, data: Partial<LearningGoalData>) {
    return teachingApi.put(`/learning-goals/${id}/`, data);
  },
  
  deleteLearningGoal(id: number) {
    return teachingApi.delete(`/learning-goals/${id}/`);
  },
  
  getLearningGoalProgress(id: number) {
    return teachingApi.get(`/learning-goals/${id}/progress/`);
  },
  
  addWordsToGoal(id: number, wordIds: number[]) {
    return teachingApi.post(`/learning-goals/${id}/add-words/`, { word_ids: wordIds });
  },
  
  removeWordsFromGoal(id: number, wordIds: number[]) {
    return teachingApi.post(`/learning-goals/${id}/remove-words/`, { word_ids: wordIds });
  },
  
  getCurrentLearningGoal() {
    return teachingApi.get('/learning-goals/current/');
  },
  
  // 学习会话管理
  createLearningSession(data: LearningSessionData) {
    return teachingApi.post('/learning-sessions/', data);
  },
  
  endLearningSession(id: number) {
    return teachingApi.post(`/learning-sessions/${id}/end/`);
  },
  
  getLearningSessionRecords(id: number) {
    return teachingApi.get(`/learning-sessions/${id}/records/`);
  },
  
  // 单词学习记录
  createWordLearningRecord(data: WordLearningRecordData) {
    return teachingApi.post('/word-learning-records/', data);
  },
  
  getWordLearningRecords(params: WordParams = {}) {
    return teachingApi.get('/word-learning-records/', { params });
  },
  
  getWordLearningStatistics() {
    return teachingApi.get('/word-learning-statistics/');
  },
  
  // 练习相关
  getPracticeWords(params: WordParams = {}) {
    return teachingApi.get('/practice-words/', { params });
  }
};

export default api;