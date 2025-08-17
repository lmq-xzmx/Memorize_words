import { createApp } from 'vue'
import type { App as VueApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 导入新的 SCSS 架构
import './styles/index.scss'

// 保持向后兼容，导入现有的 CSS 文件
import './assets/css/main.css'
import './utils/clearPositionRestrictions'

// 类型安全的动态导入
let styleConflictResolver: any = null
let authSyncModule: any = null
let permissionModule: any = null
let globalErrorHandler: any = null

// 动态导入模块以避免类型错误
try {
  styleConflictResolver = require('./utils/styleConflictResolver').default || require('./utils/styleConflictResolver')
} catch (e) {
  console.warn('styleConflictResolver module not found:', e)
}

try {
  authSyncModule = require('./utils/authSync')
} catch (e) {
  console.warn('authSync module not found:', e)
}

try {
  permissionModule = require('./directives/permission')
} catch (e) {
  console.warn('permission module not found:', e)
}

try {
  globalErrorHandler = require('./utils/globalErrorHandler').default || require('./utils/globalErrorHandler')
} catch (e) {
  console.warn('globalErrorHandler module not found:', e)
}

// 创建Vue应用实例
const app: VueApp = createApp(App)

// 使用路由和状态管理
app.use(router)
// 类型断言修复store使用问题
app.use(store as any)

// 注册权限指令
if (permissionModule && permissionModule.installPermissionDirectives) {
  permissionModule.installPermissionDirectives(app)
}

// 初始化登录状态同步
if (authSyncModule && authSyncModule.initAuthSync) {
  authSyncModule.initAuthSync().then((result: any) => {
    console.log('登录状态同步初始化完成:', result)
    
    // 启动定期同步（每5分钟）
    if (authSyncModule.startAuthSyncInterval) {
      authSyncModule.startAuthSyncInterval(5 * 60 * 1000)
      console.log('定期登录状态同步已启动')
    }
  }).catch((error: any) => {
    console.error('登录状态同步初始化失败:', error)
  })
}

// 挂载应用
app.mount('#app')

// 初始化样式冲突解决器
setTimeout(() => {
  if (styleConflictResolver) {
    styleConflictResolver.resolveAllConflicts()
    styleConflictResolver.startAutoFix()
    console.log('✅ 样式冲突解决器已启动')
  }
}, 1000)

// 全局错误处理
app.config.errorHandler = (err: unknown, vm: any, info: string) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
  
  // 使用全局错误处理器处理Vue错误
  if (globalErrorHandler && globalErrorHandler.handleError) {
    globalErrorHandler.handleError({
      type: 'vue_error',
      error: {
        message: (err as Error).message,
        stack: (err as Error).stack,
        component: vm?.$options.name || 'Unknown',
        info: info
      },
      timestamp: new Date().toISOString()
    })
  }
}

// 设置全局错误处理器实例
if (typeof window !== 'undefined' && globalErrorHandler && globalErrorHandler.handleError) {
  window.globalErrorHandler = globalErrorHandler.handleError
}

// 开发环境配置
if (import.meta.env.MODE === 'development') {
  // Vue 3中devtools配置已自动处理
  console.log('开发模式已启用')
}