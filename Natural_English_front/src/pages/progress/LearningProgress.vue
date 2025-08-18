<template>
  <div class="learning-progress">
    <div class="progress-header">
      <h1>学习进度</h1>
      <div class="time-filter">
        <button 
          v-for="period in timePeriods" 
          :key="period.value"
          class="filter-btn"
          :class="{ active: selectedPeriod === period.value }"
          @click="selectPeriod(period.value)"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <div class="progress-content">
      <!-- 总体统计 -->
      <div class="overview-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="el-icon-document"></i>
          </div>
          <div class="stat-info">
            <h3>{{ overallStats.totalWords }}</h3>
            <p>总学习单词</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon mastered">
            <i class="el-icon-check"></i>
          </div>
          <div class="stat-info">
            <h3>{{ overallStats.masteredWords }}</h3>
            <p>已掌握单词</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon studying">
            <i class="el-icon-edit"></i>
          </div>
          <div class="stat-info">
            <h3>{{ overallStats.studyingWords }}</h3>
            <p>学习中单词</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon accuracy">
            <i class="el-icon-pie-chart"></i>
          </div>
          <div class="stat-info">
            <h3>{{ overallStats.accuracy }}%</h3>
            <p>平均正确率</p>
          </div>
        </div>
      </div>

      <!-- 学习趋势图表 -->
      <div class="chart-section">
        <div class="chart-card">
          <h3>学习趋势</h3>
          <div class="chart-container">
            <div class="chart-placeholder">
              <div class="chart-bars">
                <div 
                  v-for="(data, index) in chartData" 
                  :key="index"
                  class="chart-bar"
                  :style="{ height: data.value + '%' }"
                  :title="`${data.date}: ${data.count}个单词`"
                >
                  <span class="bar-value">{{ data.count }}</span>
                </div>
              </div>
              <div class="chart-labels">
                <span v-for="(data, index) in chartData" :key="index" class="chart-label">
                  {{ data.date }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <h3>掌握程度分布</h3>
          <div class="mastery-distribution">
            <div class="mastery-item">
              <div class="mastery-bar">
                <div 
                  class="mastery-fill mastered" 
                  :style="{ width: masteryDistribution.mastered + '%' }"
                ></div>
              </div>
              <div class="mastery-info">
                <span class="mastery-label">已掌握</span>
                <span class="mastery-value">{{ masteryDistribution.mastered }}%</span>
              </div>
            </div>
            
            <div class="mastery-item">
              <div class="mastery-bar">
                <div 
                  class="mastery-fill familiar" 
                  :style="{ width: masteryDistribution.familiar + '%' }"
                ></div>
              </div>
              <div class="mastery-info">
                <span class="mastery-label">熟悉</span>
                <span class="mastery-value">{{ masteryDistribution.familiar }}%</span>
              </div>
            </div>
            
            <div class="mastery-item">
              <div class="mastery-bar">
                <div 
                  class="mastery-fill learning" 
                  :style="{ width: masteryDistribution.learning + '%' }"
                ></div>
              </div>
              <div class="mastery-info">
                <span class="mastery-label">学习中</span>
                <span class="mastery-value">{{ masteryDistribution.learning }}%</span>
              </div>
            </div>
            
            <div class="mastery-item">
              <div class="mastery-bar">
                <div 
                  class="mastery-fill difficult" 
                  :style="{ width: masteryDistribution.difficult + '%' }"
                ></div>
              </div>
              <div class="mastery-info">
                <span class="mastery-label">困难</span>
                <span class="mastery-value">{{ masteryDistribution.difficult }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细进度列表 -->
      <div class="progress-details">
        <div class="details-header">
          <h3>学习详情</h3>
          <div class="details-filters">
            <select v-model="selectedCategory" class="category-select">
              <option value="all">全部类别</option>
              <option value="words">单词学习</option>
              <option value="grammar">语法学习</option>
              <option value="listening">听力练习</option>
            </select>
          </div>
        </div>
        
        <div class="progress-list">
          <div 
            v-for="item in filteredProgressItems" 
            :key="item.id"
            class="progress-item"
          >
            <div class="item-icon">
              <i :class="item.icon"></i>
            </div>
            
            <div class="item-content">
              <div class="item-header">
                <h4>{{ item.title }}</h4>
                <span class="item-date">{{ formatDate(item.date) }}</span>
              </div>
              
              <div class="item-progress">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: item.progress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ item.progress }}%</span>
              </div>
              
              <div class="item-stats">
                <span class="stat">学习: {{ item.learned }}</span>
                <span class="stat">掌握: {{ item.mastered }}</span>
                <span class="stat">正确率: {{ item.accuracy }}%</span>
              </div>
            </div>
            
            <div class="item-actions">
              <button class="action-btn" @click="viewDetails(item)">
                <i class="el-icon-view"></i>
                查看
              </button>
              <button class="action-btn" @click="continueStudy(item)">
                <i class="el-icon-right"></i>
                继续
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 学习目标 -->
      <div class="goals-section" v-permission="'progress.goals.view'">
        <div class="goals-header">
          <h3>学习目标</h3>
          <button class="add-goal-btn" @click="showAddGoal = true">
            <i class="el-icon-plus"></i>
            添加目标
          </button>
        </div>
        
        <div class="goals-list">
          <div 
            v-for="goal in learningGoals" 
            :key="goal.id"
            class="goal-item"
            :class="{ completed: goal.completed }"
          >
            <div class="goal-content">
              <h4>{{ goal.title }}</h4>
              <p>{{ goal.description }}</p>
              
              <div class="goal-progress">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: (goal.current / goal.target) * 100 + '%' }"
                  ></div>
                </div>
                <span class="progress-text">
                  {{ goal.current }} / {{ goal.target }} {{ goal.unit }}
                </span>
              </div>
              
              <div class="goal-deadline">
                <i class="el-icon-time"></i>
                目标日期: {{ formatDate(goal.deadline) }}
              </div>
            </div>
            
            <div class="goal-actions">
              <button 
                v-if="!goal.completed"
                class="complete-btn"
                @click="completeGoal(goal.id)"
              >
                <i class="el-icon-check"></i>
              </button>
              <button class="edit-btn" @click="editGoal(goal)">
                <i class="el-icon-edit"></i>
              </button>
              <button class="delete-btn" @click="deleteGoal(goal.id)">
                <i class="el-icon-delete"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加目标对话框 -->
    <div v-if="showAddGoal" class="modal-overlay" @click="showAddGoal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加学习目标</h3>
          <button class="close-btn" @click="showAddGoal = false">
            <i class="el-icon-close"></i>
          </button>
        </div>
        
        <form @submit.prevent="addGoal" class="goal-form">
          <div class="form-group">
            <label>目标标题</label>
            <input v-model="newGoal.title" type="text" required />
          </div>
          
          <div class="form-group">
            <label>目标描述</label>
            <textarea v-model="newGoal.description" rows="3"></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>目标数量</label>
              <input v-model.number="newGoal.target" type="number" required />
            </div>
            
            <div class="form-group">
              <label>单位</label>
              <select v-model="newGoal.unit">
                <option value="个单词">个单词</option>
                <option value="个语法点">个语法点</option>
                <option value="分钟">分钟</option>
                <option value="次练习">次练习</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>截止日期</label>
            <input v-model="newGoal.deadline" type="date" required />
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showAddGoal = false">
              取消
            </button>
            <button type="submit" class="submit-btn">
              添加目标
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { permissionChecker } from '@/utils/permissions'

interface OverallStats {
  totalWords: number
  masteredWords: number
  studyingWords: number
  accuracy: number
}

interface ChartData {
  date: string
  count: number
  value: number
}

interface MasteryDistribution {
  mastered: number
  familiar: number
  learning: number
  difficult: number
}

interface ProgressItem {
  id: string
  title: string
  category: string
  date: string
  progress: number
  learned: number
  mastered: number
  accuracy: number
  icon: string
}

interface LearningGoal {
  id: string
  title: string
  description: string
  target: number
  current: number
  unit: string
  deadline: string
  completed: boolean
}

// 响应式数据
const selectedPeriod = ref('week')
const selectedCategory = ref('all')
const showAddGoal = ref(false)

// 时间周期选项
const timePeriods = ref([
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本年', value: 'year' }
])

// 总体统计数据
const overallStats = ref<OverallStats>({
  totalWords: 1250,
  masteredWords: 856,
  studyingWords: 394,
  accuracy: 87
})

// 图表数据
const chartData = ref<ChartData[]>([
  { date: '周一', count: 25, value: 80 },
  { date: '周二', count: 32, value: 100 },
  { date: '周三', count: 18, value: 60 },
  { date: '周四', count: 28, value: 90 },
  { date: '周五', count: 35, value: 100 },
  { date: '周六', count: 22, value: 70 },
  { date: '周日', count: 15, value: 50 }
])

// 掌握程度分布
const masteryDistribution = ref<MasteryDistribution>({
  mastered: 68,
  familiar: 18,
  learning: 10,
  difficult: 4
})

// 进度详情列表
const progressItems = ref<ProgressItem[]>([
  {
    id: '1',
    title: '基础词汇学习',
    category: 'words',
    date: '2024-01-15',
    progress: 85,
    learned: 120,
    mastered: 102,
    accuracy: 89,
    icon: 'el-icon-document'
  },
  {
    id: '2',
    title: '时态语法练习',
    category: 'grammar',
    date: '2024-01-14',
    progress: 72,
    learned: 15,
    mastered: 11,
    accuracy: 78,
    icon: 'el-icon-edit-outline'
  },
  {
    id: '3',
    title: '日常对话听力',
    category: 'listening',
    date: '2024-01-13',
    progress: 60,
    learned: 8,
    mastered: 5,
    accuracy: 82,
    icon: 'el-icon-headset'
  }
])

// 学习目标
const learningGoals = ref<LearningGoal[]>([
  {
    id: '1',
    title: '每日单词学习',
    description: '每天学习30个新单词',
    target: 30,
    current: 25,
    unit: '个单词',
    deadline: '2024-01-31',
    completed: false
  },
  {
    id: '2',
    title: '语法掌握目标',
    description: '掌握基础时态语法',
    target: 12,
    current: 8,
    unit: '个语法点',
    deadline: '2024-02-15',
    completed: false
  }
])

// 新目标表单
const newGoal = ref({
  title: '',
  description: '',
  target: 0,
  unit: '个单词',
  deadline: ''
})

// 计算属性
const filteredProgressItems = computed(() => {
  if (selectedCategory.value === 'all') {
    return progressItems.value
  }
  return progressItems.value.filter(item => item.category === selectedCategory.value)
})

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 选择时间周期
const selectPeriod = (period: string) => {
  selectedPeriod.value = period
  loadProgressData()
}

// 加载进度数据
const loadProgressData = async () => {
  try {
    // 根据选择的时间周期加载数据
    // 这里是模拟数据，实际应该调用API
    ElMessage.success('数据已更新')
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

// 查看详情
const viewDetails = (item: ProgressItem) => {
  ElMessage.info(`查看 ${item.title} 的详细信息`)
}

// 继续学习
const continueStudy = (item: ProgressItem) => {
  ElMessage.info(`继续学习 ${item.title}`)
}

// 添加目标
const addGoal = () => {
  if (!newGoal.value.title || !newGoal.value.target || !newGoal.value.deadline) {
    ElMessage.error('请填写完整信息')
    return
  }
  
  const goal: LearningGoal = {
    id: Date.now().toString(),
    title: newGoal.value.title,
    description: newGoal.value.description,
    target: newGoal.value.target,
    current: 0,
    unit: newGoal.value.unit,
    deadline: newGoal.value.deadline,
    completed: false
  }
  
  learningGoals.value.push(goal)
  
  // 重置表单
  newGoal.value = {
    title: '',
    description: '',
    target: 0,
    unit: '个单词',
    deadline: ''
  }
  
  showAddGoal.value = false
  ElMessage.success('目标添加成功')
}

// 完成目标
const completeGoal = (goalId: string) => {
  const goal = learningGoals.value.find(g => g.id === goalId)
  if (goal) {
    goal.completed = true
    goal.current = goal.target
    ElMessage.success('恭喜完成目标！')
  }
}

// 编辑目标
const editGoal = (goal: LearningGoal) => {
  ElMessage.info(`编辑目标: ${goal.title}`)
}

// 删除目标
const deleteGoal = (goalId: string) => {
  const index = learningGoals.value.findIndex(g => g.id === goalId)
  if (index > -1) {
    learningGoals.value.splice(index, 1)
    ElMessage.success('目标已删除')
  }
}

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadProgressData()
})
</script>

<style scoped>
.learning-progress {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.progress-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.time-filter {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  background: #f3f4f6;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  color: #374151;
  font-weight: 500;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: #e5e7eb;
}

.filter-btn.active {
  background: #667eea;
  color: white;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.stat-icon.mastered {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon.studying {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-icon.accuracy {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.stat-info h3 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 600;
}

.stat-info p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.chart-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.chart-card h3 {
  margin: 0 0 1rem 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.chart-container {
  height: 200px;
}

.chart-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-bars {
  flex: 1;
  display: flex;
  align-items: end;
  gap: 0.5rem;
  padding-bottom: 0.5rem;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(to top, #667eea, #764ba2);
  border-radius: 0.25rem 0.25rem 0 0;
  min-height: 20px;
  position: relative;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.chart-bar:hover {
  opacity: 0.8;
}

.bar-value {
  position: absolute;
  top: -1.5rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  color: #374151;
  font-weight: 500;
}

.chart-labels {
  display: flex;
  gap: 0.5rem;
}

.chart-label {
  flex: 1;
  text-align: center;
  font-size: 0.75rem;
  color: #6b7280;
}

.mastery-distribution {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mastery-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mastery-bar {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.mastery-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.mastery-fill.mastered {
  background: #10b981;
}

.mastery-fill.familiar {
  background: #3b82f6;
}

.mastery-fill.learning {
  background: #f59e0b;
}

.mastery-fill.difficult {
  background: #ef4444;
}

.mastery-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 100px;
}

.mastery-label {
  font-size: 0.875rem;
  color: #374151;
}

.mastery-value {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.progress-details {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.details-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.category-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  color: #374151;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.progress-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.item-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.item-content {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.item-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 500;
}

.item-date {
  color: #6b7280;
  font-size: 0.875rem;
}

.item-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 500;
  min-width: 35px;
}

.item-stats {
  display: flex;
  gap: 1rem;
}

.stat {
  color: #6b7280;
  font-size: 0.75rem;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: #f3f4f6;
  border: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  transition: background 0.2s ease;
}

.action-btn:hover {
  background: #e5e7eb;
}

.goals-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.goals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.goals-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.add-goal-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: background 0.2s ease;
}

.add-goal-btn:hover {
  background: #5a6fd8;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.goal-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.goal-item.completed {
  background: #ecfdf5;
  border-color: #10b981;
}

.goal-content {
  flex: 1;
}

.goal-content h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 500;
}

.goal-content p {
  margin: 0 0 0.75rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.goal-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.goal-deadline {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6b7280;
  font-size: 0.75rem;
}

.goal-actions {
  display: flex;
  gap: 0.5rem;
}

.complete-btn,
.edit-btn,
.delete-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.complete-btn {
  background: #10b981;
  color: white;
}

.complete-btn:hover {
  background: #059669;
}

.edit-btn {
  background: #f59e0b;
  color: white;
}

.edit-btn:hover {
  background: #d97706;
}

.delete-btn {
  background: #ef4444;
  color: white;
}

.delete-btn:hover {
  background: #dc2626;
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

.goal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
  .learning-progress {
    padding: 1rem;
  }
  
  .progress-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .overview-stats {
    grid-template-columns: 1fr;
  }
  
  .chart-section {
    grid-template-columns: 1fr;
  }
  
  .progress-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .goal-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>