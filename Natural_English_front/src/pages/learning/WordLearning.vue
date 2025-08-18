<template>
  <div class="word-learning">
    <div class="learning-header">
      <h1>单词学习</h1>
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
      <!-- 学习模式选择 -->
      <div class="mode-selector" v-if="!isLearning">
        <h2>选择学习模式</h2>
        <div class="mode-grid">
          <div 
            class="mode-card" 
            @click="startLearning('new')"
            v-permission="'learning.words.new'"
          >
            <div class="mode-icon">
              <i class="el-icon-plus"></i>
            </div>
            <h3>学习新单词</h3>
            <p>学习新的词汇，扩展词汇量</p>
          </div>
          
          <div 
            class="mode-card" 
            @click="startLearning('review')"
            v-permission="'learning.words.review'"
          >
            <div class="mode-icon">
              <i class="el-icon-refresh"></i>
            </div>
            <h3>复习单词</h3>
            <p>复习已学单词，巩固记忆</p>
          </div>
          
          <div 
            class="mode-card" 
            @click="startLearning('test')"
            v-permission="'learning.words.test'"
          >
            <div class="mode-icon">
              <i class="el-icon-edit-outline"></i>
            </div>
            <h3>单词测试</h3>
            <p>测试词汇掌握程度</p>
          </div>
        </div>
      </div>

      <!-- 学习界面 -->
      <div class="learning-interface" v-if="isLearning">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        
        <div class="word-card" v-if="currentWord">
          <div class="word-main">
            <h2 class="word-text">{{ currentWord.word }}</h2>
            <div class="word-phonetic" v-if="currentWord.phonetic">
              [{{ currentWord.phonetic }}]
              <button class="play-audio" @click="playAudio">
                <i class="el-icon-video-play"></i>
              </button>
            </div>
          </div>
          
          <div class="word-details" v-if="showDetails">
            <div class="word-meaning">
              <h4>释义</h4>
              <ul>
                <li v-for="meaning in currentWord.meanings" :key="meaning.id">
                  <span class="part-of-speech">{{ meaning.partOfSpeech }}</span>
                  <span class="definition">{{ meaning.definition }}</span>
                </li>
              </ul>
            </div>
            
            <div class="word-examples" v-if="currentWord.examples">
              <h4>例句</h4>
              <ul>
                <li v-for="example in currentWord.examples" :key="example.id">
                  <p class="example-text">{{ example.sentence }}</p>
                  <p class="example-translation">{{ example.translation }}</p>
                </li>
              </ul>
            </div>
          </div>
          
          <div class="word-actions">
            <button 
              class="action-btn secondary" 
              @click="toggleDetails"
              v-if="!showDetails"
            >
              查看释义
            </button>
            
            <div class="mastery-buttons" v-if="showDetails">
              <button class="action-btn danger" @click="markDifficult">
                <i class="el-icon-close"></i>
                不认识
              </button>
              <button class="action-btn warning" @click="markPartial">
                <i class="el-icon-question"></i>
                模糊
              </button>
              <button class="action-btn success" @click="markMastered">
                <i class="el-icon-check"></i>
                掌握
              </button>
            </div>
          </div>
        </div>
        
        <div class="learning-controls">
          <button class="control-btn" @click="previousWord" :disabled="currentIndex === 0">
            <i class="el-icon-arrow-left"></i>
            上一个
          </button>
          <span class="word-counter">{{ currentIndex + 1 }} / {{ totalWords }}</span>
          <button class="control-btn" @click="nextWord" :disabled="currentIndex === totalWords - 1">
            下一个
            <i class="el-icon-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { permissionChecker } from '@/utils/permissions'

interface Word {
  id: string
  word: string
  phonetic?: string
  meanings: Array<{
    id: string
    partOfSpeech: string
    definition: string
  }>
  examples?: Array<{
    id: string
    sentence: string
    translation: string
  }>
}

const store = useStore()

// 学习状态
const isLearning = ref(false)
const currentMode = ref('')
const showDetails = ref(false)

// 单词数据
const words = ref<Word[]>([])
const currentIndex = ref(0)
const currentWord = computed(() => words.value[currentIndex.value])
const totalWords = computed(() => words.value.length)

// 统计数据
const todayLearned = ref(0)
const totalMastered = ref(0)

// 进度计算
const progressPercentage = computed(() => {
  if (totalWords.value === 0) return 0
  return ((currentIndex.value + 1) / totalWords.value) * 100
})

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 开始学习
const startLearning = async (mode: string) => {
  try {
    currentMode.value = mode
    isLearning.value = true
    showDetails.value = false
    currentIndex.value = 0
    
    // 根据模式加载不同的单词
    await loadWords(mode)
    
    ElMessage.success(`开始${getModeText(mode)}`)
  } catch (error) {
    ElMessage.error('加载单词失败')
    console.error('加载单词失败:', error)
  }
}

// 加载单词
const loadWords = async (mode: string) => {
  // 模拟API调用
  const mockWords: Word[] = [
    {
      id: '1',
      word: 'artificial',
      phonetic: 'ˌɑːrtɪˈfɪʃl',
      meanings: [
        {
          id: '1',
          partOfSpeech: 'adj.',
          definition: '人工的，人造的'
        }
      ],
      examples: [
        {
          id: '1',
          sentence: 'Artificial intelligence is changing our world.',
          translation: '人工智能正在改变我们的世界。'
        }
      ]
    },
    {
      id: '2',
      word: 'intelligence',
      phonetic: 'ɪnˈtelɪdʒəns',
      meanings: [
        {
          id: '1',
          partOfSpeech: 'n.',
          definition: '智力，智能'
        }
      ],
      examples: [
        {
          id: '1',
          sentence: 'She has high emotional intelligence.',
          translation: '她有很高的情商。'
        }
      ]
    }
  ]
  
  words.value = mockWords
}

// 获取模式文本
const getModeText = (mode: string): string => {
  const modeMap: Record<string, string> = {
    'new': '新单词学习',
    'review': '单词复习',
    'test': '单词测试'
  }
  return modeMap[mode] || '学习'
}

// 切换详情显示
const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

// 播放音频
const playAudio = () => {
  // 实现音频播放逻辑
  ElMessage.info('音频播放功能待实现')
}

// 标记掌握程度
const markDifficult = () => {
  markWord('difficult')
}

const markPartial = () => {
  markWord('partial')
}

const markMastered = () => {
  markWord('mastered')
}

const markWord = async (level: string) => {
  try {
    // 发送到后端记录掌握程度
    await store.dispatch('learning/markWordMastery', {
      wordId: currentWord.value.id,
      level
    })
    
    ElMessage.success('已记录')
    nextWord()
  } catch (error) {
    ElMessage.error('记录失败')
  }
}

// 导航控制
const previousWord = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    showDetails.value = false
  }
}

const nextWord = () => {
  if (currentIndex.value < totalWords.value - 1) {
    currentIndex.value++
    showDetails.value = false
  } else {
    // 学习完成
    finishLearning()
  }
}

// 完成学习
const finishLearning = () => {
  isLearning.value = false
  ElMessage.success('学习完成！')
  loadStats()
}

// 加载统计数据
const loadStats = async () => {
  try {
    const stats = await store.dispatch('learning/getWordStats')
    todayLearned.value = stats.todayLearned
    totalMastered.value = stats.totalMastered
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.word-learning {
  max-width: 800px;
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

.mode-selector h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #1f2937;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.mode-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.mode-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.mode-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
}

.mode-card p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.learning-interface {
  max-width: 600px;
  margin: 0 auto;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  margin-bottom: 2rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.word-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.word-main {
  margin-bottom: 2rem;
}

.word-text {
  font-size: 3rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.word-phonetic {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 1.125rem;
}

.play-audio {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem;
}

.word-details {
  text-align: left;
  margin-bottom: 2rem;
}

.word-details h4 {
  color: #1f2937;
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
}

.word-details ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.word-details li {
  margin-bottom: 0.75rem;
}

.part-of-speech {
  display: inline-block;
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  margin-right: 0.5rem;
}

.definition {
  color: #1f2937;
}

.example-text {
  color: #1f2937;
  margin: 0 0 0.25rem 0;
  font-style: italic;
}

.example-translation {
  color: #6b7280;
  margin: 0;
  font-size: 0.875rem;
}

.word-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.mastery-buttons {
  display: flex;
  gap: 1rem;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.secondary:hover {
  background: #e5e7eb;
}

.action-btn.danger {
  background: #ef4444;
  color: white;
}

.action-btn.danger:hover {
  background: #dc2626;
}

.action-btn.warning {
  background: #f59e0b;
  color: white;
}

.action-btn.warning:hover {
  background: #d97706;
}

.action-btn.success {
  background: #10b981;
  color: white;
}

.action-btn.success:hover {
  background: #059669;
}

.learning-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.control-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.control-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.word-counter {
  color: #6b7280;
  font-weight: 500;
}

@media (max-width: 768px) {
  .word-learning {
    padding: 1rem;
  }
  
  .learning-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .mode-grid {
    grid-template-columns: 1fr;
  }
  
  .word-text {
    font-size: 2rem;
  }
  
  .mastery-buttons {
    flex-direction: column;
  }
  
  .learning-controls {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>