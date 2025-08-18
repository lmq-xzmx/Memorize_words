<template>
  <div class="listening-practice">
    <div class="practice-header">
      <h1>听力练习</h1>
      <div class="practice-stats">
        <div class="stat-item">
          <span class="stat-label">今日练习</span>
          <span class="stat-value">{{ todayPracticed }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">正确率</span>
          <span class="stat-value">{{ accuracyRate }}%</span>
        </div>
      </div>
    </div>

    <div class="practice-content">
      <!-- 难度选择 -->
      <div class="difficulty-selector" v-if="!currentExercise">
        <h2>选择练习难度</h2>
        <div class="difficulty-grid">
          <div 
            v-for="level in difficultyLevels" 
            :key="level.id"
            class="difficulty-card"
            @click="selectDifficulty(level)"
            v-permission="'learning.listening.access'"
          >
            <div class="difficulty-icon">
              <i :class="level.icon"></i>
            </div>
            <h3>{{ level.name }}</h3>
            <p>{{ level.description }}</p>
            <div class="difficulty-features">
              <span v-for="feature in level.features" :key="feature" class="feature-tag">
                {{ feature }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 听力练习界面 -->
      <div class="listening-interface" v-if="currentExercise">
        <div class="exercise-header">
          <button class="back-btn" @click="backToSelection">
            <i class="el-icon-arrow-left"></i>
            返回选择
          </button>
          <div class="exercise-info">
            <h3>{{ currentExercise.title }}</h3>
            <span class="exercise-type">{{ currentExercise.type }}</span>
          </div>
        </div>

        <div class="audio-player">
          <div class="audio-controls">
            <button 
              class="play-btn"
              @click="togglePlay"
              :class="{ playing: isPlaying }"
            >
              <i :class="isPlaying ? 'el-icon-video-pause' : 'el-icon-video-play'"></i>
            </button>
            
            <div class="audio-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: audioProgress + '%' }"
                ></div>
              </div>
              <span class="time-display">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
            </div>
            
            <div class="audio-controls-right">
              <button class="speed-btn" @click="changeSpeed">
                {{ playbackSpeed }}x
              </button>
              <button class="replay-btn" @click="replayAudio">
                <i class="el-icon-refresh"></i>
              </button>
            </div>
          </div>
          
          <div class="play-count" v-if="playCount > 0">
            已播放 {{ playCount }} 次
          </div>
        </div>

        <div class="exercise-content">
          <!-- 选择题 -->
          <div class="multiple-choice" v-if="currentExercise.type === 'multiple'">
            <h4>{{ currentExercise.question }}</h4>
            <div class="options-grid">
              <button 
                v-for="option in currentExercise.options" 
                :key="option.id"
                class="option-btn"
                :class="{ 
                  'selected': selectedAnswer === option.id,
                  'correct': showAnswer && option.correct,
                  'incorrect': showAnswer && selectedAnswer === option.id && !option.correct
                }"
                @click="selectAnswer(option.id)"
                :disabled="showAnswer"
              >
                {{ option.text }}
              </button>
            </div>
          </div>

          <!-- 填空题 -->
          <div class="fill-blanks" v-if="currentExercise.type === 'fill'">
            <h4>听音填空</h4>
            <div class="transcript">
              <span 
                v-for="(word, index) in transcriptWords" 
                :key="index"
                class="transcript-word"
              >
                <input 
                  v-if="word.isBlank"
                  v-model="word.userInput"
                  type="text"
                  class="blank-input"
                  :class="{ 
                    'correct': showAnswer && word.userInput?.toLowerCase() === word.correct?.toLowerCase(),
                    'incorrect': showAnswer && word.userInput?.toLowerCase() !== word.correct?.toLowerCase()
                  }"
                  :disabled="showAnswer"
                  :placeholder="showAnswer ? word.correct : ''"
                />
                <span v-else>{{ word.text }}</span>
              </span>
            </div>
          </div>

          <!-- 听写题 -->
          <div class="dictation" v-if="currentExercise.type === 'dictation'">
            <h4>听音写句</h4>
            <textarea 
              v-model="dictationText"
              class="dictation-input"
              placeholder="请输入你听到的内容..."
              :disabled="showAnswer"
              rows="4"
            ></textarea>
            <div class="dictation-hint" v-if="currentExercise.hint">
              <i class="el-icon-info"></i>
              {{ currentExercise.hint }}
            </div>
          </div>
        </div>

        <div class="exercise-actions">
          <button 
            v-if="!showAnswer"
            class="check-btn"
            @click="checkAnswer"
            :disabled="!canCheck"
          >
            检查答案
          </button>
          
          <div v-if="showAnswer" class="answer-feedback">
            <div class="feedback-header">
              <div class="feedback-icon">
                <i :class="isCorrect ? 'el-icon-check' : 'el-icon-close'"></i>
              </div>
              <span class="feedback-text">
                {{ isCorrect ? '回答正确！' : '回答错误' }}
              </span>
              <div class="score">得分: {{ currentScore }}/{{ maxScore }}</div>
            </div>
            
            <div class="correct-answer" v-if="!isCorrect && currentExercise.correctText">
              <h5>正确答案：</h5>
              <p>{{ currentExercise.correctText }}</p>
            </div>
            
            <div class="explanation" v-if="currentExercise.explanation">
              <h5>解析：</h5>
              <p>{{ currentExercise.explanation }}</p>
            </div>
            
            <div class="action-buttons">
              <button class="replay-exercise-btn" @click="replayExercise">
                <i class="el-icon-refresh"></i>
                重新练习
              </button>
              <button class="next-exercise-btn" @click="nextExercise">
                下一题
                <i class="el-icon-arrow-right"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { permissionChecker } from '@/utils/permissions'

interface DifficultyLevel {
  id: string
  name: string
  description: string
  icon: string
  features: string[]
}

interface ListeningExercise {
  id: string
  title: string
  type: 'multiple' | 'fill' | 'dictation'
  audioUrl: string
  question?: string
  options?: Array<{
    id: string
    text: string
    correct: boolean
  }>
  transcript?: string
  blanks?: number[]
  correctText?: string
  explanation?: string
  hint?: string
}

interface TranscriptWord {
  text: string
  isBlank: boolean
  correct?: string
  userInput?: string
}

// 练习状态
const currentExercise = ref<ListeningExercise | null>(null)
const selectedDifficulty = ref<DifficultyLevel | null>(null)
const selectedAnswer = ref('')
const dictationText = ref('')
const transcriptWords = ref<TranscriptWord[]>([])
const showAnswer = ref(false)
const isCorrect = ref(false)
const currentScore = ref(0)
const maxScore = ref(100)

// 音频状态
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const audioProgress = ref(0)
const playbackSpeed = ref(1)
const playCount = ref(0)
const audioElement = ref<HTMLAudioElement | null>(null)

// 统计数据
const todayPracticed = ref(0)
const accuracyRate = ref(0)

// 难度级别
const difficultyLevels = ref<DifficultyLevel[]>([
  {
    id: 'beginner',
    name: '初级',
    description: '适合英语初学者',
    icon: 'el-icon-star-off',
    features: ['慢速语音', '简单词汇', '短句练习']
  },
  {
    id: 'intermediate',
    name: '中级',
    description: '适合有一定基础的学习者',
    icon: 'el-icon-star-on',
    features: ['正常语速', '日常对话', '段落理解']
  },
  {
    id: 'advanced',
    name: '高级',
    description: '适合英语水平较高的学习者',
    icon: 'el-icon-medal',
    features: ['快速语音', '复杂内容', '长篇听力']
  }
])

// 计算属性
const canCheck = computed(() => {
  if (!currentExercise.value) return false
  
  switch (currentExercise.value.type) {
    case 'multiple':
      return selectedAnswer.value !== ''
    case 'fill':
      return transcriptWords.value.some(word => word.isBlank && word.userInput?.trim())
    case 'dictation':
      return dictationText.value.trim() !== ''
    default:
      return false
  }
})

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 选择难度
const selectDifficulty = async (level: DifficultyLevel) => {
  selectedDifficulty.value = level
  await loadExercise(level.id)
}

// 加载练习
const loadExercise = async (difficulty: string) => {
  // 模拟加载练习数据
  const mockExercise: ListeningExercise = {
    id: '1',
    title: '日常对话练习',
    type: 'multiple',
    audioUrl: '/audio/sample.mp3',
    question: '对话中提到的时间是什么？',
    options: [
      { id: 'a', text: '上午9点', correct: false },
      { id: 'b', text: '下午2点', correct: true },
      { id: 'c', text: '晚上7点', correct: false },
      { id: 'd', text: '中午12点', correct: false }
    ],
    explanation: '对话中明确提到了下午2点的约会时间。'
  }
  
  currentExercise.value = mockExercise
  resetExercise()
  initAudio()
}

// 返回选择界面
const backToSelection = () => {
  currentExercise.value = null
  selectedDifficulty.value = null
  resetExercise()
  cleanupAudio()
}

// 初始化音频
const initAudio = () => {
  if (!currentExercise.value) return
  
  // 模拟音频初始化
  duration.value = 120 // 2分钟
  currentTime.value = 0
  audioProgress.value = 0
  playCount.value = 0
}

// 清理音频
const cleanupAudio = () => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
  isPlaying.value = false
}

// 播放/暂停音频
const togglePlay = () => {
  isPlaying.value = !isPlaying.value
  
  if (isPlaying.value) {
    playCount.value++
    // 模拟播放
    startAudioProgress()
  } else {
    // 暂停
    stopAudioProgress()
  }
}

let progressInterval: ReturnType<typeof setInterval> | null = null

// 开始音频进度
const startAudioProgress = () => {
  if (progressInterval) clearInterval(progressInterval)
  
  progressInterval = setInterval(() => {
    if (currentTime.value < duration.value) {
      currentTime.value += 1
      audioProgress.value = (currentTime.value / duration.value) * 100
    } else {
      stopAudioProgress()
      isPlaying.value = false
    }
  }, 1000)
}

// 停止音频进度
const stopAudioProgress = () => {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

// 重播音频
const replayAudio = () => {
  currentTime.value = 0
  audioProgress.value = 0
  if (isPlaying.value) {
    stopAudioProgress()
    startAudioProgress()
  }
}

// 改变播放速度
const changeSpeed = () => {
  const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2]
  const currentIndex = speeds.indexOf(playbackSpeed.value)
  playbackSpeed.value = speeds[(currentIndex + 1) % speeds.length]
}

// 格式化时间
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 选择答案
const selectAnswer = (answerId: string) => {
  if (!showAnswer.value) {
    selectedAnswer.value = answerId
  }
}

// 检查答案
const checkAnswer = () => {
  if (!currentExercise.value) return
  
  showAnswer.value = true
  
  switch (currentExercise.value.type) {
    case 'multiple':
      checkMultipleChoice()
      break
    case 'fill':
      checkFillBlanks()
      break
    case 'dictation':
      checkDictation()
      break
  }
  
  if (isCorrect.value) {
    ElMessage.success('回答正确！')
  } else {
    ElMessage.error('回答错误，请查看正确答案')
  }
}

// 检查选择题
const checkMultipleChoice = () => {
  if (!currentExercise.value?.options) return
  
  const selectedOption = currentExercise.value.options.find(opt => opt.id === selectedAnswer.value)
  isCorrect.value = selectedOption?.correct || false
  currentScore.value = isCorrect.value ? 100 : 0
}

// 检查填空题
const checkFillBlanks = () => {
  let correctCount = 0
  let totalBlanks = 0
  
  transcriptWords.value.forEach(word => {
    if (word.isBlank) {
      totalBlanks++
      if (word.userInput?.toLowerCase() === word.correct?.toLowerCase()) {
        correctCount++
      }
    }
  })
  
  isCorrect.value = correctCount === totalBlanks
  currentScore.value = totalBlanks > 0 ? Math.round((correctCount / totalBlanks) * 100) : 0
}

// 检查听写题
const checkDictation = () => {
  if (!currentExercise.value?.correctText) return
  
  const userText = dictationText.value.trim().toLowerCase()
  const correctText = currentExercise.value.correctText.toLowerCase()
  
  // 简单的相似度计算
  const similarity = calculateSimilarity(userText, correctText)
  isCorrect.value = similarity >= 0.8
  currentScore.value = Math.round(similarity * 100)
}

// 计算文本相似度
const calculateSimilarity = (text1: string, text2: string): number => {
  const words1 = text1.split(/\s+/)
  const words2 = text2.split(/\s+/)
  const maxLength = Math.max(words1.length, words2.length)
  
  if (maxLength === 0) return 1
  
  let matches = 0
  words1.forEach(word => {
    if (words2.includes(word)) {
      matches++
    }
  })
  
  return matches / maxLength
}

// 重新练习
const replayExercise = () => {
  resetExercise()
  replayAudio()
}

// 下一题
const nextExercise = () => {
  // 加载下一题
  ElMessage.info('加载下一题...')
  resetExercise()
}

// 重置练习状态
const resetExercise = () => {
  selectedAnswer.value = ''
  dictationText.value = ''
  transcriptWords.value = []
  showAnswer.value = false
  isCorrect.value = false
  currentScore.value = 0
}

// 加载统计数据
const loadStats = () => {
  todayPracticed.value = 8
  accuracyRate.value = 85
}

onMounted(() => {
  loadStats()
})

onUnmounted(() => {
  cleanupAudio()
  stopAudioProgress()
})
</script>

<style scoped>
.listening-practice {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.practice-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.practice-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.stat-value {
  display: block;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.difficulty-selector h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #1f2937;
}

.difficulty-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.difficulty-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.difficulty-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.difficulty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.difficulty-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
}

.difficulty-card p {
  margin: 0 0 1rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.difficulty-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.feature-tag {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.listening-interface {
  max-width: 800px;
  margin: 0 auto;
}

.exercise-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.back-btn {
  background: #f3f4f6;
  border: none;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #374151;
  transition: background 0.2s ease;
}

.back-btn:hover {
  background: #e5e7eb;
}

.exercise-info h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
}

.exercise-type {
  background: #eff6ff;
  color: #1d4ed8;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.audio-player {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.audio-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.play-btn {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: transform 0.2s ease;
}

.play-btn:hover {
  transform: scale(1.05);
}

.play-btn.playing {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.audio-progress {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  cursor: pointer;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.1s ease;
}

.time-display {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 80px;
}

.audio-controls-right {
  display: flex;
  gap: 0.5rem;
}

.speed-btn,
.replay-btn {
  background: #f3f4f6;
  border: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  color: #374151;
  font-size: 0.875rem;
  transition: background 0.2s ease;
}

.speed-btn:hover,
.replay-btn:hover {
  background: #e5e7eb;
}

.play-count {
  margin-top: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
  text-align: center;
}

.exercise-content {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.multiple-choice h4,
.fill-blanks h4,
.dictation h4 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.125rem;
}

.options-grid {
  display: grid;
  gap: 0.75rem;
}

.option-btn {
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-btn:hover {
  border-color: #667eea;
}

.option-btn.selected {
  border-color: #667eea;
  background: #eff6ff;
}

.option-btn.correct {
  border-color: #10b981;
  background: #ecfdf5;
  color: #065f46;
}

.option-btn.incorrect {
  border-color: #ef4444;
  background: #fef2f2;
  color: #991b1b;
}

.transcript {
  line-height: 1.8;
  font-size: 1.125rem;
}

.transcript-word {
  margin-right: 0.25rem;
}

.blank-input {
  border: none;
  border-bottom: 2px solid #667eea;
  background: transparent;
  padding: 0.25rem;
  font-size: inherit;
  min-width: 80px;
  text-align: center;
}

.blank-input:focus {
  outline: none;
  border-bottom-color: #5a6fd8;
}

.blank-input.correct {
  border-bottom-color: #10b981;
  background: #ecfdf5;
}

.blank-input.incorrect {
  border-bottom-color: #ef4444;
  background: #fef2f2;
}

.dictation-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.dictation-input:focus {
  outline: none;
  border-color: #667eea;
}

.dictation-hint {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.375rem;
  color: #1e40af;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.check-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s ease;
}

.check-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.check-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.answer-feedback {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.feedback-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.feedback-icon .el-icon-check {
  color: #10b981;
  background: #ecfdf5;
}

.feedback-icon .el-icon-close {
  color: #ef4444;
  background: #fef2f2;
}

.feedback-text {
  font-weight: 500;
  color: #1f2937;
}

.score {
  margin-left: auto;
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.correct-answer,
.explanation {
  margin-bottom: 1rem;
}

.correct-answer h5,
.explanation h5 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 0.875rem;
  font-weight: 600;
}

.correct-answer p,
.explanation p {
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.replay-exercise-btn,
.next-exercise-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s ease;
}

.replay-exercise-btn:hover,
.next-exercise-btn:hover {
  background: #5a6fd8;
}

.next-exercise-btn {
  background: #10b981;
}

.next-exercise-btn:hover {
  background: #059669;
}

@media (max-width: 768px) {
  .listening-practice {
    padding: 1rem;
  }
  
  .practice-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .difficulty-grid {
    grid-template-columns: 1fr;
  }
  
  .exercise-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .audio-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .audio-progress {
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>