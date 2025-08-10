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
          <option value="selection">选择题模式</option>
          <option value="spelling">拼写模式</option>
          <option value="competition">竞技模式</option>
        </select>
      </div>
    </div>
    
    <!-- 连击指示器 -->
    <ComboIndicator 
      v-if="sessionStats.currentStreak > 1"
      :combo="sessionStats.currentStreak"
      :multiplier="sessionStats.comboMultiplier"
      class="combo-indicator"
    />
    
    <!-- 选择题模式 -->
    <div v-if="currentMode === 'selection' && currentWord" class="selection-mode">
      <div class="progress-section">
        <div class="progress-info">
          <span>进度: {{ currentIndex + 1 }}/{{ words.length }}</span>
          <span>正确率: {{ Math.round(accuracyRate) }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
      </div>
      
      <div class="word-card">
        <div class="word-display">
          <h2>{{ currentWord.word }}</h2>
          <p class="phonetic">{{ currentWord.phonetic }}</p>
          <button class="audio-btn" @click="playAudio">
            🔊
          </button>
        </div>
        
        <div class="options">
          <button 
            v-for="(option, index) in currentWord.options" 
            :key="index"
            class="option-btn"
            :class="{ 
              selected: selectedOption === index,
              correct: showResult && index === currentWord.correctIndex,
              incorrect: showResult && selectedOption === index && index !== currentWord.correctIndex
            }"
            @click="selectOption(index)"
            :disabled="showResult"
          >
            {{ option }}
          </button>
        </div>
        
        <div v-if="showResult" class="result">
          <div class="result-header" :class="isCorrect ? 'correct' : 'incorrect'">
            <span class="result-icon">{{ isCorrect ? '🎉' : '❌' }}</span>
            <span class="result-text">{{ isCorrect ? '正确！' : '错误！' }}</span>
            <span v-if="isCorrect" class="exp-gained">+{{ lastExpGained }} EXP</span>
          </div>
          <p class="explanation">{{ currentWord.explanation }}</p>
        </div>
        
        <div class="actions">
          <button 
            v-if="!showResult" 
            class="btn btn-primary" 
            @click="checkAnswer"
            :disabled="selectedOption === null"
          >
            检查答案
          </button>
          <button 
            v-else 
            class="btn btn-primary" 
            @click="nextWord"
          >
            {{ currentIndex < words.length - 1 ? '下一题' : '完成练习' }}
          </button>
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
    <div v-if="currentMode === 'selection' && !currentWord" class="completion">
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
import { useGameState } from '../../composables/useGameState.js'
import ComboIndicator from '../../components/ComboIndicator.vue'
import ParticleEffect from '../../components/ParticleEffect.vue'
import DragDropSpelling from '../../components/DragDropSpelling.vue'
import SocialCompetition from '../../components/SocialCompetition.vue'
import ProgressVisualization from '../../components/ProgressVisualization.vue'

export default {
  name: 'WordSelectionPractice',
  components: {
    ComboIndicator,
    ParticleEffect,
    DragDropSpelling,
    SocialCompetition,
    ProgressVisualization
  },
  setup() {
    const {
      gameState,
      updateExperience,
      handleCorrectAnswer,
      handleIncorrectAnswer,
      startSession,
      endSession,
      unlockAchievement,
      purchaseItem
    } = useGameState()
    
    return {
      gameState,
      updateExperience,
      handleCorrectAnswer,
      handleIncorrectAnswer,
      startSession,
      endSession,
      unlockAchievement,
      purchaseItem
    }
  },
  data() {
    return {
      currentMode: 'selection',
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
      if (this.currentMode !== 'selection') return null
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
  methods: {
    initializeSession() {
      this.sessionStats.startTime = new Date()
      this.startSession()
      
      // 随机打乱单词顺序
      this.shuffleWords()
    },
    
    shuffleWords() {
      for (let i = this.words.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[this.words[i], this.words[j]] = [this.words[j], this.words[i]]
      }
    },
    
    switchMode(mode) {
      if (typeof mode === 'string') {
        this.currentMode = mode
      } else {
        // 处理select change事件
        this.currentMode = mode.target ? mode.target.value : mode
      }
      
      if (this.currentMode === 'selection') {
        this.resetSelectionMode()
      }
    },
    
    resetSelectionMode() {
      this.currentIndex = 0
      this.selectedOption = null
      this.showResult = false
      this.shuffleWords()
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
      this.handleCorrectAnswer(this.currentWord.word, this.lastExpGained)
      
      this.sessionStats.totalExpGained += this.lastExpGained
      this.sessionStats.coinsEarned += Math.floor(this.lastExpGained / 2)
      
      // 显示粒子效果
      this.showParticleEffect('success')
      
      // 检查连击成就
      this.checkStreakAchievements()
      
      // 更新连击倍数
      this.updateComboMultiplier()
    },
    
    handleIncorrectAnswerLogic() {
      this.sessionStats.currentStreak = 0
      this.sessionStats.comboMultiplier = 1
      this.handleIncorrectAnswer(this.currentWord.word)
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
    
    nextWord() {
      if (this.currentIndex < this.words.length - 1) {
        this.currentIndex++
        this.selectedOption = null
        this.showResult = false
      } else {
        // 练习完成
        this.completeSession()
      }
    },
    
    completeSession() {
      this.sessionStats.endTime = new Date()
      this.endSession(this.sessionStats)
      
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
  }
}
</script>

<style scoped>
.word-selection-practice {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 28px;
  margin-bottom: 8px;
}

.header p {
  font-size: 16px;
  opacity: 0.9;
}

.practice-area {
  max-width: 500px;
  margin: 0 auto;
}

.word-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.word-display {
  text-align: center;
  margin-bottom: 30px;
}

.word-display h2 {
  font-size: 36px;
  color: #333;
  margin-bottom: 8px;
}

.phonetic {
  font-size: 18px;
  color: #666;
  font-style: italic;
}

.options {
  margin-bottom: 30px;
}

.option-item {
  padding: 15px 20px;
  margin-bottom: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.option-item:hover {
  border-color: #007aff;
  background: #f0f8ff;
}

.option-item.selected {
  border-color: #007aff;
  background: #007aff;
  color: white;
}

.option-item.correct {
  border-color: #4CAF50;
  background: #4CAF50;
  color: white;
}

.option-item.wrong {
  border-color: #f44336;
  background: #f44336;
  color: white;
}

.actions {
  text-align: center;
}

.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #007aff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.progress {
  text-align: center;
  color: white;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: white;
  transition: width 0.3s ease;
}
</style>