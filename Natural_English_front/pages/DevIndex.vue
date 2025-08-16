<template>
  <div class="dev-index">
    <!-- 装饰性背景元素 -->
    <div class="background-decoration">
      <div class="floating-circle circle-1"></div>
      <div class="floating-circle circle-2"></div>
      <div class="floating-circle circle-3"></div>
      <div class="floating-circle circle-4"></div>
      <div class="floating-circle circle-5"></div>
    </div>

    <!-- 主要内容 -->
    <div class="header">
      <div class="header-icon">🚀</div>
      <h1 class="animated-title">Natural English 开发中心</h1>
      <p class="subtitle">探索英语学习的无限可能</p>
    </div>

    <!-- 分类过滤器 -->
    <div class="category-filter">
      <div class="filter-header">
        <h2>📂 页面分类</h2>
        <div class="stats-summary">
          <span class="stat-item">
            <span class="stat-label">总计:</span>
            <span class="stat-value">{{ categoryStats.all.total }}</span>
          </span>
          <span class="stat-item">
            <span class="stat-label">已完成:</span>
            <span class="stat-value completed">{{ categoryStats.all.completed }}</span>
          </span>
          <span class="stat-item">
            <span class="stat-label">开发中:</span>
            <span class="stat-value developing">{{ categoryStats.all.developing }}</span>
          </span>
        </div>
      </div>
      
      <div class="category-tabs">
        <button 
          v-for="category in categories" 
          :key="category.id"
          @click="selectCategory(category.id)"
          class="category-tab"
          :class="{ 'active': selectedCategory === category.id }"
        >
          <span class="tab-icon">{{ category.icon }}</span>
          <span class="tab-name">{{ category.name }}</span>
          <span class="tab-count">({{ categoryStats[category.id].total }})</span>
        </button>
      </div>
    </div>

    <div class="page-grid">
      <div 
        v-for="page in filteredPages" 
        :key="page.path"
        class="page-card"
        :class="{ 'available': page.available, 'developing': !page.available, [`category-${page.category}`]: true }"
        @click="navigateToPage(page)"
      >
        <div class="card-header">
          <div class="page-icon">{{ page.icon }}</div>
          <div class="status-badge" :class="page.status">{{ page.statusText }}</div>
        </div>
        
        <div class="card-content">
          <h3 class="page-title">{{ page.title }}</h3>
          <p class="page-description">{{ page.description }}</p>
        </div>
        
        <div class="card-footer">
          <span class="page-path">{{ page.path }}</span>
          <button 
            v-if="page.available" 
            @click.stop="visitPage(page)"
            class="visit-btn"
          >
            访问页面
          </button>
          <button 
            v-else 
            @click.stop="developPage(page)"
            class="develop-btn"
          >
            开始开发
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DevIndex',
  data() {
    return {
      // 当前选中的分类
      selectedCategory: 'all',
      // 分类列表
      categories: [
        { id: 'all', name: '全部', icon: '🌟' },
        { id: 'word-training', name: '单词训练', icon: '📝' },
        { id: 'reading-training', name: '阅读训练', icon: '📖' },
        { id: 'listening-training', name: '听力训练', icon: '👂' },
        { id: 'conversation-training', name: '对话训练', icon: '💬' },
        { id: 'speaking-practice', name: '口语练习', icon: '🗣️' },
        { id: 'grammar-practice', name: '语法练习', icon: '📚' },
        { id: 'teacher-companion', name: '教师陪伴', icon: '👨‍🏫' },
        { id: 'management', name: '管理模块', icon: '⚙️' }
      ],
      // 所有页面项目（按分类整理）
      pages: [
        // 单词训练
        {
          title: '单词学习',
          description: 'H5版单词学习页面，展示单词详情和多种释义',
          path: '/word-learning',
          icon: '📚',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordLearning.vue',
          category: 'word-training'
        },
        {
          title: '单词详情',
          description: '单词详情页面，包含音标、释义、例句、词根词缀等完整信息',
          path: '/word-detail/institution',
          icon: '📝',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordDetail.vue',
          category: 'word-training'
        },
        {
          title: '词根分解',
          description: '词根拆解展示页面，支持词根分析和学习进度管理',
          path: '/word-root-analysis',
          icon: '🌱',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordRootAnalysis.vue',
          category: 'word-training'
        },
        {
          title: '拼写练习',
          description: '听音拼写练习页面，提升单词记忆',
          path: '/word-learning/spelling',
          icon: '✍️',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordSpelling.vue',
          category: 'word-training'
        },
        {
          title: '闪卡学习',
          description: '翻转卡片学习单词页面',
          path: '/word-learning/flashcard',
          icon: '🃏',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordFlashcard.vue',
          category: 'word-training'
        },
        {
          title: '模式匹配记忆',
          description: '三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式',
          path: '/pattern-memory',
          icon: '🧠',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'PatternMemory.vue',
          category: 'word-training'
        },
        {
          title: '单词挑战',
          description: '单词挑战游戏页面',
          path: '/word-challenge',
          icon: '⚔️',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-challenge/index.vue',
          category: 'word-training'
        },
        {
          title: '单词复习',
          description: '单词复习页面',
          path: '/word-review',
          icon: '🔄',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-review/index.vue',
          category: 'word-training'
        },
        {
          title: '单词选择',
          description: '单词选择练习页面',
          path: '/word-selection',
          icon: '✅',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-selection/index.vue',
          category: 'word-training'
        },
        {
          title: '竞技模式',
          description: '与其他学习者竞技对战，团队挑战',
          path: '/word-selection-practice',
          icon: '🏆',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-selection-practice/index.vue',
          category: 'word-training'
        },
        {
          title: '快刷模式',
          description: '快速刷题模式，自动跳转下一题，提升学习效率',
          path: '/word-selection-practice',
          icon: '⚡',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-selection-practice/index.vue',
          category: 'word-training'
        },
        // 阅读训练
        {
          title: '单词阅读',
          description: 'H5版单词阅读页面，支持音频播放和进度跟踪',
          path: '/word-reading',
          icon: '📖',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordReading.vue',
          category: 'reading-training'
        },
        {
          title: '故事阅读',
          description: '交互式故事阅读页面，支持词性标注和生词收集功能',
          path: '/story-reading',
          icon: '📚',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'StoryReading.vue',
          category: 'reading-training'
        },
        // 对话训练
        
        // 教师陪伴
        {
          title: '师生互动',
          description: '师生互动练习模式，支持单词选择和实时反馈',
          path: '/word-selection-practice2',
          icon: '👥',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordSelection.vue',
          category: 'teacher-companion'
        },
        // 管理模块
        {
          title: '资源授权',
          description: '资源授权管理页面，管理订阅、权限和资源分享',
          path: '/resource-auth',
          icon: '🔐',
          status: 'developing',
          statusText: '开发中',
          available: false,
          component: 'ResourceAuth.vue',
          category: 'management'
        },
        {
          title: '订阅管理',
          description: '订阅功能管理页面，查看和管理您的订阅状态',
          path: '/subscription-management',
          icon: '💳',
          status: 'developing',
          statusText: '开发中',
          available: false,
          component: 'SubscriptionManagement.vue',
          category: 'management'
        },
        {
          title: '资源分享',
          description: '资源分享管理页面，分享和管理您的学习资源',
          path: '/resource-sharing',
          icon: '📤',
          status: 'developing',
          statusText: '开发中',
          available: false,
          component: 'ResourceSharing.vue',
          category: 'management'
        }
      ]
    }
  },
  computed: {
    // 根据选中分类过滤页面
    filteredPages() {
      if (this.selectedCategory === 'all') {
        return this.pages
      }
      return this.pages.filter(page => page.category === this.selectedCategory)
    },
    // 统计信息
    categoryStats() {
      const stats = {}
      this.categories.forEach(category => {
        if (category.id === 'all') {
          stats[category.id] = {
            total: this.pages.length,
            completed: this.pages.filter(p => p.status === 'completed').length,
            developing: this.pages.filter(p => p.status === 'developing').length
          }
        } else {
          const categoryPages = this.pages.filter(p => p.category === category.id)
          stats[category.id] = {
            total: categoryPages.length,
            completed: categoryPages.filter(p => p.status === 'completed').length,
            developing: categoryPages.filter(p => p.status === 'developing').length
          }
        }
      })
      return stats
    }
  },
  methods: {
    // 选择分类
    selectCategory(categoryId) {
      this.selectedCategory = categoryId
    },
    navigateToPage(page) {
      if (page.available) {
        this.$router.push(page.path)
      } else {
        this.developPage(page)
      }
    },
    visitPage(page) {
      this.$router.push(page.path)
    },
    developPage(page) {
      alert(`开始开发: ${page.title}\n路径: ${page.path}\n组件: ${page.component}`)
    }
  }
}
</script>

<style scoped>
.dev-index {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
  padding: 2rem 1rem;
}

/* 分类过滤器 */
.category-filter {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  margin: 2rem 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 1.5rem;
  font-weight: 600;
}

.stats-summary {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.stat-label {
  font-size: 0.875rem;
  color: #4a5568;
  font-weight: 500;
}

.stat-value {
  font-weight: 700;
  font-size: 1rem;
  color: #2d3748;
}

.stat-value.completed {
  color: #38a169;
}

.stat-value.developing {
  color: #ed8936;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
  position: relative;
  overflow: hidden;
}

.category-tab:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.category-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.category-tab.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
  pointer-events: none;
}

.tab-icon {
  font-size: 1rem;
}

.tab-name {
  font-weight: 600;
}

.tab-count {
  font-size: 0.75rem;
  opacity: 0.8;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  margin-left: 0.25rem;
}

.category-tab.active .tab-count {
  background: rgba(255, 255, 255, 0.3);
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 120px;
  height: 120px;
  top: 20%;
  right: 15%;
  animation-delay: 2s;
}

.circle-3 {
  width: 60px;
  height: 60px;
  bottom: 30%;
  left: 20%;
  animation-delay: 4s;
}

.circle-4 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  right: 10%;
  animation-delay: 1s;
}

.circle-5 {
  width: 40px;
  height: 40px;
  top: 50%;
  left: 50%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 头部样式 */
.header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.header-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.animated-title {
  font-size: 3rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  animation: slideInDown 1s ease-out;
}

.subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  animation: slideInUp 1s ease-out 0.3s both;
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

/* 页面网格 */
.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.page-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.6s ease-out;
  position: relative;
  overflow: hidden;
}

.page-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.page-card:hover::before {
  left: 100%;
}

.page-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.page-card.available {
  border-left: 4px solid #4CAF50;
}

.page-card.developing {
  border-left: 4px solid #FF9800;
  opacity: 0.8;
}

.page-card.category-word-training {
  border-top: 3px solid #2196F3;
}

.page-card.category-practice {
  border-top: 3px solid #4CAF50;
}

.page-card.category-features {
  border-top: 3px solid #FF9800;
}

.page-card.category-games {
  border-top: 3px solid #9C27B0;
}

.page-card.category-social {
  border-top: 3px solid #E91E63;
}

.page-card.category-management {
  border-top: 3px solid #607D8B;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  position: relative;
  z-index: 1;
}

.page-icon {
  font-size: 2.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.status-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  position: relative;
  z-index: 1;
}

.status-badge.completed {
  background: #E8F5E8;
  color: #2E7D32;
}

.status-badge.developing {
  background: #FFF3E0;
  color: #F57C00;
}

.card-content {
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.8rem;
}

.page-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.page-path {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: #888;
  background: #f5f5f5;
  padding: 0.3rem 0.6rem;
  border-radius: 8px;
}

.visit-btn, .develop-btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.visit-btn::before, .develop-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.visit-btn:hover::before, .develop-btn:hover::before {
  width: 300px;
  height: 300px;
}

.visit-btn {
  background: #4CAF50;
  color: white;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.visit-btn:hover {
  background: #45a049;
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.develop-btn {
  background: #FF9800;
  color: white;
  box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
}

.develop-btn:hover {
  background: #f57c00;
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 分类过滤器 */
.category-filter {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.filter-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
  font-weight: 500;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.filter-btn.active {
  background: rgba(255, 255, 255, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

/* 分类过滤器响应式设计 */
@media (max-width: 768px) {
  .category-filter {
    padding: 1.5rem;
    margin: 1rem 0;
  }

  .filter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .filter-header h2 {
    font-size: 1.25rem;
  }

  .stats-summary {
    gap: 1rem;
    width: 100%;
  }

  .stat-item {
    flex: 1;
    min-width: 0;
    justify-content: center;
    padding: 0.5rem;
  }

  .category-tabs {
    gap: 0.5rem;
  }

  .category-tab {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }

  .tab-name {
    display: none;
  }

  .tab-icon {
    font-size: 1.2rem;
  }

  .tab-count {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
  }
}

@media (max-width: 480px) {
  .category-filter {
    padding: 1rem;
  }

  .stats-summary {
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-item {
    padding: 0.75rem;
  }

  .category-tabs {
    justify-content: center;
  }

  .category-tab {
    padding: 0.75rem;
    min-width: 60px;
    justify-content: center;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dev-index {
    padding: 1rem 0.5rem;
  }
  
  .animated-title {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .page-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .category-filter {
    gap: 0.5rem;
  }
  
  .filter-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .page-card {
    padding: 1.5rem;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .page-path {
    text-align: center;
  }
  
  .visit-btn, .develop-btn {
    width: 100%;
  }
}

/* 加载状态 */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>

