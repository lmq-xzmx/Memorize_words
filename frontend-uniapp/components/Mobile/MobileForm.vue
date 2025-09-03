<template>
  <view class="mobile-form" :class="formClasses">
    <!-- 表单标题 -->
    <view v-if="title || $slots.header" class="form-header">
      <view v-if="title" class="form-title">
        <text class="title-text">{{ title }}</text>
        <text v-if="subtitle" class="subtitle-text">{{ subtitle }}</text>
      </view>
      <slot name="header"></slot>
    </view>
    
    <!-- 表单内容 -->
    <view class="form-content">
      <slot></slot>
    </view>
    
    <!-- 表单底部 -->
    <view v-if="$slots.footer" class="form-footer">
      <slot name="footer"></slot>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MobileForm',
  props: {
    // 表单标题
    title: {
      type: String,
      default: ''
    },
    // 表单副标题
    subtitle: {
      type: String,
      default: ''
    },
    // 表单类型
    type: {
      type: String,
      default: 'default',
      validator: value => ['default', 'card', 'inset'].includes(value)
    },
    // 标签位置
    labelPosition: {
      type: String,
      default: 'left',
      validator: value => ['left', 'top'].includes(value)
    },
    // 标签宽度
    labelWidth: {
      type: String,
      default: '80px'
    },
    // 是否显示必填星号
    showRequired: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    formClasses() {
      return {
        [`form-${this.type}`]: this.type !== 'default',
        [`form-label-${this.labelPosition}`]: true
      }
    }
  },
  provide() {
    return {
      mobileForm: this
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-form {
  background-color: var(--card-background);
  
  &.form-card {
    border-radius: var(--border-radius);
    margin: var(--spacing-md);
    box-shadow: var(--shadow-light);
  }
  
  &.form-inset {
    margin: var(--spacing-md);
    border-radius: var(--border-radius);
  }
}

.form-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  
  .form-title {
    .title-text {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      line-height: 1.4;
    }
    
    .subtitle-text {
      font-size: 14px;
      color: var(--text-secondary);
      margin-top: var(--spacing-xs);
      line-height: 1.4;
    }
  }
}

.form-content {
  padding: var(--spacing-md);
}

.form-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background-color: rgba(0, 0, 0, 0.02);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .form-footer {
    background-color: rgba(255, 255, 255, 0.02);
  }
}
</style>