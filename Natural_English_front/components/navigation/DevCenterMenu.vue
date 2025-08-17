<template>
  <transition 
    name="menu-fade" 
    appear
    mode="out-in"
    @enter="onEnter"
    @after-enter="onAfterEnter"
  >
    <div 
      v-if="isVisible"
      ref="menuRef"
      class="dev-center-menu menu-container popup"
      :style="menuStyle"
      @click.stop
    >
    <!-- 头部 -->
    <div class="dev-center-header">
      <h3 class="header-title">
        <span class="header-icon">🛠️</span>
        开发中心
      </h3>
      <div class="header-stats">
        <span class="stats-text">{{ enabledCount }}/{{ tools.length }} 已启用</span>
        <div class="stats-bar">
          <div 
            class="stats-progress" 
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- 工具列表 -->
    <div class="dev-tools-list">
      <div 
        v-for="tool in tools" 
        :key="tool.id" 
        class="dev-tool-item"
        :class="{ 'dev-tool-item--enabled': tool.enabled }"
      >
        <div class="tool-info">
          <span class="tool-icon">{{ tool.icon }}</span>
          <div class="tool-details">
            <span class="tool-name">{{ tool.title }}</span>
            <span class="tool-desc">{{ tool.description }}</span>
            <div v-if="tool.tags" class="tool-tags">
              <span 
                v-for="tag in tool.tags" 
                :key="tag" 
                class="tool-tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="tool-actions">
          <!-- 开关 -->
          <div class="tool-switch" @click.stop>
            <input 
              type="checkbox" 
              :id="'dev-switch-' + tool.id"
              v-model="tool.enabled"
              @change="handleToggleTool(tool)"
              class="switch-input"
            >
            <label 
              :for="'dev-switch-' + tool.id" 
              class="switch-label"
              @click.stop
            ></label>
          </div>
          
          <!-- 状态指示器 -->
          <div class="tool-status">
            <span 
              :class="[
                'status-dot',
                tool.enabled ? 'status-dot--active' : 'status-dot--inactive'
              ]"
            ></span>
            <span class="status-text">
              {{ tool.enabled ? '已启用' : '未启用' }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部操作 -->
    <div class="dev-center-footer">
      <button 
        class="action-btn action-btn--secondary"
        @click="handleEnableAll"
        :disabled="allEnabled"
      >
        <span class="btn-icon">✅</span>
        全部启用
      </button>
      
      <button 
        class="action-btn action-btn--outline"
        @click="handleDisableAll"
        :disabled="noneEnabled"
      >
        <span class="btn-icon">❌</span>
        全部禁用
      </button>
    </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, toRefs } from 'vue'

// Props定义
const props = defineProps({
  tools: {
    type: Array,
    default: () => [],
    validator: (value) => {
      return Array.isArray(value) && value.every(tool => 
        tool && typeof tool === 'object' && 
        'id' in tool && 'title' in tool
      )
    }
  },
  enabledCount: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0
  }
})

// Emits定义
const emit = defineEmits(['toggle-tool', 'enable-all', 'disable-all'])

// 响应式解构
const { tools, enabledCount } = toRefs(props)

// 菜单可见性和位置
const isVisible = ref(true)
const menuRef = ref(null)
const position = ref({ top: '50px', left: '50px' })

// 菜单样式计算
const menuStyle = computed(() => {
  const style = {
    position: 'fixed',
    zIndex: 9999,
    transformOrigin: 'center top'
  }
  
  if (position.value) {
    Object.assign(style, position.value)
  }
  
  return style
})

// 动画事件处理
const onEnter = (el) => {
  // 进入动画开始时的处理
  el.style.transformOrigin = 'center top'
}

const onAfterEnter = (el) => {
  // 进入动画完成后的处理
  updatePosition()
}

// 更新位置
const updatePosition = () => {
  // 位置更新逻辑
}

// 计算进度百分比
const progressPercentage = computed(() => {
  try {
    if (!tools.value || tools.value.length === 0) return 0
    const percentage = Math.round((enabledCount.value / tools.value.length) * 100)
    return Math.max(0, Math.min(100, percentage)) // 确保在0-100范围内
  } catch (error) {
    console.warn('计算进度百分比时出错:', error)
    return 0
  }
})

// 检查是否全部启用
const allEnabled = computed(() => {
  try {
    return tools.value && tools.value.length > 0 && 
           tools.value.every(tool => tool && tool.enabled === true)
  } catch (error) {
    console.warn('检查全部启用状态时出错:', error)
    return false
  }
})

// 检查是否全部禁用
const noneEnabled = computed(() => {
  try {
    return !tools.value || tools.value.length === 0 || 
           tools.value.every(tool => tool && tool.enabled !== true)
  } catch (error) {
    console.warn('检查全部禁用状态时出错:', error)
    return true
  }
})

// 处理工具切换
const handleToggleTool = (tool) => {
  try {
    if (!tool || typeof tool !== 'object' || !('id' in tool)) {
      console.warn('无效的工具对象:', tool)
      return
    }
    console.log('切换工具:', tool.title || tool.id)
    emit('toggle-tool', tool)
  } catch (error) {
    console.error('切换工具时出错:', error)
  }
}

// 处理全部启用
const handleEnableAll = () => {
  try {
    if (allEnabled.value) {
      console.log('所有工具已经启用')
      return
    }
    console.log('启用所有工具')
    emit('enable-all')
  } catch (error) {
    console.error('启用所有工具时出错:', error)
  }
}

// 处理全部禁用
const handleDisableAll = () => {
  try {
    if (noneEnabled.value) {
      console.log('所有工具已经禁用')
      return
    }
    console.log('禁用所有工具')
    emit('disable-all')
  } catch (error) {
    console.error('禁用所有工具时出错:', error)
  }
}
</script>

<style lang="scss" scoped>
@use '../../assets/scss/index.scss';

.dev-center-menu {
  @include card;
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-purple-600));
  color: $color-white;
  border-radius: $border-radius-xl;
  overflow: hidden;
  min-width: 320px;
  max-width: 400px;
  @include shadow('2xl');
  
  // BEM 元素 - 头部
  @include bem-element('header') {
    padding: var(--spacing-6);
    background: rgba(var(--color-white), 0.1);
     border-bottom: 1px solid rgba(var(--color-white), 0.2);
    
    .header-title {
      @include flex-center;
      justify-content: flex-start;
      margin: 0 0 $spacing-4 0;
      @include text-style($font-size-lg, $font-weight-bold);
      
      .header-icon {
        margin-right: $spacing-2;
        font-size: $font-size-xl;
      }
    }
    
    .header-stats {
      @include flex-between;
      gap: $spacing-3;
      
      .stats-text {
        @include text-style($font-size-xs);
        opacity: 0.9;
        white-space: nowrap;
      }
      
      .stats-bar {
        flex: 1;
        height: 6px;
        background: rgba($color-white, 0.2);
        border-radius: $border-radius-sm;
        overflow: hidden;
        
        .stats-progress {
          height: 100%;
          background: linear-gradient(90deg, $color-yellow-400, $color-orange-400);
          border-radius: $border-radius-sm;
          @include transition;
        }
      }
    }
  }
}

.dev-tools-list {
  padding: $spacing-4;
  max-height: 300px;
  overflow-y: auto;
  
  // 自定义滚动条
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba($color-white, 0.1);
    border-radius: $border-radius-sm;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba($color-white, 0.3);
    border-radius: $border-radius-sm;
    
    &:hover {
      background: rgba($color-white, 0.5);
    }
  }
}

.dev-tool-item {
  @include flex-between;
  padding: $spacing-3 $spacing-4;
  margin-bottom: $spacing-3;
  background: rgba($color-white, 0.1);
  border: 1px solid rgba($color-white, 0.2);
  border-radius: $border-radius-lg;
  @include transition;
  cursor: pointer;
  
  &:hover {
    background: rgba($color-white, 0.15);
    transform: translateY(-1px);
    @include shadow('md');
  }
  
  @include bem-modifier('enabled') {
    background: rgba($color-white, 0.2);
    border-color: rgba($color-white, 0.4);
  }
  
  .tool-info {
    @include flex-center;
    justify-content: flex-start;
    flex: 1;
    gap: $spacing-3;
    
    .tool-icon {
      font-size: $font-size-xl;
      min-width: 24px;
      text-align: center;
    }
    
    .tool-details {
      flex: 1;
      
      .tool-name {
        display: block;
        @include text-style($font-size-sm, $font-weight-medium);
        margin-bottom: $spacing-1;
      }
      
      .tool-desc {
        display: block;
        @include text-style($font-size-xs);
        opacity: 0.8;
        line-height: $line-height-tight;
      }
      
      .tool-tags {
        @include flex-center;
        justify-content: flex-start;
        gap: $spacing-1;
        margin-top: $spacing-1;
        
        .tool-tag {
          @include text-style($font-size-2xs);
          padding: $spacing-1 $spacing-1_5;
          background: rgba($color-white, 0.2);
          border-radius: $border-radius-md;
          white-space: nowrap;
        }
      }
    }
  }
  
  .tool-actions {
    @include flex-center;
    gap: $spacing-3;
  }
}

// 开关样式
.tool-switch {
  position: relative;
  
  .switch-input {
    display: none;
    
    &:checked + .switch-label {
      background: $color-green-500;
      
      &::after {
        transform: translateX(20px);
      }
    }
  }
  
  .switch-label {
    display: block;
    width: 44px;
    height: 24px;
    background: rgba($color-white, 0.2);
    border-radius: $border-radius-lg;
    cursor: pointer;
    position: relative;
    @include transition;
    
    &::after {
      content: '';
      position: absolute;
      top: 2px;
      left: 2px;
      width: 20px;
      height: 20px;
      background: $color-white;
      border-radius: 50%;
      @include transition;
      @include shadow('sm');
    }
  }
}

// 状态指示器
.tool-status {
  @include flex-center;
  gap: $spacing-1_5;
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    @include transition;
    
    @include bem-modifier('active') {
      background: $color-green-400;
      box-shadow: 0 0 8px rgba($color-green-400, 0.6);
    }
    
    @include bem-modifier('inactive') {
      background: rgba($color-white, 0.3);
    }
  }
  
  .status-text {
    @include text-style($font-size-2xs);
    opacity: 0.8;
  }
}

// 底部操作样式
.dev-center-footer {
  padding: var(--spacing-4) var(--spacing-6);
  background: rgba(var(--color-white), 0.1);
   border-top: 1px solid rgba(var(--color-white), 0.2);
  @include flex-center;
  gap: var(--spacing-4);
}

.action-btn {
  flex: 1;
  @include flex-center;
  gap: $spacing-1_5;
  padding: $spacing-3 $spacing-4;
  border: none;
  border-radius: $border-radius-md;
  @include text-style($font-size-sm, $font-weight-medium);
  cursor: pointer;
  @include transition;
  
  @include bem-modifier('secondary') {
    background: rgba($color-white, 0.15);
    color: $color-white;
    border: 1px solid rgba($color-white, 0.3);
    
    &:hover:not(:disabled) {
      background: rgba($color-white, 0.25);
      transform: translateY(-1px);
    }
  }
  
  @include bem-modifier('outline') {
    background: transparent;
    color: $color-white;
    border: 1px solid rgba($color-white, 0.4);
    
    &:hover:not(:disabled) {
      background: rgba($color-white, 0.1);
      transform: translateY(-1px);
    }
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn-icon {
    font-size: $font-size-sm;
  }
}

// 过渡动画
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all $duration-normal cubic-bezier(0.4, 0, 0.2, 1);
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

// 响应式设计
@include respond-to('md') {
  .dev-center-menu {
    padding: $spacing-4;
    
    .dev-center-header {
      padding: $spacing-4 0;
    }
    
    .dev-tool-item {
      padding: $spacing-4;
      
      .tool-name {
        font-size: $font-size-base;
      }
      
      .tool-desc {
        font-size: $font-size-sm;
      }
    }
    
    .dev-center-footer {
      padding: $spacing-4;
      flex-direction: column;
      
      .action-btn {
        padding: $spacing-4;
        font-size: $font-size-base;
      }
    }
  }
}

@include respond-to('xs') {
  .dev-center-menu {
    min-width: 280px;
    max-width: calc(100vw - #{$spacing-8});
    
    .dev-center-header {
      padding: $spacing-4;
    }
    
    .dev-tools-list {
      padding: $spacing-3;
    }
    
    .dev-tool-item {
      padding: $spacing-2_5;
      
      .tool-name {
        font-size: $font-size-sm;
      }
      
      .tool-desc {
        font-size: $font-size-xs;
      }
    }
  }
}

// 深色模式支持
@media (prefers-color-scheme: dark) {
  .dev-center-menu {
    background: linear-gradient(135deg, $color-gray-800, $color-gray-900);
    backdrop-filter: blur(20px);
  }
}

// 无障碍支持
@media (prefers-reduced-motion: reduce) {
  .dev-tool-item,
  .action-btn,
  .tool-switch {
    transition: none;
  }
  
  .menu-fade-enter-active,
  .menu-fade-leave-active {
    transition: none;
  }
}
</style>

