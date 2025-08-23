<template>
  <view class="trends-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">📈 趋势</text>
      <text class="page-subtitle">发现最新学习趋势</text>
    </view>

    <!-- 趋势分类 -->
    <view class="trend-categories">
      <scroll-view scroll-x="true" class="category-scroll">
        <view class="category-list">
          <view 
            v-for="(category, index) in categories" 
            :key="index"
            class="category-item"
            :class="{ 'active': activeCategory === index }"
            @click="switchCategory(index)"
          >
            <text class="category-text">{{ category.name }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 趋势内容 -->
    <view class="trends-content">
      <!-- 热门话题 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">🔥 热门话题</text>
          <text class="section-more">查看更多</text>
        </view>
        
        <view class="hot-topics">
          <view 
            v-for="topic in hotTopics" 
            :key="topic.id"
            class="topic-card"
            @click="viewTopic(topic)"
          >
            <view class="topic-rank">
              <text class="rank-number">{{ topic.rank }}</text>
            </view>
            
            <view class="topic-info">
              <text class="topic-title">{{ topic.title }}</text>
              <text class="topic-stats">{{ topic.discussions }}讨论 · {{ topic.participants }}人参与</text>
            </view>
            
            <view class="topic-trend">
              <text class="trend-icon" :class="topic.trend">{{ getTrendIcon(topic.trend) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 学习统计 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">📊 学习统计</text>
        </view>
        
        <view class="stats-grid">
          <view 
            v-for="stat in learningStats" 
            :key="stat.id"
            class="stat-card"
          >
            <text class="stat-icon">{{ stat.icon }}</text>
            <text class="stat-value">{{ stat.value }}</text>
            <text class="stat-label">{{ stat.label }}</text>
            <view class="stat-change" :class="stat.changeType">
              <text class="change-text">{{ stat.change }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 推荐内容 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">💡 推荐内容</text>
        </view>
        
        <view class="recommended-list">
          <view 
            v-for="item in recommendedItems" 
            :key="item.id"
            class="recommended-card"
            @click="viewRecommended(item)"
          >
            <image class="recommended-image" :src="item.image" mode="aspectFill"></image>
            
            <view class="recommended-content">
              <text class="recommended-title">{{ item.title }}</text>
              <text class="recommended-description">{{ item.description }}</text>
              
              <view class="recommended-meta">
                <text class="meta-author">{{ item.author }}</text>
                <text class="meta-time">{{ item.time }}</text>
                <text class="meta-likes">❤️ {{ item.likes }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      activeCategory: 0,
      categories: [
        { name: '全部', id: 'all' },
        { name: '单词学习', id: 'vocabulary' },
        { name: '语法练习', id: 'grammar' },
        { name: '听力训练', id: 'listening' },
        { name: '口语练习', id: 'speaking' },
        { name: '阅读理解', id: 'reading' }
      ],
      
      hotTopics: [
        {
          id: 1,
          rank: 1,
          title: '高效记忆单词的5个技巧',
          discussions: 1234,
          participants: 567,
          trend: 'up'
        },
        {
          id: 2,
          rank: 2,
          title: '如何快速提升英语听力',
          discussions: 987,
          participants: 432,
          trend: 'up'
        },
        {
          id: 3,
          rank: 3,
          title: '零基础语法入门指南',
          discussions: 756,
          participants: 298,
          trend: 'down'
        },
        {
          id: 4,
          rank: 4,
          title: '口语练习最佳时间安排',
          discussions: 543,
          participants: 187,
          trend: 'stable'
        }
      ],
      
      learningStats: [
        {
          id: 1,
          icon: '📚',
          value: '2.3万',
          label: '今日学习人数',
          change: '+12%',
          changeType: 'positive'
        },
        {
          id: 2,
          icon: '⏰',
          value: '45分钟',
          label: '平均学习时长',
          change: '+5分钟',
          changeType: 'positive'
        },
        {
          id: 3,
          icon: '🎯',
          value: '87%',
          label: '目标完成率',
          change: '-3%',
          changeType: 'negative'
        },
        {
          id: 4,
          icon: '🏆',
          value: '156',
          label: '新增成就',
          change: '+23',
          changeType: 'positive'
        }
      ],
      
      recommendedItems: [
        {
          id: 1,
          title: '英语学习的黄金时间段',
          description: '科学研究表明，这些时间段学习效果最佳...',
          image: '/static/images/trend1.jpg',
          author: '学习专家',
          time: '2小时前',
          likes: 234
        },
        {
          id: 2,
          title: '单词记忆法大比拼',
          description: '对比5种主流记忆方法的优缺点...',
          image: '/static/images/trend2.jpg',
          author: '记忆大师',
          time: '4小时前',
          likes: 189
        },
        {
          id: 3,
          title: '如何制定个人学习计划',
          description: '根据自己的情况制定最适合的学习计划...',
          image: '/static/images/trend3.jpg',
          author: '规划师',
          time: '6小时前',
          likes: 156
        }
      ]
    }
  },
  
  onLoad() {
    this.loadTrendsData()
  },
  
  methods: {
    /**
     * 切换分类
     */
    switchCategory(index) {
      this.activeCategory = index
      this.loadTrendsData()
    },
    
    /**
     * 加载趋势数据
     */
    loadTrendsData() {
      // 模拟数据加载
      console.log('加载趋势数据:', this.categories[this.activeCategory].name)
    },
    
    /**
     * 查看话题详情
     */
    viewTopic(topic) {
      console.log('查看话题:', topic.title)
      uni.showToast({
        title: '话题详情页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 查看推荐内容
     */
    viewRecommended(item) {
      console.log('查看推荐内容:', item.title)
      uni.showToast({
        title: '内容详情页面开发中...',
        icon: 'none'
      })
    },
    
    /**
     * 获取趋势图标
     */
    getTrendIcon(trend) {
      switch (trend) {
        case 'up': return '📈'
        case 'down': return '📉'
        case 'stable': return '➡️'
        default: return '➡️'
      }
    }
  }
}
</script>

<style scoped>
.trends-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 200rpx;
}

.page-header {
  text-align: center;
  padding: 60rpx 32rpx 40rpx;
  
  .page-title {
    display: block;
    font-size: 56rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 16rpx;
  }
  
  .page-subtitle {
    display: block;
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}

.trend-categories {
  margin-bottom: 32rpx;
  
  .category-scroll {
    white-space: nowrap;
    
    .category-list {
      display: flex;
      padding: 0 32rpx;
      
      .category-item {
        flex-shrink: 0;
        padding: 16rpx 32rpx;
        margin-right: 16rpx;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 32rpx;
        transition: all 0.3s ease;
        
        &.active {
          background: rgba(255, 255, 255, 0.9);
          
          .category-text {
            color: #333333;
          }
        }
        
        .category-text {
          font-size: 28rpx;
          color: #ffffff;
          white-space: nowrap;
        }
      }
    }
  }
}

.trends-content {
  padding: 0 32rpx;
  
  .section {
    margin-bottom: 48rpx;
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24rpx;
      
      .section-title {
        font-size: 32rpx;
        font-weight: bold;
        color: #ffffff;
      }
      
      .section-more {
        font-size: 24rpx;
        color: rgba(255, 255, 255, 0.7);
      }
    }
  }
}

.hot-topics {
  .topic-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 16rpx;
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    &:active {
      transform: scale(0.98);
    }
    
    .topic-rank {
      width: 60rpx;
      height: 60rpx;
      background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 24rpx;
      
      .rank-number {
        font-size: 24rpx;
        font-weight: bold;
        color: #ffffff;
      }
    }
    
    .topic-info {
      flex: 1;
      
      .topic-title {
        display: block;
        font-size: 30rpx;
        font-weight: bold;
        color: #333333;
        margin-bottom: 8rpx;
      }
      
      .topic-stats {
        display: block;
        font-size: 24rpx;
        color: #666666;
      }
    }
    
    .topic-trend {
      .trend-icon {
        font-size: 32rpx;
        
        &.up {
          color: #52c41a;
        }
        
        &.down {
          color: #ff4d4f;
        }
        
        &.stable {
          color: #faad14;
        }
      }
    }
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  
  .stat-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    padding: 32rpx 24rpx;
    text-align: center;
    position: relative;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    .stat-icon {
      display: block;
      font-size: 40rpx;
      margin-bottom: 12rpx;
    }
    
    .stat-value {
      display: block;
      font-size: 36rpx;
      font-weight: bold;
      color: #333333;
      margin-bottom: 8rpx;
    }
    
    .stat-label {
      display: block;
      font-size: 24rpx;
      color: #666666;
      margin-bottom: 12rpx;
    }
    
    .stat-change {
      position: absolute;
      top: 16rpx;
      right: 16rpx;
      padding: 4rpx 8rpx;
      border-radius: 8rpx;
      
      &.positive {
        background: #f6ffed;
        
        .change-text {
          color: #52c41a;
        }
      }
      
      &.negative {
        background: #fff2f0;
        
        .change-text {
          color: #ff4d4f;
        }
      }
      
      .change-text {
        font-size: 20rpx;
        font-weight: bold;
      }
    }
  }
}

.recommended-list {
  .recommended-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    margin-bottom: 16rpx;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    &:active {
      transform: scale(0.98);
    }
    
    .recommended-image {
      width: 100%;
      height: 300rpx;
    }
    
    .recommended-content {
      padding: 24rpx;
      
      .recommended-title {
        display: block;
        font-size: 32rpx;
        font-weight: bold;
        color: #333333;
        margin-bottom: 12rpx;
        line-height: 1.4;
      }
      
      .recommended-description {
        display: block;
        font-size: 26rpx;
        color: #666666;
        line-height: 1.5;
        margin-bottom: 16rpx;
      }
      
      .recommended-meta {
        display: flex;
        align-items: center;
        font-size: 22rpx;
        color: #999999;
        
        .meta-author {
          margin-right: 16rpx;
        }
        
        .meta-time {
          margin-right: 16rpx;
        }
        
        .meta-likes {
          margin-left: auto;
        }
      }
    }
  }
}
</style>