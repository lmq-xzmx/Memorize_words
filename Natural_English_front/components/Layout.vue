<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <TopNavBar>
      <!-- 将菜单移动到顶部导航栏右侧 -->
      <template #right-menu v-if="showTopMenu">
        <div class="top-menu-container">
          <div class="menu-toggle" @click="toggleMenu">
            <span class="menu-icon">☰</span>
            <span class="menu-text">工具</span>
          </div>
          
          <!-- 下拉菜单 -->
          <transition name="dropdown">
            <div v-if="showDropdownMenu" class="dropdown-menu" @click.stop>
              <div 
                v-for="menu in accessibleMenus" 
                :key="menu.id"
                class="dropdown-item"
                :class="{ active: isActiveMenu(menu.path) }"
                @click="navigateToMenu(menu)"
              >
                <span class="item-icon">{{ menu.icon }}</span>
                <span class="item-title">{{ menu.title }}</span>
                <span v-if="menu.badge" class="item-badge">{{ menu.badge }}</span>
              </div>
            </div>
          </transition>
        </div>
      </template>
    </TopNavBar>
    
    <!-- 侧边栏（桌面端，使用优化版动态菜单） -->
    <aside class="sidebar" v-if="showSidebar">
      <OptimizedDynamicMenu 
        :show-dev-tools="isDeveloper || isAdmin"
        @menu-click="handleMenuClick"
        @collapse-change="handleSidebarCollapse"
      />
    </aside>
    
    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 权限检查提示 -->
      <div v-if="!isUserAuthenticated && $route.meta.requiresAuth" class="auth-required">
        <div class="auth-message">
          <h3>🔒 需要登录</h3>
          <p>此页面需要登录后才能访问</p>
          <button @click="$router.push('/login')" class="btn-primary">立即登录</button>
        </div>
      </div>
      
      <!-- 权限不足提示 -->
      <div v-else-if="!hasPagePermission" class="permission-denied">
        <div class="permission-message">
          <h3>⚠️ 权限不足</h3>
          <p>您没有权限访问此页面</p>
          <p class="role-info">当前角色：{{ roleDisplayName }}</p>
          <button @click="$router.push('/dashboard')" class="btn-secondary">返回仪表板</button>
        </div>
      </div>
      
      <!-- 正常内容 -->
      <div v-else class="content-wrapper">
        <router-view />
      </div>
    </main>
    
    <!-- 底部导航栏（移动端） -->
    <TabBar v-if="showBottomNav" />
  </div>
</template>

<script>
import TopNavBar from './TopNavBar.vue'
import TabBar from './navigation/TabBar.vue'
import DynamicMenu from './DynamicMenu.vue'
import OptimizedDynamicMenu from './OptimizedDynamicMenu.vue'
import permissionMixin from '../mixins/permissionMixin'

export default {
  name: 'Layout',
  mixins: [permissionMixin],
  components: {
    TopNavBar,
    TabBar,
    DynamicMenu,
    OptimizedDynamicMenu
  },
  
  data() {
    return {
      windowWidth: window.innerWidth,
      showDropdownMenu: false
    }
  },
  
  computed: {
    /**
     * 是否显示侧边栏（桌面端）
     */
    showSidebar() {
      return this.windowWidth >= 768 && this.isUserAuthenticated
    },
    
    /**
     * 是否显示顶部菜单
     */
    showTopMenu() {
      return this.isUserAuthenticated
    },
    
    /**
     * 是否显示底部导航（移动端）
     */
    showBottomNav() {
      return this.windowWidth < 768 && this.isUserAuthenticated
    },
    
    /**
     * 检查当前页面权限
     */
    hasPagePermission() {
      if (!this.$route.meta.requiresAuth) {
        return true
      }
      
      if (!this.isUserAuthenticated) {
        return false
      }
      
      return this.$canAccessPage(this.$route.path)
    },
    
    /**
     * 是否为开发者
     */
    isDeveloper() {
      return this.$hasRole('developer')
    },
    
    /**
     * 是否为管理员
     */
    isAdmin() {
      return this.$hasRole('admin')
    }
  },
  
  methods: {
    /**
     * 处理窗口大小变化
     */
    handleResize() {
      this.windowWidth = window.innerWidth
    },
    
    /**
     * 切换菜单显示状态
     */
    toggleMenu() {
      this.showDropdownMenu = !this.showDropdownMenu
    },
    
    /**
     * 检查菜单是否为当前激活状态
     */
    isActiveMenu(path) {
      return this.$route.path === path || this.$route.path.startsWith(path + '/')
    },
    
    /**
     * 导航到菜单页面
     */
    navigateToMenu(menu) {
      if (this.$canAccessPage(menu.path)) {
        this.$router.push(menu.path)
        this.showDropdownMenu = false // 关闭菜单
      } else {
        this.$showError(`您没有权限访问 ${menu.title}`)
      }
    },
    
    /**
     * 处理点击外部关闭菜单
     */
    handleClickOutside(event) {
      const menuContainer = event.target.closest('.top-menu-container')
      if (!menuContainer && this.showDropdownMenu) {
        this.showDropdownMenu = false
      }
    },
    
    /**
     * 处理权限变更
     */
    $onPermissionChange(user) {
      // 检查当前页面权限
      if (this.$route.meta.requiresAuth && (!user || !this.$canAccessPage(this.$route.path))) {
        this.$router.push(user ? '/dashboard' : '/login')
      }
    },
    
    /**
     * 处理侧边栏菜单点击
     * @param {Object} menu - 菜单项
     */
    handleMenuClick(menu) {
      console.log('侧边栏菜单点击:', menu)
    },
    
    /**
     * 处理侧边栏折叠状态变化
     * @param {boolean} collapsed - 是否折叠
     */
    handleSidebarCollapse(collapsed) {
      console.log('侧边栏折叠状态:', collapsed)
      // 可以在这里保存用户偏好设置
    }
  },
  
  mounted() {
    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize)
    
    // 监听点击外部关闭菜单
    document.addEventListener('click', this.handleClickOutside)
  },
  
  beforeUnmount() {
    // 清理事件监听
    window.removeEventListener('resize', this.handleResize)
    document.removeEventListener('click', this.handleClickOutside)
  }
}
</script>

<style lang="scss" scoped>
@use '../styles/index.scss';

.layout {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-blue-100) 100%);
  position: relative;
  @include flex-column;
  animation: fadeIn 0.6s ease-out;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 1000;
  background: var(--color-white);
  box-shadow: var(--shadow-lg);
  transition: all 0.2s ease;

  @media (max-width: 768px) {
    transform: translateX(-100%);

    @include bem-modifier('mobile-open') {
      transform: translateX(0);
    }
  }

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(var(--color-primary-500-rgb), 0.3);
    border-radius: 3px;

    &:hover {
      background: rgba(var(--color-primary-500-rgb), 0.5);
    }
  }
}

.main-content {
  flex: 1;
  min-height: calc(100vh - 120px);
  padding: var(--spacing-8);
  transition: all 0.2s ease;

  @include media-breakpoint-up('md') {
    margin-left: 280px;

    @include bem-modifier('sidebar-collapsed') {
      margin-left: 64px;
    }
  }

  @include bem-modifier('with-bottom-nav') {
    padding-bottom: 100px;
  }
}

@include bem-element('top-menu-container') {
  position: relative;
  display: inline-block;
}

@include bem-element('menu-toggle') {
  @include flex-center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-6);
  background: rgba(var(--color-white-rgb), 0.9);
  border: 1px solid rgba(var(--color-primary-500-rgb), 0.2);
  border-radius: var(--border-radius-full);
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
  box-shadow: $shadow-md;

  &:hover {
    background: rgba(var(--color-primary-500-rgb), 0.1);
    border-color: rgba(var(--color-primary-500-rgb), 0.3);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);

    .menu-icon {
      transform: rotate(90deg);
    }
  }

  @media (max-width: 768px) {
    padding: var(--spacing-2) var(--spacing-4);

    .menu-text {
      display: none;
    }
  }
}

@include bem-element('menu-icon') {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-normal);
  color: var(--color-primary-500);
  transition: transform 0.2s ease;
}

@include bem-element('menu-text') {
  @include text-style('sm', 'semibold');
  color: var(--color-gray-900);
}

/* 下拉菜单 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  min-width: 250px;
  z-index: 950;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  position: relative;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateX(5px);
}

.dropdown-item.active {
  background: rgba(102, 126, 234, 0.1);
  border-left: 4px solid #667eea;
}

.dropdown-item.active:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.item-icon {
  font-size: 1.3rem;
  width: 24px;
  text-align: center;
  transition: transform 0.3s ease;
}

.dropdown-item:hover .item-icon {
  transform: scale(1.2);
}

.item-title {
  flex: 1;
  font-weight: 500;
  font-size: 0.95rem;
}

.item-badge {
  background: #ff4757;
  color: white;
  font-size: 0.7rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
}

.dropdown-item:hover .item-badge {
  background: rgba(255, 255, 255, 0.3);
}

/* 下拉动画 */
.dropdown-enter-active {
  transition: all 0.3s ease;
}

.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* 主内容区域 */
.main-content {
  min-height: calc(100vh - 120px);
  padding: 2rem;
  transition: all 0.3s ease;
}

.main-content.with-sidebar {
  margin-left: 280px;
}

.main-content.with-bottom-nav {
  padding-bottom: 100px;
}

/* 侧边栏样式 */
.sidebar {
  position: fixed;
  left: 0;
  top: 80px;
  width: 280px;
  height: calc(100vh - 80px);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow-y: auto;
  transition: transform 0.3s ease;
}

.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* 权限提示 */
.permission-denied {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: 2rem;
}

.permission-icon {
  font-size: 4rem;
  color: #ff4757;
  margin-bottom: 1.5rem;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

.permission-title {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1rem;
}

.permission-message {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 2rem;
  max-width: 500px;
  line-height: 1.6;
}

.permission-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.permission-btn {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.permission-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.permission-btn.primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.permission-btn.secondary {
  background: rgba(255, 255, 255, 0.8);
  color: #667eea;
  border: 2px solid #667eea;
}

.permission-btn.secondary:hover {
  background: #667eea;
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content.with-sidebar {
    margin-left: 0;
  }
  
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .dropdown-menu {
    min-width: 200px;
    right: -20px;
  }
  
  .menu-toggle {
    padding: 0.6rem 1rem;
  }
  
  .menu-text {
    display: none;
  }
  
  .permission-title {
    font-size: 1.5rem;
  }
  
  .permission-message {
    font-size: 1rem;
  }
  
  .permission-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .permission-btn {
    width: 100%;
    max-width: 250px;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 1rem;
  }
  
  .dropdown-menu {
    min-width: 180px;
    right: -30px;
  }
  
  .dropdown-item {
    padding: 0.8rem 1rem;
  }
  
  .item-title {
    font-size: 0.9rem;
  }
  
  .permission-icon {
    font-size: 3rem;
  }
  
  .permission-title {
    font-size: 1.3rem;
  }
}

/* 加载动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.layout {
  animation: fadeIn 0.6s ease-out;
}
</style>

