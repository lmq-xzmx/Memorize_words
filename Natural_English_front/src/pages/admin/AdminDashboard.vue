<template>
  <div class="admin-dashboard" v-permission="'admin.dashboard.view'">
    <div class="dashboard-header">
      <h1>管理员控制台</h1>
      <div class="header-actions">
        <button class="refresh-btn" @click="refreshData">
          <i class="el-icon-refresh"></i>
          刷新数据
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon user-icon">
          <i class="el-icon-user"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalUsers }}</h3>
          <p>总用户数</p>
          <span class="stat-change positive">+{{ stats.newUsersToday }} 今日新增</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon word-icon">
          <i class="el-icon-document"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalWords }}</h3>
          <p>词汇总数</p>
          <span class="stat-change positive">+{{ stats.newWordsToday }} 今日新增</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon learning-icon">
          <i class="el-icon-reading"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.totalLearningRecords }}</h3>
          <p>学习记录</p>
          <span class="stat-change positive">+{{ stats.newRecordsToday }} 今日新增</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active-icon">
          <i class="el-icon-star-on"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.activeUsers }}</h3>
          <p>活跃用户</p>
          <span class="stat-change">过去7天</span>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>快速操作</h2>
      <div class="actions-grid">
        <div class="action-card" @click="navigateTo('/admin/users')" v-permission="'admin.users.view'">
          <div class="action-icon">
            <i class="el-icon-user-solid"></i>
          </div>
          <h3>用户管理</h3>
          <p>管理用户账户、权限和状态</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/words')" v-permission="'admin.words.view'">
          <div class="action-icon">
            <i class="el-icon-document-add"></i>
          </div>
          <h3>词汇管理</h3>
          <p>添加、编辑和管理词汇库</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/content')" v-permission="'admin.content.view'">
          <div class="action-icon">
            <i class="el-icon-edit"></i>
          </div>
          <h3>内容管理</h3>
          <p>管理学习内容和课程</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/analytics')" v-permission="'admin.analytics.view'">
          <div class="action-icon">
            <i class="el-icon-data-line"></i>
          </div>
          <h3>数据分析</h3>
          <p>查看学习数据和用户行为</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/settings')" v-permission="'admin.settings.view'">
          <div class="action-icon">
            <i class="el-icon-setting"></i>
          </div>
          <h3>系统设置</h3>
          <p>配置系统参数和功能</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/logs')" v-permission="'admin.logs.view'">
          <div class="action-icon">
            <i class="el-icon-document-copy"></i>
          </div>
          <h3>系统日志</h3>
          <p>查看系统操作和错误日志</p>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities">
      <h2>最近活动</h2>
      <div class="activities-list">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon" :class="activity.type">
            <i :class="activity.icon"></i>
          </div>
          <div class="activity-content">
            <h4>{{ activity.title }}</h4>
            <p>{{ activity.description }}</p>
            <span class="activity-time">{{ formatTime(activity.time) }}</span>
          </div>
          <div class="activity-status" :class="activity.status">
            {{ getStatusText(activity.status) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 系统状态 -->
    <div class="system-status">
      <h2>系统状态</h2>
      <div class="status-grid">
        <div class="status-item">
          <div class="status-header">
            <h3>服务器状态</h3>
            <span class="status-indicator online"></span>
          </div>
          <div class="status-details">
            <div class="detail-item">
              <span class="label">CPU使用率:</span>
              <span class="value">{{ systemStatus.cpu }}%</span>
            </div>
            <div class="detail-item">
              <span class="label">内存使用率:</span>
              <span class="value">{{ systemStatus.memory }}%</span>
            </div>
            <div class="detail-item">
              <span class="label">磁盘使用率:</span>
              <span class="value">{{ systemStatus.disk }}%</span>
            </div>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-header">
            <h3>数据库状态</h3>
            <span class="status-indicator online"></span>
          </div>
          <div class="status-details">
            <div class="detail-item">
              <span class="label">连接数:</span>
              <span class="value">{{ systemStatus.dbConnections }}</span>
            </div>
            <div class="detail-item">
              <span class="label">查询/秒:</span>
              <span class="value">{{ systemStatus.dbQueries }}</span>
            </div>
            <div class="detail-item">
              <span class="label">响应时间:</span>
              <span class="value">{{ systemStatus.dbResponseTime }}ms</span>
            </div>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-header">
            <h3>缓存状态</h3>
            <span class="status-indicator online"></span>
          </div>
          <div class="status-details">
            <div class="detail-item">
              <span class="label">命中率:</span>
              <span class="value">{{ systemStatus.cacheHitRate }}%</span>
            </div>
            <div class="detail-item">
              <span class="label">内存使用:</span>
              <span class="value">{{ systemStatus.cacheMemory }}MB</span>
            </div>
            <div class="detail-item">
              <span class="label">键数量:</span>
              <span class="value">{{ systemStatus.cacheKeys }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户增长图表 -->
    <div class="charts-section">
      <h2>用户增长趋势</h2>
      <div class="chart-container">
        <div class="chart-placeholder">
          <i class="el-icon-data-line"></i>
          <p>图表组件将在此处显示</p>
          <small>需要集成图表库（如 Chart.js 或 ECharts）</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { permissionChecker } from '@/utils/permissions'

interface Stats {
  totalUsers: number
  newUsersToday: number
  totalWords: number
  newWordsToday: number
  totalLearningRecords: number
  newRecordsToday: number
  activeUsers: number
}

interface Activity {
  id: string
  type: string
  icon: string
  title: string
  description: string
  time: string
  status: 'success' | 'warning' | 'error' | 'info'
}

interface SystemStatus {
  cpu: number
  memory: number
  disk: number
  dbConnections: number
  dbQueries: number
  dbResponseTime: number
  cacheHitRate: number
  cacheMemory: number
  cacheKeys: number
}

const router = useRouter()

// 统计数据
const stats = ref<Stats>({
  totalUsers: 1248,
  newUsersToday: 23,
  totalWords: 15420,
  newWordsToday: 45,
  totalLearningRecords: 89650,
  newRecordsToday: 234,
  activeUsers: 456
})

// 最近活动
const recentActivities = ref<Activity[]>([
  {
    id: '1',
    type: 'user',
    icon: 'el-icon-user',
    title: '新用户注册',
    description: '用户 "学习者123" 完成注册',
    time: '2024-01-15T10:30:00Z',
    status: 'success'
  },
  {
    id: '2',
    type: 'word',
    icon: 'el-icon-document-add',
    title: '词汇添加',
    description: '管理员添加了50个新词汇到数据库',
    time: '2024-01-15T09:15:00Z',
    status: 'info'
  },
  {
    id: '3',
    type: 'system',
    icon: 'el-icon-warning',
    title: '系统警告',
    description: '服务器CPU使用率超过80%',
    time: '2024-01-15T08:45:00Z',
    status: 'warning'
  },
  {
    id: '4',
    type: 'backup',
    icon: 'el-icon-download',
    title: '数据备份',
    description: '每日数据备份已完成',
    time: '2024-01-15T02:00:00Z',
    status: 'success'
  },
  {
    id: '5',
    type: 'error',
    icon: 'el-icon-close',
    title: '系统错误',
    description: '邮件服务连接失败',
    time: '2024-01-14T23:30:00Z',
    status: 'error'
  }
])

// 系统状态
const systemStatus = ref<SystemStatus>({
  cpu: 45,
  memory: 62,
  disk: 78,
  dbConnections: 25,
  dbQueries: 150,
  dbResponseTime: 12,
  cacheHitRate: 94,
  cacheMemory: 256,
  cacheKeys: 1024
})

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path)
}

// 刷新数据
const refreshData = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新统计数据
    stats.value.newUsersToday = Math.floor(Math.random() * 50) + 10
    stats.value.newWordsToday = Math.floor(Math.random() * 100) + 20
    stats.value.newRecordsToday = Math.floor(Math.random() * 500) + 100
    
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  }
}

// 格式化时间
const formatTime = (timeString: string): string => {
  const time = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else {
    return `${days}天前`
  }
}

// 获取状态文本
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    success: '成功',
    warning: '警告',
    error: '错误',
    info: '信息'
  }
  return statusMap[status] || status
}

// 组件挂载时加载数据
onMounted(() => {
  // 模拟数据加载
  console.log('管理员控制台已加载')
})
</script>

<style scoped>
.admin-dashboard {
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

.refresh-btn {
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

.refresh-btn:hover {
  background: #5a6fd8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.user-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.word-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.learning-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.active-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 600;
}

.stat-content p {
  margin: 0 0 0.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
}

.stat-change.positive {
  color: #10b981;
}

.quick-actions,
.recent-activities,
.system-status,
.charts-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.quick-actions h2,
.recent-activities h2,
.system-status h2,
.charts-section h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-card {
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.action-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.action-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.action-card p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  transition: background 0.2s ease;
}

.activity-item:hover {
  background: #f3f4f6;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.activity-icon.user {
  background: #667eea;
}

.activity-icon.word {
  background: #10b981;
}

.activity-icon.system {
  background: #f59e0b;
}

.activity-icon.backup {
  background: #3b82f6;
}

.activity-icon.error {
  background: #ef4444;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 0.875rem;
  font-weight: 600;
}

.activity-content p {
  margin: 0 0 0.25rem 0;
  color: #6b7280;
  font-size: 0.75rem;
}

.activity-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

.activity-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.activity-status.success {
  background: #dcfce7;
  color: #166534;
}

.activity-status.warning {
  background: #fef3c7;
  color: #92400e;
}

.activity-status.error {
  background: #fee2e2;
  color: #991b1b;
}

.activity-status.info {
  background: #dbeafe;
  color: #1e40af;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.status-item {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #10b981;
}

.status-indicator.offline {
  background: #ef4444;
}

.status-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-item .label {
  color: #6b7280;
  font-size: 0.875rem;
}

.detail-item .value {
  color: #1f2937;
  font-size: 0.875rem;
  font-weight: 500;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #6b7280;
}

.chart-placeholder i {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.chart-placeholder p {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.chart-placeholder small {
  font-size: 0.875rem;
  color: #9ca3af;
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>