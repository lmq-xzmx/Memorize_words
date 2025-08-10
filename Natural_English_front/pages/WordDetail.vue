<template>
  <div class="word-detail">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <span class="time">22:27</span>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">78%</span>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content">
      <!-- 单词标题区域 -->
      <div class="word-header">
        <div class="word-title">
          <h1 class="word">{{ wordData.word }}</h1>
          <button class="favorite-btn" :class="{ active: wordData.isFavorite }" @click="toggleFavorite">
            ⭐
          </button>
        </div>
        
        <!-- 音标和发音 -->
        <div class="pronunciation">
          <span class="phonetic">{{ wordData.phonetic }}</span>
          <button class="play-btn" @click="playPronunciation">
            🔊
          </button>
        </div>
        
        <!-- 词性和释义 -->
        <div class="word-info">
          <span class="part-of-speech">{{ wordData.partOfSpeech }}</span>
          <span class="chinese-meaning">{{ wordData.chineseMeaning }}</span>
        </div>
        
        <!-- 复数形式 -->
        <div class="word-forms" v-if="wordData.pluralForm">
          <span class="form-label">复数</span>
          <span class="form-value">{{ wordData.pluralForm }}</span>
        </div>
      </div>

      <!-- 图文例句区域 -->
      <div class="example-section">
        <h3 class="section-title">图文例句</h3>
        
        <div class="example-card">
          <!-- 例句图片 -->
          <div class="example-image">
            <img :src="wordData.exampleImage" alt="例句图片" class="sentence-image" @error="handleImageError" />
          </div>
          
          <!-- 例句内容 -->
          <div class="example-content">
            <div class="example-sentence">
              <p class="english-sentence">{{ wordData.exampleSentence }}</p>
              <button class="sentence-play-btn" @click="playSentence">
                🔊
              </button>
            </div>
            
            <p class="chinese-translation">{{ wordData.sentenceTranslation }}</p>
          </div>
        </div>
      </div>

      <!-- 词根词缀区域 -->
      <div class="etymology-section" v-if="wordData.etymology">
        <h3 class="section-title">词根词缀</h3>
        <div class="etymology-content">
          <p>{{ wordData.etymology }}</p>
        </div>
      </div>

      <!-- 英文释义区域 -->
      <div class="english-definition-section">
        <h3 class="section-title">英文释义</h3>
        <div class="definition-content">
          <p>{{ wordData.englishDefinition }}</p>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <div class="action-buttons">
        <button class="continue-btn" @click="continueStudy">
          继续做题
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { getDefaultPlaceholder, handleImageError, IMAGE_TYPES } from '../utils/imageConfig.js';

export default {
  name: 'WordDetail',
  data() {
    return {
      wordData: {
        word: 'institution',
        phonetic: '/ˌɪnstɪˈtuːʃn/',
        partOfSpeech: 'n.',
        chineseMeaning: '机构；制度；惯例；习俗',
        pluralForm: 'institutions',
        isFavorite: false,
        exampleImage: getDefaultPlaceholder(IMAGE_TYPES.WORD_EXAMPLE),
        exampleSentence: 'This English language training institution is very popular with parents and their children alike.',
        sentenceTranslation: '这家英语培训机构很受家长和孩子们的欢迎。',
        etymology: 'in在......里 +stitut建立 +ion名词后缀 →institution机构',
        englishDefinition: 'an organization founded and united for a specific purpose'
      }
    }
  },
  mounted() {
    // 组件挂载后可以从路由参数或API获取单词数据
    const wordId = this.$route.params.id
    if (wordId) {
      this.loadWordData(wordId)
    }
  },
  methods: {
    toggleFavorite() {
      this.wordData.isFavorite = !this.wordData.isFavorite
      // 这里可以添加API调用来保存收藏状态
    },
    playPronunciation() {
      // 播放单词发音
      console.log('播放单词发音:', this.wordData.word)
    },
    playSentence() {
      // 播放例句发音
      console.log('播放例句发音:', this.wordData.exampleSentence)
    },
    continueStudy() {
      // 继续学习功能
      this.$router.push('/word-challenge')
    },
    loadWordData(wordId) {
      // 从API加载单词数据
      console.log('加载单词数据:', wordId)
      // 这里可以根据wordId加载不同的单词数据
      if (wordId === 'institution') {
        // 当前已经是institution的数据，无需更改
      }
    },
    handleImageError(event) {
      handleImageError(event, IMAGE_TYPES.WORD_EXAMPLE);
    }
  }
}
</script>

<style scoped>
.word-detail {
  background: #f5f5f5;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 状态栏样式 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #fff;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.status-icons {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 内容区域 */
.content {
  padding: 20px 16px;
}

/* 单词标题区域 */
.word-header {
  background: #fff;
  border-radius: 12px;
  padding: 24px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.word-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.word {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.favorite-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s;
}

.favorite-btn.active {
  opacity: 1;
}

.pronunciation {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.phonetic {
  font-size: 18px;
  color: #666;
  font-family: 'Times New Roman', serif;
}

.play-btn, .sentence-play-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.play-btn:hover, .sentence-play-btn:hover {
  opacity: 1;
}

.word-info {
  margin-bottom: 12px;
}

.part-of-speech {
  color: #3498db;
  font-weight: 600;
  margin-right: 12px;
}

.chinese-meaning {
  color: #2c3e50;
  font-size: 16px;
}

.word-forms {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label {
  color: #7f8c8d;
  font-size: 14px;
}

.form-value {
  color: #2c3e50;
  font-weight: 500;
}

/* 图文例句区域 */
.example-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
}

.example-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.example-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.example-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.example-content {
  padding: 20px;
}

.example-sentence {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.english-sentence {
  flex: 1;
  font-size: 16px;
  line-height: 1.5;
  color: #2c3e50;
  margin: 0;
  margin-right: 12px;
}

.chinese-translation {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
  margin: 0;
}

/* 词根词缀和英文释义区域 */
.etymology-section,
.english-definition-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.etymology-content p,
.definition-content p {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
  color: #2c3e50;
}

/* 底部操作按钮 */
.action-buttons {
  padding: 20px 0;
}

.continue-btn {
  width: 100%;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 25px;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.continue-btn:hover {
  background: #2980b9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 16px 12px;
  }
  
  .word {
    font-size: 28px;
  }
  
  .word-header {
    padding: 20px 16px;
  }
}
</style>