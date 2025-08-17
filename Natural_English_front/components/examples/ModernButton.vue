<template>
  <component
    :is="tag"
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="tag === 'button' ? type : undefined"
    :href="tag === 'a' ? href : undefined"
    :target="tag === 'a' && external ? '_blank' : undefined"
    :rel="tag === 'a' && external ? 'noopener noreferrer' : undefined"
    @click="handleClick"
  >
    <!-- 图标前缀 -->
    <span class="modern-button__icon modern-button__icon--prefix" v-if="$slots.prefix || prefixIcon">
      <slot name="prefix">
        <i :class="prefixIcon" v-if="prefixIcon"></i>
      </slot>
    </span>

    <!-- 按钮文本 -->
    <span class="modern-button__text" v-if="!loading">
      <slot></slot>
    </span>

    <!-- 加载状态 -->
    <span class="modern-button__loading" v-if="loading">
      <span class="modern-button__spinner"></span>
      <span class="modern-button__loading-text" v-if="loadingText">
        {{ loadingText }}
      </span>
    </span>

    <!-- 图标后缀 -->
    <span class="modern-button__icon modern-button__icon--suffix" v-if="$slots.suffix || suffixIcon">
      <slot name="suffix">
        <i :class="suffixIcon" v-if="suffixIcon"></i>
      </slot>
    </span>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props 定义
interface Props {
  // 基础属性
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  type?: 'button' | 'submit' | 'reset'
  tag?: 'button' | 'a'
  
  // 状态
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  
  // 链接相关
  href?: string
  external?: boolean
  
  // 图标
  prefixIcon?: string
  suffixIcon?: string
  
  // 样式
  block?: boolean
  rounded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  tag: 'button',
  disabled: false,
  loading: false,
  external: false,
  block: false,
  rounded: false
})

// Events 定义
interface Emits {
  click: [event: MouseEvent]
}

const emit = defineEmits<Emits>()

// 计算属性
const buttonClasses = computed(() => {
  return [
    'modern-button',
    {
      [`modern-button--${props.variant}`]: true,
      [`modern-button--${props.size}`]: true,
      'modern-button--block': props.block,
      'modern-button--rounded': props.rounded,
      'modern-button--loading': props.loading,
      'modern-button--disabled': props.disabled
    }
  ]
})

// 事件处理
const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
// 使用新的 SCSS + BEM 架构
.modern-button {
  // 基础按钮样式
  @include button-base;
  @include transition();
  @include flex-center;
  gap: var(--spacing-2);
  position: relative;
  overflow: hidden;
  
  // 禁用文本选择
  user-select: none;
  
  // 按钮文本
  @include bem-element('text') {
    @include transition();
  }
  
  // 图标样式
  @include bem-element('icon') {
    @include flex-center;
    @include transition();
    
    @include bem-modifier('prefix') {
      margin-right: var(--spacing-1);
    }
    
    @include bem-modifier('suffix') {
      margin-left: var(--spacing-1);
    }
  }
  
  // 加载状态
  @include bem-element('loading') {
    @include flex-center;
    gap: var(--spacing-2);
  }
  
  @include bem-element('spinner') {
    width: 1rem;
    height: 1rem;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @include bem-element('loading-text') {
    @include transition();
  }
  
  // 按钮变体
  @include bem-modifier('primary') {
    @include button-variant(var(--color-primary-500), var(--color-white));
    
    &:hover:not(:disabled) {
      background-color: var(--color-primary-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-primary-700);
    }
  }
  
  @include bem-modifier('secondary') {
    @include button-variant(var(--color-gray-500), var(--color-white));
    
    &:hover:not(:disabled) {
      background-color: var(--color-gray-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-gray-700);
    }
  }
  
  @include bem-modifier('outline') {
    background-color: transparent;
    color: var(--color-primary-500);
      border: 2px solid var(--color-primary-500);
    
    &:hover:not(:disabled) {
      background-color: var(--color-primary-50);
        color: var(--color-primary-600);
        border-color: var(--color-primary-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-primary-100);
    }
  }
  
  @include bem-modifier('ghost') {
    background-color: transparent;
    color: var(--color-primary-500);
    border: none;
    
    &:hover:not(:disabled) {
      background-color: var(--color-primary-50);
        color: var(--color-primary-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-primary-100);
    }
  }
  
  @include bem-modifier('danger') {
    @include button-variant(var(--color-red-500), var(--color-white));
    
    &:hover:not(:disabled) {
      background-color: var(--color-red-600);
    }
    
    &:active:not(:disabled) {
      background-color: var(--color-red-700);
    }
  }
  
  // 按钮尺寸
  @include bem-modifier('sm') {
    @include text-style(var(--font-size-sm), var(--font-weight-medium));
    padding: var(--spacing-2) var(--spacing-3);
    min-height: 2rem;
    
    .modern-button__icon {
      font-size: $font-size-sm;
    }
  }
  
  @include bem-modifier('md') {
    @include text-style($font-size-base, $font-weight-medium);
    padding: $spacing-3 $spacing-4;
    min-height: 2.5rem;
  }
  
  @include bem-modifier('lg') {
    @include text-style($font-size-lg, $font-weight-medium);
    padding: var(--spacing-4) var(--spacing-6);
    min-height: 3rem;
    
    .modern-button__icon {
      font-size: $font-size-lg;
    }
  }
  
  // 按钮状态
  @include bem-modifier('block') {
    width: 100%;
  }
  
  @include bem-modifier('rounded') {
    border-radius: $border-radius-full;
  }
  
  &--loading {
    pointer-events: none;
    
    .modern-button__text {
      opacity: 0;
    }
  }
  
  &--disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  // 焦点样式
  &:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }
  
  // 响应式设计
  @media (min-width: 640px) {
    &--sm {
      padding: $spacing-2 $spacing-4;
    }
    
    &--md {
      padding: $spacing-3 $spacing-5;
    }
    
    &--lg {
      padding: $spacing-4 $spacing-8;
    }
  }
}

// 动画定义
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>