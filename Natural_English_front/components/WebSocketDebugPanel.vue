<template>
  <div class="websocket-debug-panel">
    <div class="debug-header">
      <h3>WebSocket 调试面板</h3>
      <button @click="togglePanel" class="toggle-btn">
        {{ isExpanded ? '收起' : '展开' }}
      </button>
    </div>
    
    <div v-if="isExpanded" class="debug-content">
      <!-- 连接状态 -->
      <div class="status-section">
        <h4>连接状态</h4>
        <div class="status-item">
          <span class="label">权限WebSocket:</span>
          <span :class="['status', connectionStatus ? connectionStatus.toLowerCase() : 'unknown']">
            {{ connectionStatus || 'unknown' }}
          </span>
        </div>
        <div class="status-item">
          <span class="label">重试次数:</span>
          <span>{{ retryCount }}</span>
        </div>
        <div class="status-item">
          <span class="label">最后同步:</span>
          <span>{{ lastSyncTime || '未同步' }}</span>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions-section">
        <h4>操作</h4>
        <div class="action-buttons">
          <button @click="runDiagnostic" :disabled="isRunningDiagnostic">
            {{ isRunningDiagnostic ? '诊断中...' : '运行诊断' }}
          </button>
          <button @click="reconnectWebSocket">
            重新连接
          </button>
          <button @click="clearLogs">
            清除日志
          </button>
        </div>
      </div>
      
      <!-- 诊断结果 -->
      <div v-if="diagnosticResults.length > 0" class="diagnostic-section">
        <h4>诊断结果</h4>
        <div class="diagnostic-results">
          <div 
            v-for="(result, index) in diagnosticResults" 
            :key="index"
            :class="['diagnostic-item', result.type]"
          >
            <div class="diagnostic-header">
              <span class="diagnostic-name">{{ result.category }}</span>
              <span :class="['diagnostic-status', result.type]">
                {{ result.type === 'success' ? '✓' : result.type === 'warning' ? '⚠' : result.type === 'info' ? 'ℹ' : '✗' }}
              </span>
            </div>
            <div v-if="result.message" class="diagnostic-message">
              {{ result.message }}
            </div>
            <div v-if="result.suggestions && result.suggestions.length > 0" class="diagnostic-suggestions">
              <strong>建议:</strong>
              <ul>
                <li v-for="suggestion in result.suggestions" :key="suggestion">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 错误日志 -->
      <div v-if="errorLogs.length > 0" class="logs-section">
        <h4>错误日志</h4>
        <div class="error-logs">
          <div 
            v-for="(log, index) in errorLogs" 
            :key="index"
            class="log-item"
          >
            <span class="log-time">{{ formatTime(log.time) }}</span>
            <span class="log-source">[{{ log.source }}]</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { permissionSyncManager } from '../utils/permission'

export default {
  name: 'WebSocketDebugPanel',
  data() {
    return {
      isExpanded: false,
      isRunningDiagnostic: false,
      connectionStatus: 'unknown',
      retryCount: 0,
      lastSyncTime: null,
      diagnosticResults: [],
      errorLogs: [],
      updateInterval: null
    }
  },
  mounted() {
    this.updateStatus()
    this.updateInterval = setInterval(this.updateStatus, 2000)
    
    // 监听WebSocket错误
    this.setupErrorListener()
  },
  beforeDestroy() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
    }
  },
  methods: {
    togglePanel() {
      this.isExpanded = !this.isExpanded
    },
    
    updateStatus() {
      if (permissionSyncManager) {
        const status = permissionSyncManager.getConnectionStatus()
        this.connectionStatus = status.status || 'unknown'
        this.retryCount = status.retryCount || 0
        this.lastSyncTime = status.lastSyncTime || null
      }
    },
    
    async runDiagnostic() {
      if (!window.websocketDiagnostics) {
        this.$message.error('诊断工具未初始化')
        return
      }
      
      this.isRunningDiagnostic = true
      try {
        const results = await window.websocketDiagnostics.runFullDiagnostic()
        this.diagnosticResults = results
        this.$message.success('诊断完成')
      } catch (error) {
        this.$message.error('诊断失败: ' + (error?.message || error || '未知错误'))
      } finally {
        this.isRunningDiagnostic = false
      }
    },
    
    reconnectWebSocket() {
      if (permissionSyncManager) {
        permissionSyncManager.disconnectWebSocket()
        setTimeout(() => {
          permissionSyncManager.connectWebSocket()
          this.$message.info('正在重新连接...')
        }, 1000)
      }
    },
    
    clearLogs() {
      this.errorLogs = []
      this.diagnosticResults = []
      this.$message.success('日志已清除')
    },
    
    setupErrorListener() {
      // 重写console.error来捕获WebSocket错误
      const originalError = console.error
      console.error = (...args) => {
        try {
          const message = args.map(arg => {
            if (typeof arg === 'string') return arg
            if (arg instanceof Error) return arg.message || arg.toString()
            if (typeof arg === 'object') return JSON.stringify(arg)
            return String(arg)
          }).join(' ')
          
          if (message.includes('WebSocket') || message.includes('权限')) {
            this.errorLogs.unshift({
              time: new Date(),
              source: 'Console',
              message: message
            })
            // 只保留最近50条日志
            if (this.errorLogs.length > 50) {
              this.errorLogs = this.errorLogs.slice(0, 50)
            }
          }
        } catch (e) {
          // 如果处理参数时出错，使用简单的字符串转换
          console.warn('Error processing console.error arguments:', e)
        }
        originalError.apply(console, args)
      }
    },
    
    formatTime(time) {
      return time.toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.websocket-debug-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 400px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  font-size: 14px;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
  border-radius: 8px 8px 0 0;
}

.debug-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.toggle-btn {
  padding: 4px 8px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.debug-content {
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
}

.status-section,
.actions-section,
.diagnostic-section,
.logs-section {
  margin-bottom: 20px;
}

.status-section h4,
.actions-section h4,
.diagnostic-section h4,
.logs-section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #555;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  font-weight: 500;
  color: #666;
}

.status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status.connected {
  background: #d4edda;
  color: #155724;
}

.status.connecting {
  background: #fff3cd;
  color: #856404;
}

.status.disconnected,
.status.error {
  background: #f8d7da;
  color: #721c24;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-buttons button {
  padding: 6px 12px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.action-buttons button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.diagnostic-item {
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 4px;
  border-left: 4px solid #ddd;
}

.diagnostic-item.success {
  background: #d4edda;
  border-left-color: #28a745;
}

.diagnostic-item.warning {
  background: #fff3cd;
  border-left-color: #ffc107;
}

.diagnostic-item.error {
  background: #f8d7da;
  border-left-color: #dc3545;
}

.diagnostic-item.info {
  background: #d1ecf1;
  border-left-color: #17a2b8;
}

.diagnostic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.diagnostic-name {
  font-weight: 500;
}

.diagnostic-status {
  font-weight: bold;
}

.diagnostic-status.success {
  color: #28a745;
}

.diagnostic-status.warning {
  color: #ffc107;
}

.diagnostic-status.error {
  color: #dc3545;
}

.diagnostic-status.info {
  color: #17a2b8;
}

.diagnostic-message {
  color: #666;
  margin-bottom: 5px;
}

.diagnostic-suggestions ul {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.diagnostic-suggestions li {
  margin-bottom: 3px;
  color: #555;
}

.log-item {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  padding: 6px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.log-time {
  color: #6c757d;
  white-space: nowrap;
}

.log-source {
  color: #007bff;
  font-weight: 500;
  white-space: nowrap;
}

.log-message {
  color: #dc3545;
  word-break: break-all;
}

.error-logs {
  max-height: 200px;
  overflow-y: auto;
}
</style>