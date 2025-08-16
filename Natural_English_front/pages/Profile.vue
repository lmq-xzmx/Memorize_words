<template>
  <div class="profile-container">
    <!-- 用户信息卡片 -->
    <div class="user-card">
      <div class="avatar" @click="showAvatarUpload = true">
        <img v-if="userInfo.avatar" :src="userInfo.avatar" alt="头像" />
        <div v-else class="default-avatar">{{ userInfo.username?.charAt(0)?.toUpperCase() || '用' }}</div>
        <div class="avatar-edit-overlay">
          <span class="edit-icon">📷</span>
        </div>
      </div>
      <div class="user-info">
        <h2 class="username">{{ getDisplayName() }}</h2>
        <p class="user-desc">{{ getLoginStatus() }}</p>
        <div class="user-stats">
          <div class="stat-item">
            <span class="stat-number">{{ learningStats.wordsLearned }}</span>
            <span class="stat-label">已学单词</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ learningStats.daysStreak }}</span>
            <span class="stat-label">连续天数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ learningStats.totalTime }}</span>
            <span class="stat-label">学习时长</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能菜单 -->
    <div class="menu-section">
      <div class="menu-group">
        <div class="menu-item" @click="goToPage('/word-selection')">
          <div class="menu-icon">📚</div>
          <span class="menu-text">单词本</span>
          <div class="menu-arrow">›</div>
        </div>
        <div class="menu-item" @click="goToPage('/word-review')">
          <div class="menu-icon">🔄</div>
          <span class="menu-text">复习记录</span>
          <div class="menu-arrow">›</div>
        </div>
        <div class="menu-item" @click="goToPage('/learning-progress')">
          <div class="menu-icon">📊</div>
          <span class="menu-text">学习进度</span>
          <div class="menu-arrow">›</div>
        </div>
      </div>

      <div class="menu-group">
        <div class="menu-item" @click="goToPage('/settings')">
          <div class="menu-icon">⚙️</div>
          <span class="menu-text">设置</span>
          <div class="menu-arrow">›</div>
        </div>
        <div class="menu-item" @click="goToPage('/help')">
          <div class="menu-icon">❓</div>
          <span class="menu-text">帮助与反馈</span>
          <div class="menu-arrow">›</div>
        </div>
        <div class="menu-item" @click="goToPage('/about')">
          <div class="menu-icon">ℹ️</div>
          <span class="menu-text">关于我们</span>
          <div class="menu-arrow">›</div>
        </div>
      </div>
    </div>

    <!-- 退出登录按钮 -->
    <div class="logout-section">
      <button class="logout-btn" @click="handleLogout">
        退出登录
      </button>
    </div>

    <!-- 头像上传弹窗 -->
    <div v-if="showAvatarUpload" class="modal-overlay" @click="showAvatarUpload = false">
      <div class="modal-content avatar-modal" @click.stop>
        <h3>设置头像</h3>
        <div class="avatar-options">
          <div class="default-avatars">
            <h4>选择默认头像</h4>
            <div class="avatar-grid">
              <div 
                v-for="(avatar, index) in defaultAvatars" 
                :key="index"
                class="avatar-option"
                @click="selectDefaultAvatar(avatar)"
              >
                <div class="avatar-preview">{{ avatar }}</div>
              </div>
            </div>
          </div>
          <div class="custom-avatar">
            <h4>上传自定义头像</h4>
            <input 
              type="file" 
              ref="avatarInput"
              @change="handleAvatarUpload"
              accept="image/*"
              style="display: none;"
            >
            <button class="upload-btn" @click="$refs.avatarInput.click()">
              选择图片
            </button>
          </div>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showAvatarUpload = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Profile',
  data() {
    return {
      userInfo: {
        username: '',
        real_name: '',
        email: '',
        avatar: ''
      },
      learningStats: {
        wordsLearned: 0,
        daysStreak: 0,
        totalTime: '0分钟'
      },
      showAvatarUpload: false,
      defaultAvatars: ['👤', '👨', '👩', '🧑', '👦', '👧', '🐱', '🐶', '🦊', '🐻']
    }
  },
  mounted() {
    this.loadUserInfo()
    this.loadLearningStats()
  },
  methods: {
    loadUserInfo() {
      // 从localStorage获取用户信息
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          // 检查是否是HTML内容（通常以<!DOCTYPE开头）
          if (userStr.trim().startsWith('<!DOCTYPE') || userStr.trim().startsWith('<html')) {
            console.warn('检测到localStorage中存储的是HTML内容，清除无效数据')
            localStorage.removeItem('user')
            localStorage.removeItem('token')
            // 重定向到登录页
            this.$router.push('/login')
            return
          }
          
          const parsedUser = JSON.parse(userStr)
          // 验证解析后的数据是否为有效的用户对象
          if (parsedUser && typeof parsedUser === 'object' && !Array.isArray(parsedUser)) {
            this.userInfo = parsedUser
          } else {
            console.warn('localStorage中的用户数据格式无效，清除数据')
            localStorage.removeItem('user')
            localStorage.removeItem('token')
            this.$router.push('/login')
          }
        } catch (e) {
          console.error('解析用户信息失败:', e)
          // 清除损坏的数据
          localStorage.removeItem('user')
          localStorage.removeItem('token')
          this.$router.push('/login')
        }
      }
    },
    loadLearningStats() {
      // 模拟学习统计数据，实际应该从API获取
      this.learningStats = {
        wordsLearned: 156,
        daysStreak: 7,
        totalTime: '2小时30分钟'
      }
    },
    getDisplayName() {
      if (this.userInfo.real_name) {
        return this.userInfo.real_name
      }
      if (this.userInfo.username) {
        return this.userInfo.username
      }
      return '未登录用户'
    },
    getLoginStatus() {
      const token = localStorage.getItem('token')
      if (token && this.userInfo.username) {
        return this.userInfo.email || '已登录'
      }
      return '请登录以同步学习数据'
    },
    selectDefaultAvatar(avatar) {
      // 确保userInfo是一个有效的对象
      if (!this.userInfo || typeof this.userInfo !== 'object' || Array.isArray(this.userInfo)) {
        console.error('userInfo不是有效的对象，无法设置头像')
        // 重新初始化userInfo
        this.userInfo = {
          username: '',
          real_name: '',
          email: '',
          avatar: ''
        }
      }
      
      this.userInfo.avatar = avatar
      this.saveUserInfo()
      this.showAvatarUpload = false
    },
    handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.userInfo.avatar = e.target.result
          this.saveUserInfo()
          this.showAvatarUpload = false
        }
        reader.readAsDataURL(file)
      }
    },
    saveUserInfo() {
      // 确保userInfo是有效对象再保存
      if (this.userInfo && typeof this.userInfo === 'object' && !Array.isArray(this.userInfo)) {
        try {
          localStorage.setItem('user', JSON.stringify(this.userInfo))
        } catch (e) {
          console.error('保存用户信息失败:', e)
        }
      } else {
        console.error('userInfo不是有效对象，无法保存')
      }
    },
    goToPage(path) {
      this.$router.push(path)
    },
    handleLogout() {
      if (confirm('确定要退出登录吗？')) {
        // 清除本地存储
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        // 跳转到登录页
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style scoped>
/* 个人资料页面主容器 */
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  position: relative;
  overflow-x: hidden;
}

.profile-container::before {
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

/* 用户信息卡片 */
.user-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 25px;
  padding: 2.5rem;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
  animation: slideInUp 0.8s ease-out;
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

/* 头像区域 */
.avatar {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.avatar-edit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar:hover .avatar-edit-overlay {
  opacity: 1;
}

.edit-icon {
  font-size: 2rem;
  filter: grayscale(1) brightness(2);
}

/* 用户信息 */
.user-info {
  flex: 1;
}

.username {
  font-size: 2.2rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-desc {
  font-size: 1.1rem;
  color: #666;
  margin: 0 0 1.5rem 0;
  font-weight: 500;
}

/* 用户统计 */
.user-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 15px;
  min-width: 80px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
}

.stat-number {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.3rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

/* 菜单区域 */
.menu-section {
  position: relative;
  z-index: 1;
}

.menu-group {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 1.5rem;
  animation: slideInUp 0.8s ease-out 0.2s both;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 1.5rem 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.menu-item:hover {
  background: rgba(102, 126, 234, 0.05);
  transform: translateX(5px);
}

.menu-item:hover::before {
  left: 100%;
}

.menu-icon {
  font-size: 1.8rem;
  margin-right: 1rem;
  width: 40px;
  text-align: center;
  filter: grayscale(0.3);
  transition: filter 0.3s ease;
}

.menu-item:hover .menu-icon {
  filter: grayscale(0);
}

.menu-text {
  flex: 1;
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}

.menu-arrow {
  font-size: 1.5rem;
  color: #999;
  transition: all 0.3s ease;
}

.menu-item:hover .menu-arrow {
  color: #667eea;
  transform: translateX(5px);
}

/* 头像上传弹窗 */
.avatar-upload-modal {
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

.upload-content {
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

.upload-content h3 {
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 1.5rem 0;
  text-align: center;
}

.upload-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.upload-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.upload-btn:hover::before {
  left: 100%;
}

.upload-btn:active {
  transform: translateY(0);
}

.cancel-btn {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: #e9ecef;
  color: #333;
}

.default-avatars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin: 1rem 0;
}

.default-avatar-option {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent;
}

.default-avatar-option:hover {
  transform: scale(1.1);
  border-color: #667eea;
}

.hidden-file-input {
  display: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-container {
    padding: 1rem;
  }
  
  .user-card {
    flex-direction: column;
    text-align: center;
    padding: 2rem;
    gap: 1.5rem;
  }
  
  .avatar {
    width: 100px;
    height: 100px;
  }
  
  .default-avatar {
    font-size: 2.5rem;
  }
  
  .username {
    font-size: 1.8rem;
  }
  
  .user-stats {
    justify-content: center;
    gap: 1rem;
  }
  
  .stat-item {
    min-width: 70px;
    padding: 0.8rem;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  .menu-item {
    padding: 1.2rem 1.5rem;
  }
  
  .menu-icon {
    font-size: 1.5rem;
  }
  
  .menu-text {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .user-card {
    padding: 1.5rem;
  }
  
  .avatar {
    width: 80px;
    height: 80px;
  }
  
  .default-avatar {
    font-size: 2rem;
  }
  
  .username {
    font-size: 1.5rem;
  }
  
  .user-stats {
    flex-direction: column;
    align-items: center;
    gap: 0.8rem;
  }
  
  .stat-item {
    width: 100%;
    max-width: 200px;
  }
  
  .menu-item {
    padding: 1rem;
  }
  
  .default-avatars {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .default-avatar-option {
    width: 50px;
    height: 50px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .user-card,
  .menu-group,
  .upload-content {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .username {
    color: #f0f0f0;
  }
  
  .user-desc,
  .menu-text {
    color: #b0b0b0;
  }
  
  .stat-label {
    color: #888;
  }
  
  .menu-item {
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .cancel-btn {
    background: #333;
    color: #e0e0e0;
    border-color: #555;
  }
  
  .cancel-btn:hover {
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
  .profile-container {
    background: #000;
  }
  
  .user-card,
  .menu-group,
  .upload-content {
    background: #fff;
    border: 2px solid #000;
  }
  
  .username,
  .menu-text {
    color: #000;
  }
}

/* 焦点状态 */
.menu-item:focus,
.upload-btn:focus,
.cancel-btn:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .menu-item,
  .upload-btn,
  .cancel-btn {
    min-height: 44px;
  }
  
  .menu-item:hover,
  .stat-item:hover {
    transform: none;
  }
  
  .avatar:hover {
    transform: none;
  }
}
</style>

