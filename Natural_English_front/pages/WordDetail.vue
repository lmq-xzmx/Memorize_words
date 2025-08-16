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
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* 状态栏样式 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.1);
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.status-icons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* 主要内容区域 */
.content {
  padding: 1.5rem;
  max-width: 800px;
  margin: 0 auto;
}

/* 单词标题区域 */
.word-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.word-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.word {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
  letter-spacing: -0.02em;
}

.favorite-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
  opacity: 0.6;
}

.favorite-btn:hover {
  background: rgba(255, 193, 7, 0.1);
  transform: scale(1.1);
}

.favorite-btn.active {
  opacity: 1;
  color: #ffc107;
}

.pronunciation {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.phonetic {
  font-size: 1.25rem;
  color: #4a5568;
  font-family: 'Courier New', monospace;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.play-btn, .sentence-play-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 0.75rem;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.play-btn:hover, .sentence-play-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.word-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.part-of-speech {
  background: rgba(34, 197, 94, 0.1);
  color: #059669;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.875rem;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.chinese-meaning {
  font-size: 1.125rem;
  color: #2d3748;
  font-weight: 500;
}

.word-forms {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.form-value {
  font-size: 1rem;
  color: #374151;
  font-weight: 600;
  background: rgba(156, 163, 175, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
}

/* 区域标题样式 */
.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title::before {
  content: '📖';
  font-size: 1rem;
}

/* 例句区域 */
.example-section {
  margin-bottom: 1.5rem;
}

.example-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.example-image {
  margin-bottom: 1rem;
  border-radius: 12px;
  overflow: hidden;
  background: #f8fafc;
}

.sentence-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 12px;
}

.example-content {
  space-y: 1rem;
}

.example-sentence {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.english-sentence {
  flex: 1;
  font-size: 1.125rem;
  color: #2d3748;
  line-height: 1.6;
  margin: 0;
  font-weight: 500;
}

.chinese-translation {
  font-size: 1rem;
  color: #6b7280;
  line-height: 1.5;
  margin: 0;
  font-style: italic;
}

/* 词根词缀区域 */
.etymology-section {
  margin-bottom: 1.5rem;
}

.etymology-section .section-title::before {
  content: '🌱';
}

.etymology-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.etymology-content p {
  font-size: 1rem;
  color: #4a5568;
  line-height: 1.6;
  margin: 0;
  font-family: 'Courier New', monospace;
  background: rgba(102, 126, 234, 0.05);
  padding: 1rem;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

/* 英文释义区域 */
.english-definition-section {
  margin-bottom: 2rem;
}

.english-definition-section .section-title::before {
  content: '📚';
}

.definition-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.definition-content p {
  font-size: 1rem;
  color: #4a5568;
  line-height: 1.6;
  margin: 0;
  font-style: italic;
}

/* 底部操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.continue-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  min-width: 200px;
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.continue-btn:active {
  transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
  }

  .word-header {
    padding: 1.5rem;
  }

  .word {
    font-size: 2rem;
  }

  .word-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .word-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .pronunciation {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .example-sentence {
    flex-direction: column;
    gap: 0.75rem;
  }

  .sentence-play-btn {
    align-self: flex-start;
  }
}

@media (max-width: 480px) {
  .word {
    font-size: 1.75rem;
  }

  .phonetic {
    font-size: 1rem;
  }

  .example-card,
  .etymology-content,
  .definition-content {
    padding: 1rem;
  }

  .continue-btn {
    padding: 0.875rem 1.5rem;
    font-size: 1rem;
    min-width: 160px;
  }
}
</style>

