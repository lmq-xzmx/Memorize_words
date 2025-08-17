/// <reference types="vite/client" />

// Vue单文件组件类型声明
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 环境变量类型声明
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_WS_URL: string
  readonly VITE_STATIC_URL: string
  readonly MODE: string
  // 更多环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 全局类型声明
declare global {
  interface Window {
    globalErrorHandler?: (error: any) => void
  }
}

// 模块声明

declare module './store' {
  import type { Store } from 'vuex'
  const store: Store<any>
  export default store
}

// 工具模块声明


declare module './utils/authSync' {
  export const initAuthSync: () => Promise<any>
  export const startAuthSyncInterval: (interval: number) => void
}

declare module './directives/permission' {
  import type { App } from 'vue'
  export const installPermissionDirectives: (app: App) => void
}

declare module './utils/globalErrorHandler' {
  const globalErrorHandler: {
    handleError: (error: any) => void
  }
  export default globalErrorHandler
}

// CSS和其他资源模块
declare module '*.css' {
  const content: string
  export default content
}

declare module './utils/clearPositionRestrictions' {
  // 副作用模块，无导出
}

// Vuex 类型声明
declare module 'vuex' {
  export * from 'vuex/types/index.d.ts'
}

// API 模块类型声明
declare module '../utils/api' {
  interface ApiResponse<T = any> {
    data: T
    status: number
    statusText: string
  }
  
  interface ApiInstance {
    get<T = any>(url: string, config?: any): Promise<ApiResponse<T>>
    post<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>>
    put<T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>>
    delete<T = any>(url: string, config?: any): Promise<ApiResponse<T>>
  }
  
  const api: ApiInstance
  export default api
}

export {}