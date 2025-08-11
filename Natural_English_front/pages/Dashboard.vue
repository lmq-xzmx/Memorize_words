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

export default {
  name: 'Dashboard',
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
    await this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        const [statsRes, progressRes, activitiesRes] = await Promise.all([
          api.getUserStats(),
          api.getUserProgress(),
          api.getRecentActivities()
        ])
        
        this.stats = statsRes.data
        this.progress = progressRes.data
        this.recentActivities = activitiesRes.data
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
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 16px;
}

.stat-content h3 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.stat-content p {
  color: #7f8c8d;
  margin: 0;
}

.quick-actions, .progress-section, .recent-section {
  margin-bottom: 40px;
}

.quick-actions h2, .progress-section h2, .recent-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: all 0.2s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.action-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.action-card h3 {
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.action-card p {
  color: #7f8c8d;
  margin: 0;
}

.progress-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-weight: 600;
  color: #2c3e50;
}

.progress-bar {
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.progress-text {
  color: #7f8c8d;
  margin: 0;
}

.recent-list {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.recent-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-icon {
  font-size: 2rem;
  margin-right: 16px;
}

.recent-content h4 {
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.recent-content p {
  color: #7f8c8d;
  margin: 0 0 4px 0;
}

.recent-time {
  color: #bdc3c7;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 15px;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>