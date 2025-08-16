<template>
  <div class="optimized-dynamic-menu" :class="{ 'collapsed': isCollapsed }">
    <!-- 菜单头部 -->
    <div class="menu-header">
      <div class="user-info" v-if="currentUser">
        <div class="avatar">
          <img :src="userAvatar" :alt="currentUser.username" />
        </div>
        <div class="user-details" v-if="!isCollapsed">
          <div class="username">{{ currentUser.username }}</div>
          <div class="role-badge" :class="`role-${userRole}`">
            {{ roleDisplayName }}
          </div>
        </div>
      </div>
      
      <button 
        class="collapse-btn"
        @click="toggleCollapse"
        :title="isCollapsed ? '展开菜单' : '折叠菜单'"
      >
        <i :class="isCollapsed ? 'icon-expand' : 'icon-collapse'"></i>
      </button>
    </div>

    <!-- 菜单加载状态 -->
    <div v-if="isMenuLoading" class="menu-loading">
      <div class="loading-spinner"></div>
      <span v-if="!isCollapsed">加载菜单中...</span>
    </div>

    <!-- 菜单错误状态 -->
    <div v-else-if="menuError" class="menu-error">
      <i class="icon-error"></i>
      <span v-if="!isCollapsed">{{ menuError }}</span>
      <button @click="$refreshMenus" class="retry-btn" v-if="!isCollapsed">
        重试
      </button>
    </div>

    <!-- 主菜单列表 -->
    <div v-else class="menu-content">
      <nav class="main-menu">
        <menu-item
          v-for="menu in accessibleMainMenus"
          :key="menu.id"
          :menu="menu"
          :active="activeMenu === menu.id"
          :collapsed="isCollapsed"
          :expanded="isMenuExpanded(menu.id)"
          @click="handleMenuClick"
          @toggle="handleMenuToggle"
        />
      </nav>

      <!-- 工具菜单 -->
      <div class="tool-menu-section" v-if="accessibleToolMenus.length > 0">
        <div class="section-title" v-if="!isCollapsed">
          <i class="icon-tools"></i>
          <span>工具</span>
        </div>
        <nav class="tool-menu">
          <menu-item
            v-for="tool in accessibleToolMenus"
            :key="tool.id"
            :menu="tool"
            :active="activeMenu === tool.id"
            :collapsed="isCollapsed"
            :compact="true"
            @click="handleMenuClick"
          />
        </nav>
      </div>

      <!-- 开发工具菜单 (仅开发环境或管理员) -->
      <div 
        class="dev-menu-section" 
        v-if="showDevTools && devToolMenus.length > 0"
      >
        <div class="section-title" v-if="!isCollapsed">
          <i class="icon-dev"></i>
          <span>开发工具</span>
        </div>
        <nav class="dev-menu">
          <dev-tool-item
            v-for="tool in devToolMenus"
            :key="tool.id"
            :tool="tool"
            :enabled="isDevToolEnabled(tool.id)"
            :collapsed="isCollapsed"
            @toggle="handleDevToolToggle"
            @click="handleMenuClick"
          />
        </nav>
      </div>
    </div>

    <!-- 菜单底部 -->
    <div class="menu-footer" v-if="!isCollapsed">
      <div class="quick-actions">
        <button 
          v-permission="'system.settings'"
          class="action-btn"
          @click="navigateToSettings"
          title="系统设置"
        >
          <i class="icon-settings"></i>
          <span>设置</span>
        </button>
        
        <button 
          class="action-btn logout-btn"
          @click="handleLogout"
          title="退出登录"
        >
          <i class="icon-logout"></i>
          <span>退出</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import permissionMixin from '../mixins/permissionMixin.js'
import MenuItem from './menu/MenuItem.vue'

export default {
  name: 'OptimizedDynamicMenu',
  
  components: {
    MenuItem
  },
  
  mixins: [permissionMixin],
  
  props: {
    // 是否显示开发工具
    showDevTools: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      isCollapsed: false,
      activeMenu: null,
      devToolMenus: [],
      isMenuLoading: false,
      menuError: null
    }
  },
  
  computed: {
    // 用户头像
    userAvatar() {
      return this.currentUser?.avatar || '/default-avatar.png'
    }
  },
  
  methods: {
    /**
     * 切换菜单折叠状态
     */
    toggleCollapse() {
      this.isCollapsed = !this.isCollapsed
      this.$emit('collapse-change', this.isCollapsed)
    },
    
    /**
     * 检查菜单是否展开
     * @param {string} menuId - 菜单ID
     * @returns {boolean} 是否展开
     */
    isMenuExpanded(menuId) {
      // 简化实现，可以根据需要扩展
      return false
    },
    
    /**
     * 检查开发工具是否启用
     * @param {string} toolId - 工具ID
     * @returns {boolean} 是否启用
     */
    isDevToolEnabled(toolId) {
      // 简化实现，可以根据需要扩展
      return true
    },
    
    /**
     * 处理菜单点击
     * @param {Object} menu - 菜单项
     */
    async handleMenuClick(menu) {
      if (!menu.path) {
        console.warn('菜单项缺少路径:', menu)
        return
      }
      
      try {
        // 设置活动菜单
        this.activeMenu = menu.id
        
        // 带权限检查的导航
        await this.$navigateWithPermission(menu.path)
        
        // 触发菜单点击事件
        this.$emit('menu-click', menu)
        
      } catch (error) {
        console.error('菜单导航失败:', error)
        // 恢复之前的活动菜单状态
        this.restoreActiveMenu()
      }
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
     * 导航到设置页面
     */
    async navigateToSettings() {
      await this.$navigateWithPermission('/settings')
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
        if (window.permissionService) {
          window.permissionService.clearAuth()
        }
        
        // 导航到登录页
        this.$router.push('/login')
        
        this.$emit('logout')
        
      } catch (error) {
        console.error('退出登录失败:', error)
        this.$showError('退出登录失败，请重试')
      }
    },
    
    /**
     * 恢复活动菜单状态
     */
    restoreActiveMenu() {
      const currentPath = this.$route?.path
      if (currentPath) {
        // 根据当前路径设置活动菜单
        const activeMenuItem = this.accessibleMainMenus.find(menu => 
          currentPath.startsWith(menu.path)
        )
        if (activeMenuItem) {
          this.activeMenu = activeMenuItem.id
        }
      }
    },
    
    /**
     * 处理路由变化
     * @param {Object} to - 目标路由
     */
    handleRouteChange(to) {
      const activeMenuItem = this.accessibleMainMenus.find(menu => 
        to.path.startsWith(menu.path)
      )
      if (activeMenuItem) {
        this.activeMenu = activeMenuItem.id
      }
    }
  },
  
  watch: {
    // 监听路由变化
    '$route'(to) {
      this.handleRouteChange(to)
    }
  },
  
  mounted() {
    // 初始化活动菜单
    if (this.$route) {
      this.handleRouteChange(this.$route)
    }
  }
}
</script>

<style scoped>
.optimized-dynamic-menu {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: #ffffff;
  transition: width 0.3s ease;
  width: 280px;
  min-width: 280px;
}

.optimized-dynamic-menu.collapsed {
  width: 64px;
  min-width: 64px;
}

/* 菜单头部 */
.menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 80px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 600;
  font-size: 14px;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  margin-top: 4px;
  display: inline-block;
}

.role-admin { background: #e53e3e; }
.role-teacher { background: #3182ce; }
.role-student { background: #38a169; }
.role-parent { background: #d69e2e; }
.role-dean { background: #805ad5; }

.collapse-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

/* 菜单内容 */
.menu-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.menu-loading,
.menu-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 8px;
  padding: 6px 12px;
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.retry-btn:hover {
  background: #2c5aa0;
}

/* 菜单分组 */
.tool-menu-section,
.dev-menu-section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px 8px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 菜单底部 */
.menu-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.logout-btn:hover {
  background: #e53e3e;
}

/* 图标样式 */
.icon-expand::before { content: '→'; }
.icon-collapse::before { content: '←'; }
.icon-error::before { content: '⚠'; }
.icon-tools::before { content: '🔧'; }
.icon-dev::before { content: '⚙'; }
.icon-settings::before { content: '⚙'; }
.icon-logout::before { content: '↪'; }

/* 响应式设计 */
@media (max-width: 768px) {
  .optimized-dynamic-menu {
    width: 100%;
    min-width: 100%;
  }
  
  .optimized-dynamic-menu.collapsed {
    width: 0;
    min-width: 0;
    overflow: hidden;
  }
}

/* 滚动条样式 */
.menu-content::-webkit-scrollbar {
  width: 4px;
}

.menu-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.menu-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.menu-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>