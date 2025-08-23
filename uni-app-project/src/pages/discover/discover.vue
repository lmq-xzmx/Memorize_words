<template>
  <view class="discover-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">🔍 发现</text>
      <text class="page-subtitle">探索精彩内容</text>
    </view>

    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <text class="search-icon">🔍</text>
        <input 
          class="search-input" 
          placeholder="搜索感兴趣的内容..."
          v-model="searchKeyword"
          @input="handleSearch"
        />
      </view>
    </view>

    <!-- 热门标签 -->
    <view class="tags-section">
      <text class="section-title">🔥 热门标签</text>
      <view class="tags-container">
        <view 
          v-for="tag in hotTags" 
          :key="tag.id"
          class="tag-item"
          :class="{ 'active': selectedTag === tag.id }"
          @click="selectTag(tag)"
        >
          <text class="tag-text">{{ tag.name }}</text>
        </view>
      </view>
    </view>

    <!-- 内容列表 -->
    <view class="content-section">
      <text class="section-title">📱 推荐内容</text>
      
      <view class="content-list">
        <view 
          v-for="item in contentList" 
          :key="item.id"
          class="content-card"
          @click="viewContent(item)"
        >
          <image 
            class="content-image" 
            :src="item.image || '/static/default-content.png'"
            mode="aspectFill"
          />
          
          <view class="content-info">
            <text class="content-title">{{ item.title }}</text>
            <text class="content-description">{{ item.description }}</text>
            
            <view class="content-meta">
              <view class="meta-item">
                <text class="meta-icon">👤</text>
                <text class="meta-text">{{ item.author }}</text>
              </view>
              
              <view class="meta-item">
                <text class="meta-icon">❤️</text>
                <text class="meta-text">{{ item.likes }}</text>
              </view>
              
              <view class="meta-item">
                <text class="meta-icon">💬</text>
                <text class="meta-text">{{ item.comments }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 加载更多 -->
    <view class="load-more" v-if="hasMore">
      <button class="load-more-btn" @click="loadMore" :loading="loading">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </view>
  </view>
</template>

<script>
export default {
  name: 'Discover',
  data() {
    return {
      searchKeyword: '',
      selectedTag: null,
      loading: false,
      hasMore: true,
      
      // 热门标签
      hotTags: [
        { id: 1, name: '英语学习' },
        { id: 2, name: '单词记忆' },
        { id: 3, name: '口语练习' },
        { id: 4, name: '语法技巧' },
        { id: 5, name: '考试备考' },
        { id: 6, name: '学习方法' }
      ],
      
      // 内容列表
      contentList: [
        {
          id: 1,
          title: '高效记忆单词的5个技巧',
          description: '科学的记忆方法让你事半功倍，快速掌握更多词汇...',
          image: '/static/content1.jpg',
          author: '英语达人',
          likes: 128,
          comments: 32,
          category: '学习方法'
        },
        {
          id: 2,
          title: '如何通过阅读提升词汇量',
          description: '阅读是扩大词汇量最自然的方式，这里有一些实用建议...',
          image: '/static/content2.jpg',
          author: '阅读专家',
          likes: 95,
          comments: 18,
          category: '阅读技巧'
        },
        {
          id: 3,
          title: '词根词缀记忆法详解',
          description: '掌握词根词缀，让你见到生词也能猜出大概意思...',
          image: '/static/content3.jpg',
          author: '词汇老师',
          likes: 156,
          comments: 45,
          category: '记忆技巧'
        },
        {
          id: 4,
          title: '英语口语中的高频词汇',
          description: '这些词汇在日常对话中出现频率最高，必须掌握...',
          image: '/static/content4.jpg',
          author: '口语教练',
          likes: 203,
          comments: 67,
          category: '口语练习'
        }
      ]
    }
  },
  
  onLoad() {
    this.loadContent()
  },
  
  methods: {
    /**
     * 加载内容
     */
    loadContent() {
      console.log('加载发现内容...')
    },
    
    /**
     * 处理搜索
     */
    handleSearch() {
      console.log('搜索关键词:', this.searchKeyword)
      // 实现搜索逻辑
    },
    
    /**
     * 选择标签
     */
    selectTag(tag) {
      this.selectedTag = this.selectedTag === tag.id ? null : tag.id
      console.log('选择标签:', tag.name)
      // 根据标签筛选内容
    },
    
    /**
     * 查看内容详情
     */
    viewContent(item) {
      console.log('查看内容:', item.title)
      uni.navigateTo({
        url: `/pages/content-detail/content-detail?id=${item.id}`,
        fail: () => {
          uni.showToast({
            title: '内容详情页开发中...',
            icon: 'none'
          })
        }
      })
    },
    
    /**
     * 加载更多
     */
    loadMore() {
      if (this.loading) return
      
      this.loading = true
      
      // 模拟加载
      setTimeout(() => {
        this.loading = false
        // 这里可以添加更多内容到 contentList
        console.log('加载更多内容...')
      }, 1500)
    }
  }
}
</script>

<style scoped>
.discover-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 32rpx 200rpx;
}

.page-header {
  text-align: center;
  margin-bottom: 40rpx;
  
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

.search-section {
  margin-bottom: 40rpx;
  
  .search-bar {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 50rpx;
    padding: 24rpx 32rpx;
    display: flex;
    align-items: center;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    .search-icon {
      font-size: 32rpx;
      margin-right: 16rpx;
      color: #666666;
    }
    
    .search-input {
      flex: 1;
      font-size: 28rpx;
      color: #333333;
      
      &::placeholder {
        color: #999999;
      }
    }
  }
}

.tags-section {
  margin-bottom: 40rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 16rpx;
    
    .tag-item {
      background: rgba(255, 255, 255, 0.2);
      border: 2rpx solid rgba(255, 255, 255, 0.3);
      border-radius: 32rpx;
      padding: 12rpx 24rpx;
      transition: all 0.3s ease;
      
      &.active {
        background: rgba(255, 255, 255, 0.95);
        border-color: #ffffff;
        
        .tag-text {
          color: #333333;
        }
      }
      
      .tag-text {
        font-size: 24rpx;
        color: #ffffff;
        transition: color 0.3s ease;
      }
    }
  }
}

.content-section {
  margin-bottom: 40rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 24rpx;
  }
  
  .content-list {
    .content-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      margin-bottom: 24rpx;
      overflow: hidden;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      
      &:active {
        transform: scale(0.98);
      }
      
      .content-image {
        width: 100%;
        height: 300rpx;
        background: #f5f5f5;
      }
      
      .content-info {
        padding: 24rpx;
        
        .content-title {
          display: block;
          font-size: 32rpx;
          font-weight: bold;
          color: #333333;
          margin-bottom: 12rpx;
          line-height: 1.4;
        }
        
        .content-description {
          display: block;
          font-size: 26rpx;
          color: #666666;
          line-height: 1.5;
          margin-bottom: 20rpx;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }
        
        .content-meta {
          display: flex;
          align-items: center;
          gap: 32rpx;
          
          .meta-item {
            display: flex;
            align-items: center;
            
            .meta-icon {
              font-size: 24rpx;
              margin-right: 8rpx;
            }
            
            .meta-text {
              font-size: 22rpx;
              color: #999999;
            }
          }
        }
      }
    }
  }
}

.load-more {
  text-align: center;
  
  .load-more-btn {
    background: rgba(255, 255, 255, 0.95);
    color: #333333;
    border: none;
    border-radius: 50rpx;
    padding: 24rpx 48rpx;
    font-size: 28rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    &:active {
      transform: scale(0.95);
    }
  }
}
</style>