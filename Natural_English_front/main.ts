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

// ES6 模块导入 - 符合 TypeScript 规范
import styleConflictResolver from './utils/styleConflictResolver'
import { initAuthSync, startAuthSyncInterval } from './utils/authSync'
import { installPermissionDirectives } from './directives/permission'
import globalErrorHandler from './utils/globalErrorHandler'

// 创建Vue应用实例
const app: VueApp = createApp(App)

// 使用路由和状态管理
app.use(router)
// 类型断言修复store使用问题
app.use(store as any)

// 注册权限指令
installPermissionDirectives(app)

// 初始化登录状态同步
initAuthSync().then((result: any) => {
  console.log('登录状态同步初始化完成:', result)
  
  // 启动定期同步（每5分钟）
  startAuthSyncInterval(5 * 60 * 1000)
  console.log('定期登录状态同步已启动')
}).catch((error: any) => {
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
app.config.errorHandler = (err: unknown, vm: any, info: string) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
  
  // 使用全局错误处理器处理Vue错误
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

// 设置全局错误处理器实例
if (typeof window !== 'undefined') {
  (window as any).globalErrorHandler = globalErrorHandler.handleError
}

// 开发环境配置
if (import.meta.env.MODE === 'development') {
  // Vue 3中devtools配置已自动处理
  console.log('开发模式已启用')
}