<template>
  <view class="profile-container">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-section">
      <view class="loading-spinner"></view>
      <text class="loading-text">正在加载用户数据...</text>
    </view>

    <!-- 用户信息卡片 -->
    <view v-else class="user-card">
      <view class="avatar" @tap="showAvatarUploadModal">
        <image v-if="userInfo.avatar" :src="userInfo.avatar" alt="头像" mode="aspectFill" />
        <view v-else class="default-avatar">{{ userInfo.username?.charAt(0)?.toUpperCase() || '用' }}</view>
        <view class="avatar-edit-overlay">
          <text class="edit-icon">📷</text>
        </view>
      </view>
      
      <view class="user-info">
        <view class="user-header">
          <text class="username">{{ getDisplayName() }}</text>
          <view class="edit-btn" @tap="showEditProfileModal">
            <text class="edit-text">编辑</text>
          </view>
        </view>
        
        <text class="user-desc">{{ getLoginStatus() }}</text>
        
        <!-- 等级进度 -->
        <view class="level-section">
          <view class="level-info">
            <text class="level-text">Lv.{{ userInfo.level }}</text>
            <text class="exp-text">{{ userInfo.exp }}/{{ userInfo.nextLevelExp }}</text>
          </view>
          <view class="level-progress">
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: levelProgress + '%' }"></view>
            </view>
            <text class="progress-percent">{{ levelProgress }}%</text>
          </view>
        </view>
        
        <view class="user-stats">
          <view class="stat-item">
            <text class="stat-number">{{ learningStats.wordsLearned }}</text>
            <text class="stat-label">已学单词</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ learningStats.daysStreak }}</text>
            <text class="stat-label">连续天数</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ learningStats.totalTime }}</text>
            <text class="stat-label">学习时长</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ learningStats.averageAccuracy }}%</text>
            <text class="stat-label">平均正确率</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 成就展示 -->
    <view class="achievements-section">
      <view class="section-header">
        <text class="section-title">🏆 我的成就</text>
        <text class="section-subtitle">{{ achievements.filter(a => a.unlocked).length }}/{{ achievements.length }}</text>
      </view>
      
      <view class="achievements-grid">
        <view 
          v-for="achievement in achievements" 
          :key="achievement.id"
          class="achievement-item"
          :class="{ unlocked: achievement.unlocked }"
          @tap="viewAchievement(achievement)"
        >
          <view class="achievement-icon">
            <text class="icon-text">{{ achievement.icon }}</text>
            <view v-if="!achievement.unlocked" class="lock-overlay">🔒</view>
          </view>
          <text class="achievement-title">{{ achievement.title }}</text>
        </view>
      </view>
    </view>

    <!-- 最近活动 -->
    <view class="activity-section">
      <view class="section-header">
        <text class="section-title">📋 最近活动</text>
        <view class="refresh-btn" @tap="refreshData">
          <text class="refresh-text">刷新</text>
        </view>
      </view>
      
      <view class="activity-list">
        <view 
          v-for="(activity, index) in recentActivity" 
          :key="index"
          class="activity-item"
        >
          <view class="activity-icon">
            <text class="icon-text">{{ activity.icon }}</text>
          </view>
          <view class="activity-info">
            <text class="activity-title">{{ activity.title }}</text>
            <text class="activity-desc">{{ activity.description }}</text>
          </view>
          <text class="activity-time">{{ activity.time }}</text>
        </view>
      </view>
    </view>

    <!-- 快捷设置 -->
    <view class="settings-section">
      <text class="section-title">⚙️ 快捷设置</text>
      
      <view class="settings-list">
        <view class="setting-item" @tap="toggleSetting('soundEnabled')">
          <view class="setting-info">
            <text class="setting-icon">🔊</text>
            <text class="setting-text">音效</text>
          </view>
          <view class="setting-toggle" :class="{ active: settings.soundEnabled }">
            <view class="toggle-thumb"></view>
          </view>
        </view>
        
        <view class="setting-item" @tap="toggleSetting('notificationEnabled')">
          <view class="setting-info">
            <text class="setting-icon">🔔</text>
            <text class="setting-text">通知</text>
          </view>
          <view class="setting-toggle" :class="{ active: settings.notificationEnabled }">
            <view class="toggle-thumb"></view>
          </view>
        </view>
        
        <view class="setting-item" @tap="toggleSetting('autoPlayAudio')">
          <view class="setting-info">
            <text class="setting-icon">🎵</text>
            <text class="setting-text">自动播放发音</text>
          </view>
          <view class="setting-toggle" :class="{ active: settings.autoPlayAudio }">
            <view class="toggle-thumb"></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-group">
        <view class="menu-item" @tap="goToPage('/word-selection')">
          <view class="menu-icon">📚</view>
          <text class="menu-text">单词本</text>
          <view class="menu-arrow">›</view>
        </view>
        <view class="menu-item" @tap="goToPage('/word-review')">
          <view class="menu-icon">🔄</view>
          <text class="menu-text">复习记录</text>
          <view class="menu-arrow">›</view>
        </view>
        <view class="menu-item" @tap="goToPage('/learning-progress')">
          <view class="menu-icon">📊</view>
          <text class="menu-text">学习进度</text>
          <view class="menu-arrow">›</view>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-item" @tap="goToPage('/settings')">
          <view class="menu-icon">⚙️</view>
          <text class="menu-text">设置</text>
          <view class="menu-arrow">›</view>
        </view>
        <view class="menu-item" @tap="goToPage('/help')">
          <view class="menu-icon">❓</view>
          <text class="menu-text">帮助与反馈</text>
          <view class="menu-arrow">›</view>
        </view>
        <view class="menu-item" @tap="goToPage('/about')">
          <view class="menu-icon">ℹ️</view>
          <text class="menu-text">关于我们</text>
          <view class="menu-arrow">›</view>
        </view>
      </view>
    </view>

    <!-- 退出登录按钮 -->
    <view class="logout-section">
      <button class="logout-btn" @tap="handleLogout">
        退出登录
      </button>
    </view>

    <!-- 头像上传弹窗 -->
    <view v-if="showAvatarUpload" class="modal-overlay" @tap="closeAvatarModal">
      <view class="modal-content avatar-modal" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">更换头像</text>
          <view class="close-btn" @tap="closeAvatarModal">
            <text>✕</text>
          </view>
        </view>
        <view class="avatar-options">
          <view class="option-btn" @tap="chooseFromGallery">
            <text class="option-icon">🖼️</text>
            <text class="option-text">从相册选择</text>
          </view>
          <view class="option-btn" @tap="takePhoto">
            <text class="option-icon">📷</text>
            <text class="option-text">拍照</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 编辑个人资料弹窗 -->
    <view v-if="showEditProfile" class="modal-overlay" @tap="closeEditProfileModal">
      <view class="modal-content edit-profile-modal" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">编辑个人资料</text>
          <view class="close-btn" @tap="closeEditProfileModal">
            <text>✕</text>
          </view>
        </view>
        
        <view class="edit-form">
          <view class="form-item">
            <text class="form-label">昵称</text>
            <input class="form-input" v-model="userInfo.nickname" placeholder="请输入昵称" />
          </view>
          
          <view class="form-item">
            <text class="form-label">邮箱</text>
            <input class="form-input" v-model="userInfo.email" placeholder="请输入邮箱" />
          </view>
          
          <view class="form-item">
            <text class="form-label">手机号</text>
            <input class="form-input" v-model="userInfo.phone" placeholder="请输入手机号" />
          </view>
          
          <view class="form-item">
            <text class="form-label">每日学习目标</text>
            <input class="form-input" v-model="settings.dailyGoal" type="number" placeholder="请输入每日学习目标" />
          </view>
        </view>
        
        <view class="modal-actions">
          <button class="cancel-btn" @tap="closeEditProfileModal">取消</button>
          <button class="save-btn" @tap="saveProfile">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { mockData, getUserStats, simulateApiDelay } from '@/utils/mockData'
import { audioConfig } from '@/config/audioConfig'

export default {
  name: 'Profile',
  data() {
    return {
      loading: false,
      showAvatarUpload: false,
      showEditProfile: false,
      userInfo: {
        id: 1,
        username: 'DemoUser',
        nickname: '单词学习达人',
        avatar: '',
        email: 'demo@example.com',
        phone: '138****8888',
        joinDate: '2024-01-15',
        level: 5,
        exp: 2580,
        nextLevelExp: 3000
      },
      learningStats: {
        wordsLearned: 0,
        daysStreak: 0,
        totalTime: '0h',
        challengesCompleted: 0,
        averageAccuracy: 0,
        favoriteWords: 0
      },
      achievements: [],
      recentActivity: [],
      settings: {
        soundEnabled: true,
        notificationEnabled: true,
        autoPlayAudio: true,
        dailyGoal: 20,
        reminderTime: '20:00'
      }
    }
  },
  computed: {
    levelProgress() {
      return Math.round((this.userInfo.exp / this.userInfo.nextLevelExp) * 100)
    },
    
    userLevel() {
      const levels = ['新手', '初学者', '进阶者', '熟练者', '专家', '大师', '宗师']
      return levels[Math.min(this.userInfo.level - 1, levels.length - 1)] || '新手'
    },
    
    formattedJoinDate() {
      const date = new Date(this.userInfo.joinDate)
      return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
    }
  },
  async mounted() {
    await this.loadUserData()
  },
  methods: {
    async loadUserData() {
      this.loading = true
      await simulateApiDelay()
      
      // 加载用户统计数据
      const userStats = getUserStats()
      this.learningStats = {
        wordsLearned: userStats.totalWordsLearned,
        daysStreak: userStats.consecutiveDays,
        totalTime: this.formatStudyTime(userStats.totalStudyTime),
        challengesCompleted: userStats.challengeHistory.length,
        averageAccuracy: this.calculateAverageAccuracy(userStats.challengeHistory),
        favoriteWords: userStats.bookmarkedWords?.length || 0
      }
      
      // 生成成就数据
      this.generateAchievements(userStats)
      
      // 生成最近活动
      this.generateRecentActivity(userStats)
      
      this.loading = false
    },
    
    generateAchievements(userStats) {
      this.achievements = [
        {
          id: 'first_word',
          title: '初学者',
          description: '学习第一个单词',
          icon: '🎯',
          unlocked: userStats.totalWordsLearned > 0,
          unlockedAt: userStats.totalWordsLearned > 0 ? '2024-01-15' : null
        },
        {
          id: 'hundred_words',
          title: '百词斩',
          description: '累计学习100个单词',
          icon: '💯',
          unlocked: userStats.totalWordsLearned >= 100,
          unlockedAt: userStats.totalWordsLearned >= 100 ? '2024-02-01' : null
        },
        {
          id: 'week_streak',
          title: '坚持一周',
          description: '连续学习7天',
          icon: '🔥',
          unlocked: userStats.consecutiveDays >= 7,
          unlockedAt: userStats.consecutiveDays >= 7 ? '2024-01-22' : null
        },
        {
          id: 'perfect_score',
          title: '完美主义',
          description: '挑战中获得100%正确率',
          icon: '⭐',
          unlocked: userStats.challengeHistory.some(c => c.accuracy === 100),
          unlockedAt: userStats.challengeHistory.some(c => c.accuracy === 100) ? '2024-01-20' : null
        }
      ]
    },
    
    generateRecentActivity(userStats) {
      this.recentActivity = [
        {
          type: 'learning',
          title: '完成单词学习',
          description: `学习了 ${userStats.dailyStats[userStats.dailyStats.length - 1]?.wordsLearned || 0} 个新单词`,
          time: '2小时前',
          icon: '📚'
        },
        {
          type: 'challenge',
          title: '完成挑战',
          description: `挑战得分 ${userStats.challengeHistory[userStats.challengeHistory.length - 1]?.score || 0}`,
          time: '1天前',
          icon: '🎯'
        },
        {
          type: 'achievement',
          title: '获得成就',
          description: '解锁了"坚持一周"成就',
          time: '3天前',
          icon: '🏆'
        }
      ]
    },
    
    formatStudyTime(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (hours > 0) {
        return `${hours}h${minutes}m`
      } else {
        return `${minutes}m`
      }
    },
    
    calculateAverageAccuracy(challengeHistory) {
      if (!challengeHistory.length) return 0
      const total = challengeHistory.reduce((sum, challenge) => sum + challenge.accuracy, 0)
      return Math.round(total / challengeHistory.length)
    },
    
    getDisplayName() {
      return this.userInfo.nickname || this.userInfo.username || '未登录用户'
    },
    
    getLoginStatus() {
      return `${this.userLevel} · 加入于${this.formattedJoinDate}`
    },
    
    showAvatarUploadModal() {
      this.showAvatarUpload = true
    },
    
    closeAvatarModal() {
      this.showAvatarUpload = false
    },
    
    showEditProfileModal() {
      this.showEditProfile = true
    },
    
    closeEditProfileModal() {
      this.showEditProfile = false
    },
    
    goToPage(path) {
      // 根据路径跳转到对应页面
      const pageMap = {
        '/word-selection': '/pages/word-learning/index',
        '/word-review': '/pages/review/index',
        '/learning-progress': '/pages/statistics/index',
        '/settings': '/pages/settings/index',
        '/help': '/pages/help/index',
        '/about': '/pages/about/index'
      }
      
      const targetPage = pageMap[path]
      if (targetPage) {
        uni.navigateTo({
          url: targetPage,
          fail: () => {
            uni.showToast({
              title: `页面开发中: ${path}`,
              icon: 'none'
            })
          }
        })
      } else {
        uni.showToast({
          title: `跳转到: ${path}`,
          icon: 'none'
        })
      }
    },
    
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 清除用户数据
            this.userInfo = {
              username: '',
              nickname: '',
              avatar: '',
              email: ''
            }
            
            uni.showToast({
              title: '已退出登录',
              icon: 'success'
            })
            
            // 可以跳转到登录页面
            setTimeout(() => {
              uni.reLaunch({
                url: '/pages/index/index'
              })
            }, 1500)
          }
        }
      })
    },
    
    chooseFromGallery() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album'],
        success: (res) => {
          this.userInfo.avatar = res.tempFilePaths[0]
          this.closeAvatarModal()
          uni.showToast({
            title: '头像已更新',
            icon: 'success'
          })
        }
      })
    },
    
    takePhoto() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['camera'],
        success: (res) => {
          this.userInfo.avatar = res.tempFilePaths[0]
          this.closeAvatarModal()
          uni.showToast({
            title: '头像已更新',
            icon: 'success'
          })
        }
      })
    },
    
    saveProfile() {
      // 保存个人资料
      uni.showToast({
        title: '保存成功',
        icon: 'success'
      })
      this.closeEditProfileModal()
    },
    
    toggleSetting(key) {
      this.settings[key] = !this.settings[key]
      
      // 播放音效反馈
      if (this.settings.soundEnabled && key !== 'soundEnabled') {
        audioConfig.playBeep()
      }
      
      uni.showToast({
        title: this.settings[key] ? '已开启' : '已关闭',
        icon: 'none'
      })
    },
    
    viewAchievement(achievement) {
      if (achievement.unlocked) {
        uni.showModal({
          title: achievement.title,
          content: `${achievement.description}\n\n解锁时间: ${achievement.unlockedAt}`,
          showCancel: false
        })
      } else {
        uni.showToast({
          title: '成就未解锁',
          icon: 'none'
        })
      }
    },
    
    refreshData() {
      this.loadUserData()
      uni.showToast({
        title: '数据已刷新',
        icon: 'success'
      })
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 100px;
}

/* 加载状态样式 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 500;
}

/* 用户卡片样式 */
.user-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  gap: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.avatar {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 40px;
  overflow: hidden;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar image {
  width: 100%;
  height: 100%;
}

.default-avatar {
  font-size: 32px;
  font-weight: bold;
  color: #666;
}

.avatar-edit-overlay {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 24px;
  height: 24px;
  background: #667eea;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

.edit-icon {
  font-size: 12px;
  color: white;
}

.user-info {
  flex: 1;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.username {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.edit-btn {
  padding: 6px 12px;
  background: #667eea;
  border-radius: 12px;
  cursor: pointer;
}

.edit-text {
  font-size: 12px;
  color: #ffffff;
  font-weight: 500;
}

.user-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

/* 等级进度样式 */
.level-section {
  margin-bottom: 16px;
}

.level-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.level-text {
  font-size: 16px;
  color: #667eea;
  font-weight: 600;
}

.exp-text {
  font-size: 12px;
  color: #999;
}

.level-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-percent {
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
  min-width: 32px;
}

.user-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 18px;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

/* 成就展示样式 */
.achievements-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.section-subtitle {
  font-size: 14px;
  color: #667eea;
  font-weight: 500;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.achievement-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.2s ease;
}

.achievement-item.unlocked {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.achievement-item:active {
  transform: scale(0.95);
}

.achievement-icon {
  position: relative;
  margin-bottom: 8px;
}

.icon-text {
  font-size: 24px;
}

.lock-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  font-size: 12px;
}

.achievement-title {
  font-size: 10px;
  text-align: center;
  font-weight: 500;
}

/* 最近活动样式 */
.activity-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.refresh-btn {
  padding: 6px 12px;
  background: #667eea;
  border-radius: 12px;
  cursor: pointer;
}

.refresh-text {
  font-size: 12px;
  color: #ffffff;
  font-weight: 500;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  gap: 12px;
}

.activity-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #667eea;
  border-radius: 20px;
  flex-shrink: 0;
}

.activity-icon .icon-text {
  font-size: 18px;
  color: white;
}

.activity-info {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  display: block;
}

.activity-desc {
  font-size: 12px;
  color: #666;
  display: block;
}

.activity-time {
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
}

/* 快捷设置样式 */
.settings-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.setting-item:active {
  background: #e9ecef;
}

.setting-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-icon {
  font-size: 18px;
}

.setting-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.setting-toggle {
  width: 44px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 12px;
  position: relative;
  transition: background-color 0.2s;
}

.setting-toggle.active {
  background: #667eea;
}

.toggle-thumb {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 10px;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.setting-toggle.active .toggle-thumb {
  transform: translateX(20px);
}

/* 功能菜单样式 */
.menu-section {
  margin-bottom: 30px;
}

.menu-group {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  margin-bottom: 15px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background-color: #f8f9fa;
}

.menu-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  margin-right: 15px;
  font-size: 18px;
  color: white;
}

.menu-text {
  flex: 1;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.menu-arrow {
  font-size: 18px;
  color: #ccc;
}

/* 退出登录样式 */
.logout-section {
  margin-bottom: 20px;
}

.logout-btn {
  width: 100%;
  height: 50px;
  background: rgba(255, 59, 48, 0.9);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.2s;
  box-shadow: 0 4px 20px rgba(255, 59, 48, 0.3);
}

.logout-btn:active {
  transform: scale(0.98);
  background: rgba(255, 59, 48, 1);
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
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 30px;
  margin: 20px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.close-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 15px;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  transition: background-color 0.2s;
}

.close-btn:active {
  background: #e0e0e0;
}

/* 头像上传弹窗 */
.avatar-modal {
  max-width: 320px;
}

.avatar-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.option-btn {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.2s;
  cursor: pointer;
}

.option-btn:active {
  background-color: #e9ecef;
  transform: scale(0.98);
}

.option-icon {
  font-size: 24px;
  margin-right: 15px;
}

.option-text {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

/* 编辑个人资料弹窗 */
.edit-profile-modal {
  max-width: 400px;
}

.edit-form {
  margin-bottom: 24px;
}

.form-item {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  color: #333;
  background: #f8f9fa;
  transition: all 0.2s;
}

.form-input:focus {
  border-color: #667eea;
  background: white;
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.cancel-btn,
.save-btn {
  flex: 1;
  height: 44px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #f8f9fa;
  color: #666;
}

.cancel-btn:active {
  background: #e9ecef;
  transform: scale(0.98);
}

.save-btn {
  background: #667eea;
  color: white;
}

.save-btn:active {
  background: #5a6fd8;
  transform: scale(0.98);
}
</style>