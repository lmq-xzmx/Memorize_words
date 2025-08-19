<template>
  <div class="mobile-tab-bar-container" v-if="shouldShowTabBar">
    <!-- 底部导航栏 -->
    <div class="tab-bar">
      <div class="tab-container">
        <!-- 学习中心 -->
        <div 
          class="tab-item"
          :class="{ active: activeMenu === 'learning' }"
          @click="handleTabClick('learning', '/learning')"
        >
          <div class="tab-icon">
            <span class="icon chinese-icon">学</span>
          </div>
          <div class="tab-text">学习</div>
        </div>

        <!-- 工具中心 -->
        <div 
          class="tab-item"
          :class="{ active: activeMenu === 'tools' }"
          @click="handleToolsClick"
          ref="toolsTab"
        >
          <div class="tab-icon">
            <span class="icon chinese-icon">工</span>
          </div>
          <div class="tab-text">工具</div>
        </div>

        <!-- 词汇管理 -->
        <div 
          class="tab-item"
          :class="{ active: activeMenu === 'words' }"
          @click="toggleMenu('words')"
          ref="wordsTab"
        >
          <div class="tab-icon">
            <span class="icon chinese-icon">词</span>
          </div>
          <div class="tab-text">词汇</div>
        </div>

        <!-- 我的 -->
        <div 
          class="tab-item"
          :class="{ active: currentTab === '/profile' }"
          @click="navigateTo('/profile')"
        >
          <div class="tab-icon">
            <span class="icon">👤</span>
          </div>
          <div class="tab-text">我的</div>
        </div>
      </div>
    </div>

    <!-- 弹出层容器 -->
    <div class="popup-container">
      <!-- 工具菜单 -->
      <transition name="popup-fade">
        <div v-if="activeMenu === 'tools'" class="popup-menu tools-menu" :style="toolsMenuPosition" @click.stop>
          <!-- 开发中心菜单项 -->
          <div class="menu-item dev-center-item" @click.stop="toggleDevCenter">
            <span class="menu-icon">🛠️</span>
            <span class="menu-text">开发中心</span>
            <span class="menu-arrow">{{ showDevCenter ? '▼' : '▶' }}</span>
          </div>
          
          <!-- 启用的功能菜单项 -->
          <div v-if="enabledToolItems.length > 0" class="enabled-tools">
            <div class="menu-divider"></div>
            <div v-for="item in enabledToolItems" :key="item.id" class="tool-menu-item" @click.stop>
              <input 
                type="radio" 
                :id="'radio-' + item.id"
                :value="item.id"
                v-model="selectedTool"
                @change.stop="selectTool(item)"
                class="tool-radio"
              >
              <label :for="'radio-' + item.id" class="tool-label" @click.stop>
                <span class="tool-name">{{ item.name }}</span>
              </label>
            </div>
          </div>
          
          <!-- 无启用功能时的提示 -->
          <div v-else class="no-tools-tip">
            <div class="menu-divider"></div>
            <div class="tip-text">请在开发中心启用功能</div>
          </div>
        </div>
      </transition>

      <!-- 词汇弹出菜单 -->
      <transition name="popup-fade">
        <div v-if="activeMenu === 'words'" class="popup-menu words-menu" :style="wordsMenuPosition">
          <div class="menu-item" @click="navigateTo('/words/vocabulary')">
            <span class="menu-icon">📚</span>
            <span class="menu-text">词汇管理</span>
          </div>
          <div class="menu-item" @click="navigateTo('/words/practice')">
            <span class="menu-icon">✍️</span>
            <span class="menu-text">练习模式</span>
          </div>
          <div class="menu-item" @click="navigateTo('/words/review')">
            <span class="menu-icon">🔄</span>
            <span class="menu-text">复习中心</span>
          </div>
          <div class="menu-item" @click="navigateTo('/words/statistics')">
            <span class="menu-icon">📊</span>
            <span class="menu-text">学习统计</span>
          </div>
        </div>
      </transition>

      <!-- 开发中心二级菜单 -->
      <transition name="popup-fade">
        <div v-if="showDevCenter && activeMenu === 'tools'" class="popup-menu dev-center-menu" :style="devCenterMenuPosition" @click.stop>
          <div class="dev-center-header">
            <h3>开发中心 ({{ enabledToolItems.length }}/{{ allDevTools.length }})</h3>
          </div>
          <div class="dev-tool-list">
            <div v-for="tool in allDevTools" :key="tool.id" class="dev-tool-item">
              <div class="tool-info">
                <span class="tool-icon">{{ tool.icon }}</span>
                <div class="tool-details">
                  <span class="tool-name">{{ tool.title }}</span>
                  <span class="tool-desc">{{ tool.description }}</span>
                </div>
              </div>
              <div class="tool-switch" @click.stop>
                <input 
                  type="checkbox" 
                  :id="'dev-switch-' + tool.id"
                  v-model="tool.enabled"
                  @change.stop="toggleDevTool(tool)"
                >
                <label :for="'dev-switch-' + tool.id" class="switch-label" @click.stop></label>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- 遮罩层 -->
      <transition name="overlay-fade">
        <div v-if="activeMenu || showDevCenter" class="overlay" @click="handleOverlayClick"></div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

// 接口定义
interface ToolItem {
  id: string
  name: string
  title: string
  description: string
  path: string
  icon: string
  enabled: boolean
}

// Props
interface Props {
  current?: string
}

const props = withDefaults(defineProps<Props>(), {
  current: '/dashboard'
})

// 响应式数据
const route = useRoute()
const router = useRouter()
const store = useStore()

const currentTab = ref(props.current)
const activeMenu = ref<string | null>(null)
const showDevCenter = ref(false)
const selectedTool = ref<string | null>(null)
const toolsMenuPosition = ref({})
const wordsMenuPosition = ref({})
const devCenterMenuPosition = ref({})

// 开发工具配置
const allDevTools = ref<ToolItem[]>([
  {
    id: 'word-reading',
    name: '单词阅读',
    title: '单词阅读',
    description: '支持音频播放和进度跟踪的单词阅读功能',
    path: '/words/reading',
    icon: '📖',
    enabled: false
  },
  {
    id: 'word-learning',
    name: '单词学习',
    title: '单词学习',
    description: '展示单词详情和多种释义的学习页面',
    path: '/words/learning',
    icon: '📚',
    enabled: false
  },
  {
    id: 'word-spelling',
    name: '拼写练习',
    title: '拼写练习',
    description: '听音拼写练习，提升单词记忆效果',
    path: '/words/spelling',
    icon: '✍️',
    enabled: false
  },
  {
    id: 'grammar-check',
    name: '语法检查',
    title: '语法检查',
    description: '智能语法检查和纠错功能',
    path: '/tools/grammar',
    icon: '📝',
    enabled: false
  }
])

// 计算属性
const shouldShowTabBar = computed(() => {
  // 移动端或小屏幕设备显示底部导航
  return window.innerWidth <= 768 && store.getters['user/isAuthenticated']
})

const enabledToolItems = computed(() => {
  return allDevTools.value.filter(tool => tool.enabled)
})

// 方法
const handleTabClick = (menuType: string, path: string) => {
  activeMenu.value = null
  currentTab.value = path
  navigateTo(path)
}

const handleToolsClick = () => {
  toggleMenu('tools')
  calculateMenuPosition('tools')
}

const toggleMenu = (menuType: string) => {
  if (activeMenu.value === menuType) {
    activeMenu.value = null
    showDevCenter.value = false
  } else {
    activeMenu.value = menuType
    showDevCenter.value = false
    calculateMenuPosition(menuType)
  }
}

const toggleDevCenter = () => {
  showDevCenter.value = !showDevCenter.value
  if (showDevCenter.value) {
    calculateMenuPosition('devCenter')
  }
}

const selectTool = (tool: ToolItem) => {
  selectedTool.value = tool.id
  navigateTo(tool.path)
  activeMenu.value = null
}

const toggleDevTool = (tool: ToolItem) => {
  // 这里可以添加保存到后台的逻辑
  console.log(`工具 ${tool.name} 状态变更为: ${tool.enabled}`)
}

const navigateTo = (path: string) => {
  router.push(path)
  activeMenu.value = null
  showDevCenter.value = false
}

const handleOverlayClick = () => {
  activeMenu.value = null
  showDevCenter.value = false
}

const calculateMenuPosition = (menuType: string) => {
  // 计算弹出菜单位置
  const position = {
    bottom: '60px',
    right: '16px',
    left: 'auto'
  }
  
  switch (menuType) {
    case 'tools':
      toolsMenuPosition.value = position
      break
    case 'words':
      wordsMenuPosition.value = position
      break
    case 'devCenter':
      devCenterMenuPosition.value = {
        ...position,
        right: '200px'
      }
      break
  }
}

// 初始化当前标签
currentTab.value = route.path

// 监听路由变化
watch(() => route.path, (newPath) => {
  currentTab.value = newPath
})
</script>

<style lang="scss" scoped>
.mobile-tab-bar-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-bar {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.tab-container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  max-width: 500px;
  margin: 0 auto;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  min-width: 60px;
  min-height: 44px;
  justify-content: center;
  
  /* 移动端触摸优化 */
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  
  &:hover {
    background: rgba(59, 130, 246, 0.1);
  }
  
  &:active {
    transform: scale(0.95);
    background: rgba(59, 130, 246, 0.15);
  }
  
  &.active {
    background: rgba(59, 130, 246, 0.15);
    
    .tab-icon {
      color: #3b82f6;
      transform: scale(1.1);
    }
    
    .tab-text {
      color: #3b82f6;
      font-weight: 600;
    }
  }
}

.tab-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  transition: all 0.2s ease;
  line-height: 1;
  
  .chinese-icon {
    font-size: 16px;
    font-weight: bold;
    color: #4a5568;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .icon {
    font-size: 18px;
    color: #4a5568;
  }
}

.tab-text {
  font-size: 11px;
  font-weight: 500;
  color: #4a5568;
  transition: all 0.2s ease;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  line-height: 1;
}

/* 弹出菜单样式 */
.popup-container {
  position: relative;
}

.popup-menu {
  position: fixed;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  min-width: 180px;
  max-width: 280px;
  max-height: calc(100vh - 120px - env(safe-area-inset-bottom));
  overflow-y: auto;
  z-index: 1001;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  
  &.tools-menu,
  &.words-menu {
    bottom: calc(70px + env(safe-area-inset-bottom));
    right: 16px;
  }
  
  &.dev-center-menu {
    bottom: calc(70px + env(safe-area-inset-bottom));
    right: 200px;
    min-width: 300px;
  }
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #f1f5f9;
  }
  
  &.dev-center-item {
    justify-content: space-between;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 4px;
  }
}

.menu-icon {
  margin-right: 12px;
  font-size: 16px;
}

.menu-text {
  flex: 1;
  font-size: 14px;
  color: #374151;
}

.menu-arrow {
  font-size: 12px;
  color: #6b7280;
}

.menu-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 8px 0;
}

/* 工具相关样式 */
.enabled-tools {
  padding: 0 8px;
}

.tool-menu-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 6px;
  
  &:hover {
    background: #f9fafb;
  }
}

.tool-radio {
  margin-right: 8px;
}

.tool-label {
  cursor: pointer;
  flex: 1;
}

.tool-name {
  font-size: 13px;
  color: #374151;
}

.no-tools-tip {
  padding: 0 16px;
}

.tip-text {
  font-size: 12px;
  color: #6b7280;
  text-align: center;
  padding: 8px 0;
}

/* 开发中心样式 */
.dev-center-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  
  h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #111827;
  }
}

.dev-tool-list {
  max-height: 300px;
  overflow-y: auto;
}

.dev-tool-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  
  &:last-child {
    border-bottom: none;
  }
}

.tool-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.tool-icon {
  margin-right: 12px;
  font-size: 16px;
}

.tool-details {
  display: flex;
  flex-direction: column;
}

.tool-name {
  font-size: 13px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.tool-desc {
  font-size: 11px;
  color: #6b7280;
  line-height: 1.3;
}

.tool-switch {
  position: relative;
  
  input[type="checkbox"] {
    display: none;
  }
  
  .switch-label {
    display: block;
    width: 40px;
    height: 20px;
    background: #d1d5db;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.2s ease;
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      top: 2px;
      left: 2px;
      width: 16px;
      height: 16px;
      background: #ffffff;
      border-radius: 50%;
      transition: transform 0.2s ease;
    }
  }
  
  input[type="checkbox"]:checked + .switch-label {
    background: #3b82f6;
    
    &::after {
      transform: translateX(20px);
    }
  }
}

/* 遮罩层 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

/* 过渡动画 */
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: all 0.3s ease;
}

.popup-fade-enter-from,
.popup-fade-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .popup-menu {
    right: 8px;
    min-width: 160px;
    
    &.dev-center-menu {
      right: 120px;
      min-width: 280px;
    }
  }
  
  .tab-item {
    min-width: 50px;
    padding: 4px 8px;
  }
  
  .tab-text {
    font-size: 10px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .tab-bar {
    background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
    border-top-color: #374151;
  }
  
  .tab-icon .chinese-icon,
  .tab-icon .icon,
  .tab-text {
    color: #d1d5db;
  }
  
  .tab-item.active {
    .tab-icon,
    .tab-text {
      color: #60a5fa;
    }
  }
  
  .popup-menu {
    background: #1f2937;
    border-color: #374151;
  }
  
  .menu-text {
    color: #d1d5db;
  }
  
  .menu-item:hover {
    background: #374151;
  }
}
</style>