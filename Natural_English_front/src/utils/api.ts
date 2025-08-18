import axios from 'axios';

const api = axios.create({
  baseURL: '/', 
  withCredentials: true, // 允许跨域请求携带cookie
});

// 从cookie中获取CSRF令牌的函数
function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
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

// 添加请求拦截器，在每个请求头中添加CSRF令牌
api.interceptors.request.use(config => {
  const csrfToken = getCsrfToken();
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// 添加响应拦截器处理401错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储的token
      localStorage.removeItem('token');
      
      // 清除Vuex中的认证状态
      import('@/store').then(({ default: store }) => {
        store.commit('auth/CLEAR_TOKEN');
        store.commit('user/CLEAR_USER_DATA');
      });
      
      // 如果当前不在登录页面，则重定向到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;