<template>
  <div class="enhanced-word-practice-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="back-btn" @click="goBack">
        <span class="arrow">←</span>
      </div>
      <div class="title">增强版单词练习</div>
      <div class="settings-btn" @click="showSettings = true">
        <span class="settings-icon">⚙️</span>
      </div>
    </div>

    <!-- 练习配置界面 -->
    <div v-if="!practiceStarted" class="practice-config">
      <!-- 用户信息显示 -->
      <div class="config-section" v-if="userInfo">
        <h3>当前用户</h3>
        <div class="user-info-card">
          <p><strong>用户名:</strong> {{ userInfo.username }}</p>
          <p v-if="userInfo.email"><strong>邮箱:</strong> {{ userInfo.email }}</p>
        </div>
      </div>
      
      <!-- 当前学习目标显示 -->
      <div class="config-section" v-if="currentLearningGoal">
        <h3>当前学习目标</h3>
        <div class="goal-card">
          <h4>{{ currentLearningGoal.name }}</h4>
          <p>{{ currentLearningGoal.description }}</p>
          <p><strong>目标单词数:</strong> {{ availableWords ? availableWords.length : 0 }}</p>
          <p><strong>状态:</strong> {{ currentLearningGoal.is_active ? '活跃' : '非活跃' }}</p>
        </div>
      </div>
      
      <!-- 学习目标配置区域 -->
      <div class="config-section">
        <div class="goal-config-header">
          <h3>学习目标配置</h3>
          <button class="config-btn" @click="showGoalConfig = !showGoalConfig">
            {{ showGoalConfig ? '收起配置' : '展开配置' }}
          </button>
        </div>
        
        <!-- 学习目标配置组件 -->
        <div v-if="showGoalConfig" class="goal-config-panel">
          <LearningGoalConfig 
            :current-goal="currentLearningGoal"
            :available-goals="learningGoals"
            @goal-changed="handleGoalChanged"
            @goal-created="handleGoalCreated"
            @plan-updated="handlePlanUpdated"
          />
        </div>
        
        <!-- 简化的学习目标选择 -->
        <div v-else class="simple-goal-selector">
          <div class="current-goal-display" v-if="currentLearningGoal">
            <div class="goal-info">
              <span class="goal-name">{{ currentLearningGoal.name }}</span>
              <span class="goal-progress">({{ currentLearningGoal.learned_words || 0 }}/{{ currentLearningGoal.target_words || 0 }})</span>
            </div>
            <button class="change-goal-btn" @click="showGoalSelector = true">切换目标</button>
          </div>
          
          <div v-else class="no-goal-selected">
            <p>未选择学习目标</p>
            <button class="select-goal-btn" @click="showGoalSelector = true">选择目标</button>
          </div>
        </div>
        
        <!-- 目标选择弹窗 -->
        <div v-if="showGoalSelector" class="goal-selector-modal">
          <div class="modal-content">
            <div class="modal-header">
              <h4>选择学习目标</h4>
              <button class="close-btn" @click="showGoalSelector = false">×</button>
            </div>
            <div class="modal-body">
              <div v-if="learningGoals.length === 0" class="no-goals">
                <p>暂无可用的学习目标</p>
                <button class="create-goal-btn" @click="showGoalConfig = true; showGoalSelector = false">创建学习目标</button>
              </div>
              <div v-else class="goals-list">
                <div 
                  v-for="goal in learningGoals" 
                  :key="goal.id" 
                  class="goal-item"
                  :class="{ active: selectedGoalId === goal.id }"
                  @click="selectGoal(goal)"
                >
                  <div class="goal-content">
                    <h5>{{ goal.name }}</h5>
                    <p>{{ goal.description }}</p>
                    <div class="goal-stats">
                      <span>总词数: {{ goal.total_words || 0 }}</span>
                      <span>已学: {{ goal.learned_words || 0 }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedGoalId" class="config-section">
        <h3>练习模式</h3>
        <div class="mode-selector">
          <div 
            class="mode-option" 
            :class="{ active: practiceMode === 'meaning' }"
            @click="practiceMode = 'meaning'"
          >
            <div class="mode-icon">📖</div>
            <div class="mode-title">看单词说词意</div>
            <div class="mode-desc">自我评估模式，测试词汇理解</div>
          </div>
          <div 
            class="mode-option" 
            :class="{ active: practiceMode === 'pronunciation' }"
            @click="practiceMode = 'pronunciation'"
          >
            <div class="mode-icon">🔊</div>
            <div class="mode-title">看单词听读音</div>
            <div class="mode-desc">音频学习模式，提升发音技能</div>
          </div>
        </div>
      </div>

      <div v-if="selectedGoalId && practiceMode" class="config-section">
        <h3>单词练习</h3>
        <div class="word-practice-list">
          <div class="practice-header">
            <div class="back-arrow" @click="goBack">←</div>
            <div class="practice-title">单词练习</div>
            <div class="save-btn">保存</div>
          </div>
          
          <div class="word-list-container">
            <div v-for="(word, index) in previewWords" :key="word.id || index" class="word-item">
              <div class="word-content">{{ word.word || word.text || `单词${index + 1}` }}</div>
              <div class="word-actions">
                <button class="action-btn" :class="{ active: word.marked === true }" @click="markWord(word, true)">✓</button>
              </div>
            </div>
          </div>
          
          <div class="practice-footer">
            <div class="progress-info">
              <span class="progress-text">{{ correctPreviewCount }}/{{ previewWords.length }}</span>
            </div>
          </div>
        </div>
      </div>


    </div>

    <!-- 练习界面 -->
    <div v-if="practiceStarted" class="practice-interface">
      <!-- 进度条 -->
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        <span class="progress-text">{{ currentIndex + 1 }} / {{ practiceWords.length }}</span>
      </div>

      <!-- 单词练习区域 -->
      <div class="word-practice-area">
        <div v-if="currentWord" class="current-word">
          <div class="word-display">
            <h2 class="word-text">{{ currentWord.word }}</h2>
            <div v-if="practiceMode === 'pronunciation'" class="audio-controls">
              <button class="play-btn" @click="playAudio" :disabled="audioLoading">
                {{ audioLoading ? '加载中...' : '🔊 播放发音' }}
              </button>
            </div>
          </div>

          <div v-if="practiceMode === 'meaning'" class="meaning-practice">
            <div class="question">你知道这个单词的意思吗？</div>
            <div class="answer-buttons">
              <button class="know-btn" @click="answerWord(true)">认识</button>
              <button class="unknown-btn" @click="answerWord(false)">不认识</button>
            </div>
            <div v-if="showMeaning" class="word-meaning">
              <p><strong>释义：</strong>{{ currentWord.meaning }}</p>
              <button class="next-btn" @click="nextWord">下一个</button>
            </div>
          </div>

          <div v-if="practiceMode === 'pronunciation'" class="pronunciation-practice">
            <div class="question">听完发音后，你觉得发音正确吗？</div>
            <div class="answer-buttons">
              <button class="correct-btn" @click="answerWord(true)">发音正确</button>
              <button class="incorrect-btn" @click="answerWord(false)">需要练习</button>
            </div>
            <div v-if="showMeaning" class="word-info">
              <p><strong>单词：</strong>{{ currentWord.word }}</p>
              <p><strong>释义：</strong>{{ currentWord.meaning }}</p>
              <button class="next-btn" @click="nextWord">下一个</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 练习统计 -->
      <div class="practice-stats">
        <div class="stat-item">
          <span class="stat-label">已练习：</span>
          <span class="stat-value">{{ answeredCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">掌握：</span>
          <span class="stat-value correct">{{ correctCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">需复习：</span>
          <span class="stat-value incorrect">{{ incorrectCount }}</span>
        </div>
      </div>
    </div>

    <!-- 练习完成界面 -->
    <div v-if="practiceCompleted" class="practice-completed">
      <div class="completion-header">
        <h2>🎉 练习完成！</h2>
        <div class="completion-stats">
          <div class="stat-card">
            <div class="stat-number">{{ practiceWords.length }}</div>
            <div class="stat-label">总单词数</div>
          </div>
          <div class="stat-card">
            <div class="stat-number correct">{{ correctCount }}</div>
            <div class="stat-label">掌握单词</div>
          </div>
          <div class="stat-card">
            <div class="stat-number incorrect">{{ incorrectCount }}</div>
            <div class="stat-label">需复习</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ accuracyPercentage }}%</div>
            <div class="stat-label">掌握率</div>
          </div>
        </div>
      </div>

      <div class="detailed-report">
        <h3>详细报告</h3>
        <div class="report-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'mastered' }"
            @click="activeTab = 'mastered'"
          >
            掌握单词 ({{ masteredWords.length }})
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'review' }"
            @click="activeTab = 'review'"
          >
            需复习 ({{ reviewWords.length }})
          </button>
        </div>
        
        <div class="tab-content">
          <div v-if="activeTab === 'mastered'" class="word-list">
            <div v-for="word in masteredWords" :key="word.id" class="word-item mastered">
              <span class="word">{{ word.word }}</span>
              <span class="meaning">{{ word.meaning }}</span>
            </div>
          </div>
          <div v-if="activeTab === 'review'" class="word-list">
            <div v-for="word in reviewWords" :key="word.id" class="word-item review">
              <span class="word">{{ word.word }}</span>
              <span class="meaning">{{ word.meaning }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="completion-actions">
        <button class="action-btn secondary" @click="restartPractice">重新练习</button>
        <button class="action-btn primary" @click="backToConfig">返回配置</button>
        <button class="action-btn primary" @click="viewProgress">查看进度</button>
      </div>
    </div>

    <!-- 设置弹窗 -->
    <div v-if="showSettings" class="settings-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>练习设置</h3>
          <button class="close-btn" @click="showSettings = false">×</button>
        </div>
        <div class="modal-body">
          <div class="setting-group">
            <label>音频播放</label>
            <input type="checkbox" v-model="autoPlayAudio">
            <span>自动播放单词发音</span>
          </div>
          <div class="setting-group">
            <label>显示提示</label>
            <input type="checkbox" v-model="showHints">
            <span>显示学习提示</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { learningAPI, userAPI } from '../utils/api'
import LearningGoalConfig from '../components/LearningGoalConfig.vue'

export default {
  name: 'EnhancedWordPractice',
  components: {
    LearningGoalConfig
  },
  data() {
    return {
      // 配置状态
      practiceStarted: false,
      practiceCompleted: false,
      loading: false,
      
      // 用户信息
      userInfo: null,
      
      // 学习目标
      learningGoals: [],
      selectedGoalId: '',
      currentLearningGoal: null,
      
      // UI状态
      showGoalConfig: false,
      showGoalSelector: false,
      
      // 练习设置
      practiceMode: '', // 'meaning' 或 'pronunciation'
      wordsCount: 20,
      useSmartRecommendation: true,
      
      // 练习数据
      practiceWords: [],
      previewWords: [],
      availableWords: [], // 可用单词列表
      currentIndex: 0,
      showMeaning: false,
      
      // 预览练习状态
      correctPreviewCount: 0,
      
      // 学习记录
      learningSession: null,
      wordRecords: [],
      
      // 音频相关
      audioLoading: false,
      autoPlayAudio: true,
      
      // UI状态
      showSettings: false,
      showHints: true,
      activeTab: 'mastered',
      
      // 计时
      startTime: null,
      questionStartTime: null,
      
      // 错误处理和状态管理
      networkError: false,
      sessionExpired: false,
      audioError: false,
      retryCount: 0,
      maxRetries: 3,
      offlineMode: false,
      pendingRecords: [],
      lastSyncTime: null
    }
  },
  
  computed: {
    currentWord() {
      return this.practiceWords[this.currentIndex] || null
    },
    
    progressPercentage() {
      if (this.practiceWords.length === 0) return 0
      return Math.round((this.currentIndex / this.practiceWords.length) * 100)
    },
    
    answeredCount() {
      return this.wordRecords.length
    },
    
    correctCount() {
      return this.wordRecords.filter(record => record.is_correct).length
    },
    
    incorrectCount() {
      return this.wordRecords.filter(record => !record.is_correct).length
    },
    
    accuracyPercentage() {
      if (this.answeredCount === 0) return 0
      return Math.round((this.correctCount / this.answeredCount) * 100)
    },
    
    masteredWords() {
      return this.wordRecords
        .filter(record => record.is_correct)
        .map(record => record.word)
    },
    
    reviewWords() {
      return this.wordRecords
        .filter(record => !record.is_correct)
        .map(record => record.word)
    }
  },
  
  methods: {
    // 数据加载方法
    async loadUserInfo() {
      try {
        this.loading = true
        this.networkError = false
        const response = await userAPI.getProfile()
        this.userInfo = response
        console.log('用户信息:', this.userInfo)
        this.retryCount = 0
      } catch (error) {
        console.error('加载用户信息失败:', error)
        await this.handleApiError(error, '加载用户信息失败')
      } finally {
        this.loading = false
      }
    },
    
    async loadCurrentLearningGoal() {
      try {
        this.loading = true
        this.networkError = false
        const response = await learningAPI.getCurrentLearningGoal()
        this.currentLearningGoal = response
        console.log('当前学习目标:', this.currentLearningGoal)
        
        // 如果有当前学习目标，自动选择它
        if (this.currentLearningGoal && this.currentLearningGoal.id) {
          this.selectedGoalId = this.currentLearningGoal.id
          // 加载该目标的单词
          await this.loadGoalWords()
        }
        
        this.retryCount = 0
      } catch (error) {
        console.log('没有当前活跃的学习目标，将加载所有可用目标')
        // 如果没有当前学习目标（404错误），这是正常情况，加载所有可用的学习目标
        this.currentLearningGoal = null
        await this.loadLearningGoals()
      } finally {
        this.loading = false
      }
    },
    
    async loadLearningGoals() {
      try {
        this.loading = true
        this.networkError = false
        const response = await learningAPI.getLearningGoals({ is_active: true })
        const goals = response.results || response
        // 确保learningGoals始终是数组
        this.learningGoals = Array.isArray(goals) ? goals : []
        console.log('所有学习目标:', this.learningGoals)
        this.retryCount = 0
      } catch (error) {
        console.error('加载学习目标失败:', error)
        // 出错时确保learningGoals是空数组
        this.learningGoals = []
        await this.handleApiError(error, '加载学习目标失败')
      } finally {
        this.loading = false
      }
    },
    
    async loadGoalWords() {
      if (!this.selectedGoalId) {
        this.availableWords = []
        this.previewWords = []
        return
      }
      
      try {
        this.loading = true
        this.networkError = false
        
        // 获取学习目标的详细信息，包括关联的单词
        const goalResponse = await learningAPI.getLearningGoals({ id: this.selectedGoalId })
        const goalData = goalResponse.results ? goalResponse.results[0] : goalResponse
        
        if (goalData && goalData.words) {
          this.availableWords = goalData.words
          console.log('学习目标单词:', this.availableWords)
        } else {
          // 如果目标详情中没有单词，尝试通过练习单词API获取
          const wordsResponse = await learningAPI.getPracticeWords({ 
            goal_id: this.selectedGoalId,
            count: 1000 // 获取所有单词
          })
          this.availableWords = wordsResponse.results || wordsResponse
          console.log('通过练习API获取的学习目标单词:', this.availableWords)
        }
        
        // 初始化预览单词列表（显示前14个单词）
        const defaultWords = ['cabbage', 'lemon', 'potato', 'deer', 'nut', 'ball', 'mom', 'three', 'cow', 'speak', 'please', 'brown', 'six', 'peach']
        
        if (this.availableWords.length > 0) {
          this.previewWords = this.availableWords.slice(0, 14).map((word, index) => ({
            ...word,
            word: word.word || word.text || defaultWords[index] || `单词${index + 1}`,
            marked: null // null: 未标记, true: 正确, false: 错误
          }))
        } else {
          // 如果没有可用单词，使用默认单词列表
          this.previewWords = defaultWords.map((word, index) => ({
            id: index + 1,
            word: word,
            marked: null
          }))
        }
        
        this.retryCount = 0
      } catch (error) {
        console.error('加载目标单词失败:', error)
        this.availableWords = []
        // 即使出错也显示默认单词列表
        const defaultWords = ['cabbage', 'lemon', 'potato', 'deer', 'nut', 'ball', 'mom', 'three', 'cow', 'speak', 'please', 'brown', 'six', 'peach']
        this.previewWords = defaultWords.map((word, index) => ({
          id: index + 1,
          word: word,
          marked: null
        }))
        await this.handleApiError(error, '加载目标单词失败')
      } finally {
        this.loading = false
      }
    },
    
    // 学习目标配置相关方法
    async selectGoal(goal) {
      this.selectedGoalId = goal.id
      this.currentLearningGoal = goal
      this.showGoalSelector = false
      await this.loadGoalWords()
    },
    
    async handleGoalChanged(goal) {
      this.currentLearningGoal = goal
      this.selectedGoalId = goal.id
      await this.loadGoalWords()
      this.$message?.success('学习目标已切换')
    },
    
    async handleGoalCreated(goal) {
      // 重新加载学习目标列表
      await this.loadLearningGoals()
      // 设置新创建的目标为当前目标
      this.currentLearningGoal = goal
      this.selectedGoalId = goal.id
      await this.loadGoalWords()
      this.$message?.success('学习目标创建成功')
    },
    
    async handlePlanUpdated(plan) {
      // 学习计划更新后，可能需要刷新当前学习目标的信息
      if (this.currentLearningGoal && this.currentLearningGoal.id === plan.goal) {
        await this.loadCurrentLearningGoal()
      }
      this.$message?.success('学习计划已更新')
    },
    
    // 练习控制方法
    async startPractice() {
      if (!this.selectedGoalId || !this.practiceMode) {
        this.$message?.warning('请完成练习配置')
        return
      }
      
      try {
        this.loading = true
        this.networkError = false
        this.sessionExpired = false
        
        // 创建学习会话
        const sessionResponse = await learningAPI.createLearningSession({
          goal: this.selectedGoalId
        })
        this.learningSession = sessionResponse
        
        // 获取练习单词
        await this.getPracticeWords()
        
        // 开始练习
        this.practiceStarted = true
        this.currentIndex = 0
        this.wordRecords = []
        this.startTime = Date.now()
        this.questionStartTime = Date.now()
        this.retryCount = 0
        
        // 如果是发音模式且开启自动播放，播放第一个单词
        if (this.practiceMode === 'pronunciation' && this.autoPlayAudio) {
          setTimeout(() => this.playAudio(), 500)
        }
        
      } catch (error) {
        console.error('开始练习失败:', error)
        await this.handleApiError(error, '开始练习失败')
      } finally {
        this.loading = false
      }
    },
    
    async getPracticeWords() {
      try {
        const params = {
          goal_id: this.selectedGoalId,
          count: this.wordsCount,
          smart_recommendation: this.useSmartRecommendation
        }
        
        const response = await learningAPI.getPracticeWords(params)
        this.practiceWords = response.results || response
        
        if (this.practiceWords.length === 0) {
          throw new Error('没有可练习的单词')
        }
      } catch (error) {
        console.error('获取练习单词失败:', error)
        if (error.message === '没有可练习的单词') {
          this.$message?.warning('当前学习目标没有可练习的单词，请选择其他目标')
        }
        throw error
      }
    },
    
    // 答题方法
    async answerWord(isCorrect) {
      if (!this.currentWord) return
      
      const responseTime = (Date.now() - this.questionStartTime) / 1000
      
      // 记录答题结果
      const record = {
        word: this.currentWord,
        is_correct: isCorrect,
        response_time: responseTime,
        practice_mode: this.practiceMode,
        timestamp: Date.now()
      }
      
      this.wordRecords.push(record)
      
      // 发送到后端
      const recordData = {
        session: this.learningSession?.id,
        goal: this.selectedGoalId,
        word: this.currentWord.id,
        user_answer: isCorrect ? 'correct' : 'incorrect',
        is_correct: isCorrect,
        response_time: responseTime
      }
      
      try {
        await learningAPI.createWordLearningRecord(recordData)
        this.lastSyncTime = Date.now()
      } catch (error) {
        console.error('保存学习记录失败:', error)
        // 离线模式：保存到本地待同步
        this.pendingRecords.push(recordData)
        if (!this.offlineMode) {
          this.offlineMode = true
          this.$message?.warning('网络连接不稳定，学习记录将在网络恢复后同步')
        }
      }
      
      // 显示答案
      this.showMeaning = true
    },
    
    nextWord() {
      this.showMeaning = false
      this.currentIndex++
      this.questionStartTime = Date.now()
      
      if (this.currentIndex >= this.practiceWords.length) {
        this.completePractice()
      } else if (this.practiceMode === 'pronunciation' && this.autoPlayAudio) {
        setTimeout(() => this.playAudio(), 300)
      }
    },
    
    async completePractice() {
      try {
        // 同步待处理的记录
        await this.syncPendingRecords()
        
        // 结束学习会话
        if (this.learningSession) {
          await learningAPI.endLearningSession(this.learningSession.id)
        }
        
        this.practiceStarted = false
        this.practiceCompleted = true
        this.offlineMode = false
        
      } catch (error) {
        console.error('完成练习失败:', error)
        await this.handleApiError(error, '完成练习时出现问题')
        // 即使出错也要显示完成界面
        this.practiceStarted = false
        this.practiceCompleted = true
      }
    },
    
    // 音频播放
    async playAudio() {
      if (!this.currentWord) return
      
      try {
        this.audioLoading = true
        this.audioError = false
        
        // 使用Web Speech API或第三方TTS服务
        if ('speechSynthesis' in window && !this.audioError) {
          const utterance = new SpeechSynthesisUtterance(this.currentWord.word)
          utterance.lang = 'en-US'
          utterance.rate = 0.8
          
          utterance.onerror = (event) => {
            console.error('语音合成错误:', event)
            this.audioError = true
            this.tryBackupAudio()
          }
          
          speechSynthesis.speak(utterance)
        } else {
          await this.tryBackupAudio()
        }
      } catch (error) {
        console.error('播放音频失败:', error)
        this.audioError = true
        this.$message?.error('播放音频失败，请检查设备音频设置')
      } finally {
        this.audioLoading = false
      }
    },
    
    // 备用音频播放方案
    async tryBackupAudio() {
      try {
        // 备用方案：调用后端TTS API
        const response = await axios.get(`/api/words/${this.currentWord.id}/audio/`, {
          timeout: 5000
        })
        const audio = new Audio(response.data.audio_url)
        
        audio.onerror = () => {
          this.audioError = true
          this.$message?.warning('音频播放不可用，请手动查看单词发音')
        }
        
        await audio.play()
      } catch (error) {
        console.error('备用音频播放失败:', error)
        this.audioError = true
        this.$message?.warning('音频服务暂时不可用')
      }
    },
    
    // 重置和导航方法
    restartPractice() {
      this.practiceCompleted = false
      this.practiceStarted = false
      this.currentIndex = 0
      this.wordRecords = []
      this.showMeaning = false
      this.startPractice()
    },
    
    backToConfig() {
      this.practiceCompleted = false
      this.practiceStarted = false
      this.currentIndex = 0
      this.wordRecords = []
      this.showMeaning = false
      this.selectedGoalId = ''
      this.practiceMode = ''
    },
    
    viewProgress() {
      this.$router.push({
        path: '/learning-progress',
        query: { goal_id: this.selectedGoalId }
      })
    },
    
    goBack() {
      this.$router.go(-1)
    },
    
    // 错误处理方法
    async handleApiError(error, userMessage) {
      this.retryCount++
      
      // 检查错误类型
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        this.networkError = true
        if (this.retryCount <= this.maxRetries) {
          this.$message?.warning(`网络超时，正在重试... (${this.retryCount}/${this.maxRetries})`)
          await this.delay(2000 * this.retryCount)
          return
        } else {
          this.$message?.error('网络连接超时，请检查网络设置')
        }
      } else if (error.response?.status === 401) {
        this.sessionExpired = true
        this.$message?.error('登录已过期，请重新登录')
        // 可以跳转到登录页面
        // this.$router.push('/login')
      } else if (error.response?.status === 403) {
        this.$message?.error('没有权限访问此功能')
      } else if (error.response?.status >= 500) {
        this.$message?.error('服务器错误，请稍后重试')
      } else if (!navigator.onLine) {
        this.networkError = true
        this.offlineMode = true
        this.$message?.warning('网络连接已断开，部分功能将在离线模式下运行')
      } else {
        this.$message?.error(userMessage || '操作失败，请重试')
      }
    },
    
    // 同步待处理记录
    async syncPendingRecords() {
      if (this.pendingRecords.length === 0) return
      
      try {
        for (const record of this.pendingRecords) {
          await learningAPI.createWordLearningRecord(record)
        }
        this.pendingRecords = []
        this.offlineMode = false
        this.$message?.success('学习记录已同步')
      } catch (error) {
        console.error('同步记录失败:', error)
        this.$message?.warning('部分学习记录同步失败，将在下次练习时重试')
      }
    },
    
    // 工具方法
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },
    
    // 标记单词
    markWord(word, isCorrect) {
      const wordIndex = this.previewWords.findIndex(w => w === word)
      if (wordIndex !== -1) {
        // 更新之前的计数
        if (this.previewWords[wordIndex].marked === true) {
          this.correctPreviewCount--
          this.previewWords[wordIndex].marked = null
        } else {
          // 如果之前未标记，则标记为正确
          this.previewWords[wordIndex].marked = true
          this.correctPreviewCount++
        }
      }
    },
    
    // 返回上一页
    goBack() {
      this.selectedGoalId = null
      this.practiceMode = null
      this.previewWords = []
      this.correctPreviewCount = 0
    },
    
    // 网络状态监听
    setupNetworkListeners() {
      window.addEventListener('online', () => {
        this.networkError = false
        this.offlineMode = false
        this.$message?.success('网络连接已恢复')
        this.syncPendingRecords()
      })
      
      window.addEventListener('offline', () => {
        this.networkError = true
        this.offlineMode = true
        this.$message?.warning('网络连接已断开，进入离线模式')
      })
     }
  },
  
  async mounted() {
    // 首先加载用户信息
    await this.loadUserInfo()
    
    // 然后尝试获取用户当前的学习目标
    await this.loadCurrentLearningGoal()
    
    // 如果没有当前学习目标，则加载所有可用的学习目标
    if (!this.currentLearningGoal && this.learningGoals.length === 0) {
      await this.loadLearningGoals()
    }
    
    this.setupNetworkListeners()
  },
  
  beforeDestroy() {
    // 清理事件监听器
    window.removeEventListener('online', () => {})
    window.removeEventListener('offline', () => {})
  }
}
</script>

<style scoped>
/* 学习目标配置相关样式 */
.goal-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.config-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.config-btn:hover {
  background: #0056b3;
}

.goal-config-panel {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #f9f9f9;
}

.simple-goal-selector {
  margin-bottom: 20px;
}

.current-goal-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #e8f5e8;
  border-radius: 8px;
  border: 1px solid #c3e6c3;
}

.goal-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.goal-name {
  font-weight: bold;
  color: #2d5a2d;
}

.goal-progress {
  font-size: 14px;
  color: #666;
}

.change-goal-btn, .select-goal-btn, .create-goal-btn {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.change-goal-btn:hover, .select-goal-btn:hover, .create-goal-btn:hover {
  background: #1e7e34;
}

.no-goal-selected {
  text-align: center;
  padding: 20px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  color: #856404;
}

.goal-selector-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h4 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.no-goals {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.goal-item {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.goal-item:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.goal-item.active {
  border-color: #007bff;
  background: #e3f2fd;
}

.goal-content h5 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
}

.goal-content p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.goal-stats {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #888;
}

.goal-stats span {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 12px;
}
/* 主容器样式 */
.word-selection {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow-x: hidden;
}

.word-selection::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

/* 容器内容 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* 页面标题 */
.page-title {
  text-align: center;
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 1px;
}

/* 用户信息卡片 */
.user-info {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.user-info:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.user-info h3 {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.user-info p {
  color: #666;
  margin: 0.5rem 0;
  font-size: 1rem;
}

/* 学习目标选择区域 */
.goal-selection {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.goal-selection h3 {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.goal-selection h3::before {
  content: '🎯';
  font-size: 1.2rem;
}

/* 选择框样式 */
.goal-select {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
}

.goal-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.goal-select:hover {
  border-color: #667eea;
}

/* 提示信息 */
.goal-hint {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
  border-radius: 12px;
  color: #2d3436;
  font-size: 0.9rem;
  border-left: 4px solid #fdcb6e;
}

/* 单词预览区域 */
.word-preview {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.word-preview h3 {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.word-preview h3::before {
  content: '📚';
  font-size: 1.2rem;
}

/* 单词网格 */
.word-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.word-item {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  color: white;
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.word-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.word-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(116, 185, 255, 0.3);
}

.word-item:hover::before {
  left: 100%;
}

/* 开始学习按钮 */
.start-learning {
  text-align: center;
  margin-top: 2rem;
}

.start-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
  border: none;
  padding: 1rem 3rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3);
  position: relative;
  overflow: hidden;
}

.start-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4);
}

.start-btn:hover::before {
  left: 100%;
}

.start-btn:active {
  transform: translateY(0);
}

.start-btn:disabled {
  background: #ddd;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 3rem;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error {
  background: rgba(255, 107, 107, 0.9);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin: 1rem 0;
  text-align: center;
  backdrop-filter: blur(10px);
}

.retry-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 1rem;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.empty-state .icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .word-selection {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
    margin-bottom: 1.5rem;
  }
  
  .user-info,
  .goal-selection,
  .word-preview {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .word-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 0.8rem;
  }
  
  .start-btn {
    padding: 0.8rem 2rem;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .word-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .word-item {
    padding: 0.8rem;
    font-size: 0.9rem;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .user-info,
  .goal-selection,
  .word-preview {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .user-info h3,
  .goal-selection h3,
  .word-preview h3 {
    color: #f0f0f0;
  }
  
  .user-info p {
    color: #b0b0b0;
  }
  
  .goal-select {
    background: #2a2a2a;
    color: #e0e0e0;
    border-color: #444;
  }
  
  .goal-select:focus {
    border-color: #667eea;
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .word-selection {
    background: #000;
  }
  
  .user-info,
  .goal-selection,
  .word-preview {
    background: #fff;
    border: 2px solid #000;
  }
  
  .word-item {
    background: #000;
    color: #fff;
    border: 2px solid #fff;
  }
}

/* 焦点状态 */
.goal-select:focus,
.start-btn:focus,
.retry-btn:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .word-item,
  .start-btn,
  .retry-btn {
    min-height: 44px;
    min-width: 44px;
  }
  
  .word-item:hover,
  .start-btn:hover,
  .retry-btn:hover {
    transform: none;
  }
}
</style>

