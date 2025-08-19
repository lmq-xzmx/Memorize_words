import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { checkRoutePermission } from '@/utils/permissions'
import store from '@/store'

// 页面组件
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import Dashboard from '@/pages/Dashboard.vue'
import Forbidden from '@/pages/Forbidden.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      title: '登录'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      requiresAuth: false,
      title: '注册'
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      permission: 'dashboard.view',
      title: '仪表板'
    }
  },
  // 学习中心路由
  {
    path: '/learning',
    name: 'Learning',
    redirect: '/learning/words',
    meta: {
      requiresAuth: true,
      permission: 'learning.view',
      title: '学习中心'
    },
    children: [
      {
        path: 'words',
        name: 'WordLearning',
        component: () => import('@/pages/learning/WordLearning.vue'),
        meta: {
          requiresAuth: true,
          permission: 'learning.words.view',
          title: '单词学习'
        }
      },
      {
        path: 'sentences',
        name: 'SentenceLearning',
        component: () => import('@/pages/learning/SentenceLearning.vue'),
        meta: {
          requiresAuth: true,
          permission: 'learning.sentences.view',
          title: '句子学习'
        }
      },
      {
        path: 'practice',
        name: 'Practice',
        component: () => import('@/pages/learning/Practice.vue'),
        meta: {
          requiresAuth: true,
          permission: 'learning.practice.view',
          title: '练习测试'
        }
      }
    ]
  },
  // 学习进度路由
  {
    path: '/progress',
    name: 'Progress',
    redirect: '/progress/statistics',
    meta: {
      requiresAuth: true,
      permission: 'progress.view',
      title: '学习进度'
    },
    children: [
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/pages/progress/Statistics.vue'),
        meta: {
          requiresAuth: true,
          permission: 'progress.statistics.view',
          title: '学习统计'
        }
      },
      {
        path: 'achievements',
        name: 'Achievements',
        component: () => import('@/pages/progress/Achievements.vue'),
        meta: {
          requiresAuth: true,
          permission: 'progress.achievements.view',
          title: '成就徽章'
        }
      }
    ]
  },
  // 个人中心路由
  {
    path: '/profile',
    name: 'Profile',
    redirect: '/profile/settings',
    meta: {
      requiresAuth: true,
      permission: 'profile.view',
      title: '个人中心'
    },
    children: [
      {
        path: 'settings',
        name: 'ProfileSettings',
        component: () => import('@/pages/profile/Settings.vue'),
        meta: {
          requiresAuth: true,
          permission: 'profile.settings.view',
          title: '个人设置'
        }
      },
      {
        path: 'history',
        name: 'LearningHistory',
        component: () => import('@/pages/profile/History.vue'),
        meta: {
          requiresAuth: true,
          permission: 'profile.history.view',
          title: '学习历史'
        }
      }
    ]
  },
  // 管理员路由
  {
    path: '/admin',
    name: 'Admin',
    redirect: '/admin/dashboard',
    meta: {
      requiresAuth: true,
      permission: 'admin.dashboard.view',
      roles: ['admin', 'super_admin'],
      securityLevel: 'high',
      title: '管理中心'
    },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/pages/admin/Dashboard.vue'),
        meta: {
          requiresAuth: true,
          permission: 'admin.dashboard.view',
          title: '管理仪表板'
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        redirect: '/admin/users/list',
        meta: {
          requiresAuth: true,
          permission: 'admin.users.view',
          title: '用户管理'
        },
        children: [
          {
            path: 'list',
            name: 'UserList',
            component: () => import('@/pages/admin/UserList.vue'),
            meta: {
              requiresAuth: true,
              permission: 'admin.users.list.view',
              roles: ['admin', 'super_admin'],
              securityLevel: 'medium',
              inheritPermissions: true,
              title: '用户列表'
            }
          },
          {
            path: 'roles',
            name: 'RoleManagement',
            component: () => import('@/pages/admin/RoleManagement.vue'),
            meta: {
              requiresAuth: true,
              permission: {
                permissions: ['admin.users.roles.view', 'admin.users.roles.manage'],
                mode: 'any'
              },
              roles: ['admin', 'super_admin'],
              securityLevel: 'high',
              inheritPermissions: true,
              title: '角色管理'
            }
          },
          {
            path: 'permission-test',
            name: 'PermissionTest',
            component: () => import('@/views/PermissionTest.vue'),
            meta: {
              requiresAuth: true,
              permission: 'admin.permission.test',
              roles: ['admin', 'super_admin'],
              securityLevel: 'medium',
              title: '权限测试'
            }
          },
          {
            path: 'audit-logs',
            name: 'AuditLogManagement',
            component: () => import('@/pages/admin/AuditLogManagement.vue'),
            meta: {
              requiresAuth: true,
              permission: 'admin.audit.logs.view',
              roles: ['admin', 'super_admin'],
              securityLevel: 'high',
              title: '审计日志管理'
            }
          },
          {
            path: 'permission-system',
            name: 'PermissionSystemPanel',
            component: () => import('@/pages/admin/PermissionSystemPanel.vue'),
            meta: {
              requiresAuth: true,
              permission: ['admin.system.manage', 'admin.permission.admin'],
              roles: ['admin', 'super_admin'],
              securityLevel: 'high',
              title: '权限系统管理'
            }
          }
        ]
      }
    ]
  },
  // 教师路由
  {
    path: '/teacher',
    name: 'Teacher',
    redirect: '/teacher/dashboard',
    meta: {
      requiresAuth: true,
      permission: 'teacher.dashboard.view',
      roles: ['teacher', 'admin', 'super_admin'],
      securityLevel: 'medium',
      preloadPermissions: true,
      title: '教师中心'
    },
    children: [
      {
        path: 'dashboard',
        name: 'TeacherDashboard',
        component: () => import('@/pages/teacher/Dashboard.vue'),
        meta: {
          requiresAuth: true,
          permission: 'teacher.dashboard.view',
          title: '教师仪表板'
        }
      },
      {
        path: 'classes',
        name: 'ClassManagement',
        redirect: '/teacher/classes/list',
        meta: {
          requiresAuth: true,
          permission: 'teacher.classes.view',
          title: '班级管理'
        },
        children: [
          {
            path: 'list',
            name: 'ClassList',
            component: () => import('@/pages/teacher/ClassList.vue'),
            meta: {
              requiresAuth: true,
              permission: 'teacher.classes.list.view',
              title: '班级列表'
            }
          },
          {
            path: 'progress',
            name: 'StudentProgress',
            component: () => import('@/pages/teacher/StudentProgress.vue'),
            meta: {
              requiresAuth: true,
              permission: 'teacher.classes.progress.view',
              title: '学生进度'
            }
          }
        ]
      }
    ]
  },
  // 404页面
  {
    path: '/403',
    name: 'Forbidden',
    component: Forbidden,
    meta: {
      requiresAuth: false,
      title: '权限不足'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue'),
    meta: {
      title: '页面未找到'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import { ElMessage } from 'element-plus'

// 扩展路由元信息接口
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    permission?: string | string[] | {
      permissions: string[]
      mode: 'all' | 'any'
    }
    roles?: string[]
    title?: string
    preloadPermissions?: boolean
    inheritPermissions?: boolean
    securityLevel?: 'low' | 'medium' | 'high'
    allowGuest?: boolean
    requiresReauth?: boolean
  }
}

// 权限检查结果接口
interface PermissionCheckResult {
  allowed: boolean
  reason?: string
  redirectTo?: string
  requiresReauth?: boolean
}

// 安全日志记录
function logSecurityEvent(event: string, details: any) {
  const timestamp = new Date().toISOString()
  const logEntry = {
    timestamp,
    event,
    details,
    userAgent: navigator.userAgent,
    url: window.location.href
  }
  
  console.log(`[Security] ${event}:`, logEntry)
  
  // 在生产环境中，这里应该发送到安全日志服务
  if (process.env.NODE_ENV === 'production') {
    // TODO: 发送到安全日志服务
  }
}

// 增强的权限检查函数
async function checkEnhancedPermissions(
  to: any,
  userInfo: any
): Promise<PermissionCheckResult> {
  // 动态导入权限缓存服务，避免循环依赖
  const { PermissionCache } = await import('@/services/permissionCacheService')
  const userId = userInfo.id || userInfo.user_id
  const userRole = userInfo.role
  
  // 1. 检查角色权限
  if (to.meta.roles && to.meta.roles.length > 0) {
    if (!userRole || !to.meta.roles.includes(userRole)) {
      logSecurityEvent('ROLE_ACCESS_DENIED', {
        userId,
        userRole,
        requiredRoles: to.meta.roles,
        route: to.path
      })
      return {
        allowed: false,
        reason: '角色权限不足',
        redirectTo: '/403'
      }
    }
  }
  
  // 2. 检查具体权限
  if (to.meta.permission) {
    try {
      let hasPermission = false
      
      if (typeof to.meta.permission === 'string') {
        hasPermission = await PermissionCache.checkRoute(
          to.meta.permission,
          userId.toString()
        )
      } else if (Array.isArray(to.meta.permission)) {
         // 检查多个权限（默认需要全部）
         const results = await Promise.all(
           to.meta.permission.map((perm: string) => 
             PermissionCache.checkRoute(perm, userId.toString())
           )
         )
         hasPermission = results.every(result => result)
       } else if (typeof to.meta.permission === 'object') {
         // 支持 'all' 或 'any' 模式
         const { permissions, mode = 'all' } = to.meta.permission
         const results = await Promise.all(
           permissions.map((perm: string) => 
             PermissionCache.checkRoute(perm, userId.toString())
           )
         )
        
        hasPermission = mode === 'any' 
          ? results.some(result => result)
          : results.every(result => result)
      }
      
      if (!hasPermission) {
        logSecurityEvent('PERMISSION_ACCESS_DENIED', {
          userId,
          userRole,
          requiredPermission: to.meta.permission,
          route: to.path
        })
        return {
          allowed: false,
          reason: '权限不足',
          redirectTo: '/403'
        }
      }
    } catch (error: any) {
       logSecurityEvent('PERMISSION_CHECK_ERROR', {
         userId,
         error: error?.message || 'Unknown error',
         route: to.path
       })
      return {
        allowed: false,
        reason: '权限检查失败',
        redirectTo: '/403'
      }
    }
  }
  
  // 3. 检查权限继承
  if (to.meta.inheritPermissions && to.matched.length > 1) {
    for (let i = to.matched.length - 2; i >= 0; i--) {
      const parentRoute = to.matched[i]
      if (parentRoute.meta.permission) {
        const parentResult = await checkEnhancedPermissions(
          { meta: parentRoute.meta, path: parentRoute.path },
          userInfo
        )
        if (!parentResult.allowed) {
          return parentResult
        }
      }
    }
  }
  
  // 4. 检查安全级别
  if (to.meta.securityLevel === 'high') {
    const lastAuth = localStorage.getItem('lastAuthTime')
    const authTimeout = 30 * 60 * 1000 // 30分钟
    
    if (!lastAuth || Date.now() - parseInt(lastAuth) > authTimeout) {
      logSecurityEvent('HIGH_SECURITY_REAUTH_REQUIRED', {
        userId,
        route: to.path,
        lastAuth
      })
      return {
        allowed: false,
        reason: '高安全级别页面需要重新认证',
        requiresReauth: true,
        redirectTo: '/login?reauth=true&redirect=' + encodeURIComponent(to.fullPath)
      }
    }
  }
  
  return { allowed: true }
}

// 增强的路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token
  
  // 记录路由访问
  logSecurityEvent('ROUTE_ACCESS_ATTEMPT', {
    from: from.path,
    to: to.path,
    authenticated: isAuthenticated
  })
  
  // 1. 认证检查
  if (to.meta.requiresAuth && !isAuthenticated) {
    if (!to.meta.allowGuest) {
      logSecurityEvent('UNAUTHENTICATED_ACCESS_DENIED', {
        route: to.path
      })
      next('/login?redirect=' + encodeURIComponent(to.fullPath))
      return
    }
  }
  
  // 2. 已登录用户访问登录/注册页面的处理
  if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    // 检查是否是重新认证请求
    if (to.query.reauth) {
      // 允许重新认证
      next()
      return
    }
    next('/dashboard')
    return
  }
  
  // 3. 权限检查（仅对已认证用户）
  if (isAuthenticated) {
    try {
      // 首先尝试从store获取用户信息，如果没有则从API获取
      let userInfo = store.getters['user/currentUser']
      
      if (!userInfo || !userInfo.id) {
        // 从localStorage获取基本信息
        const localUserInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        
        if (localUserInfo.id || localUserInfo.user_id) {
          // 如果localStorage有用户信息，先使用它，然后异步更新store
          userInfo = localUserInfo
          // 异步获取最新用户信息并更新store
          store.dispatch('user/fetchUserInfo').catch(error => {
            console.warn('[Router] 获取用户信息失败:', error)
          })
        } else {
          // 如果localStorage也没有有效用户信息，尝试从API获取
          try {
            await store.dispatch('user/fetchUserInfo')
            userInfo = store.getters['user/currentUser']
          } catch (error) {
            console.error('[Router] 获取用户信息失败:', error)
            logSecurityEvent('FETCH_USER_INFO_FAILED', {
              error: error.message,
              route: to.path
            })
            localStorage.removeItem('token')
            localStorage.removeItem('userInfo')
            next('/login')
            return
          }
        }
      }
      
      const userId = userInfo.id || userInfo.user_id
      
      if (!userId) {
        logSecurityEvent('INVALID_USER_INFO', {
          userInfo,
          route: to.path
        })
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        next('/login')
        return
      }
      
      // 执行增强权限检查
      const permissionResult = await checkEnhancedPermissions(to, userInfo)
      
      if (!permissionResult.allowed) {
        if (permissionResult.requiresReauth) {
          ElMessage.warning(permissionResult.reason || '需要重新认证')
        } else {
          ElMessage.error(permissionResult.reason || '权限不足')
        }
        
        next(permissionResult.redirectTo || '/403')
        return
      }
      
      // 更新最后认证时间（用于高安全级别检查）
      if (to.meta.securityLevel) {
        localStorage.setItem('lastAuthTime', Date.now().toString())
      }
      
      logSecurityEvent('ROUTE_ACCESS_GRANTED', {
        userId,
        route: to.path,
        permissions: to.meta.permission
      })
      
    } catch (error: any) {
       logSecurityEvent('ROUTE_GUARD_ERROR', {
         error: error?.message || 'Unknown error',
         route: to.path
       })
      console.error('[Router] 路由守卫错误:', error)
      next('/403')
      return
    }
  }
  
  // 4. 预加载权限数据（优化性能）
  if (isAuthenticated && to.meta.preloadPermissions) {
    try {
      const { PermissionCache } = await import('@/services/permissionCacheService')
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      const userId = userInfo.id || userInfo.user_id
      
      // 预加载用户权限到缓存
       await PermissionCache.getUserPermissions(userId.toString())
       
       // 预加载角色权限（如果需要的话，可以通过用户权限获取）
       if (userInfo.role) {
         // 通过获取用户权限来预加载相关数据
         await PermissionCache.getUserPermissions(userId.toString(), true)
       }
    } catch (error) {
      console.warn('[Router] 预加载权限数据失败:', error)
      // 预加载失败不影响路由跳转
    }
  }
  
  // 5. 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 英语学习平台`
  }
  
  next()
})

// 路由后置守卫（用于清理和统计）
router.afterEach((to, from) => {
  // 记录成功的路由跳转
  logSecurityEvent('ROUTE_NAVIGATION_SUCCESS', {
    from: from.path,
    to: to.path,
    timestamp: Date.now()
  })
  
  // 清理敏感查询参数
  if (to.query.reauth || to.query.redirect) {
    const cleanQuery = { ...to.query }
    delete cleanQuery.reauth
    if (to.query.redirect && to.path !== '/login') {
      delete cleanQuery.redirect
    }
    
    if (Object.keys(cleanQuery).length !== Object.keys(to.query).length) {
      router.replace({ path: to.path, query: cleanQuery })
    }
  }
})

export default router