<template>
  <div class="test-container">
    <h1>API测试页面</h1>
    
    <div class="test-section">
      <h2>角色列表测试</h2>
      <button @click="testRoles" :disabled="loading">测试角色API</button>
      <div v-if="rolesResult" class="result">
        <h3>角色列表结果：</h3>
        <pre>{{ JSON.stringify(rolesResult, null, 2) }}</pre>
      </div>
    </div>
    
    <div class="test-section">
      <h2>角色增项测试</h2>
      <select v-model="selectedRole" @change="testRoleExtensions">
        <option value="">选择角色</option>
        <option value="student">学生</option>
        <option value="parent">家长</option>
        <option value="teacher">老师</option>
        <option value="admin">管理员</option>
      </select>
      <div v-if="extensionsResult" class="result">
        <h3>{{ selectedRole }} 角色增项结果：</h3>
        <pre>{{ JSON.stringify(extensionsResult, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestAPI',
  data() {
    return {
      loading: false,
      rolesResult: null,
      extensionsResult: null,
      selectedRole: ''
    }
  },
  methods: {
    async testRoles() {
      this.loading = true
      try {
        const response = await fetch('http://127.0.0.1:8002/accounts/api/auth/roles/')
        const data = await response.json()
        this.rolesResult = data
        console.log('角色API结果:', data)
      } catch (error) {
        console.error('角色API错误:', error)
        this.rolesResult = { error: error.message }
      } finally {
        this.loading = false
      }
    },
    
    async testRoleExtensions() {
      if (!this.selectedRole) {
        this.extensionsResult = null
        return
      }
      
      try {
        const response = await fetch(`http://127.0.0.1:8002/accounts/api/auth/role-extensions/?role=${this.selectedRole}`)
        const data = await response.json()
        this.extensionsResult = data
        console.log(`${this.selectedRole} 角色增项结果:`, data)
      } catch (error) {
        console.error('角色增项API错误:', error)
        this.extensionsResult = { error: error.message }
      }
    }
  }
}
</script>

<style scoped>
.test-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.result {
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
}

button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 10px;
}
</style>