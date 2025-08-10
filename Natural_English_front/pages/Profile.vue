<template>
  <div class="profile-container">
    <!-- 用户信息卡片 -->
    <div class="user-card">
      <div class="avatar">
        <img v-if="userInfo.avatar" :src="userInfo.avatar" alt="头像" />
        <div v-else class="default-avatar">{{ userInfo.username?.charAt(0)?.toUpperCase() || '用' }}</div>
      </div>
      <div class="user-info">
        <h2 class="username">{{ userInfo.real_name || userInfo.username || '未登录' }}</h2>
        <p class="user-desc">{{ userInfo.email || '暂无邮箱' }}</p>
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
      }
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
          this.userInfo = JSON.parse(userStr)
        } catch (e) {
          console.error('解析用户信息失败:', e)
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