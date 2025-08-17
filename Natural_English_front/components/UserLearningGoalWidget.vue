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
import { userAPI } from '../utils/api'
import { buildApiUrl, buildPageUrl, API_ENDPOINTS } from '../config/apiConfig'

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
        const response = await fetch(buildApiUrl(API_ENDPOINTS.TEACHING.LEARNING_GOALS), {
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
      window.open(buildPageUrl(API_ENDPOINTS.TEACHING.LEARNING_DASHBOARD), '_blank')
    },

    goToGoalManagement() {
      // 跳转到后端学习目标管理页面
      window.open(buildPageUrl(API_ENDPOINTS.TEACHING.GOALS_MANAGEMENT), '_blank')
    },

    createLearningGoal() {
      // 创建学习目标功能已移除
      this.$message.info('创建学习目标功能暂不可用')
    }
  }
}
</script>

