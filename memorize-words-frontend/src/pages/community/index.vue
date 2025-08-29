<template>
  <view class="community-page">
    <view class="header">
      <text class="title">👥 社区</text>
      <text class="subtitle">分享交流，共同成长</text>
    </view>
    
    <view class="content">
      <!-- 社区导航 -->
      <view class="nav-section">
        <scroll-view class="nav-scroll" scroll-x>
          <view class="nav-list">
            <view 
              v-for="(nav, index) in navItems" 
              :key="index"
              class="nav-item"
              :class="{ active: activeNav === nav.id }"
              @tap="switchNav(nav.id)"
            >
              <text class="nav-emoji">{{ nav.emoji }}</text>
              <text class="nav-text">{{ nav.name }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
      
      <!-- 发布按钮 -->
      <view class="publish-section">
        <view class="publish-btn" @tap="showPublishModal">
          <text class="publish-icon">✏️</text>
          <text class="publish-text">分享你的想法...</text>
        </view>
      </view>
      
      <!-- 热门话题 -->
      <view class="topics-section">
        <text class="section-title">🔥 热门话题</text>
        <view class="topics-list">
          <view 
            v-for="(topic, index) in hotTopics" 
            :key="index"
            class="topic-tag"
            @tap="searchTopic(topic)"
          >
            <text class="topic-text">#{{ topic.name }}</text>
            <text class="topic-count">{{ topic.count }}</text>
          </view>
        </view>
      </view>
      
      <!-- 社区动态 -->
      <view class="posts-section">
        <view class="section-header">
          <text class="section-title">📝 最新动态</text>
          <view class="filter-btns">
            <text 
              class="filter-btn"
              :class="{ active: postFilter === 'latest' }"
              @tap="setPostFilter('latest')"
            >最新</text>
            <text 
              class="filter-btn"
              :class="{ active: postFilter === 'hot' }"
              @tap="setPostFilter('hot')"
            >热门</text>
          </view>
        </view>
        
        <view class="posts-list">
          <view 
            v-for="(post, index) in filteredPosts" 
            :key="index"
            class="post-item"
            @tap="viewPost(post)"
          >
            <view class="post-header">
              <view class="user-info">
                <view class="user-avatar">
                  <text class="avatar-text">{{ post.user.name.charAt(0) }}</text>
                </view>
                <view class="user-details">
                  <text class="user-name">{{ post.user.name }}</text>
                  <text class="post-time">{{ post.time }}</text>
                </view>
              </view>
              <view class="post-category">
                <text class="category-text">{{ post.category }}</text>
              </view>
            </view>
            
            <view class="post-content">
              <text class="post-title">{{ post.title }}</text>
              <text class="post-text">{{ post.content }}</text>
              
              <view v-if="post.images && post.images.length" class="post-images">
                <view 
                  v-for="(image, imgIndex) in post.images" 
                  :key="imgIndex"
                  class="image-placeholder"
                >
                  <text class="image-emoji">{{ image }}</text>
                </view>
              </view>
            </view>
            
            <view class="post-actions">
              <view class="action-item" @tap.stop="likePost(post)">
                <text class="action-icon">{{ post.isLiked ? '❤️' : '🤍' }}</text>
                <text class="action-text">{{ post.likes }}</text>
              </view>
              <view class="action-item" @tap.stop="commentPost(post)">
                <text class="action-icon">💬</text>
                <text class="action-text">{{ post.comments }}</text>
              </view>
              <view class="action-item" @tap.stop="sharePost(post)">
                <text class="action-icon">🔗</text>
                <text class="action-text">分享</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 发布弹窗 -->
    <view v-if="showPublish" class="publish-modal" @tap="hidePublishModal">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">发布动态</text>
          <text class="close-btn" @tap="hidePublishModal">✕</text>
        </view>
        <view class="modal-body">
          <textarea 
            class="publish-textarea" 
            v-model="publishContent" 
            placeholder="分享你的想法..."
            maxlength="500"
          ></textarea>
          <view class="publish-tools">
            <view class="tool-item" @tap="addEmoji">
              <text class="tool-icon">😊</text>
              <text class="tool-text">表情</text>
            </view>
            <view class="tool-item" @tap="addImage">
              <text class="tool-icon">📷</text>
              <text class="tool-text">图片</text>
            </view>
            <view class="tool-item" @tap="addTopic">
              <text class="tool-icon">#</text>
              <text class="tool-text">话题</text>
            </view>
          </view>
        </view>
        <view class="modal-footer">
          <button class="cancel-btn" @tap="hidePublishModal">取消</button>
          <button class="publish-submit-btn" @tap="submitPost" :disabled="!publishContent.trim()">发布</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'Community',
  data() {
    return {
      activeNav: 'all',
      postFilter: 'latest',
      showPublish: false,
      publishContent: '',
      navItems: [
        { id: 'all', emoji: '🌟', name: '全部' },
        { id: 'fashion', emoji: '👗', name: '时尚' },
        { id: 'beauty', emoji: '💄', name: '美妆' },
        { id: 'lifestyle', emoji: '🌸', name: '生活' },
        { id: 'travel', emoji: '✈️', name: '旅行' },
        { id: 'food', emoji: '🍰', name: '美食' }
      ],
      hotTopics: [
        { name: '春季穿搭', count: '2.3k' },
        { name: '护肤心得', count: '1.8k' },
        { name: '旅行攻略', count: '1.5k' },
        { name: '美食分享', count: '1.2k' },
        { name: '生活美学', count: '1.1k' }
      ],
      posts: [
        {
          id: 1,
          user: { name: '时尚达人小美', avatar: '' },
          time: '2小时前',
          category: '时尚',
          title: '春季必备单品推荐',
          content: '分享几件春季必备的时尚单品，让你轻松穿出时尚感！这些单品不仅实用，而且搭配性很强...',
          images: ['👗', '👠', '👜'],
          likes: 128,
          comments: 23,
          isLiked: false,
          type: 'hot'
        },
        {
          id: 2,
          user: { name: '美妆博主Lisa', avatar: '' },
          time: '4小时前',
          category: '美妆',
          title: '自然妆容教程',
          content: '今天分享一个超简单的自然妆容教程，适合日常上班或约会，只需要几个步骤就能完成...',
          images: ['💄', '🎨'],
          likes: 89,
          comments: 15,
          isLiked: true,
          type: 'latest'
        },
        {
          id: 3,
          user: { name: '生活家小王', avatar: '' },
          time: '6小时前',
          category: '生活',
          title: '居家收纳小技巧',
          content: '分享一些实用的居家收纳技巧，让你的家变得更加整洁有序，生活质量瞬间提升！',
          images: ['🏠', '📦'],
          likes: 67,
          comments: 12,
          isLiked: false,
          type: 'latest'
        },
        {
          id: 4,
          user: { name: '旅行者阿明', avatar: '' },
          time: '8小时前',
          category: '旅行',
          title: '樱花季京都游记',
          content: '刚从京都回来，樱花真的太美了！分享一些拍照技巧和必去的赏樱地点...',
          images: ['🌸', '📷', '🏯'],
          likes: 156,
          comments: 34,
          isLiked: false,
          type: 'hot'
        },
        {
          id: 5,
          user: { name: '美食家小张', avatar: '' },
          time: '1天前',
          category: '美食',
          title: '在家制作网红甜品',
          content: '教大家在家制作最近很火的网红甜品，材料简单，步骤详细，新手也能轻松上手！',
          images: ['🍰', '🧁'],
          likes: 92,
          comments: 18,
          isLiked: true,
          type: 'latest'
        }
      ]
    }
  },
  
  computed: {
    filteredPosts() {
      let posts = this.posts
      
      // 按导航筛选
      if (this.activeNav !== 'all') {
        posts = posts.filter(post => {
          const categoryMap = {
            'fashion': '时尚',
            'beauty': '美妆',
            'lifestyle': '生活',
            'travel': '旅行',
            'food': '美食'
          }
          return post.category === categoryMap[this.activeNav]
        })
      }
      
      // 按类型筛选
      if (this.postFilter === 'hot') {
        posts = posts.filter(post => post.type === 'hot')
      }
      
      return posts
    }
  },
  
  methods: {
    switchNav(navId) {
      this.activeNav = navId
    },
    
    setPostFilter(filter) {
      this.postFilter = filter
    },
    
    searchTopic(topic) {
      uni.showToast({
        title: `搜索话题: ${topic.name}`,
        icon: 'none'
      })
    },
    
    showPublishModal() {
      this.showPublish = true
    },
    
    hidePublishModal() {
      this.showPublish = false
      this.publishContent = ''
    },
    
    addEmoji() {
      this.publishContent += '😊'
    },
    
    addImage() {
      uni.showToast({
        title: '选择图片功能',
        icon: 'none'
      })
    },
    
    addTopic() {
      this.publishContent += '#话题 '
    },
    
    submitPost() {
      if (!this.publishContent.trim()) return
      
      uni.showToast({
        title: '发布成功！',
        icon: 'success'
      })
      
      // 添加新动态到列表
      const newPost = {
        id: Date.now(),
        user: { name: '我', avatar: '' },
        time: '刚刚',
        category: '生活',
        title: '',
        content: this.publishContent,
        images: [],
        likes: 0,
        comments: 0,
        isLiked: false,
        type: 'latest'
      }
      
      this.posts.unshift(newPost)
      this.hidePublishModal()
    },
    
    viewPost(post) {
      uni.showModal({
        title: post.title || '动态详情',
        content: post.content,
        showCancel: false
      })
    },
    
    likePost(post) {
      post.isLiked = !post.isLiked
      post.likes += post.isLiked ? 1 : -1
    },
    
    commentPost(post) {
      uni.showToast({
        title: '评论功能',
        icon: 'none'
      })
    },
    
    sharePost(post) {
      uni.showToast({
        title: '分享功能',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.community-page {
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

.nav-section {
  background: white;
  border-radius: 20rpx;
  padding: 20rpx 0;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.nav-scroll {
  white-space: nowrap;
}

.nav-list {
  display: flex;
  padding: 0 30rpx;
  gap: 20rpx;
}

.nav-item {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx;
  border-radius: 20rpx;
  transition: all 0.3s ease;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.nav-emoji {
  font-size: 32rpx;
  margin-bottom: 8rpx;
}

.nav-text {
  font-size: 24rpx;
  color: #666;
}

.nav-item.active .nav-text {
  color: white;
}

.publish-section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.1);
}

.publish-btn {
  display: flex;
  align-items: center;
  padding: 25rpx;
  background: #f8f8f8;
  border-radius: 50rpx;
  transition: all 0.3s ease;
}

.publish-btn:active {
  opacity: 0.8;
}

.publish-icon {
  font-size: 28rpx;
  margin-right: 20rpx;
}

.publish-text {
  font-size: 28rpx;
  color: #999;
}

.topics-section,
.posts-section {
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.filter-btns {
  display: flex;
  gap: 20rpx;
}

.filter-btn {
  font-size: 26rpx;
  color: #666;
  padding: 10rpx 20rpx;
  border-radius: 20rpx;
  background: #f8f8f8;
}

.filter-btn.active {
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.topics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15rpx;
}

.topic-tag {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 15rpx 25rpx;
  background: #f8f8f8;
  border-radius: 30rpx;
  transition: all 0.3s ease;
}

.topic-tag:active {
  opacity: 0.8;
}

.topic-text {
  font-size: 26rpx;
  color: #333;
}

.topic-count {
  font-size: 22rpx;
  color: #999;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.post-item {
  padding: 30rpx;
  background: #f8f8f8;
  border-radius: 20rpx;
  transition: all 0.3s ease;
}

.post-item:active {
  opacity: 0.9;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.avatar-text {
  font-size: 24rpx;
  color: white;
  font-weight: bold;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.post-time {
  font-size: 22rpx;
  color: #999;
}

.post-category {
  padding: 8rpx 16rpx;
  background: #e3f2fd;
  border-radius: 15rpx;
}

.category-text {
  font-size: 22rpx;
  color: #1976d2;
}

.post-content {
  margin-bottom: 25rpx;
}

.post-title {
  display: block;
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 15rpx;
}

.post-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 20rpx;
}

.post-images {
  display: flex;
  gap: 15rpx;
  margin-bottom: 20rpx;
}

.image-placeholder {
  width: 120rpx;
  height: 120rpx;
  background: white;
  border-radius: 15rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-emoji {
  font-size: 60rpx;
}

.post-actions {
  display: flex;
  justify-content: space-around;
  padding-top: 20rpx;
  border-top: 1rpx solid #e0e0e0;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 15rpx;
  border-radius: 25rpx;
  transition: all 0.3s ease;
}

.action-item:active {
  background: #e0e0e0;
}

.action-icon {
  font-size: 24rpx;
}

.action-text {
  font-size: 24rpx;
  color: #666;
}

/* 发布弹窗样式 */
.publish-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 600rpx;
  background: white;
  border-radius: 20rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #e0e0e0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.close-btn {
  font-size: 32rpx;
  color: #999;
  padding: 10rpx;
}

.modal-body {
  padding: 30rpx;
}

.publish-textarea {
  width: 100%;
  min-height: 200rpx;
  padding: 20rpx;
  border: 1rpx solid #e0e0e0;
  border-radius: 15rpx;
  font-size: 28rpx;
  line-height: 1.5;
  margin-bottom: 30rpx;
}

.publish-tools {
  display: flex;
  gap: 30rpx;
}

.tool-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 20rpx;
  border-radius: 15rpx;
  background: #f8f8f8;
  transition: all 0.3s ease;
}

.tool-item:active {
  opacity: 0.8;
}

.tool-icon {
  font-size: 32rpx;
}

.tool-text {
  font-size: 22rpx;
  color: #666;
}

.modal-footer {
  display: flex;
  gap: 20rpx;
  padding: 30rpx;
  border-top: 1rpx solid #e0e0e0;
}

.cancel-btn,
.publish-submit-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.publish-submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.publish-submit-btn:disabled {
  opacity: 0.5;
}
</style>