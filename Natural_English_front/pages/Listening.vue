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
import permissionMixin from '../mixins/permissionMixin';

export default {
  name: 'Listening',
  mixins: [permissionMixin],
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
      // 检查不同模式的权限
      const modePermissions = {
        'listening': 'practice_listening',
        'speaking': 'practice_speaking',
        'conversation': 'practice_conversation'
      }
      
      const requiredPermission = modePermissions[mode]
      if (requiredPermission && !this.$hasPermission(requiredPermission)) {
        this.$showError(`您没有权限使用${this.getModeDisplayName(mode)}功能`)
        return
      }
      
      console.log('Starting mode:', mode)
      this.$router.push(`/listening/${mode}`)
    },
    
    startContent(content) {
      // 检查内容访问权限
      const contentPermissions = {
        'listening': 'practice_listening',
        'speaking': 'practice_speaking',
        'conversation': 'practice_conversation'
      }
      
      const requiredPermission = contentPermissions[content.type]
      if (requiredPermission && !this.$hasPermission(requiredPermission)) {
        this.$showError(`您没有权限访问${content.title}`)
        return
      }
      
      console.log('Starting content:', content)
      this.$router.push(`/listening/content/${content.id}`)
    },
    
    getModeDisplayName(mode) {
      const modeNames = {
        'listening': '听力训练',
        'speaking': '口语练习',
        'conversation': '对话练习'
      }
      return modeNames[mode] || mode
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
  },
  
  async created() {
    // 确保权限系统已初始化
    await this.$nextTick()
    
    // 检查页面访问权限
    if (!this.$hasPermission('view_listening_training')) {
      this.$showError('您没有权限访问听说训练中心')
      this.$router.push('/')
      return
    }
    
    // 检查统计数据查看权限
    if (!this.$hasPermission('view_learning_stats')) {
      // 如果没有统计权限，隐藏统计数据
      this.stats = {
        totalMinutes: 0,
        listeningAccuracy: 0,
        speakingScore: 0,
        todayMinutes: 0
      }
    }
    
    // 根据权限过滤推荐内容
    this.recommendedContent = this.recommendedContent.filter(content => {
      const contentPermissions = {
        'listening': 'practice_listening',
        'speaking': 'practice_speaking',
        'conversation': 'practice_conversation'
      }
      const requiredPermission = contentPermissions[content.type]
      return !requiredPermission || this.$hasPermission(requiredPermission)
    })
  }
}
</script>

<style scoped>
.listening-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 100px; /* 为底部导航留出空间 */
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  color: white;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-header p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  gap: 24px;
}

/* 训练模式选择 */
.mode-section h2,
.stats-section h2,
.recommended-section h2,
.recent-section h2 {
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.mode-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.mode-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.mode-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 1);
}

.mode-icon {
  font-size: 3rem;
  margin-bottom: 12px;
  display: block;
}

.mode-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #333;
}

.mode-card p {
  color: #666;
  margin: 0;
  line-height: 1.5;
}

/* 统计数据 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 4px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 推荐内容 */
.content-list {
  display: grid;
  gap: 12px;
}

.content-item {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.content-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 1);
}

.content-thumbnail {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.content-type-icon {
  font-size: 1.5rem;
}

.content-info {
  flex: 1;
}

.content-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.content-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 8px;
  line-height: 1.4;
}

.content-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.content-duration {
  color: #888;
  font-size: 0.85rem;
}

.content-level {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.content-level.beginner {
  background: #e8f5e8;
  color: #2d7d32;
}

.content-level.intermediate {
  background: #fff3e0;
  color: #f57c00;
}

.content-level.advanced {
  background: #ffebee;
  color: #c62828;
}

.content-action {
  flex-shrink: 0;
}

.play-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.play-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 最近练习 */
.recent-list {
  display: grid;
  gap: 12px;
}

.recent-item {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.recent-info {
  flex: 1;
}

.recent-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.recent-time {
  color: #888;
  font-size: 0.85rem;
}

.recent-score {
  text-align: center;
  flex-shrink: 0;
}

.score-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 2px;
}

.score-label {
  color: #666;
  font-size: 0.75rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .listening-container {
    padding: 16px;
    padding-bottom: 100px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .mode-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-item {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .content-meta {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .recent-item {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}
</style>

