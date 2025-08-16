<template>
  <div class="word-selection-container">
    <div class="header">
      <h1>🎯 单词选择</h1>
      <p class="subtitle">选择您要学习的单词范围</p>
    </div>
    
    <div class="selection-content">
      <div class="filter-section">
        <div class="filter-group">
          <label>年级选择</label>
          <select v-model="selectedGrade" @change="loadWords">
            <option value="">全部年级</option>
            <option value="1">一年级</option>
            <option value="2">二年级</option>
            <option value="3">三年级</option>
            <option value="4">四年级</option>
            <option value="5">五年级</option>
            <option value="6">六年级</option>
            <option value="7">七年级</option>
            <option value="8">八年级</option>
            <option value="9">九年级</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>教材版本</label>
          <select v-model="selectedTextbook" @change="loadWords">
            <option value="">全部版本</option>
            <option value="人教版">人教版</option>
            <option value="外研版">外研版</option>
            <option value="牛津版">牛津版</option>
            <option value="北师大版">北师大版</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>难度等级</label>
          <select v-model="selectedDifficulty" @change="loadWords">
            <option value="">全部难度</option>
            <option value="1">简单</option>
            <option value="2">中等</option>
            <option value="3">困难</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>学习状态</label>
          <select v-model="selectedStatus" @change="loadWords">
            <option value="">全部状态</option>
            <option value="unlearned">未学习</option>
            <option value="learning">学习中</option>
            <option value="mastered">已掌握</option>
          </select>
        </div>
      </div>
      
      <div class="stats-bar">
        <div class="stat-item">
          <span class="label">总单词数：</span>
          <span class="value">{{ totalWords }}</span>
        </div>
        <div class="stat-item">
          <span class="label">已选择：</span>
          <span class="value">{{ selectedWords.length }}</span>
        </div>
        <div class="stat-item">
          <span class="label">未学习：</span>
          <span class="value">{{ unlearnedCount }}</span>
        </div>
      </div>
      
      <div class="selection-actions">
        <button @click="selectAll" class="btn btn-secondary">
          <i class="fas fa-check-square"></i>
          全选
        </button>
        <button @click="selectNone" class="btn btn-secondary">
          <i class="fas fa-square"></i>
          全不选
        </button>
        <button @click="selectUnlearned" class="btn btn-info">
          <i class="fas fa-graduation-cap"></i>
          选择未学习
        </button>
        <button @click="startLearning" class="btn btn-primary" :disabled="selectedWords.length === 0">
          <i class="fas fa-play"></i>
          开始学习 ({{ selectedWords.length }})
        </button>
      </div>
      
      <div class="word-list">
        <div class="word-item" v-for="word in filteredWords" :key="word.id">
          <div class="word-checkbox">
            <input 
              type="checkbox" 
              :id="'word-' + word.id" 
              v-model="selectedWords" 
              :value="word.id"
            >
            <label :for="'word-' + word.id"></label>
          </div>
          
          <div class="word-info">
            <div class="word-main">
              <span class="word-text">{{ word.word }}</span>
              <span class="word-phonetic">{{ word.phonetic }}</span>
              <span class="word-status" :class="getStatusClass(word.status)">{{ getStatusText(word.status) }}</span>
            </div>
            <div class="word-definition">{{ word.definition }}</div>
            <div class="word-meta">
              <span class="grade">{{ word.grade }}年级</span>
              <span class="textbook">{{ word.textbook_version }}</span>
              <span class="difficulty">{{ getDifficultyText(word.difficulty) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="pagination" v-if="totalPages > 1">
        <button 
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="page-btn"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        
        <button 
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WordSelection',
  data() {
    return {
      words: [],
      selectedWords: [],
      selectedGrade: '',
      selectedTextbook: '',
      selectedDifficulty: '',
      selectedStatus: '',
      currentPage: 1,
      pageSize: 20,
      totalWords: 0,
      loading: false
    }
  },
  computed: {
    filteredWords() {
      let filtered = this.words
      
      if (this.selectedGrade) {
        filtered = filtered.filter(word => word.grade == this.selectedGrade)
      }
      
      if (this.selectedTextbook) {
        filtered = filtered.filter(word => word.textbook_version === this.selectedTextbook)
      }
      
      if (this.selectedDifficulty) {
        filtered = filtered.filter(word => word.difficulty == this.selectedDifficulty)
      }
      
      if (this.selectedStatus) {
        filtered = filtered.filter(word => word.status === this.selectedStatus)
      }
      
      return filtered
    },
    totalPages() {
      return Math.ceil(this.filteredWords.length / this.pageSize)
    },
    unlearnedCount() {
      return this.filteredWords.filter(word => word.status === 'unlearned').length
    }
  },
  mounted() {
    this.loadWords()
  },
  methods: {
    loadWords() {
      this.loading = true
      // 模拟加载单词数据
      setTimeout(() => {
        this.words = [
          {
            id: 1,
            word: 'apple',
            phonetic: '/ˈæpl/',
            definition: '苹果',
            grade: 1,
            textbook_version: '人教版',
            difficulty: 1,
            status: 'unlearned'
          },
          {
            id: 2,
            word: 'book',
            phonetic: '/bʊk/',
            definition: '书',
            grade: 1,
            textbook_version: '人教版',
            difficulty: 1,
            status: 'learning'
          },
          {
            id: 3,
            word: 'computer',
            phonetic: '/kəmˈpjuːtər/',
            definition: '计算机',
            grade: 3,
            textbook_version: '外研版',
            difficulty: 2,
            status: 'mastered'
          }
        ]
        this.totalWords = this.words.length
        this.loading = false
      }, 500)
    },
    selectAll() {
      this.selectedWords = this.filteredWords.map(word => word.id)
    },
    selectNone() {
      this.selectedWords = []
    },
    selectUnlearned() {
      this.selectedWords = this.filteredWords
        .filter(word => word.status === 'unlearned')
        .map(word => word.id)
    },
    startLearning() {
      if (this.selectedWords.length === 0) {
        alert('请先选择要学习的单词')
        return
      }
      
      // 跳转到学习页面，传递选中的单词ID
      this.$router.push({
        path: '/word-challenge',
        query: { words: this.selectedWords.join(',') }
      })
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    getStatusClass(status) {
      return {
        'status-unlearned': status === 'unlearned',
        'status-learning': status === 'learning',
        'status-mastered': status === 'mastered'
      }
    },
    getStatusText(status) {
      const statusMap = {
        'unlearned': '未学习',
        'learning': '学习中',
        'mastered': '已掌握'
      }
      return statusMap[status] || status
    },
    getDifficultyText(difficulty) {
      const difficultyMap = {
        1: '简单',
        2: '中等',
        3: '困难'
      }
      return difficultyMap[difficulty] || difficulty
    }
  }
}
</script>

