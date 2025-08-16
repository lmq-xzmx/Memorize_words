<template>
  <div class="dashboard">
    <!-- 顶部欢迎区域 -->
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎回来，{{ userInfo.name || '学习者' }}！</h1>
      <p class="welcome-subtitle">继续你的英语学习之旅</p>
    </div>

    <!-- 学习统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <h3>{{ stats.wordsLearned }}</h3>
          <p>已学单词</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <h3>{{ stats.studyTime }}</h3>
          <p>学习时长</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <h3>{{ stats.accuracy }}%</h3>
          <p>正确率</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔥</div>
        <div class="stat-content">
          <h3>{{ stats.streak }}</h3>
          <p>连续天数</p>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>快速开始</h2>
      <div class="action-grid">
        <router-link to="/word-flashcard" class="action-card">
          <div class="action-icon">🃏</div>
          <h3>单词卡片</h3>
          <p>通过卡片记忆单词</p>
        </router-link>
        <router-link to="/listening" class="action-card">
          <div class="action-icon">🎧</div>
          <h3>听力练习</h3>
          <p>提升听力理解能力</p>
        </router-link>
        <router-link to="/reading" class="action-card">
          <div class="action-icon">📖</div>
          <h3>阅读理解</h3>
          <p>增强阅读技能</p>
        </router-link>
        <router-link to="/speaking" class="action-card">
          <div class="action-icon">🗣️</div>
          <h3>口语练习</h3>
          <p>提高口语表达</p>
        </router-link>
      </div>
    </div>

    <!-- 学习进度 -->
    <div class="progress-section">
      <h2>学习进度</h2>
      <div class="progress-card">
        <div class="progress-header">
          <span>今日目标</span>
          <span>{{ progress.completed }}/{{ progress.target }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <p class="progress-text">{{ progressText }}</p>
      </div>
    </div>

    <!-- 最近学习 -->
    <div class="recent-section">
      <h2>最近学习</h2>
      <div class="recent-list">
        <div v-for="item in recentActivities" :key="item.id" class="recent-item">
          <div class="recent-icon">{{ item.icon }}</div>
          <div class="recent-content">
            <h4>{{ item.title }}</h4>
            <p>{{ item.description }}</p>
            <span class="recent-time">{{ item.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import api from '@/utils/api'
import permissionMixin from '../mixins/permissionMixin.js'

export default {
  name: 'Dashboard',
  mixins: [permissionMixin],
  data() {
    return {
      stats: {
        wordsLearned: 0,
        studyTime: '0h',
        accuracy: 0,
        streak: 0
      },
      progress: {
        completed: 0,
        target: 50
      },
      recentActivities: []
    }
  },
  computed: {
    ...mapState(['userInfo']),
    progressPercentage() {
      return Math.min((this.progress.completed / this.progress.target) * 100, 100)
    },
    progressText() {
      if (this.progress.completed >= this.progress.target) {
        return '🎉 今日目标已完成！'
      }
      const remaining = this.progress.target - this.progress.completed
      return `还需学习 ${remaining} 个单词完成今日目标`
    }
  },
  async mounted() {
    // 确保权限系统已初始化
    await this.$nextTick()
    
    // 权限检查
    if (!this.$hasPermission('view_dashboard')) {
      this.$showError('您没有权限访问仪表板')
      this.$router.push('/')
      return
    }

    // 加载仪表板数据
    await this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 检查统计数据查看权限
        if (this.$hasPermission('view_learning_stats')) {
          const [statsRes, progressRes, activitiesRes] = await Promise.all([
            api.getUserStats(),
            api.getUserProgress(),
            api.getRecentActivities()
          ])
          
          this.stats = statsRes.data
          this.progress = progressRes.data
          this.recentActivities = activitiesRes.data
        } else {
          // 如果没有统计权限，使用默认数据
          this.loadMockData()
        }
      } catch (error) {
        console.error('加载仪表板数据失败:', error)
        // 使用模拟数据
        this.loadMockData()
      }
    },
    loadMockData() {
      this.stats = {
        wordsLearned: 156,
        studyTime: '2.5h',
        accuracy: 85,
        streak: 7
      }
      this.progress = {
        completed: 23,
        target: 50
      }
      this.recentActivities = [
        {
          id: 1,
          icon: '🃏',
          title: '单词卡片练习',
          description: '学习了 15 个新单词',
          time: '2小时前'
        },
        {
          id: 2,
          icon: '🎧',
          title: '听力练习',
          description: '完成了日常对话练习',
          time: '昨天'
        },
        {
          id: 3,
          icon: '📖',
          title: '阅读理解',
          description: '阅读了一篇新闻文章',
          time: '2天前'
        }
      ]
    }
  }
}
</script>

<style scoped>
/* 仪表板主容器 */
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  position: relative;
  overflow-x: hidden;
}

.dashboard::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  animation: slideInDown 0.8s ease-out;
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  animation: slideInUp 0.8s ease-out 0.2s both;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.stat-content p {
  font-size: 1rem;
  color: #666;
  margin: 0;
  font-weight: 500;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 快速操作区域 */
.quick-actions {
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.quick-actions h2 {
  color: white;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  text-decoration: none;
  color: inherit;
  display: block;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.action-card:hover::before {
  left: 100%;
}

.action-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.action-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.action-card p {
  color: #666;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* 学习进度区域 */
.progress-section {
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.progress-section h2 {
  color: white;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.progress-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-info h3 {
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
}

.progress-text {
  color: #666;
  font-size: 0.95rem;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e1e5e9;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  border-radius: 6px;
  transition: width 1s ease-out;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 最近活动区域 */
.recent-activities {
  position: relative;
  z-index: 1;
}

.recent-activities h2 {
  color: white;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.activity-item:hover {
  transform: translateX(5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.activity-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  color: #333;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.3rem 0;
}

.activity-content p {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.4;
}

.activity-time {
  color: #999;
  font-size: 0.85rem;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .welcome-subtitle {
    font-size: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .stat-card {
    padding: 1.5rem;
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .stat-icon {
    font-size: 2.5rem;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .action-card {
    padding: 1.5rem;
  }
  
  .activity-item {
    padding: 1rem;
    flex-direction: column;
    text-align: center;
    gap: 0.8rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-content h3 {
    font-size: 1.5rem;
  }
  
  .action-card {
    padding: 1rem;
  }
  
  .action-icon {
    font-size: 2.5rem;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .stat-card,
  .action-card,
  .progress-card,
  .activity-item {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .stat-content h3,
  .action-card h3,
  .progress-info h3,
  .activity-content h4 {
    color: #f0f0f0;
  }
  
  .stat-content p,
  .action-card p,
  .progress-text,
  .activity-content p {
    color: #b0b0b0;
  }
  
  .activity-time {
    color: #888;
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .dashboard {
    background: #000;
  }
  
  .stat-card,
  .action-card,
  .progress-card,
  .activity-item {
    background: #fff;
    border: 2px solid #000;
  }
  
  .welcome-title,
  .quick-actions h2,
  .progress-section h2,
  .recent-activities h2 {
    color: #fff;
    text-shadow: 2px 2px 4px #000;
  }
}

/* 焦点状态 */
.action-card:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .stat-card,
  .action-card,
  .activity-item {
    min-height: 44px;
  }
  
  .stat-card:hover,
  .action-card:hover,
  .activity-item:hover {
    transform: none;
  }
}
</style>

