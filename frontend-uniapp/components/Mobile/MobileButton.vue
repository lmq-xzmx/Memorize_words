<template>
  <button 
    class="mobile-button" 
    :class="buttonClasses"
    :disabled="disabled || loading"
    :form-type="formType"
    :open-type="openType"
    @tap="handleTap"
    @getuserinfo="handleGetUserInfo"
    @contact="handleContact"
    @getphonenumber="handleGetPhoneNumber"
    @error="handleError"
    @opensetting="handleOpenSetting"
    @launchapp="handleLaunchApp"
  >
    <!-- 加载状态 -->
    <view v-if="loading" class="button-loading">
      <view class="loading-spinner"></view>
      <text v-if="loadingText" class="loading-text">{{ loadingText }}</text>
    </view>
    
    <!-- 正常状态 -->
    <view v-else class="button-content">
      <!-- 图标 -->
      <view v-if="icon" class="button-icon" :class="{ 'icon-right': iconPosition === 'right' }">
        <text class="iconfont" :class="icon"></text>
      </view>
      
      <!-- 文本内容 -->
      <text class="button-text">
        <slot>{{ text }}</slot>
      </text>
      
      <!-- 右侧图标 -->
      <view v-if="icon && iconPosition === 'right'" class="button-icon icon-right">
        <text class="iconfont" :class="icon"></text>
      </view>
    </view>
  </button>
</template>

<script>
export default {
  name: 'MobileButton',
  props: {
    // 按钮文本
    text: {
      type: String,
      default: ''
    },
    // 按钮类型
    type: {
      type: String,
      default: 'default',
      validator: value => ['default', 'primary', 'secondary', 'success', 'warning', 'error', 'text'].includes(value)
    },
    // 按钮尺寸
    size: {
      type: String,
      default: 'normal',
      validator: value => ['mini', 'small', 'normal', 'large'].includes(value)
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      default: false
    },
    // 是否加载中
    loading: {
      type: Boolean,
      default: false
    },
    // 加载文本
    loadingText: {
      type: String,
      default: ''
    },
    // 是否块级按钮
    block: {
      type: Boolean,
      default: false
    },
    // 是否圆形按钮
    round: {
      type: Boolean,
      default: false
    },
    // 是否朴素按钮
    plain: {
      type: Boolean,
      default: false
    },
    // 图标
    icon: {
      type: String,
      default: ''
    },
    // 图标位置
    iconPosition: {
      type: String,
      default: 'left',
      validator: value => ['left', 'right'].includes(value)
    },
    // 表单类型
    formType: {
      type: String,
      default: '',
      validator: value => ['', 'submit', 'reset'].includes(value)
    },
    // 开放能力
    openType: {
      type: String,
      default: '',
      validator: value => [
        '', 'contact', 'share', 'getPhoneNumber', 'getUserInfo',
        'launchApp', 'openSetting', 'feedback'
      ].includes(value)
    },
    // 自定义样式
    customStyle: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    buttonClasses() {
      return {
        [`button-${this.type}`]: true,
        [`button-${this.size}`]: this.size !== 'normal',
        'button-block': this.block,
        'button-round': this.round,
        'button-plain': this.plain,
        'button-disabled': this.disabled,
        'button-loading': this.loading
      }
    }
  },
  methods: {
    handleTap(e) {
      if (this.disabled || this.loading) return
      this.$emit('click', e)
    },
    
    handleGetUserInfo(e) {
      this.$emit('getuserinfo', e)
    },
    
    handleContact(e) {
      this.$emit('contact', e)
    },
    
    handleGetPhoneNumber(e) {
      this.$emit('getphonenumber', e)
    },
    
    handleError(e) {
      this.$emit('error', e)
    },
    
    handleOpenSetting(e) {
      this.$emit('opensetting', e)
    },
    
    handleLaunchApp(e) {
      this.$emit('launchapp', e)
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid transparent;
  border-radius: var(--border-radius);
  font-size: 16px;
  font-weight: 500;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 44px;
  box-sizing: border-box;
  outline: none;
  
  &::after {
    border: none;
  }
  
  // 按钮类型样式
  &.button-default {
    background-color: var(--card-background);
    color: var(--text-primary);
    border-color: var(--border-color);
    
    &:not(.button-disabled):not(.button-loading):active {
      background-color: var(--background-color);
    }
  }
  
  &.button-primary {
    background-color: var(--primary-color);
    color: white;
    
    &:not(.button-disabled):not(.button-loading):active {
      background-color: #1976d2;
    }
  }
  
  &.button-secondary {
    background-color: transparent;
    color: var(--primary-color);
    border-color: var(--primary-color);
    
    &:not(.button-disabled):not(.button-loading):active {
      background-color: rgba(33, 150, 243, 0.1);
    }
  }
  
  &.button-success {
    background-color: var(--success-color);
    color: white;
    
    &:not(.button-disabled):not(.button-loading):active {
      background-color: #388e3c;
    }
  }
  
  &.button-warning {
    background-color: var(--warning-color);
    color: white;
    
    &:not(.button-disabled):not(.button-loading):active {
      background-color: #f57c00;
    }
  }
  
  &.button-error {
    background-color: var(--error-color);
    color: white;
    
    &:not(.button-disabled):not(.button-loading):active {
      background-color: #d32f2f;
    }
  }
  
  &.button-text {
    background-color: transparent;
    color: var(--primary-color);
    border-color: transparent;
    
    &:not(.button-disabled):not(.button-loading):active {
      background-color: rgba(33, 150, 243, 0.1);
    }
  }
  
  // 朴素按钮样式
  &.button-plain {
    background-color: transparent;
    
    &.button-primary {
      color: var(--primary-color);
      border-color: var(--primary-color);
    }
    
    &.button-success {
      color: var(--success-color);
      border-color: var(--success-color);
    }
    
    &.button-warning {
      color: var(--warning-color);
      border-color: var(--warning-color);
    }
    
    &.button-error {
      color: var(--error-color);
      border-color: var(--error-color);
    }
  }
  
  // 按钮尺寸
  &.button-mini {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 12px;
    min-height: 28px;
  }
  
  &.button-small {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 14px;
    min-height: 36px;
  }
  
  &.button-large {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: 18px;
    min-height: 52px;
  }
  
  // 块级按钮
  &.button-block {
    width: 100%;
    display: flex;
  }
  
  // 圆形按钮
  &.button-round {
    border-radius: 50px;
  }
  
  // 禁用状态
  &.button-disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  // 加载状态
  &.button-loading {
    cursor: default;
  }
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.button-icon {
  display: flex;
  align-items: center;
  
  &:not(.icon-right) {
    margin-right: var(--spacing-xs);
  }
  
  &.icon-right {
    margin-left: var(--spacing-xs);
  }
}

.button-text {
  flex: 1;
  text-align: center;
}

.button-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  
  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  .loading-text {
    margin-left: var(--spacing-xs);
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式适配 */
@media screen and (max-width: 480px) {
  .mobile-button {
    font-size: 14px;
    min-height: 40px;
    
    &.button-large {
      font-size: 16px;
      min-height: 48px;
    }
  }
}
</style>