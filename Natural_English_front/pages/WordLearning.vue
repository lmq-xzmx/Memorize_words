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
import permissionMixin from '../mixins/permissionMixin.js';

export default {
  name: 'WordLearning',
  mixins: [permissionMixin],
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
      if (!this.$hasPermission('view_word_learning')) {
        this.$showError('您没有权限进行单词学习操作')
        return
      }
      console.log('选择卡片:', card)
      // 这里可以添加卡片选择逻辑
    },
    toggleAnalysis() {
      if (!this.$hasPermission('analyze_word_roots')) {
        this.$showError('您没有权限使用词根分析功能')
        return
      }
      console.log('切换分析模式')
    },
    toggleBookmark() {
      if (!this.$hasPermission('manage_bookmarks')) {
        this.$showError('您没有权限管理书签')
        return
      }
      console.log('切换书签')
    },
    playAudio() {
      if (!this.$hasPermission('use_audio_features')) {
        this.$showError('您没有权限使用音频功能')
        return
      }
      console.log('播放音频')
      // 这里可以添加音频播放逻辑
    },
    handleImageError(event) {
      handleImageError(event, IMAGE_TYPES.WORD_EXAMPLE);
    }
  },
  
  async created() {
    // 检查页面访问权限
    if (!this.$hasPermission('view_word_learning')) {
      this.$showError('您没有权限访问单词学习页面')
      this.$router.push('/dashboard')
      return
    }
  }
}
</script>

<style scoped>
.word-learning-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
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
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 20px;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.arrow {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.nav-info {
  display: flex;
  gap: 20px;
}

.nav-text {
  color: white;
  font-size: 14px;
  font-weight: 500;
  opacity: 0.9;
}

.word-display {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.word-main {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 25px;
  padding: 40px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  min-width: 300px;
}

.word-text {
  font-size: 48px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 15px;
  letter-spacing: -1px;
}

.word-phonetic {
  font-size: 18px;
  color: #718096;
  font-style: italic;
  margin: 0;
}

.cards-container {
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.word-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.word-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 1);
}

.card-image {
  width: 100%;
  height: 80px;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #f0f0f0, #e0e0e0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  text-align: left;
}

.card-type {
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 5px;
}

.card-meaning {
  font-size: 14px;
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 5px;
  line-height: 1.3;
}

.card-example {
  font-size: 12px;
  color: #718096;
  line-height: 1.3;
}

.bottom-controls {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.control-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.control-icon {
  font-size: 20px;
}

@media (max-width: 768px) {
  .word-text {
    font-size: 36px;
  }
  
  .word-main {
    padding: 30px 20px;
    min-width: auto;
  }
  
  .cards-container {
    grid-template-columns: 1fr;
    max-height: 250px;
  }
  
  .nav-info {
    flex-direction: column;
    gap: 5px;
  }
}

@media (max-width: 480px) {
  .word-text {
    font-size: 28px;
  }
  
  .word-phonetic {
    font-size: 16px;
  }
  
  .bottom-controls {
    gap: 20px;
  }
  
  .control-btn {
    width: 45px;
    height: 45px;
  }
}
</style>

