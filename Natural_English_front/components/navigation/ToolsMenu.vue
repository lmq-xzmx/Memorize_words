<template>
  <transition 
    name="menu-fade" 
    appear
    mode="out-in"
    @enter="onEnter"
    @after-enter="onAfterEnter"
  >
    <div class="tools-menu">
    <!-- 开发中心入口 -->
    <MenuItem
      :item="devCenterItem"
      variant="primary"
      :expanded="showDevCenter"
      has-submenu
      @click="$emit('toggle-submenu', 'devCenter')"
    >
      <template #actions>
        <span class="menu-arrow">{{ showDevCenter ? '▼' : '▶' }}</span>
      </template>
    </MenuItem>
    
    <!-- 管理开发期首页（仅管理员可见） -->
    <MenuItem
      v-if="userInfo && userInfo.role === 'admin'"
      :item="adminDevItem"
      @click="$emit('navigate', '/admin/dev-index')"
    />
    
    <!-- 启用的工具列表 -->
    <div v-if="enabledTools.length > 0" class="enabled-tools">
      <div class="menu-divider"></div>
      <div class="tools-section-title">已启用的工具</div>
      
      <div 
        v-for="tool in enabledTools" 
        :key="tool.id" 
        class="tool-item"
        @click="handleToolSelect(tool)"
      >
        <input 
          type="radio" 
          :id="'radio-' + tool.id"
          :value="tool.id"
          v-model="selectedTool"
          class="tool-radio"
          @change="handleToolSelect(tool)"
        >
        <label :for="'radio-' + tool.id" class="tool-label">
          <span class="tool-icon">{{ tool.icon }}</span>
          <span class="tool-name">{{ tool.name || tool.title }}</span>
        </label>
      </div>
    </div>
    
    <!-- 无启用工具时的提示 -->
    <div v-else class="no-tools-section">
      <div class="menu-divider"></div>
      <div class="no-tools-tip">
        <span class="tip-icon">💡</span>
        <span class="tip-text">请在开发中心启用功能</span>
      </div>
    </div>
    </div>
  </transition>
</template>

<script>
import { ref, computed } from 'vue'
import MenuItem from '../menu/MenuItem.vue'

export default {
  name: 'ToolsMenu',
  components: {
    MenuItem
  },
  props: {
    userInfo: {
      type: Object,
      default: null
    },
    enabledTools: {
      type: Array,
      default: () => []
    },
    allTools: {
      type: Array,
      default: () => []
    },
    showDevCenter: {
      type: Boolean,
      default: false
    }
  },
  emits: ['navigate', 'toggle-submenu', 'tool-select'],
  setup(props, { emit }) {
    const selectedTool = ref(null)
    
    // 开发中心菜单项
    const devCenterItem = computed(() => ({
      id: 'dev-center',
      title: '开发中心',
      icon: '🛠️',
      description: `管理开发工具 (${props.enabledTools.length}/${props.allTools.length})`
    }))
    
    // 管理员开发页面菜单项
    const adminDevItem = computed(() => ({
      id: 'admin-dev',
      title: '管理开发期首页',
      icon: '⚙️',
      description: '管理员专用功能'
    }))
    
    // 处理工具选择
    const handleToolSelect = (tool) => {
      selectedTool.value = tool.id
      emit('tool-select', tool)
      emit('navigate', tool.path)
    }
    
    // 动画事件处理
    const onEnter = (el) => {
      // 进入动画开始时的处理
      el.style.transformOrigin = 'center top'
    }
    
    const onAfterEnter = (el) => {
      // 进入动画完成后的处理
      // 可以在这里添加额外的动画完成逻辑
    }
    
    return {
      selectedTool,
      devCenterItem,
      adminDevItem,
      handleToolSelect,
      onEnter,
      onAfterEnter
    }
  }
}
</script>

<style scoped>
/* 导入菜单设计系统 */
@import '../../assets/css/menu-variables.css';
@import '../../assets/css/menu-base.css';

/* ToolsMenu 组件样式 - 使用统一的设计系统 */
.tools-menu {
  /* 继承菜单容器基础样式 - 已在menu-base.css中定义 */
  /* ToolsMenu特定样式覆盖 */
  min-width: var(--menu-tools-min-width);
  max-width: var(--menu-tools-max-width);
  padding: var(--menu-spacing-lg);
  transform-origin: center top;
}

/* 菜单过渡动画 */
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-fade-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.menu-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.menu-fade-enter-to,
.menu-fade-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* 工具菜单头部 */
.tools-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--menu-spacing-lg);
  padding-bottom: var(--menu-spacing-md);
  border-bottom: 1px solid var(--menu-border-light);
}

.tools-menu-title {
  font-size: var(--menu-font-size-md);
  font-weight: var(--menu-font-weight-semibold);
  color: var(--menu-color-primary);
  text-shadow: var(--menu-text-shadow);
}

.tools-count {
  background: var(--menu-bg-badge);
  color: var(--menu-color-primary);
  font-size: var(--menu-font-size-xs);
  padding: var(--menu-spacing-xs) var(--menu-spacing-sm);
  border-radius: var(--menu-radius-full);
  font-weight: var(--menu-font-weight-medium);
}

/* 工具列表样式 - 使用设计系统 */
.tools-list {
  display: flex;
  flex-direction: column;
  gap: var(--menu-spacing-sm);
}

.tool-item {
  /* 继承菜单项基础样式 - 已在menu-base.css中定义 */
  /* 工具项特定样式覆盖 */
  padding: var(--menu-spacing-md);
}

/* 工具项状态样式 - 继承基础样式 */
.tool-item:hover {
  /* 继承menu-item:hover基础样式 */
}

.tool-item.selected {
  /* 继承menu-item.is-active基础样式 - 已在menu-base.css中定义 */
}

.tool-radio {
  margin-right: var(--menu-spacing-md);
  width: var(--menu-icon-size-sm);
  height: var(--menu-icon-size-sm);
  accent-color: var(--menu-color-accent);
}

.tool-label {
  flex: 1;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: var(--menu-spacing-xs);
}

.tool-name {
  font-size: var(--menu-font-size-sm);
  font-weight: var(--menu-font-weight-medium);
  color: var(--menu-color-primary);
  text-shadow: var(--menu-text-shadow);
}

.tool-description {
  font-size: var(--menu-font-size-xs);
  color: var(--menu-color-secondary);
  line-height: var(--menu-line-height-tight);
}

.tool-status {
  display: flex;
  align-items: center;
  gap: var(--menu-spacing-xs);
  margin-left: var(--menu-spacing-sm);
}

.status-badge {
  font-size: var(--menu-font-size-xs);
  padding: 2px var(--menu-spacing-xs);
  border-radius: var(--menu-radius-md);
  font-weight: var(--menu-font-weight-medium);
}

.status-badge.enabled {
  background: var(--menu-bg-success);
  color: var(--menu-color-primary);
}

.status-badge.disabled {
  background: var(--menu-bg-badge);
  color: var(--menu-color-secondary);
}

/* 菜单分隔线 - 使用基础样式 */
.menu-divider {
  /* 继承menu-divider基础样式 */
  /* 继承menu-divider基础样式 - 已在menu-base.css中定义 */
}

/* 无工具提示 */
.no-tools-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--menu-spacing-xl) var(--menu-spacing-lg);
  text-align: center;
  color: var(--menu-text-secondary);
}

.tip-icon {
  font-size: var(--menu-font-size-xl);
  margin-right: var(--menu-spacing-sm);
}

.tip-text {
  font-size: var(--menu-font-size-sm);
  font-weight: var(--menu-font-weight-medium);
}

/* 开发中心项目样式 */
.dev-center-item {
  background: var(--menu-bg-primary);
  border-color: var(--menu-border-primary);
  margin-bottom: var(--menu-spacing-sm);
}

.dev-center-item:hover {
  background: var(--menu-bg-primary-hover);
  box-shadow: var(--menu-shadow-primary);
}

.dev-center-icon {
  font-size: var(--menu-icon-size-md);
  margin-right: var(--menu-spacing-md);
}

.dev-center-title {
  flex: 1;
  font-size: var(--menu-font-size-sm);
  font-weight: var(--menu-font-weight-semibold);
  color: var(--menu-color-primary);
}

.dev-center-arrow {
  font-size: var(--menu-font-size-xs);
  color: var(--menu-color-secondary);
  transition: transform var(--menu-transition-normal);
}

.dev-center-item.expanded .dev-center-arrow {
  transform: rotate(90deg);
}

/* 管理员开发项目样式 */
.admin-dev-item {
  background: var(--menu-bg-danger);
  border-color: var(--menu-border-danger);
}

.admin-dev-item:hover {
  background: var(--menu-bg-danger-hover);
  box-shadow: var(--menu-shadow-danger);
}

/* ToolsMenu组件特定样式覆盖 */
/* 响应式设计 */
@media (max-width: 768px) {
  .tools-menu {
    min-width: var(--menu-tools-min-width-mobile);
    padding: var(--menu-spacing-md);
  }
  
  .no-tools-tip {
    padding: var(--menu-spacing-lg) var(--menu-spacing-md);
  }
}

/* 所有其他样式（焦点、无障碍、高对比度等）都已在menu-base.css中定义 */
</style>

