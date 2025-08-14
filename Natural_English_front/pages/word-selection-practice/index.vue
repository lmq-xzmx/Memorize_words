<template>
  <div class="word-selection-practice">
    <!-- 页面头部 -->
    <div class="practice-header">
      <h1 class="practice-title">📝 单词选择练习</h1>
      <p class="practice-subtitle">选择正确的单词含义，提升词汇理解能力</p>
    </div>
    
    <!-- 练习统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ totalQuestions }}</div>
        <div class="stat-label">总题数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ correctAnswers }}</div>
        <div class="stat-label">正确数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ accuracy }}%</div>
        <div class="stat-label">准确率</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ currentQuestion }}</div>
        <div class="stat-label">当前题目</div>
      </div>
    </div>
    
    <!-- 练习区域 -->
    <div class="practice-section">
      <div v-if="questions.length > 0 && currentQuestionIndex < questions.length" class="question-container">
        <div class="question-header">
          <h2 class="question-word">{{ currentQuestionData.word }}</h2>
          <div class="question-phonetic">{{ currentQuestionData.phonetic }}</div>
        </div>
        
        <div class="options-container">
          <div 
            v-for="(option, index) in currentQuestionData.options" 
            :key="index"
            class="option-card"
            :class="{ 
              'selected': selectedOption === index,
              'correct': showResult && index === currentQuestionData.correctAnswer,
              'incorrect': showResult && selectedOption === index && index !== currentQuestionData.correctAnswer
            }"
            @click="selectOption(index)"
          >
            <div class="option-letter">{{ String.fromCharCode(65 + index) }}</div>
            <div class="option-text">{{ option }}</div>
          </div>
        </div>
        
        <div class="action-buttons">
          <button 
            v-if="!showResult" 
            @click="submitAnswer" 
            :disabled="selectedOption === null"
            class="submit-btn"
          >
            提交答案
          </button>
          <button 
            v-if="showResult" 
            @click="nextQuestion" 
            class="next-btn"
          >
            {{ currentQuestionIndex < questions.length - 1 ? '下一题' : '完成练习' }}
          </button>
        </div>
        
        <div v-if="showResult" class="result-feedback">
          <div v-if="isCorrect" class="correct-feedback">
            ✅ 回答正确！
          </div>
          <div v-else class="incorrect-feedback">
            ❌ 回答错误，正确答案是：{{ currentQuestionData.options[currentQuestionData.correctAnswer] }}
          </div>
        </div>
      </div>
      
      <!-- 练习完成 -->
      <div v-else-if="questions.length > 0" class="completion-container">
        <div class="completion-content">
          <h2>🎉 练习完成！</h2>
          <div class="final-stats">
            <div class="final-stat">
              <span class="stat-label">总题数：</span>
              <span class="stat-value">{{ totalQuestions }}</span>
            </div>
            <div class="final-stat">
              <span class="stat-label">正确数：</span>
              <span class="stat-value">{{ correctAnswers }}</span>
            </div>
            <div class="final-stat">
              <span class="stat-label">准确率：</span>
              <span class="stat-value">{{ accuracy }}%</span>
            </div>
          </div>
          <div class="completion-actions">
            <button @click="restartPractice" class="restart-btn">重新练习</button>
            <button @click="goBack" class="back-btn">返回选择</button>
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-else class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载练习题目...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WordSelectionPractice',
  data() {
    return {
      questions: [],
      currentQuestionIndex: 0,
      selectedOption: null,
      showResult: false,
      isCorrect: false,
      correctAnswers: 0,
      totalQuestions: 0
    }
  },
  computed: {
    currentQuestion() {
      return this.currentQuestionIndex + 1
    },
    currentQuestionData() {
      return this.questions[this.currentQuestionIndex] || {}
    },
    accuracy() {
      return this.totalQuestions > 0 ? Math.round((this.correctAnswers / this.totalQuestions) * 100) : 0
    }
  },
  mounted() {
    this.loadQuestions()
  },
  methods: {
    loadQuestions() {
      // 模拟加载题目数据
      this.questions = [
        {
          word: 'apple',
          phonetic: '/ˈæpl/',
          options: ['苹果', '橙子', '香蕉', '葡萄'],
          correctAnswer: 0
        },
        {
          word: 'beautiful',
          phonetic: '/ˈbjuːtɪfl/',
          options: ['丑陋的', '美丽的', '普通的', '奇怪的'],
          correctAnswer: 1
        },
        {
          word: 'computer',
          phonetic: '/kəmˈpjuːtər/',
          options: ['电视', '收音机', '计算机', '电话'],
          correctAnswer: 2
        }
      ]
      this.totalQuestions = this.questions.length
    },
    selectOption(index) {
      if (!this.showResult) {
        this.selectedOption = index
      }
    },
    submitAnswer() {
      if (this.selectedOption !== null) {
        this.isCorrect = this.selectedOption === this.currentQuestionData.correctAnswer
        if (this.isCorrect) {
          this.correctAnswers++
        }
        this.showResult = true
      }
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
        this.selectedOption = null
        this.showResult = false
        this.isCorrect = false
      } else {
        // 练习完成
        this.currentQuestionIndex = this.questions.length
      }
    },
    restartPractice() {
      this.currentQuestionIndex = 0
      this.selectedOption = null
      this.showResult = false
      this.isCorrect = false
      this.correctAnswers = 0
      this.loadQuestions()
    },
    goBack() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.word-selection-practice {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 120px;
}

.practice-header {
  text-align: center;
  color: white;
  margin-bottom: 30px;
}

.practice-title {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.practice-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  max-width: 800px;
  margin: 0 auto 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.practice-section {
  max-width: 800px;
  margin: 0 auto;
}

.question-container {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.question-header {
  text-align: center;
  margin-bottom: 30px;
}

.question-word {
  font-size: 3rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.question-phonetic {
  font-size: 1.2rem;
  color: #666;
  font-style: italic;
}

.options-container {
  display: grid;
  gap: 15px;
  margin-bottom: 30px;
}

.option-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

.option-card:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.option-card.selected {
  border-color: #667eea;
  background: #e8f0ff;
}

.option-card.correct {
  border-color: #4caf50;
  background: #e8f5e8;
}

.option-card.incorrect {
  border-color: #f44336;
  background: #ffeaea;
}

.option-letter {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin-right: 15px;
}

.option-text {
  font-size: 1.1rem;
  color: #333;
}

.action-buttons {
  text-align: center;
  margin-bottom: 20px;
}

.submit-btn, .next-btn {
  padding: 12px 30px;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn {
  background: #667eea;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.next-btn {
  background: #4caf50;
  color: white;
}

.next-btn:hover {
  background: #45a049;
}

.result-feedback {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
}

.correct-feedback {
  color: #4caf50;
}

.incorrect-feedback {
  color: #f44336;
}

.completion-container {
  background: white;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.completion-content h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 30px;
}

.final-stats {
  margin-bottom: 30px;
}

.final-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  font-size: 1.1rem;
}

.final-stat:last-child {
  border-bottom: none;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: 700;
  color: #333;
}

.completion-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.restart-btn, .back-btn {
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.restart-btn {
  background: #667eea;
  color: white;
}

.restart-btn:hover {
  background: #5a6fd8;
}

.back-btn {
  background: #f0f0f0;
  color: #333;
}

.back-btn:hover {
  background: #e0e0e0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .practice-title {
    font-size: 2rem;
  }
  
  .question-word {
    font-size: 2.5rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .completion-actions {
    flex-direction: column;
  }
}
</style>