<template>
  <div class="listening-container">
    <div class="page-header">
      <h1>听说训练中心</h1>
      <p>提升听力和口语能力</p>
    </div>
    
    <div class="content-grid">
      <!-- 训练模式选择 -->
      <div class="mode-section">
        <h2>训练模式</h2>
        <div class="mode-cards">
          <div class="mode-card" @click="startMode('listening')">
            <div class="mode-icon">👂</div>
            <h3>听力训练</h3>
            <p>通过音频材料提升听力理解</p>
          </div>
          <div class="mode-card" @click="startMode('speaking')">
            <div class="mode-icon">🗣️</div>
            <h3>口语练习</h3>
            <p>跟读练习，提升发音准确度</p>
          </div>
          <div class="mode-card" @click="startMode('conversation')">
            <div class="mode-icon">💬</div>
            <h3>对话练习</h3>
            <p>模拟真实对话场景</p>
          </div>
        </div>
      </div>
      
      <!-- 学习统计 -->
      <div class="stats-section">
        <h2>训练统计</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalMinutes }}</div>
            <div class="stat-label">总训练时长(分钟)</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.listeningAccuracy }}%</div>
            <div class="stat-label">听力准确率</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.speakingScore }}</div>
            <div class="stat-label">口语评分</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.todayMinutes }}</div>
            <div class="stat-label">今日训练(分钟)</div>
          </div>
        </div>
      </div>
      
      <!-- 推荐内容 -->
      <div class="recommended-section">
        <h2>推荐内容</h2>
        <div class="content-list">
          <div v-for="content in recommendedContent" :key="content.id" class="content-item" @click="startContent(content)">
            <div class="content-thumbnail">
              <div class="content-type-icon">{{ getContentIcon(content.type) }}</div>
            </div>
            <div class="content-info">
              <div class="content-title">{{ content.title }}</div>
              <div class="content-description">{{ content.description }}</div>
              <div class="content-meta">
                <span class="content-duration">{{ content.duration }}</span>
                <span class="content-level" :class="content.level">{{ getLevelText(content.level) }}</span>
              </div>
            </div>
            <div class="content-action">
              <button class="play-btn">开始</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 最近练习 -->
      <div class="recent-section">
        <h2>最近练习</h2>
        <div class="recent-list">
          <div v-for="item in recentPractice" :key="item.id" class="recent-item">
            <div class="recent-info">
              <div class="recent-title">{{ item.title }}</div>
              <div class="recent-time">{{ item.practiceTime }}</div>
            </div>
            <div class="recent-score">
              <div class="score-value">{{ item.score }}%</div>
              <div class="score-label">准确率</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Listening',
  data() {
    return {
      stats: {
        totalMinutes: 245,
        listeningAccuracy: 85,
        speakingScore: 78,
        todayMinutes: 25
      },
      recommendedContent: [
        {
          id: 1,
          title: '日常对话练习',
          description: '学习日常生活中的英语对话',
          duration: '15分钟',
          level: 'beginner',
          type: 'conversation'
        },
        {
          id: 2,
          title: '新闻听力训练',
          description: '通过新闻提升听力理解能力',
          duration: '20分钟',
          level: 'intermediate',
          type: 'listening'
        },
        {
          id: 3,
          title: '发音纠正练习',
          description: '针对性改善发音问题',
          duration: '10分钟',
          level: 'beginner',
          type: 'speaking'
        },
        {
          id: 4,
          title: '商务英语对话',
          description: '职场英语交流技巧',
          duration: '25分钟',
          level: 'advanced',
          type: 'conversation'
        }
      ],
      recentPractice: [
        { id: 1, title: '日常对话练习', practiceTime: '2小时前', score: 88 },
        { id: 2, title: '发音纠正练习', practiceTime: '昨天', score: 92 },
        { id: 3, title: '新闻听力训练', practiceTime: '2天前', score: 76 },
        { id: 4, title: '商务英语对话', practiceTime: '3天前', score: 82 }
      ]
    }
  },
  methods: {
    startMode(mode) {
      console.log('Starting mode:', mode)
      this.$router.push(`/listening/${mode}`)
    },
    startContent(content) {
      console.log('Starting content:', content)
      this.$router.push(`/listening/content/${content.id}`)
    },
    getContentIcon(type) {
      const iconMap = {
        'listening': '👂',
        'speaking': '🗣️',
        'conversation': '💬'
      }
      return iconMap[type] || '📚'
    },
    getLevelText(level) {
      const levelMap = {
        'beginner': '初级',
        'intermediate': '中级',
        'advanced': '高级'
      }
      return levelMap[level] || '未知'
    }
  }
}
</script>

<style scoped>
.listening-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  padding: 20px;
  padding-bottom: 80px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-header p {
  font-size: 16px;
  opacity: 0.9;
}

.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  gap: 30px;
}

.mode-section,
.stats-section,
.recommended-section,
.recent-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.mode-section h2,
.stats-section h2,
.recommended-section h2,
.recent-section h2 {
  margin-bottom: 20px;
  color: #2d3748;
  font-size: 20px;
  font-weight: 700;
}

.mode-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.mode-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.mode-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.mode-card h3 {
  margin-bottom: 10px;
  color: #2d3748;
  font-weight: 600;
}

.mode-card p {
  color: #718096;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: rgba(168, 237, 234, 0.2);
  border-radius: 15px;
  border: 1px solid rgba(168, 237, 234, 0.3);
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #319795;
  margin-bottom: 5px;
}

.stat-label {
  color: #718096;
  font-size: 12px;
  font-weight: 500;
}

.content-list,
.recent-list {
  display: grid;
  gap: 15px;
}

.content-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.content-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.content-thumbnail {
  width: 60px;
  height: 60px;
  background: rgba(168, 237, 234, 0.3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.content-type-icon {
  font-size: 24px;
}

.content-info {
  flex: 1;
}

.content-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 5px;
}

.content-description {
  color: #718096;
  font-size: 14px;
  margin-bottom: 8px;
}

.content-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.content-duration {
  color: #718096;
  font-size: 12px;
}

.content-level {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.content-level.beginner {
  background: #c6f6d5;
  color: #22543d;
}

.content-level.intermediate {
  background: #feebc8;
  color: #7b341e;
}

.content-level.advanced {
  background: #fed7d7;
  color: #742a2a;
}

.content-action {
  margin-left: 15px;
}

.play-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #2d3748;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.play-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.recent-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(5px);
}

.recent-info {
  flex: 1;
}

.recent-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 5px;
}

.recent-time {
  color: #718096;
  font-size: 14px;
}

.recent-score {
  text-align: center;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
  color: #319795;
  margin-bottom: 2px;
}

.score-label {
  color: #718096;
  font-size: 12px;
}

@media (max-width: 768px) {
  .mode-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .content-thumbnail {
    margin-right: 0;
  }
  
  .content-action {
    margin-left: 0;
    align-self: stretch;
  }
  
  .play-btn {
    width: 100%;
  }
}
</style>