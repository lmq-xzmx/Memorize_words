<template>
  <div class="word-spelling-container">
    <div class="spelling-header">
      <h2>拼写练习</h2>
      <p>听音拼写，提升单词记忆</p>
    </div>
    
    <div class="spelling-content">
      <div class="word-audio">
        <button @click="playWord" class="play-btn">
          <span class="play-icon">🔊</span>
          <span>播放单词</span>
        </button>
      </div>
      
      <div class="spelling-input">
        <input 
          v-model="userInput" 
          @keyup.enter="checkSpelling"
          placeholder="请输入您听到的单词"
          class="spelling-field"
        />
        <button @click="checkSpelling" class="check-btn">检查</button>
      </div>
      
      <div v-if="feedback" class="feedback" :class="feedbackClass">
        {{ feedback }}
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
  name: 'WordSpelling',
  data() {
    return {
      currentWord: 'institution',
      userInput: '',
      feedback: '',
      feedbackClass: '',
      currentIndex: 0,
      totalWords: 10,
      progress: 10
    }
  },
  methods: {
    playWord() {
      console.log('播放单词:', this.currentWord);
      // 这里可以添加音频播放逻辑
    },
    checkSpelling() {
      if (this.userInput.toLowerCase() === this.currentWord.toLowerCase()) {
        this.feedback = '正确！';
        this.feedbackClass = 'correct';
        setTimeout(() => {
          this.nextWord();
        }, 1500);
      } else {
        this.feedback = `错误，正确答案是：${this.currentWord}`;
        this.feedbackClass = 'incorrect';
      }
    },
    nextWord() {
      this.userInput = '';
      this.feedback = '';
      this.currentIndex++;
      this.progress = (this.currentIndex / this.totalWords) * 100;
      // 这里可以加载下一个单词
    }
  }
}
</script>

<style scoped>
.word-spelling-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.spelling-header {
  text-align: center;
  margin-bottom: 30px;
}

.spelling-header h2 {
  color: #4A90E2;
  margin-bottom: 10px;
}

.word-audio {
  text-align: center;
  margin-bottom: 30px;
}

.play-btn {
  background: #4A90E2;
  color: white;
  border: none;
  border-radius: 25px;
  padding: 15px 30px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 auto;
}

.spelling-input {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.spelling-field {
  flex: 1;
  padding: 15px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

.check-btn {
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 15px 25px;
  cursor: pointer;
}

.feedback {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: bold;
}

.feedback.correct {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.feedback.incorrect {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
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