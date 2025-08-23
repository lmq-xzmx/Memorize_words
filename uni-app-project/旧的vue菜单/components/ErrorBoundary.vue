<template>
  <div class="error-boundary">
    <!-- 正常渲染子组件 -->
    <slot v-if="!hasError" />
    
    <!-- 错误状态显示 -->
    <div v-else class="error-boundary-content">
      <!-- 简单错误显示 -->
      <div v-if="!showDetails" class="error-simple">
        <div class="error-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        
        <h3 class="error-title">{{ errorTitle }}</h3>
        <p class="error-message">{{ errorMessage }}</p>
        
        <div class="error-actions">
          <button class="error-btn error-btn-primary" @click="handleRetry">
            重试
          </button>
          <button class="error-btn error-btn-secondary" @click="showDetails = true">
            查看详情
          </button>
          <button v-if="showReportButton" class="error-btn error-btn-secondary" @click="reportError">
            报告错误
          </button>
        </div>
      </div>
      
      <!-- 详细错误显示 -->
      <div v-else class="error-detailed">
        <div class="error-header">
          <h3 class="error-title">错误详情</h3>
          <button class="error-close" @click="showDetails = false">
            ✕
          </button>
        </div>
        
        <div class="error-details">
          <div class="error-section">
            <h4>错误信息</h4>
            <div class="error-info">
              <div class="info-item">
                <label>类型:</label>
                <span>{{ errorInfo.type }}</span>
              </div>
              <div class="info-item">
                <label>消息:</label>
                <span>{{ errorInfo.message }}</span>
              </div>
              <div class="info-item">
                <label>时间:</label>
                <span>{{ formatTime(errorInfo.timestamp) }}</span>
              </div>
              <div class="info-item">
                <label>组件:</label>
                <span>{{ errorInfo.componentName }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="errorInfo.stack" class="error-section">
            <h4>错误堆栈</h4>
            <pre class="error-stack">{{ errorInfo.stack }}</pre>
          </div>
          
          <div v-if="errorInfo.componentStack" class="error-section">
            <h4>组件堆栈</h4>
            <pre class="error-stack">{{ errorInfo.componentStack }}</pre>
          </div>
          
          <div class="error-section">
            <h4>环境信息</h4>
            <div class="error-info">
              <div class="info-item">
                <label>浏览器:</label>
                <span>{{ environmentInfo.userAgent }}</span>
              </div>
              <div class="info-item">
                <label>URL:</label>
                <span>{{ environmentInfo.url }}</span>
              </div>
              <div class="info-item">
                <label>视口:</label>
                <span>{{ environmentInfo.viewport }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="errorInfo.props" class="error-section">
            <h4>组件属性</h4>
            <pre class="error-stack">{{ JSON.stringify(errorInfo.props, null, 2) }}</pre>
          </div>
        </div>
        
        <div class="error-actions">
          <button class="error-btn error-btn-primary" @click="handleRetry">
            重试
          </button>
          <button class="error-btn error-btn-secondary" @click="copyErrorInfo">
            复制错误信息
          </button>
          <button v-if="showReportButton" class="error-btn error-btn-secondary" @click="reportError">
            报告错误
          </button>
          <button class="error-btn error-btn-secondary" @click="showDetails = false">
            收起详情
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onErrorCaptured, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'ErrorBoundary',
  
  props: {
    // 自定义错误标题
    title: {
      type: String,
      default: '页面出现错误'
    },
    
    // 自定义错误消息
    message: {
      type: String,
      default: '抱歉，页面遇到了一些问题。请尝试刷新页面或联系技术支持。'
    },
    
    // 是否显示报告按钮
    showReportButton: {
      type: Boolean,
      default: true
    },
    
    // 是否自动重试
    autoRetry: {
      type: Boolean,
      default: false
    },
    
    // 自动重试次数
    maxRetries: {
      type: Number,
      default: 3
    },
    
    // 重试延迟（毫秒）
    retryDelay: {
      type: Number,
      default: 1000
    },
    
    // 错误回调
    onError: {
      type: Function,
      default: null
    },
    
    // 重试回调
    onRetry: {
      type: Function,
      default: null
    }
  },
  
  emits: ['error', 'retry'],
  
  setup(props, { emit }) {
    const router = useRouter()
    const route = useRoute()
    
    // 响应式状态
    const hasError = ref(false)
    const showDetails = ref(false)
    const retryCount = ref(0)
    const errorInfo = ref({})
    const environmentInfo = ref({})
    
    // 计算属性
    const errorTitle = computed(() => {
      return errorInfo.value.title || props.title
    })
    
    const errorMessage = computed(() => {
      return errorInfo.value.message || props.message
    })
    
    // 错误捕获
    onErrorCaptured((error, instance, info) => {
      console.error('ErrorBoundary caught an error:', error)
      
      // 收集错误信息
      const errorData = {
        type: error.name || 'Error',
        message: error.message || '未知错误',
        stack: error.stack,
        componentStack: info,
        componentName: instance?.$options.name || instance?.$options.__name || 'Unknown',
        timestamp: Date.now(),
        props: instance?.$props,
        route: {
          path: route.path,
          name: route.name,
          params: route.params,
          query: route.query
        }
      }
      
      errorInfo.value = errorData
      hasError.value = true
      
      // 收集环境信息
      collectEnvironmentInfo()
      
      // 触发错误事件
      emit('error', errorData)
      
      // 调用错误回调
      if (props.onError) {
        props.onError(errorData)
      }
      
      // 自动重试
      if (props.autoRetry && retryCount.value < props.maxRetries) {
        setTimeout(() => {
          handleRetry()
        }, props.retryDelay)
      }
      
      // 阻止错误继续传播
      return false
    })
    
    // 收集环境信息
    const collectEnvironmentInfo = () => {
      environmentInfo.value = {
        userAgent: navigator.userAgent,
        url: window.location.href,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
        timestamp: new Date().toISOString(),
        language: navigator.language,
        platform: navigator.platform,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine
      }
    }
    
    // 格式化时间
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }
    
    // 处理重试
    const handleRetry = () => {
      retryCount.value++
      hasError.value = false
      showDetails.value = false
      errorInfo.value = {}
      
      // 触发重试事件
      emit('retry', retryCount.value)
      
      // 调用重试回调
      if (props.onRetry) {
        props.onRetry(retryCount.value)
      }
      
      // 强制重新渲染
      setTimeout(() => {
        // 可以在这里添加额外的重试逻辑
      }, 100)
    }
    
    // 复制错误信息
    const copyErrorInfo = async () => {
      const errorText = `
错误报告
========

错误信息:
类型: ${errorInfo.value.type}
消息: ${errorInfo.value.message}
时间: ${formatTime(errorInfo.value.timestamp)}
组件: ${errorInfo.value.componentName}

环境信息:
浏览器: ${environmentInfo.value.userAgent}
URL: ${environmentInfo.value.url}
视口: ${environmentInfo.value.viewport}

错误堆栈:
${errorInfo.value.stack || '无'}

组件堆栈:
${errorInfo.value.componentStack || '无'}
      `.trim()
      
      try {
        await navigator.clipboard.writeText(errorText)
        // 可以添加成功提示
        console.log('错误信息已复制到剪贴板')
      } catch (err) {
        console.error('复制失败:', err)
        // 降级方案：创建临时文本区域
        const textArea = document.createElement('textarea')
        textArea.value = errorText
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
      }
    }
    
    // 报告错误
    const reportError = async () => {
      try {
        const reportData = {
          error: errorInfo.value,
          environment: environmentInfo.value,
          userAgent: navigator.userAgent,
          timestamp: Date.now()
        }
        
        // 发送错误报告到服务器
        const response = await fetch('/api/error-report', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(reportData)
        })
        
        if (response.ok) {
          console.log('错误报告已发送')
          // 可以添加成功提示
        } else {
          console.error('错误报告发送失败')
        }
      } catch (err) {
        console.error('发送错误报告时出错:', err)
      }
    }
    
    // 全局错误处理
    const setupGlobalErrorHandling = () => {
      // 捕获未处理的 Promise 拒绝
      window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason)
        
        const errorData = {
          type: 'UnhandledPromiseRejection',
          message: event.reason?.message || String(event.reason),
          stack: event.reason?.stack,
          timestamp: Date.now()
        }
        
        errorInfo.value = errorData
        hasError.value = true
        collectEnvironmentInfo()
        
        emit('error', errorData)
        
        if (props.onError) {
          props.onError(errorData)
        }
      })
      
      // 捕获全局 JavaScript 错误
      window.addEventListener('error', (event) => {
        console.error('Global error:', event.error)
        
        const errorData = {
          type: 'GlobalError',
          message: event.message,
          stack: event.error?.stack,
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          timestamp: Date.now()
        }
        
        errorInfo.value = errorData
        hasError.value = true
        collectEnvironmentInfo()
        
        emit('error', errorData)
        
        if (props.onError) {
          props.onError(errorData)
        }
      })
    }
    
    // 重置错误状态
    const resetError = () => {
      hasError.value = false
      showDetails.value = false
      errorInfo.value = {}
      retryCount.value = 0
    }
    
    // 生命周期
    onMounted(() => {
      setupGlobalErrorHandling()
      collectEnvironmentInfo()
    })
    
    // 暴露方法给父组件
    const expose = {
      resetError,
      hasError: () => hasError.value,
      getErrorInfo: () => errorInfo.value
    }
    
    return {
      // 响应式状态
      hasError,
      showDetails,
      errorInfo,
      environmentInfo,
      
      // 计算属性
      errorTitle,
      errorMessage,
      
      // 方法
      formatTime,
      handleRetry,
      copyErrorInfo,
      reportError,
      resetError,
      
      // 暴露给父组件
      ...expose
    }
  }
}
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-boundary-content {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: var(--space-6);
  background: var(--color-bg);
}

/* 简单错误显示 */
.error-simple {
  text-align: center;
  max-width: 500px;
}

.error-icon {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-4);
  color: var(--color-error);
}

.error-title {
  margin: 0 0 var(--space-3) 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.error-message {
  margin: 0 0 var(--space-6) 0;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.error-btn {
  padding: var(--space-2) var(--space-4);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.error-btn-primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.error-btn-primary:hover {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.error-btn-secondary {
  background: transparent;
  color: var(--color-text);
  border-color: var(--color-border);
}

.error-btn-secondary:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-border-hover);
}

/* 详细错误显示 */
.error-detailed {
  width: 100%;
  max-width: 800px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.error-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.error-header .error-title {
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--color-text);
}

.error-close {
  padding: var(--space-1);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.error-close:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text);
}

.error-details {
  padding: var(--space-4);
  max-height: 60vh;
  overflow-y: auto;
}

.error-section {
  margin-bottom: var(--space-6);
}

.error-section:last-child {
  margin-bottom: 0;
}

.error-section h4 {
  margin: 0 0 var(--space-3) 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--space-2);
}

.error-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

.info-item label {
  min-width: 80px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.info-item span {
  flex: 1;
  color: var(--color-text);
  word-break: break-all;
}

.error-stack {
  margin: 0;
  padding: var(--space-3);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  color: var(--color-text);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow: auto;
}

.error-detailed .error-actions {
  padding: var(--space-4);
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .error-boundary-content {
    padding: var(--space-4);
    min-height: 300px;
  }
  
  .error-simple {
    max-width: 100%;
  }
  
  .error-detailed {
    max-width: 100%;
    margin: 0;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .error-btn {
    width: 100%;
  }
  
  .info-item {
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .info-item label {
    min-width: auto;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .error-boundary-content {
    background: var(--color-bg-dark, #1a1a1a);
  }
  
  .error-detailed {
    background: var(--color-bg-dark, #1a1a1a);
    border-color: var(--color-border-dark, #333);
  }
  
  .error-header {
    background: var(--color-bg-secondary-dark, #2a2a2a);
    border-color: var(--color-border-dark, #333);
  }
  
  .error-stack {
    background: var(--color-bg-secondary-dark, #2a2a2a);
    border-color: var(--color-border-dark, #333);
  }
}

/* 打印样式 */
@media print {
  .error-boundary-content {
    background: white;
    color: black;
  }
  
  .error-actions {
    display: none;
  }
}
</style>