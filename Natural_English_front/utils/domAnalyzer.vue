<template>
  <div class="word-selection-practice">
    <!-- 游戏化头部信息 -->
    <div class="game-header">
      <div class="user-info">
        <div class="avatar">{{ gameState.avatar || '🎓' }}</div>
        <div class="user-details">
          <div class="username">{{ gameState.username || '学习者' }}</div>
          <div class="level">Lv.{{ gameState.level }}</div>
        </div>
      </div>
      
      <div class="session-stats">
        <div class="stat-item">
          <span class="stat-icon">⭐</span>
          <span class="stat-value">{{ gameState.experience }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">💰</span>
          <span class="stat-value">{{ gameState.coins }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🔥</span>
          <span class="stat-value">{{ sessionStats.currentStreak }}</span>
        </div>
      </div>
      
      <div class="mode-selector">
        <select v-model="currentMode" @change="switchMode">
          <option value="quick-brush">倒计时模式</option>
          <option value="spelling">拼写模式</option>
          <option value="competition">竞技模式</option>
        </select>
      </div>
    </div>
    
    <!-- 连击提示 -->
    <div v-if="showComboIndicator" class="combo-notification">
      {{ comboText }}
    </div>
    

    
    <!-- 倒计时模式 -->
    <div v-if="currentMode === 'quick-brush' && currentWord" class="quick-brush-mode">
      <div class="progress-section">
        <div class="progress-info">
          <span>进度: {{ currentIndex + 1 }}/{{ words.length }}</span>
          <span>正确率: {{ Math.round(accuracyRate) }}%</span>
          <span class="countdown-timer" :class="{ warning: countdownTime <= 2 }">⏰ {{ countdownTime }}秒</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <div class="countdown-bar">
          <div class="countdown-fill" :style="{ width: (countdownTime / 5) * 100 + '%' }"></div>
        </div>
      </div>
      
      <div class="word-card quick-style">
        <div class="word-display">
          <h2>{{ currentWord.word }}</h2>
          <p class="phonetic">{{ currentWord.phonetic }}</p>
          <button class="audio-btn" @click="playAudio">
            🔊
          </button>
        </div>
        
        <div class="options quick-options">
          <button 
            v-for="(option, index) in currentWord.options" 
            :key="index"
            class="option-btn quick-btn"
            :class="{ 
              selected: selectedOption === index,
              correct: showResult && index === currentWord.correctIndex,
              incorrect: showResult && selectedOption === index && index !== currentWord.correctIndex
            }"
            @click="quickSelectOption(index)"
            :disabled="showResult"
          >
            {{ option }}
          </button>
        </div>
        
        <div v-if="showResult" class="result quick-result">
          <div class="result-header" :class="isCorrect ? 'correct' : 'incorrect'">
            <span class="result-icon">{{ isCorrect ? '🎉' : '❌' }}</span>
            <span class="result-text">{{ isCorrect ? '正确！' : '错误！' }}</span>
            <span v-if="isCorrect" class="exp-gained">+{{ lastExpGained }} EXP</span>
          </div>
          <p class="explanation">{{ currentWord.explanation }}</p>
        </div>
      </div>
    </div>
    
    <!-- 拼写模式 -->
    <div v-if="currentMode === 'spelling' && currentWord" class="spelling-mode">
      <DragDropSpelling 
        :word="currentWord.word"
        :phonetic="currentWord.phonetic"
        :meaning="currentWord.explanation"
        @result="handleSpellingResult"
      />
    </div>
    
    <!-- 竞技模式 -->
    <div v-if="currentMode === 'competition'" class="competition-mode">
      <SocialCompetition 
        :current-user="gameState"
        :game-state="gameState"
        @battle-end="handleBattleEnd"
        @create-team="handleCreateTeam"
        @join-team="handleJoinTeam"
        @leave-team="handleLeaveTeam"
        @start-team-challenge="handleTeamChallenge"
        @invite-members="handleInviteMembers"
        @join-event="handleJoinEvent"
      />
    </div>
    
    <!-- 练习完成界面 -->
    <div v-if="(currentMode === 'quick-brush' || currentMode === 'spelling') && !currentWord" class="completion">
      <div class="completion-header">
        <h2>🎉 练习完成！</h2>
        <div class="final-stats">
          <div class="stat-card">
            <div class="stat-value">{{ Math.round(accuracyRate) }}%</div>
            <div class="stat-label">正确率</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ sessionStats.totalExpGained }}</div>
            <div class="stat-label">获得经验</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ sessionStats.maxStreak }}</div>
            <div class="stat-label">最高连击</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ sessionStats.coinsEarned }}</div>
            <div class="stat-label">获得金币</div>
          </div>
          <div v-if="currentMode === 'quick-brush'" class="stat-card">
            <div class="stat-value">{{ formatTime(elapsedTime) }}</div>
            <div class="stat-label">用时</div>
          </div>
        </div>
      </div>
      
      <!-- 新解锁的成就 -->
      <div v-if="newAchievements.length > 0" class="new-achievements">
        <h3>🏆 新获得的成就</h3>
        <div class="achievements-list">
          <div 
            v-for="achievement in newAchievements" 
            :key="achievement.id"
            class="achievement-item"
            :class="achievement.rarity"
          >
            <div class="achievement-icon">{{ achievement.icon }}</div>
            <div class="achievement-info">
              <div class="achievement-name">{{ achievement.name }}</div>
              <div class="achievement-desc">{{ achievement.description }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="completion-actions">
        <button class="btn btn-primary" @click="restart">
          重新开始
        </button>
        <button class="btn btn-secondary" @click="viewProgress">
          查看进度
        </button>
        <button class="btn btn-secondary" @click="switchMode('competition')">
          挑战其他玩家
        </button>
      </div>
    </div>
    
    <!-- 进度可视化弹窗 -->
    <div v-if="showProgressModal" class="modal-overlay" @click="closeProgressModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>学习进度</h3>
          <button class="close-btn" @click="closeProgressModal">×</button>
        </div>
        <ProgressVisualization 
          :game-state="gameState"
          :session-data="sessionStats"
        />
      </div>
    </div>
    
    <!-- 粒子效果 -->
    <ParticleEffect 
      v-if="showParticles"
      :type="particleType"
      :count="particleCount"
      @complete="hideParticles"
    />
  </div>
</template>

<script>
import { useGameState } from '../../composables/useGameState'
import ParticleEffect from '../../components/ParticleEffect.vue'
import DragDropSpelling from '../../components/DragDropSpelling.vue'
import SocialCompetition from '../../components/SocialCompetition.vue'
import ProgressVisualization from '../../components/ProgressVisualization.vue'

export default {
  name: 'WordSelectionPractice',
  components: {
    ParticleEffect,
    DragDropSpelling,
    SocialCompetition,
    ProgressVisualization
  },
  setup() {
    const {
      gameState,
      updateExperience,
      handleAnswer,
      startSession,
      endSession,
      unlockAchievement,
      purchaseItem
    } = useGameState()
    
    return {
      gameState,
      updateExperience,
      handleAnswer,
      startSession,
      endSession,
      unlockAchievement,
      purchaseItem
    }
  },
  data() {
    return {
      currentMode: this.getInitialMode(),
      currentIndex: 0,
      selectedOption: null,
      showResult: false,
      correctCount: 0,
      lastExpGained: 0,
      sessionStats: {
        currentStreak: 0,
        maxStreak: 0,
        comboMultiplier: 1,
        totalExpGained: 0,
        coinsEarned: 0,
        startTime: null,
        endTime: null
      },
      newAchievements: [],
      showProgressModal: false,
      showParticles: false,
      particleType: 'success',
      particleCount: 20,
      showComboIndicator: false,
      comboText: '',
      comboTimeout: null,
      autoNextTimeout: null,
      elapsedTime: 0,
      gameTimer: null,
      countdownTime: 5,
      countdownTimer: null,
      words: [
        {
          word: 'apple',
          phonetic: '/ˈæpəl/',
          options: ['苹果', '香蕉', '橙子', '葡萄'],
          correctIndex: 0,
          explanation: 'Apple是苹果的意思，是一种常见的水果。'
        },
        {
          word: 'book',
          phonetic: '/bʊk/',
          options: ['笔', '书', '桌子', '椅子'],
          correctIndex: 1,
          explanation: 'Book是书的意思，用于阅读和学习。'
        },
        {
          word: 'cat',
          phonetic: '/kæt/',
          options: ['狗', '鸟', '猫', '鱼'],
          correctIndex: 2,
          explanation: 'Cat是猫的意思，是一种常见的宠物。'
        },
        {
          word: 'dog',
          phonetic: '/dɔːɡ/',
          options: ['猫', '狗', '鸟', '鱼'],
          correctIndex: 1,
          explanation: 'Dog是狗的意思，是人类最忠实的朋友。'
        },
        {
          word: 'house',
          phonetic: '/haʊs/',
          options: ['房子', '汽车', '学校', '医院'],
          correctIndex: 0,
          explanation: 'House是房子的意思，是人们居住的地方。'
        },
        {
          word: 'water',
          phonetic: '/ˈwɔːtər/',
          options: ['火', '水', '土', '空气'],
          correctIndex: 1,
          explanation: 'Water是水的意思，是生命必需的物质。'
        },
        {
          word: 'friend',
          phonetic: '/frend/',
          options: ['敌人', '朋友', '陌生人', '老师'],
          correctIndex: 1,
          explanation: 'Friend是朋友的意思，指亲密的伙伴。'
        },
        {
          word: 'school',
          phonetic: '/skuːl/',
          options: ['医院', '商店', '学校', '公园'],
          correctIndex: 2,
          explanation: 'School是学校的意思，是学习知识的地方。'
        }
      ]
    }
  },
  computed: {
    currentWord() {
      return this.words[this.currentIndex] || null
    },
    progressPercentage() {
      return (this.currentIndex / this.words.length) * 100
    },
    accuracyRate() {
      const totalAnswered = this.currentIndex + (this.showResult ? 1 : 0)
      return totalAnswered > 0 ? (this.correctCount / totalAnswered) * 100 : 0
    },
    isCorrect() {
      return this.selectedOption === this.currentWord?.correctIndex
    }
  },
  mounted() {
    this.initializeSession()
  },
  
  beforeUnmount() {
    // 组件销毁前清理所有定时器
    this.cleanupCurrentMode()
  },
  methods: {
    getInitialMode() {
      // 从路由路径获取模式
      const path = this.$route?.path || window.location.pathname
      if (path === '/competition') {
        return 'competition'
      } else if (path === '/quick-brush') {
        return 'quick-brush'
      }
      
      // 兼容旧的查询参数方式
      const urlParams = new URLSearchParams(window.location.search)
      const mode = urlParams.get('mode')
      if (mode && ['quick-brush', 'spelling', 'competition'].includes(mode)) {
        return mode
      }
      return 'quick-brush' // 默认模式
    },
    
    initializeSession() {
      this.sessionStats.startTime = new Date()
      this.startSession()
      
      // 只有非竞技模式才需要单词数据
      if (this.currentMode !== 'competition') {
        // 随机打乱单词顺序
        this.shuffleWords()
        
        // 如果是倒计时模式，启动计时器和倒计时
        if (this.currentMode === 'quick-brush') {
          this.startTimer()
          this.startCountdown()
        }
      }
    },
    
    shuffleWords() {
      for (let i = this.words.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[this.words[i], this.words[j]] = [this.words[j], this.words[i]]
      }
    },
    
    switchMode(mode) {
      // 清理当前模式的定时器
      this.cleanupCurrentMode()
      
      if (typeof mode === 'string') {
        this.currentMode = mode
      } else {
        // 处理select change事件
        this.currentMode = mode.target ? mode.target.value : mode
      }
      
      // 根据新模式初始化
      if (this.currentMode === 'quick-brush') {
        this.resetQuickBrushMode()
      } else if (this.currentMode === 'spelling') {
        this.resetSpellingMode()
      } else if (this.currentMode === 'competition') {
        this.resetCompetitionMode()
      }
    },
    
    cleanupCurrentMode() {
      // 清理所有定时器
      this.stopTimer()
      this.stopCountdown()
      if (this.autoNextTimeout) {
        clearTimeout(this.autoNextTimeout)
        this.autoNextTimeout = null
      }
    },
    
    resetSpellingMode() {
      this.currentIndex = 0
      this.selectedOption = null
      this.showResult = false
      this.shuffleWords()
    },
    
    resetCompetitionMode() {
      // 竞技模式不需要单词数据，重置为初始状态
      this.currentIndex = 0
      this.selectedOption = null
      this.showResult = false
      // 不调用shuffleWords，因为竞技模式使用SocialCompetition组件
    },
    
    resetQuickBrushMode() {
      this.currentIndex = 0
      this.selectedOption = null
      this.showResult = false
      this.elapsedTime = 0
      this.shuffleWords()
      this.startTimer()
      this.startCountdown()
    },
    
    startTimer() {
      if (this.gameTimer) {
        clearInterval(this.gameTimer)
      }
      this.gameTimer = setInterval(() => {
        this.elapsedTime++
      }, 1000)
    },
    
    stopTimer() {
      if (this.gameTimer) {
        clearInterval(this.gameTimer)
        this.gameTimer = null
      }
    },
    
    startCountdown() {
      this.countdownTime = 5
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
      }
      this.countdownTimer = setInterval(() => {
        this.countdownTime--
        if (this.countdownTime <= 0) {
          this.stopCountdown()
          // 时间到，自动选择错误答案或跳过
          if (!this.showResult) {
            this.handleTimeUp()
          }
        }
      }, 1000)
    },
    
    stopCountdown() {
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }
    },
    
    handleTimeUp() {
      // 时间到，标记为错误答案
      this.selectedOption = -1 // 使用-1表示超时
      this.showResult = true
      this.handleIncorrectAnswerLogic()
      
      // 0.5秒后自动跳转到下一题
      this.autoNextTimeout = setTimeout(() => {
        this.nextWord()
      }, 500)
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    
    quickSelectOption(index) {
      if (!this.showResult) {
        this.selectedOption = index
        this.stopCountdown() // 停止倒计时
        this.quickCheckAnswer()
      }
    },
    
    quickCheckAnswer() {
      this.showResult = true
      
      if (this.isCorrect) {
        this.handleCorrectAnswerLogic()
      } else {
        this.handleIncorrectAnswerLogic()
      }
      
      // 快刷模式：0.5秒后自动跳转到下一题
      this.autoNextTimeout = setTimeout(() => {
        this.nextWord()
      }, 500)
    },
    
    selectOption(index) {
      if (!this.showResult) {
        this.selectedOption = index
      }
    },
    
    playAudio() {
      // 实现音频播放功能
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(this.currentWord.word)
        utterance.lang = 'en-US'
        utterance.rate = 0.8
        speechSynthesis.speak(utterance)
      }
    },
    
    checkAnswer() {
      this.showResult = true
      
      if (this.isCorrect) {
        this.handleCorrectAnswerLogic()
      } else {
        this.handleIncorrectAnswerLogic()
      }
      
      // 1秒后自动跳转到下一题
      this.autoNextTimeout = setTimeout(() => {
        this.nextWord()
      }, 1000)
    },
    
    handleCorrectAnswerLogic() {
      this.correctCount++
      this.sessionStats.currentStreak++
      this.sessionStats.maxStreak = Math.max(this.sessionStats.maxStreak, this.sessionStats.currentStreak)
      
      // 计算经验值奖励
      const baseExp = 10
      const streakBonus = Math.floor(this.sessionStats.currentStreak / 5) * 5
      const difficultyBonus = this.currentIndex < 3 ? 0 : 5 // 后面的题目更难
      this.lastExpGained = baseExp + streakBonus + difficultyBonus
      
      // 更新游戏状态
      this.updateExperience(this.lastExpGained)
      this.handleAnswer(true) // 使用正确的方法名
      
      this.sessionStats.totalExpGained += this.lastExpGained
      this.sessionStats.coinsEarned += Math.floor(this.lastExpGained / 2)
      
      // 显示粒子效果
      this.showParticleEffect('success')
      
      // 显示连击提示
      this.showComboNotification()
      
      // 检查连击成就
      this.checkStreakAchievements()
      
      // 更新连击倍数
      this.updateComboMultiplier()
      
      // 显示连击通知
      this.showComboNotification()
    },
    
    handleIncorrectAnswerLogic() {
      this.sessionStats.currentStreak = 0
      this.sessionStats.comboMultiplier = 1
      this.handleAnswer(false) // 使用正确的方法名
      this.lastExpGained = 0
    },
    
    updateComboMultiplier() {
      if (this.sessionStats.currentStreak >= 10) {
        this.sessionStats.comboMultiplier = 3
      } else if (this.sessionStats.currentStreak >= 5) {
        this.sessionStats.comboMultiplier = 2
      } else {
        this.sessionStats.comboMultiplier = 1
      }
    },
    
    showComboNotification() {
      const streak = this.sessionStats.currentStreak
      if (streak >= 3) {
        this.comboText = `🔥 ${streak}连击！`
        if (streak >= 10) {
          this.comboText = `⚡ 超级连击 ${streak}！`
        } else if (streak >= 5) {
          this.comboText = `🌟 连击王 ${streak}！`
        }
        
        this.showComboIndicator = true
        
        // 清除之前的定时器
        if (this.comboTimeout) {
          clearTimeout(this.comboTimeout)
        }
        
        // 2秒后隐藏连击通知
        this.comboTimeout = setTimeout(() => {
          this.showComboIndicator = false
        }, 2000)
      }
    },
    
    checkStreakAchievements() {
      const streak = this.sessionStats.currentStreak
      
      if (streak === 5) {
        this.unlockNewAchievement('first_streak', '连击新手', '首次达成5连击', '🔥', 'common')
      } else if (streak === 10) {
        this.unlockNewAchievement('streak_master', '连击大师', '达成10连击', '⚡', 'rare')
      } else if (streak === 20) {
        this.unlockNewAchievement('streak_legend', '连击传说', '达成20连击', '🌟', 'epic')
      }
    },
    
    unlockNewAchievement(id, name, description, icon, rarity) {
      const achievement = {
        id,
        name,
        description,
        icon,
        rarity,
        unlockedAt: new Date().toISOString()
      }
      
      this.newAchievements.push(achievement)
      this.unlockAchievement(id, achievement)
      
      // 显示成就粒子效果
      this.showParticleEffect('achievement', 30)
    },
    
    showParticleEffect(type, count = 20) {
      this.particleType = type
      this.particleCount = count
      this.showParticles = true
    },
    
    hideParticles() {
      this.showParticles = false
    },
    
    showComboNotification() {
      if (this.sessionStats.currentStreak >= 2) {
        this.comboText = `${this.sessionStats.currentStreak}连击！`
        this.showComboIndicator = true
        
        // 清除之前的定时器
        if (this.comboTimeout) {
          clearTimeout(this.comboTimeout)
        }
        
        // 2秒后隐藏连击提示
        this.comboTimeout = setTimeout(() => {
          this.showComboIndicator = false
        }, 2000)
      }
    },
    
    nextWord() {
      // 清除自动跳转定时器
      if (this.autoNextTimeout) {
        clearTimeout(this.autoNextTimeout)
        this.autoNextTimeout = null
      }
      
      if (this.currentIndex < this.words.length - 1) {
        this.currentIndex++
        this.selectedOption = null
        this.showResult = false
        // 如果是倒计时模式，重新启动倒计时
        if (this.currentMode === 'quick-brush') {
          this.startCountdown()
        }
      } else {
        // 练习完成
        this.completeSession()
      }
    },
    
    previousWord() {
      // 清除自动跳转定时器
      if (this.autoNextTimeout) {
        clearTimeout(this.autoNextTimeout)
        this.autoNextTimeout = null
      }
      
      if (this.currentIndex > 0) {
        this.currentIndex--
        this.selectedOption = null
        this.showResult = false
      }
    },
    
    completeSession() {
      this.sessionStats.endTime = new Date()
      this.endSession(this.sessionStats)
      
      // 如果是倒计时模式，停止计时器和倒计时
      if (this.currentMode === 'quick-brush') {
        this.stopTimer()
        this.stopCountdown()
      }
      
      // 检查完成成就
      this.checkCompletionAchievements()
      
      // 设置当前单词为null以显示完成界面
      this.currentIndex = this.words.length
    },
    
    checkCompletionAchievements() {
      const accuracy = this.accuracyRate
      
      if (accuracy === 100) {
        this.unlockNewAchievement('perfect_score', '完美表现', '获得100%正确率', '🏆', 'legendary')
      } else if (accuracy >= 90) {
        this.unlockNewAchievement('excellent_score', '优秀表现', '获得90%以上正确率', '⭐', 'epic')
      } else if (accuracy >= 80) {
        this.unlockNewAchievement('good_score', '良好表现', '获得80%以上正确率', '👍', 'rare')
      }
      
      if (this.sessionStats.maxStreak >= 15) {
        this.unlockNewAchievement('streak_champion', '连击冠军', '单次会话最高连击15+', '🏅', 'epic')
      }
    },
    
    restart() {
      this.currentIndex = 0
      this.selectedOption = null
      this.showResult = false
      this.correctCount = 0
      this.newAchievements = []
      this.elapsedTime = 0
      
      // 重置会话统计
      this.sessionStats = {
        currentStreak: 0,
        maxStreak: 0,
        comboMultiplier: 1,
        totalExpGained: 0,
        coinsEarned: 0,
        startTime: new Date(),
        endTime: null
      }
      
      this.shuffleWords()
      this.startSession()
      
      // 如果是倒计时模式，重新启动计时器和倒计时
      if (this.currentMode === 'quick-brush') {
        this.startTimer()
        this.startCountdown()
      }
    },
    
    viewProgress() {
      this.showProgressModal = true
    },
    
    closeProgressModal() {
      this.showProgressModal = false
    },
    
    // 拼写模式处理
    handleSpellingResult(result) {
      if (result.isCorrect) {
        this.handleCorrectAnswerLogic()
      } else {
        this.handleIncorrectAnswerLogic()
      }
      
      // 自动进入下一题
      setTimeout(() => {
        this.nextWord()
      }, 2000)
    },
    
    // 社交竞争事件处理
    handleBattleEnd(result) {
      console.log('Battle ended:', result)
      // 处理对战结束逻辑
    },
    
    handleCreateTeam() {
      console.log('Create team requested')
      // 处理创建团队逻辑
    },
    
    handleJoinTeam(team) {
      console.log('Join team requested:', team)
      // 处理加入团队逻辑
    },
    
    handleLeaveTeam() {
      console.log('Leave team requested')
      // 处理离开团队逻辑
    },
    
    handleTeamChallenge() {
      console.log('Team challenge requested')
      // 处理团队挑战逻辑
    },
    
    handleInviteMembers() {
      console.log('Invite members requested')
      // 处理邀请成员逻辑
    },
    
    handleJoinEvent(event) {
      console.log('Join event requested:', event)
      // 处理参加活动逻辑
    }
  },
  
  beforeUnmount() {
    // 清理定时器
    if (this.comboTimeout) {
      clearTimeout(this.comboTimeout)
    }
    if (this.autoNextTimeout) {
      clearTimeout(this.autoNextTimeout)
    }
    if (this.gameTimer) {
      clearInterval(this.gameTimer)
    }
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }
  }
}
</script>

<style scoped>
.word-selection-practice {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow-x: hidden;
}

/* 游戏化头部样式 */
.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 20px;
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  font-size: 16px;
}

.level {
  font-size: 14px;
  opacity: 0.8;
}

.session-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.stat-icon {
  font-size: 16px;
}

.mode-selector select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
}

.mode-selector select option {
  background: #333;
  color: white;
}

/* 连击指示器样式 */
.combo-indicator {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  pointer-events: none;
}

/* 连击提示样式 */
.combo-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #ff6b6b, #ffa500);
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
  z-index: 1001;
  animation: comboSlideIn 0.3s ease-out, comboSlideOut 0.3s ease-in 1.7s;
  pointer-events: none;
}

@keyframes comboSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes comboSlideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* 选择题模式样式 */
.selection-mode {
  max-width: 600px;
  margin: 0 auto;
}

.progress-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  color: white;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.5s ease;
  border-radius: 4px;
}

.word-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 20px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.word-card:hover {
  transform: translateY(-4px);
}

.word-display {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
}

.word-display h2 {
  font-size: 42px;
  color: #333;
  margin-bottom: 12px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.phonetic {
  font-size: 20px;
  color: #666;
  font-style: italic;
  margin-bottom: 16px;
}

.audio-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  font-size: 24px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.audio-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.options {
  margin-bottom: 32px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.option-btn {
  padding: 20px 24px;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 500;
  background: white;
  text-align: center;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-btn:hover:not(:disabled) {
  border-color: #667eea;
  background: linear-gradient(135deg, #f8f9ff, #f0f4ff);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.option-btn.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #ffffff !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  font-weight: 600;
}

.option-btn.correct {
  border-color: #4CAF50;
  background: linear-gradient(135deg, #4CAF50, #66BB6A);
  color: #ffffff !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  font-weight: 600;
  animation: correctPulse 0.6s ease;
}

.option-btn.incorrect {
  border-color: #f44336;
  background: linear-gradient(135deg, #f44336, #EF5350);
  color: #ffffff !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  font-weight: 600;
  animation: incorrectShake 0.6s ease;
}

@keyframes correctPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes incorrectShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 结果显示样式 */
.result {
  margin: 24px 0;
  padding: 20px;
  border-radius: 16px;
  text-align: center;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.result-header.correct {
  color: #4CAF50;
}

.result-header.incorrect {
  color: #f44336;
}

.result-icon {
  font-size: 24px;
}

.exp-gained {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.explanation {
  color: #666;
  font-size: 16px;
  line-height: 1.5;
  margin: 0;
}

/* 操作按钮样式 */
.actions {
  text-align: center;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.btn {
  padding: 14px 32px;
  border: none;
  border-radius: 28px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  color: #495057;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* 完成界面样式 */
.completion {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.completion-header {
  background: white;
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.completion-header h2 {
  font-size: 32px;
  color: #333;
  margin-bottom: 32px;
  font-weight: 700;
}

.final-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #f8f9ff, #f0f4ff);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid #e0e6ff;
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-card .stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 成就展示样式 */
.new-achievements {
  background: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.new-achievements h3 {
  font-size: 24px;
  color: #333;
  margin-bottom: 24px;
  font-weight: 600;
}

.achievements-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.achievement-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid;
  animation: achievementUnlock 0.8s ease;
}

.achievement-item.common {
  border-color: #9E9E9E;
  background: linear-gradient(135deg, #f5f5f5, #eeeeee);
}

.achievement-item.rare {
  border-color: #2196F3;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
}

.achievement-item.epic {
  border-color: #9C27B0;
  background: linear-gradient(135deg, #f3e5f5, #e1bee7);
}

.achievement-item.legendary {
  border-color: #FF9800;
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
}

.achievement-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.achievement-info {
  flex: 1;
  text-align: left;
}

.achievement-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.achievement-desc {
  font-size: 14px;
  color: #666;
}

@keyframes achievementUnlock {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.completion-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  font-size: 24px;
  color: #333;
  margin: 0;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

/* 快刷模式样式 */
.quick-brush-mode {
  max-width: 600px;
  margin: 0 auto;
}

.quick-brush-mode .word-card.quick-style {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 15px;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  transition: all 0.2s ease;
}

.quick-brush-mode .word-display h2 {
  color: white;
  font-size: 2.2rem;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.quick-brush-mode .phonetic {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  margin-bottom: 15px;
}

.quick-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 20px;
}

.option-btn.quick-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  backdrop-filter: blur(10px);
}

.option-btn.quick-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.option-btn.quick-btn.selected {
  background: rgba(255, 255, 255, 0.4);
  border-color: white;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
}

.option-btn.quick-btn.correct {
  background: rgba(76, 175, 80, 0.8);
  border-color: #4CAF50;
  animation: correctPulse 0.3s ease;
}

.option-btn.quick-btn.incorrect {
  background: rgba(244, 67, 54, 0.8);
  border-color: #f44336;
  animation: incorrectShake 0.3s ease;
}

.quick-result {
  margin-top: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
}

.timer {
   color: #ff6b6b;
   font-weight: bold;
   font-size: 1.1rem;
 }
 
 .countdown-timer {
   color: #4CAF50;
   font-weight: bold;
   font-size: 1.2rem;
   transition: color 0.3s ease;
 }
 
 .countdown-timer.warning {
   color: #ff6b6b;
   animation: pulse 1s infinite;
 }
 
 .countdown-bar {
   width: 100%;
   height: 6px;
   background: rgba(255, 255, 255, 0.2);
   border-radius: 3px;
   margin-top: 8px;
   overflow: hidden;
 }
 
 .countdown-fill {
   height: 100%;
   background: linear-gradient(90deg, #4CAF50, #8BC34A);
   border-radius: 3px;
   transition: width 1s linear;
 }
 
 .countdown-timer.warning + .progress-bar + .countdown-bar .countdown-fill {
   background: linear-gradient(90deg, #ff6b6b, #ff8a80);
 }
 
 @keyframes pulse {
   0% { opacity: 1; }
   50% { opacity: 0.5; }
   100% { opacity: 1; }
 }
 
 @keyframes correctPulse {
   0% { transform: scale(1); }
   50% { transform: scale(1.05); }
   100% { transform: scale(1); }
 }
 
 @keyframes incorrectShake {
   0%, 100% { transform: translateX(0); }
   25% { transform: translateX(-5px); }
   75% { transform: translateX(5px); }
 }

/* 拼写模式样式 */
.spelling-mode {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.spelling-mode:hover {
  transform: translateY(-4px);
}

/* 连击通知样式 */
.combo-notification {
  position: fixed;
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 18px;
  font-weight: 600;
  z-index: 1000;
  animation: comboSlideIn 0.5s ease;
  box-shadow: 0 8px 24px rgba(255, 107, 107, 0.3);
}

@keyframes comboSlideIn {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .session-stats {
    justify-content: center;
  }
  
  .options {
    grid-template-columns: 1fr;
  }
  
  .final-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .completion-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .completion-actions .btn {
    width: 100%;
    max-width: 300px;
  }
  
  .spelling-mode {
    margin: 0 10px;
    padding: 20px;
  }
  
  .combo-notification {
    font-size: 16px;
    padding: 10px 20px;
  }
}
</style>