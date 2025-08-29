<template>
  <view class="trends-page">
    <view class="header">
      <text class="title">📈 趋势</text>
      <text class="subtitle">时尚趋势与热门话题</text>
    </view>
    
    <view class="content">
      <!-- 趋势分类 -->
      <view class="category-section">
        <scroll-view class="category-scroll" scroll-x>
          <view class="category-list">
            <view 
              v-for="(category, index) in categories" 
              :key="index"
              class="category-item"
              :class="{ active: activeCategory === category.id }"
              @tap="switchCategory(category.id)"
            >
              <text class="category-text">{{ category.name }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
      
      <!-- 热门趋势 -->
      <view class="trends-section">
        <view class="section-header">
          <text class="section-title">🔥 热门趋势</text>
          <text class="refresh-btn" @tap="refreshTrends">刷新</text>
        </view>
        
        <view class="trends-list">
          <view 
            v-for="(trend, index) in filteredTrends" 
            :key="index"
            class="trend-item"
            @tap="viewTrend(trend)"
          >
            <view class="trend-rank">
              <text class="rank-number">{{ index + 1 }}</text>
            </view>
            <view class="trend-content">
              <view class="trend-header">
                <text class="trend-title">{{ trend.title }}</text>
                <view class="trend-badge" :class="trend.status">
                  <text class="badge-text">{{ trend.statusText }}</text>
                </view>
              </view>
              <text class="trend-desc">{{ trend.description }}</text>
              <view class="trend-stats">
                <text class="stat-item">🔥 {{ trend.heat }}</text>
                <text class="stat-item">💬 {{ trend.discussions }}</text>
                <text class="stat-item">📈 {{ trend.growth }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 趋势图表 -->
      <view class="chart-section">
        <text class="section-title">📊 趋势分析</text>
        <view class="chart-container">
          <view class="chart-placeholder">
            <text class="chart-text">趋势图表</text>
            <text class="chart-subtitle">{{ activeCategory }} 类别趋势变化</text>
            <!-- 这里可以集成图表库 -->
            <view class="mock-chart">
              <view 
                v-for="(bar, index) in chartData" 
                :key="index"
                class="chart-bar"
                :style="{ height: bar + '%' }"
              ></view>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 相关话题 -->
      <view class="topics-section">
        <text class="section-title">💭 相关话题</text>
        <view class="topics-grid">
          <view 
            v-for="(topic, index) in relatedTopics" 
            :key="index"
            class="topic-item"
            @tap="searchTopic(topic)"
          >
            <text class="topic-emoji">{{ topic.emoji }}</text>
            <text class="topic-name">{{ topic.name }}</text>
            <text class="topic-count">{{ topic.count }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'Trends',
  data() {
    return {
      activeCategory: 'fashion',
      categories: [
        { id: 'fashion', name: '时尚' },
        { id: 'beauty', name: '美妆' },
        { id: 'lifestyle', name: '生活' },
        { id: 'travel', name: '旅行' },
        { id: 'food', name: '美食' },
        { id: 'tech', name: '科技' }
      ],
      allTrends: {
        fashion: [
          {
            title: '复古风回潮',
            description: '90年代复古风格重新流行，复古单品成为时尚焦点',
            heat: '98.5k',
            discussions: '12.3k',
            growth: '+25%',
            status: 'hot',
            statusText: '热门',
            category: 'fashion'
          },
          {
            title: '可持续时尚',
            description: '环保材料和可持续生产方式受到更多关注',
            heat: '76.2k',
            discussions: '8.9k',
            growth: '+18%',
            status: 'rising',
            statusText: '上升',
            category: 'fashion'
          },
          {
            title: '极简主义穿搭',
            description: '简约而不简单的穿搭风格持续受到青睐',
            heat: '65.8k',
            discussions: '7.1k',
            growth: '+12%',
            status: 'stable',
            statusText: '稳定',
            category: 'fashion'
          }
        ],
        beauty: [
          {
            title: '自然妆容',
            description: '强调自然美感的妆容风格成为主流',
            heat: '89.3k',
            discussions: '15.6k',
            growth: '+22%',
            status: 'hot',
            statusText: '热门',
            category: 'beauty'
          },
          {
            title: '护肤极简化',
            description: '简化护肤步骤，注重产品质量而非数量',
            heat: '72.1k',
            discussions: '9.8k',
            growth: '+16%',
            status: 'rising',
            statusText: '上升',
            category: 'beauty'
          }
        ],
        lifestyle: [
          {
            title: '居家办公美学',
            description: '打造舒适高效的居家办公环境',
            heat: '94.7k',
            discussions: '11.2k',
            growth: '+28%',
            status: 'hot',
            statusText: '热门',
            category: 'lifestyle'
          }
        ]
      },
      chartData: [60, 80, 45, 90, 75, 65, 85],
      relatedTopics: [
        { emoji: '👗', name: '春季穿搭', count: '2.3k' },
        { emoji: '💄', name: '妆容教程', count: '1.8k' },
        { emoji: '👠', name: '鞋履搭配', count: '1.5k' },
        { emoji: '💍', name: '配饰选择', count: '1.2k' },
        { emoji: '🎨', name: '色彩搭配', count: '1.1k' },
        { emoji: '📷', name: '拍照技巧', count: '0.9k' }
      ]
    }
  },
  
  computed: {
    filteredTrends() {
      return this.allTrends[this.activeCategory] || []
    }
  },
  
  onLoad() {
    this.loadTrends()
  },
  
  methods: {
    switchCategory(categoryId) {
      this.activeCategory = categoryId
      this.loadTrends()
    },
    
    loadTrends() {
      // 模拟加载趋势数据
      uni.showLoading({
        title: '加载中...'
      })
      
      setTimeout(() => {
        uni.hideLoading()
        // 更新图表数据
        this.chartData = Array.from({ length: 7 }, () => Math.floor(Math.random() * 80) + 20)
      }, 500)
    },
    
    refreshTrends() {
      uni.showToast({
        title: '刷新趋势数据',
        icon: 'none'
      })
      this.loadTrends()
    },
    
    viewTrend(trend) {
      uni.showModal({
        title: trend.title,
        content: trend.description,
        showCancel: false
      })
    },
    
    searchTopic(topic) {
      uni.showToast({
        title: `搜索: ${topic.name}`,
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.trends-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 30rpx;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.subtitle {
  display: block;
  font-size: 26rpx;
  color: #666;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.category-section {
  background: white;
  border-radius: 20rpx;
  padding: 20rpx 0;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.category-scroll {
  white-space: nowrap;
}

.category-list {
  display: flex;
  padding: 0 30rpx;
  gap: 20rpx;
}

.category-item {
  flex-shrink: 0;
  padding: 15rpx 30rpx;
  border-radius: 30rpx;
  background: #f8f8f8;
  transition: all 0.3s ease;
}

.category-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.category-text {
  font-size: 26rpx;
  color: #666;
}

.category-item.active .category-text {
  color: white;
}

.trends-section,
.chart-section,
.topics-section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.refresh-btn {
  font-size: 26rpx;
  color: #667eea;
  padding: 10rpx 20rpx;
  border-radius: 20rpx;
  background: #f0f2ff;
}

.trends-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.trend-item {
  display: flex;
  padding: 25rpx;
  background: #f8f8f8;
  border-radius: 15rpx;
  transition: all 0.3s ease;
}

.trend-item:active {
  opacity: 0.8;
  transform: scale(0.98);
}

.trend-rank {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.rank-number {
  font-size: 24rpx;
  color: white;
  font-weight: bold;
}

.trend-content {
  flex: 1;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.trend-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.trend-badge {
  padding: 5rpx 15rpx;
  border-radius: 15rpx;
  font-size: 20rpx;
}

.trend-badge.hot {
  background: #ff5722;
}

.trend-badge.rising {
  background: #4caf50;
}

.trend-badge.stable {
  background: #2196f3;
}

.badge-text {
  color: white;
  font-size: 20rpx;
}

.trend-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.4;
  margin-bottom: 15rpx;
}

.trend-stats {
  display: flex;
  gap: 30rpx;
}

.stat-item {
  font-size: 24rpx;
  color: #999;
}

.chart-container {
  background: #f8f8f8;
  border-radius: 15rpx;
  padding: 30rpx;
  text-align: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-text {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
}

.chart-subtitle {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 30rpx;
}

.mock-chart {
  display: flex;
  align-items: end;
  justify-content: center;
  gap: 10rpx;
  height: 200rpx;
  width: 100%;
}

.chart-bar {
  width: 30rpx;
  background: linear-gradient(to top, #667eea, #764ba2);
  border-radius: 5rpx 5rpx 0 0;
  transition: height 0.5s ease;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
}

.topic-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 25rpx 15rpx;
  background: #f8f8f8;
  border-radius: 15rpx;
  transition: all 0.3s ease;
}

.topic-item:active {
  opacity: 0.8;
  transform: scale(0.95);
}

.topic-emoji {
  font-size: 40rpx;
  margin-bottom: 10rpx;
}

.topic-name {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 5rpx;
  text-align: center;
}

.topic-count {
  font-size: 22rpx;
  color: #999;
}
</style>