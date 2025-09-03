<template>
  <view class="tools-container">
    <!-- 状态栏占位 -->
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 头部区域 -->
    <view class="header">
      <view class="header-content">
        <text class="header-title">学习工具</text>
        <view class="header-subtitle">
          <text class="subtitle-text">提升英语学习效率的实用工具</text>
        </view>
      </view>
    </view>
    
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <view class="search-icon">
          <text class="icon-text">🔍</text>
        </view>
        <input 
          class="search-input" 
          placeholder="搜索单词、短语或工具"
          v-model="searchKeyword"
          @input="handleSearch"
          @confirm="performSearch"
        />
        <view class="search-btn" @tap="performSearch" v-if="searchKeyword">
          <text class="btn-text">搜索</text>
        </view>
      </view>
    </view>
    
    <!-- 快速工具 -->
    <view class="quick-tools">
      <view class="section-title">
        <text class="title-text">快速工具</text>
        <text class="title-desc">常用学习工具，一键直达</text>
      </view>
      <view class="tools-grid">
        <view 
          class="tool-item" 
          v-for="tool in quickTools" 
          :key="tool.id"
          @tap="openTool(tool)"
        >
          <view class="tool-icon" :style="{ backgroundColor: tool.color }">
            <text class="icon-text">{{ tool.icon }}</text>
          </view>
          <text class="tool-name">{{ tool.name }}</text>
          <text class="tool-desc">{{ tool.description }}</text>
        </view>
      </view>
    </view>
    
    <!-- 学习功能 -->
    <view class="learning-features">
      <view class="section-title">
        <text class="title-text">学习功能</text>
        <text class="title-desc">系统化的学习模块</text>
      </view>
      <view class="feature-list">
        <view 
          class="feature-item" 
          v-for="feature in learningFeatures" 
          :key="feature.id"
          @tap="openFeature(feature)"
        >
          <view class="feature-left">
            <view class="feature-icon" :style="{ backgroundColor: feature.color }">
              <text class="icon-text">{{ feature.icon }}</text>
            </view>
            <view class="feature-content">
              <text class="feature-name">{{ feature.name }}</text>
              <text class="feature-desc">{{ feature.description }}</text>
              <view class="feature-meta">
                <text class="meta-item">{{ feature.level }}</text>
                <text class="meta-divider">•</text>
                <text class="meta-item">{{ feature.duration }}</text>
              </view>
            </view>
          </view>
          <view class="feature-right">
            <view class="feature-badge" v-if="feature.isNew">
              <text class="badge-text">NEW</text>
            </view>
            <view class="feature-arrow">
              <text class="arrow-text">→</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 实用工具 -->
    <view class="utility-tools">
      <view class="section-title">
        <text class="title-text">实用工具</text>
        <text class="title-desc">辅助学习的便捷工具</text>
      </view>
      <view class="utility-grid">
        <view 
          class="utility-item" 
          v-for="utility in utilityTools" 
          :key="utility.id"
          @tap="openUtility(utility)"
        >
          <view class="utility-header">
            <view class="utility-icon">
              <text class="icon-text">{{ utility.icon }}</text>
            </view>
            <view class="utility-status" v-if="utility.status">
              <text class="status-text">{{ utility.status }}</text>
            </view>
          </view>
          <text class="utility-name">{{ utility.name }}</text>
          <text class="utility-desc">{{ utility.description }}</text>
          <view class="utility-stats" v-if="utility.stats">
            <text class="stats-text">{{ utility.stats }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 最近使用 -->
    <view class="recent-tools" v-if="recentTools.length > 0">
      <view class="section-title">
        <text class="title-text">最近使用</text>
        <text class="title-more" @tap="clearRecent">清空</text>
      </view>
      <scroll-view class="recent-scroll" scroll-x="true" show-scrollbar="false">
        <view class="recent-list">
          <view 
            class="recent-item" 
            v-for="item in recentTools" 
            :key="item.id"
            @tap="openTool(item)"
          >
            <view class="recent-icon" :style="{ backgroundColor: item.color }">
              <text class="icon-text">{{ item.icon }}</text>
            </view>
            <text class="recent-name">{{ item.name }}</text>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <!-- 底部间距 -->
    <view class="bottom-spacing"></view>
  </view>
</template>

<script>
  import { mapState, mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Tools',
    data() {
      return {
        searchKeyword: '',
        
        quickTools: [
          {
            id: 1,
            name: '单词查询',
            description: '快速查词',
            icon: '📖',
            color: '#FF6B6B',
            path: '/pages/tools/dictionary'
          },
          {
            id: 2,
            name: '翻译助手',
            description: '中英互译',
            icon: '🔄',
            color: '#4ECDC4',
            path: '/pages/tools/translator'
          },
          {
            id: 3,
            name: '语音识别',
            description: '语音转文字',
            icon: '🎤',
            color: '#45B7D1',
            path: '/pages/tools/speech'
          },
          {
            id: 4,
            name: '发音练习',
            description: '纠正发音',
            icon: '🗣️',
            color: '#96CEB4',
            path: '/pages/tools/pronunciation'
          }
        ],
        
        learningFeatures: [
          {
            id: 1,
            name: '听力训练',
            description: '提升英语听力理解能力',
            icon: '🎧',
            color: '#FF6B6B',
            level: '初级-高级',
            duration: '15-30分钟',
            isNew: false,
            path: '/pages/learning/listening'
          },
          {
            id: 2,
            name: '口语练习',
            description: 'AI对话练习，提升口语表达',
            icon: '💬',
            color: '#4ECDC4',
            level: '中级-高级',
            duration: '10-20分钟',
            isNew: true,
            path: '/pages/learning/speaking'
          },
          {
            id: 3,
            name: '语法专练',
            description: '系统学习英语语法规则',
            icon: '📝',
            color: '#45B7D1',
            level: '初级-中级',
            duration: '20-40分钟',
            isNew: false,
            path: '/pages/learning/grammar'
          },
          {
            id: 4,
            name: '阅读理解',
            description: '提升英语阅读理解能力',
            icon: '📚',
            color: '#96CEB4',
            level: '中级-高级',
            duration: '25-45分钟',
            isNew: false,
            path: '/pages/learning/reading'
          },
          {
            id: 5,
            name: '写作训练',
            description: '英语写作技巧与练习',
            icon: '✍️',
            color: '#FECA57',
            level: '中级-高级',
            duration: '30-60分钟',
            isNew: true,
            path: '/pages/learning/writing'
          }
        ],
        
        utilityTools: [
          {
            id: 1,
            name: '单词本',
            description: '管理收藏的单词',
            icon: '📔',
            status: '已同步',
            stats: '共收藏 156 个单词',
            path: '/pages/tools/wordbook'
          },
          {
            id: 2,
            name: '学习计划',
            description: '制定个性化学习计划',
            icon: '📅',
            status: '进行中',
            stats: '本周完成 5/7 天',
            path: '/pages/tools/plan'
          },
          {
            id: 3,
            name: '学习统计',
            description: '查看学习数据分析',
            icon: '📊',
            status: null,
            stats: '今日学习 45 分钟',
            path: '/pages/tools/statistics'
          },
          {
            id: 4,
            name: '错题本',
            description: '复习错误的题目',
            icon: '❌',
            status: '待复习',
            stats: '共 23 道错题',
            path: '/pages/tools/mistakes'
          },
          {
            id: 5,
            name: '学习提醒',
            description: '设置学习提醒通知',
            icon: '⏰',
            status: '已开启',
            stats: '每日 19:00 提醒',
            path: '/pages/tools/reminder'
          },
          {
            id: 6,
            name: '离线下载',
            description: '下载内容离线学习',
            icon: '📥',
            status: null,
            stats: '已下载 3 个课程',
            path: '/pages/tools/offline'
          }
        ],
        
        recentTools: [
          {
            id: 1,
            name: '单词查询',
            icon: '📖',
            color: '#FF6B6B'
          },
          {
            id: 3,
            name: '语音识别',
            icon: '🎤',
            color: '#45B7D1'
          }
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
      this.loadRecentTools()
    },
    
    onPullDownRefresh() {
      this.refreshData().finally(() => {
        uni.stopPullDownRefresh()
      })
    },
    
    methods: {
      ...mapActions('app', ['navigateTo', 'showToast', 'showLoading', 'hideLoading']),
      
      // 初始化页面
      initPage() {
        this.loadRecentTools()
      },
      
      // 刷新数据
      async refreshData() {
        try {
          await Promise.all([
            this.loadRecentTools(),
            this.loadToolsData()
          ])
        } catch (error) {
          console.error('刷新数据失败:', error)
        }
      },
      
      // 加载最近使用的工具
      loadRecentTools() {
        try {
          // 这里应该从本地存储或API加载最近使用的工具
          const recent = uni.getStorageSync('recentTools') || []
          this.recentTools = recent.slice(0, 5) // 最多显示5个
        } catch (error) {
          console.error('加载最近使用工具失败:', error)
        }
      },
      
      // 加载工具数据
      async loadToolsData() {
        try {
          // 这里应该调用API加载工具数据
          console.log('加载工具数据')
        } catch (error) {
          console.error('加载工具数据失败:', error)
        }
      },
      
      // 处理搜索输入
      handleSearch() {
        // 实时搜索建议
        if (this.searchKeyword.trim()) {
          this.searchSuggestions()
        }
      },
      
      // 执行搜索
      performSearch() {
        if (!this.searchKeyword.trim()) {
          this.showToast({ title: '请输入搜索内容' })
          return
        }
        
        this.navigateTo({
          url: `/pages/search/search?keyword=${encodeURIComponent(this.searchKeyword)}&type=tools`
        })
      },
      
      // 搜索建议
      searchSuggestions() {
        // 这里可以实现搜索建议功能
        console.log('搜索建议:', this.searchKeyword)
      },
      
      // 打开工具
      openTool(tool) {
        this.addToRecent(tool)
        
        if (tool.path) {
          this.navigateTo({
            url: tool.path
          })
        } else {
          this.showToast({ title: '功能开发中' })
        }
      },
      
      // 打开功能
      openFeature(feature) {
        this.addToRecent(feature)
        
        if (feature.path) {
          this.navigateTo({
            url: feature.path
          })
        } else {
          this.showToast({ title: '功能开发中' })
        }
      },
      
      // 打开实用工具
      openUtility(utility) {
        this.addToRecent(utility)
        
        if (utility.path) {
          this.navigateTo({
            url: utility.path
          })
        } else {
          this.showToast({ title: '功能开发中' })
        }
      },
      
      // 添加到最近使用
      addToRecent(item) {
        try {
          let recent = uni.getStorageSync('recentTools') || []
          
          // 移除已存在的项目
          recent = recent.filter(r => r.id !== item.id)
          
          // 添加到开头
          recent.unshift({
            id: item.id,
            name: item.name,
            icon: item.icon,
            color: item.color || '#007aff',
            path: item.path
          })
          
          // 限制数量
          recent = recent.slice(0, 10)
          
          uni.setStorageSync('recentTools', recent)
          this.recentTools = recent.slice(0, 5)
        } catch (error) {
          console.error('添加到最近使用失败:', error)
        }
      },
      
      // 清空最近使用
      clearRecent() {
        uni.showModal({
          title: '确认清空',
          content: '确定要清空最近使用的工具吗？',
          success: (res) => {
            if (res.confirm) {
              try {
                uni.removeStorageSync('recentTools')
                this.recentTools = []
                this.showToast({ title: '已清空' })
              } catch (error) {
                console.error('清空最近使用失败:', error)
                this.showToast({ title: '清空失败' })
              }
            }
          }
        })
      }
    }
  }
</script>

<style>
  .tools-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  }
  
  .status-bar {
    background: #ffffff;
  }
  
  .header {
    background: #ffffff;
    padding: 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .header-content {
    text-align: center;
  }
  
  .header-title {
    font-size: 40rpx;
    font-weight: 700;
    color: #333333;
    margin-bottom: 10rpx;
  }
  
  .header-subtitle {
    margin-top: 10rpx;
  }
  
  .subtitle-text {
    font-size: 26rpx;
    color: #666666;
  }
  
  .search-section {
    padding: 30rpx;
    background: #ffffff;
  }
  
  .search-bar {
    display: flex;
    align-items: center;
    background: #f8f9fa;
    border-radius: 25rpx;
    padding: 0 20rpx;
    height: 80rpx;
  }
  
  .search-icon {
    margin-right: 15rpx;
  }
  
  .icon-text {
    font-size: 28rpx;
    color: #999999;
  }
  
  .search-input {
    flex: 1;
    font-size: 28rpx;
    color: #333333;
    background: transparent;
    border: none;
    outline: none;
  }
  
  .search-btn {
    background: #007aff;
    color: #ffffff;
    padding: 10rpx 20rpx;
    border-radius: 20rpx;
    margin-left: 15rpx;
  }
  
  .btn-text {
    font-size: 24rpx;
  }
  
  .quick-tools {
    padding: 30rpx;
  }
  
  .section-title {
    margin-bottom: 30rpx;
  }
  
  .title-text {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 10rpx;
  }
  
  .title-desc {
    font-size: 26rpx;
    color: #666666;
  }
  
  .title-more {
    font-size: 26rpx;
    color: #007aff;
    cursor: pointer;
  }
  
  .tools-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20rpx;
  }
  
  .tool-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 30rpx 20rpx;
    text-align: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .tool-item:active {
    transform: scale(0.98);
  }
  
  .tool-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20rpx;
  }
  
  .tool-icon .icon-text {
    font-size: 36rpx;
    color: #ffffff;
  }
  
  .tool-name {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .tool-desc {
    font-size: 24rpx;
    color: #666666;
  }
  
  .learning-features {
    padding: 30rpx;
  }
  
  .feature-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .feature-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .feature-item:active {
    transform: scale(0.98);
  }
  
  .feature-left {
    display: flex;
    align-items: center;
    flex: 1;
  }
  
  .feature-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 25rpx;
  }
  
  .feature-icon .icon-text {
    font-size: 36rpx;
    color: #ffffff;
  }
  
  .feature-content {
    flex: 1;
  }
  
  .feature-name {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .feature-desc {
    display: block;
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 10rpx;
  }
  
  .feature-meta {
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
  
  .feature-right {
    display: flex;
    align-items: center;
    gap: 15rpx;
  }
  
  .feature-badge {
    background: #ff4757;
    color: #ffffff;
    padding: 4rpx 12rpx;
    border-radius: 12rpx;
  }
  
  .badge-text {
    font-size: 20rpx;
    font-weight: 600;
  }
  
  .feature-arrow {
    color: #cccccc;
  }
  
  .arrow-text {
    font-size: 24rpx;
  }
  
  .utility-tools {
    padding: 30rpx;
  }
  
  .utility-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20rpx;
  }
  
  .utility-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 25rpx 20rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .utility-item:active {
    transform: scale(0.98);
  }
  
  .utility-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15rpx;
  }
  
  .utility-icon {
    font-size: 40rpx;
  }
  
  .utility-status {
    background: #e8f5e8;
    color: #34c759;
    padding: 4rpx 10rpx;
    border-radius: 10rpx;
  }
  
  .status-text {
    font-size: 20rpx;
  }
  
  .utility-name {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .utility-desc {
    display: block;
    font-size: 24rpx;
    color: #666666;
    margin-bottom: 15rpx;
    line-height: 1.4;
  }
  
  .utility-stats {
    padding-top: 15rpx;
    border-top: 1rpx solid #f0f0f0;
  }
  
  .stats-text {
    font-size: 22rpx;
    color: #999999;
  }
  
  .recent-tools {
    padding: 30rpx;
  }
  
  .section-title {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 30rpx;
  }
  
  .recent-scroll {
    width: 100%;
  }
  
  .recent-list {
    display: flex;
    gap: 20rpx;
    padding-bottom: 10rpx;
  }
  
  .recent-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    flex-shrink: 0;
  }
  
  .recent-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10rpx;
  }
  
  .recent-icon .icon-text {
    font-size: 36rpx;
    color: #ffffff;
  }
  
  .recent-name {
    font-size: 24rpx;
    color: #333333;
    text-align: center;
    max-width: 100rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .bottom-spacing {
    height: 120rpx;
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .tools-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 15rpx;
    }
    
    .tool-item {
      padding: 25rpx 15rpx;
    }
    
    .tool-icon {
      width: 70rpx;
      height: 70rpx;
    }
    
    .tool-icon .icon-text {
      font-size: 32rpx;
    }
    
    .utility-grid {
      grid-template-columns: 1fr;
    }
    
    .feature-item {
      padding: 25rpx;
    }
    
    .feature-icon {
      width: 70rpx;
      height: 70rpx;
      margin-right: 20rpx;
    }
  }
</style>