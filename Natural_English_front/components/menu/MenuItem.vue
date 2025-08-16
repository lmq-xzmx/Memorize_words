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

<style scoped>
/* 导入菜单设计系统 */
@import '../../assets/css/menu-variables.css';
@import '../../assets/css/menu-base.css';

/* MenuItem 组件样式 - 使用统一的设计系统 */
.menu-item {
  /* 继承菜单项基础样式 - 已在menu-base.css中定义 */
  /* MenuItem特定样式覆盖 */
  margin-bottom: var(--menu-spacing-xs);
  position: relative;
  overflow: hidden;
}

/* MenuItem状态样式 - 继承基础样式 */
.menu-item:hover {
  /* 继承menu-item:hover基础样式 */
}

.menu-item:active {
  /* 继承menu-item:active基础样式 */
}

.menu-item.is-active {
  /* 继承menu-item.is-active基础样式 */
}

.menu-item.is-disabled {
  /* 继承menu-item.is-disabled基础样式 */
}

.menu-item.is-expandable {
  /* 继承menu-item.is-expandable基础样式 */
}

/* 菜单项变体样式 - 继承基础样式 */
.menu-item.menu-item--primary {
  /* 继承menu-item--primary基础样式 */
}

.menu-item.menu-item--secondary {
  /* 继承menu-item--secondary基础样式 */
}

.menu-item.menu-item--danger {
  /* 继承menu-item--danger基础样式 */
}

/* 菜单项内部元素样式 - 继承基础样式 */
.menu-item__icon {
  /* 继承menu-item__icon基础样式 */
}

.menu-item__content {
  /* 继承menu-item__content基础样式 */
}

.menu-item__title {
  /* 继承menu-item__title基础样式 */
}

.menu-item__desc {
  /* 继承menu-item__desc基础样式 */
}

.menu-item__actions {
  /* 继承menu-item__actions基础样式 */
}

.menu-item__arrow {
  /* 继承menu-item__arrow基础样式 */
}

.menu-item.is-expandable .menu-item__arrow {
  /* 继承基础样式 */
}

.menu-item.is-expandable.is-expanded .menu-item__arrow {
  /* 继承基础样式 */
}

/* MenuItem组件特定样式覆盖 */
/* 所有基础样式、响应式设计、无障碍支持等都已在menu-base.css中定义 */
/* 这里只保留组件特定的样式覆盖 */
</style>

