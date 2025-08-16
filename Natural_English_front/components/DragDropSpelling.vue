<template>
  <div class="drag-drop-spelling">
    <div class="word-target">
      <h3>拼写单词</h3>
      <div class="target-word">{{ targetWord }}</div>
      <div class="phonetic">{{ phonetic }}</div>
    </div>
    
    <div class="drop-zone">
      <div 
        v-for="(slot, index) in wordSlots" 
        :key="index"
        class="letter-slot"
        :class="{ 
          filled: slot.letter, 
          correct: slot.correct,
          incorrect: slot.incorrect 
        }"
        @drop="onDrop($event, index)"
        @dragover.prevent
        @dragenter.prevent
      >
        <span v-if="slot.letter" class="slot-letter">{{ slot.letter }}</span>
        <span v-else class="slot-placeholder">_</span>
      </div>
    </div>
    
    <div class="letter-bank">
      <div class="bank-title">拖拽字母到上方</div>
      <div class="letters-container">
        <div 
          v-for="(letter, index) in availableLetters" 
          :key="`${letter.char}-${index}`"
          class="letter-tile"
          :class="{ 
            dragging: letter.isDragging,
            used: letter.isUsed,
            disabled: letter.isDisabled
          }"
          :draggable="!letter.isUsed && !letter.isDisabled"
          @dragstart="onDragStart($event, letter, index)"
          @dragend="onDragEnd($event, letter)"
          @click="onLetterClick(letter, index)"
        >
          {{ letter.char }}
        </div>
      </div>
    </div>
    
    <div class="actions">
      <button 
        class="btn btn-secondary" 
        @click="clearAll"
        :disabled="isChecking"
      >
        清空
      </button>
      <button 
        class="btn btn-primary" 
        @click="checkSpelling"
        :disabled="!isComplete || isChecking"
      >
        {{ isChecking ? '检查中...' : '检查拼写' }}
      </button>
    </div>
    
    <!-- 结果显示 -->>
    <div v-if="showResult" class="result" :class="resultClass">
      <div class="result-icon">{{ resultIcon }}</div>
      <div class="result-text">{{ resultText }}</div>
      <div v-if="!isCorrect" class="correct-spelling">
        正确拼写: <strong>{{ targetWord }}</strong>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DragDropSpelling',
  props: {
    word: {
      type: String,
      required: true
    },
    phonetic: {
      type: String,
      default: ''
    },
    meaning: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      wordSlots: [],
      availableLetters: [],
      showResult: false,
      isCorrect: false,
      isChecking: false,
      selectedLetterIndex: null
    }
  },
  computed: {
    targetWord() {
      return this.word.toLowerCase()
    },
    isComplete() {
      return this.wordSlots.every(slot => slot.letter)
    },
    currentSpelling() {
      return this.wordSlots.map(slot => slot.letter || '').join('')
    },
    resultClass() {
      return this.isCorrect ? 'result-correct' : 'result-incorrect'
    },
    resultIcon() {
      return this.isCorrect ? '🎉' : '❌'
    },
    resultText() {
      return this.isCorrect ? '拼写正确！' : '拼写错误，再试一次'
    }
  },
  watch: {
    word: {
      immediate: true,
      handler() {
        this.initializeGame()
      }
    }
  },
  methods: {
    initializeGame() {
      this.showResult = false
      this.isCorrect = false
      this.isChecking = false
      
      // 初始化单词槽位
      this.wordSlots = Array(this.targetWord.length).fill(null).map(() => ({
        letter: '',
        correct: false,
        incorrect: false
      }))
      
      // 创建字母库（包含正确字母和干扰字母）
      this.createLetterBank()
    },
    
    createLetterBank() {
      const wordLetters = this.targetWord.split('')
      const distractorLetters = this.generateDistractors(wordLetters)
      const allLetters = [...wordLetters, ...distractorLetters]
      
      // 打乱字母顺序
      this.availableLetters = this.shuffleArray(allLetters).map(char => ({
        char: char.toUpperCase(),
        isDragging: false,
        isUsed: false,
        isDisabled: false
      }))
    },
    
    generateDistractors(wordLetters) {
      const commonLetters = ['A', 'E', 'I', 'O', 'U', 'R', 'S', 'T', 'L', 'N']
      const distractors = []
      const wordLettersUpper = wordLetters.map(l => l.toUpperCase())
      
      // 添加3-5个干扰字母
      const distractorCount = Math.min(5, Math.max(3, Math.floor(wordLetters.length / 2)))
      
      for (let i = 0; i < distractorCount; i++) {
        let distractor
        do {
          distractor = commonLetters[Math.floor(Math.random() * commonLetters.length)]
        } while (wordLettersUpper.includes(distractor) || distractors.includes(distractor))
        
        distractors.push(distractor)
      }
      
      return distractors
    },
    
    shuffleArray(array) {
      const shuffled = [...array]
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
      }
      return shuffled
    },
    
    onDragStart(event, letter, index) {
      if (letter.isUsed || letter.isDisabled) return
      
      letter.isDragging = true
      event.dataTransfer.setData('text/plain', JSON.stringify({
        letter: letter.char,
        sourceIndex: index
      }))
      event.dataTransfer.effectAllowed = 'move'
    },
    
    onDragEnd(event, letter) {
      letter.isDragging = false
    },
    
    onDrop(event, slotIndex) {
      event.preventDefault()
      const data = JSON.parse(event.dataTransfer.getData('text/plain'))
      const { letter, sourceIndex } = data
      
      // 如果槽位已被占用，将原字母返回字母库
      if (this.wordSlots[slotIndex].letter) {
        this.returnLetterToBank(this.wordSlots[slotIndex].letter)
      }
      
      // 放置新字母
      this.wordSlots[slotIndex].letter = letter.toLowerCase()
      this.wordSlots[slotIndex].correct = false
      this.wordSlots[slotIndex].incorrect = false
      
      // 标记字母为已使用
      this.availableLetters[sourceIndex].isUsed = true
      
      // 触发放置动画
      this.triggerDropAnimation(slotIndex)
    },
    
    onLetterClick(letter, index) {
      if (letter.isUsed || letter.isDisabled) return
      
      // 移动端点击模式：找到第一个空槽位
      const emptySlotIndex = this.wordSlots.findIndex(slot => !slot.letter)
      if (emptySlotIndex !== -1) {
        this.wordSlots[emptySlotIndex].letter = letter.char.toLowerCase()
        letter.isUsed = true
        this.triggerDropAnimation(emptySlotIndex)
      }
    },
    
    returnLetterToBank(letterChar) {
      const letter = this.availableLetters.find(l => 
        l.char.toLowerCase() === letterChar.toLowerCase() && l.isUsed
      )
      if (letter) {
        letter.isUsed = false
      }
    },
    
    triggerDropAnimation(slotIndex) {
      // 添加放置动画效果
      const slot = document.querySelectorAll('.letter-slot')[slotIndex]
      if (slot) {
        slot.classList.add('drop-animation')
        setTimeout(() => {
          slot.classList.remove('drop-animation')
        }, 300)
      }
    },
    
    clearAll() {
      this.wordSlots.forEach(slot => {
        if (slot.letter) {
          this.returnLetterToBank(slot.letter)
          slot.letter = ''
          slot.correct = false
          slot.incorrect = false
        }
      })
      this.showResult = false
    },
    
    async checkSpelling() {
      this.isChecking = true
      
      // 模拟检查延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const userSpelling = this.currentSpelling
      this.isCorrect = userSpelling === this.targetWord
      
      // 标记每个字母的正确性
      this.wordSlots.forEach((slot, index) => {
        const isCorrectLetter = slot.letter === this.targetWord[index]
        slot.correct = isCorrectLetter
        slot.incorrect = !isCorrectLetter
      })
      
      this.showResult = true
      this.isChecking = false
      
      // 触发结果事件
      this.$emit('result', {
        isCorrect: this.isCorrect,
        userAnswer: userSpelling,
        correctAnswer: this.targetWord,
        attempts: 1 // 可以跟踪尝试次数
      })
      
      // 如果正确，禁用所有交互
      if (this.isCorrect) {
        this.availableLetters.forEach(letter => {
          letter.isDisabled = true
        })
      }
    }
  }
}
</script>

<style scoped>
.drag-drop-spelling {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', sans-serif;
}

.word-target {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.word-target h3 {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.target-word {
  font-size: 2rem;
  font-weight: bold;
  color: #4a90e2;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.phonetic {
  font-size: 1.2rem;
  color: #666;
  font-style: italic;
}

.drop-zone {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
  min-height: 80px;
  align-items: center;
  flex-wrap: wrap;
}

.letter-slot {
  width: 50px;
  height: 60px;
  border: 3px dashed #ccc;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.letter-slot::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s ease;
}

.letter-slot:hover::before {
  left: 100%;
}

.letter-slot.filled {
  border-color: #4a90e2;
  background: rgba(74, 144, 226, 0.1);
  border-style: solid;
}

.letter-slot.correct {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.2);
  animation: correctPulse 0.6s ease-out;
}

.letter-slot.incorrect {
  border-color: #f44336;
  background: rgba(244, 67, 54, 0.2);
  animation: incorrectShake 0.6s ease-out;
}

@keyframes correctPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes incorrectShake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

.slot-letter {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  position: relative;
  z-index: 1;
}

.slot-placeholder {
  font-size: 2rem;
  color: #ccc;
  font-weight: bold;
}

.letter-bank {
  margin-bottom: 2rem;
}

.bank-title {
  text-align: center;
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 1rem;
  font-weight: 500;
}

.letters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
  min-height: 80px;
}

.letter-tile {
  width: 45px;
  height: 45px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  font-weight: bold;
  cursor: grab;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.letter-tile::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.3) 50%, transparent 70%);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.letter-tile:hover::before {
  transform: translateX(100%);
}

.letter-tile:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
}

.letter-tile:active {
  cursor: grabbing;
  transform: scale(0.95);
}

.letter-tile.dragging {
  opacity: 0.7;
  transform: rotate(5deg) scale(1.1);
  z-index: 1000;
}

.letter-tile.used {
  opacity: 0.3;
  cursor: not-allowed;
  background: #ccc;
  transform: none;
}

.letter-tile.used:hover {
  transform: none;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.letter-tile.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #999;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(149, 165, 166, 0.3);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(149, 165, 166, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.result {
  text-align: center;
  padding: 1.5rem;
  border-radius: 15px;
  margin-top: 1rem;
  animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result.correct {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  box-shadow: 0 10px 25px rgba(76, 175, 80, 0.3);
}

.result.incorrect {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
  box-shadow: 0 10px 25px rgba(244, 67, 54, 0.3);
}

.result-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: bounceIn 0.8s ease-out;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.result-text {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.result-details {
  font-size: 1rem;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .drag-drop-spelling {
    padding: 1rem;
  }
  
  .target-word {
    font-size: 1.5rem;
  }
  
  .letter-slot {
    width: 40px;
    height: 50px;
  }
  
  .letter-tile {
    width: 40px;
    height: 40px;
    font-size: 1.1rem;
  }
  
  .slot-letter {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .drop-zone {
    gap: 0.3rem;
  }
  
  .letter-slot {
    width: 35px;
    height: 45px;
  }
  
  .letter-tile {
    width: 35px;
    height: 35px;
    font-size: 1rem;
  }
  
  .letters-container {
    gap: 0.3rem;
  }
  
  .actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 200px;
  }
}

/* 触摸设备优化 */
@media (hover: none) {
  .letter-tile:hover {
    transform: none;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
  
  .btn:hover {
    transform: none;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .drag-drop-spelling {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  }
  
  .word-target {
    background: rgba(52, 73, 94, 0.9);
    color: #ecf0f1;
  }
  
  .word-target h3 {
    color: #ecf0f1;
  }
  
  .target-word {
    color: #3498db;
  }
  
  .phonetic {
    color: #bdc3c7;
  }
  
  .drop-zone {
    background: rgba(52, 73, 94, 0.7);
  }
  
  .letter-slot {
    background: rgba(44, 62, 80, 0.8);
    border-color: #7f8c8d;
  }
  
  .letters-container {
    background: rgba(52, 73, 94, 0.7);
  }
  
  .bank-title {
    color: #bdc3c7;
  }
}

/* 无障碍支持 */
.letter-tile:focus {
  outline: 3px solid #4a90e2;
  outline-offset: 2px;
}

.btn:focus {
  outline: 3px solid #4a90e2;
  outline-offset: 2px;
}

/* 减少动画效果（用户偏好） */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>

