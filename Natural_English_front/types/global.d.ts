// 全局类型声明文件

// 扩展Window接口
declare global {
  interface Window {
    dynamicPermissionUtils?: any
    __VUE_DEVTOOLS_GLOBAL_HOOK__?: any
    webkitSpeechRecognition?: any
    SpeechRecognition?: any
  }
}

// 声明一些常用的第三方库模块
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '*.json' {
  const value: any
  export default value
}

declare module '*.css' {
  const content: any
  export default content
}

declare module '*.scss' {
  const content: any
  export default content
}

declare module '*.sass' {
  const content: any
  export default content
}

declare module '*.less' {
  const content: any
  export default content
}

declare module '*.styl' {
  const content: any
  export default content
}

// 声明一些可能缺失类型的npm包
declare module 'lodash' {
  const _: any
  export = _
}

declare module 'axios' {
  const axios: any
  export = axios
}

declare module 'moment' {
  const moment: any
  export = moment
}

declare module 'dayjs' {
  const dayjs: any
  export = dayjs
}

// 环境变量类型声明
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string
  readonly MODE: string
  readonly BASE_URL: string
  readonly PROD: boolean
  readonly DEV: boolean
  readonly SSR: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 导出空对象以使此文件成为模块
export {}