<template>
  <view class="top-menu" v-if="shouldShowMenu">
    <!-- 主菜单栏 -->
    <view class="menu-bar">
      <!-- 底部导航菜单 -->
      <view class="bottom-menus">
        <view 
          v-for="menu in visibleBottomMenus" 
          :key="menu.id"
          class="menu-item"
          :class="{ active: currentPath === menu.path }"
          @click="handleMenuClick(menu)"
        >
          <text class="menu-icon">{{ menu.icon }}</text>
          <text class="menu-title">{{ menu.title }}</text>
          <text v-if="menu.isDropdown" class="dropdown-arrow">▼</text>
        </view>
      </view>
    </view>
    
    <!-- 下拉菜单 -->
    <view v-if="showDropdown" class="dropdown-menu" @click="closeDropdown">
      <view class="dropdown-content" @click.stop>
        <!-- 工具菜单 -->
        <view v-if="activeDropdown === 'tools'" class="dropdown-section">
          <view class="section-title">🔧 工具菜单</view>
          <view 
            v-for="tool in visibleToolMenus" 
            :key="tool.id"
            class="dropdown-item"
            @click="handleToolClick(tool)"
          >
            <text class="item-icon">{{ tool.icon }}</text>
            <text class="item-title">{{ tool.title }}</text>
            <text v-if="tool.isExpandable" class="expand-arrow">▶</text>
          </view>
          
          <!-- 开发工具子菜单 -->
          <view v-if="showDevTools" class="sub-menu">
            <view class="sub-title">🛠️ 开发工具</view>
            <view 
              v-for="devTool in visibleDevTools" 
              :key="devTool.id"
              class="sub-item"
              :class="{ disabled: !devTool.enabled }"
              @click="handleDevToolClick(devTool)"
            >
              <text class="item-icon">{{ devTool.icon }}</text>
              <text class="item-title">{{ devTool.title }}</text>
              <text v-if="!devTool.enabled" class="status-badge">未启用</text>
            </view>
          </view>
        </view>
        
        <!-- 时尚菜单 -->
        <view v-if="activeDropdown === 'fashion'" class="dropdown-section">
          <view class="section-title">✨ 时尚菜单</view>
          <view 
            v-for="fashion in visibleFashionMenus" 
            :key="fashion.id"
            class="dropdown-item"
            @click="handleFashionClick(fashion)"
          >
            <text class="item-icon">{{ fashion.icon }}</text>
            <text class="item-title">{{ fashion.title }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { MENU_ITEMS, hasPermission, getCurrentUserRole } from '@/config/menuConfig.js'

export default {
  name: 'TopMenu',
  data() {
    return {
      currentPath: '',
      showDropdown: false,
      activeDropdown: '',
      showDevTools: false,
      userRole: 'student' // 默认角色
    }
  },
  computed: {
    shouldShowMenu() {
      // 在所有页面都显示菜单
      return true
    },
    visibleBottomMenus() {
      return MENU_ITEMS.BOTTOM_MENUS.filter(menu => 
        hasPermission(menu.permission, this.userRole)
      )
    },
    visibleToolMenus() {
      return MENU_ITEMS.TOOL_MENUS.filter(menu => 
        hasPermission(menu.permission, this.userRole)
      )
    },
    visibleDevTools() {
      return MENU_ITEMS.DEV_TOOLS.filter(tool => 
        hasPermission(tool.permission, this.userRole)
      )
    },
    visibleFashionMenus() {
      return MENU_ITEMS.FASHION_MENUS.filter(menu => 
        hasPermission(menu.permission, this.userRole)
      )
    }
  },
  mounted() {
    this.updateCurrentPath()
    this.userRole = getCurrentUserRole()
  },
  methods: {
    updateCurrentPath() {
      // 获取当前页面路径
      const pages = getCurrentPages()
      if (pages.length > 0) {
        const currentPage = pages[pages.length - 1]
        this.currentPath = '/' + currentPage.route
      }
    },
    handleMenuClick(menu) {
      if (menu.isDropdown) {
        this.toggleDropdown(menu.id)
      } else if (menu.path) {
        this.navigateTo(menu.path)
      }
    },
    toggleDropdown(menuId) {
      if (this.activeDropdown === menuId && this.showDropdown) {
        this.closeDropdown()
      } else {
        this.activeDropdown = menuId
        this.showDropdown = true
        this.showDevTools = false
      }
    },
    closeDropdown() {
      this.showDropdown = false
      this.activeDropdown = ''
      this.showDevTools = false
    },
    handleToolClick(tool) {
      if (tool.isExpandable) {
        this.showDevTools = !this.showDevTools
      } else if (tool.path) {
        this.navigateTo(tool.path)
        this.closeDropdown()
      }
    },
    handleDevToolClick(devTool) {
      if (devTool.enabled && devTool.path) {
        this.navigateTo(devTool.path)
        this.closeDropdown()
      }
    },
    handleFashionClick(fashion) {
      if (fashion.path) {
        this.navigateTo(fashion.path)
        this.closeDropdown()
      }
    },
    navigateTo(path) {
      uni.navigateTo({
        url: path,
        fail: () => {
          // 如果navigateTo失败，尝试switchTab
          uni.switchTab({
            url: path,
            fail: () => {
              console.error('导航失败:', path)
            }
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.top-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.menu-bar {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bottom-menus {
  display: flex;
  flex: 1;
  justify-content: space-around;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1);
}

.menu-item.active {
  background: rgba(255,255,255,0.2);
}

.menu-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.menu-title {
  font-size: 12px;
  color: #fff;
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 10px;
  color: #fff;
  margin-top: 2px;
}

.dropdown-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 10000;
}

.dropdown-content {
  background: #fff;
  margin: 80px 20px 0;
  border-radius: 12px;
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.dropdown-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.item-icon {
  font-size: 18px;
  margin-right: 12px;
}

.item-title {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.expand-arrow {
  font-size: 12px;
  color: #666;
}

.sub-menu {
  margin-left: 20px;
  margin-top: 10px;
  padding-left: 15px;
  border-left: 2px solid #e9ecef;
}

.sub-title {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 10px;
}

.sub-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 6px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.sub-item:hover:not(.disabled) {
  background: #f1f3f4;
}

.sub-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-badge {
  background: #ffc107;
  color: #fff;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}
</style>