<template>
  <div class="progress-visualization">
    <!-- 用户等级和经验 -->
    <div class="level-section">
      <div class="level-badge">
        <div class="level-number">{{ level }}</div>
        <div class="level-label">等级</div>
      </div>
      
      <div class="exp-container">
        <div class="exp-info">
          <span class="exp-current">{{ currentExp }}</span>
          <span class="exp-separator">/</span>
          <span class="exp-required">{{ requiredExp }}</span>
          <span class="exp-label">经验值</span>
        </div>
        
        <div class="exp-bar">
          <div 
            class="exp-fill" 
            :style="{ width: expPercentage + '%' }"
            :class="{ 'exp-gaining': isGainingExp }"
          ></div>
          <div class="exp-percentage">{{ Math.round(expPercentage) }}%</div>
        </div>
        
        <div v-if="expToNext > 0" class="exp-to-next">
          还需 {{ expToNext }} 经验升级
        </div>
      </div>
    </div>
    
    <!-- 学习统计 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-value">{{ totalWordsLearned }}</div>
        <div class="stat-label">已学单词</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-value">{{ accuracyRate }}%</div>
        <div class="stat-label">正确率</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🔥</div>
        <div class="stat-value">{{ currentStreak }}</div>
        <div class="stat-label">连续天数</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-value">{{ totalAchievements }}</div>
        <div class="stat-label">成就数量</div>
      </div>
    </div>
    
    <!-- 今日进度 -->
    <div class="daily-progress">
      <h4>今日学习进度</h4>
      <div class="daily-goals">
        <div class="goal-item">
          <div class="goal-header">
            <span class="goal-title">单词练习</span>
            <span class="goal-progress">{{ dailyWordsCompleted }}/{{ dailyWordsGoal }}</span>
          </div>
          <div class="goal-bar">
            <div 
              class="goal-fill" 
              :style="{ width: dailyWordsPercentage + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="goal-item">
          <div class="goal-header">
            <span class="goal-title">学习时长</span>
            <span class="goal-progress">{{ formatTime(dailyTimeSpent) }}/{{ formatTime(dailyTimeGoal) }}</span>
          </div>
          <div class="goal-bar">
            <div 
              class="goal-fill" 
              :style="{ width: dailyTimePercentage + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="goal-item">
          <div class="goal-header">
            <span class="goal-title">正确答题</span>
            <span class="goal-progress">{{ dailyCorrectAnswers }}/{{ dailyCorrectGoal }}</span>
          </div>
          <div class="goal-bar">
            <div 
              class="goal-fill" 
              :style="{ width: dailyCorrectPercentage + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 周学习热力图 -->
    <div class="heatmap-section">
      <h4>本周学习活动</h4>
      <div class="heatmap">
        <div 
          v-for="(day, index) in weeklyActivity" 
          :key="index"
          class="heatmap-day"
          :class="getHeatmapClass(day.intensity)"
          :title="`${day.date}: ${day.wordsLearned} 个单词`"
        >
          <div class="day-label">{{ day.dayName }}</div>
          <div class="day-count">{{ day.wordsLearned }}</div>
        </div>
      </div>
    </div>
    
    <!-- 最近成就 -->
    <div v-if="recentAchievements.length > 0" class="achievements-section">
      <h4>最近获得的成就</h4>
      <div class="achievements-list">
        <div 
          v-for="achievement in recentAchievements" 
          :key="achievement.id"
          class="achievement-item"
          :class="achievement.rarity"
        >
          <div class="achievement-icon">{{ achievement.icon }}</div>
          <div class="achievement-info">
            <div class="achievement-name">{{ achievement.name }}</div>
            <div class="achievement-desc">{{ achievement.description }}</div>
            <div class="achievement-date">{{ formatDate(achievement.unlockedAt) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressVisualization',
  props: {
    gameState: {
      type: Object,
      required: true
    },
    sessionData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      isGainingExp: false,
      weeklyActivity: []
    }
  },
  computed: {
    level() {
      return this.gameState.level || 1
    },
    currentExp() {
      return this.gameState.experience || 0
    },
    requiredExp() {
      return this.calculateRequiredExp(this.level)
    },
    expPercentage() {
      const levelStartExp = this.calculateRequiredExp(this.level - 1)
      const currentLevelExp = this.currentExp - levelStartExp
      const requiredLevelExp = this.requiredExp - levelStartExp
      return Math.min(100, (currentLevelExp / requiredLevelExp) * 100)
    },
    expToNext() {
      return Math.max(0, this.requiredExp - this.currentExp)
    },
    totalWordsLearned() {
      return this.gameState.totalWordsLearned || 0
    },
    accuracyRate() {
      const total = this.gameState.totalAnswers || 0
      const correct = this.gameState.correctAnswers || 0
      return total > 0 ? Math.round((correct / total) * 100) : 0
    },
    currentStreak() {
      return this.gameState.currentStreak || 0
    },
    totalAchievements() {
      return Object.keys(this.gameState.achievements || {}).filter(
        key => this.gameState.achievements[key].unlocked
      ).length
    },
    dailyWordsCompleted() {
      return this.gameState.dailyProgress?.wordsCompleted || 0
    },
    dailyWordsGoal() {
      return this.gameState.dailyProgress?.wordsGoal || 20
    },
    dailyWordsPercentage() {
      return Math.min(100, (this.dailyWordsCompleted / this.dailyWordsGoal) * 100)
    },
    dailyTimeSpent() {
      return this.gameState.dailyProgress?.timeSpent || 0
    },
    dailyTimeGoal() {
      return this.gameState.dailyProgress?.timeGoal || 1800 // 30分钟
    },
    dailyTimePercentage() {
      return Math.min(100, (this.dailyTimeSpent / this.dailyTimeGoal) * 100)
    },
    dailyCorrectAnswers() {
      return this.gameState.dailyProgress?.correctAnswers || 0
    },
    dailyCorrectGoal() {
      return this.gameState.dailyProgress?.correctGoal || 15
    },
    dailyCorrectPercentage() {
      return Math.min(100, (this.dailyCorrectAnswers / this.dailyCorrectGoal) * 100)
    },
    recentAchievements() {
      const achievements = this.gameState.achievements || {}
      return Object.values(achievements)
        .filter(achievement => achievement.unlocked)
        .sort((a, b) => new Date(b.unlockedAt) - new Date(a.unlockedAt))
        .slice(0, 3)
    }
  },
  watch: {
    'gameState.experience': {
      handler(newExp, oldExp) {
        if (newExp > oldExp) {
          this.animateExpGain()
        }
      }
    }
  },
  mounted() {
    this.generateWeeklyActivity()
  },
  methods: {
    calculateRequiredExp(level) {
      // 经验值计算公式：每级所需经验递增
      return Math.floor(100 * Math.pow(1.5, level - 1))
    },
    
    animateExpGain() {
      this.isGainingExp = true
      setTimeout(() => {
        this.isGainingExp = false
      }, 1000)
    },
    
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = now - date
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) return '今天'
      if (diffDays === 1) return '昨天'
      if (diffDays < 7) return `${diffDays}天前`
      return date.toLocaleDateString('zh-CN')
    },
    
    generateWeeklyActivity() {
      const today = new Date()
      const weekDays = ['日', '一', '二', '三', '四', '五', '六']
      
      this.weeklyActivity = Array.from({ length: 7 }, (_, i) => {
        const date = new Date(today)
        date.setDate(today.getDate() - (6 - i))
        
        // 模拟学习数据（实际应用中从后端获取）
        const wordsLearned = Math.floor(Math.random() * 30)
        const intensity = this.calculateIntensity(wordsLearned)
        
        return {
          date: date.toLocaleDateString('zh-CN'),
          dayName: weekDays[date.getDay()],
          wordsLearned,
          intensity
        }
      })
    },
    
    calculateIntensity(wordsLearned) {
      if (wordsLearned === 0) return 0
      if (wordsLearned < 5) return 1
      if (wordsLearned < 15) return 2
      if (wordsLearned < 25) return 3
      return 4
    },
    
    getHeatmapClass(intensity) {
      return `intensity-${intensity}`
    }
  }
}
</script>

