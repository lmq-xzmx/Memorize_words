<template>
  <view class="api-test-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">🔧 API测试</text>
      <text class="page-subtitle">开发工具 - 接口调试</text>
    </view>

    <!-- 测试配置 -->
    <view class="test-config">
      <view class="config-section">
        <text class="section-title">请求配置</text>
        
        <!-- 请求方法 -->
        <view class="config-item">
          <text class="config-label">请求方法</text>
          <picker 
            :value="methodIndex" 
            :range="methods" 
            @change="onMethodChange"
            class="method-picker"
          >
            <view class="picker-content">
              <text class="picker-text">{{ methods[methodIndex] }}</text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>
        
        <!-- 请求URL -->
        <view class="config-item">
          <text class="config-label">请求URL</text>
          <input 
            v-model="requestUrl" 
            placeholder="请输入API地址"
            class="url-input"
          />
        </view>
        
        <!-- 请求头 -->
        <view class="config-item">
          <view class="config-header">
            <text class="config-label">请求头</text>
            <button class="add-btn" @click="addHeader">+ 添加</button>
          </view>
          
          <view class="headers-list">
            <view 
              v-for="(header, index) in headers" 
              :key="index"
              class="header-item"
            >
              <input 
                v-model="header.key" 
                placeholder="Header名称"
                class="header-input key"
              />
              <input 
                v-model="header.value" 
                placeholder="Header值"
                class="header-input value"
              />
              <button class="remove-btn" @click="removeHeader(index)">×</button>
            </view>
          </view>
        </view>
        
        <!-- 请求体 -->
        <view class="config-item" v-if="needsBody">
          <text class="config-label">请求体</text>
          <textarea 
            v-model="requestBody" 
            placeholder="请输入JSON格式的请求体"
            class="body-textarea"
          ></textarea>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="test-btn" @click="sendRequest" :disabled="testing">
        {{ testing ? '测试中...' : '🚀 发送请求' }}
      </button>
      
      <button class="clear-btn" @click="clearAll">
        🗑️ 清空
      </button>
      
      <button class="save-btn" @click="saveConfig">
        💾 保存配置
      </button>
    </view>

    <!-- 响应结果 -->
    <view class="response-section" v-if="response">
      <view class="section-header">
        <text class="section-title">响应结果</text>
        <view class="response-status" :class="getStatusClass(response.status)">
          <text class="status-text">{{ response.status }}</text>
        </view>
      </view>
      
      <!-- 响应信息 -->
      <view class="response-info">
        <view class="info-item">
          <text class="info-label">状态码:</text>
          <text class="info-value">{{ response.statusCode }}</text>
        </view>
        
        <view class="info-item">
          <text class="info-label">响应时间:</text>
          <text class="info-value">{{ response.responseTime }}ms</text>
        </view>
        
        <view class="info-item">
          <text class="info-label">数据大小:</text>
          <text class="info-value">{{ response.dataSize }}</text>
        </view>
      </view>
      
      <!-- 响应头 -->
      <view class="response-headers" v-if="response.headers">
        <text class="sub-title">响应头</text>
        <view class="headers-content">
          <text class="headers-text">{{ formatHeaders(response.headers) }}</text>
        </view>
      </view>
      
      <!-- 响应体 -->
      <view class="response-body">
        <text class="sub-title">响应体</text>
        <view class="body-content">
          <text class="body-text">{{ formatResponseBody(response.data) }}</text>
        </view>
      </view>
    </view>

    <!-- 历史记录 -->
    <view class="history-section" v-if="history.length > 0">
      <view class="section-header">
        <text class="section-title">📋 历史记录</text>
        <button class="clear-history-btn" @click="clearHistory">清空历史</button>
      </view>
      
      <view class="history-list">
        <view 
          v-for="(item, index) in history" 
          :key="index"
          class="history-item"
          @click="loadFromHistory(item)"
        >
          <view class="history-method" :class="item.method.toLowerCase()">
            <text class="method-text">{{ item.method }}</text>
          </view>
          
          <view class="history-info">
            <text class="history-url">{{ item.url }}</text>
            <text class="history-time">{{ item.time }}</text>
          </view>
          
          <view class="history-status" :class="getStatusClass(item.status)">
            <text class="status-code">{{ item.statusCode }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      // 请求配置
      methodIndex: 0,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
      requestUrl: 'https://jsonplaceholder.typicode.com/posts/1',
      headers: [
        { key: 'Content-Type', value: 'application/json' }
      ],
      requestBody: '',
      
      // 状态
      testing: false,
      response: null,
      
      // 历史记录
      history: []
    }
  },
  
  computed: {
    needsBody() {
      return ['POST', 'PUT', 'PATCH'].includes(this.methods[this.methodIndex])
    }
  },
  
  onLoad() {
    this.loadHistory()
  },
  
  methods: {
    /**
     * 切换请求方法
     */
    onMethodChange(e) {
      this.methodIndex = e.detail.value
    },
    
    /**
     * 添加请求头
     */
    addHeader() {
      this.headers.push({ key: '', value: '' })
    },
    
    /**
     * 移除请求头
     */
    removeHeader(index) {
      this.headers.splice(index, 1)
    },
    
    /**
     * 发送请求
     */
    async sendRequest() {
      if (!this.requestUrl.trim()) {
        uni.showToast({
          title: '请输入请求URL',
          icon: 'none'
        })
        return
      }
      
      this.testing = true
      const startTime = Date.now()
      
      try {
        // 构建请求头
        const headers = {}
        this.headers.forEach(header => {
          if (header.key && header.value) {
            headers[header.key] = header.value
          }
        })
        
        // 构建请求配置
        const config = {
          url: this.requestUrl,
          method: this.methods[this.methodIndex],
          header: headers,
          timeout: 10000
        }
        
        // 添加请求体
        if (this.needsBody && this.requestBody) {
          try {
            config.data = JSON.parse(this.requestBody)
          } catch (e) {
            config.data = this.requestBody
          }
        }
        
        // 发送请求
        const result = await this.makeRequest(config)
        const endTime = Date.now()
        
        // 构建响应对象
        this.response = {
          status: 'success',
          statusCode: result.statusCode,
          responseTime: endTime - startTime,
          dataSize: this.calculateDataSize(result.data),
          headers: result.header,
          data: result.data
        }
        
        // 保存到历史记录
        this.saveToHistory({
          method: this.methods[this.methodIndex],
          url: this.requestUrl,
          statusCode: result.statusCode,
          status: 'success',
          time: new Date().toLocaleString()
        })
        
        uni.showToast({
          title: '请求成功',
          icon: 'success'
        })
        
      } catch (error) {
        const endTime = Date.now()
        
        this.response = {
          status: 'error',
          statusCode: error.statusCode || 0,
          responseTime: endTime - startTime,
          dataSize: '0B',
          headers: null,
          data: error.errMsg || '请求失败'
        }
        
        // 保存到历史记录
        this.saveToHistory({
          method: this.methods[this.methodIndex],
          url: this.requestUrl,
          statusCode: error.statusCode || 0,
          status: 'error',
          time: new Date().toLocaleString()
        })
        
        uni.showToast({
          title: '请求失败',
          icon: 'error'
        })
      } finally {
        this.testing = false
      }
    },
    
    /**
     * 发起网络请求
     */
    makeRequest(config) {
      return new Promise((resolve, reject) => {
        uni.request({
          ...config,
          success: resolve,
          fail: reject
        })
      })
    },
    
    /**
     * 计算数据大小
     */
    calculateDataSize(data) {
      const size = JSON.stringify(data).length
      if (size < 1024) {
        return size + 'B'
      } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + 'KB'
      } else {
        return (size / (1024 * 1024)).toFixed(2) + 'MB'
      }
    },
    
    /**
     * 格式化响应头
     */
    formatHeaders(headers) {
      if (!headers) return '无'
      return Object.entries(headers)
        .map(([key, value]) => `${key}: ${value}`)
        .join('\n')
    },
    
    /**
     * 格式化响应体
     */
    formatResponseBody(data) {
      if (typeof data === 'object') {
        return JSON.stringify(data, null, 2)
      }
      return String(data)
    },
    
    /**
     * 获取状态样式类
     */
    getStatusClass(status) {
      if (status === 'success') return 'success'
      if (status === 'error') return 'error'
      return 'default'
    },
    
    /**
     * 清空所有配置
     */
    clearAll() {
      this.methodIndex = 0
      this.requestUrl = ''
      this.headers = [{ key: 'Content-Type', value: 'application/json' }]
      this.requestBody = ''
      this.response = null
      
      uni.showToast({
        title: '已清空配置',
        icon: 'success'
      })
    },
    
    /**
     * 保存配置
     */
    saveConfig() {
      const config = {
        method: this.methods[this.methodIndex],
        url: this.requestUrl,
        headers: this.headers,
        body: this.requestBody
      }
      
      uni.setStorageSync('api_test_config', config)
      
      uni.showToast({
        title: '配置已保存',
        icon: 'success'
      })
    },
    
    /**
     * 保存到历史记录
     */
    saveToHistory(item) {
      this.history.unshift(item)
      if (this.history.length > 20) {
        this.history = this.history.slice(0, 20)
      }
      uni.setStorageSync('api_test_history', this.history)
    },
    
    /**
     * 加载历史记录
     */
    loadHistory() {
      try {
        const history = uni.getStorageSync('api_test_history')
        if (history) {
          this.history = history
        }
        
        const config = uni.getStorageSync('api_test_config')
        if (config) {
          this.methodIndex = this.methods.indexOf(config.method) || 0
          this.requestUrl = config.url || ''
          this.headers = config.headers || [{ key: 'Content-Type', value: 'application/json' }]
          this.requestBody = config.body || ''
        }
      } catch (e) {
        console.error('加载历史记录失败:', e)
      }
    },
    
    /**
     * 从历史记录加载
     */
    loadFromHistory(item) {
      this.methodIndex = this.methods.indexOf(item.method) || 0
      this.requestUrl = item.url
      
      uni.showToast({
        title: '已加载历史配置',
        icon: 'success'
      })
    },
    
    /**
     * 清空历史记录
     */
    clearHistory() {
      uni.showModal({
        title: '确认清空',
        content: '确定要清空所有历史记录吗？',
        success: (res) => {
          if (res.confirm) {
            this.history = []
            uni.removeStorageSync('api_test_history')
            uni.showToast({
              title: '历史记录已清空',
              icon: 'success'
            })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.api-test-page {
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

.test-config {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 32rpx 24rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .config-section {
    .section-title {
      display: block;
      font-size: 32rpx;
      font-weight: bold;
      color: #333333;
      margin-bottom: 24rpx;
    }
    
    .config-item {
      margin-bottom: 24rpx;
      
      .config-label {
        display: block;
        font-size: 26rpx;
        color: #666666;
        margin-bottom: 12rpx;
      }
      
      .config-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12rpx;
        
        .add-btn {
          padding: 8rpx 16rpx;
          background: #1890ff;
          color: #ffffff;
          border: none;
          border-radius: 8rpx;
          font-size: 22rpx;
        }
      }
    }
  }
}

.method-picker {
  .picker-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16rpx 20rpx;
    background: #f5f5f5;
    border-radius: 8rpx;
    border: 2rpx solid #e8e8e8;
    
    .picker-text {
      font-size: 28rpx;
      color: #333333;
    }
    
    .picker-arrow {
      font-size: 20rpx;
      color: #999999;
    }
  }
}

.url-input {
  width: 100%;
  padding: 16rpx 20rpx;
  background: #f5f5f5;
  border: 2rpx solid #e8e8e8;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333333;
}

.headers-list {
  .header-item {
    display: flex;
    align-items: center;
    margin-bottom: 12rpx;
    
    .header-input {
      padding: 12rpx 16rpx;
      background: #f5f5f5;
      border: 2rpx solid #e8e8e8;
      border-radius: 8rpx;
      font-size: 24rpx;
      color: #333333;
      
      &.key {
        flex: 1;
        margin-right: 12rpx;
      }
      
      &.value {
        flex: 2;
        margin-right: 12rpx;
      }
    }
    
    .remove-btn {
      width: 48rpx;
      height: 48rpx;
      background: #ff4d4f;
      color: #ffffff;
      border: none;
      border-radius: 50%;
      font-size: 24rpx;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

.body-textarea {
  width: 100%;
  min-height: 200rpx;
  padding: 16rpx 20rpx;
  background: #f5f5f5;
  border: 2rpx solid #e8e8e8;
  border-radius: 8rpx;
  font-size: 24rpx;
  color: #333333;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 16rpx;
  margin-bottom: 32rpx;
  
  .test-btn {
    flex: 2;
    height: 88rpx;
    background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
    color: #ffffff;
    border: none;
    border-radius: 44rpx;
    font-size: 28rpx;
    font-weight: bold;
    
    &:disabled {
      opacity: 0.6;
    }
  }
  
  .clear-btn, .save-btn {
    flex: 1;
    height: 88rpx;
    background: rgba(255, 255, 255, 0.9);
    color: #333333;
    border: 2rpx solid #e8e8e8;
    border-radius: 44rpx;
    font-size: 24rpx;
    font-weight: bold;
  }
}

.response-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 32rpx 24rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
    
    .section-title {
      font-size: 32rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .response-status {
      padding: 8rpx 16rpx;
      border-radius: 16rpx;
      
      &.success {
        background: #f6ffed;
        
        .status-text {
          color: #52c41a;
        }
      }
      
      &.error {
        background: #fff2f0;
        
        .status-text {
          color: #ff4d4f;
        }
      }
      
      .status-text {
        font-size: 22rpx;
        font-weight: bold;
      }
    }
  }
  
  .response-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 24rpx;
    
    .info-item {
      text-align: center;
      
      .info-label {
        display: block;
        font-size: 22rpx;
        color: #999999;
        margin-bottom: 8rpx;
      }
      
      .info-value {
        display: block;
        font-size: 26rpx;
        font-weight: bold;
        color: #333333;
      }
    }
  }
  
  .sub-title {
    display: block;
    font-size: 26rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 12rpx;
  }
  
  .response-headers {
    margin-bottom: 24rpx;
    
    .headers-content {
      background: #f5f5f5;
      border-radius: 8rpx;
      padding: 16rpx;
      
      .headers-text {
        font-size: 22rpx;
        color: #666666;
        line-height: 1.5;
        white-space: pre-line;
      }
    }
  }
  
  .response-body {
    .body-content {
      background: #f5f5f5;
      border-radius: 8rpx;
      padding: 16rpx;
      max-height: 600rpx;
      overflow-y: auto;
      
      .body-text {
        font-size: 22rpx;
        color: #333333;
        line-height: 1.5;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
  }
}

.history-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 32rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
    
    .section-title {
      font-size: 32rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .clear-history-btn {
      padding: 8rpx 16rpx;
      background: #ff4d4f;
      color: #ffffff;
      border: none;
      border-radius: 8rpx;
      font-size: 22rpx;
    }
  }
  
  .history-list {
    .history-item {
      display: flex;
      align-items: center;
      padding: 16rpx 0;
      border-bottom: 1rpx solid #f0f0f0;
      transition: all 0.3s ease;
      
      &:last-child {
        border-bottom: none;
      }
      
      &:active {
        background: #f5f5f5;
      }
      
      .history-method {
        width: 120rpx;
        padding: 8rpx 12rpx;
        border-radius: 8rpx;
        text-align: center;
        margin-right: 16rpx;
        
        &.get {
          background: #e6f7ff;
          
          .method-text {
            color: #1890ff;
          }
        }
        
        &.post {
          background: #f6ffed;
          
          .method-text {
            color: #52c41a;
          }
        }
        
        &.put {
          background: #fff7e6;
          
          .method-text {
            color: #fa8c16;
          }
        }
        
        &.delete {
          background: #fff2f0;
          
          .method-text {
            color: #ff4d4f;
          }
        }
        
        .method-text {
          font-size: 20rpx;
          font-weight: bold;
        }
      }
      
      .history-info {
        flex: 1;
        
        .history-url {
          display: block;
          font-size: 24rpx;
          color: #333333;
          margin-bottom: 4rpx;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .history-time {
          display: block;
          font-size: 20rpx;
          color: #999999;
        }
      }
      
      .history-status {
        width: 80rpx;
        text-align: center;
        
        &.success {
          .status-code {
            color: #52c41a;
          }
        }
        
        &.error {
          .status-code {
            color: #ff4d4f;
          }
        }
        
        .status-code {
          font-size: 22rpx;
          font-weight: bold;
        }
      }
    }
  }
}
</style>