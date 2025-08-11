<template>
  <div class="settings-container">
    <div class="header">
      <h1>设置</h1>
      <p class="subtitle">个人偏好和账户设置</p>
    </div>
    
    <div class="content">
      <div class="settings-sections">
        <!-- 账户设置 -->
        <div class="settings-section">
          <h2>账户设置</h2>
          <div class="setting-item" @click="navigateTo('/profile')">
            <div class="setting-icon">👤</div>
            <div class="setting-info">
              <h3>个人资料</h3>
              <p>编辑个人信息和头像</p>
            </div>
            <div class="setting-arrow">›</div>
          </div>
          
          <div class="setting-item" @click="showChangePassword = true">
            <div class="setting-icon">🔒</div>
            <div class="setting-info">
              <h3>修改密码</h3>
              <p>更改登录密码</p>
            </div>
            <div class="setting-arrow">›</div>
          </div>
        </div>
        
        <!-- 学习设置 -->
        <div class="settings-section">
          <h2>学习设置</h2>
          <div class="setting-item" @click="navigateTo('/learning-modes')">
            <div class="setting-icon">📚</div>
            <div class="setting-info">
              <h3>学习模式</h3>
              <p>选择和配置学习模式</p>
            </div>
            <div class="setting-arrow">›</div>
          </div>
          
          <div class="setting-item">
            <div class="setting-icon">🎯</div>
            <div class="setting-info">
              <h3>学习目标</h3>
              <p>设置每日学习目标</p>
            </div>
            <div class="setting-control">
              <select v-model="dailyGoal">
                <option value="10">10个单词/天</option>
                <option value="20">20个单词/天</option>
                <option value="30">30个单词/天</option>
                <option value="50">50个单词/天</option>
              </select>
            </div>
          </div>
          
          <div class="setting-item">
            <div class="setting-icon">🔔</div>
            <div class="setting-info">
              <h3>学习提醒</h3>
              <p>开启学习提醒通知</p>
            </div>
            <div class="setting-control">
              <label class="switch">
                <input type="checkbox" v-model="notifications">
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- 显示设置 -->
        <div class="settings-section">
          <h2>显示设置</h2>
          <div class="setting-item">
            <div class="setting-icon">🌙</div>
            <div class="setting-info">
              <h3>深色模式</h3>
              <p>切换到深色主题</p>
            </div>
            <div class="setting-control">
              <label class="switch">
                <input type="checkbox" v-model="darkMode">
                <span class="slider"></span>
              </label>
            </div>
          </div>
          
          <div class="setting-item">
            <div class="setting-icon">🔤</div>
            <div class="setting-info">
              <h3>字体大小</h3>
              <p>调整界面字体大小</p>
            </div>
            <div class="setting-control">
              <select v-model="fontSize">
                <option value="small">小</option>
                <option value="medium">中</option>
                <option value="large">大</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- 其他设置 -->
        <div class="settings-section">
          <h2>其他</h2>
          <div class="setting-item" @click="showAbout = true">
            <div class="setting-icon">ℹ️</div>
            <div class="setting-info">
              <h3>关于应用</h3>
              <p>版本信息和帮助</p>
            </div>
            <div class="setting-arrow">›</div>
          </div>
          
          <div class="setting-item" @click="logout">
            <div class="setting-icon">🚪</div>
            <div class="setting-info">
              <h3>退出登录</h3>
              <p>安全退出当前账户</p>
            </div>
            <div class="setting-arrow">›</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="modal-overlay" @click="showChangePassword = false">
      <div class="modal" @click.stop>
        <h3>修改密码</h3>
        <form @submit.prevent="changePassword">
          <input type="password" v-model="oldPassword" placeholder="当前密码" required>
          <input type="password" v-model="newPassword" placeholder="新密码" required>
          <input type="password" v-model="confirmPassword" placeholder="确认新密码" required>
          <div class="modal-buttons">
            <button type="button" @click="showChangePassword = false">取消</button>
            <button type="submit">确认</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 关于弹窗 -->
    <div v-if="showAbout" class="modal-overlay" @click="showAbout = false">
      <div class="modal" @click.stop>
        <h3>关于 Natural English</h3>
        <p>版本: 1.0.0</p>
        <p>一个智能的英语学习平台，帮助您高效学习英语单词。</p>
        <div class="modal-buttons">
          <button @click="showAbout = false">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      dailyGoal: '20',
      notifications: true,
      darkMode: false,
      fontSize: 'medium',
      showChangePassword: false,
      showAbout: false,
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  },
  mounted() {
    this.loadSettings()
  },
  methods: {
    navigateTo(path) {
      this.$router.push(path)
    },
    
    loadSettings() {
      // 从localStorage加载设置
      const settings = localStorage.getItem('userSettings')
      if (settings) {
        const parsed = JSON.parse(settings)
        this.dailyGoal = parsed.dailyGoal || '20'
        this.notifications = parsed.notifications !== false
        this.darkMode = parsed.darkMode || false
        this.fontSize = parsed.fontSize || 'medium'
      }
    },
    
    saveSettings() {
      const settings = {
        dailyGoal: this.dailyGoal,
        notifications: this.notifications,
        darkMode: this.darkMode,
        fontSize: this.fontSize
      }
      localStorage.setItem('userSettings', JSON.stringify(settings))
    },
    
    async changePassword() {
      if (this.newPassword !== this.confirmPassword) {
        alert('新密码和确认密码不一致')
        return
      }
      
      try {
        // 这里应该调用API修改密码
        alert('密码修改成功')
        this.showChangePassword = false
        this.oldPassword = ''
        this.newPassword = ''
        this.confirmPassword = ''
      } catch (error) {
        alert('密码修改失败: ' + error.message)
      }
    },
    
    logout() {
      if (confirm('确定要退出登录吗？')) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        this.$router.push('/login')
      }
    }
  },
  
  watch: {
    dailyGoal() { this.saveSettings() },
    notifications() { this.saveSettings() },
    darkMode() { this.saveSettings() },
    fontSize() { this.saveSettings() }
  }
}
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  padding: 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 30px;
  padding-top: 20px;
}

.header h1 {
  font-size: 2.2rem;
  margin-bottom: 8px;
  font-weight: 700;
}

.subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.content {
  max-width: 800px;
  margin: 0 auto;
}

.settings-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.settings-section h2 {
  font-size: 1.3rem;
  margin-bottom: 15px;
  color: #333;
  font-weight: 600;
}

.setting-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:hover {
  background-color: rgba(116, 185, 255, 0.05);
  border-radius: 8px;
  margin: 0 -10px;
  padding: 15px 10px;
}

.setting-icon {
  font-size: 1.5rem;
  margin-right: 15px;
  width: 30px;
  text-align: center;
}

.setting-info {
  flex: 1;
}

.setting-info h3 {
  font-size: 1rem;
  margin: 0 0 4px 0;
  color: #333;
  font-weight: 500;
}

.setting-info p {
  font-size: 0.85rem;
  margin: 0;
  color: #666;
}

.setting-arrow {
  font-size: 1.2rem;
  color: #999;
  margin-left: 10px;
}

.setting-control {
  margin-left: 10px;
}

.setting-control select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
  font-size: 0.9rem;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #74b9ff;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 15px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.modal input {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.modal-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.modal-buttons button[type="button"] {
  background: #f5f5f5;
  color: #666;
}

.modal-buttons button[type="submit"],
.modal-buttons button:not([type]) {
  background: #74b9ff;
  color: white;
}

.modal-buttons button:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 1.8rem;
  }
  
  .settings-section {
    padding: 15px;
  }
  
  .setting-item {
    padding: 12px 0;
  }
  
  .setting-icon {
    font-size: 1.3rem;
    margin-right: 12px;
  }
}
</style>