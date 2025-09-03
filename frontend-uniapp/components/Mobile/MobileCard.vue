<template>
  <view class="mobile-card" :class="cardClasses" @tap="handleTap">
    <!-- 卡片头部 -->
    <view v-if="showHeader" class="card-header">
      <view class="card-title-wrapper">
        <text class="card-title">{{ title }}</text>
        <text v-if="subtitle" class="card-subtitle">{{ subtitle }}</text>
      </view>
      <view v-if="$slots.action" class="card-action">
        <slot name="action"></slot>
      </view>
    </view>
    
    <!-- 卡片内容 -->
    <view class="card-content" :class="{ 'no-padding': noPadding }">
      <slot></slot>
    </view>
    
    <!-- 卡片底部 -->
    <view v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MobileCard',
  props: {
    // 卡片标题
    title: {
      type: String,
      default: ''
    },
    // 卡片副标题
    subtitle: {
      type: String,
      default: ''
    },
    // 是否显示头部
    showHeader: {
      type: Boolean,
      default: true
    },
    // 是否有阴影
    shadow: {
      type: Boolean,
      default: true
    },
    // 是否可点击
    clickable: {
      type: Boolean,
      default: false
    },
    // 内容区域是否无内边距
    noPadding: {
      type: Boolean,
      default: false
    },
    // 卡片类型
    type: {
      type: String,
      default: 'default',
      validator: value => ['default', 'primary', 'success', 'warning', 'error'].includes(value)
    },
    // 圆角大小
    radius: {
      type: String,
      default: 'normal',
      validator: value => ['none', 'small', 'normal', 'large', 'round'].includes(value)
    }
  },
  computed: {
    cardClasses() {
      return {
        'card-shadow': this.shadow,
        'card-clickable': this.clickable,
        [`card-${this.type}`]: this.type !== 'default',
        [`card-radius-${this.radius}`]: this.radius !== 'normal'
      }
    }
  },
  methods: {
    handleTap() {
      if (this.clickable) {
        this.$emit('click')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-card {
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-md);
  overflow: hidden;
  transition: all 0.2s ease;
  
  &.card-shadow {
    box-shadow: var(--shadow-light);
  }
  
  &.card-clickable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-medium);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
  
  // 卡片类型样式
  &.card-primary {
    border-left: 4px solid var(--primary-color);
  }
  
  &.card-success {
    border-left: 4px solid var(--success-color);
  }
  
  &.card-warning {
    border-left: 4px solid var(--warning-color);
  }
  
  &.card-error {
    border-left: 4px solid var(--error-color);
  }
  
  // 圆角样式
  &.card-radius-none {
    border-radius: 0;
  }
  
  &.card-radius-small {
    border-radius: 4px;
  }
  
  &.card-radius-large {
    border-radius: 16px;
  }
  
  &.card-radius-round {
    border-radius: 24px;
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  
  .card-title-wrapper {
    flex: 1;
  }
  
  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.4;
  }
  
  .card-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: var(--spacing-xs);
    line-height: 1.4;
  }
  
  .card-action {
    margin-left: var(--spacing-md);
  }
}

.card-content {
  padding: var(--spacing-md);
  
  &.no-padding {
    padding: 0;
  }
}

.card-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background-color: rgba(0, 0, 0, 0.02);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .card-footer {
    background-color: rgba(255, 255, 255, 0.02);
  }
}
</style>