import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './assets/css/main.css'
import './utils/clearPositionRestrictions.js'
import { initAuthSync, startAuthSyncInterval } from './utils/authSync.js'

// 创建Vue应用实例
const app = createApp(App)

// 使用路由和状态管理
app.use(store)
app.use(router)

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

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
}

// 开发环境配置
if (process.env.NODE_ENV === 'development') {
  app.config.devtools = true
}