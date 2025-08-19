<template>
  <div class="register-container">
    <div class="register-background">
      <div class="bg-decoration bg-decoration-1"></div>
      <div class="bg-decoration bg-decoration-2"></div>
      <div class="bg-decoration bg-decoration-3"></div>
    </div>
    
    <div class="register-card">
      <div class="register-header">
        <h1 class="register-title">加入 Natural English</h1>
        <p class="register-subtitle">开启您的英语学习之旅</p>
      </div>
      
      <el-form 
        ref="registerFormRef" 
        :model="registerForm" 
        :rules="registerRules" 
        class="register-form"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="registerForm.email"
                type="email"
                placeholder="请输入邮箱地址"
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="real_name">
              <el-input
                v-model="registerForm.real_name"
                placeholder="请输入真实姓名"
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="registerForm.phone"
                placeholder="请输入手机号"
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="网名" prop="display_name">
          <el-input
            v-model="registerForm.display_name"
            placeholder="请输入网名（可选）"
            :disabled="loading"
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select
            v-model="registerForm.role"
            placeholder="请选择您的角色"
            style="width: 100%"
            :disabled="loading || rolesLoading"
            @change="handleRoleChange"
          >
            <el-option 
              v-for="role in availableRoles" 
              :key="role.value" 
              :label="role.label" 
              :value="role.value" 
            />
          </el-select>
        </el-form-item>
        
        <!-- 动态扩展字段 -->
        <div v-if="extendedFields.length > 0" class="extended-fields">
          <el-divider content-position="left">角色信息</el-divider>
          <el-form-item
            v-for="field in extendedFields"
            :key="field.name"
            :label="field.label"
            :prop="field.name"
          >
            <!-- 文本输入框 -->
            <el-input
              v-if="field.type === 'text'"
              v-model="registerForm[field.name]"
              :placeholder="field.placeholder"
              :disabled="loading"
              clearable
            />
            
            <!-- 选择框 -->
            <el-select
              v-else-if="field.type === 'select'"
              v-model="registerForm[field.name]"
              :placeholder="field.placeholder"
              style="width: 100%"
              :disabled="loading"
              clearable
            >
              <el-option
                v-for="option in field.options"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
            
            <!-- 数字输入框 -->
            <el-input-number
              v-else-if="field.type === 'number'"
              v-model="registerForm[field.name]"
              :placeholder="field.placeholder"
              style="width: 100%"
              :disabled="loading"
            />
            
            <!-- 日期选择器 -->
            <el-date-picker
              v-else-if="field.type === 'date'"
              v-model="registerForm[field.name]"
              type="date"
              :placeholder="field.placeholder"
              style="width: 100%"
              :disabled="loading"
            />
            
            <!-- 多行文本 -->
            <el-input
              v-else-if="field.type === 'textarea'"
              v-model="registerForm[field.name]"
              type="textarea"
              :placeholder="field.placeholder"
              :rows="3"
              :disabled="loading"
            />
          </el-form-item>
        </div>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                show-password
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                show-password
                :disabled="loading"
                @keyup.enter="handleRegister"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-checkbox v-model="registerForm.agreeTerms" :disabled="loading">
            我已阅读并同意
            <a href="#" class="terms-link">《用户协议》</a>
            和
            <a href="#" class="terms-link">《隐私政策》</a>
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '立即注册' }}
          </el-button>
        </el-form-item>
        
        <div class="register-footer">
          <router-link to="/login" class="login-link">
            已有账号？立即登录
          </router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import roleService from '@/services/roleService'
import type { RoleField } from '@/services/roleService'

// 使用roleService中定义的类型
type ExtendedField = RoleField

const router = useRouter()
const store = useStore()

// 表单引用
const registerFormRef = ref<FormInstance>()

// 加载状态
const loading = ref(false)
const rolesLoading = ref(false)

// 角色列表
const availableRoles = ref<Array<{value: string, label: string, description?: string}>>([])

// 动态扩展字段
const extendedFields = ref<RoleField[]>([])

// 表单数据
const registerForm: Record<string, any> = reactive({
  username: '',
  email: '',
  real_name: '',
  phone: '',
  display_name: '',
  role: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
  // 动态字段将根据角色选择动态添加
})

// 动态生成表单验证规则
const generateFieldRules = (field: RoleField): any[] => {
  const rules: any[] = []
  
  if (field.required) {
    rules.push({ required: true, message: `请输入${field.label}`, trigger: 'blur' })
  }
  
  if (field.validation) {
    const { pattern, min, max, message } = field.validation
    
    if (pattern) {
      rules.push({ pattern: new RegExp(pattern), message: message || `${field.label}格式不正确`, trigger: 'blur' })
    }
    
    if (min !== undefined || max !== undefined) {
      rules.push({ 
        min: min || 0, 
        max: max || 999, 
        message: message || `${field.label}长度在 ${min || 0} 到 ${max || 999} 个字符`, 
        trigger: 'blur' 
      })
    }
  }
  
  return rules
}

// 密码确认验证器
const validateConfirmPassword = (rule: any, value: string, callback: Function) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 30, message: '用户名长度在 3 到 30 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' },
    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{6,}$/, message: '密码必须包含大小写字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  agreeTerms: [
    { 
      validator: (rule: any, value: boolean, callback: Function) => {
        if (!value) {
          callback(new Error('请阅读并同意用户协议和隐私政策'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ]
}

// 初始化角色列表（动态获取）
const initializeRoles = async () => {
  try {
    rolesLoading.value = true
    availableRoles.value = await roleService.getAvailableRoles()
  } catch (error) {
    console.error('初始化角色列表失败:', error)
    ElMessage.error('获取角色列表失败，请刷新页面重试')
  } finally {
    rolesLoading.value = false
  }
}

// 角色变化处理
const handleRoleChange = async () => {
  if (!registerForm.role) {
    extendedFields.value = []
    return
  }
  
  try {
    // 清空之前的扩展字段数据
    extendedFields.value.forEach((field: RoleField) => {
      delete registerForm[field.name]
    })
    
    // 获取新角色的字段配置
    extendedFields.value = await roleService.getRoleFields(registerForm.role)
    
    // 初始化新字段的默认值
    extendedFields.value.forEach((field: RoleField) => {
      registerForm[field.name] = ''
    })
    
    // 动态更新表单验证规则
    updateFormRules()
    
  } catch (error) {
    console.error('获取角色字段配置失败:', error)
    ElMessage.warning('获取角色配置失败，将使用默认配置')
    extendedFields.value = []
  }
}

// 更新表单验证规则
const updateFormRules = (): void => {
  // 为动态字段添加验证规则
  extendedFields.value.forEach((field: RoleField) => {
    const rules = generateFieldRules(field)
    if (rules.length > 0) {
      registerRules[field.name] = rules
    }
  })
}

// 组件挂载时初始化
onMounted(async () => {
  await initializeRoles()
})

// 注册处理
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    const valid = await registerFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    // 构建注册数据
    const registerData = {
      username: registerForm.username,
      email: registerForm.email,
      real_name: registerForm.real_name,
      phone: registerForm.phone,
      display_name: registerForm.display_name || registerForm.real_name,
      role: registerForm.role,
      password: registerForm.password,
      // 添加角色相关的扩展字段
      ...Object.fromEntries(
        extendedFields.value.map((field: any) => [
          field.name, 
          registerForm[field.name as keyof typeof registerForm]
        ])
      )
    }
    
    const result = await store.dispatch('auth/register', registerData)
    
    if (result.success) {
      ElMessage.success('注册成功！请登录您的账号')
      router.push('/login')
    } else {
      ElMessage.error(result.message || '注册失败')
    }
  } catch (error) {
    console.error('注册错误:', error)
    ElMessage.error('注册过程中发生错误')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.register-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
  padding: var(--spacing-md);
}

.register-background {
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

.register-card {
  width: 100%;
  max-width: 600px;
  padding: var(--spacing-xl);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-large);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.register-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.register-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.register-form {
  .el-form-item {
    margin-bottom: var(--spacing-md);
  }
  
  .register-btn {
    width: 100%;
    height: 48px;
    font-size: var(--font-size-medium);
    font-weight: 600;
  }
}

.extended-fields {
  .el-divider {
    margin: var(--spacing-lg) 0 var(--spacing-md) 0;
  }
}

.terms-link {
  color: var(--color-primary);
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
}

.register-footer {
  text-align: center;
  margin-top: var(--spacing-lg);
}

.login-link {
  color: var(--color-primary);
  font-size: var(--font-size-small);
  transition: var(--transition-base);
  
  &:hover {
    color: var(--color-primary-light);
    text-decoration: underline;
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .register-card {
    margin: var(--spacing-sm);
    padding: var(--spacing-lg);
    max-height: 95vh;
  }
  
  .register-title {
    font-size: 24px;
  }
  
  .el-col {
    margin-bottom: var(--spacing-sm);
  }
}

@media (max-width: $breakpoint-sm) {
  .register-container {
    padding: var(--spacing-sm);
  }
  
  .register-card {
    padding: var(--spacing-md);
  }
  
  .el-row .el-col {
    span: 24 !important;
  }
}
</style>