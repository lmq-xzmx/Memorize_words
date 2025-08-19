# Natural English uni-app 技术架构规范

## 📋 文档信息
- **项目名称**: Natural English 英语学习平台
- **文档类型**: uni-app 技术架构规范
- **更新日期**: 2025年1月
- **系统完成度**: 98%
- **技术栈**: uni-app + Vue3 + TypeScript + Pinia + 权限管理系统

## 📖 目录
1. [架构概览](#架构概览)
2. [权限驱动架构](#权限驱动架构)
3. [技术栈选型](#技术栈选型)
4. [项目结构规范](#项目结构规范)
5. [权限集成架构](#权限集成架构)
6. [状态管理规范](#状态管理规范)
7. [组件开发规范](#组件开发规范)
8. [API接口规范](#API接口规范)
9. [实时通信架构](#实时通信架构)
10. [性能优化策略](#性能优化策略)
11. [安全架构设计](#安全架构设计)
12. [测试架构规范](#测试架构规范)
13. [部署与运维](#部署与运维)

## 🏗️ 架构概览

### 1.1 整体架构图

```
Natural English uni-app 技术架构
├── 🎨 表现层 (Presentation Layer)
│   ├── 页面组件 (Pages)
│   ├── 业务组件 (Components)
│   ├── 权限指令 (Directives)
│   └── 路由守卫 (Route Guards)
├── 🔐 权限控制层 (Permission Layer)
│   ├── 权限验证 (Permission Validation)
│   ├── 角色管理 (Role Management)
│   ├── 菜单控制 (Menu Control)
│   └── 数据过滤 (Data Filtering)
├── 🎛️ 业务逻辑层 (Business Logic Layer)
│   ├── 状态管理 (State Management)
│   ├── 业务服务 (Business Services)
│   ├── 数据处理 (Data Processing)
│   └── 工具函数 (Utilities)
├── 🔄 通信层 (Communication Layer)
│   ├── HTTP 客户端 (HTTP Client)
│   ├── WebSocket 管理 (WebSocket Manager)
│   ├── 权限同步 (Permission Sync)
│   └── 缓存管理 (Cache Management)
├── 📱 平台适配层 (Platform Adapter Layer)
│   ├── 微信小程序 (WeChat Mini Program)
│   ├── 支付宝小程序 (Alipay Mini Program)
│   ├── H5 应用 (H5 Application)
│   └── App 应用 (Native App)
└── 🛠️ 基础设施层 (Infrastructure Layer)
    ├── 构建工具 (Build Tools)
    ├── 代码规范 (Code Standards)
    ├── 测试框架 (Testing Framework)
    └── 部署配置 (Deployment Config)
```

### 1.2 核心设计原则

**权限驱动原则：**
- 所有功能模块基于权限系统设计
- 实时权限验证和同步
- 细粒度权限控制

**模块化原则：**
- 高内聚、低耦合的模块设计
- 可插拔的功能组件
- 标准化的接口规范

**性能优先原则：**
- 懒加载和按需加载
- 智能缓存策略
- 代码分割优化

**跨平台兼容原则：**
- 统一的代码基础
- 平台特性适配
- 一致的用户体验

## 🔐 权限驱动架构

### 2.1 权限架构设计

#### 权限系统集成架构
```typescript
// 权限系统架构接口
interface PermissionArchitecture {
  // 权限验证层
  validation: {
    userPermissions: UserPermissionValidator
    rolePermissions: RolePermissionValidator
    resourcePermissions: ResourcePermissionValidator
    dynamicPermissions: DynamicPermissionValidator
  }
  
  // 权限缓存层
  cache: {
    permissionCache: PermissionCacheManager
    roleCache: RoleCacheManager
    userCache: UserCacheManager
    menuCache: MenuCacheManager
  }
  
  // 权限同步层
  sync: {
    websocketSync: WebSocketPermissionSync
    httpSync: HttpPermissionSync
    localSync: LocalPermissionSync
    conflictResolver: PermissionConflictResolver
  }
  
  // 权限控制层
  control: {
    menuControl: MenuPermissionController
    pageControl: PagePermissionController
    componentControl: ComponentPermissionController
    dataControl: DataPermissionController
  }
}
```

#### 权限验证流程
```typescript
// 权限验证服务
class PermissionValidationService {
  private cache = new PermissionCacheManager()
  private sync = new WebSocketPermissionSync()
  
  // 验证用户权限
  async validateUserPermission(
    userId: string, 
    permission: string, 
    resource?: string
  ): Promise<PermissionValidationResult> {
    try {
      // 1. 检查缓存
      const cachedResult = await this.cache.getPermissionCache(userId, permission)
      if (cachedResult && !this.isExpired(cachedResult)) {
        return cachedResult
      }
      
      // 2. 获取用户权限
      const userPermissions = await this.getUserPermissions(userId)
      
      // 3. 验证权限
      const hasPermission = this.checkPermission(userPermissions, permission, resource)
      
      // 4. 缓存结果
      const result: PermissionValidationResult = {
        hasPermission,
        userId,
        permission,
        resource,
        timestamp: new Date(),
        ttl: 5 * 60 * 1000 // 5分钟
      }
      
      await this.cache.setPermissionCache(userId, permission, result)
      
      return result
      
    } catch (error) {
      console.error('权限验证失败:', error)
      return {
        hasPermission: false,
        userId,
        permission,
        resource,
        timestamp: new Date(),
        error: error.message
      }
    }
  }
  
  // 批量验证权限
  async validateBatchPermissions(
    userId: string, 
    permissions: string[]
  ): Promise<Record<string, boolean>> {
    const results: Record<string, boolean> = {}
    
    const validationPromises = permissions.map(async (permission) => {
      const result = await this.validateUserPermission(userId, permission)
      results[permission] = result.hasPermission
    })
    
    await Promise.all(validationPromises)
    return results
  }
  
  // 实时权限同步
  private initPermissionSync() {
    this.sync.onPermissionUpdate((data) => {
      this.handlePermissionUpdate(data)
    })
    
    this.sync.onRoleUpdate((data) => {
      this.handleRoleUpdate(data)
    })
  }
  
  private async handlePermissionUpdate(data: PermissionUpdateData) {
    // 清除相关缓存
    await this.cache.clearUserPermissionCache(data.userId)
    
    // 通知组件更新
    this.notifyPermissionChange(data)
  }
}

export const permissionValidationService = new PermissionValidationService()
```

### 2.2 权限组合式API

#### usePermission Hook
```typescript
// composables/usePermission.ts
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { permissionValidationService } from '@/services/permissionService'

export function usePermission() {
  const userPermissions = ref<string[]>([])
  const userRole = ref<string>('')
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 检查单个权限
  const hasPermission = (permission: string, resource?: string): boolean => {
    if (!permission) return true
    
    // 超级管理员拥有所有权限
    if (userRole.value === 'super_admin') return true
    
    // 检查具体权限
    return userPermissions.value.includes(permission)
  }
  
  // 检查多个权限（AND关系）
  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(permission => hasPermission(permission))
  }
  
  // 检查多个权限（OR关系）
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(permission => hasPermission(permission))
  }
  
  // 检查角色权限
  const hasRole = (role: string): boolean => {
    return userRole.value === role
  }
  
  // 检查多个角色
  const hasAnyRole = (roles: string[]): boolean => {
    return roles.includes(userRole.value)
  }
  
  // 获取用户权限
  const getUserPermissions = async () => {
    loading.value = true
    error.value = null
    
    try {
      const user = getCurrentUser()
      if (!user) throw new Error('用户未登录')
      
      const permissions = await permissionValidationService.getUserPermissions(user.id)
      userPermissions.value = permissions
      userRole.value = user.role
      
    } catch (err) {
      error.value = err.message
      console.error('获取用户权限失败:', err)
    } finally {
      loading.value = false
    }
  }
  
  // 刷新权限
  const refreshPermissions = async () => {
    await getUserPermissions()
  }
  
  // 权限变更监听
  const setupPermissionListener = () => {
    const handlePermissionUpdate = (data: any) => {
      if (data.userId === getCurrentUser()?.id) {
        refreshPermissions()
      }
    }
    
    // WebSocket监听
    websocketManager.on('permission_updated', handlePermissionUpdate)
    websocketManager.on('role_updated', handlePermissionUpdate)
    
    return () => {
      websocketManager.off('permission_updated', handlePermissionUpdate)
      websocketManager.off('role_updated', handlePermissionUpdate)
    }
  }
  
  // 计算属性
  const isAdmin = computed(() => hasRole('admin'))
  const isTeacher = computed(() => hasRole('teacher'))
  const isStudent = computed(() => hasRole('student'))
  const canManageUsers = computed(() => hasPermission('user_management_access'))
  const canManageClasses = computed(() => hasPermission('class_management_access'))
  
  // 生命周期
  onMounted(() => {
    getUserPermissions()
    const cleanup = setupPermissionListener()
    
    onUnmounted(() => {
      cleanup()
    })
  })
  
  return {
    // 状态
    userPermissions: readonly(userPermissions),
    userRole: readonly(userRole),
    loading: readonly(loading),
    error: readonly(error),
    
    // 方法
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    hasRole,
    hasAnyRole,
    refreshPermissions,
    
    // 计算属性
    isAdmin,
    isTeacher,
    isStudent,
    canManageUsers,
    canManageClasses
  }
}
```

## 🛠️ 技术栈选型

### 3.1 核心技术栈

| 技术分类 | 选择方案 | 版本要求 | 选择理由 |
|----------|----------|----------|----------|
| **框架** | uni-app | 3.0+ | 跨平台支持，生态完善 |
| **前端框架** | Vue 3 | 3.3+ | 组合式API，性能优化 |
| **语言** | TypeScript | 5.0+ | 类型安全，开发效率 |
| **状态管理** | Pinia | 2.1+ | Vue 3原生支持，轻量级 |
| **UI框架** | uni-ui | 1.4+ | 官方组件库，兼容性好 |
| **HTTP客户端** | uni.request | - | 平台统一API |
| **实时通信** | WebSocket | - | 权限实时同步 |
| **构建工具** | Vite | 4.0+ | 快速构建，HMR支持 |
| **代码规范** | ESLint + Prettier | 最新 | 代码质量保证 |
| **测试框架** | Vitest + @vue/test-utils | 最新 | Vue 3测试支持 |

### 3.2 权限相关技术选型

| 功能模块 | 技术方案 | 实现方式 |
|----------|----------|----------|
| **权限验证** | 自研权限系统 | 基于RBAC模型 |
| **权限缓存** | LRU Cache + LocalStorage | 内存+持久化双重缓存 |
| **权限同步** | WebSocket + HTTP轮询 | 实时+兜底双重保障 |
| **权限指令** | Vue 3自定义指令 | v-permission指令 |
| **路由守卫** | Vue Router守卫 | 页面级权限控制 |
| **组件权限** | 高阶组件 + Composables | 组件级权限控制 |

## 📁 项目结构规范

### 4.1 目录结构

```
src/
├── 📱 pages/                    # 页面目录
│   ├── auth/                    # 认证相关页面
│   │   ├── login/
│   │   └── register/
│   ├── learning/                # 学习模块页面
│   │   ├── words/
│   │   ├── reading/
│   │   └── listening/
│   ├── teacher/                 # 教师功能页面
│   │   ├── classes/
│   │   ├── students/
│   │   └── analytics/
│   ├── admin/                   # 管理员页面
│   │   ├── users/
│   │   ├── roles/
│   │   └── permissions/
│   └── profile/                 # 个人中心
├── 🧩 components/               # 组件目录
│   ├── base/                    # 基础组件
│   │   ├── BaseButton/
│   │   ├── BaseInput/
│   │   └── BaseModal/
│   ├── business/                # 业务组件
│   │   ├── WordCard/
│   │   ├── ProgressChart/
│   │   └── ClassList/
│   ├── permission/              # 权限组件
│   │   ├── PermissionGuard/
│   │   ├── RoleGuard/
│   │   └── PermissionButton/
│   └── layout/                  # 布局组件
│       ├── AppHeader/
│       ├── AppTabBar/
│       └── AppSidebar/
├── 🎛️ composables/              # 组合式函数
│   ├── usePermission.ts         # 权限相关
│   ├── useAuth.ts              # 认证相关
│   ├── useMenu.ts              # 菜单相关
│   ├── useWebSocket.ts         # WebSocket
│   └── useCache.ts             # 缓存管理
├── 🏪 stores/                   # 状态管理
│   ├── auth.ts                 # 认证状态
│   ├── permission.ts           # 权限状态
│   ├── menu.ts                 # 菜单状态
│   ├── user.ts                 # 用户状态
│   └── app.ts                  # 应用状态
├── 🔧 services/                 # 服务层
│   ├── api/                    # API服务
│   │   ├── authApi.ts
│   │   ├── permissionApi.ts
│   │   ├── userApi.ts
│   │   └── learningApi.ts
│   ├── permission/             # 权限服务
│   │   ├── permissionService.ts
│   │   ├── roleService.ts
│   │   └── menuService.ts
│   ├── cache/                  # 缓存服务
│   │   ├── cacheManager.ts
│   │   └── permissionCache.ts
│   └── websocket/              # WebSocket服务
│       ├── websocketManager.ts
│       └── permissionSync.ts
├── 🛠️ utils/                    # 工具函数
│   ├── request.ts              # HTTP请求封装
│   ├── storage.ts              # 存储工具
│   ├── permission.ts           # 权限工具
│   ├── validation.ts           # 验证工具
│   └── common.ts               # 通用工具
├── 🎨 styles/                   # 样式文件
│   ├── variables.scss          # 变量定义
│   ├── mixins.scss            # 混入函数
│   ├── base.scss              # 基础样式
│   └── themes/                # 主题样式
├── 🔧 config/                   # 配置文件
│   ├── app.config.ts           # 应用配置
│   ├── api.config.ts           # API配置
│   ├── permission.config.ts    # 权限配置
│   └── websocket.config.ts     # WebSocket配置
├── 📝 types/                    # 类型定义
│   ├── api.ts                  # API类型
│   ├── permission.ts           # 权限类型
│   ├── user.ts                 # 用户类型
│   └── common.ts               # 通用类型
└── 🧪 __tests__/                # 测试文件
    ├── components/
    ├── composables/
    ├── services/
    └── utils/
```

### 4.2 文件命名规范

#### 组件命名
```typescript
// 基础组件：Base + 功能名称
BaseButton.vue
BaseInput.vue
BaseModal.vue

// 业务组件：功能名称 + 组件类型
WordCard.vue
ProgressChart.vue
ClassList.vue

// 权限组件：Permission + 功能名称
PermissionGuard.vue
PermissionButton.vue
RoleGuard.vue

// 页面组件：功能名称 + Index
WordLearningIndex.vue
ClassManagementIndex.vue
UserManagementIndex.vue
```

#### 文件命名
```typescript
// 服务文件：功能名称 + Service
authService.ts
permissionService.ts
userService.ts

// 工具文件：功能名称 + Utils
permissionUtils.ts
validationUtils.ts
storageUtils.ts

// 类型文件：功能名称 + Types
permissionTypes.ts
userTypes.ts
apiTypes.ts

// 配置文件：功能名称 + Config
appConfig.ts
permissionConfig.ts
websocketConfig.ts
```

## 🔐 权限集成架构

### 5.1 权限系统集成

#### 权限配置管理
```typescript
// config/permission.config.ts
export const permissionConfig = {
  // 权限缓存配置
  cache: {
    ttl: 5 * 60 * 1000,           // 5分钟
    maxSize: 1000,                // 最大缓存数量
    strategy: 'LRU'               // 缓存策略
  },
  
  // WebSocket配置
  websocket: {
    url: process.env.VUE_APP_WS_URL,
    reconnectInterval: 3000,      // 重连间隔
    maxReconnectAttempts: 5       // 最大重连次数
  },
  
  // 权限验证配置
  validation: {
    enableCache: true,            // 启用缓存
    enableRealTimeSync: true,     // 启用实时同步
    fallbackToLocal: true,        // 网络失败时使用本地缓存
    strictMode: false             // 严格模式
  },
  
  // 角色权限映射
  rolePermissions: {
    super_admin: ['*'],           // 超级管理员拥有所有权限
    admin: [
      'user_management_access',
      'role_management_access',
      'system_config_access',
      'analytics_access'
    ],
    teacher: [
      'class_management_access',
      'student_progress_access',
      'teaching_resources_access',
      'basic_access'
    ],
    student: [
      'learning_access',
      'word_learning_access',
      'reading_access',
      'listening_access',
      'basic_access'
    ],
    parent: [
      'student_progress_view',
      'basic_access'
    ]
  },
  
  // 菜单权限映射
  menuPermissions: {
    '/pages/admin/users': ['user_management_access'],
    '/pages/admin/roles': ['role_management_access'],
    '/pages/teacher/classes': ['class_management_access'],
    '/pages/teacher/students': ['student_progress_access'],
    '/pages/learning/words': ['word_learning_access'],
    '/pages/learning/reading': ['reading_access'],
    '/pages/learning/listening': ['listening_access']
  }
}
```

#### 权限路由守卫
```typescript
// router/permission.guard.ts
import { usePermission } from '@/composables/usePermission'
import { permissionConfig } from '@/config/permission.config'

export function setupPermissionGuard(router: any) {
  router.beforeEach(async (to: any, from: any, next: any) => {
    const { hasPermission, loading, getUserPermissions } = usePermission()
    
    // 等待权限加载完成
    if (loading.value) {
      await new Promise(resolve => {
        const unwatch = watch(loading, (newLoading) => {
          if (!newLoading) {
            unwatch()
            resolve(true)
          }
        })
      })
    }
    
    // 检查页面权限
    const requiredPermissions = permissionConfig.menuPermissions[to.path]
    
    if (requiredPermissions && requiredPermissions.length > 0) {
      const hasAccess = requiredPermissions.some(permission => 
        hasPermission(permission)
      )
      
      if (!hasAccess) {
        // 无权限访问
        uni.showModal({
          title: '访问受限',
          content: '您没有访问此页面的权限',
          showCancel: false,
          success: () => {
            // 跳转到首页或登录页
            if (from.path !== '/') {
              next('/')
            } else {
              next('/pages/auth/login')
            }
          }
        })
        return
      }
    }
    
    next()
  })
}
```

### 5.2 权限指令实现

#### v-permission指令
```typescript
// directives/permission.ts
import { Directive } from 'vue'
import { usePermission } from '@/composables/usePermission'

export const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding) {
    const { hasPermission, hasAnyPermission, hasRole } = usePermission()
    
    const { value, modifiers } = binding
    
    let hasAccess = false
    
    if (modifiers.role) {
      // 角色验证
      hasAccess = Array.isArray(value) 
        ? value.some(role => hasRole(role))
        : hasRole(value)
    } else if (modifiers.any) {
      // 任一权限验证
      hasAccess = Array.isArray(value) 
        ? hasAnyPermission(value)
        : hasPermission(value)
    } else {
      // 默认权限验证
      hasAccess = Array.isArray(value)
        ? value.every(permission => hasPermission(permission))
        : hasPermission(value)
    }
    
    if (!hasAccess) {
      if (modifiers.hide) {
        // 隐藏元素
        el.style.display = 'none'
      } else if (modifiers.disable) {
        // 禁用元素
        el.setAttribute('disabled', 'true')
        el.style.opacity = '0.5'
        el.style.pointerEvents = 'none'
      } else {
        // 默认移除元素
        el.remove()
      }
    }
  },
  
  updated(el: HTMLElement, binding) {
    // 权限变更时重新验证
    this.mounted(el, binding)
  }
}

// 使用示例
/*
<!-- 基础权限验证 -->
<button v-permission="'user_management_access'">用户管理</button>

<!-- 多权限验证（AND关系） -->
<button v-permission="['user_management_access', 'role_management_access']">
  高级管理
</button>

<!-- 任一权限验证（OR关系） -->
<button v-permission.any="['teacher_access', 'admin_access']">
  教学功能
</button>

<!-- 角色验证 -->
<button v-permission.role="'admin'">管理员功能</button>

<!-- 隐藏而不是移除 -->
<button v-permission.hide="'admin_access'">管理功能</button>

<!-- 禁用而不是移除 -->
<button v-permission.disable="'premium_access'">高级功能</button>
*/
```

## 🏪 状态管理规范

### 6.1 Pinia Store架构

#### 权限状态管理
```typescript
// stores/permission.ts
import { defineStore } from 'pinia'
import { permissionValidationService } from '@/services/permissionService'
import { websocketManager } from '@/services/websocket/websocketManager'

export const usePermissionStore = defineStore('permission', {
  state: () => ({
    // 用户权限
    userPermissions: [] as string[],
    userRole: '' as string,
    
    // 权限缓存
    permissionCache: new Map<string, any>(),
    
    // 加载状态
    loading: false,
    error: null as string | null,
    
    // 同步状态
    lastSyncTime: null as Date | null,
    syncStatus: 'idle' as 'idle' | 'syncing' | 'error'
  }),
  
  getters: {
    // 检查权限
    hasPermission: (state) => (permission: string) => {
      if (state.userRole === 'super_admin') return true
      return state.userPermissions.includes(permission)
    },
    
    // 检查多个权限
    hasAllPermissions: (state) => (permissions: string[]) => {
      if (state.userRole === 'super_admin') return true
      return permissions.every(permission => 
        state.userPermissions.includes(permission)
      )
    },
    
    // 检查任一权限
    hasAnyPermission: (state) => (permissions: string[]) => {
      if (state.userRole === 'super_admin') return true
      return permissions.some(permission => 
        state.userPermissions.includes(permission)
      )
    },
    
    // 检查角色
    hasRole: (state) => (role: string) => {
      return state.userRole === role
    },
    
    // 权限统计
    permissionStats: (state) => ({
      totalPermissions: state.userPermissions.length,
      role: state.userRole,
      lastSync: state.lastSyncTime,
      cacheSize: state.permissionCache.size
    })
  },
  
  actions: {
    // 初始化权限
    async initPermissions() {
      this.loading = true
      this.error = null
      
      try {
        const user = getCurrentUser()
        if (!user) throw new Error('用户未登录')
        
        // 获取用户权限
        const permissions = await permissionValidationService.getUserPermissions(user.id)
        
        this.userPermissions = permissions
        this.userRole = user.role
        this.lastSyncTime = new Date()
        
        // 初始化WebSocket监听
        this.setupWebSocketListeners()
        
      } catch (error) {
        this.error = error.message
        console.error('初始化权限失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    // 刷新权限
    async refreshPermissions() {
      await this.initPermissions()
    },
    
    // 更新权限
    updatePermissions(permissions: string[]) {
      this.userPermissions = permissions
      this.lastSyncTime = new Date()
      
      // 清除相关缓存
      this.clearPermissionCache()
    },
    
    // 更新角色
    updateRole(role: string) {
      this.userRole = role
      this.lastSyncTime = new Date()
      
      // 清除相关缓存
      this.clearPermissionCache()
    },
    
    // 缓存权限验证结果
    cachePermissionResult(key: string, result: any) {
      this.permissionCache.set(key, {
        ...result,
        timestamp: Date.now()
      })
    },
    
    // 获取缓存的权限结果
    getCachedPermissionResult(key: string) {
      const cached = this.permissionCache.get(key)
      if (!cached) return null
      
      // 检查是否过期（5分钟）
      if (Date.now() - cached.timestamp > 5 * 60 * 1000) {
        this.permissionCache.delete(key)
        return null
      }
      
      return cached
    },
    
    // 清除权限缓存
    clearPermissionCache() {
      this.permissionCache.clear()
    },
    
    // 设置同步状态
    setSyncStatus(status: 'idle' | 'syncing' | 'error') {
      this.syncStatus = status
    },
    
    // WebSocket监听器
    setupWebSocketListeners() {
      websocketManager.on('permission_updated', (data) => {
        this.handlePermissionUpdate(data)
      })
      
      websocketManager.on('role_updated', (data) => {
        this.handleRoleUpdate(data)
      })
    },
    
    // 处理权限更新
    handlePermissionUpdate(data: any) {
      const user = getCurrentUser()
      if (data.userId === user?.id) {
        this.updatePermissions(data.permissions)
        
        // 通知其他组件
        uni.$emit('permission-updated', data)
      }
    },
    
    // 处理角色更新
    handleRoleUpdate(data: any) {
      const user = getCurrentUser()
      if (data.userId === user?.id) {
        this.updateRole(data.role)
        
        // 通知其他组件
        uni.$emit('role-updated', data)
      }
    }
  }
})
```

#### 菜单状态管理
```typescript
// stores/menu.ts
import { defineStore } from 'pinia'
import { usePermissionStore } from './permission'
import { menuPermissionConfig } from '@/config/menuConfig'

export const useMenuStore = defineStore('menu', {
  state: () => ({
    // 菜单配置
    menuConfig: menuPermissionConfig,
    
    // 当前菜单状态
    currentTab: 'learning',
    activeMenu: '',
    
    // 自定义配置
    customization: {
      tabBarOrder: [] as string[],
      hiddenMenus: [] as string[],
      quickActions: [] as any[],
      theme: {
        primaryColor: '#007AFF',
        darkMode: false
      }
    },
    
    // 加载状态
    loading: false,
    lastUpdateTime: null as Date | null
  }),
  
  getters: {
    // 过滤后的TabBar
    filteredTabBar: (state) => {
      const permissionStore = usePermissionStore()
      
      return state.menuConfig.tabBar.filter(tab => {
        return permissionStore.hasPermission(tab.permission)
      })
    },
    
    // 过滤后的菜单
    filteredMenus: (state) => {
      const permissionStore = usePermissionStore()
      const result: any = {}
      
      Object.keys(state.menuConfig.primaryMenus).forEach(category => {
        result[category] = state.menuConfig.primaryMenus[category].filter(menu => {
          // 检查权限
          if (!permissionStore.hasPermission(menu.permission)) {
            return false
          }
          
          // 检查角色
          if (menu.roles && !menu.roles.includes(permissionStore.userRole)) {
            return false
          }
          
          // 检查是否被隐藏
          if (state.customization.hiddenMenus.includes(menu.id)) {
            return false
          }
          
          return true
        })
      })
      
      return result
    },
    
    // 快捷操作
    availableQuickActions: (state) => {
      const permissionStore = usePermissionStore()
      
      return state.customization.quickActions.filter(action => {
        return permissionStore.hasPermission(action.permission)
      })
    }
  },
  
  actions: {
    // 设置当前Tab
    setCurrentTab(tabId: string) {
      this.currentTab = tabId
    },
    
    // 设置活动菜单
    setActiveMenu(menuId: string) {
      this.activeMenu = menuId
    },
    
    // 更新菜单配置
    updateMenuConfig(config: any) {
      this.menuConfig = { ...this.menuConfig, ...config }
      this.lastUpdateTime = new Date()
    },
    
    // 保存自定义配置
    async saveCustomization(customization: any) {
      try {
        this.loading = true
        
        // 保存到服务器
        await menuCustomizationService.saveUserCustomization(customization)
        
        // 更新本地状态
        this.customization = { ...this.customization, ...customization }
        
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
        
      } catch (error) {
        console.error('保存菜单自定义失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    // 重置自定义配置
    resetCustomization() {
      this.customization = {
        tabBarOrder: [],
        hiddenMenus: [],
        quickActions: [],
        theme: {
          primaryColor: '#007AFF',
          darkMode: false
        }
      }
    },
    
    // 添加快捷操作
    addQuickAction(action: any) {
      if (this.customization.quickActions.length < 6) {
        this.customization.quickActions.push(action)
      }
    },
    
    // 移除快捷操作
    removeQuickAction(actionId: string) {
      const index = this.customization.quickActions.findIndex(
        action => action.id === actionId
      )
      if (index > -1) {
        this.customization.quickActions.splice(index, 1)
      }
    }
  }
})
```

## 🧩 组件开发规范

### 7.1 权限组件开发

#### 权限守卫组件
```vue
<!-- components/permission/PermissionGuard.vue -->
<template>
  <div v-if="hasAccess" class="permission-guard">
    <slot />
  </div>
  <div v-else-if="showFallback" class="permission-fallback">
    <slot name="fallback">
      <div class="no-permission">
        <text class="no-permission-text">{{ fallbackText }}</text>
      </div>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePermission } from '@/composables/usePermission'

interface Props {
  permission?: string | string[]
  role?: string | string[]
  requireAll?: boolean
  showFallback?: boolean
  fallbackText?: string
}

const props = withDefaults(defineProps<Props>(), {
  requireAll: true,
  showFallback: false,
  fallbackText: '暂无访问权限'
})

const { hasPermission, hasAnyPermission, hasRole, hasAnyRole } = usePermission()

const hasAccess = computed(() => {
  // 角色验证
  if (props.role) {
    if (Array.isArray(props.role)) {
      return hasAnyRole(props.role)
    } else {
      return hasRole(props.role)
    }
  }
  
  // 权限验证
  if (props.permission) {
    if (Array.isArray(props.permission)) {
      return props.requireAll 
        ? props.permission.every(p => hasPermission(p))
        : hasAnyPermission(props.permission)
    } else {
      return hasPermission(props.permission)
    }
  }
  
  // 默认允许访问
  return true
})
</script>

<style scoped>
.permission-guard {
  width: 100%;
}

.permission-fallback {
  width: 100%;
}

.no-permission {
  padding: 20px;
  text-align: center;
  color: #999;
}

.no-permission-text {
  font-size: 14px;
}
</style>
```

#### 权限按钮组件
```vue
<!-- components/permission/PermissionButton.vue -->
<template>
  <button
    v-if="visible"
    :class="buttonClass"
    :disabled="isDisabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePermission } from '@/composables/usePermission'

interface Props {
  permission?: string | string[]
  role?: string | string[]
  requireAll?: boolean
  hideWhenNoPermission?: boolean
  disableWhenNoPermission?: boolean
  type?: 'primary' | 'secondary' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  requireAll: true,
  hideWhenNoPermission: false,
  disableWhenNoPermission: true,
  type: 'primary',
  size: 'medium',
  disabled: false
})

const emit = defineEmits<{
  click: [event: Event]
  permissionDenied: [permission: string | string[]]
}>()

const { hasPermission, hasAnyPermission, hasRole, hasAnyRole } = usePermission()

const hasAccess = computed(() => {
  // 角色验证
  if (props.role) {
    if (Array.isArray(props.role)) {
      return hasAnyRole(props.role)
    } else {
      return hasRole(props.role)
    }
  }
  
  // 权限验证
  if (props.permission) {
    if (Array.isArray(props.permission)) {
      return props.requireAll 
        ? props.permission.every(p => hasPermission(p))
        : hasAnyPermission(props.permission)
    } else {
      return hasPermission(props.permission)
    }
  }
  
  return true
})

const visible = computed(() => {
  if (props.hideWhenNoPermission) {
    return hasAccess.value
  }
  return true
})

const isDisabled = computed(() => {
  if (props.disabled) return true
  if (props.disableWhenNoPermission && !hasAccess.value) return true
  return false
})

const buttonClass = computed(() => {
  return [
    'permission-button',
    `permission-button--${props.type}`,
    `permission-button--${props.size}`,
    {
      'permission-button--disabled': isDisabled.value,
      'permission-button--no-permission': !hasAccess.value
    }
  ]
})

const handleClick = (event: Event) => {
  if (!hasAccess.value) {
    emit('permissionDenied', props.permission || props.role || '')
    return
  }
  
  emit('click', event)
}
</script>

<style scoped>
.permission-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.permission-button--primary {
  background-color: #007AFF;
  color: white;
}

.permission-button--secondary {
  background-color: #f0f0f0;
  color: #333;
}

.permission-button--danger {
  background-color: #FF3B30;
  color: white;
}

.permission-button--small {
  padding: 4px 8px;
  font-size: 12px;
}

.permission-button--large {
  padding: 12px 24px;
  font-size: 16px;
}

.permission-button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.permission-button--no-permission {
  background-color: #ccc;
  color: #666;
}
</style>
```

### 7.2 业务组件规范

#### 组件开发模板
```vue
<!-- components/business/ExampleComponent.vue -->
<template>
  <div class="example-component">
    <!-- 权限控制的内容 -->
    <PermissionGuard :permission="requiredPermission">
      <div class="component-content">
        <!-- 组件内容 -->
      </div>
    </PermissionGuard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePermission } from '@/composables/usePermission'
import PermissionGuard from '@/components/permission/PermissionGuard.vue'

// Props定义
interface Props {
  // 基础属性
  title?: string
  data?: any[]
  
  // 权限属性
  requiredPermission?: string
  requiredRole?: string
  
  // 样式属性
  theme?: 'light' | 'dark'
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  data: () => [],
  theme: 'light',
  size: 'medium'
})

// Emits定义
const emit = defineEmits<{
  click: [item: any]
  change: [value: any]
  permissionDenied: [permission: string]
}>()

// 权限检查
const { hasPermission } = usePermission()

// 响应式数据
const loading = ref(false)
const error = ref<string | null>(null)

// 计算属性
const componentClass = computed(() => [
  'example-component',
  `example-component--${props.theme}`,
  `example-component--${props.size}`
])

const hasAccess = computed(() => {
  if (props.requiredPermission) {
    return hasPermission(props.requiredPermission)
  }
  return true
})

// 方法
const handleClick = (item: any) => {
  if (!hasAccess.value) {
    emit('permissionDenied', props.requiredPermission || '')
    return
  }
  
  emit('click', item)
}

// 生命周期
onMounted(() => {
  // 组件初始化逻辑
})

// 暴露给父组件的方法
defineExpose({
  refresh: () => {
    // 刷新组件数据
  }
})
</script>

<style scoped>
.example-component {
  /* 组件样式 */
}

.example-component--light {
  /* 浅色主题 */
}

.example-component--dark {
  /* 深色主题 */
}

.example-component--small {
  /* 小尺寸 */
}

.example-component--medium {
  /* 中等尺寸 */
}

.example-component--large {
  /* 大尺寸 */
}
</style>
```

## 🌐 API接口规范

### 8.1 HTTP客户端封装

#### 请求拦截器
```typescript
// utils/request.ts
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

class HttpClient {
  private baseURL: string
  private timeout: number
  
  constructor() {
    this.baseURL = process.env.VUE_APP_API_BASE_URL || ''
    this.timeout = 10000
  }
  
  // 请求拦截器
  private async beforeRequest(config: any) {
    const authStore = useAuthStore()
    
    // 添加认证头
    if (authStore.token) {
      config.header = {
        ...config.header,
        'Authorization': `Bearer ${authStore.token}`
      }
    }
    
    // 添加权限头
    const permissionStore = usePermissionStore()
    if (permissionStore.userRole) {
      config.header = {
        ...config.header,
        'X-User-Role': permissionStore.userRole
      }
    }
    
    // 添加请求ID用于追踪
    config.header = {
      ...config.header,
      'X-Request-ID': this.generateRequestId()
    }
    
    return config
  }
  
  // 响应拦截器
  private async afterResponse(response: any) {
    const { statusCode, data } = response
    
    // 处理权限相关错误
    if (statusCode === 401) {
      // 未认证
      const authStore = useAuthStore()
      await authStore.logout()
      
      uni.showModal({
        title: '认证失败',
        content: '请重新登录',
        showCancel: false,
        success: () => {
          uni.reLaunch({
            url: '/pages/auth/login'
          })
        }
      })
      
      throw new Error('未认证')
    }
    
    if (statusCode === 403) {
      // 权限不足
      uni.showModal({
        title: '权限不足',
        content: '您没有执行此操作的权限',
        showCancel: false
      })
      
      throw new Error('权限不足')
    }
    
    if (statusCode === 200) {
      // 检查权限变更
      if (data.permissionUpdated) {
        const permissionStore = usePermissionStore()
        await permissionStore.refreshPermissions()
      }
      
      return data
    }
    
    throw new Error(`请求失败: ${statusCode}`)
  }
  
  // 通用请求方法
  async request(config: any) {
    try {
      // 请求前处理
      const processedConfig = await this.beforeRequest({
        url: this.baseURL + config.url,
        timeout: this.timeout,
        ...config
      })
      
      // 发送请求
      const response = await uni.request(processedConfig)
      
      // 响应后处理
      return await this.afterResponse(response)
      
    } catch (error) {
      console.error('HTTP请求失败:', error)
      throw error
    }
  }
  
  // GET请求
  get(url: string, params?: any) {
    return this.request({
      url,
      method: 'GET',
      data: params
    })
  }
  
  // POST请求
  post(url: string, data?: any) {
    return this.request({
      url,
      method: 'POST',
      data
    })
  }
  
  // PUT请求
  put(url: string, data?: any) {
    return this.request({
      url,
      method: 'PUT',
      data
    })
  }
  
  // DELETE请求
  delete(url: string, params?: any) {
    return this.request({
      url,
      method: 'DELETE',
      data: params
    })
  }
  
  // 生成请求ID
  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }
}

export const httpClient = new HttpClient()
```

### 8.2 权限相关API

#### 权限API服务
```typescript
// services/api/permissionApi.ts
import { httpClient } from '@/utils/request'

export class PermissionApi {
  // 获取用户权限
  static async getUserPermissions(userId: string): Promise<string[]> {
    const response = await httpClient.get(`/api/permissions/user/${userId}`)
    return response.data.permissions
  }
  
  // 获取角色权限
  static async getRolePermissions(roleId: string): Promise<string[]> {
    const response = await httpClient.get(`/api/permissions/role/${roleId}`)
    return response.data.permissions
  }
  
  // 验证权限
  static async validatePermission(
    userId: string, 
    permission: string, 
    resource?: string
  ): Promise<boolean> {
    const response = await httpClient.post('/api/permissions/validate', {
      userId,
      permission,
      resource
    })
    return response.data.hasPermission
  }
  
  // 批量验证权限
  static async validateBatchPermissions(
    userId: string, 
    permissions: string[]
  ): Promise<Record<string, boolean>> {
    const response = await httpClient.post('/api/permissions/validate-batch', {
      userId,
      permissions
    })
    return response.data.results
  }
  
  // 更新用户权限
  static async updateUserPermissions(
    userId: string, 
    permissions: string[]
  ): Promise<void> {
    await httpClient.put(`/api/permissions/user/${userId}`, {
      permissions
    })
  }
  
  // 获取权限树
  static async getPermissionTree(): Promise<any[]> {
    const response = await httpClient.get('/api/permissions/tree')
    return response.data.tree
  }
  
  // 获取用户菜单权限
  static async getUserMenuPermissions(userId: string): Promise<any> {
    const response = await httpClient.get(`/api/permissions/menu/${userId}`)
    return response.data.menuConfig
  }
}
```

## 🔄 实时通信架构

### 9.1 WebSocket管理器

#### WebSocket连接管理
```typescript
// services/websocket/websocketManager.ts
import { permissionConfig } from '@/config/permission.config'

export class WebSocketManager {
  private ws: any = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000
  private heartbeatInterval: any = null
  private listeners = new Map<string, Function[]>()
  
  constructor() {
    this.url = permissionConfig.websocket.url
    this.maxReconnectAttempts = permissionConfig.websocket.maxReconnectAttempts
    this.reconnectInterval = permissionConfig.websocket.reconnectInterval
  }
  
  // 连接WebSocket
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = uni.connectSocket({
          url: this.url,
          success: () => {
            console.log('WebSocket连接成功')
          },
          fail: (error) => {
            console.error('WebSocket连接失败:', error)
            reject(error)
          }
        })
        
        this.ws.onOpen(() => {
          console.log('WebSocket连接已打开')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        })
        
        this.ws.onMessage((event: any) => {
          this.handleMessage(event.data)
        })
        
        this.ws.onClose(() => {
          console.log('WebSocket连接已关闭')
          this.stopHeartbeat()
          this.attemptReconnect()
        })
        
        this.ws.onError((error: any) => {
          console.error('WebSocket错误:', error)
          this.stopHeartbeat()
        })
        
      } catch (error) {
        reject(error)
      }
    })
  }
  
  // 断开连接
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.stopHeartbeat()
  }
  
  // 发送消息
  send(message: any) {
    if (this.ws && this.isConnected()) {
      this.ws.send({
        data: JSON.stringify(message)
      })
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }
  
  // 检查连接状态
  isConnected(): boolean {
    return this.ws && this.ws.readyState === 1
  }
  
  // 添加消息监听器
  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(callback)
  }
  
  // 移除消息监听器
  off(event: string, callback?: Function) {
    if (!this.listeners.has(event)) return
    
    if (callback) {
      const callbacks = this.listeners.get(event)!
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    } else {
      this.listeners.delete(event)
    }
  }
  
  // 处理接收到的消息
  private handleMessage(data: string) {
    try {
      const message = JSON.parse(data)
      const { type, payload } = message
      
      // 触发对应的监听器
      if (this.listeners.has(type)) {
        const callbacks = this.listeners.get(type)!
        callbacks.forEach(callback => {
          try {
            callback(payload)
          } catch (error) {
            console.error('WebSocket消息处理错误:', error)
          }
        })
      }
      
    } catch (error) {
      console.error('WebSocket消息解析错误:', error)
    }
  }
  
  // 尝试重连
  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('WebSocket重连次数已达上限')
      return
    }
    
    this.reconnectAttempts++
    console.log(`WebSocket重连尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
    
    setTimeout(() => {
      this.connect().catch(() => {
        // 重连失败，继续尝试
      })
    }, this.reconnectInterval)
  }
  
  // 开始心跳
  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send({
          type: 'heartbeat',
          timestamp: Date.now()
        })
      }
    }, 30000) // 30秒心跳
  }
  
  // 停止心跳
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }
}

export const websocketManager = new WebSocketManager()
```

### 9.2 权限实时同步

#### 权限同步服务
```typescript
// services/websocket/permissionSync.ts
import { websocketManager } from './websocketManager'
import { usePermissionStore } from '@/stores/permission'
import { useMenuStore } from '@/stores/menu'

export class PermissionSyncService {
  private permissionStore = usePermissionStore()
  private menuStore = useMenuStore()
  
  constructor() {
    this.initListeners()
  }
  
  // 初始化监听器
  private initListeners() {
    // 权限更新
    websocketManager.on('permission_updated', this.handlePermissionUpdate.bind(this))
    
    // 角色更新
    websocketManager.on('role_updated', this.handleRoleUpdate.bind(this))
    
    // 菜单配置更新
    websocketManager.on('menu_config_updated', this.handleMenuConfigUpdate.bind(this))
    
    // 用户状态更新
    websocketManager.on('user_status_updated', this.handleUserStatusUpdate.bind(this))
  }
  
  // 处理权限更新
  private async handlePermissionUpdate(data: any) {
    const { userId, permissions, timestamp } = data
    const currentUser = getCurrentUser()
    
    if (currentUser && userId === currentUser.id) {
      console.log('收到权限更新通知:', data)
      
      // 更新权限状态
      this.permissionStore.updatePermissions(permissions)
      
      // 刷新菜单
      await this.refreshMenus()
      
      // 显示通知
      this.showPermissionUpdateNotification('权限已更新')
      
      // 触发全局事件
      uni.$emit('permission-updated', data)
    }
  }
  
  // 处理角色更新
  private async handleRoleUpdate(data: any) {
    const { userId, role, permissions, timestamp } = data
    const currentUser = getCurrentUser()
    
    if (currentUser &&