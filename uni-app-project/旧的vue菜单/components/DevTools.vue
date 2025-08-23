<template>
  <div class="dev-tools" :class="{ 'dev-tools-collapsed': collapsed }">
    <!-- 工具栏头部 -->
    <div class="dev-tools-header">
      <div class="dev-tools-title">
        <span class="dev-tools-icon">🛠️</span>
        <span v-if="!collapsed">开发工具</span>
      </div>
      <div class="dev-tools-controls">
        <button
          class="dev-tools-btn"
          @click="toggleCollapse"
          :title="collapsed ? '展开' : '收起'"
        >
          <span v-if="collapsed">📖</span>
          <span v-else>📕</span>
        </button>
        <button
          class="dev-tools-btn"
          @click="$emit('close')"
          title="关闭"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- 工具内容 -->
    <div v-if="!collapsed" class="dev-tools-content">
      <!-- 标签页导航 -->
      <div class="dev-tools-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          class="dev-tools-tab"
          @click="activeTab = tab.id"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- 标签页内容 -->
      <div class="dev-tools-panel">
        <!-- 状态面板 -->
        <div v-if="activeTab === 'state'" class="panel-content">
          <div class="state-section">
            <h4>Vuex 状态</h4>
            <div class="state-tree">
              <pre>{{ JSON.stringify(vuexState, null, 2) }}</pre>
            </div>
          </div>
          
          <div class="state-section">
            <h4>权限服务状态</h4>
            <div class="state-tree">
              <pre>{{ JSON.stringify(permissionState, null, 2) }}</pre>
            </div>
          </div>
          
          <div class="state-section">
            <h4>菜单状态</h4>
            <div class="state-tree">
              <pre>{{ JSON.stringify(menuState, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <!-- 路由面板 -->
        <div v-if="activeTab === 'router'" class="panel-content">
          <div class="router-info">
            <h4>当前路由</h4>
            <div class="info-item">
              <label>路径:</label>
              <span>{{ currentRoute.path }}</span>
            </div>
            <div class="info-item">
              <label>名称:</label>
              <span>{{ currentRoute.name }}</span>
            </div>
            <div class="info-item">
              <label>参数:</label>
              <pre>{{ JSON.stringify(currentRoute.params, null, 2) }}</pre>
            </div>
            <div class="info-item">
              <label>查询:</label>
              <pre>{{ JSON.stringify(currentRoute.query, null, 2) }}</pre>
            </div>
            <div class="info-item">
              <label>元信息:</label>
              <pre>{{ JSON.stringify(currentRoute.meta, null, 2) }}</pre>
            </div>
          </div>
          
          <div class="router-history">
            <h4>路由历史</h4>
            <div class="history-list">
              <div
                v-for="(route, index) in routeHistory"
                :key="index"
                class="history-item"
              >
                <span class="history-time">{{ formatTime(route.timestamp) }}</span>
                <span class="history-path">{{ route.path }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 性能面板 -->
        <div v-if="activeTab === 'performance'" class="panel-content">
          <div class="performance-metrics">
            <h4>性能指标</h4>
            <div class="metrics-grid">
              <div class="metric-item">
                <label>页面加载时间</label>
                <span>{{ performanceData.loadTime }}ms</span>
              </div>
              <div class="metric-item">
                <label>DOM 就绪时间</label>
                <span>{{ performanceData.domReady }}ms</span>
              </div>
              <div class="metric-item">
                <label>首次绘制</label>
                <span>{{ performanceData.firstPaint }}ms</span>
              </div>
              <div class="metric-item">
                <label>内存使用</label>
                <span>{{ formatMemory(performanceData.memory) }}</span>
              </div>
            </div>
          </div>
          
          <div class="performance-chart">
            <h4>性能图表</h4>
            <canvas ref="performanceChart" width="300" height="150"></canvas>
          </div>
        </div>

        <!-- 网络面板 -->
        <div v-if="activeTab === 'network'" class="panel-content">
          <div class="network-controls">
            <button class="dev-tools-btn" @click="clearNetworkLogs">
              清除日志
            </button>
            <button class="dev-tools-btn" @click="toggleNetworkMonitoring">
              {{ networkMonitoring ? '停止监控' : '开始监控' }}
            </button>
          </div>
          
          <div class="network-list">
            <div
              v-for="request in networkLogs"
              :key="request.id"
              :class="getRequestClass(request)"
              class="network-item"
              @click="selectRequest(request)"
            >
              <span class="request-method">{{ request.method }}</span>
              <span class="request-url">{{ request.url }}</span>
              <span class="request-status">{{ request.status }}</span>
              <span class="request-time">{{ request.duration }}ms</span>
            </div>
          </div>
          
          <div v-if="selectedRequest" class="request-details">
            <h4>请求详情</h4>
            <div class="request-info">
              <div class="info-section">
                <h5>请求头</h5>
                <pre>{{ JSON.stringify(selectedRequest.headers, null, 2) }}</pre>
              </div>
              <div class="info-section">
                <h5>响应</h5>
                <pre>{{ JSON.stringify(selectedRequest.response, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- 控制台面板 -->
        <div v-if="activeTab === 'console'" class="panel-content">
          <div class="console-controls">
            <button class="dev-tools-btn" @click="clearConsoleLogs">
              清除日志
            </button>
            <select v-model="consoleFilter" class="console-filter">
              <option value="all">全部</option>
              <option value="log">日志</option>
              <option value="warn">警告</option>
              <option value="error">错误</option>
            </select>
          </div>
          
          <div class="console-output">
            <div
              v-for="log in filteredConsoleLogs"
              :key="log.id"
              :class="`console-${log.level}`"
              class="console-item"
            >
              <span class="console-time">{{ formatTime(log.timestamp) }}</span>
              <span class="console-level">{{ log.level.toUpperCase() }}</span>
              <span class="console-message">{{ log.message }}</span>
            </div>
          </div>
          
          <div class="console-input">
            <input
              v-model="consoleCommand"
              class="console-command"
              placeholder="输入 JavaScript 命令..."
              @keydown.enter="executeCommand"
            >
            <button class="dev-tools-btn" @click="executeCommand">
              执行
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import permissionService from '../services/PermissionService.js'
import menuStateManager from '../services/MenuStateManager.js'

export default {
  name: 'DevTools',
  
  emits: ['close'],
  
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    // 响应式状态
    const collapsed = ref(false)
    const activeTab = ref('state')
    const routeHistory = ref([])
    const networkLogs = ref([])
    const consoleLogs = ref([])
    const selectedRequest = ref(null)
    const networkMonitoring = ref(true)
    const consoleFilter = ref('all')
    const consoleCommand = ref('')
    const performanceChart = ref(null)
    
    // 标签页配置
    const tabs = [
      { id: 'state', label: '状态', icon: '📊' },
      { id: 'router', label: '路由', icon: '🛣️' },
      { id: 'performance', label: '性能', icon: '⚡' },
      { id: 'network', label: '网络', icon: '🌐' },
      { id: 'console', label: '控制台', icon: '💻' }
    ]
    
    // 计算属性
    const vuexState = computed(() => store.state)
    const permissionState = computed(() => ({
      isAuthenticated: permissionService.isAuthenticated(),
      currentUser: permissionService.getCurrentUser(),
      permissions: permissionService.getUserPermissions()
    }))
    const menuState = computed(() => menuStateManager.getState())
    const currentRoute = computed(() => route)
    
    const performanceData = ref({
      loadTime: 0,
      domReady: 0,
      firstPaint: 0,
      memory: 0
    })
    
    const filteredConsoleLogs = computed(() => {
      if (consoleFilter.value === 'all') {
        return consoleLogs.value
      }
      return consoleLogs.value.filter(log => log.level === consoleFilter.value)
    })
    
    // 方法
    const toggleCollapse = () => {
      collapsed.value = !collapsed.value
    }
    
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString()
    }
    
    const formatMemory = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const getRequestClass = (request) => {
      return {
        'request-success': request.status >= 200 && request.status < 300,
        'request-error': request.status >= 400,
        'request-pending': !request.status
      }
    }
    
    const selectRequest = (request) => {
      selectedRequest.value = request
    }
    
    const clearNetworkLogs = () => {
      networkLogs.value = []
      selectedRequest.value = null
    }
    
    const toggleNetworkMonitoring = () => {
      networkMonitoring.value = !networkMonitoring.value
    }
    
    const clearConsoleLogs = () => {
      consoleLogs.value = []
    }
    
    const executeCommand = () => {
      if (!consoleCommand.value.trim()) return
      
      try {
        // 在全局作用域中执行命令
        const result = eval(consoleCommand.value)
        
        // 添加到控制台日志
        consoleLogs.value.push({
          id: Date.now(),
          level: 'log',
          message: `> ${consoleCommand.value}`,
          timestamp: Date.now()
        })
        
        consoleLogs.value.push({
          id: Date.now() + 1,
          level: 'log',
          message: `< ${JSON.stringify(result)}`,
          timestamp: Date.now()
        })
        
      } catch (error) {
        consoleLogs.value.push({
          id: Date.now(),
          level: 'error',
          message: `Error: ${error.message}`,
          timestamp: Date.now()
        })
      }
      
      consoleCommand.value = ''
    }
    
    const updatePerformanceData = () => {
      if (performance.getEntriesByType) {
        const navigation = performance.getEntriesByType('navigation')[0]
        if (navigation) {
          performanceData.value.loadTime = Math.round(navigation.loadEventEnd - navigation.loadEventStart)
          performanceData.value.domReady = Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart)
        }
        
        const paint = performance.getEntriesByType('paint')
        const firstPaint = paint.find(entry => entry.name === 'first-paint')
        if (firstPaint) {
          performanceData.value.firstPaint = Math.round(firstPaint.startTime)
        }
      }
      
      if (performance.memory) {
        performanceData.value.memory = performance.memory.usedJSHeapSize
      }
    }
    
    const drawPerformanceChart = () => {
      if (!performanceChart.value) return
      
      const canvas = performanceChart.value
      const ctx = canvas.getContext('2d')
      const width = canvas.width
      const height = canvas.height
      
      // 清除画布
      ctx.clearRect(0, 0, width, height)
      
      // 绘制性能图表（简单的柱状图）
      const data = [
        { label: '加载', value: performanceData.value.loadTime, color: '#3b82f6' },
        { label: 'DOM', value: performanceData.value.domReady, color: '#10b981' },
        { label: '绘制', value: performanceData.value.firstPaint, color: '#f59e0b' }
      ]
      
      const maxValue = Math.max(...data.map(d => d.value))
      const barWidth = width / data.length - 20
      
      data.forEach((item, index) => {
        const barHeight = (item.value / maxValue) * (height - 40)
        const x = index * (barWidth + 20) + 10
        const y = height - barHeight - 20
        
        // 绘制柱子
        ctx.fillStyle = item.color
        ctx.fillRect(x, y, barWidth, barHeight)
        
        // 绘制标签
        ctx.fillStyle = '#374151'
        ctx.font = '12px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(item.label, x + barWidth / 2, height - 5)
        ctx.fillText(`${item.value}ms`, x + barWidth / 2, y - 5)
      })
    }
    
    // 网络监控
    const setupNetworkMonitoring = () => {
      const originalFetch = window.fetch
      
      window.fetch = async (...args) => {
        if (!networkMonitoring.value) {
          return originalFetch(...args)
        }
        
        const startTime = Date.now()
        const requestId = Date.now() + Math.random()
        
        // 记录请求开始
        const request = {
          id: requestId,
          method: args[1]?.method || 'GET',
          url: args[0],
          startTime,
          headers: args[1]?.headers || {},
          status: null,
          duration: null,
          response: null
        }
        
        networkLogs.value.unshift(request)
        
        try {
          const response = await originalFetch(...args)
          const endTime = Date.now()
          
          // 更新请求信息
          request.status = response.status
          request.duration = endTime - startTime
          
          // 尝试获取响应内容
          try {
            const clonedResponse = response.clone()
            const responseData = await clonedResponse.text()
            request.response = responseData
          } catch (e) {
            request.response = 'Unable to read response'
          }
          
          return response
          
        } catch (error) {
          const endTime = Date.now()
          request.status = 'Error'
          request.duration = endTime - startTime
          request.response = error.message
          throw error
        }
      }
    }
    
    // 控制台监控
    const setupConsoleMonitoring = () => {
      const originalConsole = {
        log: console.log,
        warn: console.warn,
        error: console.error
      }
      
      const createConsoleWrapper = (level) => {
        return (...args) => {
          // 调用原始方法
          originalConsole[level](...args)
          
          // 记录到开发工具
          consoleLogs.value.unshift({
            id: Date.now() + Math.random(),
            level,
            message: args.map(arg => 
              typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
            ).join(' '),
            timestamp: Date.now()
          })
          
          // 限制日志数量
          if (consoleLogs.value.length > 100) {
            consoleLogs.value = consoleLogs.value.slice(0, 100)
          }
        }
      }
      
      console.log = createConsoleWrapper('log')
      console.warn = createConsoleWrapper('warn')
      console.error = createConsoleWrapper('error')
    }
    
    // 监听路由变化
    watch(
      () => route.path,
      (newPath) => {
        routeHistory.value.unshift({
          path: newPath,
          timestamp: Date.now()
        })
        
        // 限制历史记录数量
        if (routeHistory.value.length > 20) {
          routeHistory.value = routeHistory.value.slice(0, 20)
        }
      },
      { immediate: true }
    )
    
    // 监听性能数据变化
    watch(
      () => activeTab.value,
      (newTab) => {
        if (newTab === 'performance') {
          updatePerformanceData()
          setTimeout(drawPerformanceChart, 100)
        }
      }
    )
    
    // 生命周期
    onMounted(() => {
      setupNetworkMonitoring()
      setupConsoleMonitoring()
      updatePerformanceData()
      
      // 定期更新性能数据
      const performanceInterval = setInterval(updatePerformanceData, 5000)
      
      // 清理函数
      onUnmounted(() => {
        clearInterval(performanceInterval)
      })
    })
    
    return {
      // 响应式状态
      collapsed,
      activeTab,
      routeHistory,
      networkLogs,
      consoleLogs,
      selectedRequest,
      networkMonitoring,
      consoleFilter,
      consoleCommand,
      performanceChart,
      
      // 配置
      tabs,
      
      // 计算属性
      vuexState,
      permissionState,
      menuState,
      currentRoute,
      performanceData,
      filteredConsoleLogs,
      
      // 方法
      toggleCollapse,
      formatTime,
      formatMemory,
      getRequestClass,
      selectRequest,
      clearNetworkLogs,
      toggleNetworkMonitoring,
      clearConsoleLogs,
      executeCommand
    }
  }
}
</script>

<style scoped>
.dev-tools {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 400px;
  max-height: 60vh;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  box-shadow: var(--shadow-xl);
  z-index: var(--z-modal);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  transition: all var(--duration-normal) var(--ease-out);
}

.dev-tools-collapsed {
  width: 120px;
  max-height: 40px;
}

.dev-tools-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.dev-tools-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.dev-tools-icon {
  font-size: 16px;
}

.dev-tools-controls {
  display: flex;
  gap: var(--space-1);
}

.dev-tools-btn {
  padding: var(--space-1) var(--space-2);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  font-size: var(--font-size-xs);
}

.dev-tools-btn:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text);
}

.dev-tools-content {
  display: flex;
  flex-direction: column;
  height: calc(60vh - 40px);
}

.dev-tools-tabs {
  display: flex;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.dev-tools-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  padding: var(--space-2);
  background: transparent;
  border: none;
  border-right: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  font-size: var(--font-size-xs);
}

.dev-tools-tab:last-child {
  border-right: none;
}

.dev-tools-tab:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text);
}

.dev-tools-tab.active {
  background: var(--color-bg);
  color: var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
}

.tab-icon {
  font-size: 14px;
}

.tab-label {
  font-size: var(--font-size-xs);
}

.dev-tools-panel {
  flex: 1;
  overflow: hidden;
}

.panel-content {
  height: 100%;
  overflow-y: auto;
  padding: var(--space-3);
}

/* 状态面板样式 */
.state-section {
  margin-bottom: var(--space-4);
}

.state-section h4 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.state-tree {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2);
  max-height: 200px;
  overflow: auto;
}

.state-tree pre {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
}

/* 路由面板样式 */
.router-info,
.router-history {
  margin-bottom: var(--space-4);
}

.router-info h4,
.router-history h4 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.info-item {
  display: flex;
  margin-bottom: var(--space-2);
}

.info-item label {
  min-width: 60px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}

.info-item span,
.info-item pre {
  flex: 1;
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text);
}

.history-list {
  max-height: 150px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1);
  border-bottom: 1px solid var(--color-border);
}

.history-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  min-width: 80px;
}

.history-path {
  font-size: var(--font-size-xs);
  color: var(--color-text);
}

/* 性能面板样式 */
.performance-metrics {
  margin-bottom: var(--space-4);
}

.performance-metrics h4 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
}

.metric-item {
  display: flex;
  flex-direction: column;
  padding: var(--space-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
}

.metric-item label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

.metric-item span {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.performance-chart h4 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

/* 网络面板样式 */
.network-controls {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.network-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: var(--space-3);
}

.network-item {
  display: grid;
  grid-template-columns: 60px 1fr 60px 60px;
  gap: var(--space-2);
  padding: var(--space-1);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background-color var(--duration-fast) var(--ease-out);
}

.network-item:hover {
  background: var(--color-bg-secondary);
}

.network-item.request-success {
  border-left: 3px solid var(--color-success);
}

.network-item.request-error {
  border-left: 3px solid var(--color-error);
}

.network-item.request-pending {
  border-left: 3px solid var(--color-warning);
}

.request-method,
.request-url,
.request-status,
.request-time {
  font-size: var(--font-size-xs);
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.request-details {
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-3);
}

.request-details h4 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.request-info {
  max-height: 200px;
  overflow-y: auto;
}

.info-section {
  margin-bottom: var(--space-3);
}

.info-section h5 {
  margin: 0 0 var(--space-1) 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.info-section pre {
  margin: 0;
  padding: var(--space-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text);
  max-height: 100px;
  overflow: auto;
}

/* 控制台面板样式 */
.console-controls {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.console-filter {
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg);
  color: var(--color-text);
  font-size: var(--font-size-xs);
}

.console-output {
  height: 200px;
  overflow-y: auto;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2);
  margin-bottom: var(--space-3);
}

.console-item {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
  font-size: var(--font-size-xs);
}

.console-time {
  color: var(--color-text-muted);
  min-width: 80px;
}

.console-level {
  min-width: 50px;
  font-weight: var(--font-weight-semibold);
}

.console-log .console-level {
  color: var(--color-text);
}

.console-warn .console-level {
  color: var(--color-warning);
}

.console-error .console-level {
  color: var(--color-error);
}

.console-message {
  flex: 1;
  color: var(--color-text);
  word-break: break-all;
}

.console-input {
  display: flex;
  gap: var(--space-2);
}

.console-command {
  flex: 1;
  padding: var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .dev-tools {
    width: 100%;
    right: 0;
    left: 0;
  }
  
  .dev-tools-collapsed {
    width: 100px;
  }
}
</style>