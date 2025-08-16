<template>
  <div class="error-boundary">
    <div v-if="hasError" class="error-fallback">
      <div class="error-icon">
        <span class="error-icon">⚠️</span>
      </div>
      <h3 class="error-title">组件加载失败</h3>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <button 
          @click="retry" 
          class="retry-button"
          :disabled="retrying"
        >
          <span class="retry-icon">🔄</span>
          {{ retrying ? '重试中...' : '重试' }}
        </button>
        <button 
          @click="reset" 
          class="reset-button"
        >
          重置
        </button>
      </div>
      <details v-if="showDetails" class="error-details">
        <summary>错误详情</summary>
        <pre class="error-stack">{{ errorStack }}</pre>
      </details>
    </div>
    <slot v-else></slot>
  </div>
</template>

<script setup>
import { ref, onErrorCaptured, nextTick } from 'vue'
// 使用文本图标替代lucide图标

const props = defineProps({
  fallbackComponent: {
    type: Object,
    default: null
  },
  showDetails: {
    type: Boolean,
    default: false
  },
  maxRetries: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits(['error', 'retry', 'reset'])

const hasError = ref(false)
const errorMessage = ref('')
const errorStack = ref('')
const retrying = ref(false)
const retryCount = ref(0)

// 捕获子组件错误
onErrorCaptured((error, instance, info) => {
  try {
    console.error('ErrorBoundary 捕获到错误:', error)
    console.error('错误信息:', info)
    console.error('组件实例:', instance)
    
    hasError.value = true
    errorMessage.value = error.message || '未知错误'
    errorStack.value = error.stack || '无堆栈信息'
    
    emit('error', { error, instance, info })
    
    // 阻止错误继续向上传播
    return false
  } catch (handlerError) {
    console.error('ErrorBoundary 处理错误时出现异常:', handlerError)
    return false
  }
})

// 重试逻辑
const retry = async () => {
  if (retryCount.value >= props.maxRetries) {
    console.warn(`已达到最大重试次数 (${props.maxRetries})`)
    return
  }
  
  try {
    retrying.value = true
    retryCount.value++
    
    emit('retry', retryCount.value)
    
    // 等待一段时间后重试
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    hasError.value = false
    errorMessage.value = ''
    errorStack.value = ''
    
    await nextTick()
  } catch (error) {
    console.error('重试失败:', error)
  } finally {
    retrying.value = false
  }
}

// 重置状态
const reset = () => {
  try {
    hasError.value = false
    errorMessage.value = ''
    errorStack.value = ''
    retryCount.value = 0
    retrying.value = false
    
    emit('reset')
  } catch (error) {
    console.error('重置状态失败:', error)
  }
}

// 暴露方法给父组件
defineExpose({
  retry,
  reset,
  hasError: () => hasError.value,
  retryCount: () => retryCount.value
})
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  background: rgba(254, 242, 242, 0.8);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 0.5rem;
  backdrop-filter: blur(10px);
  min-height: 200px;
}

.error-icon {
  margin-bottom: 1rem;
  font-size: 2.25rem;
}

.error-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-message {
  color: #7f1d1d;
  margin-bottom: 1.5rem;
  max-width: 400px;
}

.error-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.retry-button,
.reset-button {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
}

.retry-icon {
  margin-right: 0.5rem;
  font-size: 1rem;
  transition: transform 0.3s ease;
}

.retry-button:disabled .retry-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.retry-button {
  background: #dc2626;
  color: white;
}

.retry-button:hover:not(:disabled) {
  background: #b91c1c;
}

.retry-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reset-button {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.reset-button:hover {
  background: #e5e7eb;
}

.error-details {
  width: 100%;
  max-width: 600px;
  text-align: left;
}

.error-details summary {
  cursor: pointer;
  font-weight: 500;
  color: #7f1d1d;
  margin-bottom: 0.5rem;
}

.error-stack {
  background: #1f2937;
  color: #f9fafb;
  padding: 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .error-fallback {
    background: rgba(17, 24, 39, 0.9);
    border-color: rgba(239, 68, 68, 0.3);
  }
  
  .error-title {
    color: #f87171;
  }
  
  .error-message {
    color: #fca5a5;
  }
  
  .reset-button {
    background: #374151;
    color: #f9fafb;
    border-color: #4b5563;
  }
  
  .reset-button:hover {
    background: #4b5563;
  }
}
</style>