<template>
  <div class="word-challenge">
    <!-- 页面头部 -->
    <div class="challenge-header">
      <h1 class="challenge-title">🗡️ 单词斩</h1>
      <p class="challenge-subtitle">挑战你的词汇极限，斩断遗忘的枷锁</p>
    </div>
    
    <!-- 学习统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ totalWords }}</div>
        <div class="stat-label">总单词数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ learnedWords }}</div>
        <div class="stat-label">已掌握</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ learningProgress }}%</div>
        <div class="stat-label">掌握进度</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ challengeWords.length }}</div>
        <div class="stat-label">今日挑战</div>
      </div>
    </div>
    
    <!-- 学习进度 -->
    <div class="progress-container">
      <h3>学习进度</h3>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: learningProgress + '%' }"></div>
      </div>
      <p class="progress-text">
        已掌握 {{ learnedWords }} 个单词，还需努力 {{ totalWords - learnedWords }} 个单词
      </p>
    </div>
    
    <!-- 挑战单词 -->
    <div class="challenge-section">
      <h2 class="section-title">🗡️ 今日挑战</h2>
      
      <div v-if="challengeWords.length > 0" class="word-grid">
        <div 
          v-for="word in challengeWords" 
          :key="word.id" 
          class="word-card"
          :data-word-id="word.id"
        >
          <div class="word-text">{{ word.word }}</div>
          <div v-if="word.phonetic" class="word-phonetic">[{{ word.phonetic }}]</div>
          <div class="word-definition">{{ word.definition || '暂无释义' }}</div>
          <div v-if="word.example" class="word-example">例: {{ word.example }}</div>
          <div class="word-mastery">掌握度: {{ word.mastery_level }}%</div>
          <div class="challenge-actions">
            <button class="btn-challenge btn-mastered" @click="markAsLearned(word.id)">
              ✅ 已掌握
            </button>
            <button class="btn-challenge btn-difficult" @click="markAsDifficult(word.id)">
              ⚠️ 有难度
            </button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <h3>🎉 太棒了！</h3>
        <p>你已经掌握了所有单词，继续保持！</p>
        <button class="btn-add-words" @click="addMoreWords">
          ➕ 添加更多单词
        </button>
      </div>
    </div>
    
    <!-- 学习建议 -->
    <div class="challenge-section">
      <h2 class="section-title">💡 学习建议</h2>
      <div class="suggestions-grid">
        <div class="suggestion-card">
          <h4>📚 每日复习</h4>
          <p>建议每天复习已掌握的单词，巩固记忆效果。</p>
        </div>
        <div class="suggestion-card">
          <h4>🎯 重点突破</h4>
          <p>对于有难度的单词，可以多花时间重点学习。</p>
        </div>
        <div class="suggestion-card">
          <h4>⏰ 坚持打卡</h4>
          <p>保持每日学习习惯，建立长期记忆。</p>
        </div>
      </div>
    </div>
    
    <!-- 消息提示 -->
    <div v-if="message" class="message-toast" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'WordChallenge',
  data() {
    return {
      totalWords: 0,
      learnedWords: 0,
      learningProgress: 0,
      challengeWords: [],
      message: '',
      messageType: 'success'
    }
  },
  mounted() {
    this.loadChallengeData()
  },
  methods: {
    // 加载挑战数据
    async loadChallengeData() {
      try {
        // 模拟API调用
        const response = await fetch('/api/words/statistics/')
        if (response.ok) {
          const data = await response.json()
          this.totalWords = data.total_words || 0
          this.learnedWords = data.learned_words || 0
          this.learningProgress = data.learning_rate || 0
        } else {
          // 使用模拟数据
          this.loadMockData()
        }
      } catch (error) {
        console.log('使用模拟数据')
        this.loadMockData()
      }
    },
    
    // 加载模拟数据
    loadMockData() {
      this.totalWords = 150
      this.learnedWords = 85
      this.learningProgress = Math.round((this.learnedWords / this.totalWords) * 100)
      
      this.challengeWords = [
        {
          id: 1,
          word: 'apple',
          phonetic: 'ˈæpl',
          definition: '苹果',
          example: 'I eat an apple every day.',
          mastery_level: 30
        },
        {
          id: 2,
          word: 'beautiful',
          phonetic: 'ˈbjuːtɪfʊl',
          definition: '美丽的',
          example: 'She is a beautiful girl.',
          mastery_level: 25
        },
        {
          id: 3,
          word: 'computer',
          phonetic: 'kəmˈpjuːtə',
          definition: '计算机',
          example: 'I use my computer to work.',
          mastery_level: 45
        },
        {
          id: 4,
          word: 'difficult',
          phonetic: 'ˈdɪfɪkəlt',
          definition: '困难的',
          example: 'This question is very difficult.',
          mastery_level: 20
        },
        {
          id: 5,
          word: 'education',
          phonetic: 'ˌedʒuˈkeɪʃn',
          definition: '教育',
          example: 'Education is very important.',
          mastery_level: 35
        }
      ]
    },
    
    // 标记为已掌握
    async markAsLearned(wordId) {
      try {
        await this.$api.wordAPI.markAsLearned(wordId)
        this.showMessage('✅ 单词已标记为已掌握！', 'success')
        this.updateWordStatus(wordId, true)
      } catch (error) {
        console.error('标记单词失败:', error)
        this.showMessage('❌ 操作失败，请重试', 'error')
      }
    },
    
    // 标记为有难度
    async markAsDifficult(wordId) {
      try {
        await this.$api.wordAPI.updateMastery(wordId, 1)
        this.showMessage('⚠️ 单词已标记为有难度，将重点复习', 'warning')
      } catch (error) {
        console.error('标记单词难度失败:', error)
        this.showMessage('❌ 操作失败，请重试', 'error')
      }
    },
    
    // 更新单词状态
    updateWordStatus(wordId, isLearned) {
      const wordIndex = this.challengeWords.findIndex(w => w.id === wordId)
      if (wordIndex !== -1) {
        const word = this.challengeWords[wordIndex]
        if (isLearned) {
          word.mastery_level = 100
          this.learnedWords++
          this.learningProgress = Math.round((this.learnedWords / this.totalWords) * 100)
        }
      }
    },
    
    // 显示消息提示
    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 3000)
    },
    
    // 添加更多单词
    addMoreWords() {
      this.$router.push('/dashboard')
    }
  }
}
</script>

<style scoped>
.word-challenge {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.challenge-header {
  text-align: center;
  margin-bottom: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.challenge-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.challenge-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.progress-container {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-top: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 10px;
  transition: width 0.5s ease;
}

.progress-text {
  margin-top: 10px;
  color: #666;
}

.challenge-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.word-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.word-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.word-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

.word-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.word-card:hover::before {
  left: 100%;
}

.word-text {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.word-phonetic {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 10px;
}

.word-definition {
  font-size: 1rem;
  margin-bottom: 15px;
  line-height: 1.4;
}

.word-example {
  font-size: 0.9rem;
  opacity: 0.9;
  font-style: italic;
  margin-bottom: 10px;
}

.word-mastery {
  margin-top: 10px;
  font-size: 0.9rem;
  opacity: 0.8;
}

.challenge-actions {
  display: flex;
  gap: 15px;
  margin-top: 15px;
}

.btn-challenge {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-mastered {
  background: #28a745;
  color: white;
}

.btn-mastered:hover {
  background: #218838;
  transform: scale(1.05);
}

.btn-difficult {
  background: #ffc107;
  color: #333;
}

.btn-difficult:hover {
  background: #e0a800;
  transform: scale(1.05);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: #333;
}

.empty-state p {
  font-size: 1rem;
  margin-bottom: 20px;
}

.btn-add-words {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  cursor: pointer;
}

.btn-add-words:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.suggestion-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #28a745;
}

.suggestion-card h4 {
  color: #28a745;
  margin-bottom: 10px;
}

.suggestion-card p {
  color: #666;
  font-size: 0.9rem;
}

.suggestion-card:nth-child(2) {
  border-left-color: #ffc107;
}

.suggestion-card:nth-child(2) h4 {
  color: #ffc107;
}

.suggestion-card:nth-child(3) {
  border-left-color: #17a2b8;
}

.suggestion-card:nth-child(3) h4 {
  color: #17a2b8;
}

.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 5px;
  color: white;
  font-weight: bold;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.message-toast.success {
  background: #28a745;
}

.message-toast.error {
  background: #dc3545;
}

.message-toast.warning {
  background: #ffc107;
  color: #333;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .challenge-title {
    font-size: 2rem;
  }
  
  .word-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}
</style>