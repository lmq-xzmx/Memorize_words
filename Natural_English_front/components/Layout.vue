<template>
  <div class="layout">
    <!-- 顶部菜单栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <h2>英语学习平台</h2>
        </div>
        <nav class="top-nav">
          <div class="nav-item" @click="toggleSidebar">
            <i class="menu-icon">☰</i>
          </div>
          <div class="nav-item user-menu">
            <span>{{ username }}</span>
            <div class="dropdown">
              <button @click="logout" class="logout-btn">退出登录</button>
            </div>
          </div>
        </nav>
      </div>
    </header>

    <div class="main-container">
      <!-- 侧边菜单 -->
      <aside class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <nav class="sidebar-nav">
          <div class="menu-section">
            <h3 class="menu-title">开发工具</h3>
            <ul class="menu-list">
              <li class="menu-item" :class="{ active: $route.path === '/dev-index' }">
                <router-link to="/dev-index" class="menu-link">
                  <i class="menu-icon">🔧</i>
                  <span class="menu-text">开发期页面</span>
                </router-link>
              </li>
            </ul>
          </div>

          <div class="menu-section">
            <h3 class="menu-title">学习模块</h3>
            <ul class="menu-list">
              <li class="menu-item" :class="{ active: $route.path === '/dashboard' }">
                <router-link to="/dashboard" class="menu-link">
                  <i class="menu-icon">📊</i>
                  <span class="menu-text">学习面板</span>
                </router-link>
              </li>
              <li class="menu-item" :class="{ active: $route.path === '/word-examples' }">
                <router-link to="/word-examples" class="menu-link">
                  <i class="menu-icon">📖</i>
                  <span class="menu-text">单词例句</span>
                </router-link>
              </li>
              <li class="menu-item" :class="{ active: $route.path === '/word-reading' }">
                <router-link to="/word-reading" class="menu-link">
                  <i class="menu-icon">📚</i>
                  <span class="menu-text">单词阅读</span>
                </router-link>
              </li>
            </ul>
          </div>

          <div class="menu-section">
            <h3 class="menu-title">练习模块</h3>
            <ul class="menu-list">
              <li class="menu-item" :class="{ active: $route.path.includes('/word-challenge') }">
                <router-link to="/word-challenge/" class="menu-link">
                  <i class="menu-icon">🎯</i>
                  <span class="menu-text">单词挑战</span>
                </router-link>
              </li>
              <li class="menu-item" :class="{ active: $route.path.includes('/word-review') }">
                <router-link to="/word-review" class="menu-link">
                  <i class="menu-icon">🔄</i>
                  <span class="menu-text">单词复习</span>
                </router-link>
              </li>
              <li class="menu-item" :class="{ active: $route.path.includes('/word-selection') }">
                <router-link to="/word-selection" class="menu-link">
                  <i class="menu-icon">✅</i>
                  <span class="menu-text">单词选择</span>
                </router-link>
              </li>
              <li class="menu-item" :class="{ active: $route.path === '/word-selection-practice' }">
                <router-link to="/word-selection-practice" class="menu-link">
                  <i class="menu-icon">📝</i>
                  <span class="menu-text">选择练习</span>
                </router-link>
              </li>
            </ul>
          </div>
        </nav>
      </aside>

      <!-- 主内容区域 -->
      <main class="content" :class="{ 'content-expanded': sidebarCollapsed }">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Layout',
  data() {
    return {
      sidebarCollapsed: false,
      username: ''
    }
  },
  mounted() {
    // 获取用户名
    this.username = localStorage.getItem('username') || '用户'
  },
  methods: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部菜单栏 */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 60px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 100%;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-item {
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-menu {
  position: relative;
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px;
  min-width: 120px;
  display: none;
}

.user-menu:hover .dropdown {
  display: block;
}

.logout-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background: #ff3742;
}

/* 主容器 */
.main-container {
  display: flex;
  margin-top: 60px;
  min-height: calc(100vh - 60px);
}

/* 侧边菜单 */
.sidebar {
  width: 260px;
  background: #2c3e50;
  color: white;
  transition: width 0.3s ease;
  overflow-y: auto;
}

.sidebar-collapsed {
  width: 60px;
}

.sidebar-nav {
  padding: 20px 0;
}

.menu-section {
  margin-bottom: 30px;
}

.menu-title {
  color: #bdc3c7;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 15px 20px;
  transition: opacity 0.3s;
}

.sidebar-collapsed .menu-title {
  opacity: 0;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  margin-bottom: 2px;
}

.menu-link {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #ecf0f1;
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.menu-link:hover {
  background-color: #34495e;
  border-left-color: #3498db;
}

.menu-item.active .menu-link {
  background-color: #3498db;
  border-left-color: #2980b9;
  color: white;
}

.menu-icon {
  font-size: 18px;
  margin-right: 12px;
  min-width: 20px;
  text-align: center;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.3s;
}

.sidebar-collapsed .menu-text {
  opacity: 0;
}

/* 主内容区域 */
.content {
  flex: 1;
  padding: 30px;
  background-color: #f8f9fa;
  transition: margin-left 0.3s ease;
}

.content-expanded {
  margin-left: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -260px;
    top: 60px;
    height: calc(100vh - 60px);
    z-index: 999;
  }
  
  .sidebar.show {
    left: 0;
  }
  
  .content {
    margin-left: 0;
  }
  
  .header-content {
    padding: 0 15px;
  }
  
  .logo h2 {
    font-size: 18px;
  }
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: #34495e;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #7f8c8d;
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #95a5a6;
}
</style>