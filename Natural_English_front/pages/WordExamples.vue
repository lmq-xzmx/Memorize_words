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
import { wordAPI } from '../utils/api'

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

