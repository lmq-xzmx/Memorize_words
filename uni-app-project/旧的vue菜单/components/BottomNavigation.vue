<template>
  <div 
    class="optimized-bottom-navigation"
    :class="{ 'hidden': !visible }"
    v-if="shouldShowBottomNav"
  >
    <!-- 主要导航项 -->
    <nav class="bottom-nav-content">
      <div 
        v-for="menu in accessibleBottomMenus"
        :key="menu.id"
        class="nav-item"
        :class="{
          'active': activeBottomMenu === menu.id,
          'disabled': menu.disabled
        }"
        @click="handleNavClick(menu)"
      >
        <div class="nav-icon">
          <i :class="menu.icon || 'icon-default'"></i>
          <span 
            v-if="menu.badge" 
            class="nav-badge"
            :class="`badge-${menu.badge.type || 'default'}`"
          >
            {{ menu.badge.text }}
          </span>
        </div>
        <span class="nav-label">{{ menu.title }}</span>
      </div>
    </nav>
    
    <!-- 更多菜单 -->
    <div class="more-menu" v-if="hasMoreMenus">
      <div 
        class="nav-item more-item"
        :class="{ 'active': showMoreMenu }"
        @click="toggleMoreMenu"
      >
        <div class="nav-icon">
          <i class="icon-more"></i>
        </div>
        <span class="nav-label">更多</span>
      </div>
      
      <!-- 更多菜单弹出层 -->
      <transition name="more-menu-popup">
        <div v-if="showMoreMenu" class="more-menu-popup">
          <div class="popup-header">
            <h3>更多功能</h3>
            <button class="close-btn" @click="closeMoreMenu">
              <i class="icon-close"></i>
            </button>
          </div>
          
          <div class="popup-content">
            <!-- 工具菜单 -->
            <div class="menu-section" v-if="accessibleToolMenus.length > 0">
              <h4>工具</h4>
              <div class="menu-grid">
                <div 
                  v-for="tool in accessibleToolMenus"
                  :key="tool.id"
                  class="menu-grid-item"
                  @click="handleToolClick(tool)"
                >
                  <div class="grid-icon">
                    <i :class="tool.icon || 'icon-tool'"></i>
                  </div>
                  <span class="grid-label">{{ tool.title }}</span>
                </div>
              </div>
            </div>
            
            <!-- 时尚菜单 -->
            <div class="menu-section" v-if="fashionMenus.length > 0">
              <h4>时尚</h4>
              <div class="menu-grid">
                <div 
                  v-for="fashion in fashionMenus"
                  :key="fashion.id"
                  class="menu-grid-item fashion-item"
                  @click="handleFashionClick(fashion)"
                >
                  <div class="grid-icon">
                    <i :class="fashion.icon || 'icon-fashion'"></i>
                  </div>
                  <span class="grid-label">{{ fashion.title }}</span>
                </div>
              </div>
            </div>
            
            <!-- 快速操作 -->
            <div class="menu-section">
              <h4>快速操作</h4>
              <div class="quick-actions">
                <button 
                  v-permission="'profile.view'"
                  class="quick-action-btn"
                  @click="navigateToProfile"
                >
                  <i class="icon-profile"></i>
                  <span>个人资料</span>
                </button>
                
                <button 
                  v-permission="'notifications.view'"
                  class="quick-action-btn"
                  @click="navigateToNotifications"
                >
                  <i class="icon-notifications"></i>
                  <span>通知中心</span>
                  <span 
                    v-if="notificationCount > 0"
                    class="action-badge"
                  >
                    {{ notificationCount }}
                  </span>
                </button>
                
                <button 
                  v-permission="'help.view'"
                  class="quick-action-btn"
                  @click="navigateToHelp"
                >
                  <i class="icon-help"></i>
                  <span>帮助中心</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
    
    <!-- 遮罩层 -->
    <div 
      v-if="showMoreMenu"
      class="overlay"
      @click="closeMoreMenu"
    ></div>
  </div>
</template>

<script>
import { optimizedPermissionMixin } from '../mixins/optimizedPermissionMixin.js'
import menuStateManager, { menuState } from '../services/MenuStateManager.js'

export default {
  name: 'OptimizedBottomNavigation',
  
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

<style scoped>
.optimized-bottom-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: transform 0.3s ease;
}

.optimized-bottom-navigation.hidden {
  transform: translateY(100%);
}

/* 底部导航内容 */
.bottom-nav-content {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 8px 16px;
  min-height: 64px;
}

/* 导航项 */
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.2s ease;
  min-width: 60px;
  position: relative;
}

.nav-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.nav-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-item.disabled:hover {
  background: transparent;
  transform: none;
}

/* 导航图标 */
.nav-icon {
  position: relative;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 4px;
  color: #4a5568;
}

.nav-item.active .nav-icon {
  color: #ffffff;
}

/* 导航标签 */
.nav-label {
  font-size: 11px;
  font-weight: 500;
  color: #4a5568;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 60px;
}

.nav-item.active .nav-label {
  color: #ffffff;
}

/* 徽章 */
.nav-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  padding: 0 4px;
}

.badge-default { background: #e53e3e; }
.badge-primary { background: #3182ce; }
.badge-success { background: #38a169; }
.badge-warning { background: #d69e2e; }
.badge-info { background: #3182ce; }

/* 更多菜单 */
.more-menu {
  position: relative;
}

.more-item {
  position: relative;
}

/* 更多菜单弹出层 */
.more-menu-popup {
  position: absolute;
  bottom: 100%;
  right: 16px;
  width: 320px;
  max-height: 400px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  margin-bottom: 8px;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #f7fafc;
}

.popup-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #718096;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #e2e8f0;
  color: #2d3748;
}

.popup-content {
  max-height: 320px;
  overflow-y: auto;
  padding: 16px 20px;
}

/* 菜单分组 */
.menu-section {
  margin-bottom: 20px;
}

.menu-section:last-child {
  margin-bottom: 0;
}

.menu-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  margin: 0 0 12px 0;
}

/* 菜单网格 */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.menu-grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f7fafc;
}

.menu-grid-item:hover {
  background: #edf2f7;
  transform: translateY(-2px);
}

.menu-grid-item.fashion-item {
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
  color: #2d3748;
}

.menu-grid-item.fashion-item:hover {
  background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
}

.grid-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 6px;
  color: #4a5568;
}

.fashion-item .grid-icon {
  color: #2d3748;
}

.grid-label {
  font-size: 11px;
  font-weight: 500;
  text-align: center;
  color: #4a5568;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.fashion-item .grid-label {
  color: #2d3748;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #4a5568;
  position: relative;
}

.quick-action-btn:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
  transform: translateY(-1px);
}

.action-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  min-width: 18px;
  height: 18px;
  background: #e53e3e;
  color: #ffffff;
  border-radius: 9px;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

/* 遮罩层 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: -1;
}

/* 过渡动画 */
.more-menu-popup-enter-active,
.more-menu-popup-leave-active {
  transition: all 0.3s ease;
}

.more-menu-popup-enter-from,
.more-menu-popup-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.more-menu-popup-enter-to,
.more-menu-popup-leave-from {
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