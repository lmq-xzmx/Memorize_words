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
  min-height: 100vh;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.challenge-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.challenge-title {
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin-bottom: 10px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.challenge-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 400;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 25px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #4facfe;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.progress-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.progress-container h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: rgba(79, 172, 254, 0.2);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 6px;
  transition: width 0.3s ease;
  box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3);
}

.progress-text {
  margin: 0;
  color: #666;
  font-size: 14px;
  text-align: center;
}

.challenge-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: white;
  margin-bottom: 20px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.word-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.word-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.word-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.word-text {
  font-size: 24px;
  font-weight: 700;
  color: #4facfe;
  margin-bottom: 8px;
}

.word-phonetic {
  font-size: 14px;
  color: #888;
  margin-bottom: 10px;
  font-style: italic;
}

.word-definition {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 500;
}

.word-example {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  font-style: italic;
  padding: 10px;
  background: rgba(79, 172, 254, 0.1);
  border-radius: 8px;
  border-left: 3px solid #4facfe;
}

.word-mastery {
  font-size: 12px;
  color: #888;
  margin-bottom: 15px;
  font-weight: 500;
}

.challenge-actions {
  display: flex;
  gap: 10px;
}

.btn-challenge {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: none;
}

.btn-mastered {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.btn-mastered:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(79, 172, 254, 0.3);
}

.btn-difficult {
  background: linear-gradient(135deg, #ffa726 0%, #ff7043 100%);
  color: white;
}

.btn-difficult:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 167, 38, 0.3);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.empty-state h3 {
  font-size: 24px;
  color: #4facfe;
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 16px;
  color: #666;
  margin-bottom: 20px;
}

.btn-add-words {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-add-words:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.suggestion-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.suggestion-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.suggestion-card h4 {
  font-size: 16px;
  color: #4facfe;
  margin-bottom: 10px;
  font-weight: 600;
}

.suggestion-card p {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.message-toast.success {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
}

.message-toast.error {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
}

.message-toast.warning {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
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
  .word-challenge {
    padding: 15px;
  }
  
  .challenge-title {
    font-size: 24px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-number {
    font-size: 28px;
  }
  
  .word-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .word-card {
    padding: 20px;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .challenge-header {
    padding: 20px 15px;
  }
  
  .challenge-title {
    font-size: 20px;
  }
  
  .challenge-subtitle {
    font-size: 14px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .challenge-actions {
    flex-direction: column;
  }
  
  .message-toast {
    right: 10px;
    left: 10px;
    top: 10px;
  }
}
</style>

