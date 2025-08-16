<template>
  <div class="fashion">
    <div class="header">
      <h1>时尚趋势</h1>
      <p>探索英语世界的流行文化</p>
    </div>
    
    <div class="content">
      <div class="tabs">
        <div 
          v-for="tab in tabs" 
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.name }}
        </div>
      </div>
      
      <div class="tab-content">
        <!-- 流行趋势 -->
        <div v-if="activeTab === 'trends'" class="trends-list">
          <div v-for="trend in trendsList" :key="trend.id" class="trend-card">
            <div class="trend-image">
              <div class="trend-tag">{{ trend.tag }}</div>
              <div class="trend-placeholder">{{ trend.title }}</div>
            </div>
            <div class="trend-content">
              <h3>{{ trend.title }}</h3>
              <p>{{ trend.description }}</p>
              <div class="trend-meta">
                <span>{{ trend.date }}</span>
                <span>{{ trend.views }} 浏览</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 英语表达 -->
        <div v-if="activeTab === 'expressions'" class="expressions-list">
          <div v-for="expr in expressionsList" :key="expr.id" class="expression-card">
            <div class="expression-header">
              <div class="expression-icon">🔤</div>
              <div class="expression-title">{{ expr.title }}</div>
            </div>
            <div class="expression-content">
              <div class="expression-original">{{ expr.original }}</div>
              <div class="expression-translation">{{ expr.translation }}</div>
              <div class="expression-example">
                <div class="example-title">例句：</div>
                <div class="example-content">{{ expr.example }}</div>
              </div>
            </div>
            <div class="expression-actions">
              <button class="action-btn">
                <span class="icon">🔊</span>
                朗读
              </button>
              <button class="action-btn">
                <span class="icon">📝</span>
                记笔记
              </button>
              <button class="action-btn">
                <span class="icon">💾</span>
                保存
              </button>
            </div>
          </div>
        </div>
        
        <!-- 文化解析 -->
        <div v-if="activeTab === 'culture'" class="culture-list">
          <div v-for="culture in cultureList" :key="culture.id" class="culture-card">
            <div class="culture-header">
              <h3>{{ culture.title }}</h3>
              <div class="culture-category">{{ culture.category }}</div>
            </div>
            <div class="culture-content">
              <p>{{ culture.content }}</p>
              <div v-if="culture.keywords.length > 0" class="culture-keywords">
                <span v-for="(keyword, index) in culture.keywords" :key="index" class="keyword">
                  {{ keyword }}
                </span>
              </div>
            </div>
            <div class="culture-footer">
              <div class="culture-author">作者：{{ culture.author }}</div>
              <div class="culture-date">{{ culture.date }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 订阅区域 -->
    <div class="subscription">
      <div class="subscription-content">
        <h3>订阅时尚英语周刊</h3>
        <p>每周获取最新的英语表达和流行文化解析</p>
        <div class="subscription-form">
          <input type="email" placeholder="输入您的邮箱" v-model="email">
          <button @click="subscribe">订阅</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Fashion',
  data() {
    return {
      activeTab: 'trends',
      email: '',
      tabs: [
        { key: 'trends', name: '流行趋势' },
        { key: 'expressions', name: '英语表达' },
        { key: 'culture', name: '文化解析' }
      ],
      trendsList: [
        {
          id: 1,
          title: '2023年最流行的英语缩写',
          description: '了解年轻人社交媒体上最常用的英语缩写和它们的含义。',
          tag: '社交媒体',
          date: '2023-05-15',
          views: 1245
        },
        {
          id: 2,
          title: '英美口语差异大盘点',
          description: '同样是英语，英国人和美国人的表达方式有哪些不同？',
          tag: '语言对比',
          date: '2023-05-10',
          views: 982
        },
        {
          id: 3,
          title: '流行歌曲中的英语学习',
          description: '通过当下流行的英文歌曲学习地道的英语表达。',
          tag: '音乐英语',
          date: '2023-05-05',
          views: 1567
        }
      ],
      expressionsList: [
        {
          id: 1,
          title: '时尚圈常用表达',
          original: 'Fashion-forward',
          translation: '走在时尚前沿的',
          example: 'Her fashion-forward style always turns heads at events.'
        },
        {
          id: 2,
          title: '社交媒体热词',
          original: 'Throwing shade',
          translation: '暗讽、暗中批评',
          example: 'He wasn\'t directly criticizing her, but he was definitely throwing shade.'
        },
        {
          id: 3,
          title: '流行文化用语',
          original: 'Binge-watching',
          translation: '连续观看（剧集）',
          example: 'I spent the entire weekend binge-watching the new season of my favorite show.'
        }
      ],
      cultureList: [
        {
          id: 1,
          title: '美国感恩节的文化背景',
          category: '节日文化',
          content: '感恩节是美国人最重要的节日之一，起源于1621年，最初是为了感谢丰收。现代感恩节通常包括家庭聚餐、火鸡大餐、橄榄球比赛和游行等传统活动。',
          keywords: ['感恩节', '美国文化', '传统节日'],
          author: '文化研究员',
          date: '2023-04-20'
        },
        {
          id: 2,
          title: '英国饮茶文化的历史演变',
          category: '生活习俗',
          content: '英国的下午茶文化始于19世纪，最初是由贝德福德公爵夫人安娜引入的。传统英式下午茶包括茶、三明治、司康饼和各种甜点。了解这一文化有助于理解英国人的社交礼仪。',
          keywords: ['英国文化', '下午茶', '社交礼仪'],
          author: '历史学者',
          date: '2023-04-15'
        }
      ]
    }
  },
  methods: {
    subscribe() {
      if (this.email && this.validateEmail(this.email)) {
        alert('订阅成功！每周五我们会向您发送时尚英语周刊。')
        this.email = ''
      } else {
        alert('请输入有效的邮箱地址')
      }
    },
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    }
  }
}
</script>

<style scoped>
.fashion {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6c5ce7 100%);
  position: relative;
  overflow-x: hidden;
}

/* 背景装饰 */
.fashion::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="fashion-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23fashion-pattern)"/></svg>') repeat;
  pointer-events: none;
  z-index: 0;
}

/* 头部样式 */
.header {
  text-align: center;
  padding: 4rem 2rem 2rem;
  position: relative;
  z-index: 1;
}

.header h1 {
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  animation: fadeInDown 1s ease-out;
  background: linear-gradient(45deg, #ffffff, #e8f4fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header p {
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.9);
  animation: fadeInUp 1s ease-out 0.3s both;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

/* 内容区域 */
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 1;
}

/* 标签页样式 */
.tabs {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.tab-item {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  padding: 1rem 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
  position: relative;
  overflow: hidden;
}

.tab-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.tab-item:hover::before {
  left: 100%;
}

.tab-item:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.tab-item.active {
  background: rgba(255, 255, 255, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

/* 标签内容 */
.tab-content {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 趋势列表 */
.trends-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.trend-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
  position: relative;
}

.trend-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.trend-image {
  height: 200px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.trend-tag {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  padding: 0.5rem 1rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 600;
}

.trend-placeholder {
  text-align: center;
  padding: 1rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.trend-content {
  padding: 1.5rem;
}

.trend-content h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.8rem;
}

.trend-content p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.trend-meta {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 0.9rem;
}

/* 表达列表 */
.expressions-list {
  display: grid;
  gap: 2rem;
  margin-bottom: 3rem;
}

.expression-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: slideInLeft 0.6s ease-out;
  border-left: 4px solid #667eea;
}

.expression-card:hover {
  transform: translateX(10px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.expression-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.expression-icon {
  font-size: 2rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-5px);
  }
  60% {
    transform: translateY(-3px);
  }
}

.expression-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.expression-content {
  margin-bottom: 1.5rem;
}

.expression-original {
  font-size: 1.4rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.expression-translation {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 1rem;
}

.expression-example {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 10px;
  border-left: 3px solid #a29bfe;
}

.example-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.example-content {
  color: #555;
  font-style: italic;
}

.expression-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 0.8rem 1.2rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-btn::before {
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

.action-btn:hover::before {
  width: 300px;
  height: 300px;
}

.action-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.action-btn .icon {
  font-size: 1.1rem;
}

/* 文化列表 */
.culture-list {
  display: grid;
  gap: 2rem;
  margin-bottom: 3rem;
}

.culture-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: slideInRight 0.6s ease-out;
  border-top: 4px solid #a29bfe;
}

.culture-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.culture-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.culture-header h3 {
  font-size: 1.4rem;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.culture-category {
  background: #a29bfe;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 600;
}

.culture-content p {
  color: #555;
  line-height: 1.8;
  margin-bottom: 1.5rem;
}

.culture-keywords {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.keyword {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
}

.culture-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  color: #888;
  font-size: 0.9rem;
}

/* 订阅区域 */
.subscription {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  margin: 4rem 2rem 2rem;
  border-radius: 30px;
  padding: 3rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.subscription-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.subscription-content p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
}

.subscription-form {
  display: flex;
  gap: 1rem;
  max-width: 400px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.subscription-form input {
  flex: 1;
  min-width: 200px;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.subscription-form input:focus {
  outline: none;
  background: white;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  transform: scale(1.02);
}

.subscription-form button {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.subscription-form button::before {
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

.subscription-form button:hover::before {
  width: 300px;
  height: 300px;
}

.subscription-form button:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

/* 动画效果 */
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

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 2rem 1rem 1rem;
  }
  
  .header h1 {
    font-size: 2.5rem;
  }
  
  .header p {
    font-size: 1.1rem;
  }
  
  .content {
    padding: 0 1rem;
  }
  
  .tabs {
    gap: 0.5rem;
  }
  
  .tab-item {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
  }
  
  .trends-list {
    grid-template-columns: 1fr;
  }
  
  .expression-actions {
    justify-content: center;
  }
  
  .culture-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .culture-footer {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .subscription {
    margin: 2rem 1rem;
    padding: 2rem;
  }
  
  .subscription-content h3 {
    font-size: 1.5rem;
  }
  
  .subscription-form {
    flex-direction: column;
  }
  
  .subscription-form input,
  .subscription-form button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .trend-card,
  .expression-card,
  .culture-card {
    padding: 1.5rem;
  }
  
  .action-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
}
</style>

