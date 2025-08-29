<template>
  <view class="review-page">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-section">
      <view class="loading-spinner"></view>
      <text class="loading-text">正在加载复习内容...</text>
    </view>

    <!-- 复习内容 -->
    <view v-else class="review-content">
      <!-- 头部统计 -->
      <view class="review-header">
        <view class="stats-section">
          <view class="stat-item">
            <text class="stat-number">{{ reviewStats.total }}</text>
            <text class="stat-label">总计</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ reviewStats.reviewed }}</text>
            <text class="stat-label">已复习</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ reviewStats.remembered }}</text>
            <text class="stat-label">已掌握</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ reviewStats.needReview }}</text>
            <text class="stat-label">需复习</text>
          </view>
        </view>
        
        <view class="mode-selector">
          <view 
            v-for="mode in [{ key: 'flashcard', name: '卡片' }, { key: 'list', name: '列表' }]" 
            :key="mode.key"
            class="mode-option"
            :class="{ active: reviewMode === mode.key }"
            @click="changeReviewMode(mode.key)"
          >
            <text class="mode-text">{{ mode.name }}</text>
          </view>
        </view>
      </view>

      <!-- 卡片模式 -->
      <view v-if="reviewMode === 'flashcard'" class="flashcard-section">
        <view v-if="currentWord" class="flashcard-container">
          <!-- 进度条 -->
          <view class="progress-section">
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: progress + '%' }"></view>
            </view>
            <text class="progress-text">{{ currentWordIndex + 1 }} / {{ reviewWords.length }}</text>
          </view>
          
          <!-- 单词卡片 -->
          <view class="word-card" :class="{ flipped: showAnswer }">
            <view class="card-front">
              <view class="word-header">
                <text class="word-text">{{ currentWord.word }}</text>
                <button class="audio-btn" @click="playWordAudio">
                  <text class="audio-icon">🔊</text>
                </button>
              </view>
              
              <view class="word-image">
                <image :src="getWordImage(currentWord.word)" class="word-img" mode="aspectFit"></image>
              </view>
              
              <view class="word-phonetic">
                <text class="phonetic-text">{{ currentWord.phonetic }}</text>
              </view>
              
              <button class="reveal-btn" @click="toggleAnswer">
                <text class="reveal-text">点击查看释义</text>
              </button>
            </view>
            
            <view v-if="showAnswer" class="card-back">
              <view class="word-meanings">
                <view v-for="(meaning, index) in currentWord.meanings" :key="index" class="meaning-item">
                  <text class="meaning-type">{{ meaning.partOfSpeech }}</text>
                  <text class="meaning-text">{{ meaning.definition }}</text>
                  <text v-if="meaning.example" class="meaning-example">{{ meaning.example }}</text>
                </view>
              </view>
              
              <view class="review-actions">
                <button class="action-btn need-review" @click="markAsNeedReview">
                  <text class="action-text">需要复习</text>
                </button>
                <button class="action-btn remembered" @click="markAsRemembered">
                  <text class="action-text">已掌握</text>
                </button>
              </view>
            </view>
          </view>
          
          <!-- 导航按钮 -->
          <view class="navigation-section">
            <button class="nav-btn" :class="{ disabled: currentWordIndex === 0 }" @click="prevWord">
              <text class="nav-text">上一个</text>
            </button>
            <button class="nav-btn" :class="{ disabled: currentWordIndex === reviewWords.length - 1 }" @click="nextWord">
              <text class="nav-text">下一个</text>
            </button>
          </view>
        </view>
        
        <view v-else class="empty-state">
          <text class="empty-text">暂无复习内容</text>
          <button class="reload-btn" @click="loadReviewWords">
            <text class="reload-text">重新加载</text>
          </button>
        </view>
      </view>

      <!-- 列表模式 -->
      <view v-else-if="reviewMode === 'list'" class="list-section">
        <!-- 过滤和排序 -->
        <view class="filter-section">
          <view class="filter-group">
            <text class="filter-label">过滤:</text>
            <view class="filter-options">
              <view 
                v-for="filter in [{ key: 'all', name: '全部' }, { key: 'difficult', name: '困难' }, { key: 'recent', name: '最近' }]" 
                :key="filter.key"
                class="filter-option"
                :class="{ active: filterType === filter.key }"
                @click="changeFilter(filter.key)"
              >
                <text class="filter-text">{{ filter.name }}</text>
              </view>
            </view>
          </view>
          
          <view class="sort-group">
            <text class="sort-label">排序:</text>
            <view class="sort-options">
              <view 
                v-for="sort in [{ key: 'date', name: '日期' }, { key: 'difficulty', name: '难度' }, { key: 'alphabetical', name: '字母' }]" 
                :key="sort.key"
                class="sort-option"
                :class="{ active: sortBy === sort.key }"
                @click="changeSort(sort.key)"
              >
                <text class="sort-text">{{ sort.name }}</text>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 单词列表 -->
        <view class="word-list">
          <view 
            v-for="(word, index) in filteredWords" 
            :key="word.id"
            class="word-list-item"
            :class="{ 
              reviewed: word.reviewed,
              remembered: word.remembered,
              needReview: word.needReview
            }"
            @click="goToWord(reviewWords.indexOf(word))"
          >
            <view class="word-info">
              <text class="word-name">{{ word.word }}</text>
              <text class="word-phonetic">{{ word.phonetic }}</text>
              <text class="word-meaning">{{ word.meanings[0]?.definition }}</text>
            </view>
            
            <view class="word-status">
              <view v-if="word.remembered" class="status-badge remembered">
                <text class="status-text">已掌握</text>
              </view>
              <view v-else-if="word.needReview" class="status-badge need-review">
                <text class="status-text">需复习</text>
              </view>
              <view v-else-if="word.reviewed" class="status-badge reviewed">
                <text class="status-text">已复习</text>
              </view>
              <view v-else class="status-badge pending">
                <text class="status-text">待复习</text>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 底部操作栏 -->
      <view class="bottom-actions">
        <button class="action-btn secondary" @click="resetReview">
          <text class="action-text">重置复习</text>
        </button>
        <button class="action-btn primary" @click="$uni.navigateBack()">
          <text class="action-text">返回首页</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script>
import { mockData, getReviewWords, simulateApiDelay } from '@/utils/mockData'
import { playAudio, playSuccessSound } from '@/config/audioConfig'
import { getWordImage } from '@/config/imageConfig'

export default {
  name: 'Review',
  data() {
    return {
      loading: true,
      reviewWords: [],
      currentWordIndex: 0,
      reviewMode: 'flashcard', // flashcard, list, quiz
      showAnswer: false,
      reviewStats: {
        total: 0,
        reviewed: 0,
        remembered: 0,
        needReview: 0
      },
      filterType: 'all', // all, difficult, recent
      sortBy: 'date' // date, difficulty, alphabetical
    }
  },
  computed: {
    currentWord() {
      return this.reviewWords[this.currentWordIndex] || null
    },
    progress() {
      return this.reviewWords.length > 0 ? (this.currentWordIndex / this.reviewWords.length) * 100 : 0
    },
    filteredWords() {
      let words = [...this.reviewWords]
      
      // 应用过滤器
      if (this.filterType === 'difficult') {
        words = words.filter(word => word.difficulty === 'hard' || word.reviewCount > 3)
      } else if (this.filterType === 'recent') {
        const threeDaysAgo = Date.now() - 3 * 24 * 60 * 60 * 1000
        words = words.filter(word => new Date(word.lastReviewed).getTime() > threeDaysAgo)
      }
      
      // 应用排序
      if (this.sortBy === 'date') {
        words.sort((a, b) => new Date(b.lastReviewed) - new Date(a.lastReviewed))
      } else if (this.sortBy === 'difficulty') {
        const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3 }
        words.sort((a, b) => difficultyOrder[b.difficulty] - difficultyOrder[a.difficulty])
      } else if (this.sortBy === 'alphabetical') {
        words.sort((a, b) => a.word.localeCompare(b.word))
      }
      
      return words
    }
  },
  async mounted() {
    await this.loadReviewWords()
  },
  methods: {
    async loadReviewWords() {
      this.loading = true
      await simulateApiDelay()
      
      this.reviewWords = getReviewWords()
      this.updateReviewStats()
      this.loading = false
    },
    
    updateReviewStats() {
      this.reviewStats = {
        total: this.reviewWords.length,
        reviewed: this.reviewWords.filter(w => w.reviewed).length,
        remembered: this.reviewWords.filter(w => w.remembered).length,
        needReview: this.reviewWords.filter(w => w.needReview).length
      }
    },
    
    nextWord() {
      if (this.currentWordIndex < this.reviewWords.length - 1) {
        this.currentWordIndex++
        this.showAnswer = false
      }
    },
    
    prevWord() {
      if (this.currentWordIndex > 0) {
        this.currentWordIndex--
        this.showAnswer = false
      }
    },
    
    toggleAnswer() {
      this.showAnswer = !this.showAnswer
      if (this.showAnswer && !this.currentWord.reviewed) {
        this.markAsReviewed()
      }
    },
    
    markAsRemembered() {
      if (this.currentWord) {
        this.currentWord.remembered = true
        this.currentWord.reviewed = true
        this.currentWord.needReview = false
        this.updateReviewStats()
        playSuccessSound()
        
        setTimeout(() => {
          this.nextWord()
        }, 500)
      }
    },
    
    markAsNeedReview() {
      if (this.currentWord) {
        this.currentWord.needReview = true
        this.currentWord.reviewed = true
        this.currentWord.remembered = false
        this.updateReviewStats()
        
        setTimeout(() => {
          this.nextWord()
        }, 500)
      }
    },
    
    markAsReviewed() {
      if (this.currentWord && !this.currentWord.reviewed) {
        this.currentWord.reviewed = true
        this.updateReviewStats()
      }
    },
    
    playWordAudio() {
      if (this.currentWord) {
        playAudio(this.currentWord.word)
      }
    },
    
    getWordImage(word) {
      return getWordImage(word)
    },
    
    changeReviewMode(mode) {
      this.reviewMode = mode
      this.showAnswer = false
    },
    
    changeFilter(type) {
      this.filterType = type
    },
    
    changeSort(sortBy) {
      this.sortBy = sortBy
    },
    
    resetReview() {
      this.reviewWords.forEach(word => {
        word.reviewed = false
        word.remembered = false
        word.needReview = false
      })
      this.currentWordIndex = 0
      this.showAnswer = false
      this.updateReviewStats()
    },
    
    goToWord(index) {
      this.currentWordIndex = index
      this.showAnswer = false
      this.reviewMode = 'flashcard'
    }
  }
}
</script>

<style scoped>
.review-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 100px;
}

/* 加载状态样式 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 500;
}

/* 复习内容样式 */
.review-content {
  padding: 20px;
}

.review-header {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
}

.stats-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-number {
  font-size: 24px;
  color: #ffffff;
  font-weight: bold;
  margin-bottom: 4px;
  display: block;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.mode-selector {
  display: flex;
  gap: 8px;
}

.mode-option {
  flex: 1;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.mode-option.active {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
}

.mode-option.active .mode-text {
  color: #667eea;
  font-weight: 600;
}

.mode-text {
  font-size: 14px;
  color: #ffffff;
  font-weight: 500;
}

/* 卡片模式样式 */
.flashcard-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.flashcard-container {
  width: 100%;
  max-width: 400px;
}

.progress-section {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  display: block;
}

.word-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.word-card.flipped {
  transform: rotateY(180deg);
}

.card-front, .card-back {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.word-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.word-text {
  font-size: 32px;
  color: #1e293b;
  font-weight: bold;
}

.audio-btn {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.audio-icon {
  font-size: 18px;
}

.word-image {
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  background: #f8fafc;
}

.word-img {
  width: 100%;
  height: 100%;
}

.word-phonetic {
  margin-bottom: 20px;
}

.phonetic-text {
  font-size: 18px;
  color: #64748b;
  font-style: italic;
}

.reveal-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 24px;
  border: none;
}

.reveal-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
}

.word-meanings {
  margin-bottom: 30px;
}

.meaning-item {
  margin-bottom: 16px;
  text-align: left;
  width: 100%;
}

.meaning-type {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 4px;
  display: block;
}

.meaning-text {
  font-size: 18px;
  color: #1e293b;
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
}

.meaning-example {
  font-size: 14px;
  color: #64748b;
  font-style: italic;
  display: block;
}

.review-actions {
  display: flex;
  gap: 16px;
  width: 100%;
}

.action-btn {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-btn.need-review {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-btn.remembered {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.action-btn.primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.action-btn:active {
  transform: translateY(2px);
}

.action-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
}

.navigation-section {
  display: flex;
  gap: 16px;
}

.nav-btn {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  border: none;
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-btn.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.nav-btn:active {
  transform: translateY(2px);
}

.nav-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-text {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
  display: block;
}

.reload-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 24px;
  border: none;
}

.reload-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
}

/* 列表模式样式 */
.list-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-group, .sort-group {
  margin-bottom: 16px;
}

.filter-label, .sort-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
}

.filter-options, .sort-options {
  display: flex;
  gap: 8px;
}

.filter-option, .sort-option {
  padding: 8px 12px;
  background: #f1f5f9;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.filter-option.active, .sort-option.active {
  background: #667eea;
  transform: translateY(-1px);
}

.filter-option.active .filter-text, .sort-option.active .sort-text {
  color: #ffffff;
  font-weight: 600;
}

.filter-text, .sort-text {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.word-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.word-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.word-list-item:active {
  transform: scale(0.98);
}

.word-list-item.reviewed {
  border-color: #e2e8f0;
}

.word-list-item.remembered {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}

.word-list-item.needReview {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.05);
}

.word-info {
  flex: 1;
}

.word-name {
  font-size: 18px;
  color: #1e293b;
  font-weight: 600;
  margin-bottom: 4px;
  display: block;
}

.word-phonetic {
  font-size: 14px;
  color: #64748b;
  font-style: italic;
  margin-bottom: 4px;
  display: block;
}

.word-meaning {
  font-size: 14px;
  color: #64748b;
  display: block;
}

.word-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 12px;
}

.status-badge.remembered {
  background: rgba(16, 185, 129, 0.1);
}

.status-badge.need-review {
  background: rgba(245, 158, 11, 0.1);
}

.status-badge.reviewed {
  background: rgba(100, 116, 139, 0.1);
}

.status-badge.pending {
  background: rgba(148, 163, 184, 0.1);
}

.status-text {
  font-weight: 500;
}

.status-badge.remembered .status-text {
  color: #059669;
}

.status-badge.need-review .status-text {
  color: #d97706;
}

.status-badge.reviewed .status-text {
  color: #475569;
}

.status-badge.pending .status-text {
  color: #64748b;
}

/* 底部操作栏样式 */
.bottom-actions {
  display: flex;
  gap: 16px;
  margin-top: 20px;
}
</style>