<template>
  <div class="top-nav-bar" v-if="showTopNav">
    <!-- 左侧返回按钮 -->
    <div class="nav-left">
      <div 
        v-if="canGoBack" 
        class="nav-btn back-btn" 
        @click="goBack"
      >
        <span class="icon">←</span>
        <span class="text">返回</span>
      </div>
    </div>

    <!-- 中间标题 -->
    <div class="nav-center">
      <h1 class="nav-title">{{ pageTitle }}</h1>
    </div>

    <!-- 右侧操作按钮 -->
    <div class="nav-right">
      <!-- 插槽：右侧菜单 -->
      <slot name="right-menu"></slot>
      
      <!-- 首页按钮 -->
      <div 
        class="nav-btn home-btn" 
        @click="goHome"
        v-if="!isHomePage"
      >
        <span class="icon">🏠</span>
      </div>
      
      <!-- 设置按钮 -->
      <div 
        class="nav-btn settings-btn" 
        @click="openSettings"
      >
        <span class="icon">⚙️</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.top-nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 900;
  height: 60px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  transition: all 0.3s ease;
}

.nav-left,
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 100px;
}

.nav-left {
  justify-content: flex-start;
}

.nav-right {
  justify-content: flex-end;
}

.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  text-align: center;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  border: none;
}

.nav-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
}

.nav-btn .icon {
  font-size: 16px;
}

.nav-btn .text {
  font-size: 14px;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-brand:hover {
  color: #5a67d8;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 20px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  position: relative;
}

.nav-link {
  color: #4b5563;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-link:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.nav-link.active {
  color: #667eea;
  background: rgba(102, 126, 234, 0.15);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-button {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.nav-button.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.nav-button.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.nav-button.secondary {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.nav-button.secondary:hover {
  background: rgba(102, 126, 234, 0.2);
}

.user-menu {
  position: relative;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.mobile-menu-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #4b5563;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.mobile-menu-toggle:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .top-nav {
    padding: 0 16px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .nav-actions {
    gap: 8px;
  }
  
  .nav-button {
    padding: 6px 12px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .nav-brand {
    font-size: 1.25rem;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
  }
}

/* 下拉菜单样式 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  min-width: 180px;
  z-index: 950;
}

.dropdown-item {
  display: block;
  padding: 8px 16px;
  color: #4b5563;
  text-decoration: none;
  transition: all 0.3s ease;
}

.dropdown-item:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.dropdown-divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
  margin: 4px 0;
}
</style>

<script>
export default {
  name: 'TopNavBar',
  data() {
    return {
      // 页面标题映射
      pageTitles: {
        '/dashboard': '英语学习平台',
        '/word-reading': '单词阅读',
        '/word-learning': '单词学习',
        '/word-learning/spelling': '拼写练习',
        '/word-learning/flashcard': '闪卡学习',
        '/word-detail': '单词详情',
        '/word-root-analysis': '词根分解',
        '/pattern-memory': '模式匹配记忆',
        '/story-reading': '故事阅读',
        '/word-challenge': '单词挑战',
        '/word-review': '单词复习',
        '/word-selection': '单词选择',
        '/word-selection-practice': '斩词练习',
        '/profile': '个人中心',
        '/community': '社区互动',
        '/fashion': '时尚趋势',
        '/dev-index': '发现'
      }
    }
  },
  computed: {
    // 是否显示顶部导航
    showTopNav() {
      // 在有TabBar的页面显示顶部导航
      const tabBarPages = [
        '/',
        '/dashboard',
        '/learning-modes',
        '/learning-mode',
        '/word-reading', 
        '/word-challenge',
        '/word-selection',
        '/word-selection-practice',
        '/word-examples',
        '/word-learning/spelling',
        '/word-learning/flashcard',
        '/word-learning',
        '/word-detail',
        '/word-root-analysis',
        '/pattern-memory',
        '/story-reading',
        '/word-review',
        '/profile',
        '/community',
        '/fashion',
        '/dev-index'
      ]
      return tabBarPages.some(page => this.$route.path.startsWith(page))
    },
    // 页面标题
    pageTitle() {
      const currentPath = this.$route.path
      return this.pageTitles[currentPath] || '英语学习平台'
    },
    // 是否可以返回
    canGoBack() {
      return this.$router && window.history.length > 1 && this.$route.path !== '/dashboard'
    },
    // 是否是首页
    isHomePage() {
      return this.$route.path === '/dashboard'
    }
  },
  methods: {
    // 返回上一页
    goBack() {
      if (this.canGoBack) {
        this.$router.go(-1)
      }
    },
    // 回到首页
    goHome() {
      this.$router.push('/dashboard')
    },
    // 打开设置
    openSettings() {
      // 可以打开设置弹窗或跳转到设置页面
      this.$emit('open-settings')
    }
  }
}
</script>

