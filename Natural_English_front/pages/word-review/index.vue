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
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header h1 {
  font-size: 36px;
  font-weight: 700;
  color: white;
  margin-bottom: 10px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 400;
}

.review-content {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.stat-card h3 {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-number {
  font-size: 48px;
  font-weight: 700;
  color: #667eea;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.review-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.btn {
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  min-width: 150px;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
  color: #333;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(255, 234, 167, 0.3);
}

.btn-success {
  background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
  color: white;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 184, 148, 0.3);
}

.btn-danger {
  background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
  color: white;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(225, 112, 85, 0.3);
}

.review-session {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 30px;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.word-card {
  text-align: center;
}

.word-card h2 {
  font-size: 48px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 15px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.phonetic {
  font-size: 20px;
  color: #888;
  margin-bottom: 20px;
  font-style: italic;
  font-weight: 500;
}

.definition {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  font-weight: 600;
  line-height: 1.4;
}

.example {
  font-size: 18px;
  color: #666;
  margin-bottom: 40px;
  font-style: italic;
  padding: 20px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  border-left: 4px solid #667eea;
  line-height: 1.5;
}

.review-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
}

.results-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.results-section h2 {
  font-size: 32px;
  color: #667eea;
  margin-bottom: 30px;
  font-weight: 700;
}

.results-stats {
  margin-bottom: 30px;
}

.results-stats p {
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .word-review-container {
    padding: 15px;
  }
  
  .header {
    padding: 30px 15px;
  }
  
  .header h1 {
    font-size: 28px;
  }
  
  .subtitle {
    font-size: 16px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stat-card {
    padding: 25px;
  }
  
  .stat-number {
    font-size: 36px;
  }
  
  .review-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 300px;
  }
  
  .review-session {
    padding: 25px;
  }
  
  .word-card h2 {
    font-size: 36px;
  }
  
  .definition {
    font-size: 20px;
  }
  
  .example {
    font-size: 16px;
    padding: 15px;
  }
  
  .review-buttons {
    flex-direction: column;
    gap: 15px;
  }
  
  .results-section {
    padding: 30px 20px;
  }
  
  .results-section h2 {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .header h1 {
    font-size: 24px;
  }
  
  .word-card h2 {
    font-size: 28px;
  }
  
  .phonetic {
    font-size: 16px;
  }
  
  .definition {
    font-size: 18px;
  }
  
  .example {
    font-size: 14px;
  }
  
  .btn {
    padding: 12px 20px;
    font-size: 14px;
  }
}
</style>

