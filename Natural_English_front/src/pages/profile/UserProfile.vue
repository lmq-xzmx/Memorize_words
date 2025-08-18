<template>
  <div class="user-profile">
    <div class="profile-header">
      <h1>个人中心</h1>
    </div>

    <div class="profile-content">
      <!-- 用户信息卡片 -->
      <div class="profile-card">
        <div class="profile-avatar">
          <div class="avatar-container">
            <img 
              v-if="userInfo.avatar" 
              :src="userInfo.avatar" 
              :alt="userInfo.username"
              class="avatar-image"
            />
            <div v-else class="avatar-placeholder">
              {{ userInfo.username?.charAt(0)?.toUpperCase() }}
            </div>
            <button class="avatar-edit-btn" @click="showAvatarUpload = true">
              <i class="el-icon-camera"></i>
            </button>
          </div>
        </div>
        
        <div class="profile-info">
          <h2>{{ userInfo.username }}</h2>
          <p class="user-email">{{ userInfo.email }}</p>
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-value">{{ userStats.studyDays }}</span>
              <span class="stat-label">学习天数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userStats.totalWords }}</span>
              <span class="stat-label">学习单词</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userStats.level }}</span>
              <span class="stat-label">当前等级</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 设置选项 -->
      <div class="settings-section">
        <h3>账户设置</h3>
        <div class="settings-list">
          <div class="setting-item" @click="showEditProfile = true">
            <div class="setting-icon">
              <i class="el-icon-user"></i>
            </div>
            <div class="setting-content">
              <h4>编辑个人信息</h4>
              <p>修改用户名、邮箱等基本信息</p>
            </div>
            <div class="setting-arrow">
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
          
          <div class="setting-item" @click="showChangePassword = true">
            <div class="setting-icon">
              <i class="el-icon-lock"></i>
            </div>
            <div class="setting-content">
              <h4>修改密码</h4>
              <p>更改登录密码</p>
            </div>
            <div class="setting-arrow">
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
          
          <div class="setting-item" @click="showLearningSettings = true">
            <div class="setting-icon">
              <i class="el-icon-setting"></i>
            </div>
            <div class="setting-content">
              <h4>学习设置</h4>
              <p>自定义学习偏好和目标</p>
            </div>
            <div class="setting-arrow">
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
          
          <div class="setting-item" @click="showNotificationSettings = true">
            <div class="setting-icon">
              <i class="el-icon-bell"></i>
            </div>
            <div class="setting-content">
              <h4>通知设置</h4>
              <p>管理推送通知和提醒</p>
            </div>
            <div class="setting-arrow">
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 学习成就 -->
      <div class="achievements-section" v-permission="'profile.achievements.view'">
        <h3>学习成就</h3>
        <div class="achievements-grid">
          <div 
            v-for="achievement in achievements" 
            :key="achievement.id"
            class="achievement-item"
            :class="{ unlocked: achievement.unlocked }"
          >
            <div class="achievement-icon">
              <i :class="achievement.icon"></i>
            </div>
            <div class="achievement-info">
              <h4>{{ achievement.title }}</h4>
              <p>{{ achievement.description }}</p>
              <div class="achievement-progress" v-if="!achievement.unlocked">
                <div class="progress-bar">
                  <div 
                  class="progress-fill" 
                  :style="{ width: ((achievement.current || 0) / (achievement.target || 1)) * 100 + '%' }"
                ></div>
                </div>
                <span class="progress-text">
                  {{ achievement.current || 0 }} / {{ achievement.target || 0 }}
                </span>
              </div>
              <div class="achievement-date" v-if="achievement.unlocked && achievement.unlockedAt">
                获得于 {{ formatDate(achievement.unlockedAt) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑个人信息对话框 -->
    <div v-if="showEditProfile" class="modal-overlay" @click="showEditProfile = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑个人信息</h3>
          <button class="close-btn" @click="showEditProfile = false">
            <i class="el-icon-close"></i>
          </button>
        </div>
        
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="editForm.username" type="text" required />
          </div>
          
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="editForm.email" type="email" required />
          </div>
          
          <div class="form-group">
            <label>个人简介</label>
            <textarea v-model="editForm.bio" rows="3" placeholder="介绍一下自己..."></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showEditProfile = false">
              取消
            </button>
            <button type="submit" class="submit-btn">
              保存
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <div v-if="showChangePassword" class="modal-overlay" @click="showChangePassword = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="showChangePassword = false">
            <i class="el-icon-close"></i>
          </button>
        </div>
        
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label>当前密码</label>
            <input v-model="passwordForm.currentPassword" type="password" required />
          </div>
          
          <div class="form-group">
            <label>新密码</label>
            <input v-model="passwordForm.newPassword" type="password" required />
          </div>
          
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="passwordForm.confirmPassword" type="password" required />
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showChangePassword = false">
              取消
            </button>
            <button type="submit" class="submit-btn">
              修改密码
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 学习设置对话框 -->
    <div v-if="showLearningSettings" class="modal-overlay" @click="showLearningSettings = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>学习设置</h3>
          <button class="close-btn" @click="showLearningSettings = false">
            <i class="el-icon-close"></i>
          </button>
        </div>
        
        <div class="settings-form">
          <div class="form-group">
            <label>每日学习目标</label>
            <select v-model="learningSettings.dailyGoal">
              <option value="10">10个单词</option>
              <option value="20">20个单词</option>
              <option value="30">30个单词</option>
              <option value="50">50个单词</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>学习提醒时间</label>
            <input v-model="learningSettings.reminderTime" type="time" />
          </div>
          
          <div class="form-group">
            <label>难度偏好</label>
            <select v-model="learningSettings.difficulty">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
              <option value="mixed">混合</option>
            </select>
          </div>
          
          <div class="form-group">
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input 
                  v-model="learningSettings.autoPlay" 
                  type="checkbox"
                />
                <span class="checkbox-text">自动播放单词发音</span>
              </label>
              
              <label class="checkbox-label">
                <input 
                  v-model="learningSettings.showTranslation" 
                  type="checkbox"
                />
                <span class="checkbox-text">显示中文释义</span>
              </label>
              
              <label class="checkbox-label">
                <input 
                  v-model="learningSettings.enableReminder" 
                  type="checkbox"
                />
                <span class="checkbox-text">启用学习提醒</span>
              </label>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showLearningSettings = false">
              取消
            </button>
            <button type="button" class="submit-btn" @click="saveLearningSettings">
              保存设置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知设置对话框 -->
    <div v-if="showNotificationSettings" class="modal-overlay" @click="showNotificationSettings = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>通知设置</h3>
          <button class="close-btn" @click="showNotificationSettings = false">
            <i class="el-icon-close"></i>
          </button>
        </div>
        
        <div class="notification-settings">
          <div class="notification-item">
            <div class="notification-info">
              <h4>学习提醒</h4>
              <p>每日学习时间提醒</p>
            </div>
            <label class="switch">
              <input v-model="notificationSettings.learningReminder" type="checkbox" />
              <span class="slider"></span>
            </label>
          </div>
          
          <div class="notification-item">
            <div class="notification-info">
              <h4>成就通知</h4>
              <p>获得新成就时通知</p>
            </div>
            <label class="switch">
              <input v-model="notificationSettings.achievementNotification" type="checkbox" />
              <span class="slider"></span>
            </label>
          </div>
          
          <div class="notification-item">
            <div class="notification-info">
              <h4>进度报告</h4>
              <p>每周学习进度报告</p>
            </div>
            <label class="switch">
              <input v-model="notificationSettings.progressReport" type="checkbox" />
              <span class="slider"></span>
            </label>
          </div>
          
          <div class="notification-item">
            <div class="notification-info">
              <h4>复习提醒</h4>
              <p>单词复习时间提醒</p>
            </div>
            <label class="switch">
              <input v-model="notificationSettings.reviewReminder" type="checkbox" />
              <span class="slider"></span>
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showNotificationSettings = false">
              取消
            </button>
            <button type="button" class="submit-btn" @click="saveNotificationSettings">
              保存设置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 头像上传对话框 -->
    <div v-if="showAvatarUpload" class="modal-overlay" @click="showAvatarUpload = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>更换头像</h3>
          <button class="close-btn" @click="showAvatarUpload = false">
            <i class="el-icon-close"></i>
          </button>
        </div>
        
        <div class="avatar-upload">
          <div class="upload-area" @click="triggerFileInput">
            <input 
              ref="fileInput" 
              type="file" 
              accept="image/*" 
              @change="handleFileSelect"
              style="display: none;"
            />
            <div class="upload-placeholder">
              <i class="el-icon-plus"></i>
              <p>点击选择图片</p>
            </div>
          </div>
          
          <div class="upload-tips">
            <p>支持 JPG、PNG 格式，文件大小不超过 2MB</p>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showAvatarUpload = false">
              取消
            </button>
            <button type="button" class="submit-btn" @click="uploadAvatar" :disabled="!selectedFile">
              上传头像
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { permissionChecker } from '@/utils/permissions'

interface UserInfo {
  id: string
  username: string
  email: string
  avatar?: string
  bio?: string
}

interface UserStats {
  studyDays: number
  totalWords: number
  level: string
}

interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  unlocked: boolean
  current?: number
  target?: number
  unlockedAt?: string
}

// 响应式数据
const showEditProfile = ref(false)
const showChangePassword = ref(false)
const showLearningSettings = ref(false)
const showNotificationSettings = ref(false)
const showAvatarUpload = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// 用户信息
const userInfo = ref<UserInfo>({
  id: '1',
  username: '学习者',
  email: 'learner@example.com',
  bio: '热爱学习英语的小伙伴'
})

// 用户统计
const userStats = ref<UserStats>({
  studyDays: 45,
  totalWords: 1250,
  level: 'B1'
})

// 编辑表单
const editForm = ref({
  username: '',
  email: '',
  bio: ''
})

// 密码表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 学习设置
const learningSettings = ref({
  dailyGoal: '20',
  reminderTime: '09:00',
  difficulty: 'medium',
  autoPlay: true,
  showTranslation: true,
  enableReminder: true
})

// 通知设置
const notificationSettings = ref({
  learningReminder: true,
  achievementNotification: true,
  progressReport: false,
  reviewReminder: true
})

// 成就列表
const achievements = ref<Achievement[]>([
  {
    id: '1',
    title: '初学者',
    description: '完成第一次单词学习',
    icon: 'el-icon-star-off',
    unlocked: true,
    unlockedAt: '2024-01-01'
  },
  {
    id: '2',
    title: '坚持者',
    description: '连续学习7天',
    icon: 'el-icon-trophy',
    unlocked: true,
    unlockedAt: '2024-01-08'
  },
  {
    id: '3',
    title: '词汇达人',
    description: '学习1000个单词',
    icon: 'el-icon-medal',
    unlocked: false,
    current: 856,
    target: 1000
  },
  {
    id: '4',
    title: '完美主义者',
    description: '单次测试100%正确率',
    icon: 'el-icon-check',
    unlocked: false,
    current: 0,
    target: 1
  }
])

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 初始化编辑表单
const initEditForm = () => {
  editForm.value = {
    username: userInfo.value.username,
    email: userInfo.value.email,
    bio: userInfo.value.bio || ''
  }
}

// 更新个人信息
const updateProfile = async () => {
  try {
    // 模拟API调用
    userInfo.value.username = editForm.value.username
    userInfo.value.email = editForm.value.email
    userInfo.value.bio = editForm.value.bio
    
    showEditProfile.value = false
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    ElMessage.error('更新失败，请重试')
  }
}

// 修改密码
const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.error('密码长度至少6位')
    return
  }
  
  try {
    // 模拟API调用
    showChangePassword.value = false
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    ElMessage.success('密码修改成功')
  } catch (error) {
    ElMessage.error('密码修改失败，请重试')
  }
}

// 保存学习设置
const saveLearningSettings = async () => {
  try {
    // 模拟API调用
    showLearningSettings.value = false
    ElMessage.success('学习设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  }
}

// 保存通知设置
const saveNotificationSettings = async () => {
  try {
    // 模拟API调用
    showNotificationSettings.value = false
    ElMessage.success('通知设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  }
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error('文件大小不能超过2MB')
      return
    }
    
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      return
    }
    
    selectedFile.value = file
  }
}

// 上传头像
const uploadAvatar = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请先选择图片')
    return
  }
  
  try {
    // 模拟上传
    const reader = new FileReader()
    reader.onload = (e) => {
      userInfo.value.avatar = e.target?.result as string
      showAvatarUpload.value = false
      selectedFile.value = null
      ElMessage.success('头像上传成功')
    }
    reader.readAsDataURL(selectedFile.value)
  } catch (error) {
    ElMessage.error('上传失败，请重试')
  }
}

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  initEditForm()
})
</script>

<style scoped>
.user-profile {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.profile-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.profile-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 2rem;
  align-items: center;
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar-container {
  position: relative;
  width: 120px;
  height: 120px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e5e7eb;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.5rem;
  font-weight: 600;
  border: 3px solid #e5e7eb;
}

.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36px;
  height: 36px;
  background: #667eea;
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: background 0.2s ease;
}

.avatar-edit-btn:hover {
  background: #5a6fd8;
}

.profile-info {
  flex: 1;
}

.profile-info h2 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 600;
}

.user-email {
  margin: 0 0 1.5rem 0;
  color: #6b7280;
  font-size: 1rem;
}

.user-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.stat-label {
  display: block;
  color: #6b7280;
  font-size: 0.875rem;
}

.settings-section,
.achievements-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.settings-section h3,
.achievements-section h3 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.setting-item:hover {
  background: #f9fafb;
}

.setting-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.setting-content {
  flex: 1;
}

.setting-content h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 500;
}

.setting-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.setting-arrow {
  color: #9ca3af;
  font-size: 1rem;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.achievement-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.achievement-item.unlocked {
  background: #ecfdf5;
  border-color: #10b981;
}

.achievement-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  background: #f3f4f6;
  color: #6b7280;
}

.achievement-item.unlocked .achievement-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.achievement-info {
  flex: 1;
}

.achievement-info h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 500;
}

.achievement-info p {
  margin: 0 0 0.75rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.achievement-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 500;
}

.achievement-date {
  color: #10b981;
  font-size: 0.75rem;
  font-weight: 500;
}

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

.modal-content {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #374151;
}

.profile-form,
.password-form,
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #374151;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-text {
  color: #374151;
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s ease;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.submit-btn {
  background: #667eea;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.submit-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.notification-settings {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.notification-info h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 500;
}

.notification-info p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 48px;
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
  background-color: #d1d5db;
  transition: 0.2s;
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
  transition: 0.2s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #667eea;
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.avatar-upload {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.upload-area:hover {
  border-color: #667eea;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
}

.upload-placeholder i {
  font-size: 2rem;
}

.upload-tips {
  text-align: center;
}

.upload-tips p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .user-profile {
    padding: 1rem;
  }
  
  .profile-card {
    flex-direction: column;
    text-align: center;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .achievements-grid {
    grid-template-columns: 1fr;
  }
  
  .notification-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>