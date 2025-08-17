<template>
  <div class="error-container">
    <!-- 权限不足错误 -->
    <div v-if="errorType === 'permission'" class="error-container__error-content permission-error">
      <div class="error-container__error-icon">🔒</div>
      <h2>权限不足</h2>
      <p>{{ errorMessage || '您没有权限访问此功能' }}</p>
      <div class="error-container__error-actions">
        <button @click="goBack" class="error-container__btn error-container__btn--secondary">返回上一页</button>
        <button @click="goHome" class="error-container__btn error-container__btn--primary">返回首页</button>
      </div>
    </div>
    
    <!-- 认证错误 -->
    <div v-else-if="errorType === 'auth'" class="error-container__error-content auth-error">
      <div class="error-container__error-icon">🔐</div>
      <h2>需要登录</h2>
      <p>{{ errorMessage || '请先登录后再访问此功能' }}</p>
      <div class="error-container__error-actions">
        <button @click="goToLogin" class="error-container__btn error-container__btn--primary">立即登录</button>
        <button @click="goHome" class="error-container__btn error-container__btn--secondary">返回首页</button>
      </div>
    </div>
    
    <!-- 网络错误 -->
    <div v-else-if="errorType === 'network'" class="error-container__error-content network-error">
      <div class="error-container__error-icon">🌐</div>
      <h2>网络连接异常</h2>
      <p>{{ errorMessage || '请检查网络连接后重试' }}</p>
      <div class="error-container__error-actions">
        <button @click="retry" class="error-container__btn error-container__btn--primary">重试</button>
        <button @click="goHome" class="error-container__btn error-container__btn--secondary">返回首页</button>
      </div>
    </div>
    
    <!-- 通用错误 -->
    <div v-else class="error-container__error-content general-error">
      <div class="error-container__error-icon">⚠️</div>
      <h2>出现错误</h2>
      <p>{{ errorMessage || '系统出现异常，请稍后重试' }}</p>
      <div class="error-container__error-actions">
        <button @click="retry" class="error-container__btn error-container__btn--primary">重试</button>
        <button @click="goHome" class="error-container__btn error-container__btn--secondary">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

type ErrorType = 'permission' | 'auth' | 'network' | 'general'

interface Props {
  errorType?: ErrorType
  errorMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  errorType: 'general',
  errorMessage: ''
})

const emit = defineEmits<{
  retry: []
}>()

const router = useRouter()

const goHome = (): void => {
  router.push('/')
}

const goBack = (): void => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}

const goToLogin = (): void => {
  router.push('/login')
}

const retry = (): void => {
  emit('retry')
  // 如果没有监听retry事件，则刷新页面
  setTimeout(() => {
    window.location.reload()
  }, 100)
}
</script>

<style lang="scss" scoped>
@use '../styles/index.scss';
@use '../styles/variables.scss' as *;
@use '../styles/mixins.scss' as *;

.error-container {
  @include flex-center;
  min-height: 100vh;
  padding: var(--spacing-8);
  background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-purple-600) 100%);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
    pointer-events: none;
  }
}

.error-container__error-content {
  background: rgba(var(--color-white), 0.95);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-2xl);
  padding: var(--spacing-12) var(--spacing-10);
  text-align: center;
  box-shadow: var(--shadow-2xl);
  max-width: 500px;
  width: 100%;
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;

  h2 {
    @include text-style('2xl', 'semibold');
    color: var(--color-gray-800);
    margin-bottom: var(--spacing-4);
  }

  p {
    @include text-style('lg');
    color: var(--color-gray-600);
    margin-bottom: var(--spacing-8);
    line-height: 1.6;
  }
}

.error-container__error-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-6);
  animation: bounce 2s infinite;
}

.error-container__error-actions {
  @include flex-center;
  gap: var(--spacing-4);
  flex-wrap: wrap;
}

.error-container__btn {
  padding: var(--spacing-3) var(--spacing-6);
    border: none;
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  @include flex-center;
  gap: var(--spacing-2);
  min-width: 120px;
}

.error-container__btn--primary {
  background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-purple-600) 100%);
  color: var(--color-white);
  box-shadow: 0 4px 15px rgba(var(--color-primary-500), 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(var(--color-primary-500), 0.4);
  }
}

.error-container__btn--secondary {
  background: rgba(var(--color-white), 0.8);
  color: var(--color-primary-500);
  border: 2px solid var(--color-primary-500);

  &:hover {
    background: var(--color-primary-500);
    color: var(--color-white);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(var(--color-primary-500), 0.3);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-15px);
  }
  60% {
    transform: translateY(-7px);
  }
}

// 响应式设计
@media (max-width: 768px) {
  @include bem-block('error-container') {
    padding: var(--spacing-4);
    
    @include bem-element('error-content') {
      padding: var(--spacing-8) var(--spacing-6);
    }
    
    @include bem-element('error-actions') {
      flex-direction: column;
      align-items: center;
    }
    
    @include bem-element('btn') {
      width: 100%;
      max-width: 250px;
    }
  }
}

@media (max-width: 576px) {
  @include bem-block('error-container') {
    @include bem-element('error-icon') {
      font-size: 3rem;
    }
    
    @include bem-element('error-content') {
      padding: var(--spacing-6) var(--spacing-4);
      
      h2 {
        @include text-style('xl', 'semibold');
      }
      
      p {
        @include text-style('base');
      }
    }
  }
}
</style>

