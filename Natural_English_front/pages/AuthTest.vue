<template>
  <div class="auth-test-container">
    <div class="test-header">
      <h1>登录状态同步测试页面</h1>
      <p>用于测试前后端登录状态同步功能</p>
    </div>
    
    <div class="test-sections">
      <!-- 当前状态显示 -->
      <div class="status-section">
        <h2>当前状态</h2>
        <div class="status-grid">
          <div class="status-item">
            <label>前端Token:</label>
            <span :class="{ 'status-ok': frontendToken, 'status-error': !frontendToken }">
              {{ frontendToken ? '✓ 存在' : '✗ 不存在' }}
            </span>
          </div>
          <div class="status-item">
            <label>前端用户信息:</label>
            <span :class="{ 'status-ok': frontendUser, 'status-error': !frontendUser }">
              {{ frontendUser ? '✓ 存在' : '✗ 不存在' }}
            </span>
          </div>
          <div class="status-item">
            <label>后端认证状态:</label>
            <span :class="{ 'status-ok': backendAuth === true, 'status-error': backendAuth === false, 'status-loading': backendAuth === null }">
              {{ backendAuth === null ? '⏳ 检查中...' : (backendAuth ? '✓ 已认证' : '✗ 未认证') }}
            </span>
          </div>
          <div class="status-item">
            <label>同步状态:</label>
            <span :class="{ 'status-ok': syncStatus === 'success', 'status-error': syncStatus === 'error', 'status-loading': syncStatus === 'loading' }">
              {{ syncStatusText }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 用户信息显示 -->
      <div class="user-section" v-if="userInfo">
        <h2>用户信息</h2>
        <div class="user-info">
          <div class="info-item">
            <label>用户名:</label>
            <span>{{ userInfo.username }}</span>
          </div>
          <div class="info-item">
            <label>真实姓名:</label>
            <span>{{ userInfo.real_name }}</span>
          </div>
          <div class="info-item">
            <label>角色:</label>
            <span>{{ userInfo.role }}</span>
          </div>
          <div class="info-item">
            <label>邮箱:</label>
            <span>{{ userInfo.email }}</span>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions-section">
        <h2>测试操作</h2>
        <div class="action-buttons">
          <button @click="checkBackendAuth" :disabled="loading" class="btn btn-primary">
            {{ loading ? '检查中...' : '检查后端认证状态' }}
          </button>
          <button @click="syncAuthState" :disabled="loading" class="btn btn-secondary">
            {{ loading ? '同步中...' : '手动同步登录状态' }}
          </button>
          <button @click="clearFrontendAuth" :disabled="loading" class="btn btn-warning">
            清除前端登录信息
          </button>
          <button @click="refreshStatus" :disabled="loading" class="btn btn-info">
            刷新状态
          </button>
        </div>
      </div>
      
      <!-- 日志显示 -->
      <div class="logs-section">
        <h2>操作日志</h2>
        <div class="logs-container">
          <div v-for="(log, index) in logs" :key="index" class="log-item" :class="log.type">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
        <button @click="clearLogs" class="btn btn-sm">清除日志</button>
      </div>
    </div>
  </div>
</template>

<script>
import { verifyBackendAuth, fetchUserFromBackend, manualSyncAuth } from '../utils/authSync.js'
import { getCurrentUser } from '../utils/permission.js'

export default {
  name: 'AuthTest',
  data() {
    return {
      frontendToken: null,
      frontendUser: null,
      backendAuth: null,
      userInfo: null,
      syncStatus: null, // 'loading', 'success', 'error'
      loading: false,
      logs: []
    }
  },
  computed: {
    syncStatusText() {
      switch (this.syncStatus) {
        case 'loading': return '⏳ 同步中...'
        case 'success': return '✓ 同步成功'
        case 'error': return '✗ 同步失败'
        default: return '⚪ 未同步'
      }
    }
  },
  mounted() {
    this.addLog('页面加载完成', 'info')
    this.refreshStatus()
  },
  methods: {
    // 添加日志
    addLog(message, type = 'info') {
      const now = new Date()
      const time = now.toLocaleTimeString()
      this.logs.unshift({ time, message, type })
      
      // 限制日志数量
      if (this.logs.length > 50) {
        this.logs = this.logs.slice(0, 50)
      }
    },
    
    // 清除日志
    clearLogs() {
      this.logs = []
      this.addLog('日志已清除', 'info')
    },
    
    // 刷新状态
    async refreshStatus() {
      this.addLog('开始刷新状态...', 'info')
      
      // 检查前端状态
      this.frontendToken = localStorage.getItem('token')
      const userStr = localStorage.getItem('user')
      this.frontendUser = userStr ? JSON.parse(userStr) : null
      this.userInfo = getCurrentUser()
      
      this.addLog(`前端Token: ${this.frontendToken ? '存在' : '不存在'}`, 'info')
      this.addLog(`前端用户信息: ${this.frontendUser ? '存在' : '不存在'}`, 'info')
      
      // 检查后端状态
      await this.checkBackendAuth()
    },
    
    // 检查后端认证状态
    async checkBackendAuth() {
      this.loading = true
      this.backendAuth = null
      this.addLog('开始检查后端认证状态...', 'info')
      
      try {
        const isAuthenticated = await verifyBackendAuth()
        this.backendAuth = isAuthenticated
        
        if (isAuthenticated) {
          this.addLog('后端认证状态: 已认证', 'success')
          
          // 获取后端用户信息
          const backendUser = await fetchUserFromBackend()
          if (backendUser) {
            this.addLog(`后端用户信息: ${backendUser.username} (${backendUser.role})`, 'success')
          }
        } else {
          this.addLog('后端认证状态: 未认证', 'warning')
        }
      } catch (error) {
        this.backendAuth = false
        this.addLog(`检查后端认证状态失败: ${error.message}`, 'error')
      } finally {
        this.loading = false
      }
    },
    
    // 同步登录状态
    async syncAuthState() {
      this.loading = true
      this.syncStatus = 'loading'
      this.addLog('开始手动同步登录状态...', 'info')
      
      try {
        const result = await manualSyncAuth()
        
        if (result.success) {
          this.syncStatus = 'success'
          this.addLog(`同步成功: ${result.message}`, 'success')
          
          if (result.authenticated) {
            this.addLog(`用户已登录: ${result.user?.username}`, 'success')
          } else {
            this.addLog('用户未登录', 'warning')
          }
        } else {
          this.syncStatus = 'error'
          this.addLog(`同步失败: ${result.message}`, 'error')
        }
        
        // 刷新前端状态
        await this.refreshStatus()
        
      } catch (error) {
        this.syncStatus = 'error'
        this.addLog(`同步过程中发生错误: ${error.message}`, 'error')
      } finally {
        this.loading = false
      }
    },
    
    // 清除前端登录信息
    clearFrontendAuth() {
      this.addLog('清除前端登录信息...', 'info')
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      this.frontendToken = null
      this.frontendUser = null
      this.userInfo = null
      
      this.addLog('前端登录信息已清除', 'success')
    }
  }
}
</script>

<style scoped>
.auth-test-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.test-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.test-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
}

.test-header p {
  margin: 0;
  opacity: 0.9;
}

.test-sections {
  display: grid;
  gap: 20px;
}

.status-section,
.user-section,
.actions-section,
.logs-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.status-section h2,
.user-section h2,
.actions-section h2,
.logs-section h2 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 20px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.status-item,
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.status-item label,
.info-item label {
  font-weight: 600;
  color: #555;
}

.status-ok {
  color: #28a745;
  font-weight: 600;
}

.status-error {
  color: #dc3545;
  font-weight: 600;
}

.status-loading {
  color: #ffc107;
  font-weight: 600;
}

.user-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background: #e0a800;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #117a8b;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  background: #6c757d;
  color: white;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  margin-bottom: 10px;
}

.log-item {
  display: flex;
  padding: 8px 12px;
  border-bottom: 1px solid #f1f3f4;
  font-size: 14px;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.info {
  background: #f8f9fa;
}

.log-item.success {
  background: #d4edda;
  color: #155724;
}

.log-item.warning {
  background: #fff3cd;
  color: #856404;
}

.log-item.error {
  background: #f8d7da;
  color: #721c24;
}

.log-time {
  font-weight: 600;
  margin-right: 10px;
  min-width: 80px;
}

.log-message {
  flex: 1;
}

@media (max-width: 768px) {
  .auth-test-container {
    padding: 10px;
  }
  
  .status-grid,
  .user-info {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>