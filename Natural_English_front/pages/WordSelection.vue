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
      
      <!-- 学习目标选择区域 -->
      <div class="config-section" v-if="!currentLearningGoal || learningGoals.length > 0">
        <h3>{{ currentLearningGoal ? '选择其他学习目标' : '选择学习目标' }}</h3>
        <div class="goal-selector">
          <select v-model="selectedGoalId" @change="loadGoalWords">
            <option value="">{{ currentLearningGoal ? '使用当前学习目标' : '请选择学习目标' }}</option>
            <option v-if="currentLearningGoal" :value="currentLearningGoal.id">
              {{ currentLearningGoal.name }} (当前目标)
            </option>
            <option v-for="goal in learningGoals.filter(g => !currentLearningGoal || g.id !== currentLearningGoal.id)" :key="goal.id" :value="goal.id">
              {{ goal.name }} ({{ goal.total_words }}词)
            </option>
          </select>
        </div>
        
        <!-- 提示信息 -->
        <div v-if="currentLearningGoal" class="alternative-goals">
          <p class="alternative-text">当前正在使用您的活跃学习目标，也可以选择其他目标进行练习</p>
        </div>
        <div v-else-if="learningGoals.length === 0" class="no-goals-hint">
          <p class="hint-text">您还没有创建任何学习目标，请先创建学习目标</p>
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
import { learningAPI, userAPI } from '../utils/api.js'

export default {
  name: 'EnhancedWordPractice',
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
      
      // 练习设置
      practiceMode: '', // 'meaning' 或 'pronunciation'
      wordsCount: 20,
      useSmartRecommendation: true,
      
      // 练习数据
      practiceWords: [],
      previewWords: [],
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
        this.learningGoals = response.results || response
        console.log('所有学习目标:', this.learningGoals)
        this.retryCount = 0
      } catch (error) {
        console.error('加载学习目标失败:', error)
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
/* 主容器 */
.enhanced-word-practice-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 顶部导航栏 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  color: #333;
  font-size: 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn, .settings-btn {
  padding: 8px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.back-btn:hover, .settings-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: scale(1.1);
}

.arrow {
  font-size: 20px;
  color: #667eea;
}

.title {
  font-weight: 600;
  font-size: 18px;
  color: #333;
}

.settings-icon {
  font-size: 18px;
}

/* 练习配置界面 */
.practice-config {
  flex: 1;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

/* 用户信息卡片 */
.user-info-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #007bff;
  margin-bottom: 20px;
}

.user-info-card p {
  margin: 5px 0;
  color: #495057;
}

/* 学习目标卡片 */
.goal-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.goal-card h4 {
  margin: 0 0 10px 0;
  font-size: 1.3em;
  font-weight: 600;
}

.goal-card p {
  margin: 8px 0;
  opacity: 0.9;
}

/* 替代选择提示 */
.alternative-goals {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e9ecef;
}

.alternative-text {
  color: #6c757d;
  font-size: 0.9em;
  margin: 0;
  font-style: italic;
}

/* 无学习目标提示 */
.no-goals-hint {
  margin-top: 15px;
  padding: 15px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  text-align: center;
}

.hint-text {
  color: #856404;
  font-size: 0.9em;
  margin: 0;
  font-weight: 500;
}

.config-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 0;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.config-section h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  display: none;
}

.goal-selector select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  font-size: 16px;
  background: white;
  transition: all 0.3s ease;
}

.goal-selector select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 模式选择器 */
.mode-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.mode-option {
  padding: 20px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  background: white;
}

.mode-option:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.mode-option.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.mode-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.mode-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.mode-desc {
  font-size: 14px;
  opacity: 0.8;
}

/* 练习设置 */
.practice-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.setting-item label {
  font-weight: 500;
  min-width: 80px;
}

.setting-item select {
  padding: 8px 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  background: white;
}

.setting-desc {
  font-size: 14px;
  color: #666;
  margin-left: 8px;
}

/* 单词练习列表样式 */
.word-practice-list {
  background: #4CAF50;
  color: white;
  min-height: 600px;
}

.practice-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: #4CAF50;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.back-arrow {
  font-size: 24px;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.back-arrow:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.practice-title {
  font-size: 18px;
  font-weight: 600;
  flex: 1;
  text-align: center;
}

.save-btn {
  font-size: 16px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.save-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.word-list-container {
  padding: 20px;
  max-height: 450px;
  overflow-y: auto;
}

.word-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.1);
  margin-bottom: 8px;
  border-radius: 8px;
}

.word-item:last-child {
  margin-bottom: 0;
}

.word-content {
  flex: 1;
  font-size: 18px;
  font-weight: 500;
  color: white;
}

.word-actions {
  display: flex;
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.action-btn:hover {
  background-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.05);
}

.action-btn.active {
  background-color: #2E7D32;
  transform: scale(1.1);
}

.practice-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: center;
  align-items: center;
}

.progress-info {
  display: flex;
  justify-content: center;
}

.progress-text {
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

/* 练习界面 */
.practice-interface {
  flex: 1;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

/* 进度条 */
.progress-bar {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50px;
  padding: 8px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.progress-fill {
  height: 8px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 50px;
  transition: width 0.5s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

/* 单词练习区域 */
.word-practice-area {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 24px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.current-word {
  width: 100%;
}

.word-display {
  margin-bottom: 32px;
}

.word-text {
  font-size: 48px;
  font-weight: 700;
  color: #333;
  margin: 0 0 16px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.audio-controls {
  margin-top: 16px;
}

.play-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.play-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.question {
  font-size: 20px;
  color: #333;
  margin-bottom: 24px;
  font-weight: 500;
}

.answer-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 24px;
}

.know-btn, .unknown-btn, .correct-btn, .incorrect-btn {
  padding: 16px 32px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.know-btn, .correct-btn {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.unknown-btn, .incorrect-btn {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
}

.know-btn:hover, .correct-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
}

.unknown-btn:hover, .incorrect-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(244, 67, 54, 0.4);
}

.word-meaning, .word-info {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.next-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 16px;
  transition: all 0.3s ease;
}

.next-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 练习统计 */
.practice-stats {
  display: flex;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.stat-value.correct {
  color: #4CAF50;
}

.stat-value.incorrect {
  color: #f44336;
}

/* 练习完成界面 */
.practice-completed {
  flex: 1;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.completion-header {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.completion-header h2 {
  font-size: 32px;
  margin: 0 0 24px 0;
  color: #333;
}

.completion-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.stat-card {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.stat-number.correct {
  color: #4CAF50;
}

.stat-number.incorrect {
  color: #f44336;
}

/* 详细报告 */
.detailed-report {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.detailed-report h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
}

.report-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 12px 20px;
  border: 2px solid #e1e5e9;
  background: white;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tab-btn.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: transparent;
}

.word-list {
  max-height: 300px;
  overflow-y: auto;
}

.word-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.word-item.mastered {
  background: rgba(76, 175, 80, 0.1);
  border-left: 4px solid #4CAF50;
}

.word-item.review {
  background: rgba(244, 67, 54, 0.1);
  border-left: 4px solid #f44336;
}

.word-item .word {
  font-weight: 600;
  color: #333;
}

.word-item .meaning {
  color: #666;
  font-size: 14px;
}

/* 完成操作按钮 */
.completion-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 14px 28px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.action-btn.secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn.primary:hover {
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

/* 设置弹窗 */
.settings-modal {
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
  backdrop-filter: blur(5px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.modal-body {
  padding: 24px;
}

.setting-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.setting-group label {
  font-weight: 500;
  min-width: 80px;
}

.setting-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .practice-config {
    padding: 16px;
  }
  
  .config-section {
    padding: 20px;
  }
  
  .mode-selector {
    grid-template-columns: 1fr;
  }
  
  .word-text {
    font-size: 36px;
  }
  
  .answer-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .completion-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .completion-actions {
    flex-direction: column;
  }
  
  .practice-stats {
    flex-direction: column;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 12px 16px;
  }
  
  .title {
    font-size: 16px;
  }
  
  .word-practice-area {
    padding: 24px 16px;
  }
  
  .word-text {
    font-size: 28px;
  }
  
  .completion-stats {
    grid-template-columns: 1fr;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.config-section, .practice-interface > *, .practice-completed > * {
  animation: fadeInUp 0.6s ease-out;
}

/* 加载状态 */
.loading {
  opacity: 0.6;
  pointer-events: none;
}
</style>