<template>
  <div 
    :class="navItemClasses"
    @click="handleClick"
    @mouseenter="$emit('hover', item)"
    @mouseleave="$emit('leave', item)"
  >
    <div class="nav-item__icon">
      <span :class="iconClasses">{{ item.icon }}</span>
    </div>
    <div class="nav-item__text">{{ item.title }}</div>
    <div v-if="showBadge" class="nav-item__badge">{{ badgeText }}</div>
  </div>
</template>

<script>
export default {
  name: 'NavItem',
  props: {
    item: {
      type: Object,
      required: true
    },
    active: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    badge: {
      type: [String, Number],
      default: null
    }
  },
  emits: ['click', 'hover', 'leave'],
  computed: {
    navItemClasses() {
      return [
        'nav-item',
        {
          'nav-item--active': this.active,
          'nav-item--disabled': this.disabled,
          'nav-item--menu': this.item.type === 'menu'
        }
      ]
    },
    iconClasses() {
      return [
        'icon',
        {
          'icon--chinese': this.isChinese(this.item.icon),
          'icon--emoji': this.isEmoji(this.item.icon)
        }
      ]
    },
    showBadge() {
      return this.badge !== null && this.badge !== undefined && this.badge !== ''
    },
    badgeText() {
      if (typeof this.badge === 'number' && this.badge > 99) {
        return '99+'
      }
      return this.badge
    }
  },
  methods: {
    handleClick() {
      if (this.disabled) return
      this.$emit('click', this.item)
    },
    isChinese(text) {
      return /[\u4e00-\u9fa5]/.test(text)
    },
    isEmoji(text) {
      return /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u.test(text)
    }
  }
}
</script>

<style lang="scss" scoped>
// 使用新的 SCSS + BEM 架构
.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: $spacing-2 $spacing-3;
  border-radius: $border-radius-xl;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  min-width: 60px;
  height: 50px;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, var(--color-primary-500), var(--color-purple-500));
    border-radius: $border-radius-xl;
    opacity: 0;
    transform: scale(0.8);
    transition: all 0.2s ease;
  }
  
  &:hover::before {
    opacity: 0.1;
    transform: scale(1);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  // BEM 修饰符
  &--active {
    &::before {
      opacity: 0.2;
      transform: scale(1);
    }
  }
  
  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
    
    &:hover::before {
      opacity: 0;
    }
  }
  
  &--menu {
    // 菜单类型特殊样式
  }

  // BEM 元素 - 导航图标
  &__icon {
    font-size: $font-size-2xl;
    margin-bottom: $spacing-1;
    position: relative;
    z-index: var(--z-index-base);
    transition: all 0.2s ease;
  }
  
  &:hover {
     .nav-item__icon {
       transform: scale(1.1);
     }
     
     .nav-item__text {
       color: $color-gray-900;
     }
     
     .icon--chinese {
       color: var(--color-primary-500);
     }
   }
   
   &--active {
     .nav-item__icon {
       color: var(--color-primary-500);
       transform: scale(1.1);
     }
     
     .nav-item__text {
       color: var(--color-primary-500);
       font-weight: $font-weight-semibold;
     }
     
     .icon--chinese {
       color: var(--color-primary-500);
     }
   }

  // BEM 元素 - 导航文本
   &__text {
     font-size: $font-size-xs;
     font-weight: $font-weight-medium;
     color: $color-gray-600;
     position: relative;
     z-index: $z-index-base;
     transition: all 0.2s ease;
     text-align: center;
     line-height: $line-height-tight;
   }
}

// 图标样式
.icon {
  transition: all 0.2s ease;
  
  &--chinese {
    font-family: $font-family-chinese;
    font-weight: $font-weight-semibold;
    font-size: 1.2em;
    color: $color-gray-600;
  }
  
  &--emoji {
    font-family: $font-family-emoji;
  }
}

.nav-item {
  
  // BEM 元素 - 徽章
  &__badge {
    position: absolute;
    top: 2px;
    right: $spacing-2;
    background: linear-gradient(45deg, $color-red-500, $color-orange-500);
    color: $color-white;
    font-size: $font-size-xs;
    font-weight: $font-weight-semibold;
    padding: 2px $spacing-1_5;
    border-radius: $border-radius-full;
    min-width: 16px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    z-index: var(--z-index-tooltip);
    animation: pulse 2s infinite;
  }

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

  // 响应式设计
  @media (max-width: 480px) {
    min-width: 50px;
    padding: $spacing-1_5 $spacing-2;
    
    .nav-item__icon {
      font-size: $font-size-xl;
    }
    
    .nav-item__text {
      font-size: $font-size-2xs;
    }
  }
  
  // 深色模式支持
  @media (prefers-color-scheme: dark) {
    .nav-item__text {
      color: $color-gray-300;
    }
    
    &:hover .nav-item__text {
      color: $color-white;
    }
    
    .icon--chinese {
      color: $color-gray-300;
    }
    
    &:hover .icon--chinese,
    &.nav-item--active .icon--chinese {
      color: var(--color-primary-500);
    }
  }
  
  // 无障碍支持
  @media (prefers-reduced-motion: reduce) {
    &, .nav-item__icon, .nav-item__text {
      transition: none;
    }
    
    &::before {
      display: none;
    }
    
    .nav-item__badge {
      animation: none;
    }
  }
  
  // 焦点状态
  &:focus {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }
  
  &:focus:not(:focus-visible) {
    outline: none;
  }
  
  // 触摸设备优化
  @media (hover: none) and (pointer: coarse) {
    padding: $spacing-2_5 $spacing-3;
    
    &:hover {
      transform: none;
      
      .nav-item__icon {
        transform: none;
      }
    }
  }
}
</style>

