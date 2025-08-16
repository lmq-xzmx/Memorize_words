<template>
  <div class="register-container">
    <!-- 装饰性背景元素 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
      <div class="circle circle-4"></div>
    </div>
    
    <div class="register-card">
      <div class="logo-section">
        <div class="logo-icon">🚀</div>
        <h1 class="logo">Natural English</h1>
        <p class="subtitle">创建您的学习账号，开启英语学习新体验</p>
      </div>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-row">
          <div class="form-group">
            <label for="username">用户名 *</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              required
              :disabled="loading"
            />
            <div v-if="errors.username" class="field-error">
              {{ errors.username[0] }}
            </div>
          </div>
          
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱（选填）"
              :disabled="loading"
            />
            <div v-if="errors.email" class="field-error">
              {{ errors.email[0] }}
            </div>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="real_name">真实姓名</label>
            <input
              id="real_name"
              v-model="form.real_name"
              type="text"
              placeholder="请输入真实姓名（选填）"
              :disabled="loading"
            />
          </div>
          
          <div class="form-group">
            <label for="phone">手机号 *</label>
            <input
              id="phone"
              v-model="form.phone"
              type="tel"
              placeholder="请输入手机号"
              required
              :disabled="loading"
            />
            <div v-if="errors.phone" class="field-error">
              {{ errors.phone[0] }}
            </div>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="nickname">网名</label>
            <input
              id="nickname"
              v-model="form.nickname"
              type="text"
              placeholder="请输入网名（选填，不可与他人相同）"
              :disabled="loading"
            />
            <div v-if="errors.nickname" class="field-error">
              {{ errors.nickname[0] }}
            </div>
          </div>
          
          <div class="form-group">
            <label for="role">角色 *</label>
            <select id="role" v-model="form.role" required :disabled="loading || loadingRoles">
              <option value="">{{ loadingRoles ? '加载中...' : '请选择角色' }}</option>
              <option
                v-for="role in roles"
                :key="role.value"
                :value="role.value"
              >
                {{ role.label }}
              </option>
            </select>
            <div v-if="errors.role" class="field-error">
              {{ errors.role[0] }}
            </div>
          </div>
        </div>
        
        <!-- 动态角色增项字段 -->
        <div v-if="roleExtensions.length > 0" class="extension-fields">
          <div class="extension-header">
            <h4>{{ form.role === 'student' ? '学生' : form.role === 'parent' ? '家长' : form.role === 'teacher' ? '老师' : '管理员' }}专属信息</h4>
            <div v-if="loadingExtensions" class="loading-text">加载中...</div>
          </div>
          
          <!-- 管理员申请提示 -->
          <div v-if="form.role === 'admin'" class="admin-notice">
            申请管理员时，需等待后台审批
          </div>
          
          <div v-for="extension in roleExtensions" :key="extension.field_name" class="form-row">
            <div class="form-group">
              <label :for="extension.field_name">
                {{ extension.field_label }}
                <span v-if="extension.is_required" class="required">*</span>
              </label>
              
              <!-- 文本输入框 -->
              <input
                v-if="extension.field_type === 'text'"
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                type="text"
                :placeholder="extension.help_text || `请输入${extension.field_label}`"
                :required="extension.is_required"
                :disabled="loading"
              />
              
              <!-- 数字输入框 -->
              <input
                v-else-if="extension.field_type === 'number'"
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                type="number"
                :placeholder="extension.help_text || `请输入${extension.field_label}`"
                :required="extension.is_required"
                :disabled="loading"
              />
              
              <!-- 邮箱输入框 -->
              <input
                v-else-if="extension.field_type === 'email'"
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                type="email"
                :placeholder="extension.help_text || `请输入${extension.field_label}`"
                :required="extension.is_required"
                :disabled="loading"
              />
              
              <!-- 电话输入框 -->
              <input
                v-else-if="extension.field_type === 'phone'"
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                type="tel"
                :placeholder="extension.help_text || `请输入${extension.field_label}`"
                :required="extension.is_required"
                :disabled="loading"
              />
              
              <!-- 选择框 -->
              <select
                v-else-if="extension.field_type === 'choice'"
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                :required="extension.is_required"
                :disabled="loading"
              >
                <option value="">请选择{{ extension.field_label }}</option>
                <option
                  v-for="choice in extension.choices"
                  :key="choice[0]"
                  :value="choice[0]"
                >
                  {{ choice[1] }}
                </option>
              </select>
              
              <!-- 多行文本框 -->
              <textarea
                v-else-if="extension.field_type === 'textarea'"
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                :placeholder="extension.help_text || `请输入${extension.field_label}`"
                :required="extension.is_required"
                :disabled="loading"
                rows="3"
              ></textarea>
              
              <!-- 日期输入框 -->
              <input
                v-else-if="extension.field_type === 'date'"
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                type="date"
                :required="extension.is_required"
                :disabled="loading"
              />
              
              <!-- 默认文本输入框 -->
              <input
                v-else
                :id="extension.field_name"
                v-model="extensionData[extension.field_name]"
                type="text"
                :placeholder="extension.help_text || `请输入${extension.field_label}`"
                :required="extension.is_required"
                :disabled="loading"
              />
              
              <!-- 帮助文本 -->
              <div v-if="extension.help_text" class="help-text">
                {{ extension.help_text }}
              </div>
              
              <!-- 错误信息 -->
              <div v-if="errors[`ext_${extension.field_name}`]" class="field-error">
                {{ errors[`ext_${extension.field_name}`][0] }}
              </div>
            </div>
            
            <div class="form-group">
              <!-- 占位空间 -->
            </div>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="grade_level">年级</label>
            <input
              id="grade_level"
              v-model="form.grade_level"
              type="text"
              placeholder="如：高一、初二"
              :disabled="loading"
            />
          </div>
          
          <div class="form-group">
            <!-- 占位空间 -->
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="school">学校</label>
            <input
              id="school"
              v-model="form.school"
              type="text"
              placeholder="请输入学校名称"
              :disabled="loading"
            />
          </div>
          
          <div class="form-group">
            <label for="class_name">班级</label>
            <input
              id="class_name"
              v-model="form.class_name"
              type="text"
              placeholder="如：1班、A班"
              :disabled="loading"
            />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="password">密码 *</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="至少8位，包含字母和数字"
              required
              :disabled="loading"
            />
          </div>
          
          <div class="form-group">
            <label for="confirm_password">确认密码 *</label>
            <input
              id="confirm_password"
              v-model="form.confirm_password"
              type="password"
              placeholder="请再次输入密码"
              required
              :disabled="loading"
            />
            <div v-if="errors.confirm_password" class="field-error">
              {{ errors.confirm_password[0] }}
            </div>
          </div>
        </div>
        
        <div v-if="generalError" class="error-message">
          {{ generalError }}
        </div>
        
        <button type="submit" class="register-btn" :disabled="loading">
          <span v-if="loading">注册中...</span>
          <span v-else>立即注册</span>
        </button>
      </form>
      
      <div class="login-link">
        <p>已有账号？ <router-link to="/login">立即登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../utils/api.js'
import { buildApiUrl, API_ENDPOINTS } from '../config/apiConfig.js'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        username: '',
        email: '',
        real_name: '',
        phone: '',
        nickname: '',
        role: '',
        grade_level: '',
        school: '',
        class_name: '',
        password: '',
        confirm_password: ''
      },
      roles: [], // 角色列表
      roleExtensions: [], // 角色增项字段配置
      extensionData: {}, // 增项字段数据
      loading: false,
      loadingRoles: false,
      loadingExtensions: false,
      errors: {},
      generalError: ''
    }
  },
  mounted() {
    this.loadRoles()
  },
  watch: {
    'form.role': {
      handler(newRole) {
        if (newRole) {
          this.loadRoleExtensions(newRole)
        } else {
          this.roleExtensions = []
          this.extensionData = {}
        }
      },
      immediate: false
    }
  },
  methods: {
    async loadRoles() {
      // 检查缓存
      const cachedRoles = localStorage.getItem('cached_roles')
      const cacheTime = localStorage.getItem('roles_cache_time')
      const now = Date.now()
      
      // 如果缓存存在且未过期（5分钟内），直接使用缓存
      if (cachedRoles && cacheTime && (now - parseInt(cacheTime)) < 5 * 60 * 1000) {
        this.roles = JSON.parse(cachedRoles)
        return
      }
      
      this.loadingRoles = true
      try {
        const response = await fetch(buildApiUrl(API_ENDPOINTS.AUTH.ROLES))
        if (response.ok) {
          const data = await response.json()
          // 转换API返回的数组格式 [value, label] 为对象格式 {value, label}
          this.roles = (data.roles || []).map(role => ({
            value: role[0],
            label: role[1]
          })).filter(role => role.value !== '') // 过滤掉空选项
          
          // 缓存角色列表
          localStorage.setItem('cached_roles', JSON.stringify(this.roles))
          localStorage.setItem('roles_cache_time', now.toString())
        } else {
          console.error('加载角色列表失败')
          this.setDefaultRoles()
        }
      } catch (error) {
        console.error('加载角色列表失败:', error)
        this.setDefaultRoles()
      } finally {
        this.loadingRoles = false
      }
    },
    
    setDefaultRoles() {
      // 如果API失败，使用默认角色列表作为备选
      this.roles = [
        { value: 'student', label: '学生' },
        { value: 'parent', label: '家长' },
        { value: 'teacher', label: '自由老师' },
        { value: 'admin', label: '管理员' }
      ]
    },
    
    async loadRoleExtensions(role) {
      // 检查缓存
      const cacheKey = `role_extensions_${role}`
      const cachedExtensions = localStorage.getItem(cacheKey)
      const cacheTimeKey = `${cacheKey}_time`
      const cacheTime = localStorage.getItem(cacheTimeKey)
      const now = Date.now()
      
      // 如果缓存存在且未过期（5分钟内），直接使用缓存
      if (cachedExtensions && cacheTime && (now - parseInt(cacheTime)) < 5 * 60 * 1000) {
        this.roleExtensions = JSON.parse(cachedExtensions)
        this.initializeExtensionData()
        return
      }
      
      this.loadingExtensions = true
      try {
        const response = await fetch(buildApiUrl(`${API_ENDPOINTS.AUTH.ROLE_EXTENSIONS}?role=${role}`))
        if (response.ok) {
          const data = await response.json()
          this.roleExtensions = data.extensions || []
          
          // 缓存角色增项配置
          localStorage.setItem(cacheKey, JSON.stringify(this.roleExtensions))
          localStorage.setItem(cacheTimeKey, now.toString())
          
          this.initializeExtensionData()
        } else {
          console.error('加载角色增项失败')
          this.roleExtensions = []
        }
      } catch (error) {
        console.error('加载角色增项失败:', error)
        this.roleExtensions = []
      } finally {
        this.loadingExtensions = false
      }
    },
    
    initializeExtensionData() {
      // 初始化增项数据
      this.extensionData = {}
      this.roleExtensions.forEach(ext => {
        this.extensionData[ext.field_name] = ext.default_value || ''
      })
    },
    
    async handleRegister() {
      this.loading = true
      this.errors = {}
      this.generalError = ''
      
      // 前端验证
      if (this.form.password !== this.form.confirm_password) {
        this.errors.confirm_password = ['两次输入的密码不一致']
        this.loading = false
        return
      }
      
      try {
        // 准备注册数据
        const registerData = { ...this.form }
        
        // 如果有角色增项，使用动态注册接口
        if (this.roleExtensions.length > 0) {
          // 添加增项数据到注册数据中
          this.roleExtensions.forEach(ext => {
            const fieldName = `ext_${ext.field_name}`
            registerData[fieldName] = this.extensionData[ext.field_name] || ''
          })
          
          // 使用动态注册接口
          const response = await fetch(buildApiUrl(API_ENDPOINTS.AUTH.REGISTER_WITH_EXTENSIONS), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(registerData)
          })
          
          if (response.ok) {
            const data = await response.json()
            // 保存用户信息和Token
            localStorage.setItem('token', data.token)
            localStorage.setItem('user', JSON.stringify(data.user))
            // 跳转到仪表板
            this.$router.push('/dashboard')
          } else {
            const errorData = await response.json()
            throw errorData
          }
        } else {
          // 使用普通注册接口
          const response = await authAPI.register(this.form)
          
          // 保存用户信息和Token
          localStorage.setItem('token', response.token)
          localStorage.setItem('user', JSON.stringify(response.user))
          
          // 跳转到仪表板
          this.$router.push('/dashboard')
        }
      } catch (error) {
        console.error('注册失败:', error)
        
        if (typeof error === 'object' && error !== null) {
          // 处理字段级错误
          this.errors = error
        } else {
          this.generalError = error || '注册失败，请稍后重试'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

