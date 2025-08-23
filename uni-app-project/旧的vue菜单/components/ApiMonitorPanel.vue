<template>
  <div class="api-monitor-panel" v-if="showPanel">
    <div class="panel-header">
      <h3>API 性能监控</h3>
      <div class="panel-controls">
        <button @click="refreshData" class="btn-refresh">刷新</button>
        <button @click="clearData" class="btn-clear">清空</button>
        <button @click="exportData" class="btn-export">导出</button>
        <button @click="togglePanel" class="btn-close">×</button>
      </div>
    </div>

    <div class="panel-content">
      <!-- 总体统计 -->
      <div class="stats-section">
        <h4>总体统计</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">总请求数</span>
            <span class="stat-value">{{ stats.totalRequests }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">成功率</span>
            <span class="stat-value success">{{ (100 - stats.errorRate).toFixed(1) }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">错误率</span>
            <span class="stat-value error">{{ stats.errorRate.toFixed(1) }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">平均响应时间</span>
            <span class="stat-value">{{ stats.averageResponseTime.toFixed(0) }}ms</span>
          </div>
        </div>
      </div>

      <!-- 端点统计 -->
      <div class="endpoints-section">
        <h4>端点统计</h4>
        <div class="endpoints-table">
          <div class="table-header">
            <span>端点</span>
            <span>请求数</span>
            <span>成功率</span>
            <span>平均响应时间</span>
            <span>最大响应时间</span>
          </div>
          <div 
            v-for="endpoint in endpointStats" 
            :key="endpoint.endpoint"
            class="table-row"
            :class="{ 'error-row': endpoint.errorRate > 10 }"
          >
            <span class="endpoint-name" :title="endpoint.endpoint">{{ endpoint.endpoint }}</span>
            <span>{{ endpoint.totalRequests }}</span>
            <span :class="{ 'success': endpoint.errorRate < 5, 'warning': endpoint.errorRate >= 5 && endpoint.errorRate < 10, 'error': endpoint.errorRate >= 10 }">
              {{ (100 - endpoint.errorRate).toFixed(1) }}%
            </span>
            <span>{{ endpoint.averageResponseTime.toFixed(0) }}ms</span>
            <span>{{ endpoint.maxResponseTime }}ms</span>
          </div>
        </div>
      </div>

      <!-- 最近请求 -->
      <div class="recent-requests-section">
        <h4>最近请求</h4>
        <div class="requests-list">
          <div 
            v-for="request in recentRequests" 
            :key="request.id"
            class="request-item"
            :class="{ 'error-request': !request.success, 'slow-request': request.responseTime > 3000 }"
          >
            <div class="request-info">
              <span class="method" :class="request.method.toLowerCase()">{{ request.method }}</span>
              <span class="url">{{ request.url }}</span>
              <span class="time">{{ formatTime(request.startTime) }}</span>
            </div>
            <div class="request-stats">
              <span class="response-time" :class="getResponseTimeClass(request.responseTime)">
                {{ request.responseTime }}ms
              </span>
              <span class="status" :class="getStatusClass(request.status)">
                {{ request.status || 'N/A' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误请求 -->
      <div class="error-requests-section" v-if="errorRequests.length > 0">
        <h4>错误请求</h4>
        <div class="error-list">
          <div 
            v-for="error in errorRequests" 
            :key="error.id"
            class="error-item"
          >
            <div class="error-info">
              <span class="method error">{{ error.method }}</span>
              <span class="url">{{ error.url }}</span>
              <span class="time">{{ formatTime(error.startTime) }}</span>
            </div>
            <div class="error-details">
              <span class="status error">{{ error.status }}</span>
              <span class="error-message">{{ error.error?.message || '未知错误' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 浮动按钮 -->
  <div class="monitor-toggle" v-if="!showPanel && isDevelopment" @click="togglePanel">
    📊
  </div>
</template>

<script>
import apiMonitor from '../utils/apiMonitor.js'

export default {
  name: 'ApiMonitorPanel',
  data() {
    return {
      showPanel: false,
      stats: {
        totalRequests: 0,
        successRequests: 0,
        errorRequests: 0,
        totalResponseTime: 0,
        averageResponseTime: 0,
        errorRate: 0
      },
      endpointStats: [],
      recentRequests: [],
      errorRequests: [],
      refreshInterval: null
    }
  },
  computed: {
    isDevelopment() {
      return import.meta.env.MODE === 'development'
    }
  },
  mounted() {
    if (this.isDevelopment) {
      this.refreshData()
      this.startAutoRefresh()
      
      // 监听API调用完成事件
      apiMonitor.addListener(this.onApiEvent)
    }
  },
  beforeUnmount() {
    this.stopAutoRefresh()
    apiMonitor.removeListener(this.onApiEvent)
  },
  methods: {
    togglePanel() {
      this.showPanel = !this.showPanel
      if (this.showPanel) {
        this.refreshData()
      }
    },
    
    refreshData() {
      this.stats = apiMonitor.getStats()
      this.endpointStats = apiMonitor.getEndpointStats().slice(0, 10)
      this.recentRequests = apiMonitor.getRecentRequests(20)
      this.errorRequests = apiMonitor.getErrorRequests(10)
    },
    
    clearData() {
      if (confirm('确定要清空所有监控数据吗？')) {
        apiMonitor.reset()
        this.refreshData()
      }
    },
    
    exportData() {
      const data = apiMonitor.export()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `api-monitor-${new Date().toISOString().slice(0, 19)}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
    
    startAutoRefresh() {
      this.refreshInterval = setInterval(() => {
        if (this.showPanel) {
          this.refreshData()
        }
      }, 5000) // 每5秒刷新一次
    },
    
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    
    onApiEvent(event, data) {
      if (event === 'requestComplete' && this.showPanel) {
        // 实时更新数据
        this.refreshData()
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    },
    
    getResponseTimeClass(responseTime) {
      if (responseTime < 500) return 'fast'
      if (responseTime < 2000) return 'normal'
      if (responseTime < 5000) return 'slow'
      return 'very-slow'
    },
    
    getStatusClass(status) {
      if (status >= 200 && status < 300) return 'success'
      if (status >= 300 && status < 400) return 'redirect'
      if (status >= 400 && status < 500) return 'client-error'
      if (status >= 500) return 'server-error'
      return 'unknown'
    }
  }
}
</script>

<style scoped>
.api-monitor-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 800px;
  max-height: 80vh;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.panel-controls {
  display: flex;
  gap: 8px;
}

.panel-controls button {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
}

.panel-controls button:hover {
  background: #f0f0f0;
}

.btn-close {
  font-weight: bold;
  color: #666;
}

.panel-content {
  max-height: calc(80vh - 60px);
  overflow-y: auto;
  padding: 16px;
}

.stats-section, .endpoints-section, .recent-requests-section, .error-requests-section {
  margin-bottom: 20px;
}

.stats-section h4, .endpoints-section h4, .recent-requests-section h4, .error-requests-section h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
}

.stat-label {
  font-size: 10px;
  color: #666;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.stat-value.success {
  color: #28a745;
}

.stat-value.error {
  color: #dc3545;
}

.endpoints-table {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px;
  background: #f5f5f5;
  font-weight: bold;
  border-bottom: 1px solid #ddd;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 6px 8px;
  border-bottom: 1px solid #eee;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row.error-row {
  background: #fff5f5;
}

.endpoint-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.requests-list, .error-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.request-item, .error-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-bottom: 1px solid #eee;
}

.request-item:last-child, .error-item:last-child {
  border-bottom: none;
}

.request-item.error-request {
  background: #fff5f5;
}

.request-item.slow-request {
  background: #fffbf0;
}

.request-info, .error-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.request-stats, .error-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.method {
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: bold;
  font-size: 10px;
  text-transform: uppercase;
}

.method.get {
  background: #d4edda;
  color: #155724;
}

.method.post {
  background: #cce5ff;
  color: #004085;
}

.method.put {
  background: #fff3cd;
  color: #856404;
}

.method.delete {
  background: #f8d7da;
  color: #721c24;
}

.method.error {
  background: #f8d7da;
  color: #721c24;
}

.url {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #666;
}

.time {
  color: #999;
  font-size: 10px;
}

.response-time.fast {
  color: #28a745;
}

.response-time.normal {
  color: #17a2b8;
}

.response-time.slow {
  color: #ffc107;
}

.response-time.very-slow {
  color: #dc3545;
}

.status.success {
  color: #28a745;
}

.status.redirect {
  color: #17a2b8;
}

.status.client-error {
  color: #ffc107;
}

.status.server-error {
  color: #dc3545;
}

.status.error {
  color: #dc3545;
}

.success {
  color: #28a745;
}

.warning {
  color: #ffc107;
}

.error {
  color: #dc3545;
}

.error-message {
  color: #666;
  font-style: italic;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.monitor-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 9998;
  font-size: 20px;
}

.monitor-toggle:hover {
  background: #0056b3;
}
</style>