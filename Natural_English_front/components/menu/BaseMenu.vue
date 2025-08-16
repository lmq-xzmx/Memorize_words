<template>
  <transition
    :name="transitionName"
    appear
    mode="out-in"
    @enter="onEnter"
    @after-enter="onAfterEnter"
    @leave="onLeave"
    @after-leave="onAfterLeave"
  >
    <div 
      v-if="visible" 
      ref="menuRef"
      :class="menuClasses"
      :style="menuStyle"
      :data-menu-type="dataMenuType"
      v-bind="$attrs"
      @click.stop
    >
      <slot></slot>
    </div>
  </transition>
</template>

<script setup>
import { computed, toRefs, onMounted, onUnmounted, ref, watch } from 'vue'

// Props定义
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  position: {
    type: Object,
    default: () => ({}),
    validator: (value) => {
      return value && typeof value === 'object'
    }
  },
  menuType: {
    type: String,
    default: 'popup',
    validator: value => ['popup', 'dropdown', 'sidebar'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: value => ['small', 'medium', 'large'].includes(value)
  },
  zIndex: {
    type: [Number, String],
    default: 1001,
    validator: (value) => {
      if (typeof value === 'number') {
        return value > 0
      }
      if (typeof value === 'string') {
        return value.includes('var(--') || !isNaN(Number(value))
      }
      return false
    }
  },
  dataMenuType: {
    type: String,
    default: '',
    required: false
  }
})

// 响应式解构
const { visible, position, menuType, size, zIndex, dataMenuType } = toRefs(props)

// 菜单元素引用
const menuRef = ref(null)

// 计算菜单类名
const menuClasses = computed(() => {
  try {
    return [
      'base-menu',
      `base-menu--${menuType.value}`,
      `base-menu--${size.value}`,
      visible.value ? 'base-menu--visible' : 'base-menu--hidden'
    ]
  } catch (error) {
    console.warn('计算菜单类名时出错:', error)
    return ['base-menu']
  }
})

// 计算菜单样式
const menuStyle = computed(() => {
  try {
    const baseStyle = {
      zIndex: zIndex.value
    }
    
    // 安全地合并位置样式
    if (position.value && typeof position.value === 'object') {
      // 确保位置值是有效的
      const validPosition = {}
      
      if (typeof position.value.top === 'number' || typeof position.value.top === 'string') {
        validPosition.top = typeof position.value.top === 'number' ? `${position.value.top}px` : position.value.top
      }
      
      if (typeof position.value.left === 'number' || typeof position.value.left === 'string') {
        validPosition.left = typeof position.value.left === 'number' ? `${position.value.left}px` : position.value.left
      }
      
      if (typeof position.value.right === 'number' || typeof position.value.right === 'string') {
        validPosition.right = typeof position.value.right === 'number' ? `${position.value.right}px` : position.value.right
      }
      
      if (typeof position.value.bottom === 'number' || typeof position.value.bottom === 'string') {
        validPosition.bottom = typeof position.value.bottom === 'number' ? `${position.value.bottom}px` : position.value.bottom
      }
      
      if (typeof position.value.width === 'number' || typeof position.value.width === 'string') {
        validPosition.width = typeof position.value.width === 'number' ? `${position.value.width}px` : position.value.width
      }
      
      if (typeof position.value.height === 'number' || typeof position.value.height === 'string') {
        validPosition.height = typeof position.value.height === 'number' ? `${position.value.height}px` : position.value.height
      }
      
      return { ...baseStyle, ...validPosition }
    }
    
    return baseStyle
  } catch (error) {
    console.warn('计算菜单样式时出错:', error)
    return { zIndex: 1001 }
  }
})

// 计算过渡动画名称
const transitionName = computed(() => {
  try {
    switch (menuType.value) {
      case 'sidebar':
        return 'menu-slide'
      case 'dropdown':
        return 'menu-fade'
      case 'popup':
      default:
        return 'popup-fade'
    }
  } catch (error) {
    console.warn('计算过渡动画名称时出错:', error)
    return 'popup-fade'
  }
})

// 监听可见性变化，进行边界检查
watch(visible, (newVisible) => {
  if (newVisible && menuRef.value) {
    // 确保菜单在视口内
    setTimeout(() => {
      adjustMenuPosition()
    }, 0)
  }
})

// 调整菜单位置以确保在视口内
const adjustMenuPosition = () => {
  try {
    if (!menuRef.value) return
    
    const rect = menuRef.value.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    
    // 检查是否超出视口边界
    if (rect.right > viewportWidth || rect.bottom > viewportHeight || rect.left < 0 || rect.top < 0) {
      console.log('菜单位置需要调整，当前位置:', rect)
      // 这里可以触发重新定位的事件
    }
  } catch (error) {
    console.warn('调整菜单位置时出错:', error)
  }
}

// 动画事件处理
const onEnter = (el) => {
  // 进入动画开始时的处理
  el.style.transformOrigin = 'center top'
}

const onAfterEnter = (el) => {
  // 进入动画完成后的处理
  adjustMenuPosition()
}

const onLeave = (el) => {
  // 离开动画开始时的处理
}

const onAfterLeave = (el) => {
  // 离开动画完成后的处理
}

// 组件挂载时的处理
onMounted(() => {
  console.log('BaseMenu组件已挂载，类型:', menuType.value)
})

// 组件卸载时的清理
onUnmounted(() => {
  console.log('BaseMenu组件已卸载')
})

// 暴露给模板的属性
defineOptions({
  inheritAttrs: false
})
</script>

<style scoped>
/* 导入菜单设计系统 */
@import '../../assets/css/menu-variables.css';
@import '../../assets/css/menu-base.css';

/* BaseMenu 组件样式 - 使用统一的设计系统 */
.base-menu {
  /* 继承菜单容器基础样式 - 已在menu-base.css中定义 */
  /* BaseMenu特定样式覆盖 */
  border-radius: var(--menu-radius-large);
  box-shadow: var(--menu-shadow-lg);
  border: 1px solid var(--menu-border-light);
  padding: var(--base-menu-padding);
  transition: all var(--menu-transition-normal) var(--menu-ease-in-out);
}

/* 可见性状态 */
.base-menu--visible {
  pointer-events: auto;
  opacity: 1;
}

.base-menu--hidden {
  pointer-events: none;
  opacity: 0;
}

/* 菜单类型样式 - 使用统一的设计系统类 */
.base-menu--popup {
  /* 继承popup容器样式 - 已在menu-base.css中定义 */
  /* 特定样式覆盖 */
}

.base-menu--dropdown {
  /* 继承dropdown容器样式 - 已在menu-base.css中定义 */
  min-width: var(--base-menu-dropdown-min-width);
}

.base-menu--sidebar {
  /* 继承sidebar容器样式 - 已在menu-base.css中定义 */
  height: 100vh;
  width: var(--base-menu-sidebar-width);
  left: 0;
  z-index: var(--menu-z-sidebar);
  border-radius: 0;
  border-right: 1px solid var(--menu-border-light);
  border-left: none;
  border-top: none;
  border-bottom: none;
}

/* 菜单尺寸样式 - 使用统一的设计系统类 */
.base-menu--small {
  /* 继承小尺寸容器样式 - 已在menu-base.css中定义 */
  min-width: var(--base-menu-small-min-width);
  max-width: var(--base-menu-small-max-width);
  padding: var(--menu-spacing-sm);
}

.base-menu--medium {
  /* 默认中等尺寸 */
  min-width: var(--base-menu-medium-min-width);
  max-width: var(--base-menu-medium-max-width);
  padding: var(--menu-spacing-md);
}

.base-menu--large {
  /* 继承大尺寸容器样式 - 已在menu-base.css中定义 */
  min-width: var(--base-menu-large-min-width);
  max-width: var(--base-menu-large-max-width);
  padding: var(--menu-spacing-lg);
}

/* 过渡动画 - 使用统一的设计系统动画 */
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: all var(--menu-transition-normal) var(--menu-ease-in-out);
}

.popup-fade-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.popup-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.menu-slide-enter-active,
.menu-slide-leave-active {
  transition: all var(--menu-transition-normal) var(--menu-ease-in-out);
}

.menu-slide-enter-from {
  opacity: 0;
  transform: translateX(-100%);
}

.menu-slide-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all var(--menu-transition-fast) var(--menu-ease-in-out);
}

.menu-fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 悬停效果 - 使用统一的设计系统 */
.base-menu:hover {
  box-shadow: var(--menu-shadow-xl);
  transform: translateY(-2px);
}

/* 焦点状态 - 使用统一的设计系统 */
.base-menu:focus-within {
  outline: 2px solid var(--menu-border-focus);
  outline-offset: 2px;
}

/* 响应式设计 - 使用统一的设计系统 */
@media (max-width: 768px) {
  .base-menu--sidebar {
    width: 100vw;
    max-width: 100vw;
  }
  
  .base-menu--popup,
  .base-menu--dropdown {
    max-width: calc(100vw - var(--menu-spacing-xl));
    margin: 0 var(--menu-spacing-md);
    min-width: 280px;
  }
  
  .base-menu {
    min-width: var(--base-menu-mobile-min-width);
    padding: var(--menu-spacing-sm);
  }
}

/* 触摸设备优化 - 使用统一的设计系统 */
@media (hover: none) and (pointer: coarse) {
  .base-menu {
    min-height: 48px;
    padding: var(--menu-spacing-md) var(--menu-spacing-lg);
  }
  
  .base-menu:hover {
    transform: none;
  }
}

/* 无障碍支持 - 使用统一的设计系统 */
@media (prefers-reduced-motion: reduce) {
  .popup-fade-enter-active,
  .popup-fade-leave-active,
  .menu-slide-enter-active,
  .menu-slide-leave-active,
  .menu-fade-enter-active,
  .menu-fade-leave-active,
  .base-menu {
    transition: none;
  }
  
  .base-menu:hover {
    transform: none;
  }
}

/* 高对比度模式 - 使用统一的设计系统 */
@media (prefers-contrast: high) {
  .base-menu {
    border: 2px solid var(--menu-text-primary);
    box-shadow: none;
    background: var(--menu-bg-primary);
  }
}
</style>

