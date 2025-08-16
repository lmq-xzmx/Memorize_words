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
/* 页面容器 */
.word-flashcard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 页面头部 */
.flashcard-header {
  text-align: center;
  margin-bottom: 3rem;
  color: white;
}

.flashcard-header h2 {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.flashcard-header p {
  font-size: 1.25rem;
  margin: 0;
  opacity: 0.9;
  font-weight: 300;
}

/* 卡片内容区域 */
.flashcard-content {
  max-width: 500px;
  width: 100%;
  text-align: center;
}

/* 翻转卡片 */
.flashcard {
  position: relative;
  width: 100%;
  height: 400px;
  margin-bottom: 2rem;
  perspective: 1000px;
  cursor: pointer;
}

.flashcard-front,
.flashcard-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  transition: transform 0.6s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.flashcard-front {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  transform: rotateY(0deg);
}

.flashcard-back {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  transform: rotateY(180deg);
}

.flashcard.flipped .flashcard-front {
  transform: rotateY(-180deg);
}

.flashcard.flipped .flashcard-back {
  transform: rotateY(0deg);
}

/* 卡片正面 */
.word-display h1 {
  font-size: 3rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 1rem 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.phonetic {
  font-size: 1.5rem;
  color: #667eea;
  font-weight: 500;
  margin: 0 0 2rem 0;
  font-style: italic;
}

.flip-hint {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1rem;
  color: #a0aec0;
  opacity: 0.8;
  animation: pulse 2s infinite;
}

/* 卡片背面 */
.meaning-display h3 {
  font-size: 1.5rem;
  color: #667eea;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.meaning {
  font-size: 1.25rem;
  color: #2d3748;
  font-weight: 500;
  margin: 0 0 2rem 0;
  line-height: 1.6;
}

.example {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 16px;
  border-left: 4px solid #667eea;
}

.example-en {
  font-size: 1.125rem;
  color: #2d3748;
  margin: 0 0 0.5rem 0;
  font-style: italic;
}

.example-cn {
  font-size: 1rem;
  color: #718096;
  margin: 0;
}

/* 控制按钮 */
.card-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.control-btn {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 1rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 100px;
  font-weight: 600;
  color: #2d3748;
}

.control-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
}

.control-btn.difficult {
  border-color: rgba(245, 101, 101, 0.5);
}

.control-btn.difficult:hover {
  background: rgba(245, 101, 101, 0.1);
  border-color: #f56565;
}

.control-btn.easy {
  border-color: rgba(72, 187, 120, 0.5);
}

.control-btn.easy:hover {
  background: rgba(72, 187, 120, 0.1);
  border-color: #48bb78;
}

.control-btn.known {
  border-color: rgba(102, 126, 234, 0.5);
}

.control-btn.known:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

.control-btn span:first-child {
  font-size: 1.5rem;
}

.control-btn span:last-child {
  font-size: 0.875rem;
}

/* 进度条 */
.progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: white;
}

.progress-bar {
  flex: 1;
  height: 12px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  transition: width 0.5s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

.progress-text {
  font-size: 1rem;
  font-weight: 600;
  min-width: 80px;
  text-align: right;
  color: white;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 0.4;
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .word-flashcard-container {
    padding: 1rem;
  }
  
  .flashcard-header h2 {
    font-size: 2.5rem;
  }
  
  .flashcard {
    height: 350px;
    margin-bottom: 1.5rem;
  }
  
  .flashcard-front,
  .flashcard-back {
    padding: 1.5rem;
  }
  
  .word-display h1 {
    font-size: 2.5rem;
  }
  
  .phonetic {
    font-size: 1.25rem;
  }
  
  .card-controls {
    gap: 0.75rem;
  }
  
  .control-btn {
    padding: 0.875rem 1.25rem;
    min-width: 80px;
  }
}

@media (max-width: 480px) {
  .flashcard-header h2 {
    font-size: 2rem;
  }
  
  .flashcard {
    height: 300px;
  }
  
  .flashcard-front,
  .flashcard-back {
    padding: 1rem;
  }
  
  .word-display h1 {
    font-size: 2rem;
  }
  
  .phonetic {
    font-size: 1.125rem;
  }
  
  .meaning-display h3 {
    font-size: 1.25rem;
  }
  
  .meaning {
    font-size: 1.125rem;
  }
  
  .example {
    padding: 1rem;
  }
  
  .card-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .control-btn {
    width: 100%;
    max-width: 200px;
    flex-direction: row;
    justify-content: center;
  }
}
</style>

