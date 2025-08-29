<template>
  <view class="discover-page">
    <view class="header">
      <text class="title">🔍 发现</text>
      <text class="subtitle">探索精彩内容</text>
    </view>
    
    <view class="content">
      <!-- 搜索栏 -->
      <view class="search-section">
        <view class="search-box">
          <text class="search-icon">🔍</text>
          <input 
            class="search-input" 
            v-model="searchKeyword" 
            placeholder="搜索感兴趣的内容"
            @confirm="onSearch"
          />
        </view>
      </view>
      
      <!-- 热门标签 -->
      <view class="tags-section">
        <text class="section-title">热门标签</text>
        <view class="tags-container">
          <view 
            v-for="(tag, index) in hotTags" 
            :key="index"
            class="tag-item"
            @tap="searchByTag(tag)"
          >
            <text class="tag-text">{{ tag }}</text>
          </view>
        </view>
      </view>
      
      <!-- 推荐内容 -->
      <view class="recommend-section">
        <text class="section-title">为你推荐</text>
        <view class="content-list">
          <view 
            v-for="(item, index) in recommendList" 
            :key="index"
            class="content-item"
            @tap="viewContent(item)"
          >
            <view class="content-image">
              <text class="image-placeholder">{{ item.emoji }}</text>
            </view>
            <view class="content-info">
              <text class="content-title">{{ item.title }}</text>
              <text class="content-desc">{{ item.description }}</text>
              <view class="content-meta">
                <text class="meta-item">👁️ {{ item.views }}</text>
                <text class="meta-item">❤️ {{ item.likes }}</text>
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
  name: 'Discover',
  data() {
    return {
      searchKeyword: '',
      hotTags: ['时尚', '美妆', '穿搭', '生活', '旅行', '美食', '摄影', '艺术'],
      recommendList: [
        {
          id: 1,
          emoji: '👗',
          title: '春季穿搭指南',
          description: '2024年春季最新穿搭趋势，让你成为街头焦点',
          views: '1.2k',
          likes: '89'
        },
        {
          id: 2,
          emoji: '💄',
          title: '自然妆容教程',
          description: '简单几步打造清新自然的日常妆容',
          views: '856',
          likes: '67'
        },
        {
          id: 3,
          emoji: '📸',
          title: '手机摄影技巧',
          description: '用手机也能拍出专业级的照片',
          views: '2.1k',
          likes: '156'
        },
        {
          id: 4,
          emoji: '🌸',
          title: '樱花季旅行攻略',
          description: '最佳赏樱地点和拍照技巧分享',
          views: '3.4k',
          likes: '234'
        },
        {
          id: 5,
          emoji: '🎨',
          title: '色彩搭配艺术',
          description: '掌握色彩搭配的基本原理和实用技巧',
          views: '945',
          likes: '78'
        }
      ]
    }
  },
  methods: {
    onSearch() {
      if (!this.searchKeyword.trim()) {
        uni.showToast({
          title: '请输入搜索关键词',
          icon: 'none'
        })
        return
      }
      
      uni.showToast({
        title: `搜索: ${this.searchKeyword}`,
        icon: 'none'
      })
    },
    
    searchByTag(tag) {
      this.searchKeyword = tag
      this.onSearch()
    },
    
    viewContent(item) {
      uni.showToast({
        title: `查看: ${item.title}`,
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.discover-page {
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
  gap: 40rpx;
}

.search-section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.search-box {
  display: flex;
  align-items: center;
  background: #f8f8f8;
  border-radius: 50rpx;
  padding: 20rpx 30rpx;
}

.search-icon {
  font-size: 28rpx;
  margin-right: 20rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  border: none;
  background: transparent;
}

.tags-section,
.recommend-section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.tag-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 30rpx;
  padding: 15rpx 30rpx;
}

.tag-item:active {
  opacity: 0.8;
}

.tag-text {
  font-size: 26rpx;
  color: white;
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.content-item {
  display: flex;
  background: #f8f8f8;
  border-radius: 15rpx;
  padding: 20rpx;
}

.content-item:active {
  opacity: 0.8;
}

.content-image {
  width: 120rpx;
  height: 120rpx;
  background: white;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.image-placeholder {
  font-size: 60rpx;
}

.content-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.content-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.content-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.4;
  margin-bottom: 15rpx;
}

.content-meta {
  display: flex;
  gap: 30rpx;
}

.meta-item {
  font-size: 24rpx;
  color: #999;
}
</style>