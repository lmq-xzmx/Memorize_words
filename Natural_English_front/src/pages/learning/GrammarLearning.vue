<template>
  <div class="grammar-learning">
    <div class="learning-header">
      <h1>语法学习</h1>
      <div class="learning-stats">
        <div class="stat-item">
          <span class="stat-label">今日学习</span>
          <span class="stat-value">{{ todayLearned }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总掌握</span>
          <span class="stat-value">{{ totalMastered }}</span>
        </div>
      </div>
    </div>

    <div class="learning-content">
      <!-- 语法主题列表 -->
      <div class="topic-list" v-if="!selectedTopic">
        <h2>选择语法主题</h2>
        <div class="topic-grid">
          <div 
            v-for="topic in grammarTopics" 
            :key="topic.id"
            class="topic-card"
            @click="selectTopic(topic)"
            v-permission="'learning.grammar.access'"
          >
            <div class="topic-icon">
              <i :class="topic.icon"></i>
            </div>
            <h3>{{ topic.title }}</h3>
            <p>{{ topic.description }}</p>
            <div class="topic-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: topic.progress + '%' }"
                ></div>
              </div>
              <span class="progress-text">{{ topic.progress }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 语法学习界面 -->
      <div class="grammar-interface" v-if="selectedTopic">
        <div class="topic-header">
          <button class="back-btn" @click="backToTopics">
            <i class="el-icon-arrow-left"></i>
            返回主题
          </button>
          <h2>{{ selectedTopic.title }}</h2>
        </div>

        <div class="lesson-content">
          <!-- 语法规则 -->
          <div class="grammar-rules" v-if="currentLesson">
            <h3>{{ currentLesson.title }}</h3>
            <div class="rule-explanation">
              <div v-html="currentLesson.explanation"></div>
            </div>
            
            <!-- 例句 -->
            <div class="examples" v-if="currentLesson.examples">
              <h4>例句</h4>
              <div 
                v-for="example in currentLesson.examples" 
                :key="example.id"
                class="example-item"
              >
                <p class="example-sentence">{{ example.sentence }}</p>
                <p class="example-translation">{{ example.translation }}</p>
                <p class="example-note" v-if="example.note">{{ example.note }}</p>
              </div>
            </div>
          </div>

          <!-- 练习题 -->
          <div class="exercises" v-if="showExercises">
            <h3>练习题</h3>
            <div class="exercise-item" v-if="currentExercise">
              <div class="exercise-question">
                <p>{{ currentExercise.question }}</p>
                <div class="exercise-options" v-if="currentExercise.type === 'multiple'">
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
                
                <div class="exercise-input" v-if="currentExercise.type === 'fill'">
                  <input 
                    v-model="userAnswer"
                    type="text"
                    placeholder="请输入答案"
                    :disabled="showAnswer"
                    @keyup.enter="checkAnswer"
                  />
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
                  <div class="feedback-content">
                    <i :class="isCorrect ? 'el-icon-check' : 'el-icon-close'"></i>
                    <span>{{ isCorrect ? '正确！' : '错误' }}</span>
                  </div>
                  <p class="correct-answer" v-if="!isCorrect">
                    正确答案：{{ currentExercise.correctAnswer }}
                  </p>
                  <p class="explanation" v-if="currentExercise.explanation">
                    {{ currentExercise.explanation }}
                  </p>
                  <button class="next-btn" @click="nextExercise">
                    下一题
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="lesson-navigation">
          <button 
            class="nav-btn"
            @click="toggleExercises"
            :class="{ active: showExercises }"
          >
            {{ showExercises ? '查看规则' : '开始练习' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { permissionChecker } from '@/utils/permissions'

interface GrammarTopic {
  id: string
  title: string
  description: string
  icon: string
  progress: number
  lessons: GrammarLesson[]
}

interface GrammarLesson {
  id: string
  title: string
  explanation: string
  examples: Array<{
    id: string
    sentence: string
    translation: string
    note?: string
  }>
  exercises: Exercise[]
}

interface Exercise {
  id: string
  type: 'multiple' | 'fill'
  question: string
  options?: Array<{
    id: string
    text: string
    correct: boolean
  }>
  correctAnswer: string
  explanation?: string
}

// 学习状态
const selectedTopic = ref<GrammarTopic | null>(null)
const currentLesson = ref<GrammarLesson | null>(null)
const showExercises = ref(false)
const currentExerciseIndex = ref(0)
const selectedAnswer = ref('')
const userAnswer = ref('')
const showAnswer = ref(false)
const isCorrect = ref(false)

// 统计数据
const todayLearned = ref(0)
const totalMastered = ref(0)

// 语法主题数据
const grammarTopics = ref<GrammarTopic[]>([
  {
    id: '1',
    title: '时态',
    description: '学习英语的各种时态用法',
    icon: 'el-icon-time',
    progress: 75,
    lessons: [
      {
        id: '1',
        title: '一般现在时',
        explanation: '<p>一般现在时表示经常性、习惯性的动作或状态。</p><p><strong>构成：</strong>主语 + 动词原形/第三人称单数</p>',
        examples: [
          {
            id: '1',
            sentence: 'I go to school every day.',
            translation: '我每天去上学。',
            note: '表示习惯性动作'
          }
        ],
        exercises: [
          {
            id: '1',
            type: 'multiple',
            question: 'She _____ to work by bus every morning.',
            options: [
              { id: 'a', text: 'go', correct: false },
              { id: 'b', text: 'goes', correct: true },
              { id: 'c', text: 'going', correct: false },
              { id: 'd', text: 'went', correct: false }
            ],
            correctAnswer: 'goes',
            explanation: '第三人称单数主语后面的动词要加s或es'
          }
        ]
      }
    ]
  },
  {
    id: '2',
    title: '语态',
    description: '掌握主动语态和被动语态',
    icon: 'el-icon-switch-button',
    progress: 45,
    lessons: []
  },
  {
    id: '3',
    title: '从句',
    description: '学习各种从句的用法',
    icon: 'el-icon-connection',
    progress: 30,
    lessons: []
  }
])

// 计算属性
const currentExercise = computed(() => {
  if (!currentLesson.value || !currentLesson.value.exercises) return null
  return currentLesson.value.exercises[currentExerciseIndex.value]
})

const canCheck = computed(() => {
  if (!currentExercise.value) return false
  if (currentExercise.value.type === 'multiple') {
    return selectedAnswer.value !== ''
  }
  return userAnswer.value.trim() !== ''
})

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 选择主题
const selectTopic = (topic: GrammarTopic) => {
  selectedTopic.value = topic
  if (topic.lessons.length > 0) {
    currentLesson.value = topic.lessons[0]
  }
  showExercises.value = false
  resetExercise()
}

// 返回主题列表
const backToTopics = () => {
  selectedTopic.value = null
  currentLesson.value = null
  showExercises.value = false
  resetExercise()
}

// 切换练习模式
const toggleExercises = () => {
  showExercises.value = !showExercises.value
  if (showExercises.value) {
    resetExercise()
  }
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
  
  if (currentExercise.value.type === 'multiple') {
    const selectedOption = currentExercise.value.options?.find(opt => opt.id === selectedAnswer.value)
    isCorrect.value = selectedOption?.correct || false
  } else {
    isCorrect.value = userAnswer.value.trim().toLowerCase() === currentExercise.value.correctAnswer.toLowerCase()
  }
  
  if (isCorrect.value) {
    ElMessage.success('答对了！')
  } else {
    ElMessage.error('答错了，再试试吧')
  }
}

// 下一题
const nextExercise = () => {
  if (!currentLesson.value) return
  
  if (currentExerciseIndex.value < currentLesson.value.exercises.length - 1) {
    currentExerciseIndex.value++
    resetExercise()
  } else {
    ElMessage.success('练习完成！')
    showExercises.value = false
    currentExerciseIndex.value = 0
    resetExercise()
  }
}

// 重置练习状态
const resetExercise = () => {
  selectedAnswer.value = ''
  userAnswer.value = ''
  showAnswer.value = false
  isCorrect.value = false
}

// 加载统计数据
const loadStats = () => {
  // 模拟数据
  todayLearned.value = 5
  totalMastered.value = 23
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.grammar-learning {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.learning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.learning-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.learning-stats {
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

.topic-list h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #1f2937;
}

.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.topic-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.topic-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.topic-icon {
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

.topic-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
}

.topic-card p {
  margin: 0 0 1rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.topic-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 500;
}

.grammar-interface {
  max-width: 800px;
  margin: 0 auto;
}

.topic-header {
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

.topic-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
}

.lesson-content {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.grammar-rules h3 {
  color: #1f2937;
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
}

.rule-explanation {
  margin-bottom: 2rem;
  line-height: 1.6;
}

.examples h4 {
  color: #1f2937;
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
}

.example-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.example-sentence {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-weight: 500;
}

.example-translation {
  margin: 0 0 0.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.example-note {
  margin: 0;
  color: #059669;
  font-size: 0.75rem;
  font-style: italic;
}

.exercises h3 {
  color: #1f2937;
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
}

.exercise-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.exercise-question p {
  margin: 0 0 1rem 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 500;
}

.exercise-options {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
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

.exercise-input {
  margin-bottom: 1.5rem;
}

.exercise-input input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.exercise-input input:focus {
  outline: none;
  border-color: #667eea;
}

.check-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
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
  padding-top: 1rem;
}

.feedback-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
}

.feedback-content i {
  font-size: 1.25rem;
}

.feedback-content .el-icon-check {
  color: #10b981;
}

.feedback-content .el-icon-close {
  color: #ef4444;
}

.correct-answer {
  margin: 0 0 0.5rem 0;
  color: #059669;
  font-weight: 500;
}

.explanation {
  margin: 0 0 1rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.next-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s ease;
}

.next-btn:hover {
  background: #059669;
}

.lesson-navigation {
  text-align: center;
}

.nav-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: #5a6fd8;
}

.nav-btn.active {
  background: #10b981;
}

.nav-btn.active:hover {
  background: #059669;
}

@media (max-width: 768px) {
  .grammar-learning {
    padding: 1rem;
  }
  
  .learning-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .topic-grid {
    grid-template-columns: 1fr;
  }
  
  .topic-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .exercise-options {
    grid-template-columns: 1fr;
  }
}
</style>