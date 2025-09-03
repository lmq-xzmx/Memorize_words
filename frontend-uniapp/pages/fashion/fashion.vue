<template>
  <view class="fashion-container">
    <!-- 状态栏占位 -->
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 头部区域 -->
    <view class="header">
      <view class="header-content">
        <text class="header-title">时尚英语</text>
        <view class="header-subtitle">
          <text class="subtitle-text">潮流英语内容，让学习更有趣</text>
        </view>
      </view>
      <view class="header-actions">
        <view class="search-btn" @tap="openSearch">
          <text class="search-icon">🔍</text>
        </view>
        <view class="notification-btn" @tap="openNotification">
          <text class="notification-icon">🔔</text>
          <view class="notification-badge" v-if="unreadCount > 0">
            <text class="badge-text">{{ unreadCount > 99 ? '99+' : unreadCount }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 分类导航 -->
    <view class="category-nav">
      <scroll-view class="nav-scroll" scroll-x="true" show-scrollbar="false">
        <view class="nav-list">
          <view 
            class="nav-item" 
            v-for="category in categories" 
            :key="category.id"
            @tap="selectCategory(category)"
            :class="{ active: selectedCategory.id === category.id }"
          >
            <text class="nav-text">{{ category.name }}</text>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <!-- 轮播图 -->
    <view class="banner-section" v-if="banners.length > 0">
      <swiper 
        class="banner-swiper" 
        :indicator-dots="true" 
        :autoplay="true" 
        :interval="3000" 
        :duration="500"
        indicator-color="rgba(255, 255, 255, 0.5)"
        indicator-active-color="#ffffff"
      >
        <swiper-item v-for="banner in banners" :key="banner.id">
          <view class="banner-item" @tap="openBanner(banner)">
            <image class="banner-image" :src="banner.image" mode="aspectFill"></image>
            <view class="banner-overlay">
              <text class="banner-title">{{ banner.title }}</text>
              <text class="banner-desc">{{ banner.description }}</text>
            </view>
          </view>
        </swiper-item>
      </swiper>
    </view>
    
    <!-- 内容列表 -->
    <view class="content-section">
      <!-- 推荐内容 -->
      <view class="featured-content" v-if="featuredContent.length > 0">
        <view class="section-title">
          <text class="title-text">精选推荐</text>
          <text class="title-desc">编辑精选的优质内容</text>
        </view>
        <scroll-view class="featured-scroll" scroll-x="true" show-scrollbar="false">
          <view class="featured-list">
            <view 
              class="featured-item" 
              v-for="item in featuredContent" 
              :key="item.id"
              @tap="openContent(item)"
            >
              <image class="featured-image" :src="item.image" mode="aspectFill"></image>
              <view class="featured-content-info">
                <view class="featured-tag">
                  <text class="tag-text">{{ item.tag }}</text>
                </view>
                <text class="featured-title">{{ item.title }}</text>
                <text class="featured-desc">{{ item.description }}</text>
                <view class="featured-meta">
                  <text class="meta-item">{{ item.readTime }}</text>
                  <text class="meta-divider">•</text>
                  <text class="meta-item">{{ item.views }} 阅读</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
      
      <!-- 内容列表 -->
      <view class="content-list">
        <view class="section-title">
          <text class="title-text">{{ selectedCategory.name }}</text>
          <view class="filter-btn" @tap="showFilter">
            <text class="filter-icon">⚙️</text>
            <text class="filter-text">筛选</text>
          </view>
        </view>
        
        <view class="list-container">
          <view 
            class="content-item" 
            v-for="item in contentList" 
            :key="item.id"
            @tap="openContent(item)"
          >
            <image class="content-image" :src="item.image" mode="aspectFill"></image>
            <view class="content-info">
              <view class="content-header">
                <view class="content-tag">
                  <text class="tag-text">{{ item.tag }}</text>
                </view>
                <view class="content-level" :class="item.level">
                  <text class="level-text">{{ item.levelText }}</text>
                </view>
              </view>
              <text class="content-title">{{ item.title }}</text>
              <text class="content-desc">{{ item.description }}</text>
              <view class="content-meta">
                <view class="meta-left">
                  <text class="meta-item">{{ item.author }}</text>
                  <text class="meta-divider">•</text>
                  <text class="meta-item">{{ item.publishTime }}</text>
                </view>
                <view class="meta-right">
                  <view class="meta-stats">
                    <text class="stats-item">👁 {{ item.views }}</text>
                    <text class="stats-item">❤️ {{ item.likes }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 加载更多 -->
        <view class="load-more" v-if="hasMore">
          <view class="load-btn" @tap="loadMore" :class="{ loading: isLoading }">
            <text class="load-text">{{ isLoading ? '加载中...' : '加载更多' }}</text>
          </view>
        </view>
        
        <!-- 没有更多 -->
        <view class="no-more" v-if="!hasMore && contentList.length > 0">
          <text class="no-more-text">没有更多内容了</text>
        </view>
      </view>
    </view>
    
    <!-- 筛选弹窗 -->
    <view class="filter-overlay" v-if="showFilterModal" @tap="hideFilter">
      <view class="filter-modal" @tap.stop>
        <view class="filter-header">
          <text class="filter-title">内容筛选</text>
          <view class="close-btn" @tap="hideFilter">
            <text class="close-icon">×</text>
          </view>
        </view>
        <view class="filter-content">
          <view class="filter-section">
            <text class="filter-label">难度等级</text>
            <view class="filter-options">
              <view 
                class="filter-option" 
                v-for="level in levelOptions" 
                :key="level.value"
                @tap="selectLevel(level)"
                :class="{ active: selectedLevel === level.value }"
              >
                <text class="option-text">{{ level.label }}</text>
              </view>
            </view>
          </view>
          <view class="filter-section">
            <text class="filter-label">内容类型</text>
            <view class="filter-options">
              <view 
                class="filter-option" 
                v-for="type in typeOptions" 
                :key="type.value"
                @tap="selectType(type)"
                :class="{ active: selectedType === type.value }"
              >
                <text class="option-text">{{ type.label }}</text>
              </view>
            </view>
          </view>
        </view>
        <view class="filter-actions">
          <button class="filter-btn reset" @tap="resetFilter">重置</button>
          <button class="filter-btn confirm" @tap="applyFilter">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  import { mapState, mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Fashion',
    data() {
      return {
        unreadCount: 2,
        showFilterModal: false,
        isLoading: false,
        hasMore: true,
        selectedLevel: '',
        selectedType: '',
        
        categories: [
          { id: 1, name: '全部', value: 'all' },
          { id: 2, name: '热门话题', value: 'trending' },
          { id: 3, name: '英语新闻', value: 'news' },
          { id: 4, name: '影视英语', value: 'movies' },
          { id: 5, name: '音乐英语', value: 'music' },
          { id: 6, name: '旅游英语', value: 'travel' },
          { id: 7, name: '商务英语', value: 'business' },
          { id: 8, name: '生活英语', value: 'lifestyle' }
        ],
        
        selectedCategory: { id: 1, name: '全部', value: 'all' },
        
        banners: [
          {
            id: 1,
            title: '2024年度英语学习趋势',
            description: '了解最新的英语学习方法和趋势',
            image: '/static/images/banner1.jpg'
          },
          {
            id: 2,
            title: 'AI助力英语学习',
            description: '体验人工智能带来的学习革命',
            image: '/static/images/banner2.jpg'
          },
          {
            id: 3,
            title: '英语口语突破指南',
            description: '从零基础到流利表达的完整路径',
            image: '/static/images/banner3.jpg'
          }
        ],
        
        featuredContent: [
          {
            id: 1,
            title: 'ChatGPT时代的英语学习',
            description: '如何利用AI工具提升英语水平',
            image: '/static/images/featured1.jpg',
            tag: '科技',
            readTime: '5分钟',
            views: 1234
          },
          {
            id: 2,
            title: '英语电影中的经典台词',
            description: '从电影台词学习地道英语表达',
            image: '/static/images/featured2.jpg',
            tag: '影视',
            readTime: '8分钟',
            views: 2156
          },
          {
            id: 3,
            title: '商务英语邮件写作技巧',
            description: '职场必备的邮件沟通技能',
            image: '/static/images/featured3.jpg',
            tag: '商务',
            readTime: '6分钟',
            views: 987
          }
        ],
        
        contentList: [
          {
            id: 1,
            title: '英语学习的5个常见误区',
            description: '避开这些误区，让你的英语学习更高效',
            image: '/static/images/content1.jpg',
            tag: '学习方法',
            level: 'beginner',
            levelText: '初级',
            author: '英语老师Amy',
            publishTime: '2小时前',
            views: 856,
            likes: 42
          },
          {
            id: 2,
            title: '如何在30天内提升英语口语',
            description: '实用的口语练习方法和技巧分享',
            image: '/static/images/content2.jpg',
            tag: '口语练习',
            level: 'intermediate',
            levelText: '中级',
            author: '口语达人Tom',
            publishTime: '5小时前',
            views: 1203,
            likes: 78
          },
          {
            id: 3,
            title: '英语写作中的高级句型',
            description: '让你的英语写作更加地道和专业',
            image: '/static/images/content3.jpg',
            tag: '写作技巧',
            level: 'advanced',
            levelText: '高级',
            author: '写作专家Lisa',
            publishTime: '1天前',
            views: 654,
            likes: 35
          },
          {
            id: 4,
            title: '美剧中的实用英语表达',
            description: '从热门美剧学习地道的英语表达',
            image: '/static/images/content4.jpg',
            tag: '影视英语',
            level: 'intermediate',
            levelText: '中级',
            author: '美剧达人Jack',
            publishTime: '2天前',
            views: 2341,
            likes: 156
          }
        ],
        
        levelOptions: [
          { label: '全部', value: '' },
          { label: '初级', value: 'beginner' },
          { label: '中级', value: 'intermediate' },
          { label: '高级', value: 'advanced' }
        ],
        
        typeOptions: [
          { label: '全部', value: '' },
          { label: '学习方法', value: 'method' },
          { label: '口语练习', value: 'speaking' },
          { label: '写作技巧', value: 'writing' },
          { label: '影视英语', value: 'movies' },
          { label: '商务英语', value: 'business' }
        ]
      }
    },
    
    computed: {
      ...mapGetters('app', ['statusBarHeight'])
    },
    
    onLoad() {
      this.initPage()
    },
    
    onShow() {
      this.refreshData()
    },
    
    onPullDownRefresh() {
      this.refreshData().finally(() => {
        uni.stopPullDownRefresh()
      })
    },
    
    onReachBottom() {
      if (this.hasMore && !this.isLoading) {
        this.loadMore()
      }
    },
    
    methods: {
      ...mapActions('app', ['navigateTo', 'showToast', 'showLoading', 'hideLoading']),
      
      // 初始化页面
      initPage() {
        this.loadBanners()
        this.loadFeaturedContent()
        this.loadContentList()
      },
      
      // 刷新数据
      async refreshData() {
        try {
          await Promise.all([
            this.loadBanners(),
            this.loadFeaturedContent(),
            this.loadContentList(true)
          ])
        } catch (error) {
          console.error('刷新数据失败:', error)
        }
      },
      
      // 加载轮播图
      async loadBanners() {
        try {
          // 这里应该调用API加载轮播图数据
          console.log('加载轮播图')
        } catch (error) {
          console.error('加载轮播图失败:', error)
        }
      },
      
      // 加载精选内容
      async loadFeaturedContent() {
        try {
          // 这里应该调用API加载精选内容
          console.log('加载精选内容')
        } catch (error) {
          console.error('加载精选内容失败:', error)
        }
      },
      
      // 加载内容列表
      async loadContentList(refresh = false) {
        try {
          if (refresh) {
            this.contentList = []
            this.hasMore = true
          }
          
          // 这里应该调用API加载内容列表
          console.log('加载内容列表')
        } catch (error) {
          console.error('加载内容列表失败:', error)
        }
      },
      
      // 选择分类
      selectCategory(category) {
        this.selectedCategory = category
        this.loadContentList(true)
      },
      
      // 打开搜索
      openSearch() {
        this.navigateTo({
          url: '/pages/search/search?type=fashion'
        })
      },
      
      // 打开通知
      openNotification() {
        this.navigateTo({
          url: '/pages/notification/notification'
        })
      },
      
      // 打开轮播图
      openBanner(banner) {
        this.navigateTo({
          url: `/pages/content/content?id=${banner.id}&type=banner`
        })
      },
      
      // 打开内容
      openContent(content) {
        this.navigateTo({
          url: `/pages/content/content?id=${content.id}&type=article`
        })
      },
      
      // 加载更多
      async loadMore() {
        if (this.isLoading || !this.hasMore) return
        
        this.isLoading = true
        
        try {
          // 这里应该调用API加载更多内容
          await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟加载
          
          // 模拟没有更多数据
          if (this.contentList.length >= 20) {
            this.hasMore = false
          }
        } catch (error) {
          console.error('加载更多失败:', error)
          this.showToast({ title: '加载失败，请重试' })
        } finally {
          this.isLoading = false
        }
      },
      
      // 显示筛选
      showFilter() {
        this.showFilterModal = true
      },
      
      // 隐藏筛选
      hideFilter() {
        this.showFilterModal = false
      },
      
      // 选择难度
      selectLevel(level) {
        this.selectedLevel = level.value
      },
      
      // 选择类型
      selectType(type) {
        this.selectedType = type.value
      },
      
      // 重置筛选
      resetFilter() {
        this.selectedLevel = ''
        this.selectedType = ''
      },
      
      // 应用筛选
      applyFilter() {
        this.hideFilter()
        this.loadContentList(true)
        this.showToast({ title: '筛选已应用' })
      }
    }
  }
</script>

<style>
  .fashion-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  }
  
  .status-bar {
    background: #ffffff;
  }
  
  .header {
    background: #ffffff;
    padding: 20rpx 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .header-content {
    flex: 1;
  }
  
  .header-title {
    font-size: 40rpx;
    font-weight: 700;
    color: #333333;
    margin-bottom: 5rpx;
  }
  
  .header-subtitle {
    margin-top: 5rpx;
  }
  
  .subtitle-text {
    font-size: 24rpx;
    color: #666666;
  }
  
  .header-actions {
    display: flex;
    gap: 20rpx;
  }
  
  .search-btn, .notification-btn {
    position: relative;
    width: 60rpx;
    height: 60rpx;
    background: #f8f9fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .search-icon, .notification-icon {
    font-size: 28rpx;
  }
  
  .notification-badge {
    position: absolute;
    top: -5rpx;
    right: -5rpx;
    background: #ff4757;
    color: #ffffff;
    font-size: 20rpx;
    padding: 2rpx 8rpx;
    border-radius: 20rpx;
    min-width: 30rpx;
    text-align: center;
  }
  
  .badge-text {
    font-size: 20rpx;
  }
  
  .category-nav {
    background: #ffffff;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .nav-scroll {
    width: 100%;
  }
  
  .nav-list {
    display: flex;
    gap: 10rpx;
    padding: 0 30rpx;
  }
  
  .nav-item {
    padding: 15rpx 25rpx;
    background: #f8f9fa;
    border-radius: 25rpx;
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.3s ease;
  }
  
  .nav-item.active {
    background: #007aff;
  }
  
  .nav-text {
    font-size: 26rpx;
    color: #666666;
  }
  
  .nav-item.active .nav-text {
    color: #ffffff;
  }
  
  .banner-section {
    margin: 20rpx 30rpx;
  }
  
  .banner-swiper {
    height: 300rpx;
    border-radius: 16rpx;
    overflow: hidden;
  }
  
  .banner-item {
    position: relative;
    width: 100%;
    height: 100%;
  }
  
  .banner-image {
    width: 100%;
    height: 100%;
  }
  
  .banner-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
    padding: 40rpx 30rpx 30rpx;
    color: #ffffff;
  }
  
  .banner-title {
    display: block;
    font-size: 32rpx;
    font-weight: 600;
    margin-bottom: 10rpx;
  }
  
  .banner-desc {
    font-size: 24rpx;
    opacity: 0.9;
  }
  
  .content-section {
    padding: 20rpx 0;
  }
  
  .featured-content {
    margin-bottom: 40rpx;
  }
  
  .section-title {
    padding: 0 30rpx;
    margin-bottom: 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  
  .title-text {
    font-size: 36rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 5rpx;
  }
  
  .title-desc {
    font-size: 24rpx;
    color: #666666;
  }
  
  .filter-btn {
    display: flex;
    align-items: center;
    gap: 8rpx;
    background: #f8f9fa;
    padding: 10rpx 20rpx;
    border-radius: 20rpx;
    cursor: pointer;
  }
  
  .filter-icon {
    font-size: 24rpx;
  }
  
  .filter-text {
    font-size: 24rpx;
    color: #666666;
  }
  
  .featured-scroll {
    width: 100%;
  }
  
  .featured-list {
    display: flex;
    gap: 20rpx;
    padding: 0 30rpx;
  }
  
  .featured-item {
    width: 280rpx;
    background: #ffffff;
    border-radius: 16rpx;
    overflow: hidden;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    flex-shrink: 0;
  }
  
  .featured-image {
    width: 100%;
    height: 160rpx;
  }
  
  .featured-content-info {
    padding: 20rpx;
  }
  
  .featured-tag {
    background: #e8f5e8;
    color: #34c759;
    padding: 4rpx 12rpx;
    border-radius: 10rpx;
    display: inline-block;
    margin-bottom: 15rpx;
  }
  
  .tag-text {
    font-size: 20rpx;
  }
  
  .featured-title {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
    line-height: 1.4;
  }
  
  .featured-desc {
    display: block;
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 15rpx;
    line-height: 1.4;
  }
  
  .featured-meta {
    display: flex;
    align-items: center;
    gap: 10rpx;
  }
  
  .meta-item {
    font-size: 22rpx;
    color: #999999;
  }
  
  .meta-divider {
    font-size: 22rpx;
    color: #cccccc;
  }
  
  .content-list {
    padding: 0 30rpx;
  }
  
  .list-container {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .content-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 20rpx;
    display: flex;
    gap: 20rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .content-item:active {
    transform: scale(0.98);
  }
  
  .content-image {
    width: 200rpx;
    height: 150rpx;
    border-radius: 12rpx;
    flex-shrink: 0;
  }
  
  .content-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
  }
  
  .content-tag {
    background: #f0f8ff;
    color: #007aff;
    padding: 4rpx 12rpx;
    border-radius: 10rpx;
  }
  
  .content-level {
    padding: 4rpx 10rpx;
    border-radius: 8rpx;
    font-size: 20rpx;
  }
  
  .content-level.beginner {
    background: #e8f5e8;
    color: #34c759;
  }
  
  .content-level.intermediate {
    background: #fff3cd;
    color: #ff9500;
  }
  
  .content-level.advanced {
    background: #f8d7da;
    color: #dc3545;
  }
  
  .level-text {
    font-size: 20rpx;
  }
  
  .content-title {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
    line-height: 1.4;
  }
  
  .content-desc {
    display: block;
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 15rpx;
    line-height: 1.4;
    flex: 1;
  }
  
  .content-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .meta-left {
    display: flex;
    align-items: center;
    gap: 10rpx;
  }
  
  .meta-right {
    display: flex;
    align-items: center;
  }
  
  .meta-stats {
    display: flex;
    gap: 15rpx;
  }
  
  .stats-item {
    font-size: 22rpx;
    color: #999999;
  }
  
  .load-more {
    text-align: center;
    padding: 40rpx 0;
  }
  
  .load-btn {
    background: #f8f9fa;
    color: #666666;
    padding: 20rpx 40rpx;
    border-radius: 25rpx;
    cursor: pointer;
    display: inline-block;
  }
  
  .load-btn.loading {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .load-text {
    font-size: 26rpx;
  }
  
  .no-more {
    text-align: center;
    padding: 40rpx 0;
  }
  
  .no-more-text {
    font-size: 24rpx;
    color: #999999;
  }
  
  .filter-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: flex-end;
    z-index: 1000;
  }
  
  .filter-modal {
    width: 100%;
    background: #ffffff;
    border-radius: 20rpx 20rpx 0 0;
    padding: 40rpx 30rpx;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
    padding-bottom: 20rpx;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .filter-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .close-btn {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .close-icon {
    font-size: 36rpx;
    color: #666666;
  }
  
  .filter-content {
    margin-bottom: 40rpx;
  }
  
  .filter-section {
    margin-bottom: 30rpx;
  }
  
  .filter-label {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 20rpx;
  }
  
  .filter-options {
    display: flex;
    flex-wrap: wrap;
    gap: 15rpx;
  }
  
  .filter-option {
    background: #f8f9fa;
    color: #666666;
    padding: 15rpx 25rpx;
    border-radius: 25rpx;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2rpx solid transparent;
  }
  
  .filter-option.active {
    background: #007aff;
    color: #ffffff;
    border-color: #007aff;
  }
  
  .option-text {
    font-size: 26rpx;
  }
  
  .filter-actions {
    display: flex;
    gap: 20rpx;
  }
  
  .filter-btn {
    flex: 1;
    height: 80rpx;
    border: none;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: 600;
    cursor: pointer;
  }
  
  .filter-btn.reset {
    background: #f8f9fa;
    color: #666666;
  }
  
  .filter-btn.confirm {
    background: #007aff;
    color: #ffffff;
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .content-item {
      flex-direction: column;
    }
    
    .content-image {
      width: 100%;
      height: 200rpx;
    }
    
    .featured-item {
      width: 260rpx;
    }
    
    .banner-swiper {
      height: 250rpx;
    }
  }
</style>