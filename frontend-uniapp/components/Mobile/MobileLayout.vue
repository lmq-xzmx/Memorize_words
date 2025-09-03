<template>
  <view class="mobile-layout" :class="layoutClasses" :style="layoutStyle">
    <!-- 导航栏 -->
    <MobileNavBar
      v-if="showNavbar"
      ref="navbar"
      :title="navbarTitle"
      :title-color="navbarTitleColor"
      :background-color="navbarBackground"
      :show-back="showBack"
      :back-text="backText"
      :right-icon="rightIcon"
      :right-text="rightText"
      :fixed="navbarFixed"
      :border="navbarBorder"
      :safe-area-inset-top="safeAreaInsetTop"
      :height="navbarHeight"
      :z-index="navbarZIndex"
      @left-click="handleNavbarLeftClick"
      @right-click="handleNavbarRightClick"
      @back="handleNavbarBack"
    >
      <template #left>
        <slot name="navbar-left"></slot>
      </template>
      <template #center>
        <slot name="navbar-center"></slot>
      </template>
      <template #right>
        <slot name="navbar-right"></slot>
      </template>
    </MobileNavBar>
    
    <!-- 主内容区域 -->
    <view class="layout-content" :style="contentStyle">
      <!-- 内容占位 -->
      <view v-if="showNavbar && navbarFixed" class="content-placeholder" :style="placeholderStyle"></view>
      
      <!-- 页面内容 -->
      <view class="content-body" :class="contentClasses">
        <slot></slot>
      </view>
      
      <!-- 底部占位 -->
      <view v-if="showTabbar && tabbarFixed" class="tabbar-placeholder" :style="tabbarPlaceholderStyle"></view>
    </view>
    
    <!-- 底部标签栏 -->
    <MobileTabBar
      v-if="showTabbar"
      ref="tabbar"
      :tabs="tabbarTabs"
      :current="tabbarCurrent"
      :background-color="tabbarBackground"
      :active-color="tabbarActiveColor"
      :inactive-color="tabbarInactiveColor"
      :fixed="tabbarFixed"
      :border="tabbarBorder"
      :safe-area-inset-bottom="safeAreaInsetBottom"
      :height="tabbarHeight"
      :z-index="tabbarZIndex"
      @change="handleTabbarChange"
      @click="handleTabbarClick"
    >
      <template v-for="tab in tabbarTabs" :key="tab.key" #[tab.slot]="slotProps">
        <slot :name="`tabbar-${tab.slot}`" v-bind="slotProps"></slot>
      </template>
    </MobileTabBar>
    
    <!-- 加载遮罩 -->
    <view v-if="loading" class="layout-loading">
      <view class="loading-content">
        <view class="loading-spinner"></view>
        <text v-if="loadingText" class="loading-text">{{ loadingText }}</text>
      </view>
    </view>
    
    <!-- 错误状态 -->
    <view v-if="error" class="layout-error">
      <view class="error-content">
        <text class="error-icon">⚠️</text>
        <text class="error-message">{{ errorMessage || '页面加载失败' }}</text>
        <MobileButton v-if="showRetry" type="primary" size="small" @click="handleRetry">
          重试
        </MobileButton>
      </view>
    </view>
  </view>
</template>

<script>
import MobileNavBar from './MobileNavBar.vue'
import MobileTabBar from './MobileTabBar.vue'
import MobileButton from './MobileButton.vue'

export default {
  name: 'MobileLayout',
  components: {
    MobileNavBar,
    MobileTabBar,
    MobileButton
  },
  props: {
    // 布局配置
    backgroundColor: {
      type: String,
      default: ''
    },
    
    // 导航栏配置
    showNavbar: {
      type: Boolean,
      default: true
    },
    navbarTitle: {
      type: String,
      default: ''
    },
    navbarTitleColor: {
      type: String,
      default: ''
    },
    navbarBackground: {
      type: String,
      default: ''
    },
    showBack: {
      type: Boolean,
      default: true
    },
    backText: {
      type: String,
      default: ''
    },
    rightIcon: {
      type: String,
      default: ''
    },
    rightText: {
      type: String,
      default: ''
    },
    navbarFixed: {
      type: Boolean,
      default: true
    },
    navbarBorder: {
      type: Boolean,
      default: true
    },
    navbarHeight: {
      type: Number,
      default: 44
    },
    navbarZIndex: {
      type: Number,
      default: 999
    },
    
    // 标签栏配置
    showTabbar: {
      type: Boolean,
      default: false
    },
    tabbarTabs: {
      type: Array,
      default: () => []
    },
    tabbarCurrent: {
      type: Number,
      default: 0
    },
    tabbarBackground: {
      type: String,
      default: ''
    },
    tabbarActiveColor: {
      type: String,
      default: ''
    },
    tabbarInactiveColor: {
      type: String,
      default: ''
    },
    tabbarFixed: {
      type: Boolean,
      default: true
    },
    tabbarBorder: {
      type: Boolean,
      default: true
    },
    tabbarHeight: {
      type: Number,
      default: 50
    },
    tabbarZIndex: {
      type: Number,
      default: 998
    },
    
    // 安全区域
    safeAreaInsetTop: {
      type: Boolean,
      default: true
    },
    safeAreaInsetBottom: {
      type: Boolean,
      default: true
    },
    
    // 内容配置
    contentPadding: {
      type: String,
      default: ''
    },
    contentBackground: {
      type: String,
      default: ''
    },
    
    // 状态配置
    loading: {
      type: Boolean,
      default: false
    },
    loadingText: {
      type: String,
      default: ''
    },
    error: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: ''
    },
    showRetry: {
      type: Boolean,
      default: true
    }
  },
  emits: [
    'navbar-left-click', 'navbar-right-click', 'navbar-back',
    'tabbar-change', 'tabbar-click', 'retry'
  ],
  data() {
    return {
      statusBarHeight: 0
    }
  },
  computed: {
    layoutClasses() {
      return {
        'layout-navbar': this.showNavbar,
        'layout-tabbar': this.showTabbar,
        'layout-loading': this.loading,
        'layout-error': this.error
      }
    },
    
    layoutStyle() {
      return {
        backgroundColor: this.backgroundColor || 'var(--background-color)'
      }
    },
    
    contentStyle() {
      return {
        backgroundColor: this.contentBackground || 'transparent',
        padding: this.contentPadding
      }
    },
    
    contentClasses() {
      return {
        'content-safe-top': this.safeAreaInsetTop && this.showNavbar,
        'content-safe-bottom': this.safeAreaInsetBottom && this.showTabbar
      }
    },
    
    placeholderStyle() {
      const height = this.getNavbarTotalHeight()
      return {
        height: height + 'px'
      }
    },
    
    tabbarPlaceholderStyle() {
      const height = this.getTabbarTotalHeight()
      return {
        height: height + 'px'
      }
    }
  },
  mounted() {
    this.getSystemInfo()
  },
  methods: {
    // 获取系统信息
    getSystemInfo() {
      try {
        const systemInfo = uni.getSystemInfoSync()
        this.statusBarHeight = systemInfo.statusBarHeight || 0
      } catch (e) {
        console.warn('获取系统信息失败:', e)
        this.statusBarHeight = 20
      }
    },
    
    // 获取导航栏总高度
    getNavbarTotalHeight() {
      return (this.safeAreaInsetTop ? this.statusBarHeight : 0) + this.navbarHeight
    },
    
    // 获取标签栏总高度
    getTabbarTotalHeight() {
      // 这里需要考虑安全区域
      return this.tabbarHeight + (this.safeAreaInsetBottom ? 34 : 0) // 34是大概的安全区域高度
    },
    
    // 导航栏事件处理
    handleNavbarLeftClick() {
      this.$emit('navbar-left-click')
    },
    
    handleNavbarRightClick() {
      this.$emit('navbar-right-click')
    },
    
    handleNavbarBack() {
      this.$emit('navbar-back')
    },
    
    // 标签栏事件处理
    handleTabbarChange(data) {
      this.$emit('tabbar-change', data)
    },
    
    handleTabbarClick(data) {
      this.$emit('tabbar-click', data)
    },
    
    // 重试事件
    handleRetry() {
      this.$emit('retry')
    },
    
    // 设置导航栏标题
    setNavbarTitle(title) {
      this.navbarTitle = title
    },
    
    // 设置标签栏当前项
    setTabbarCurrent(index) {
      if (this.$refs.tabbar) {
        this.$refs.tabbar.setCurrent(index)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-layout {
  position: relative;
  min-height: 100vh;
  background-color: var(--background-color);
  
  &.layout-loading,
  &.layout-error {
    .layout-content {
      pointer-events: none;
    }
  }
}

.layout-content {
  position: relative;
  min-height: 100vh;
  
  .content-placeholder {
    flex-shrink: 0;
  }
  
  .content-body {
    flex: 1;
    position: relative;
  }
  
  .tabbar-placeholder {
    flex-shrink: 0;
  }
}

.layout-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  
  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .loading-spinner {
      width: 32px;
      height: 32px;
      border: 3px solid var(--border-color);
      border-top-color: var(--primary-color);
      border-radius: 50%;
      animation: loading-spin 1s linear infinite;
    }
    
    .loading-text {
      margin-top: var(--spacing-md);
      font-size: 14px;
      color: var(--text-secondary);
    }
  }
}

.layout-error {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  
  .error-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--spacing-xl);
    
    .error-icon {
      font-size: 48px;
      margin-bottom: var(--spacing-md);
    }
    
    .error-message {
      font-size: 16px;
      color: var(--text-secondary);
      text-align: center;
      margin-bottom: var(--spacing-lg);
      line-height: 1.5;
    }
  }
}

/* 动画 */
@keyframes loading-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .mobile-layout {
    background-color: var(--background-color-dark);
  }
  
  .layout-loading {
    background-color: rgba(0, 0, 0, 0.8);
    
    .loading-spinner {
      border-color: var(--border-color-dark);
      border-top-color: var(--primary-color);
    }
    
    .loading-text {
      color: var(--text-secondary-dark);
    }
  }
  
  .layout-error {
    background-color: rgba(0, 0, 0, 0.9);
    
    .error-message {
      color: var(--text-secondary-dark);
    }
  }
}

/* 响应式适配 */
@media screen and (max-width: 480px) {
  .layout-loading .loading-content {
    .loading-spinner {
      width: 28px;
      height: 28px;
    }
    
    .loading-text {
      font-size: 12px;
    }
  }
  
  .layout-error .error-content {
    padding: var(--spacing-lg);
    
    .error-icon {
      font-size: 40px;
    }
    
    .error-message {
      font-size: 14px;
    }
  }
}
</style>