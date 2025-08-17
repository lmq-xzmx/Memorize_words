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
import { getDefaultPlaceholder, handleImageError, IMAGE_TYPES } from '../utils/imageConfig';

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
/* 页面容器 */
.word-spelling-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 页面头部 */
.spelling-header {
  text-align: center;
  margin-bottom: 3rem;
  color: white;
}

.spelling-header h2 {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.spelling-header p {
  font-size: 1.25rem;
  margin: 0;
  opacity: 0.9;
  font-weight: 300;
}

/* 拼写内容区域 */
.spelling-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 600px;
  width: 100%;
  text-align: center;
}

/* 音频播放区域 */
.word-audio {
  margin-bottom: 2.5rem;
}

.play-btn {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  padding: 1.5rem 3rem;
  border-radius: 50px;
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 auto;
}

.play-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(79, 172, 254, 0.4);
}

.play-btn:active {
  transform: translateY(-1px);
}

.play-icon {
  font-size: 1.5rem;
}

/* 拼写输入区域 */
.spelling-input {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.spelling-field {
  flex: 1;
  padding: 1.25rem 1.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-size: 1.125rem;
  background: #f8fafc;
  transition: all 0.3s ease;
  outline: none;
}

.spelling-field:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.check-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1.25rem 2rem;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  min-width: 120px;
}

.check-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.check-btn:active {
  transform: translateY(0);
}

/* 反馈信息 */
.feedback {
  padding: 1.25rem 2rem;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 2rem;
  animation: fadeInUp 0.5s ease;
}

.feedback.correct {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
}

.feedback.incorrect {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(245, 101, 101, 0.3);
}

/* 进度条 */
.progress {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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
  color: #4a5568;
  min-width: 80px;
  text-align: right;
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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
  .word-spelling-container {
    padding: 1rem;
  }
  
  .spelling-header h2 {
    font-size: 2.5rem;
  }
  
  .spelling-content {
    padding: 2rem;
    margin: 0 1rem;
  }
  
  .spelling-input {
    flex-direction: column;
    gap: 1rem;
  }
  
  .spelling-field {
    width: 100%;
  }
  
  .check-btn {
    width: 100%;
  }
  
  .play-btn {
    padding: 1.25rem 2.5rem;
    font-size: 1.125rem;
  }
}

@media (max-width: 480px) {
  .spelling-header h2 {
    font-size: 2rem;
  }
  
  .spelling-content {
    padding: 1.5rem;
  }
  
  .play-btn {
    padding: 1rem 2rem;
    font-size: 1rem;
  }
  
  .spelling-field,
  .check-btn {
    padding: 1rem 1.25rem;
    font-size: 1rem;
  }
}
</style>

