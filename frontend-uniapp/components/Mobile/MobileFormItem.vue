<template>
  <view class="mobile-form-item" :class="formItemClasses">
    <!-- 标签 -->
    <view v-if="label || $slots.label" class="form-item-label" :style="labelStyle">
      <view class="label-content">
        <!-- 必填标记 -->
        <text v-if="required && showRequired" class="required-mark">*</text>
        
        <!-- 标签文本 -->
        <text v-if="label" class="label-text">{{ label }}</text>
        
        <!-- 自定义标签 -->
        <slot name="label"></slot>
      </view>
    </view>
    
    <!-- 输入区域 -->
    <view class="form-item-content" :class="{ 'content-error': hasError }">
      <!-- 输入框 -->
      <input 
        v-if="type === 'text' || type === 'number' || type === 'password'"
        class="form-input"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :maxlength="maxlength"
        :focus="focus"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @confirm="handleConfirm"
      />
      
      <!-- 文本域 -->
      <textarea 
        v-else-if="type === 'textarea'"
        class="form-textarea"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :maxlength="maxlength"
        :auto-height="autoHeight"
        :show-confirm-bar="false"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @confirm="handleConfirm"
      />
      
      <!-- 选择器 -->
      <picker 
        v-else-if="type === 'picker'"
        :mode="pickerMode"
        :range="pickerRange"
        :range-key="pickerRangeKey"
        :value="pickerValue"
        :disabled="disabled"
        @change="handlePickerChange"
      >
        <view class="picker-display" :class="{ 'picker-placeholder': !displayValue }">
          <text>{{ displayValue || placeholder }}</text>
          <text class="picker-arrow">›</text>
        </view>
      </picker>
      
      <!-- 开关 -->
      <switch 
        v-else-if="type === 'switch'"
        :checked="modelValue"
        :disabled="disabled"
        :color="switchColor"
        @change="handleSwitchChange"
      />
      
      <!-- 滑块 -->
      <slider 
        v-else-if="type === 'slider'"
        :value="modelValue"
        :min="sliderMin"
        :max="sliderMax"
        :step="sliderStep"
        :disabled="disabled"
        :show-value="showSliderValue"
        :activeColor="sliderActiveColor"
        @change="handleSliderChange"
      />
      
      <!-- 自定义内容 -->
      <slot v-else></slot>
      
      <!-- 右侧图标 -->
      <view v-if="rightIcon" class="form-item-icon" @tap="handleIconTap">
        <text class="iconfont" :class="rightIcon"></text>
      </view>
    </view>
    
    <!-- 错误信息 -->
    <view v-if="hasError" class="form-item-error">
      <text class="error-text">{{ errorMessage }}</text>
    </view>
    
    <!-- 帮助信息 -->
    <view v-if="help" class="form-item-help">
      <text class="help-text">{{ help }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MobileFormItem',
  inject: {
    mobileForm: {
      default: null
    }
  },
  props: {
    // 标签
    label: {
      type: String,
      default: ''
    },
    // 输入类型
    type: {
      type: String,
      default: 'text',
      validator: value => [
        'text', 'number', 'password', 'textarea', 
        'picker', 'switch', 'slider', 'custom'
      ].includes(value)
    },
    // 双向绑定值
    modelValue: {
      type: [String, Number, Boolean, Array],
      default: ''
    },
    // 占位符
    placeholder: {
      type: String,
      default: ''
    },
    // 是否必填
    required: {
      type: Boolean,
      default: false
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      default: false
    },
    // 最大长度
    maxlength: {
      type: Number,
      default: -1
    },
    // 是否自动获取焦点
    focus: {
      type: Boolean,
      default: false
    },
    // 右侧图标
    rightIcon: {
      type: String,
      default: ''
    },
    // 错误信息
    errorMessage: {
      type: String,
      default: ''
    },
    // 帮助信息
    help: {
      type: String,
      default: ''
    },
    // 文本域自动高度
    autoHeight: {
      type: Boolean,
      default: true
    },
    // 选择器模式
    pickerMode: {
      type: String,
      default: 'selector',
      validator: value => ['selector', 'multiSelector', 'time', 'date'].includes(value)
    },
    // 选择器数据
    pickerRange: {
      type: Array,
      default: () => []
    },
    // 选择器显示字段
    pickerRangeKey: {
      type: String,
      default: ''
    },
    // 开关颜色
    switchColor: {
      type: String,
      default: '#2196f3'
    },
    // 滑块最小值
    sliderMin: {
      type: Number,
      default: 0
    },
    // 滑块最大值
    sliderMax: {
      type: Number,
      default: 100
    },
    // 滑块步长
    sliderStep: {
      type: Number,
      default: 1
    },
    // 是否显示滑块值
    showSliderValue: {
      type: Boolean,
      default: true
    },
    // 滑块激活颜色
    sliderActiveColor: {
      type: String,
      default: '#2196f3'
    }
  },
  emits: ['update:modelValue', 'input', 'blur', 'focus', 'confirm', 'icon-tap'],
  computed: {
    formItemClasses() {
      return {
        'form-item-required': this.required,
        'form-item-disabled': this.disabled,
        'form-item-error': this.hasError,
        'form-item-label-top': this.labelPosition === 'top'
      }
    },
    
    labelPosition() {
      return this.mobileForm?.labelPosition || 'left'
    },
    
    showRequired() {
      return this.mobileForm?.showRequired !== false
    },
    
    labelStyle() {
      if (this.labelPosition === 'left') {
        return {
          width: this.mobileForm?.labelWidth || '80px'
        }
      }
      return {}
    },
    
    inputType() {
      const typeMap = {
        text: 'text',
        number: 'number',
        password: 'password'
      }
      return typeMap[this.type] || 'text'
    },
    
    hasError() {
      return !!this.errorMessage
    },
    
    pickerValue() {
      if (this.pickerMode === 'selector') {
        return this.pickerRange.findIndex(item => {
          if (this.pickerRangeKey) {
            return item[this.pickerRangeKey] === this.modelValue
          }
          return item === this.modelValue
        })
      }
      return this.modelValue
    },
    
    displayValue() {
      if (this.type === 'picker' && this.modelValue !== undefined && this.modelValue !== '') {
        if (this.pickerMode === 'selector') {
          const item = this.pickerRange[this.pickerValue]
          if (item) {
            return this.pickerRangeKey ? item[this.pickerRangeKey] : item
          }
        }
        return this.modelValue
      }
      return ''
    }
  },
  methods: {
    handleInput(e) {
      const value = e.detail.value
      this.$emit('update:modelValue', value)
      this.$emit('input', e)
    },
    
    handleBlur(e) {
      this.$emit('blur', e)
    },
    
    handleFocus(e) {
      this.$emit('focus', e)
    },
    
    handleConfirm(e) {
      this.$emit('confirm', e)
    },
    
    handlePickerChange(e) {
      const index = e.detail.value
      let value = this.pickerRange[index]
      
      if (this.pickerRangeKey && value) {
        value = value[this.pickerRangeKey]
      }
      
      this.$emit('update:modelValue', value)
    },
    
    handleSwitchChange(e) {
      this.$emit('update:modelValue', e.detail.value)
    },
    
    handleSliderChange(e) {
      this.$emit('update:modelValue', e.detail.value)
    },
    
    handleIconTap() {
      this.$emit('icon-tap')
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-form-item {
  display: flex;
  align-items: flex-start;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-color);
  
  &:last-child {
    border-bottom: none;
  }
  
  &.form-item-label-top {
    flex-direction: column;
    
    .form-item-label {
      width: 100% !important;
      margin-bottom: var(--spacing-sm);
    }
  }
  
  &.form-item-disabled {
    opacity: 0.5;
  }
  
  &.form-item-error {
    .form-item-content {
      border-color: var(--error-color);
    }
  }
}

.form-item-label {
  flex-shrink: 0;
  padding-right: var(--spacing-md);
  
  .label-content {
    display: flex;
    align-items: center;
    height: 44px;
    
    .required-mark {
      color: var(--error-color);
      margin-right: var(--spacing-xs);
    }
    
    .label-text {
      font-size: 16px;
      color: var(--text-primary);
      font-weight: 500;
    }
  }
}

.form-item-content {
  flex: 1;
  display: flex;
  align-items: center;
  
  .form-input,
  .form-textarea {
    flex: 1;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 16px;
    background-color: var(--card-background);
    color: var(--text-primary);
    
    &:focus {
      border-color: var(--primary-color);
      outline: none;
    }
    
    &::placeholder {
      color: var(--text-disabled);
    }
    
    &:disabled {
      background-color: var(--background-color);
      color: var(--text-disabled);
    }
  }
  
  .form-input {
    height: 44px;
  }
  
  .form-textarea {
    min-height: 88px;
    resize: vertical;
  }
  
  .picker-display {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background-color: var(--card-background);
    min-height: 44px;
    
    &.picker-placeholder {
      color: var(--text-disabled);
    }
    
    .picker-arrow {
      color: var(--text-disabled);
      font-size: 16px;
    }
  }
  
  .form-item-icon {
    margin-left: var(--spacing-sm);
    padding: var(--spacing-sm);
    color: var(--text-secondary);
    cursor: pointer;
    
    &:active {
      color: var(--primary-color);
    }
  }
}

.form-item-error {
  margin-top: var(--spacing-xs);
  
  .error-text {
    font-size: 12px;
    color: var(--error-color);
    line-height: 1.4;
  }
}

.form-item-help {
  margin-top: var(--spacing-xs);
  
  .help-text {
    font-size: 12px;
    color: var(--text-disabled);
    line-height: 1.4;
  }
}

/* 响应式适配 */
@media screen and (max-width: 480px) {
  .mobile-form-item {
    &:not(.form-item-label-top) {
      flex-direction: column;
      
      .form-item-label {
        width: 100% !important;
        margin-bottom: var(--spacing-sm);
        padding-right: 0;
        
        .label-content {
          height: auto;
        }
      }
    }
  }
}
</style>