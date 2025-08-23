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
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #87CEEB 0%, #98D8E8 50%, #B0E0E6 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 装饰性几何图形 */
.pattern-memory::before {
  content: '';
  position: absolute;
  top: 20%;
  left: -10%;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  z-index: 0;
}

.pattern-memory::after {
  content: '';
  position: absolute;
  bottom: 30%;
  right: -15%;
  width: 150px;
  height: 150px;
  background: rgba(255, 255, 255, 0.08);
  transform: rotate(45deg);
  z-index: 0;
}

/* 状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  z-index: 10;
}

.status-icons {
  display: flex;
  gap: 5px;
  align-items: center;
}

/* 导航栏 */
.nav-bar {
  padding: 15px 20px;
  z-index: 10;
}

.nav-left {
  display: flex;
  align-items: center;
  color: #666;
  cursor: pointer;
}

.back-icon {
  font-size: 24px;
  margin-right: 8px;
  color: #007AFF;
}

.nav-title {
  font-size: 16px;
  color: #666;
}

/* Level选择器 */
.level-selector {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 20px;
  z-index: 10;
}

.level-btn {
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.3);
  color: #666;
  border: 2px solid transparent;
}

.level-btn.active {
  background: #FF6B35;
  color: white;
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
}

/* 学习内容区域 */
.learning-content {
  flex: 1;
  padding: 20px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Level 1 样式 */
.level-1-content {
  text-align: center;
}

.question-text {
  font-size: 24px;
  font-weight: 700;
  color: #8B4513;
  margin-bottom: 40px;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
}

.image-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  max-width: 400px;
  margin: 0 auto;
}

.image-option {
  background: white;
  border-radius: 15px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.image-option:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.image-option.selected {
  border: 3px solid #FF6B35;
  transform: scale(1.05);
}

.image-option img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 10px;
}

.image-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* Level 2 样式 */
.level-2-content {
  text-align: center;
}

.large-image {
  margin-bottom: 40px;
}

.large-image img {
  width: 300px;
  height: 200px;
  object-fit: cover;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 300px;
  margin: 0 auto;
}

.text-option {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 18px;
  font-weight: 600;
}

.text-option:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateX(10px);
}

.text-option.selected {
  background: #4CAF50;
  color: white;
  transform: scale(1.05);
}

.option-letter {
  color: #8B4513;
  font-weight: 700;
  margin-right: 15px;
  font-size: 20px;
}

.text-option.selected .option-letter {
  color: white;
}

/* Level 3 样式 */
.level-3-content {
  text-align: center;
}

.word-image {
  margin-bottom: 40px;
}

.word-image img {
  width: 250px;
  height: 180px;
  object-fit: cover;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
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
  display: flex;
  align-items: center;
  justify-content: center;
  background: #8B4513;
  color: white;
  font-size: 24px;
  font-weight: 700;
  border-radius: 8px;
}

.letter-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  max-width: 300px;
  margin: 0 auto;
}

.letter-option {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
}

.letter-option:hover {
  background: #FF6B35;
  color: white;
  transform: scale(1.1);
}

/* 底部控制栏 */
.bottom-controls {
  display: flex;
  justify-content: space-around;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  z-index: 10;
}

.control-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.control-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.btn-icon {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

/* 底部指示器 */
.bottom-indicator {
  width: 134px;
  height: 5px;
  background: #333;
  border-radius: 3px;
  margin: 10px auto;
  z-index: 10;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .image-grid {
    grid-template-columns: 1fr;
    max-width: 300px;
  }
  
  .question-text {
    font-size: 20px;
  }
  
  .large-image img {
    width: 250px;
    height: 150px;
  }
  
  .letter-grid {
    max-width: 250px;
  }
}
</style>