<template>
  <view class="bottom-navigation" v-if="showBottomNav">
    <!-- 主要导航项 -->
    <view class="nav-container">
      <view 
        v-for="(item, index) in visibleNavItems" 
        :key="item.id"
        class="nav-item"
        :class="{ 'nav-item-active': isActiveItem(item) }"
        @tap="handleNavClick(item)"
      >
        <view class="nav-icon">
          <text class="icon-text">{{ getIconText(item.icon) }}</text>
          <view class="badge" v-if="item.badge">
            <text class="badge-text">{{ item.badge }}</text>
          </view>
        </view>
        <text class="nav-label">{{ item.title }}</text>
      </view>
      
      <!-- 更多菜单按钮 -->
      <view 
        v-if="hasMoreMenus"
        class="nav-item more-item"
        :class="{ 'nav-item-active': showMoreMenu }"
        @tap="toggleMoreMenu"
      >
        <view class="nav-icon">
          <text class="icon-text">{{ showMoreMenu ? '✕' : '⋯' }}</text>
        </view>
        <text class="nav-label">更多</text>
      </view>
    </view>
    
    <!-- 更多菜单弹出层 -->
    <view 
      class="more-menu-overlay"
      :class="{ 'overlay-show': showMoreMenu }"
      @tap="hideMoreMenu"
      v-if="showMoreMenu"
    >
      <view class="more-menu" @tap.stop="">
        <!-- 工具菜单 -->
        <view class="menu-section" v-if="toolMenus.length > 0">
          <view class="section-header">
            <text class="section-title">工具</text>
          </view>
          <view class="menu-grid">
            <view 
              v-for="tool in toolMenus"
              :key="tool.id"
              class="menu-grid-item"
              @tap="handleToolClick(tool)"
            >
              <view class="grid-icon">
                <text class="icon-text">{{ getIconText(tool.icon) }}</text>
              </view>
              <text class="grid-label">{{ tool.title }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { MENU_ITEMS, hasPermission, getCurrentUserRole } from '@/config/menuConfig.js'
import menuManager from '@/utils/menuManager.js'

export default {
  name: 'BottomNavigation',
  props: {
    maxVisibleItems: {
      type: Number,
      default: 4
    }
  },
  data() {
    return {
      showMoreMenu: false,
      bottomMenus: [],
      toolMenus: [],
      currentPlatform: 'h5',
      userRole: 'student'
    }
  },
  computed: {
    showBottomNav() {
      // 简化的显示逻辑，避免复杂的页面检查
      return true
    },
    
    visibleNavItems() {
      const maxItems = this.hasMoreMenus ? this.maxVisibleItems - 1 : this.maxVisibleItems
      return this.bottomMenus.slice(0, maxItems)
    },
    
    hasMoreMenus() {
      return this.bottomMenus.length > this.maxVisibleItems || this.toolMenus.length > 0
    }
  },
  mounted() {
    this.userRole = getCurrentUserRole()
    this.loadMenus()
  },
  methods: {
    async loadMenus() {
      try {
        // 优先从后端API获取菜单数据
        const [bottomMenus, toolMenus] = await Promise.all([
          this.loadBottomMenus(),
          this.loadToolMenus()
        ])
        
        this.bottomMenus = bottomMenus
        this.toolMenus = toolMenus
        
      } catch (error) {
        console.error('加载菜单失败:', error)
        // 提供默认菜单
        this.bottomMenus = [
          { id: 'home', title: '首页', icon: 'home', path: '/pages/index/index' },
          { id: 'study', title: '学习', icon: 'book', path: '/pages/study/index' },
          { id: 'profile', title: '我的', icon: 'user', path: '/pages/profile/index' }
        ]
        this.toolMenus = []
      }
    },
    
    /**
     * 加载底部菜单
     */
    async loadBottomMenus() {
      try {
        return await menuManager.getBottomMenus()
      } catch (error) {
        console.warn('从后端获取底部菜单失败，使用本地配置:', error)
        // 回退到本地配置
        if (MENU_ITEMS && MENU_ITEMS.BOTTOM_MENUS) {
          return MENU_ITEMS.BOTTOM_MENUS.filter(menu => 
            hasPermission(menu.permission, this.userRole)
          )
        }
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
        console.warn('从后端获取工具菜单失败，使用本地配置:', error)
        // 回退到本地配置
        if (MENU_ITEMS && MENU_ITEMS.TOOL_MENUS) {
          return MENU_ITEMS.TOOL_MENUS.filter(menu => 
            hasPermission(menu.permission, this.userRole)
          )
        }
        return []
      }
    },
    
    getIconText(icon) {
      const iconMap = {
        'home': '🏠',
        'book': '📚',
        'user': '👤',
        'settings': '⚙️',
        'community': '👥',
        'tools': '🔧'
      }
      return iconMap[icon] || '📱'
    },
    
    isActiveItem(item) {
      try {
        const pages = getCurrentPages()
        if (!pages || pages.length === 0) return false
        
        const currentPage = pages[pages.length - 1]
        if (!currentPage || !currentPage.route) return false
        
        const currentPath = `/${currentPage.route}`
        return currentPath === item.path
      } catch (error) {
        return false
      }
    },
    
    handleNavClick(item) {
      if (!item || !item.path) return
      
      try {
        // 使用MenuManager的导航功能，包含权限检查
        const success = menuManager.navigateTo(item.path)
        if (!success) {
          uni.showToast({
            title: '页面暂未开放',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('导航错误:', error)
        uni.showToast({
          title: '导航失败',
          icon: 'error'
        })
      }
    },
    
    handleToolClick(tool) {
      this.handleNavClick(tool)
      this.hideMoreMenu()
    },
    
    toggleMoreMenu() {
      this.showMoreMenu = !this.showMoreMenu
    },
    
    hideMoreMenu() {
      this.showMoreMenu = false
    }
  }
}
</script>

<style lang="scss" scoped>
.bottom-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #fff;
  border-top: 1px solid #eee;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.nav-container {
  display: flex;
  height: 60px;
  align-items: center;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:active {
    background-color: #f5f5f5;
  }
  
  &.nav-item-active {
    .nav-label {
      color: #007aff;
    }
  }
}

.nav-icon {
  position: relative;
  margin-bottom: 4px;
}

.icon-text {
  font-size: 20px;
  line-height: 1;
}

.nav-label {
  font-size: 12px;
  color: #666;
  line-height: 1;
}

.badge {
  position: absolute;
  top: -4px;
  right: -8px;
  background: #ff3b30;
  border-radius: 8px;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-text {
  color: #fff;
  font-size: 10px;
  line-height: 1;
}

.more-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 60px;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  
  &.overlay-show {
    opacity: 1;
    visibility: visible;
  }
}

.more-menu {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 12px 12px 0 0;
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
}

.menu-section {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-header {
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.menu-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.menu-grid-item {
  flex: 0 0 calc(25% - 12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:active {
    background-color: #f5f5f5;
  }
}

.grid-icon {
  margin-bottom: 8px;
}

.grid-label {
  font-size: 12px;
  color: #666;
  text-align: center;
  line-height: 1.2;
}
</style>