<template>
  <view class="learning-container">
    <!-- 自定义导航栏 -->
    <MobileNavBar title="学习中心" />
    
    <!-- 学习统计卡片 -->
    <view class="stats-section">
      <MobileCard class="stats-card">
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-number">{{ userStats.wordsLearned }}</text>
            <text class="stat-label">已学单词</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ userStats.studyDays }}</text>
            <text class="stat-label">学习天数</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ userStats.studyTime }}</text>
            <text class="stat-label">学习时长(分)</text>
          </view>
        </view>
      </MobileCard>
    </view>

    <!-- 学习功能区 -->
    <view class="function-section">
      <view class="section-title">学习功能</view>
      
      <view class="function-grid">
        <MobileCard 
          v-for="item in learningFunctions" 
          :key="item.id"
          class="function-card"
          @click="navigateToFunction(item)"
        >
          <view class="function-content">
            <view class="function-icon">
              <text class="iconfont" :class="item.icon"></text>
            </view>
            <view class="function-info">
              <text class="function-title">{{ item.title }}</text>
              <text class="function-desc">{{ item.description }}</text>
            </view>
          </view>
        </MobileCard>
      </view>
    </view>

    <!-- 学习进度 -->
    <view class="progress-section">
      <view class="section-title">学习进度</view>
      
      <MobileCard class="progress-card">
        <view class="progress-item">
          <view class="progress-header">
            <text class="progress-title">今日学习目标</text>
            <text class="progress-percent">{{ todayProgress }}%</text>
          </view>
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: todayProgress + '%' }"></view>
          </view>
          <text class="progress-text">已完成 {{ completedToday }}/{{ dailyTarget }} 个单词</text>
        </view>
      </MobileCard>
    </view>

    <!-- 最近学习记录 -->
    <view class="recent-section">
      <view class="section-title">最近学习</view>
      
      <MobileList :items="recentStudy" @item-click="viewStudyDetail">
        <template #item="{ item }">
          <view class="study-item">
            <view class="study-word">{{ item.word }}</view>
            <view class="study-info">
              <text class="study-meaning">{{ item.meaning }}</text>
              <text class="study-time">{{ formatTime(item.studyTime) }}</text>
            </view>
          </view>
        </template>
      </MobileList>
    </view>
  </view>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import MobileNavBar from '@/components/Mobile/MobileNavBar.vue'
import MobileCard from '@/components/Mobile/MobileCard.vue'
import MobileList from '@/components/Mobile/MobileList.vue'

export default {
  name: 'LearningPage',
  components: {
    MobileNavBar,
    MobileCard,
    MobileList
  },
  setup() {
    // 用户学习统计
    const userStats = reactive({
      wordsLearned: 0,
      studyDays: 0,
      studyTime: 0
    })

    // 学习功能列表
    const learningFunctions = ref([
      {
        id: 1,
        title: '单词练习',
        description: '巩固词汇记忆',
        icon: 'icon-word',
        path: '/pages/practice/practice'
      },
      {
        id: 2,
        title: '听力训练',
        description: '提升听力水平',
        icon: 'icon-listen',
        path: '/pages/listening/listening'
      },
      {
        id: 3,
        title: '口语练习',
        description: '锻炼口语表达',
        icon: 'icon-speak',
        path: '/pages/speaking/speaking'
      },
      {
        id: 4,
        title: '阅读理解',
        description: '提高阅读能力',
        icon: 'icon-read',
        path: '/pages/reading/reading'
      }
    ])

    // 今日学习进度
    const todayProgress = ref(0)
    const completedToday = ref(0)
    const dailyTarget = ref(20)

    // 最近学习记录
    const recentStudy = ref([])

    // 导航到功能页面
    const navigateToFunction = (item) => {
      uni.navigateTo({
        url: item.path
      })
    }

    // 查看学习详情
    const viewStudyDetail = (item) => {
      uni.navigateTo({
        url: `/pages/word/detail?word=${item.word}`
      })
    }

    // 格式化时间
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) {
        return '刚刚'
      } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`
      } else {
        return `${Math.floor(diff / 86400000)}天前`
      }
    }

    // 加载学习数据
    const loadLearningData = async () => {
      try {
        // 模拟数据加载
        userStats.wordsLearned = 156
        userStats.studyDays = 23
        userStats.studyTime = 480
        
        completedToday.value = 12
        todayProgress.value = Math.round((completedToday.value / dailyTarget.value) * 100)
        
        recentStudy.value = [
          {
            id: 1,
            word: 'abandon',
            meaning: '放弃，抛弃',
            studyTime: Date.now() - 300000
          },
          {
            id: 2,
            word: 'ability',
            meaning: '能力，才能',
            studyTime: Date.now() - 600000
          },
          {
            id: 3,
            word: 'absolute',
            meaning: '绝对的，完全的',
            studyTime: Date.now() - 900000
          }
        ]
      } catch (error) {
        console.error('加载学习数据失败:', error)
        uni.showToast({
          title: '数据加载失败',
          icon: 'none'
        })
      }
    }

    onMounted(() => {
      loadLearningData()
    })

    return {
      userStats,
      learningFunctions,
      todayProgress,
      completedToday,
      dailyTarget,
      recentStudy,
      navigateToFunction,
      viewStudyDetail,
      formatTime
    }
  }
}
</script>

<style lang="scss" scoped>
.learning-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 100rpx;
}

.stats-section {
  padding: 20rpx;
  margin-top: 20rpx;
}

.stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  padding: 30rpx 20rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.stat-number {
  font-size: 48rpx;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 24rpx;
  color: #666;
}

.function-section,
.progress-section,
.recent-section {
  padding: 0 20rpx;
  margin-top: 40rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 20rpx;
  padding-left: 10rpx;
}

.function-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.function-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.function-card:active {
  transform: scale(0.95);
  background: rgba(255, 255, 255, 0.8);
}

.function-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30rpx 20rpx;
  gap: 20rpx;
}

.function-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.function-icon .iconfont {
  font-size: 40rpx;
  color: #fff;
}

.function-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.function-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.function-desc {
  font-size: 22rpx;
  color: #666;
}

.progress-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.progress-item {
  padding: 30rpx;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.progress-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.progress-percent {
  font-size: 28rpx;
  font-weight: bold;
  color: #667eea;
}

.progress-bar {
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
  margin-bottom: 15rpx;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 6rpx;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 24rpx;
  color: #666;
}

.study-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
}

.study-word {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.study-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
}

.study-meaning {
  font-size: 24rpx;
  color: #666;
}

.study-time {
  font-size: 20rpx;
  color: #999;
}
</style>