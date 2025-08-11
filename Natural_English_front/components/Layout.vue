<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <TopNavBar />
    
    <!-- 侧边栏（桌面端） -->
    <aside class="sidebar" v-if="showSidebar">
      <DynamicMenu />
    </aside>
    
    <!-- 主要内容区域 -->
    <main class="main-content" :class="{ 'with-sidebar': showSidebar }">
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
    <BottomNavigation v-if="showBottomNav" />
  </div>
</template>

<script>
import TopNavBar from './TopNavBar.vue'
import BottomNavigation from './BottomNavigation.vue'
import DynamicMenu from './DynamicMenu.vue'

export default {
  name: 'Layout',
  components: {
    TopNavBar,
    BottomNavigation,
    DynamicMenu
  },
  
  data() {
    return {
      windowWidth: window.innerWidth
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
     * 处理权限变更
     */
    $onPermissionChange(user) {
      // 检查当前页面权限
      if (this.$route.meta.requiresAuth && (!user || !this.$canAccessPage(this.$route.path))) {
        this.$router.push(user ? '/dashboard' : '/login')
      }
    }
  },
  
  mounted() {
    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize)
  },
  
  beforeUnmount() {
    // 清理事件监听
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.sidebar {
  position: fixed;
  left: 0;
  top: 60px;
  width: 250px;
  height: calc(100vh - 60px);
  z-index: 100;
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  padding-top: 60px;
  padding-bottom: 20px;
  overflow-y: auto;
  transition: margin-left 0.3s ease;
}

.main-content.with-sidebar {
  margin-left: 250px;
}

.content-wrapper {
  padding: 20px;
}

.auth-required,
.permission-denied {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 140px);
  padding: 20px;
}

.auth-message,
.permission-message {
  text-align: center;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}

.auth-message {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 1px solid rgba(33, 150, 243, 0.2);
}

.permission-message {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.auth-message h3 {
  color: #1976d2;
  margin-bottom: 16px;
  font-size: 1.5rem;
}

.permission-message h3 {
  color: #f57c00;
  margin-bottom: 16px;
  font-size: 1.5rem;
}

.auth-message p,
.permission-message p {
  color: #666;
  margin-bottom: 12px;
  line-height: 1.5;
}

.role-info {
  font-weight: 600;
  color: #f57c00;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 16px;
}

.btn-primary {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .main-content {
    margin-left: 0;
    padding-bottom: 100px;
  }
  
  .main-content.with-sidebar {
    margin-left: 0;
  }
  
  .content-wrapper {
    padding: 10px;
  }
  
  .auth-message,
  .permission-message {
    padding: 20px;
    margin: 10px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .sidebar {
    background: #2d3748;
    border-right-color: #4a5568;
  }
  
  .auth-message {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    border-color: rgba(66, 165, 245, 0.3);
  }
  
  .permission-message {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    border-color: rgba(255, 183, 77, 0.3);
  }
  
  .auth-message h3 {
    color: #42a5f5;
  }
  
  .permission-message h3 {
    color: #ffb74d;
  }
  
  .auth-message p,
  .permission-message p {
    color: #a0aec0;
  }
  
  .role-info {
    color: #ffb74d;
  }
}
</style>