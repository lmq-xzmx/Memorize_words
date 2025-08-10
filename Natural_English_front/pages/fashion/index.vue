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
  background: #f8f9fa;
  padding-bottom: 80px;
}

.header {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
  text-align: center;
  padding: 30px 20px;
}

.header h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.header p {
  font-size: 14px;
  opacity: 0.9;
}

.content {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.tabs {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  color: #666;
}

.tab-item.active {
  background: #ff6b6b;
  color: white;
}

.trend-card,
.expression-card,
.culture-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.trend-image {
  height: 150px;
  background: #f0f0f0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-placeholder {
  color: #aaa;
  font-size: 18px;
  font-weight: bold;
}

.trend-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 107, 107, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.trend-content {
  padding: 16px;
}

.trend-content h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.trend-content p {
  color: #666;
  line-height: 1.5;
  margin-bottom: 12px;
  font-size: 14px;
}

.trend-meta {
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 12px;
}

.expression-card {
  padding: 16px;
}

.expression-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.expression-icon {
  width: 36px;
  height: 36px;
  background: #f8f9fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
}

.expression-title {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.expression-content {
  margin-bottom: 16px;
}

.expression-original {
  font-size: 18px;
  color: #ff6b6b;
  font-weight: 600;
  margin-bottom: 8px;
}

.expression-translation {
  color: #666;
  margin-bottom: 12px;
  font-size: 14px;
}

.example-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  font-size: 14px;
}

.example-content {
  color: #666;
  font-style: italic;
  line-height: 1.5;
  font-size: 14px;
}

.expression-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  background: white;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #f5f5f5;
  border-color: #ff6b6b;
}

.culture-card {
  padding: 16px;
}

.culture-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.culture-header h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.culture-category {
  background: #f0f0f0;
  color: #666;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.culture-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
  font-size: 14px;
}

.culture-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.keyword {
  background: #f0f0f0;
  color: #666;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.culture-footer {
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 12px;
  margin-top: 12px;
}

.subscription {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  padding: 30px 20px;
  margin-top: 30px;
}

.subscription-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  color: white;
}

.subscription-content h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.subscription-content p {
  font-size: 14px;
  margin-bottom: 20px;
  opacity: 0.9;
}

.subscription-form {
  display: flex;
  max-width: 400px;
  margin: 0 auto;
}

.subscription-form input {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px 0 0 8px;
  font-size: 14px;
}

.subscription-form button {
  background: #333;
  color: white;
  border: none;
  padding: 0 20px;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.subscription-form button:hover {
  background: #555;
}
</style>