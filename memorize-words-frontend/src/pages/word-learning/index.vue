<template>
  <view class="word-learning-container">
    <!-- 顶部状态栏 -->
    <view class="status-bar">
      <view class="time">{{ currentTime }}</view>
      <view class="status-icons">
        <text class="signal">📶</text>
        <text class="wifi">📶</text>
        <text class="battery">{{ batteryLevel }}%</text>
      </view>
    </view>

    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="back-btn" @tap="goBack">
        <text class="arrow">←</text>
      </view>
      <view class="nav-info">
        <view class="nav-text">新单词 {{ newWordsCount }}</view>
        <view class="nav-text">需复习 {{ reviewWordsCount }}</view>
      </view>
    </view>

    <!-- 单词显示区域 -->
    <view class="word-section">
      <view class="word-header" v-if="currentWord">
        <text class="word-text">{{ currentWord.word }}</text>
        <text class="phonetic-text">{{ currentWord.pronunciation }}</text>
      </view>
      <view class="word-stats">
        <view class="stat-item">
          <text class="stat-number">{{ studyProgress.learned }}</text>
          <text class="stat-label">已学</text>
        </view>
        <view class="stat-item">
          <text class="stat-number">{{ studyProgress.total - studyProgress.learned }}</text>
          <text class="stat-label">剩余</text>
        </view>
        <view class="stat-item">
          <text class="stat-number">{{ currentWordIndex + 1 }}/{{ totalWords }}</text>
          <text class="stat-label">进度</text>
        </view>
      </view>
    </view>

    <!-- 图片卡片区域 -->
    <view class="cards-section" v-if="wordCards.length > 0">
      <view 
        class="word-card" 
        v-for="(card, index) in wordCards" 
        :key="card.id"
        :class="{ 'card-selected': card.selected, 'card-correct': card.selected && card.isCorrect, 'card-wrong': card.selected && !card.isCorrect }"
        @click="selectCard(card)"
      >
        <image 
          class="card-image" 
          :src="card.image" 
          mode="aspectFill"
          @error="handleImageError(index)"
        />
        <view class="card-content">
          <view class="card-type">{{ card.type || currentWord?.partOfSpeech }}</view>
          <view class="card-meaning">{{ card.meaning }}</view>
          <view class="card-example" v-if="showAnalysis && card.example">{{ card.example }}</view>
        </view>
        <view class="card-indicator" v-if="card.selected">
          <text class="indicator-icon">{{ card.isCorrect ? '✓' : '✗' }}</text>
        </view>
      </view>
    </view>
    
    <!-- 加载状态 -->
    <view class="loading-section" v-if="loading">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 底部控制栏 -->
    <view class="bottom-controls">
      <view class="control-item" @click="toggleAnalysis">
        <text class="control-icon">📊</text>
        <text class="control-label">{{ showAnalysis ? '隐藏分析' : '显示分析' }}</text>
      </view>
      <view class="control-item" @click="toggleBookmark">
        <text class="control-icon" :class="{ 'bookmarked': isBookmarked }">{{ isBookmarked ? '⭐' : '☆' }}</text>
        <text class="control-label">收藏</text>
      </view>
      <view class="control-item" @click="playAudio" :class="{ 'disabled': isPlaying }">
        <text class="control-icon" :class="{ 'playing': isPlaying }">{{ isPlaying ? '🔊' : '🔉' }}</text>
        <text class="control-label">发音</text>
      </view>
      <view class="control-item" @click="skipWord">
        <text class="control-icon">⏭️</text>
        <text class="control-label">跳过</text>
      </view>
    </view>
  </view>
</template>

<script>
import { imageConfig } from '@/config/imageConfig'
import { audioConfig } from '@/config/audioConfig'
import { mockWords, getRandomWord, simulateApiDelay } from '@/utils/mockData'

export default {
  name: 'WordLearning',
  data() {
    return {
      currentTime: '',
      batteryLevel: 85,
      currentWord: null,
      wordCards: [],
      showAnalysis: false,
      isBookmarked: false,
      isPlaying: false,
      loading: false,
      currentWordIndex: 0,
      totalWords: mockWords.length,
      studyProgress: {
        learned: 0,
        total: 10
      }
    }
  },
  async mounted() {
    this.updateTime()
    setInterval(this.updateTime, 1000)
    await this.loadCurrentWord()
  },
  computed: {
    newWordsCount() {
      return this.studyProgress.total - this.studyProgress.learned
    },
    reviewWordsCount() {
      return Math.floor(this.studyProgress.learned * 0.3)
    }
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.currentTime = now.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })
    },
    
    async loadCurrentWord() {
      this.loading = true
      try {
        await simulateApiDelay(300)
        
        // 获取当前单词
        this.currentWord = mockWords[this.currentWordIndex] || getRandomWord()
        
        // 生成选项卡片
        this.generateWordCards()
        
        // 更新学习进度
        this.studyProgress.learned = Math.min(this.currentWordIndex + 1, this.studyProgress.total)
      } catch (error) {
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    generateWordCards() {
      if (!this.currentWord) return
      
      // 创建正确答案卡片
      const correctCard = {
        id: 1,
        image: this.currentWord.image,
        type: this.currentWord.type,
        meaning: this.currentWord.meaning,
        example: this.currentWord.example,
        isCorrect: true,
        selected: false
      }
      
      // 创建干扰项卡片
      const distractorWords = mockWords
        .filter(w => w.id !== this.currentWord.id)
        .sort(() => Math.random() - 0.5)
        .slice(0, 2)
      
      const distractorCards = distractorWords.map((word, index) => ({
        id: index + 2,
        image: word.image,
        type: word.type,
        meaning: word.meaning,
        example: word.example,
        isCorrect: false,
        selected: false
      }))
      
      // 随机排列卡片
      this.wordCards = [correctCard, ...distractorCards]
        .sort(() => Math.random() - 0.5)
        .map((card, index) => ({ ...card, id: index + 1 }))
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    selectCard(card) {
      // 重置所有卡片选中状态
      this.wordCards.forEach(c => {
        c.selected = false
      })
      
      // 选中当前卡片
      card.selected = true
      
      // 播放反馈音效
      if (card.isCorrect) {
        uni.showToast({
          title: '回答正确！',
          icon: 'success'
        })
        
        // 延迟加载下一个单词
        setTimeout(() => {
          this.nextWord()
        }, 1500)
      } else {
        uni.showToast({
          title: '回答错误，再试试',
          icon: 'none'
        })
      }
    },
    
    async nextWord() {
      if (this.currentWordIndex < this.totalWords - 1) {
        this.currentWordIndex++
        await this.loadCurrentWord()
      } else {
        uni.showModal({
          title: '恭喜',
          content: '您已完成所有单词的学习！',
          showCancel: false,
          success: () => {
            this.goBack()
          }
        })
      }
    },
    
    toggleAnalysis() {
      this.showAnalysis = !this.showAnalysis
      uni.showToast({
        title: this.showAnalysis ? '显示分析' : '隐藏分析',
        icon: 'none'
      })
    },
    
    toggleBookmark() {
      this.isBookmarked = !this.isBookmarked
      uni.showToast({
        title: this.isBookmarked ? '已收藏' : '已取消收藏',
        icon: 'none'
      })
    },
    
    async playAudio() {
      if (this.isPlaying || !this.currentWord) return
      
      this.isPlaying = true
      try {
        // 模拟音频播放
        await new Promise(resolve => setTimeout(resolve, 1000))
        uni.showToast({
          title: '播放完成',
          icon: 'none'
        })
      } catch (error) {
        uni.showToast({
          title: '播放失败',
          icon: 'none'
        })
      } finally {
        this.isPlaying = false
      }
    },
    
    handleImageError() {
      console.log('图片加载失败')
    },
    
    skipWord() {
      uni.showModal({
        title: '跳过单词',
        content: '确定要跳过这个单词吗？',
        success: (res) => {
          if (res.confirm) {
            this.nextWord()
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.word-learning-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.1);
}

.status-icons {
  display: flex;
  gap: 8px;
}

.nav-bar {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  gap: 20px;
}

.back-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
}

.arrow {
  font-size: 18px;
  font-weight: bold;
}

.nav-info {
  display: flex;
  gap: 20px;
}

.nav-text {
  font-size: 14px;
  opacity: 0.9;
}

.word-display {
  text-align: center;
  padding: 40px 20px;
}

.word-text {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.word-phonetic {
  font-size: 18px;
  opacity: 0.8;
  font-style: italic;
}

/* 图片卡片样式 */
.cards-section {
  padding: 20px;
}

.word-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
  border-radius: 16px;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  position: relative;
  padding: 20px;
  display: flex;
  gap: 15px;
  color: #333;
}

.word-card:active {
  transform: scale(0.98);
}

.word-card.card-selected {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.word-card.card-correct {
  border-color: #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
}

.word-card.card-wrong {
  border-color: #ef4444;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
}

.card-image {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  overflow: hidden;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  flex: 1;
}

.card-type {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-meaning {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  line-height: 1.3;
}

.card-example {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
  font-style: italic;
  padding: 8px 12px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 8px;
  margin-top: 8px;
}

.card-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.indicator-icon {
  font-size: 18px;
  font-weight: bold;
}

.card-correct .indicator-icon {
  color: #10b981;
}

.card-wrong .indicator-icon {
  color: #ef4444;
}

/* 加载状态样式 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.bottom-controls {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
  backdrop-filter: blur(20px);
  padding: 20px;
  display: flex;
  justify-content: space-around;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
}

.control-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  min-width: 60px;
}

.control-item:active {
  transform: scale(0.95);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.control-item.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.control-icon {
  font-size: 24px;
  margin-bottom: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.control-icon.bookmarked {
  color: #fbbf24;
  transform: scale(1.1);
}

.control-icon.playing {
  color: #10b981;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.control-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  text-align: center;
  line-height: 1.2;
}
</style>