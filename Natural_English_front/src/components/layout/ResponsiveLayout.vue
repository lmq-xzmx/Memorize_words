<template>
  <div class="responsive-layout" :class="layoutClasses">
    <!-- 移动端顶部导航栏 -->
    <header v-if="isMobile" class="mobile-header">
      <div class="header-content">
        <button 
          class="menu-toggle"
          @click="toggleSidebar"
          :aria-label="sidebarVisible ? '关闭菜单' : '打开菜单'"
        >
          <i :class="sidebarVisible ? 'fas fa-times' : 'fas fa-bars'"></i>
        </button>
        
        <div class="header-title">
          <slot name="header-title">
            <h1>{{ title }}</h1>
          </slot>
        </div>
        
        <div class="header-actions">
          <slot name="header-actions"></slot>
        </div>
      </div>
    </header>

    <!-- 侧边栏遮罩层 -->
    <div 
      v-if="isMobile && sidebarVisible" 
      class="sidebar-overlay"
      @click="closeSidebar"
    ></div>

    <!-- 主要内容区域 -->
    <div class="layout-container">
      <!-- 侧边栏 -->
      <aside 
        v-if="showSidebar"
        class="sidebar"
        :class="sidebarClasses"
      >
        <div class="sidebar-content">
          <slot name="sidebar">
            <!-- 默认侧边栏内容 -->
            <div class="sidebar-placeholder">
              <p>侧边栏内容</p>
            </div>
          </slot>
        </div>
      </aside>

      <!-- 主内容区域 -->
      <main class="main-content" :class="mainContentClasses">
        <div class="content-wrapper">
          <slot name="main">
            <!-- 默认主内容 -->
            <div class="main-placeholder">
              <p>主要内容区域</p>
            </div>
          </slot>
        </div>
      </main>
    </div>

    <!-- 移动端底部导航 -->
    <footer v-if="isMobile && showBottomNav" class="mobile-footer">
      <slot name="bottom-nav">
        <!-- 默认底部导航 -->
        <div class="bottom-nav-placeholder">
          <p>底部导航</p>
        </div>
      </slot>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  title?: string
  showSidebar?: boolean
  showBottomNav?: boolean
  sidebarWidth?: string
  breakpoint?: number
  collapsible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '应用标题',
  showSidebar: true,
  showBottomNav: true,
  sidebarWidth: '260px',
  breakpoint: 768,
  collapsible: true
})

const emit = defineEmits<{
  sidebarToggle: [visible: boolean]
  breakpointChange: [isMobile: boolean]
}>()

// 响应式状态
const windowWidth = ref(window.innerWidth)
const sidebarVisible = ref(false)

// 计算属性
const isMobile = computed(() => windowWidth.value < props.breakpoint)
const isTablet = computed(() => windowWidth.value >= props.breakpoint && windowWidth.value < 1024)
const isDesktop = computed(() => windowWidth.value >= 1024)

// 布局类名
const layoutClasses = computed(() => ({
  'is-mobile': isMobile.value,
  'is-tablet': isTablet.value,
  'is-desktop': isDesktop.value,
  'sidebar-visible': sidebarVisible.value,
  'has-sidebar': props.showSidebar,
  'has-bottom-nav': props.showBottomNav && isMobile.value
}))

// 侧边栏类名
const sidebarClasses = computed(() => ({
  'sidebar-mobile': isMobile.value,
  'sidebar-desktop': !isMobile.value,
  'sidebar-visible': sidebarVisible.value || !isMobile.value,
  'sidebar-collapsible': props.collapsible
}))

// 主内容区域类名
const mainContentClasses = computed(() => ({
  'with-sidebar': props.showSidebar && (!isMobile.value || sidebarVisible.value),
  'with-bottom-nav': props.showBottomNav && isMobile.value,
  'full-width': !props.showSidebar || (isMobile.value && !sidebarVisible.value)
}))

// 侧边栏显示控制
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
  emit('sidebarToggle', sidebarVisible.value)
}

const closeSidebar = () => {
  sidebarVisible.value = false
  emit('sidebarToggle', false)
}

// 窗口大小变化处理
const handleResize = () => {
  const newWidth = window.innerWidth
  const wasMobile = windowWidth.value < props.breakpoint
  const nowMobile = newWidth < props.breakpoint
  
  windowWidth.value = newWidth
  
  // 断点变化时的处理
  if (wasMobile !== nowMobile) {
    emit('breakpointChange', nowMobile)
    
    // 从移动端切换到桌面端时，关闭移动端侧边栏
    if (!nowMobile && sidebarVisible.value) {
      sidebarVisible.value = false
      emit('sidebarToggle', false)
    }
  }
}

// 键盘事件处理
const handleKeydown = (event: KeyboardEvent) => {
  // ESC键关闭侧边栏
  if (event.key === 'Escape' && isMobile.value && sidebarVisible.value) {
    closeSidebar()
  }
}

// 生命周期
onMounted(() => {
  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleKeydown)
})

// 暴露方法给父组件
defineExpose({
  toggleSidebar,
  closeSidebar,
  isMobile,
  isTablet,
  isDesktop,
  sidebarVisible
})
</script>

<style scoped>
.responsive-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-background);
}

/* 移动端顶部导航栏 */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: white;
  border-bottom: 1px solid var(--color-border-light);
  z-index: 1000;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
}

.menu-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  border-radius: 8px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
  
  &:hover {
    background: var(--color-background-light);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  i {
    font-size: 18px;
  }
}

.header-title {
  flex: 1;
  margin: 0 16px;
  
  h1 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 侧边栏遮罩层 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

/* 主要布局容器 */
.layout-container {
  display: flex;
  flex: 1;
  position: relative;
}

/* 侧边栏样式 */
.sidebar {
  background: white;
  border-right: 1px solid var(--color-border-light);
  transition: all 0.3s ease;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-desktop {
  position: relative;
  width: v-bind('props.sidebarWidth');
  flex-shrink: 0;
}

.sidebar-mobile {
  position: fixed;
  top: 56px;
  left: 0;
  width: 280px;
  height: calc(100vh - 56px);
  z-index: 1000;
  transform: translateX(-100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  
  &.sidebar-visible {
    transform: translateX(0);
  }
}

.sidebar-content {
  padding: 16px 0;
  height: 100%;
}

.sidebar-placeholder {
  padding: 16px;
  color: var(--color-text-secondary);
  text-align: center;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--color-background);
}

.main-content.with-bottom-nav {
  padding-bottom: 80px;
}

.is-mobile .main-content {
  padding-top: 56px;
}

.content-wrapper {
  flex: 1;
  padding: 16px;
  max-width: 100%;
  overflow-x: auto;
}

.main-placeholder {
  padding: 32px;
  text-align: center;
  color: var(--color-text-secondary);
}

/* 移动端底部导航 */
.mobile-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid var(--color-border-light);
  z-index: 1000;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding-bottom: env(safe-area-inset-bottom);
}

.bottom-nav-placeholder {
  padding: 16px;
  text-align: center;
  color: var(--color-text-secondary);
}

/* 平板适配 */
@media (min-width: 769px) and (max-width: 1023px) {
  .sidebar-desktop {
    width: 240px;
  }
  
  .content-wrapper {
    padding: 20px;
  }
}

/* 桌面端适配 */
@media (min-width: 1024px) {
  .content-wrapper {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .menu-toggle:hover {
    background: none;
  }
}

/* 横屏适配 */
@media (orientation: landscape) and (max-height: 500px) {
  .mobile-header {
    height: 48px;
  }
  
  .sidebar-mobile {
    top: 48px;
    height: calc(100vh - 48px);
  }
  
  .is-mobile .main-content {
    padding-top: 48px;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .mobile-header,
  .sidebar,
  .mobile-footer {
    background: #2a2a2a;
    border-color: #333333;
  }
  
  .sidebar-overlay {
    background: rgba(0, 0, 0, 0.7);
  }
}

/* 减少动画偏好适配 */
@media (prefers-reduced-motion: reduce) {
  .sidebar,
  .sidebar-overlay,
  .menu-toggle {
    transition: none;
  }
  
  .sidebar-overlay {
    animation: none;
    opacity: 1;
  }
}
</style>