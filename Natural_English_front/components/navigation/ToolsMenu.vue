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

<style lang="scss" scoped>
@use '../../styles/index.scss';

.tools-menu {
    @include card;
    @include transition();
    
    min-width: 280px;
    max-width: 320px;
    padding: var(--spacing-6);
    transform-origin: center top;
    background: var(--color-white);
     border: 1px solid var(--color-gray-200);
     border-radius: var(--border-radius-xl);
     box-shadow: var(--shadow-2xl);
    
    @include respond-to(mobile) {
      min-width: 240px;
      padding: $spacing-4;
    }
  }

// 菜单过渡动画
.menu-fade-enter-active,
.menu-fade-leave-active {
  @include transition(all, $duration-normal, $easing-smooth);
}

.menu-fade-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(-#{$spacing-3});
}

.menu-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-#{$spacing-3});
}

.menu-fade-enter-to,
.menu-fade-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

// 工具菜单头部
.tools-menu {
  .tools-menu__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-6);
    padding-bottom: var(--spacing-4);
     border-bottom: 1px solid var(--color-gray-200);
  }
  
  .tools-menu__title {
    font-size: var(--font-size-md);
    font-weight: var(--font-weight-semibold);
    color: var(--color-gray-900);
  }
  
  .tools-menu__count {
    background: var(--color-gray-100);
    color: var(--color-gray-700);
    font-size: var(--font-size-xs);
    padding: var(--spacing-1) var(--spacing-2);
    border-radius: var(--border-radius-full);
    font-weight: var(--font-weight-medium);
  }
}

// 启用的工具列表
.enabled-tools {
  margin-top: var(--spacing-4);
}

.tools-section-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-gray-700);
  margin-bottom: var(--spacing-3);
  padding: 0 var(--spacing-2);
}

.tool-item {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  padding: $spacing-3;
  border-radius: $border-radius-md;
  cursor: pointer;
  
  &:hover {
    background: $color-gray-50;
  }
  
  &.selected {
    background: $color-primary-50;
    border-color: $color-primary-200;
  }
}

.tool-radio {
  margin-right: $spacing-4;
  width: $size-4;
  height: $size-4;
  accent-color: var(--color-primary-500);
}

.tool-label {
  flex: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: $spacing-2;
}

.tool-icon {
  font-size: var(--font-size-lg);
  margin-right: var(--spacing-2);
}

.tool-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-gray-900);
}

// 菜单分隔线
.menu-divider {
  height: 1px;
  background: var(--color-gray-200);
  margin: var(--spacing-4) 0;
  border: none;
}

// 无工具提示
.no-tools-section {
  margin-top: var(--spacing-4);
}

.no-tools-tip {
  @include flex-center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  
  padding: var(--spacing-8) var(--spacing-6);
  text-align: center;
  color: var(--color-gray-500);
  
  @include respond-to(mobile) {
    padding: var(--spacing-6) var(--spacing-4);
  }
}

.tip-icon {
  font-size: var(--font-size-xl);
  margin-right: var(--spacing-2);
}

.tip-text {
  color: var(--color-gray-600);
}

// 菜单箭头
.menu-arrow {
  @include transition(transform);
  font-size: $font-size-xs;
  color: $color-gray-500;
  
  .expanded & {
    transform: rotate(90deg);
  }
}
</style>

