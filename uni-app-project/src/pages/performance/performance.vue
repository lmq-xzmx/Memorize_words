<template>
  <view class="performance-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">📊 性能监控</text>
      <text class="page-subtitle">开发工具 - 应用性能分析</text>
    </view>

    <!-- 功能状态 -->
    <view class="status-card">
      <view class="status-header">
        <text class="status-title">⚡ 监控状态</text>
        <view class="status-badge disabled">
          <text class="badge-text">未启用</text>
        </view>
      </view>
      
      <text class="status-description">
        性能监控功能当前处于开发阶段，暂未启用。此功能将提供应用性能的实时监控、分析和优化建议。
      </text>
      
      <view class="status-features">
        <text class="features-title">监控指标:</text>
        <view class="feature-list">
          <view class="feature-item">
            <text class="feature-icon">🚀</text>
            <text class="feature-text">页面加载性能</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">💾</text>
            <text class="feature-text">内存使用情况</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">🔄</text>
            <text class="feature-text">网络请求分析</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">📱</text>
            <text class="feature-text">设备性能指标</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 性能概览 -->
    <view class="overview-section">
      <text class="section-title">📈 性能概览</text>
      <text class="section-subtitle">应用整体性能表现</text>
      
      <view class="metrics-grid">
        <view class="metric-card disabled">
          <view class="metric-icon">⚡</view>
          <view class="metric-content">
            <text class="metric-label">性能评分</text>
            <text class="metric-value">--</text>
            <text class="metric-unit">/100</text>
          </view>
        </view>
        
        <view class="metric-card disabled">
          <view class="metric-icon">🚀</view>
          <view class="metric-content">
            <text class="metric-label">平均加载时间</text>
            <text class="metric-value">--</text>
            <text class="metric-unit">ms</text>
          </view>
        </view>
        
        <view class="metric-card disabled">
          <view class="metric-icon">💾</view>
          <view class="metric-content">
            <text class="metric-label">内存使用</text>
            <text class="metric-value">--</text>
            <text class="metric-unit">MB</text>
          </view>
        </view>
        
        <view class="metric-card disabled">
          <view class="metric-icon">📊</view>
          <view class="metric-content">
            <text class="metric-label">FPS</text>
            <text class="metric-value">--</text>
            <text class="metric-unit">fps</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 详细监控面板 -->
    <view class="monitoring-section">
      <text class="section-title">🔍 详细监控</text>
      
      <!-- 页面性能 -->
      <view class="monitor-panel disabled">
        <view class="panel-header">
          <text class="panel-title">📄 页面性能</text>
          <view class="panel-status">
            <view class="status-dot offline"></view>
            <text class="status-text">离线</text>
          </view>
        </view>
        
        <view class="performance-chart">
          <view class="chart-placeholder">
            <text class="placeholder-text">📊 性能图表</text>
            <text class="placeholder-desc">功能启用后显示实时性能数据</text>
          </view>
        </view>
        
        <view class="performance-details">
          <view class="detail-row">
            <text class="detail-label">首屏渲染时间</text>
            <text class="detail-value">-- ms</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">DOM 构建时间</text>
            <text class="detail-value">-- ms</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">资源加载时间</text>
            <text class="detail-value">-- ms</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">交互响应时间</text>
            <text class="detail-value">-- ms</text>
          </view>
        </view>
      </view>
      
      <!-- 网络监控 -->
      <view class="monitor-panel disabled">
        <view class="panel-header">
          <text class="panel-title">🌐 网络监控</text>
          <view class="panel-status">
            <view class="status-dot offline"></view>
            <text class="status-text">离线</text>
          </view>
        </view>
        
        <view class="network-stats">
          <view class="stat-item">
            <text class="stat-label">请求总数</text>
            <text class="stat-value">--</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">成功率</text>
            <text class="stat-value">--%</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">平均响应时间</text>
            <text class="stat-value">-- ms</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">数据传输量</text>
            <text class="stat-value">-- KB</text>
          </view>
        </view>
        
        <view class="request-list">
          <view class="list-header">
            <text class="header-text">最近请求</text>
          </view>
          <view class="request-item">
            <text class="request-method">--</text>
            <text class="request-url">等待数据...</text>
            <text class="request-status">--</text>
            <text class="request-time">-- ms</text>
          </view>
        </view>
      </view>
      
      <!-- 资源监控 -->
      <view class="monitor-panel disabled">
        <view class="panel-header">
          <text class="panel-title">💾 资源监控</text>
          <view class="panel-status">
            <view class="status-dot offline"></view>
            <text class="status-text">离线</text>
          </view>
        </view>
        
        <view class="resource-usage">
          <view class="usage-item">
            <view class="usage-header">
              <text class="usage-label">内存使用</text>
              <text class="usage-percent">--%</text>
            </view>
            <view class="usage-bar">
              <view class="usage-fill" style="width: 0%"></view>
            </view>
            <text class="usage-detail">-- MB / -- MB</text>
          </view>
          
          <view class="usage-item">
            <view class="usage-header">
              <text class="usage-label">CPU 使用</text>
              <text class="usage-percent">--%</text>
            </view>
            <view class="usage-bar">
              <view class="usage-fill" style="width: 0%"></view>
            </view>
            <text class="usage-detail">-- 核心</text>
          </view>
          
          <view class="usage-item">
            <view class="usage-header">
              <text class="usage-label">存储空间</text>
              <text class="usage-percent">--%</text>
            </view>
            <view class="usage-bar">
              <view class="usage-fill" style="width: 0%"></view>
            </view>
            <text class="usage-detail">-- MB / -- MB</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 性能建议 -->
    <view class="suggestions-section">
      <text class="section-title">💡 性能建议</text>
      
      <view class="suggestion-list">
        <view class="suggestion-item">
          <view class="suggestion-icon">🚀</view>
          <view class="suggestion-content">
            <text class="suggestion-title">优化页面加载</text>
            <text class="suggestion-desc">减少首屏资源大小，使用懒加载技术</text>
          </view>
          <view class="suggestion-priority high">
            <text class="priority-text">高</text>
          </view>
        </view>
        
        <view class="suggestion-item">
          <view class="suggestion-icon">💾</view>
          <view class="suggestion-content">
            <text class="suggestion-title">内存优化</text>
            <text class="suggestion-desc">及时释放不用的对象，避免内存泄漏</text>
          </view>
          <view class="suggestion-priority medium">
            <text class="priority-text">中</text>
          </view>
        </view>
        
        <view class="suggestion-item">
          <view class="suggestion-icon">🔄</view>
          <view class="suggestion-content">
            <text class="suggestion-title">网络优化</text>
            <text class="suggestion-desc">合并请求，使用缓存策略</text>
          </view>
          <view class="suggestion-priority low">
            <text class="priority-text">低</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-section">
      <button class="enable-btn" @click="requestEnable">
        ⚡ 申请启用
      </button>
      
      <button class="report-btn" @click="generateReport">
        📋 生成报告
      </button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      enableRequested: false
    }
  },
  
  onLoad() {
    this.checkEnableStatus()
  },
  
  methods: {
    /**
     * 检查启用状态
     */
    checkEnableStatus() {
      try {
        const status = uni.getStorageSync('performance_monitor_request')
        this.enableRequested = !!status
      } catch (e) {
        console.error('检查启用状态失败:', e)
      }
    },
    
    /**
     * 申请启用功能
     */
    requestEnable() {
      if (this.enableRequested) {
        uni.showToast({
          title: '已提交申请',
          icon: 'success'
        })
        return
      }
      
      uni.showModal({
        title: '申请启用',
        content: '性能监控功能需要获取应用运行数据，是否申请启用此功能？',
        success: (res) => {
          if (res.confirm) {
            try {
              uni.setStorageSync('performance_monitor_request', true)
              this.enableRequested = true
              
              uni.showToast({
                title: '申请已提交',
                icon: 'success'
              })
              
              // 模拟申请处理
              setTimeout(() => {
                uni.showModal({
                  title: '申请处理中',
                  content: '您的申请正在处理中，我们会在功能开发完成后第一时间通知您。',
                  showCancel: false,
                  confirmText: '知道了'
                })
              }, 1500)
            } catch (e) {
              uni.showToast({
                title: '申请失败',
                icon: 'error'
              })
            }
          }
        }
      })
    },
    
    /**
     * 生成性能报告
     */
    generateReport() {
      uni.showLoading({
        title: '生成中...'
      })
      
      // 模拟报告生成
      setTimeout(() => {
        uni.hideLoading()
        
        uni.showModal({
          title: '性能报告',
          content: '当前功能未启用，无法生成性能报告。\n\n报告将包含：\n• 性能评分\n• 优化建议\n• 详细分析\n• 历史对比',
          showCancel: false,
          confirmText: '知道了'
        })
      }, 2000)
    }
  }
}
</script>

<style scoped>
.performance-page {
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

.overview-section {
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
  
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16rpx;
    
    .metric-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 24rpx;
      display: flex;
      align-items: center;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      &.disabled {
        opacity: 0.6;
      }
      
      .metric-icon {
        font-size: 40rpx;
        margin-right: 16rpx;
      }
      
      .metric-content {
        flex: 1;
        
        .metric-label {
          display: block;
          font-size: 22rpx;
          color: #666666;
          margin-bottom: 4rpx;
        }
        
        .metric-value {
          font-size: 32rpx;
          font-weight: bold;
          color: #333333;
        }
        
        .metric-unit {
          font-size: 20rpx;
          color: #999999;
          margin-left: 4rpx;
        }
      }
    }
  }
}

.monitoring-section {
  margin-bottom: 32rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .monitor-panel {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 16rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    &.disabled {
      opacity: 0.6;
    }
    
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
      
      .panel-status {
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
  }
}

.performance-chart {
  margin-bottom: 20rpx;
  
  .chart-placeholder {
    height: 200rpx;
    background: #f5f5f5;
    border-radius: 8rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    
    .placeholder-text {
      font-size: 28rpx;
      color: #999999;
      margin-bottom: 8rpx;
    }
    
    .placeholder-desc {
      font-size: 22rpx;
      color: #cccccc;
    }
  }
}

.performance-details {
  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .detail-label {
      font-size: 24rpx;
      color: #666666;
    }
    
    .detail-value {
      font-size: 24rpx;
      color: #999999;
      font-family: monospace;
    }
  }
}

.network-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  margin-bottom: 20rpx;
  
  .stat-item {
    text-align: center;
    padding: 16rpx;
    background: #f5f5f5;
    border-radius: 8rpx;
    
    .stat-label {
      display: block;
      font-size: 22rpx;
      color: #666666;
      margin-bottom: 8rpx;
    }
    
    .stat-value {
      display: block;
      font-size: 28rpx;
      font-weight: bold;
      color: #999999;
    }
  }
}

.request-list {
  .list-header {
    padding: 12rpx 0;
    border-bottom: 2rpx solid #e8e8e8;
    margin-bottom: 12rpx;
    
    .header-text {
      font-size: 24rpx;
      font-weight: bold;
      color: #333333;
    }
  }
  
  .request-item {
    display: flex;
    align-items: center;
    padding: 12rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
    
    .request-method {
      width: 80rpx;
      font-size: 20rpx;
      color: #999999;
      font-family: monospace;
    }
    
    .request-url {
      flex: 1;
      font-size: 22rpx;
      color: #666666;
      margin: 0 12rpx;
    }
    
    .request-status {
      width: 60rpx;
      font-size: 20rpx;
      color: #999999;
      text-align: center;
    }
    
    .request-time {
      width: 80rpx;
      font-size: 20rpx;
      color: #999999;
      text-align: right;
      font-family: monospace;
    }
  }
}

.resource-usage {
  .usage-item {
    margin-bottom: 24rpx;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .usage-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8rpx;
      
      .usage-label {
        font-size: 24rpx;
        color: #333333;
      }
      
      .usage-percent {
        font-size: 24rpx;
        font-weight: bold;
        color: #999999;
      }
    }
    
    .usage-bar {
      height: 12rpx;
      background: #f0f0f0;
      border-radius: 6rpx;
      overflow: hidden;
      margin-bottom: 8rpx;
      
      .usage-fill {
        height: 100%;
        background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
        transition: width 0.3s ease;
      }
    }
    
    .usage-detail {
      font-size: 20rpx;
      color: #999999;
    }
  }
}

.suggestions-section {
  margin-bottom: 32rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .suggestion-list {
    .suggestion-item {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 24rpx;
      margin-bottom: 16rpx;
      display: flex;
      align-items: center;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      .suggestion-icon {
        font-size: 32rpx;
        margin-right: 16rpx;
      }
      
      .suggestion-content {
        flex: 1;
        
        .suggestion-title {
          display: block;
          font-size: 26rpx;
          font-weight: bold;
          color: #333333;
          margin-bottom: 8rpx;
        }
        
        .suggestion-desc {
          display: block;
          font-size: 22rpx;
          color: #666666;
          line-height: 1.4;
        }
      }
      
      .suggestion-priority {
        padding: 6rpx 12rpx;
        border-radius: 12rpx;
        
        &.high {
          background: #fff2f0;
          
          .priority-text {
            color: #ff4d4f;
          }
        }
        
        &.medium {
          background: #fff7e6;
          
          .priority-text {
            color: #fa8c16;
          }
        }
        
        &.low {
          background: #f6ffed;
          
          .priority-text {
            color: #52c41a;
          }
        }
        
        .priority-text {
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
  
  .enable-btn, .report-btn {
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
  
  .enable-btn {
    background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
    color: #ffffff;
    box-shadow: 0 8rpx 24rpx rgba(24, 144, 255, 0.4);
  }
  
  .report-btn {
    background: rgba(255, 255, 255, 0.9);
    color: #333333;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  }
}
</style>