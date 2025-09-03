<template>
  <view class="record-container">
    <!-- 状态栏占位 -->
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 头部导航 -->
    <view class="header">
      <view class="header-left">
        <view class="back-btn" @tap="goBack">
          <text class="back-icon">‹</text>
        </view>
        <text class="header-title">学习记录</text>
      </view>
      <view class="header-right">
        <view class="filter-btn" @tap="showFilterModal">
          <text class="filter-icon">⚙</text>
        </view>
      </view>
    </view>
    
    <!-- 统计概览 -->
    <view class="stats-overview">
      <view class="stats-card">
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-number">{{ overviewStats.totalDays }}</text>
            <text class="stat-label">学习天数</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ overviewStats.totalWords }}</text>
            <text class="stat-label">学习单词</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ overviewStats.totalTime }}</text>
            <text class="stat-label">学习时长</text>
          </view>
          <view class="stat-item">
            <text class="stat-number">{{ overviewStats.avgAccuracy }}%</text>
            <text class="stat-label">平均准确率</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 时间筛选 -->
    <view class="time-filter">
      <scroll-view class="filter-scroll" scroll-x="true">
        <view class="filter-list">
          <view 
            class="filter-item" 
            v-for="filter in timeFilters" 
            :key="filter.value"
            @tap="selectTimeFilter(filter)"
            :class="{ active: selectedTimeFilter.value === filter.value }"
          >
            <text class="filter-text">{{ filter.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <!-- 记录列表 -->
    <view class="record-list">
      <view class="list-header">
        <text class="list-title">学习记录</text>
        <text class="list-count">共 {{ filteredRecords.length }} 条记录</text>
      </view>
      
      <!-- 加载状态 -->
      <view class="loading-state" v-if="loading">
        <view class="loading-spinner"></view>
        <text class="loading-text">加载中...</text>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-else-if="filteredRecords.length === 0">
        <view class="empty-icon">
          <text class="icon-text">📚</text>
        </view>
        <text class="empty-title">暂无学习记录</text>
        <text class="empty-desc">开始学习后，这里会显示你的学习记录</text>
        <button class="start-learn-btn" @tap="goToStudy">
          <text class="btn-text">开始学习</text>
        </button>
      </view>
      
      <!-- 记录项 -->
      <view class="record-items" v-else>
        <view 
          class="record-item" 
          v-for="record in filteredRecords" 
          :key="record.id"
          @tap="viewRecordDetail(record)"
        >
          <view class="record-header">
            <view class="record-date">
              <text class="date-text">{{ formatDate(record.date) }}</text>
              <text class="time-text">{{ formatTime(record.date) }}</text>
            </view>
            <view class="record-type" :class="record.type">
              <text class="type-text">{{ getTypeText(record.type) }}</text>
            </view>
          </view>
          
          <view class="record-content">
            <view class="content-main">
              <text class="content-title">{{ record.title }}</text>
              <text class="content-desc">{{ record.description }}</text>
            </view>
            
            <view class="record-stats">
              <view class="stat-row">
                <view class="stat-col">
                  <text class="stat-label">学习单词</text>
                  <text class="stat-value">{{ record.wordCount }}</text>
                </view>
                <view class="stat-col">
                  <text class="stat-label">正确率</text>
                  <text class="stat-value" :class="getAccuracyClass(record.accuracy)">{{ record.accuracy }}%</text>
                </view>
                <view class="stat-col">
                  <text class="stat-label">用时</text>
                  <text class="stat-value">{{ record.duration }}</text>
                </view>
              </view>
            </view>
          </view>
          
          <view class="record-footer">
            <view class="progress-info">
              <text class="progress-text">学习进度</text>
              <view class="progress-bar">
                <view class="progress-fill" :style="{ width: record.progress + '%' }"></view>
              </view>
              <text class="progress-percent">{{ record.progress }}%</text>
            </view>
            
            <view class="record-actions">
              <view class="action-btn" @tap.stop="shareRecord(record)">
                <text class="action-icon">📤</text>
              </view>
              <view class="action-btn" @tap.stop="deleteRecord(record)">
                <text class="action-icon">🗑</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 筛选弹窗 -->
    <view class="filter-modal" v-if="showFilter" @tap="hideFilterModal">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">筛选条件</text>
          <view class="close-btn" @tap="hideFilterModal">
            <text class="close-icon">×</text>
          </view>
        </view>
        
        <view class="modal-body">
          <!-- 学习类型筛选 -->
          <view class="filter-section">
            <text class="section-title">学习类型</text>
            <view class="option-list">
              <view 
                class="option-item" 
                v-for="type in studyTypes" 
                :key="type.value"
                @tap="toggleTypeFilter(type)"
                :class="{ active: selectedTypes.includes(type.value) }"
              >
                <text class="option-text">{{ type.label }}</text>
                <view class="option-check" v-if="selectedTypes.includes(type.value)">
                  <text class="check-icon">✓</text>
                </view>
              </view>
            </view>
          </view>
          
          <!-- 准确率筛选 -->
          <view class="filter-section">
            <text class="section-title">准确率范围</text>
            <view class="range-selector">
              <view class="range-item">
                <text class="range-label">最低准确率</text>
                <slider 
                  :value="accuracyRange.min" 
                  @change="updateMinAccuracy" 
                  min="0" 
                  max="100" 
                  step="5"
                  activeColor="#007aff"
                  backgroundColor="#e0e0e0"
                />
                <text class="range-value">{{ accuracyRange.min }}%</text>
              </view>
              <view class="range-item">
                <text class="range-label">最高准确率</text>
                <slider 
                  :value="accuracyRange.max" 
                  @change="updateMaxAccuracy" 
                  min="0" 
                  max="100" 
                  step="5"
                  activeColor="#007aff"
                  backgroundColor="#e0e0e0"
                />
                <text class="range-value">{{ accuracyRange.max }}%</text>
              </view>
            </view>
          </view>
        </view>
        
        <view class="modal-footer">
          <button class="modal-btn secondary" @tap="resetFilter">
            <text class="btn-text">重置</text>
          </button>
          <button class="modal-btn primary" @tap="applyFilter">
            <text class="btn-text">应用</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  import { mapState, mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Record',
    data() {
      return {
        loading: false,
        showFilter: false,
        
        // 统计数据
        overviewStats: {
          totalDays: 0,
          totalWords: 0,
          totalTime: '0小时',
          avgAccuracy: 0
        },
        
        // 时间筛选
        timeFilters: [
          { label: '全部', value: 'all' },
          { label: '今天', value: 'today' },
          { label: '本周', value: 'week' },
          { label: '本月', value: 'month' },
          { label: '最近3个月', value: 'quarter' }
        ],
        selectedTimeFilter: { label: '全部', value: 'all' },
        
        // 学习类型
        studyTypes: [
          { label: '单词学习', value: 'word' },
          { label: '选择题', value: 'choice' },
          { label: '填空题', value: 'fill' },
          { label: '听写练习', value: 'dictation' },
          { label: '复习练习', value: 'review' }
        ],
        selectedTypes: [],
        
        // 准确率范围
        accuracyRange: {
          min: 0,
          max: 100
        },
        
        // 学习记录
        allRecords: [],
        filteredRecords: []
      }
    },
    
    computed: {
      ...mapGetters('app', ['statusBarHeight'])
    },
    
    onLoad() {
      this.initPage()
    },
    
    onShow() {
      this.loadRecords()
    },
    
    methods: {
      ...mapActions('app', ['navigateTo', 'showToast', 'showLoading', 'hideLoading']),
      
      // 初始化页面
      async initPage() {
        try {
          this.loading = true
          await Promise.all([
            this.loadOverviewStats(),
            this.loadRecords()
          ])
        } catch (error) {
          console.error('初始化页面失败:', error)
          this.showToast({ title: '加载失败，请重试' })
        } finally {
          this.loading = false
        }
      },
      
      // 加载统计概览
      async loadOverviewStats() {
        try {
          // 这里应该调用API获取统计数据
          // 模拟数据
          this.overviewStats = {
            totalDays: 15,
            totalWords: 328,
            totalTime: '12小时30分',
            avgAccuracy: 85
          }
        } catch (error) {
          console.error('加载统计数据失败:', error)
        }
      },
      
      // 加载学习记录
      async loadRecords() {
        try {
          // 这里应该调用API获取学习记录
          // 模拟数据
          this.allRecords = [
            {
              id: 1,
              date: new Date('2024-01-15 14:30:00'),
              type: 'word',
              title: '基础词汇学习',
              description: '学习了日常生活相关的基础词汇',
              wordCount: 25,
              accuracy: 88,
              duration: '15分钟',
              progress: 75
            },
            {
              id: 2,
              date: new Date('2024-01-15 10:15:00'),
              type: 'choice',
              title: '选择题练习',
              description: '完成了词汇选择题练习',
              wordCount: 20,
              accuracy: 95,
              duration: '12分钟',
              progress: 100
            },
            {
              id: 3,
              date: new Date('2024-01-14 16:45:00'),
              type: 'fill',
              title: '填空练习',
              description: '根据中文释义填写英文单词',
              wordCount: 15,
              accuracy: 73,
              duration: '18分钟',
              progress: 60
            },
            {
              id: 4,
              date: new Date('2024-01-14 09:20:00'),
              type: 'dictation',
              title: '听写练习',
              description: '听音频写单词练习',
              wordCount: 10,
              accuracy: 80,
              duration: '20分钟',
              progress: 80
            },
            {
              id: 5,
              date: new Date('2024-01-13 15:30:00'),
              type: 'review',
              title: '复习练习',
              description: '复习之前学过的单词',
              wordCount: 30,
              accuracy: 92,
              duration: '25分钟',
              progress: 90
            }
          ]
          
          this.applyFilters()
        } catch (error) {
          console.error('加载学习记录失败:', error)
        }
      },
      
      // 选择时间筛选
      selectTimeFilter(filter) {
        this.selectedTimeFilter = filter
        this.applyFilters()
      },
      
      // 应用筛选条件
      applyFilters() {
        let filtered = [...this.allRecords]
        
        // 时间筛选
        if (this.selectedTimeFilter.value !== 'all') {
          const now = new Date()
          const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
          
          filtered = filtered.filter(record => {
            const recordDate = new Date(record.date)
            
            switch (this.selectedTimeFilter.value) {
              case 'today':
                return recordDate >= today
              case 'week':
                const weekStart = new Date(today)
                weekStart.setDate(today.getDate() - today.getDay())
                return recordDate >= weekStart
              case 'month':
                const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
                return recordDate >= monthStart
              case 'quarter':
                const quarterStart = new Date(today)
                quarterStart.setMonth(today.getMonth() - 3)
                return recordDate >= quarterStart
              default:
                return true
            }
          })
        }
        
        // 类型筛选
        if (this.selectedTypes.length > 0) {
          filtered = filtered.filter(record => 
            this.selectedTypes.includes(record.type)
          )
        }
        
        // 准确率筛选
        filtered = filtered.filter(record => 
          record.accuracy >= this.accuracyRange.min && 
          record.accuracy <= this.accuracyRange.max
        )
        
        // 按时间倒序排列
        filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
        
        this.filteredRecords = filtered
      },
      
      // 显示筛选弹窗
      showFilterModal() {
        this.showFilter = true
      },
      
      // 隐藏筛选弹窗
      hideFilterModal() {
        this.showFilter = false
      },
      
      // 切换类型筛选
      toggleTypeFilter(type) {
        const index = this.selectedTypes.indexOf(type.value)
        if (index > -1) {
          this.selectedTypes.splice(index, 1)
        } else {
          this.selectedTypes.push(type.value)
        }
      },
      
      // 更新最低准确率
      updateMinAccuracy(e) {
        this.accuracyRange.min = e.detail.value
        if (this.accuracyRange.min > this.accuracyRange.max) {
          this.accuracyRange.max = this.accuracyRange.min
        }
      },
      
      // 更新最高准确率
      updateMaxAccuracy(e) {
        this.accuracyRange.max = e.detail.value
        if (this.accuracyRange.max < this.accuracyRange.min) {
          this.accuracyRange.min = this.accuracyRange.max
        }
      },
      
      // 重置筛选
      resetFilter() {
        this.selectedTypes = []
        this.accuracyRange = { min: 0, max: 100 }
      },
      
      // 应用筛选
      applyFilter() {
        this.applyFilters()
        this.hideFilterModal()
        this.showToast({ title: '筛选已应用' })
      },
      
      // 查看记录详情
      viewRecordDetail(record) {
        this.navigateTo({
          url: `/pages/record-detail/record-detail?id=${record.id}`
        })
      },
      
      // 分享记录
      shareRecord(record) {
        uni.showActionSheet({
          itemList: ['分享到微信', '分享到朋友圈', '复制链接'],
          success: (res) => {
            const actions = ['wechat', 'moments', 'copy']
            const action = actions[res.tapIndex]
            this.handleShare(record, action)
          }
        })
      },
      
      // 处理分享
      handleShare(record, action) {
        const shareContent = {
          title: `我在英语学习中取得了${record.accuracy}%的准确率！`,
          desc: record.description,
          path: `/pages/record-detail/record-detail?id=${record.id}`
        }
        
        switch (action) {
          case 'wechat':
            // 分享到微信
            this.showToast({ title: '分享到微信' })
            break
          case 'moments':
            // 分享到朋友圈
            this.showToast({ title: '分享到朋友圈' })
            break
          case 'copy':
            // 复制链接
            uni.setClipboardData({
              data: shareContent.path,
              success: () => {
                this.showToast({ title: '链接已复制' })
              }
            })
            break
        }
      },
      
      // 删除记录
      deleteRecord(record) {
        uni.showModal({
          title: '确认删除',
          content: '确定要删除这条学习记录吗？',
          success: async (res) => {
            if (res.confirm) {
              try {
                // 这里应该调用API删除记录
                const index = this.allRecords.findIndex(r => r.id === record.id)
                if (index > -1) {
                  this.allRecords.splice(index, 1)
                  this.applyFilters()
                  this.showToast({ title: '删除成功' })
                }
              } catch (error) {
                console.error('删除记录失败:', error)
                this.showToast({ title: '删除失败，请重试' })
              }
            }
          }
        })
      },
      
      // 前往学习
      goToStudy() {
        uni.switchTab({
          url: '/pages/word/word'
        })
      },
      
      // 返回上一页
      goBack() {
        uni.navigateBack()
      },
      
      // 格式化日期
      formatDate(date) {
        const d = new Date(date)
        const today = new Date()
        const yesterday = new Date(today)
        yesterday.setDate(today.getDate() - 1)
        
        if (d.toDateString() === today.toDateString()) {
          return '今天'
        } else if (d.toDateString() === yesterday.toDateString()) {
          return '昨天'
        } else {
          return `${d.getMonth() + 1}月${d.getDate()}日`
        }
      },
      
      // 格式化时间
      formatTime(date) {
        const d = new Date(date)
        const hours = d.getHours().toString().padStart(2, '0')
        const minutes = d.getMinutes().toString().padStart(2, '0')
        return `${hours}:${minutes}`
      },
      
      // 获取类型文本
      getTypeText(type) {
        const typeMap = {
          word: '单词学习',
          choice: '选择题',
          fill: '填空题',
          dictation: '听写',
          review: '复习'
        }
        return typeMap[type] || '未知'
      },
      
      // 获取准确率样式类
      getAccuracyClass(accuracy) {
        if (accuracy >= 90) return 'excellent'
        if (accuracy >= 80) return 'good'
        if (accuracy >= 70) return 'average'
        return 'poor'
      }
    }
  }
</script>

<style>
  .record-container {
    min-height: 100vh;
    background: #f8f9fa;
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
  
  .header-left {
    display: flex;
    align-items: center;
  }
  
  .back-btn {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    cursor: pointer;
  }
  
  .back-icon {
    font-size: 36rpx;
    color: #007aff;
    font-weight: 600;
  }
  
  .header-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .header-right {
    display: flex;
    align-items: center;
  }
  
  .filter-btn {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .filter-icon {
    font-size: 32rpx;
    color: #666666;
  }
  
  .stats-overview {
    padding: 30rpx;
  }
  
  .stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20rpx;
    padding: 40rpx;
    color: #ffffff;
    box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.3);
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30rpx;
  }
  
  .stat-item {
    text-align: center;
  }
  
  .stat-number {
    display: block;
    font-size: 48rpx;
    font-weight: 700;
    margin-bottom: 8rpx;
  }
  
  .stat-label {
    font-size: 24rpx;
    opacity: 0.9;
  }
  
  .time-filter {
    padding: 0 30rpx 20rpx;
  }
  
  .filter-scroll {
    white-space: nowrap;
  }
  
  .filter-list {
    display: flex;
    gap: 15rpx;
  }
  
  .filter-item {
    flex-shrink: 0;
    padding: 15rpx 30rpx;
    background: #ffffff;
    border-radius: 25rpx;
    border: 2rpx solid #e0e0e0;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .filter-item.active {
    background: #007aff;
    border-color: #007aff;
  }
  
  .filter-item.active .filter-text {
    color: #ffffff;
  }
  
  .filter-text {
    font-size: 26rpx;
    color: #333333;
    white-space: nowrap;
  }
  
  .record-list {
    padding: 0 30rpx 30rpx;
  }
  
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
  }
  
  .list-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .list-count {
    font-size: 24rpx;
    color: #666666;
  }
  
  .loading-state {
    text-align: center;
    padding: 80rpx 0;
  }
  
  .loading-spinner {
    width: 60rpx;
    height: 60rpx;
    border: 4rpx solid #f0f0f0;
    border-top: 4rpx solid #007aff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20rpx;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .loading-text {
    font-size: 26rpx;
    color: #666666;
  }
  
  .empty-state {
    text-align: center;
    padding: 80rpx 0;
  }
  
  .empty-icon {
    font-size: 120rpx;
    margin-bottom: 30rpx;
  }
  
  .icon-text {
    opacity: 0.6;
  }
  
  .empty-title {
    display: block;
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 15rpx;
  }
  
  .empty-desc {
    display: block;
    font-size: 26rpx;
    color: #666666;
    margin-bottom: 40rpx;
  }
  
  .start-learn-btn {
    background: #007aff;
    color: #ffffff;
    border: none;
    border-radius: 25rpx;
    padding: 20rpx 40rpx;
    font-size: 26rpx;
    cursor: pointer;
  }
  
  .record-items {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .record-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 30rpx;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  }
  
  .record-item:active {
    transform: translateY(2rpx);
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  }
  
  .record-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
  }
  
  .record-date {
    display: flex;
    flex-direction: column;
  }
  
  .date-text {
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 5rpx;
  }
  
  .time-text {
    font-size: 22rpx;
    color: #666666;
  }
  
  .record-type {
    padding: 8rpx 16rpx;
    border-radius: 12rpx;
    font-size: 22rpx;
  }
  
  .record-type.word {
    background: #e8f5e8;
    color: #34c759;
  }
  
  .record-type.choice {
    background: #f0f8ff;
    color: #007aff;
  }
  
  .record-type.fill {
    background: #fff3cd;
    color: #ff9500;
  }
  
  .record-type.dictation {
    background: #f8d7da;
    color: #dc3545;
  }
  
  .record-type.review {
    background: #e2e3e5;
    color: #6c757d;
  }
  
  .type-text {
    font-size: 22rpx;
  }
  
  .record-content {
    margin-bottom: 20rpx;
  }
  
  .content-main {
    margin-bottom: 20rpx;
  }
  
  .content-title {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 8rpx;
  }
  
  .content-desc {
    font-size: 24rpx;
    color: #666666;
    line-height: 1.5;
  }
  
  .record-stats {
    background: #f8f9fa;
    border-radius: 12rpx;
    padding: 20rpx;
  }
  
  .stat-row {
    display: flex;
    justify-content: space-between;
  }
  
  .stat-col {
    text-align: center;
    flex: 1;
  }
  
  .stat-label {
    display: block;
    font-size: 22rpx;
    color: #666666;
    margin-bottom: 5rpx;
  }
  
  .stat-value {
    font-size: 26rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .stat-value.excellent {
    color: #34c759;
  }
  
  .stat-value.good {
    color: #007aff;
  }
  
  .stat-value.average {
    color: #ff9500;
  }
  
  .stat-value.poor {
    color: #dc3545;
  }
  
  .record-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .progress-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 15rpx;
  }
  
  .progress-text {
    font-size: 22rpx;
    color: #666666;
    white-space: nowrap;
  }
  
  .progress-bar {
    flex: 1;
    height: 8rpx;
    background: #f0f0f0;
    border-radius: 4rpx;
    overflow: hidden;
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #007aff 0%, #34c759 100%);
    border-radius: 4rpx;
    transition: width 0.3s ease;
  }
  
  .progress-percent {
    font-size: 22rpx;
    color: #666666;
    white-space: nowrap;
  }
  
  .record-actions {
    display: flex;
    gap: 15rpx;
    margin-left: 20rpx;
  }
  
  .action-btn {
    width: 60rpx;
    height: 60rpx;
    background: #f8f9fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .action-btn:active {
    background: #e0e0e0;
  }
  
  .action-icon {
    font-size: 24rpx;
  }
  
  .filter-modal {
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
  
  .modal-content {
    width: 100%;
    background: #ffffff;
    border-radius: 20rpx 20rpx 0 0;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .modal-title {
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
  
  .modal-body {
    padding: 30rpx;
  }
  
  .filter-section {
    margin-bottom: 40rpx;
  }
  
  .section-title {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 20rpx;
  }
  
  .option-list {
    display: flex;
    flex-direction: column;
    gap: 15rpx;
  }
  
  .option-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx;
    background: #f8f9fa;
    border-radius: 12rpx;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2rpx solid transparent;
  }
  
  .option-item.active {
    background: #f0f8ff;
    border-color: #007aff;
  }
  
  .option-text {
    font-size: 26rpx;
    color: #333333;
  }
  
  .option-check {
    width: 40rpx;
    height: 40rpx;
    background: #007aff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .check-icon {
    font-size: 24rpx;
    color: #ffffff;
  }
  
  .range-selector {
    display: flex;
    flex-direction: column;
    gap: 30rpx;
  }
  
  .range-item {
    display: flex;
    align-items: center;
    gap: 20rpx;
  }
  
  .range-label {
    font-size: 26rpx;
    color: #333333;
    white-space: nowrap;
    min-width: 120rpx;
  }
  
  .range-value {
    font-size: 26rpx;
    color: #007aff;
    font-weight: 600;
    min-width: 80rpx;
    text-align: right;
  }
  
  .modal-footer {
    display: flex;
    gap: 20rpx;
    padding: 30rpx;
    border-top: 1rpx solid #f0f0f0;
  }
  
  .modal-btn {
    flex: 1;
    height: 80rpx;
    border: none;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .modal-btn.primary {
    background: #007aff;
    color: #ffffff;
  }
  
  .modal-btn.secondary {
    background: #f8f9fa;
    color: #666666;
    border: 2rpx solid #e0e0e0;
  }
  
  .btn-text {
    font-size: 28rpx;
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 20rpx;
    }
    
    .stat-number {
      font-size: 36rpx;
    }
    
    .record-footer {
      flex-direction: column;
      align-items: stretch;
      gap: 20rpx;
    }
    
    .record-actions {
      margin-left: 0;
      justify-content: center;
    }
  }
</style>