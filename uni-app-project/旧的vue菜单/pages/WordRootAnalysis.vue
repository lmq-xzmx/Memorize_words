<template>
  <div class="word-root-analysis">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <span class="time">22:27</span>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">78%</span>
      </div>
    </div>

    <!-- 导航栏 -->
    <div class="nav-bar">
      <div class="back-btn" @click="goBack">
        <span class="arrow">←</span>
      </div>
      <div class="nav-info">
        <div class="nav-text">新单词 50</div>
        <div class="nav-text">需复习 9</div>
      </div>
      <div class="nav-right">
        <span class="nav-word">{{ currentWord.word }}</span>
        <span class="nav-details">机构；制度；惯例；习俗</span>
      </div>
    </div>

    <!-- 词根分解显示区域 -->
    <div class="word-root-display">
      <div class="word-breakdown">
        <div class="root-part root-prefix">{{ currentWord.prefix }}</div>
        <div class="root-separator">+</div>
        <div class="root-part root-suffix">{{ currentWord.suffix }}</div>
      </div>
      <div class="root-explanation">
        <span class="prefix-meaning">{{ currentWord.prefixMeaning }}</span>
        <span class="suffix-meaning">{{ currentWord.suffixMeaning }}</span>
        <span class="word-formation">→{{ currentWord.formation }}</span>
      </div>
    </div>

    <!-- 图片卡片区域 -->
    <div class="cards-container">
      <div 
        v-for="(card, index) in wordCards" 
        :key="index"
        class="word-card"
        @click="selectCard(card)"
      >
        <div class="card-image">
          <img :src="card.image" :alt="card.alt" @error="handleImageError" />
        </div>
        <div class="card-content">
          <div class="card-type">{{ card.type }}</div>
          <div class="card-meaning">{{ card.meaning }}</div>
          <div class="card-example">{{ card.example }}</div>
        </div>
      </div>
    </div>

    <!-- 底部控制栏 -->
    <div class="bottom-controls">
      <div class="control-btn slash-btn" @click="markAsLearned">
        <span class="control-text">斩</span>
      </div>
      <div class="control-btn light-btn" @click="toggleVocabulary">
        <span class="control-icon">💡</span>
      </div>
      <div class="control-btn detail-btn" @click="openWordDetail">
        <span class="control-text">详</span>
      </div>
    </div>
  </div>
</template>

<script>
import { getDefaultPlaceholder, handleImageError, IMAGE_TYPES } from '../utils/imageConfig.js';

export default {
  name: 'WordRootAnalysis',
  data() {
    return {
      currentWord: {
        word: 'institution',
        prefix: 'altern',
        suffix: 'ative',
        prefixMeaning: 'altern另外的',
        suffixMeaning: '+ative形容词/名词后缀',
        formation: 'alternative替换的，...'
      },
      wordCards: [
        {
          type: 'Plan A',
          meaning: 'adj.可供选择的',
          example: 'n.可供选择...',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: 'Plan A图片'
        },
        {
          type: 'Plan B',
          meaning: 'n.安慰；慰藉；减轻；缓解',
          example: '',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: 'Plan B图片'
        },
        {
          type: 'vt.引起',
          meaning: '造成；创造；产...',
          example: '',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: '引起图片'
        },
        {
          type: 'adj.为数众多的',
          meaning: '许多的',
          example: '',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: '众多图片'
        }
      ],
      isVocabularyOpen: false
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1)
    },
    selectCard(card) {
      console.log('选择卡片:', card)
      // 这里可以添加卡片选择逻辑
    },
    markAsLearned() {
      console.log('标记为已学会')
      // 这里可以添加标记学习状态的逻辑
      this.$router.go(-1) // 返回上一页
    },
    toggleVocabulary() {
      this.isVocabularyOpen = !this.isVocabularyOpen
      console.log('切换词汇显示:', this.isVocabularyOpen ? '打开' : '关闭')
      // 这里可以添加打开/关闭词汇的逻辑
    },
    openWordDetail() {
      console.log('打开单词详情')
      // 跳转到单词详情页面
      this.$router.push(`/word-detail/${this.currentWord.word}`)
    },
    handleImageError(event) {
      handleImageError(event, IMAGE_TYPES.WORD_EXAMPLE);
    }
  }
}
</script>

<style scoped>
.word-root-analysis {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 状态栏样式 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  background: #000;
  color: white;
  font-size: 14px;
  font-weight: 600;
}

.status-icons {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 导航栏样式 */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #eee;
}

.back-btn {
  padding: 5px;
  cursor: pointer;
}

.arrow {
  font-size: 18px;
  color: #333;
}

.nav-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-text {
  font-size: 12px;
  color: #666;
}

.nav-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.nav-word {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.nav-details {
  font-size: 12px;
  color: #666;
}

/* 词根分解显示区域 */
.word-root-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: white;
}

.word-breakdown {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.root-part {
  font-size: 48px;
  font-weight: 300;
  letter-spacing: 1px;
}

.root-prefix {
  color: #4A90E2;
}

.root-suffix {
  color: #4A90E2;
}

.root-separator {
  font-size: 36px;
  color: #999;
  margin: 0 5px;
}

.root-explanation {
  text-align: center;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.prefix-meaning,
.suffix-meaning,
.word-formation {
  display: block;
  margin-bottom: 4px;
}

.word-formation {
  color: #333;
  font-weight: 500;
}

/* 图片卡片区域 */
.cards-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 20px;
  background: #f5f5f5;
}

.word-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.word-card:hover {
  transform: translateY(-2px);
}

.card-image {
  height: 100px;
  background: #e8f4f8;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  padding: 12px;
}

.card-type {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.card-meaning {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  margin-bottom: 4px;
  line-height: 1.3;
}

.card-example {
  font-size: 12px;
  color: #999;
}

/* 底部控制栏 */
.bottom-controls {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 20px;
  background: white;
  border-top: 1px solid #eee;
}

.control-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: #e0e0e0;
  transform: scale(1.05);
}

.slash-btn {
  background: #ff6b6b;
  color: white;
}

.slash-btn:hover {
  background: #ff5252;
}

.light-btn {
  background: #ffd93d;
}

.light-btn:hover {
  background: #ffcd02;
}

.detail-btn {
  background: #4ecdc4;
  color: white;
}

.detail-btn:hover {
  background: #26a69a;
}

.control-text {
  font-size: 18px;
  font-weight: 600;
}

.control-icon {
  font-size: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .root-part {
    font-size: 36px;
  }
  
  .root-separator {
    font-size: 28px;
  }
  
  .cards-container {
    padding: 15px;
    gap: 8px;
  }
  
  .card-content {
    padding: 10px;
  }
  
  .bottom-controls {
    gap: 30px;
  }
}
</style>