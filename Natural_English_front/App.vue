<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <TopNavBar @open-settings="handleOpenSettings" />
    
    <!-- 主内容区域 -->
    <div class="main-content" :class="{ 'has-top-nav': showTopNav, 'has-bottom-nav': showTabBar }">
      <router-view />
    </div>
    
    <!-- 底部菜单栏，只在特定页面显示 -->
    <TabBar 
      v-if="showTabBar" 
      :current="$route.path"
      @tab-change="handleTabChange"
    />
  </div>
</template>

<script>
import TabBar from './components/TabBar.vue'
import TopNavBar from './components/TopNavBar.vue'

export default {
  name: 'App',
  components: {
    TabBar,
    TopNavBar
  },
  computed: {
    showTabBar() {
      // 定义需要显示底部菜单栏的页面
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
    showTopNav() {
      // 与showTabBar保持一致
      return this.showTabBar
    }
  },
  methods: {
    handleTabChange(item) {
      console.log('切换到:', item.text, item.path)
    },
    handleOpenSettings() {
      // 处理设置按钮点击
      console.log('打开设置')
      // 可以在这里添加设置弹窗或跳转逻辑
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  position: relative;
  min-height: 100vh;
}

/* 有顶部导航时的内容区域 */
.main-content.has-top-nav {
  padding-top: 44px;
  min-height: calc(100vh - 44px);
}

/* 有底部导航时的内容区域 */
.main-content.has-bottom-nav {
  padding-bottom: 60px;
  min-height: calc(100vh - 60px);
}

/* 同时有顶部和底部导航时的内容区域 */
.main-content.has-top-nav.has-bottom-nav {
  padding-top: 44px;
  padding-bottom: 60px;
  min-height: calc(100vh - 104px);
}

/* 登录注册页面不需要间距 */
.login-container,
.register-container {
  padding: 0 !important;
}

/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background-color: #f5f5f5;
}
</style>