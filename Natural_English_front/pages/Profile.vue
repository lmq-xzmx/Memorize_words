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
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 80px;
}

.user-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px 20px;
  margin-bottom: 20px;
  text-align: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  color: white;
  font-size: 32px;
  font-weight: bold;
}

.username {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.user-desc {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 20px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.menu-section {
  margin-bottom: 20px;
}

.menu-group {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  margin-bottom: 16px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: rgba(102, 126, 234, 0.1);
}

.menu-item:active {
  transform: scale(0.98);
}

.menu-icon {
  font-size: 20px;
  margin-right: 16px;
  width: 24px;
  text-align: center;
}

.menu-text {
  flex: 1;
  font-size: 16px;
  color: #333;
}

.menu-arrow {
  font-size: 18px;
  color: #ccc;
}

.logout-section {
  padding: 0 20px;
}

.logout-btn {
  width: 100%;
  padding: 16px;
  background: rgba(255, 71, 87, 0.9);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.logout-btn:hover {
  background: rgba(255, 71, 87, 1);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 71, 87, 0.3);
}

.logout-btn:active {
  transform: translateY(0);
}

/* 头像编辑样式 */
.avatar {
  position: relative;
  cursor: pointer;
}

.avatar-edit-overlay {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 24px;
  height: 24px;
  background: #667eea;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

.edit-icon {
  font-size: 12px;
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

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin: 20px;
  max-width: 400px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}

.avatar-modal h3 {
  margin: 0 0 20px 0;
  text-align: center;
  color: #333;
}

.avatar-modal h4 {
  margin: 16px 0 12px 0;
  color: #666;
  font-size: 14px;
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.avatar-option {
  cursor: pointer;
  transition: transform 0.2s;
}

.avatar-option:hover {
  transform: scale(1.1);
}

.avatar-preview {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  border: 2px solid transparent;
}

.avatar-option:hover .avatar-preview {
  border-color: #667eea;
}

.upload-btn {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.upload-btn:hover {
  background: #5a6fd8;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 8px 16px;
  background: #f5f5f5;
  color: #666;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

/* 响应式设计 */
@media screen and (max-width: 480px) {
  .profile-container {
    padding: 16px;
  }
  
  .user-card {
    padding: 24px 16px;
  }
  
  .user-stats {
    gap: 16px;
  }
  
  .stat-number {
    font-size: 18px;
  }
}
</style>