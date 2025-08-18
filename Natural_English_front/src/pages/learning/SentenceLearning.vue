<template>
  <div class="sentence-learning" v-permission="'learning.sentences.view'">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>句子学习</h1>
      <p>通过句子学习提高语言理解能力</p>
    </div>

    <!-- 学习模式选择 -->
    <div class="mode-selector">
      <div class="mode-card" 
           v-for="mode in learningModes" 
           :key="mode.id"
           :class="{ active: selectedMode === mode.id }"
           @click="selectMode(mode.id)">
        <div class="mode-icon">
          <i :class="mode.icon"></i>
        </div>
        <h3>{{ mode.title }}</h3>
        <p>{{ mode.description }}</p>
      </div>
    </div>

    <!-- 句子学习界面 -->
    <div class="learning-content" v-if="selectedMode && currentSentence">
      <div class="sentence-card">
        <div class="sentence-header">
          <span class="difficulty-badge" :class="currentSentence.difficulty">
            {{ difficultyMap[currentSentence.difficulty] }}
          </span>
          <span class="category-tag">{{ currentSentence.category }}</span>
        </div>
        
        <div class="sentence-main">
          <div class="sentence-text">
            <p class="english">{{ currentSentence.english }}</p>
            <p class="chinese" v-if="showTranslation">{{ currentSentence.chinese }}</p>
          </div>
          
          <div class="sentence-audio">
            <button @click="playAudio" class="audio-btn">
              <i class="fas fa-volume-up"></i>
              播放发音
            </button>
            <div class="speed-control">
              <label>语速:</label>
              <select v-model="playbackSpeed">
                <option value="0.5">0.5x</option>
                <option value="0.75">0.75x</option>
                <option value="1">1x</option>
                <option value="1.25">1.25x</option>
              </select>
            </div>
          </div>
        </div>

        <div class="sentence-details">
          <div class="grammar-points" v-if="currentSentence.grammarPoints">
            <h4>语法要点</h4>
            <ul>
              <li v-for="point in currentSentence.grammarPoints" :key="point">
                {{ point }}
              </li>
            </ul>
          </div>
          
          <div class="key-words" v-if="currentSentence.keyWords">
            <h4>重点词汇</h4>
            <div class="word-tags">
              <span v-for="word in currentSentence.keyWords" 
                    :key="word.word" 
                    class="word-tag"
                    @click="showWordDetail(word)">
                {{ word.word }}
              </span>
            </div>
          </div>
        </div>

        <div class="sentence-actions">
          <button @click="toggleTranslation" class="btn-secondary">
            {{ showTranslation ? '隐藏翻译' : '显示翻译' }}
          </button>
          <button @click="markAsLearned" class="btn-success">
            <i class="fas fa-check"></i>
            已掌握
          </button>
          <button @click="markForReview" class="btn-warning">
            <i class="fas fa-bookmark"></i>
            需复习
          </button>
          <button @click="nextSentence" class="btn-primary">
            下一句
            <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 学习进度 -->
    <div class="progress-section">
      <div class="progress-stats">
        <div class="stat-item">
          <span class="stat-number">{{ todayProgress.learned }}</span>
          <span class="stat-label">今日已学</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ todayProgress.target }}</span>
          <span class="stat-label">今日目标</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ totalProgress.mastered }}</span>
          <span class="stat-label">总计掌握</span>
        </div>
      </div>
      
      <div class="progress-bar">
        <div class="progress-fill" 
             :style="{ width: progressPercentage + '%' }">
        </div>
      </div>
    </div>

    <!-- 词汇详情弹窗 -->
    <div class="word-modal" v-if="selectedWord" @click="closeWordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedWord.word }}</h3>
          <button @click="closeWordModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p class="phonetic">{{ selectedWord.phonetic }}</p>
          <p class="meaning">{{ selectedWord.meaning }}</p>
          <div class="examples" v-if="selectedWord.examples">
            <h4>例句</h4>
            <ul>
              <li v-for="example in selectedWord.examples" :key="example">
                {{ example }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

interface Sentence {
  id: number
  english: string
  chinese: string
  difficulty: 'easy' | 'medium' | 'hard'
  category: string
  grammarPoints?: string[]
  keyWords?: Array<{
    word: string
    phonetic: string
    meaning: string
    examples?: string[]
  }>
}

interface LearningMode {
  id: string
  title: string
  description: string
  icon: string
}

const store = useStore()

// 响应式数据
const selectedMode = ref<string>('')
const currentSentence = ref<Sentence | null>(null)
const showTranslation = ref(false)
const playbackSpeed = ref(1)
const selectedWord = ref<any>(null)

// 学习模式
const learningModes: LearningMode[] = [
  {
    id: 'new',
    title: '新句子学习',
    description: '学习新的句子结构',
    icon: 'fas fa-plus-circle'
  },
  {
    id: 'review',
    title: '复习练习',
    description: '复习已学过的句子',
    icon: 'fas fa-redo'
  },
  {
    id: 'test',
    title: '理解测试',
    description: '测试句子理解能力',
    icon: 'fas fa-clipboard-check'
  }
]

// 难度映射
const difficultyMap = {
  easy: '简单',
  medium: '中等',
  hard: '困难'
}

// 模拟数据
const mockSentences: Sentence[] = [
  {
    id: 1,
    english: "The weather is beautiful today.",
    chinese: "今天天气很好。",
    difficulty: 'easy',
    category: '日常对话',
    grammarPoints: ['主系表结构', '形容词作表语'],
    keyWords: [
      {
        word: 'weather',
        phonetic: '/ˈweðər/',
        meaning: '天气',
        examples: ['What\'s the weather like?']
      },
      {
        word: 'beautiful',
        phonetic: '/ˈbjuːtɪfl/',
        meaning: '美丽的，漂亮的',
        examples: ['She has beautiful eyes.']
      }
    ]
  },
  {
    id: 2,
    english: "I have been studying English for three years.",
    chinese: "我学英语已经三年了。",
    difficulty: 'medium',
    category: '学习经历',
    grammarPoints: ['现在完成进行时', '时间状语for的用法'],
    keyWords: [
      {
        word: 'studying',
        phonetic: '/ˈstʌdiɪŋ/',
        meaning: '学习（现在分词）',
        examples: ['I am studying for the exam.']
      }
    ]
  }
]

// 进度数据
const todayProgress = ref({
  learned: 5,
  target: 10
})

const totalProgress = ref({
  mastered: 156
})

// 计算属性
const progressPercentage = computed(() => {
  return Math.round((todayProgress.value.learned / todayProgress.value.target) * 100)
})

// 方法
const selectMode = (modeId: string) => {
  selectedMode.value = modeId
  loadSentence()
}

const loadSentence = () => {
  // 模拟加载句子
  const randomIndex = Math.floor(Math.random() * mockSentences.length)
  currentSentence.value = mockSentences[randomIndex]
  showTranslation.value = false
}

const playAudio = () => {
  // 模拟音频播放
  console.log(`Playing audio at ${playbackSpeed.value}x speed`)
}

const toggleTranslation = () => {
  showTranslation.value = !showTranslation.value
}

const markAsLearned = () => {
  if (currentSentence.value) {
    console.log('Marked as learned:', currentSentence.value.id)
    todayProgress.value.learned++
    nextSentence()
  }
}

const markForReview = () => {
  if (currentSentence.value) {
    console.log('Marked for review:', currentSentence.value.id)
    nextSentence()
  }
}

const nextSentence = () => {
  loadSentence()
}

const showWordDetail = (word: any) => {
  selectedWord.value = word
}

const closeWordModal = () => {
  selectedWord.value = null
}

// 生命周期
onMounted(() => {
  // 默认选择第一个模式
  if (learningModes.length > 0) {
    selectMode(learningModes[0].id)
  }
})
</script>

<style scoped lang="scss">
.sentence-learning {
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

.mode-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.mode-card {
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
  
  .mode-icon {
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
  }
}

.learning-content {
  margin-bottom: 30px;
}

.sentence-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sentence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.difficulty-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  
  &.easy {
    background: #d4edda;
    color: #155724;
  }
  
  &.medium {
    background: #fff3cd;
    color: #856404;
  }
  
  &.hard {
    background: #f8d7da;
    color: #721c24;
  }
}

.category-tag {
  background: #e9ecef;
  color: #495057;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.sentence-main {
  margin-bottom: 24px;
}

.sentence-text {
  margin-bottom: 20px;
  
  .english {
    font-size: 24px;
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 12px;
    line-height: 1.4;
  }
  
  .chinese {
    font-size: 18px;
    color: #7f8c8d;
    line-height: 1.4;
  }
}

.sentence-audio {
  display: flex;
  align-items: center;
  gap: 20px;
}

.audio-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
  
  &:hover {
    background: #2980b9;
  }
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 8px;
  
  label {
    font-size: 14px;
    color: #7f8c8d;
  }
  
  select {
    padding: 4px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
}

.sentence-details {
  margin-bottom: 24px;
}

.grammar-points, .key-words {
  margin-bottom: 20px;
  
  h4 {
    color: #2c3e50;
    margin-bottom: 12px;
    font-size: 16px;
  }
}

.grammar-points ul {
  list-style: none;
  padding: 0;
  
  li {
    background: #f8f9fa;
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 6px;
    border-left: 3px solid #3498db;
  }
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.word-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #bbdefb;
  }
}

.sentence-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-secondary, .btn-success, .btn-warning, .btn-primary {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  
  &:hover {
    background: #5a6268;
  }
}

.btn-success {
  background: #28a745;
  color: white;
  
  &:hover {
    background: #218838;
  }
}

.btn-warning {
  background: #ffc107;
  color: #212529;
  
  &:hover {
    background: #e0a800;
  }
}

.btn-primary {
  background: #007bff;
  color: white;
  
  &:hover {
    background: #0056b3;
  }
}

.progress-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  
  .stat-number {
    display: block;
    font-size: 24px;
    font-weight: 600;
    color: #3498db;
    margin-bottom: 4px;
  }
  
  .stat-label {
    font-size: 14px;
    color: #7f8c8d;
  }
}

.progress-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.word-modal {
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
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  
  h3 {
    margin: 0;
    color: #2c3e50;
  }
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #7f8c8d;
  cursor: pointer;
  
  &:hover {
    color: #2c3e50;
  }
}

.modal-body {
  padding: 24px;
  
  .phonetic {
    color: #7f8c8d;
    font-style: italic;
    margin-bottom: 12px;
  }
  
  .meaning {
    font-size: 16px;
    color: #2c3e50;
    margin-bottom: 20px;
  }
  
  .examples {
    h4 {
      color: #2c3e50;
      margin-bottom: 12px;
    }
    
    ul {
      list-style: none;
      padding: 0;
      
      li {
        background: #f8f9fa;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        border-left: 3px solid #28a745;
      }
    }
  }
}

@media (max-width: 768px) {
  .sentence-learning {
    padding: 16px;
  }
  
  .sentence-card {
    padding: 20px;
  }
  
  .sentence-text .english {
    font-size: 20px;
  }
  
  .sentence-actions {
    flex-direction: column;
  }
  
  .sentence-audio {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>