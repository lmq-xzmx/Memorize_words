<template>
  <div class="student-progress" v-permission="['teacher', 'admin']">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>学生进度</h1>
      <p>跟踪和分析学生的学习进度</p>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-bar">
      <div class="search-section">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索学生姓名或学号"
            @input="handleSearch"
          >
          <span class="search-icon">🔍</span>
        </div>
        
        <select v-model="classFilter" @change="handleFilter" class="filter-select">
          <option value="">全部班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
        
        <select v-model="progressFilter" @change="handleFilter" class="filter-select">
          <option value="">全部进度</option>
          <option value="excellent">优秀 (90%+)</option>
          <option value="good">良好 (70-89%)</option>
          <option value="average">一般 (50-69%)</option>
          <option value="poor">需要帮助 (<50%)</option>
        </select>
        
        <select v-model="timeFilter" @change="handleFilter" class="filter-select">
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="quarter">本季度</option>
          <option value="all">全部时间</option>
        </select>
      </div>
      
      <div class="action-buttons">
        <button @click="exportProgress" class="export-btn">
          📊 导出报告
        </button>
        <button @click="showBatchModal = true" class="batch-btn">
          📝 批量操作
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon students">👨‍🎓</div>
        <div class="stat-content">
          <h3>{{ filteredStudents.length }}</h3>
          <p>学生总数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon average">📈</div>
        <div class="stat-content">
          <h3>{{ averageProgress }}%</h3>
          <p>平均进度</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">🔥</div>
        <div class="stat-content">
          <h3>{{ activeStudents }}</h3>
          <p>活跃学生</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon help">⚠️</div>
        <div class="stat-content">
          <h3>{{ studentsNeedHelp }}</h3>
          <p>需要帮助</p>
        </div>
      </div>
    </div>

    <!-- 进度图表 -->
    <div class="progress-charts">
      <div class="chart-container">
        <h3>学习进度分布</h3>
        <div class="progress-distribution">
          <div class="distribution-item excellent">
            <div class="distribution-bar" :style="{ width: progressDistribution.excellent + '%' }"></div>
            <span class="distribution-label">优秀 {{ progressDistribution.excellent }}%</span>
          </div>
          <div class="distribution-item good">
            <div class="distribution-bar" :style="{ width: progressDistribution.good + '%' }"></div>
            <span class="distribution-label">良好 {{ progressDistribution.good }}%</span>
          </div>
          <div class="distribution-item average">
            <div class="distribution-bar" :style="{ width: progressDistribution.average + '%' }"></div>
            <span class="distribution-label">一般 {{ progressDistribution.average }}%</span>
          </div>
          <div class="distribution-item poor">
            <div class="distribution-bar" :style="{ width: progressDistribution.poor + '%' }"></div>
            <span class="distribution-label">需要帮助 {{ progressDistribution.poor }}%</span>
          </div>
        </div>
      </div>
      
      <div class="chart-container">
        <h3>学习活跃度趋势</h3>
        <div class="activity-chart">
          <canvas ref="activityChart" width="400" height="200"></canvas>
        </div>
      </div>
    </div>

    <!-- 学生列表 -->
    <div class="students-container">
      <div class="list-header">
        <h2>学生进度详情</h2>
        <div class="sort-options">
          <select v-model="sortBy" @change="handleSort" class="sort-select">
            <option value="name">按姓名排序</option>
            <option value="progress">按进度排序</option>
            <option value="score">按分数排序</option>
            <option value="lastActive">按活跃度排序</option>
          </select>
          <button @click="toggleSortOrder" class="sort-order-btn">
            {{ sortOrder === 'asc' ? '↑' : '↓' }}
          </button>
        </div>
      </div>
      
      <div class="students-grid">
        <div 
          v-for="student in paginatedStudents" 
          :key="student.id" 
          class="student-card"
          :class="getProgressClass(student.progress)"
          @click="viewStudentDetail(student)"
        >
          <div class="student-header">
            <div class="student-avatar">
              {{ student.name.charAt(0) }}
            </div>
            <div class="student-info">
              <h4>{{ student.name }}</h4>
              <p>{{ student.studentId }} | {{ student.className }}</p>
            </div>
            <div class="student-status">
              <span :class="`status-dot ${student.isActive ? 'active' : 'inactive'}`"></span>
              <span class="last-active">{{ formatLastActive(student.lastActive) }}</span>
            </div>
          </div>
          
          <div class="progress-section">
            <div class="progress-header">
              <span>学习进度</span>
              <span class="progress-value">{{ student.progress }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: student.progress + '%' }"
                :class="getProgressClass(student.progress)"
              ></div>
            </div>
          </div>
          
          <div class="metrics-grid">
            <div class="metric">
              <span class="metric-value">{{ student.wordsLearned }}</span>
              <span class="metric-label">已学单词</span>
            </div>
            <div class="metric">
              <span class="metric-value">{{ student.averageScore }}%</span>
              <span class="metric-label">平均分</span>
            </div>
            <div class="metric">
              <span class="metric-value">{{ student.studyTime }}h</span>
              <span class="metric-label">学习时长</span>
            </div>
            <div class="metric">
              <span class="metric-value">{{ student.streak }}</span>
              <span class="metric-label">连续天数</span>
            </div>
          </div>
          
          <div class="recent-activities">
            <h5>最近活动</h5>
            <div class="activity-list">
              <div 
                v-for="activity in student.recentActivities.slice(0, 3)" 
                :key="activity.id" 
                class="activity-item"
              >
                <span class="activity-icon">{{ getActivityIcon(activity.type) }}</span>
                <span class="activity-text">{{ activity.description }}</span>
                <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-actions">
            <button @click.stop="sendMessage(student)" class="action-btn message">
              💬 发消息
            </button>
            <button @click.stop="viewProgress(student)" class="action-btn progress">
              📊 详细进度
            </button>
            <button @click.stop="assignTask(student)" class="action-btn task">
              📝 布置任务
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <button 
        @click="currentPage = 1" 
        :disabled="currentPage === 1"
        class="page-btn"
      >
        首页
      </button>
      <button 
        @click="currentPage--" 
        :disabled="currentPage === 1"
        class="page-btn"
      >
        上一页
      </button>
      
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
      </span>
      
      <button 
        @click="currentPage++" 
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        下一页
      </button>
      <button 
        @click="currentPage = totalPages" 
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        末页
      </button>
    </div>

    <!-- 学生详情弹窗 -->
    <div v-if="showStudentModal" class="modal-overlay" @click="closeStudentModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedStudent?.name }} - 学习详情</h2>
          <button @click="closeStudentModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedStudent" class="student-detail">
            <!-- 基本信息 -->
            <div class="detail-section">
              <h3>基本信息</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>学号:</label>
                  <span>{{ selectedStudent.studentId }}</span>
                </div>
                <div class="info-item">
                  <label>班级:</label>
                  <span>{{ selectedStudent.className }}</span>
                </div>
                <div class="info-item">
                  <label>注册时间:</label>
                  <span>{{ formatDate(selectedStudent.joinDate) }}</span>
                </div>
                <div class="info-item">
                  <label>最后活跃:</label>
                  <span>{{ formatLastActive(selectedStudent.lastActive) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 学习统计 -->
            <div class="detail-section">
              <h3>学习统计</h3>
              <div class="stats-grid">
                <div class="stat-box">
                  <div class="stat-number">{{ selectedStudent.progress }}%</div>
                  <div class="stat-title">总体进度</div>
                </div>
                <div class="stat-box">
                  <div class="stat-number">{{ selectedStudent.wordsLearned }}</div>
                  <div class="stat-title">已学单词</div>
                </div>
                <div class="stat-box">
                  <div class="stat-number">{{ selectedStudent.averageScore }}%</div>
                  <div class="stat-title">平均分数</div>
                </div>
                <div class="stat-box">
                  <div class="stat-number">{{ selectedStudent.studyTime }}h</div>
                  <div class="stat-title">学习时长</div>
                </div>
              </div>
            </div>
            
            <!-- 学习进度图表 -->
            <div class="detail-section">
              <h3>学习进度趋势</h3>
              <div class="progress-chart">
                <canvas ref="studentProgressChart" width="600" height="300"></canvas>
              </div>
            </div>
            
            <!-- 最近活动 -->
            <div class="detail-section">
              <h3>最近活动</h3>
              <div class="activity-timeline">
                <div 
                  v-for="activity in selectedStudent.recentActivities" 
                  :key="activity.id" 
                  class="timeline-item"
                >
                  <div class="timeline-dot"></div>
                  <div class="timeline-content">
                    <div class="timeline-header">
                      <span class="activity-type">{{ getActivityIcon(activity.type) }} {{ activity.description }}</span>
                      <span class="activity-timestamp">{{ formatDateTime(activity.timestamp) }}</span>
                    </div>
                    <div v-if="activity.details" class="timeline-details">
                      {{ activity.details }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量操作弹窗 -->
    <div v-if="showBatchModal" class="modal-overlay" @click="closeBatchModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>批量操作</h2>
          <button @click="closeBatchModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="batch-options">
            <div class="option-group">
              <h4>选择学生</h4>
              <div class="student-selection">
                <label class="checkbox-item">
                  <input type="checkbox" @change="selectAllStudents" :checked="allSelected">
                  全选
                </label>
                <div class="student-list">
                  <label 
                    v-for="student in filteredStudents" 
                    :key="student.id" 
                    class="checkbox-item"
                  >
                    <input 
                      type="checkbox" 
                      :value="student.id" 
                      v-model="selectedStudentIds"
                    >
                    {{ student.name }} ({{ student.className }})
                  </label>
                </div>
              </div>
            </div>
            
            <div class="option-group">
              <h4>操作类型</h4>
              <div class="action-options">
                <label class="radio-item">
                  <input type="radio" value="message" v-model="batchAction">
                  发送消息
                </label>
                <label class="radio-item">
                  <input type="radio" value="assignment" v-model="batchAction">
                  布置作业
                </label>
                <label class="radio-item">
                  <input type="radio" value="reminder" v-model="batchAction">
                  发送提醒
                </label>
                <label class="radio-item">
                  <input type="radio" value="export" v-model="batchAction">
                  导出数据
                </label>
              </div>
            </div>
            
            <div v-if="batchAction === 'message'" class="option-group">
              <h4>消息内容</h4>
              <textarea 
                v-model="batchMessage" 
                placeholder="请输入要发送的消息内容"
                rows="4"
              ></textarea>
            </div>
          </div>
          
          <div class="batch-actions">
            <button @click="closeBatchModal" class="cancel-btn">
              取消
            </button>
            <button @click="executeBatchAction" class="submit-btn" :disabled="!canExecuteBatch">
              执行操作
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

interface Student {
  id: string
  name: string
  studentId: string
  className: string
  classId: string
  progress: number
  wordsLearned: number
  averageScore: number
  studyTime: number
  streak: number
  isActive: boolean
  lastActive: string
  joinDate: string
  recentActivities: Activity[]
}

interface Activity {
  id: string
  type: 'study' | 'test' | 'assignment' | 'login'
  description: string
  timestamp: string
  details?: string
}

interface Class {
  id: string
  name: string
}

const router = useRouter()

// 响应式数据
const students = ref<Student[]>([
  {
    id: '1',
    name: '张小明',
    studentId: 'S001',
    className: '高一A班',
    classId: '1',
    progress: 85,
    wordsLearned: 1250,
    averageScore: 92,
    studyTime: 45,
    streak: 12,
    isActive: true,
    lastActive: '2024-01-15T14:30:00Z',
    joinDate: '2024-01-01',
    recentActivities: [
      {
        id: '1',
        type: 'study',
        description: '完成词汇练习',
        timestamp: '2024-01-15T14:30:00Z',
        details: '学习了20个新单词'
      },
      {
        id: '2',
        type: 'test',
        description: '完成单元测试',
        timestamp: '2024-01-15T10:15:00Z',
        details: '得分: 95分'
      }
    ]
  },
  {
    id: '2',
    name: '李小红',
    studentId: 'S002',
    className: '高一A班',
    classId: '1',
    progress: 72,
    wordsLearned: 980,
    averageScore: 88,
    studyTime: 38,
    streak: 8,
    isActive: true,
    lastActive: '2024-01-15T13:45:00Z',
    joinDate: '2024-01-01',
    recentActivities: [
      {
        id: '3',
        type: 'assignment',
        description: '提交作业',
        timestamp: '2024-01-15T13:45:00Z',
        details: '语法练习作业'
      }
    ]
  },
  {
    id: '3',
    name: '王小强',
    studentId: 'S003',
    className: '高二B班',
    classId: '2',
    progress: 95,
    wordsLearned: 1580,
    averageScore: 96,
    studyTime: 62,
    streak: 25,
    isActive: true,
    lastActive: '2024-01-15T15:20:00Z',
    joinDate: '2023-12-15',
    recentActivities: [
      {
        id: '4',
        type: 'study',
        description: '完成高级阅读',
        timestamp: '2024-01-15T15:20:00Z',
        details: '阅读理解练习'
      }
    ]
  },
  {
    id: '4',
    name: '赵小华',
    studentId: 'S004',
    className: '高一A班',
    classId: '1',
    progress: 45,
    wordsLearned: 650,
    averageScore: 68,
    studyTime: 22,
    streak: 3,
    isActive: false,
    lastActive: '2024-01-13T16:30:00Z',
    joinDate: '2024-01-01',
    recentActivities: [
      {
        id: '5',
        type: 'login',
        description: '登录系统',
        timestamp: '2024-01-13T16:30:00Z'
      }
    ]
  }
])

const classes = ref<Class[]>([
  { id: '1', name: '高一A班' },
  { id: '2', name: '高二B班' },
  { id: '3', name: '高三冲刺班' }
])

const searchQuery = ref('')
const classFilter = ref('')
const progressFilter = ref('')
const timeFilter = ref('month')
const sortBy = ref('name')
const sortOrder = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)
const pageSize = ref(12)

const showStudentModal = ref(false)
const selectedStudent = ref<Student | null>(null)
const showBatchModal = ref(false)
const selectedStudentIds = ref<string[]>([])
const batchAction = ref('')
const batchMessage = ref('')

const activityChart = ref<HTMLCanvasElement>()
const studentProgressChart = ref<HTMLCanvasElement>()

// 计算属性
const filteredStudents = computed(() => {
  let result = students.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(student => 
      student.name.toLowerCase().includes(query) ||
      student.studentId.toLowerCase().includes(query)
    )
  }
  
  // 班级过滤
  if (classFilter.value) {
    result = result.filter(student => student.classId === classFilter.value)
  }
  
  // 进度过滤
  if (progressFilter.value) {
    switch (progressFilter.value) {
      case 'excellent':
        result = result.filter(student => student.progress >= 90)
        break
      case 'good':
        result = result.filter(student => student.progress >= 70 && student.progress < 90)
        break
      case 'average':
        result = result.filter(student => student.progress >= 50 && student.progress < 70)
        break
      case 'poor':
        result = result.filter(student => student.progress < 50)
        break
    }
  }
  
  // 排序
  result.sort((a, b) => {
    let aVal: any = a[sortBy.value as keyof Student]
    let bVal: any = b[sortBy.value as keyof Student]
    
    if (sortBy.value === 'lastActive') {
      aVal = new Date(aVal).getTime()
      bVal = new Date(bVal).getTime()
    }
    
    if (sortOrder.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
  
  return result
})

const totalPages = computed(() => {
  return Math.ceil(filteredStudents.value.length / pageSize.value)
})

const paginatedStudents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStudents.value.slice(start, end)
})

const averageProgress = computed(() => {
  if (filteredStudents.value.length === 0) return 0
  const total = filteredStudents.value.reduce((sum, student) => sum + student.progress, 0)
  return Math.round(total / filteredStudents.value.length)
})

const activeStudents = computed(() => {
  return filteredStudents.value.filter(student => student.isActive).length
})

const studentsNeedHelp = computed(() => {
  return filteredStudents.value.filter(student => student.progress < 50).length
})

const progressDistribution = computed(() => {
  const total = filteredStudents.value.length
  if (total === 0) return { excellent: 0, good: 0, average: 0, poor: 0 }
  
  const excellent = filteredStudents.value.filter(s => s.progress >= 90).length
  const good = filteredStudents.value.filter(s => s.progress >= 70 && s.progress < 90).length
  const average = filteredStudents.value.filter(s => s.progress >= 50 && s.progress < 70).length
  const poor = filteredStudents.value.filter(s => s.progress < 50).length
  
  return {
    excellent: Math.round((excellent / total) * 100),
    good: Math.round((good / total) * 100),
    average: Math.round((average / total) * 100),
    poor: Math.round((poor / total) * 100)
  }
})

const allSelected = computed(() => {
  return selectedStudentIds.value.length === filteredStudents.value.length
})

const canExecuteBatch = computed(() => {
  return selectedStudentIds.value.length > 0 && batchAction.value !== ''
})

// 方法
const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleSort = () => {
  currentPage.value = 1
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const getProgressClass = (progress: number) => {
  if (progress >= 90) return 'excellent'
  if (progress >= 70) return 'good'
  if (progress >= 50) return 'average'
  return 'poor'
}

const getActivityIcon = (type: string) => {
  const icons = {
    study: '📚',
    test: '📝',
    assignment: '📋',
    login: '🔑'
  }
  return icons[type as keyof typeof icons] || '📌'
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (hours < 24) {
    return `${hours}小时前`
  } else {
    return `${days}天前`
  }
}

const formatLastActive = (dateString: string) => {
  return formatTime(dateString)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const viewStudentDetail = (student: Student) => {
  selectedStudent.value = student
  showStudentModal.value = true
  
  nextTick(() => {
    drawStudentProgressChart()
  })
}

const closeStudentModal = () => {
  showStudentModal.value = false
  selectedStudent.value = null
}

const sendMessage = (student: Student) => {
  console.log('发送消息给:', student.name)
}

const viewProgress = (student: Student) => {
  router.push(`/teacher/students/${student.id}/progress`)
}

const assignTask = (student: Student) => {
  console.log('为学生布置任务:', student.name)
}

const exportProgress = () => {
  console.log('导出进度报告')
}

const selectAllStudents = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.checked) {
    selectedStudentIds.value = filteredStudents.value.map(s => s.id)
  } else {
    selectedStudentIds.value = []
  }
}

const closeBatchModal = () => {
  showBatchModal.value = false
  selectedStudentIds.value = []
  batchAction.value = ''
  batchMessage.value = ''
}

const executeBatchAction = () => {
  console.log('执行批量操作:', {
    action: batchAction.value,
    students: selectedStudentIds.value,
    message: batchMessage.value
  })
  closeBatchModal()
}

const drawActivityChart = () => {
  if (!activityChart.value) return
  
  const ctx = activityChart.value.getContext('2d')
  if (!ctx) return
  
  // 简单的活跃度趋势图
  ctx.clearRect(0, 0, 400, 200)
  ctx.strokeStyle = '#007bff'
  ctx.lineWidth = 2
  
  ctx.beginPath()
  const points = [50, 80, 65, 90, 75, 85, 95]
  points.forEach((point, index) => {
    const x = (index / (points.length - 1)) * 350 + 25
    const y = 175 - (point / 100) * 150
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
}

const drawStudentProgressChart = () => {
  if (!studentProgressChart.value) return
  
  const ctx = studentProgressChart.value.getContext('2d')
  if (!ctx) return
  
  // 简单的学生进度图表
  ctx.clearRect(0, 0, 600, 300)
  ctx.strokeStyle = '#28a745'
  ctx.lineWidth = 3
  
  ctx.beginPath()
  const progressData = [20, 35, 45, 60, 70, 80, 85]
  progressData.forEach((progress, index) => {
    const x = (index / (progressData.length - 1)) * 550 + 25
    const y = 275 - (progress / 100) * 250
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
}

// 生命周期
onMounted(() => {
  nextTick(() => {
    drawActivityChart()
  })
})
</script>

<style scoped lang="scss">
.student-progress {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  
  h1 {
    font-size: 32px;
    color: #333;
    margin-bottom: 8px;
  }
  
  p {
    color: #666;
    font-size: 16px;
  }
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
  
  .search-section {
    display: flex;
    gap: 15px;
    flex: 1;
    
    .search-box {
      position: relative;
      flex: 1;
      max-width: 300px;
      
      input {
        width: 100%;
        padding: 10px 40px 10px 15px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
        
        &:focus {
          outline: none;
          border-color: #007bff;
        }
      }
      
      .search-icon {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        color: #666;
      }
    }
    
    .filter-select {
      padding: 10px 15px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
      background: white;
      
      &:focus {
        outline: none;
        border-color: #007bff;
      }
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 10px;
    
    button {
      padding: 10px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
      
      &.export-btn {
        background: #28a745;
        color: white;
        
        &:hover {
          background: #1e7e34;
        }
      }
      
      &.batch-btn {
        background: #6f42c1;
        color: white;
        
        &:hover {
          background: #5a2d91;
        }
      }
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
      width: 50px;
      height: 50px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      
      &.students {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.average {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.active {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.help {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      }
    }
    
    .stat-content {
      h3 {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
      }
      
      p {
        color: #666;
        font-size: 14px;
      }
    }
  }
}

.progress-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
  
  .chart-container {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    
    h3 {
      color: #333;
      margin-bottom: 20px;
      font-size: 18px;
    }
    
    .progress-distribution {
      .distribution-item {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        
        .distribution-bar {
          height: 20px;
          border-radius: 10px;
          margin-right: 10px;
          min-width: 20px;
          transition: width 0.3s;
          
          &.excellent {
            background: #28a745;
          }
          
          &.good {
            background: #007bff;
          }
          
          &.average {
            background: #ffc107;
          }
          
          &.poor {
            background: #dc3545;
          }
        }
        
        .distribution-label {
          font-size: 14px;
          color: #666;
        }
      }
    }
    
    .activity-chart {
      canvas {
        width: 100%;
        height: 200px;
      }
    }
  }
}

.students-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      color: #333;
      font-size: 20px;
    }
    
    .sort-options {
      display: flex;
      gap: 10px;
      align-items: center;
      
      .sort-select {
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        
        &:focus {
          outline: none;
          border-color: #007bff;
        }
      }
      
      .sort-order-btn {
        width: 32px;
        height: 32px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        
        &:hover {
          background: #f8f9fa;
        }
      }
    }
  }
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  
  .student-card {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    &.excellent {
      border-left: 4px solid #28a745;
    }
    
    &.good {
      border-left: 4px solid #007bff;
    }
    
    &.average {
      border-left: 4px solid #ffc107;
    }
    
    &.poor {
      border-left: 4px solid #dc3545;
    }
    
    .student-header {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 15px;
      
      .student-avatar {
        width: 50px;
        height: 50px;
        background: #007bff;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
      }
      
      .student-info {
        flex: 1;
        
        h4 {
          color: #333;
          margin-bottom: 4px;
          font-size: 16px;
        }
        
        p {
          color: #666;
          font-size: 12px;
        }
      }
      
      .student-status {
        text-align: right;
        
        .status-dot {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-right: 5px;
          
          &.active {
            background: #28a745;
          }
          
          &.inactive {
            background: #dc3545;
          }
        }
        
        .last-active {
          display: block;
          font-size: 11px;
          color: #666;
        }
      }
    }
    
    .progress-section {
      margin-bottom: 15px;
      
      .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
        font-size: 12px;
        
        .progress-value {
          font-weight: bold;
          color: #333;
        }
      }
      
      .progress-bar {
        height: 8px;
        background: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
        
        .progress-fill {
          height: 100%;
          transition: width 0.3s;
          
          &.excellent {
            background: #28a745;
          }
          
          &.good {
            background: #007bff;
          }
          
          &.average {
            background: #ffc107;
          }
          
          &.poor {
            background: #dc3545;
          }
        }
      }
    }
    
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin-bottom: 15px;
      
      .metric {
        text-align: center;
        
        .metric-value {
          display: block;
          font-size: 16px;
          font-weight: bold;
          color: #007bff;
        }
        
        .metric-label {
          font-size: 10px;
          color: #666;
        }
      }
    }
    
    .recent-activities {
      margin-bottom: 15px;
      
      h5 {
        color: #333;
        margin-bottom: 10px;
        font-size: 14px;
      }
      
      .activity-list {
        .activity-item {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 5px;
          font-size: 12px;
          
          .activity-icon {
            font-size: 14px;
          }
          
          .activity-text {
            flex: 1;
            color: #333;
          }
          
          .activity-time {
            color: #666;
          }
        }
      }
    }
    
    .card-actions {
      display: flex;
      gap: 8px;
      
      .action-btn {
        flex: 1;
        padding: 6px 10px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 4px;
        cursor: pointer;
        font-size: 11px;
        transition: all 0.2s;
        
        &:hover {
          background: #f8f9fa;
        }
        
        &.message {
          border-color: #007bff;
          color: #007bff;
          
          &:hover {
            background: #007bff;
            color: white;
          }
        }
        
        &.progress {
          border-color: #28a745;
          color: #28a745;
          
          &:hover {
            background: #28a745;
            color: white;
          }
        }
        
        &.task {
          border-color: #ffc107;
          color: #856404;
          
          &:hover {
            background: #ffc107;
            color: #856404;
          }
        }
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
  
  .page-btn {
    padding: 8px 16px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
    
    &:hover:not(:disabled) {
      background: #f8f9fa;
      border-color: #007bff;
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
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
    
    &.large {
      max-width: 900px;
    }
    
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
      
      .student-detail {
        .detail-section {
          margin-bottom: 30px;
          
          h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
          }
          
          .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            
            .info-item {
              display: flex;
              
              label {
                font-weight: 500;
                color: #666;
                min-width: 80px;
              }
              
              span {
                color: #333;
              }
            }
          }
          
          .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            
            .stat-box {
              text-align: center;
              padding: 20px;
              background: #f8f9fa;
              border-radius: 8px;
              
              .stat-number {
                font-size: 24px;
                font-weight: bold;
                color: #007bff;
                margin-bottom: 5px;
              }
              
              .stat-title {
                font-size: 12px;
                color: #666;
              }
            }
          }
          
          .progress-chart {
            canvas {
              width: 100%;
              height: 300px;
              border: 1px solid #eee;
              border-radius: 4px;
            }
          }
          
          .activity-timeline {
            .timeline-item {
              display: flex;
              margin-bottom: 20px;
              
              .timeline-dot {
                width: 12px;
                height: 12px;
                background: #007bff;
                border-radius: 50%;
                margin-right: 15px;
                margin-top: 4px;
                flex-shrink: 0;
              }
              
              .timeline-content {
                flex: 1;
                
                .timeline-header {
                  display: flex;
                  justify-content: space-between;
                  margin-bottom: 5px;
                  
                  .activity-type {
                    font-weight: 500;
                    color: #333;
                  }
                  
                  .activity-timestamp {
                    font-size: 12px;
                    color: #666;
                  }
                }
                
                .timeline-details {
                  font-size: 14px;
                  color: #666;
                }
              }
            }
          }
        }
      }
      
      .batch-options {
        .option-group {
          margin-bottom: 25px;
          
          h4 {
            color: #333;
            margin-bottom: 10px;
            font-size: 16px;
          }
          
          .student-selection {
            .checkbox-item {
              display: flex;
              align-items: center;
              margin-bottom: 8px;
              
              input[type="checkbox"] {
                margin-right: 8px;
              }
            }
            
            .student-list {
              max-height: 200px;
              overflow-y: auto;
              border: 1px solid #eee;
              border-radius: 4px;
              padding: 10px;
              margin-top: 10px;
            }
          }
          
          .action-options {
            .radio-item {
              display: flex;
              align-items: center;
              margin-bottom: 8px;
              
              input[type="radio"] {
                margin-right: 8px;
              }
            }
          }
          
          textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
            
            &:focus {
              outline: none;
              border-color: #007bff;
            }
          }
        }
      }
      
      .batch-actions {
        display: flex;
        gap: 10px;
        justify-content: flex-end;
        
        button {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          
          &.cancel-btn {
            background: #6c757d;
            color: white;
            
            &:hover {
              background: #545b62;
            }
          }
          
          &.submit-btn {
            background: #007bff;
            color: white;
            
            &:hover:not(:disabled) {
              background: #0056b3;
            }
            
            &:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .student-progress {
    padding: 15px;
  }
  
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    
    .search-section {
      flex-direction: column;
      
      .search-box {
        max-width: none;
      }
    }
  }
  
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .progress-charts {
    grid-template-columns: 1fr;
  }
  
  .students-grid {
    grid-template-columns: 1fr;
    
    .student-card {
      .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  }
  
  .modal-content {
    .modal-body {
      .student-detail {
        .detail-section {
          .info-grid {
            grid-template-columns: 1fr;
          }
          
          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      }
    }
  }
}
</style>