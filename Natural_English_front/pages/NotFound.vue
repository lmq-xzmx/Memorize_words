<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-icon">🔍</div>
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面未找到</h2>
      <p class="error-description">
        抱歉，您访问的页面不存在或已被移除。
      </p>
      
      <div class="action-buttons">
        <button @click="goHome" class="btn-primary">
          <span class="btn-icon">🏠</span>
          返回首页
        </button>
        <button @click="goBack" class="btn-secondary">
          <span class="btn-icon">↩️</span>
          返回上页
        </button>
      </div>
      
      <div class="suggestions">
        <h3 class="suggestions__title">您可能想要：</h3>
        <ul class="suggestion-list">
          <li class="suggestion-list__item"><router-link to="/" class="suggestion-list__link">📚 开始学习</router-link></li>
          <li class="suggestion-list__item"><router-link to="/dashboard" class="suggestion-list__link">📊 查看仪表板</router-link></li>
          <li class="suggestion-list__item"><router-link to="/profile" class="suggestion-list__link">👤 个人资料</router-link></li>
          <li class="suggestion-list__item"><router-link to="/settings" class="suggestion-list__link">⚙️ 系统设置</router-link></li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goHome() {
      this.$router.push('/')
    },
    goBack() {
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        this.$router.push('/')
      }
    }
  },
  mounted() {
    // 设置页面标题
    document.title = '页面未找到 - Natural English'
  }
}
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;
@use '../styles/mixins.scss' as *;

@include bem-block('not-found-container') {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  @include flex-center;
  padding: var(--spacing-8);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="3" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
    animation: float 20s linear infinite;
  }
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  100% {
    transform: translateY(-100px);
  }
}

@include bem-block('not-found-content') {
  text-align: center;
  background: rgba(var(--color-white), 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-3xl);
  padding: var(--spacing-16) var(--spacing-12);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(var(--color-white), 0.3);
  max-width: 600px;
  width: 100%;
  position: relative;
  z-index: 1;
  animation: slideInUp 0.8s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-6);
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

.error-code {
  font-size: var(--font-size-6xl);
  font-weight: 900;
  color: #667eea;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.error-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-slate-800);
  margin: var(--spacing-4) 0;
  animation: fadeIn 1s ease-out 0.3s both;
}

.error-description {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-normal);
  color: var(--color-slate-600);
  margin-bottom: var(--spacing-12);
  line-height: 1.6;
  animation: fadeIn 1s ease-out 0.6s both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-12);
  flex-wrap: wrap;
  animation: fadeIn 1s ease-out 0.9s both;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-4) var(--spacing-8);
  border: none;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-lg);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  min-width: 150px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: var(--color-white);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
  }
}

.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-4) var(--spacing-8);
  border: none;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-lg);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  min-width: 150px;
  background: rgba(var(--color-white), 0.8);
  color: #667eea;
  border: 2px solid #667eea;
  
  &:hover {
    background: #667eea;
    color: var(--color-white);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
}

.btn-icon {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-normal);
}

.suggestions {
  animation: fadeIn 1s ease-out 1.2s both;
  
  .suggestions__title {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--color-slate-800);
    margin-bottom: var(--spacing-6);
  }
}

.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
  
  .suggestion-list__item {
    background: rgba(102, 126, 234, 0.1);
    border-radius: var(--border-radius-xl);
    transition: all 0.3s ease;
    
    &:hover {
      background: rgba(102, 126, 234, 0.2);
      transform: translateY(-2px);
    }
    
    .suggestion-list__item__link {
      display: block;
      padding: var(--spacing-4);
      text-decoration: none;
      color: #667eea;
      font-weight: 500;
      border-radius: var(--border-radius-xl);
      transition: all 0.3s ease;
      
      &:hover {
        color: #764ba2;
      }
    }
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .not-found-content {
    padding: var(--spacing-12) var(--spacing-8);
  margin: var(--spacing-4);
  }
  
  .error-code {
    font-size: var(--font-size-5xl);
    font-weight: var(--font-weight-bold);
  }
  
  .error-title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
  }
  
  .error-description {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-normal);
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-primary {
     width: 100%;
     max-width: 250px;
   }
   
   .btn-secondary {
     width: 100%;
     max-width: 250px;
   }
  
  .suggestion-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .not-found-content {
    padding: var(--spacing-8) var(--spacing-6);
  }
  
  .error-code {
    font-size: var(--font-size-4xl);
    font-weight: var(--font-weight-bold);
  }
  
  .error-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
  }
  
  .error-icon {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
  }
}
</style>

