<template>
  <view class="challenge-container">
    <!-- 顶部状态栏 -->
    <view class="status-bar">
      <view class="status-left">
        <text class="time">{{ currentTime }}</text>
      </view>
      <view class="status-right">
        <text class="battery">{{ batteryLevel }}%</text>
      </view>
    </view>

    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <view class="nav-center">
        <text class="nav-title">单词挑战</text>
      </view>
      <view class="nav-right">
        <text class="score">得分: {{ currentScore }}</text>
      </view>
    </view>

    <!-- 挑战进度 -->
    <view class="progress-section">
      <view class="progress-info">
        <text class="progress-text">{{ currentQuestion }}/{{ totalQuestions }}</text>
        <text class="level-text">{{ challengeLevel }}</text>
      </view>
      <view class="progress-bar">
        <view class="progress-fill" :style="{ width: progressPercentage + '%' }"></view>
      </view>
    </view>

    <!-- 题目区域 -->
    <view class="question-section">
      <view class="question-type">
        <text class="type-label">{{ questionTypeLabel }}</text>
      </view>
      
      <view class="question-content">
        <view v-if="currentQuestionData.type === 'word-meaning'" class="word-question">
          <text class="question-word">{{ currentQuestionData.word }}</text>
          <text class="question-phonetic">{{ currentQuestionData.phonetic }}</text>
          <text class="question-prompt">选择正确的中文意思</text>
        </view>
        
        <view v-if="currentQuestionData.type === 'meaning-word'" class="meaning-question">
          <text class="question-meaning">{{ currentQuestionData.meaning }}</text>
          <text class="question-prompt">选择对应的英文单词</text>
        </view>
        
        <view v-if="currentQuestionData.type === 'fill-blank'" class="fill-question">
          <text class="question-sentence">{{ currentQuestionData.sentence }}</text>
          <text class="question-prompt">选择正确的单词填空</text>
        </view>
      </view>
    </view>

    <!-- 选项区域 -->
    <view class="options-section">
      <view 
        v-for="(option, index) in currentQuestionData.options" 
        :key="index"
        class="option-item"
        :class="{ 
          'selected': selectedOption === index,
          'correct': showResult && option.isCorrect,
          'wrong': showResult && selectedOption === index && !option.isCorrect
        }"
        @tap="selectOption(index)"
      >
        <text class="option-label">{{ String.fromCharCode(65 + index) }}</text>
        <text class="option-text">{{ option.text }}</text>
        <view v-if="showResult && option.isCorrect" class="result-icon correct-icon">✓</view>
        <view v-if="showResult && selectedOption === index && !option.isCorrect" class="result-icon wrong-icon">✗</view>
      </view>
    </view>

    <!-- 底部控制 -->
    <view class="control-section">
      <view v-if="!showResult" class="answer-controls">
        <button 
          class="submit-btn" 
          :class="{ disabled: selectedOption === null }"
          :disabled="selectedOption === null"
          @tap="submitAnswer"
        >
          提交答案
        </button>
      </view>
      
      <view v-if="showResult" class="result-controls">
        <view class="result-info">
          <text class="result-text" :class="{ correct: isCorrect, wrong: !isCorrect }">
            {{ isCorrect ? '回答正确！' : '回答错误' }}
          </text>
          <text v-if="!isCorrect" class="correct-answer">
            正确答案：{{ getCorrectAnswer() }}
          </text>
        </view>
        <button class="next-btn" @tap="nextQuestion">
          {{ isLastQuestion ? '查看结果' : '下一题' }}
        </button>
      </view>
    </view>

    <!-- 挑战完成弹窗 -->
    <view v-if="showResultModal" class="modal-overlay">
      <view class="modal-content result-modal">
        <view class="modal-header">
          <text class="modal-title">挑战完成！</text>
        </view>
        <view class="result-summary">
          <view class="score-display">
            <text class="final-score">{{ currentScore }}</text>
            <text class="score-label">最终得分</text>
          </view>
          <view class="stats-grid">
            <view class="stat-item">
              <text class="stat-number">{{ correctCount }}</text>
              <text class="stat-label">正确</text>
            </view>
            <view class="stat-item">
              <text class="stat-number">{{ wrongCount }}</text>
              <text class="stat-label">错误</text>
            </view>
            <view class="stat-item">
              <text class="stat-number">{{ Math.round(accuracy) }}%</text>
              <text class="stat-label">准确率</text>
            </view>
          </view>
        </view>
        <view class="modal-actions">
          <button class="action-btn secondary" @tap="restartChallenge">重新挑战</button>
          <button class="action-btn primary" @tap="backToMenu">返回菜单</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'WordChallenge',
  data() {
    return {
      currentTime: '',
      batteryLevel: 85,
      currentScore: 0,
      currentQuestion: 1,
      totalQuestions: 10,
      challengeLevel: '初级挑战',
      selectedOption: null,
      showResult: false,
      showResultModal: false,
      isCorrect: false,
      correctCount: 0,
      wrongCount: 0,
      currentQuestionData: {
        type: 'word-meaning',
        word: 'challenge',
        phonetic: '/ˈtʃælɪndʒ/',
        meaning: '挑战',
        sentence: 'This is a great _____ for me.',
        options: [
          { text: '挑战', isCorrect: true },
          { text: '机会', isCorrect: false },
          { text: '困难', isCorrect: false },
          { text: '问题', isCorrect: false }
        ]
      },
      questionBank: [
        {
          type: 'word-meaning',
          word: 'challenge',
          phonetic: '/ˈtʃælɪndʒ/',
          options: [
            { text: '挑战', isCorrect: true },
            { text: '机会', isCorrect: false },
            { text: '困难', isCorrect: false },
            { text: '问题', isCorrect: false }
          ]
        },
        {
          type: 'meaning-word',
          meaning: '学习',
          options: [
            { text: 'learn', isCorrect: true },
            { text: 'teach', isCorrect: false },
            { text: 'study', isCorrect: false },
            { text: 'read', isCorrect: false }
          ]
        },
        {
          type: 'fill-blank',
          sentence: 'I want to _____ English every day.',
          options: [
            { text: 'practice', isCorrect: true },
            { text: 'forget', isCorrect: false },
            { text: 'ignore', isCorrect: false },
            { text: 'avoid', isCorrect: false }
          ]
        }
      ]
    }
  },
  computed: {
    progressPercentage() {
      return (this.currentQuestion / this.totalQuestions) * 100
    },
    questionTypeLabel() {
      const types = {
        'word-meaning': '英译中',
        'meaning-word': '中译英',
        'fill-blank': '填空题'
      }
      return types[this.currentQuestionData.type] || '选择题'
    },
    isLastQuestion() {
      return this.currentQuestion >= this.totalQuestions
    },
    accuracy() {
      const total = this.correctCount + this.wrongCount
      return total > 0 ? (this.correctCount / total) * 100 : 0
    }
  },
  mounted() {
    this.updateTime()
    this.loadQuestion()
    setInterval(this.updateTime, 1000)
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.currentTime = now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    goBack() {
      uni.navigateBack()
    },
    loadQuestion() {
      if (this.currentQuestion <= this.totalQuestions && this.questionBank.length > 0) {
        const randomIndex = Math.floor(Math.random() * this.questionBank.length)
        this.currentQuestionData = { ...this.questionBank[randomIndex] }
        this.selectedOption = null
        this.showResult = false
      }
    },
    selectOption(index) {
      if (!this.showResult) {
        this.selectedOption = index
      }
    },
    submitAnswer() {
      if (this.selectedOption === null) return
      
      this.showResult = true
      this.isCorrect = this.currentQuestionData.options[this.selectedOption].isCorrect
      
      if (this.isCorrect) {
        this.correctCount++
        this.currentScore += 10
      } else {
        this.wrongCount++
      }
    },
    getCorrectAnswer() {
      const correctOption = this.currentQuestionData.options.find(option => option.isCorrect)
      return correctOption ? correctOption.text : ''
    },
    nextQuestion() {
      if (this.isLastQuestion) {
        this.showResultModal = true
      } else {
        this.currentQuestion++
        this.loadQuestion()
      }
    },
    restartChallenge() {
      this.currentScore = 0
      this.currentQuestion = 1
      this.correctCount = 0
      this.wrongCount = 0
      this.showResultModal = false
      this.loadQuestion()
    },
    backToMenu() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.challenge-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  font-size: 14px;
}

.nav-bar {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-left {
  width: 40px;
}

.back-icon {
  font-size: 24px;
  font-weight: bold;
}

.nav-center {
  flex: 1;
  text-align: center;
}

.nav-title {
  font-size: 18px;
  font-weight: bold;
}

.nav-right {
  font-size: 14px;
}

.progress-section {
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-text {
  font-size: 16px;
  font-weight: bold;
}

.level-text {
  font-size: 14px;
  opacity: 0.8;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s ease;
}

.question-section {
  flex: 1;
  padding: 30px 20px;
  background: white;
  margin: 20px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.question-type {
  text-align: center;
  margin-bottom: 20px;
}

.type-label {
  background: #667eea;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.question-content {
  text-align: center;
  margin-bottom: 30px;
}

.question-word {
  display: block;
  font-size: 36px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.question-phonetic {
  display: block;
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
}

.question-meaning {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}

.question-sentence {
  display: block;
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
  line-height: 1.5;
}

.question-prompt {
  display: block;
  font-size: 16px;
  color: #666;
}

.options-section {
  padding: 0 20px;
  margin-bottom: 30px;
}

.option-item {
  display: flex;
  align-items: center;
  background: white;
  margin-bottom: 15px;
  padding: 20px;
  border-radius: 15px;
  border: 2px solid #f0f0f0;
  transition: all 0.2s;
  position: relative;
}

.option-item.selected {
  border-color: #667eea;
  background: #f8f9ff;
}

.option-item.correct {
  border-color: #4CAF50;
  background: #f1f8e9;
}

.option-item.wrong {
  border-color: #f44336;
  background: #ffebee;
}

.option-label {
  width: 30px;
  height: 30px;
  background: #667eea;
  color: white;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 15px;
}

.option-item.correct .option-label {
  background: #4CAF50;
}

.option-item.wrong .option-label {
  background: #f44336;
}

.option-text {
  flex: 1;
  font-size: 16px;
  color: #333;
}

.result-icon {
  width: 24px;
  height: 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
}

.correct-icon {
  background: #4CAF50;
}

.wrong-icon {
  background: #f44336;
}

.control-section {
  padding: 20px;
}

.submit-btn {
  width: 100%;
  height: 50px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.2s;
}

.submit-btn.disabled {
  background: #ccc;
  opacity: 0.6;
}

.submit-btn:not(.disabled):active {
  transform: scale(0.98);
}

.result-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-info {
  text-align: center;
}

.result-text {
  display: block;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.result-text.correct {
  color: #4CAF50;
}

.result-text.wrong {
  color: #f44336;
}

.correct-answer {
  display: block;
  font-size: 14px;
  color: #666;
}

.next-btn {
  width: 100%;
  height: 50px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
}

.next-btn:active {
  transform: scale(0.98);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 30px;
  margin: 20px;
  max-width: 400px;
  width: 100%;
}

.modal-header {
  text-align: center;
  margin-bottom: 30px;
}

.modal-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.result-summary {
  text-align: center;
  margin-bottom: 30px;
}

.score-display {
  margin-bottom: 20px;
}

.final-score {
  display: block;
  font-size: 48px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.score-label {
  font-size: 16px;
  color: #666;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  flex: 1;
  height: 45px;
  border: none;
  border-radius: 22px;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #667eea;
  color: white;
}

.action-btn.secondary {
  background: #f0f0f0;
  color: #333;
}

.action-btn:active {
  transform: scale(0.98);
}
</style>