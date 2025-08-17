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
import permissionMixin from '../mixins/permissionMixin'
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

<style lang="scss" scoped>
@use '../styles/index.scss';
@include bem-block('optimized-dynamic-menu') {
  @include flex-column;
  height: 100%;
  background: linear-gradient(180deg, var(--color-slate-900) 0%, var(--color-slate-800) 100%);
  color: var(--color-white);
  transition: all 0.2s ease;
  width: 280px;
  min-width: 280px;

  @include bem-modifier('collapsed') {
    width: 64px;
    min-width: 64px;
  }
}

@include bem-element('menu-header') {
  @include flex-between;
  padding: var(--spacing-4);
  border-bottom: 1px solid rgba(var(--color-white), 0.1);
  min-height: 80px;
}

@include bem-element('user-info') {
  @include flex-start;
  gap: var(--spacing-3);
  flex: 1;
  min-width: 0;
}

@include bem-element('avatar') {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-full);
  overflow: hidden;
  border: 2px solid rgba(var(--color-white), 0.2);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

@include bem-element('user-details') {
  flex: 1;
  min-width: 0;
}

@include bem-element('username') {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-white);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@include bem-element('role-badge') {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-normal);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-full);
  margin-top: var(--spacing-1);
  display: inline-block;

  @include bem-modifier('admin') {
    background: var(--color-red-500);
  }

  @include bem-modifier('teacher') {
    background: var(--color-blue-500);
  }

  @include bem-modifier('student') {
    background: var(--color-green-500);
  }

  @include bem-modifier('parent') {
    background: var(--color-yellow-500);
  }

  @include bem-modifier('dean') {
    background: var(--color-purple-500);
  }
}

@include bem-element('collapse-btn') {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(var(--color-white), 0.1);
  color: var(--color-white);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  @include flex-center;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(var(--color-white), 0.2);
    transform: scale(1.05);
  }
}

@include bem-element('menu-content') {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-4) 0;
}

@include bem-element('menu-loading') {
  @include flex-center;
  flex-direction: column;
  padding: var(--spacing-8) var(--spacing-4);
  text-align: center;
  color: rgba(var(--color-white), 0.7);
}

@include bem-element('menu-error') {
  @include flex-center;
  flex-direction: column;
  padding: var(--spacing-8) var(--spacing-4);
  text-align: center;
  color: rgba(var(--color-white), 0.7);
}

@include bem-element('loading-spinner') {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(var(--color-white), 0.3);
  border-top: 2px solid var(--color-white);
  border-radius: var(--border-radius-full);
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-2);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@include bem-element('retry-btn') {
  margin-top: var(--spacing-2);
  padding: var(--spacing-1) var(--spacing-3);
  background: var(--color-blue-500);
  color: var(--color-white);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-normal);
  transition: all 0.2s ease;

  &:hover {
    background: var(--color-blue-600);
  }
}

@include bem-element('tool-menu-section') {
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: 1px solid rgba(var(--color-white), 0.1);
}

@include bem-element('dev-menu-section') {
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: 1px solid rgba(var(--color-white), 0.1);
}

@include bem-element('section-title') {
  @include flex-start;
  gap: var(--spacing-2);
  padding: 0 var(--spacing-4) var(--spacing-2);
  @include text-style('xs', 'semibold');
  color: rgba(var(--color-white), 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

@include bem-element('menu-footer') {
  padding: var(--spacing-4);
  border-top: 1px solid rgba(var(--color-white), 0.1);
}

@include bem-element('quick-actions') {
  @include flex-start;
  gap: var(--spacing-2);
}

@include bem-element('action-btn') {
  flex: 1;
  @include flex-center;
  gap: var(--spacing-1);
  padding: var(--spacing-2) var(--spacing-3);
  background: rgba(var(--color-white), 0.1);
  color: var(--color-white);
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-normal);
  transition: all 0.2s ease;

  &:hover {
    background: rgba(var(--color-white), 0.2);
    transform: translateY(-1px);
  }

  @include bem-modifier('logout') {
    &:hover {
      background: var(--color-red-500);
    }
  }
}

// 图标样式
.icon-expand::before { content: '→'; }
.icon-collapse::before { content: '←'; }
.icon-error::before { content: '⚠'; }
.icon-tools::before { content: '🔧'; }
.icon-dev::before { content: '⚙'; }
.icon-settings::before { content: '⚙'; }
.icon-logout::before { content: '↪'; }

// 响应式设计
@media (max-width: 768px) {
  @include bem-block('optimized-dynamic-menu') {
    width: 100%;
    min-width: 100%;
    
    @include bem-modifier('collapsed') {
      width: 0;
      min-width: 0;
      overflow: hidden;
    }
  }
}

// 滚动条样式
@include bem-element('menu-content') {
  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(var(--color-white), 0.1);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(var(--color-white), 0.3);
    border-radius: 2px;

    &:hover {
      background: rgba(var(--color-white), 0.5);
    }
  }
}
</style>