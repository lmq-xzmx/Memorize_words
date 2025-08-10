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

    <div class="page-grid">
      <div 
        v-for="page in pages" 
        :key="page.path"
        class="page-card"
        :class="{ 'available': page.available, 'developing': !page.available }"
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
      pages: [
        {
          title: '单词阅读',
          description: 'H5版单词阅读页面，支持音频播放和进度跟踪',
          path: '/word-reading',
          icon: '📖',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordReading.vue'
        },
        {
          title: '单词学习',
          description: 'H5版单词学习页面，展示单词详情和多种释义',
          path: '/word-learning',
          icon: '📚',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordLearning.vue'
        },
        {
          title: '拼写练习',
          description: '听音拼写练习页面，提升单词记忆',
          path: '/word-learning/spelling',
          icon: '✍️',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordSpelling.vue'
        },
        {
          title: '闪卡学习',
          description: '翻转卡片学习单词页面',
          path: '/word-learning/flashcard',
          icon: '🃏',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordFlashcard.vue'
        },
        {
          title: '单词详情',
          description: '单词详情页面，包含音标、释义、例句、词根词缀等完整信息',
          path: '/word-detail/institution',
          icon: '📝',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordDetail.vue'
        },
        {
          title: '词根分解',
          description: '词根拆解展示页面，支持词根分析和学习进度管理',
          path: '/word-root-analysis',
          icon: '🌱',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'WordRootAnalysis.vue'
        },
        {
          title: '模式匹配记忆',
          description: '三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式',
          path: '/pattern-memory',
          icon: '🧠',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'PatternMemory.vue'
        },
        {
          title: '故事阅读',
          description: '交互式故事阅读页面，支持词性标注和生词收集功能',
          path: '/story-reading',
          icon: '📚',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'StoryReading.vue'
        },
        {
          title: '单词挑战',
          description: '单词挑战游戏页面',
          path: '/word-challenge',
          icon: '⚔️',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-challenge/index.vue'
        },
        {
          title: '单词复习',
          description: '单词复习页面',
          path: '/word-review',
          icon: '🔄',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-review/index.vue'
        },
        {
          title: '单词选择',
          description: '单词选择练习页面',
          path: '/word-selection',
          icon: '✅',
          status: 'completed',
          statusText: '已完成',
          available: true,
          component: 'word-selection/index.vue'
        }
      ]
    }
  },
  methods: {
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
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  min-height: 100vh;
  color: white;
  position: relative;
  overflow: hidden;
}

/* 装饰性背景元素 */
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
  backdrop-filter: blur(10px);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 120px;
  height: 120px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 80px;
  height: 80px;
  top: 20%;
  right: 15%;
  animation-delay: 1s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  left: 5%;
  animation-delay: 2s;
}

.circle-4 {
  width: 100px;
  height: 100px;
  bottom: 30%;
  right: 10%;
  animation-delay: 3s;
}

.circle-5 {
  width: 60px;
  height: 60px;
  top: 50%;
  left: 50%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.header-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: bounce 2s ease-in-out infinite;
  display: inline-block;
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
  font-size: 2.8rem;
  margin-bottom: 15px;
  text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
  background: linear-gradient(45deg, #fff, #f0f8ff, #fff);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s ease-in-out infinite;
  font-weight: 700;
}

@keyframes shimmer {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  position: relative;
  z-index: 1;
}

.page-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  color: #333;
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
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transition: left 0.5s;
}

.page-card:hover::before {
  left: 100%;
}

.page-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.page-card.available {
  border-left: 4px solid #28a745;
}

.page-card.developing {
  border-left: 4px solid #ffc107;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.page-icon {
  font-size: 2.5rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.completed {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
}

.status-badge.developing {
  background: linear-gradient(45deg, #ffc107, #fd7e14);
  color: #333;
}

.card-content {
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #2c3e50;
  background: linear-gradient(45deg, #2c3e50, #3498db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-description {
  color: #666;
  line-height: 1.6;
  font-size: 0.95rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.page-path {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.8rem;
  color: #666;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.visit-btn, .develop-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.visit-btn {
  background: linear-gradient(45deg, #007bff, #0056b3);
  color: white;
}

.visit-btn:hover {
  background: linear-gradient(45deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.develop-btn {
  background: linear-gradient(45deg, #ffc107, #e0a800);
  color: #333;
}

.develop-btn:hover {
  background: linear-gradient(45deg, #e0a800, #d39e00);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dev-index {
    padding: 15px;
  }
  
  .page-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .animated-title {
    font-size: 2.2rem;
  }
  
  .header-icon {
    font-size: 3rem;
  }
}

@media (max-width: 480px) {
  .page-card {
    padding: 20px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .visit-btn, .develop-btn {
    width: 100%;
    text-align: center;
  }
}
</style>