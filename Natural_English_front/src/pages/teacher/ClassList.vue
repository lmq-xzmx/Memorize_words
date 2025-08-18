<template>
  <div class="class-list" v-permission="['teacher', 'admin']">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>班级管理</h1>
      <p>管理您的所有班级和学生</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="search-filters">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索班级名称或班级代码"
            @input="handleSearch"
          >
          <span class="search-icon">🔍</span>
        </div>
        
        <select v-model="statusFilter" @change="handleFilter" class="filter-select">
          <option value="">全部状态</option>
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
          <option value="archived">已归档</option>
        </select>
        
        <select v-model="goalFilter" @change="handleFilter" class="filter-select">
          <option value="">全部目标</option>
          <option value="basic">基础英语</option>
          <option value="intermediate">中级英语</option>
          <option value="advanced">高级英语</option>
          <option value="exam">考试准备</option>
        </select>
      </div>
      
      <div class="action-buttons">
        <button @click="exportClasses" class="export-btn">
          📊 导出数据
        </button>
        <button @click="showCreateModal = true" class="create-btn">
          + 创建班级
        </button>
      </div>
    </div>

    <!-- 班级统计 -->
    <div class="class-stats">
      <div class="stat-item">
        <span class="stat-value">{{ filteredClasses.length }}</span>
        <span class="stat-label">总班级数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ totalStudents }}</span>
        <span class="stat-label">总学生数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ activeClasses }}</span>
        <span class="stat-label">活跃班级</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ averageProgress }}%</span>
        <span class="stat-label">平均进度</span>
      </div>
    </div>

    <!-- 班级列表 -->
    <div class="classes-container">
      <div class="view-toggle">
        <button 
          @click="viewMode = 'grid'" 
          :class="{ active: viewMode === 'grid' }"
          class="view-btn"
        >
          📱 卡片视图
        </button>
        <button 
          @click="viewMode = 'list'" 
          :class="{ active: viewMode === 'list' }"
          class="view-btn"
        >
          📋 列表视图
        </button>
      </div>
      
      <!-- 卡片视图 -->
      <div v-if="viewMode === 'grid'" class="classes-grid">
        <div 
          v-for="classItem in paginatedClasses" 
          :key="classItem.id" 
          class="class-card"
          :class="classItem.status"
        >
          <div class="card-header">
            <div class="class-info">
              <h3>{{ classItem.name }}</h3>
              <span class="class-code">{{ classItem.code }}</span>
            </div>
            <div class="class-status">
              <span :class="`status-badge ${classItem.status}`">
                {{ getStatusText(classItem.status) }}
              </span>
            </div>
          </div>
          
          <div class="card-content">
            <div class="class-description">
              <p>{{ classItem.description }}</p>
            </div>
            
            <div class="class-metrics">
              <div class="metric">
                <span class="metric-value">{{ classItem.studentCount }}</span>
                <span class="metric-label">学生</span>
              </div>
              <div class="metric">
                <span class="metric-value">{{ classItem.assignmentCount }}</span>
                <span class="metric-label">作业</span>
              </div>
              <div class="metric">
                <span class="metric-value">{{ classItem.averageScore }}%</span>
                <span class="metric-label">平均分</span>
              </div>
            </div>
            
            <div class="progress-section">
              <div class="progress-header">
                <span>学习进度</span>
                <span>{{ classItem.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: classItem.progress + '%' }"
                ></div>
              </div>
            </div>
            
            <div class="class-goal">
              <span class="goal-label">学习目标:</span>
              <span class="goal-value">{{ getGoalText(classItem.goal) }}</span>
            </div>
          </div>
          
          <div class="card-actions">
            <button @click="viewClassDetails(classItem.id)" class="action-btn primary">
              查看详情
            </button>
            <button @click="manageStudents(classItem.id)" class="action-btn">
              管理学生
            </button>
            <button @click="editClass(classItem)" class="action-btn">
              编辑
            </button>
            <button @click="showClassMenu(classItem, $event)" class="action-btn menu">
              ⋯
            </button>
          </div>
        </div>
      </div>
      
      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="classes-table">
        <table>
          <thead>
            <tr>
              <th @click="sortBy('name')" class="sortable">
                班级名称
                <span v-if="sortField === 'name'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>班级代码</th>
              <th @click="sortBy('studentCount')" class="sortable">
                学生数
                <span v-if="sortField === 'studentCount'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click="sortBy('averageScore')" class="sortable">
                平均分
                <span v-if="sortField === 'averageScore'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click="sortBy('progress')" class="sortable">
                进度
                <span v-if="sortField === 'progress'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>状态</th>
              <th>学习目标</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="classItem in paginatedClasses" :key="classItem.id">
              <td>
                <div class="class-name-cell">
                  <strong>{{ classItem.name }}</strong>
                  <small>{{ classItem.description }}</small>
                </div>
              </td>
              <td>
                <span class="class-code">{{ classItem.code }}</span>
              </td>
              <td>{{ classItem.studentCount }}</td>
              <td>
                <span class="score-badge" :class="getScoreClass(classItem.averageScore)">
                  {{ classItem.averageScore }}%
                </span>
              </td>
              <td>
                <div class="progress-cell">
                  <div class="mini-progress">
                    <div 
                      class="mini-progress-fill" 
                      :style="{ width: classItem.progress + '%' }"
                    ></div>
                  </div>
                  <span>{{ classItem.progress }}%</span>
                </div>
              </td>
              <td>
                <span :class="`status-badge ${classItem.status}`">
                  {{ getStatusText(classItem.status) }}
                </span>
              </td>
              <td>{{ getGoalText(classItem.goal) }}</td>
              <td>
                <div class="table-actions">
                  <button @click="viewClassDetails(classItem.id)" class="table-action-btn" title="查看详情">
                    👁️
                  </button>
                  <button @click="manageStudents(classItem.id)" class="table-action-btn" title="管理学生">
                    👥
                  </button>
                  <button @click="editClass(classItem)" class="table-action-btn" title="编辑">
                    ✏️
                  </button>
                  <button @click="showClassMenu(classItem, $event)" class="table-action-btn" title="更多">
                    ⋯
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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

    <!-- 创建/编辑班级弹窗 -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ showCreateModal ? '创建新班级' : '编辑班级' }}</h2>
          <button @click="closeModals" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="showCreateModal ? createClass() : updateClass()">
            <div class="form-row">
              <div class="form-group">
                <label>班级名称 *</label>
                <input 
                  v-model="classForm.name" 
                  type="text" 
                  placeholder="请输入班级名称"
                  required
                >
              </div>
              <div class="form-group">
                <label>班级代码</label>
                <input 
                  v-model="classForm.code" 
                  type="text" 
                  placeholder="自动生成或手动输入"
                >
              </div>
            </div>
            
            <div class="form-group">
              <label>班级描述</label>
              <textarea 
                v-model="classForm.description" 
                placeholder="请输入班级描述"
                rows="3"
              ></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>学习目标 *</label>
                <select v-model="classForm.goal" required>
                  <option value="">请选择学习目标</option>
                  <option value="basic">基础英语</option>
                  <option value="intermediate">中级英语</option>
                  <option value="advanced">高级英语</option>
                  <option value="exam">考试准备</option>
                </select>
              </div>
              <div class="form-group">
                <label>班级状态</label>
                <select v-model="classForm.status">
                  <option value="active">活跃</option>
                  <option value="inactive">非活跃</option>
                  <option value="archived">已归档</option>
                </select>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModals" class="cancel-btn">
                取消
              </button>
              <button type="submit" class="submit-btn">
                {{ showCreateModal ? '创建班级' : '保存修改' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 右键菜单 -->
    <div 
      v-if="showContextMenu" 
      class="context-menu" 
      :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }"
      @click="hideContextMenu"
    >
      <div class="menu-item" @click="viewClassDetails(selectedClass?.id)">
        👁️ 查看详情
      </div>
      <div class="menu-item" @click="manageStudents(selectedClass?.id)">
        👥 管理学生
      </div>
      <div class="menu-item" @click="editClass(selectedClass)">
        ✏️ 编辑班级
      </div>
      <div class="menu-item" @click="duplicateClass(selectedClass)">
        📋 复制班级
      </div>
      <div class="menu-divider"></div>
      <div class="menu-item" @click="archiveClass(selectedClass?.id)">
        📦 归档班级
      </div>
      <div class="menu-item danger" @click="deleteClass(selectedClass?.id)">
        🗑️ 删除班级
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface ClassItem {
  id: string
  name: string
  code: string
  description: string
  studentCount: number
  assignmentCount: number
  averageScore: number
  progress: number
  status: 'active' | 'inactive' | 'archived'
  goal: 'basic' | 'intermediate' | 'advanced' | 'exam'
  createdAt: string
}

interface ClassForm {
  name: string
  code: string
  description: string
  goal: string
  status: string
}

const router = useRouter()

// 响应式数据
const classes = ref<ClassItem[]>([
  {
    id: '1',
    name: '高一英语A班',
    code: 'ENG-A1',
    description: '面向高一学生的基础英语课程',
    studentCount: 32,
    assignmentCount: 8,
    averageScore: 87,
    progress: 75,
    status: 'active',
    goal: 'basic',
    createdAt: '2024-01-01'
  },
  {
    id: '2',
    name: '高二英语B班',
    code: 'ENG-B2',
    description: '高二学生中级英语提升课程',
    studentCount: 28,
    assignmentCount: 6,
    averageScore: 82,
    progress: 68,
    status: 'active',
    goal: 'intermediate',
    createdAt: '2024-01-02'
  },
  {
    id: '3',
    name: '高三冲刺班',
    code: 'ENG-C3',
    description: '高考英语冲刺强化训练',
    studentCount: 25,
    assignmentCount: 12,
    averageScore: 91,
    progress: 85,
    status: 'active',
    goal: 'exam',
    createdAt: '2024-01-03'
  },
  {
    id: '4',
    name: '商务英语班',
    code: 'BUS-01',
    description: '职场商务英语专项训练',
    studentCount: 18,
    assignmentCount: 5,
    averageScore: 89,
    progress: 60,
    status: 'inactive',
    goal: 'advanced',
    createdAt: '2024-01-04'
  },
  {
    id: '5',
    name: '雅思备考班',
    code: 'IELTS-01',
    description: '雅思考试专项备考课程',
    studentCount: 15,
    assignmentCount: 10,
    averageScore: 85,
    progress: 45,
    status: 'archived',
    goal: 'exam',
    createdAt: '2023-12-01'
  }
])

const searchQuery = ref('')
const statusFilter = ref('')
const goalFilter = ref('')
const viewMode = ref<'grid' | 'list'>('grid')
const sortField = ref('name')
const sortOrder = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)
const pageSize = ref(12)

const showCreateModal = ref(false)
const showEditModal = ref(false)
const classForm = ref<ClassForm>({
  name: '',
  code: '',
  description: '',
  goal: '',
  status: 'active'
})

const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const selectedClass = ref<ClassItem | null>(null)

// 计算属性
const filteredClasses = computed(() => {
  let result = classes.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(cls => 
      cls.name.toLowerCase().includes(query) ||
      cls.code.toLowerCase().includes(query)
    )
  }
  
  // 状态过滤
  if (statusFilter.value) {
    result = result.filter(cls => cls.status === statusFilter.value)
  }
  
  // 目标过滤
  if (goalFilter.value) {
    result = result.filter(cls => cls.goal === goalFilter.value)
  }
  
  // 排序
  result.sort((a, b) => {
    const aVal = a[sortField.value as keyof ClassItem]
    const bVal = b[sortField.value as keyof ClassItem]
    
    if (sortOrder.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
  
  return result
})

const totalPages = computed(() => {
  return Math.ceil(filteredClasses.value.length / pageSize.value)
})

const paginatedClasses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredClasses.value.slice(start, end)
})

const totalStudents = computed(() => {
  return filteredClasses.value.reduce((sum, cls) => sum + cls.studentCount, 0)
})

const activeClasses = computed(() => {
  return filteredClasses.value.filter(cls => cls.status === 'active').length
})

const averageProgress = computed(() => {
  if (filteredClasses.value.length === 0) return 0
  const total = filteredClasses.value.reduce((sum, cls) => sum + cls.progress, 0)
  return Math.round(total / filteredClasses.value.length)
})

// 方法
const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '活跃',
    inactive: '非活跃',
    archived: '已归档'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getGoalText = (goal: string) => {
  const goalMap = {
    basic: '基础英语',
    intermediate: '中级英语',
    advanced: '高级英语',
    exam: '考试准备'
  }
  return goalMap[goal as keyof typeof goalMap] || goal
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  return 'poor'
}

const viewClassDetails = (classId: string | undefined) => {
  if (classId) {
    router.push(`/teacher/classes/${classId}`)
  }
}

const manageStudents = (classId: string | undefined) => {
  if (classId) {
    router.push(`/teacher/classes/${classId}/students`)
  }
}

const editClass = (classItem: ClassItem | null) => {
  if (classItem) {
    classForm.value = {
      name: classItem.name,
      code: classItem.code,
      description: classItem.description,
      goal: classItem.goal,
      status: classItem.status
    }
    showEditModal.value = true
  }
}

const showClassMenu = (classItem: ClassItem, event: MouseEvent) => {
  selectedClass.value = classItem
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  showContextMenu.value = true
}

const hideContextMenu = () => {
  showContextMenu.value = false
  selectedClass.value = null
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  classForm.value = {
    name: '',
    code: '',
    description: '',
    goal: '',
    status: 'active'
  }
}

const createClass = () => {
  // 创建班级逻辑
  console.log('创建班级:', classForm.value)
  closeModals()
}

const updateClass = () => {
  // 更新班级逻辑
  console.log('更新班级:', classForm.value)
  closeModals()
}

const duplicateClass = (classItem: ClassItem | null) => {
  if (classItem) {
    console.log('复制班级:', classItem.name)
  }
  hideContextMenu()
}

const archiveClass = (classId: string | undefined) => {
  if (classId) {
    console.log('归档班级:', classId)
  }
  hideContextMenu()
}

const deleteClass = (classId: string | undefined) => {
  if (classId && confirm('确定要删除这个班级吗？此操作不可恢复。')) {
    console.log('删除班级:', classId)
  }
  hideContextMenu()
}

const exportClasses = () => {
  console.log('导出班级数据')
}

// 生命周期
onMounted(() => {
  // 点击其他地方隐藏右键菜单
  document.addEventListener('click', hideContextMenu)
})
</script>

<style scoped lang="scss">
.class-list {
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

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
  
  .search-filters {
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
      
      &.create-btn {
        background: #007bff;
        color: white;
        
        &:hover {
          background: #0056b3;
        }
      }
    }
  }
}

.class-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
  
  .stat-item {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
    
    .stat-value {
      display: block;
      font-size: 24px;
      font-weight: bold;
      color: #007bff;
      margin-bottom: 5px;
    }
    
    .stat-label {
      color: #666;
      font-size: 14px;
    }
  }
}

.classes-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  
  .view-toggle {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    
    .view-btn {
      padding: 8px 16px;
      border: 1px solid #ddd;
      background: white;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
      
      &:hover {
        background: #f8f9fa;
      }
      
      &.active {
        background: #007bff;
        color: white;
        border-color: #007bff;
      }
    }
  }
}

.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  
  .class-card {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 20px;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    &.active {
      border-left: 4px solid #28a745;
    }
    
    &.inactive {
      border-left: 4px solid #ffc107;
      opacity: 0.8;
    }
    
    &.archived {
      border-left: 4px solid #6c757d;
      opacity: 0.6;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 15px;
      
      .class-info {
        h3 {
          color: #333;
          font-size: 18px;
          margin-bottom: 5px;
        }
        
        .class-code {
          background: #f8f9fa;
          color: #666;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
        }
      }
      
      .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        
        &.active {
          background: #d4edda;
          color: #155724;
        }
        
        &.inactive {
          background: #fff3cd;
          color: #856404;
        }
        
        &.archived {
          background: #f8d7da;
          color: #721c24;
        }
      }
    }
    
    .card-content {
      .class-description {
        margin-bottom: 15px;
        
        p {
          color: #666;
          font-size: 14px;
          line-height: 1.4;
        }
      }
      
      .class-metrics {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
        
        .metric {
          text-align: center;
          
          .metric-value {
            display: block;
            font-size: 18px;
            font-weight: bold;
            color: #007bff;
          }
          
          .metric-label {
            font-size: 12px;
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
          color: #666;
        }
        
        .progress-bar {
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
      }
      
      .class-goal {
        font-size: 12px;
        
        .goal-label {
          color: #666;
        }
        
        .goal-value {
          color: #333;
          font-weight: 500;
        }
      }
    }
    
    .card-actions {
      display: flex;
      gap: 8px;
      margin-top: 15px;
      
      .action-btn {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
        
        &:hover {
          background: #f8f9fa;
        }
        
        &.primary {
          background: #007bff;
          color: white;
          border-color: #007bff;
          
          &:hover {
            background: #0056b3;
          }
        }
        
        &.menu {
          flex: 0 0 auto;
          width: 36px;
          padding: 8px;
        }
      }
    }
  }
}

.classes-table {
  overflow-x: auto;
  
  table {
    width: 100%;
    border-collapse: collapse;
    
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #eee;
    }
    
    th {
      background: #f8f9fa;
      font-weight: 600;
      color: #333;
      
      &.sortable {
        cursor: pointer;
        user-select: none;
        
        &:hover {
          background: #e9ecef;
        }
        
        .sort-icon {
          margin-left: 5px;
          color: #007bff;
        }
      }
    }
    
    .class-name-cell {
      strong {
        display: block;
        color: #333;
        margin-bottom: 2px;
      }
      
      small {
        color: #666;
        font-size: 12px;
      }
    }
    
    .class-code {
      background: #f8f9fa;
      color: #666;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
    }
    
    .score-badge {
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      
      &.excellent {
        background: #d4edda;
        color: #155724;
      }
      
      &.good {
        background: #cce5ff;
        color: #004085;
      }
      
      &.average {
        background: #fff3cd;
        color: #856404;
      }
      
      &.poor {
        background: #f8d7da;
        color: #721c24;
      }
    }
    
    .progress-cell {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .mini-progress {
        flex: 1;
        height: 4px;
        background: #e9ecef;
        border-radius: 2px;
        overflow: hidden;
        
        .mini-progress-fill {
          height: 100%;
          background: #007bff;
          transition: width 0.3s;
        }
      }
      
      span {
        font-size: 12px;
        color: #666;
        min-width: 35px;
      }
    }
    
    .table-actions {
      display: flex;
      gap: 5px;
      
      .table-action-btn {
        width: 28px;
        height: 28px;
        border: none;
        background: #f8f9fa;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
        
        &:hover {
          background: #e9ecef;
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
      
      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        
        @media (max-width: 600px) {
          grid-template-columns: 1fr;
        }
      }
      
      .form-group {
        margin-bottom: 20px;
        
        label {
          display: block;
          margin-bottom: 5px;
          color: #333;
          font-weight: 500;
        }
        
        input, textarea, select {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
          
          &:focus {
            outline: none;
            border-color: #007bff;
          }
        }
        
        textarea {
          resize: vertical;
        }
      }
      
      .form-actions {
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
            
            &:hover {
              background: #0056b3;
            }
          }
        }
      }
    }
  }
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  min-width: 150px;
  
  .menu-item {
    padding: 10px 15px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s;
    
    &:hover {
      background: #f8f9fa;
    }
    
    &.danger {
      color: #dc3545;
      
      &:hover {
        background: #f8d7da;
      }
    }
  }
  
  .menu-divider {
    height: 1px;
    background: #eee;
    margin: 5px 0;
  }
}

@media (max-width: 768px) {
  .class-list {
    padding: 15px;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
    
    .search-filters {
      flex-direction: column;
      
      .search-box {
        max-width: none;
      }
    }
  }
  
  .class-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .classes-grid {
    grid-template-columns: 1fr;
  }
  
  .classes-table {
    font-size: 12px;
    
    th, td {
      padding: 8px;
    }
  }
}
</style>