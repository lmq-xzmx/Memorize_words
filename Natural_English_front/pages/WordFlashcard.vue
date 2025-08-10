<template>
  <div class="word-flashcard-container">
    <div class="flashcard-header">
      <h2>单词卡片</h2>
      <p>翻转卡片学习单词</p>
    </div>
    
    <div class="flashcard-content">
      <div class="flashcard" :class="{flipped: isFlipped}" @click="flipCard">
        <div class="flashcard-front">
          <div class="word-display">
            <h1>{{ currentWord.word }}</h1>
            <p class="phonetic">{{ currentWord.phonetic }}</p>
          </div>
          <div class="flip-hint">点击翻转查看释义</div>
        </div>
        
        <div class="flashcard-back">
          <div class="meaning-display">
            <h3>{{ currentWord.partOfSpeech }}</h3>
            <p class="meaning">{{ currentWord.meaning }}</p>
            <div class="example">
              <p class="example-en">{{ currentWord.example }}</p>
              <p class="example-cn">{{ currentWord.exampleCn }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card-controls">
        <button @click="markDifficult" class="control-btn difficult">
          <span>😰</span>
          <span>困难</span>
        </button>
        <button @click="markEasy" class="control-btn easy">
          <span>😊</span>
          <span>简单</span>
        </button>
        <button @click="markKnown" class="control-btn known">
          <span>✅</span>
          <span>认识</span>
        </button>
      </div>
      
      <div class="progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{width: progress + '%'}"></div>
        </div>
        <span class="progress-text">{{ currentIndex + 1 }} / {{ totalWords }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { getDefaultPlaceholder, handleImageError, IMAGE_TYPES } from '../utils/imageConfig.js';

export default {
  name: 'WordFlashcard',
  data() {
    return {
      isFlipped: false,
      currentIndex: 0,
      totalWords: 10,
      progress: 10,
      currentWord: {
        word: 'institution',
        phonetic: '/ˌɪnstɪˈtuːʃn/',
        partOfSpeech: 'n. 机构',
        meaning: '机构；制度；惯例；习俗',
        example: 'This English language training institution is very popular.',
        exampleCn: '这家英语培训机构很受欢迎。'
      }
    }
  },
  methods: {
    flipCard() {
      this.isFlipped = !this.isFlipped;
    },
    markDifficult() {
      console.log('标记为困难');
      this.nextCard();
    },
    markEasy() {
      console.log('标记为简单');
      this.nextCard();
    },
    markKnown() {
      console.log('标记为认识');
      this.nextCard();
    },
    nextCard() {
      this.isFlipped = false;
      this.currentIndex++;
      this.progress = (this.currentIndex / this.totalWords) * 100;
      // 这里可以加载下一张卡片
    }
  }
}
</script>

<style scoped>
.word-flashcard-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.flashcard-header {
  text-align: center;
  margin-bottom: 30px;
}

.flashcard-header h2 {
  color: #4A90E2;
  margin-bottom: 10px;
}

.flashcard {
  width: 100%;
  height: 300px;
  position: relative;
  margin-bottom: 30px;
  cursor: pointer;
  perspective: 1000px;
}

.flashcard-front,
.flashcard-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: transform 0.6s;
}

.flashcard-front {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.flashcard-back {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  transform: rotateY(180deg);
}

.flashcard.flipped .flashcard-front {
  transform: rotateY(-180deg);
}

.flashcard.flipped .flashcard-back {
  transform: rotateY(0deg);
}

.word-display {
  text-align: center;
}

.word-display h1 {
  font-size: 48px;
  margin: 0 0 10px 0;
  font-weight: 300;
}

.phonetic {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
}

.flip-hint {
  position: absolute;
  bottom: 20px;
  font-size: 14px;
  opacity: 0.7;
}

.meaning-display {
  text-align: center;
  padding: 20px;
}

.meaning-display h3 {
  font-size: 24px;
  margin: 0 0 15px 0;
}

.meaning {
  font-size: 20px;
  margin: 0 0 20px 0;
  line-height: 1.4;
}

.example {
  border-top: 1px solid rgba(255,255,255,0.3);
  padding-top: 15px;
}

.example-en {
  font-size: 16px;
  margin: 0 0 8px 0;
  font-style: italic;
}

.example-cn {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
}

.card-controls {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 30px;
}

.control-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 15px 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.control-btn.difficult {
  background: #ff6b6b;
  color: white;
}

.control-btn.easy {
  background: #51cf66;
  color: white;
}

.control-btn.known {
  background: #339af0;
  color: white;
}

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.progress {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4A90E2;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
}
</style>