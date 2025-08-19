<template>
  <div class="test-menu-integration">
    <h1>菜单集成测试页面</h1>
    
    <div class="test-section">
      <h2>1. 菜单配置状态</h2>
      <div class="status-grid">
        <div class="status-item" :class="{ success: menuConfigLoaded, error: !menuConfigLoaded }">
          <span class="status-icon">{{ menuConfigLoaded ? '✅' : '❌' }}</span>
          <span>菜单配置加载</span>
        </div>
        <div class="status-item" :class="{ success: websocketConnected, error: !websocketConnected }">
          <span class="status-icon">{{ websocketConnected ? '✅' : '❌' }}</span>
          <span>WebSocket连接</span>
        </div>
        <div class="status-item" :class="{ success: permissionsLoaded, error: !permissionsLoaded }">
          <span class="status-icon">{{ permissionsLoaded ? '✅' : '❌' }}</span>
          <span>权限系统</span>
        </div>
      </div>
    </div>
    
    <div class="test-section">
      <h2>2. 菜单数据</h2>
      <div class="menu-data">
        <h3>底部导航菜单 ({{ bottomNavMenus.length }} 项)</h3>
        <div class="menu-items">
          <div 
            v-for="item in bottomNavMenus" 
            :key="item.id"
            class="menu-item"
            @click="testMenuClick(item)"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span class="menu-name">{{ item.name }}</span>
            <span class="menu-path">{{ item.path }}</span>
          </div>
        </div>
        
        <h3>工具菜单 ({{ toolsMenuItems.length }} 项)</h3>
        <div class="menu-items">
          <div 
            v-for="item in toolsMenuItems" 
            :key="item.id"
            class="menu-item"
            @click="testToolClick(item)"
          >
            <span class="menu-icon">{{ item.icon || '🔧' }}</span>
            <span class="menu-name">{{ item.name }}</span>
            <span class="menu-path">{{ item.path }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="test-section">
      <h2>3. 实时更新测试</h2>
      <div class="realtime-test">
        <button @click="testMenuUpdate" class="test-button">
          模拟菜单更新
        </button>
        <button @click="testPermissionChange" class="test-button">
          模拟权限变更
        </button>
        <button @click="refreshMenuConfig" class="test-button">
          刷新菜单配置
        </button>
      </div>
      
      <div class="update-log">
        <h4>更新日志:</h4>
        <div class="log-entries">
          <div 
            v-for="(log, index) in updateLogs" 
            :key="index"
            class="log-entry"
          >
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="test-section">
      <h2>4. 菜单集成组件</h2>
      <div class="menu-integration-container">
        <MenuIntegration 
          title="测试菜单"
          :force-mode="forceMode"
          @menu-click="handleMenuClick"
          @tool-select="handleToolSelect"
        />
      </div>
      
      <div class="mode-controls">
        <button 
          @click="forceMode = 'mobile'" 
          :class="{ active: forceMode === 'mobile' }"
          class="mode-button"
        >
          移动端模式
        </button>
        <button 
          @click="forceMode = 'desktop'" 
          :class="{ active: forceMode === 'desktop' }"
          class="mode-button"
        >
          桌面端模式
        </button>
        <button 
          @click="forceMode = 'auto'" 
          :class="{ active: forceMode === 'auto' }"
          class="mode-button"
        >
          自动模式
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import MenuIntegration from './menu/MenuIntegration.vue'
import { useMenuManager } from '@/composables/useMenuManager'

const store = useStore()
const { filteredMenus, toolsConfig, loadMenuConfig, loadToolsConfig } = useMenuManager()

// 响应式数据
const forceMode = ref<'mobile' | 'desktop' | 'auto'>('auto')
const updateLogs = ref<Array<{ timestamp: number, message: string }>>([])

// 计算属性
const menuConfigLoaded = computed(() => {
  return filteredMenus.value.length > 0
})

const websocketConnected = computed(() => {
  return store.getters['menu/isWebSocketConnected']
})

const permissionsLoaded = computed(() => {
  return store.getters['user/hasPermissions']
})

const bottomNavMenus = computed(() => {
  return store.getters['menu/bottomNavMenus'] || []
})

const toolsMenuItems = computed(() => {
  return toolsConfig.value?.items || []
})

// 方法
const addLog = (message: string) => {
  updateLogs.value.unshift({
    timestamp: Date.now(),
    message
  })
  
  // 保持最多20条日志
  if (updateLogs.value.length > 20) {
    updateLogs.value = updateLogs.value.slice(0, 20)
  }
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString()
}

const testMenuClick = (item: any) => {
  addLog(`点击菜单: ${item.name} (${item.path})`)
}

const testToolClick = (item: any) => {
  addLog(`点击工具: ${item.name} (${item.path})`)
}

const testMenuUpdate = () => {
  addLog('模拟菜单更新事件')
  store.dispatch('menu/simulateMenuUpdate')
}

const testPermissionChange = () => {
  addLog('模拟权限变更事件')
  store.dispatch('user/simulatePermissionChange')
}

const refreshMenuConfig = async () => {
  addLog('开始刷新菜单配置...')
  try {
    await Promise.all([
      loadMenuConfig(),
      loadToolsConfig()
    ])
    addLog('菜单配置刷新成功')
  } catch (error) {
    addLog(`菜单配置刷新失败: ${error.message}`)
  }
}

const handleMenuClick = (item: any) => {
  addLog(`MenuIntegration菜单点击: ${item.title || item.name}`)
}

const handleToolSelect = (tool: any) => {
  addLog(`MenuIntegration工具选择: ${tool.title || tool.name}`)
}

// 初始化
onMounted(async () => {
  addLog('测试页面初始化')
  
  try {
    await Promise.all([
      loadMenuConfig(),
      loadToolsConfig()
    ])
    addLog('菜单配置加载完成')
  } catch (error) {
    addLog(`菜单配置加载失败: ${error.message}`)
  }
})
</script>

<style scoped>
.test-menu-integration {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.test-section {
  margin: 30px 0;
  padding: 20px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  background: #fff;
}

.test-section h2 {
  margin: 0 0 20px 0;
  color: #24292e;
  font-size: 20px;
  font-weight: 600;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 6px;
  border: 1px solid #e1e5e9;
  transition: all 0.2s ease;
}

.status-item.success {
  background: #f0f9ff;
  border-color: #0969da;
  color: #0969da;
}

.status-item.error {
  background: #fff5f5;
  border-color: #d1242f;
  color: #d1242f;
}

.status-icon {
  margin-right: 8px;
  font-size: 16px;
}

.menu-data h3 {
  margin: 20px 0 10px 0;
  color: #656d76;
  font-size: 16px;
  font-weight: 500;
}

.menu-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 10px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: #f6f8fa;
  border-color: #0969da;
}

.menu-icon {
  margin-right: 8px;
  font-size: 16px;
}

.menu-name {
  font-weight: 500;
  margin-right: 8px;
}

.menu-path {
  color: #656d76;
  font-size: 12px;
  margin-left: auto;
}

.realtime-test {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.test-button {
  padding: 8px 16px;
  background: #0969da;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s ease;
}

.test-button:hover {
  background: #0860ca;
}

.update-log {
  margin-top: 20px;
}

.update-log h4 {
  margin: 0 0 10px 0;
  color: #24292e;
  font-size: 14px;
  font-weight: 600;
}

.log-entries {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #f6f8fa;
}

.log-entry {
  display: flex;
  padding: 8px 12px;
  border-bottom: 1px solid #e1e5e9;
  font-size: 13px;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-time {
  color: #656d76;
  margin-right: 12px;
  min-width: 80px;
}

.log-message {
  color: #24292e;
}

.menu-integration-container {
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  min-height: 300px;
  margin-bottom: 15px;
  position: relative;
  overflow: hidden;
}

.mode-controls {
  display: flex;
  gap: 10px;
}

.mode-button {
  padding: 6px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.mode-button:hover {
  background: #f6f8fa;
}

.mode-button.active {
  background: #0969da;
  color: white;
  border-color: #0969da;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-menu-integration {
    padding: 15px;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .menu-items {
    grid-template-columns: 1fr;
  }
  
  .realtime-test {
    flex-direction: column;
  }
  
  .mode-controls {
    flex-direction: column;
  }
}
</style>