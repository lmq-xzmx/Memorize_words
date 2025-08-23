<template>
  <view class="community-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">👥 社区</text>
      <text class="page-subtitle">与学习伙伴一起进步</text>
    </view>

    <!-- 功能导航 -->
    <view class="feature-nav">
      <view 
        v-for="feature in features" 
        :key="feature.id"
        class="feature-item"
        @click="navigateToFeature(feature)"
      >
        <text class="feature-icon">{{ feature.icon }}</text>
        <text class="feature-name">{{ feature.name }}</text>
      </view>
    </view>

    <!-- 社区动态 -->
    <view class="community-content">
      <!-- 热门讨论 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">🔥 热门讨论</text>
          <text class="section-more" @click="viewAllDiscussions">查看全部</text>
        </view>
        
        <view class="discussion-list">
          <view 
            v-for="discussion in hotDiscussions" 
            :key="discussion.id"
            class="discussion-card"
            @click="viewDiscussion(discussion)"
          >
            <view class="discussion-header">
              <image class="user-avatar" :src="discussion.author.avatar" mode="aspectFill"></image>
              
              <view class="user-info">
                <text class="user-name">{{ discussion.author.name }}</text>
                <text class="post-time">{{ discussion.time }}</text>
              </view>
              
              <view class="discussion-tag" :class="discussion.category">
                <text class="tag-text">{{ discussion.categoryName }}</text>
              </view>
            </view>
            
            <view class="discussion-content">
              <text class="discussion-title">{{ discussion.title }}</text>
              <text class="discussion-preview">{{ discussion.preview }}</text>
            </view>
            
            <view class="discussion-stats">
              <view class="stat-item">
                <text class="stat-icon">💬</text>
                <text class="stat-text">{{ discussion.replies }}</text>
              </view>
              
              <view class="stat-item">
                <text class="stat-icon">👍</text>
                <text class="stat-text">{{ discussion.likes }}</text>
              </view>
              
              <view class="stat-item">
                <text class="stat-icon">👀</text>
                <text class="stat-text">{{ discussion.views }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 学习小组 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">📚 学习小组</text>
          <text class="section-more" @click="viewAllGroups">查看全部</text>
        </view>
        
        <scroll-view scroll-x="true" class="groups-scroll">
          <view class="groups-list">
            <view 
              v-for="group in studyGroups" 
              :key="group.id"
              class="group-card"
              @click="joinGroup(group)"
            >
              <image class="group-cover" :src="group.cover" mode="aspectFill"></image>
              
              <view class="group-info">
                <text class="group-name">{{ group.name }}</text>
                <text class="group-description">{{ group.description }}</text>
                
                <view class="group-stats">
                  <text class="group-members">👥 {{ group.members }}人</text>
                  <text class="group-level">{{ group.level }}</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 每日挑战 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">⚡ 每日挑战</text>
          <text class="section-more" @click="viewAllChallenges">历史挑战</text>
        </view>
        
        <view class="challenge-card">
          <view class="challenge-header">
            <text class="challenge-title">{{ todayChallenge.title }}</text>
            <view class="challenge-reward">
              <text class="reward-icon">🏆</text>
              <text class="reward-text">{{ todayChallenge.reward }}</text>
            </view>
          </view>
          
          <text class="challenge-description">{{ todayChallenge.description }}</text>
          
          <view class="challenge-progress">
            <view class="progress-info">
              <text class="progress-text">进度: {{ todayChallenge.progress }}%</text>
              <text class="participants-text">{{ todayChallenge.participants }}人参与</text>
            </view>
            
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: todayChallenge.progress + '%' }"></view>
            </view>
          </view>
          
          <button class="challenge-btn" @click="joinChallenge">
            {{ todayChallenge.joined ? '继续挑战' : '参与挑战' }}
          </button>
        </view>
      </view>

      <!-- 排行榜 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">🏆 本周排行榜</text>
          <text class="section-more" @click="viewFullRanking">完整榜单</text>
        </view>
        
        <view class="ranking-list">
          <view 
            v-for="(user, index) in weeklyRanking" 
            :key="user.id"
            class="ranking-item"
            :class="{ 'top-three': index < 3 }"
          >
            <view class="rank-number" :class="getRankClass(index)">
              <text class="rank-text">{{ index + 1 }}</text>
            </view>
            
            <image class="rank-avatar" :src="user.avatar" mode="aspectFill"></image>
            
            <view class="rank-info">
              <text class="rank-name">{{ user.name }}</text>
              <text class="rank-score">{{ user.score }}分</text>
            </view>
            
            <view class="rank-badge" v-if="index < 3">
              <text class="badge-icon">{{ getBadgeIcon(index) }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      features: [
        { id: 1, name: '讨论区', icon: '💬' },
        { id: 2, name: '学习小组', icon: '👥' },
        { id: 3, name: '问答', icon: '❓' },
        { id: 4, name: '分享', icon: '📤' },
        { id: 5, name: '活动', icon: '🎉' }
      ],
      
      hotDiscussions: [
        {
          id: 1,
          title: '如何快速记忆英语单词？',
          preview: '分享一些我在学习过程中总结的记忆技巧...',
          author: {
            name: '学习达人',
            avatar: '/static/images/avatar1.jpg'
          },
          time: '2小时前',
          category: 'study',
          categoryName: '学习方法',
          replies: 23,
          likes: 45,
          views: 156
        },
        {
          id: 2,
          title: '英语口语练习的最佳时间',
          preview: '根据科学研究，这些时间段练习口语效果最好...',
          author: {
            name: '口语专家',
            avatar: '/static/images/avatar2.jpg'
          },
          time: '4小时前',
          category: 'speaking',
          categoryName: '口语练习',
          replies: 18,
          likes: 32,
          views: 89
        },
        {
          id: 3,
          title: '零基础如何开始学英语？',
          preview: '给初学者的一些建议和学习路径规划...',
          author: {
            name: '英语老师',
            avatar: '/static/images/avatar3.jpg'
          },
          time: '6小时前',
          category: 'beginner',
          categoryName: '新手指南',
          replies: 35,
          likes: 67,
          views: 234
        }
      ],
      
      studyGroups: [
        {
          id: 1,
          name: '四级冲刺小组',
          description: '一起备考英语四级',
          cover: '/static/images/group1.jpg',
          members: 128,
          level: '初级'
        },
        {
          id: 2,
          name: '口语练习营',
          description: '每日口语打卡',
          cover: '/static/images/group2.jpg',
          members: 89,
          level: '中级'
        },
        {
          id: 3,
          name: '商务英语学习',
          description: '职场英语提升',
          cover: '/static/images/group3.jpg',
          members: 56,
          level: '高级'
        }
      ],
      
      todayChallenge: {
        title: '今日单词挑战',
        description: '学习并掌握20个新单词，完成相关练习',
        reward: '50积分',
        progress: 65,
        participants: 1234,
        joined: false
      },
      
      weeklyRanking: [
        {
          id: 1,
          name: '学霸小王',
          avatar: '/static/images/rank1.jpg',
          score: 2580
        },
        {
          id: 2,
          name: '努力小李',
          avatar: '/static/images/rank2.jpg',
          score: 2340
        },
        {
          id: 3,
          name: '坚持小张',
          avatar: '/static/images/rank3.jpg',
          score: 2156
        },
        {
          id: 4,
          name: '进步小陈',
          avatar: '/static/images/rank4.jpg',
          score: 1987
        },
        {
          id: 5,
          name: '勤奋小刘',
          avatar: '/static/images/rank5.jpg',
          score: 1834
        }
      ]
    }
  },
  
  onLoad() {
    this.loadCommunityData()
  },
  
  methods: {
    /**
     * 加载社区数据
     */
    loadCommunityData() {
      // 模拟数据加载
      console.log('加载社区数据')
    },
    
    /**
     * 导航到功能页面
     */
    navigateToFeature(feature) {
      console.log('导航到功能:', feature.name)
      uni.showToast({
        title: `${feature.name}功能开发中...`,
        icon: 'none'
      })
    },
    
    /**
     * 查看讨论详情
     */
    viewDiscussion(discussion) {
      console.log('查看讨论:', discussion.title)
      uni.showToast({
        title: '讨论详情页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 查看所有讨论
     */
    viewAllDiscussions() {
      uni.showToast({
        title: '讨论列表页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 加入学习小组
     */
    joinGroup(group) {
      console.log('加入小组:', group.name)
      uni.showToast({
        title: '小组详情页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 查看所有小组
     */
    viewAllGroups() {
      uni.showToast({
        title: '小组列表页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 参与挑战
     */
    joinChallenge() {
      if (!this.todayChallenge.joined) {
        this.todayChallenge.joined = true
        this.todayChallenge.participants += 1
        uni.showToast({
          title: '成功参与挑战！',
          icon: 'success'
        })
      } else {
        uni.showToast({
          title: '挑战页面开发中...',
          icon: 'none'
        })
      }
    },
    
    /**
     * 查看所有挑战
     */
    viewAllChallenges() {
      uni.showToast({
        title: '挑战历史页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 查看完整排行榜
     */
    viewFullRanking() {
      uni.showToast({
        title: '完整排行榜页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 获取排名样式类
     */
    getRankClass(index) {
      if (index === 0) return 'first'
      if (index === 1) return 'second'
      if (index === 2) return 'third'
      return 'normal'
    },
    
    /**
     * 获取徽章图标
     */
    getBadgeIcon(index) {
      if (index === 0) return '🥇'
      if (index === 1) return '🥈'
      if (index === 2) return '🥉'
      return ''
    }
  }
}
</script>

<style scoped>
.community-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 200rpx;
}

.page-header {
  text-align: center;
  padding: 60rpx 32rpx 40rpx;
  
  .page-title {
    display: block;
    font-size: 56rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 16rpx;
  }
  
  .page-subtitle {
    display: block;
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}

.feature-nav {
  display: flex;
  justify-content: space-around;
  padding: 0 32rpx 32rpx;
  
  .feature-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 16rpx;
    transition: all 0.3s ease;
    
    &:active {
      transform: scale(0.95);
      background: rgba(255, 255, 255, 0.3);
    }
    
    .feature-icon {
      font-size: 32rpx;
      margin-bottom: 8rpx;
    }
    
    .feature-name {
      font-size: 22rpx;
      color: #ffffff;
    }
  }
}

.community-content {
  padding: 0 32rpx;
  
  .section {
    margin-bottom: 48rpx;
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24rpx;
      
      .section-title {
        font-size: 32rpx;
        font-weight: bold;
        color: #ffffff;
      }
      
      .section-more {
        font-size: 24rpx;
        color: rgba(255, 255, 255, 0.7);
      }
    }
  }
}

.discussion-list {
  .discussion-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 16rpx;
    transition: all 0.3s ease;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    &:active {
      transform: scale(0.98);
    }
    
    .discussion-header {
      display: flex;
      align-items: center;
      margin-bottom: 16rpx;
      
      .user-avatar {
        width: 60rpx;
        height: 60rpx;
        border-radius: 50%;
        margin-right: 16rpx;
      }
      
      .user-info {
        flex: 1;
        
        .user-name {
          display: block;
          font-size: 26rpx;
          font-weight: bold;
          color: #333333;
          margin-bottom: 4rpx;
        }
        
        .post-time {
          display: block;
          font-size: 22rpx;
          color: #999999;
        }
      }
      
      .discussion-tag {
        padding: 8rpx 16rpx;
        border-radius: 16rpx;
        
        &.study {
          background: #e6f7ff;
          
          .tag-text {
            color: #1890ff;
          }
        }
        
        &.speaking {
          background: #f6ffed;
          
          .tag-text {
            color: #52c41a;
          }
        }
        
        &.beginner {
          background: #fff2e8;
          
          .tag-text {
            color: #fa8c16;
          }
        }
        
        .tag-text {
          font-size: 20rpx;
          font-weight: bold;
        }
      }
    }
    
    .discussion-content {
      margin-bottom: 16rpx;
      
      .discussion-title {
        display: block;
        font-size: 30rpx;
        font-weight: bold;
        color: #333333;
        margin-bottom: 8rpx;
        line-height: 1.4;
      }
      
      .discussion-preview {
        display: block;
        font-size: 26rpx;
        color: #666666;
        line-height: 1.5;
      }
    }
    
    .discussion-stats {
      display: flex;
      align-items: center;
      
      .stat-item {
        display: flex;
        align-items: center;
        margin-right: 24rpx;
        
        .stat-icon {
          font-size: 20rpx;
          margin-right: 4rpx;
        }
        
        .stat-text {
          font-size: 22rpx;
          color: #999999;
        }
      }
    }
  }
}

.groups-scroll {
  white-space: nowrap;
  
  .groups-list {
    display: flex;
    
    .group-card {
      flex-shrink: 0;
      width: 280rpx;
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      margin-right: 16rpx;
      overflow: hidden;
      transition: all 0.3s ease;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      &:active {
        transform: scale(0.95);
      }
      
      .group-cover {
        width: 100%;
        height: 160rpx;
      }
      
      .group-info {
        padding: 20rpx;
        
        .group-name {
          display: block;
          font-size: 28rpx;
          font-weight: bold;
          color: #333333;
          margin-bottom: 8rpx;
        }
        
        .group-description {
          display: block;
          font-size: 24rpx;
          color: #666666;
          margin-bottom: 12rpx;
          line-height: 1.4;
        }
        
        .group-stats {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          .group-members {
            font-size: 22rpx;
            color: #999999;
          }
          
          .group-level {
            font-size: 20rpx;
            color: #1890ff;
            background: #e6f7ff;
            padding: 4rpx 8rpx;
            border-radius: 8rpx;
          }
        }
      }
    }
  }
}

.challenge-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 32rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  
  .challenge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
    
    .challenge-title {
      font-size: 32rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .challenge-reward {
      display: flex;
      align-items: center;
      background: #fff7e6;
      padding: 8rpx 16rpx;
      border-radius: 16rpx;
      
      .reward-icon {
        font-size: 20rpx;
        margin-right: 4rpx;
      }
      
      .reward-text {
        font-size: 22rpx;
        color: #fa8c16;
        font-weight: bold;
      }
    }
  }
  
  .challenge-description {
    display: block;
    font-size: 26rpx;
    color: #666666;
    line-height: 1.5;
    margin-bottom: 20rpx;
  }
  
  .challenge-progress {
    margin-bottom: 24rpx;
    
    .progress-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 12rpx;
      
      .progress-text {
        font-size: 24rpx;
        color: #333333;
        font-weight: bold;
      }
      
      .participants-text {
        font-size: 22rpx;
        color: #999999;
      }
    }
    
    .progress-bar {
      height: 8rpx;
      background: #f5f5f5;
      border-radius: 4rpx;
      overflow: hidden;
      
      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
        transition: width 0.3s ease;
      }
    }
  }
  
  .challenge-btn {
    width: 100%;
    height: 80rpx;
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: #ffffff;
    border: none;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: bold;
    transition: all 0.3s ease;
    
    &:active {
      transform: scale(0.98);
    }
  }
}

.ranking-list {
  .ranking-item {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    padding: 20rpx 24rpx;
    margin-bottom: 12rpx;
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    &.top-three {
      background: linear-gradient(135deg, #fff7e6 0%, #fffbe6 100%);
    }
    
    .rank-number {
      width: 48rpx;
      height: 48rpx;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16rpx;
      
      &.first {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
      }
      
      &.second {
        background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
      }
      
      &.third {
        background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
      }
      
      &.normal {
        background: #f5f5f5;
      }
      
      .rank-text {
        font-size: 22rpx;
        font-weight: bold;
        color: #333333;
      }
    }
    
    .rank-avatar {
      width: 60rpx;
      height: 60rpx;
      border-radius: 50%;
      margin-right: 16rpx;
    }
    
    .rank-info {
      flex: 1;
      
      .rank-name {
        display: block;
        font-size: 28rpx;
        font-weight: bold;
        color: #333333;
        margin-bottom: 4rpx;
      }
      
      .rank-score {
        display: block;
        font-size: 24rpx;
        color: #666666;
      }
    }
    
    .rank-badge {
      .badge-icon {
        font-size: 32rpx;
      }
    }
  }
}
</style>