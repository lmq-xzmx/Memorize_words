<template>
  <div class="teacher-dashboard" v-permission="'teacher.dashboard.view'">
    <div class="dashboard-header">
      <h1>教师工作台</h1>
      <div class="header-actions">
        <button class="create-btn" @click="showCreateClass = true" v-permission="'teacher.class.create'">
          <i class="el-icon-plus"></i>
          创建班级
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon class-icon">
          <i class="el-icon-school"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teacherStats.totalClasses }}</h3>
          <p>管理班级</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon student-icon">
          <i class="el-icon-user"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teacherStats.totalStudents }}</h3>
          <p>学生总数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon assignment-icon">
          <i class="el-icon-document"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teacherStats.totalAssignments }}</h3>
          <p>作业任务</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon progress-icon">
          <i class="el-icon-data-line"></i>
        </div>
        <div class="stat-content">
          <h3>{{ teacherStats.averageProgress }}%</h3>
          <p>平均进度</p>
        </div>
      </div>
    </div>

    <!-- 我的班级 -->
    <div class="my-classes">
      <div class="section-header">
        <h2>我的班级</h2>
        <button class="view-all-btn" @click="navigateTo('/teacher/classes')">
          查看全部
        </button>
      </div>
      
      <div class="classes-grid">
        <div 
          v-for="classItem in myClasses" 
          :key="classItem.id"
          class="class-card"
          @click="navigateTo(`/teacher/classes/${classItem.id}`)"
        >
          <div class="class-header">
            <h3>{{ classItem.name }}</h3>
            <span class="class-level">{{ classItem.level }}</span>
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
              <span class="stat-value">{{ classItem.averageScore }}</span>
              <span class="stat-label">平均分</span>
            </div>
          </div>
          
          <div class="class-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: classItem.progress + '%' }"
              ></div>
            </div>
            <span class="progress-text">学习进度 {{ classItem.progress }}%</span>
          </div>
          
          <div class="class-actions">
            <button 
              class="action-btn" 
              @click.stop="createAssignment(classItem.id)"
              v-permission="'teacher.assignment.create'"
            >
              <i class="el-icon-document-add"></i>
              布置作业
            </button>
            <button 
              class="action-btn" 
              @click.stop="viewProgress(classItem.id)"
              v-permission="'teacher.progress.view'"
            >
              <i class="el-icon-data-analysis"></i>
              查看进度
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
            <i :class="task.icon"></i>
          </div>
          <div class="task-content">
            <h4>{{ task.title }}</h4>
            <p>{{ task.description }}</p>
            <span class="task-time">{{ formatTime(task.dueDate) }}</span>
          </div>
          <div class="task-actions">
            <button class="task-btn primary" @click="handleTask(task.id)">
              处理
            </button>
            <button class="task-btn secondary" @click="postponeTask(task.id)">
              稍后
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
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="performance-content">
        <div v-if="activeTab === 'top'" class="top-students">
          <div 
            v-for="(student, index) in topStudents" 
            :key="student.id"
            class="student-item"
          >
            <div class="student-rank">
              <span class="rank-number" :class="getRankClass(index)">{{ index + 1 }}</span>
            </div>
            <div class="student-avatar">
              <img v-if="student.avatar" :src="student.avatar" :alt="student.name" />
              <div v-else class="avatar-placeholder">
                {{ student.name.charAt(0) }}
              </div>
            </div>
            <div class="student-info">
              <h4>{{ student.name }}</h4>
              <p>{{ student.className }}</p>
            </div>
            <div class="student-score">
              <span class="score">{{ student.score }}</span>
              <span class="score-label">分</span>
            </div>
          </div>
        </div>
        
        <div v-if="activeTab === 'recent'" class="recent-activities">
          <div 
            v-for="activity in recentActivities" 
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-icon">
              <i :class="activity.icon"></i>
            </div>
            <div class="activity-content">
              <h4>{{ activity.studentName }}</h4>
              <p>{{ activity.action }}</p>
              <span class="activity-time">{{ formatTime(activity.time) }}</span>
            </div>
            <div class="activity-result" :class="activity.result">
              {{ getResultText(activity.result) }}
            </div>
          </div>
        </div>
        
        <div v-if="activeTab === 'struggling'" class="struggling-students">
          <div 
            v-for="student in strugglingStudents" 
            :key="student.id"
            class="struggling-item"
          >
            <div class="student-avatar">
              <img v-if="student.avatar" :src="student.avatar" :alt="student.name" />
              <div v-else class="avatar-placeholder">
                {{ student.name.charAt(0) }}
              </div>
            </div>
            <div class="student-info">
              <h4>{{ student.name }}</h4>
              <p>{{ student.className }}</p>
              <div class="struggle-areas">
                <span 
                  v-for="area in student.struggleAreas" 
                  :key="area"
                  class="struggle-tag"
                >
                  {{ area }}
                </span>
              </div>
            </div>
            <div class="student-actions">
              <button class="help-btn" @click="provideHelp(student.id)">
                <i class="el-icon-chat-dot-round"></i>
                提供帮助
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建班级对话框 -->
    <div v-if="showCreateClass" class="modal-overlay" @click="showCreateClass = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>创建新班级</h3>
          <button class="close-btn" @click="showCreateClass = false">
            <i class="el-icon-close"></i>
          </button>
        </div>
        
        <form @submit.prevent="createClass" class="create-form">
          <div class="form-group">
            <label>班级名称</label>
            <input v-model="newClass.name" type="text" required placeholder="请输入班级名称" />
          </div>
          
          <div class="form-group">
            <label>年级水平</label>
            <select v-model="newClass.level" required>
              <option value="">请选择年级</option>
              <option value="初级">初级</option>
              <option value="中级">中级</option>
              <option value="高级">高级</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>班级描述</label>
            <textarea v-model="newClass.description" rows="3" placeholder="请输入班级描述"></textarea>
          </div>
          
          <div class="form-group">
            <label>最大学生数</label>
            <input v-model.number="newClass.maxStudents" type="number" min="1" max="50" required />
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showCreateClass = false">
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
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { permissionChecker } from '@/utils/permissions'

interface TeacherStats {
  totalClasses: number
  totalStudents: number
  totalAssignments: number
  averageProgress: number
}

interface ClassItem {
  id: string
  name: string
  level: string
  studentCount: number
  assignmentCount: number
  averageScore: number
  progress: number
}

interface Task {
  id: string
  title: string
  description: string
  icon: string
  priority: 'high' | 'medium' | 'low'
  dueDate: string
}

interface Student {
  id: string
  name: string
  className: string
  avatar?: string
  score?: number
  struggleAreas?: string[]
}

interface Activity {
  id: string
  studentName: string
  action: string
  icon: string
  time: string
  result: 'excellent' | 'good' | 'average' | 'poor'
}

const router = useRouter()

// 响应式数据
const showCreateClass = ref(false)
const activeTab = ref('top')

// 教师统计
const teacherStats = ref<TeacherStats>({
  totalClasses: 5,
  totalStudents: 128,
  totalAssignments: 23,
  averageProgress: 76
})

// 我的班级
const myClasses = ref<ClassItem[]>([
  {
    id: '1',
    name: '初级英语A班',
    level: '初级',
    studentCount: 25,
    assignmentCount: 8,
    averageScore: 85,
    progress: 78
  },
  {
    id: '2',
    name: '中级英语B班',
    level: '中级',
    studentCount: 30,
    assignmentCount: 12,
    averageScore: 78,
    progress: 65
  },
  {
    id: '3',
    name: '高级英语C班',
    level: '高级',
    studentCount: 20,
    assignmentCount: 15,
    averageScore: 92,
    progress: 88
  }
])

// 待处理任务
const pendingTasks = ref<Task[]>([
  {
    id: '1',
    title: '批改作业',
    description: '初级英语A班 - 单词测试作业',
    icon: 'el-icon-edit',
    priority: 'high',
    dueDate: '2024-01-16T10:00:00Z'
  },
  {
    id: '2',
    title: '准备课件',
    description: '中级英语B班 - 语法课程课件',
    icon: 'el-icon-document',
    priority: 'medium',
    dueDate: '2024-01-17T14:00:00Z'
  },
  {
    id: '3',
    title: '学生评估',
    description: '高级英语C班 - 月度学习评估',
    icon: 'el-icon-data-analysis',
    priority: 'low',
    dueDate: '2024-01-20T16:00:00Z'
  }
])

// 表现标签页
const performanceTabs = [
  { key: 'top', label: '优秀学生' },
  { key: 'recent', label: '最近活动' },
  { key: 'struggling', label: '需要帮助' }
]

// 优秀学生
const topStudents = ref<Student[]>([
  {
    id: '1',
    name: '张小明',
    className: '高级英语C班',
    score: 98
  },
  {
    id: '2',
    name: '李小红',
    className: '中级英语B班',
    score: 95
  },
  {
    id: '3',
    name: '王小华',
    className: '初级英语A班',
    score: 92
  }
])

// 最近活动
const recentActivities = ref<Activity[]>([
  {
    id: '1',
    studentName: '张小明',
    action: '完成了单词测试',
    icon: 'el-icon-check',
    time: '2024-01-15T14:30:00Z',
    result: 'excellent'
  },
  {
    id: '2',
    studentName: '李小红',
    action: '提交了听力作业',
    icon: 'el-icon-upload',
    time: '2024-01-15T13:15:00Z',
    result: 'good'
  },
  {
    id: '3',
    studentName: '王小华',
    action: '参与了语法练习',
    icon: 'el-icon-edit-outline',
    time: '2024-01-15T11:45:00Z',
    result: 'average'
  }
])

// 需要帮助的学生
const strugglingStudents = ref<Student[]>([
  {
    id: '1',
    name: '赵小刚',
    className: '初级英语A班',
    struggleAreas: ['单词记忆', '语法理解']
  },
  {
    id: '2',
    name: '钱小美',
    className: '中级英语B班',
    struggleAreas: ['听力理解', '口语表达']
  }
])

// 新班级表单
const newClass = ref({
  name: '',
  level: '',
  description: '',
  maxStudents: 30
})

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path)
}

// 创建作业
const createAssignment = (classId: string) => {
  router.push(`/teacher/assignments/create?classId=${classId}`)
}

// 查看进度
const viewProgress = (classId: string) => {
  router.push(`/teacher/progress/${classId}`)
}

// 处理任务
const handleTask = (taskId: string) => {
  const task = pendingTasks.value.find(t => t.id === taskId)
  if (task) {
    ElMessage.success(`开始处理任务: ${task.title}`)
    // 这里可以导航到具体的任务处理页面
  }
}

// 推迟任务
const postponeTask = (taskId: string) => {
  const taskIndex = pendingTasks.value.findIndex(t => t.id === taskId)
  if (taskIndex !== -1) {
    pendingTasks.value.splice(taskIndex, 1)
    ElMessage.info('任务已推迟')
  }
}

// 提供帮助
const provideHelp = (studentId: string) => {
  const student = strugglingStudents.value.find(s => s.id === studentId)
  if (student) {
    ElMessage.success(`为 ${student.name} 提供帮助`)
    // 这里可以打开帮助对话框或导航到帮助页面
  }
}

// 创建班级
const createClass = async () => {
  try {
    // 模拟API调用
    const newClassData: ClassItem = {
      id: Date.now().toString(),
      name: newClass.value.name,
      level: newClass.value.level,
      studentCount: 0,
      assignmentCount: 0,
      averageScore: 0,
      progress: 0
    }
    
    myClasses.value.push(newClassData)
    teacherStats.value.totalClasses++
    
    // 重置表单
    newClass.value = {
      name: '',
      level: '',
      description: '',
      maxStudents: 30
    }
    
    showCreateClass.value = false
    ElMessage.success('班级创建成功')
  } catch (error) {
    ElMessage.error('班级创建失败')
  }
}

// 获取排名样式
const getRankClass = (index: number): string => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return 'normal'
}

// 获取结果文本
const getResultText = (result: string): string => {
  const resultMap: Record<string, string> = {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    poor: '较差'
  }
  return resultMap[result] || result
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const time = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (diff < 0) {
    const futureDays = Math.ceil(-diff / (1000 * 60 * 60 * 24))
    return `${futureDays}天后`
  }
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else {
    return `${days}天前`
  }
}

// 组件挂载时加载数据
onMounted(() => {
  console.log('教师工作台已加载')
})
</script>

<style scoped>
.teacher-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.dashboard-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s ease;
}

.create-btn:hover {
  background: #5a6fd8;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.class-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.student-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.assignment-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.progress-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.stat-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.my-classes,
.pending-tasks,
.student-performance {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2,
.pending-tasks h2,
.student-performance h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.view-all-btn {
  color: #667eea;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  text-decoration: underline;
}

.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.class-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.class-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.class-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.class-level {
  padding: 0.25rem 0.75rem;
  background: #e0e7ff;
  color: #3730a3;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.class-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.stat-label {
  color: #6b7280;
  font-size: 0.75rem;
}

.class-progress {
  margin-bottom: 1rem;
}

.progress-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  color: #6b7280;
  font-size: 0.75rem;
}

.class-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.5rem;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.2s ease;
}

.action-btn:hover {
  background: #e5e7eb;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: border-color 0.2s ease;
}

.task-item.high {
  border-left: 4px solid #ef4444;
}

.task-item.medium {
  border-left: 4px solid #f59e0b;
}

.task-item.low {
  border-left: 4px solid #10b981;
}

.task-icon {
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: 1rem;
}

.task-content {
  flex: 1;
}

.task-content h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 0.875rem;
  font-weight: 600;
}

.task-content p {
  margin: 0 0 0.25rem 0;
  color: #6b7280;
  font-size: 0.75rem;
}

.task-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
}

.task-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
  transition: background 0.2s ease;
}

.task-btn.primary {
  background: #667eea;
  color: white;
}

.task-btn.primary:hover {
  background: #5a6fd8;
}

.task-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.task-btn.secondary:hover {
  background: #e5e7eb;
}

.performance-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.tab-btn {
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.tab-btn:hover {
  color: #374151;
}

.top-students,
.recent-activities,
.struggling-students {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.student-item,
.activity-item,
.struggling-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.student-rank {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rank-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
}

.rank-number.gold {
  background: #f59e0b;
}

.rank-number.silver {
  background: #9ca3af;
}

.rank-number.bronze {
  background: #d97706;
}

.rank-number.normal {
  background: #6b7280;
}

.student-avatar,
.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.student-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.activity-icon {
  background: #f3f4f6;
  color: #6b7280;
}

.student-info,
.activity-content {
  flex: 1;
}

.student-info h4,
.activity-content h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 0.875rem;
  font-weight: 600;
}

.student-info p,
.activity-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.75rem;
}

.student-score {
  text-align: center;
}

.score {
  display: block;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.score-label {
  color: #6b7280;
  font-size: 0.75rem;
}

.activity-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

.activity-result {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.activity-result.excellent {
  background: #dcfce7;
  color: #166534;
}

.activity-result.good {
  background: #dbeafe;
  color: #1e40af;
}

.activity-result.average {
  background: #fef3c7;
  color: #92400e;
}

.activity-result.poor {
  background: #fee2e2;
  color: #991b1b;
}

.struggle-areas {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.struggle-tag {
  padding: 0.25rem 0.5rem;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.student-actions {
  display: flex;
  gap: 0.5rem;
}

.help-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.2s ease;
}

.help-btn:hover {
  background: #5a6fd8;
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
}

.modal-content {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #374151;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #374151;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s ease;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.submit-btn {
  background: #667eea;
  color: white;
}

.submit-btn:hover {
  background: #5a6fd8;
}

@media (max-width: 768px) {
  .teacher-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .classes-grid {
    grid-template-columns: 1fr;
  }
  
  .class-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .class-actions {
    flex-direction: column;
  }
  
  .task-item,
  .student-item,
  .activity-item,
  .struggling-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .performance-tabs {
    flex-wrap: wrap;
  }
}
</style>