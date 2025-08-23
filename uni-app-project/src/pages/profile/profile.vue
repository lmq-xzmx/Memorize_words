<template>
  <view class="profile-page">
    <!-- 用户信息头部 -->
    <view class="profile-header">
      <view class="avatar-section">
        <image 
          class="user-avatar" 
          :src="userInfo.avatar || '/static/default-avatar.png'"
          mode="aspectFill"
        />
        <view class="avatar-edit" @click="changeAvatar">
          <text class="edit-icon">📷</text>
        </view>
      </view>
      
      <view class="user-info">
        <text class="username">{{ userInfo.username || '用户' }}</text>
        <text class="user-role">{{ getRoleDisplayName(userInfo.role) }}</text>
        <text class="join-date">加入时间: {{ formatDate(userInfo.joinDate) }}</text>
      </view>
    </view>

    <!-- 学习统计 -->
    <view class="stats-section">
      <text class="section-title">📊 学习统计</text>
      
      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-icon">📚</text>
          <text class="stat-number">{{ learningStats.totalWords }}</text>
          <text class="stat-label">掌握单词</text>
        </view>
        
        <view class="stat-card">
          <text class="stat-icon">🔥</text>
          <text class="stat-number">{{ learningStats.streak }}</text>
          <text class="stat-label">连续天数</text>
        </view>
        
        <view class="stat-card">
          <text class="stat-icon">⏱️</text>
          <text class="stat-number">{{ learningStats.totalTime }}</text>
          <text class="stat-label">学习时长(h)</text>
        </view>
        
        <view class="stat-card">
          <text class="stat-icon">🏆</text>
          <text class="stat-number">{{ learningStats.achievements }}</text>
          <text class="stat-label">获得成就</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <text class="section-title">⚙️ 个人设置</text>
      
      <view class="menu-list">
        <view 
          v-for="item in menuItems" 
          :key="item.id"
          class="menu-item"
          @click="handleMenuClick(item)"
        >
          <text class="menu-icon">{{ item.icon }}</text>
          <text class="menu-title">{{ item.title }}</text>
          <text class="menu-arrow">></text>
        </view>
      </view>
    </view>

    <!-- 学习进度 -->
    <view class="progress-section">
      <text class="section-title">📈 本周进度</text>
      
      <view class="progress-chart">
        <view 
          v-for="(day, index) in weekProgress" 
          :key="index"
          class="progress-day"
        >
          <view 
            class="progress-bar"
            :style="{ height: day.progress + '%' }"
          ></view>
          <text class="day-label">{{ day.label }}</text>
        </view>
      </view>
    </view>

    <!-- 最近成就 -->
    <view class="achievements-section">
      <text class="section-title">🏅 最近成就</text>
      
      <view class="achievement-list">
        <view 
          v-for="achievement in recentAchievements" 
          :key="achievement.id"
          class="achievement-item"
        >
          <text class="achievement-icon">{{ achievement.icon }}</text>
          <view class="achievement-info">
            <text class="achievement-title">{{ achievement.title }}</text>
            <text class="achievement-desc">{{ achievement.description }}</text>
            <text class="achievement-date">{{ formatDate(achievement.date) }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { ROLE_DISPLAY_NAMES } from '@/config/menuConfig.js'

export default {
  name: 'Profile',
  data() {
    return {
      // 用户信息
      userInfo: {
        username: '学习者小明',
        role: 'student',
        avatar: '',
        joinDate: '2024-01-15'
      },
      
      // 学习统计
      learningStats: {
        totalWords: 1248,
        streak: 15,
        totalTime: 127,
        achievements: 8
      },
      
      // 菜单项
      menuItems: [
        {
          id: 'edit-profile',
          title: '编辑资料',
          icon: '✏️',
          path: '/pages/edit-profile/edit-profile'
        },
        {
          id: 'learning-settings',
          title: '学习设置',
          icon: '📚',
          path: '/pages/learning-settings/learning-settings'
        },
        {
          id: 'notification',
          title: '通知设置',
          icon: '🔔',
          path: '/pages/notification-settings/notification-settings'
        },
        {
          id: 'privacy',
          title: '隐私设置',
          icon: '🔒',
          path: '/pages/privacy-settings/privacy-settings'
        },
        {
          id: 'help',
          title: '帮助中心',
          icon: '❓',
          path: '/pages/help/help'
        },
        {
          id: 'about',
          title: '关于我们',
          icon: 'ℹ️',
          path: '/pages/about/about'
        }
      ],
      
      // 本周进度
      weekProgress: [
        { label: '周一', progress: 80 },
        { label: '周二', progress: 65 },
        { label: '周三', progress: 90 },
        { label: '周四', progress: 75 },
        { label: '周五', progress: 95 },
        { label: '周六', progress: 60 },
        { label: '周日', progress: 40 }
      ],
      
      // 最近成就
      recentAchievements: [
        {
          id: 1,
          title: '连续学习达人',
          description: '连续学习15天',
          icon: '🔥',
          date: '2024-01-20'
        },
        {
          id: 2,
          title: '单词大师',
          description: '掌握1000个单词',
          icon: '📚',
          date: '2024-01-18'
        },
        {
          id: 3,
          title: '挑战者',
          description: '完成10次挑战',
          icon: '⚡',
          date: '2024-01-15'
        }
      ]
    }
  },
  
  onLoad() {
    this.loadUserProfile()
  },
  
  methods: {
    /**
     * 加载用户资料
     */
    loadUserProfile() {
      // 模拟加载用户数据
      console.log('加载用户资料...')
    },
    
    /**
     * 获取角色显示名称
     */
    getRoleDisplayName(role) {
      return ROLE_DISPLAY_NAMES[role] || '用户'
    },
    
    /**
     * 格式化日期
     */
    formatDate(dateString) {
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    },
    
    /**
     * 更换头像
     */
    changeAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.userInfo.avatar = res.tempFilePaths[0]
          uni.showToast({
            title: '头像更新成功',
            icon: 'success'
          })
        },
        fail: () => {
          uni.showToast({
            title: '头像更新失败',
            icon: 'none'
          })
        }
      })
    },
    
    /**
     * 处理菜单点击
     */
    handleMenuClick(item) {
      console.log('点击菜单:', item.title)
      
      if (item.path) {
        uni.navigateTo({
          url: item.path,
          fail: () => {
            uni.showToast({
              title: '页面开发中...',
              icon: 'none'
            })
          }
        })
      }
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 32rpx 200rpx;
}

.profile-header {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
  
  .avatar-section {
    position: relative;
    margin-right: 32rpx;
    
    .user-avatar {
      width: 120rpx;
      height: 120rpx;
      border-radius: 60rpx;
      border: 4rpx solid #ffffff;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    }
    
    .avatar-edit {
      position: absolute;
      bottom: -8rpx;
      right: -8rpx;
      width: 48rpx;
      height: 48rpx;
      background: #007aff;
      border-radius: 24rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2rpx 8rpx rgba(0, 122, 255, 0.3);
      
      .edit-icon {
        font-size: 24rpx;
        color: #ffffff;
      }
    }
  }
  
  .user-info {
    flex: 1;
    
    .username {
      display: block;
      font-size: 36rpx;
      font-weight: bold;
      color: #333333;
      margin-bottom: 8rpx;
    }
    
    .user-role {
      display: block;
      font-size: 26rpx;
      color: #007aff;
      background: rgba(0, 122, 255, 0.1);
      padding: 4rpx 12rpx;
      border-radius: 12rpx;
      margin-bottom: 12rpx;
      width: fit-content;
    }
    
    .join-date {
      display: block;
      font-size: 24rpx;
      color: #666666;
    }
  }
}

.stats-section {
  margin-bottom: 40rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16rpx;
    
    .stat-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 32rpx 24rpx;
      text-align: center;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      .stat-icon {
        display: block;
        font-size: 40rpx;
        margin-bottom: 12rpx;
      }
      
      .stat-number {
        display: block;
        font-size: 36rpx;
        font-weight: bold;
        color: #333333;
        margin-bottom: 8rpx;
      }
      
      .stat-label {
        display: block;
        font-size: 24rpx;
        color: #666666;
      }
    }
  }
}

.menu-section {
  margin-bottom: 40rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .menu-list {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    overflow: hidden;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    .menu-item {
      display: flex;
      align-items: center;
      padding: 32rpx 24rpx;
      border-bottom: 1rpx solid #f5f5f5;
      transition: background 0.2s ease;
      
      &:last-child {
        border-bottom: none;
      }
      
      &:active {
        background: rgba(0, 122, 255, 0.05);
      }
      
      .menu-icon {
        font-size: 32rpx;
        margin-right: 24rpx;
      }
      
      .menu-title {
        flex: 1;
        font-size: 28rpx;
        color: #333333;
      }
      
      .menu-arrow {
        font-size: 24rpx;
        color: #999999;
      }
    }
  }
}

.progress-section {
  margin-bottom: 40rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .progress-chart {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    padding: 32rpx 24rpx;
    display: flex;
    align-items: end;
    justify-content: space-between;
    height: 200rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    .progress-day {
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 1;
      
      .progress-bar {
        width: 24rpx;
        background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 12rpx;
        margin-bottom: 16rpx;
        min-height: 8rpx;
        transition: height 0.3s ease;
      }
      
      .day-label {
        font-size: 20rpx;
        color: #666666;
      }
    }
  }
}

.achievements-section {
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .achievement-list {
    .achievement-item {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 24rpx;
      margin-bottom: 16rpx;
      display: flex;
      align-items: center;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      .achievement-icon {
        font-size: 48rpx;
        margin-right: 24rpx;
      }
      
      .achievement-info {
        flex: 1;
        
        .achievement-title {
          display: block;
          font-size: 28rpx;
          font-weight: bold;
          color: #333333;
          margin-bottom: 8rpx;
        }
        
        .achievement-desc {
          display: block;
          font-size: 24rpx;
          color: #666666;
          margin-bottom: 8rpx;
        }
        
        .achievement-date {
          display: block;
          font-size: 20rpx;
          color: #999999;
        }
      }
    }
  }
}
</style>