<template>
  <div class="story-reading">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧内容区 -->
      <div class="left-section">
        <!-- 图片区域 -->
        <div class="image-section">
          <img 
            :src="storyImage" 
            alt="Story illustration" 
            class="story-image"
          />
        </div>
        
        <!-- 文章区域 -->
        <div class="article-section">
          <h2 class="story-title">{{ storyTitle }}</h2>
          <div class="story-content">
            <p v-for="(paragraph, index) in storyParagraphs" :key="index" class="paragraph">
              <span 
                v-for="(word, wordIndex) in paragraph.words" 
                :key="wordIndex"
                :class="getWordClass(word)"
                @click="addToVocabulary(word)"
              >
                {{ word.text }}
              </span>
            </p>
          </div>
        </div>
      </div>
      
      <!-- 右侧生词列表 -->
      <div class="vocabulary-section">
        <h3 class="vocabulary-title">生词列表</h3>
        
        <!-- 词性图例 -->
        <div class="pos-legend">
          <div class="legend-item" v-for="pos in partOfSpeechTypes" :key="pos.type">
            <span :class="`pos-${pos.type}`" class="legend-color"></span>
            <span class="legend-text">{{ pos.label }} ({{ pos.count }})</span>
          </div>
        </div>
        
        <!-- 生词列表 -->
        <div class="vocabulary-list">
          <div 
            v-for="word in vocabularyWords" 
            :key="word.id"
            class="vocabulary-item"
            :class="`pos-${word.partOfSpeech}`"
          >
            <div class="word-info">
              <span class="word-text">{{ word.word }}</span>
              <span class="word-phonetic">{{ word.phonetic }}</span>
            </div>
            <div class="word-definition">{{ word.definition }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StoryReading',
  data() {
    return {
      storyImage: '/lost.jpg',
      storyTitle: 'The Ant and the Grasshopper (蚂蚁和蚱蜢)',
      storyParagraphs: [
        {
          words: [
            { text: 'It ', partOfSpeech: 'pronoun' },
            { text: 'is ', partOfSpeech: 'verb' },
            { text: 'a ', partOfSpeech: 'article' },
            { text: 'sunny ', partOfSpeech: 'adjective' },
            { text: 'summer ', partOfSpeech: 'noun' },
            { text: 'day. ', partOfSpeech: 'noun' },
            { text: 'The ', partOfSpeech: 'article' },
            { text: 'grass ', partOfSpeech: 'noun' },
            { text: 'is ', partOfSpeech: 'verb' },
            { text: 'green.', partOfSpeech: 'adjective' }
          ]
        },
        {
          words: [
            { text: 'The ', partOfSpeech: 'article' },
            { text: 'sky ', partOfSpeech: 'noun' },
            { text: 'is ', partOfSpeech: 'verb' },
            { text: 'blue. ', partOfSpeech: 'adjective' },
            { text: 'Grasshopper ', partOfSpeech: 'noun' },
            { text: 'is ', partOfSpeech: 'verb' },
            { text: 'jumping ', partOfSpeech: 'verb' },
            { text: 'up ', partOfSpeech: 'adverb' },
            { text: 'and ', partOfSpeech: 'conjunction' },
            { text: 'down.', partOfSpeech: 'adverb' }
          ]
        },
        {
          words: [
            { text: 'He ', partOfSpeech: 'pronoun' },
            { text: 'is ', partOfSpeech: 'verb' },
            { text: 'singing ', partOfSpeech: 'verb' },
            { text: 'a ', partOfSpeech: 'article' },
            { text: 'song. ', partOfSpeech: 'noun' },
            { text: 'He ', partOfSpeech: 'pronoun' },
            { text: 'is ', partOfSpeech: 'verb' },
            { text: 'happy.', partOfSpeech: 'adjective' }
          ]
        }
      ],
      vocabularyWords: [
        { id: 1, word: 'sunny', phonetic: '[ˈsʌni]', definition: '晴朗的', partOfSpeech: 'adjective' },
        { id: 2, word: 'grass', phonetic: '[ɡrɑːs]', definition: '草', partOfSpeech: 'noun' },
        { id: 3, word: 'green', phonetic: '[ɡriːn]', definition: '绿色的', partOfSpeech: 'adjective' },
        { id: 4, word: 'sky', phonetic: '[skaɪ]', definition: '天空', partOfSpeech: 'noun' },
        { id: 5, word: 'blue', phonetic: '[bluː]', definition: '蓝色的', partOfSpeech: 'adjective' },
        { id: 6, word: 'jump', phonetic: '[dʒʌmp]', definition: '跳', partOfSpeech: 'verb' },
        { id: 7, word: 'sing', phonetic: '[sɪŋ]', definition: '唱', partOfSpeech: 'verb' },
        { id: 8, word: 'song', phonetic: '[sɔːŋ]', definition: '歌', partOfSpeech: 'noun' },
        { id: 9, word: 'happy', phonetic: '[ˈhæpi]', definition: '快乐的', partOfSpeech: 'adjective' }
      ]
    }
  },
  computed: {
    partOfSpeechTypes() {
      const types = {}
      this.vocabularyWords.forEach(word => {
        if (!types[word.partOfSpeech]) {
          types[word.partOfSpeech] = {
            type: word.partOfSpeech,
            label: this.getPosLabel(word.partOfSpeech),
            count: 0
          }
        }
        types[word.partOfSpeech].count++
      })
      return Object.values(types)
    }
  },
  methods: {
    getWordClass(word) {
      return {
        'word-token': true,
        [`pos-${word.partOfSpeech}`]: true,
        'clickable': this.isVocabularyWord(word.text)
      }
    },
    isVocabularyWord(text) {
      const cleanText = text.replace(/[.,!?]/g, '').toLowerCase()
      return this.vocabularyWords.some(word => word.word.toLowerCase() === cleanText)
    },
    addToVocabulary(word) {
      if (this.isVocabularyWord(word.text)) {
        console.log('添加到生词本:', word.text)
        // 这里可以添加实际的添加到生词本的逻辑
      }
    },
    getPosLabel(pos) {
      const labels = {
        'noun': '名词',
        'verb': '动词',
        'adjective': '形容词',
        'adverb': '副词',
        'pronoun': '代词',
        'article': '冠词',
        'conjunction': '连词',
        'preposition': '介词'
      }
      return labels[pos] || pos
    }
  }
}
</script>

<style scoped>
.story-reading {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f8f9fa;
  min-height: 100vh;
}

.main-content {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

/* 左侧内容区 */
.left-section {
  flex: 2;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 图片区域 */
.image-section {
  margin-bottom: 20px;
  text-align: center;
}

.story-image {
  max-width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 文章区域 */
.article-section {
  margin-top: 20px;
}

.story-title {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.story-content {
  line-height: 1.8;
  font-size: 16px;
}

.paragraph {
  margin-bottom: 15px;
  text-align: justify;
}

.word-token {
  padding: 2px 4px;
  border-radius: 3px;
  margin: 0 1px;
  transition: all 0.2s ease;
}

.word-token.clickable {
  cursor: pointer;
}

.word-token.clickable:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 词性颜色 */
.pos-noun {
  background-color: #e3f2fd;
  color: #1976d2;
}

.pos-verb {
  background-color: #fce4ec;
  color: #c2185b;
}

.pos-adjective {
  background-color: #e8f5e8;
  color: #388e3c;
}

.pos-adverb {
  background-color: #fff3e0;
  color: #f57c00;
}

.pos-pronoun {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.pos-article {
  background-color: #e0f2f1;
  color: #00695c;
}

.pos-conjunction {
  background-color: #fef7e0;
  color: #ef6c00;
}

.pos-preposition {
  background-color: #e8eaf6;
  color: #3f51b5;
}

/* 右侧生词列表 */
.vocabulary-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 80vh;
  overflow-y: auto;
}

.vocabulary-title {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

/* 词性图例 */
.pos-legend {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  margin-right: 8px;
  display: inline-block;
}

.legend-text {
  font-size: 14px;
  color: #666;
}

/* 生词列表 */
.vocabulary-list {
  max-height: 400px;
  overflow-y: auto;
}

.vocabulary-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  border-left: 4px solid;
  background: #f8f9fa;
  transition: all 0.2s ease;
}

.vocabulary-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.vocabulary-item.pos-noun {
  border-left-color: #1976d2;
}

.vocabulary-item.pos-verb {
  border-left-color: #c2185b;
}

.vocabulary-item.pos-adjective {
  border-left-color: #388e3c;
}

.vocabulary-item.pos-adverb {
  border-left-color: #f57c00;
}

.word-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.word-text {
  font-weight: bold;
  font-size: 16px;
  color: #2c3e50;
}

.word-phonetic {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

.word-definition {
  font-size: 14px;
  color: #555;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .left-section,
  .vocabulary-section {
    flex: none;
    width: 100%;
  }
  
  .vocabulary-section {
    max-height: none;
  }
}
</style>

