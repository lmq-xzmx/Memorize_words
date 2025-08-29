<template>
  <view class="review-container">
    <!-- 顶部状态栏 -->
    <view class="status-bar">
      <view class="status-left">
        <text class="time">{{ currentTime }}</text>
      </view>
      <view class="status-right">
        <text class="battery">{{ batteryLevel }}%</text>
      </view>
    </view>

    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <view class="nav-center">
        <text class="nav-title">单词复习</text>
      </view>
      <view class="nav-right">
        <text class="filter-btn" @tap="showFilterModal">筛选</text>
      </view>
    </view>

    <!-- 复习统计 -->
    <view class="stats-section">
      <view class="stat-card">
        <text class="stat-number">{{ reviewStats.totalWords }}</text>
        <text class="stat-label">待复习</text>
      </view>
      <view class="stat-card">
        <text class="stat-number">{{ reviewStats.masteredWords }}</text>
        <text class="stat-label">已掌握</text>
      </view>
      <view class="stat-card">
        <text class="stat-number">{{ reviewStats.reviewedToday }}</text>
        <text class="stat-label">今日复习</text>
      </view>
    </view>

    <!-- 复习模式选择 -->
    <view class="mode-section">
      <text class="section-title">复习模式</text>
      <view class="mode-grid">
        <view 
          v-for="mode in reviewModes" 
          :key="mode.id"
          class="mode-card"
          @tap="selectMode(mode)"
        >
          <view class="mode-icon">{{ mode.icon }}</view>
          <text class="mode-name">{{ mode.name }}</text>
          <text class="mode-desc">{{ mode.description }}</text>
        </view>
      </view>
    </view>

    <!-- 单词列表 -->
    <view class="words-section">
      <view class="section-header">
        <text class="section-title">复习单词</text>
        <text class="word-count">共{{ filteredWords.length }}个单词</text>
      </view>
      
      <view class="words-list">
        <view 
          v-for="word in filteredWords" 
          :key="word.id"
          class="word-item"
          @tap="reviewWord(word)"
        >
          <view class="word-content">
            <view class="word-main">
              <text class="word-text">{{ word.word }}</text>
              <text class="word-phonetic">{{ word.phonetic }}</text>
            </view>
            <text class="word-meaning">{{ word.meaning }}</text>
            <view class="word-meta">
              <text class="difficulty-tag" :class="word.difficulty">{{ getDifficultyText(word.difficulty) }}</text>
              <text class="review-count">复习{{ word.reviewCount }}次</text>
            </view>
          </view>
          <view class="word-actions">
            <view class="mastery-level" :class="word.masteryLevel">
              <text class="mastery-text">{{ getMasteryText(word.masteryLevel) }}</text>
            </view>
            <view class="action-btn" @tap.stop="toggleBookmark(word)">
              <text class="bookmark-icon" :class="{ active: word.isBookmarked }">{{ word.isBookmarked ? '★' : '☆' }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 筛选弹窗 -->
    <view v-if="showFilter" class="modal-overlay" @tap="closeFilterModal">
      <view class="modal-content filter-modal" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">筛选条件</text>
          <view class="close-btn" @tap="closeFilterModal">
            <text>✕</text>
          </view>
        </view>
        
        <view class="filter-section">
          <text class="filter-label">难度等级</text>
          <view class="filter-options">
            <view 
              v-for="difficulty in difficultyOptions" 
              :key="difficulty.value"
              class="filter-option"
              :class="{ active: selectedDifficulty === difficulty.value }"
              @tap="selectDifficulty(difficulty.value)"
            >
              <text class="option-text">{{ difficulty.label }}</text>
            </view>
          </view>
        </view>
        
        <view class="filter-section">
          <text class="filter-label">掌握程度</text>
          <view class="filter-options">
            <view 
              v-for="mastery in masteryOptions" 
              :key="mastery.value"
              class="filter-option"
              :class="{ active: selectedMastery === mastery.value }"
              @tap="selectMastery(mastery.value)"
            >
              <text class="option-text">{{ mastery.label }}</text>
            </view>
          </view>
        </view>
        
        <view class="filter-actions">
          <button class="filter-btn reset" @tap="resetFilters">重置</button>
          <button class="filter-btn apply" @tap="applyFilters">应用</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'WordReview',
  data() {
    return {
      currentTime: '',
      batteryLevel: 85,
      showFilter: false,
      selectedDifficulty: 'all',
      selectedMastery: 'all',
      reviewStats: {
        totalWords: 156,
        masteredWords: 89,
        reviewedToday: 23
      },
      reviewModes: [
        {
          id: 'flashcard',
          name: '闪卡模式',
          description: '快速记忆',
          icon: '📚'
        },
        {
          id: 'quiz',
          name: '测试模式',
          description: '选择题练习',
          icon: '📝'
        },
        {
          id: 'spelling',
          name: '拼写模式',
          description: '拼写练习',
          icon: '✏️'
        },
        {
          id: 'listening',
          name: '听力模式',
          description: '听音识词',
          icon: '🎧'
        }
      ],
      words: [
        {
          id: 1,
          word: 'challenge',
          phonetic: '/ˈtʃælɪndʒ/',
          meaning: '挑战；质疑',
          difficulty: 'medium',
          masteryLevel: 'learning',
          reviewCount: 3,
          isBookmarked: true,
          lastReview: '2024-01-15'
        },
        {
          id: 2,
          word: 'opportunity',
          phonetic: '/ˌɒpəˈtjuːnəti/',
          meaning: '机会；时机',
          difficulty: 'hard',
          masteryLevel: 'familiar',
          reviewCount: 5,
          isBookmarked: false,
          lastReview: '2024-01-14'
        },
        {
          id: 3,
          word: 'practice',
          phonetic: '/ˈpræktɪs/',
          meaning: '练习；实践',
          difficulty: 'easy',
          masteryLevel: 'mastered',
          reviewCount: 8,
          isBookmarked: true,
          lastReview: '2024-01-13'
        },
        {
          id: 4,
          word: 'knowledge',
          phonetic: '/ˈnɒlɪdʒ/',
          meaning: '知识；学问',
          difficulty: 'medium',
          masteryLevel: 'learning',
          reviewCount: 2,
          isBookmarked: false,
          lastReview: '2024-01-15'
        },
        {
          id: 5,
          word: 'experience',
          phonetic: '/ɪkˈspɪəriəns/',
          meaning: '经验；体验',
          difficulty: 'medium',
          masteryLevel: 'familiar',
          reviewCount: 4,
          isBookmarked: true,
          lastReview: '2024-01-12'
        }
      ],
      difficultyOptions: [
        { value: 'all', label: '全部' },
        { value: 'easy', label: '简单' },
        { value: 'medium', label: '中等' },
        { value: 'hard', label: '困难' }
      ],
      masteryOptions: [
        { value: 'all', label: '全部' },
        { value: 'learning', label: '学习中' },
        { value: 'familiar', label: '熟悉' },
        { value: 'mastered', label: '已掌握' }
      ]
    }
  },
  computed: {
    filteredWords() {
      return this.words.filter(word => {
        const difficultyMatch = this.selectedDifficulty === 'all' || word.difficulty === this.selectedDifficulty
        const masteryMatch = this.selectedMastery === 'all' || word.masteryLevel === this.selectedMastery
        return difficultyMatch && masteryMatch
      })
    }
  },
  mounted() {
    this.updateTime()
    setInterval(this.updateTime, 1000)
  },
  methods: {
    updateTime() {
      const now = new Date()
      this.currentTime = now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    goBack() {
      uni.navigateBack()
    },
    showFilterModal() {
      this.showFilter = true
    },
    closeFilterModal() {
      this.showFilter = false
    },
    selectMode(mode) {
      uni.showToast({
        title: `选择了${mode.name}`,
        icon: 'none'
      })
    },
    reviewWord(word) {
      uni.showToast({
        title: `开始复习: ${word.word}`,
        icon: 'none'
      })
    },
    toggleBookmark(word) {
      word.isBookmarked = !word.isBookmarked
      uni.showToast({
        title: word.isBookmarked ? '已收藏' : '已取消收藏',
        icon: 'none'
      })
    },
    getDifficultyText(difficulty) {
      const texts = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      }
      return texts[difficulty] || '未知'
    },
    getMasteryText(level) {
      const texts = {
        learning: '学习中',
        familiar: '熟悉',
        mastered: '已掌握'
      }
      return texts[level] || '未知'
    },
    selectDifficulty(difficulty) {
      this.selectedDifficulty = difficulty
    },
    selectMastery(mastery) {
      this.selectedMastery = mastery
    },
    resetFilters() {
      this.selectedDifficulty = 'all'
      this.selectedMastery = 'all'
    },
    applyFilters() {
      this.closeFilterModal()
      uni.showToast({
        title: '筛选条件已应用',
        icon: 'success'
      })
    }
  }
}
</script>

<style scoped>
.review-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  font-size: 14px;
}

.nav-bar {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-left {
  width: 40px;
}

.back-icon {
  font-size: 24px;
  font-weight: bold;
}

.nav-center {
  flex: 1;
  text-align: center;
}

.nav-title {
  font-size: 18px;
  font-weight: bold;
}

.nav-right {
  width: 60px;
  text-align: right;
}

.filter-btn {
  font-size: 14px;
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
}

.stats-section {
  display: flex;
  padding: 20px;
  gap: 15px;
}

.stat-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.mode-section {
  padding: 0 20px 20px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin-bottom: 15px;
}

.mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.mode-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: all 0.2s;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.mode-card:active {
  transform: scale(0.98);
}

.mode-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.mode-name {
  display: block;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.mode-desc {
  font-size: 12px;
  color: #666;
}

.words-section {
  background: white;
  border-radius: 20px 20px 0 0;
  padding: 20px;
  min-height: 400px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.word-count {
  font-size: 14px;
  color: #666;
}

.words-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.word-item {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border-radius: 15px;
  padding: 20px;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.word-item:active {
  background: #e9ecef;
  border-color: #667eea;
}

.word-content {
  flex: 1;
}

.word-main {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.word-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.word-phonetic {
  font-size: 14px;
  color: #666;
}

.word-meaning {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.word-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.difficulty-tag {
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 12px;
  color: white;
}

.difficulty-tag.easy {
  background: #4CAF50;
}

.difficulty-tag.medium {
  background: #FF9800;
}

.difficulty-tag.hard {
  background: #f44336;
}

.review-count {
  font-size: 12px;
  color: #999;
}

.word-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.mastery-level {
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 12px;
}

.mastery-level.learning {
  background: #ffebee;
  color: #f44336;
}

.mastery-level.familiar {
  background: #fff3e0;
  color: #FF9800;
}

.mastery-level.mastered {
  background: #e8f5e8;
  color: #4CAF50;
}

.mastery-text {
  font-weight: bold;
}

.action-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 15px;
  background: #f0f0f0;
}

.bookmark-icon {
  font-size: 16px;
  color: #ccc;
  transition: color 0.2s;
}

.bookmark-icon.active {
  color: #FFD700;
}

.modal-overlay {
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
  border-radius: 20px;
  padding: 30px;
  margin: 20px;
  max-width: 400px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.close-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 15px;
  font-size: 16px;
  color: #666;
}

.filter-section {
  margin-bottom: 25px;
}

.filter-label {
  display: block;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-option {
  padding: 10px 15px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  transition: all 0.2s;
}

.filter-option.active {
  background: #667eea;
  border-color: #667eea;
}

.filter-option.active .option-text {
  color: white;
}

.option-text {
  font-size: 14px;
  color: #333;
}

.filter-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.filter-btn {
  flex: 1;
  height: 45px;
  border: none;
  border-radius: 22px;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.2s;
}

.filter-btn.reset {
  background: #f0f0f0;
  color: #333;
}

.filter-btn.apply {
  background: #667eea;
  color: white;
}

.filter-btn:active {
  transform: scale(0.98);
}
</style>