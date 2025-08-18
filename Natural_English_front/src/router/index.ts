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
              title: '用户列表'
            }
          },
          {
            path: 'roles',
            name: 'RoleManagement',
            component: () => import('@/pages/admin/RoleManagement.vue'),
            meta: {
              requiresAuth: true,
              permission: 'admin.users.roles.view',
              title: '角色管理'
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

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token
  
  // 如果路由需要认证但用户未登录，跳转到登录页
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  
  // 如果用户已登录但访问登录或注册页，跳转到仪表板
  if (isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/dashboard')
    return
  }
  
  // 权限检查
  if (isAuthenticated && to.meta.permission) {
    try {
      // 确保用户信息已加载
      if (!store.getters['user/userProfile'].id) {
        await store.dispatch('user/fetchUserInfo')
      }
      
      const userPermissions = store.getters['user/userPermissions']
      const hasPermission = checkRoutePermission(to, userPermissions)
      
      if (!hasPermission) {
        // 权限不足，跳转到403页面
        console.warn(`权限不足: 访问 ${to.path} 需要权限 ${to.meta.permission}`)
        next('/403')
        return
      }
    } catch (error) {
      console.error('权限检查失败:', error)
      // 权限检查失败，跳转到登录页
      next('/login')
      return
    }
  }
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 英语学习平台`
  }
  
  next()
})

export default router