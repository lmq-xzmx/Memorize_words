<template>
  <div class="word-review-container">
    <div class="header">
      <h1>📚 单词复习</h1>
      <p class="subtitle">巩固已学单词，提升记忆效果</p>
    </div>
    
    <div class="review-content">
      <div class="stats-section">
        <div class="stat-card">
          <h3>待复习单词</h3>
          <div class="stat-number">{{ reviewWords.length }}</div>
        </div>
        <div class="stat-card">
          <h3>今日已复习</h3>
          <div class="stat-number">{{ reviewedToday }}</div>
        </div>
        <div class="stat-card">
          <h3>复习准确率</h3>
          <div class="stat-number">{{ accuracy }}%</div>
        </div>
      </div>
      
      <div class="review-actions">
        <button @click="startReview" class="btn btn-primary" :disabled="reviewWords.length === 0">
          <i class="fas fa-play"></i>
          开始复习
        </button>
        <button @click="resetProgress" class="btn btn-secondary">
          <i class="fas fa-refresh"></i>
          重置进度
        </button>
      </div>
      
      <div v-if="isReviewing" class="review-session">
        <div class="progress-bar">
          <div class="progress" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        
        <div class="word-card">
          <h2>{{ currentWord.word }}</h2>
          <p class="phonetic">{{ currentWord.phonetic }}</p>
          <div class="definition">{{ currentWord.definition }}</div>
          <div class="example">{{ currentWord.example }}</div>
          
          <div class="review-buttons">
            <button @click="markCorrect" class="btn btn-success">
              <i class="fas fa-check"></i>
              记得
            </button>
            <button @click="markIncorrect" class="btn btn-danger">
              <i class="fas fa-times"></i>
              忘记了
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="showResults" class="results-section">
        <h2>复习完成！</h2>
        <div class="results-stats">
          <p>总计复习：{{ totalReviewed }} 个单词</p>
          <p>正确率：{{ finalAccuracy }}%</p>
          <p>需要加强：{{ incorrectWords.length }} 个单词</p>
        </div>
        <button @click="restartReview" class="btn btn-primary">
          再次复习
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WordReview',
  data() {
    return {
      reviewWords: [],
      currentWordIndex: 0,
      isReviewing: false,
      showResults: false,
      reviewedToday: 0,
      correctCount: 0,
      totalReviewed: 0,
      incorrectWords: []
    }
  },
  computed: {
    currentWord() {
      return this.reviewWords[this.currentWordIndex] || {}
    },
    progressPercentage() {
      return this.reviewWords.length > 0 ? (this.currentWordIndex / this.reviewWords.length) * 100 : 0
    },
    accuracy() {
      return this.totalReviewed > 0 ? Math.round((this.correctCount / this.totalReviewed) * 100) : 0
    },
    finalAccuracy() {
      return this.accuracy
    }
  },
  mounted() {
    this.loadReviewWords()
  },
  methods: {
    loadReviewWords() {
      // 模拟加载待复习单词
      this.reviewWords = [
        {
          id: 1,
          word: 'example',
          phonetic: '/ɪɡˈzæmpl/',
          definition: '例子，实例',
          example: 'This is a good example of modern art.'
        },
        {
          id: 2,
          word: 'review',
          phonetic: '/rɪˈvjuː/',
          definition: '复习，回顾',
          example: 'Let\'s review what we learned yesterday.'
        }
      ]
    },
    startReview() {
      this.isReviewing = true
      this.currentWordIndex = 0
      this.correctCount = 0
      this.totalReviewed = 0
      this.incorrectWords = []
      this.showResults = false
    },
    markCorrect() {
      this.correctCount++
      this.nextWord()
    },
    markIncorrect() {
      this.incorrectWords.push(this.currentWord)
      this.nextWord()
    },
    nextWord() {
      this.totalReviewed++
      this.currentWordIndex++
      
      if (this.currentWordIndex >= this.reviewWords.length) {
        this.finishReview()
      }
    },
    finishReview() {
      this.isReviewing = false
      this.showResults = true
      this.reviewedToday += this.totalReviewed
    },
    restartReview() {
      this.startReview()
    },
    resetProgress() {
      this.reviewedToday = 0
      this.correctCount = 0
      this.totalReviewed = 0
      this.incorrectWords = []
      this.isReviewing = false
      this.showResults = false
    }
  }
}
</script>

<style scoped>
.word-review-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #2d3748;
  margin-bottom: 10px;
}

.subtitle {
  color: #718096;
  font-size: 16px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h3 {
  color: #4a5568;
  margin-bottom: 10px;
  font-size: 14px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
}

.review-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 30px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a67d8;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.review-session {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  margin-bottom: 30px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.word-card {
  text-align: center;
}

.word-card h2 {
  font-size: 36px;
  color: #2d3748;
  margin-bottom: 10px;
}

.phonetic {
  font-size: 18px;
  color: #718096;
  margin-bottom: 20px;
  font-style: italic;
}

.definition {
  font-size: 20px;
  color: #4a5568;
  margin-bottom: 15px;
  font-weight: 500;
}

.example {
  font-size: 16px;
  color: #718096;
  margin-bottom: 30px;
  font-style: italic;
}

.review-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.btn-success {
  background: #48bb78;
  color: white;
}

.btn-success:hover {
  background: #38a169;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.results-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.results-section h2 {
  color: #2d3748;
  margin-bottom: 20px;
}

.results-stats {
  margin-bottom: 20px;
}

.results-stats p {
  font-size: 16px;
  color: #4a5568;
  margin-bottom: 8px;
}
</style>