<template>
  <div class="permission-denied" :class="{ 'full-page': fullPage }">
    <div class="permission-denied-content">
      <!-- 图标区域 -->
      <div class="icon-container">
        <div class="icon-wrapper" :class="iconType">
          <svg v-if="iconType === 'lock'" viewBox="0 0 24 24" width="48" height="48">
            <path fill="currentColor" d="M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
          </svg>
          <svg v-else-if="iconType === 'shield'" viewBox="0 0 24 24" width="48" height="48">
            <path fill="currentColor" d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16V13C8,12.4 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="48" height="48">
            <path fill="currentColor" d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
          </svg>
        </div>
      </div>

      <!-- 主要内容 -->
      <div class="main-content">
        <h3 class="title">{{ title }}</h3>
        <p class="description">{{ description }}</p>
        
        <!-- 权限详情 -->
        <div v-if="showDetails" class="permission-details">
          <div class="detail-item">
            <span class="detail-label">所需权限:</span>
            <span class="detail-value">{{ requiredPermission }}</span>
          </div>
          <div v-if="currentRole" class="detail-item">
            <span class="detail-label">当前角色:</span>
            <span class="detail-value">{{ currentRole }}</span>
          </div>
          <div v-if="errorCode" class="detail-item">
            <span class="detail-label">错误代码:</span>
            <span class="detail-value">{{ errorCode }}</span>
          </div>
        </div>

        <!-- 建议操作 -->
        <div class="suggestions">
          <h4 class="suggestions-title">您可以尝试:</h4>
          <ul class="suggestions-list">
            <li v-for="suggestion in suggestions" :key="suggestion.id" class="suggestion-item">
              <span class="suggestion-text">{{ suggestion.text }}</span>
              <button 
                v-if="suggestion.action" 
                @click="suggestion.action" 
                class="suggestion-button"
                :class="suggestion.buttonClass"
              >
                {{ suggestion.buttonText }}
              </button>
            </li>
          </ul>
        </div>

        <!-- 操作按钮 -->
        <div class="actions">
          <button 
            v-if="showRetry" 
            @click="handleRetry" 
            class="action-button primary"
            :disabled="retrying"
          >
            <svg v-if="retrying" class="loading-icon" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
            </svg>
            {{ retrying ? '重试中...' : '重新验证' }}
          </button>
          
          <button 
            v-if="showContact" 
            @click="handleContact" 
            class="action-button secondary"
          >
            联系管理员
          </button>
          
          <button 
            v-if="showGoBack" 
            @click="handleGoBack" 
            class="action-button outline"
          >
            返回上一页
          </button>
        </div>
      </div>
    </div>

    <!-- 底部信息 -->
    <div v-if="showFooter" class="footer">
      <p class="footer-text">
        如果您认为这是一个错误，请联系系统管理员或查看
        <a href="#" @click.prevent="showHelp" class="help-link">帮助文档</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
// @ts-ignore
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

interface Suggestion {
  id: string
  text: string
  action?: () => void
  buttonText?: string
  buttonClass?: string
}

interface Props {
  title?: string
  description?: string
  requiredPermission?: string
  currentRole?: string
  errorCode?: string
  iconType?: 'lock' | 'shield' | 'warning'
  showDetails?: boolean
  showRetry?: boolean
  showContact?: boolean
  showGoBack?: boolean
  showFooter?: boolean
  fullPage?: boolean
  customSuggestions?: Suggestion[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '访问被拒绝',
  description: '抱歉，您没有足够的权限访问此功能。请联系管理员获取相应权限。',
  iconType: 'lock',
  showDetails: true,
  showRetry: true,
  showContact: true,
  showGoBack: true,
  showFooter: true,
  fullPage: false
})

const emit = defineEmits<{
  retry: []
  contact: []
  goBack: []
  help: []
}>()

const router = useRouter()
const retrying = ref(false)

// 默认建议列表
const defaultSuggestions = computed<Suggestion[]>(() => [
  {
    id: 'refresh',
    text: '刷新页面重新加载权限信息',
    action: () => window.location.reload(),
    buttonText: '刷新页面',
    buttonClass: 'outline'
  },
  {
    id: 'login',
    text: '重新登录以获取最新权限',
    action: () => {
      router.push('/login')
    },
    buttonText: '重新登录',
    buttonClass: 'outline'
  },
  {
    id: 'profile',
    text: '查看个人资料和权限设置',
    action: () => {
      router.push('/profile')
    },
    buttonText: '个人资料',
    buttonClass: 'outline'
  }
])

// 合并自定义建议和默认建议
const suggestions = computed(() => {
  if (props.customSuggestions && props.customSuggestions.length > 0) {
    return props.customSuggestions
  }
  return defaultSuggestions.value
})

// 重试权限验证
const handleRetry = async () => {
  retrying.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟验证过程
    emit('retry')
    ElMessage.success('权限验证已重新发起')
  } catch (error) {
    ElMessage.error('重试失败，请稍后再试')
  } finally {
    retrying.value = false
  }
}

// 联系管理员
const handleContact = () => {
  emit('contact')
  // 可以打开邮件客户端或显示联系方式
  ElMessage.info('正在为您跳转到联系页面...')
}

// 返回上一页
const handleGoBack = () => {
  emit('goBack')
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

// 显示帮助
const showHelp = () => {
  emit('help')
  ElMessage.info('正在为您打开帮助文档...')
}
</script>

<style scoped>
.permission-denied {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 400px;
  text-align: center;
}

.permission-denied.full-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.permission-denied-content {
  max-width: 500px;
  width: 100%;
  background: white;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.icon-container {
  margin-bottom: 1.5rem;
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 1rem;
}

.icon-wrapper.lock {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.icon-wrapper.shield {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.icon-wrapper.warning {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #d69e2e;
}

.main-content {
  margin-bottom: 2rem;
}

.title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.description {
  font-size: 1rem;
  color: #718096;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.permission-details {
  background: #f7fafc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  text-align: left;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.875rem;
}

.detail-value {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #edf2f7;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #2d3748;
}

.suggestions {
  text-align: left;
  margin-bottom: 1.5rem;
}

.suggestions-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: #f7fafc;
  border-radius: 6px;
  border-left: 3px solid #4299e1;
}

.suggestion-text {
  flex: 1;
  font-size: 0.875rem;
  color: #4a5568;
}

.suggestion-button {
  margin-left: 1rem;
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.suggestion-button.outline {
  background: transparent;
  color: #4299e1;
  border-color: #4299e1;
}

.suggestion-button.outline:hover {
  background: #4299e1;
  color: white;
}

.actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

.action-button {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-button.primary {
  background: #4299e1;
  color: white;
}

.action-button.primary:hover:not(:disabled) {
  background: #3182ce;
}

.action-button.secondary {
  background: #48bb78;
  color: white;
}

.action-button.secondary:hover {
  background: #38a169;
}

.action-button.outline {
  background: transparent;
  color: #718096;
  border-color: #e2e8f0;
}

.action-button.outline:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.footer {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.footer-text {
  font-size: 0.875rem;
  color: #718096;
  margin: 0;
}

.help-link {
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
}

.help-link:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .permission-denied {
    padding: 1rem;
  }
  
  .permission-denied-content {
    padding: 1.5rem;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
    justify-content: center;
  }
  
  .suggestion-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .suggestion-button {
    margin-left: 0;
    align-self: flex-end;
  }
}
</style>