<template>
  <view class="performance-page">
    <view class="header">
      <text class="title">📊 性能监控</text>
      <text class="subtitle">应用性能实时监控</text>
    </view>
    
    <view class="content">
      <!-- 系统信息 -->
      <view class="info-card">
        <text class="card-title">系统信息</text>
        <view class="info-grid">
          <view class="info-item">
            <text class="label">平台</text>
            <text class="value">{{ systemInfo.platform }}</text>
          </view>
          <view class="info-item">
            <text class="label">系统版本</text>
            <text class="value">{{ systemInfo.system }}</text>
          </view>
          <view class="info-item">
            <text class="label">设备型号</text>
            <text class="value">{{ systemInfo.model }}</text>
          </view>
          <view class="info-item">
            <text class="label">屏幕尺寸</text>
            <text class="value">{{ systemInfo.screenWidth }}x{{ systemInfo.screenHeight }}</text>
          </view>
        </view>
      </view>
      
      <!-- 性能指标 -->
      <view class="metrics-card">
        <text class="card-title">性能指标</text>
        <view class="metrics-grid">
          <view class="metric-item">
            <text class="metric-label">内存使用</text>
            <view class="metric-bar">
              <view 
                class="metric-fill memory" 
                :style="{ width: memoryUsage + '%' }"
              ></view>
            </view>
            <text class="metric-value">{{ memoryUsage }}%</text>
          </view>
          
          <view class="metric-item">
            <text class="metric-label">CPU使用率</text>
            <view class="metric-bar">
              <view 
                class="metric-fill cpu" 
                :style="{ width: cpuUsage + '%' }"
              ></view>
            </view>
            <text class="metric-value">{{ cpuUsage }}%</text>
          </view>
          
          <view class="metric-item">
            <text class="metric-label">网络延迟</text>
            <view class="metric-bar">
              <view 
                class="metric-fill network" 
                :style="{ width: Math.min(networkLatency / 10, 100) + '%' }"
              ></view>
            </view>
            <text class="metric-value">{{ networkLatency }}ms</text>
          </view>
        </view>
      </view>
      
      <!-- 页面性能 -->
      <view class="page-performance-card">
        <text class="card-title">页面性能</text>
        <view class="performance-list">
          <view class="performance-item">
            <text class="perf-label">页面加载时间</text>
            <text class="perf-value">{{ pageLoadTime }}ms</text>
          </view>
          <view class="performance-item">
            <text class="perf-label">首屏渲染时间</text>
            <text class="perf-value">{{ firstPaintTime }}ms</text>
          </view>
          <view class="performance-item">
            <text class="perf-label">DOM节点数量</text>
            <text class="perf-value">{{ domNodeCount }}</text>
          </view>
          <view class="performance-item">
            <text class="perf-label">JS堆内存</text>
            <text class="perf-value">{{ jsHeapSize }}MB</text>
          </view>
        </view>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-section">
        <button 
          class="action-btn primary" 
          @tap="refreshMetrics"
          :disabled="isRefreshing"
        >
          {{ isRefreshing ? '刷新中...' : '刷新数据' }}
        </button>
        
        <button 
          class="action-btn secondary" 
          @tap="startMonitoring"
          :disabled="isMonitoring"
        >
          {{ isMonitoring ? '监控中...' : '开始监控' }}
        </button>
        
        <button 
          class="action-btn secondary" 
          @tap="stopMonitoring"
          :disabled="!isMonitoring"
        >
          停止监控
        </button>
        
        <button 
          class="action-btn warning" 
          @tap="clearData"
        >
          清除数据
        </button>
      </view>
      
      <!-- 监控日志 -->
      <view class="log-section">
        <text class="section-title">监控日志</text>
        <scroll-view class="log-container" scroll-y>
          <view 
            v-for="(log, index) in monitorLogs" 
            :key="index"
            class="log-item"
          >
            <text class="log-time">{{ log.time }}</text>
            <text class="log-message">{{ log.message }}</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'Performance',
  data() {
    return {
      isRefreshing: false,
      isMonitoring: false,
      monitorTimer: null,
      systemInfo: {},
      memoryUsage: 0,
      cpuUsage: 0,
      networkLatency: 0,
      pageLoadTime: 0,
      firstPaintTime: 0,
      domNodeCount: 0,
      jsHeapSize: 0,
      monitorLogs: []
    }
  },
  
  onLoad() {
    this.initSystemInfo()
    this.initPerformanceMetrics()
    this.addLog('性能监控页面初始化完成')
  },
  
  onUnload() {
    this.stopMonitoring()
  },
  
  methods: {
    initSystemInfo() {
      uni.getSystemInfo({
        success: (res) => {
          this.systemInfo = {
            platform: res.platform,
            system: res.system,
            model: res.model,
            screenWidth: res.screenWidth,
            screenHeight: res.screenHeight
          }
          this.addLog('系统信息获取成功')
        },
        fail: (err) => {
          this.addLog(`系统信息获取失败: ${err.errMsg}`)
        }
      })
    },
    
    initPerformanceMetrics() {
      // 模拟性能数据
      this.memoryUsage = Math.floor(Math.random() * 60) + 20
      this.cpuUsage = Math.floor(Math.random() * 40) + 10
      this.networkLatency = Math.floor(Math.random() * 200) + 50
      this.pageLoadTime = Math.floor(Math.random() * 1000) + 500
      this.firstPaintTime = Math.floor(Math.random() * 800) + 200
      this.domNodeCount = Math.floor(Math.random() * 500) + 100
      this.jsHeapSize = (Math.random() * 50 + 10).toFixed(2)
    },
    
    refreshMetrics() {
      this.isRefreshing = true
      this.addLog('开始刷新性能数据...')
      
      setTimeout(() => {
        this.initPerformanceMetrics()
        this.isRefreshing = false
        this.addLog('性能数据刷新完成')
      }, 1000)
    },
    
    startMonitoring() {
      if (this.isMonitoring) return
      
      this.isMonitoring = true
      this.addLog('开始实时监控...')
      
      this.monitorTimer = setInterval(() => {
        // 模拟实时数据变化
        this.memoryUsage = Math.max(10, Math.min(90, this.memoryUsage + (Math.random() - 0.5) * 10))
        this.cpuUsage = Math.max(5, Math.min(80, this.cpuUsage + (Math.random() - 0.5) * 15))
        this.networkLatency = Math.max(20, Math.min(500, this.networkLatency + (Math.random() - 0.5) * 50))
        
        // 记录异常情况
        if (this.memoryUsage > 80) {
          this.addLog('⚠️ 内存使用率过高: ' + this.memoryUsage.toFixed(1) + '%')
        }
        if (this.cpuUsage > 70) {
          this.addLog('⚠️ CPU使用率过高: ' + this.cpuUsage.toFixed(1) + '%')
        }
        if (this.networkLatency > 300) {
          this.addLog('⚠️ 网络延迟过高: ' + this.networkLatency.toFixed(0) + 'ms')
        }
      }, 2000)
    },
    
    stopMonitoring() {
      if (!this.isMonitoring) return
      
      this.isMonitoring = false
      if (this.monitorTimer) {
        clearInterval(this.monitorTimer)
        this.monitorTimer = null
      }
      this.addLog('监控已停止')
    },
    
    clearData() {
      this.monitorLogs = []
      this.initPerformanceMetrics()
      this.addLog('数据已清除')
    },
    
    addLog(message) {
      const now = new Date()
      const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
      
      this.monitorLogs.unshift({
        time,
        message
      })
      
      // 限制日志数量
      if (this.monitorLogs.length > 100) {
        this.monitorLogs = this.monitorLogs.slice(0, 100)
      }
    }
  }
}
</script>

<style scoped>
.performance-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 30rpx;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.subtitle {
  display: block;
  font-size: 26rpx;
  color: #666;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.info-card,
.metrics-card,
.page-performance-card {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.card-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 10rpx;
}

.label {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.value {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.metrics-grid {
  display: flex;
  flex-direction: column;
  gap: 25rpx;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.metric-label {
  font-size: 26rpx;
  color: #333;
  min-width: 140rpx;
}

.metric-bar {
  flex: 1;
  height: 20rpx;
  background: #f0f0f0;
  border-radius: 10rpx;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 10rpx;
  transition: width 0.3s ease;
}

.metric-fill.memory {
  background: linear-gradient(90deg, #4caf50, #8bc34a);
}

.metric-fill.cpu {
  background: linear-gradient(90deg, #2196f3, #03a9f4);
}

.metric-fill.network {
  background: linear-gradient(90deg, #ff9800, #ffc107);
}

.metric-value {
  font-size: 24rpx;
  color: #666;
  min-width: 80rpx;
  text-align: right;
}

.performance-list {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.performance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 10rpx;
}

.perf-label {
  font-size: 26rpx;
  color: #333;
}

.perf-value {
  font-size: 26rpx;
  color: #666;
  font-weight: 500;
}

.action-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.action-btn {
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.secondary {
  background: white;
  color: #333;
  border: 2rpx solid #e0e0e0;
}

.action-btn.warning {
  background: #ff5722;
  color: white;
}

.action-btn:disabled {
  opacity: 0.6;
}

.log-section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.log-container {
  height: 400rpx;
  background: #f8f8f8;
  border-radius: 10rpx;
  padding: 20rpx;
}

.log-item {
  display: flex;
  margin-bottom: 15rpx;
  padding: 15rpx;
  background: white;
  border-radius: 8rpx;
  border-left: 4rpx solid #2196f3;
}

.log-time {
  font-size: 24rpx;
  color: #999;
  margin-right: 20rpx;
  min-width: 120rpx;
}

.log-message {
  font-size: 26rpx;
  color: #333;
  flex: 1;
}
</style>