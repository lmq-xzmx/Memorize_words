<template>
  <view class="dynamic-menu" :class="{ 'menu-collapsed': isCollapsed }">
    <!-- 菜单头部 -->
    <view class="menu-header">
      <view class="user-info" v-if="userInfo">
        <image 
          class="avatar" 
          :src="userInfo.avatar || '/static/images/default-avatar.png'"
          mode="aspectFill"
        />
        <view class="user-details">
          <text class="username">{{ userInfo.nickname || userInfo.username }}</text>
          <text class="role">{{ getRoleDisplayName(userInfo.role) }}</text>
        </view>
      </view>
      
      <view class="menu-toggle" @tap="toggleMenu">
        <text class="toggle-icon">{{ isCollapsed ? '▶' : '◀' }}</text>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-state">
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 错误状态 -->
    <view v-else-if="error" class="error-state">
      <text class="error-text">{{ error }}</text>
      <button class="retry-btn" @tap="loadMenus">重试</button>
    </view>

    <!-- 菜单内容 -->
    <scroll-view v-else class="menu-content" scroll-y="true">
      <!-- 主菜单 -->
      <view class="menu-section" v-if="mainMenus.length > 0">
        <view class="section-title" v-if="!isCollapsed">
          <text>主菜单</text>
        </view>
        <view class="menu-list">
          <menu-item
            v-for="menu in mainMenus"
            :key="menu.id"
            :menu="menu"
            :collapsed="isCollapsed"
            @click="handleMenuClick"
          />
        </view>
      </view>

      <!-- 工具菜单 -->
      <view class="menu-section" v-if="toolMenus.length > 0">
        <view class="section-title" v-if="!isCollapsed">
          <text>工具</text>
        </view>
        <view class="menu-list">
          <menu-item
            v-for="menu in toolMenus"
            :key="menu.id"
            :menu="menu"
            :collapsed="isCollapsed"
            @click="handleMenuClick"
          />
        </view>
      </view>

      <!-- 开发工具菜单 (仅开发环境或有权限时显示) -->
      <view class="menu-section" v-if="showDevTools && devToolMenus.length > 0">
        <view class="section-title" v-if="!isCollapsed">
          <text>开发工具</text>
        </view>
        <view class="menu-list">
          <dev-tool-item
            v-for="tool in devToolMenus"
            :key="tool.id"
            :tool="tool"
            :collapsed="isCollapsed"
            @click="handleDevToolClick"
          />
        </view>
      </view>
    </scroll-view>

    <!-- 菜单底部 -->
    <view class="menu-footer" v-if="!isCollapsed">
      <view class="version-info">
        <text class="version-text">v{{ version }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import menuManager from '@/utils/menuManager.js'
import { ROLE_DISPLAY_NAMES } from '@/config/menuConfig.js'
import MenuItem from './MenuItem.vue'
import DevToolItem from './DevToolItem.vue'

export default {
  name: 'DynamicMenu',
  components: {
    MenuItem,
    DevToolItem
  },
  props: {
    collapsed: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isCollapsed: this.collapsed,
      loading: true,
      error: null,
      userInfo: null,
      mainMenus: [],
      toolMenus: [],
      devToolMenus: [],
      version: '1.0.0'
    }
  },
  computed: {
    showDevTools() {
      // 开发环境或有开发权限时显示
      // #ifdef H5
      if (process.env.NODE_ENV === 'development') return true
      // #endif
      
      return menuManager.hasPermission('dev')
    }
  },
  watch: {
    collapsed(newVal) {
      this.isCollapsed = newVal
    }
  },
  mounted() {
    this.loadUserInfo()
    this.loadMenus()
  },
  methods: {
    /**
     * 加载用户信息
     */
    loadUserInfo() {
      try {
        this.userInfo = menuManager.getCurrentUser()
      } catch (e) {
        console.error('加载用户信息失败:', e)
      }
    },

    /**
     * 加载菜单数据
     */
    async loadMenus() {
      this.loading = true
      this.error = null
      
      try {
        // 并行加载所有菜单
        const [mainMenus, toolMenus] = await Promise.all([
          this.loadMainMenus(),
          this.loadToolMenus()
        ])
        
        this.mainMenus = mainMenus
        this.toolMenus = toolMenus
        
        // 如果有开发权限，加载开发工具菜单
        if (this.showDevTools) {
          this.devToolMenus = await this.loadDevToolMenus()
        }
        
      } catch (e) {
        console.error('加载菜单失败:', e)
        this.error = '菜单加载失败，请重试'
      } finally {
        this.loading = false
      }
    },

    /**
     * 加载主菜单
     */
    async loadMainMenus() {
      try {
        return await menuManager.getMainMenus()
      } catch (error) {
        console.error('加载主菜单失败:', error)
        return []
      }
    },

    /**
     * 加载工具菜单
     */
    async loadToolMenus() {
      try {
        return await menuManager.getToolMenus()
      } catch (error) {
        console.error('加载工具菜单失败:', error)
        return []
      }
    },

    /**
     * 加载开发工具菜单
     */
    async loadDevToolMenus() {
      try {
        return await menuManager.getDevTools()
      } catch (error) {
        console.error('加载开发工具菜单失败:', error)
        // 回退到本地配置
        const devTools = [
          {
            id: 'api-test',
            title: 'API测试',
            icon: 'api',
            path: '/pages/dev/api-test',
            permission: 'dev'
          },
          {
            id: 'performance-monitor',
            title: '性能监控',
            icon: 'monitor',
            path: '/pages/dev/performance',
            permission: 'dev'
          }
        ]
        return devTools.filter(tool => menuManager.hasPermission(tool.permission))
      }
    },

    /**
     * 切换菜单折叠状态
     */
    toggleMenu() {
      this.isCollapsed = !this.isCollapsed
      this.$emit('toggle', this.isCollapsed)
    },

    /**
     * 处理菜单点击
     */
    handleMenuClick(menu) {
      if (menu.path) {
        const success = menuManager.navigateTo(menu.path)
        if (success) {
          this.$emit('menu-click', menu)
        }
      } else if (menu.action) {
        this.handleMenuAction(menu)
      }
    },

    /**
     * 处理开发工具点击
     */
    handleDevToolClick(tool) {
      if (tool.path) {
        const success = menuManager.navigateTo(tool.path)
        if (success) {
          this.$emit('dev-tool-click', tool)
        }
      }
    },

    /**
     * 处理菜单动作
     */
    handleMenuAction(menu) {
      switch (menu.action) {
        case 'logout':
          this.handleLogout()
          break
        case 'refresh':
          this.refreshMenus()
          break
        default:
          console.warn('未知的菜单动作:', menu.action)
      }
    },

    /**
     * 处理登出
     */
    handleLogout() {
      uni.showModal({
        title: '确认登出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 清除用户信息和token
            uni.removeStorageSync('user_info')
            uni.removeStorageSync('access_token')
            menuManager.clearCache()
            
            // 跳转到登录页
            uni.reLaunch({
              url: '/pages/login/login'
            })
          }
        }
      })
    },

    /**
     * 刷新菜单
     */
    async refreshMenus() {
      try {
        uni.showLoading({ title: '刷新中...' })
        
        // 刷新MenuManager缓存
        await menuManager.refreshMenus()
        
        // 重新加载组件菜单数据
        await this.loadMenus()
        
        uni.hideLoading()
        uni.showToast({
          title: '菜单已刷新',
          icon: 'success'
        })
      } catch (error) {
        uni.hideLoading()
        console.error('刷新菜单失败:', error)
        uni.showToast({
          title: '刷新失败',
          icon: 'error'
        })
      }
    },

    /**
     * 获取角色显示名称
     */
    getRoleDisplayName(role) {
      return ROLE_DISPLAY_NAMES[role] || role
    }
  }
}
</script>

<style lang="scss" scoped>
.dynamic-menu {
  height: 100vh;
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  width: 280px;
  
  &.menu-collapsed {
    width: 80px;
  }
}

.menu-header {
  padding: 20px;
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .user-info {
    display: flex;
    align-items: center;
    flex: 1;
    
    .avatar {
      width: 40px;
      height: 40px;
      border-radius: 20px;
      margin-right: 12px;
    }
    
    .user-details {
      display: flex;
      flex-direction: column;
      
      .username {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin-bottom: 4px;
      }
      
      .role {
        font-size: 12px;
        color: #666;
      }
    }
  }
  
  .menu-toggle {
    padding: 8px;
    cursor: pointer;
    
    .toggle-icon {
      font-size: 14px;
      color: #666;
    }
  }
}

.loading-state,
.error-state {
  padding: 40px 20px;
  text-align: center;
  
  .loading-text,
  .error-text {
    font-size: 14px;
    color: #666;
    margin-bottom: 16px;
  }
  
  .retry-btn {
    background: #007AFF;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
  }
}

.menu-content {
  flex: 1;
  padding: 16px 0;
}

.menu-section {
  margin-bottom: 24px;
  
  .section-title {
    padding: 0 20px 8px;
    
    text {
      font-size: 12px;
      color: #999;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
  }
  
  .menu-list {
    // 菜单项样式由子组件处理
  }
}

.menu-footer {
  padding: 16px 20px;
  border-top: 1px solid #e9ecef;
  background: #ffffff;
  
  .version-info {
    text-align: center;
    
    .version-text {
      font-size: 12px;
      color: #999;
    }
  }
}

/* 响应式适配 */
/* #ifdef H5 */
@media (max-width: 768px) {
  .dynamic-menu {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &.menu-show {
      transform: translateX(0);
    }
  }
}
/* #endif */

/* 小程序适配 */
/* #ifdef MP */
.dynamic-menu {
  width: 100%;
  height: auto;
  
  &.menu-collapsed {
    width: 100%;
  }
}
/* #endif */
</style>