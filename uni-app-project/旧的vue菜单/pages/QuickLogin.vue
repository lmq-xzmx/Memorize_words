<template>
  <div class="quick-login-container">
    <div class="login-card">
      <h2>快速登录测试</h2>
      <div class="login-form">
        <div class="form-group">
          <label>用户名:</label>
          <input 
            v-model="loginForm.username" 
            type="text" 
            placeholder="请输入用户名"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label>密码:</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label>角色:</label>
          <select v-model="loginForm.role" class="form-select">
            <option value="student">学生</option>
            <option value="teacher">教师</option>
            <option value="admin">管理员</option>
            <option value="dean">教导主任</option>
            <option value="academic_director">教务主任</option>
            <option value="research_leader">教研组长</option>
            <option value="parent">家长</option>
          </select>
        </div>
        <button @click="quickLogin" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '快速登录' }}
        </button>
        <button @click="testLogin" class="test-btn" :disabled="loading">
          {{ loading ? '测试中...' : '测试登录状态' }}
        </button>
      </div>
      
      <div class="status-info">
        <h3>当前状态:</h3>
        <p><strong>认证状态:</strong> {{ authStatus ? '已认证' : '未认证' }}</p>
        <p><strong>用户信息:</strong> {{ userInfo ? JSON.stringify(userInfo) : '无' }}</p>
        <p><strong>Token:</strong> {{ token ? '已设置' : '未设置' }}</p>
      </div>
      
      <div class="menu-test">
        <h3>菜单测试:</h3>
        <button @click="testMenus" class="test-menu-btn">测试获取菜单</button>
        <div v-if="menuData" class="menu-result">
          <h4>菜单数据:</h4>
          <pre>{{ JSON.stringify(menuData, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI, menuAPI } from '../utils/api.js'
import { isAuthenticated, getCurrentUser, clearAuth } from '../utils/permission.js'
import { menuManager } from '../utils/menuManager.js'

export default {
  name: 'QuickLogin',
  data() {
    return {
      loading: false,
      loginForm: {
        username: 'testuser',
        password: 'testpass123',
        role: 'student'
      },
      authStatus: false,
      userInfo: null,
      token: null,
      menuData: null
    }
  },
  mounted() {
    this.checkStatus()
  },
  methods: {
    checkStatus() {
      this.authStatus = isAuthenticated()
      this.userInfo = getCurrentUser()
      this.token = localStorage.getItem('token')
    },
    
    async quickLogin() {
      this.loading = true
      try {
        // 模拟登录 - 直接设置用户信息和token
        const mockUser = {
          id: 1,
          username: this.loginForm.username,
          role: this.loginForm.role,
          email: `${this.loginForm.username}@test.com`,
          is_active: true
        }
        
        const mockToken = 'mock-jwt-token-' + Date.now()
        
        // 设置到localStorage
        localStorage.setItem('user', JSON.stringify(mockUser))
        localStorage.setItem('token', mockToken)
        
        // 更新状态
        this.checkStatus()
        
        this.$message?.success('快速登录成功！')
        
        // 清除菜单缓存
        menuManager.clearCache()
        
      } catch (error) {
        console.error('快速登录失败:', error)
        this.$message?.error('快速登录失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    async testLogin() {
      this.loading = true
      try {
        // 尝试真实登录
        const response = await authAPI.login({
          username: this.loginForm.username,
          password: this.loginForm.password
        })
        
        if (response.data) {
          localStorage.setItem('token', response.data.token)
          localStorage.setItem('user', JSON.stringify(response.data.user))
          this.checkStatus()
          this.$message?.success('真实登录成功！')
        }
      } catch (error) {
        console.error('真实登录失败:', error)
        this.$message?.error('真实登录失败，使用快速登录代替')
        await this.quickLogin()
      } finally {
        this.loading = false
      }
    },
    
    async testMenus() {
      try {
        console.log('开始测试菜单获取...')
        
        // 检查认证状态
        console.log('认证状态:', isAuthenticated())
        console.log('用户信息:', getCurrentUser())
        
        // 测试菜单API
        const menuResponse = await menuAPI.getUserMenus()
        console.log('菜单API响应:', menuResponse)
        
        // 测试菜单管理器
        const managerMenus = await menuManager.getUserMenus()
        console.log('菜单管理器响应:', managerMenus)
        
        this.menuData = {
          apiResponse: menuResponse,
          managerResponse: managerMenus
        }
        
      } catch (error) {
        console.error('测试菜单失败:', error)
        this.menuData = {
          error: error.message,
          stack: error.stack
        }
      }
    },
    
    logout() {
      clearAuth()
      this.checkStatus()
      this.menuData = null
      this.$message?.success('已退出登录')
    }
  }
}
</script>

<style scoped>
.quick-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.login-card h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

.form-input, .form-select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #667eea;
}

.login-btn, .test-btn, .test-menu-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 10px;
}

.login-btn {
  background: #667eea;
  color: white;
}

.login-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.test-btn {
  background: #28a745;
  color: white;
}

.test-btn:hover:not(:disabled) {
  background: #218838;
}

.test-menu-btn {
  background: #17a2b8;
  color: white;
}

.test-menu-btn:hover:not(:disabled) {
  background: #138496;
}

.login-btn:disabled, .test-btn:disabled, .test-menu-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.status-info {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.status-info h3 {
  margin-top: 0;
  color: #333;
}

.status-info p {
  margin: 10px 0;
  word-break: break-all;
}

.menu-test {
  margin-top: 20px;
  padding: 20px;
  background: #e9ecef;
  border-radius: 6px;
}

.menu-test h3 {
  margin-top: 0;
  color: #333;
}

.menu-result {
  margin-top: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.menu-result pre {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
}
</style>