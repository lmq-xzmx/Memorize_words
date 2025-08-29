<template>
  <view class="statistics-page">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-section">
      <view class="loading-spinner"></view>
      <text class="loading-text">正在加载统计数据...</text>
    </view>

    <!-- 统计内容 -->
    <view v-else class="statistics-content">
      <!-- 今日概览 -->
      <view class="overview-section">
        <text class="section-title">今日概览</text>
        
        <view class="overview-cards">
          <view class="overview-card">
            <text class="card-number">{{ userStats?.todayLearned || 0 }}</text>
            <text class="card-label">今日学习</text>
            <view class="progress-ring">
              <view class="progress-fill" :style="{ transform: `rotate(${todayProgress * 3.6}deg)` }"></view>
            </view>
          </view>
          
          <view class="overview-card">
            <text class="card-number">{{ userStats?.weekLearned || 0 }}</text>
            <text class="card-label">本周学习</text>
            <view class="progress-ring">
              <view class="progress-fill" :style="{ transform: `rotate(${weekProgress * 3.6}deg)` }"></view>
            </view>
          </view>
          
          <view class="overview-card">
            <text class="card-number">{{ learningStreak }}</text>
            <text class="card-label">连续天数</text>
            <text class="card-icon">🔥</text>
          </view>
        </view>
      </view>

      <!-- 学习统计 -->
      <view class="stats-section">
        <view class="section-header">
          <text class="section-title">学习统计</text>
          <view class="chart-selector">
            <view 
              v-for="type in [{ key: 'learning', name: '学习量', icon: '📚' }, { key: 'accuracy', name: '正确率', icon: '🎯' }, { key: 'time', name: '时长', icon: '⏱️' }]" 
              :key="type.key"
              class="chart-option"
              :class="{ active: chartType === type.key }"
              @click="changeChartType(type.key)"
            >
              <text class="chart-icon">{{ type.icon }}</text>
              <text class="chart-name">{{ type.name }}</text>
            </view>
          </view>
        </view>
        
        <view class="chart-container">
          <view class="chart-area">
            <view class="chart-bars">
              <view 
                v-for="(item, index) in chartData" 
                :key="index"
                class="chart-bar"
                :style="{ height: getBarHeight(item.value) + '%', backgroundColor: item.color }"
              >
                <text class="bar-value">{{ item.value }}</text>
              </view>
            </view>
            <view class="chart-labels">
              <text 
                v-for="(item, index) in chartData" 
                :key="index"
                class="chart-label"
              >
                {{ item.label }}
              </text>
            </view>
          </view>
          
          <view class="chart-summary">
            <view class="summary-item">
              <text class="summary-label">平均值</text>
              <text class="summary-value">
                {{ chartData.length ? Math.round(chartData.reduce((sum, item) => sum + item.value, 0) / chartData.length) : 0 }}
                {{ chartType === 'accuracy' ? '%' : chartType === 'time' ? '分钟' : '个' }}
              </text>
            </view>
            <view class="summary-item">
              <text class="summary-label">最高值</text>
              <text class="summary-value">
                {{ maxChartValue }}
                {{ chartType === 'accuracy' ? '%' : chartType === 'time' ? '分钟' : '个' }}
              </text>
            </view>
          </view>
        </view>
      </view>

      <!-- 总体数据 -->
      <view class="total-stats-section">
        <text class="section-title">总体数据</text>
        
        <view class="total-stats-grid">
          <view class="stat-item">
            <text class="stat-icon">📖</text>
            <text class="stat-number">{{ userStats?.totalWordsLearned || 0 }}</text>
            <text class="stat-label">累计学习单词</text>
          </view>
          
          <view class="stat-item">
            <text class="stat-icon">🎯</text>
            <text class="stat-number">{{ averageAccuracy }}%</text>
            <text class="stat-label">平均正确率</text>
          </view>
          
          <view class="stat-item">
            <text class="stat-icon">⏰</text>
            <text class="stat-number">{{ totalStudyTime }}</text>
            <text class="stat-label">总学习时长(分钟)</text>
          </view>
          
          <view class="stat-item">
            <text class="stat-icon">🏆</text>
            <text class="stat-number">{{ userStats?.challengeHistory?.length || 0 }}</text>
            <text class="stat-label">完成挑战</text>
          </view>
        </view>
      </view>

      <!-- 成就系统 -->
      <view class="achievements-section">
        <text class="section-title">成就徽章</text>
        
        <view class="achievements-grid">
          <view 
            v-for="achievement in achievementData" 
            :key="achievement.id"
            class="achievement-item"
            :class="{ unlocked: achievement.unlocked }"
          >
            <view class="achievement-icon">
              <text class="icon-text">{{ achievement.icon }}</text>
              <view v-if="!achievement.unlocked" class="lock-overlay">🔒</view>
            </view>
            
            <view class="achievement-info">
              <text class="achievement-title">{{ achievement.title }}</text>
              <text class="achievement-desc">{{ achievement.description }}</text>
              
              <view class="achievement-progress">
                <view class="progress-bar">
                  <view class="progress-fill" :style="{ width: achievement.progress + '%' }"></view>
                </view>
                <text class="progress-text">{{ Math.round(achievement.progress) }}%</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 学习目标 -->
      <view class="goals-section">
        <text class="section-title">学习目标</text>
        
        <view class="goals-container">
          <view class="goal-item">
            <view class="goal-header">
              <text class="goal-title">每日目标</text>
              <text class="goal-progress">{{ userStats?.todayLearned || 0 }} / {{ dailyGoal }}</text>
            </view>
            <view class="goal-bar">
              <view class="goal-fill" :style="{ width: todayProgress + '%' }"></view>
            </view>
            <text class="goal-status">{{ todayProgress >= 100 ? '已完成 🎉' : `还需 ${dailyGoal - (userStats?.todayLearned || 0)} 个单词` }}</text>
          </view>
          
          <view class="goal-item">
            <view class="goal-header">
              <text class="goal-title">每周目标</text>
              <text class="goal-progress">{{ userStats?.weekLearned || 0 }} / {{ weeklyGoal }}</text>
            </view>
            <view class="goal-bar">
              <view class="goal-fill" :style="{ width: weekProgress + '%' }"></view>
            </view>
            <text class="goal-status">{{ weekProgress >= 100 ? '已完成 🎉' : `还需 ${weeklyGoal - (userStats?.weekLearned || 0)} 个单词` }}</text>
          </view>
        </view>
      </view>

      <!-- 最近挑战记录 -->
      <view class="recent-challenges-section">
        <text class="section-title">最近挑战</text>
        
        <view class="challenges-list">
          <view 
            v-for="(challenge, index) in (userStats?.challengeHistory || []).slice(0, 5)" 
            :key="index"
            class="challenge-item"
          >
            <view class="challenge-info">
              <text class="challenge-date">{{ formatDate(challenge.date) }}</text>
              <text class="challenge-score">{{ challenge.score }} / {{ challenge.totalScore }}</text>
            </view>
            
            <view class="challenge-stats">
              <view class="challenge-accuracy" :class="{ excellent: challenge.accuracy >= 90, good: challenge.accuracy >= 70 }">
                <text class="accuracy-text">{{ challenge.accuracy }}%</text>
              </view>
              <text class="challenge-time">{{ formatTime(challenge.timeUsed) }}</text>
            </view>
          </view>
        </view>
        
        <view v-if="!userStats?.challengeHistory?.length" class="empty-challenges">
          <text class="empty-text">暂无挑战记录</text>
          <text class="empty-hint">完成第一个挑战来查看统计数据</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { mockData, getUserStats, simulateApiDelay } from '@/utils/mockData'

export default {
  name: 'Statistics',
  data() {
    return {
      loading: true,
      userStats: null,
      selectedPeriod: 'week', // week, month, year
      chartType: 'learning', // learning, accuracy, time
      studyData: [],
      achievementData: [],
      weeklyGoal: 50, // 每周学习目标（单词数）
      dailyGoal: 10 // 每日学习目标（单词数）
    }
  },
  computed: {
    todayProgress() {
      if (!this.userStats) return 0
      return Math.min((this.userStats.todayLearned / this.dailyGoal) * 100, 100)
    },
    weekProgress() {
      if (!this.userStats) return 0
      return Math.min((this.userStats.weekLearned / this.weeklyGoal) * 100, 100)
    },
    averageAccuracy() {
      if (!this.userStats || !this.userStats.challengeHistory.length) return 0
      const total = this.userStats.challengeHistory.reduce((sum, challenge) => sum + challenge.accuracy, 0)
      return Math.round(total / this.userStats.challengeHistory.length)
    },
    totalStudyTime() {
      if (!this.userStats) return 0
      return Math.round(this.userStats.totalStudyTime / 60) // 转换为分钟
    },
    learningStreak() {
      if (!this.userStats) return 0
      return this.userStats.consecutiveDays
    },
    chartData() {
      if (!this.userStats) return []
      
      const data = this.userStats.dailyStats.slice(-7) // 最近7天
      
      if (this.chartType === 'learning') {
        return data.map(day => ({
          label: this.formatDate(day.date),
          value: day.wordsLearned,
          color: '#667eea'
        }))
      } else if (this.chartType === 'accuracy') {
        return data.map(day => ({
          label: this.formatDate(day.date),
          value: day.accuracy,
          color: '#10b981'
        }))
      } else if (this.chartType === 'time') {
        return data.map(day => ({
          label: this.formatDate(day.date),
          value: Math.round(day.studyTime / 60), // 转换为分钟
          color: '#f59e0b'
        }))
      }
      
      return []
    },
    maxChartValue() {
      if (!this.chartData.length) return 100
      return Math.max(...this.chartData.map(item => item.value))
    }
  },
  async mounted() {
    await this.loadStatistics()
  },
  methods: {
    async loadStatistics() {
      this.loading = true
      await simulateApiDelay()
      
      this.userStats = getUserStats()
      this.generateStudyData()
      this.generateAchievementData()
      
      this.loading = false
    },
    
    generateStudyData() {
      // 生成学习数据用于图表显示
      this.studyData = this.userStats.dailyStats.map(day => ({
        date: day.date,
        wordsLearned: day.wordsLearned,
        accuracy: day.accuracy,
        studyTime: day.studyTime
      }))
    },
    
    generateAchievementData() {
      // 生成成就数据
      this.achievementData = [
        {
          id: 'first_word',
          title: '初学者',
          description: '学习第一个单词',
          icon: '🎯',
          unlocked: this.userStats.totalWordsLearned > 0,
          progress: this.userStats.totalWordsLearned > 0 ? 100 : 0
        },
        {
          id: 'hundred_words',
          title: '百词斩',
          description: '累计学习100个单词',
          icon: '💯',
          unlocked: this.userStats.totalWordsLearned >= 100,
          progress: Math.min((this.userStats.totalWordsLearned / 100) * 100, 100)
        },
        {
          id: 'week_streak',
          title: '坚持一周',
          description: '连续学习7天',
          icon: '🔥',
          unlocked: this.userStats.consecutiveDays >= 7,
          progress: Math.min((this.userStats.consecutiveDays / 7) * 100, 100)
        },
        {
          id: 'perfect_score',
          title: '完美主义',
          description: '挑战中获得100%正确率',
          icon: '⭐',
          unlocked: this.userStats.challengeHistory.some(c => c.accuracy === 100),
          progress: this.userStats.challengeHistory.some(c => c.accuracy === 100) ? 100 : this.averageAccuracy
        },
        {
          id: 'speed_learner',
          title: '学习达人',
          description: '单日学习50个单词',
          icon: '⚡',
          unlocked: this.userStats.dailyStats.some(d => d.wordsLearned >= 50),
          progress: Math.min((Math.max(...this.userStats.dailyStats.map(d => d.wordsLearned)) / 50) * 100, 100)
        },
        {
          id: 'time_master',
          title: '时间管理大师',
          description: '累计学习10小时',
          icon: '⏰',
          unlocked: this.userStats.totalStudyTime >= 36000, // 10小时 = 36000秒
          progress: Math.min((this.userStats.totalStudyTime / 36000) * 100, 100)
        }
      ]
    },
    
    changePeriod(period) {
      this.selectedPeriod = period
    },
    
    changeChartType(type) {
      this.chartType = type
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return `${date.getMonth() + 1}/${date.getDate()}`
    },
    
    formatTime(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      } else {
        return `${minutes}分钟`
      }
    },
    
    getBarHeight(value) {
      if (this.maxChartValue === 0) return 0
      return Math.max((value / this.maxChartValue) * 100, 2) // 最小高度2%
    }
  }
}
</script>

<style scoped>
.statistics-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

/* 统计内容样式 */
.statistics-content {
  padding: 20px;
}

.section-title {
  font-size: 20px;
  color: #ffffff;
  font-weight: bold;
  margin-bottom: 16px;
  display: block;
}

/* 今日概览样式 */
.overview-section {
  margin-bottom: 24px;
}

.overview-cards {
  display: flex;
  gap: 12px;
}

.overview-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  backdrop-filter: blur(10px);
  position: relative;
}

.card-number {
  font-size: 24px;
  color: #ffffff;
  font-weight: bold;
  margin-bottom: 4px;
  display: block;
}

.card-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.card-icon {
  font-size: 20px;
  margin-top: 8px;
  display: block;
}

.progress-ring {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.progress-fill {
  width: 50%;
  height: 100%;
  background: #10b981;
  transform-origin: right center;
  transition: transform 0.3s ease;
}

/* 学习统计样式 */
.stats-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header .section-title {
  color: #1e293b;
  margin-bottom: 0;
}

.chart-selector {
  display: flex;
  gap: 8px;
}

.chart-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: #f1f5f9;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.chart-option.active {
  background: #667eea;
  transform: translateY(-2px);
}

.chart-option.active .chart-icon,
.chart-option.active .chart-name {
  color: #ffffff;
}

.chart-icon {
  font-size: 16px;
  margin-bottom: 2px;
}

.chart-name {
  font-size: 10px;
  color: #64748b;
  font-weight: 500;
}

.chart-container {
  margin-top: 20px;
}

.chart-area {
  margin-bottom: 16px;
}

.chart-bars {
  display: flex;
  align-items: end;
  gap: 8px;
  height: 120px;
  margin-bottom: 8px;
  padding: 0 4px;
}

.chart-bar {
  flex: 1;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  min-height: 4px;
  display: flex;
  align-items: end;
  justify-content: center;
}

.bar-value {
  font-size: 10px;
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 4px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.chart-labels {
  display: flex;
  gap: 8px;
  padding: 0 4px;
}

.chart-label {
  flex: 1;
  font-size: 10px;
  color: #64748b;
  text-align: center;
}

.chart-summary {
  display: flex;
  justify-content: space-around;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
  display: block;
}

.summary-value {
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
  display: block;
}

/* 总体数据样式 */
.total-stats-section {
  margin-bottom: 24px;
}

.total-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  backdrop-filter: blur(10px);
}

.stat-icon {
  font-size: 24px;
  margin-bottom: 8px;
  display: block;
}

.stat-number {
  font-size: 20px;
  color: #ffffff;
  font-weight: bold;
  margin-bottom: 4px;
  display: block;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

/* 成就系统样式 */
.achievements-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.achievements-section .section-title {
  color: #1e293b;
}

.achievements-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.achievement-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.achievement-item.unlocked {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}

.achievement-icon {
  width: 48px;
  height: 48px;
  border-radius: 24px;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  position: relative;
  flex-shrink: 0;
}

.achievement-item.unlocked .achievement-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.icon-text {
  font-size: 20px;
}

.lock-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.achievement-info {
  flex: 1;
}

.achievement-title {
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
  margin-bottom: 4px;
  display: block;
}

.achievement-desc {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
  display: block;
}

.achievement-progress {
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
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  min-width: 32px;
}

/* 学习目标样式 */
.goals-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.goals-section .section-title {
  color: #1e293b;
}

.goals-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.goal-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.goal-title {
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
}

.goal-progress {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.goal-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.goal-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.goal-status {
  font-size: 14px;
  color: #64748b;
  display: block;
}

/* 最近挑战记录样式 */
.recent-challenges-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 20px;
}

.recent-challenges-section .section-title {
  color: #1e293b;
}

.challenges-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.challenge-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.challenge-info {
  flex: 1;
}

.challenge-date {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
  display: block;
}

.challenge-score {
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
  display: block;
}

.challenge-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.challenge-accuracy {
  padding: 4px 8px;
  border-radius: 8px;
  background: #ef4444;
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
}

.challenge-accuracy.good {
  background: #f59e0b;
}

.challenge-accuracy.excellent {
  background: #10b981;
}

.accuracy-text {
  font-size: 12px;
  font-weight: 600;
}

.challenge-time {
  font-size: 12px;
  color: #64748b;
}

.empty-challenges {
  text-align: center;
  padding: 40px 20px;
}

.empty-text {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 8px;
  display: block;
}

.empty-hint {
  font-size: 14px;
  color: #94a3b8;
  display: block;
}
</style>