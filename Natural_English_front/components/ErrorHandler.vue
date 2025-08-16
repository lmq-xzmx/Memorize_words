<template>
  <div class="error-container">
    <!-- 权限不足错误 -->
    <div v-if="errorType === 'permission'" class="error-content permission-error">
      <div class="error-icon">🔒</div>
      <h2>权限不足</h2>
      <p>{{ errorMessage || '您没有权限访问此功能' }}</p>
      <div class="error-actions">
        <button @click="goBack" class="btn-secondary">返回上一页</button>
        <button @click="goHome" class="btn-primary">返回首页</button>
      </div>
    </div>
    
    <!-- 认证错误 -->
    <div v-else-if="errorType === 'auth'" class="error-content auth-error">
      <div class="error-icon">🔐</div>
      <h2>需要登录</h2>
      <p>{{ errorMessage || '请先登录后再访问此功能' }}</p>
      <div class="error-actions">
        <button @click="goToLogin" class="btn-primary">立即登录</button>
        <button @click="goHome" class="btn-secondary">返回首页</button>
      </div>
    </div>
    
    <!-- 网络错误 -->
    <div v-else-if="errorType === 'network'" class="error-content network-error">
      <div class="error-icon">🌐</div>
      <h2>网络连接异常</h2>
      <p>{{ errorMessage || '请检查网络连接后重试' }}</p>
      <div class="error-actions">
        <button @click="retry" class="btn-primary">重试</button>
        <button @click="goHome" class="btn-secondary">返回首页</button>
      </div>
    </div>
    
    <!-- 通用错误 -->
    <div v-else class="error-content general-error">
      <div class="error-icon">⚠️</div>
      <h2>出现错误</h2>
      <p>{{ errorMessage || '系统出现异常，请稍后重试' }}</p>
      <div class="error-actions">
        <button @click="retry" class="btn-primary">重试</button>
        <button @click="goHome" class="btn-secondary">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ErrorHandler',
  props: {
    errorType: {
      type: String,
      default: 'general',
      validator: value => ['permission', 'auth', 'network', 'general'].includes(value)
    },
    errorMessage: {
      type: String,
      default: ''
    },
    showRetry: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    goBack() {
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        this.goHome()
      }
    },
    
    goHome() {
      this.$router.push('/')
    },
    
    goToLogin() {
      this.$router.push('/login')
    },
    
    retry() {
      this.$emit('retry')
      // 如果没有监听retry事件，则刷新页面
      if (!this.$listeners.retry) {
        window.location.reload()
      }
    }
  }
}
</script>

<style scoped>
.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.error-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
  pointer-events: none;
}

.error-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem 2.5rem;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
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
  margin-bottom: 1.5rem;
  animation: bounce 2s infinite;
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

.error-content h2 {
  font-size: 2rem;
  color: #2d3748;
  margin-bottom: 1rem;
  font-weight: 600;
}

.error-content p {
  font-size: 1.1rem;
  color: #4a5568;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 120px;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.8);
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

/* 特定错误类型的样式 */
.auth-error .error-icon {
  color: #f56565;
}

.permission-error .error-icon {
  color: #ed8936;
}

.network-error .error-icon {
  color: #4299e1;
}

.general-error .error-icon {
  color: #9f7aea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-container {
    padding: 1rem;
  }
  
  .error-content {
    padding: 2rem 1.5rem;
  }
  
  .error-content h2 {
    font-size: 1.5rem;
  }
  
  .error-content p {
    font-size: 1rem;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-primary, .btn-secondary {
    width: 100%;
    max-width: 250px;
  }
}

@media (max-width: 480px) {
  .error-icon {
    font-size: 3rem;
  }
  
  .error-content h2 {
    font-size: 1.25rem;
  }
  
  .error-content {
    padding: 1.5rem 1rem;
  }
}
</style>

