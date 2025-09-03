<template>
  <BaseLayout 
    title="英语学习首页"
    :show-header="true"
    :show-sidebar="false"
    :show-tab-bar="true"
    layout-type="default"
    @menu-click="handleMenuClick"
  >
    <view class="index-container">
      <!-- 头部区域 -->
      <view class="header">
      <view class="header-content">
        <view class="user-info">
          <image 
            class="avatar" 
            :src="userInfo.avatar || '/static/images/default-avatar.png'"
            mode="aspectFill"
          ></image>
          <view class="user-text">
            <text class="greeting">{{ greeting }}</text>
            <text class="username">{{ displayName }}</text>
          </view>
        </view>
        <view class="header-actions">
          <view class="action-btn" @tap="handleNotification">
            <text class="action-icon">🔔</text>
            <view v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</view>
          </view>
          <view class="action-btn" @tap="handleSettings">
            <text class="action-icon">⚙️</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 学习统计卡片 -->
    <view class="stats-card">
      <view class="stats-header">
        <text class="stats-title">今日学习</text>
        <text class="stats-date">{{ todayDate }}</text>
      </view>
      <view class="stats-content">
        <view class="stat-item">
          <text class="stat-number">{{ todayStats.wordsLearned }}</text>
          <text class="stat-label">已学单词</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-number">{{ todayStats.studyTime }}</text>
          <text class="stat-label">学习时长(分钟)</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-number">{{ todayStats.accuracy }}%</text>
          <text class="stat-label">正确率</text>
        </view>
      </view>
    </view>
    
    <!-- 快速入口 -->
    <view class="quick-actions">
      <view class="section-title">
        <text class="title-text">快速开始</text>
        <text class="title-subtitle">选择你想要的学习方式</text>
      </view>
      <view class="actions-grid">
        <view 
          class="action-item" 
          v-for="action in quickActions" 
          :key="action.id"
          @tap="handleQuickAction(action)"
        >
          <view class="action-icon-wrapper" :style="{ backgroundColor: action.color }">
            <text class="action-icon">{{ action.icon }}</text>
          </view>
          <text class="action-title">{{ action.title }}</text>
          <text class="action-desc">{{ action.description }}</text>
        </view>
      </view>
    </view>
    
    <!-- 学习进度 -->
    <view class="progress-section">
      <view class="section-title">
        <text class="title-text">学习进度</text>
        <text class="title-more" @tap="viewAllProgress">查看全部</text>
      </view>
      <view class="progress-list">
        <view 
          class="progress-item" 
          v-for="course in recentCourses" 
          :key="course.id"
          @tap="continueCourse(course)"
        >
          <view class="course-info">
            <text class="course-title">{{ course.title }}</text>
            <text class="course-desc">{{ course.description }}</text>
            <view class="progress-bar">
              <view 
                class="progress-fill" 
                :style="{ width: course.progress + '%' }"
              ></view>
            </view>
            <text class="progress-text">{{ course.progress }}% 完成</text>
          </view>
          <view class="course-action">
            <text class="continue-btn">继续学习</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 推荐内容 -->
    <view class="recommendations">
      <view class="section-title">
        <text class="title-text">为你推荐</text>
        <text class="title-subtitle">基于你的学习情况</text>
      </view>
      <scroll-view class="recommend-scroll" scroll-x="true" show-scrollbar="false">
        <view class="recommend-list">
          <view 
            class="recommend-item" 
            v-for="item in recommendations" 
            :key="item.id"
            @tap="openRecommendation(item)"
          >
            <image class="recommend-image" :src="item.image" mode="aspectFill"></image>
            <view class="recommend-content">
              <text class="recommend-title">{{ item.title }}</text>
              <text class="recommend-desc">{{ item.description }}</text>
              <view class="recommend-meta">
                <text class="recommend-tag">{{ item.tag }}</text>
                <text class="recommend-time">{{ item.duration }}</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>
    
      <!-- 底部间距 -->
      <view class="bottom-spacing"></view>
    </view>
  </BaseLayout>
</template>

<script>
  import { mapState, mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Index',
    data() {
      return {
        unreadCount: 3,
        todayStats: {
          wordsLearned: 25,
          studyTime: 45,
          accuracy: 85
        },
        quickActions: [
          {
            id: 1,
            title: '斩词练习',
            description: '快速记忆单词',
            icon: '📚',
            color: '#FF6B6B',
            path: '/pages/word/word'
          },
          {
            id: 2,
            title: '听力训练',
            description: '提升听力水平',
            icon: '🎧',
            color: '#4ECDC4',
            path: '/pages/learning/listening'
          },
          {
            id: 3,
            title: '语法练习',
            description: '掌握语法规则',
            icon: '📝',
            color: '#45B7D1',
            path: '/pages/learning/grammar'
          },
          {
            id: 4,
            title: '口语练习',
            description: '提高口语表达',
            icon: '🗣️',
            color: '#96CEB4',
            path: '/pages/learning/speaking'
          }
        ],
        recentCourses: [
          {
            id: 1,
            title: '基础词汇 1000',
            description: '掌握日常基础词汇',
            progress: 65
          },
          {
            id: 2,
            title: '商务英语入门',
            description: '职场英语必备',
            progress: 30
          },
          {
            id: 3,
            title: '旅游英语',
            description: '出国旅游必备用语',
            progress: 80
          }
        ],
        recommendations: [
          {
            id: 1,
            title: '每日一句',
            description: '精选英语美句',
            image: '/static/images/daily-sentence.jpg',
            tag: '美句',
            duration: '2分钟'
          },
          {
            id: 2,
            title: '英语新闻',
            description: '时事英语阅读',
            image: '/static/images/english-news.jpg',
            tag: '新闻',
            duration: '5分钟'
          },
          {
            id: 3,
            title: '英语歌曲',
            description: '在音乐中学英语',
            image: '/static/images/english-songs.jpg',
            tag: '音乐',
            duration: '3分钟'
          }
        ]
      }
    },
    computed: {
      ...mapState('user', ['userInfo', 'isLoggedIn']),
      ...mapGetters('app', ['statusBarHeight']),
      
      greeting() {
        const hour = new Date().getHours()
        if (hour < 6) {
          return '夜深了'
        } else if (hour < 12) {
          return '早上好'
        } else if (hour < 18) {
          return '下午好'
        } else {
          return '晚上好'
        }
      },
      
      displayName() {
        if (!this.isLoggedIn) {
          return '游客'
        }
        return this.userInfo.nickname || this.userInfo.username || '学习者'
      },
      
      todayDate() {
        const today = new Date()
        const month = today.getMonth() + 1
        const date = today.getDate()
        return `${month}月${date}日`
      }
    },
    onLoad() {
      this.initPage()
    },
    onShow() {
      this.refreshData()
    },
    onPullDownRefresh() {
      this.refreshData().finally(() => {
        uni.stopPullDownRefresh()
      })
    },
    methods: {
      ...mapActions('user', ['getUserInfo']),
      ...mapActions('app', ['navigateTo', 'switchTab', 'showToast']),
      
      // 初始化页面
      async initPage() {
        try {
          if (this.isLoggedIn) {
            await this.getUserInfo()
            await this.loadTodayStats()
          }
        } catch (error) {
          console.error('页面初始化失败:', error)
        }
      },
      
      // 刷新数据
      async refreshData() {
        try {
          await Promise.all([
            this.loadTodayStats(),
            this.loadRecentCourses(),
            this.loadRecommendations()
          ])
        } catch (error) {
          console.error('刷新数据失败:', error)
        }
      },
      
      // 加载今日统计
      async loadTodayStats() {
        try {
          // 这里应该调用实际的API
          // const stats = await getUserLearningStats()
          // this.todayStats = stats
          console.log('加载今日统计')
        } catch (error) {
          console.error('加载今日统计失败:', error)
        }
      },
      
      // 加载最近课程
      async loadRecentCourses() {
        try {
          // 这里应该调用实际的API
          console.log('加载最近课程')
        } catch (error) {
          console.error('加载最近课程失败:', error)
        }
      },
      
      // 加载推荐内容
      async loadRecommendations() {
        try {
          // 这里应该调用实际的API
          console.log('加载推荐内容')
        } catch (error) {
          console.error('加载推荐内容失败:', error)
        }
      },
      
      // 处理通知
      handleNotification() {
        this.navigateTo({
          url: '/pages/notification/notification'
        })
      },
      
      // 处理设置
      handleSettings() {
        this.navigateTo({
          url: '/pages/settings/settings'
        })
      },
      
      // 处理快速操作
      handleQuickAction(action) {
        if (action.path.startsWith('/pages/word/') || 
            action.path.startsWith('/pages/tools/') || 
            action.path.startsWith('/pages/fashion/') || 
            action.path.startsWith('/pages/profile/')) {
          this.switchTab({
            url: action.path
          })
        } else {
          this.navigateTo({
            url: action.path
          })
        }
      },
      
      // 查看全部进度
      viewAllProgress() {
        this.navigateTo({
          url: '/pages/progress/progress'
        })
      },
      
      // 继续课程
      continueCourse(course) {
        this.navigateTo({
          url: `/pages/course/course?id=${course.id}`
        })
      },
      
      // 打开推荐内容
      openRecommendation(item) {
        this.navigateTo({
          url: `/pages/content/content?id=${item.id}&type=${item.tag}`
        })
      },
      
      // 处理菜单点击
      handleMenuClick(menuItem) {
        console.log('菜单点击:', menuItem)
        // 菜单点击事件已在BaseLayout中处理
        // 这里可以添加额外的处理逻辑
      }
    }
  }
</script>

<style>
  .index-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  }
  
  .status-bar {
    background: #ffffff;
  }
  
  .header {
    background: #ffffff;
    padding: 20rpx 30rpx 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .user-info {
    display: flex;
    align-items: center;
  }
  
  .avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    margin-right: 20rpx;
    border: 2rpx solid #e9ecef;
  }
  
  .user-text {
    display: flex;
    flex-direction: column;
  }
  
  .greeting {
    font-size: 24rpx;
    color: #999999;
    margin-bottom: 5rpx;
  }
  
  .username {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .header-actions {
    display: flex;
    gap: 20rpx;
  }
  
  .action-btn {
    position: relative;
    width: 60rpx;
    height: 60rpx;
    background: #f8f9fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .action-icon {
    font-size: 28rpx;
  }
  
  .badge {
    position: absolute;
    top: -5rpx;
    right: -5rpx;
    background: #ff4757;
    color: #ffffff;
    font-size: 20rpx;
    padding: 2rpx 8rpx;
    border-radius: 20rpx;
    min-width: 30rpx;
    text-align: center;
  }
  
  .stats-card {
    margin: 30rpx;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20rpx;
    padding: 40rpx 30rpx;
    color: #ffffff;
  }
  
  .stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
  }
  
  .stats-title {
    font-size: 32rpx;
    font-weight: 600;
  }
  
  .stats-date {
    font-size: 24rpx;
    opacity: 0.8;
  }
  
  .stats-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
  }
  
  .stat-number {
    font-size: 48rpx;
    font-weight: 700;
    margin-bottom: 10rpx;
  }
  
  .stat-label {
    font-size: 24rpx;
    opacity: 0.8;
  }
  
  .stat-divider {
    width: 1rpx;
    height: 60rpx;
    background: rgba(255, 255, 255, 0.3);
  }
  
  .quick-actions {
    margin: 30rpx;
  }
  
  .section-title {
    margin-bottom: 30rpx;
  }
  
  .title-text {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 10rpx;
  }
  
  .title-subtitle {
    font-size: 26rpx;
    color: #666666;
  }
  
  .title-more {
    font-size: 26rpx;
    color: #007aff;
    cursor: pointer;
  }
  
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20rpx;
  }
  
  .action-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 30rpx 20rpx;
    text-align: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .action-item:active {
    transform: scale(0.98);
  }
  
  .action-icon-wrapper {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20rpx;
  }
  
  .action-icon {
    font-size: 36rpx;
    color: #ffffff;
  }
  
  .action-title {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .action-desc {
    font-size: 24rpx;
    color: #666666;
  }
  
  .progress-section {
    margin: 30rpx;
  }
  
  .section-title {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 30rpx;
  }
  
  .progress-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .progress-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
  }
  
  .course-info {
    flex: 1;
  }
  
  .course-title {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .course-desc {
    display: block;
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 20rpx;
  }
  
  .progress-bar {
    width: 100%;
    height: 8rpx;
    background: #f0f0f0;
    border-radius: 4rpx;
    overflow: hidden;
    margin-bottom: 10rpx;
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #007aff 0%, #5856d6 100%);
    border-radius: 4rpx;
    transition: width 0.3s ease;
  }
  
  .progress-text {
    font-size: 22rpx;
    color: #999999;
  }
  
  .course-action {
    margin-left: 20rpx;
  }
  
  .continue-btn {
    background: #007aff;
    color: #ffffff;
    padding: 15rpx 25rpx;
    border-radius: 20rpx;
    font-size: 24rpx;
  }
  
  .recommendations {
    margin: 30rpx;
  }
  
  .recommend-scroll {
    width: 100%;
  }
  
  .recommend-list {
    display: flex;
    gap: 20rpx;
    padding-bottom: 10rpx;
  }
  
  .recommend-item {
    width: 280rpx;
    background: #ffffff;
    border-radius: 16rpx;
    overflow: hidden;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    flex-shrink: 0;
  }
  
  .recommend-image {
    width: 100%;
    height: 160rpx;
  }
  
  .recommend-content {
    padding: 20rpx;
  }
  
  .recommend-title {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .recommend-desc {
    display: block;
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 15rpx;
  }
  
  .recommend-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .recommend-tag {
    background: #f0f8ff;
    color: #007aff;
    padding: 4rpx 12rpx;
    border-radius: 12rpx;
    font-size: 20rpx;
  }
  
  .recommend-time {
    font-size: 20rpx;
    color: #999999;
  }
  
  .bottom-spacing {
    height: 120rpx;
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .actions-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 15rpx;
    }
    
    .action-item {
      padding: 25rpx 15rpx;
    }
    
    .action-icon-wrapper {
      width: 70rpx;
      height: 70rpx;
    }
    
    .action-icon {
      font-size: 32rpx;
    }
    
    .recommend-item {
      width: 260rpx;
    }
  }
</style>