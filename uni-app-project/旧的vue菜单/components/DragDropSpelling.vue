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
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.word-target {
  text-align: center;
  margin-bottom: 30px;
}

.word-target h3 {
  color: #333;
  margin-bottom: 10px;
}

.target-word {
  font-size: 24px;
  font-weight: bold;
  color: #007aff;
  margin-bottom: 5px;
}

.phonetic {
  font-size: 16px;
  color: #666;
  font-style: italic;
}

.drop-zone {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.letter-slot {
  width: 50px;
  height: 60px;
  border: 2px dashed #ccc;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

.letter-slot.filled {
  border-style: solid;
  border-color: #007aff;
  background: #e3f2fd;
}

.letter-slot.correct {
  border-color: #4CAF50;
  background: #e8f5e8;
  color: #4CAF50;
}

.letter-slot.incorrect {
  border-color: #f44336;
  background: #ffebee;
  color: #f44336;
}

.letter-slot:hover {
  border-color: #007aff;
  background: #f0f8ff;
}

.slot-letter {
  text-transform: uppercase;
}

.slot-placeholder {
  color: #ccc;
  font-size: 30px;
}

.letter-bank {
  margin-bottom: 30px;
}

.bank-title {
  text-align: center;
  color: #666;
  margin-bottom: 15px;
  font-size: 14px;
}

.letters-container {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.letter-tile {
  width: 45px;
  height: 45px;
  background: #007aff;
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  cursor: grab;
  transition: all 0.3s ease;
  user-select: none;
}

.letter-tile:hover:not(.used):not(.disabled) {
  background: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.letter-tile.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
}

.letter-tile.used {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.5;
}

.letter-tile.disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-primary {
  background: #007aff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.result {
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  animation: resultAppear 0.5s ease-out;
}

.result-correct {
  background: #e8f5e8;
  border: 2px solid #4CAF50;
  color: #2e7d32;
}

.result-incorrect {
  background: #ffebee;
  border: 2px solid #f44336;
  color: #c62828;
}

.result-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.result-text {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.correct-spelling {
  font-size: 16px;
  margin-top: 10px;
}

/* 动画效果 */
@keyframes resultAppear {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.drop-animation {
  animation: dropBounce 0.3s ease-out;
}

@keyframes dropBounce {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .letter-slot {
    width: 40px;
    height: 50px;
    font-size: 20px;
  }
  
  .letter-tile {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .target-word {
    font-size: 20px;
  }
}
</style>