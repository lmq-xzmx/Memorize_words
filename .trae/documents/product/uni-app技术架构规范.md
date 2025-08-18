# uni-app 技术架构规范

## 1. 技术栈概述

### 1.1 核心技术栈

**前端框架：**
- **Vue 3.3.0+** - 使用 Composition API 和 TypeScript
- **uni-app 3.0+** - 跨平台开发框架
- **TypeScript 4.9+** - 类型安全和开发体验
- **Vite 4.0+** - 构建工具和开发服务器

**UI 组件库：**
- **uni-ui** - uni-app 官方组件库
- **uView Plus** - 第三方 UI 组件库（可选）
- **自定义组件** - 游戏化学习组件

**状态管理：**
- **Pinia** - Vue 3 推荐的状态管理库
- **uni.storage** - 本地数据持久化
- **Vuex 4.x** - 备选方案（兼容性考虑）

### 1.2 跨平台支持

**目标平台：**
- 微信小程序
- 支付宝小程序
- H5 网页版
- Android App
- iOS App

**平台特性适配：**
```javascript
// 条件编译示例
// #ifdef MP-WEIXIN
// 微信小程序特有代码
// #endif

// #ifdef H5
// H5 特有代码
// #endif

// #ifdef APP-PLUS
// App 特有代码
// #endif
```

## 2. 项目结构规范

### 2.1 目录结构

```
uni-app-project/
├── src/
│   ├── components/          # 公共组件
│   │   ├── base/           # 基础组件
│   │   ├── business/       # 业务组件
│   │   └── game/          # 游戏化组件
│   ├── pages/              # 页面文件
│   │   ├── index/         # 首页
│   │   ├── learning/      # 学习模块
│   │   ├── profile/       # 个人中心
│   │   └── admin/         # 管理模块
│   ├── static/             # 静态资源
│   │   ├── images/        # 图片资源
│   │   ├── icons/         # 图标资源
│   │   └── audio/         # 音频资源
│   ├── store/              # 状态管理
│   │   ├── modules/       # 模块化 store
│   │   └── index.ts       # store 入口
│   ├── utils/              # 工具函数
│   │   ├── api.ts         # API 封装
│   │   ├── auth.ts        # 认证工具
│   │   ├── permission.ts  # 权限工具
│   │   └── storage.ts     # 存储工具
│   ├── styles/             # 样式文件
│   │   ├── common.scss    # 公共样式
│   │   ├── variables.scss # 变量定义
│   │   └── mixins.scss    # 混入样式
│   ├── types/              # TypeScript 类型定义
│   ├── App.vue            # 应用入口
│   ├── main.ts            # 主入口文件
│   ├── manifest.json      # 应用配置
│   └── pages.json         # 页面配置
├── dist/                   # 构建输出
├── node_modules/          # 依赖包
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript 配置
├── vite.config.ts         # Vite 配置
└── README.md              # 项目说明
```

### 2.2 核心配置文件

**manifest.json 配置：**
```json
{
  "name": "Natural English",
  "appid": "__UNI__XXXXXX",
  "description": "英语学习小程序",
  "versionName": "1.0.0",
  "versionCode": "100",
  "transformPx": false,
  "mp-weixin": {
    "appid": "wx1234567890",
    "setting": {
      "urlCheck": false,
      "es6": true,
      "minified": true
    },
    "usingComponents": true,
    "permission": {
      "scope.userLocation": {
        "desc": "用于获取用户位置信息"
      }
    }
  },
  "h5": {
    "title": "Natural English",
    "template": "index.html",
    "router": {
      "mode": "hash"
    }
  }
}
```

**pages.json 配置：**
```json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页",
        "enablePullDownRefresh": true
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "Natural English",
    "navigationBarBackgroundColor": "#F8F8F8",
    "backgroundColor": "#F8F8F8"
  },
  "tabBar": {
    "color": "#7A7E83",
    "selectedColor": "#3cc51f",
    "borderStyle": "black",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "iconPath": "static/tab-home.png",
        "selectedIconPath": "static/tab-home-active.png",
        "text": "首页"
      }
    ]
  }
}
```

## 3. 开发规范

### 3.1 组件开发规范

**组件命名：**
- 使用 PascalCase 命名
- 组件文件名与组件名保持一致
- 业务组件添加业务前缀

**组件结构：**
```vue
<template>
  <view class="component-name">
    <!-- 组件内容 -->
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props 定义
interface Props {
  title: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// Emits 定义
interface Emits {
  click: [event: Event]
  change: [value: string]
}

const emit = defineEmits<Emits>()

// 响应式数据
const isLoading = ref(false)

// 计算属性
const computedClass = computed(() => {
  return {
    'is-disabled': props.disabled,
    'is-loading': isLoading.value
  }
})

// 生命周期
onMounted(() => {
  // 初始化逻辑
})

// 方法
const handleClick = (event: Event) => {
  if (props.disabled) return
  emit('click', event)
}
</script>

<style lang="scss" scoped>
.component-name {
  // 样式定义
}
</style>
```

### 3.2 API 调用规范

**API 封装：**
```typescript
// utils/api.ts
import { request } from '@/utils/request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  userInfo: UserInfo
}

export const authAPI = {
  // 登录
  login: (params: LoginParams) => {
    return request<LoginResponse>({
      url: '/api/auth/login',
      method: 'POST',
      data: params
    })
  },
  
  // 获取用户信息
  getUserInfo: () => {
    return request<UserInfo>({
      url: '/api/user/info',
      method: 'GET'
    })
  }
}
```

**请求拦截器：**
```typescript
// utils/request.ts
interface RequestConfig {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

export function request<T>(config: RequestConfig): Promise<T> {
  return new Promise((resolve, reject) => {
    // 添加认证头
    const token = uni.getStorageSync('token')
    if (token) {
      config.header = {
        ...config.header,
        'Authorization': `Bearer ${token}`
      }
    }
    
    uni.request({
      ...config,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data as T)
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}
```

### 3.3 状态管理规范

**Pinia Store 定义：**
```typescript
// store/modules/auth.ts
import { defineStore } from 'pinia'
import { authAPI } from '@/utils/api'

interface AuthState {
  token: string
  userInfo: UserInfo | null
  isLoggedIn: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: uni.getStorageSync('token') || '',
    userInfo: null,
    isLoggedIn: false
  }),
  
  getters: {
    hasPermission: (state) => (permission: string) => {
      return state.userInfo?.permissions?.includes(permission) || false
    }
  },
  
  actions: {
    async login(params: LoginParams) {
      try {
        const response = await authAPI.login(params)
        this.token = response.token
        this.userInfo = response.userInfo
        this.isLoggedIn = true
        
        // 持久化存储
        uni.setStorageSync('token', response.token)
        uni.setStorageSync('userInfo', response.userInfo)
        
        return response
      } catch (error) {
        throw error
      }
    },
    
    logout() {
      this.token = ''
      this.userInfo = null
      this.isLoggedIn = false
      
      // 清除存储
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
    }
  }
})
```

## 4. 性能优化

### 4.1 代码分割

```typescript
// 路由懒加载
const routes = [
  {
    path: '/learning',
    component: () => import('@/pages/learning/index.vue')
  }
]
```

### 4.2 图片优化

```vue
<template>
  <!-- 使用 lazy-load 属性 -->
  <image 
    :src="imageSrc" 
    lazy-load
    mode="aspectFit"
    @load="onImageLoad"
    @error="onImageError"
  />
</template>
```

### 4.3 列表优化

```vue
<template>
  <!-- 使用虚拟列表 -->
  <recycle-list 
    :list="dataList"
    :item-height="100"
    @scroll="onScroll"
  >
    <template #default="{ item, index }">
      <ListItem :data="item" :index="index" />
    </template>
  </recycle-list>
</template>
```

## 5. 测试规范

### 5.1 单元测试

```typescript
// tests/components/Button.spec.ts
import { mount } from '@vue/test-utils'
import Button from '@/components/Button.vue'

describe('Button Component', () => {
  it('should render correctly', () => {
    const wrapper = mount(Button, {
      props: {
        text: 'Click me'
      }
    })
    
    expect(wrapper.text()).toBe('Click me')
  })
  
  it('should emit click event', async () => {
    const wrapper = mount(Button)
    await wrapper.trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

### 5.2 E2E 测试

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('/login')
  
  await page.fill('[data-testid="username"]', 'testuser')
  await page.fill('[data-testid="password"]', 'password')
  await page.click('[data-testid="login-button"]')
  
  await expect(page).toHaveURL('/dashboard')
})
```

## 6. 部署配置

### 6.1 构建配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version)
  }
})
```

### 6.2 环境配置

```typescript
// config/env.ts
interface EnvConfig {
  API_BASE_URL: string
  APP_NAME: string
  DEBUG: boolean
}

const envConfigs: Record<string, EnvConfig> = {
  development: {
    API_BASE_URL: 'http://localhost:8001/api',
    APP_NAME: 'Natural English (Dev)',
    DEBUG: true
  },
  production: {
    API_BASE_URL: 'https://api.naturalenglish.com',
    APP_NAME: 'Natural English',
    DEBUG: false
  }
}

export const ENV = envConfigs[process.env.NODE_ENV || 'development']
```

## 7. 最佳实践

### 7.1 代码规范
- 使用 ESLint + Prettier 进行代码格式化
- 遵循 Vue 3 Composition API 最佳实践
- 使用 TypeScript 严格模式
- 组件单一职责原则

### 7.2 性能优化
- 合理使用 v-show 和 v-if
- 避免在模板中使用复杂表达式
- 使用 Object.freeze() 冻结大型数据
- 合理使用缓存策略

### 7.3 用户体验
- 提供加载状态反馈
- 实现错误边界处理
- 支持离线功能
- 优化首屏加载时间

---

本规范文档将随着项目发展持续更新，确保技术栈的先进性和开发效率的最大化。