import { createRouter, createWebHistory } from 'vue-router'
import { 
  isAuthenticated, 
  canAccessPage, 
  checkRoutePermission,
  getDefaultPageForRole,
  getCurrentUser,
  getRolePermissions
} from '../utils/permission.js'
import { ROLES } from '../utils/roleDefinitions.js'
import { pageRequiresAuth } from '../utils/learningModePermissions.js'

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
import NotFound from '../components/NotFound.vue'
import ErrorHandler from '../components/ErrorHandler.vue'

// 导入子页面组件
import WordChallenge from '../pages/word-challenge/index.vue'
import WordReview from '../pages/word-review/index.vue'
import WordSelectionPractice from '../pages/word-selection-practice/index.vue'
import WordSelectionIndex from '../pages/word-selection/index.vue'
import AuthTest from '../pages/AuthTest.vue'
import LoginTest from '../pages/login-test.vue'
import CommunityIndex from '../pages/community/index.vue'
import FashionIndex from '../pages/fashion/index.vue'

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
    path: '/dev-index',
    name: 'DevIndex',
    component: DevIndex,
    meta: { title: '开发中心' }
  },
  {
    path: '/admin/dev-index',
    name: 'AdminDevIndex',
    component: DevIndex,
    meta: { title: '管理员开发中心', requiresAuth: true }
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
    path: '/learning-modes',
    name: 'LearningModes',
    component: LearningModeSelector,
    meta: { title: '学习模式' }
  },
  {
    path: '/fashion',
    name: 'Fashion',
    component: FashionIndex,
    meta: { title: '时尚' }
  },
  {
    path: '/community',
    name: 'Community',
    component: CommunityIndex,
    meta: { title: '社区' }
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
  {
    path: '/auth-test',
    name: 'AuthTest',
    component: AuthTest,
    meta: { title: '登录状态测试' }
  },
  {
    path: '/login-test',
    name: 'LoginTest',
    component: LoginTest,
    meta: { title: '登录功能测试' }
  },
  // 学习模式相关路由
  {
    path: '/word-learning/spelling',
    name: 'WordLearningSpelling',
    component: WordSpelling,
    meta: { title: '拼写练习' }
  },
  {
    path: '/word-learning/flashcard',
    name: 'WordLearningFlashcard',
    component: WordFlashcard,
    meta: { title: '闪卡学习' }
  },
  {
    path: '/word-challenge',
    name: 'WordChallenge',
    component: WordChallenge,
    meta: { title: '单词挑战' }
  },
  {
    path: '/word-review',
    name: 'WordReview',
    component: WordReview,
    meta: { title: '单词复习' }
  },
  {
    path: '/word-selection-practice',
    name: 'WordSelectionPractice',
    component: WordSelectionPractice,
    meta: { title: '竞技模式' }
  },
  {
    path: '/word-selection-practice2',
    name: 'WordSelectionPractice2',
    component: WordSelection,
    meta: { title: '师生互动' }
  },
  {
    path: '/competition',
    name: 'Competition',
    component: WordSelectionPractice,
    meta: { title: '竞技模式' }
  },
  {
    path: '/quick-brush',
    name: 'QuickBrush',
    component: WordSelectionPractice,
    meta: { title: '快刷模式' }
  },
  // 错误处理页面
  {
    path: '/error',
    name: 'Error',
    component: ErrorHandler,
    props: route => ({
      errorType: route.query.type || 'general',
      errorMessage: route.query.message || ''
    }),
    meta: { title: '错误页面' }
  },
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到' }
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

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta && to.meta.title) {
    document.title = `${to.meta.title} - Natural English`
  }
  
  try {
    // 使用统一的路由权限检查，传递完整的路由对象
    await checkRoutePermission(to, from, next)
  } catch (error) {
    console.error('路由权限检查失败:', error)
    // 发生错误时的安全处理
    const authenticated = await isAuthenticated()
    if (!authenticated) {
      next('/login')
    } else {
      next('/dashboard')
    }
  }
})

// 全局后置守卫 - 用于权限日志记录和分析
router.afterEach((to, from) => {
  // 记录页面访问日志（可选）
  if (import.meta.env.MODE === 'development') {
    console.log(`页面访问: ${from.path} -> ${to.path}`)
  }
  
  // 可以在这里添加页面访问统计或权限使用分析
})

export default router