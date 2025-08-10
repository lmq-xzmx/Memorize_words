<template>
  <div class="word-examples-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="fas fa-quote-left"></i>
        单词例句
      </h1>
      <p class="page-subtitle">学习单词的最佳方式是通过例句理解其用法</p>
    </div>

    <!-- 统计信息 -->
    <div class="stats-card">
      <div class="stat-item">
        <div class="stat-number">{{ totalWords }}</div>
        <div class="stat-label">个单词包含例句</div>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-form">
        <div class="form-group">
          <label for="search">搜索单词或例句</label>
          <input
            type="text"
            id="search"
            v-model="searchQuery"
            @input="handleSearch"
            placeholder="输入单词、释义或例句内容..."
            class="form-control"
          />
        </div>
        
        <div class="form-group">
          <label for="grade">年级筛选</label>
          <select
            id="grade"
            v-model="gradeFilter"
            @change="handleSearch"
            class="form-control"
          >
            <option value="">所有年级</option>
            <option v-for="grade in gradeChoices" :key="grade.value" :value="grade.value">
              {{ grade.label }}
            </option>
          </select>
        </div>
        
        <div class="form-actions">
          <button @click="handleSearch" class="btn btn-primary">
            <i class="fas fa-search"></i>
            搜索
          </button>
          <button @click="clearSearch" class="btn btn-secondary">
            <i class="fas fa-times"></i>
            清除
          </button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载单词例句...</p>
    </div>

    <!-- 单词列表 -->
    <div v-else-if="words.length > 0" class="words-list">
      <div v-for="word in words" :key="word.id" class="word-card">
        <div class="word-header">
          <h3 class="word-title">{{ word.word }}</h3>
          <span v-if="word.phonetic" class="phonetic">{{ word.phonetic }}</span>
        </div>
        
        <div v-if="word.definition" class="definition">
          <i class="fas fa-book-open"></i>
          {{ word.definition }}
        </div>
        
        <div class="example-section">
          <h6 class="example-title">
            <i class="fas fa-quote-left"></i>
            例句
          </h6>
          <p class="example-text">{{ word.example }}</p>
        </div>
        
        <div class="word-meta">
          <span v-if="word.part_of_speech" class="meta-tag pos">
            <i class="fas fa-tag"></i>
            {{ word.part_of_speech }}
          </span>
          
          <span v-if="word.grade" class="meta-tag grade">
            <i class="fas fa-graduation-cap"></i>
            {{ getGradeLabel(word.grade) }}
          </span>
          
          <span v-if="word.textbook_version" class="meta-tag">
            <i class="fas fa-book"></i>
            {{ word.textbook_version }}
          </span>
          
          <span v-if="word.difficulty_level" class="meta-tag">
            <i class="fas fa-star"></i>
            难度 {{ word.difficulty_level }}
          </span>
        </div>
      </div>
    </div>

    <!-- 无结果状态 -->
    <div v-else class="no-results">
      <i class="fas fa-search"></i>
      <h4>没有找到相关单词</h4>
      <p>请尝试调整搜索条件或清除筛选器</p>
      <button @click="clearSearch" class="btn btn-primary">
        <i class="fas fa-refresh"></i>
        查看所有例句
      </button>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination-section">
      <nav class="pagination">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="page-btn"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="goToPage(page)"
          :class="['page-btn', { active: page === currentPage }]"
        >
          {{ page }}
        </button>
        
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </nav>
    </div>
  </div>
</template>

<script>
import { wordAPI } from '../utils/api.js'

export default {
  name: 'WordExamples',
  data() {
    return {
      words: [],
      loading: false,
      searchQuery: '',
      gradeFilter: '',
      currentPage: 1,
      totalPages: 1,
      totalWords: 0,
      searchTimeout: null,
      gradeChoices: [
        { value: '1', label: '一年级' },
        { value: '2', label: '二年级' },
        { value: '3', label: '三年级' },
        { value: '4', label: '四年级' },
        { value: '5', label: '五年级' },
        { value: '6', label: '六年级' },
        { value: '7', label: '初一' },
        { value: '8', label: '初二' },
        { value: '9', label: '初三' },
        { value: '10', label: '高一' },
        { value: '11', label: '高二' },
        { value: '12', label: '高三' }
      ]
    }
  },
  computed: {
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.currentPage - 2)
      const end = Math.min(this.totalPages, this.currentPage + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    }
  },
  mounted() {
    this.loadWords()
  },
  methods: {
    async loadWords() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          search: this.searchQuery,
          grade: this.gradeFilter
        }
        
        // 过滤空参数
        Object.keys(params).forEach(key => {
          if (!params[key]) {
            delete params[key]
          }
        })
        
        const response = await wordAPI.getWordExamples(params)
        
        this.words = response.data.results || []
        this.totalWords = response.data.count || 0
        this.totalPages = Math.ceil(this.totalWords / 20) // 假设每页20个
        
      } catch (error) {
        console.error('加载单词例句失败:', error)
        this.$message?.error('加载单词例句失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    handleSearch() {
      // 防抖搜索
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.loadWords()
      }, 300)
    },
    
    clearSearch() {
      this.searchQuery = ''
      this.gradeFilter = ''
      this.currentPage = 1
      this.loadWords()
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadWords()
        
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    
    getGradeLabel(gradeValue) {
      const grade = this.gradeChoices.find(g => g.value === gradeValue)
      return grade ? grade.label : gradeValue
    }
  }
}
</script>

<style scoped>
.word-examples-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
  padding: 0;
}

.word-examples-page::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: float 20s ease-in-out infinite;
  z-index: 1;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px 20px;
  position: relative;
  z-index: 10;
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  color: white;
  margin-bottom: 15px;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  position: relative;
}

.page-title i {
  margin-right: 20px;
  color: rgba(255, 255, 255, 0.9);
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  color: #2d3748;
  padding: 35px;
  border-radius: 20px;
  margin: 0 20px 40px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 10;
  transition: all 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.stat-number {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 1.2rem;
  color: #718096;
  font-weight: 600;
}

.search-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  margin: 0 20px 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 10;
  transition: all 0.3s ease;
}

.search-section:hover {
  transform: translateY(-3px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.search-form {
  display: flex;
  gap: 25px;
  align-items: end;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 220px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.form-actions {
  display: flex;
  gap: 15px;
  align-items: end;
}

.btn {
  padding: 14px 24px;
  border: none;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(108, 117, 125, 0.9);
  color: white;
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(90, 98, 104, 0.95);
  transform: translateY(-2px);
}

.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.8);
  position: relative;
  z-index: 10;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 25px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.words-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
  padding: 0 20px;
  position: relative;
  z-index: 10;
  max-width: 1200px;
  margin: 0 auto;
}

.word-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.word-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.word-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.word-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.phonetic {
  font-size: 1.3rem;
  color: #718096;
  font-style: italic;
  font-weight: 500;
  background: rgba(102, 126, 234, 0.1);
  padding: 5px 12px;
  border-radius: 15px;
}

.definition {
  font-size: 1.1rem;
  color: #4a5568;
  margin-bottom: 25px;
  padding: 18px 20px;
  background: rgba(52, 152, 219, 0.1);
  border-radius: 15px;
  border-left: 4px solid #3498db;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
}

.example-section {
  margin-bottom: 25px;
  padding: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 18px;
  color: white;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.example-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.example-text {
  font-size: 1.15rem;
  line-height: 1.7;
  margin: 0;
  font-style: italic;
  font-weight: 400;
}

.word-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-tag {
  background: rgba(236, 240, 241, 0.8);
  color: #2d3748;
  padding: 8px 16px;
  border-radius: 25px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.meta-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.meta-tag.grade {
  background: rgba(232, 245, 232, 0.9);
  color: #27ae60;
  border: 1px solid rgba(39, 174, 96, 0.2);
}

.meta-tag.pos {
  background: rgba(255, 243, 205, 0.9);
  color: #856404;
  border: 1px solid rgba(133, 100, 4, 0.2);
}

.no-results {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.8);
  position: relative;
  z-index: 10;
}

.no-results i {
  font-size: 5rem;
  margin-bottom: 25px;
  color: rgba(255, 255, 255, 0.6);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.8; }
}

.no-results h4 {
  margin-bottom: 18px;
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
}

.no-results p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  margin-bottom: 25px;
}

.pagination-section {
  margin-top: 50px;
  padding: 0 20px 40px;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 10;
}

.pagination {
  display: flex;
  gap: 8px;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 15px 20px;
  border-radius: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.page-btn {
  padding: 12px 16px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.8);
  color: #667eea;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  backdrop-filter: blur(10px);
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.page-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .word-examples-page {
    padding: 10px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .search-form {
    flex-direction: column;
  }
  
  .form-group {
    min-width: 100%;
  }
  
  .form-actions {
    width: 100%;
    justify-content: center;
  }
  
  .word-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .word-title {
    font-size: 1.5rem;
  }
}
</style>