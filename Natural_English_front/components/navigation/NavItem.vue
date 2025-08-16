<template>
  <div 
    :class="navItemClasses"
    @click="handleClick"
    @mouseenter="$emit('hover', item)"
    @mouseleave="$emit('leave', item)"
  >
    <div class="nav-icon">
      <span :class="iconClasses">{{ item.icon }}</span>
    </div>
    <div class="nav-text">{{ item.title }}</div>
    <div v-if="showBadge" class="nav-badge">{{ badgeText }}</div>
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
          'chinese-icon': this.isChinese(this.item.icon),
          'emoji-icon': this.isEmoji(this.item.icon)
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

<style scoped>
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-width: 60px;
  height: 50px;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.3s ease;
}

.nav-item:hover::before {
  opacity: 0.1;
  transform: scale(1);
}

.nav-item--active::before {
  opacity: 0.2;
  transform: scale(1);
}

.nav-item:active {
  transform: scale(0.95);
}

.nav-item--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-item--disabled:hover::before {
  opacity: 0;
}

/* 导航项图标 */
.nav-icon {
  font-size: 24px;
  margin-bottom: 4px;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-item--active .nav-icon {
  color: #667eea;
  transform: scale(1.1);
}

.icon {
  transition: all 0.3s ease;
}

.chinese-icon {
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-weight: 600;
  font-size: 1.2em;
  color: #666;
}

.nav-item--active .chinese-icon {
  color: #667eea;
}

.nav-item:hover .chinese-icon {
  color: #667eea;
}

.emoji-icon {
  font-family: 'Apple Color Emoji', 'Segoe UI Emoji', sans-serif;
}

/* 导航项文本 */
.nav-text {
  font-size: 11px;
  font-weight: 500;
  color: #666;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
  text-align: center;
  line-height: 1.2;
}

.nav-item:hover .nav-text {
  color: #333;
}

.nav-item--active .nav-text {
  color: #667eea;
  font-weight: 600;
}

/* 徽章样式 */
.nav-badge {
  position: absolute;
  top: 2px;
  right: 8px;
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
  z-index: 2;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .nav-item {
    min-width: 50px;
    padding: 6px 8px;
  }
  
  .nav-icon {
    font-size: 20px;
  }
  
  .nav-text {
    font-size: 10px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .nav-text {
    color: #ccc;
  }
  
  .nav-item:hover .nav-text {
    color: #fff;
  }
  
  .chinese-icon {
    color: #ccc;
  }
  
  .nav-item:hover .chinese-icon,
  .nav-item--active .chinese-icon {
    color: #667eea;
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  .nav-item,
  .nav-icon,
  .nav-text {
    transition: none;
  }
  
  .nav-item::before {
    display: none;
  }
  
  .nav-badge {
    animation: none;
  }
}

/* 焦点状态 */
.nav-item:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

.nav-item:focus:not(:focus-visible) {
  outline: none;
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .nav-item {
    padding: 10px 12px;
  }
  
  .nav-item:hover {
    transform: none;
  }
  
  .nav-item:hover .nav-icon {
    transform: none;
  }
}
</style>

