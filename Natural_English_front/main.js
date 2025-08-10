import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Layout from './components/Layout.vue'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'
import Dashboard from './pages/Dashboard.vue'
import WordExamples from './pages/WordExamples.vue'
import WordChallenge from './pages/word-challenge/index.vue'
import WordReview from './pages/word-review/index.vue'
import WordSelection from './pages/word-selection/index.vue'
import WordSelectionPractice from './pages/word-selection-practice/index.vue'
import WordSelectionPractice2 from './pages/WordSelection.vue'
import WordReading from './pages/WordReading.vue'
import WordLearning from './pages/WordLearning.vue'
import WordSpelling from './pages/WordSpelling.vue'
import WordFlashcard from './pages/WordFlashcard.vue'
import WordDetail from './pages/WordDetail.vue'
import WordRootAnalysis from './pages/WordRootAnalysis.vue'
import PatternMemory from './pages/PatternMemory.vue'
import StoryReading from './pages/StoryReading.vue'
import DevIndex from './pages/DevIndex.vue'
import Profile from './pages/Profile.vue'
import Listening from './pages/Listening.vue'
import Community from './pages/community/index.vue'
import Fashion from './pages/fashion/index.vue'
import ResourceAuth from './pages/ResourceAuth.vue'
import SubscriptionManagement from './pages/SubscriptionManagement.vue'
import ResourceSharing from './pages/ResourceSharing.vue'

// 路由配置
const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  
  // 带Layout的管理页面（侧边栏导航）
  {
    path: '/admin',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: 'dev-index', component: DevIndex }
    ]
  },
  
  // 底部菜单栏页面（直接路由，不使用Layout）
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/help', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/word-reading', component: WordReading, meta: { requiresAuth: true } },
  { path: '/word-learning', component: WordLearning, meta: { requiresAuth: true } },
  { path: '/word-learning/spelling', component: WordSpelling, meta: { requiresAuth: true } },
  { path: '/word-learning/flashcard', component: WordFlashcard, meta: { requiresAuth: true } },
  { path: '/word-detail/:id?', component: WordDetail, meta: { requiresAuth: true } },
  { path: '/word-root-analysis', component: WordRootAnalysis, meta: { requiresAuth: true } },
  { path: '/pattern-memory', component: PatternMemory, meta: { requiresAuth: true } },
  { path: '/story-reading', component: StoryReading, meta: { requiresAuth: true } },
  { path: '/word-challenge', component: WordChallenge, meta: { requiresAuth: true } },
  { path: '/word-selection', component: WordSelection, meta: { requiresAuth: true } },
  { path: '/word-examples', component: WordExamples, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/listening', component: Listening, meta: { requiresAuth: true } },
  
  // 其他功能页面
  { path: '/word-review', component: WordReview, meta: { requiresAuth: true } },
  { path: '/word-selection-practice', component: WordSelectionPractice, meta: { requiresAuth: true } },
  { path: '/word-selection-practice2', component: WordSelectionPractice2, meta: { requiresAuth: true } },
  { path: '/dev-index', component: DevIndex, meta: { requiresAuth: true } },
  { path: '/community', component: Community, meta: { requiresAuth: true } },
  { path: '/fashion', component: Fashion, meta: { requiresAuth: true } },
  { path: '/resource-auth', component: ResourceAuth, meta: { requiresAuth: true } },
  { path: '/subscription-management', component: SubscriptionManagement, meta: { requiresAuth: true } },
  { path: '/resource-sharing', component: ResourceSharing, meta: { requiresAuth: true } },
  { path: '/discover', component: () => import('./pages/Discover.vue'), meta: { requiresAuth: true } },
  { path: '/settings', component: () => import('./pages/Settings.vue'), meta: { requiresAuth: true } },
  { path: '/test-api', component: () => import('./pages/TestAPI.vue') },
  
  // 兼容旧路由
  { path: '/words/word-challenge/', redirect: '/word-challenge' },
  { path: '/words/word-challenge', redirect: '/word-challenge' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')