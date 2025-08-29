<template>
  <view class="challenge-page">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-section">
      <view class="loading-spinner"></view>
      <text class="loading-text">正在准备挑战...</text>
    </view>

    <!-- 游戏开始前 -->
    <view v-else-if="!gameStarted && !gameFinished" class="start-section">
      <view class="challenge-header">
        <text class="challenge-title">单词挑战</text>
        <text class="challenge-subtitle">测试你的单词掌握程度</text>
      </view>
      
      <view class="difficulty-selector">
        <text class="selector-label">选择难度</text>
        <view class="difficulty-options">
          <view 
            v-for="level in ['easy', 'medium', 'hard']" 
            :key="level"
            class="difficulty-option"
            :class="{ active: difficulty === level }"
            @click="changeDifficulty(level)"
          >
            <text class="option-text">{{ level === 'easy' ? '简单' : level === 'medium' ? '中等' : '困难' }}</text>
          </view>
        </view>
      </view>
      
      <view class="challenge-info">
        <view class="info-item">
          <text class="info-label">题目数量</text>
          <text class="info-value">{{ totalQuestions }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">每题时间</text>
          <text class="info-value">30秒</text>
        </view>
        <view class="info-item">
          <text class="info-label">总分</text>
          <text class="info-value">{{ totalQuestions * 10 }}分</text>
        </view>
      </view>
      
      <button class="start-btn" @click="startChallenge">
        <text class="start-btn-text">开始挑战</text>
      </button>
    </view>

    <!-- 游戏进行中 -->
    <view v-else-if="gameStarted && !gameFinished" class="game-section">
      <!-- 游戏头部 -->
      <view class="game-header">
        <view class="progress-section">
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: progress + '%' }"></view>
          </view>
          <text class="progress-text">{{ currentQuestionIndex + 1 }} / {{ totalQuestions }}</text>
        </view>
        
        <view class="game-stats">
          <view class="stat-item">
            <text class="stat-label">得分</text>
            <text class="stat-value">{{ score }}</text>
          </view>
          <view class="stat-item timer-item">
            <text class="stat-label">时间</text>
            <text class="stat-value" :class="{ warning: timeLeft <= 10 }">{{ timeLeft }}s</text>
          </view>
        </view>
      </view>
      
      <!-- 题目区域 -->
      <view v-if="currentQuestion" class="question-section">
        <view class="question-header">
          <text class="question-type">{{ currentQuestion.type === 'translation' ? '翻译题' : currentQuestion.type === 'listening' ? '听力题' : '选择题' }}</text>
          <button v-if="currentQuestion.audio" class="audio-btn" @click="playQuestionAudio">
            <text class="audio-icon">🔊</text>
          </button>
        </view>
        
        <view class="question-content">
          <text class="question-text">{{ currentQuestion.question }}</text>
          <text v-if="currentQuestion.context" class="question-context">{{ currentQuestion.context }}</text>
        </view>
        
        <view class="options-section">
          <view 
            v-for="(option, index) in currentQuestion.options" 
            :key="index"
            class="option-item"
            :class="{
              selected: selectedAnswer === index,
              correct: showResult && index === currentQuestion.correctAnswer,
              wrong: showResult && selectedAnswer === index && index !== currentQuestion.correctAnswer
            }"
            @click="selectAnswer(index)"
          >
            <text class="option-label">{{ String.fromCharCode(65 + index) }}</text>
            <text class="option-text">{{ option }}</text>
            <view v-if="showResult && index === currentQuestion.correctAnswer" class="result-icon correct-icon">✓</view>
            <view v-else-if="showResult && selectedAnswer === index && index !== currentQuestion.correctAnswer" class="result-icon wrong-icon">✗</view>
          </view>
        </view>
        
        <view v-if="showResult" class="result-section">
          <text v-if="selectedAnswer === currentQuestion.correctAnswer" class="result-text correct">回答正确！</text>
          <text v-else-if="selectedAnswer === -1" class="result-text timeout">时间到！</text>
          <text v-else class="result-text wrong">回答错误</text>
          <text v-if="currentQuestion.explanation" class="explanation-text">{{ currentQuestion.explanation }}</text>
        </view>
      </view>
    </view>

    <!-- 游戏结束 -->
    <view v-else-if="gameFinished" class="result-section">
      <view class="result-header">
        <text class="result-title">挑战完成！</text>
        <view class="final-score">
          <text class="score-text">{{ score }}</text>
          <text class="score-label">/ {{ totalQuestions * 10 }}</text>
        </view>
      </view>
      
      <view class="result-stats">
        <view class="stat-card">
          <text class="stat-number">{{ accuracy }}%</text>
          <text class="stat-name">正确率</text>
        </view>
        <view class="stat-card">
          <text class="stat-number">{{ userAnswers.filter(a => a.correct).length }}</text>
          <text class="stat-name">答对题数</text>
        </view>
        <view class="stat-card">
          <text class="stat-number">{{ Math.round(userAnswers.reduce((sum, a) => sum + a.timeUsed, 0) / userAnswers.length) }}s</text>
          <text class="stat-name">平均用时</text>
        </view>
      </view>
      
      <view class="result-actions">
        <button class="action-btn secondary" @click="restartChallenge">
          <text class="action-btn-text">重新挑战</text>
        </button>
        <button class="action-btn primary" @click="$uni.navigateBack()">
          <text class="action-btn-text">返回首页</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script>
import { mockData, getRandomChallengeQuestions, simulateApiDelay } from '@/utils/mockData'
import { playAudio, playBeep, playSuccessSound } from '@/config/audioConfig'

export default {
  name: 'Challenge',
  data() {
    return {
      loading: true,
      currentQuestion: null,
      currentQuestionIndex: 0,
      totalQuestions: 10,
      score: 0,
      timeLeft: 30,
      timer: null,
      gameStarted: false,
      gameFinished: false,
      selectedAnswer: null,
      showResult: false,
      questions: [],
      userAnswers: [],
      challengeType: 'mixed', // mixed, listening, reading, translation
      difficulty: 'medium' // easy, medium, hard
    }
  },
  computed: {
    progress() {
      return this.totalQuestions > 0 ? (this.currentQuestionIndex / this.totalQuestions) * 100 : 0
    },
    accuracy() {
      const correctAnswers = this.userAnswers.filter(answer => answer.correct).length
      return this.userAnswers.length > 0 ? Math.round((correctAnswers / this.userAnswers.length) * 100) : 0
    }
  },
  async mounted() {
    await this.initializeChallenge()
  },
  beforeDestroy() {
    this.clearTimer()
  },
  methods: {
    async initializeChallenge() {
      this.loading = true
      await simulateApiDelay()
      this.questions = getRandomChallengeQuestions(this.totalQuestions, this.difficulty)
      this.loading = false
    },
    
    startChallenge() {
      this.gameStarted = true
      this.loadCurrentQuestion()
      this.startTimer()
      playSuccessSound()
    },
    
    loadCurrentQuestion() {
      if (this.currentQuestionIndex < this.questions.length) {
        this.currentQuestion = this.questions[this.currentQuestionIndex]
        this.selectedAnswer = null
        this.showResult = false
        this.timeLeft = 30
      } else {
        this.finishChallenge()
      }
    },
    
    selectAnswer(optionIndex) {
      if (this.selectedAnswer !== null || this.showResult) return
      
      this.selectedAnswer = optionIndex
      this.showResult = true
      this.clearTimer()
      
      const isCorrect = optionIndex === this.currentQuestion.correctAnswer
      
      this.userAnswers.push({
        questionIndex: this.currentQuestionIndex,
        selectedAnswer: optionIndex,
        correctAnswer: this.currentQuestion.correctAnswer,
        correct: isCorrect,
        timeUsed: 30 - this.timeLeft
      })
      
      if (isCorrect) {
        this.score += 10
        playSuccessSound()
      } else {
        playBeep()
      }
      
      setTimeout(() => {
        this.nextQuestion()
      }, 2000)
    },
    
    nextQuestion() {
      this.currentQuestionIndex++
      this.loadCurrentQuestion()
      if (!this.gameFinished) {
        this.startTimer()
      }
    },
    
    startTimer() {
      this.clearTimer()
      this.timer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this.timeUp()
        }
      }, 1000)
    },
    
    clearTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    },
    
    timeUp() {
      if (this.selectedAnswer === null) {
        this.selectedAnswer = -1 // 表示超时
        this.showResult = true
        
        this.userAnswers.push({
          questionIndex: this.currentQuestionIndex,
          selectedAnswer: -1,
          correctAnswer: this.currentQuestion.correctAnswer,
          correct: false,
          timeUsed: 30
        })
        
        playBeep()
        
        setTimeout(() => {
          this.nextQuestion()
        }, 2000)
      }
    },
    
    finishChallenge() {
      this.gameFinished = true
      this.clearTimer()
      playSuccessSound()
    },
    
    restartChallenge() {
      this.gameStarted = false
      this.gameFinished = false
      this.currentQuestionIndex = 0
      this.score = 0
      this.timeLeft = 30
      this.selectedAnswer = null
      this.showResult = false
      this.userAnswers = []
      this.clearTimer()
      this.initializeChallenge()
    },
    
    playQuestionAudio() {
      if (this.currentQuestion && this.currentQuestion.audio) {
        playAudio(this.currentQuestion.audio)
      }
    },
    
    changeDifficulty(newDifficulty) {
      this.difficulty = newDifficulty
      this.restartChallenge()
    }
  }
}
</script>

<style scoped>
.challenge-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 100px;
}

/* 加载状态样式 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 500;
}

/* 开始页面样式 */
.start-section {
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.challenge-header {
  text-align: center;
  margin-bottom: 40px;
}

.challenge-title {
  font-size: 32px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 8px;
  display: block;
}

.challenge-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.difficulty-selector {
  width: 100%;
  margin-bottom: 40px;
}

.selector-label {
  font-size: 18px;
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 16px;
  display: block;
  text-align: center;
}

.difficulty-options {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.difficulty-option {
  flex: 1;
  max-width: 100px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.difficulty-option.active {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.difficulty-option.active .option-text {
  color: #667eea;
  font-weight: 600;
}

.option-text {
  font-size: 14px;
  color: #ffffff;
  font-weight: 500;
}

.challenge-info {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
}

.info-value {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
}

.start-btn {
  width: 200px;
  height: 50px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 25px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.start-btn:active {
  transform: translateY(2px);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);
}

.start-btn-text {
  font-size: 18px;
  color: #ffffff;
  font-weight: 600;
}

/* 游戏进行中样式 */
.game-section {
  padding: 20px;
}

.game-header {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
}

.progress-section {
  margin-bottom: 16px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  display: block;
}

.game-stats {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
  display: block;
}

.stat-value {
  font-size: 20px;
  color: #ffffff;
  font-weight: bold;
  display: block;
}

.stat-value.warning {
  color: #fbbf24;
  animation: pulse 1s ease-in-out infinite;
}

/* 题目区域样式 */
.question-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question-type {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
  background: rgba(102, 126, 234, 0.1);
  padding: 6px 12px;
  border-radius: 12px;
}

.audio-btn {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.audio-icon {
  font-size: 18px;
}

.question-content {
  margin-bottom: 24px;
}

.question-text {
  font-size: 20px;
  color: #1e293b;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 8px;
  display: block;
}

.question-context {
  font-size: 14px;
  color: #64748b;
  font-style: italic;
  display: block;
}

.options-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
}

.option-item:active {
  transform: scale(0.98);
}

.option-item.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.option-item.correct {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.option-item.wrong {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.option-label {
  width: 32px;
  height: 32px;
  background: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin-right: 12px;
  flex-shrink: 0;
}

.option-item.selected .option-label {
  background: #667eea;
  color: #ffffff;
}

.option-item.correct .option-label {
  background: #10b981;
  color: #ffffff;
}

.option-item.wrong .option-label {
  background: #ef4444;
  color: #ffffff;
}

.option-text {
  flex: 1;
  font-size: 16px;
  color: #334155;
  line-height: 1.4;
}

.result-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  margin-left: 8px;
}

.correct-icon {
  background: #10b981;
  color: #ffffff;
}

.wrong-icon {
  background: #ef4444;
  color: #ffffff;
}

.result-section {
  text-align: center;
  padding: 16px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  margin-top: 16px;
}

.result-text {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
}

.result-text.correct {
  color: #10b981;
}

.result-text.wrong {
  color: #ef4444;
}

.result-text.timeout {
  color: #f59e0b;
}

.explanation-text {
  font-size: 14px;
  color: #64748b;
  line-height: 1.4;
  display: block;
}

/* 结果页面样式 */
.result-section {
  padding: 40px 20px;
  text-align: center;
}

.result-header {
  margin-bottom: 40px;
}

.result-title {
  font-size: 28px;
  color: #ffffff;
  font-weight: bold;
  margin-bottom: 16px;
  display: block;
}

.final-score {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.score-text {
  font-size: 48px;
  color: #10b981;
  font-weight: bold;
}

.score-label {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.8);
}

.result-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 40px;
}

.stat-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.stat-number {
  font-size: 24px;
  color: #ffffff;
  font-weight: bold;
  margin-bottom: 8px;
  display: block;
}

.stat-name {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.action-btn {
  flex: 1;
  max-width: 140px;
  height: 48px;
  border-radius: 24px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-btn.primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.action-btn:active {
  transform: translateY(2px);
}

.action-btn-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
}
</style>