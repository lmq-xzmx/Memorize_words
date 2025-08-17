<template>
  <div class="learning-mode-selector">
    <!-- 几何背景装饰层 -->
    <div class="geometric-background">
      <div class="geometric-shape shape-1"></div>
      <div class="geometric-shape shape-2"></div>
      <div class="geometric-shape shape-3"></div>
      <div class="geometric-shape shape-4"></div>
      <div class="geometric-shape shape-5"></div>
      <div class="geometric-shape shape-6"></div>
    </div>
    
    <div class="header">
      <h1>英语学习中心</h1>
      <p class="subtitle">选择您的学习模式</p>
    </div>
    
    <!-- 分类标题 -->
    <div class="category-section">
      <h2 class="category-title">📚 学习模块</h2>
      <div class="mode-grid">
        <!-- 单词阅读 -->
        <div v-if="canUseMode('word-reading')" class="mode-card" @click="navigateToMode('word-reading')">
          <div class="mode-header">
            <div class="mode-icon">📖</div>
            <div class="mode-title">单词阅读</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-reading"
                v-model="selectedHomepage"
                @change="setHomepage('word-reading')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>H5版单词阅读页面，支持音频播放和进度跟踪</p>
            <div class="mode-features">
              <span class="feature-tag">音频播放</span>
              <span class="feature-tag">进度跟踪</span>
              <span class="feature-tag">发音练习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">发音练习</span>
            </div>
          </div>
        </div>

        <!-- 单词学习 -->
        <div v-if="canUseMode('word-learning')" class="mode-card" @click="navigateToMode('word-learning')">
          <div class="mode-header">
            <div class="mode-icon">📚</div>
            <div class="mode-title">单词学习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-learning"
                v-model="selectedHomepage"
                @change="setHomepage('word-learning')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>H5版单词学习页面，展示单词详情和多种释义</p>
            <div class="mode-features">
              <span class="feature-tag">详细释义</span>
              <span class="feature-tag">例句展示</span>
              <span class="feature-tag">词汇积累</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">系统学习</span>
            </div>
          </div>
        </div>

        <!-- 单词详情 -->
        <div v-if="canUseMode('word-detail')" class="mode-card" @click="navigateToMode('word-detail')">
          <div class="mode-header">
            <div class="mode-icon">📝</div>
            <div class="mode-title">单词详情</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-detail"
                v-model="selectedHomepage"
                @change="setHomepage('word-detail')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词详情页面，包含音标、释义、例句、词根词缀等完整信息</p>
            <div class="mode-features">
              <span class="feature-tag">音标标注</span>
              <span class="feature-tag">词根分析</span>
              <span class="feature-tag">例句丰富</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">深度学习</span>
            </div>
          </div>
        </div>

        <!-- 词根分解 -->
        <div v-if="canUseMode('word-root-analysis')" class="mode-card" @click="navigateToMode('word-root-analysis')">
          <div class="mode-header">
            <div class="mode-icon">🌱</div>
            <div class="mode-title">词根分解</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-root-analysis"
                v-model="selectedHomepage"
                @change="setHomepage('word-root-analysis')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>词根拆解展示页面，支持词根分析和学习进度管理</p>
            <div class="mode-features">
              <span class="feature-tag">词根拆解</span>
              <span class="feature-tag">词缀分析</span>
              <span class="feature-tag">记忆技巧</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">词汇扩展</span>
            </div>
          </div>
        </div>

        <!-- 故事阅读 -->
        <div v-if="canUseMode('story-reading')" class="mode-card" @click="navigateToMode('story-reading')">
          <div class="mode-header">
            <div class="mode-icon">📚</div>
            <div class="mode-title">故事阅读</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="story-reading"
                v-model="selectedHomepage"
                @change="setHomepage('story-reading')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>交互式故事阅读页面，支持词性标注和生词收集功能</p>
            <div class="mode-features">
              <span class="feature-tag">词性标注</span>
              <span class="feature-tag">生词收集</span>
              <span class="feature-tag">情境学习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">阅读提升</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 练习模块 -->
    <div class="category-section">
      <h2 class="category-title">✍️ 练习模块</h2>
      <div class="mode-grid">

        <!-- 拼写练习 -->
        <div v-if="canUseMode('spelling')" class="mode-card" @click="navigateToMode('spelling')">
          <div class="mode-header">
            <div class="mode-icon">✍️</div>
            <div class="mode-title">拼写练习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="spelling"
                v-model="selectedHomepage"
                @change="setHomepage('spelling')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>听音拼写练习页面，提升单词记忆</p>
            <div class="mode-features">
              <span class="feature-tag">听音练习</span>
              <span class="feature-tag">拖拽拼写</span>
              <span class="feature-tag">记忆强化</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">拼写练习</span>
            </div>
          </div>
        </div>

        <!-- 闪卡学习 -->
        <div v-if="canUseMode('flashcard')" class="mode-card" @click="navigateToMode('flashcard')">
          <div class="mode-header">
            <div class="mode-icon">🃏</div>
            <div class="mode-title">闪卡学习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="flashcard"
                v-model="selectedHomepage"
                @change="setHomepage('flashcard')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>翻转卡片学习单词页面</p>
            <div class="mode-features">
              <span class="feature-tag">卡片翻转</span>
              <span class="feature-tag">快速记忆</span>
              <span class="feature-tag">重复练习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">快速记忆</span>
            </div>
          </div>
        </div>

        <!-- 模式匹配记忆 -->
        <div v-if="canUseMode('pattern-memory')" class="mode-card" @click="navigateToMode('pattern-memory')">
          <div class="mode-header">
            <div class="mode-icon">🧠</div>
            <div class="mode-title">模式匹配记忆</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="pattern-memory"
                v-model="selectedHomepage"
                @change="setHomepage('pattern-memory')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式</p>
            <div class="mode-features">
              <span class="feature-tag">图片选择</span>
              <span class="feature-tag">选择题</span>
              <span class="feature-tag">单词补全</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">系统学习</span>
            </div>
          </div>
        </div>

        <!-- 单词挑战 -->
        <div v-if="canUseMode('word-challenge')" class="mode-card" @click="navigateToMode('word-challenge')">
          <div class="mode-header">
            <div class="mode-icon">⚔️</div>
            <div class="mode-title">单词挑战</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-challenge"
                v-model="selectedHomepage"
                @change="setHomepage('word-challenge')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词挑战游戏页面</p>
            <div class="mode-features">
              <span class="feature-tag">游戏化</span>
              <span class="feature-tag">挑战模式</span>
              <span class="feature-tag">竞技对战</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">竞技挑战</span>
            </div>
          </div>
        </div>

        <!-- 单词复习 -->
        <div v-if="canUseMode('word-review')" class="mode-card" @click="navigateToMode('word-review')">
          <div class="mode-header">
            <div class="mode-icon">🔄</div>
            <div class="mode-title">单词复习</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-review"
                v-model="selectedHomepage"
                @change="setHomepage('word-review')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词复习页面</p>
            <div class="mode-features">
              <span class="feature-tag">复习计划</span>
              <span class="feature-tag">遗忘曲线</span>
              <span class="feature-tag">智能推荐</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">巩固复习</span>
            </div>
          </div>
        </div>

        <!-- 单词选择 -->
        <div v-if="canUseMode('word-selection')" class="mode-card" @click="navigateToMode('word-selection')">
          <div class="mode-header">
            <div class="mode-icon">✅</div>
            <div class="mode-title">单词选择</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="word-selection"
                v-model="selectedHomepage"
                @change="setHomepage('word-selection')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>单词选择练习页面</p>
            <div class="mode-features">
              <span class="feature-tag">选择题</span>
              <span class="feature-tag">快速判断</span>
              <span class="feature-tag">准确率统计</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">快速练习</span>
            </div>
          </div>
        </div>

        <!-- 师生互动 -->
        <div v-if="canUseMode('teacher-student-interaction')" class="mode-card" @click="navigateToMode('teacher-student-interaction')">
          <div class="mode-header">
            <div class="mode-icon">👥</div>
            <div class="mode-title">师生互动</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="teacher-student-interaction"
                v-model="selectedHomepage"
                @change="setHomepage('teacher-student-interaction')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>师生互动练习模式，支持单词选择和实时反馈</p>
            <div class="mode-features">
              <span class="feature-tag">师生互动</span>
              <span class="feature-tag">实时反馈</span>
              <span class="feature-tag">协作学习</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">课堂教学</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 特色模块 -->
    <div class="category-section">
      <h2 class="category-title">🏆 特色模块</h2>
      <div class="mode-grid">
        <!-- 竞技模式 -->
        <div v-if="canUseMode('competition')" class="mode-card" @click="navigateToMode('competition')">
          <div class="mode-header">
            <div class="mode-icon">🏆</div>
            <div class="mode-title">竞技模式</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="competition"
                v-model="selectedHomepage"
                @change="setHomepage('competition')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>与其他学习者竞技对战，团队挑战</p>
            <div class="mode-features">
              <span class="feature-tag">实时对战</span>
              <span class="feature-tag">团队挑战</span>
              <span class="feature-tag">排行榜</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">竞技挑战</span>
            </div>
          </div>
        </div>

        <!-- 快刷模式 -->
        <div v-if="canUseMode('quick-brush')" class="mode-card" @click="navigateToMode('quick-brush')">
          <div class="mode-header">
            <div class="mode-icon">⚡</div>
            <div class="mode-title">快刷模式</div>
            <div class="homepage-selector">
              <input 
                type="radio" 
                name="homepage" 
                value="quick-brush"
                v-model="selectedHomepage"
                @change="setHomepage('quick-brush')"
                @click.stop
              >
              <label>设为首页</label>
            </div>
          </div>
          <div class="mode-description">
            <p>快速刷题模式，自动跳转下一题，提升学习效率</p>
            <div class="mode-features">
              <span class="feature-tag">实时计时</span>
              <span class="feature-tag">自动跳转</span>
              <span class="feature-tag">快速反馈</span>
            </div>
          </div>
          <div class="mode-stats">
            <div class="stat-item">
              <span class="stat-label">适合人群</span>
              <span class="stat-value">快速复习</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 当前首页设置提示 -->
    <div v-if="selectedHomepage" class="homepage-tip">
      <div class="tip-content">
        <span class="tip-icon">🏠</span>
        <span class="tip-text">当前首页：{{ getModeName(selectedHomepage) }}</span>
        <button @click="clearHomepage" class="clear-btn">清除设置</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.learning-mode-selector {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

/* 几何背景装饰 */
.geometric-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.geometric-shape {
  position: absolute;
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  top: 10%;
  left: 10%;
  width: 80px;
  height: 80px;
  background: linear-gradient(45deg, #fff, transparent);
  border-radius: 50%;
  animation-delay: 0s;
}

.shape-2 {
  top: 20%;
  right: 15%;
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, #fff, transparent);
  transform: rotate(45deg);
  animation-delay: 1s;
}

.shape-3 {
  bottom: 30%;
  left: 20%;
  width: 100px;
  height: 100px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation-delay: 2s;
}

.shape-4 {
  bottom: 20%;
  right: 10%;
  width: 70px;
  height: 70px;
  background: linear-gradient(45deg, #fff, transparent);
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
  animation-delay: 3s;
}

.shape-5 {
  top: 50%;
  left: 5%;
  width: 50px;
  height: 50px;
  background: linear-gradient(45deg, #fff, transparent);
  transform: rotate(45deg);
  animation-delay: 4s;
}

.shape-6 {
  top: 70%;
  right: 25%;
  width: 90px;
  height: 90px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transform: rotate(30deg);
  animation-delay: 5s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 主要内容区域 */
.header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  z-index: 2;
}

.header h1 {
  color: white;
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.25rem;
  font-weight: 400;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.category-section {
  margin-bottom: 3rem;
  position: relative;
  z-index: 2;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.content {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
}

.category-title {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 3rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.modes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.mode-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.mode-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
}

.mode-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
  text-align: center;
}

.mode-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  text-align: center;
}

.mode-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
  position: relative;
}

.mode-description {
  color: #666;
  line-height: 1.6;
  text-align: center;
  margin-bottom: 1.5rem;
}

.mode-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}

.feature-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.mode-stats {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #888;
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-value {
  color: #333;
  font-size: 0.875rem;
  font-weight: 600;
}

.homepage-selector {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #666;
}

.homepage-selector input[type="radio"] {
  margin: 0;
  width: 14px;
  height: 14px;
}

.homepage-selector label {
  margin: 0;
  cursor: pointer;
  user-select: none;
}

.mode-button {
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.homepage-tip {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 2;
}

.tip-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.tip-icon {
  font-size: 1.5rem;
}

.clear-btn {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
  border: 1px solid #ff3b30;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: #ff3b30;
  color: white;
}

.tip-text {
  color: #555;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.tip-button {
  padding: 10px 20px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tip-button:hover {
  background: #667eea;
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .learning-mode-selector {
    padding: 16px;
  }
  
  .category-title {
    font-size: 2rem;
    margin-bottom: 2rem;
  }
  
  .modes-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .mode-card {
    padding: 1.5rem;
  }
  
  .mode-icon {
    font-size: 2.5rem;
  }
  
  .mode-title {
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .category-title {
    font-size: 1.75rem;
  }
  
  .mode-card {
    padding: 1.25rem;
  }
  
  .mode-icon {
    font-size: 2rem;
  }
}
</style>

<script>
import { UserSettingsManager } from '../utils/userSettings'
import userPersonalizationMixin, { predefinedElementConfigs } from '../mixins/userPersonalization'
import permissionMixin from '../mixins/permissionMixin'
import { homepageManager } from '../utils/homepageManager'

export default {
  name: 'LearningModeSelector',
  mixins: [userPersonalizationMixin, permissionMixin],
  data() {
    return {
      selectedHomepage: '',
      userId: 'default',
      userSettings: new UserSettingsManager(),
      // 学习模式权限映射
      modePermissions: {
        'word-reading': 'practice_reading',
        'word-learning': 'view_word_learning',
        'word-detail': 'view_word_detail',
        'word-root-analysis': 'analyze_word_roots',
        'story-reading': 'practice_story_reading',
        'spelling': 'practice_spelling',
        'flashcard': 'use_flashcard',
        'pattern-memory': 'use_pattern_memory',
        'word-challenge': 'participate_challenge',
        'word-review': 'review_words',
        'word-selection': 'practice_word_selection',
        'teacher-student-interaction': 'practice_word_selection',
        'competition': 'participate_challenge',
        'quick-brush': 'review_words'
      }
    }
  },
  
  computed: {
    /**
     * 根据用户权限过滤可用的学习模式
     */
    availableModes() {
      const allModes = Object.keys(this.modePermissions)
      return allModes.filter(mode => {
        const permission = this.modePermissions[mode]
        return this.$hasPermission(permission)
      })
    }
  },
  methods: {
    /**
     * 检查用户是否有权限使用指定模式
     */
    canUseMode(mode) {
      const permission = this.modePermissions[mode]
      if (!permission) {
        console.warn(`未定义模式 ${mode} 的权限要求`)
        return false
      }
      return this.$hasPermission(permission)
    },
    
    /**
     * 导航到指定模式（带权限检查）
     */
    navigateToMode(mode) {
      if (!this.canUseMode(mode)) {
        this.$showError(`您没有权限使用${this.getModeName(mode)}功能`)
        return
      }
      
      // 执行导航
      switch(mode) {
        case 'word-reading':
          this.$router.push('/word-reading')
          break
        case 'word-learning':
          this.$router.push('/word-learning')
          break
        case 'word-detail':
          this.$router.push('/word-detail/institution')
          break
        case 'word-root-analysis':
          this.$router.push('/word-root-analysis')
          break
        case 'story-reading':
          this.$router.push('/story-reading')
          break
        case 'spelling':
          this.$router.push('/word-learning/spelling')
          break
        case 'flashcard':
          this.$router.push('/word-learning/flashcard')
          break
        case 'pattern-memory':
          this.$router.push('/pattern-memory')
          break
        case 'word-challenge':
          this.$router.push('/word-challenge')
          break
        case 'word-review':
          this.$router.push('/word-review')
          break
        case 'word-selection':
          this.$router.push('/word-selection')
          break
        case 'teacher-student-interaction':
          this.$router.push('/word-selection-practice2')
          break
        case 'competition':
          this.$router.push('/competition')
          break
        case 'quick-brush':
          this.$router.push('/quick-brush')
          break
        default:
          console.log('未知模式:', mode)
      }
    },
    
    setHomepage(mode) {
      if (!this.canUseMode(mode)) {
        this.$showError(`您没有权限将${this.getModeName(mode)}设置为首页`)
        return
      }
      
      const success = homepageManager.setHomepage(mode)
      if (success) {
        this.selectedHomepage = mode
        
        // 只显示设置成功提示，不自动跳转
        this.$nextTick(() => {
          this.$showSuccess(`已将"${homepageManager.getModeName(mode)}"设置为首页`)
        })
      } else {
        this.$showError('设置首页失败，请重试')
      }
    },
    
    clearHomepage() {
      const success = homepageManager.clearHomepage()
      if (success) {
        this.selectedHomepage = ''
      }
    },
    
    getModeName(mode) {
      return homepageManager.getModeName(mode)
    },
    
    // 获取用户ID
    getUserId() {
      this.userId = this.userSettings.userId
    },
    
    // 加载用户的首页设置
    loadUserHomepageSettings() {
      this.selectedHomepage = homepageManager.getHomepage() || ''
    }
  },
  
  mounted() {
    // 获取用户ID
    this.getUserId()
    
    // 加载用户的首页设置
    this.loadUserHomepageSettings()
    
    // 应用竞技模式元素配置
    this.$nextTick(() => {
      const competitionConfigs = predefinedElementConfigs.competitionElements
      if (competitionConfigs && typeof competitionConfigs === 'object') {
        // competitionConfigs 是对象，不是数组，所以使用 Object.entries 遍历
        Object.entries(competitionConfigs).forEach(([key, config]) => {
          if (config && config.position && config.size) {
            // 应用元素配置
            console.log(`Applying config for ${key}:`, config)
          }
        })
      }
    })
    
    // 暂时禁用自动重定向功能
    // 这样可以避免登录后立即跳转的问题
    console.log('LearningModeSelector: 已禁用自动重定向，用户可手动选择学习模式')
  }
}
</script>