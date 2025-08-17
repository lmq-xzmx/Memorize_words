<template>
  <div class="login-test-container">
    <h2>登录测试页面</h2>
    
    <div class="login-form">
      <div class="form-group">
        <label>用户名:</label>
        <input v-model="loginForm.username" type="text" placeholder="请输入用户名" />
      </div>
      
      <div class="form-group">
        <label>密码:</label>
        <input v-model="loginForm.password" type="password" placeholder="请输入密码" />
      </div>
      
      <button @click="testLogin" :disabled="isLoading">{{ isLoading ? '登录中...' : '测试登录' }}</button>
    </div>
    
    <div class="test-results">
      <h3>测试结果:</h3>
      <div class="result-item">
        <strong>登录状态:</strong> 
        <span :class="loginResult.success ? 'success' : 'error'">
          {{ loginResult.message }}
        </span>
      </div>
      
      <div v-if="loginResult.token" class="result-item">
        <strong>Token:</strong> {{ loginResult.token.substring(0, 20) }}...
      </div>
      
      <div v-if="loginResult.user" class="result-item">
        <strong>用户信息:</strong> {{ JSON.stringify(loginResult.user, null, 2) }}
      </div>
      
      <div class="result-item">
        <strong>认证验证:</strong> 
        <span :class="authVerifyResult.success ? 'success' : 'error'">
          {{ authVerifyResult.message }}
        </span>
      </div>
      
      <div class="result-item">
        <strong>用户信息获取:</strong> 
        <span :class="userInfoResult.success ? 'success' : 'error'">
          {{ userInfoResult.message }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../utils/api'

export default {
  name: 'LoginTest',
  data() {
    return {
      isLoading: false,
      loginForm: {
        username: 'xzmx',
        password: '123456'
      },
      loginResult: {
        success: false,
        message: '未测试',
        token: null,
        user: null
      },
      authVerifyResult: {
        success: false,
        message: '未测试'
      },
      userInfoResult: {
        success: false,
        message: '未测试'
      }
    }
  },
  methods: {
    async testLogin() {
      this.isLoading = true
      
      try {
        // 测试登录
        console.log('开始测试登录...')
        const loginResponse = await authAPI.login(this.loginForm.username, this.loginForm.password)
        
        this.loginResult = {
          success: true,
          message: '登录成功',
          token: loginResponse.token,
          user: loginResponse
        }
        
        // 保存token到localStorage
        if (loginResponse.token) {
          localStorage.setItem('token', loginResponse.token)
        }
        
        // 测试认证验证
        await this.testAuthVerify()
        
        // 测试用户信息获取
        await this.testUserInfo()
        
      } catch (error) {
        console.error('登录测试失败:', error)
        this.loginResult = {
          success: false,
          message: `登录失败: ${error.message || error}`,
          token: null,
          user: null
        }
      } finally {
        this.isLoading = false
      }
    },
    
    async testAuthVerify() {
      try {
        const response = await fetch('http://127.0.0.1:8000/accounts/api/auth/verify/', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        const data = await response.json()
        
        this.authVerifyResult = {
          success: response.ok && data.authenticated,
          message: data.authenticated ? '认证验证成功' : '认证验证失败'
        }
      } catch (error) {
        this.authVerifyResult = {
          success: false,
          message: `认证验证错误: ${error.message}`
        }
      }
    },
    
    async testUserInfo() {
      try {
        const response = await fetch('http://127.0.0.1:8000/accounts/api/users/current/', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        const data = await response.json()
        
        this.userInfoResult = {
          success: response.ok && data.success,
          message: data.success ? '用户信息获取成功' : '用户信息获取失败'
        }
      } catch (error) {
        this.userInfoResult = {
          success: false,
          message: `用户信息获取错误: ${error.message}`
        }
      }
    }
  }
}
</script>

