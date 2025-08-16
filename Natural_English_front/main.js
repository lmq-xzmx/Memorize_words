import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import './assets/css/main.css'
import './utils/clearPositionRestrictions.js'
import styleConflictResolver from './utils/styleConflictResolver.js'
import { initAuthSync, startAuthSyncInterval } from './utils/authSync.js'
import { installPermissionDirectives } from './directives/permission.js'
import globalErrorHandler from './utils/globalErrorHandler.js'

// 创建Vue应用实例
const app = createApp(App)

// 使用路由和状态管理
app.use(store)
app.use(router)

// 注册权限指令
installPermissionDirectives(app)

// 初始化登录状态同步
initAuthSync().then(result => {
  console.log('登录状态同步初始化完成:', result)
  
  // 启动定期同步（每5分钟）
  startAuthSyncInterval(5 * 60 * 1000)
  console.log('定期登录状态同步已启动')
}).catch(error => {
  console.error('登录状态同步初始化失败:', error)
})

// 挂载应用
app.mount('#app')

// 初始化样式冲突解决器
setTimeout(() => {
  styleConflictResolver.resolveAllConflicts()
  styleConflictResolver.startAutoFix()
  console.log('✅ 样式冲突解决器已启动')
}, 1000)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
  
  // 使用全局错误处理器处理Vue错误
  globalErrorHandler.handleError({
    type: 'vue_error',
    error: {
      message: err.message,
      stack: err.stack,
      component: vm?.$options.name || 'Unknown',
      info: info
    },
    timestamp: new Date().toISOString()
  })
}

// 设置全局错误处理器实例
window.globalErrorHandler = globalErrorHandler

// 开发环境配置
if (import.meta.env.MODE === 'development') {
  app.config.devtools = true
}