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

<style scoped>
@import '../../assets/css/menu-variables.css';
@import '../../assets/css/menu-base.css';

.dev-center-menu {
  background: var(--menu-bg-gradient-secondary);
  color: var(--menu-text-color-inverse);
  border-radius: var(--menu-border-radius-large);
  overflow: hidden;
  min-width: 320px;
  max-width: 400px;
}

/* 头部样式 */
.dev-center-header {
  padding: var(--menu-padding-large);
  background: var(--menu-item-bg-transparent);
  border-bottom: 1px solid var(--menu-border-color-light);
}

.header-title {
  display: flex;
  align-items: center;
  margin: 0 0 var(--menu-spacing-medium) 0;
  font-size: var(--menu-text-size-large);
  font-weight: var(--menu-text-weight-bold);
}

.header-icon {
  margin-right: 8px;
  font-size: 20px;
}

.header-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.stats-text {
  font-size: 12px;
  opacity: 0.9;
  white-space: nowrap;
}

.stats-bar {
  flex: 1;
  height: 6px;
  background: var(--menu-item-bg-hover-transparent);
  border-radius: var(--menu-border-radius-tiny);
  overflow: hidden;
}

.stats-progress {
  height: 100%;
  background: var(--menu-accent-gradient);
  border-radius: var(--menu-border-radius-tiny);
  transition: var(--menu-transition-base);
}

/* 工具列表样式 */
.dev-tools-list {
  padding: var(--menu-padding-horizontal);
  max-height: 300px;
  overflow-y: auto;
}

.dev-tool-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--menu-item-padding-vertical) var(--menu-item-padding-horizontal);
  margin-bottom: var(--menu-spacing-small);
  background: var(--menu-item-bg-transparent);
  border: 1px solid var(--menu-border-color-transparent);
  border-radius: var(--menu-border-radius-medium);
  transition: var(--menu-transition-base);
  cursor: pointer;
}

.dev-tool-item:hover {
  background: var(--menu-item-bg-hover-transparent);
  transform: var(--menu-item-transform-hover);
  box-shadow: var(--menu-shadow-subtle);
}

.dev-tool-item--enabled {
  background: var(--menu-item-bg-active);
  border-color: var(--menu-border-color-light);
}

.tool-info {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 12px;
}

.tool-icon {
  font-size: 20px;
  min-width: 24px;
  text-align: center;
}

.tool-details {
  flex: 1;
}

.tool-name {
  display: block;
  font-size: var(--menu-text-size-medium);
  font-weight: var(--menu-text-weight-medium);
  margin-bottom: 2px;
}

.tool-desc {
  display: block;
  font-size: var(--menu-text-size-small);
  opacity: var(--menu-text-opacity-muted);
  line-height: 1.3;
}

.tool-tags {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.tool-tag {
  font-size: var(--menu-text-size-tiny);
  padding: 2px 6px;
  background: var(--menu-item-bg-hover-transparent);
  border-radius: var(--menu-border-radius-small);
  white-space: nowrap;
}

.tool-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 开关样式 */
.tool-switch {
  position: relative;
}

.switch-input {
  display: none;
}

.switch-label {
  display: block;
  width: 44px;
  height: 24px;
  background: var(--menu-item-bg-hover-transparent);
  border-radius: var(--menu-border-radius-medium);
  cursor: pointer;
  position: relative;
  transition: var(--menu-transition-base);
}

.switch-label::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: var(--menu-text-color-inverse);
  border-radius: 50%;
  transition: var(--menu-transition-base);
  box-shadow: var(--menu-shadow-subtle);
}

.switch-input:checked + .switch-label {
  background: var(--menu-accent-color);
}

.switch-input:checked + .switch-label::after {
  transform: translateX(20px);
}

/* 状态指示器 */
.tool-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.status-dot--active {
  background: var(--menu-accent-color);
  box-shadow: var(--menu-shadow-glow);
}

.status-dot--inactive {
  background: var(--menu-item-bg-variant);
}

.status-text {
  font-size: 11px;
  opacity: 0.8;
}

/* 底部操作样式 */
.dev-center-footer {
  padding: var(--menu-padding-horizontal) var(--menu-padding-large);
  background: var(--menu-item-bg-transparent);
  border-top: 1px solid var(--menu-border-color-light);
  display: flex;
  gap: var(--menu-spacing-medium);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: var(--menu-item-padding-vertical) var(--menu-padding-horizontal);
  border: none;
  border-radius: var(--menu-border-radius-small);
  font-size: var(--menu-text-size-small);
  font-weight: var(--menu-text-weight-medium);
  cursor: pointer;
  transition: var(--menu-transition-base);
}

.action-btn--secondary {
  background: var(--menu-item-bg-hover-transparent);
  color: var(--menu-text-color-inverse);
  border: 1px solid var(--menu-border-color-light);
}

.action-btn--secondary:hover:not(:disabled) {
  background: var(--menu-item-bg-active);
  transform: var(--menu-item-transform-hover);
}

.action-btn--outline {
  background: transparent;
  color: var(--menu-text-color-inverse);
  border: 1px solid var(--menu-border-color-variant);
}

.action-btn--outline:hover:not(:disabled) {
  background: var(--menu-item-bg-transparent);
  transform: var(--menu-item-transform-hover);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 14px;
}

/* 滚动条样式 */
.dev-tools-list::-webkit-scrollbar {
  width: 4px;
}

.dev-tools-list::-webkit-scrollbar-track {
  background: var(--menu-item-bg-transparent);
  border-radius: var(--menu-border-radius-tiny);
}

.dev-tools-list::-webkit-scrollbar-thumb {
  background: var(--menu-border-color-light);
  border-radius: var(--menu-border-radius-tiny);
}

.dev-tools-list::-webkit-scrollbar-thumb:hover {
  background: var(--menu-item-bg-variant);
}

/* 过渡动画 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .dev-center-menu {
    padding: var(--menu-padding-horizontal);
  }
  
  .dev-center-header {
    padding: var(--menu-padding-horizontal) 0;
  }
  
  .dev-center-title {
    font-size: var(--menu-text-size-large);
  }
  
  .dev-tool-item {
    padding: var(--menu-spacing-medium);
  }
  
  .tool-name {
    font-size: var(--menu-text-size-base);
  }
  
  .tool-description {
    font-size: var(--menu-text-size-small);
  }
  
  .dev-center-footer {
    padding: var(--menu-spacing-medium) var(--menu-padding-horizontal);
    flex-direction: column;
  }
  
  .action-btn {
    padding: var(--menu-spacing-medium) var(--menu-padding-horizontal);
    font-size: var(--menu-text-size-base);
  }
}

@media (max-width: 480px) {
  .dev-center-menu {
    min-width: 280px;
    max-width: calc(100vw - 32px);
  }
  
  .dev-center-header {
    padding: 16px;
  }
  
  .dev-tools-list {
    padding: 12px;
  }
  
  .dev-tool-item {
    padding: 10px;
  }
  
  .tool-name {
    font-size: 13px;
  }
  
  .tool-desc {
    font-size: 11px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .dev-center-menu {
    background: var(--menu-bg-dark);
    backdrop-filter: var(--menu-backdrop-filter);
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  .dev-tool-item,
  .action-btn,
  .tool-switch {
    transition: var(--menu-transition-reduced);
  }
}
</style>

