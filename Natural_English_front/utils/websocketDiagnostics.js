/**
 * WebSocket诊断工具
 * 用于检测和解决权限WebSocket连接问题
 */

import { permissionSyncManager } from './permission.js'

class WebSocketDiagnostics {
  constructor() {
    this.diagnosticResults = []
    this.isRunning = false
    this.autoRunEnabled = true
    this.lastDiagnosticTime = 0
  }
  
  /**
   * 初始化诊断工具
   */
  init() {
    // 监听WebSocket错误事件
    this.setupErrorListeners()
    console.log('WebSocket诊断工具已初始化')
  }
  
  /**
   * 设置错误监听器
   */
  setupErrorListeners() {
    // 监听全局错误
    window.addEventListener('error', (event) => {
      if (event.message && event.message.includes('WebSocket')) {
        this.handleWebSocketError('全局错误', event.message)
      }
    })
    
    // 监听未处理的Promise拒绝
    window.addEventListener('unhandledrejection', (event) => {
      if (event.reason && event.reason.toString().includes('WebSocket')) {
        this.handleWebSocketError('Promise拒绝', event.reason.toString())
      }
    })
  }
  
  /**
   * 处理WebSocket错误
   */
  handleWebSocketError(source, message) {
    console.error(`WebSocket错误来源[${source}]:`, message)
    
    // 避免频繁运行诊断（5分钟内只运行一次）
    const now = Date.now()
    if (this.autoRunEnabled && (now - this.lastDiagnosticTime) > 5 * 60 * 1000) {
      this.lastDiagnosticTime = now
      console.log('检测到WebSocket错误，自动运行诊断...')
      this.runFullDiagnostic()
    }
  }

  /**
   * 运行完整诊断
   */
  async runFullDiagnostic() {
    if (this.isRunning) {
      console.warn('诊断正在进行中，请稍候')
      return this.diagnosticResults
    }

    this.isRunning = true
    this.diagnosticResults = []
    
    console.log('开始WebSocket诊断...')
    
    try {
      // 1. 检查网络连接
      await this.checkNetworkConnection()
      
      // 2. 检查用户认证状态
      this.checkUserAuthentication()
      
      // 3. 检查WebSocket配置
      this.checkWebSocketConfig()
      
      // 4. 检查后端服务状态
      await this.checkBackendService()
      
      // 5. 检查WebSocket连接状态
      this.checkWebSocketConnection()
      
      // 6. 测试WebSocket连接
      await this.testWebSocketConnection()
      
    } catch (error) {
      this.addResult('error', '诊断过程中发生错误', error.message)
    } finally {
      this.isRunning = false
    }
    
    this.generateReport()
    return this.diagnosticResults
  }

  /**
   * 检查网络连接
   */
  async checkNetworkConnection() {
    if (!navigator.onLine) {
      this.addResult('error', '网络连接', '设备未连接到网络')
      return
    }
    
    try {
      const response = await fetch('http://localhost:8000/api/health-check', { 
        method: 'HEAD',
        timeout: 5000 
      })
      
      if (response.ok) {
        this.addResult('success', '网络连接', '网络连接正常')
      } else {
        this.addResult('warning', '网络连接', `HTTP状态码: ${response.status}`)
      }
    } catch (error) {
      this.addResult('error', '网络连接', `网络请求失败: ${error.message}`)
    }
  }

  /**
   * 检查用户认证状态
   */
  checkUserAuthentication() {
    const token = localStorage.getItem('token')
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    
    if (!token) {
      this.addResult('error', '用户认证', '缺少认证令牌')
      return
    }
    
    if (!user || !user.id) {
      this.addResult('error', '用户认证', '缺少用户信息')
      return
    }
    
    // 检查token是否过期
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const now = Date.now() / 1000
      
      if (payload.exp && payload.exp < now) {
        this.addResult('error', '用户认证', '认证令牌已过期')
        return
      }
    } catch (error) {
      this.addResult('warning', '用户认证', '无法解析令牌，可能不是JWT格式')
    }
    
    this.addResult('success', '用户认证', `用户已认证: ${user.username || user.id}`)
  }

  /**
   * 检查WebSocket配置
   */
  checkWebSocketConfig() {
    const config = {
      endpoint: import.meta.env.MODE === 'production' ? '/ws/permissions/' : 'ws://127.0.0.1:8000/ws/permissions/',
      retryAttempts: 5,
      retryDelay: 2000
    }
    
    this.addResult('info', 'WebSocket配置', `端点: ${config.endpoint}`)
    this.addResult('info', 'WebSocket配置', `重试次数: ${config.retryAttempts}`)
    this.addResult('info', 'WebSocket配置', `重试延迟: ${config.retryDelay}ms`)
    
    // 检查WebSocket支持
    if (typeof WebSocket === 'undefined') {
      this.addResult('error', 'WebSocket支持', '浏览器不支持WebSocket')
    } else {
      this.addResult('success', 'WebSocket支持', '浏览器支持WebSocket')
    }
  }

  /**
   * 检查后端服务状态
   */
  async checkBackendService() {
    const backendUrl = import.meta.env.MODE === 'production' ? '' : 'http://127.0.0.1:8000'
    
    try {
      const response = await fetch(`${backendUrl}/api/permissions/`, {
        method: 'HEAD',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (response.ok) {
        this.addResult('success', '后端服务', '权限API服务正常')
      } else {
        this.addResult('error', '后端服务', `权限API返回状态码: ${response.status}`)
      }
    } catch (error) {
      this.addResult('error', '后端服务', `无法连接到后端服务: ${error.message}`)
    }
  }

  /**
   * 检查WebSocket连接状态
   */
  checkWebSocketConnection() {
    const status = permissionSyncManager.getConnectionStatus()
    
    this.addResult('info', 'WebSocket状态', `连接状态: ${status.status}`)
    this.addResult('info', 'WebSocket状态', `重试次数: ${status.retryCount}`)
    
    if (status.websocketState !== null) {
      const stateNames = {
        0: 'CONNECTING',
        1: 'OPEN', 
        2: 'CLOSING',
        3: 'CLOSED'
      }
      this.addResult('info', 'WebSocket状态', `连接状态码: ${status.websocketState} (${stateNames[status.websocketState]})`)
    }
    
    if (permissionSyncManager.isConnectionHealthy()) {
      this.addResult('success', 'WebSocket连接', '连接健康')
    } else {
      this.addResult('warning', 'WebSocket连接', '连接不健康或未认证')
    }
  }

  /**
   * 测试WebSocket连接
   */
  async testWebSocketConnection() {
    return new Promise((resolve) => {
      const token = localStorage.getItem('token')
      const user = JSON.parse(localStorage.getItem('user') || 'null')
      
      if (!token || !user) {
        this.addResult('error', 'WebSocket测试', '缺少认证信息，无法测试连接')
        resolve()
        return
      }
      
      const wsUrl = `ws://127.0.0.1:8001/ws/permissions/?token=${encodeURIComponent(token)}&userId=${user.id}`
      let testSocket
      
      try {
        testSocket = new WebSocket(wsUrl)
        
        const timeout = setTimeout(() => {
          this.addResult('error', 'WebSocket测试', '连接超时')
          testSocket.close()
          resolve()
        }, 10000)
        
        testSocket.onopen = () => {
          clearTimeout(timeout)
          this.addResult('success', 'WebSocket测试', '测试连接成功建立')
          testSocket.close(1000, '测试完成')
          resolve()
        }
        
        testSocket.onerror = (error) => {
          clearTimeout(timeout)
          this.addResult('error', 'WebSocket测试', `连接错误: ${error.message || '未知错误'}`)
          resolve()
        }
        
        testSocket.onclose = (event) => {
          if (event.code !== 1000) {
            this.addResult('error', 'WebSocket测试', `连接关闭: 代码${event.code}, 原因: ${event.reason || '未知'}`)
          }
        }
        
      } catch (error) {
        this.addResult('error', 'WebSocket测试', `创建连接失败: ${error.message}`)
        resolve()
      }
    })
  }

  /**
   * 添加诊断结果
   */
  addResult(type, category, message, details = null) {
    this.diagnosticResults.push({
      type, // success, warning, error, info
      category,
      message,
      details,
      timestamp: new Date().toISOString()
    })
  }

  /**
   * 生成诊断报告
   */
  generateReport() {
    const summary = {
      total: this.diagnosticResults.length,
      success: this.diagnosticResults.filter(r => r.type === 'success').length,
      warning: this.diagnosticResults.filter(r => r.type === 'warning').length,
      error: this.diagnosticResults.filter(r => r.type === 'error').length,
      info: this.diagnosticResults.filter(r => r.type === 'info').length
    }
    
    console.group('🔍 WebSocket诊断报告')
    console.log('📊 诊断摘要:', summary)
    
    if (summary.error > 0) {
      console.group('❌ 错误项')
      this.diagnosticResults
        .filter(r => r.type === 'error')
        .forEach(r => console.error(`${r.category}: ${r.message}`, r.details || ''))
      console.groupEnd()
    }
    
    if (summary.warning > 0) {
      console.group('⚠️ 警告项')
      this.diagnosticResults
        .filter(r => r.type === 'warning')
        .forEach(r => console.warn(`${r.category}: ${r.message}`, r.details || ''))
      console.groupEnd()
    }
    
    console.group('✅ 成功项')
    this.diagnosticResults
      .filter(r => r.type === 'success')
      .forEach(r => console.log(`${r.category}: ${r.message}`))
    console.groupEnd()
    
    console.groupEnd()
    
    // 提供修复建议
    this.provideSuggestions()
  }

  /**
   * 提供修复建议
   */
  provideSuggestions() {
    const errors = this.diagnosticResults.filter(r => r.type === 'error')
    
    if (errors.length === 0) {
      console.log('🎉 所有检查都通过了！WebSocket连接应该正常工作。')
      return
    }
    
    console.group('💡 修复建议')
    
    errors.forEach(error => {
      switch (error.category) {
        case '网络连接':
          console.log('• 检查网络连接是否正常')
          console.log('• 确认防火墙没有阻止WebSocket连接')
          break
        case '用户认证':
          console.log('• 重新登录以获取新的认证令牌')
          console.log('• 检查用户信息是否完整')
          break
        case '后端服务':
          console.log('• 确认Django服务器正在运行')
          console.log('• 检查Django Channels配置')
          console.log('• 验证权限API端点是否可访问')
          break
        case 'WebSocket测试':
          console.log('• 检查WebSocket路由配置')
          console.log('• 确认后端WebSocket服务正常运行')
          console.log('• 检查CORS设置')
          break
      }
    })
    
    console.groupEnd()
  }

  /**
   * 获取诊断结果
   */
  getResults() {
    return this.diagnosticResults
  }

  /**
   * 清除诊断结果
   */
  clearResults() {
    this.diagnosticResults = []
  }
}

// 创建全局实例
export const websocketDiagnostics = new WebSocketDiagnostics()

// 添加到window对象供调试使用
if (typeof window !== 'undefined') {
  window.websocketDiagnostics = websocketDiagnostics
}

export default WebSocketDiagnostics