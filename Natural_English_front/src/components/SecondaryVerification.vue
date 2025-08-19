<template>
  <div class="secondary-verification">
    <!-- 遮罩层 -->
    <div v-if="visible" class="verification-overlay" @click="handleOverlayClick">
      <div class="verification-modal" @click.stop>
        <!-- 头部 -->
        <div class="modal-header">
          <div class="header-icon">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="#f56565" d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16V13C8,12.4 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
            </svg>
          </div>
          <h3 class="modal-title">{{ title }}</h3>
          <button class="close-button" @click="handleCancel">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
            </svg>
          </button>
        </div>

        <!-- 内容区域 -->
        <div class="modal-body">
          <div class="warning-message">
            <p class="warning-text">{{ description }}</p>
            <div v-if="operationDetails" class="operation-details">
              <h4>操作详情:</h4>
              <ul>
                <li v-for="detail in operationDetails" :key="detail.key">
                  <span class="detail-label">{{ detail.label }}:</span>
                  <span class="detail-value">{{ detail.value }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- 验证方式选择 -->
          <div class="verification-methods">
            <h4>请选择验证方式:</h4>
            <div class="method-options">
              <label 
                v-for="method in availableMethods" 
                :key="method.type"
                class="method-option"
                :class="{ active: selectedMethod === method.type }"
              >
                <input 
                  type="radio" 
                  :value="method.type" 
                  v-model="selectedMethod"
                  @change="handleMethodChange"
                >
                <div class="method-icon">
                  <svg v-if="method.type === 'password'" viewBox="0 0 24 24" width="20" height="20">
                    <path fill="currentColor" d="M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
                  </svg>
                  <svg v-else-if="method.type === 'sms'" viewBox="0 0 24 24" width="20" height="20">
                    <path fill="currentColor" d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2M6,9V7H18V9H6M14,11V13H6V11H14M16,15H6V17H16V15Z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" width="20" height="20">
                    <path fill="currentColor" d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M10,17L6,13L7.41,11.59L10,14.17L16.59,7.58L18,9L10,17Z"/>
                  </svg>
                </div>
                <div class="method-info">
                  <span class="method-name">{{ method.name }}</span>
                  <span class="method-desc">{{ method.description }}</span>
                </div>
              </label>
            </div>
          </div>

          <!-- 验证输入区域 -->
          <div v-if="selectedMethod" class="verification-input">
            <!-- 密码验证 -->
            <div v-if="selectedMethod === 'password'" class="password-verification">
              <label class="input-label">请输入当前密码:</label>
              <div class="password-input-wrapper">
                <input 
                  ref="passwordInput"
                  v-model="verificationData.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="verification-input-field"
                  placeholder="请输入密码"
                  @keyup.enter="handleVerify"
                  :disabled="verifying"
                >
                <button 
                  type="button" 
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="showPassword" viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.09L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.76,7.13 11.37,7 12,7Z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- 短信验证 -->
            <div v-else-if="selectedMethod === 'sms'" class="sms-verification">
              <label class="input-label">验证码已发送至 {{ maskedPhone }}</label>
              <div class="sms-input-wrapper">
                <input 
                  ref="smsInput"
                  v-model="verificationData.smsCode"
                  type="text"
                  class="verification-input-field"
                  placeholder="请输入6位验证码"
                  maxlength="6"
                  @keyup.enter="handleVerify"
                  :disabled="verifying"
                >
                <button 
                  type="button" 
                  class="resend-button"
                  @click="handleResendSms"
                  :disabled="smsCountdown > 0 || sendingSms"
                >
                  {{ smsCountdown > 0 ? `${smsCountdown}s后重发` : '重新发送' }}
                </button>
              </div>
            </div>

            <!-- TOTP验证 -->
            <div v-else-if="selectedMethod === 'totp'" class="totp-verification">
              <label class="input-label">请输入身份验证器中的6位数字:</label>
              <input 
                ref="totpInput"
                v-model="verificationData.totpCode"
                type="text"
                class="verification-input-field"
                placeholder="请输入6位验证码"
                maxlength="6"
                @keyup.enter="handleVerify"
                :disabled="verifying"
              >
            </div>
          </div>

          <!-- 错误信息 -->
          <div v-if="errorMessage" class="error-message">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="#f56565" d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
            </svg>
            <span>{{ errorMessage }}</span>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="modal-footer">
          <button class="cancel-button" @click="handleCancel" :disabled="verifying">
            取消
          </button>
          <button 
            class="verify-button" 
            @click="handleVerify" 
            :disabled="!canVerify || verifying"
          >
            <svg v-if="verifying" class="loading-icon" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
            </svg>
            {{ verifying ? '验证中...' : '确认操作' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
// @ts-ignore
import { onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

interface OperationDetail {
  key: string
  label: string
  value: string
}

interface VerificationMethod {
  type: 'password' | 'sms' | 'totp'
  name: string
  description: string
  enabled: boolean
}

interface Props {
  visible?: boolean
  title?: string
  description?: string
  operationDetails?: OperationDetail[]
  availableMethods?: VerificationMethod[]
  defaultMethod?: string
  userPhone?: string
  allowOverlayClose?: boolean
  autoFocus?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '安全验证',
  description: '此操作需要二次验证，请选择验证方式完成身份确认。',
  availableMethods: () => [
    {
      type: 'password',
      name: '密码验证',
      description: '使用当前登录密码验证',
      enabled: true
    },
    {
      type: 'sms',
      name: '短信验证',
      description: '发送验证码到手机',
      enabled: true
    },
    {
      type: 'totp',
      name: '身份验证器',
      description: '使用TOTP身份验证器',
      enabled: false
    }
  ],
  defaultMethod: 'password',
  userPhone: '',
  allowOverlayClose: false,
  autoFocus: true
})

const emit = defineEmits<{
  verify: [data: { method: string; value: string }]
  cancel: []
  close: []
}>()

// 响应式数据
const selectedMethod = ref(props.defaultMethod)
const verificationData = ref({
  password: '',
  smsCode: '',
  totpCode: ''
})
const showPassword = ref(false)
const verifying = ref(false)
const errorMessage = ref('')
const smsCountdown = ref(0)
const sendingSms = ref(false)

// 引用
const passwordInput = ref<HTMLInputElement>()
const smsInput = ref<HTMLInputElement>()
const totpInput = ref<HTMLInputElement>()

// 计算属性
const enabledMethods = computed(() => 
  props.availableMethods.filter(method => method.enabled)
)

const maskedPhone = computed(() => {
  if (!props.userPhone) return '***'
  const phone = props.userPhone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
})

const canVerify = computed(() => {
  if (!selectedMethod.value) return false
  
  switch (selectedMethod.value) {
    case 'password':
      return verificationData.value.password.length >= 6
    case 'sms':
      return verificationData.value.smsCode.length === 6
    case 'totp':
      return verificationData.value.totpCode.length === 6
    default:
      return false
  }
})

// 方法
const handleMethodChange = () => {
  errorMessage.value = ''
  verificationData.value = {
    password: '',
    smsCode: '',
    totpCode: ''
  }
  
  // 自动发送短信验证码
  if (selectedMethod.value === 'sms') {
    handleSendSms()
  }
  
  // 自动聚焦输入框
  nextTick(() => {
    focusInput()
  })
}

const handleSendSms = async () => {
  if (!props.userPhone) {
    errorMessage.value = '未绑定手机号码'
    return
  }
  
  sendingSms.value = true
  try {
    // 模拟发送短信
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('验证码已发送')
    startSmsCountdown()
  } catch (error) {
    errorMessage.value = '发送验证码失败，请重试'
  } finally {
    sendingSms.value = false
  }
}

const handleResendSms = () => {
  handleSendSms()
}

const startSmsCountdown = () => {
  smsCountdown.value = 60
  const timer = setInterval(() => {
    smsCountdown.value--
    if (smsCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const handleVerify = async () => {
  if (!canVerify.value || verifying.value) return
  
  errorMessage.value = ''
  verifying.value = true
  
  try {
    let verificationValue = ''
    
    switch (selectedMethod.value) {
      case 'password':
        verificationValue = verificationData.value.password
        break
      case 'sms':
        verificationValue = verificationData.value.smsCode
        break
      case 'totp':
        verificationValue = verificationData.value.totpCode
        break
    }
    
    // 模拟验证过程
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 模拟验证结果（70%成功率）
    const success = Math.random() > 0.3
    
    if (success) {
      emit('verify', {
        method: selectedMethod.value,
        value: verificationValue
      })
    } else {
      throw new Error('验证失败')
    }
  } catch (error) {
    errorMessage.value = getErrorMessage(selectedMethod.value)
  } finally {
    verifying.value = false
  }
}

const getErrorMessage = (method: 'password' | 'sms' | 'totp') => {
  switch (method) {
    case 'password':
      return '密码错误，请重新输入'
    case 'sms':
      return '验证码错误或已过期'
    case 'totp':
      return '验证码错误，请检查时间同步'
    default:
      return '验证失败，请重试'
  }
}

const handleCancel = () => {
  emit('cancel')
  resetForm()
}

const handleOverlayClick = () => {
  if (props.allowOverlayClose) {
    emit('close')
    resetForm()
  }
}

const resetForm = () => {
  selectedMethod.value = props.defaultMethod
  verificationData.value = {
    password: '',
    smsCode: '',
    totpCode: ''
  }
  showPassword.value = false
  errorMessage.value = ''
  verifying.value = false
  smsCountdown.value = 0
}

const focusInput = () => {
  if (!props.autoFocus) return
  
  nextTick(() => {
    switch (selectedMethod.value) {
      case 'password':
        passwordInput.value?.focus()
        break
      case 'sms':
        smsInput.value?.focus()
        break
      case 'totp':
        totpInput.value?.focus()
        break
    }
  })
}

// 监听器
watch(() => props.visible, (visible) => {
  if (visible) {
    resetForm()
    focusInput()
  }
})

// 键盘事件处理
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.visible) {
    handleCancel()
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.secondary-verification {
  position: relative;
}

.verification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.verification-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.header-icon {
  margin-right: 0.75rem;
}

.modal-title {
  flex: 1;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
}

.close-button {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #f7fafc;
  color: #2d3748;
}

.modal-body {
  padding: 1.5rem;
}

.warning-message {
  margin-bottom: 1.5rem;
}

.warning-text {
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.operation-details {
  background: #fef5e7;
  border: 1px solid #f6e05e;
  border-radius: 6px;
  padding: 1rem;
}

.operation-details h4 {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #744210;
}

.operation-details ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.operation-details li {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.detail-label {
  color: #744210;
  font-weight: 500;
}

.detail-value {
  color: #2d3748;
  font-family: 'Monaco', 'Menlo', monospace;
}

.verification-methods {
  margin-bottom: 1.5rem;
}

.verification-methods h4 {
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
}

.method-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.method-option {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.method-option:hover {
  border-color: #cbd5e0;
  background: #f7fafc;
}

.method-option.active {
  border-color: #4299e1;
  background: #ebf8ff;
}

.method-option input[type="radio"] {
  margin-right: 0.75rem;
}

.method-icon {
  margin-right: 0.75rem;
  color: #4a5568;
}

.method-option.active .method-icon {
  color: #4299e1;
}

.method-info {
  flex: 1;
}

.method-name {
  display: block;
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.method-desc {
  display: block;
  font-size: 0.875rem;
  color: #718096;
}

.verification-input {
  margin-bottom: 1rem;
}

.input-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2d3748;
}

.password-input-wrapper,
.sms-input-wrapper {
  display: flex;
  gap: 0.5rem;
}

.verification-input-field {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.verification-input-field:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.verification-input-field:disabled {
  background: #f7fafc;
  color: #a0aec0;
}

.password-toggle {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-left: none;
  border-radius: 0 6px 6px 0;
  background: #f7fafc;
  color: #718096;
  cursor: pointer;
  transition: all 0.2s ease;
}

.password-toggle:hover {
  background: #edf2f7;
  color: #4a5568;
}

.resend-button {
  padding: 0.75rem 1rem;
  border: 1px solid #4299e1;
  border-radius: 6px;
  background: transparent;
  color: #4299e1;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.resend-button:hover:not(:disabled) {
  background: #4299e1;
  color: white;
}

.resend-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fed7d7;
  border: 1px solid #feb2b2;
  border-radius: 6px;
  color: #c53030;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.cancel-button,
.verify-button {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cancel-button {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #718096;
}

.cancel-button:hover:not(:disabled) {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.verify-button {
  background: #4299e1;
  border: 1px solid #4299e1;
  color: white;
}

.verify-button:hover:not(:disabled) {
  background: #3182ce;
  border-color: #3182ce;
}

.verify-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .verification-overlay {
    padding: 0.5rem;
  }
  
  .verification-modal {
    max-height: 95vh;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .method-options {
    gap: 0.5rem;
  }
  
  .method-option {
    padding: 0.75rem;
  }
  
  .password-input-wrapper,
  .sms-input-wrapper {
    flex-direction: column;
  }
  
  .password-toggle {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .cancel-button,
  .verify-button {
    width: 100%;
    justify-content: center;
  }
}
</style>