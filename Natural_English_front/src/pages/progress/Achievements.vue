<template>
  <div class="achievements" v-permission="'progress.achievements.view'">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>成就徽章</h1>
      <p>记录你的学习成就和里程碑</p>
    </div>

    <!-- 成就统计 -->
    <div class="achievement-stats">
      <div class="stat-item">
        <div class="stat-icon">
          <i class="fas fa-trophy"></i>
        </div>
        <div class="stat-content">
          <h3>{{ unlockedCount }}</h3>
          <p>已解锁成就</p>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon">
          <i class="fas fa-star"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalPoints }}</h3>
          <p>成就积分</p>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon">
          <i class="fas fa-percentage"></i>
        </div>
        <div class="stat-content">
          <h3>{{ completionRate }}%</h3>
          <p>完成率</p>
        </div>
      </div>
    </div>

    <!-- 成就分类 -->
    <div class="achievement-categories">
      <button v-for="category in categories" 
              :key="category.id"
              :class="{ active: selectedCategory === category.id }"
              @click="selectedCategory = category.id"
              class="category-btn">
        <i :class="category.icon"></i>
        {{ category.name }}
        <span class="category-count">({{ getCategoryCount(category.id) }})</span>
      </button>
    </div>

    <!-- 成就列表 -->
    <div class="achievements-grid">
      <div v-for="achievement in filteredAchievements" 
           :key="achievement.id"
           class="achievement-card"
           :class="{ 
             unlocked: achievement.unlocked,
             locked: !achievement.unlocked,
             featured: achievement.featured
           }">
        <div class="achievement-header">
          <div class="achievement-icon" :style="{ background: achievement.color }">
            <i :class="achievement.icon"></i>
          </div>
          <div class="achievement-badge" v-if="achievement.featured">
            <i class="fas fa-crown"></i>
          </div>
        </div>
        
        <div class="achievement-content">
          <h3>{{ achievement.title }}</h3>
          <p>{{ achievement.description }}</p>
          
          <!-- 进度条 -->
          <div class="achievement-progress" v-if="!achievement.unlocked">
            <div class="progress-bar">
              <div class="progress-fill" 
                   :style="{ width: getProgressPercentage(achievement) + '%' }">
              </div>
            </div>
            <span class="progress-text">
              {{ achievement.current || 0 }} / {{ achievement.target }}
            </span>
          </div>
          
          <!-- 解锁信息 -->
          <div class="achievement-unlock" v-if="achievement.unlocked">
            <div class="unlock-date">
              <i class="fas fa-calendar"></i>
              {{ formatDate(achievement.unlockedAt) }}
            </div>
            <div class="unlock-points">
              <i class="fas fa-star"></i>
              +{{ achievement.points }} 积分
            </div>
          </div>
        </div>
        
        <!-- 奖励信息 -->
        <div class="achievement-reward" v-if="achievement.reward">
          <div class="reward-item">
            <i class="fas fa-gift"></i>
            {{ achievement.reward }}
          </div>
        </div>
      </div>
    </div>

    <!-- 成就详情弹窗 -->
    <div class="achievement-modal" v-if="selectedAchievement" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <div class="achievement-icon large" :style="{ background: selectedAchievement.color }">
            <i :class="selectedAchievement.icon"></i>
          </div>
          <button @click="closeModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <h2>{{ selectedAchievement.title }}</h2>
          <p class="achievement-description">{{ selectedAchievement.description }}</p>
          
          <div class="achievement-details">
            <div class="detail-item">
              <span class="detail-label">类别</span>
              <span class="detail-value">{{ getCategoryName(selectedAchievement.category) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">积分奖励</span>
              <span class="detail-value">{{ selectedAchievement.points }} 分</span>
            </div>
            <div class="detail-item" v-if="selectedAchievement.unlocked">
              <span class="detail-label">解锁时间</span>
              <span class="detail-value">{{ formatDate(selectedAchievement.unlockedAt) }}</span>
            </div>
            <div class="detail-item" v-if="!selectedAchievement.unlocked">
              <span class="detail-label">完成进度</span>
              <span class="detail-value">
                {{ selectedAchievement.current || 0 }} / {{ selectedAchievement.target }}
              </span>
            </div>
          </div>
          
          <div class="achievement-tips" v-if="selectedAchievement.tips">
            <h4>获取提示</h4>
            <ul>
              <li v-for="tip in selectedAchievement.tips" :key="tip">
                {{ tip }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Achievement {
  id: number
  title: string
  description: string
  icon: string
  color: string
  category: string
  points: number
  unlocked: boolean
  unlockedAt?: string
  current?: number
  target: number
  reward?: string
  featured?: boolean
  tips?: string[]
}

interface Category {
  id: string
  name: string
  icon: string
}

// 响应式数据
const selectedCategory = ref('all')
const selectedAchievement = ref<Achievement | null>(null)

// 成就分类
const categories: Category[] = [
  { id: 'all', name: '全部', icon: 'fas fa-th' },
  { id: 'learning', name: '学习成就', icon: 'fas fa-graduation-cap' },
  { id: 'vocabulary', name: '词汇成就', icon: 'fas fa-book' },
  { id: 'streak', name: '坚持成就', icon: 'fas fa-fire' },
  { id: 'accuracy', name: '准确率成就', icon: 'fas fa-bullseye' },
  { id: 'time', name: '时长成就', icon: 'fas fa-clock' },
  { id: 'special', name: '特殊成就', icon: 'fas fa-crown' }
]

// 成就数据
const achievements: Achievement[] = [
  {
    id: 1,
    title: '初学者',
    description: '完成第一次学习',
    icon: 'fas fa-seedling',
    color: '#27ae60',
    category: 'learning',
    points: 10,
    unlocked: true,
    unlockedAt: '2024-01-01',
    target: 1,
    current: 1
  },
  {
    id: 2,
    title: '词汇新手',
    description: '学习100个单词',
    icon: 'fas fa-book-open',
    color: '#3498db',
    category: 'vocabulary',
    points: 50,
    unlocked: true,
    unlockedAt: '2024-01-05',
    target: 100,
    current: 100
  },
  {
    id: 3,
    title: '词汇达人',
    description: '学习500个单词',
    icon: 'fas fa-book',
    color: '#9b59b6',
    category: 'vocabulary',
    points: 200,
    unlocked: true,
    unlockedAt: '2024-01-15',
    target: 500,
    current: 500,
    reward: '解锁高级词汇包'
  },
  {
    id: 4,
    title: '词汇大师',
    description: '学习1000个单词',
    icon: 'fas fa-trophy',
    color: '#f1c40f',
    category: 'vocabulary',
    points: 500,
    unlocked: false,
    target: 1000,
    current: 756,
    reward: '专属头像框',
    featured: true,
    tips: [
      '每天坚持学习新单词',
      '多做词汇练习题',
      '使用单词卡片记忆法'
    ]
  },
  {
    id: 5,
    title: '坚持一周',
    description: '连续学习7天',
    icon: 'fas fa-calendar-week',
    color: '#e74c3c',
    category: 'streak',
    points: 30,
    unlocked: true,
    unlockedAt: '2024-01-08',
    target: 7,
    current: 7
  },
  {
    id: 6,
    title: '坚持一月',
    description: '连续学习30天',
    icon: 'fas fa-fire',
    color: '#e67e22',
    category: 'streak',
    points: 150,
    unlocked: false,
    target: 30,
    current: 23,
    tips: [
      '设定每日学习提醒',
      '制定合理的学习计划',
      '找到适合的学习时间'
    ]
  },
  {
    id: 7,
    title: '完美主义者',
    description: '单次测试100%正确率',
    icon: 'fas fa-star',
    color: '#9b59b6',
    category: 'accuracy',
    points: 100,
    unlocked: true,
    unlockedAt: '2024-01-12',
    target: 1,
    current: 1,
    featured: true
  },
  {
    id: 8,
    title: '学霸',
    description: '平均正确率达到90%',
    icon: 'fas fa-medal',
    color: '#f39c12',
    category: 'accuracy',
    points: 200,
    unlocked: false,
    target: 90,
    current: 87,
    tips: [
      '仔细阅读题目',
      '多复习错题',
      '加强基础知识学习'
    ]
  },
  {
    id: 9,
    title: '时间管理大师',
    description: '累计学习100小时',
    icon: 'fas fa-clock',
    color: '#1abc9c',
    category: 'time',
    points: 300,
    unlocked: false,
    target: 100,
    current: 67,
    reward: '学习效率分析报告'
  },
  {
    id: 10,
    title: '早起鸟儿',
    description: '早上6点前学习10次',
    icon: 'fas fa-sun',
    color: '#f1c40f',
    category: 'special',
    points: 80,
    unlocked: false,
    target: 10,
    current: 3,
    tips: [
      '调整作息时间',
      '前一晚早点休息',
      '设置早起闹钟'
    ]
  }
]

// 计算属性
const filteredAchievements = computed(() => {
  if (selectedCategory.value === 'all') {
    return achievements
  }
  return achievements.filter(achievement => achievement.category === selectedCategory.value)
})

const unlockedCount = computed(() => {
  return achievements.filter(achievement => achievement.unlocked).length
})

const totalPoints = computed(() => {
  return achievements
    .filter(achievement => achievement.unlocked)
    .reduce((total, achievement) => total + achievement.points, 0)
})

const completionRate = computed(() => {
  return Math.round((unlockedCount.value / achievements.length) * 100)
})

// 方法
const getCategoryCount = (categoryId: string): number => {
  if (categoryId === 'all') {
    return achievements.length
  }
  return achievements.filter(achievement => achievement.category === categoryId).length
}

const getCategoryName = (categoryId: string): string => {
  const category = categories.find(cat => cat.id === categoryId)
  return category ? category.name : '未知分类'
}

const getProgressPercentage = (achievement: Achievement): number => {
  if (achievement.unlocked) return 100
  const current = achievement.current || 0
  return Math.min(Math.round((current / achievement.target) * 100), 100)
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const openModal = (achievement: Achievement) => {
  selectedAchievement.value = achievement
}

const closeModal = () => {
  selectedAchievement.value = null
}
</script>

<style scoped lang="scss">
.achievements {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    color: #2c3e50;
    margin-bottom: 10px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 16px;
  }
}

.achievement-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-content {
  h3 {
    color: #2c3e50;
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 4px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 14px;
    margin: 0;
  }
}

.achievement-categories {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.category-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  
  &:hover {
    border-color: #3498db;
    background: #f8f9fa;
  }
  
  &.active {
    background: #3498db;
    color: white;
    border-color: #3498db;
  }
}

.category-count {
  font-size: 12px;
  opacity: 0.8;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.achievement-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
  
  &.locked {
    opacity: 0.6;
    
    .achievement-icon {
      background: #95a5a6 !important;
    }
  }
  
  &.featured {
    border: 2px solid #f1c40f;
    
    &::before {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      background: linear-gradient(45deg, #f1c40f, #e67e22);
      border-radius: 16px;
      z-index: -1;
      animation: glow 2s ease-in-out infinite alternate;
    }
  }
}

@keyframes glow {
  from {
    box-shadow: 0 0 5px rgba(241, 196, 15, 0.5);
  }
  to {
    box-shadow: 0 0 20px rgba(241, 196, 15, 0.8);
  }
}

.achievement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.achievement-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  
  &.large {
    width: 80px;
    height: 80px;
    font-size: 32px;
  }
}

.achievement-badge {
  background: linear-gradient(135deg, #f1c40f, #e67e22);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.achievement-content {
  h3 {
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 18px;
  }
  
  p {
    color: #7f8c8d;
    font-size: 14px;
    line-height: 1.4;
    margin-bottom: 16px;
  }
}

.achievement-progress {
  margin-bottom: 16px;
}

.progress-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #7f8c8d;
}

.achievement-unlock {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #27ae60;
  margin-bottom: 16px;
}

.unlock-date, .unlock-points {
  display: flex;
  align-items: center;
  gap: 4px;
}

.achievement-reward {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  padding: 12px;
  border-left: 4px solid #f39c12;
}

.reward-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f39c12;
  font-size: 14px;
  font-weight: 500;
}

.achievement-modal {
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
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e9ecef;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #7f8c8d;
  cursor: pointer;
  
  &:hover {
    color: #2c3e50;
  }
}

.modal-body {
  padding: 24px;
  
  h2 {
    color: #2c3e50;
    margin-bottom: 12px;
  }
}

.achievement-description {
  color: #7f8c8d;
  font-size: 16px;
  line-height: 1.5;
  margin-bottom: 24px;
}

.achievement-details {
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f8f9fa;
  
  &:last-child {
    border-bottom: none;
  }
}

.detail-label {
  color: #7f8c8d;
  font-size: 14px;
}

.detail-value {
  color: #2c3e50;
  font-weight: 500;
}

.achievement-tips {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  
  h4 {
    color: #2c3e50;
    margin-bottom: 12px;
    font-size: 16px;
  }
  
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    
    li {
      color: #7f8c8d;
      font-size: 14px;
      line-height: 1.4;
      margin-bottom: 8px;
      padding-left: 16px;
      position: relative;
      
      &::before {
        content: '•';
        color: #3498db;
        position: absolute;
        left: 0;
      }
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

@media (max-width: 768px) {
  .achievements {
    padding: 16px;
  }
  
  .achievement-stats {
    grid-template-columns: 1fr;
  }
  
  .achievements-grid {
    grid-template-columns: 1fr;
  }
  
  .achievement-categories {
    justify-content: center;
  }
  
  .category-btn {
    font-size: 12px;
    padding: 8px 12px;
  }
}
</style>