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

