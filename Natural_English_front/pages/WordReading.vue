<template>
  <div class="word-reading-container">
    <div class="page-header">
      <h1>单词学习</h1>
      <p>提升词汇量，掌握英语基础</p>
    </div>
    
    <div class="content-grid">
      <!-- 学习模式选择 -->
      <div class="mode-section">
        <h2>学习模式</h2>
        <div class="mode-cards">
          <div class="mode-card" @click="startMode('flashcard')">
            <div class="mode-icon">📚</div>
            <h3>单词卡片</h3>
            <p>通过卡片形式学习新单词</p>
          </div>
          <div class="mode-card" @click="startMode('spelling')">
            <div class="mode-icon">✍️</div>
            <h3>拼写练习</h3>
            <p>练习单词拼写和记忆</p>
          </div>
          <div class="mode-card" @click="startMode('quiz')">
            <div class="mode-icon">🎯</div>
            <h3>单词测试</h3>
            <p>测试你的词汇掌握程度</p>
          </div>
        </div>
      </div>
      
      <!-- 词汇统计 -->
      <div class="stats-section">
        <h2>学习统计</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalWords }}</div>
            <div class="stat-label">总词汇量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.masteredWords }}</div>
            <div class="stat-label">已掌握</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.todayWords }}</div>
            <div class="stat-label">今日学习</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.streakDays }}</div>
            <div class="stat-label">连续天数</div>
          </div>
        </div>
      </div>
      
      <!-- 最近学习的单词 -->
      <div class="recent-section">
        <h2>最近学习</h2>
        <div class="word-list">
          <div v-for="word in recentWords" :key="word.id" class="word-item">
            <div class="word-content">
              <div class="word-text">{{ word.word }}</div>
              <div class="word-meaning">{{ word.meaning }}</div>
            </div>
            <div class="word-status" :class="word.status">
              {{ getStatusText(word.status) }}
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
  name: 'WordReading',
  mixins: [permissionMixin],
  data() {
    return {
      stats: {
        totalWords: 1250,
        masteredWords: 680,
        todayWords: 25,
        streakDays: 7
      },
      recentWords: [
        { id: 1, word: 'abundant', meaning: '丰富的，充裕的', status: 'mastered' },
        { id: 2, word: 'challenge', meaning: '挑战，质疑', status: 'learning' },
        { id: 3, word: 'determine', meaning: '决定，确定', status: 'mastered' },
        { id: 4, word: 'efficient', meaning: '高效的，有效的', status: 'review' },
        { id: 5, word: 'flexible', meaning: '灵活的，可弯曲的', status: 'learning' }
      ]
    }
  },
  methods: {
    startMode(mode) {
      // 检查不同模式的权限
      const modePermissions = {
        'flashcard': 'view_word_learning',
        'spelling': 'practice_spelling',
        'quiz': 'take_word_quiz'
      }
      
      const requiredPermission = modePermissions[mode]
      if (requiredPermission && !this.$hasPermission(requiredPermission)) {
        this.$showError(`您没有权限使用${this.getModeDisplayName(mode)}功能`)
        return
      }
      
      console.log('Starting mode:', mode)
      // 这里可以跳转到具体的学习模式页面
      this.$router.push(`/word-learning/${mode}`)
    },
    
    getModeDisplayName(mode) {
      const modeNames = {
        'flashcard': '单词卡片',
        'spelling': '拼写练习',
        'quiz': '单词测试'
      }
      return modeNames[mode] || mode
    },
    getStatusText(status) {
      const statusMap = {
        'mastered': '已掌握',
        'learning': '学习中',
        'review': '待复习'
      }
      return statusMap[status] || '未知'
    }
  },
  
  async created() {
    // 检查页面访问权限
    if (!this.$hasPermission('view_word_reading')) {
      this.$showError('您没有权限访问单词阅读页面')
      this.$router.push('/dashboard')
      return
    }
    
    // 检查统计数据查看权限
    if (!this.$hasPermission('view_learning_stats')) {
      // 如果没有统计权限，隐藏统计数据
      this.stats = {
        totalWords: 0,
        masteredWords: 0,
        todayWords: 0,
        streakDays: 0
      }
    }
  }
}
</script>

<style scoped>
.word-reading-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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
.recent-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.mode-section h2,
.stats-section h2,
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
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: rgba(79, 172, 254, 0.1);
  border-radius: 15px;
  border: 1px solid rgba(79, 172, 254, 0.2);
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #4facfe;
  margin-bottom: 5px;
}

.stat-label {
  color: #718096;
  font-size: 14px;
  font-weight: 500;
}

.word-list {
  display: grid;
  gap: 15px;
}

.word-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.word-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(5px);
}

.word-content {
  flex: 1;
}

.word-text {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 5px;
}

.word-meaning {
  color: #718096;
  font-size: 14px;
}

.word-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.word-status.mastered {
  background: #c6f6d5;
  color: #22543d;
}

.word-status.learning {
  background: #fed7d7;
  color: #742a2a;
}

.word-status.review {
  background: #feebc8;
  color: #7b341e;
}

@media (max-width: 768px) {
  .mode-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .word-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>

