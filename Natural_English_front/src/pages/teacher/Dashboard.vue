<template>
  <div class="teacher-dashboard" v-permission="['teacher', 'admin']">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>教师工作台</h1>
      <p>管理您的班级和学生学习进度</p>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon classes">🏫</div>
        <div class="stat-content">
          <h3>{{ stats.totalClasses }}</h3>
          <p>我的班级</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon students">👨‍🎓</div>
        <div class="stat-content">
          <h3>{{ stats.totalStudents }}</h3>
          <p>学生总数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon assignments">📝</div>
        <div class="stat-content">
          <h3>{{ stats.totalAssignments }}</h3>
          <p>作业数量</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon average">📊</div>
        <div class="stat-content">
          <h3>{{ stats.averageScore }}%</h3>
          <p>平均分数</p>
        </div>
      </div>
    </div>

    <!-- 我的班级 -->
    <div class="my-classes">
      <div class="section-header">
        <h2>我的班级</h2>
        <button @click="showCreateClassModal = true" class="create-btn">
          + 创建班级
        </button>
      </div>
      
      <div class="classes-grid">
        <div 
          v-for="classItem in classes" 
          :key="classItem.id" 
          class="class-card"
          @click="navigateToClass(classItem.id)"
        >
          <div class="class-header">
            <h3>{{ classItem.name }}</h3>
            <span class="class-code">{{ classItem.code }}</span>
          </div>
          <div class="class-stats">
            <div class="stat-item">
              <span class="stat-value">{{ classItem.studentCount }}</span>
              <span class="stat-label">学生</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ classItem.assignmentCount }}</span>
              <span class="stat-label">作业</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ classItem.averageScore }}%</span>
              <span class="stat-label">平均分</span>
            </div>
          </div>
          <div class="class-progress">
            <div class="progress-label">学习进度</div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: classItem.progress + '%' }"
              ></div>
            </div>
            <span class="progress-text">{{ classItem.progress }}%</span>
          </div>
          <div class="class-actions">
            <button @click.stop="viewClassDetails(classItem)" class="action-btn">
              查看详情
            </button>
            <button @click.stop="manageAssignments(classItem.id)" class="action-btn">
              管理作业
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 待处理任务 -->
    <div class="pending-tasks">
      <h2>待处理任务</h2>
      <div class="tasks-list">
        <div 
          v-for="task in pendingTasks" 
          :key="task.id" 
          class="task-item"
          :class="task.priority"
        >
          <div class="task-icon">
            {{ getTaskIcon(task.type) }}
          </div>
          <div class="task-content">
            <h4>{{ task.title }}</h4>
            <p>{{ task.description }}</p>
            <span class="task-time">{{ formatTime(task.dueDate) }}</span>
          </div>
          <div class="task-actions">
            <button @click="handleTask(task)" class="handle-btn">
              处理
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 学生表现 -->
    <div class="student-performance">
      <h2>学生表现</h2>
      <div class="performance-tabs">
        <button 
          v-for="tab in performanceTabs" 
          :key="tab.id" 
          @click="activeTab = tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
        >
          {{ tab.name }}
        </button>
      </div>
      
      <div class="performance-content">
        <!-- 优秀学生 -->
        <div v-if="activeTab === 'excellent'" class="excellent-students">
          <div 
            v-for="student in excellentStudents" 
            :key="student.id" 
            class="student-item"
          >
            <div class="student-avatar">
              {{ student.name.charAt(0) }}
            </div>
            <div class="student-info">
              <h4>{{ student.name }}</h4>
              <p>{{ student.className }}</p>
            </div>
            <div class="student-score">
              <span class="score">{{ student.score }}%</span>
              <span class="improvement">+{{ student.improvement }}%</span>
            </div>
          </div>
        </div>
        
        <!-- 最近活动 -->
        <div v-if="activeTab === 'recent'" class="recent-activities">
          <div 
            v-for="activity in recentActivities" 
            :key="activity.id" 
            class="activity-item"
          >
            <div class="activity-time">{{ formatTime(activity.timestamp) }}</div>
            <div class="activity-content">
              <strong>{{ activity.studentName }}</strong> {{ activity.action }}
            </div>
            <div class="activity-class">{{ activity.className }}</div>
          </div>
        </div>
        
        <!-- 需要帮助 -->
        <div v-if="activeTab === 'help'" class="help-needed">
          <div 
            v-for="student in studentsNeedHelp" 
            :key="student.id" 
            class="help-item"
          >
            <div class="student-avatar warning">
              {{ student.name.charAt(0) }}
            </div>
            <div class="student-info">
              <h4>{{ student.name }}</h4>
              <p>{{ student.className }}</p>
              <span class="issue">{{ student.issue }}</span>
            </div>
            <div class="help-actions">
              <button @click="contactStudent(student)" class="contact-btn">
                联系学生
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建班级弹窗 -->
    <div v-if="showCreateClassModal" class="modal-overlay" @click="closeCreateClassModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>创建新班级</h2>
          <button @click="closeCreateClassModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createClass">
            <div class="form-group">
              <label>班级名称</label>
              <input 
                v-model="newClass.name" 
                type="text" 
                placeholder="请输入班级名称"
                required
              >
            </div>
            <div class="form-group">
              <label>班级描述</label>
              <textarea 
                v-model="newClass.description" 
                placeholder="请输入班级描述"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label>学习目标</label>
              <select v-model="newClass.goal" required>
                <option value="">请选择学习目标</option>
                <option value="basic">基础英语</option>
                <option value="intermediate">中级英语</option>
                <option value="advanced">高级英语</option>
                <option value="exam">考试准备</option>
              </select>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeCreateClassModal" class="cancel-btn">
                取消
              </button>
              <button type="submit" class="submit-btn">
                创建班级
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface Stats {
  totalClasses: number
  totalStudents: number
  totalAssignments: number
  averageScore: number
}

interface ClassItem {
  id: string
  name: string
  code: string
  studentCount: number
  assignmentCount: number
  averageScore: number
  progress: number
}

interface Task {
  id: string
  type: 'grade' | 'assignment' | 'message' | 'report'
  title: string
  description: string
  dueDate: string
  priority: 'high' | 'medium' | 'low'
}

interface Student {
  id: string
  name: string
  className: string
  score?: number
  improvement?: number
  issue?: string
}

interface Activity {
  id: string
  studentName: string
  action: string
  className: string
  timestamp: string
}

interface NewClass {
  name: string
  description: string
  goal: string
}

const router = useRouter()

// 响应式数据
const stats = ref<Stats>({
  totalClasses: 5,
  totalStudents: 128,
  totalAssignments: 23,
  averageScore: 85
})

const classes = ref<ClassItem[]>([
  {
    id: '1',
    name: '高一英语A班',
    code: 'ENG-A1',
    studentCount: 32,
    assignmentCount: 8,
    averageScore: 87,
    progress: 75
  },
  {
    id: '2',
    name: '高二英语B班',
    code: 'ENG-B2',
    studentCount: 28,
    assignmentCount: 6,
    averageScore: 82,
    progress: 68
  },
  {
    id: '3',
    name: '高三冲刺班',
    code: 'ENG-C3',
    studentCount: 25,
    assignmentCount: 12,
    averageScore: 91,
    progress: 85
  }
])

const pendingTasks = ref<Task[]>([
  {
    id: '1',
    type: 'grade',
    title: '批改作业',
    description: '高一A班词汇测试需要批改',
    dueDate: '2024-01-16T10:00:00Z',
    priority: 'high'
  },
  {
    id: '2',
    type: 'assignment',
    title: '发布作业',
    description: '为高二B班准备新的语法练习',
    dueDate: '2024-01-17T14:00:00Z',
    priority: 'medium'
  },
  {
    id: '3',
    type: 'message',
    title: '回复消息',
    description: '3条学生消息待回复',
    dueDate: '2024-01-15T18:00:00Z',
    priority: 'low'
  }
])

const activeTab = ref('excellent')
const performanceTabs = [
  { id: 'excellent', name: '优秀学生' },
  { id: 'recent', name: '最近活动' },
  { id: 'help', name: '需要帮助' }
]

const excellentStudents = ref<Student[]>([
  {
    id: '1',
    name: '张小明',
    className: '高一A班',
    score: 95,
    improvement: 8
  },
  {
    id: '2',
    name: '李小红',
    className: '高二B班',
    score: 92,
    improvement: 5
  },
  {
    id: '3',
    name: '王小强',
    className: '高三冲刺班',
    score: 98,
    improvement: 12
  }
])

const recentActivities = ref<Activity[]>([
  {
    id: '1',
    studentName: '张小明',
    action: '完成了词汇练习',
    className: '高一A班',
    timestamp: '2024-01-15T14:30:00Z'
  },
  {
    id: '2',
    studentName: '李小红',
    action: '提交了作业',
    className: '高二B班',
    timestamp: '2024-01-15T13:45:00Z'
  },
  {
    id: '3',
    studentName: '王小强',
    action: '参与了讨论',
    className: '高三冲刺班',
    timestamp: '2024-01-15T12:20:00Z'
  }
])

const studentsNeedHelp = ref<Student[]>([
  {
    id: '1',
    name: '赵小华',
    className: '高一A班',
    issue: '语法理解困难'
  },
  {
    id: '2',
    name: '钱小丽',
    className: '高二B班',
    issue: '词汇记忆问题'
  }
])

const showCreateClassModal = ref(false)
const newClass = ref<NewClass>({
  name: '',
  description: '',
  goal: ''
})

// 方法
const navigateToClass = (classId: string) => {
  router.push(`/teacher/classes/${classId}`)
}

const viewClassDetails = (classItem: ClassItem) => {
  router.push(`/teacher/classes/${classItem.id}/details`)
}

const manageAssignments = (classId: string) => {
  router.push(`/teacher/classes/${classId}/assignments`)
}

const getTaskIcon = (type: string) => {
  const icons = {
    grade: '📝',
    assignment: '📋',
    message: '💬',
    report: '📊'
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

const handleTask = (task: Task) => {
  // 处理任务逻辑
  console.log('处理任务:', task.title)
}

const contactStudent = (student: Student) => {
  // 联系学生逻辑
  console.log('联系学生:', student.name)
}

const closeCreateClassModal = () => {
  showCreateClassModal.value = false
  newClass.value = {
    name: '',
    description: '',
    goal: ''
  }
}

const createClass = () => {
  // 创建班级逻辑
  console.log('创建班级:', newClass.value)
  closeCreateClassModal()
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style scoped lang="scss">
.teacher-dashboard {
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

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
  
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
      
      &.classes {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.students {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.assignments {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.average {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
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

.my-classes {
  margin-bottom: 40px;
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      color: #333;
      font-size: 24px;
    }
    
    .create-btn {
      background: #007bff;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      
      &:hover {
        background: #0056b3;
      }
    }
  }
  
  .classes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    
    .class-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
      }
      
      .class-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        h3 {
          color: #333;
          font-size: 18px;
        }
        
        .class-code {
          background: #f8f9fa;
          color: #666;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
        }
      }
      
      .class-stats {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
        
        .stat-item {
          text-align: center;
          
          .stat-value {
            display: block;
            font-size: 20px;
            font-weight: bold;
            color: #007bff;
          }
          
          .stat-label {
            font-size: 12px;
            color: #666;
          }
        }
      }
      
      .class-progress {
        margin-bottom: 15px;
        
        .progress-label {
          font-size: 12px;
          color: #666;
          margin-bottom: 5px;
        }
        
        .progress-bar {
          height: 6px;
          background: #e9ecef;
          border-radius: 3px;
          overflow: hidden;
          margin-bottom: 5px;
          
          .progress-fill {
            height: 100%;
            background: #007bff;
            transition: width 0.3s;
          }
        }
        
        .progress-text {
          font-size: 12px;
          color: #666;
        }
      }
      
      .class-actions {
        display: flex;
        gap: 8px;
        
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
            border-color: #007bff;
            color: #007bff;
          }
        }
      }
    }
  }
}

.pending-tasks {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 40px;
  
  h2 {
    color: #333;
    margin-bottom: 20px;
    font-size: 20px;
  }
  
  .tasks-list {
    .task-item {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 15px 0;
      border-bottom: 1px solid #eee;
      
      &:last-child {
        border-bottom: none;
      }
      
      &.high {
        border-left: 4px solid #dc3545;
        padding-left: 11px;
      }
      
      &.medium {
        border-left: 4px solid #ffc107;
        padding-left: 11px;
      }
      
      &.low {
        border-left: 4px solid #28a745;
        padding-left: 11px;
      }
      
      .task-icon {
        width: 40px;
        height: 40px;
        background: #f8f9fa;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
      }
      
      .task-content {
        flex: 1;
        
        h4 {
          color: #333;
          margin-bottom: 4px;
          font-size: 16px;
        }
        
        p {
          color: #666;
          margin-bottom: 4px;
          font-size: 14px;
        }
        
        .task-time {
          color: #999;
          font-size: 12px;
        }
      }
      
      .task-actions {
        .handle-btn {
          background: #007bff;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          
          &:hover {
            background: #0056b3;
          }
        }
      }
    }
  }
}

.student-performance {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  
  h2 {
    color: #333;
    margin-bottom: 20px;
    font-size: 20px;
  }
  
  .performance-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    
    .tab-btn {
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
  
  .performance-content {
    .student-item, .help-item {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 15px 0;
      border-bottom: 1px solid #eee;
      
      &:last-child {
        border-bottom: none;
      }
      
      .student-avatar {
        width: 40px;
        height: 40px;
        background: #007bff;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        
        &.warning {
          background: #ffc107;
          color: #333;
        }
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
          margin-bottom: 4px;
          font-size: 14px;
        }
        
        .issue {
          color: #dc3545;
          font-size: 12px;
        }
      }
      
      .student-score {
        text-align: right;
        
        .score {
          display: block;
          font-size: 18px;
          font-weight: bold;
          color: #28a745;
        }
        
        .improvement {
          font-size: 12px;
          color: #666;
        }
      }
      
      .help-actions {
        .contact-btn {
          background: #28a745;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          
          &:hover {
            background: #1e7e34;
          }
        }
      }
    }
    
    .activity-item {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 15px 0;
      border-bottom: 1px solid #eee;
      
      &:last-child {
        border-bottom: none;
      }
      
      .activity-time {
        color: #666;
        font-size: 12px;
        min-width: 80px;
      }
      
      .activity-content {
        flex: 1;
        font-size: 14px;
        
        strong {
          color: #333;
        }
      }
      
      .activity-class {
        color: #666;
        font-size: 12px;
        background: #f8f9fa;
        padding: 2px 8px;
        border-radius: 12px;
      }
    }
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
    max-width: 500px;
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

@media (max-width: 768px) {
  .teacher-dashboard {
    padding: 15px;
  }
  
  .stats-overview {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .classes-grid {
    grid-template-columns: 1fr;
  }
  
  .task-item, .student-item, .help-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .performance-tabs {
    flex-wrap: wrap;
  }
}
</style>