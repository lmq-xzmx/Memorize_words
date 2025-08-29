<template>
  <view 
    class="dev-tool-item" 
    :class="{ 
      'dev-tool-collapsed': collapsed,
      'dev-tool-active': isActive,
      'dev-tool-disabled': tool.disabled
    }"
    @tap="handleClick"
  >
    <!-- 工具图标 -->
    <view class="tool-icon">
      <text class="icon" v-if="tool.icon">{{ getIconText(tool.icon) }}</text>
      <view class="icon-placeholder" v-else></view>
    </view>
    
    <!-- 工具信息 -->
    <view class="tool-info" v-if="!collapsed">
      <view class="tool-title">
        <text class="title-text">{{ tool.title }}</text>
        <view class="dev-badge" v-if="tool.isDev">
          <text class="badge-text">DEV</text>
        </view>
      </view>
      <text class="description-text" v-if="tool.description">{{ tool.description }}</text>
    </view>
    
    <!-- 状态指示器 -->
    <view class="tool-status" v-if="!collapsed">
      <view 
        class="status-dot" 
        :class="{
          'status-online': tool.status === 'online',
          'status-offline': tool.status === 'offline',
          'status-error': tool.status === 'error'
        }"
      ></view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'DevToolItem',
  props: {
    tool: {
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
      // 检查当前页面是否匹配此工具
      const pages = getCurrentPages()
      if (pages.length === 0) return false
      
      const currentPage = pages[pages.length - 1]
      const currentPath = `/${currentPage.route}`
      
      return currentPath === this.tool.path
    }
  },
  methods: {
    handleClick() {
      if (this.tool.disabled) return
      
      // 开发工具可能需要特殊处理
      if (this.tool.requiresConfirm) {
        uni.showModal({
          title: '确认操作',
          content: `确定要打开 ${this.tool.title} 吗？`,
          success: (res) => {
            if (res.confirm) {
              this.$emit('click', this.tool)
            }
          }
        })
      } else {
        this.$emit('click', this.tool)
      }
    },
    
    /**
     * 获取图标文本
     */
    getIconText(iconName) {
      const iconMap = {
        'api': '🔌',
        'monitor': '📊',
        'test': '🧪',
        'performance': '⚡',
        'debug': '🐛',
        'console': '💻',
        'network': '🌐',
        'storage': '💾',
        'cache': '🗄️',
        'log': '📝',
        'analytics': '📈',
        'security': '🔒'
      }
      
      return iconMap[iconName] || '🔧'
    }
  }
}
</script>

<style lang="scss" scoped>
.dev-tool-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0;
  margin: 0 8px;
  border-radius: 6px;
  border-left: 3px solid transparent;
  
  &:hover {
    background: #f8f9fa;
    border-left-color: #007AFF;
  }
  
  &:active {
    background: #e9ecef;
  }
  
  &.dev-tool-active {
    background: #fff3cd;
    border-left-color: #ffc107;
    
    .tool-icon .icon {
      color: #856404;
    }
    
    .tool-title .title-text {
      color: #856404;
    }
  }
  
  &.dev-tool-disabled {
    opacity: 0.5;
    cursor: not-allowed;
    
    &:hover {
      background: transparent;
      border-left-color: transparent;
    }
  }
  
  &.dev-tool-collapsed {
    justify-content: center;
    padding: 10px 8px;
    
    .tool-icon {
      margin-right: 0;
    }
  }
}

.tool-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 12px;
  
  .icon {
    font-size: 16px;
    color: #666;
  }
  
  .icon-placeholder {
    width: 16px;
    height: 16px;
    background: #ddd;
    border-radius: 2px;
  }
}

.tool-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  
  .tool-title {
    display: flex;
    align-items: center;
    margin-bottom: 2px;
    
    .title-text {
      font-size: 13px;
      color: #333;
      font-weight: 500;
      line-height: 1.4;
    }
    
    .dev-badge {
      margin-left: 6px;
      
      .badge-text {
        background: #28a745;
        color: white;
        font-size: 8px;
        padding: 1px 4px;
        border-radius: 2px;
        font-weight: 600;
        letter-spacing: 0.5px;
      }
    }
  }
  
  .description-text {
    font-size: 11px;
    color: #999;
    line-height: 1.3;
  }
}

.tool-status {
  margin-left: 8px;
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #6c757d;
    
    &.status-online {
      background: #28a745;
    }
    
    &.status-offline {
      background: #6c757d;
    }
    
    &.status-error {
      background: #dc3545;
    }
  }
}

/* 小程序适配 */
/* #ifdef MP */
.dev-tool-item {
  &:hover {
    background: transparent;
    border-left-color: transparent;
  }
  
  &:active {
    background: #f8f9fa;
    border-left-color: #007AFF;
  }
}
/* #endif */

/* 深色模式适配 */
/* #ifdef H5 */
@media (prefers-color-scheme: dark) {
  .dev-tool-item {
    &:hover {
      background: #2a2a2a;
      border-left-color: #90caf9;
    }
    
    &:active {
      background: #3a3a3a;
    }
    
    &.dev-tool-active {
      background: #3e2723;
      border-left-color: #ffb74d;
      
      .tool-icon .icon {
        color: #ffb74d;
      }
      
      .tool-title .title-text {
        color: #ffb74d;
      }
    }
  }
  
  .tool-info .tool-title .title-text {
    color: #fff;
  }
  
  .tool-info .description-text {
    color: #bbb;
  }
  
  .tool-icon .icon {
    color: #bbb;
  }
}
/* #endif */
</style>