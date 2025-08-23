<template>
  <div class="loading-component" :class="loadingClasses">
    <!-- 全屏加载遮罩 -->
    <div v-if="overlay" class="loading-overlay" @click="handleOverlayClick">
      <div class="loading-content" @click.stop>
        <div class="loading-spinner" :class="spinnerClasses">
          <component :is="spinnerComponent" />
        </div>
        
        <div v-if="showText" class="loading-text">
          <h3 v-if="title" class="loading-title">{{ title }}</h3>
          <p v-if="message" class="loading-message">{{ message }}</p>
          
          <!-- 进度条 -->
          <div v-if="showProgress" class="loading-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
            <span class="progress-text">{{ progress }}%</span>
          </div>
          
          <!-- 加载步骤 -->
          <div v-if="steps && steps.length" class="loading-steps">
            <div 
              v-for="(step, index) in steps" 
              :key="index"
              class="loading-step"
              :class="getStepClass(index)"
            >
              <div class="step-icon">
                <span v-if="index < currentStep">✓</span>
                <span v-else-if="index === currentStep" class="step-spinner">⟳</span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <span class="step-text">{{ step }}</span>
            </div>
          </div>
          
          <!-- 取消按钮 -->
          <button 
            v-if="showCancel" 
            class="loading-cancel"
            @click="handleCancel"
          >
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 内联加载 -->
    <div v-else class="loading-inline">
      <div class="loading-spinner" :class="spinnerClasses">
        <component :is="spinnerComponent" />
      </div>
      
      <div v-if="showText" class="loading-text">
        <span v-if="message" class="loading-message">{{ message }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'

// 加载动画组件
const SpinnerDefault = {
  template: `
    <svg class="spinner-svg" viewBox="0 0 50 50">
      <circle 
        class="spinner-circle" 
        cx="25" 
        cy="25" 
        r="20" 
        fill="none" 
        stroke="currentColor" 
        stroke-width="2" 
        stroke-linecap="round" 
        stroke-dasharray="31.416" 
        stroke-dashoffset="31.416"
      />
    </svg>
  `
}

const SpinnerDots = {
  template: `
    <div class="spinner-dots">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
  `
}

const SpinnerPulse = {
  template: `
    <div class="spinner-pulse">
      <div class="pulse-ring"></div>
      <div class="pulse-ring"></div>
      <div class="pulse-ring"></div>
    </div>
  `
}

const SpinnerBars = {
  template: `
    <div class="spinner-bars">
      <div class="bar"></div>
      <div class="bar"></div>
      <div class="bar"></div>
      <div class="bar"></div>
      <div class="bar"></div>
    </div>
  `
}

const SpinnerRipple = {
  template: `
    <div class="spinner-ripple">
      <div class="ripple"></div>
      <div class="ripple"></div>
    </div>
  `
}

export default {
  name: 'LoadingComponent',
  
  components: {
    SpinnerDefault,
    SpinnerDots,
    SpinnerPulse,
    SpinnerBars,
    SpinnerRipple
  },
  
  props: {
    // 是否显示加载状态
    loading: {
      type: Boolean,
      default: true
    },
    
    // 是否显示遮罩层
    overlay: {
      type: Boolean,
      default: false
    },
    
    // 加载标题
    title: {
      type: String,
      default: ''
    },
    
    // 加载消息
    message: {
      type: String,
      default: '加载中...'
    },
    
    // 是否显示文本
    showText: {
      type: Boolean,
      default: true
    },
    
    // 加载器类型
    type: {
      type: String,
      default: 'default',
      validator: (value) => {
        return ['default', 'dots', 'pulse', 'bars', 'ripple'].includes(value)
      }
    },
    
    // 加载器大小
    size: {
      type: String,
      default: 'medium',
      validator: (value) => {
        return ['small', 'medium', 'large'].includes(value)
      }
    },
    
    // 加载器颜色
    color: {
      type: String,
      default: 'primary'
    },
    
    // 是否显示进度条
    showProgress: {
      type: Boolean,
      default: false
    },
    
    // 进度值 (0-100)
    progress: {
      type: Number,
      default: 0,
      validator: (value) => {
        return value >= 0 && value <= 100
      }
    },
    
    // 加载步骤
    steps: {
      type: Array,
      default: () => []
    },
    
    // 当前步骤索引
    currentStep: {
      type: Number,
      default: 0
    },
    
    // 是否显示取消按钮
    showCancel: {
      type: Boolean,
      default: false
    },
    
    // 是否可以点击遮罩关闭
    closeOnOverlay: {
      type: Boolean,
      default: false
    },
    
    // 自动关闭延迟（毫秒）
    autoClose: {
      type: Number,
      default: 0
    },
    
    // 最小显示时间（毫秒）
    minDuration: {
      type: Number,
      default: 0
    }
  },
  
  emits: ['cancel', 'close', 'timeout'],
  
  setup(props, { emit }) {
    // 响应式状态
    const startTime = ref(Date.now())
    const autoCloseTimer = ref(null)
    const minDurationTimer = ref(null)
    const canClose = ref(false)
    
    // 计算属性
    const loadingClasses = computed(() => {
      return {
        'loading-overlay-mode': props.overlay,
        'loading-inline-mode': !props.overlay,
        [`loading-${props.size}`]: true,
        [`loading-${props.color}`]: true
      }
    })
    
    const spinnerClasses = computed(() => {
      return {
        [`spinner-${props.size}`]: true,
        [`spinner-${props.color}`]: true
      }
    })
    
    const spinnerComponent = computed(() => {
      const typeMap = {
        default: 'SpinnerDefault',
        dots: 'SpinnerDots',
        pulse: 'SpinnerPulse',
        bars: 'SpinnerBars',
        ripple: 'SpinnerRipple'
      }
      return typeMap[props.type] || 'SpinnerDefault'
    })
    
    // 方法
    const getStepClass = (index) => {
      return {
        'step-completed': index < props.currentStep,
        'step-active': index === props.currentStep,
        'step-pending': index > props.currentStep
      }
    }
    
    const handleOverlayClick = () => {
      if (props.closeOnOverlay && canClose.value) {
        emit('close')
      }
    }
    
    const handleCancel = () => {
      emit('cancel')
    }
    
    const setupAutoClose = () => {
      if (props.autoClose > 0) {
        autoCloseTimer.value = setTimeout(() => {
          emit('timeout')
          emit('close')
        }, props.autoClose)
      }
    }
    
    const setupMinDuration = () => {
      if (props.minDuration > 0) {
        minDurationTimer.value = setTimeout(() => {
          canClose.value = true
        }, props.minDuration)
      } else {
        canClose.value = true
      }
    }
    
    const clearTimers = () => {
      if (autoCloseTimer.value) {
        clearTimeout(autoCloseTimer.value)
        autoCloseTimer.value = null
      }
      
      if (minDurationTimer.value) {
        clearTimeout(minDurationTimer.value)
        minDurationTimer.value = null
      }
    }
    
    // 监听加载状态变化
    watch(
      () => props.loading,
      (newLoading) => {
        if (newLoading) {
          startTime.value = Date.now()
          canClose.value = false
          setupAutoClose()
          setupMinDuration()
        } else {
          clearTimers()
        }
      },
      { immediate: true }
    )
    
    // 生命周期
    onMounted(() => {
      if (props.loading) {
        setupAutoClose()
        setupMinDuration()
      }
    })
    
    onUnmounted(() => {
      clearTimers()
    })
    
    return {
      // 计算属性
      loadingClasses,
      spinnerClasses,
      spinnerComponent,
      
      // 方法
      getStepClass,
      handleOverlayClick,
      handleCancel
    }
  }
}
</script>

<style scoped>
.loading-component {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 遮罩层模式 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-6);
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 400px;
  margin: var(--space-4);
  animation: slideUp var(--duration-normal) var(--ease-out);
}

/* 内联模式 */
.loading-inline {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
}

/* 加载器容器 */
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-4);
}

.loading-inline .loading-spinner {
  margin-bottom: 0;
}

/* 加载器大小 */
.spinner-small {
  width: 20px;
  height: 20px;
}

.spinner-medium {
  width: 32px;
  height: 32px;
}

.spinner-large {
  width: 48px;
  height: 48px;
}

/* 加载器颜色 */
.spinner-primary {
  color: var(--color-primary);
}

.spinner-secondary {
  color: var(--color-text-secondary);
}

.spinner-success {
  color: var(--color-success);
}

.spinner-warning {
  color: var(--color-warning);
}

.spinner-error {
  color: var(--color-error);
}

/* 默认加载器 */
.spinner-svg {
  width: 100%;
  height: 100%;
  animation: rotate 2s linear infinite;
}

.spinner-circle {
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

/* 点状加载器 */
.spinner-dots {
  display: flex;
  gap: 4px;
}

.spinner-dots .dot {
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 50%;
  animation: dotPulse 1.4s ease-in-out infinite both;
}

.spinner-dots .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.spinner-dots .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes dotPulse {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 脉冲加载器 */
.spinner-pulse {
  position: relative;
  width: 100%;
  height: 100%;
}

.pulse-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid currentColor;
  border-radius: 50%;
  opacity: 1;
  animation: pulseRing 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

.pulse-ring:nth-child(2) {
  animation-delay: 0.5s;
}

.pulse-ring:nth-child(3) {
  animation-delay: 1s;
}

@keyframes pulseRing {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

/* 条状加载器 */
.spinner-bars {
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 100%;
}

.spinner-bars .bar {
  width: 4px;
  background: currentColor;
  animation: barStretch 1.2s infinite ease-in-out;
}

.spinner-bars .bar:nth-child(1) {
  animation-delay: -1.2s;
}

.spinner-bars .bar:nth-child(2) {
  animation-delay: -1.1s;
}

.spinner-bars .bar:nth-child(3) {
  animation-delay: -1.0s;
}

.spinner-bars .bar:nth-child(4) {
  animation-delay: -0.9s;
}

.spinner-bars .bar:nth-child(5) {
  animation-delay: -0.8s;
}

@keyframes barStretch {
  0%, 40%, 100% {
    height: 20%;
  }
  20% {
    height: 100%;
  }
}

/* 波纹加载器 */
.spinner-ripple {
  position: relative;
  width: 100%;
  height: 100%;
}

.ripple {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid currentColor;
  border-radius: 50%;
  opacity: 1;
  animation: rippleEffect 2s cubic-bezier(0, 0.2, 0.8, 1) infinite;
}

.ripple:nth-child(2) {
  animation-delay: 1s;
}

@keyframes rippleEffect {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

/* 文本内容 */
.loading-text {
  text-align: center;
  color: var(--color-text);
}

.loading-title {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.loading-message {
  margin: 0 0 var(--space-4) 0;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.loading-inline .loading-message {
  margin: 0;
  font-size: var(--font-size-sm);
}

/* 进度条 */
.loading-progress {
  width: 100%;
  margin-bottom: var(--space-4);
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  transition: width var(--duration-normal) var(--ease-out);
}

.progress-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 加载步骤 */
.loading-steps {
  width: 100%;
  margin-bottom: var(--space-4);
}

.loading-step {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border);
}

.loading-step:last-child {
  border-bottom: none;
}

.step-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  flex-shrink: 0;
}

.step-completed .step-icon {
  background: var(--color-success);
  color: white;
}

.step-active .step-icon {
  background: var(--color-primary);
  color: white;
}

.step-pending .step-icon {
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.step-spinner {
  animation: rotate 1s linear infinite;
}

.step-text {
  flex: 1;
  font-size: var(--font-size-sm);
}

.step-completed .step-text {
  color: var(--color-text);
}

.step-active .step-text {
  color: var(--color-text);
  font-weight: var(--font-weight-medium);
}

.step-pending .step-text {
  color: var(--color-text-secondary);
}

/* 取消按钮 */
.loading-cancel {
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.loading-cancel:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-border-hover);
  color: var(--color-text);
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .loading-content {
    margin: var(--space-2);
    padding: var(--space-4);
    max-width: calc(100vw - var(--space-4));
  }
  
  .loading-steps {
    font-size: var(--font-size-sm);
  }
  
  .step-icon {
    width: 20px;
    height: 20px;
    font-size: var(--font-size-xs);
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .loading-overlay {
    background: rgba(0, 0, 0, 0.7);
  }
  
  .loading-content {
    background: var(--color-bg-dark, #1a1a1a);
    border: 1px solid var(--color-border-dark, #333);
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .spinner-svg,
  .dot,
  .pulse-ring,
  .bar,
  .ripple,
  .step-spinner {
    animation: none;
  }
  
  .progress-fill {
    transition: none;
  }
}
</style>