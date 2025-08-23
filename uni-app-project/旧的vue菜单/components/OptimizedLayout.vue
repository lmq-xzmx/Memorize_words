<template>
  <div class="optimized-layout" :class="layoutClasses">
    <!-- 顶部导航栏 -->
    <header class="layout-header" v-if="showTopNav">
      <top-nav-bar 
        :user="currentUser"
        :collapsed="sidebarCollapsed"
        @toggle-sidebar="handleSidebarToggle"
        @user-action="handleUserAction"
      />
    </header>

    <!-- 主要内容区域 -->
    <div class="layout-main">
      <!-- 侧边栏 -->
      <aside 
        class="layout-sidebar"
        :class="{ 'collapsed': sidebarCollapsed }"
        v-if="showSidebar"
      >
        <optimized-dynamic-menu
          :show-dev-tools="showDevTools"
          @menu-click="handleMenuClick"
          @menu-toggle="handleMenuToggle"
          @dev-tool-toggle="handleDevToolToggle"
          @logout="handleLogout"
        />
      </aside>

      <!-- 内容区域 -->
      <main class="layout-content" :class="contentClasses">
        <!-- 加载状态 -->
        <div v-if="isMenuLoading" class="loading-overlay">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>正在加载菜单...</p>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="menuError" class="error-overlay">
          <div class="error-content">
            <i class="error-icon">⚠</i>
            <h3>菜单加载失败</h3>
            <p>{{ menuError }}</p>
            <button class="retry-btn" @click="retryLoadMenu">
              重新加载
            </button>
          </div>
        </div>

        <!-- 未认证状态 -->
        <div v-else-if="!isUserAuthenticated" class="auth-overlay">
          <div class="auth-content">
            <i class="auth-icon">🔒</i>
            <h3>请先登录</h3>
            <p>您需要登录后才能访问此页面</p>
            <button class="login-btn" @click="navigateToLogin">
              前往登录
            </button>
          </div>
        </div>

        <!-- 权限不足状态 -->
        <div v-else-if="!hasPagePermission" class="permission-overlay">
          <div class="permission-content">
            <i class="permission-icon">🚫</i>
            <h3>权限不足</h3>
            <p>您没有权限访问此页面</p>
            <button class="back-btn" @click="navigateBack">
              返回上一页
            </button>
            <button class="dashboard-btn" @click="navigateToDashboard">
              返回首页
            </button>
          </div>
        </div>

        <!-- 正常内容 -->
        <div v-else class="page-content">
          <!-- 面包屑导航 -->
          <nav class="breadcrumb" v-if="showBreadcrumb && breadcrumbs.length > 0">
            <ol class="breadcrumb-list">
              <li 
                v-for="(crumb, index) in breadcrumbs"
                :key="crumb.path || index"
                class="breadcrumb-item"
                :class="{ 'active': index === breadcrumbs.length - 1 }"
              >
                <router-link 
                  v-if="crumb.path && index < breadcrumbs.length - 1"
                  :to="crumb.path"
                  class="breadcrumb-link"
                >
                  {{ crumb.title }}
                </router-link>
                <span v-else class="breadcrumb-text">
                  {{ crumb.title }}
                </span>
                <i 
                  v-if="index < breadcrumbs.length - 1"
                  class="breadcrumb-separator"
                >›</i>
              </li>
            </ol>
          </nav>

          <!-- 页面标题 -->
          <div class="page-header" v-if="showPageHeader">
            <h1 class="page-title">{{ pageTitle }}</h1>
            <p class="page-description" v-if="pageDescription">
              {{ pageDescription }}
            </p>
          </div>

          <!-- 路由视图 -->
          <div class="router-view-container">
            <router-view 
              v-slot="{ Component, route }"
              :key="route.fullPath"
            >
              <transition 
                :name="pageTransition"
                mode="out-in"
                @enter="onPageEnter"
                @leave="onPageLeave"
              >
                <component 
                  :is="Component"
                  :key="route.fullPath"
                  v-if="Component"
                />
              </transition>
            </router-view>
          </div>
        </div>
      </main>
    </div>

    <!-- 底部导航 -->
    <footer class="layout-footer" v-if="showBottomNav">
      <optimized-bottom-navigation
        :max-visible-items="4"
        :auto-hide="true"
        @nav-click="handleBottomNavClick"
        @theme-change="handleThemeChange"
        @language-change="handleLanguageChange"
        @font-size-change="handleFontSizeChange"
      />
    </footer>

    <!-- 全局通知 -->
    <div class="global-notifications" v-if="notifications.length > 0">
      <transition-group name="notification" tag="div">
        <div 
          v-for="notification in notifications"
          :key="notification.id"
          class="notification"
          :class="`notification-${notification.type}`"
          @click="dismissNotification(notification.id)"
        >
          <i class="notification-icon" :class="getNotificationIcon(notification.type)"></i>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-message">{{ notification.message }}</div>
          </div>
          <button class="notification-close" @click.stop="dismissNotification(notification.id)">
            ✕
          </button>
        </div>
      </transition-group>
    </div>

    <!-- 返回顶部按钮 -->
    <button 
      v-if="showBackToTop"
      class="back-to-top"
      @click="scrollToTop"
      title="返回顶部"
    >
      <i class="icon-arrow-up">↑</i>
    </button>
  </div>
</template>

<script>
import { optimizedPermissionMixin } from '../mixins/optimizedPermissionMixin.js'
import menuStateManager, { menuState } from '../services/MenuStateManager.js'
import permissionService from '../services/PermissionService.js'
import OptimizedDynamicMenu from './OptimizedDynamicMenu.vue'
import OptimizedBottomNavigation from './OptimizedBottomNavigation.vue'
import TopNavBar from './TopNavBar.vue'

export default {
  name: 'OptimizedLayout',
  
  components: {
    OptimizedDynamicMenu,
    OptimizedBottomNavigation,
    TopNavBar
  },
  
  mixins: [optimizedPermissionMixin],
  
  props: {
    // 是否显示开发工具
    showDevTools: {
      type: Boolean,
      default: () => import.meta.env.MODE === 'development'
    },
    
    // 页面过渡动画
    pageTransition: {
      type: String,
      default: 'fade'
    },
    
    // 是否显示面包屑
    showBreadcrumb: {
      type: Boolean,
      default: true
    },
    
    // 是否显示页面标题
    showPageHeader: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      notifications: [],
      showBackToTop: false,
      scrollY: 0,
      windowWidth: window.innerWidth
    }
  },
  
  computed: {
    // 布局样式类
    layoutClasses() {
      return {
        'sidebar-collapsed': this.sidebarCollapsed,
        'mobile': this.isMobile,
        'tablet': this.isTablet,
        'desktop': this.isDesktop,
        'has-sidebar': this.showSidebar,
        'has-bottom-nav': this.showBottomNav
      }
    },
    
    // 内容区域样式类
    contentClasses() {
      return {
        'with-sidebar': this.showSidebar && !this.isMobile,
        'sidebar-collapsed': this.sidebarCollapsed,
        'with-bottom-nav': this.showBottomNav
      }
    },
    
    // 侧边栏折叠状态
    sidebarCollapsed() {
      return menuState.sidebarCollapsed
    },
    
    // 设备类型判断
    isMobile() {
      return this.windowWidth <= 768
    },
    
    isTablet() {
      return this.windowWidth > 768 && this.windowWidth <= 1024
    },
    
    isDesktop() {
      return this.windowWidth > 1024
    },
    
    // 显示控制
    showTopNav() {
      return !this.isMobile && this.isUserAuthenticated
    },
    
    showSidebar() {
      return !this.isMobile && this.isUserAuthenticated
    },
    
    showBottomNav() {
      return this.isMobile && this.isUserAuthenticated
    },
    
    // 页面权限检查
    hasPagePermission() {
      const currentPath = this.$route?.path
      if (!currentPath || !this.userRole) return true
      
      return permissionService.canAccessPage(this.userRole, currentPath)
    },
    
    // 面包屑导航
    breadcrumbs() {
      const route = this.$route
      if (!route || !route.matched) return []
      
      return route.matched
        .filter(record => record.meta && record.meta.breadcrumb)
        .map(record => ({
          title: record.meta.breadcrumb,
          path: record.path
        }))
    },
    
    // 页面标题
    pageTitle() {
      return this.$route?.meta?.title || '页面'
    },
    
    // 页面描述
    pageDescription() {
      return this.$route?.meta?.description
    }
  },
  
  methods: {
    /**
     * 处理侧边栏切换
     */
    handleSidebarToggle() {
      menuStateManager.toggleSidebar()
    },
    
    /**
     * 处理菜单点击
     * @param {Object} menu - 菜单项
     */
    handleMenuClick(menu) {
      this.$emit('menu-click', menu)
    },
    
    /**
     * 处理菜单展开/折叠
     * @param {Object} menu - 菜单项
     */
    handleMenuToggle(menu) {
      this.$emit('menu-toggle', menu)
    },
    
    /**
     * 处理开发工具切换
     * @param {Object} tool - 工具项
     */
    handleDevToolToggle(tool) {
      this.$emit('dev-tool-toggle', tool)
    },
    
    /**
     * 处理底部导航点击
     * @param {Object} menu - 菜单项
     */
    handleBottomNavClick(menu) {
      this.$emit('bottom-nav-click', menu)
    },
    
    /**
     * 处理用户操作
     * @param {string} action - 操作类型
     * @param {*} data - 操作数据
     */
    handleUserAction(action, data) {
      switch (action) {
        case 'logout':
          this.handleLogout()
          break
        case 'profile':
          this.$navigateWithPermission('/profile')
          break
        case 'settings':
          this.$navigateWithPermission('/settings')
          break
        default:
          this.$emit('user-action', action, data)
      }
    },
    
    /**
     * 处理退出登录
     */
    async handleLogout() {
      try {
        // 确认对话框
        if (!confirm('确定要退出登录吗？')) {
          return
        }
        
        // 清除认证信息
        permissionService.clearAuth()
        
        // 重置菜单状态
        menuStateManager.reset()
        
        // 导航到登录页
        this.$router.push('/login')
        
        // 显示通知
        this.addNotification({
          type: 'success',
          title: '退出成功',
          message: '您已成功退出登录'
        })
        
        this.$emit('logout')
        
      } catch (error) {
        console.error('退出登录失败:', error)
        this.addNotification({
          type: 'error',
          title: '退出失败',
          message: '退出登录失败，请重试'
        })
      }
    },
    
    /**
     * 处理主题变更
     * @param {string} theme - 新主题
     */
    handleThemeChange(theme) {
      this.$emit('theme-change', theme)
      this.addNotification({
        type: 'info',
        title: '主题已切换',
        message: `已切换到${theme === 'dark' ? '暗色' : '亮色'}主题`
      })
    },
    
    /**
     * 处理语言变更
     * @param {string} language - 新语言
     */
    handleLanguageChange(language) {
      this.$emit('language-change', language)
      this.addNotification({
        type: 'info',
        title: '语言已切换',
        message: `已切换到${language === 'zh' ? '中文' : 'English'}`
      })
    },
    
    /**
     * 处理字体大小变更
     * @param {number} fontSize - 新字体大小
     */
    handleFontSizeChange(fontSize) {
      this.$emit('font-size-change', fontSize)
      this.addNotification({
        type: 'info',
        title: '字体大小已调整',
        message: `字体大小已调整为 ${fontSize}px`
      })
    },
    
    /**
     * 导航到登录页
     */
    navigateToLogin() {
      this.$router.push('/login')
    },
    
    /**
     * 返回上一页
     */
    navigateBack() {
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        this.navigateToDashboard()
      }
    },
    
    /**
     * 导航到仪表板
     */
    navigateToDashboard() {
      this.$router.push('/dashboard')
    },
    
    /**
     * 重试加载菜单
     */
    async retryLoadMenu() {
      await menuStateManager.loadMenus()
    },
    
    /**
     * 页面进入动画
     * @param {Element} el - 元素
     */
    onPageEnter(el) {
      // 页面进入时的处理
      this.scrollToTop()
    },
    
    /**
     * 页面离开动画
     * @param {Element} el - 元素
     */
    onPageLeave(el) {
      // 页面离开时的处理
    },
    
    /**
     * 滚动到顶部
     */
    scrollToTop() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    },
    
    /**
     * 处理滚动事件
     */
    handleScroll() {
      this.scrollY = window.scrollY
      this.showBackToTop = this.scrollY > 300
    },
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
      this.windowWidth = window.innerWidth
      
      // 移动端自动折叠侧边栏
      if (this.isMobile && !this.sidebarCollapsed) {
        menuStateManager.setSidebarCollapsed(true)
      }
    },
    
    /**
     * 添加通知
     * @param {Object} notification - 通知对象
     */
    addNotification(notification) {
      const id = Date.now() + Math.random()
      const notif = {
        id,
        type: 'info',
        title: '',
        message: '',
        duration: 3000,
        ...notification
      }
      
      this.notifications.push(notif)
      
      // 自动移除
      if (notif.duration > 0) {
        setTimeout(() => {
          this.dismissNotification(id)
        }, notif.duration)
      }
    },
    
    /**
     * 移除通知
     * @param {string|number} id - 通知ID
     */
    dismissNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },
    
    /**
     * 获取通知图标
     * @param {string} type - 通知类型
     * @returns {string} 图标类名
     */
    getNotificationIcon(type) {
      const icons = {
        success: 'icon-success',
        error: 'icon-error',
        warning: 'icon-warning',
        info: 'icon-info'
      }
      return icons[type] || icons.info
    }
  },
  
  watch: {
    // 监听路由变化
    '$route'(to, from) {
      // 更新页面标题
      if (to.meta?.title) {
        document.title = `${to.meta.title} - 自然英语学习平台`
      }
      
      // 检查页面权限
      if (!this.hasPagePermission) {
        this.addNotification({
          type: 'error',
          title: '权限不足',
          message: '您没有权限访问此页面'
        })
      }
    }
  },
  
  mounted() {
    // 添加事件监听
    window.addEventListener('scroll', this.handleScroll, { passive: true })
    window.addEventListener('resize', this.handleResize)
    
    // 初始化
    this.handleResize()
    
    // 设置初始页面标题
    if (this.$route?.meta?.title) {
      document.title = `${this.$route.meta.title} - 自然英语学习平台`
    }
  },
  
  beforeUnmount() {
    // 移除事件监听
    window.removeEventListener('scroll', this.handleScroll)
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.optimized-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f7fafc;
}

/* 布局头部 */
.layout-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 主要内容区域 */
.layout-main {
  display: flex;
  flex: 1;
  margin-top: 64px; /* 为固定头部留出空间 */
}

.optimized-layout.mobile .layout-main {
  margin-top: 0;
}

/* 侧边栏 */
.layout-sidebar {
  position: fixed;
  top: 64px;
  left: 0;
  bottom: 0;
  z-index: 900;
  transition: all 0.3s ease;
}

.optimized-layout.mobile .layout-sidebar {
  top: 0;
}

.layout-sidebar.collapsed {
  width: 64px;
}

/* 内容区域 */
.layout-content {
  flex: 1;
  min-height: calc(100vh - 64px);
  transition: all 0.3s ease;
  padding-left: 280px;
}

.layout-content.with-sidebar.sidebar-collapsed {
  padding-left: 64px;
}

.layout-content.with-bottom-nav {
  padding-left: 0;
  padding-bottom: 80px;
  min-height: calc(100vh - 80px);
}

.optimized-layout.mobile .layout-content {
  padding-left: 0;
}

/* 覆盖层样式 */
.loading-overlay,
.error-overlay,
.auth-overlay,
.permission-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px 20px;
}

.loading-content,
.error-content,
.auth-content,
.permission-content {
  text-align: center;
  max-width: 400px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3182ce;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.auth-icon,
.permission-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.retry-btn,
.login-btn,
.back-btn,
.dashboard-btn {
  padding: 10px 20px;
  margin: 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.retry-btn,
.login-btn,
.dashboard-btn {
  background: #3182ce;
  color: #ffffff;
}

.back-btn {
  background: #718096;
  color: #ffffff;
}

.retry-btn:hover,
.login-btn:hover,
.dashboard-btn:hover {
  background: #2c5aa0;
  transform: translateY(-1px);
}

.back-btn:hover {
  background: #4a5568;
  transform: translateY(-1px);
}

/* 页面内容 */
.page-content {
  padding: 24px;
}

/* 面包屑导航 */
.breadcrumb {
  margin-bottom: 16px;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 14px;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-link {
  color: #3182ce;
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: #2c5aa0;
}

.breadcrumb-text {
  color: #4a5568;
}

.breadcrumb-item.active .breadcrumb-text {
  color: #2d3748;
  font-weight: 500;
}

.breadcrumb-separator {
  margin: 0 8px;
  color: #a0aec0;
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: #718096;
  margin: 0;
}

/* 路由视图容器 */
.router-view-container {
  min-height: 200px;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}

/* 布局底部 */
.layout-footer {
  position: relative;
  z-index: 1000;
}

/* 全局通知 */
.global-notifications {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 2000;
  max-width: 400px;
}

.notification {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid #3182ce;
  cursor: pointer;
  transition: all 0.2s ease;
}

.notification:hover {
  transform: translateX(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.notification-success {
  border-left-color: #38a169;
}

.notification-error {
  border-left-color: #e53e3e;
}

.notification-warning {
  border-left-color: #d69e2e;
}

.notification-info {
  border-left-color: #3182ce;
}

.notification-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.4;
}

.notification-close {
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: #a0aec0;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.notification-close:hover {
  background: #edf2f7;
  color: #4a5568;
}

/* 通知动画 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-enter-to,
.notification-leave-from {
  opacity: 1;
  transform: translateX(0);
}

/* 返回顶部按钮 */
.back-to-top {
  position: fixed;
  bottom: 100px;
  right: 20px;
  width: 48px;
  height: 48px;
  background: #3182ce;
  color: #ffffff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(49, 130, 206, 0.3);
  transition: all 0.2s ease;
  z-index: 1500;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.back-to-top:hover {
  background: #2c5aa0;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(49, 130, 206, 0.4);
}

/* 图标 */
.icon-success::before { content: '✓'; color: #38a169; }
.icon-error::before { content: '✕'; color: #e53e3e; }
.icon-warning::before { content: '⚠'; color: #d69e2e; }
.icon-info::before { content: 'ℹ'; color: #3182ce; }
.icon-arrow-up::before { content: '↑'; }

/* 响应式设计 */
@media (max-width: 768px) {
  .page-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .global-notifications {
    top: 20px;
    right: 16px;
    left: 16px;
    max-width: none;
  }
  
  .back-to-top {
    bottom: 90px;
    right: 16px;
    width: 44px;
    height: 44px;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 12px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .breadcrumb-list {
    font-size: 12px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .optimized-layout {
    background: #1a202c;
  }
  
  .layout-header {
    background: #2d3748;
    border-bottom-color: #4a5568;
  }
  
  .page-title {
    color: #e2e8f0;
  }
  
  .page-description {
    color: #a0aec0;
  }
  
  .breadcrumb-text {
    color: #a0aec0;
  }
  
  .breadcrumb-item.active .breadcrumb-text {
    color: #e2e8f0;
  }
  
  .notification {
    background: #2d3748;
  }
  
  .notification-title {
    color: #e2e8f0;
  }
  
  .notification-message {
    color: #a0aec0;
  }
}
</style>