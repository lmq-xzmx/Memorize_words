<template>
  <div class="word-learning-container">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <div class="time">22:26</div>
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
    </div>

    <!-- 单词显示区域 -->
    <div class="word-display">
      <div class="word-main">
        <h1 class="word-text">{{ currentWord.word }}</h1>
        <p class="word-phonetic">{{ currentWord.phonetic }}</p>
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
      <div class="control-btn" @click="toggleAnalysis">
        <span class="control-icon">📊</span>
      </div>
      <div class="control-btn" @click="toggleBookmark">
        <span class="control-icon">🔖</span>
      </div>
      <div class="control-btn" @click="playAudio">
        <span class="control-icon">🔊</span>
      </div>
    </div>
    
    <!-- 子路由视图 -->
    <router-view></router-view>
  </div>
</template>

<script>
import { getDefaultPlaceholder, handleImageError, IMAGE_TYPES } from '../utils/imageConfig.js';

export default {
  name: 'WordLearning',
  data() {
    return {
      currentWord: {
        word: 'institution',
        phonetic: '/ˌɪnstɪˈtuːʃn/'
      },
      wordCards: [
        {
          type: 'n.机构',
          meaning: 'adj.激烈的',
          example: '例句：习俗',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: '机构图片'
        },
        {
          type: 'n.机构',
          meaning: '制度；惯例；习俗',
          example: '例句：习俗',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: '制度图片'
        },
        {
          type: 'n.众多',
          meaning: '群众；水量；v...',
          example: '例句：群众',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: '群众图片'
        },
        {
          type: 'v.增强',
          meaning: '加剧',
          example: '例句：加剧',
          image: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
          alt: '增强图片'
        }
      ]
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
    toggleAnalysis() {
      console.log('切换分析模式')
    },
    toggleBookmark() {
      console.log('切换书签')
    },
    playAudio() {
      console.log('播放音频')
      // 这里可以添加音频播放逻辑
    },
    handleImageError(event) {
      handleImageError(event, IMAGE_TYPES.WORD_EXAMPLE);
    }
  }
}
</script>

<style scoped>
.word-learning-container {
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
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #eee;
}

.back-btn {
  padding: 5px;
  cursor: pointer;
  margin-right: 15px;
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

/* 单词显示区域 */
.word-display {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: white;
}

.word-main {
  text-align: center;
}

.word-text {
  font-size: 48px;
  font-weight: 300;
  color: #4A90E2;
  margin: 0 0 10px 0;
  letter-spacing: 1px;
}

.word-phonetic {
  font-size: 18px;
  color: #999;
  margin: 0;
  font-style: italic;
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

.control-icon {
  font-size: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .word-text {
    font-size: 36px;
  }
  
  .word-phonetic {
    font-size: 16px;
  }
  
  .cards-container {
    padding: 15px;
    gap: 8px;
  }
  
  .card-content {
    padding: 10px;
  }
}
</style>