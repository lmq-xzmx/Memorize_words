<template>
  <div class="forbidden-container">
    <div class="forbidden-content">
      <div class="error-icon">
        <svg width="120" height="120" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="#f56565" stroke-width="2"/>
          <path d="M15 9l-6 6" stroke="#f56565" stroke-width="2" stroke-linecap="round"/>
          <path d="M9 9l6 6" stroke="#f56565" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      
      <h1 class="error-title">403</h1>
      <h2 class="error-subtitle">权限不足</h2>
      <p class="error-description">
        抱歉，您没有访问此页面的权限。请联系管理员获取相应权限。
      </p>
      
      <div class="action-buttons">
        <el-button type="primary" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上一页
        </el-button>
        <el-button @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
      </div>
      
      <div class="user-info" v-if="userProfile.username">
        <p>当前用户：{{ userProfile.username }}</p>
        <p>用户角色：{{ userProfile.role }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElButton, ElIcon } from 'element-plus'
import { ArrowLeft, House } from '@element-plus/icons-vue'

const router = useRouter()
const store = useStore()

const userProfile = computed(() => store.getters['user/userProfile'])

const goBack = () => {
  router.go(-1)
}

const goHome = () => {
  // 根据用户角色跳转到合适的首页
  const role = userProfile.value.role
  if (role === 'admin') {
    router.push('/admin/dashboard')
  } else if (role === 'teacher') {
    router.push('/teacher/dashboard')
  } else {
    router.push('/dashboard')
  }
}
</script>

<style scoped lang="scss">
.forbidden-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forbidden-content {
  text-align: center;
  background: white;
  padding: 60px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.error-icon {
  margin-bottom: 30px;
  
  svg {
    filter: drop-shadow(0 4px 8px rgba(245, 101, 101, 0.3));
  }
}

.error-title {
  font-size: 72px;
  font-weight: 700;
  color: #f56565;
  margin: 0 0 10px 0;
  text-shadow: 0 2px 4px rgba(245, 101, 101, 0.3);
}

.error-subtitle {
  font-size: 32px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 20px 0;
}

.error-description {
  font-size: 16px;
  color: #718096;
  line-height: 1.6;
  margin-bottom: 40px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 30px;
  
  .el-button {
    padding: 12px 24px;
    font-size: 14px;
    border-radius: 8px;
    
    .el-icon {
      margin-right: 8px;
    }
  }
}

.user-info {
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  
  p {
    margin: 5px 0;
    font-size: 14px;
    color: #718096;
  }
}

@media (max-width: 768px) {
  .forbidden-content {
    padding: 40px 20px;
  }
  
  .error-title {
    font-size: 56px;
  }
  
  .error-subtitle {
    font-size: 24px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
    
    .el-button {
      width: 200px;
    }
  }
}
</style>