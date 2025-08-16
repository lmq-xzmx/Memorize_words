<template>
  <div class="pattern-memory">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <div class="time">22:33</div>
      <div class="status-icons">
        <span class="signal">📶</span>
        <span class="wifi">📶</span>
        <span class="battery">80%</span>
      </div>
    </div>

    <!-- 导航栏 -->
    <div class="nav-bar">
      <div class="nav-left" @click="goBack">
        <span class="back-icon">‹</span>
        <span class="nav-title">Snow leopards 雪豹</span>
      </div>
    </div>

    <!-- Level选择器 -->
    <div class="level-selector">
      <div 
        v-for="level in levels" 
        :key="level.id"
        class="level-btn"
        :class="{ active: currentLevel === level.id }"
        @click="switchLevel(level.id)"
      >
        LEVEL {{ level.id }}
      </div>
    </div>

    <!-- 学习内容区域 -->
    <div class="learning-content">
      <!-- Level 1: 图片选择 -->
      <div v-if="currentLevel === 1" class="level-1-content">
        <div class="question-text">
          Which one is "{{ currentWord }}" ?
        </div>
        <div class="image-grid">
          <div 
            v-for="(option, index) in imageOptions" 
            :key="index"
            class="image-option"
            :class="{ selected: selectedImageIndex === index }"
            @click="selectImage(index)"
          >
            <img :src="option.image" :alt="option.label" />
            <div class="image-label">{{ option.label }}</div>
          </div>
        </div>
      </div>

      <!-- Level 2: 选择题 -->
      <div v-if="currentLevel === 2" class="level-2-content">
        <div class="large-image">
          <img :src="currentImage" alt="Question image" />
        </div>
        <div class="options-list">
          <div 
            v-for="(option, index) in textOptions" 
            :key="index"
            class="text-option"
            :class="{ selected: selectedOptionIndex === index }"
            @click="selectOption(index)"
          >
            <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
            <span class="option-text">{{ option }}</span>
          </div>
        </div>
      </div>

      <!-- Level 3: 单词补全 -->
      <div v-if="currentLevel === 3" class="level-3-content">
        <div class="word-image">
          <img :src="currentImage" alt="Word image" />
        </div>
        <div class="word-completion">
          <div class="word-pattern">
            <span v-for="(char, index) in wordPattern" :key="index" class="pattern-char">
              {{ char }}
            </span>
          </div>
          <div class="letter-grid">
            <div 
              v-for="letter in availableLetters" 
              :key="letter"
              class="letter-option"
              @click="selectLetter(letter)"
            >
              {{ letter }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部控制栏 -->
    <div class="bottom-controls">
      <div class="control-btn" @click="markAsKnown">
        <span class="btn-icon">斩</span>
      </div>
      <div class="control-btn" @click="toggleHint">
        <span class="btn-icon">💡</span>
      </div>
      <div class="control-btn" @click="showWordDetail">
        <span class="btn-icon">详</span>
      </div>
    </div>

    <!-- 底部指示器 -->
    <div class="bottom-indicator"></div>
  </div>
</template>

<script>
export default {
  name: 'PatternMemory',
  data() {
    return {
      currentLevel: 1,
      currentWord: 'farmer',
      currentImage: '/lost.jpg',
      selectedImageIndex: null,
      selectedOptionIndex: null,
      levels: [
        { id: 1, name: 'LEVEL 1' },
        { id: 2, name: 'LEVEL 2' },
        { id: 3, name: 'LEVEL 3' }
      ],
      imageOptions: [
        {
          image: '/lost.jpg',
          label: '针织套衫'
        },
        {
          image: '/lost.jpg',
          label: '农夫'
        },
        {
          image: '/lost.jpg',
          label: '黑色方块'
        },
        {
          image: '/lost.jpg',
          label: '模特'
        }
      ],
      textOptions: ['farmer', 'jumper', 'pale', 'area'],
      wordPattern: ['p', '_', '_', '_'],
      availableLetters: ['g', 'l', 'h', 'q', 'v', 'r', 'e', 'a', 'f', 'n']
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1)
    },
    switchLevel(levelId) {
      this.currentLevel = levelId
      this.resetSelections()
    },
    selectImage(index) {
      this.selectedImageIndex = index
    },
    selectOption(index) {
      this.selectedOptionIndex = index
    },
    selectLetter(letter) {
      // 实现字母选择逻辑
      console.log('Selected letter:', letter)
    },
    markAsKnown() {
      // 标记为已掌握
      console.log('Marked as known')
    },
    toggleHint() {
      // 切换提示
      console.log('Toggle hint')
    },
    showWordDetail() {
      // 显示单词详情
      this.$router.push('/word-detail/' + this.currentWord)
    },
    resetSelections() {
      this.selectedImageIndex = null
      this.selectedOptionIndex = null
    }
  }
}
</script>

<style scoped>
.pattern-memory {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
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
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: white;
}

.back-icon {
  font-size: 24px;
  font-weight: bold;
}

.nav-title {
  font-size: 16px;
  font-weight: 600;
}

.level-selector {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.level-btn {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.level-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.level-btn.active {
  background: rgba(255, 255, 255, 0.9);
  color: #ff6b9d;
  box-shadow: 0 5px 15px rgba(255, 255, 255, 0.3);
}

.learning-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Level 1 样式 */
.level-1-content {
  text-align: center;
}

.question-text {
  font-size: 20px;
  font-weight: 600;
  color: white;
  margin-bottom: 30px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  max-width: 400px;
  margin: 0 auto;
}

.image-option {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.image-option:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.image-option.selected {
  border-color: #ff6b9d;
  background: rgba(255, 107, 157, 0.1);
}

.image-option img {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 10px;
}

.image-label {
  font-size: 14px;
  color: #2d3748;
  font-weight: 500;
}

/* Level 2 样式 */
.level-2-content {
  text-align: center;
}

.large-image {
  margin-bottom: 30px;
}

.large-image img {
  width: 200px;
  height: 200px;
  object-fit: cover;
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.options-list {
  display: grid;
  gap: 15px;
  max-width: 300px;
  margin: 0 auto;
}

.text-option {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.text-option:hover {
  transform: translateX(5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.text-option.selected {
  border-color: #ff6b9d;
  background: rgba(255, 107, 157, 0.1);
}

.option-letter {
  width: 30px;
  height: 30px;
  background: #ff6b9d;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.option-text {
  font-size: 16px;
  color: #2d3748;
  font-weight: 500;
}

/* Level 3 样式 */
.level-3-content {
  text-align: center;
}

.word-image {
  margin-bottom: 30px;
}

.word-image img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.word-completion {
  max-width: 400px;
  margin: 0 auto;
}

.word-pattern {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
}

.pattern-char {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.letter-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.letter-option {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.letter-option:hover {
  background: #ff6b9d;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(255, 107, 157, 0.3);
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
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
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

.btn-icon {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.bottom-indicator {
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 20px 20px;
  border-radius: 2px;
}

@media (max-width: 768px) {
  .image-grid {
    grid-template-columns: 1fr;
    max-width: 250px;
  }
  
  .large-image img {
    width: 150px;
    height: 150px;
  }
  
  .word-image img {
    width: 120px;
    height: 120px;
  }
  
  .letter-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .question-text {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .level-selector {
    gap: 5px;
    padding: 15px;
  }
  
  .level-btn {
    padding: 8px 15px;
    font-size: 11px;
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

