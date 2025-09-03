<template>
  <view class="base-layout">
    <!-- 页面头部 -->
    <view class="layout-header" v-if="showHeader">
      <slot name="header">
        <view class="default-header">
          <text class="header-title">{{ title }}</text>
        </view>
      </slot>
    </view>
    
    <!-- 页面内容区域 -->
    <view class="layout-content" :class="contentClass">
      <!-- 侧边栏菜单 -->
      <view class="layout-sidebar" v-if="showSidebar">
        <DynamicMenu 
          type="sidebar" 
          :role="currentRole"
          @menu-click="handleMenuClick"
        />
      </view>
      
      <!-- 主要内容 -->
      <view class="layout-main" :class="mainClass">
        <slot></slot>
      </view>
    </view>
    
    <!-- 底部导航 -->
    <view class="layout-footer" v-if="showTabBar">
      <DynamicMenu 
        type="tabbar" 
        :role="currentRole"
        @menu-click="handleMenuClick"
      />
    </view>
    
    <!-- 菜单管理器 -->
    <MenuManager ref="menuManager" />
  </view>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'BaseLayout',
  props: {
    // 页面标题
    title: {
      type: String,
      default: '英语学习'
    },
    // 是否显示头部
    showHeader: {
      type: Boolean,
      default: true
    },
    // 是否显示侧边栏
    showSidebar: {
      type: Boolean,
      default: false
    },
    // 是否显示底部导航
    showTabBar: {
      type: Boolean,
      default: true
    },
    // 布局类型
    layoutType: {
      type: String,
      default: 'default', // default, sidebar, fullscreen
      validator: value => ['default', 'sidebar', 'fullscreen'].includes(value)
    }
  },
  
  computed: {
    ...mapState('permission', ['currentRole']),
    
    // 内容区域样式类
    contentClass() {
      return {
        'has-sidebar': this.showSidebar,
        'has-tabbar': this.showTabBar,
        'fullscreen': this.layoutType === 'fullscreen'
      }
    },
    
    // 主要内容区域样式类
    mainClass() {
      return {
        'with-sidebar': this.showSidebar
      }
    }
  },
  
  methods: {
    ...mapActions('permission', ['checkMenuPermission']),
    
    // 处理菜单点击
    async handleMenuClick(menuItem) {
      try {
        // 检查菜单权限
        const hasPermission = await this.checkMenuPermission({
          menuId: menuItem.id,
          userId: this.$store.state.user?.id
        })
        
        if (!hasPermission) {
          uni.showToast({
            title: '没有访问权限',
            icon: 'none'
          })
          return
        }
        
        // 触发菜单点击事件
        this.$emit('menu-click', menuItem)
        
        // 页面导航
        if (menuItem.path) {
          this.navigateToPage(menuItem)
        }
      } catch (error) {
        console.error('菜单点击处理失败:', error)
        uni.showToast({
          title: '操作失败',
          icon: 'none'
        })
      }
    },
    
    // 页面导航
    navigateToPage(menuItem) {
      const { path, isTabBar } = menuItem
      
      if (isTabBar) {
        // TabBar页面使用switchTab
        uni.switchTab({
          url: path,
          fail: (err) => {
            console.error('TabBar导航失败:', err)
          }
        })
      } else {
        // 普通页面使用navigateTo
        uni.navigateTo({
          url: path,
          fail: (err) => {
            console.error('页面导航失败:', err)
            // 如果navigateTo失败，尝试使用redirectTo
            uni.redirectTo({
              url: path,
              fail: (redirectErr) => {
                console.error('页面重定向失败:', redirectErr)
              }
            })
          }
        })
      }
    },
    
    // 刷新菜单
    refreshMenu() {
      if (this.$refs.menuManager) {
        this.$refs.menuManager.refreshMenu()
      }
    },
    
    // 切换角色
    switchRole(role) {
      if (this.$refs.menuManager) {
        this.$refs.menuManager.switchRole(role)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.base-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.layout-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  
  .default-header {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 88rpx;
    padding: 0 32rpx;
    
    .header-title {
      font-size: 36rpx;
      font-weight: 600;
      color: #333;
    }
  }
}

.layout-content {
  flex: 1;
  display: flex;
  margin-top: 88rpx;
  margin-bottom: 0;
  
  &.has-tabbar {
    margin-bottom: 100rpx;
  }
  
  &.fullscreen {
    margin-top: 0;
    margin-bottom: 0;
  }
}

.layout-sidebar {
  width: 200rpx;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
}

.layout-main {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f5f5;
  
  &.with-sidebar {
    margin-left: 0;
  }
}

.layout-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: #fff;
  border-top: 1px solid #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 750rpx) {
  .layout-sidebar {
    width: 160rpx;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .base-layout {
    background-color: #1a1a1a;
  }
  
  .layout-header,
  .layout-sidebar,
  .layout-footer {
    background-color: #2d2d2d;
    border-color: #404040;
  }
  
  .layout-main {
    background-color: #1a1a1a;
  }
  
  .header-title {
    color: #fff;
  }
}
</style>