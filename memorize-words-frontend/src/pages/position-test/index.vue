<template>
  <view class="position-test-page">
    <view class="header">
      <text class="title">📍 位置测试</text>
      <text class="subtitle">地理位置功能测试</text>
    </view>
    
    <view class="content">
      <!-- 当前位置信息 -->
      <view class="info-card">
        <text class="card-title">当前位置信息</text>
        <view class="info-item">
          <text class="label">经度:</text>
          <text class="value">{{ locationInfo.longitude || '未获取' }}</text>
        </view>
        <view class="info-item">
          <text class="label">纬度:</text>
          <text class="value">{{ locationInfo.latitude || '未获取' }}</text>
        </view>
        <view class="info-item">
          <text class="label">精度:</text>
          <text class="value">{{ locationInfo.accuracy || '未获取' }}米</text>
        </view>
        <view class="info-item">
          <text class="label">地址:</text>
          <text class="value">{{ locationInfo.address || '未获取' }}</text>
        </view>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-section">
        <button 
          class="action-btn primary" 
          @tap="getCurrentLocation"
          :disabled="isLoading"
        >
          {{ isLoading ? '获取中...' : '获取当前位置' }}
        </button>
        
        <button 
          class="action-btn secondary" 
          @tap="openLocationSettings"
        >
          打开位置设置
        </button>
        
        <button 
          class="action-btn secondary" 
          @tap="clearLocationInfo"
        >
          清除位置信息
        </button>
      </view>
      
      <!-- 测试日志 -->
      <view class="log-section">
        <text class="section-title">测试日志</text>
        <scroll-view class="log-container" scroll-y>
          <view 
            v-for="(log, index) in testLogs" 
            :key="index"
            class="log-item"
            :class="log.type"
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
  name: 'PositionTest',
  data() {
    return {
      isLoading: false,
      locationInfo: {
        longitude: '',
        latitude: '',
        accuracy: '',
        address: ''
      },
      testLogs: []
    }
  },
  
  onLoad() {
    this.addLog('页面加载完成', 'info')
  },
  
  methods: {
    getCurrentLocation() {
      this.isLoading = true
      this.addLog('开始获取位置信息...', 'info')
      
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.locationInfo = {
            longitude: res.longitude.toFixed(6),
            latitude: res.latitude.toFixed(6),
            accuracy: res.accuracy,
            address: res.address || '地址解析中...'
          }
          
          this.addLog(`位置获取成功: ${res.latitude}, ${res.longitude}`, 'success')
          
          // 尝试获取详细地址
          this.getLocationAddress(res.latitude, res.longitude)
        },
        fail: (err) => {
          this.addLog(`位置获取失败: ${err.errMsg}`, 'error')
          
          if (err.errMsg.includes('auth deny')) {
            uni.showModal({
              title: '位置权限',
              content: '需要位置权限才能使用此功能，请在设置中开启位置权限',
              confirmText: '去设置',
              success: (modalRes) => {
                if (modalRes.confirm) {
                  this.openLocationSettings()
                }
              }
            })
          }
        },
        complete: () => {
          this.isLoading = false
        }
      })
    },
    
    getLocationAddress(latitude, longitude) {
      // 这里可以调用地图API获取详细地址
      // 由于是测试页面，这里模拟地址获取
      setTimeout(() => {
        this.locationInfo.address = `模拟地址: 经度${longitude}, 纬度${latitude}`
        this.addLog('地址解析完成', 'info')
      }, 1000)
    },
    
    openLocationSettings() {
      this.addLog('尝试打开位置设置', 'info')
      
      // #ifdef APP-PLUS
      plus.runtime.openURL('app-settings:')
      // #endif
      
      // #ifdef MP-WEIXIN
      uni.openSetting({
        success: (res) => {
          this.addLog('设置页面打开成功', 'success')
        },
        fail: (err) => {
          this.addLog(`设置页面打开失败: ${err.errMsg}`, 'error')
        }
      })
      // #endif
      
      // #ifdef H5
      this.addLog('H5环境下无法直接打开系统设置', 'warning')
      // #endif
    },
    
    clearLocationInfo() {
      this.locationInfo = {
        longitude: '',
        latitude: '',
        accuracy: '',
        address: ''
      }
      this.addLog('位置信息已清除', 'info')
    },
    
    addLog(message, type = 'info') {
      const now = new Date()
      const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
      
      this.testLogs.unshift({
        time,
        message,
        type
      })
      
      // 限制日志数量
      if (this.testLogs.length > 50) {
        this.testLogs = this.testLogs.slice(0, 50)
      }
    }
  }
}
</script>

<style scoped>
.position-test-page {
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

.info-card {
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

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-size: 28rpx;
  color: #666;
  font-weight: 500;
}

.value {
  font-size: 28rpx;
  color: #333;
  flex: 1;
  text-align: right;
  word-break: break-all;
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
  padding: 10rpx;
  border-radius: 8rpx;
  background: white;
}

.log-item.success {
  border-left: 6rpx solid #4caf50;
}

.log-item.error {
  border-left: 6rpx solid #f44336;
}

.log-item.warning {
  border-left: 6rpx solid #ff9800;
}

.log-item.info {
  border-left: 6rpx solid #2196f3;
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
  word-break: break-all;
}
</style>