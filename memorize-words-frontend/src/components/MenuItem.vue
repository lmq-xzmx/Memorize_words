<template>
  <view 
    class="menu-item" 
    :class="{ 
      'menu-item-collapsed': collapsed,
      'menu-item-active': isActive,
      'menu-item-disabled': menu.disabled
    }"
    @tap="handleClick"
  >
    <!-- 菜单图标 -->
    <view class="menu-icon">
      <text class="icon" v-if="menu.icon">{{ getIconText(menu.icon) }}</text>
      <view class="icon-placeholder" v-else></view>
    </view>
    
    <!-- 菜单标题 -->
    <view class="menu-title" v-if="!collapsed">
      <text class="title-text">{{ menu.title }}</text>
      <text class="subtitle-text" v-if="menu.subtitle">{{ menu.subtitle }}</text>
    </view>
    
    <!-- 菜单徽章 -->
    <view class="menu-badge" v-if="menu.badge && !collapsed">
      <text class="badge-text">{{ menu.badge }}</text>
    </view>
    
    <!-- 箭头指示器 -->
    <view class="menu-arrow" v-if="menu.hasChildren && !collapsed">
      <text class="arrow-icon">▶</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MenuItem',
  props: {
    menu: {
      type: Object,
      required: true
    },
    collapsed: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    isActive() {
      // 检查当前页面是否匹配此菜单项
      const pages = getCurrentPages()
      if (pages.length === 0) return false
      
      const currentPage = pages[pages.length - 1]
      const currentPath = `/${currentPage.route}`
      
      return currentPath === this.menu.path
    }
  },
  methods: {
    handleClick() {
      if (this.menu.disabled) return
      
      this.$emit('click', this.menu)
    },
    
    /**
     * 获取图标文本
     * 这里使用简单的图标映射，实际项目中可以使用图标字体或图片
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
        'resource-auth': '🔐',
        'api': '🔌',
        'monitor': '📊',
        'discover': '🔍',
        'trends': '📈',
        'community': '👥',
        'test': '🧪',
        'performance': '⚡'
      }
      
      return iconMap[iconName] || '📄'
    }
  }
}
</script>

<style lang="scss" scoped>
.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0;
  margin: 0 8px;
  border-radius: 8px;
  
  &:hover {
    background: #f0f0f0;
  }
  
  &:active {
    background: #e0e0e0;
  }
  
  &.menu-item-active {
    background: #e3f2fd;
    color: #1976d2;
    
    .menu-icon .icon {
      color: #1976d2;
    }
  }
  
  &.menu-item-disabled {
    opacity: 0.5;
    cursor: not-allowed;
    
    &:hover {
      background: transparent;
    }
  }
  
  &.menu-item-collapsed {
    justify-content: center;
    padding: 12px 8px;
    
    .menu-icon {
      margin-right: 0;
    }
  }
}

.menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin-right: 12px;
  
  .icon {
    font-size: 18px;
    color: #666;
  }
  
  .icon-placeholder {
    width: 18px;
    height: 18px;
    background: #ddd;
    border-radius: 2px;
  }
}

.menu-title {
  flex: 1;
  display: flex;
  flex-direction: column;
  
  .title-text {
    font-size: 14px;
    color: #333;
    font-weight: 500;
    line-height: 1.4;
  }
  
  .subtitle-text {
    font-size: 12px;
    color: #999;
    margin-top: 2px;
    line-height: 1.3;
  }
}

.menu-badge {
  margin-left: 8px;
  
  .badge-text {
    background: #ff4757;
    color: white;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 16px;
    text-align: center;
    line-height: 1.2;
  }
}

.menu-arrow {
  margin-left: 8px;
  
  .arrow-icon {
    font-size: 10px;
    color: #999;
  }
}

/* 小程序适配 */
/* #ifdef MP */
.menu-item {
  &:hover {
    background: transparent;
  }
  
  &:active {
    background: #f0f0f0;
  }
}
/* #endif */

/* 深色模式适配 */
/* #ifdef H5 */
@media (prefers-color-scheme: dark) {
  .menu-item {
    &:hover {
      background: #2a2a2a;
    }
    
    &:active {
      background: #3a3a3a;
    }
    
    &.menu-item-active {
      background: #1a237e;
      color: #90caf9;
      
      .menu-icon .icon {
        color: #90caf9;
      }
    }
  }
  
  .menu-title .title-text {
    color: #fff;
  }
  
  .menu-title .subtitle-text {
    color: #bbb;
  }
  
  .menu-icon .icon {
    color: #bbb;
  }
  
  .menu-arrow .arrow-icon {
    color: #bbb;
  }
}
/* #endif */
</style>