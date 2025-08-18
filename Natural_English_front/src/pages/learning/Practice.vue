<template>
  <div class="practice" v-permission="'learning.practice.view'">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>练习测试</h1>
      <p>通过各种练习巩固学习成果</p>
    </div>

    <!-- 练习类型选择 -->
    <div class="practice-types">
      <div class="type-card" 
           v-for="type in practiceTypes" 
           :key="type.id"
           :class="{ active: selectedType === type.id }"
           @click="selectType(type.id)">
        <div class="type-icon">
          <i :class="type.icon"></i>
        </div>
        <h3>{{ type.title }}</h3>
        <p>{{ type.description }}</p>
        <div class="type-stats">
          <span>{{ type.questionCount }} 题</span>
          <span>{{ type.duration }} 分钟</span>
        </div>
      </div>
    </div>

    <!-- 练习界面 -->
    <div class="practice-content" v-if="selectedType && currentQuestion">
      <div class="practice-header">
        <div class="progress-info">
          <span>第 {{ currentQuestionIndex + 1 }} 题 / 共 {{ totalQuestions }} 题</span>
          <div class="progress-bar">
            <div class="progress-fill" 
                 :style="{ width: progressPercentage + '%' }">
            </div>
          </div>
        </div>
        <div class="timer" v-if="timeRemaining > 0">
          <i class="fas fa-clock"></i>
          {{ formatTime(timeRemaining) }}
        </div>
      </div>

      <div class="question-card">
        <div class="question-type-badge">
          {{ questionTypeMap[currentQuestion.type] }}
        </div>
        
        <div class="question-content">
          <h3>{{ currentQuestion.question }}</h3>
          
          <!-- 选择题 -->
          <div v-if="currentQuestion.type === 'choice'" class="choice-options">
            <div v-for="(option, index) in currentQuestion.options" 
                 :key="index"
                 class="option-item"
                 :class="{ 
                   selected: selectedAnswer === index,
                   correct: showResult && index === currentQuestion.correctAnswer,
                   incorrect: showResult && selectedAnswer === index && index !== currentQuestion.correctAnswer
                 }"
                 @click="selectAnswer(index)">
              <span class="option-label">{{ String.fromCharCode(65 + index) }}</span>
              <span class="option-text">{{ option }}</span>
            </div>
          </div>
          
          <!-- 填空题 -->
          <div v-if="currentQuestion.type === 'fill'" class="fill-question">
            <div class="sentence-with-blank">
              <span v-for="(part, index) in currentQuestion.sentenceParts" 
                    :key="index">
                <span v-if="part.type === 'text'">{{ part.content }}</span>
                <input v-if="part.type === 'blank' && part.id !== undefined" 
                       v-model="fillAnswers[part.id]"
                       class="blank-input"
                       :placeholder="'填空' + (part.id + 1)"
                       :class="{ 
                         correct: showResult && fillAnswers[part.id] === part.answer,
                         incorrect: showResult && fillAnswers[part.id] !== part.answer
                       }">
              </span>
            </div>
          </div>
          
          <!-- 翻译题 -->
          <div v-if="currentQuestion.type === 'translate'" class="translate-question">
            <textarea v-model="translateAnswer" 
                      class="translate-input"
                      :placeholder="currentQuestion.placeholder"
                      rows="3">
            </textarea>
          </div>
        </div>

        <!-- 答案解析 -->
        <div v-if="showResult" class="answer-explanation">
          <div class="result-header">
            <i :class="isCorrect ? 'fas fa-check-circle correct' : 'fas fa-times-circle incorrect'"></i>
            <span>{{ isCorrect ? '回答正确！' : '回答错误' }}</span>
          </div>
          <div class="explanation-content">
            <p><strong>正确答案：</strong>{{ getCorrectAnswerText() }}</p>
            <p v-if="currentQuestion.explanation">
              <strong>解析：</strong>{{ currentQuestion.explanation }}
            </p>
          </div>
        </div>

        <div class="question-actions">
          <button v-if="!showResult" 
                  @click="submitAnswer" 
                  class="btn-primary"
                  :disabled="!hasAnswer">
            提交答案
          </button>
          <button v-if="showResult" 
                  @click="nextQuestion" 
                  class="btn-primary">
            {{ currentQuestionIndex < totalQuestions - 1 ? '下一题' : '完成练习' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 练习结果 -->
    <div class="practice-result" v-if="practiceCompleted">
      <div class="result-card">
        <div class="result-header">
          <h2>练习完成！</h2>
          <div class="score-circle">
            <div class="score-text">
              <span class="score-number">{{ score }}</span>
              <span class="score-total">/ {{ totalQuestions }}</span>
            </div>
          </div>
        </div>
        
        <div class="result-stats">
          <div class="stat-item">
            <span class="stat-label">正确率</span>
            <span class="stat-value">{{ Math.round((score / totalQuestions) * 100) }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">用时</span>
            <span class="stat-value">{{ formatTime(totalTime - timeRemaining) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">平均用时</span>
            <span class="stat-value">{{ formatTime(Math.round((totalTime - timeRemaining) / totalQuestions)) }}</span>
          </div>
        </div>
        
        <div class="result-actions">
          <button @click="reviewMistakes" class="btn-secondary">
            <i class="fas fa-eye"></i>
            查看错题
          </button>
          <button @click="restartPractice" class="btn-primary">
            <i class="fas fa-redo"></i>
            重新练习
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface PracticeType {
  id: string
  title: string
  description: string
  icon: string
  questionCount: number
  duration: number
}

interface Question {
  id: number
  type: 'choice' | 'fill' | 'translate'
  question: string
  options?: string[]
  correctAnswer?: number
  sentenceParts?: Array<{
    type: 'text' | 'blank'
    content?: string
    id?: number
    answer?: string
  }>
  placeholder?: string
  correctTranslation?: string
  explanation?: string
}

// 响应式数据
const selectedType = ref<string>('')
const currentQuestion = ref<Question | null>(null)
const currentQuestionIndex = ref(0)
const selectedAnswer = ref<number | null>(null)
const fillAnswers = ref<Record<number, string>>({})
const translateAnswer = ref('')
const showResult = ref(false)
const practiceCompleted = ref(false)
const score = ref(0)
const timeRemaining = ref(0)
const totalTime = ref(0)
const timer = ref<ReturnType<typeof setInterval> | null>(null)

// 练习类型
const practiceTypes: PracticeType[] = [
  {
    id: 'vocabulary',
    title: '词汇练习',
    description: '测试词汇掌握程度',
    icon: 'fas fa-book',
    questionCount: 20,
    duration: 15
  },
  {
    id: 'grammar',
    title: '语法练习',
    description: '巩固语法知识点',
    icon: 'fas fa-language',
    questionCount: 15,
    duration: 20
  },
  {
    id: 'reading',
    title: '阅读理解',
    description: '提升阅读理解能力',
    icon: 'fas fa-glasses',
    questionCount: 10,
    duration: 25
  },
  {
    id: 'translation',
    title: '翻译练习',
    description: '中英文互译练习',
    icon: 'fas fa-exchange-alt',
    questionCount: 12,
    duration: 18
  }
]

// 题型映射
const questionTypeMap = {
  choice: '选择题',
  fill: '填空题',
  translate: '翻译题'
}

// 模拟题目数据
const mockQuestions: Question[] = [
  {
    id: 1,
    type: 'choice',
    question: '下列哪个单词的意思是"美丽的"？',
    options: ['Beautiful', 'Ugly', 'Terrible', 'Awful'],
    correctAnswer: 0,
    explanation: 'Beautiful 意为"美丽的"，是形容词。'
  },
  {
    id: 2,
    type: 'fill',
    question: '请填入合适的单词完成句子：',
    sentenceParts: [
      { type: 'text', content: 'I ' },
      { type: 'blank', id: 0, answer: 'am' },
      { type: 'text', content: ' a student.' }
    ],
    explanation: '这里需要用be动词am，因为主语是I。'
  },
  {
    id: 3,
    type: 'translate',
    question: '请将下列中文翻译成英文：',
    placeholder: '我喜欢学习英语。',
    correctTranslation: 'I like learning English.',
    explanation: '"喜欢做某事"可以用like doing sth表达。'
  }
]

const totalQuestions = computed(() => mockQuestions.length)

const progressPercentage = computed(() => {
  return Math.round(((currentQuestionIndex.value + 1) / totalQuestions.value) * 100)
})

const hasAnswer = computed(() => {
  if (!currentQuestion.value) return false
  
  switch (currentQuestion.value.type) {
    case 'choice':
      return selectedAnswer.value !== null
    case 'fill':
      return Object.values(fillAnswers.value).some(answer => answer.trim() !== '')
    case 'translate':
      return translateAnswer.value.trim() !== ''
    default:
      return false
  }
})

const isCorrect = computed(() => {
  if (!currentQuestion.value) return false
  
  switch (currentQuestion.value.type) {
    case 'choice':
      return selectedAnswer.value === currentQuestion.value.correctAnswer
    case 'fill':
      return currentQuestion.value.sentenceParts?.every(part => {
        if (part.type === 'blank' && part.id !== undefined) {
          return fillAnswers.value[part.id]?.toLowerCase().trim() === part.answer?.toLowerCase()
        }
        return true
      }) || false
    case 'translate':
      // 简单的翻译检查，实际应用中需要更复杂的算法
      return translateAnswer.value.toLowerCase().trim() === currentQuestion.value.correctTranslation?.toLowerCase()
    default:
      return false
  }
})

// 方法
const selectType = (typeId: string) => {
  selectedType.value = typeId
  const type = practiceTypes.find(t => t.id === typeId)
  if (type) {
    totalTime.value = type.duration * 60 // 转换为秒
    timeRemaining.value = totalTime.value
    startPractice()
  }
}

const startPractice = () => {
  currentQuestionIndex.value = 0
  score.value = 0
  practiceCompleted.value = false
  loadQuestion()
  startTimer()
}

const loadQuestion = () => {
  if (currentQuestionIndex.value < mockQuestions.length) {
    currentQuestion.value = mockQuestions[currentQuestionIndex.value]
    resetAnswers()
    showResult.value = false
  } else {
    completePractice()
  }
}

const resetAnswers = () => {
  selectedAnswer.value = null
  fillAnswers.value = {}
  translateAnswer.value = ''
}

const selectAnswer = (index: number) => {
  if (!showResult.value) {
    selectedAnswer.value = index
  }
}

const submitAnswer = () => {
  showResult.value = true
  if (isCorrect.value) {
    score.value++
  }
}

const nextQuestion = () => {
  currentQuestionIndex.value++
  loadQuestion()
}

const getCorrectAnswerText = (): string => {
  if (!currentQuestion.value) return ''
  
  switch (currentQuestion.value.type) {
    case 'choice':
      const correctIndex = currentQuestion.value.correctAnswer
      return correctIndex !== undefined ? currentQuestion.value.options?.[correctIndex] || '' : ''
    case 'fill':
      return currentQuestion.value.sentenceParts
        ?.filter(part => part.type === 'blank')
        .map(part => part.answer)
        .join(', ') || ''
    case 'translate':
      return currentQuestion.value.correctTranslation || ''
    default:
      return ''
  }
}

const startTimer = () => {
  if (timer.value) {
    clearInterval(timer.value)
  }
  
  timer.value = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      completePractice()
    }
  }, 1000)
}

const completePractice = () => {
  practiceCompleted.value = true
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = null
  }
}

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}

const reviewMistakes = () => {
  // 实现查看错题功能
  console.log('Review mistakes')
}

const restartPractice = () => {
  startPractice()
}

// 生命周期
onMounted(() => {
  // 组件挂载时的初始化
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped lang="scss">
.practice {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    color: #2c3e50;
    margin-bottom: 10px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 16px;
  }
}

.practice-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.type-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #e9ecef;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  &.active {
    border-color: #3498db;
    background: #f8f9fa;
  }
  
  .type-icon {
    font-size: 32px;
    color: #3498db;
    margin-bottom: 16px;
  }
  
  h3 {
    color: #2c3e50;
    margin-bottom: 8px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 16px;
  }
  
  .type-stats {
    display: flex;
    justify-content: center;
    gap: 16px;
    font-size: 12px;
    color: #6c757d;
  }
}

.practice-content {
  margin-bottom: 30px;
}

.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.progress-info {
  flex: 1;
  
  span {
    display: block;
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 8px;
  }
}

.progress-bar {
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  max-width: 200px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.timer {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e74c3c;
  font-weight: 600;
  font-size: 16px;
}

.question-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.question-type-badge {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 20px;
}

.question-content {
  margin-bottom: 24px;
  
  h3 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 18px;
    line-height: 1.4;
  }
}

.choice-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #3498db;
    background: #f8f9fa;
  }
  
  &.selected {
    border-color: #3498db;
    background: #e3f2fd;
  }
  
  &.correct {
    border-color: #28a745;
    background: #d4edda;
  }
  
  &.incorrect {
    border-color: #dc3545;
    background: #f8d7da;
  }
}

.option-label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #6c757d;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  margin-right: 16px;
  flex-shrink: 0;
}

.option-item.selected .option-label {
  background: #3498db;
}

.option-item.correct .option-label {
  background: #28a745;
}

.option-item.incorrect .option-label {
  background: #dc3545;
}

.option-text {
  flex: 1;
  font-size: 16px;
}

.fill-question {
  .sentence-with-blank {
    font-size: 18px;
    line-height: 1.6;
    
    .blank-input {
      display: inline-block;
      min-width: 100px;
      padding: 4px 8px;
      border: 2px solid #3498db;
      border-radius: 4px;
      font-size: 16px;
      text-align: center;
      margin: 0 4px;
      
      &.correct {
        border-color: #28a745;
        background: #d4edda;
      }
      
      &.incorrect {
        border-color: #dc3545;
        background: #f8d7da;
      }
    }
  }
}

.translate-question {
  .translate-input {
    width: 100%;
    padding: 16px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 16px;
    resize: vertical;
    
    &:focus {
      outline: none;
      border-color: #3498db;
    }
  }
}

.answer-explanation {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #3498db;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  
  i {
    font-size: 20px;
    
    &.correct {
      color: #28a745;
    }
    
    &.incorrect {
      color: #dc3545;
    }
  }
  
  span {
    font-weight: 600;
    font-size: 16px;
  }
}

.explanation-content {
  p {
    margin-bottom: 8px;
    line-height: 1.5;
  }
}

.question-actions {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: #3498db;
  color: white;
  
  &:hover:not(:disabled) {
    background: #2980b9;
  }
}

.btn-secondary {
  background: #6c757d;
  color: white;
  
  &:hover {
    background: #5a6268;
  }
}

.practice-result {
  display: flex;
  justify-content: center;
}

.result-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.result-card .result-header {
  margin-bottom: 30px;
  
  h2 {
    color: #2c3e50;
    margin-bottom: 20px;
  }
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.score-text {
  color: white;
  text-align: center;
  
  .score-number {
    display: block;
    font-size: 32px;
    font-weight: 700;
  }
  
  .score-total {
    font-size: 16px;
  }
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  
  .stat-label {
    display: block;
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .stat-value {
    display: block;
    color: #2c3e50;
    font-size: 18px;
    font-weight: 600;
  }
}

.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

@media (max-width: 768px) {
  .practice {
    padding: 16px;
  }
  
  .practice-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .question-card {
    padding: 20px;
  }
  
  .result-stats {
    grid-template-columns: 1fr;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>