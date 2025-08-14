<template>
  <div class="user-learning-goal-widget">
    <!-- 用户信息区域 -->
    <div class="user-info-section">
      <div class="user-avatar">
        <img v-if="userInfo.avatar" :src="userInfo.avatar" alt="用户头像" />
        <div v-else class="default-avatar">
          {{ userInfo.username?.charAt(0)?.toUpperCase() || 'U' }}
        </div>
      </div>
      <div class="user-details">
        <h3 class="username">{{ userInfo.username || '未登录用户' }}</h3>
        <p class="user-role">{{ getUserRoleDisplay() }}</p>
      </div>
    </div>

    <!-- 学习目标信息 -->
    <div class="learning-goal-section" v-if="currentGoal">
      <div class="goal-header">
        <h4 class="goal-title">{{ currentGoal.name }}</h4>
        <span class="goal-status" :class="getGoalStatusClass()">{{ getGoalStatusText() }}</span>
      </div>
      
      <div class="goal-progress">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
        <div class="progress-text">
          <span class="learned">已学: {{ currentGoal.learned_words || 0 }}</span>
          <span class="total">总计: {{ currentGoal.total_words || 0 }}</span>
          <span class="percentage">{{ progressPercentage }}%</span>
        </div>
      </div>

      <div class="goal-actions">
        <button @click="goToLearningDashboard" class="action-btn primary">
          <i class="icon">📊</i>
          查看详情
        </button>
        <button @click="goToGoalManagement" class="action-btn secondary">
          <i class="icon">⚙️</i>
          管理目标
        </button>
      </div>
    </div>

    <!-- 无学习目标时的提示 -->
    <div class="no-goal-section" v-else>
      <div class="no-goal-icon">🎯</div>
      <p class="no-goal-text">暂无激活的学习目标</p>
      <button @click="createLearningGoal" class="action-btn primary">
        <i class="icon">➕</i>
        创建目标
      </button>
    </div>
  </div>
</template>

<script>
import { userAPI } from '../utils/api.js'

export default {
  name: 'UserLearningGoalWidget',
  data() {
    return {
      userInfo: {},
      currentGoal: null,
      loading: false
    }
  },
  computed: {
    progressPercentage() {
      if (!this.currentGoal || !this.currentGoal.total_words) {
        return 0
      }
      const learned = this.currentGoal.learned_words || 0
      const total = this.currentGoal.total_words || 1
      return Math.round((learned / total) * 100)
    }
  },
  mounted() {
    this.loadUserInfo()
    this.loadCurrentGoal()
  },
  methods: {
    async loadUserInfo() {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          this.userInfo = { username: '游客用户' }
          return
        }

        // 从localStorage获取基本用户信息
        this.userInfo = {
          username: localStorage.getItem('username') || '用户',
          role: localStorage.getItem('role') || 'student',
          avatar: localStorage.getItem('avatar') || null
        }

        // 尝试从API获取更详细的用户信息
        const userProfile = await userAPI.getProfile()
        if (userProfile) {
          this.userInfo = { ...this.userInfo, ...userProfile }
        }
      } catch (error) {
        console.warn('获取用户信息失败:', error)
        // 使用localStorage中的基本信息作为后备
      }
    },

    async loadCurrentGoal() {
      try {
        const token = localStorage.getItem('token')
        if (!token) return

        // 调用学习目标API
        const response = await fetch('http://127.0.0.1:8001/teaching/api/learning-goals/', {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const data = await response.json()
          // 查找当前激活的学习目标
          const activeGoals = data.results || data
          this.currentGoal = Array.isArray(activeGoals) 
            ? activeGoals.find(goal => goal.is_active || goal.is_current)
            : null
        }
      } catch (error) {
        console.warn('获取学习目标失败:', error)
      }
    },

    getUserRoleDisplay() {
      const roleMap = {
        'student': '学生',
        'teacher': '教师',
        'admin': '管理员',
        'parent': '家长'
      }
      return roleMap[this.userInfo.role] || '学习者'
    },

    getGoalStatusClass() {
      if (!this.currentGoal) return ''
      const percentage = this.progressPercentage
      if (percentage >= 80) return 'status-excellent'
      if (percentage >= 60) return 'status-good'
      if (percentage >= 30) return 'status-normal'
      return 'status-need-effort'
    },

    getGoalStatusText() {
      if (!this.currentGoal) return ''
      const percentage = this.progressPercentage
      if (percentage >= 80) return '优秀'
      if (percentage >= 60) return '良好'
      if (percentage >= 30) return '进行中'
      return '需努力'
    },

    goToLearningDashboard() {
      // 跳转到后端学习看板页面
      window.open('http://127.0.0.1:8001/teaching/learning-dashboard/', '_blank')
    },

    goToGoalManagement() {
      // 跳转到后端学习目标管理页面
      window.open('http://127.0.0.1:8001/teaching/goals/', '_blank')
    },

    createLearningGoal() {
      // 创建学习目标功能已移除
      this.$message.info('创建学习目标功能暂不可用')
    }
  }
}
</script>

<style scoped>
.user-learning-goal-widget {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 16px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin: 12px;
  min-height: 200px;
}

.user-info-section {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: white;
}

.user-details {
  flex: 1;
}

.username {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
}

.user-role {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

.learning-goal-section {
  margin-top: 16px;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.goal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.goal-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-excellent {
  background: rgba(76, 175, 80, 0.3);
  color: #4CAF50;
}

.status-good {
  background: rgba(255, 193, 7, 0.3);
  color: #FFC107;
}

.status-normal {
  background: rgba(33, 150, 243, 0.3);
  color: #2196F3;
}

.status-need-effort {
  background: rgba(244, 67, 54, 0.3);
  color: #F44336;
}

.goal-progress {
  margin-bottom: 16px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  opacity: 0.9;
}

.goal-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-btn.primary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.no-goal-section {
  text-align: center;
  padding: 20px;
}

.no-goal-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.no-goal-text {
  margin: 0 0 16px 0;
  font-size: 16px;
  opacity: 0.9;
}

.icon {
  font-size: 14px;
}
</style>