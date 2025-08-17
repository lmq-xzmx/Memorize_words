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
      :current-path="$route.path"
    />
    
    <!-- WebSocket调试面板 -->
    <WebSocketDebugPanel />
  </div>
</template>

<style scoped>
/* 移除有害的position-reset.css引用 */

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f5f5f5;
}

.main-content {
  flex: 1;
  transition: all 0.3s ease;
  position: relative;
}

.main-content.has-top-nav {
  padding-top: 70px;
}

.main-content.has-bottom-nav {
  padding-bottom: 80px;
}

/* 登录和注册页面特殊样式 */
.auth-page .main-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

/* 确保正常的布局流 */
.main-content > * {
  position: relative;
}
</style>

<style>
/* 全局样式重置 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f5f5f5;
  line-height: 1.6;
}

html {
  height: 100%;
}

/* 确保路由视图正常显示 */
.router-view {
  width: 100%;
  min-height: 100%;
}
</style>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from './components/navigation/TabBar.vue'
import TopNavBar from './components/TopNavBar.vue'
import elementPositionReset from './mixins/elementPositionReset'
import './assets/css/style-fixes.css'
import styleConflictResolver from './utils/styleConflictResolver'
import { websocketDiagnostics } from './utils/websocketDiagnostics'
import WebSocketDebugPanel from './components/WebSocketDebugPanel.vue'

const route = useRoute()

// 使用mixin的功能
elementPositionReset.mounted?.()

onMounted(() => {
  // 启动样式冲突解决器
  styleConflictResolver.startAutoFix()
  console.log('样式冲突解决器已启动')
  
  // 启动WebSocket诊断工具
  websocketDiagnostics.init()
  ;(window as any).websocketDiagnostics = websocketDiagnostics
  console.log('WebSocket诊断工具已启动')
})

const showTabBar = computed((): boolean => {
  // 定义不需要显示底部菜单栏的页面（登录页和注册页）
  const excludePages = ['/login', '/register']
  
  // 如果当前页面是排除页面，则不显示底部导航
  return !excludePages.some(page => route.path.startsWith(page))
})

const showTopNav = computed((): boolean => {
  // 与showTabBar保持一致
  return showTabBar.value
})

const handleOpenSettings = (): void => {
  // 处理设置按钮点击
  console.log('打开设置')
  // 可以在这里添加设置弹窗或跳转逻辑
}
</script>