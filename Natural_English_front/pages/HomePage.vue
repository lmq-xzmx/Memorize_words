<template>
  <div class="homepage-container">
    <!-- 加载中状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在跳转到您的首页...</p>
    </div>
    
    <!-- 如果没有设置首页，显示学习模式选择器 -->
    <LearningModeSelector v-else />
  </div>
</template>

<script>
import { homepageManager } from '../utils/homepageManager.js'
import { isAuthenticated, getCurrentUser, hasPermission } from '../utils/permission.js'
import LearningModeSelector from './LearningModeSelector.vue'

export default {
  name: 'HomePage',
  components: {
    LearningModeSelector
  },
  data() {
    return {
      isLoading: true
    }
  },
  mounted() {
    this.handleHomepageRedirect()
  },
  methods: {
    handleHomepageRedirect() {
      try {
        // 检查用户是否已登录
        if (!isAuthenticated()) {
          console.log('用户未登录，显示学习模式选择器')
          this.isLoading = false
          return
        }
        
        const user = getCurrentUser()
        console.log('当前用户:', user)
        
        // 检查用户信息是否完整
        if (!user || !user.role) {
          console.log('用户信息不完整，显示学习模式选择器')
          this.isLoading = false
          return
        }
        
        // 检查是否有设置的首页（带权限验证）
        const redirectInfo = homepageManager.checkHomepageRedirect(
          this.$route, 
          (permission) => hasPermission(user.role, permission)
        )
        
        if (redirectInfo) {
          console.log(`重定向到设置的首页: ${redirectInfo.name} (${redirectInfo.route})`)
          this.$router.push(redirectInfo.route)
          return
        }
        
        // 如果没有设置首页或路由无效，显示学习模式选择器
        this.isLoading = false
      } catch (error) {
        console.error('首页重定向失败:', error)
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.homepage-container {
  min-height: 100vh;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  font-size: 1.1rem;
  opacity: 0.9;
}
</style>