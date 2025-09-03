<template>
  <view class="word-container">
    <!-- 状态栏占位 -->
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 头部导航 -->
    <view class="header">
      <view class="header-left">
        <view class="back-btn" @tap="goBack">
          <text class="back-icon">←</text>
        </view>
        <text class="header-title">斩词练习</text>
      </view>
      <view class="header-right">
        <view class="progress-info">
          <text class="progress-text">{{ currentIndex + 1 }}/{{ totalWords }}</text>
        </view>
        <view class="menu-btn" @tap="showMenu">
          <text class="menu-icon">⋯</text>
        </view>
      </view>
    </view>
    
    <!-- 进度条 -->
    <view class="progress-bar">
      <view 
        class="progress-fill" 
        :style="{ width: progressPercent + '%' }"
      ></view>
    </view>
    
    <!-- 学习模式选择 -->
    <view class="mode-selector" v-if="!isLearning">
      <view class="mode-title">
        <text class="title-text">选择学习模式</text>
        <text class="title-desc">根据你的需求选择合适的学习方式</text>
      </view>
      <view class="mode-list">
        <view 
          class="mode-item" 
          v-for="mode in learningModes" 
          :key="mode.id"
          @tap="selectMode(mode)"
          :class="{ active: selectedMode?.id === mode.id }"
        >
          <view class="mode-icon" :style="{ backgroundColor: mode.color }">
            <text class="icon-text">{{ mode.icon }}</text>
          </view>
          <view class="mode-content">
            <text class="mode-name">{{ mode.name }}</text>
            <text class="mode-desc">{{ mode.description }}</text>
          </view>
          <view class="mode-check" v-if="selectedMode?.id === mode.id">
            <text class="check-icon">✓</text>
          </view>
        </view>
      </view>
      <view class="start-section">
        <button 
          class="start-btn" 
          @tap="startLearning"
          :disabled="!selectedMode"
          :class="{ disabled: !selectedMode }"
        >
          开始学习
        </button>
      </view>
    </view>
    
    <!-- 学习界面 -->
    <view class="learning-content" v-if="isLearning && currentWord">
      <!-- 单词卡片 -->
      <view class="word-card">
        <view class="word-main">
          <text class="word-text">{{ currentWord.word }}</text>
          <view class="word-phonetic" v-if="currentWord.phonetic">
            <text class="phonetic-text">{{ currentWord.phonetic }}</text>
            <view class="play-btn" @tap="playPronunciation">
              <text class="play-icon">🔊</text>
            </view>
          </view>
        </view>
        
        <!-- 词性和释义 -->
        <view class="word-meanings" v-if="showMeaning">
          <view 
            class="meaning-item" 
            v-for="(meaning, index) in currentWord.meanings" 
            :key="index"
          >
            <text class="part-of-speech">{{ meaning.partOfSpeech }}</text>
            <text class="definition">{{ meaning.definition }}</text>
          </view>
        </view>
        
        <!-- 例句 -->
        <view class="word-examples" v-if="showExample && currentWord.examples">
          <view 
            class="example-item" 
            v-for="(example, index) in currentWord.examples" 
            :key="index"
          >
            <text class="example-text">{{ example.sentence }}</text>
            <text class="example-translation">{{ example.translation }}</text>
          </view>
        </view>
      </view>
      
      <!-- 操作按钮 -->
      <view class="action-buttons">
        <view class="action-row" v-if="!showMeaning">
          <button class="action-btn know-btn" @tap="markAsKnown">
            <text class="btn-icon">✓</text>
            <text class="btn-text">认识</text>
          </button>
          <button class="action-btn unknown-btn" @tap="markAsUnknown">
            <text class="btn-icon">✗</text>
            <text class="btn-text">不认识</text>
          </button>
        </view>
        
        <view class="action-row" v-if="showMeaning">
          <button class="action-btn easy-btn" @tap="markAsEasy">
            <text class="btn-text">简单</text>
          </button>
          <button class="action-btn normal-btn" @tap="markAsNormal">
            <text class="btn-text">一般</text>
          </button>
          <button class="action-btn hard-btn" @tap="markAsHard">
            <text class="btn-text">困难</text>
          </button>
        </view>
        
        <view class="helper-buttons">
          <button class="helper-btn" @tap="toggleMeaning" v-if="!showMeaning">
            <text class="helper-text">查看释义</text>
          </button>
          <button class="helper-btn" @tap="toggleExample" v-if="showMeaning && !showExample">
            <text class="helper-text">查看例句</text>
          </button>
          <button class="helper-btn" @tap="addToFavorites">
            <text class="helper-text">{{ isFavorited ? '取消收藏' : '收藏单词' }}</text>
          </button>
        </view>
      </view>
    </view>
    
    <!-- 学习完成 -->
    <view class="completion-screen" v-if="isCompleted">
      <view class="completion-content">
        <view class="completion-icon">
          <text class="icon-text">🎉</text>
        </view>
        <text class="completion-title">学习完成！</text>
        <text class="completion-desc">恭喜你完成了今天的学习任务</text>
        
        <view class="completion-stats">
          <view class="stat-item">
            <text class="stat-number">{{ learningStats.totalWords }}</text>
            <text class="stat-label">学习单词</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ learningStats.knownWords }}</text>
            <text class="stat-label">已掌握</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ learningStats.accuracy }}%</text>
            <text class="stat-label">正确率</text>
          </view>
        </view>
        
        <view class="completion-actions">
          <button class="completion-btn primary" @tap="continueNext">
            继续下一组
          </button>
          <button class="completion-btn secondary" @tap="reviewMistakes">
            复习错词
          </button>
          <button class="completion-btn secondary" @tap="backToHome">
            返回首页
          </button>
        </view>
      </view>
    </view>
    
    <!-- 菜单弹窗 -->
    <view class="menu-overlay" v-if="showMenuModal" @tap="hideMenu">
      <view class="menu-modal" @tap.stop>
        <view class="menu-header">
          <text class="menu-title">学习设置</text>
          <view class="close-btn" @tap="hideMenu">
            <text class="close-icon">×</text>
          </view>
        </view>
        <view class="menu-content">
          <view class="menu-item" @tap="pauseLearning">
            <text class="menu-icon">⏸️</text>
            <text class="menu-text">暂停学习</text>
          </view>
          <view class="menu-item" @tap="restartLearning">
            <text class="menu-icon">🔄</text>
            <text class="menu-text">重新开始</text>
          </view>
          <view class="menu-item" @tap="changeDifficulty">
            <text class="menu-icon">⚙️</text>
            <text class="menu-text">调整难度</text>
          </view>
          <view class="menu-item" @tap="viewProgress">
            <text class="menu-icon">📊</text>
            <text class="menu-text">学习统计</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  import { mapState, mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Word',
    data() {
      return {
        isLearning: false,
        isCompleted: false,
        showMenuModal: false,
        selectedMode: null,
        currentIndex: 0,
        totalWords: 20,
        showMeaning: false,
        showExample: false,
        isFavorited: false,
        
        learningModes: [
          {
            id: 1,
            name: '快速模式',
            description: '快速浏览，适合复习',
            icon: '⚡',
            color: '#FF6B6B'
          },
          {
            id: 2,
            name: '标准模式',
            description: '标准学习，平衡速度与效果',
            icon: '📚',
            color: '#4ECDC4'
          },
          {
            id: 3,
            name: '深度模式',
            description: '深入学习，包含例句和用法',
            icon: '🎯',
            color: '#45B7D1'
          }
        ],
        
        currentWord: {
          id: 1,
          word: 'example',
          phonetic: '/ɪɡˈzæmpl/',
          meanings: [
            {
              partOfSpeech: 'n.',
              definition: '例子，实例，榜样'
            },
            {
              partOfSpeech: 'v.',
              definition: '举例说明'
            }
          ],
          examples: [
            {
              sentence: 'This is a good example of modern architecture.',
              translation: '这是现代建筑的一个好例子。'
            },
            {
              sentence: 'Can you give me an example?',
              translation: '你能给我举个例子吗？'
            }
          ]
        },
        
        learningStats: {
          totalWords: 20,
          knownWords: 15,
          accuracy: 75
        }
      }
    },
    
    computed: {
      ...mapGetters('app', ['statusBarHeight']),
      
      progressPercent() {
        if (this.totalWords === 0) return 0
        return Math.round((this.currentIndex / this.totalWords) * 100)
      }
    },
    
    onLoad(options) {
      this.initPage(options)
    },
    
    onUnload() {
      this.saveLearningProgress()
    },
    
    methods: {
      ...mapActions('app', ['navigateBack', 'showToast', 'showModal']),
      
      // 初始化页面
      initPage(options) {
        if (options.mode) {
          const mode = this.learningModes.find(m => m.id == options.mode)
          if (mode) {
            this.selectedMode = mode
            this.startLearning()
          }
        }
      },
      
      // 返回上一页
      goBack() {
        if (this.isLearning) {
          this.showModal({
            title: '确认退出',
            content: '学习进度将会保存，确定要退出吗？',
            success: (res) => {
              if (res.confirm) {
                this.saveLearningProgress()
                this.navigateBack()
              }
            }
          })
        } else {
          this.navigateBack()
        }
      },
      
      // 选择学习模式
      selectMode(mode) {
        this.selectedMode = mode
      },
      
      // 开始学习
      async startLearning() {
        if (!this.selectedMode) {
          this.showToast({ title: '请选择学习模式' })
          return
        }
        
        try {
          // 这里应该调用API获取单词列表
          await this.loadWords()
          this.isLearning = true
          this.currentIndex = 0
          this.resetWordState()
        } catch (error) {
          console.error('开始学习失败:', error)
          this.showToast({ title: '加载失败，请重试' })
        }
      },
      
      // 加载单词
      async loadWords() {
        try {
          // 这里应该调用实际的API
          console.log('加载单词列表')
        } catch (error) {
          throw error
        }
      },
      
      // 重置单词状态
      resetWordState() {
        this.showMeaning = false
        this.showExample = false
        this.isFavorited = false
      },
      
      // 播放发音
      playPronunciation() {
        try {
          // 这里应该调用语音播放API
          console.log('播放发音:', this.currentWord.word)
          this.showToast({ title: '播放发音' })
        } catch (error) {
          console.error('播放发音失败:', error)
        }
      },
      
      // 切换释义显示
      toggleMeaning() {
        this.showMeaning = !this.showMeaning
      },
      
      // 切换例句显示
      toggleExample() {
        this.showExample = !this.showExample
      },
      
      // 添加到收藏
      addToFavorites() {
        this.isFavorited = !this.isFavorited
        const message = this.isFavorited ? '已添加到收藏' : '已取消收藏'
        this.showToast({ title: message })
      },
      
      // 标记为认识
      markAsKnown() {
        this.recordAnswer('known')
        this.nextWord()
      },
      
      // 标记为不认识
      markAsUnknown() {
        this.showMeaning = true
        this.recordAnswer('unknown')
      },
      
      // 标记为简单
      markAsEasy() {
        this.recordAnswer('easy')
        this.nextWord()
      },
      
      // 标记为一般
      markAsNormal() {
        this.recordAnswer('normal')
        this.nextWord()
      },
      
      // 标记为困难
      markAsHard() {
        this.recordAnswer('hard')
        this.nextWord()
      },
      
      // 记录答案
      recordAnswer(type) {
        try {
          // 这里应该调用API记录学习结果
          console.log('记录答案:', type, this.currentWord.word)
        } catch (error) {
          console.error('记录答案失败:', error)
        }
      },
      
      // 下一个单词
      nextWord() {
        if (this.currentIndex < this.totalWords - 1) {
          this.currentIndex++
          this.resetWordState()
          // 这里应该加载下一个单词
        } else {
          this.completeLearning()
        }
      },
      
      // 完成学习
      completeLearning() {
        this.isLearning = false
        this.isCompleted = true
        this.saveLearningProgress()
      },
      
      // 保存学习进度
      saveLearningProgress() {
        try {
          // 这里应该调用API保存学习进度
          console.log('保存学习进度')
        } catch (error) {
          console.error('保存学习进度失败:', error)
        }
      },
      
      // 继续下一组
      continueNext() {
        this.isCompleted = false
        this.startLearning()
      },
      
      // 复习错词
      reviewMistakes() {
        // 这里应该加载错词列表
        this.showToast({ title: '加载错词复习' })
      },
      
      // 返回首页
      backToHome() {
        uni.switchTab({
          url: '/pages/index/index'
        })
      },
      
      // 显示菜单
      showMenu() {
        this.showMenuModal = true
      },
      
      // 隐藏菜单
      hideMenu() {
        this.showMenuModal = false
      },
      
      // 暂停学习
      pauseLearning() {
        this.hideMenu()
        this.showModal({
          title: '暂停学习',
          content: '学习进度将会保存',
          success: (res) => {
            if (res.confirm) {
              this.saveLearningProgress()
              this.navigateBack()
            }
          }
        })
      },
      
      // 重新开始
      restartLearning() {
        this.hideMenu()
        this.showModal({
          title: '重新开始',
          content: '当前进度将会丢失，确定要重新开始吗？',
          success: (res) => {
            if (res.confirm) {
              this.currentIndex = 0
              this.resetWordState()
            }
          }
        })
      },
      
      // 调整难度
      changeDifficulty() {
        this.hideMenu()
        this.showToast({ title: '功能开发中' })
      },
      
      // 查看进度
      viewProgress() {
        this.hideMenu()
        this.showToast({ title: '功能开发中' })
      }
    }
  }
</script>

<style>
  .word-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    display: flex;
    flex-direction: column;
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
    color: #333333;
  }
  
  .header-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 20rpx;
  }
  
  .progress-info {
    background: #f8f9fa;
    padding: 8rpx 16rpx;
    border-radius: 20rpx;
  }
  
  .progress-text {
    font-size: 24rpx;
    color: #666666;
  }
  
  .menu-btn {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .menu-icon {
    font-size: 28rpx;
    color: #333333;
  }
  
  .progress-bar {
    height: 6rpx;
    background: #f0f0f0;
    position: relative;
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #007aff 0%, #5856d6 100%);
    transition: width 0.3s ease;
  }
  
  .mode-selector {
    flex: 1;
    padding: 40rpx 30rpx;
  }
  
  .mode-title {
    text-align: center;
    margin-bottom: 60rpx;
  }
  
  .title-text {
    display: block;
    font-size: 40rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 15rpx;
  }
  
  .title-desc {
    font-size: 28rpx;
    color: #666666;
  }
  
  .mode-list {
    margin-bottom: 60rpx;
  }
  
  .mode-item {
    background: #ffffff;
    border-radius: 20rpx;
    padding: 30rpx;
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2rpx solid transparent;
  }
  
  .mode-item.active {
    border-color: #007aff;
    box-shadow: 0 4rpx 20rpx rgba(0, 122, 255, 0.2);
  }
  
  .mode-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 30rpx;
  }
  
  .icon-text {
    font-size: 36rpx;
    color: #ffffff;
  }
  
  .mode-content {
    flex: 1;
  }
  
  .mode-name {
    display: block;
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .mode-desc {
    font-size: 26rpx;
    color: #666666;
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
  
  .start-section {
    text-align: center;
  }
  
  .start-btn {
    width: 100%;
    height: 88rpx;
    background: linear-gradient(135deg, #007aff 0%, #5856d6 100%);
    color: #ffffff;
    border: none;
    border-radius: 44rpx;
    font-size: 32rpx;
    font-weight: 600;
    cursor: pointer;
  }
  
  .start-btn.disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
  
  .learning-content {
    flex: 1;
    padding: 40rpx 30rpx;
    display: flex;
    flex-direction: column;
  }
  
  .word-card {
    background: #ffffff;
    border-radius: 24rpx;
    padding: 60rpx 40rpx;
    margin-bottom: 40rpx;
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  
  .word-main {
    text-align: center;
    margin-bottom: 40rpx;
  }
  
  .word-text {
    display: block;
    font-size: 72rpx;
    font-weight: 700;
    color: #333333;
    margin-bottom: 20rpx;
  }
  
  .word-phonetic {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15rpx;
  }
  
  .phonetic-text {
    font-size: 32rpx;
    color: #666666;
    font-style: italic;
  }
  
  .play-btn {
    width: 60rpx;
    height: 60rpx;
    background: #f8f9fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .play-icon {
    font-size: 28rpx;
  }
  
  .word-meanings {
    margin-bottom: 30rpx;
  }
  
  .meaning-item {
    margin-bottom: 20rpx;
    padding: 20rpx;
    background: #f8f9fa;
    border-radius: 12rpx;
  }
  
  .part-of-speech {
    display: inline-block;
    background: #007aff;
    color: #ffffff;
    padding: 4rpx 12rpx;
    border-radius: 8rpx;
    font-size: 22rpx;
    margin-right: 15rpx;
  }
  
  .definition {
    font-size: 28rpx;
    color: #333333;
    line-height: 1.5;
  }
  
  .word-examples {
    margin-top: 30rpx;
  }
  
  .example-item {
    margin-bottom: 25rpx;
    padding: 25rpx;
    background: #f0f8ff;
    border-radius: 12rpx;
    border-left: 4rpx solid #007aff;
  }
  
  .example-text {
    display: block;
    font-size: 28rpx;
    color: #333333;
    line-height: 1.6;
    margin-bottom: 10rpx;
    font-style: italic;
  }
  
  .example-translation {
    font-size: 26rpx;
    color: #666666;
    line-height: 1.5;
  }
  
  .action-buttons {
    padding: 20rpx 0;
  }
  
  .action-row {
    display: flex;
    gap: 20rpx;
    margin-bottom: 20rpx;
  }
  
  .action-btn {
    flex: 1;
    height: 80rpx;
    border: none;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10rpx;
  }
  
  .know-btn {
    background: #34c759;
    color: #ffffff;
  }
  
  .unknown-btn {
    background: #ff3b30;
    color: #ffffff;
  }
  
  .easy-btn {
    background: #34c759;
    color: #ffffff;
  }
  
  .normal-btn {
    background: #ff9500;
    color: #ffffff;
  }
  
  .hard-btn {
    background: #ff3b30;
    color: #ffffff;
  }
  
  .btn-icon {
    font-size: 24rpx;
  }
  
  .btn-text {
    font-size: 28rpx;
  }
  
  .helper-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 15rpx;
    justify-content: center;
  }
  
  .helper-btn {
    background: #f8f9fa;
    border: 1rpx solid #e9ecef;
    color: #666666;
    padding: 15rpx 25rpx;
    border-radius: 25rpx;
    font-size: 24rpx;
    cursor: pointer;
  }
  
  .helper-text {
    font-size: 24rpx;
  }
  
  .completion-screen {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40rpx 30rpx;
  }
  
  .completion-content {
    text-align: center;
    width: 100%;
  }
  
  .completion-icon {
    font-size: 120rpx;
    margin-bottom: 40rpx;
  }
  
  .completion-title {
    display: block;
    font-size: 48rpx;
    font-weight: 700;
    color: #333333;
    margin-bottom: 15rpx;
  }
  
  .completion-desc {
    display: block;
    font-size: 28rpx;
    color: #666666;
    margin-bottom: 60rpx;
  }
  
  .completion-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 60rpx;
    padding: 40rpx;
    background: #ffffff;
    border-radius: 20rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  }
  
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .stat-number {
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
  
  .completion-btn {
    height: 80rpx;
    border: none;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: 600;
    cursor: pointer;
  }
  
  .completion-btn.primary {
    background: linear-gradient(135deg, #007aff 0%, #5856d6 100%);
    color: #ffffff;
  }
  
  .completion-btn.secondary {
    background: #f8f9fa;
    color: #333333;
    border: 1rpx solid #e9ecef;
  }
  
  .menu-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: flex-end;
    z-index: 1000;
  }
  
  .menu-modal {
    width: 100%;
    background: #ffffff;
    border-radius: 20rpx 20rpx 0 0;
    padding: 40rpx 30rpx;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .menu-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
    padding-bottom: 20rpx;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .menu-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .close-btn {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .close-icon {
    font-size: 36rpx;
    color: #666666;
  }
  
  .menu-content {
    display: flex;
    flex-direction: column;
    gap: 5rpx;
  }
  
  .menu-item {
    display: flex;
    align-items: center;
    padding: 25rpx 20rpx;
    border-radius: 12rpx;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }
  
  .menu-item:active {
    background: #f8f9fa;
  }
  
  .menu-icon {
    font-size: 32rpx;
    margin-right: 20rpx;
    width: 40rpx;
    text-align: center;
  }
  
  .menu-text {
    font-size: 28rpx;
    color: #333333;
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .word-text {
      font-size: 60rpx;
    }
    
    .action-row {
      flex-direction: column;
    }
    
    .action-btn {
      height: 70rpx;
    }
    
    .completion-stats {
      padding: 30rpx;
    }
  }
</style>