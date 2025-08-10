<template>
  <div class="discover-container">
    <div class="header">
      <h1>发现</h1>
      <p class="subtitle">探索更多学习内容和功能</p>
    </div>
    
    <div class="content">
      <div class="feature-grid">
        <div class="feature-card" @click="navigateTo('/word-challenge')">
          <div class="feature-icon">🎯</div>
          <h3>单词挑战</h3>
          <p>挑战你的词汇量</p>
        </div>
        
        <div class="feature-card" @click="navigateTo('/story-reading')">
          <div class="feature-icon">📚</div>
          <h3>故事阅读</h3>
          <p>在故事中学习单词</p>
        </div>
        
        <div class="feature-card" @click="navigateTo('/pattern-memory')">
          <div class="feature-icon">🧠</div>
          <h3>模式记忆</h3>
          <p>科学记忆方法</p>
        </div>
        
        <div class="feature-card" @click="navigateTo('/listening')">
          <div class="feature-icon">🎧</div>
          <h3>听力练习</h3>
          <p>提升听力技能</p>
        </div>
        
        <div class="feature-card" @click="navigateTo('/word-root-analysis')">
          <div class="feature-icon">🔍</div>
          <h3>词根分析</h3>
          <p>深入理解单词构成</p>
        </div>
        
        <div class="feature-card" @click="navigateTo('/community')">
          <div class="feature-icon">👥</div>
          <h3>学习社区</h3>
          <p>与其他学习者交流</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Discover',
  methods: {
    navigateTo(path) {
      this.$router.push(path)
    }
  }
}
</script>

<style scoped>
.discover-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
  padding-top: 40px;
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.feature-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  background: white;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.feature-card h3 {
  font-size: 1.3rem;
  margin-bottom: 10px;
  color: #333;
  font-weight: 600;
}

.feature-card p {
  color: #666;
  font-size: 0.95rem;
  margin: 0;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .feature-card {
    padding: 25px;
  }
}
</style>