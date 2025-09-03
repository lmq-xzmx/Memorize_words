import { createSSRApp } from 'vue'
import App from './App.vue'
import store from './store'
import { createPinia } from 'pinia'
import uView from 'uview-ui'
import './styles/index.scss'
import './uni.scss'
import './utils/request.js'

// 导入全局组件
import { registerGlobalComponents } from './components/GlobalComponents'

// 导入工具函数
import * as utils from './utils'

// 导入API
import api from './api'

// 导入权限管理
import permission from './utils/permission'

// 导入路由守卫
import routeGuard from './utils/routeGuard'

// 导入权限指令
import { registerPermissionDirectives } from './directives/permission'

export function createApp() {
  const app = createSSRApp(App)
  
  // 使用 Vuex store
  app.use(store)
  
  // 使用Pinia
  const pinia = createPinia()
  app.use(pinia)
  
  // 使用uView UI
  app.use(uView)
  
  // 注册全局组件
  registerGlobalComponents(app)
  
  // 安装路由守卫
  routeGuard.install()
  
  // 注册权限指令
  registerPermissionDirectives(app)
  
  // 全局配置
  app.config.globalProperties.$store = store
  app.config.globalProperties.$api = api
  app.config.globalProperties.$utils = utils
  app.config.globalProperties.$permission = permission
  
  // 全局方法
  app.config.globalProperties.$showToast = (title, icon = 'none', duration = 2000) => {
    uni.showToast({
      title,
      icon,
      duration
    })
  }
  
  app.config.globalProperties.$showLoading = (title = '加载中...') => {
    uni.showLoading({
      title,
      mask: true
    })
  }
  
  app.config.globalProperties.$hideLoading = () => {
    uni.hideLoading()
  }
  
  app.config.globalProperties.$showModal = (title, content) => {
    return new Promise((resolve) => {
      uni.showModal({
        title,
        content,
        success: (res) => {
          resolve(res.confirm)
        },
        fail: () => {
          resolve(false)
        }
      })
    })
  }
  
  app.config.globalProperties.$navigateTo = (url, params = {}) => {
    let queryString = ''
    if (Object.keys(params).length > 0) {
      queryString = '?' + Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')
    }
    
    uni.navigateTo({
      url: url + queryString,
      fail: (err) => {
        console.error('页面跳转失败:', err)
        uni.showToast({
          title: '页面跳转失败',
          icon: 'none'
        })
      }
    })
  }
  
  app.config.globalProperties.$redirectTo = (url, params = {}) => {
    let queryString = ''
    if (Object.keys(params).length > 0) {
      queryString = '?' + Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')
    }
    
    uni.redirectTo({
      url: url + queryString,
      fail: (err) => {
        console.error('页面重定向失败:', err)
        uni.showToast({
          title: '页面重定向失败',
          icon: 'none'
        })
      }
    })
  }
  
  app.config.globalProperties.$switchTab = (url) => {
    uni.switchTab({
      url,
      fail: (err) => {
        console.error('切换标签页失败:', err)
        uni.showToast({
          title: '切换页面失败',
          icon: 'none'
        })
      }
    })
  }
  
  // 全局错误处理
  app.config.errorHandler = (err, vm, info) => {
    console.error('全局错误:', err)
    console.error('错误信息:', info)
    
    // 在生产环境中，可以将错误发送到错误监控服务
    if (process.env.NODE_ENV === 'production') {
      // 发送错误到监控服务
      // errorReporting.captureException(err, { extra: { info } })
    }
    
    // 显示用户友好的错误提示
    uni.showToast({
      title: '应用出现异常，请稍后重试',
      icon: 'none',
      duration: 3000
    })
  }
  
  // 全局警告处理
  app.config.warnHandler = (msg, vm, trace) => {
    if (process.env.NODE_ENV === 'development') {
      console.warn('Vue警告:', msg)
      console.warn('组件追踪:', trace)
    }
  }
  
  return {
    app
  }
}