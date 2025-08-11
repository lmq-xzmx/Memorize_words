import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import HomePage from '../pages/HomePage.vue'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Dashboard from '../pages/Dashboard.vue'
import Profile from '../pages/Profile.vue'
import Settings from '../pages/Settings.vue'
import Discover from '../pages/Discover.vue'
import DevIndex from '../pages/DevIndex.vue'
import WordLearning from '../pages/WordLearning.vue'
import WordDetail from '../pages/WordDetail.vue'
import WordFlashcard from '../pages/WordFlashcard.vue'
import WordSpelling from '../pages/WordSpelling.vue'
import WordReading from '../pages/WordReading.vue'
import WordSelection from '../pages/WordSelection.vue'
import StoryReading from '../pages/StoryReading.vue'
import Listening from '../pages/Listening.vue'
import PatternMemory from '../pages/PatternMemory.vue'
import ResourceAuth from '../pages/ResourceAuth.vue'
import ResourceSharing from '../pages/ResourceSharing.vue'
import SubscriptionManagement from '../pages/SubscriptionManagement.vue'
import TestAPI from '../pages/TestAPI.vue'
import LearningModeSelector from '../pages/LearningModeSelector.vue'
import WordRootAnalysis from '../pages/WordRootAnalysis.vue'
import WordExamples from '../pages/WordExamples.vue'
import PositionTestPage from '../pages/PositionTestPage.vue'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '仪表板', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: '个人资料', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { title: '设置', requiresAuth: true }
  },
  {
    path: '/discover',
    name: 'Discover',
    component: Discover,
    meta: { title: '发现' }
  },
  {
    path: '/dev',
    name: 'DevIndex',
    component: DevIndex,
    meta: { title: '开发索引' }
  },
  {
    path: '/word-learning',
    name: 'WordLearning',
    component: WordLearning,
    meta: { title: '单词学习' }
  },
  {
    path: '/word-detail/:id?',
    name: 'WordDetail',
    component: WordDetail,
    meta: { title: '单词详情' }
  },
  {
    path: '/word-flashcard',
    name: 'WordFlashcard',
    component: WordFlashcard,
    meta: { title: '闪卡学习' }
  },
  {
    path: '/word-spelling',
    name: 'WordSpelling',
    component: WordSpelling,
    meta: { title: '拼写练习' }
  },
  {
    path: '/word-reading',
    name: 'WordReading',
    component: WordReading,
    meta: { title: '单词阅读' }
  },
  {
    path: '/word-selection',
    name: 'WordSelection',
    component: WordSelection,
    meta: { title: '单词选择' }
  },
  {
    path: '/story-reading',
    name: 'StoryReading',
    component: StoryReading,
    meta: { title: '故事阅读' }
  },
  {
    path: '/listening',
    name: 'Listening',
    component: Listening,
    meta: { title: '听力练习' }
  },
  {
    path: '/pattern-memory',
    name: 'PatternMemory',
    component: PatternMemory,
    meta: { title: '模式记忆' }
  },
  {
    path: '/resource-auth',
    name: 'ResourceAuth',
    component: ResourceAuth,
    meta: { title: '资源授权' }
  },
  {
    path: '/resource-sharing',
    name: 'ResourceSharing',
    component: ResourceSharing,
    meta: { title: '资源共享' }
  },
  {
    path: '/subscription',
    name: 'SubscriptionManagement',
    component: SubscriptionManagement,
    meta: { title: '订阅管理' }
  },
  {
    path: '/test-api',
    name: 'TestAPI',
    component: TestAPI,
    meta: { title: 'API测试' }
  },
  {
    path: '/learning-mode',
    name: 'LearningModeSelector',
    component: LearningModeSelector,
    meta: { title: '学习模式选择' }
  },
  {
    path: '/word-root-analysis',
    name: 'WordRootAnalysis',
    component: WordRootAnalysis,
    meta: { title: '词根分析' }
  },
  {
    path: '/word-examples',
    name: 'WordExamples',
    component: WordExamples,
    meta: { title: '单词例句' }
  },
  {
    path: '/position-test',
    name: 'PositionTestPage',
    component: PositionTestPage,
    meta: { title: '位置测试' }
  },
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 导入权限检查工具
import { isAuthenticated, getCurrentUser, canAccessPage } from '../utils/permission.js'

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Natural English`
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!isAuthenticated()) {
      console.log('用户未认证，重定向到登录页')
      next('/login')
      return
    }
  }
  
  // 检查页面权限
  const user = getCurrentUser()
  if (user && !canAccessPage(user.role, to.path)) {
    console.warn(`用户 ${user.username}(${user.role}) 无权访问页面 ${to.path}`)
    // 重定向到仪表板或首页
    next('/dashboard')
    return
  }
  
  next()
})

export default router