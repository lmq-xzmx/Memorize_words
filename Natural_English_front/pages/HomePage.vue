<template>
  <div class="homepage-container">
    <!-- 加载中状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在跳转到您的首页...</p>
    </div>
    
    <div v-else>
      <!-- 调试工具 - 仅在开发环境显示 -->
      <div v-if="isDevelopment" class="debug-tools" style="position: fixed; top: 10px; right: 10px; z-index: 9999; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; font-size: 12px;">
        <div>当前首页设置: {{ currentHomepage || '无' }}</div>
        <button @click="clearHomepageSettings" style="margin-top: 5px; padding: 5px 10px; background: #ff4444; color: white; border: none; border-radius: 3px; cursor: pointer;">清除首页设置</button>
        <button @click="forceShowSelector" style="margin-top: 5px; margin-left: 5px; padding: 5px 10px; background: #4444ff; color: white; border: none; border-radius: 3px; cursor: pointer;">强制显示选择器</button>
      </div>
      <!-- 如果没有设置首页，显示学习模式选择器 -->
      <LearningModeSelector />
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-section {
  text-align: center;
  margin-bottom: 4rem;
  max-width: 800px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1.5rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-button {
  padding: 16px 32px;
  border: none;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 160px;
  justify-content: center;
}

.hero-button.primary {
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.hero-button.primary:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  background: white;
}

.hero-button.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.hero-button.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.features-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  width: 100%;
  margin-bottom: 4rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #667eea;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

.feature-description {
  color: #666;
  line-height: 1.6;
}

.stats-section {
  display: flex;
  gap: 3rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 4rem;
}

.stat-item {
  text-align: center;
  color: white;
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  display: block;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-top: 0.5rem;
}

.cta-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 600px;
  width: 100%;
}

.cta-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
}

.cta-description {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.cta-button {
  padding: 16px 40px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: none;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.cta-button:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-page {
    padding: 16px;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-button {
    width: 100%;
    max-width: 280px;
  }
  
  .features-section {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .feature-card {
    padding: 1.5rem;
  }
  
  .stats-section {
    gap: 2rem;
  }
  
  .stat-number {
    font-size: 2.5rem;
  }
  
  .cta-section {
    padding: 2rem;
  }
  
  .cta-title {
    font-size: 1.75rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-button {
    padding: 14px 24px;
    font-size: 16px;
  }
  
  .feature-icon {
    font-size: 2.5rem;
  }
  
  .feature-title {
    font-size: 1.25rem;
  }
  
  .stats-section {
    gap: 1.5rem;
  }
  
  .stat-number {
    font-size: 2rem;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in-up {
  animation: fadeInUp 0.8s ease-out;
}

.fade-in-up:nth-child(2) {
  animation-delay: 0.2s;
}

.fade-in-up:nth-child(3) {
  animation-delay: 0.4s;
}

.fade-in-up:nth-child(4) {
  animation-delay: 0.6s;
}
</style>

<script>
import { homepageManager } from '../utils/homepageManager'
import { isAuthenticated, getCurrentUser, hasPermission } from '../utils/permission'
import LearningModeSelector from './LearningModeSelector.vue'

export default {
  name: 'HomePage',
  components: {
    LearningModeSelector
  },
  data() {
    return {
      isLoading: true,
      isDevelopment: process.env.NODE_ENV === 'development',
      currentHomepage: null
    }
  },
  mounted() {
    this.currentHomepage = homepageManager.getHomepage()
    this.handleHomepageRedirect()
  },
  methods: {
    async handleHomepageRedirect() {
      try {
        console.log('HomePage: 开始处理首页逻辑')
        
        // 调试：检查当前路径和查询参数
        console.log('当前路径:', this.$route.path)
        console.log('查询参数:', this.$route.query)
        
        // 如果URL包含 force=true 参数，清除首页设置并显示选择器
        if (this.$route.query && this.$route.query.force === 'true') {
          console.log('检测到force参数，清除首页设置')
          homepageManager.clearHomepage()
          this.isLoading = false
          return
        }
        
        // 检查是否有设置的首页
        const currentHomepage = homepageManager.getHomepage()
        console.log('当前设置的首页:', currentHomepage)
        this.currentHomepage = currentHomepage
        
        // 暂时禁用自动重定向，让用户手动选择
        // 这样可以避免登录后立即跳转的问题
        console.log('首页加载完成，显示学习模式选择器')
        this.isLoading = false
        
      } catch (error) {
        console.error('首页处理失败:', error)
        this.isLoading = false
      }
    },
    
    clearHomepageSettings() {
      homepageManager.clearHomepage()
      this.currentHomepage = null
      console.log('首页设置已清除')
      // 刷新页面以重新显示选择器
      this.$forceUpdate()
    },
    
    forceShowSelector() {
      this.isLoading = false
      this.currentHomepage = null
      console.log('强制显示学习模式选择器')
    }
  }
}
</script>

