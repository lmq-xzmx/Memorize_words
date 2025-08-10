<template>
  <div class="word-selection-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="back-btn" @click="goBack">
        <span class="arrow">←</span>
      </div>
      <div class="title">单词练习</div>
      <div class="download-btn">
        <span class="download-icon">⬇</span>
        <span class="download-text">保存</span>
      </div>
    </div>

    <!-- 单词列表区域 -->
    <div class="word-list">
      <div 
        v-for="(word, index) in words" 
        :key="word.id" 
        class="word-item"
        :class="{ 'selected': selectedWords.includes(word.id), 'rejected': rejectedWords.includes(word.id) }"
      >
        <div class="word-content">
          <span class="word-number">{{ index + 1 }}.</span>
          <span class="word-text">{{ word.word }}</span>
        </div>
        <div class="word-actions">
          <button 
            class="action-btn correct-btn" 
            @click="selectWord(word.id, true)"
            :class="{ 'active': selectedWords.includes(word.id) }"
          >
            <span class="btn-icon">✓</span>
          </button>
          <button 
            class="action-btn wrong-btn" 
            @click="selectWord(word.id, false)"
            :class="{ 'active': rejectedWords.includes(word.id) }"
          >
            <span class="btn-icon">✗</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div class="bottom-bar">
      <div class="status-text">正确 {{ selectedWords.length }} 错误 {{ rejectedWords.length }}</div>
      <div class="mic-btn" @click="toggleMic">
        <span class="mic-icon">🎤</span>
      </div>
      <div class="submit-btn" @click="submitSelection">
        提交
      </div>
    </div>

    <!-- 结果弹窗 -->
    <div v-if="showResult" class="result-modal">
      <div class="modal-content">
        <h3>练习完成！</h3>
        <div class="result-stats">
          <p>总计：{{ totalWords }} 个单词</p>
          <p>正确：{{ correctCount }} 个</p>
          <p>错误：{{ wrongCount }} 个</p>
          <p>准确率：{{ accuracy }}%</p>
        </div>
        <div class="modal-actions">
          <button @click="viewSelectedWords" class="view-btn">查看选中单词</button>
          <button @click="restart" class="restart-btn">重新开始</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WordSelection',
  data() {
    return {
      showResult: false,
      selectedWords: [], // 存储选中的单词ID
      rejectedWords: [], // 存储拒绝的单词ID
      words: [
        { id: 1, word: 'cabbage', meaning: '卷心菜' },
        { id: 2, word: 'lemon', meaning: '柠檬' },
        { id: 3, word: 'potato', meaning: '土豆' },
        { id: 4, word: 'deer', meaning: '鹿' },
        { id: 5, word: 'nut', meaning: '坚果' },
        { id: 6, word: 'ball', meaning: '球' },
        { id: 7, word: 'mom', meaning: '妈妈' },
        { id: 8, word: 'three', meaning: '三' },
        { id: 9, word: 'cow', meaning: '奶牛' },
        { id: 10, word: 'speak', meaning: '说话' },
        { id: 11, word: 'please', meaning: '请' },
        { id: 12, word: 'brown', meaning: '棕色' },
        { id: 13, word: 'six', meaning: '六' },
        { id: 14, word: 'peach', meaning: '桃子' }
      ]
    }
  },
  computed: {
    totalWords() {
      return this.words.length
    },
    correctCount() {
      return this.selectedWords.length
    },
    wrongCount() {
      return this.rejectedWords.length
    },
    accuracy() {
      const total = this.correctCount + this.wrongCount
      if (total === 0) return 0
      return Math.round((this.correctCount / total) * 100)
    }
  },
  methods: {
    selectWord(wordId, isCorrect) {
      // 移除之前的选择状态
      this.selectedWords = this.selectedWords.filter(id => id !== wordId)
      this.rejectedWords = this.rejectedWords.filter(id => id !== wordId)
      
      // 添加新的选择状态
      if (isCorrect) {
        this.selectedWords.push(wordId)
      } else {
        this.rejectedWords.push(wordId)
      }
    },
    
    toggleMic() {
      console.log('切换麦克风状态')
    },
    
    goBack() {
      this.$router.go(-1)
    },
    
    submitSelection() {
      if (this.selectedWords.length === 0) {
        alert('请至少选择一个单词')
        return
      }
      
      // 获取选中的单词对象
      const selectedWordObjects = this.words.filter(word => 
        this.selectedWords.includes(word.id)
      )
      
      // 跳转到单词朗读页面
      this.$router.push({
        path: '/word-reading',
        query: {
          words: JSON.stringify(selectedWordObjects)
        }
      })
    },
    
    restart() {
      this.selectedWords = []
      this.rejectedWords = []
      this.showResult = false
    }
  }
}
</script>

<style scoped>
.word-selection-container {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 15px;
  background: #4CAF50;
  color: white;
  font-size: 16px;
}

.back-btn {
  padding: 5px;
  cursor: pointer;
}

.arrow {
  font-size: 18px;
}

.title {
  font-weight: bold;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 14px;
}

.download-icon {
  font-size: 16px;
}

.word-list {
  flex: 1;
  background: white;
  overflow-y: auto;
}

.word-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.word-item:hover {
  background-color: #f9f9f9;
}

.word-item.selected {
  background-color: #e8f5e8;
}

.word-item.rejected {
  background-color: #ffeaea;
}

.word-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.word-number {
  font-size: 16px;
  color: #666;
  min-width: 30px;
}

.word-text {
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.word-actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.correct-btn {
  background: #e0e0e0;
  color: #666;
}

.correct-btn.active {
  background: #4CAF50;
  color: white;
}

.wrong-btn {
  background: #e0e0e0;
  color: #666;
}

.wrong-btn.active {
  background: #f44336;
  color: white;
}

.bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: white;
  border-top: 1px solid #eee;
  min-height: 60px;
}

.status-text {
  font-size: 14px;
  color: #666;
  flex: 1;
}

.mic-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin: 0 15px;
}

.mic-icon {
  font-size: 24px;
  color: white;
}

.submit-btn {
  background: #e0e0e0;
  color: #666;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  border: none;
  transition: all 0.2s ease;
}

.submit-btn:hover {
  background: #4CAF50;
  color: white;
}

.result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  max-width: 300px;
  width: 90%;
}

.modal-content h3 {
  margin-bottom: 20px;
  color: #333;
}

.result-stats {
  margin-bottom: 20px;
  text-align: left;
}

.result-stats p {
  margin: 8px 0;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.view-btn, .restart-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.view-btn {
  background: #4CAF50;
  color: white;
}

.restart-btn {
  background: #2196F3;
  color: white;
}

.view-btn:hover {
  background: #45a049;
}

.restart-btn:hover {
  background: #1976D2;
}
</style>