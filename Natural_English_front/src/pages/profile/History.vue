<template>
  <div class="history-page" v-permission="['user', 'teacher', 'admin']">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>学习历史</h1>
      <p>查看您的学习记录和进度轨迹</p>
    </div>

    <!-- 筛选器 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <label>时间范围：</label>
          <select v-model="filters.timeRange">
            <option value="today">今天</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="all">全部</option>
          </select>
        </div>
        <div class="filter-item">
          <label>学习类型：</label>
          <select v-model="filters.type">
            <option value="all">全部</option>
            <option value="word">单词学习</option>
            <option value="sentence">句子学习</option>
            <option value="grammar">语法学习</option>
            <option value="listening">听力练习</option>
            <option value="practice">练习测试</option>
          </select>
        </div>
        <div class="filter-item">
          <label>结果筛选：</label>
          <select v-model="filters.result">
            <option value="all">全部</option>
            <option value="correct">正确</option>
            <option value="incorrect">错误</option>
          </select>
        </div>
        <button @click="applyFilters" class="filter-btn">筛选</button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalSessions }}</div>
          <div class="stat-label">学习次数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏱️</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalTime }}</div>
          <div class="stat-label">学习时长</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.accuracy }}%</div>
          <div class="stat-label">平均正确率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.wordsLearned }}</div>
          <div class="stat-label">学习单词</div>
        </div>
      </div>
    </div>

    <!-- 学习历史列表 -->
    <div class="history-list">
      <div class="list-header">
        <h2>学习记录</h2>
        <div class="sort-options">
          <label>排序：</label>
          <select v-model="sortBy" @change="sortHistory">
            <option value="date">按时间</option>
            <option value="type">按类型</option>
            <option value="score">按成绩</option>
          </select>
        </div>
      </div>

      <div class="history-items">
        <div 
          v-for="item in filteredHistory" 
          :key="item.id" 
          class="history-item"
          @click="showDetails(item)"
        >
          <div class="item-icon">
            <span :class="getTypeIcon(item.type)">{{ getTypeEmoji(item.type) }}</span>
          </div>
          <div class="item-content">
            <div class="item-header">
              <h3>{{ item.title }}</h3>
              <span class="item-time">{{ formatTime(item.createdAt) }}</span>
            </div>
            <div class="item-details">
              <span class="item-type">{{ getTypeName(item.type) }}</span>
              <span class="item-duration">{{ item.duration }}分钟</span>
              <span class="item-score" :class="getScoreClass(item.score)">{{ item.score }}%</span>
            </div>
            <div class="item-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: item.score + '%' }"
                ></div>
              </div>
              <span class="progress-text">{{ item.correctAnswers }}/{{ item.totalQuestions }}</span>
            </div>
          </div>
          <div class="item-actions">
            <button @click.stop="reviewMistakes(item)" v-if="item.incorrectAnswers > 0">
              复习错题
            </button>
            <button @click.stop="repeatSession(item)">
              重新练习
            </button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="page-btn"
        >
          上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>学习详情</h2>
          <button @click="closeDetailModal" class="close-btn">×</button>
        </div>
        <div class="modal-body" v-if="selectedItem">
          <div class="detail-section">
            <h3>基本信息</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label>学习类型：</label>
                <span>{{ getTypeName(selectedItem.type) }}</span>
              </div>
              <div class="detail-item">
                <label>开始时间：</label>
                <span>{{ formatDateTime(selectedItem.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <label>学习时长：</label>
                <span>{{ selectedItem.duration }}分钟</span>
              </div>
              <div class="detail-item">
                <label>总题数：</label>
                <span>{{ selectedItem.totalQuestions }}</span>
              </div>
              <div class="detail-item">
                <label>正确数：</label>
                <span>{{ selectedItem.correctAnswers }}</span>
              </div>
              <div class="detail-item">
                <label>正确率：</label>
                <span>{{ selectedItem.score }}%</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section" v-if="selectedItem.mistakes && selectedItem.mistakes.length > 0">
            <h3>错题回顾</h3>
            <div class="mistakes-list">
              <div v-for="mistake in selectedItem.mistakes" :key="mistake.id" class="mistake-item">
                <div class="mistake-question">{{ mistake.question }}</div>
                <div class="mistake-answers">
                  <div class="wrong-answer">您的答案：{{ mistake.userAnswer }}</div>
                  <div class="correct-answer">正确答案：{{ mistake.correctAnswer }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

interface HistoryItem {
  id: string
  title: string
  type: 'word' | 'sentence' | 'grammar' | 'listening' | 'practice'
  createdAt: string
  duration: number
  totalQuestions: number
  correctAnswers: number
  incorrectAnswers: number
  score: number
  mistakes?: Array<{
    id: string
    question: string
    userAnswer: string
    correctAnswer: string
  }>
}

interface Stats {
  totalSessions: number
  totalTime: string
  accuracy: number
  wordsLearned: number
}

const store = useStore()

// 响应式数据
const filters = ref({
  timeRange: 'all',
  type: 'all',
  result: 'all'
})

const sortBy = ref('date')
const currentPage = ref(1)
const pageSize = 10
const showDetailModal = ref(false)
const selectedItem = ref<HistoryItem | null>(null)

// 模拟数据
const historyData = ref<HistoryItem[]>([
  {
    id: '1',
    title: '日常词汇练习',
    type: 'word',
    createdAt: '2024-01-15T10:30:00Z',
    duration: 25,
    totalQuestions: 20,
    correctAnswers: 18,
    incorrectAnswers: 2,
    score: 90,
    mistakes: [
      {
        id: '1',
        question: 'What does "elaborate" mean?',
        userAnswer: 'simple',
        correctAnswer: 'detailed'
      }
    ]
  },
  {
    id: '2',
    title: '语法练习 - 时态',
    type: 'grammar',
    createdAt: '2024-01-14T14:20:00Z',
    duration: 30,
    totalQuestions: 15,
    correctAnswers: 12,
    incorrectAnswers: 3,
    score: 80
  }
])

const stats = ref<Stats>({
  totalSessions: 45,
  totalTime: '12小时30分钟',
  accuracy: 85,
  wordsLearned: 320
})

// 计算属性
const filteredHistory = computed(() => {
  let filtered = [...historyData.value]
  
  // 时间筛选
  if (filters.value.timeRange !== 'all') {
    const now = new Date()
    const filterDate = new Date()
    
    switch (filters.value.timeRange) {
      case 'today':
        filterDate.setHours(0, 0, 0, 0)
        break
      case 'week':
        filterDate.setDate(now.getDate() - 7)
        break
      case 'month':
        filterDate.setMonth(now.getMonth() - 1)
        break
    }
    
    filtered = filtered.filter(item => new Date(item.createdAt) >= filterDate)
  }
  
  // 类型筛选
  if (filters.value.type !== 'all') {
    filtered = filtered.filter(item => item.type === filters.value.type)
  }
  
  // 结果筛选
  if (filters.value.result !== 'all') {
    if (filters.value.result === 'correct') {
      filtered = filtered.filter(item => item.score >= 80)
    } else {
      filtered = filtered.filter(item => item.score < 80)
    }
  }
  
  return filtered.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize)
})

const totalPages = computed(() => {
  return Math.ceil(historyData.value.length / pageSize)
})

// 方法
const applyFilters = () => {
  currentPage.value = 1
  // 这里可以调用API重新获取数据
}

const sortHistory = () => {
  historyData.value.sort((a, b) => {
    switch (sortBy.value) {
      case 'date':
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      case 'type':
        return a.type.localeCompare(b.type)
      case 'score':
        return b.score - a.score
      default:
        return 0
    }
  })
}

const getTypeIcon = (type: string) => {
  const icons = {
    word: 'word-icon',
    sentence: 'sentence-icon',
    grammar: 'grammar-icon',
    listening: 'listening-icon',
    practice: 'practice-icon'
  }
  return icons[type as keyof typeof icons] || 'default-icon'
}

const getTypeEmoji = (type: string) => {
  const emojis = {
    word: '📝',
    sentence: '💬',
    grammar: '📖',
    listening: '🎧',
    practice: '🎯'
  }
  return emojis[type as keyof typeof emojis] || '📚'
}

const getTypeName = (type: string) => {
  const names = {
    word: '单词学习',
    sentence: '句子学习',
    grammar: '语法学习',
    listening: '听力练习',
    practice: '练习测试'
  }
  return names[type as keyof typeof names] || '未知类型'
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 60) return 'score-average'
  return 'score-poor'
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const showDetails = (item: HistoryItem) => {
  selectedItem.value = item
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedItem.value = null
}

const reviewMistakes = (item: HistoryItem) => {
  // 跳转到错题复习页面
  console.log('复习错题:', item.id)
}

const repeatSession = (item: HistoryItem) => {
  // 重新开始相同类型的练习
  console.log('重新练习:', item.id)
}

// 生命周期
onMounted(() => {
  sortHistory()
})
</script>

<style scoped lang="scss">
.history-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  
  h1 {
    font-size: 28px;
    color: #333;
    margin-bottom: 8px;
  }
  
  p {
    color: #666;
    font-size: 16px;
  }
}

.filter-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  
  .filter-row {
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }
  
  .filter-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    label {
      font-weight: 500;
      color: #333;
    }
    
    select {
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
    }
  }
  
  .filter-btn {
    padding: 8px 16px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    
    &:hover {
      background: #0056b3;
    }
  }
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  
  .stat-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 15px;
    
    .stat-icon {
      font-size: 24px;
      width: 50px;
      height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f8f9fa;
      border-radius: 50%;
    }
    
    .stat-info {
      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
      }
      
      .stat-label {
        color: #666;
        font-size: 14px;
      }
    }
  }
}

.history-list {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  
  .list-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h2 {
      font-size: 20px;
      color: #333;
      margin: 0;
    }
    
    .sort-options {
      display: flex;
      align-items: center;
      gap: 8px;
      
      label {
        font-size: 14px;
        color: #666;
      }
      
      select {
        padding: 6px 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
      }
    }
  }
  
  .history-items {
    .history-item {
      padding: 20px;
      border-bottom: 1px solid #eee;
      display: flex;
      align-items: center;
      gap: 15px;
      cursor: pointer;
      transition: background-color 0.2s;
      
      &:hover {
        background: #f8f9fa;
      }
      
      &:last-child {
        border-bottom: none;
      }
      
      .item-icon {
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f0f8ff;
        border-radius: 50%;
        font-size: 20px;
      }
      
      .item-content {
        flex: 1;
        
        .item-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          
          h3 {
            font-size: 16px;
            color: #333;
            margin: 0;
          }
          
          .item-time {
            color: #666;
            font-size: 14px;
          }
        }
        
        .item-details {
          display: flex;
          gap: 15px;
          margin-bottom: 8px;
          
          span {
            font-size: 14px;
            color: #666;
          }
          
          .item-score {
            font-weight: 500;
            
            &.score-excellent {
              color: #28a745;
            }
            
            &.score-good {
              color: #007bff;
            }
            
            &.score-average {
              color: #ffc107;
            }
            
            &.score-poor {
              color: #dc3545;
            }
          }
        }
        
        .item-progress {
          display: flex;
          align-items: center;
          gap: 10px;
          
          .progress-bar {
            flex: 1;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            
            .progress-fill {
              height: 100%;
              background: #007bff;
              transition: width 0.3s;
            }
          }
          
          .progress-text {
            font-size: 12px;
            color: #666;
            min-width: 40px;
          }
        }
      }
      
      .item-actions {
        display: flex;
        gap: 8px;
        
        button {
          padding: 6px 12px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.2s;
          
          &:hover {
            background: #f8f9fa;
            border-color: #007bff;
            color: #007bff;
          }
        }
      }
    }
  }
}

.pagination {
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  
  .page-btn {
    padding: 8px 16px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    &:not(:disabled):hover {
      background: #f8f9fa;
    }
  }
  
  .page-info {
    color: #666;
    font-size: 14px;
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  
  .modal-content {
    background: white;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    
    .modal-header {
      padding: 20px;
      border-bottom: 1px solid #eee;
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        color: #333;
      }
      
      .close-btn {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        
        &:hover {
          color: #333;
        }
      }
    }
    
    .modal-body {
      padding: 20px;
      
      .detail-section {
        margin-bottom: 30px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        h3 {
          color: #333;
          margin-bottom: 15px;
          font-size: 18px;
        }
        
        .detail-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          
          .detail-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
            
            label {
              font-weight: 500;
              color: #666;
              font-size: 14px;
            }
            
            span {
              color: #333;
              font-size: 16px;
            }
          }
        }
        
        .mistakes-list {
          .mistake-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            
            .mistake-question {
              font-weight: 500;
              color: #333;
              margin-bottom: 8px;
            }
            
            .mistake-answers {
              display: flex;
              flex-direction: column;
              gap: 4px;
              
              .wrong-answer {
                color: #dc3545;
                font-size: 14px;
              }
              
              .correct-answer {
                color: #28a745;
                font-size: 14px;
              }
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .history-page {
    padding: 15px;
  }
  
  .filter-row {
    flex-direction: column;
    align-items: stretch;
    
    .filter-item {
      justify-content: space-between;
    }
  }
  
  .stats-overview {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .history-item {
    flex-direction: column;
    align-items: stretch;
    
    .item-content {
      .item-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
      }
      
      .item-details {
        flex-wrap: wrap;
      }
    }
    
    .item-actions {
      justify-content: center;
    }
  }
}
</style>