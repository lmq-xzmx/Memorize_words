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

<style lang="scss" scoped>
@use '../../assets/scss/index.scss';

.error-boundary {
  width: 100%;
  height: 100%;
  
  // BEM 元素 - 错误回退界面
  @include bem-element('fallback') {
    @include flex-center;
    flex-direction: column;
    padding: var(--spacing-8);
    text-align: center;
    background: rgba(var(--color-red-50), 0.9);
  border: 1px solid rgba(var(--color-red-200), 0.5);
  border-radius: var(--border-radius-lg);
    backdrop-filter: blur(10px);
    min-height: 200px;
  }
  
  // BEM 元素 - 错误图标
  @include bem-element('icon') {
    margin-bottom: var(--spacing-4);
    font-size: var(--font-size-4xl);
    font-weight: var(--font-weight-normal);
  }
  
  // BEM 元素 - 错误标题
  @include bem-element('title') {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--color-red-600);
  margin-bottom: var(--spacing-2);
  }
  
  // BEM 元素 - 错误消息
  @include bem-element('message') {
    color: var(--color-red-800);
  margin-bottom: var(--spacing-6);
    max-width: 400px;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-normal);
  }

  // BEM 元素 - 错误操作
  @include bem-element('actions') {
    @include flex-center;
    gap: var(--spacing-3);
  margin-bottom: var(--spacing-4);
  }
}

// 重试按钮
.retry-button {
  @include flex-center;
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  background: var(--color-red-600);
    color: var(--color-white);
  
  &:hover:not(:disabled) {
    background: var(--color-red-700);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

// 重置按钮
.reset-button {
  @include flex-center;
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all 0.2s ease;
  cursor: pointer;
  background: var(--color-gray-100);
    color: var(--color-gray-700);
    border: 1px solid var(--color-gray-300);
  
  &:hover {
    background: var(--color-gray-200);
  }
}

// 重试图标
.retry-icon {
  margin-right: var(--spacing-2);
  @include text-style('base', 'normal');
  @include transition('transform');
}

// 重试中的旋转动画
.retry-button:disabled .retry-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 错误详情
.error-details {
  width: 100%;
  max-width: 600px;
  text-align: left;
  
  summary {
    cursor: pointer;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-red-800);
  margin-bottom: var(--spacing-2);
  }
}

// 错误堆栈
.error-stack {
  background: var(--color-gray-900);
  color: var(--color-gray-50);
  padding: var(--spacing-4);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

// 深色模式支持
@media (prefers-color-scheme: dark) {
  .error-boundary {
    @include bem-element('fallback') {
      background: rgba(var(--color-gray-900), 0.9);
    border-color: rgba(var(--color-red-500), 0.3);
    }
    
    @include bem-element('title') {
      color: var(--color-red-400);
    }
    
    @include bem-element('message') {
      color: var(--color-red-300);
    }
  }
  
  .reset-button {
    background: var(--color-gray-700);
      color: var(--color-gray-100);
      border-color: var(--color-gray-600);
    
    &:hover {
      background: var(--color-gray-600);
    }
  }
}
</style>