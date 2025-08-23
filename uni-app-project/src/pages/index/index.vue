<template>
  <view class="tools-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">🛠️ 工具中心</text>
      <text class="page-subtitle">开发与学习工具集合</text>
    </view>

    <!-- 工具菜单 -->
    <view class="tools-section">
      <text class="section-title">💻 开发工具</text>
      
      <view class="tool-category">
        <view 
          v-for="tool in devTools" 
          :key="tool.id"
          class="tool-card"
          :class="{ 'disabled': !tool.enabled }"
          @click="handleToolClick(tool)"
        >
          <view class="tool-icon-wrapper">
            <text class="tool-icon">{{ tool.icon }}</text>
            <view v-if="!tool.enabled" class="tool-badge">{{ tool.status }}</view>
          </view>
          
          <view class="tool-info">
            <text class="tool-title">{{ tool.title }}</text>
            <text class="tool-description">{{ tool.description }}</text>
          </view>
          
          <view class="tool-arrow">
            <text class="arrow-icon">></text>
          </view>
        </view>
      </view>
    </view>

    <!-- 学习工具 -->
    <view class="tools-section">
      <text class="section-title">📚 学习工具</text>
      
      <view class="tool-grid">
        <view 
          v-for="tool in learningTools" 
          :key="tool.id"
          class="tool-grid-item"
          @click="handleToolClick(tool)"
        >
          <text class="grid-tool-icon">{{ tool.icon }}</text>
          <text class="grid-tool-title">{{ tool.title }}</text>
        </view>
      </view>
    </view>

    <!-- 快捷操作 -->
    <view class="quick-actions">
      <text class="section-title">⚡ 快捷操作</text>
      
      <view class="action-buttons">
        <button class="action-btn primary" @click="quickStart">
          🚀 快速开始学习
        </button>
        <button class="action-btn secondary" @click="viewProgress">
          📊 查看学习进度
        </button>
      </view>
    </view>

    <!-- 系统状态 -->
    <view class="system-status">
      <text class="section-title">📱 系统状态</text>
      
      <view class="status-card">
        <view class="status-item">
          <text class="status-label">应用版本</text>
          <text class="status-value">v1.0.0</text>
        </view>
        
        <view class="status-item">
          <text class="status-label">数据同步</text>
          <text class="status-value sync-status">✅ 已同步</text>
        </view>
        
        <view class="status-item">
          <text class="status-label">缓存大小</text>
          <text class="status-value">12.5MB</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { MENU_ITEMS, MENU_UTILS } from '../../config/menuConfig.js'

export default {
  data() {
    return {
      // 用户权限（模拟）
      userPermissions: ['access_dev_tools', 'view_analytics', 'view_word_learning'],
      
      // 开发工具
      devTools: [],
      
      // 学习工具
      learningTools: [
        {
          id: 'word-flashcard',
          title: '单词卡片',
          icon: '🃏',
          path: '/pages/word-flashcard/word-flashcard'
        },
        {
          id: 'word-spelling',
          title: '拼写练习',
          icon: '✍️',
          path: '/pages/word-spelling/word-spelling'
        },
        {
          id: 'listening',
          title: '听力训练',
          icon: '🎧',
          path: '/pages/listening/listening'
        },
        {
          id: 'word-challenge',
          title: '单词挑战',
          icon: '⚡',
          path: '/pages/word-challenge/word-challenge'
        },
        {
          id: 'word-review',
          title: '复习模式',
          icon: '🔄',
          path: '/pages/word-review/word-review'
        },
        {
          id: 'progress',
          title: '学习统计',
          icon: '📈',
          path: '/pages/progress/progress'
        }
      ]
    }
  },
  
  onLoad() {
    this.loadDevTools()
  },
  
  methods: {
    /**
     * 加载开发工具
     */
    loadDevTools() {
      // 获取开发工具菜单
      const devToolsMenu = MENU_ITEMS.DEV_TOOLS || []
      
      // 根据权限过滤
      this.devTools = MENU_UTILS.filterMenuByPermissions(
        devToolsMenu,
        this.userPermissions
      )
    },
    
    /**
     * 处理工具点击
     */
    handleToolClick(tool) {
      if (!tool.enabled) {
        uni.showToast({
          title: `${tool.title}功能${tool.status}`,
          icon: 'none'
        })
        return
      }
      
      if (tool.path) {
        console.log('导航到:', tool.path)
        uni.navigateTo({
          url: tool.path,
          fail: () => {
            uni.showToast({
              title: '页面开发中...',
              icon: 'none'
            })
          }
        })
      }
    },
    
    /**
     * 快速开始学习
     */
    quickStart() {
      uni.switchTab({
        url: '/pages/word-learning/word-learning'
      })
    },
    
    /**
     * 查看学习进度
     */
    viewProgress() {
      uni.navigateTo({
        url: '/pages/progress/progress',
        fail: () => {
          uni.showToast({
            title: '进度页面开发中...',
            icon: 'none'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.tools-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 32rpx 200rpx;
}

.page-header {
  text-align: center;
  margin-bottom: 60rpx;
  
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

.tools-section {
  margin-bottom: 60rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 32rpx;
  }
  
  .tool-category {
    .tool-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 32rpx 24rpx;
      margin-bottom: 16rpx;
      display: flex;
      align-items: center;
      transition: all 0.3s ease;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      &:active {
        transform: scale(0.98);
      }
      
      &.disabled {
        opacity: 0.6;
      }
      
      .tool-icon-wrapper {
        position: relative;
        margin-right: 24rpx;
        
        .tool-icon {
          font-size: 48rpx;
        }
        
        .tool-badge {
          position: absolute;
          top: -8rpx;
          right: -16rpx;
          background: #ff6b6b;
          color: #ffffff;
          font-size: 18rpx;
          padding: 4rpx 8rpx;
          border-radius: 8rpx;
          white-space: nowrap;
        }
      }
      
      .tool-info {
        flex: 1;
        
        .tool-title {
          display: block;
          font-size: 32rpx;
          font-weight: bold;
          color: #333333;
          margin-bottom: 8rpx;
        }
        
        .tool-description {
          display: block;
          font-size: 24rpx;
          color: #666666;
          line-height: 1.4;
        }
      }
      
      .tool-arrow {
        .arrow-icon {
          font-size: 28rpx;
          color: #999999;
        }
      }
    }
  }
  
  .tool-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16rpx;
    
    .tool-grid-item {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 32rpx 16rpx;
      text-align: center;
      transition: all 0.3s ease;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      &:active {
        transform: scale(0.95);
      }
      
      .grid-tool-icon {
        display: block;
        font-size: 40rpx;
        margin-bottom: 12rpx;
      }
      
      .grid-tool-title {
        display: block;
        font-size: 24rpx;
        color: #333333;
        font-weight: 500;
      }
    }
  }
}

.quick-actions {
  margin-bottom: 60rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 32rpx;
  }
  
  .action-buttons {
    display: flex;
    gap: 16rpx;
    
    .action-btn {
      flex: 1;
      height: 88rpx;
      border-radius: 44rpx;
      font-size: 28rpx;
      font-weight: bold;
      border: none;
      transition: all 0.3s ease;
      
      &.primary {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: #ffffff;
        box-shadow: 0 8rpx 24rpx rgba(255, 107, 107, 0.4);
      }
      
      &.secondary {
        background: rgba(255, 255, 255, 0.95);
        color: #333333;
        box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      }
      
      &:active {
        transform: scale(0.95);
      }
    }
  }
}

.system-status {
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 32rpx;
  }
  
  .status-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16rpx;
    padding: 32rpx 24rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
    
    .status-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16rpx 0;
      border-bottom: 1rpx solid #f5f5f5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .status-label {
        font-size: 28rpx;
        color: #333333;
      }
      
      .status-value {
        font-size: 26rpx;
        color: #666666;
        
        &.sync-status {
          color: #52c41a;
        }
      }
    }
  }
}
</style>
