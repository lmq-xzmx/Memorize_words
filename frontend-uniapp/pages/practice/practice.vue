<template>
  <view class="practice-container">
    <!-- 状态栏占位 -->
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 头部导航 -->
    <view class="header">
      <view class="header-left">
        <view class="back-btn" @tap="goBack">
          <text class="back-icon">‹</text>
        </view>
        <view class="header-title">
          <text class="title-text">学习练习</text>
          <text class="subtitle-text">{{ currentMode.name }}</text>
        </view>
      </view>
      <view class="header-right">
        <view class="progress-info">
          <text class="progress-text">{{ currentIndex + 1 }}/{{ totalWords }}</text>
        </view>
      </view>
    </view>
    
    <!-- 练习模式选择 -->
    <view class="mode-selector" v-if="!practiceStarted">
      <view class="selector-header">
        <text class="selector-title">选择练习模式</text>
        <text class="selector-desc">根据你的需要选择合适的练习方式</text>
      </view>
      
      <view class="mode-list">
        <view 
          class="mode-item" 
          v-for="mode in practiceMode" 
          :key="mode.id"
          @tap="selectMode(mode)"
          :class="{ active: selectedMode.id === mode.id }"
        >
          <view class="mode-icon" :class="mode.type">
            <text class="icon-text">{{ mode.icon }}</text>
          </view>
          <view class="mode-content">
            <text class="mode-name">{{ mode.name }}</text>
            <text class="mode-desc">{{ mode.description }}</text>
            <view class="mode-meta">
              <text class="meta-item">{{ mode.wordCount }} 个单词</text>
              <text class="meta-divider">•</text>
              <text class="meta-item">{{ mode.duration }}</text>
            </view>
          </view>
          <view class="mode-check" v-if="selectedMode.id === mode.id">
            <text class="check-icon">✓</text>
          </view>
        </view>
      </view>
      
      <!-- 设置选项 -->
      <view class="settings-section">
        <view class="settings-title">
          <text class="title-text">练习设置</text>
        </view>
        <view class="settings-list">
          <view class="setting-item">
            <text class="setting-label">单词数量</text>
            <view class="setting-control">
              <view class="counter">
                <view class="counter-btn" @tap="decreaseCount">
                  <text class="btn-text">-</text>
                </view>
                <text class="counter-value">{{ wordCount }}</text>
                <view class="counter-btn" @tap="increaseCount">
                  <text class="btn-text">+</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="setting-item">
            <text class="setting-label">显示音标</text>
            <view class="setting-control">
              <switch 
                :checked="showPhonetic" 
                @change="togglePhonetic" 
                color="#007aff"
              />
            </view>
          </view>
          
          <view class="setting-item">
            <text class="setting-label">自动播放发音</text>
            <view class="setting-control">
              <switch 
                :checked="autoPlay" 
                @change="toggleAutoPlay" 
                color="#007aff"
              />
            </view>
          </view>
        </view>
      </view>
      
      <!-- 开始按钮 -->
      <view class="start-section">
        <button class="start-btn" @tap="startPractice" :disabled="!selectedMode.id">
          <text class="start-text">开始练习</text>
        </button>
      </view>
    </view>
    
    <!-- 练习内容 -->
    <view class="practice-content" v-if="practiceStarted && !practiceCompleted">
      <!-- 进度条 -->
      <view class="progress-bar">
        <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      </view>
      
      <!-- 单词卡片 -->
      <view class="word-card" v-if="currentWord">
        <view class="card-header">
          <view class="word-type">
            <text class="type-text">{{ currentWord.partOfSpeech || 'n.' }}</text>
          </view>
          <view class="difficulty-level" :class="currentWord.difficulty">
            <text class="level-text">{{ getDifficultyText(currentWord.difficulty) }}</text>
          </view>
        </view>
        
        <view class="word-main">
          <text class="word-text">{{ currentWord.word }}</text>
          <view class="phonetic-section" v-if="showPhonetic && currentWord.phonetic">
            <text class="phonetic-text">/{{ currentWord.phonetic }}/</text>
            <view class="play-btn" @tap="playPronunciation">
              <text class="play-icon">🔊</text>
            </view>
          </view>
        </view>
        
        <!-- 选择题模式 -->
        <view class="choice-section" v-if="currentMode.type === 'choice'">
          <view class="question">
            <text class="question-text">选择正确的中文释义：</text>
          </view>
          <view class="choices">
            <view 
              class="choice-item" 
              v-for="(choice, index) in currentChoices" 
              :key="index"
              @tap="selectChoice(choice, index)"
              :class="{ 
                selected: selectedChoice === index,
                correct: showResult && choice.isCorrect,
                wrong: showResult && selectedChoice === index && !choice.isCorrect
              }"
            >
              <text class="choice-label">{{ String.fromCharCode(65 + index) }}.</text>
              <text class="choice-text">{{ choice.text }}</text>
              <view class="choice-icon" v-if="showResult">
                <text class="icon-text">{{ choice.isCorrect ? '✓' : (selectedChoice === index ? '✗' : '') }}</text>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 填空模式 -->
        <view class="fill-section" v-if="currentMode.type === 'fill'">
          <view class="question">
            <text class="question-text">根据中文释义填写单词：</text>
          </view>
          <view class="meaning">
            <text class="meaning-text">{{ currentWord.meaning }}</text>
          </view>
          <view class="input-section">
            <input 
              class="word-input" 
              v-model="userInput" 
              placeholder="请输入单词"
              :disabled="showResult"
              @confirm="checkFillAnswer"
            />
            <button class="check-btn" @tap="checkFillAnswer" :disabled="!userInput.trim()">
              <text class="check-text">检查</text>
            </button>
          </view>
          <view class="result-section" v-if="showResult">
            <view class="result-item" :class="{ correct: isCorrect, wrong: !isCorrect }">
              <text class="result-label">{{ isCorrect ? '正确' : '错误' }}</text>
              <text class="result-text">正确答案：{{ currentWord.word }}</text>
            </view>
          </view>
        </view>
        
        <!-- 听写模式 -->
        <view class="dictation-section" v-if="currentMode.type === 'dictation'">
          <view class="question">
            <text class="question-text">听音频写单词：</text>
          </view>
          <view class="audio-control">
            <view class="play-audio-btn" @tap="playPronunciation">
              <text class="audio-icon">🔊</text>
              <text class="audio-text">播放发音</text>
            </view>
          </view>
          <view class="input-section">
            <input 
              class="word-input" 
              v-model="userInput" 
              placeholder="请输入听到的单词"
              :disabled="showResult"
              @confirm="checkDictationAnswer"
            />
            <button class="check-btn" @tap="checkDictationAnswer" :disabled="!userInput.trim()">
              <text class="check-text">检查</text>
            </button>
          </view>
          <view class="result-section" v-if="showResult">
            <view class="result-item" :class="{ correct: isCorrect, wrong: !isCorrect }">
              <text class="result-label">{{ isCorrect ? '正确' : '错误' }}</text>
              <text class="result-text">正确答案：{{ currentWord.word }}</text>
              <text class="result-meaning">释义：{{ currentWord.meaning }}</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-buttons">
        <button class="action-btn secondary" @tap="skipWord" v-if="!showResult">
          <text class="btn-text">跳过</text>
        </button>
        <button class="action-btn primary" @tap="nextWord" v-if="showResult">
          <text class="btn-text">{{ currentIndex < totalWords - 1 ? '下一个' : '完成' }}</text>
        </button>
      </view>
    </view>
    
    <!-- 练习完成 -->
    <view class="completion-section" v-if="practiceCompleted">
      <view class="completion-header">
        <view class="completion-icon">
          <text class="icon-text">🎉</text>
        </view>
        <text class="completion-title">练习完成！</text>
        <text class="completion-desc">恭喜你完成了本次练习</text>
      </view>
      
      <view class="stats-section">
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-number">{{ practiceStats.correct }}</text>
            <text class="stat-label">正确</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ practiceStats.wrong }}</text>
            <text class="stat-label">错误</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ practiceStats.accuracy }}%</text>
            <text class="stat-label">准确率</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ practiceStats.duration }}</text>
            <text class="stat-label">用时</text>
          </view>
        </view>
      </view>
      
      <view class="completion-actions">
        <button class="action-btn secondary" @tap="reviewWrongWords" v-if="practiceStats.wrong > 0">
          <text class="btn-text">复习错题</text>
        </button>
        <button class="action-btn primary" @tap="restartPractice">
          <text class="btn-text">再次练习</text>
        </button>
        <button class="action-btn outline" @tap="backToHome">
          <text class="btn-text">返回首页</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script>
  import { mapState, mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Practice',
    data() {
      return {
        practiceStarted: false,
        practiceCompleted: false,
        showResult: false,
        selectedChoice: -1,
        userInput: '',
        isCorrect: false,
        currentIndex: 0,
        startTime: null,
        
        // 练习设置
        wordCount: 20,
        showPhonetic: true,
        autoPlay: false,
        
        // 练习模式
        practiceMode: [
          {
            id: 1,
            name: '选择题',
            type: 'choice',
            description: '从四个选项中选择正确答案',
            icon: '📝',
            wordCount: 20,
            duration: '5-10分钟'
          },
          {
            id: 2,
            name: '填空题',
            type: 'fill',
            description: '根据中文释义填写英文单词',
            icon: '✏️',
            wordCount: 15,
            duration: '8-15分钟'
          },
          {
            id: 3,
            name: '听写练习',
            type: 'dictation',
            description: '听发音写出对应的单词',
            icon: '🎧',
            wordCount: 10,
            duration: '10-20分钟'
          }
        ],
        
        selectedMode: {},
        currentMode: {},
        
        // 练习数据
        practiceWords: [],
        currentWord: null,
        currentChoices: [],
        wrongWords: [],
        
        // 统计数据
        practiceStats: {
          correct: 0,
          wrong: 0,
          accuracy: 0,
          duration: '0分0秒'
        }
      }
    },
    
    computed: {
      ...mapGetters('app', ['statusBarHeight']),
      
      totalWords() {
        return this.practiceWords.length
      },
      
      progressPercent() {
        return this.totalWords > 0 ? Math.round((this.currentIndex / this.totalWords) * 100) : 0
      }
    },
    
    onLoad(options) {
      this.initPractice(options)
    },
    
    methods: {
      ...mapActions('app', ['navigateTo', 'showToast', 'showLoading', 'hideLoading']),
      
      // 初始化练习
      initPractice(options) {
        // 设置默认选中模式
        this.selectedMode = this.practiceMode[0]
        
        // 如果有传入模式参数
        if (options && options.mode) {
          const mode = this.practiceMode.find(m => m.type === options.mode)
          if (mode) {
            this.selectedMode = mode
          }
        }
      },
      
      // 选择练习模式
      selectMode(mode) {
        this.selectedMode = mode
        this.wordCount = mode.wordCount
      },
      
      // 增加单词数量
      increaseCount() {
        if (this.wordCount < 50) {
          this.wordCount += 5
        }
      },
      
      // 减少单词数量
      decreaseCount() {
        if (this.wordCount > 5) {
          this.wordCount -= 5
        }
      },
      
      // 切换音标显示
      togglePhonetic(e) {
        this.showPhonetic = e.detail.value
      },
      
      // 切换自动播放
      toggleAutoPlay(e) {
        this.autoPlay = e.detail.value
      },
      
      // 开始练习
      async startPractice() {
        if (!this.selectedMode.id) {
          this.showToast({ title: '请选择练习模式' })
          return
        }
        
        try {
          this.showLoading({ title: '准备练习...' })
          
          // 获取练习单词
          await this.loadPracticeWords()
          
          this.currentMode = this.selectedMode
          this.practiceStarted = true
          this.startTime = Date.now()
          this.currentIndex = 0
          this.practiceStats = { correct: 0, wrong: 0, accuracy: 0, duration: '0分0秒' }
          this.wrongWords = []
          
          this.loadCurrentWord()
        } catch (error) {
          console.error('开始练习失败:', error)
          this.showToast({ title: '加载失败，请重试' })
        } finally {
          this.hideLoading()
        }
      },
      
      // 加载练习单词
      async loadPracticeWords() {
        // 这里应该调用API获取练习单词
        // 模拟数据
        this.practiceWords = [
          {
            id: 1,
            word: 'apple',
            phonetic: 'ˈæpl',
            meaning: '苹果',
            partOfSpeech: 'n.',
            difficulty: 'easy'
          },
          {
            id: 2,
            word: 'beautiful',
            phonetic: 'ˈbjuːtɪfl',
            meaning: '美丽的',
            partOfSpeech: 'adj.',
            difficulty: 'medium'
          },
          {
            id: 3,
            word: 'complicated',
            phonetic: 'ˈkɒmplɪkeɪtɪd',
            meaning: '复杂的',
            partOfSpeech: 'adj.',
            difficulty: 'hard'
          }
        ].slice(0, this.wordCount)
      },
      
      // 加载当前单词
      loadCurrentWord() {
        if (this.currentIndex < this.practiceWords.length) {
          this.currentWord = this.practiceWords[this.currentIndex]
          this.showResult = false
          this.selectedChoice = -1
          this.userInput = ''
          this.isCorrect = false
          
          if (this.currentMode.type === 'choice') {
            this.generateChoices()
          }
          
          if (this.autoPlay) {
            setTimeout(() => {
              this.playPronunciation()
            }, 500)
          }
        } else {
          this.completePractice()
        }
      },
      
      // 生成选择题选项
      generateChoices() {
        const correctAnswer = this.currentWord.meaning
        const wrongAnswers = ['错误选项1', '错误选项2', '错误选项3'] // 这里应该从API获取
        
        const choices = [
          { text: correctAnswer, isCorrect: true },
          ...wrongAnswers.map(text => ({ text, isCorrect: false }))
        ]
        
        // 随机打乱选项
        this.currentChoices = this.shuffleArray(choices)
      },
      
      // 打乱数组
      shuffleArray(array) {
        const newArray = [...array]
        for (let i = newArray.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1))
          ;[newArray[i], newArray[j]] = [newArray[j], newArray[i]]
        }
        return newArray
      },
      
      // 选择答案
      selectChoice(choice, index) {
        if (this.showResult) return
        
        this.selectedChoice = index
        this.isCorrect = choice.isCorrect
        this.showResult = true
        
        if (this.isCorrect) {
          this.practiceStats.correct++
        } else {
          this.practiceStats.wrong++
          this.wrongWords.push(this.currentWord)
        }
      },
      
      // 检查填空答案
      checkFillAnswer() {
        if (!this.userInput.trim()) return
        
        this.isCorrect = this.userInput.trim().toLowerCase() === this.currentWord.word.toLowerCase()
        this.showResult = true
        
        if (this.isCorrect) {
          this.practiceStats.correct++
        } else {
          this.practiceStats.wrong++
          this.wrongWords.push(this.currentWord)
        }
      },
      
      // 检查听写答案
      checkDictationAnswer() {
        this.checkFillAnswer() // 逻辑相同
      },
      
      // 跳过单词
      skipWord() {
        this.practiceStats.wrong++
        this.wrongWords.push(this.currentWord)
        this.nextWord()
      },
      
      // 下一个单词
      nextWord() {
        this.currentIndex++
        this.loadCurrentWord()
      },
      
      // 完成练习
      completePractice() {
        const endTime = Date.now()
        const duration = Math.round((endTime - this.startTime) / 1000)
        const minutes = Math.floor(duration / 60)
        const seconds = duration % 60
        
        this.practiceStats.duration = `${minutes}分${seconds}秒`
        this.practiceStats.accuracy = this.totalWords > 0 ? 
          Math.round((this.practiceStats.correct / this.totalWords) * 100) : 0
        
        this.practiceCompleted = true
        
        // 保存练习记录
        this.savePracticeRecord()
      },
      
      // 保存练习记录
      async savePracticeRecord() {
        try {
          // 这里应该调用API保存练习记录
          console.log('保存练习记录:', this.practiceStats)
        } catch (error) {
          console.error('保存练习记录失败:', error)
        }
      },
      
      // 播放发音
      playPronunciation() {
        // 这里应该播放单词发音
        console.log('播放发音:', this.currentWord.word)
        this.showToast({ title: '播放发音' })
      },
      
      // 获取难度文本
      getDifficultyText(difficulty) {
        const difficultyMap = {
          easy: '简单',
          medium: '中等',
          hard: '困难'
        }
        return difficultyMap[difficulty] || '未知'
      },
      
      // 复习错题
      reviewWrongWords() {
        this.practiceWords = [...this.wrongWords]
        this.currentIndex = 0
        this.practiceCompleted = false
        this.practiceStats = { correct: 0, wrong: 0, accuracy: 0, duration: '0分0秒' }
        this.wrongWords = []
        this.startTime = Date.now()
        this.loadCurrentWord()
      },
      
      // 重新练习
      restartPractice() {
        this.practiceStarted = false
        this.practiceCompleted = false
        this.currentIndex = 0
        this.selectedMode = this.practiceMode[0]
      },
      
      // 返回首页
      backToHome() {
        uni.switchTab({
          url: '/pages/index/index'
        })
      },
      
      // 返回上一页
      goBack() {
        if (this.practiceStarted && !this.practiceCompleted) {
          uni.showModal({
            title: '确认退出',
            content: '练习尚未完成，确定要退出吗？',
            success: (res) => {
              if (res.confirm) {
                uni.navigateBack()
              }
            }
          })
        } else {
          uni.navigateBack()
        }
      }
    }
  }
</script>

<style>
  .practice-container {
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  .status-bar {
    background: #ffffff;
  }
  
  .header {
    background: #ffffff;
    padding: 20rpx 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .header-left {
    display: flex;
    align-items: center;
  }
  
  .back-btn {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    cursor: pointer;
  }
  
  .back-icon {
    font-size: 36rpx;
    color: #007aff;
    font-weight: 600;
  }
  
  .header-title {
    display: flex;
    flex-direction: column;
  }
  
  .title-text {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .subtitle-text {
    font-size: 24rpx;
    color: #666666;
    margin-top: 5rpx;
  }
  
  .header-right {
    display: flex;
    align-items: center;
  }
  
  .progress-info {
    background: #f8f9fa;
    padding: 10rpx 20rpx;
    border-radius: 20rpx;
  }
  
  .progress-text {
    font-size: 24rpx;
    color: #666666;
  }
  
  .mode-selector {
    padding: 30rpx;
  }
  
  .selector-header {
    text-align: center;
    margin-bottom: 40rpx;
  }
  
  .selector-title {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 10rpx;
  }
  
  .selector-desc {
    font-size: 26rpx;
    color: #666666;
  }
  
  .mode-list {
    margin-bottom: 40rpx;
  }
  
  .mode-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 30rpx;
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2rpx solid transparent;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  }
  
  .mode-item.active {
    border-color: #007aff;
    background: #f0f8ff;
  }
  
  .mode-icon {
    width: 80rpx;
    height: 80rpx;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 25rpx;
  }
  
  .icon-text {
    font-size: 32rpx;
  }
  
  .mode-content {
    flex: 1;
  }
  
  .mode-name {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .mode-desc {
    display: block;
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 10rpx;
  }
  
  .mode-meta {
    display: flex;
    align-items: center;
    gap: 10rpx;
  }
  
  .meta-item {
    font-size: 22rpx;
    color: #999999;
  }
  
  .meta-divider {
    font-size: 22rpx;
    color: #cccccc;
  }
  
  .mode-check {
    width: 40rpx;
    height: 40rpx;
    background: #007aff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .check-icon {
    font-size: 24rpx;
    color: #ffffff;
  }
  
  .settings-section {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 30rpx;
    margin-bottom: 40rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  }
  
  .settings-title {
    margin-bottom: 30rpx;
  }
  
  .settings-list {
    display: flex;
    flex-direction: column;
    gap: 30rpx;
  }
  
  .setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .setting-label {
    font-size: 28rpx;
    color: #333333;
  }
  
  .setting-control {
    display: flex;
    align-items: center;
  }
  
  .counter {
    display: flex;
    align-items: center;
    background: #f8f9fa;
    border-radius: 25rpx;
    overflow: hidden;
  }
  
  .counter-btn {
    width: 60rpx;
    height: 50rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #007aff;
    color: #ffffff;
    cursor: pointer;
  }
  
  .btn-text {
    font-size: 28rpx;
    font-weight: 600;
  }
  
  .counter-value {
    min-width: 80rpx;
    text-align: center;
    font-size: 26rpx;
    color: #333333;
    padding: 0 20rpx;
  }
  
  .start-section {
    text-align: center;
  }
  
  .start-btn {
    width: 100%;
    height: 80rpx;
    background: #007aff;
    color: #ffffff;
    border: none;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .start-btn:disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
  
  .start-text {
    font-size: 28rpx;
  }
  
  .practice-content {
    padding: 30rpx;
  }
  
  .progress-bar {
    height: 8rpx;
    background: #f0f0f0;
    border-radius: 4rpx;
    overflow: hidden;
    margin-bottom: 40rpx;
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #007aff 0%, #34c759 100%);
    border-radius: 4rpx;
    transition: width 0.3s ease;
  }
  
  .word-card {
    background: #ffffff;
    border-radius: 20rpx;
    padding: 40rpx;
    margin-bottom: 40rpx;
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
  }
  
  .word-type {
    background: #f0f8ff;
    color: #007aff;
    padding: 8rpx 16rpx;
    border-radius: 12rpx;
  }
  
  .type-text {
    font-size: 22rpx;
  }
  
  .difficulty-level {
    padding: 8rpx 16rpx;
    border-radius: 12rpx;
  }
  
  .difficulty-level.easy {
    background: #e8f5e8;
    color: #34c759;
  }
  
  .difficulty-level.medium {
    background: #fff3cd;
    color: #ff9500;
  }
  
  .difficulty-level.hard {
    background: #f8d7da;
    color: #dc3545;
  }
  
  .level-text {
    font-size: 22rpx;
  }
  
  .word-main {
    text-align: center;
    margin-bottom: 40rpx;
  }
  
  .word-text {
    display: block;
    font-size: 60rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 20rpx;
  }
  
  .phonetic-section {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15rpx;
  }
  
  .phonetic-text {
    font-size: 28rpx;
    color: #666666;
  }
  
  .play-btn {
    width: 50rpx;
    height: 50rpx;
    background: #007aff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .play-icon {
    font-size: 24rpx;
    color: #ffffff;
  }
  
  .choice-section, .fill-section, .dictation-section {
    margin-top: 30rpx;
  }
  
  .question {
    margin-bottom: 30rpx;
    text-align: center;
  }
  
  .question-text {
    font-size: 28rpx;
    color: #333333;
    font-weight: 500;
  }
  
  .choices {
    display: flex;
    flex-direction: column;
    gap: 15rpx;
  }
  
  .choice-item {
    display: flex;
    align-items: center;
    padding: 25rpx;
    background: #f8f9fa;
    border-radius: 16rpx;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2rpx solid transparent;
  }
  
  .choice-item.selected {
    border-color: #007aff;
    background: #f0f8ff;
  }
  
  .choice-item.correct {
    border-color: #34c759;
    background: #e8f5e8;
  }
  
  .choice-item.wrong {
    border-color: #ff4757;
    background: #ffe8e8;
  }
  
  .choice-label {
    font-size: 26rpx;
    font-weight: 600;
    color: #007aff;
    margin-right: 20rpx;
    min-width: 40rpx;
  }
  
  .choice-text {
    flex: 1;
    font-size: 26rpx;
    color: #333333;
  }
  
  .choice-icon {
    width: 40rpx;
    text-align: center;
  }
  
  .meaning {
    text-align: center;
    margin-bottom: 30rpx;
  }
  
  .meaning-text {
    font-size: 32rpx;
    color: #333333;
    font-weight: 500;
  }
  
  .input-section {
    display: flex;
    gap: 15rpx;
    margin-bottom: 30rpx;
  }
  
  .word-input {
    flex: 1;
    height: 80rpx;
    background: #f8f9fa;
    border: 2rpx solid #e0e0e0;
    border-radius: 16rpx;
    padding: 0 25rpx;
    font-size: 28rpx;
    color: #333333;
  }
  
  .word-input:focus {
    border-color: #007aff;
    background: #ffffff;
  }
  
  .check-btn {
    width: 120rpx;
    height: 80rpx;
    background: #007aff;
    color: #ffffff;
    border: none;
    border-radius: 16rpx;
    font-size: 26rpx;
    cursor: pointer;
  }
  
  .check-btn:disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
  
  .check-text {
    font-size: 26rpx;
  }
  
  .audio-control {
    text-align: center;
    margin-bottom: 30rpx;
  }
  
  .play-audio-btn {
    display: inline-flex;
    align-items: center;
    gap: 10rpx;
    background: #007aff;
    color: #ffffff;
    padding: 20rpx 30rpx;
    border-radius: 25rpx;
    cursor: pointer;
  }
  
  .audio-icon {
    font-size: 24rpx;
  }
  
  .audio-text {
    font-size: 26rpx;
  }
  
  .result-section {
    text-align: center;
  }
  
  .result-item {
    padding: 20rpx;
    border-radius: 12rpx;
    margin-bottom: 10rpx;
  }
  
  .result-item.correct {
    background: #e8f5e8;
    color: #34c759;
  }
  
  .result-item.wrong {
    background: #ffe8e8;
    color: #ff4757;
  }
  
  .result-label {
    display: block;
    font-size: 26rpx;
    font-weight: 600;
    margin-bottom: 8rpx;
  }
  
  .result-text {
    display: block;
    font-size: 24rpx;
    margin-bottom: 5rpx;
  }
  
  .result-meaning {
    display: block;
    font-size: 24rpx;
  }
  
  .action-buttons {
    display: flex;
    gap: 20rpx;
    justify-content: center;
  }
  
  .action-btn {
    min-width: 200rpx;
    height: 80rpx;
    border: none;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .action-btn.primary {
    background: #007aff;
    color: #ffffff;
  }
  
  .action-btn.secondary {
    background: #f8f9fa;
    color: #666666;
    border: 2rpx solid #e0e0e0;
  }
  
  .action-btn.outline {
    background: transparent;
    color: #007aff;
    border: 2rpx solid #007aff;
  }
  
  .completion-section {
    padding: 60rpx 30rpx;
    text-align: center;
  }
  
  .completion-header {
    margin-bottom: 60rpx;
  }
  
  .completion-icon {
    font-size: 120rpx;
    margin-bottom: 30rpx;
  }
  
  .completion-title {
    display: block;
    font-size: 48rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 15rpx;
  }
  
  .completion-desc {
    font-size: 28rpx;
    color: #666666;
  }
  
  .stats-section {
    margin-bottom: 60rpx;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30rpx;
    background: #ffffff;
    border-radius: 20rpx;
    padding: 40rpx;
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  }
  
  .stat-item {
    text-align: center;
  }
  
  .stat-number {
    display: block;
    font-size: 48rpx;
    font-weight: 700;
    color: #007aff;
    margin-bottom: 10rpx;
  }
  
  .stat-label {
    font-size: 24rpx;
    color: #666666;
  }
  
  .completion-actions {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .mode-item {
      flex-direction: column;
      text-align: center;
    }
    
    .mode-icon {
      margin-right: 0;
      margin-bottom: 20rpx;
    }
    
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 20rpx;
    }
    
    .word-text {
      font-size: 48rpx;
    }
  }
</style>