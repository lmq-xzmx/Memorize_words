<template>
  <div class="login-container">
    <div class="login-background">
      <div class="bg-decoration bg-decoration-1"></div>
      <div class="bg-decoration bg-decoration-2"></div>
      <div class="bg-decoration bg-decoration-3"></div>
    </div>
    
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">Natural English</h1>
        <p class="login-subtitle">英语学习平台</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名或邮箱"
            size="large"
            prefix-icon="User"
            :disabled="loading"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            :disabled="loading"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
        
        <div class="login-footer">
          <router-link to="/register" class="register-link">
            还没有账号？立即注册
          </router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const store = useStore()

// 表单引用
const loginFormRef = ref<FormInstance>()

// 加载状态
const loading = ref(false)

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ]
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    const result = await store.dispatch('auth/login', {
      username: loginForm.username,
      password: loginForm.password
    })
    
    if (result.success) {
      // 登录成功后获取用户信息
      try {
        const userInfo = await store.dispatch('user/fetchUserInfo')
        // 将用户信息存储到localStorage供路由守卫使用
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
        
        ElMessage.success('登录成功')
        
        // 检查是否有重定向参数
        const redirect = router.currentRoute.value.query.redirect as string
        router.push(redirect || '/dashboard')
      } catch (userError) {
        console.error('获取用户信息失败:', userError)
        ElMessage.warning('登录成功，但获取用户信息失败，请刷新页面')
        router.push('/dashboard')
      }
    } else {
      ElMessage.error(result.message || '登录失败')
    }
  } catch (error) {
    console.error('登录错误:', error)
    ElMessage.error('登录过程中发生错误')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.bg-decoration {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
  
  &.bg-decoration-1 {
    width: 200px;
    height: 200px;
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }
  
  &.bg-decoration-2 {
    width: 150px;
    height: 150px;
    top: 60%;
    right: 15%;
    animation-delay: 2s;
  }
  
  &.bg-decoration-3 {
    width: 100px;
    height: 100px;
    bottom: 20%;
    left: 20%;
    animation-delay: 4s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-large);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.login-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.login-form {
  .el-form-item {
    margin-bottom: var(--spacing-lg);
  }
  
  .login-btn {
    width: 100%;
    height: 48px;
    font-size: var(--font-size-medium);
    font-weight: 600;
  }
}

.login-footer {
  text-align: center;
  margin-top: var(--spacing-lg);
}

.register-link {
  color: var(--color-primary);
  font-size: var(--font-size-small);
  transition: var(--transition-base);
  
  &:hover {
    color: var(--color-primary-light);
    text-decoration: underline;
  }
}

// 响应式设计
@media (max-width: $breakpoint-sm) {
  .login-card {
    margin: var(--spacing-md);
    padding: var(--spacing-lg);
  }
  
  .login-title {
    font-size: 24px;
  }
}
</style>