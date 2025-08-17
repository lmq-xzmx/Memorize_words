// Vue 组件类型声明
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 样式冲突解决器类型声明
declare module '*/utils/styleConflictResolver' {
  interface StyleConflictResolver {
    resolveAllConflicts(): void
    startAutoFix(): void
  }
  
  const styleConflictResolver: StyleConflictResolver
  export default styleConflictResolver
}

// 权限同步工具类型声明
declare module '*/utils/authSync' {
  export function initAuthSync(): Promise<any>
  export function startAuthSyncInterval(interval: number): void
}

// 权限指令类型声明
declare module '*/directives/permission' {
  import type { App } from 'vue'
  // 权限指令相关类型已在实际模块中定义
}

// 全局错误处理器类型声明
declare module '*/utils/globalErrorHandler' {
  const globalErrorHandler: any
  export default globalErrorHandler
}

// 清除位置限制工具类型声明
declare module '*/utils/clearPositionRestrictions' {
  // 这个模块可能只是执行一些初始化代码，不导出任何内容
}

// Store 类型声明
declare module '*/store' {
  import type { Store } from 'vuex'
  import type { RootState } from '../types/store'
  
  const store: Store<RootState>
  export default store
}

// Router 类型声明
declare module '*/router' {
  import type { Router } from 'vue-router'
  
  const router: Router
  export default router
}