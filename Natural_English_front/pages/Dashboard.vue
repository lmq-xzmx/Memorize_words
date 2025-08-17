<template>
  <div class="dashboard">
    <!-- 顶部欢迎区域 -->
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎回来，{{ userInfo.name || '学习者' }}！</h1>
      <p class="welcome-subtitle">继续你的英语学习之旅</p>
    </div>

    <!-- 学习统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <h3 class="stat-content__title">{{ stats.wordsLearned }}</h3>
          <p class="stat-content__label">已学单词</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <h3 class="stat-content__title">{{ stats.studyTime }}</h3>
          <p class="stat-content__label">学习时长</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <h3 class="stat-content__title">{{ stats.accuracy }}%</h3>
          <p class="stat-content__label">正确率</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔥</div>
        <div class="stat-content">
          <h3 class="stat-content__title">{{ stats.streak }}</h3>
          <p class="stat-content__label">连续天数</p>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2 class="quick-actions__title">快速开始</h2>
      <div class="action-grid">
        <router-link to="/word-flashcard" class="action-card">
          <div class="action-icon">🃏</div>
          <h3 class="action-card__title">单词卡片</h3>
          <p class="action-card__description">通过卡片记忆单词</p>
        </router-link>
        <router-link to="/listening" class="action-card">
          <div class="action-icon">🎧</div>
          <h3 class="action-card__title">听力练习</h3>
          <p class="action-card__description">提升听力理解能力</p>
        </router-link>
        <router-link to="/reading" class="action-card">
          <div class="action-icon">📖</div>
          <h3 class="action-card__title">阅读理解</h3>
          <p class="action-card__description">增强阅读技能</p>
        </router-link>
        <router-link to="/speaking" class="action-card">
          <div class="action-icon">🗣️</div>
          <h3 class="action-card__title">口语练习</h3>
          <p class="action-card__description">提高口语表达</p>
        </router-link>
      </div>
    </div>

    <!-- 学习进度 -->
    <div class="progress-section">
      <h2 class="progress-section__title">学习进度</h2>
      <div class="progress-card">
        <div class="progress-header">
          <span class="progress-header__label">今日目标</span>
          <span class="progress-header__count">{{ progress.completed }}/{{ progress.target }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <p class="progress-text">{{ progressText }}</p>
      </div>
    </div>

    <!-- 最近学习 -->
    <div class="recent-section">
      <h2 class="recent-section__title">最近学习</h2>
      <div class="recent-list">
        <div v-for="item in recentActivities" :key="item.id" class="recent-item">
          <div class="recent-icon">{{ item.icon }}</div>
          <div class="recent-content">
            <h4 class="recent-content__title">{{ item.title }}</h4>
            <p class="recent-content__description">{{ item.description }}</p>
          </div>
          <span class="recent-time">{{ item.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import api from '@/utils/api'
import permissionMixin from '../mixins/permissionMixin'

export default {
  name: 'Dashboard',
  mixins: [permissionMixin],
  data() {
    return {
      stats: {
        wordsLearned: 0,
        studyTime: '0h',
        accuracy: 0,
        streak: 0
      },
      progress: {
        completed: 0,
        target: 50
      },
      recentActivities: []
    }
  },
  computed: {
    ...mapState(['userInfo']),
    progressPercentage() {
      return Math.min((this.progress.completed / this.progress.target) * 100, 100)
    },
    progressText() {
      if (this.progress.completed >= this.progress.target) {
        return '🎉 今日目标已完成！'
      }
      const remaining = this.progress.target - this.progress.completed
      return `还需学习 ${remaining} 个单词完成今日目标`
    }
  },
  async mounted() {
    // 确保权限系统已初始化
    await this.$nextTick()
    
    // 权限检查
    if (!this.$hasPermission('view_dashboard')) {
      this.$showError('您没有权限访问仪表板')
      this.$router.push('/')
      return
    }

    // 加载仪表板数据
    await this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 检查统计数据查看权限
        if (this.$hasPermission('view_learning_stats')) {
          const [statsRes, progressRes, activitiesRes] = await Promise.all([
            api.getUserStats(),
            api.getUserProgress(),
            api.getRecentActivities()
          ])
          
          this.stats = statsRes.data
          this.progress = progressRes.data
          this.recentActivities = activitiesRes.data
        } else {
          // 如果没有统计权限，使用默认数据
          this.loadMockData()
        }
      } catch (error) {
        console.error('加载仪表板数据失败:', error)
        // 使用模拟数据
        this.loadMockData()
      }
    },
    loadMockData() {
      this.stats = {
        wordsLearned: 156,
        studyTime: '2.5h',
        accuracy: 85,
        streak: 7
      }
      this.progress = {
        completed: 23,
        target: 50
      }
      this.recentActivities = [
        {
          id: 1,
          icon: '🃏',
          title: '单词卡片练习',
          description: '学习了 15 个新单词',
          time: '2小时前'
        },
        {
          id: 2,
          icon: '🎧',
          title: '听力练习',
          description: '完成了日常对话练习',
          time: '昨天'
        },
        {
          id: 3,
          icon: '📖',
          title: '阅读理解',
          description: '阅读了一篇新闻文章',
          time: '2天前'
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
@use '../styles/index.scss';
@use '../styles/variables.scss' as *;
@use '../styles/mixins.scss' as *;
@include bem-block('dashboard') {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: var(--spacing-8);
  position: relative;
  overflow-x: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
    pointer-events: none;
  }
}

@include bem-block('welcome-section') {
  text-align: center;
  margin-bottom: var(--spacing-12);
  position: relative;
  z-index: 1;
}

@include bem-block('welcome-title') {
  @include text-style('heading', 'xl');
  font-weight: 700;
  color: var(--color-white);
  margin-bottom: var(--spacing-2);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  animation: slideInDown 0.8s ease-out;
}

@include bem-block('welcome-subtitle') {
  @include text-style('body', 'lg');
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  animation: slideInUp 0.8s ease-out 0.2s both;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@include bem-block('stats-grid') {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-12);
  position: relative;
  z-index: 1;
}

@include bem-block('stat-card') {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-8);
  @include flex-start;
  gap: var(--spacing-6);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  @include transition;
  animation: fadeInUp 0.6s ease-out;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  }
}

.stat-icon {
  @include text-style('display', 'sm');
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-content {
  .stat-content__title {
    @include text-style('heading', 'lg');
    font-weight: 700;
    color: var(--color-slate-800);
    margin: 0 0 var(--spacing-2) 0;
  }

  .stat-content__label {
    @include text-style('body', 'base');
    color: var(--color-slate-600);
    margin: 0;
    font-weight: 500;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.quick-actions {
  margin-bottom: var(--spacing-12);
  position: relative;
  z-index: 1;

  .quick-actions__title {
    color: var(--color-white);
    @include text-style('heading', 'lg');
    font-weight: 600;
    margin-bottom: var(--spacing-6);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-6);
}

.action-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-8);
  text-decoration: none;
  color: inherit;
  display: block;
  transition: all 0.2s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
    @include transition('left', 0.5s);
  }

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);

    &::before {
      left: 100%;
    }
  }
}

@include bem-block('action-icon') {
  @include text-style('display', 'sm');
  margin-bottom: var(--spacing-4);
  display: block;
}

@include bem-block('action-card') {
  @include bem-element('title') {
    @include text-style('heading', 'base');
    font-weight: 600;
    color: var(--color-slate-800);
    margin: 0 0 var(--spacing-2) 0;
  }

  @include bem-element('description') {
    color: var(--color-slate-600);
    margin: 0;
    @include text-style('body', 'sm');
    line-height: 1.5;
  }
}

@include bem-block('progress-section') {
  margin-bottom: var(--spacing-12);
  position: relative;
  z-index: 1;

  @include bem-element('title') {
    color: var(--color-white);
    @include text-style('heading', 'lg');
    font-weight: 600;
    margin-bottom: var(--spacing-6);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
}

@include bem-block('progress-card') {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-8);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

@include bem-block('progress-header') {
  @include flex-between;
  margin-bottom: var(--spacing-4);

  @include bem-element('label') {
    color: var(--color-slate-800);
    @include text-style('heading', 'base');
    font-weight: 600;
    margin: 0;
  }

  @include bem-element('count') {
    color: var(--color-slate-600);
    @include text-style('body', 'sm');
    font-weight: 500;
  }
}

@include bem-block('progress-text') {
  color: var(--color-slate-600);
  @include text-style('body', 'sm');
  margin-top: var(--spacing-2);
}

@include bem-block('progress-bar') {
  width: 100%;
  height: 12px;
  background: var(--color-slate-200);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  position: relative;
  margin-bottom: var(--spacing-2);
}

@include bem-block('progress-fill') {
  height: 100%;
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  border-radius: var(--border-radius-md);
  @include transition('width', 1s);
  position: relative;
}

@include bem-block('progress-fill') {
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(var(--color-white), 0.3), transparent);
    animation: shimmer 2s infinite;
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@include bem-block('recent-section') {
  position: relative;
  z-index: 1;

  @include bem-element('title') {
    color: var(--color-white);
    @include text-style('heading', 'lg');
    font-weight: 600;
    margin-bottom: var(--spacing-6);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
}

@include bem-block('recent-list') {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

@include bem-block('recent-item') {
  background: rgba(var(--color-white), 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-6);
  @include flex-start;
  gap: var(--spacing-4);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(var(--color-white), 0.2);
  @include transition;

  &:hover {
    transform: translateX(5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
}

@include bem-block('recent-icon') {
  @include text-style('heading', 'lg');
  flex-shrink: 0;
}

@include bem-block('recent-content') {
  flex: 1;

  @include bem-element('title') {
    color: var(--color-slate-800);
    @include text-style('heading', 'sm');
    font-weight: 600;
    margin: 0 0 var(--spacing-1) 0;
  }

  @include bem-element('description') {
    color: var(--color-slate-600);
    @include text-style('body', 'sm');
    margin: 0;
    line-height: 1.4;
  }
}

@include bem-block('recent-time') {
  color: var(--color-slate-500);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-normal);
  flex-shrink: 0;
}

// 响应式设计 - 中等屏幕
@media (max-width: 768px) {
  .dashboard {
    padding: var(--spacing-4);
  }
  
  .welcome-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
  }
  
  .welcome-subtitle {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-normal);
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-4);
  }
  
  .stat-card {
    padding: var(--spacing-6);
    display: flex;
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-4);
  }
  
  .stat-icon {
    @include text-style('display', 'xs');
  }
  
  .action-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .action-card {
    padding: var(--spacing-6);
  }
  
  .recent-item {
    padding: var(--spacing-4);
    display: flex;
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-3);
  }
}

// 响应式设计 - 小屏幕
@media (max-width: 576px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: var(--spacing-4);
  }
  
  .stat-content__title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
  }
  
  .action-card {
    padding: var(--spacing-4);
  }
  
  .action-icon {
    @include text-style('display', 'xs');
  }
}

// 暗色主题
@media (prefers-color-scheme: dark) {
  .stat-card {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .action-card {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .progress-card {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .recent-item {
    background: rgba(30, 30, 30, 0.95);
    color: #e0e0e0;
  }
  
  .stat-content__title {
    color: #f0f0f0;
  }
  
  .stat-content__label {
    color: #b0b0b0;
  }
  
  .action-card__title {
    color: #f0f0f0;
  }
  
  .action-card__description {
    color: #b0b0b0;
  }
  
  .progress-header__label {
    color: #f0f0f0;
  }
  
  .progress-text {
    color: #b0b0b0;
  }
  
  .recent-content__title {
    color: #f0f0f0;
  }
  
  .recent-content__description {
    color: #b0b0b0;
  }
  
  .recent-time {
    color: #888;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

// 高对比度主题
@media (prefers-contrast: high) {
  .dashboard {
    background: #000;
  }
  
  .stat-card {
    background: #fff;
    border: 2px solid #000;
  }
  
  .action-card {
    background: #fff;
    border: 2px solid #000;
  }
  
  .progress-card {
    background: #fff;
    border: 2px solid #000;
  }
  
  .recent-item {
    background: #fff;
    border: 2px solid #000;
  }
  
  .welcome-title {
    color: #fff;
    text-shadow: 2px 2px 4px #000;
  }
  
  .quick-actions__title {
    color: #fff;
    text-shadow: 2px 2px 4px #000;
  }
  
  .progress-section__title {
    color: #fff;
    text-shadow: 2px 2px 4px #000;
  }
  
  .recent-section__title {
    color: #fff;
    text-shadow: 2px 2px 4px #000;
  }
}

@include bem-block('action-card') {
  &:focus {
    outline: 2px solid #667eea;
    outline-offset: 2px;
  }
}

// 触摸设备优化
@media (hover: none) and (pointer: coarse) {
  .stat-card {
    min-height: 44px;
    
    &:hover {
      transform: none;
    }
  }
  
  .action-card {
    min-height: 44px;
    
    &:hover {
      transform: none;
    }
  }
  
  .recent-item {
    min-height: 44px;
    
    &:hover {
      transform: none;
    }
  }
}
</style>

