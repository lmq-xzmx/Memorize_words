<template>
  <div class="settings" v-permission="'profile.settings.view'">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>个人设置</h1>
      <p>管理你的账户信息和学习偏好</p>
    </div>

    <!-- 设置内容 -->
    <div class="settings-content">
      <!-- 个人信息 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>个人信息</h2>
          <p>更新你的基本信息</p>
        </div>
        
        <div class="settings-card">
          <form @submit.prevent="updateProfile">
            <div class="form-row">
              <div class="form-group">
                <label>头像</label>
                <div class="avatar-upload">
                  <div class="avatar-preview">
                    <img :src="profileForm.avatar || '/default-avatar.png'" 
                         alt="头像" 
                         class="avatar-image">
                    <div class="avatar-overlay">
                      <i class="fas fa-camera"></i>
                    </div>
                  </div>
                  <input type="file" 
                         ref="avatarInput" 
                         @change="handleAvatarChange" 
                         accept="image/*" 
                         class="avatar-input">
                  <button type="button" 
                          @click="avatarInput?.click()" 
                          class="upload-btn">
                    更换头像
                  </button>
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" 
                       id="username" 
                       v-model="profileForm.username" 
                       class="form-input"
                       placeholder="请输入用户名">
              </div>
              <div class="form-group">
                <label for="email">邮箱</label>
                <input type="email" 
                       id="email" 
                       v-model="profileForm.email" 
                       class="form-input"
                       placeholder="请输入邮箱">
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="phone">手机号</label>
                <input type="tel" 
                       id="phone" 
                       v-model="profileForm.phone" 
                       class="form-input"
                       placeholder="请输入手机号">
              </div>
              <div class="form-group">
                <label for="birthday">生日</label>
                <input type="date" 
                       id="birthday" 
                       v-model="profileForm.birthday" 
                       class="form-input">
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group full-width">
                <label for="bio">个人简介</label>
                <textarea id="bio" 
                          v-model="profileForm.bio" 
                          class="form-textarea"
                          placeholder="介绍一下自己吧..."
                          rows="3">
                </textarea>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="submit" class="btn-primary">
                <i class="fas fa-save"></i>
                保存更改
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 安全设置 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>安全设置</h2>
          <p>管理你的账户安全</p>
        </div>
        
        <div class="settings-card">
          <!-- 修改密码 -->
          <div class="security-item">
            <div class="security-info">
              <h3>修改密码</h3>
              <p>定期更换密码以保护账户安全</p>
            </div>
            <button @click="showPasswordModal = true" class="btn-secondary">
              修改密码
            </button>
          </div>
          
          <!-- 两步验证 -->
          <div class="security-item">
            <div class="security-info">
              <h3>两步验证</h3>
              <p>为账户添加额外的安全保护</p>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" 
                     id="twoFactor" 
                     v-model="securitySettings.twoFactorEnabled">
              <label for="twoFactor" class="toggle-label"></label>
            </div>
          </div>
          
          <!-- 登录通知 -->
          <div class="security-item">
            <div class="security-info">
              <h3>登录通知</h3>
              <p>新设备登录时发送邮件通知</p>
            </div>
            <div class="toggle-switch">
              <input type="checkbox" 
                     id="loginNotification" 
                     v-model="securitySettings.loginNotification">
              <label for="loginNotification" class="toggle-label"></label>
            </div>
          </div>
        </div>
      </div>

      <!-- 学习偏好 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>学习偏好</h2>
          <p>个性化你的学习体验</p>
        </div>
        
        <div class="settings-card">
          <div class="preference-item">
            <label>每日学习目标</label>
            <div class="goal-selector">
              <button v-for="goal in dailyGoals" 
                      :key="goal.value"
                      :class="{ active: learningPreferences.dailyGoal === goal.value }"
                      @click="learningPreferences.dailyGoal = goal.value"
                      class="goal-btn">
                {{ goal.label }}
              </button>
            </div>
          </div>
          
          <div class="preference-item">
            <label>学习提醒</label>
            <div class="reminder-settings">
              <div class="toggle-switch">
                <input type="checkbox" 
                       id="dailyReminder" 
                       v-model="learningPreferences.dailyReminder">
                <label for="dailyReminder" class="toggle-label"></label>
              </div>
              <div class="reminder-time" v-if="learningPreferences.dailyReminder">
                <input type="time" 
                       v-model="learningPreferences.reminderTime" 
                       class="time-input">
              </div>
            </div>
          </div>
          
          <div class="preference-item">
            <label>难度偏好</label>
            <select v-model="learningPreferences.difficulty" class="form-select">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
              <option value="adaptive">自适应</option>
            </select>
          </div>
          
          <div class="preference-item">
            <label>语音播放速度</label>
            <div class="speed-slider">
              <input type="range" 
                     v-model="learningPreferences.speechSpeed" 
                     min="0.5" 
                     max="2" 
                     step="0.1" 
                     class="slider">
              <span class="speed-value">{{ learningPreferences.speechSpeed }}x</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 通知设置 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>通知设置</h2>
          <p>管理你接收的通知类型</p>
        </div>
        
        <div class="settings-card">
          <div class="notification-item" v-for="notification in notificationSettings" :key="notification.key">
            <div class="notification-info">
              <h3>{{ notification.title }}</h3>
              <p>{{ notification.description }}</p>
            </div>
            <div class="notification-controls">
              <div class="toggle-switch">
                <input type="checkbox" 
                       :id="notification.key" 
                       v-model="notification.enabled">
                <label :for="notification.key" class="toggle-label"></label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据管理 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>数据管理</h2>
          <p>管理你的学习数据</p>
        </div>
        
        <div class="settings-card">
          <div class="data-item">
            <div class="data-info">
              <h3>导出学习数据</h3>
              <p>下载你的学习记录和进度数据</p>
            </div>
            <button @click="exportData" class="btn-secondary">
              <i class="fas fa-download"></i>
              导出数据
            </button>
          </div>
          
          <div class="data-item">
            <div class="data-info">
              <h3>清除缓存</h3>
              <p>清除本地缓存数据以释放存储空间</p>
            </div>
            <button @click="clearCache" class="btn-secondary">
              <i class="fas fa-trash"></i>
              清除缓存
            </button>
          </div>
          
          <div class="data-item danger">
            <div class="data-info">
              <h3>删除账户</h3>
              <p>永久删除你的账户和所有数据</p>
            </div>
            <button @click="showDeleteModal = true" class="btn-danger">
              <i class="fas fa-exclamation-triangle"></i>
              删除账户
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div class="modal" v-if="showPasswordModal" @click="showPasswordModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button @click="showPasswordModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label for="currentPassword">当前密码</label>
              <input type="password" 
                     id="currentPassword" 
                     v-model="passwordForm.currentPassword" 
                     class="form-input"
                     placeholder="请输入当前密码">
            </div>
            <div class="form-group">
              <label for="newPassword">新密码</label>
              <input type="password" 
                     id="newPassword" 
                     v-model="passwordForm.newPassword" 
                     class="form-input"
                     placeholder="请输入新密码">
            </div>
            <div class="form-group">
              <label for="confirmPassword">确认新密码</label>
              <input type="password" 
                     id="confirmPassword" 
                     v-model="passwordForm.confirmPassword" 
                     class="form-input"
                     placeholder="请再次输入新密码">
            </div>
            <div class="form-actions">
              <button type="button" 
                      @click="showPasswordModal = false" 
                      class="btn-secondary">
                取消
              </button>
              <button type="submit" class="btn-primary">
                确认修改
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 删除账户确认弹窗 -->
    <div class="modal" v-if="showDeleteModal" @click="showDeleteModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>删除账户</h3>
          <button @click="showDeleteModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="warning-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>此操作不可撤销！删除账户将永久清除所有学习数据、进度记录和个人信息。</p>
          </div>
          <div class="form-group">
            <label for="deleteConfirm">请输入 "DELETE" 确认删除</label>
            <input type="text" 
                   id="deleteConfirm" 
                   v-model="deleteConfirmText" 
                   class="form-input"
                   placeholder="输入 DELETE">
          </div>
          <div class="form-actions">
            <button type="button" 
                    @click="showDeleteModal = false" 
                    class="btn-secondary">
              取消
            </button>
            <button @click="deleteAccount" 
                    :disabled="deleteConfirmText !== 'DELETE'"
                    class="btn-danger">
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// 响应式数据
const showPasswordModal = ref(false)
const showDeleteModal = ref(false)
const deleteConfirmText = ref('')
const avatarInput = ref<HTMLInputElement | null>(null)

// 表单数据
const profileForm = reactive({
  username: 'john_doe',
  email: 'john@example.com',
  phone: '13800138000',
  birthday: '1990-01-01',
  bio: '热爱学习英语的程序员',
  avatar: '/default-avatar.png'
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const securitySettings = reactive({
  twoFactorEnabled: false,
  loginNotification: true
})

const learningPreferences = reactive({
  dailyGoal: 30,
  dailyReminder: true,
  reminderTime: '19:00',
  difficulty: 'medium',
  speechSpeed: 1.0
})

const notificationSettings = reactive([
  {
    key: 'learningReminder',
    title: '学习提醒',
    description: '每日学习时间提醒',
    enabled: true
  },
  {
    key: 'achievementNotification',
    title: '成就通知',
    description: '获得新成就时的通知',
    enabled: true
  },
  {
    key: 'weeklyReport',
    title: '周报告',
    description: '每周学习进度报告',
    enabled: false
  },
  {
    key: 'systemUpdate',
    title: '系统更新',
    description: '系统功能更新通知',
    enabled: true
  }
])

// 每日目标选项
const dailyGoals = [
  { value: 15, label: '15分钟' },
  { value: 30, label: '30分钟' },
  { value: 60, label: '1小时' },
  { value: 120, label: '2小时' }
]

// 方法
const updateProfile = () => {
  console.log('更新个人信息:', profileForm)
  // 实际应用中这里会调用API
}

const handleAvatarChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      profileForm.avatar = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const changePassword = () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('新密码和确认密码不匹配')
    return
  }
  console.log('修改密码')
  showPasswordModal.value = false
  // 重置表单
  Object.assign(passwordForm, {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
}

const exportData = () => {
  console.log('导出学习数据')
  // 实际应用中这里会生成并下载数据文件
}

const clearCache = () => {
  console.log('清除缓存')
  // 实际应用中这里会清除本地缓存
}

const deleteAccount = () => {
  console.log('删除账户')
  showDeleteModal.value = false
  deleteConfirmText.value = ''
  // 实际应用中这里会调用删除账户的API
}
</script>

<style scoped lang="scss">
.settings {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    color: #2c3e50;
    margin-bottom: 10px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 16px;
  }
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.settings-section {
  .section-header {
    margin-bottom: 20px;
    
    h2 {
      color: #2c3e50;
      margin-bottom: 8px;
      font-size: 20px;
    }
    
    p {
      color: #7f8c8d;
      font-size: 14px;
    }
  }
}

.settings-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  
  &.full-width {
    grid-column: 1 / -1;
  }
  
  label {
    color: #2c3e50;
    font-weight: 500;
    margin-bottom: 8px;
    font-size: 14px;
  }
}

.form-input, .form-textarea, .form-select {
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #3498db;
  }
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  
  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .avatar-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover .avatar-overlay {
    opacity: 1;
  }
}

.avatar-input {
  display: none;
}

.upload-btn {
  padding: 8px 16px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s ease;
  
  &:hover {
    background: #2980b9;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary, .btn-secondary, .btn-danger {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: #3498db;
  color: white;
  
  &:hover:not(:disabled) {
    background: #2980b9;
  }
}

.btn-secondary {
  background: #6c757d;
  color: white;
  
  &:hover {
    background: #5a6268;
  }
}

.btn-danger {
  background: #e74c3c;
  color: white;
  
  &:hover:not(:disabled) {
    background: #c0392b;
  }
}

.security-item, .data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f8f9fa;
  
  &:last-child {
    border-bottom: none;
  }
  
  &.danger {
    .security-info, .data-info {
      h3 {
        color: #e74c3c;
      }
    }
  }
}

.security-info, .data-info {
  flex: 1;
  
  h3 {
    color: #2c3e50;
    margin-bottom: 4px;
    font-size: 16px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 14px;
    margin: 0;
  }
}

.toggle-switch {
  position: relative;
  
  input[type="checkbox"] {
    display: none;
  }
  
  .toggle-label {
    display: block;
    width: 50px;
    height: 26px;
    background: #ddd;
    border-radius: 13px;
    cursor: pointer;
    position: relative;
    transition: background 0.3s ease;
    
    &::after {
      content: '';
      position: absolute;
      top: 2px;
      left: 2px;
      width: 22px;
      height: 22px;
      background: white;
      border-radius: 50%;
      transition: transform 0.3s ease;
    }
  }
  
  input[type="checkbox"]:checked + .toggle-label {
    background: #3498db;
    
    &::after {
      transform: translateX(24px);
    }
  }
}

.preference-item {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  label {
    display: block;
    color: #2c3e50;
    font-weight: 500;
    margin-bottom: 12px;
    font-size: 14px;
  }
}

.goal-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.goal-btn {
  padding: 8px 16px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #3498db;
  }
  
  &.active {
    background: #3498db;
    color: white;
    border-color: #3498db;
  }
}

.reminder-settings {
  display: flex;
  align-items: center;
  gap: 16px;
}

.time-input {
  padding: 8px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
}

.speed-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.slider {
  flex: 1;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  outline: none;
  
  &::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    background: #3498db;
    border-radius: 50%;
    cursor: pointer;
  }
}

.speed-value {
  color: #3498db;
  font-weight: 600;
  min-width: 40px;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f8f9fa;
  
  &:last-child {
    border-bottom: none;
  }
}

.notification-info {
  flex: 1;
  
  h3 {
    color: #2c3e50;
    margin-bottom: 4px;
    font-size: 16px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 14px;
    margin: 0;
  }
}

.modal {
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

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  
  h3 {
    margin: 0;
    color: #2c3e50;
  }
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #7f8c8d;
  cursor: pointer;
  
  &:hover {
    color: #2c3e50;
  }
}

.modal-body {
  padding: 24px;
}

.warning-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  
  i {
    color: #856404;
    font-size: 20px;
    margin-top: 2px;
  }
  
  p {
    color: #856404;
    margin: 0;
    line-height: 1.4;
  }
}

@media (max-width: 768px) {
  .settings {
    padding: 16px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .security-item, .data-item, .notification-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .avatar-upload {
    flex-direction: column;
    align-items: center;
  }
  
  .goal-selector {
    justify-content: center;
  }
}
</style>