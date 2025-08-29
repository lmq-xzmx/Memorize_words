<template>
  <view class="api-test-page">
    <view class="header">
      <text class="title">🔧 API测试</text>
      <text class="subtitle">开发工具 - API接口测试</text>
    </view>
    
    <view class="content">
      <view class="test-section">
        <text class="section-title">接口测试</text>
        
        <view class="input-group">
          <text class="label">请求URL:</text>
          <input 
            class="input" 
            v-model="apiUrl" 
            placeholder="输入API接口地址"
          />
        </view>
        
        <view class="input-group">
          <text class="label">请求方法:</text>
          <picker 
            class="picker" 
            :value="methodIndex" 
            :range="methods" 
            @change="onMethodChange"
          >
            <view class="picker-text">{{ methods[methodIndex] }}</view>
          </picker>
        </view>
        
        <view class="input-group">
          <text class="label">请求参数:</text>
          <textarea 
            class="textarea" 
            v-model="requestData" 
            placeholder="输入JSON格式的请求参数"
          />
        </view>
        
        <button class="test-btn" @tap="sendRequest" :disabled="loading">
          {{ loading ? '请求中...' : '发送请求' }}
        </button>
      </view>
      
      <view class="result-section" v-if="response">
        <text class="section-title">响应结果</text>
        <view class="response-box">
          <text class="response-text">{{ response }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'ApiTest',
  data() {
    return {
      apiUrl: 'https://jsonplaceholder.typicode.com/posts/1',
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      methodIndex: 0,
      requestData: '',
      response: '',
      loading: false
    }
  },
  methods: {
    onMethodChange(e) {
      this.methodIndex = e.detail.value
    },
    
    async sendRequest() {
      if (!this.apiUrl.trim()) {
        uni.showToast({
          title: '请输入API地址',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      this.response = ''
      
      try {
        const method = this.methods[this.methodIndex]
        let requestOptions = {
          url: this.apiUrl,
          method: method,
          timeout: 10000
        }
        
        // 如果有请求数据且不是GET请求
        if (this.requestData.trim() && method !== 'GET') {
          try {
            requestOptions.data = JSON.parse(this.requestData)
          } catch (e) {
            uni.showToast({
              title: '请求参数格式错误',
              icon: 'none'
            })
            this.loading = false
            return
          }
        }
        
        const result = await this.makeRequest(requestOptions)
        this.response = JSON.stringify(result, null, 2)
        
        uni.showToast({
          title: '请求成功',
          icon: 'success'
        })
        
      } catch (error) {
        this.response = `请求失败: ${error.message || error}`
        uni.showToast({
          title: '请求失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    makeRequest(options) {
      return new Promise((resolve, reject) => {
        uni.request({
          ...options,
          success: (res) => {
            resolve({
              statusCode: res.statusCode,
              data: res.data,
              header: res.header
            })
          },
          fail: (err) => {
            reject(err)
          }
        })
      })
    }
  }
}
</script>

<style scoped>
.api-test-page {
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

.test-section,
.result-section {
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
  margin-bottom: 30rpx;
}

.input-group {
  margin-bottom: 30rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 15rpx;
}

.input,
.textarea {
  width: 100%;
  padding: 20rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 10rpx;
  font-size: 26rpx;
  box-sizing: border-box;
}

.textarea {
  height: 200rpx;
  resize: none;
}

.picker {
  width: 100%;
  padding: 20rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 10rpx;
  background: white;
}

.picker-text {
  font-size: 26rpx;
  color: #333;
}

.test-btn {
  width: 100%;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 40rpx;
  font-size: 30rpx;
  font-weight: bold;
}

.test-btn:disabled {
  opacity: 0.6;
}

.test-btn:active:not(:disabled) {
  opacity: 0.8;
}

.response-box {
  background: #f8f8f8;
  border-radius: 10rpx;
  padding: 20rpx;
  max-height: 600rpx;
  overflow-y: auto;
}

.response-text {
  font-size: 24rpx;
  color: #333;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>