<template>
  <div class="bottom-nav-container" v-if="shouldShowBottomNav">
    <!-- 底部导航栏 -->
    <nav class="bottom-navigation" :class="{ 'bottom-nav--hidden': !visible }">
      <!-- 主要导航项 -->
      <div class="nav-items">
        <div 
          v-for="item in visibleBottomMenus" 
          :key="item.id"
          class="nav-item"
          :class="{ 'nav-item--active': item.id === activeBottomMenu }"
          @click="handleNavClick(item)"
        >
          <div class="nav-icon">
            <i :class="item.icon"></i>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </div>
          <span class="nav-label">{{ item.name }}</span>
        </div>
        
        <!-- 更多菜单按钮 -->
        <div 
          v-if="hasMoreMenus"
          class="nav-item nav-item--more"
          :class="{ 'nav-item--active': showMoreMenu }"
          @click="toggleMoreMenu"
        >
          <div class="nav-icon">
            <i class="fas fa-ellipsis-h"></i>
          </div>
          <span class="nav-label">更多</span>
        </div>
      </div>
    </nav>
    
    <!-- 更多菜单弹出层 -->
    <transition name="popup-slide">
      <div v-if="showMoreMenu" class="more-menu-popup">
        <!-- 遮罩层 -->
        <div class="overlay" @click="closeMoreMenu"></div>
        
        <!-- 弹出层内容 -->
        <div class="popup-content">
          <!-- 弹出层头部 -->
          <div class="popup-header">
            <h3>更多功能</h3>
            <button class="close-btn" @click="closeMoreMenu">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <!-- 工具菜单 -->
          <div class="menu-section">
            <h4>工具菜单</h4>
            <div class="menu-grid">
              <div 
                v-for="tool in accessibleToolMenus" 
                :key="tool.id"
                class="menu-grid-item"
                @click="handleToolClick(tool)"
              >
                <div class="tool-icon">
                  <i :class="tool.icon"></i>
                </div>
                <span class="tool-name">{{ tool.name }}</span>
              </div>
            </div>
          </div>
          
          <!-- 时尚菜单 -->
          <div class="menu-section">
            <h4>时尚菜单</h4>
            <div class="menu-grid">
              <div 
                v-for="fashion in fashionMenus" 
                :key="fashion.id"
                class="menu-grid-item"
                @click="handleFashionClick(fashion)"
              >
                <div class="fashion-icon">
                  <i :class="fashion.icon"></i>
                </div>
                <span class="fashion-name">{{ fashion.name }}</span>
              </div>
            </div>
          </div>
          
          <!-- 快速操作 -->
          <div class="quick-actions">
            <button class="quick-action-btn" @click="navigateToProfile">
              <i class="fas fa-user"></i>
              <span>个人资料</span>
            </button>
            <button class="quick-action-btn" @click="toggleTheme">
              <i class="fas fa-moon"></i>
              <span>切换主题</span>
            </button>
            <button class="quick-action-btn" @click="switchLanguage">
              <i class="fas fa-globe"></i>
              <span>语言设置</span>
            </button>
            <button class="quick-action-btn" @click="adjustFontSize">
              <i class="fas fa-text-height"></i>
              <span>字体大小</span>
            </button>
            <button class="quick-action-btn" @click="loadNotificationCount">
              <i class="fas fa-bell"></i>
              <span>通知中心</span>
              <span v-if="notificationCount > 0" class="action-badge">{{ notificationCount }}</span>
            </button>
            <button class="quick-action-btn" @click="$navigateWithPermission('/help')">
              <i class="fas fa-question-circle"></i>
              <span>帮助中心</span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import optimizedPermissionMixin from '../../mixins/optimizedPermissionMixin'
import menuStateManager, { menuState } from '../../services/MenuStateManager'

export default {
  name: 'TabBar',
  
  mixins: [optimizedPermissionMixin],
  
  props: {
    // 最大显示菜单数量
    maxVisibleItems: {
      type: Number,
      default: 4
    },
    
    // 是否自动隐藏
    autoHide: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      showMoreMenu: false,
      notificationCount: 0,
      lastScrollY: 0,
      isScrollingDown: false
    }
  },
  
  computed: {
    // 是否显示底部导航
    shouldShowBottomNav() {
      // 移动端或小屏幕设备显示底部导航
      return window.innerWidth <= 768 && this.isUserAuthenticated
    },
    
    // 底部导航可见性
    visible() {
      return menuState.bottomMenuVisible && !this.isScrollingDown
    },
    
    // 活动底部菜单
    activeBottomMenu() {
      return menuState.activeBottomMenu
    },
    
    // 可访问的底部菜单
    accessibleBottomMenus() {
      return menuState.bottomMenus.filter(menu => {
        return !menu.permission || this.$hasPermission(menu.permission)
      })
    },
    
    // 可访问的工具菜单
    accessibleToolMenus() {
      return menuState.toolMenus.filter(tool => {
        return !tool.permission || this.$hasPermission(tool.permission)
      })
    },
    
    // 时尚菜单
    fashionMenus() {
      return menuState.fashionMenus
    },
    
    // 是否有更多菜单
    hasMoreMenus() {
      const totalItems = this.accessibleBottomMenus.length
      return totalItems > this.maxVisibleItems || 
             this.accessibleToolMenus.length > 0 || 
             this.fashionMenus.length > 0
    },
    
    // 显示的底部菜单（限制数量）
    visibleBottomMenus() {
      if (!this.hasMoreMenus) {
        return this.accessibleBottomMenus
      }
      return this.accessibleBottomMenus.slice(0, this.maxVisibleItems - 1)
    }
  },
  
  methods: {
    /**
     * 处理导航点击
     * @param {Object} menu - 菜单项
     */
    async handleNavClick(menu) {
      if (menu.disabled) {
        return
      }
      
      try {
        // 设置活动菜单
        menuStateManager.setActiveBottomMenu(menu.id)
        
        // 关闭更多菜单
        this.closeMoreMenu()
        
        // 带权限检查的导航
        await this.$navigateWithPermission(menu.path)
        
        // 触发导航事件
        this.$emit('nav-click', menu)
        
      } catch (error) {
        console.error('底部导航失败:', error)
        // 恢复之前的状态
        this.restoreActiveBottomMenu()
      }
    },
    
    /**
     * 处理工具点击
     * @param {Object} tool - 工具项
     */
    async handleToolClick(tool) {
      this.closeMoreMenu()
      await this.handleNavClick(tool)
    },
    
    /**
     * 处理时尚菜单点击
     * @param {Object} fashion - 时尚菜单项
     */
    async handleFashionClick(fashion) {
      this.closeMoreMenu()
      
      // 时尚菜单可能有特殊处理逻辑
      if (fashion.action) {
        this.executeFashionAction(fashion)
      } else {
        await this.handleNavClick(fashion)
      }
    },
    
    /**
     * 执行时尚菜单动作
     * @param {Object} fashion - 时尚菜单项
     */
    executeFashionAction(fashion) {
      switch (fashion.action) {
        case 'theme-toggle':
          this.toggleTheme()
          break
        case 'language-switch':
          this.switchLanguage()
          break
        case 'font-size':
          this.adjustFontSize()
          break
        default:
          console.warn('未知的时尚菜单动作:', fashion.action)
      }
    },
    
    /**
     * 切换更多菜单
     */
    toggleMoreMenu() {
      this.showMoreMenu = !this.showMoreMenu
    },
    
    /**
     * 关闭更多菜单
     */
    closeMoreMenu() {
      this.showMoreMenu = false
    },
    
    /**
     * 导航到个人资料
     */
    async navigateToProfile() {
      this.closeMoreMenu()
      await this.$navigateWithPermission('/profile')
    },
    
    /**
     * 导航到通知中心
     */
    async navigateToNotifications() {
      this.closeMoreMenu()
      await this.$navigateWithPermission('/notifications')
    },
    
    /**
     * 导航到帮助中心
     */
    async navigateToHelp() {
      this.closeMoreMenu()
      await this.$navigateWithPermission('/help')
    },
    
    /**
     * 切换主题
     */
    toggleTheme() {
      // 实现主题切换逻辑
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light'
      const newTheme = currentTheme === 'light' ? 'dark' : 'light'
      document.documentElement.setAttribute('data-theme', newTheme)
      localStorage.setItem('theme', newTheme)
      
      this.$emit('theme-change', newTheme)
    },
    
    /**
     * 切换语言
     */
    switchLanguage() {
      // 实现语言切换逻辑
      const currentLang = this.$i18n?.locale || 'zh'
      const newLang = currentLang === 'zh' ? 'en' : 'zh'
      
      if (this.$i18n) {
        this.$i18n.locale = newLang
      }
      
      localStorage.setItem('language', newLang)
      this.$emit('language-change', newLang)
    },
    
    /**
     * 调整字体大小
     */
    adjustFontSize() {
      // 实现字体大小调整逻辑
      const currentSize = parseInt(document.documentElement.style.fontSize) || 16
      const sizes = [14, 16, 18, 20]
      const currentIndex = sizes.indexOf(currentSize)
      const nextIndex = (currentIndex + 1) % sizes.length
      const newSize = sizes[nextIndex]
      
      document.documentElement.style.fontSize = `${newSize}px`
      localStorage.setItem('fontSize', newSize)
      
      this.$emit('font-size-change', newSize)
    },
    
    /**
     * 恢复活动底部菜单状态
     */
    restoreActiveBottomMenu() {
      const currentPath = this.$route?.path
      if (currentPath) {
        const activeMenu = this.accessibleBottomMenus.find(menu => 
          currentPath === menu.path || currentPath.startsWith(menu.path + '/')
        )
        if (activeMenu) {
          menuStateManager.setActiveBottomMenu(activeMenu.id)
        }
      }
    },
    
    /**
     * 处理滚动事件
     */
    handleScroll() {
      if (!this.autoHide) return
      
      const currentScrollY = window.scrollY
      this.isScrollingDown = currentScrollY > this.lastScrollY && currentScrollY > 100
      this.lastScrollY = currentScrollY
    },
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
      // 强制重新计算是否显示底部导航
      this.$forceUpdate()
    },
    
    /**
     * 加载通知数量
     */
    async loadNotificationCount() {
      try {
        // 这里应该调用API获取通知数量
        // const response = await api.getNotificationCount()
        // this.notificationCount = response.count
        
        // 模拟数据
        this.notificationCount = Math.floor(Math.random() * 10)
      } catch (error) {
        console.error('加载通知数量失败:', error)
      }
    }
  },
  
  watch: {
    // 监听路由变化
    '$route'(to) {
      this.restoreActiveBottomMenu()
      this.closeMoreMenu()
    },
    
    // 监听用户认证状态
    isUserAuthenticated(newVal) {
      if (newVal) {
        this.loadNotificationCount()
      }
    }
  },
  
  mounted() {
    // 添加滚动监听
    if (this.autoHide) {
      window.addEventListener('scroll', this.handleScroll, { passive: true })
    }
    
    // 添加窗口大小变化监听
    window.addEventListener('resize', this.handleResize)
    
    // 初始化活动菜单
    this.restoreActiveBottomMenu()
    
    // 加载通知数量
    if (this.isUserAuthenticated) {
      this.loadNotificationCount()
    }
  },
  
  beforeUnmount() {
    // 移除事件监听
    if (this.autoHide) {
      window.removeEventListener('scroll', this.handleScroll)
    }
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style lang="scss" scoped>
@use '../../styles/index.scss';
@use '../../styles/variables.scss' as *;
@use '../../styles/mixins.scss' as *;

.bottom-nav-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: var(--z-index-navigation);
}

.bottom-navigation {
  @include flex-center;
  @include transition(transform);
  
  background: linear-gradient(180deg, var(--color-white) 0%, var(--color-gray-50) 100%);
  border-top: 1px solid var(--color-gray-200);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-2) var(--spacing-4);
  min-height: 64px;
  
}

.bottom-navigation--hidden {
  transform: translateY(100%);
}

@include respond-to(mobile) {
  .bottom-navigation {
    padding: var(--spacing-2);
  }
}

// 导航项容器
.nav-items {
  @include flex-center;
  justify-content: space-around;
  width: 100%;
  gap: var(--spacing-2);
}

// 导航项
.nav-item {
  @include flex-center;
  @include transition();
  
  flex-direction: column;
  padding: var(--spacing-2) var(--spacing-3);
  cursor: pointer;
  border-radius: var(--border-radius-lg);
  min-width: 60px;
  position: relative;
  
  &:hover {
    background: rgba(var(--color-primary-500), 0.1);
    transform: translateY(calc(-1 * var(--spacing-1)));
  }
}

.nav-item--active {
  background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-purple-600) 100%);
  color: var(--color-white);
  box-shadow: var(--shadow-md);
  
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    
    &:hover {
      background: transparent;
      transform: none;
    }
  }
}

.nav-item--active--more {
  // 更多按钮特殊样式
}

@include respond-to(mobile) {
  .nav-item {
    min-width: 50px;
    padding: var(--spacing-1) var(--spacing-2);
  }
}

// 导航图标
.nav-icon {
  @include flex-center;
  position: relative;
  width: 24px;
  height: 24px;
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-1);
  color: var(--color-gray-600);
  
  .nav-item--active & {
    color: var(--color-white);
  }
}

// 导航标签
.nav-label {
  @include text-style(xs, medium);
  color: var(--color-gray-600);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 60px;
  
  .nav-item--active & {
    color: var(--color-white);
  }
}

@include respond-to(mobile) {
  .nav-label {
    font-size: var(--font-size-2xs);
    max-width: 50px;
  }
}

// 徽章
.nav-badge {
  @include absolute-center;
  @include flex-center;
  
  top: calc(-1 * var(--spacing-1));
  right: calc(-1 * var(--spacing-1));
  min-width: 16px;
  height: 16px;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-white);
  background: var(--color-red-500);
  padding: 0 var(--spacing-1);
}

// 更多菜单弹出层
.more-menu-popup {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: var(--z-index-modal);
}

.overlay {
  @include absolute-full;
  background: rgba(var(--color-black), 0.3);
  z-index: -1;
}

.popup-content {
  @include card;
  
  position: absolute;
  bottom: 80px;
  right: var(--spacing-4);
  width: 320px;
  max-height: 400px;
  background: var(--color-white);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-2xl);
  border: 1px solid var(--color-gray-200);
  overflow: hidden;
}

@include respond-to(mobile) {
  .popup-content {
    width: calc(100vw - 2 * var(--spacing-4));
    right: var(--spacing-4);
  }
}

.popup-header {
  @include flex-between;
  padding: var(--spacing-4) var(--spacing-5);
  border-bottom: 1px solid var(--color-gray-200);
  background: var(--color-gray-50);
  
  h3 {
    @include text-style(md, semibold);
    color: var(--color-gray-900);
    margin: 0;
  }
}

.close-btn {
  @include flex-center;
  @include transition();
  
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--color-gray-500);
  cursor: pointer;
  border-radius: var(--border-radius-md);
  
  &:hover {
    background: var(--color-gray-200);
    color: var(--color-gray-900);
  }
}

.popup-content {
  max-height: 320px;
  overflow-y: auto;
  padding: var(--spacing-4) var(--spacing-5);
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--color-gray-100);
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--color-gray-300);
    border-radius: var(--border-radius-sm);
    
    &:hover {
      background: var(--color-gray-400);
    }
  }
}

// 菜单分组
.menu-section {
  margin-bottom: var(--spacing-5);
  
  &:last-child {
    margin-bottom: 0;
  }
  
  h4 {
    @include text-style(sm, semibold);
    color: var(--color-gray-600);
    margin: 0 0 var(--spacing-3) 0;
  }
}

// 菜单网格
.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: var(--spacing-3);
}

@include respond-to(mobile) {
  .menu-grid {
    grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
    gap: var(--spacing-2);
  }
}

.menu-grid-item {
  @include flex-center;
  @include transition();
  
  flex-direction: column;
  padding: var(--spacing-3) var(--spacing-2);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  background: var(--color-gray-50);
  
  &:hover {
    background: var(--color-gray-100);
    transform: translateY(calc(-1 * var(--spacing-1)));
  }
  
  &.fashion-item {
    background: linear-gradient(135deg, var(--color-yellow-200) 0%, var(--color-orange-300) 100%);
    color: var(--color-gray-900);
    
    &:hover {
      background: linear-gradient(135deg, var(--color-yellow-300) 0%, var(--color-orange-400) 100%);
    }
  }
}

.tool-icon,
.fashion-icon {
  @include flex-center;
  width: 32px;
  height: 32px;
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-1);
  color: var(--color-gray-600);
  
  .fashion-item & {
    color: var(--color-gray-900);
  }
}

.tool-name,
.fashion-name {
  @include text-style(xs, medium);
  text-align: center;
  color: var(--color-gray-600);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  
  .fashion-item & {
    color: var(--color-gray-900);
  }
}

// 快速操作
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.quick-action-btn {
  @include flex-center;
  @include transition();
  
  justify-content: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-gray-50);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-gray-600);
  position: relative;
  
  &:hover {
    background: var(--color-gray-100);
    border-color: var(--color-gray-300);
    transform: translateY(calc(-1 * var(--spacing-px)));
  }
}

.action-badge {
  @include absolute-center;
  @include flex-center;
  
  top: var(--spacing-2);
  right: var(--spacing-2);
  min-width: 18px;
  height: 18px;
  background: var(--color-red-500);
  color: var(--color-white);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-semibold);
  padding: 0 var(--spacing-1);
}

// 过渡动画
.popup-slide-enter-active,
.popup-slide-leave-active {
  @include transition(all, var(--duration-normal), var(--easing-smooth));
}

.popup-slide-enter-from,
.popup-slide-leave-to {
  opacity: 0;
  transform: translateY(var(--spacing-5)) scale(0.95);
}

.popup-slide-enter-to,
.popup-slide-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* 图标 */
.icon-default::before { content: '📄'; }
.icon-more::before { content: '⋯'; }
.icon-close::before { content: '✕'; }
.icon-tool::before { content: '🔧'; }
.icon-fashion::before { content: '✨'; }
.icon-profile::before { content: '👤'; }
.icon-notifications::before { content: '🔔'; }
.icon-help::before { content: '❓'; }

/* 常用底部导航图标 */
.icon-home::before { content: '🏠'; }
.icon-dashboard::before { content: '📊'; }
.icon-courses::before { content: '📚'; }
.icon-messages::before { content: '💬'; }
.icon-calendar::before { content: '📅'; }
.icon-grades::before { content: '📝'; }
.icon-library::before { content: '📖'; }
.icon-community::before { content: '👥'; }

/* 滚动条样式 */
.popup-content::-webkit-scrollbar {
  width: 4px;
}

.popup-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.popup-content::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 2px;
}

.popup-content::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .more-menu-popup {
    width: calc(100vw - 32px);
    right: 16px;
  }
  
  .menu-grid {
    grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
    gap: 8px;
  }
  
  .nav-item {
    min-width: 50px;
    padding: 6px 8px;
  }
  
  .nav-label {
    font-size: 10px;
    max-width: 50px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .optimized-bottom-navigation {
    background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    border-top-color: #4a5568;
  }
  
  .nav-icon,
  .nav-label {
    color: #e2e8f0;
  }
  
  .more-menu-popup {
    background: #2d3748;
    border-color: #4a5568;
  }
  
  .popup-header {
    background: #1a202c;
    border-bottom-color: #4a5568;
  }
  
  .popup-header h3 {
    color: #e2e8f0;
  }
  
  .menu-grid-item,
  .quick-action-btn {
    background: #1a202c;
    border-color: #4a5568;
    color: #e2e8f0;
  }
  
  .menu-grid-item:hover,
  .quick-action-btn:hover {
    background: #2d3748;
  }
}
</style>

