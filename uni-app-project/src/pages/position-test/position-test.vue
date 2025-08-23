<template>
  <view class="position-test-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">📍 位置测试</text>
      <text class="page-subtitle">开发工具 - 定位功能调试</text>
    </view>

    <!-- 功能状态 -->
    <view class="status-card">
      <view class="status-header">
        <text class="status-title">🚧 功能状态</text>
        <view class="status-badge disabled">
          <text class="badge-text">未启用</text>
        </view>
      </view>
      
      <text class="status-description">
        位置测试功能当前处于开发阶段，暂未启用。此功能将用于测试应用的定位服务、地理位置获取和相关API调用。
      </text>
      
      <view class="status-features">
        <text class="features-title">计划功能:</text>
        <view class="feature-list">
          <view class="feature-item">
            <text class="feature-icon">🌍</text>
            <text class="feature-text">GPS定位测试</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">📡</text>
            <text class="feature-text">网络定位测试</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">🗺️</text>
            <text class="feature-text">地图服务集成</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">📊</text>
            <text class="feature-text">定位精度分析</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 模拟界面预览 -->
    <view class="preview-section">
      <text class="section-title">🎨 界面预览</text>
      <text class="section-subtitle">功能启用后的界面效果</text>
      
      <view class="preview-container">
        <!-- 定位控制面板 -->
        <view class="control-panel disabled">
          <view class="panel-header">
            <text class="panel-title">定位控制</text>
            <view class="location-status">
              <view class="status-dot offline"></view>
              <text class="status-text">离线</text>
            </view>
          </view>
          
          <view class="control-buttons">
            <button class="control-btn" disabled>
              📍 获取当前位置
            </button>
            <button class="control-btn" disabled>
              🔄 刷新位置
            </button>
            <button class="control-btn" disabled>
              ⚙️ 定位设置
            </button>
          </view>
        </view>
        
        <!-- 位置信息显示 -->
        <view class="location-info disabled">
          <text class="info-title">位置信息</text>
          
          <view class="info-grid">
            <view class="info-item">
              <text class="info-label">经度</text>
              <text class="info-value">---.------</text>
            </view>
            
            <view class="info-item">
              <text class="info-label">纬度</text>
              <text class="info-value">---.------</text>
            </view>
            
            <view class="info-item">
              <text class="info-label">精度</text>
              <text class="info-value">--- 米</text>
            </view>
            
            <view class="info-item">
              <text class="info-label">海拔</text>
              <text class="info-value">--- 米</text>
            </view>
            
            <view class="info-item">
              <text class="info-label">速度</text>
              <text class="info-value">--- m/s</text>
            </view>
            
            <view class="info-item">
              <text class="info-label">方向</text>
              <text class="info-value">---°</text>
            </view>
          </view>
        </view>
        
        <!-- 地址解析 -->
        <view class="address-section disabled">
          <text class="address-title">地址解析</text>
          
          <view class="address-content">
            <view class="address-item">
              <text class="address-label">国家:</text>
              <text class="address-value">---</text>
            </view>
            
            <view class="address-item">
              <text class="address-label">省份:</text>
              <text class="address-value">---</text>
            </view>
            
            <view class="address-item">
              <text class="address-label">城市:</text>
              <text class="address-value">---</text>
            </view>
            
            <view class="address-item">
              <text class="address-label">区县:</text>
              <text class="address-value">---</text>
            </view>
            
            <view class="address-item">
              <text class="address-label">详细地址:</text>
              <text class="address-value">---</text>
            </view>
          </view>
        </view>
        
        <!-- 测试日志 -->
        <view class="test-logs disabled">
          <view class="logs-header">
            <text class="logs-title">测试日志</text>
            <button class="clear-logs-btn" disabled>清空</button>
          </view>
          
          <view class="logs-content">
            <view class="log-item">
              <text class="log-time">[--:--:--]</text>
              <text class="log-message">等待功能启用...</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 开发计划 -->
    <view class="roadmap-section">
      <text class="section-title">🛣️ 开发计划</text>
      
      <view class="roadmap-list">
        <view class="roadmap-item">
          <view class="roadmap-status planning">
            <text class="status-icon">📋</text>
          </view>
          
          <view class="roadmap-content">
            <text class="roadmap-title">需求分析与设计</text>
            <text class="roadmap-description">分析定位功能需求，设计用户界面和交互流程</text>
            <text class="roadmap-progress">规划中</text>
          </view>
        </view>
        
        <view class="roadmap-item">
          <view class="roadmap-status planning">
            <text class="status-icon">🔧</text>
          </view>
          
          <view class="roadmap-content">
            <text class="roadmap-title">核心功能开发</text>
            <text class="roadmap-description">实现GPS定位、网络定位和地址解析功能</text>
            <text class="roadmap-progress">待开发</text>
          </view>
        </view>
        
        <view class="roadmap-item">
          <view class="roadmap-status planning">
            <text class="status-icon">🧪</text>
          </view>
          
          <view class="roadmap-content">
            <text class="roadmap-title">功能测试</text>
            <text class="roadmap-description">在不同设备和环境下测试定位功能的准确性和稳定性</text>
            <text class="roadmap-progress">待测试</text>
          </view>
        </view>
        
        <view class="roadmap-item">
          <view class="roadmap-status planning">
            <text class="status-icon">🚀</text>
          </view>
          
          <view class="roadmap-content">
            <text class="roadmap-title">功能发布</text>
            <text class="roadmap-description">完成测试后正式发布位置测试功能</text>
            <text class="roadmap-progress">待发布</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-section">
      <button class="notify-btn" @click="requestNotification">
        🔔 功能上线通知
      </button>
      
      <button class="feedback-btn" @click="submitFeedback">
        💬 提交建议
      </button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      notificationRequested: false
    }
  },
  
  onLoad() {
    this.checkNotificationStatus()
  },
  
  methods: {
    /**
     * 检查通知状态
     */
    checkNotificationStatus() {
      try {
        const status = uni.getStorageSync('position_test_notification')
        this.notificationRequested = !!status
      } catch (e) {
        console.error('检查通知状态失败:', e)
      }
    },
    
    /**
     * 请求功能上线通知
     */
    requestNotification() {
      if (this.notificationRequested) {
        uni.showToast({
          title: '已设置通知提醒',
          icon: 'success'
        })
        return
      }
      
      uni.showModal({
        title: '设置通知',
        content: '是否在位置测试功能上线时通知您？',
        success: (res) => {
          if (res.confirm) {
            try {
              uni.setStorageSync('position_test_notification', true)
              this.notificationRequested = true
              
              uni.showToast({
                title: '通知设置成功',
                icon: 'success'
              })
            } catch (e) {
              uni.showToast({
                title: '设置失败',
                icon: 'error'
              })
            }
          }
        }
      })
    },
    
    /**
     * 提交功能建议
     */
    submitFeedback() {
      uni.showModal({
        title: '功能建议',
        content: '您可以通过以下方式提交对位置测试功能的建议：\n\n1. 应用内反馈\n2. 邮件联系\n3. 社区讨论',
        showCancel: false,
        confirmText: '知道了'
      })
    }
  }
}
</script>

<style scoped>
.position-test-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 32rpx 200rpx;
}

.page-header {
  text-align: center;
  margin-bottom: 40rpx;
  
  .page-title {
    display: block;
    font-size: 56rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 16rpx;
  }
  
  .page-subtitle {
    display: block;
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}

.status-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 32rpx 24rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
    
    .status-title {
      font-size: 32rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .status-badge {
      padding: 8rpx 16rpx;
      border-radius: 16rpx;
      
      &.disabled {
        background: #fff2f0;
        
        .badge-text {
          color: #ff4d4f;
          font-size: 22rpx;
          font-weight: bold;
        }
      }
    }
  }
  
  .status-description {
    display: block;
    font-size: 26rpx;
    color: #666666;
    line-height: 1.6;
    margin-bottom: 24rpx;
  }
  
  .status-features {
    .features-title {
      display: block;
      font-size: 26rpx;
      font-weight: bold;
      color: #333333;
      margin-bottom: 16rpx;
    }
    
    .feature-list {
      .feature-item {
        display: flex;
        align-items: center;
        padding: 12rpx 0;
        
        .feature-icon {
          font-size: 24rpx;
          margin-right: 12rpx;
        }
        
        .feature-text {
          font-size: 24rpx;
          color: #666666;
        }
      }
    }
  }
}

.preview-section {
  margin-bottom: 32rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 8rpx;
  }
  
  .section-subtitle {
    display: block;
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 24rpx;
  }
  
  .preview-container {
    .disabled {
      opacity: 0.6;
      pointer-events: none;
    }
  }
}

.control-panel {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    
    .panel-title {
      font-size: 28rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .location-status {
      display: flex;
      align-items: center;
      
      .status-dot {
        width: 16rpx;
        height: 16rpx;
        border-radius: 50%;
        margin-right: 8rpx;
        
        &.offline {
          background: #ff4d4f;
        }
        
        &.online {
          background: #52c41a;
        }
      }
      
      .status-text {
        font-size: 22rpx;
        color: #666666;
      }
    }
  }
  
  .control-buttons {
    display: flex;
    gap: 12rpx;
    
    .control-btn {
      flex: 1;
      height: 64rpx;
      background: #f5f5f5;
      color: #999999;
      border: 2rpx solid #e8e8e8;
      border-radius: 32rpx;
      font-size: 24rpx;
    }
  }
}

.location-info {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .info-title {
    display: block;
    font-size: 28rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 20rpx;
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16rpx;
    
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12rpx 16rpx;
      background: #f5f5f5;
      border-radius: 8rpx;
      
      .info-label {
        font-size: 24rpx;
        color: #666666;
      }
      
      .info-value {
        font-size: 24rpx;
        color: #999999;
        font-family: monospace;
      }
    }
  }
}

.address-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .address-title {
    display: block;
    font-size: 28rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 20rpx;
  }
  
  .address-content {
    .address-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12rpx 0;
      border-bottom: 1rpx solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .address-label {
        font-size: 24rpx;
        color: #666666;
        width: 120rpx;
      }
      
      .address-value {
        flex: 1;
        font-size: 24rpx;
        color: #999999;
        text-align: right;
      }
    }
  }
}

.test-logs {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .logs-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
    
    .logs-title {
      font-size: 28rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .clear-logs-btn {
      padding: 8rpx 16rpx;
      background: #f5f5f5;
      color: #999999;
      border: 1rpx solid #e8e8e8;
      border-radius: 8rpx;
      font-size: 22rpx;
    }
  }
  
  .logs-content {
    background: #f5f5f5;
    border-radius: 8rpx;
    padding: 16rpx;
    min-height: 120rpx;
    
    .log-item {
      display: flex;
      margin-bottom: 8rpx;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .log-time {
        font-size: 20rpx;
        color: #999999;
        margin-right: 12rpx;
        font-family: monospace;
      }
      
      .log-message {
        font-size: 22rpx;
        color: #666666;
        flex: 1;
      }
    }
  }
}

.roadmap-section {
  margin-bottom: 32rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .roadmap-list {
    .roadmap-item {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 24rpx;
      margin-bottom: 16rpx;
      display: flex;
      align-items: flex-start;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      .roadmap-status {
        width: 60rpx;
        height: 60rpx;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20rpx;
        flex-shrink: 0;
        
        &.planning {
          background: #fff7e6;
          
          .status-icon {
            font-size: 24rpx;
          }
        }
      }
      
      .roadmap-content {
        flex: 1;
        
        .roadmap-title {
          display: block;
          font-size: 28rpx;
          font-weight: bold;
          color: #333333;
          margin-bottom: 8rpx;
        }
        
        .roadmap-description {
          display: block;
          font-size: 24rpx;
          color: #666666;
          line-height: 1.5;
          margin-bottom: 12rpx;
        }
        
        .roadmap-progress {
          display: inline-block;
          padding: 4rpx 12rpx;
          background: #fff7e6;
          color: #fa8c16;
          border-radius: 12rpx;
          font-size: 20rpx;
          font-weight: bold;
        }
      }
    }
  }
}

.action-section {
  display: flex;
  gap: 16rpx;
  
  .notify-btn, .feedback-btn {
    flex: 1;
    height: 88rpx;
    border: none;
    border-radius: 44rpx;
    font-size: 28rpx;
    font-weight: bold;
    transition: all 0.3s ease;
    
    &:active {
      transform: scale(0.98);
    }
  }
  
  .notify-btn {
    background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
    color: #ffffff;
    box-shadow: 0 8rpx 24rpx rgba(82, 196, 26, 0.4);
  }
  
  .feedback-btn {
    background: rgba(255, 255, 255, 0.9);
    color: #333333;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  }
}
</style>