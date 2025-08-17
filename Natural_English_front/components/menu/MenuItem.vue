<template>
  <div 
    :class="itemClasses"
    @click="handleClick"
    @mouseenter="$emit('hover', item)"
    @mouseleave="$emit('leave', item)"
  >
    <span v-if="item && item.icon" class="menu-item__icon">{{ item.icon }}</span>
    <div class="menu-item__content">
      <span class="menu-item__title">{{ (item && (item.title || item.name)) || '未命名菜单项' }}</span>
      <span v-if="item && item.description" class="menu-item__desc">{{ item.description }}</span>
    </div>
    <div v-if="hasActions" class="menu-item__actions">
      <slot name="actions" :item="item"></slot>
    </div>
    <span v-if="hasSubmenu" class="menu-item__arrow">{{ expanded ? '▼' : '▶' }}</span>
  </div>
</template>

<script>
export default {
  name: 'MenuItem',
  props: {
    item: {
      type: Object,
      required: true,
      default: () => ({})
    },
    active: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    expanded: {
      type: Boolean,
      default: false
    },
    hasSubmenu: {
      type: Boolean,
      default: false
    },
    variant: {
      type: String,
      default: 'default',
      validator: value => ['default', 'primary', 'secondary', 'danger'].includes(value)
    }
  },
  computed: {
    itemClasses() {
      return [
        'menu-item',
        `menu-item--${this.variant}`,
        {
          'menu-item--active': this.active,
          'menu-item--disabled': this.disabled,
          'menu-item--expandable': this.hasSubmenu
        }
      ]
    },
    hasActions() {
      return !!this.$slots.actions
    }
  },
  methods: {
    handleClick() {
      if (this.disabled || !this.item) return
      this.$emit('click', this.item)
    }
  }
}
</script>

<style lang="scss" scoped>
@use '../../assets/scss/index.scss';

.menu-item {
  @include flex-between;
  @include transition;
  position: relative;
  padding: $spacing-3 $spacing-4;
  margin-bottom: $spacing-1;
  border-radius: $border-radius-md;
  cursor: pointer;
  overflow: hidden;
  background: $color-white;
  
  &:hover {
    background: $color-gray-50;
    transform: translateX(4px);
  }
  
  &:active {
    background: $color-gray-100;
    transform: translateX(2px);
  }
  
  // BEM 修饰符 - 状态
  @include bem-modifier('active') {
    background: $color-primary-50;
    color: $color-primary-700;
    border-left: 3px solid var(--color-primary-500);
  }
  
  @include bem-modifier('disabled') {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  @include bem-modifier('expandable') {
    padding-right: $spacing-8;
  }

  // BEM 修饰符 - 变体
  @include bem-modifier('primary') {
    background: var(--color-primary-500);
    color: $color-white;
    
    &:hover {
      background: $color-primary-600;
    }
  }
  
  @include bem-modifier('secondary') {
    background: $color-gray-100;
    color: $color-gray-700;
    
    &:hover {
      background: $color-gray-200;
    }
  }
  
  &--danger {
    background: $color-red-50;
    color: $color-red-700;
    
    &:hover {
      background: $color-red-100;
    }
  }
  
  // BEM 元素
  .menu-item__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--spacing-6);
    height: var(--spacing-6);
    margin-right: var(--spacing-3);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-medium);
    color: var(--color-gray-600);
  }
  
  .menu-item__content {
    flex: 1;
    min-width: 0;
  }
  
  .menu-item__title {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-gray-900);
    display: block;
    line-height: var(--line-height-tight);
  }
  
  .menu-item__desc {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-normal);
    color: var(--color-gray-500);
    display: block;
    margin-top: var(--spacing-1);
    line-height: var(--line-height-tight);
  }
  
  .menu-item__actions {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: $spacing-2;
  }
  
  .menu-item__arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    position: absolute;
    right: var(--spacing-3);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-normal);
    color: var(--color-gray-400);
    transform: rotate(0deg);
  }
}

// 展开状态的箭头动画
.menu-item--expandable .menu-item__arrow {
  transform: rotate(90deg);
}
</style>

