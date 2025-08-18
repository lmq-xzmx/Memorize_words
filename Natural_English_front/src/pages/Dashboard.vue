<template>
  <div class="dashboard">
    <!-- 侧边栏菜单 -->
    <aside class="sidebar">
      <BaseMenu 
        title="英语学习平台"
        :menu-items="userMenuItems"
      />
    </aside>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <header class="dashboard-header">
        <h1>{{ getGreeting() }}</h1>
        <div class="user-info">
          <span>{{ userProfile.username || '用户' }}</span>
          <span class="user-role">({{ getRoleDisplayName(userProfile.role) }})</span>
          <button @click="logout" class="logout-btn">退出登录</button>
        </div>
      </header>
      
      <main class="dashboard-main">
        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card" v-permission="'dashboard.view'">
            <div class="stat-icon">
              <i class="el-icon-user"></i>
            </div>
            <div class="stat-content">
              <h3>学习天数</h3>
              <p class="stat-number">{{ stats.learningDays }}</p>
            </div>
          </div>
          
          <div class="stat-card" v-permission="'learning.view'">
            <div class="stat-icon">
              <i class="el-icon-reading"></i>
            </div>
            <div class="stat-content">
              <h3>掌握单词</h3>
              <p class="stat-number">{{ stats.masteredWords }}</p>
            </div>
          </div>
          
          <div class="stat-card" v-permission="'learning.practice.view'">
            <div class="stat-icon">
              <i class="el-icon-edit-outline"></i>
            </div>
            <div class="stat-content">
              <h3>完成练习</h3>
              <p class="stat-number">{{ stats.completedExercises }}</p>
            </div>
          </div>
          
          <div class="stat-card" v-permission="'progress.view'">
            <div class="stat-icon">
              <i class="el-icon-trophy"></i>
            </div>
            <div class="stat-content">
              <h3>获得积分</h3>
              <p class="stat-number">{{ stats.totalPoints }}</p>
            </div>
          </div>
        </div>
        
        <div class="content-grid">
          <!-- 快速开始 -->
          <section class="quick-start">
            <h2>快速开始</h2>
            <div class="quick-actions">
              <router-link 
                to="/learning/words" 
                class="action-btn"
                v-permission="'learning.words.view'"
              >
                <i class="el-icon-document"></i>
                单词学习
              </router-link>
              
              <router-link 
                to="/learning/practice" 
                class="action-btn"
                v-permission="'learning.practice.view'"
              >
                <i class="el-icon-edit-outline"></i>
                练习测试
              </router-link>
              
              <router-link 
                to="/progress/statistics" 
                class="action-btn"
                v-permission="'progress.statistics.view'"
              >
                <i class="el-icon-data-analysis"></i>
                查看进度
              </router-link>
            </div>
          </section>
          
          <!-- 学习进度 -->
          <section class="learning-progress" v-permission="'progress.view'">
            <h2>学习进度</h2>
            <div class="progress-list">
              <div class="progress-item">
                <div class="progress-info">
                  <span class="progress-label">单词掌握</span>
                  <span class="progress-percentage">{{ progress.wordMastery }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: progress.wordMastery + '%' }"
                  ></div>
                </div>
              </div>
              
              <div class="progress-item">
                <div class="progress-info">
                  <span class="progress-label">语法练习</span>
                  <span class="progress-percentage">{{ progress.grammarPractice }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: progress.grammarPractice + '%' }"
                  ></div>
                </div>
              </div>
              
              <div class="progress-item">
                <div class="progress-info">
                  <span class="progress-label">听力训练</span>
                  <span class="progress-percentage">{{ progress.listeningTraining }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: progress.listeningTraining + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </section>
          
          <!-- 最近活动 -->
          <section class="recent-activity">
            <h2>最近活动</h2>
            <div class="activity-list">
              <div 
                v-for="activity in recentActivities" 
                :key="activity.id" 
                class="activity-item"
              >
                <div class="activity-icon">
                  <i :class="activity.icon"></i>
                </div>
                <div class="activity-content">
                  <p class="activity-text">{{ activity.text }}</p>
                  <span class="activity-time">{{ activity.time }}</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import BaseMenu from '@/components/menu/BaseMenu.vue'
import { getMenuByRole } from '@/config/menu'
import { permissionChecker } from '@/utils/permissions'

interface Activity {
  id: string
  icon: string
  text: string
  time: string
}

const router = useRouter()
const store = useStore()

// 用户信息
const userProfile = computed(() => {
  return store.getters['user/profile'] || { username: '用户', role: 'student' }
})

// 用户菜单
const userMenuItems = computed(() => {
  return getMenuByRole(userProfile.value.role || 'student')
})

// 权限检查
const hasPermission = (permission: string): boolean => {
  return permissionChecker.check(permission)
}

// 统计数据
const stats = ref({
  learningDays: 0,
  masteredWords: 0,
  completedExercises: 0,
  totalPoints: 0
})

// 学习进度
const progress = ref({
  wordMastery: 0,
  grammarPractice: 0,
  listeningTraining: 0
})

// 最近活动
const recentActivities = ref<Activity[]>([])

// 获取问候语
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好！'
  if (hour < 18) return '下午好！'
  return '晚上好！'
}

// 获取角色显示名称
const getRoleDisplayName = (role: string) => {
  const roleMap: Record<string, string> = {
    'student': '学生',
    'teacher': '教师',
    'admin': '管理员'
  }
  return roleMap[role] || '用户'
}

// 退出登录
const logout = async () => {
  try {
    await store.dispatch('auth/logout')
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

// 加载数据
const loadData = async () => {
  try {
    // 加载统计数据
    if (hasPermission('dashboard.view')) {
      const statsData = await store.dispatch('dashboard/getStats')
      stats.value = statsData
    }
    
    // 加载进度数据
    if (hasPermission('progress.view')) {
      const progressData = await store.dispatch('dashboard/getProgress')
      progress.value = progressData
    }
    
    // 加载最近活动
    const activitiesData = await store.dispatch('dashboard/getRecentActivities')
    recentActivities.value = activitiesData
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 260px;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dashboard-header {
  background: #fff;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-role {
  color: #6b7280;
  font-size: 0.875rem;
}

.logout-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.dashboard-main {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #fff;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1.5rem;
}

.stat-content h3 {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 0.25rem 0;
  font-weight: 500;
}

.stat-number {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.quick-start,
.learning-progress,
.recent-activity {
  background: #fff;
  padding: 1.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.quick-start h2,
.learning-progress h2,
.recent-activity h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.action-btn i {
  font-size: 1.25rem;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  color: #374151;
  font-weight: 500;
  font-size: 0.875rem;
}

.progress-percentage {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
  border-radius: 0.25rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  color: #374151;
  font-size: 0.875rem;
  margin: 0 0 0.25rem 0;
  line-height: 1.4;
}

.activity-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 220px;
  }
  
  .dashboard-main {
    padding: 1.5rem;
  }
}

@media (max-width: 768px) {
  .dashboard {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
  }
  
  .dashboard-header {
    padding: 1rem;
  }
  
  .dashboard-header h1 {
    font-size: 1.5rem;
  }
  
  .dashboard-main {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>