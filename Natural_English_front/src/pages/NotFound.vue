<template>
  <div class="not-found">
    <div class="not-found-container">
      <div class="error-code">404</div>
      <div class="error-message">
        <h1>页面未找到</h1>
        <p>抱歉，您访问的页面不存在或已被移除。</p>
      </div>
      <div class="actions">
        <el-button type="primary" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { House, ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped lang="scss">
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;

  .not-found-container {
    text-align: center;
    background: white;
    border-radius: 20px;
    padding: 60px 40px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    width: 100%;

    .error-code {
      font-size: 120px;
      font-weight: bold;
      color: #667eea;
      line-height: 1;
      margin-bottom: 20px;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }

    .error-message {
      margin-bottom: 40px;

      h1 {
        font-size: 32px;
        color: #333;
        margin-bottom: 16px;
        font-weight: 600;
      }

      p {
        font-size: 16px;
        color: #666;
        line-height: 1.6;
        margin: 0;
      }
    }

    .actions {
      display: flex;
      gap: 16px;
      justify-content: center;
      flex-wrap: wrap;

      .el-button {
        padding: 12px 24px;
        font-size: 16px;
        border-radius: 8px;
        min-width: 120px;
      }
    }
  }
}

@media (max-width: 768px) {
  .not-found {
    .not-found-container {
      padding: 40px 20px;
      margin: 20px;

      .error-code {
        font-size: 80px;
      }

      .error-message h1 {
        font-size: 24px;
      }

      .actions {
        flex-direction: column;
        align-items: center;

        .el-button {
          width: 100%;
          max-width: 200px;
        }
      }
    }
  }
}
</style>