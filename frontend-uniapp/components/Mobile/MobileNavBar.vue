<template>
  <view class="mobile-navbar" :class="navbarClasses" :style="navbarStyle">
    <!-- 状态栏占位 -->
    <view v-if="safeAreaInsetTop" class="navbar-status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 导航栏内容 -->
    <view class="navbar-content" :style="{ height: navbarHeight + 'px' }">
      <!-- 左侧内容 -->
      <view class="navbar-left" @tap="handleLeftClick">
        <!-- 返回按钮 -->
        <view v-if="showBack" class="navbar-back">
          <text class="iconfont icon-arrow-left"></text>
          <text v-if="backText" class="back-text">{{ backText }}</text>
        </view>
        
        <!-- 自定义左侧内容 -->
        <slot name="left"></slot>
      </view>
      
      <!-- 中间标题 -->
      <view class="navbar-center">
        <!-- 标题文本 -->
        <text v-if="title" class="navbar-title" :style="titleStyle">{{ title }}</text>
        
        <!-- 自定义标题内容 -->
        <slot name="center"></slot>
      </view>
      
      <!-- 右侧内容 -->
      <view class="navbar-right" @tap="handleRightClick">
        <!-- 右侧图标 -->
        <view v-if="rightIcon" class="navbar-icon">
          <text class="iconfont" :class="rightIcon"></text>
        </view>
        
        <!-- 右侧文本 -->
        <text v-if="rightText" class="navbar-text">{{ rightText }}</text>
        
        <!-- 自定义右侧内容 -->
        <slot name="right"></slot>
      </view>
    </view>
    
    <!-- 底部边框 -->
    <view v-if="border" class="navbar-border"></view>
  </view>
</template>

<script>
export default {
  name: 'MobileNavBar',
  props: {
    // 标题
    title: {
      type: String,
      default: ''
    },
    // 标题颜色
    titleColor: {
      type: String,
      default: ''
    },
    // 背景色
    backgroundColor: {
      type: String,
      default: ''
    },
    // 是否显示返回按钮
    showBack: {
      type: Boolean,
      default: true
    },
    // 返回按钮文本
    backText: {
      type: String,
      default: ''
    },
    // 右侧图标
    rightIcon: {
      type: String,
      default: ''
    },
    // 右侧文本
    rightText: {
      type: String,
      default: ''
    },
    // 是否固定在顶部
    fixed: {
      type: Boolean,
      default: true
    },
    // 是否显示底部边框
    border: {
      type: Boolean,
      default: true
    },
    // 是否适配安全区域
    safeAreaInsetTop: {
      type: Boolean,
      default: true
    },
    // 导航栏高度
    height: {
      type: Number,
      default: 44
    },
    // z-index层级
    zIndex: {
      type: Number,
      default: 999
    },
    // 透明度
    opacity: {
      type: Number,
      default: 1
    }
  },
  emits: ['left-click', 'right-click', 'back'],
  data() {
    return {
      statusBarHeight: 0,
      navbarHeight: 44
    }
  },
  computed: {
    navbarClasses() {
      return {
        'navbar-fixed': this.fixed,
        'navbar-border': this.border
      }
    },
    
    navbarStyle() {
      return {
        backgroundColor: this.backgroundColor || 'var(--card-background)',
        zIndex: this.zIndex,
        opacity: this.opacity
      }
    },
    
    titleStyle() {
      return {
        color: this.titleColor || 'var(--text-primary)'
      }
    }
  },
  mounted() {
    this.getSystemInfo()
    this.navbarHeight = this.height
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
    
    // 左侧点击事件
    handleLeftClick() {
      if (this.showBack) {
        this.handleBack()
      }
      this.$emit('left-click')
    },
    
    // 右侧点击事件
    handleRightClick() {
      this.$emit('right-click')
    },
    
    // 返回事件
    handleBack() {
      this.$emit('back')
      
      // 默认返回行为
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack()
      } else {
        uni.switchTab({
          url: '/pages/index/index'
        })
      }
    },
    
    // 获取导航栏总高度
    getNavbarHeight() {
      return (this.safeAreaInsetTop ? this.statusBarHeight : 0) + this.navbarHeight
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-navbar {
  position: relative;
  background-color: var(--card-background);
  
  &.navbar-fixed {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999;
  }
  
  &.navbar-border {
    .navbar-border {
      display: block;
    }
  }
}

.navbar-status-bar {
  background-color: inherit;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-md);
  background-color: inherit;
}

.navbar-left {
  display: flex;
  align-items: center;
  min-width: 60px;
  
  .navbar-back {
    display: flex;
    align-items: center;
    padding: var(--spacing-xs) 0;
    
    .iconfont {
      font-size: 18px;
      color: var(--text-primary);
      margin-right: var(--spacing-xs);
    }
    
    .back-text {
      font-size: 16px;
      color: var(--text-primary);
    }
  }
}

.navbar-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 var(--spacing-md);
  
  .navbar-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  }
}

.navbar-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 60px;
  
  .navbar-icon {
    padding: var(--spacing-xs);
    
    .iconfont {
      font-size: 18px;
      color: var(--text-primary);
    }
  }
  
  .navbar-text {
    font-size: 16px;
    color: var(--primary-color);
    padding: var(--spacing-xs) 0;
  }
}

.navbar-border {
  display: none;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background-color: var(--border-color);
  transform: scaleY(0.5);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .mobile-navbar {
    background-color: var(--card-background-dark);
    
    .navbar-title {
      color: var(--text-primary-dark);
    }
    
    .navbar-back {
      .iconfont,
      .back-text {
        color: var(--text-primary-dark);
      }
    }
    
    .navbar-icon .iconfont {
      color: var(--text-primary-dark);
    }
    
    .navbar-border {
      background-color: var(--border-color-dark);
    }
  }
}

/* 点击态效果 */
.navbar-left,
.navbar-right {
  &:active {
    opacity: 0.7;
  }
}

/* 响应式适配 */
@media screen and (max-width: 480px) {
  .navbar-content {
    padding: 0 var(--spacing-sm);
  }
  
  .navbar-center {
    margin: 0 var(--spacing-sm);
    
    .navbar-title {
      font-size: 16px;
    }
  }
  
  .navbar-left .navbar-back {
    .back-text {
      font-size: 14px;
    }
  }
  
  .navbar-right .navbar-text {
    font-size: 14px;
  }
}
</style>