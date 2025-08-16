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
/* 设置页面主容器 */
.settings-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  position: relative;
  overflow-x: hidden;
}

.settings-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

/* 页面头部 */
.header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  animation: slideInDown 0.8s ease-out;
}

.subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  animation: slideInUp 0.8s ease-out 0.2s both;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 内容区域 */
.content {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.settings-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 设置区块 */
.settings-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 设置项 */
.setting-item {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  margin: 0 -1rem;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.setting-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.setting-item:hover {
  background: rgba(102, 126, 234, 0.05);
  transform: translateX(5px);
}

.setting-item:hover::before {
  left: 100%;
}

.setting-icon {
  font-size: 2rem;
  margin-right: 1rem;
  width: 50px;
  text-align: center;
  filter: grayscale(0.3);
  transition: filter 0.3s ease;
}

.setting-item:hover .setting-icon {
  filter: grayscale(0);
}

.setting-info {
  flex: 1;
}

.setting-info h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.3rem 0;
}

.setting-info p {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
  line-height: 1.4;
}

.setting-arrow {
  font-size: 1.5rem;
  color: #999;
  transition: all 0.3s ease;
}

.setting-item:hover .setting-arrow {
  color: #667eea;
  transform: translateX(5px);
}

/* 设置控件 */
.setting-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.setting-control input[type="number"] {
  width: 80px;
  padding: 0.5rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  text-align: center;
  transition: border-color 0.3s ease;
}

.setting-control input[type="number"]:focus {
  outline: none;
  border-color: #667eea;
}

.setting-control select {
  padding: 0.5rem 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.setting-control select:focus {
  outline: none;
  border-color: #667eea;
}

/* 开关控件 */
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
  transition: 0.4s;
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
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

input:checked + .slider:before {
  transform: translateX(26px);
}

/* 修改密码弹窗 */
.password-modal {
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
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.password-content {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  animation: slideInScale 0.3s ease;
}

@keyframes slideInScale {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.password-content h3 {
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 1.5rem 0;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  flex: 1;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
}

.btn-secondary:hover {
  background: #e9ecef;
  color: #333;
}

.btn-danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 1rem;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .settings-section {
    padding: 1.5rem;
  }
  
  .setting-item {
    padding: 1rem;
    margin: 0 -0.5rem;
  }
  
  .setting-icon {
    font-size: 1.5rem;
    width: 40px;
  }
  
  .setting-info h3 {
    font-size: 1rem;
  }
  
  .setting-info p {
    font-size: 0.85rem;
  }
  
  .setting-control {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .settings-container {
    padding: 0.5rem;
  }
  
  .header {
    margin-bottom: 2rem;
  }
  
  .header h1 {
    font-size: 1.8rem;
  }
  
  .settings-section {
    padding: 1rem;
  }
  
  .setting-item {
    padding: 0.8rem;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .setting-icon {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
  
  .setting-arrow {
    display: none;
  }
  
  .password-content {
    padding: 1.5rem;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .settings-section,
  .password-content {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .settings-section h2 {
    color: #f0f0f0;
  }
  
  .setting-info h3 {
    color: #f0f0f0;
  }
  
  .setting-info p {
    color: #b0b0b0;
  }
  
  .form-group label {
    color: #e0e0e0;
  }
  
  .form-group input,
  .setting-control input,
  .setting-control select {
    background: #333;
    color: #e0e0e0;
    border-color: #555;
  }
  
  .btn-secondary {
    background: #333;
    color: #e0e0e0;
    border-color: #555;
  }
  
  .btn-secondary:hover {
    background: #444;
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .settings-container {
    background: #000;
  }
  
  .settings-section,
  .password-content {
    background: #fff;
    border: 2px solid #000;
  }
  
  .header h1,
  .subtitle {
    color: #fff;
    text-shadow: 2px 2px 4px #000;
  }
  
  .setting-info h3,
  .setting-info p {
    color: #000;
  }
}

/* 焦点状态 */
.setting-item:focus,
.btn:focus,
.form-group input:focus,
.setting-control input:focus,
.setting-control select:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .setting-item,
  .btn {
    min-height: 44px;
  }
  
  .setting-item:hover {
    transform: none;
  }
  
  .btn:hover {
    transform: none;
  }
}
</style>

