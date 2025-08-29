<template>
  <view class="menu-demo-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">菜单系统演示</text>
      <button class="toggle-btn" @tap="toggleMenuType">{{ menuType === 'dynamic' ? '切换到底部导航' : '切换到动态菜单' }}</button>
    </view>
    
    <!-- 用户信息 -->
    <view class="user-section">
      <view class="user-info">
        <text class="info-label">当前用户:</text>
        <text class="info-value">{{ userInfo?.username || '未登录' }}</text>
      </view>
      <view class="user-info">
        <text class="info-label">用户角色:</text>
        <text class="info-value">{{ getRoleDisplayName(userInfo?.role) }}</text>
      </view>
      <view class="user-info">
        <text class="info-label">认证状态:</text>
        <text class="info-value" :class="{ 'status-success': isAuthenticated, 'status-error': !isAuthenticated }">
          {{ isAuthenticated ? '已认证' : '未认证' }}
        </text>
      </view>
    </view>
    
    <!-- 权限测试 -->
    <view class="permission-section">
      <view class="section-title">
        <text>权限测试</text>
      </view>
      
      <view class="permission-list">
        <view 
          v-for="permission in testPermissions" 
          :key="permission.key"
          class="permission-item"
        >
          <text class="permission-name">{{ permission.name }}</text>
          <view class="permission-status">
            <text 
              class="status-text" 
              :class="{ 'status-success': hasPermission(permission.key), 'status-error': !hasPermission(permission.key) }"
            >
              {{ hasPermission(permission.key) ? '✓ 有权限' : '✗ 无权限' }}
            </text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 菜单数据展示 -->
    <view class="menu-data-section">
      <view class="section-title">
        <text>菜单数据</text>
        <button class="refresh-btn" @tap="refreshMenuData">刷新</button>
      </view>
      
      <view class="menu-tabs">
        <view 
          v-for="tab in menuTabs" 
          :key="tab.key"
          class="menu-tab"
          :class="{ 'tab-active': activeTab === tab.key }"
          @tap="switchTab(tab.key)"
        >
          <text class="tab-text">{{ tab.name }}</text>
        </view>
      </view>
      
      <scroll-view class="menu-content" scroll-y="true">
        <view class="menu-items">
          <view 
            v-for="(item, index) in currentMenuData" 
            :key="index"
            class="menu-item-card"
            @tap="handleMenuItemClick(item)"
          >
            <view class="item-header">
              <text class="item-icon">{{ getIconText(item.icon) }}</text>
              <text class="item-title">{{ item.title }}</text>
              <view class="item-badge" v-if="item.badge">
                <text class="badge-text">{{ item.badge }}</text>
              </view>
            </view>
            
            <view class="item-details">
              <text class="item-path">路径: {{ item.path || '无' }}</text>
              <text class="item-permission">权限: {{ item.permission || '无' }}</text>
              <text class="item-category">分类: {{ item.category || '无' }}</text>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <!-- 菜单组件展示 -->
    <view class="menu-component-section" v-if="menuType === 'dynamic'">
      <view class="section-title">
        <text>动态菜单组件</text>
      </view>
      
      <view class="menu-container">
        <DynamicMenu 
          :collapsed="menuCollapsed"
          @toggle="handleMenuToggle"
          @menu-click="handleMenuClick"
          @dev-tool-click="handleDevToolClick"
        />
      </view>
    </view>
    
    <!-- 底部导航组件 -->
    <BottomNavigation 
      v-if="menuType === 'bottom'"
      @nav-click="handleNavClick"
      @tool-click="handleToolClick"
      @fashion-click="handleFashionClick"
      @dev-click="handleDevClick"
    />
  </view>
</template>

<script>
import menuManager from '@/utils/menuManager.js'
import { ROLE_DISPLAY_NAMES } from '@/config/menuConfig.js'
import DynamicMenu from '@/components/DynamicMenu.vue'
import BottomNavigation from '@/components/BottomNavigation.vue'

export default {
  name: 'MenuDemo',
  components: {
    DynamicMenu,
    BottomNavigation
  },
  data() {
    return {
      menuType: 'dynamic', // 'dynamic' | 'bottom'
      menuCollapsed: false,
      activeTab: 'main',
      userInfo: null,
      isAuthenticated: false,
      testPermissions: [
        { key: 'word-slash', name: '单词学习' },
        { key: 'tools', name: '工具权限' },
        { key: 'fashion', name: '时尚权限' },
        { key: 'dev', name: '开发权限' },
        { key: 'admin', name: '管理员权限' },
        { key: 'resource-auth', name: '资源授权' }
      ],
      menuTabs: [
        { key: 'main', name: '主菜单' },
        { key: 'bottom', name: '底部导航' },
        { key: 'tool', name: '工具菜单' }
      ],
      menuData: {
        main: [],
        bottom: [],
        tool: []
      }
    }
  },
  computed: {
    currentMenuData() {
      return this.menuData[this.activeTab] || []
    }
  },
  onLoad() {
    this.loadUserInfo()
    this.loadMenuData()
  },
  methods: {
    /**
     * 加载用户信息
     */
    loadUserInfo() {
      this.userInfo = menuManager.getCurrentUser()
      this.isAuthenticated = menuManager.isAuthenticated()
      
      // 如果没有用户信息，创建一个测试用户
      if (!this.userInfo) {
        this.createTestUser()
      }
    },
    
    /**
     * 创建测试用户
     */
    createTestUser() {
      const testUser = {
        id: 1,
        username: 'test_user',
        nickname: '测试用户',
        role: 'student',
        avatar: '/static/images/default-avatar.png'
      }
      
      try {
        uni.setStorageSync('user_info', testUser)
        uni.setStorageSync('access_token', 'test_token_123')
        this.userInfo = testUser
        this.isAuthenticated = true
        
        uni.showToast({
          title: '已创建测试用户',
          icon: 'success'
        })
      } catch (e) {
        console.error('创建测试用户失败:', e)
      }
    },
    
    /**
     * 加载菜单数据
     */
    loadMenuData() {
      this.menuData.main = menuManager.getMainMenus()
      this.menuData.bottom = menuManager.getBottomMenus()
      this.menuData.tool = menuManager.getToolMenus()
    },
    
    /**
     * 刷新菜单数据
     */
    refreshMenuData() {
      menuManager.refreshMenus()
      this.loadMenuData()
      
      uni.showToast({
        title: '菜单数据已刷新',
        icon: 'success'
      })
    },
    
    /**
     * 切换菜单类型
     */
    toggleMenuType() {
      this.menuType = this.menuType === 'dynamic' ? 'bottom' : 'dynamic'
    },
    
    /**
     * 切换标签页
     */
    switchTab(tabKey) {
      this.activeTab = tabKey
    },
    
    /**
     * 检查权限
     */
    hasPermission(permission) {
      return this.$hasPermission(permission)
    },
    
    /**
     * 获取角色显示名称
     */
    getRoleDisplayName(role) {
      return ROLE_DISPLAY_NAMES[role] || role || '未知'
    },
    
    /**
     * 获取图标文本
     */
    getIconText(iconName) {
      const iconMap = {
        'home': '🏠',
        'word-slash': '📚',
        'tools': '🔧',
        'fashion': '👗',
        'profile': '👤',
        'settings': '⚙️',
        'dev': '💻',
        'resource-auth': '🔐'
      }
      
      return iconMap[iconName] || '📄'
    },
    
    /**
     * 处理菜单项点击
     */
    handleMenuItemClick(item) {
      if (item.path) {
        uni.showModal({
          title: '菜单点击',
          content: `点击了菜单: ${item.title}\n路径: ${item.path}`,
          showCancel: true,
          confirmText: '跳转',
          success: (res) => {
            if (res.confirm) {
              menuManager.navigateTo(item.path)
            }
          }
        })
      } else {
        uni.showToast({
          title: `点击了: ${item.title}`,
          icon: 'none'
        })
      }
    },
    
    /**
     * 处理动态菜单事件
     */
    handleMenuToggle(collapsed) {
      this.menuCollapsed = collapsed
    },
    
    handleMenuClick(menu) {
      console.log('动态菜单点击:', menu)
      this.showMenuClickToast(menu.title)
    },
    
    handleDevToolClick(tool) {
      console.log('开发工具点击:', tool)
      this.showMenuClickToast(`开发工具: ${tool.title}`)
    },
    
    /**
     * 处理底部导航事件
     */
    handleNavClick(nav) {
      console.log('底部导航点击:', nav)
      this.showMenuClickToast(nav.title)
    },
    
    handleToolClick(tool) {
      console.log('工具点击:', tool)
      this.showMenuClickToast(`工具: ${tool.title}`)
    },
    
    handleFashionClick(fashion) {
      console.log('时尚菜单点击:', fashion)
      this.showMenuClickToast(`时尚: ${fashion.title}`)
    },
    
    handleDevClick(dev) {
      console.log('开发工具点击:', dev)
      this.showMenuClickToast(`开发: ${dev.title}`)
    },
    
    /**
     * 显示菜单点击提示
     */
    showMenuClickToast(title) {
      uni.showToast({
        title: `点击了: ${title}`,
        icon: 'none',
        duration: 1500
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.menu-demo-page {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
  }
  
  .toggle-btn {
    background: #007AFF;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
  }
}

.user-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  
  .user-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .info-label {
      font-size: 14px;
      color: #666;
    }
    
    .info-value {
      font-size: 14px;
      color: #333;
      font-weight: 500;
      
      &.status-success {
        color: #28a745;
      }
      
      &.status-error {
        color: #dc3545;
      }
    }
  }
}

.permission-section,
.menu-data-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  text {
    font-size: 16px;
    font-weight: 600;
    color: #333;
  }
  
  .refresh-btn {
    background: #28a745;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
  }
}

.permission-list {
  .permission-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .permission-name {
      font-size: 14px;
      color: #333;
    }
    
    .status-text {
      font-size: 12px;
      font-weight: 500;
      
      &.status-success {
        color: #28a745;
      }
      
      &.status-error {
        color: #dc3545;
      }
    }
  }
}

.menu-tabs {
  display: flex;
  margin-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
  
  .menu-tab {
    flex: 1;
    text-align: center;
    padding: 12px;
    cursor: pointer;
    
    .tab-text {
      font-size: 14px;
      color: #666;
    }
    
    &.tab-active {
      border-bottom: 2px solid #007AFF;
      
      .tab-text {
        color: #007AFF;
        font-weight: 500;
      }
    }
  }
}

.menu-content {
  max-height: 300px;
}

.menu-items {
  .menu-item-card {
    background: #f8f9fa;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 8px;
    cursor: pointer;
    
    &:active {
      background: #e9ecef;
    }
    
    .item-header {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      
      .item-icon {
        font-size: 16px;
        margin-right: 8px;
      }
      
      .item-title {
        flex: 1;
        font-size: 14px;
        font-weight: 500;
        color: #333;
      }
      
      .item-badge {
        .badge-text {
          background: #ff4757;
          color: white;
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 10px;
        }
      }
    }
    
    .item-details {
      display: flex;
      flex-direction: column;
      
      text {
        font-size: 12px;
        color: #666;
        margin-bottom: 2px;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
}

.menu-component-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  
  .menu-container {
    height: 400px;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    overflow: hidden;
  }
}
</style>