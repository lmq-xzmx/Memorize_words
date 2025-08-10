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
        '/discover': '发现'
      }
    }
  },
  computed: {
    // 是否显示顶部导航
    showTopNav() {
      // 在有TabBar的页面显示顶部导航
      const tabBarPages = [
        '/dashboard',
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
        '/discover'
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

<style scoped>
.top-nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 44px;
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.nav-left,
.nav-right {
  display: flex;
  align-items: center;
  min-width: 60px;
}

.nav-left {
  justify-content: flex-start;
}

.nav-right {
  justify-content: flex-end;
  gap: 8px;
}

.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  text-align: center;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  user-select: none;
}

.nav-btn:hover {
  background-color: #f5f5f5;
}

.nav-btn:active {
  background-color: #e5e5e5;
}

.nav-btn .icon {
  font-size: 16px;
  line-height: 1;
}

.nav-btn .text {
  font-size: 14px;
  color: #333;
}

.back-btn .icon {
  font-size: 18px;
  font-weight: bold;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .top-nav-bar {
    background: #1a1a1a;
    border-bottom-color: #333;
  }
  
  .nav-title {
    color: #fff;
  }
  
  .nav-btn .text {
    color: #fff;
  }
  
  .nav-btn:hover {
    background-color: #333;
  }
  
  .nav-btn:active {
    background-color: #444;
  }
}

/* 小程序适配 */
/* #ifdef MP */
.top-nav-bar {
  padding-top: var(--status-bar-height, 0);
  height: calc(44px + var(--status-bar-height, 0));
}
/* #endif */

/* iOS安全区域适配 */
/* #ifdef APP-PLUS */
.top-nav-bar {
  padding-top: var(--status-bar-height, 0);
  height: calc(44px + var(--status-bar-height, 0));
}
/* #endif */
</style>