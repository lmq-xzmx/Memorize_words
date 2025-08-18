<template>
  <div class="admin-dashboard" v-permission="['admin']">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>管理员控制台</h1>
      <p>系统管理和数据监控</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon users">👥</div>
        <div class="stat-content">
          <h3>{{ stats.totalUsers }}</h3>
          <p>总用户数</p>
          <span class="stat-change positive">+{{ stats.newUsersToday }} 今日新增</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon words">📚</div>
        <div class="stat-content">
          <h3>{{ stats.totalWords }}</h3>
          <p>词汇总数</p>
          <span class="stat-change positive">+{{ stats.newWordsToday }} 今日新增</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon sessions">📊</div>
        <div class="stat-content">
          <h3>{{ stats.totalSessions }}</h3>
          <p>学习记录</p>
          <span class="stat-change positive">+{{ stats.sessionsToday }} 今日</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">🔥</div>
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
        <div class="action-card" @click="navigateTo('/admin/users')">
          <div class="action-icon">👤</div>
          <h3>用户管理</h3>
          <p>管理用户账户和权限</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/content')">
          <div class="action-icon">📝</div>
          <h3>内容管理</h3>
          <p>管理词汇和学习内容</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/analytics')">
          <div class="action-icon">📈</div>
          <h3>数据分析</h3>
          <p>查看使用统计和报告</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/settings')">
          <div class="action-icon">⚙️</div>
          <h3>系统设置</h3>
          <p>配置系统参数</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/logs')">
          <div class="action-icon">📋</div>
          <h3>日志管理</h3>
          <p>查看系统日志</p>
        </div>
        
        <div class="action-card" @click="navigateTo('/admin/backup')">
          <div class="action-icon">💾</div>
          <h3>数据备份</h3>
          <p>备份和恢复数据</p>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities">
      <h2>最近活动</h2>
      <div class="activity-list">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id" 
          class="activity-item"
        >
          <div class="activity-icon" :class="activity.type">
            {{ getActivityIcon(activity.type) }}
          </div>
          <div class="activity-content">
            <p class="activity-text">{{ activity.description }}</p>
            <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
          </div>
          <div class="activity-user">
            {{ activity.user }}
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
            <span class="status-label">CPU使用率</span>
            <span class="status-value">{{ systemStatus.cpu }}%</span>
          </div>
          <div class="status-bar">
            <div 
              class="status-fill" 
              :style="{ width: systemStatus.cpu + '%' }"
              :class="getStatusClass(systemStatus.cpu)"
            ></div>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-header">
            <span class="status-label">内存使用</span>
            <span class="status-value">{{ systemStatus.memory }}%</span>
          </div>
          <div class="status-bar">
            <div 
              class="status-fill" 
              :style="{ width: systemStatus.memory + '%' }"
              :class="getStatusClass(systemStatus.memory)"
            ></div>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-header">
            <span class="status-label">磁盘空间</span>
            <span class="status-value">{{ systemStatus.disk }}%</span>
          </div>
          <div class="status-bar">
            <div 
              class="status-fill" 
              :style="{ width: systemStatus.disk + '%' }"
              :class="getStatusClass(systemStatus.disk)"
            ></div>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-header">
            <span class="status-label">数据库</span>
            <span class="status-indicator" :class="systemStatus.database ? 'online' : 'offline'">
              {{ systemStatus.database ? '在线' : '离线' }}
            </span>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-header">
            <span class="status-label">缓存服务</span>
            <span class="status-indicator" :class="systemStatus.cache ? 'online' : 'offline'">
              {{ systemStatus.cache ? '在线' : '离线' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface Stats {
  totalUsers: number
  newUsersToday: number
  totalWords: number
  newWordsToday: number
  totalSessions: number
  sessionsToday: number
  activeUsers: number
}

interface Activity {
  id: string
  type: 'user' | 'content' | 'system' | 'error'
  description: string
  timestamp: string
  user: string
}

interface SystemStatus {
  cpu: number
  memory: number
  disk: number
  database: boolean
  cache: boolean
}

const router = useRouter()

// 响应式数据
const stats = ref<Stats>({
  totalUsers: 1248,
  newUsersToday: 23,
  totalWords: 5420,
  newWordsToday: 15,
  totalSessions: 8934,
  sessionsToday: 156,
  activeUsers: 342
})

const recentActivities = ref<Activity[]>([
  {
    id: '1',
    type: 'user',
    description: '新用户注册',
    timestamp: '2024-01-15T10:30:00Z',
    user: 'system'
  },
  {
    id: '2',
    type: 'content',
    description: '添加了50个新词汇',
    timestamp: '2024-01-15T09:15:00Z',
    user: 'admin'
  },
  {
    id: '3',
    type: 'system',
    description: '系统备份完成',
    timestamp: '2024-01-15T08:00:00Z',
    user: 'system'
  },
  {
    id: '4',
    type: 'user',
    description: '用户权限更新',
    timestamp: '2024-01-15T07:45:00Z',
    user: 'admin'
  },
  {
    id: '5',
    type: 'error',
    description: '检测到异常登录尝试',
    timestamp: '2024-01-15T07:30:00Z',
    user: 'system'
  }
])

const systemStatus = ref<SystemStatus>({
  cpu: 45,
  memory: 62,
  disk: 78,
  database: true,
  cache: true
})

// 方法
const navigateTo = (path: string) => {
  router.push(path)
}

const getActivityIcon = (type: string) => {
  const icons = {
    user: '👤',
    content: '📝',
    system: '⚙️',
    error: '⚠️'
  }
  return icons[type as keyof typeof icons] || '📋'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else {
    return date.toLocaleDateString()
  }
}

const getStatusClass = (value: number) => {
  if (value < 50) return 'low'
  if (value < 80) return 'medium'
  return 'high'
}

// 生命周期
onMounted(() => {
  // 定期更新系统状态
  setInterval(() => {
    // 模拟系统状态更新
    systemStatus.value.cpu = Math.floor(Math.random() * 100)
    systemStatus.value.memory = Math.floor(Math.random() * 100)
  }, 30000) // 30秒更新一次
})
</script>

<style scoped lang="scss">
.admin-dashboard {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
  
  .stat-card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 16px;
    
    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      
      &.users {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.words {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.sessions {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.active {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }
    
    .stat-content {
      flex: 1;
      
      h3 {
        font-size: 28px;
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
      }
      
      p {
        color: #666;
        margin-bottom: 8px;
        font-size: 14px;
      }
      
      .stat-change {
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 12px;
        background: #f8f9fa;
        color: #666;
        
        &.positive {
          background: #d4edda;
          color: #155724;
        }
      }
    }
  }
}

.quick-actions {
  margin-bottom: 40px;
  
  h2 {
    color: #333;
    margin-bottom: 20px;
    font-size: 24px;
  }
  
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    
    .action-card {
      background: white;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      cursor: pointer;
      transition: all 0.3s ease;
      text-align: center;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
      }
      
      .action-icon {
        font-size: 32px;
        margin-bottom: 12px;
      }
      
      h3 {
        color: #333;
        margin-bottom: 8px;
        font-size: 16px;
      }
      
      p {
        color: #666;
        font-size: 14px;
        line-height: 1.4;
      }
    }
  }
}

.recent-activities {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 40px;
  
  h2 {
    color: #333;
    margin-bottom: 20px;
    font-size: 20px;
  }
  
  .activity-list {
    .activity-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px 0;
      border-bottom: 1px solid #eee;
      
      &:last-child {
        border-bottom: none;
      }
      
      .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        
        &.user {
          background: #e3f2fd;
        }
        
        &.content {
          background: #f3e5f5;
        }
        
        &.system {
          background: #e8f5e8;
        }
        
        &.error {
          background: #ffebee;
        }
      }
      
      .activity-content {
        flex: 1;
        
        .activity-text {
          color: #333;
          margin-bottom: 4px;
          font-size: 14px;
        }
        
        .activity-time {
          color: #666;
          font-size: 12px;
        }
      }
      
      .activity-user {
        color: #666;
        font-size: 12px;
        background: #f8f9fa;
        padding: 4px 8px;
        border-radius: 12px;
      }
    }
  }
}

.system-status {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  
  h2 {
    color: #333;
    margin-bottom: 20px;
    font-size: 20px;
  }
  
  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    
    .status-item {
      .status-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .status-label {
          color: #666;
          font-size: 14px;
        }
        
        .status-value {
          color: #333;
          font-weight: 500;
          font-size: 14px;
        }
        
        .status-indicator {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 12px;
          
          &.online {
            background: #d4edda;
            color: #155724;
          }
          
          &.offline {
            background: #f8d7da;
            color: #721c24;
          }
        }
      }
      
      .status-bar {
        height: 6px;
        background: #e9ecef;
        border-radius: 3px;
        overflow: hidden;
        
        .status-fill {
          height: 100%;
          transition: width 0.3s ease;
          
          &.low {
            background: #28a745;
          }
          
          &.medium {
            background: #ffc107;
          }
          
          &.high {
            background: #dc3545;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 15px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .actions-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>