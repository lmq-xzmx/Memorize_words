<template>
  <div class="statistics" v-permission="'progress.statistics.view'">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>学习统计</h1>
      <p>详细的学习数据分析和统计</p>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card" v-for="stat in overviewStats" :key="stat.key">
        <div class="stat-icon" :style="{ background: stat.color }">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stat.value }}</h3>
          <p>{{ stat.label }}</p>
          <span class="stat-change" :class="stat.trend">
            <i :class="stat.trend === 'up' ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
            {{ stat.change }}
          </span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-row">
        <!-- 学习时长趋势 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>学习时长趋势</h3>
            <div class="time-filter">
              <button v-for="period in timePeriods" 
                      :key="period.value"
                      :class="{ active: selectedPeriod === period.value }"
                      @click="selectedPeriod = period.value"
                      class="filter-btn">
                {{ period.label }}
              </button>
            </div>
          </div>
          <div class="chart-content">
            <canvas ref="studyTimeChart" width="400" height="200"></canvas>
          </div>
        </div>

        <!-- 学习进度分布 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>学习进度分布</h3>
          </div>
          <div class="chart-content">
            <canvas ref="progressChart" width="300" height="300"></canvas>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <!-- 词汇掌握情况 -->
        <div class="chart-card full-width">
          <div class="chart-header">
            <h3>词汇掌握情况</h3>
            <div class="legend">
              <span class="legend-item">
                <span class="legend-color" style="background: #3498db;"></span>
                已掌握
              </span>
              <span class="legend-item">
                <span class="legend-color" style="background: #f39c12;"></span>
                学习中
              </span>
              <span class="legend-item">
                <span class="legend-color" style="background: #e74c3c;"></span>
                待学习
              </span>
            </div>
          </div>
          <div class="chart-content">
            <canvas ref="vocabularyChart" width="800" height="300"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细统计 -->
    <div class="detailed-stats">
      <div class="stats-grid">
        <!-- 学习习惯 -->
        <div class="stats-card">
          <h3>学习习惯</h3>
          <div class="habit-stats">
            <div class="habit-item">
              <span class="habit-label">平均每日学习时长</span>
              <span class="habit-value">{{ learningHabits.avgDailyTime }}</span>
            </div>
            <div class="habit-item">
              <span class="habit-label">连续学习天数</span>
              <span class="habit-value">{{ learningHabits.streakDays }} 天</span>
            </div>
            <div class="habit-item">
              <span class="habit-label">最佳学习时段</span>
              <span class="habit-value">{{ learningHabits.bestTimeSlot }}</span>
            </div>
            <div class="habit-item">
              <span class="habit-label">学习频率</span>
              <span class="habit-value">{{ learningHabits.frequency }}</span>
            </div>
          </div>
        </div>

        <!-- 成就统计 -->
        <div class="stats-card">
          <h3>成就统计</h3>
          <div class="achievement-stats">
            <div class="achievement-item" v-for="achievement in achievements" :key="achievement.id">
              <div class="achievement-icon">
                <i :class="achievement.icon" :style="{ color: achievement.color }"></i>
              </div>
              <div class="achievement-info">
                <h4>{{ achievement.title }}</h4>
                <p>{{ achievement.description }}</p>
                <span class="achievement-date">{{ achievement.unlockedAt }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 学习目标 -->
        <div class="stats-card">
          <h3>学习目标</h3>
          <div class="goals-list">
            <div class="goal-item" v-for="goal in learningGoals" :key="goal.id">
              <div class="goal-header">
                <h4>{{ goal.title }}</h4>
                <span class="goal-progress">{{ goal.current }}/{{ goal.target }}</span>
              </div>
              <div class="goal-bar">
                <div class="goal-fill" 
                     :style="{ width: (goal.current / goal.target * 100) + '%' }">
                </div>
              </div>
              <p class="goal-deadline">截止日期: {{ goal.deadline }}</p>
            </div>
          </div>
        </div>

        <!-- 错误分析 -->
        <div class="stats-card">
          <h3>错误分析</h3>
          <div class="error-analysis">
            <div class="error-category" v-for="category in errorAnalysis" :key="category.type">
              <div class="category-header">
                <span class="category-name">{{ category.name }}</span>
                <span class="category-count">{{ category.count }} 次</span>
              </div>
              <div class="category-bar">
                <div class="category-fill" 
                     :style="{ width: (category.count / maxErrorCount * 100) + '%' }">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'

interface OverviewStat {
  key: string
  label: string
  value: string
  icon: string
  color: string
  trend: 'up' | 'down'
  change: string
}

interface Achievement {
  id: number
  title: string
  description: string
  icon: string
  color: string
  unlockedAt: string
}

interface LearningGoal {
  id: number
  title: string
  current: number
  target: number
  deadline: string
}

interface ErrorCategory {
  type: string
  name: string
  count: number
}

// 响应式数据
const selectedPeriod = ref('week')
const studyTimeChart = ref<HTMLCanvasElement | null>(null)
const progressChart = ref<HTMLCanvasElement | null>(null)
const vocabularyChart = ref<HTMLCanvasElement | null>(null)

// 时间周期选项
const timePeriods = [
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' },
  { value: 'quarter', label: '本季度' },
  { value: 'year', label: '本年' }
]

// 概览统计数据
const overviewStats: OverviewStat[] = [
  {
    key: 'totalWords',
    label: '累计学习单词',
    value: '1,234',
    icon: 'fas fa-book',
    color: '#3498db',
    trend: 'up',
    change: '+12%'
  },
  {
    key: 'studyTime',
    label: '总学习时长',
    value: '156h',
    icon: 'fas fa-clock',
    color: '#2ecc71',
    trend: 'up',
    change: '+8%'
  },
  {
    key: 'accuracy',
    label: '平均正确率',
    value: '87%',
    icon: 'fas fa-target',
    color: '#f39c12',
    trend: 'up',
    change: '+3%'
  },
  {
    key: 'streak',
    label: '连续学习天数',
    value: '23',
    icon: 'fas fa-fire',
    color: '#e74c3c',
    trend: 'up',
    change: '+1'
  }
]

// 学习习惯数据
const learningHabits = {
  avgDailyTime: '2.5小时',
  streakDays: 23,
  bestTimeSlot: '晚上 19:00-21:00',
  frequency: '每天'
}

// 成就数据
const achievements: Achievement[] = [
  {
    id: 1,
    title: '词汇大师',
    description: '累计学习1000个单词',
    icon: 'fas fa-trophy',
    color: '#f1c40f',
    unlockedAt: '2024-01-15'
  },
  {
    id: 2,
    title: '坚持不懈',
    description: '连续学习30天',
    icon: 'fas fa-medal',
    color: '#e74c3c',
    unlockedAt: '2024-01-10'
  },
  {
    id: 3,
    title: '完美主义者',
    description: '单次测试100%正确率',
    icon: 'fas fa-star',
    color: '#9b59b6',
    unlockedAt: '2024-01-08'
  }
]

// 学习目标数据
const learningGoals: LearningGoal[] = [
  {
    id: 1,
    title: '本月学习目标',
    current: 180,
    target: 300,
    deadline: '2024-01-31'
  },
  {
    id: 2,
    title: '词汇量目标',
    current: 1234,
    target: 2000,
    deadline: '2024-03-31'
  },
  {
    id: 3,
    title: '学习时长目标',
    current: 156,
    target: 200,
    deadline: '2024-02-29'
  }
]

// 错误分析数据
const errorAnalysis: ErrorCategory[] = [
  { type: 'spelling', name: '拼写错误', count: 45 },
  { type: 'grammar', name: '语法错误', count: 32 },
  { type: 'vocabulary', name: '词汇理解', count: 28 },
  { type: 'pronunciation', name: '发音错误', count: 15 }
]

// 计算属性
const maxErrorCount = computed(() => {
  return Math.max(...errorAnalysis.map(item => item.count))
})

// 方法
const drawStudyTimeChart = () => {
  if (!studyTimeChart.value) return
  
  const ctx = studyTimeChart.value.getContext('2d')
  if (!ctx) return
  
  // 简单的图表绘制示例
  ctx.clearRect(0, 0, 400, 200)
  ctx.strokeStyle = '#3498db'
  ctx.lineWidth = 2
  
  // 绘制折线图
  const data = [30, 45, 60, 40, 70, 55, 80]
  const width = 400
  const height = 200
  const padding = 40
  
  ctx.beginPath()
  data.forEach((value, index) => {
    const x = padding + (index * (width - 2 * padding)) / (data.length - 1)
    const y = height - padding - (value / 100) * (height - 2 * padding)
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
}

const drawProgressChart = () => {
  if (!progressChart.value) return
  
  const ctx = progressChart.value.getContext('2d')
  if (!ctx) return
  
  // 绘制饼图
  const centerX = 150
  const centerY = 150
  const radius = 100
  
  const data = [
    { label: '已掌握', value: 60, color: '#2ecc71' },
    { label: '学习中', value: 25, color: '#f39c12' },
    { label: '待学习', value: 15, color: '#e74c3c' }
  ]
  
  let currentAngle = 0
  
  data.forEach(item => {
    const sliceAngle = (item.value / 100) * 2 * Math.PI
    
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.lineTo(centerX, centerY)
    ctx.fillStyle = item.color
    ctx.fill()
    
    currentAngle += sliceAngle
  })
}

const drawVocabularyChart = () => {
  if (!vocabularyChart.value) return
  
  const ctx = vocabularyChart.value.getContext('2d')
  if (!ctx) return
  
  // 绘制柱状图
  ctx.clearRect(0, 0, 800, 300)
  
  const data = [120, 150, 180, 200, 160, 190, 220]
  const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const barWidth = 80
  const padding = 60
  const maxValue = Math.max(...data)
  
  data.forEach((value, index) => {
    const x = padding + index * (barWidth + 20)
    const barHeight = (value / maxValue) * 200
    const y = 250 - barHeight
    
    ctx.fillStyle = '#3498db'
    ctx.fillRect(x, y, barWidth, barHeight)
    
    // 绘制标签
    ctx.fillStyle = '#2c3e50'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(labels[index], x + barWidth / 2, 280)
    ctx.fillText(value.toString(), x + barWidth / 2, y - 10)
  })
}

// 生命周期
onMounted(async () => {
  await nextTick()
  drawStudyTimeChart()
  drawProgressChart()
  drawVocabularyChart()
})
</script>

<style scoped lang="scss">
.statistics {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    color: #2c3e50;
    margin-bottom: 10px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 16px;
  }
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-content {
  flex: 1;
  
  h3 {
    color: #2c3e50;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 4px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 8px;
  }
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  
  &.up {
    color: #27ae60;
  }
  
  &.down {
    color: #e74c3c;
  }
}

.charts-section {
  margin-bottom: 30px;
}

.chart-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  &.full-width {
    grid-column: 1 / -1;
  }
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h3 {
    color: #2c3e50;
    margin: 0;
  }
}

.time-filter {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid #e9ecef;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #3498db;
  }
  
  &.active {
    background: #3498db;
    color: white;
    border-color: #3498db;
  }
}

.legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #7f8c8d;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.chart-content {
  display: flex;
  justify-content: center;
  align-items: center;
}

.detailed-stats {
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
  }
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 18px;
  }
}

.habit-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.habit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f8f9fa;
  
  &:last-child {
    border-bottom: none;
  }
}

.habit-label {
  color: #7f8c8d;
  font-size: 14px;
}

.habit-value {
  color: #2c3e50;
  font-weight: 600;
}

.achievement-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.achievement-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.achievement-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.achievement-info {
  flex: 1;
  
  h4 {
    color: #2c3e50;
    margin-bottom: 4px;
    font-size: 14px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 12px;
    margin-bottom: 4px;
  }
}

.achievement-date {
  color: #95a5a6;
  font-size: 11px;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.goal-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  
  h4 {
    color: #2c3e50;
    margin: 0;
    font-size: 14px;
  }
}

.goal-progress {
  color: #3498db;
  font-weight: 600;
  font-size: 12px;
}

.goal-bar {
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.goal-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.goal-deadline {
  color: #7f8c8d;
  font-size: 11px;
  margin: 0;
}

.error-analysis {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.error-category {
  .category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  
  .category-name {
    color: #2c3e50;
    font-size: 14px;
  }
  
  .category-count {
    color: #7f8c8d;
    font-size: 12px;
  }
}

.category-bar {
  height: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  overflow: hidden;
}

.category-fill {
  height: 100%;
  background: #e74c3c;
  transition: width 0.3s ease;
}

@media (max-width: 1200px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .statistics {
    padding: 16px;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .detailed-stats .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card {
    padding: 16px;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>