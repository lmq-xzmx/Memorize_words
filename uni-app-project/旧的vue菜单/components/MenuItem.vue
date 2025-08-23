<template>
  <div class="menu-item" :class="menuItemClasses">
    <!-- 主菜单项 -->
    <div 
      class="menu-item-content"
      @click="handleClick"
      :title="collapsed ? menu.title : ''"
    >
      <div class="menu-icon">
        <i :class="menu.icon || 'icon-default'"></i>
      </div>
      
      <div class="menu-text" v-if="!collapsed">
        <span class="menu-title">{{ menu.title }}</span>
        <span class="menu-subtitle" v-if="menu.subtitle">{{ menu.subtitle }}</span>
      </div>
      
      <div class="menu-actions" v-if="!collapsed">
        <!-- 徽章 -->
        <span 
          v-if="menu.badge" 
          class="menu-badge"
          :class="`badge-${menu.badge.type || 'default'}`"
        >
          {{ menu.badge.text }}
        </span>
        
        <!-- 展开/折叠按钮 -->
        <button 
          v-if="hasChildren"
          class="expand-btn"
          @click.stop="handleToggle"
          :class="{ 'expanded': expanded }"
        >
          <i class="icon-chevron"></i>
        </button>
      </div>
    </div>
    
    <!-- 子菜单 -->
    <transition name="submenu">
      <div v-if="hasChildren && expanded && !collapsed" class="submenu">
        <menu-item
          v-for="child in menu.children"
          :key="child.id"
          :menu="child"
          :active="active && activeChild === child.id"
          :collapsed="false"
          :compact="true"
          :level="level + 1"
          @click="$emit('click', $event)"
          @toggle="$emit('toggle', $event)"
        />
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'MenuItem',
  
  props: {
    // 菜单数据
    menu: {
      type: Object,
      required: true
    },
    
    // 是否激活
    active: {
      type: Boolean,
      default: false
    },
    
    // 是否折叠
    collapsed: {
      type: Boolean,
      default: false
    },
    
    // 是否展开
    expanded: {
      type: Boolean,
      default: false
    },
    
    // 紧凑模式
    compact: {
      type: Boolean,
      default: false
    },
    
    // 菜单层级
    level: {
      type: Number,
      default: 0
    }
  },
  
  computed: {
    // 菜单项样式类
    menuItemClasses() {
      return {
        'active': this.active,
        'collapsed': this.collapsed,
        'compact': this.compact,
        'has-children': this.hasChildren,
        'expanded': this.expanded,
        'disabled': this.menu.disabled,
        [`level-${this.level}`]: true
      }
    },
    
    // 是否有子菜单
    hasChildren() {
      return this.menu.children && this.menu.children.length > 0
    },
    
    // 当前激活的子菜单
    activeChild() {
      if (!this.hasChildren) return null
      
      const currentPath = this.$route?.path
      if (!currentPath) return null
      
      const activeChild = this.menu.children.find(child => 
        currentPath === child.path || currentPath.startsWith(child.path + '/')
      )
      
      return activeChild?.id || null
    }
  },
  
  methods: {
    /**
     * 处理菜单点击
     */
    handleClick() {
      if (this.menu.disabled) {
        return
      }
      
      // 如果有子菜单且在折叠状态，则展开子菜单
      if (this.hasChildren && this.collapsed) {
        this.handleToggle()
        return
      }
      
      // 如果有路径，则触发导航
      if (this.menu.path) {
        this.$emit('click', this.menu)
      } else if (this.hasChildren) {
        // 如果没有路径但有子菜单，则切换展开状态
        this.handleToggle()
      }
    },
    
    /**
     * 处理展开/折叠切换
     */
    handleToggle() {
      if (this.hasChildren) {
        this.$emit('toggle', this.menu)
      }
    }
  }
}
</script>

<style scoped>
.menu-item {
  margin-bottom: 2px;
}

.menu-item-content {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 8px;
  margin: 0 8px;
  transition: all 0.2s ease;
  position: relative;
  min-height: 48px;
}

.menu-item-content:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(2px);
}

.menu-item.active > .menu-item-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.menu-item.disabled > .menu-item-content {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-item.disabled > .menu-item-content:hover {
  background: transparent;
  transform: none;
}

/* 折叠状态 */
.menu-item.collapsed .menu-item-content {
  justify-content: center;
  padding: 12px;
  margin: 0 4px;
}

/* 紧凑模式 */
.menu-item.compact .menu-item-content {
  min-height: 40px;
  padding: 8px 16px;
}

/* 层级缩进 */
.menu-item.level-1 .menu-item-content {
  padding-left: 32px;
}

.menu-item.level-2 .menu-item-content {
  padding-left: 48px;
}

.menu-item.level-3 .menu-item-content {
  padding-left: 64px;
}

/* 菜单图标 */
.menu-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  flex-shrink: 0;
}

.menu-item.collapsed .menu-icon {
  margin-right: 0;
}

.menu-item.active .menu-icon {
  color: #ffffff;
}

/* 菜单文本 */
.menu-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.menu-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 菜单操作 */
.menu-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* 徽章 */
.menu-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-default {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.badge-primary {
  background: #3182ce;
  color: #ffffff;
}

.badge-success {
  background: #38a169;
  color: #ffffff;
}

.badge-warning {
  background: #d69e2e;
  color: #ffffff;
}

.badge-danger {
  background: #e53e3e;
  color: #ffffff;
}

.badge-info {
  background: #3182ce;
  color: #ffffff;
}

/* 展开按钮 */
.expand-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.expand-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.expand-btn.expanded {
  transform: rotate(90deg);
}

/* 子菜单 */
.submenu {
  overflow: hidden;
}

.submenu .menu-item-content {
  background: rgba(0, 0, 0, 0.2);
  margin-left: 16px;
  margin-right: 8px;
}

.submenu .menu-item-content:hover {
  background: rgba(255, 255, 255, 0.1);
}

.submenu .menu-item.active > .menu-item-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 过渡动画 */
.submenu-enter-active,
.submenu-leave-active {
  transition: all 0.3s ease;
}

.submenu-enter-from,
.submenu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
}

.submenu-enter-to,
.submenu-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 500px;
}

/* 图标 */
.icon-default::before { content: '📄'; }
.icon-chevron::before { content: '▶'; }

/* 常用菜单图标 */
.icon-dashboard::before { content: '📊'; }
.icon-users::before { content: '👥'; }
.icon-courses::before { content: '📚'; }
.icon-grades::before { content: '📝'; }
.icon-calendar::before { content: '📅'; }
.icon-messages::before { content: '💬'; }
.icon-reports::before { content: '📈'; }
.icon-settings::before { content: '⚙'; }
.icon-profile::before { content: '👤'; }
.icon-help::before { content: '❓'; }
.icon-notifications::before { content: '🔔'; }
.icon-files::before { content: '📁'; }
.icon-analytics::before { content: '📊'; }
.icon-tools::before { content: '🔧'; }
.icon-admin::before { content: '🛡'; }

/* 响应式设计 */
@media (max-width: 768px) {
  .menu-item-content {
    padding: 10px 12px;
    min-height: 44px;
  }
  
  .menu-icon {
    width: 20px;
    height: 20px;
    font-size: 16px;
    margin-right: 10px;
  }
  
  .menu-title {
    font-size: 13px;
  }
  
  .menu-subtitle {
    font-size: 11px;
  }
}
</style>