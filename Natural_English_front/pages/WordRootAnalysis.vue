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
import { getDefaultPlaceholder, handleImageError, IMAGE_TYPES } from '../utils/imageConfig';

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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.status-icons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
}

.back-btn {
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.arrow {
  font-size: 20px;
  font-weight: bold;
}

.nav-info {
  display: flex;
  gap: 20px;
}

.nav-text {
  font-size: 12px;
  opacity: 0.8;
}

.nav-right {
  text-align: right;
}

.nav-word {
  display: block;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 2px;
}

.nav-details {
  font-size: 12px;
  opacity: 0.8;
}

.word-root-display {
  padding: 30px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  margin: 20px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.word-breakdown {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.root-part {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  padding: 15px 25px;
  border-radius: 15px;
  font-size: 18px;
  font-weight: 600;
  color: #667eea;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.root-part:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.root-prefix {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
}

.root-suffix {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #667eea;
}

.root-separator {
  font-size: 24px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.root-explanation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  color: white;
  font-size: 14px;
}

.prefix-meaning,
.suffix-meaning {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 15px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.word-formation {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  padding: 8px 15px;
  border-radius: 20px;
  font-weight: 600;
}

.cards-container {
  flex: 1;
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  overflow-y: auto;
}

.word-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.word-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.card-image {
  height: 120px;
  overflow: hidden;
  position: relative;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.word-card:hover .card-image img {
  transform: scale(1.05);
}

.card-content {
  padding: 15px;
}

.card-type {
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.card-meaning {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 5px;
  line-height: 1.4;
}

.card-example {
  font-size: 12px;
  color: #718096;
  line-height: 1.3;
}

.bottom-controls {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 25px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.control-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.slash-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
}

.slash-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 10px 25px rgba(255, 107, 107, 0.3);
}

.light-btn {
  background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
  color: white;
}

.light-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 10px 25px rgba(254, 202, 87, 0.3);
}

.detail-btn {
  background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%);
  color: white;
}

.detail-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 10px 25px rgba(72, 219, 251, 0.3);
}

.control-text {
  font-size: 18px;
  font-weight: 600;
}

.control-icon {
  font-size: 20px;
}

@media (max-width: 768px) {
  .cards-container {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .word-breakdown {
    flex-direction: column;
    gap: 10px;
  }
  
  .root-explanation {
    flex-direction: column;
    gap: 8px;
  }
  
  .nav-info {
    gap: 10px;
  }
  
  .bottom-controls {
    gap: 25px;
  }
  
  .control-btn {
    width: 50px;
    height: 50px;
  }
}

@media (max-width: 480px) {
  .word-root-display {
    margin: 10px;
    padding: 20px 15px;
  }
  
  .root-part {
    padding: 10px 15px;
    font-size: 16px;
  }
  
  .cards-container {
    padding: 15px;
  }
  
  .card-image {
    height: 100px;
  }
  
  .nav-bar {
    padding: 10px 15px;
  }
  
  .nav-right {
    font-size: 12px;
  }
}
</style>

