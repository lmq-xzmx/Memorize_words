<template>
  <div class="not-found-container">
    <div class="not-found-container__content">
      <div class="error-icon">🔍</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-message">抱歉，您访问的页面不存在或已被移除。</p>
      <div class="error-actions">
        <button @click="goBack" class="btn btn-secondary">
          <span class="icon">←</span>
          返回上页
        </button>
        <button @click="goHome" class="btn btn-primary">
          <span class="icon">🏠</span>
          回到首页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = (): void => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}

const goHome = (): void => {
  router.push('/')
}
</script>

<style lang="scss" scoped>
@use '../styles/index.scss';

.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
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

.not-found-container__content {
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

.error-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-6);
  animation: bounce 2s infinite;
}

.error-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-gray-800);
  margin-bottom: var(--spacing-4);
}

.error-message {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-normal);
  color: var(--color-gray-600);
  margin-bottom: var(--spacing-8);
  line-height: 1.6;
}

.error-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-4);
  flex-wrap: wrap;
}

.btn {
  padding: var(--spacing-3) var(--spacing-6);
  border: none;
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  min-width: 120px;

  &.btn-primary {
    background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-purple-600) 100%);
    color: var(--color-white);
    box-shadow: 0 4px 15px rgba(var(--color-primary-500), 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(var(--color-primary-500), 0.4);
    }
  }

  &.btn-secondary {
    background: rgba(255, 255, 255, 0.8);
    color: var(--color-primary-500);
    border: 2px solid var(--color-primary-500);

    &:hover {
      background: var(--color-primary-500);
      color: var(--color-white);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(var(--color-primary-500), 0.3);
    }
  }
}

.icon {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-normal);
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .not-found-container {
    padding: var(--spacing-4);
  }
  
  .not-found-container__content {
    padding: var(--spacing-8) var(--spacing-6);
  }
  
  .error-title {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
  }
  
  .error-message {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-normal);
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 250px;
  }
}

@media (max-width: 576px) {
  .not-found-container {
    .error-icon {
      font-size: 3rem;
    }
  }
  
  .not-found-container__content {
    padding: var(--spacing-6) var(--spacing-4);
  }
  
  .error-title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
  }
}
</style>

