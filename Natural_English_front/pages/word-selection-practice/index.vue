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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding: 1rem;
}

/* 页面头部 */
.practice-header {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.practice-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.practice-subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
  font-weight: 400;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* 练习区域 */
.practice-section {
  max-width: 900px;
  margin: 0 auto;
}

.question-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.question-header {
  text-align: center;
  margin-bottom: 2rem;
}

.question-word {
  font-size: 3rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.02em;
}

.question-phonetic {
  font-size: 1.25rem;
  color: #6b7280;
  font-family: 'Courier New', monospace;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  display: inline-block;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

/* 选项容器 */
.options-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.option-card {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  overflow: hidden;
}

.option-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.option-card.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
}

.option-card.correct {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.2);
}

.option-card.incorrect {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.2);
}

.option-letter {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.option-card.correct .option-letter {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.option-card.incorrect .option-letter {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.option-text {
  font-size: 1.125rem;
  color: #2d3748;
  font-weight: 500;
  flex: 1;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.submit-btn, .next-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  min-width: 150px;
}

.submit-btn:hover, .next-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

/* 结果反馈 */
.result-feedback {
  text-align: center;
  margin-top: 1rem;
}

.correct-feedback {
  color: #10b981;
  font-size: 1.25rem;
  font-weight: 600;
  padding: 1rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.incorrect-feedback {
  color: #ef4444;
  font-size: 1.25rem;
  font-weight: 600;
  padding: 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* 完成页面 */
.completion-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.completion-content h2 {
  font-size: 2.5rem;
  color: #2d3748;
  margin: 0 0 2rem 0;
  font-weight: 700;
}

.final-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.final-stat {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.final-stat .stat-label {
  font-size: 1rem;
  color: #6b7280;
  font-weight: 500;
}

.final-stat .stat-value {
  font-size: 1.5rem;
  color: #667eea;
  font-weight: 700;
  margin-left: 0.5rem;
}

.completion-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.restart-btn, .back-btn {
  padding: 1rem 2rem;
  border-radius: 25px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 150px;
}

.restart-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.restart-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.back-btn {
  background: #f8fafc;
  color: #4a5568;
  border: 2px solid #e2e8f0;
}

.back-btn:hover {
  background: #e2e8f0;
  transform: translateY(-2px);
}

/* 加载状态 */
.loading-container {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  font-size: 1.125rem;
  margin: 0;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .word-selection-practice {
    padding: 0.5rem;
  }

  .practice-title {
    font-size: 2rem;
  }

  .practice-subtitle {
    font-size: 1rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-number {
    font-size: 1.5rem;
  }

  .question-container {
    padding: 1.5rem;
  }

  .question-word {
    font-size: 2rem;
  }

  .question-phonetic {
    font-size: 1rem;
  }

  .options-container {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .option-card {
    padding: 1rem;
  }

  .option-text {
    font-size: 1rem;
  }

  .completion-container {
    padding: 2rem 1rem;
  }

  .completion-content h2 {
    font-size: 2rem;
  }

  .final-stats {
    grid-template-columns: 1fr;
  }

  .completion-actions {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .practice-title {
    font-size: 1.75rem;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .question-word {
    font-size: 1.75rem;
  }

  .submit-btn, .next-btn, .restart-btn, .back-btn {
    padding: 0.875rem 1.5rem;
    font-size: 1rem;
    min-width: 120px;
  }
}
</style>

