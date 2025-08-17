<template>
  <div 
    :class="cardClasses"
    @click="handleClick"
  >
    <!-- 卡片头部 -->
    <div class="modern-card__header" v-if="$slots.header || title">
      <slot name="header">
        <h3 class="modern-card__title">{{ title }}</h3>
        <p class="modern-card__subtitle" v-if="subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- 卡片内容 -->
    <div class="modern-card__body">
      <slot></slot>
    </div>

    <!-- 卡片底部 -->
    <div class="modern-card__footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>

    <!-- 加载状态 -->
    <div class="modern-card__loading" v-if="loading">
      <div class="loading__spinner"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props 定义
interface Props {
  title?: string
  subtitle?: string
  variant?: 'default' | 'highlighted' | 'compact'
  interactive?: boolean
  loading?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  interactive: false,
  loading: false,
  disabled: false
})

// Events 定义
interface Emits {
  click: [event: MouseEvent]
}

const emit = defineEmits<Emits>()

// 计算属性
const cardClasses = computed(() => {
  return [
    'modern-card',
    {
      [`modern-card--${props.variant}`]: props.variant !== 'default',
      'modern-card--interactive': props.interactive,
      'modern-card--loading': props.loading,
      'modern-card--disabled': props.disabled
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
.modern-card {
  // 基础卡片样式
  @include card(var(--spacing-6));
  @include transition();
  position: relative;
  overflow: hidden;
  
  // 卡片头部
  @include bem-element('header') {
    padding-bottom: $spacing-4;
    border-bottom: 1px solid $color-gray-200;
    margin-bottom: $spacing-4;
    
    &:last-child {
      margin-bottom: 0;
      border-bottom: none;
      padding-bottom: 0;
    }
  }
  
  // 卡片标题
  @include bem-element('title') {
    @include heading(3);
    margin: 0;
    color: $color-gray-900;
  }
  
  // 卡片副标题
  @include bem-element('subtitle') {
    @include text-style($font-size-sm, $font-weight-normal);
    color: $color-gray-600;
    margin: $spacing-1 0 0 0;
  }
  
  // 卡片内容
  @include bem-element('body') {
    color: $color-gray-700;
    line-height: $line-height-relaxed;
    
    // 如果没有头部，移除上边距
    .modern-card__header + & {
      margin-top: 0;
    }
  }
  
  // 卡片底部
  @include bem-element('footer') {
    padding-top: $spacing-4;
    border-top: 1px solid $color-gray-200;
    margin-top: $spacing-4;
    @include flex-between;
    gap: $spacing-3;
  }
  
  // 加载状态覆盖层
  @include bem-element('loading') {
    @include absolute-center;
    width: 100%;
    height: 100%;
    background-color: rgba($color-white, 0.8);
    @include flex-center;
    z-index: var(--z-index-overlay);
  }
  
  // 卡片变体
  @include bem-modifier('highlighted') {
    border: 2px solid var(--color-primary-500);
    @include shadow('lg');
    
    .modern-card__title {
      color: $color-primary-700;
    }
  }
  
  @include bem-modifier('compact') {
    padding: $spacing-4;
    
    .modern-card__header {
      padding-bottom: $spacing-2;
      margin-bottom: $spacing-2;
    }
    
    .modern-card__footer {
      padding-top: $spacing-2;
      margin-top: $spacing-2;
    }
  }
  
  // 交互状态
  @include bem-modifier('interactive') {
    @include hover-lift;
    cursor: pointer;
    
    &:hover {
      @include shadow('xl');
    }
    
    &:active {
      transform: translateY(0);
    }
  }
  
  // 加载状态
  @include bem-modifier('loading') {
    pointer-events: none;
  }
  
  // 禁用状态
  @include bem-modifier('disabled') {
    opacity: 0.6;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
      @include shadow('base');
    }
  }
  
  // 响应式设计
  @include respond-to('sm') {
    padding: $spacing-8;
    
    @include bem-modifier('compact') {
      padding: var(--spacing-6);
    }
  }
}

// 加载动画
.loading {
  @include bem-element('spinner') {
    width: 2rem;
    height: 2rem;
    border: 2px solid $color-gray-200;
    border-top-color: var(--color-primary-500);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>