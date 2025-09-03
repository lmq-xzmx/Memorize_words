<template>
  <view class="mobile-tabbar" :class="tabbarClasses" :style="tabbarStyle">
    <!-- 标签项 -->
    <view 
      v-for="(item, index) in tabs" 
      :key="item.key || index"
      class="tabbar-item" 
      :class="{ 'tabbar-item-active': currentIndex === index }"
      @tap="handleTabClick(item, index)"
    >
      <!-- 图标 -->
      <view class="tabbar-icon">
        <!-- 自定义图标 -->
        <slot v-if="item.slot" :name="item.slot" :item="item" :active="currentIndex === index"></slot>
        
        <!-- 默认图标 -->
        <template v-else>
          <text 
            v-if="item.icon" 
            class="iconfont" 
            :class="currentIndex === index ? (item.activeIcon || item.icon) : item.icon"
          ></text>
          
          <!-- 徽章 -->
          <view v-if="item.badge" class="tabbar-badge" :class="badgeClasses(item.badge)">
            <text v-if="typeof item.badge === 'string' || typeof item.badge === 'number'" class="badge-text">
              {{ item.badge }}
            </text>
          </view>
        </template>
      </view>
      
      <!-- 文本 -->
      <text v-if="item.text" class="tabbar-text" :style="getTextStyle(index)">
        {{ item.text }}
      </text>
    </view>
    
    <!-- 安全区域占位 -->
    <view v-if="safeAreaInsetBottom" class="tabbar-safe-area"></view>
  </view>
</template>

<script>
export default {
  name: 'MobileTabBar',
  props: {
    // 标签数据
    tabs: {
      type: Array,
      default: () => [],
      validator: (tabs) => {
        return tabs.every(tab => tab.text || tab.icon || tab.slot)
      }
    },
    // 当前激活索引
    current: {
      type: Number,
      default: 0
    },
    // 背景色
    backgroundColor: {
      type: String,
      default: ''
    },
    // 激活颜色
    activeColor: {
      type: String,
      default: ''
    },
    // 默认颜色
    inactiveColor: {
      type: String,
      default: ''
    },
    // 是否固定在底部
    fixed: {
      type: Boolean,
      default: true
    },
    // 是否显示顶部边框
    border: {
      type: Boolean,
      default: true
    },
    // 是否适配安全区域
    safeAreaInsetBottom: {
      type: Boolean,
      default: true
    },
    // 高度
    height: {
      type: Number,
      default: 50
    },
    // z-index层级
    zIndex: {
      type: Number,
      default: 998
    }
  },
  emits: ['change', 'click'],
  data() {
    return {
      currentIndex: 0
    }
  },
  computed: {
    tabbarClasses() {
      return {
        'tabbar-fixed': this.fixed,
        'tabbar-border': this.border,
        'tabbar-safe': this.safeAreaInsetBottom
      }
    },
    
    tabbarStyle() {
      return {
        backgroundColor: this.backgroundColor || 'var(--card-background)',
        height: this.height + 'px',
        zIndex: this.zIndex
      }
    }
  },
  watch: {
    current: {
      handler(newVal) {
        this.currentIndex = newVal
      },
      immediate: true
    }
  },
  methods: {
    // 标签点击事件
    handleTabClick(item, index) {
      if (this.currentIndex === index) {
        return
      }
      
      this.currentIndex = index
      this.$emit('change', { item, index })
      this.$emit('click', { item, index })
      
      // 如果有路径，进行页面跳转
      if (item.pagePath) {
        this.switchTab(item.pagePath)
      }
    },
    
    // 切换标签页
    switchTab(url) {
      uni.switchTab({
        url,
        fail: (err) => {
          console.warn('切换标签页失败:', err)
          // 如果switchTab失败，尝试使用navigateTo
          uni.navigateTo({
            url,
            fail: (navErr) => {
              console.error('页面跳转失败:', navErr)
            }
          })
        }
      })
    },
    
    // 获取文本样式
    getTextStyle(index) {
      const isActive = this.currentIndex === index
      return {
        color: isActive 
          ? (this.activeColor || 'var(--primary-color)') 
          : (this.inactiveColor || 'var(--text-secondary)')
      }
    },
    
    // 获取徽章样式类
    badgeClasses(badge) {
      if (typeof badge === 'object') {
        return {
          'badge-dot': badge.dot,
          'badge-number': !badge.dot && (badge.count || badge.text)
        }
      }
      return {
        'badge-number': true
      }
    },
    
    // 设置当前激活项
    setCurrent(index) {
      if (index >= 0 && index < this.tabs.length) {
        this.currentIndex = index
      }
    },
    
    // 获取当前激活项
    getCurrent() {
      return this.currentIndex
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-tabbar {
  display: flex;
  align-items: center;
  background-color: var(--card-background);
  position: relative;
  
  &.tabbar-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
  }
  
  &.tabbar-border::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background-color: var(--border-color);
    transform: scaleY(0.5);
  }
  
  &.tabbar-safe {
    padding-bottom: env(safe-area-inset-bottom);
  }
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xs) var(--spacing-xs);
  transition: all 0.2s ease;
  
  &:active {
    opacity: 0.7;
  }
  
  &.tabbar-item-active {
    .tabbar-icon .iconfont {
      color: var(--primary-color);
    }
    
    .tabbar-text {
      color: var(--primary-color);
    }
  }
}

.tabbar-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-xs);
  
  .iconfont {
    font-size: 22px;
    color: var(--text-secondary);
    transition: color 0.2s ease;
  }
  
  .tabbar-badge {
    position: absolute;
    top: -6px;
    right: -6px;
    
    &.badge-dot {
      width: 8px;
      height: 8px;
      background-color: var(--error-color);
      border-radius: 50%;
    }
    
    &.badge-number {
      min-width: 16px;
      height: 16px;
      background-color: var(--error-color);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 4px;
      
      .badge-text {
        font-size: 10px;
        color: #fff;
        line-height: 1;
        transform: scale(0.8);
      }
    }
  }
}

.tabbar-text {
  font-size: 10px;
  color: var(--text-secondary);
  line-height: 1.2;
  text-align: center;
  transition: color 0.2s ease;
  transform: scale(0.9);
}

.tabbar-safe-area {
  height: env(safe-area-inset-bottom);
  background-color: inherit;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .mobile-tabbar {
    background-color: var(--card-background-dark);
    
    &.tabbar-border::before {
      background-color: var(--border-color-dark);
    }
    
    .tabbar-item {
      .tabbar-icon .iconfont {
        color: var(--text-secondary-dark);
      }
      
      .tabbar-text {
        color: var(--text-secondary-dark);
      }
      
      &.tabbar-item-active {
        .tabbar-icon .iconfont,
        .tabbar-text {
          color: var(--primary-color);
        }
      }
    }
  }
}

/* 响应式适配 */
@media screen and (max-width: 480px) {
  .tabbar-item {
    padding: var(--spacing-xs) 2px;
    
    .tabbar-icon .iconfont {
      font-size: 20px;
    }
    
    .tabbar-text {
      font-size: 9px;
    }
  }
}

/* 动画效果 */
@keyframes tabbar-bounce {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.tabbar-item.tabbar-item-active .tabbar-icon {
  animation: tabbar-bounce 0.3s ease;
}
</style>