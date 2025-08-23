<template>
  <view class="word-learning-page">
    <!-- 页面头部 -->
    <view class="page-header">
      <text class="page-title">⚔️ 斩词学习</text>
      <text class="page-subtitle">开始你的单词征程</text>
    </view>

    <!-- 学习统计卡片 -->
    <view class="stats-section">
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-number">{{ todayLearned }}</text>
          <text class="stat-label">今日已学</text>
        </view>
        <view class="stat-item">
          <text class="stat-number">{{ totalLearned }}</text>
          <text class="stat-label">累计掌握</text>
        </view>
        <view class="stat-item">
          <text class="stat-number">{{ streak }}</text>
          <text class="stat-label">连续天数</text>
        </view>
      </view>
    </view>

    <!-- 学习模式选择 -->
    <view class="learning-modes">
      <text class="section-title">📚 选择学习模式</text>
      
      <view class="mode-grid">
        <view 
          v-for="mode in learningModes" 
          :key="mode.id"
          class="mode-card"
          :class="{ 'disabled': !mode.enabled }"
          @click="selectLearningMode(mode)"
        >
          <text class="mode-icon">{{ mode.icon }}</text>
          <text class="mode-title">{{ mode.title }}</text>
          <text class="mode-description">{{ mode.description }}</text>
          <view v-if="!mode.enabled" class="mode-badge">即将开放</view>
        </view>
      </view>
    </view>

    <!-- 今日单词预览 -->
    <view class="today-words">
      <text class="section-title">🎯 今日单词</text>
      
      <view class="word-preview-list">
        <view 
          v-for="word in todayWords" 
          :key="word.id"
          class="word-preview-card"
          @click="previewWord(word)"
        >
          <view class="word-main">
            <text class="word-text">{{ word.word }}</text>
            <text class="word-phonetic">{{ word.phonetic }}</text>
          </view>
          <view class="word-meaning">
            <text class="word-translation">{{ word.translation }}</text>
          </view>
          <view class="word-progress">
            <view 
              class="progress-bar"
              :style="{ width: word.progress + '%' }"
            ></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 快速操作按钮 -->
    <view class="quick-actions">
      <button class="action-btn primary" @click="startLearning">
        🚀 开始学习
      </button>
      <button class="action-btn secondary" @click="reviewWords">
        🔄 复习单词
      </button>
    </view>
  </view>
</template>

<script>
export default {
  name: 'WordLearning',
  data() {
    return {
      // 学习统计数据
      todayLearned: 15,
      totalLearned: 1248,
      streak: 7,
      
      // 学习模式配置
      learningModes: [
        {
          id: 'flashcard',
          title: '闪卡记忆',
          icon: '🃏',
          description: '快速记忆单词',
          enabled: true
        },
        {
          id: 'spelling',
          title: '拼写练习',
          icon: '✍️',
          description: '强化拼写能力',
          enabled: true
        },
        {
          id: 'listening',
          title: '听力训练',
          icon: '🎧',
          description: '提升听力理解',
          enabled: true
        },
        {
          id: 'reading',
          title: '阅读理解',
          icon: '📖',
          description: '语境中学习',
          enabled: false
        },
        {
          id: 'story',
          title: '故事记忆',
          icon: '📚',
          description: '故事情境学习',
          enabled: false
        },
        {
          id: 'challenge',
          title: '挑战模式',
          icon: '⚡',
          description: '限时挑战',
          enabled: true
        }
      ],
      
      // 今日单词数据
      todayWords: [
        {
          id: 1,
          word: 'adventure',
          phonetic: '/ədˈventʃər/',
          translation: '冒险，奇遇',
          progress: 75
        },
        {
          id: 2,
          word: 'brilliant',
          phonetic: '/ˈbrɪljənt/',
          translation: '聪明的，杰出的',
          progress: 45
        },
        {
          id: 3,
          word: 'challenge',
          phonetic: '/ˈtʃælɪndʒ/',
          translation: '挑战，质疑',
          progress: 90
        }
      ]
    }
  },
  
  onLoad() {
    this.loadLearningData()
  },
  
  methods: {
    /**
     * 加载学习数据
     */
    loadLearningData() {
      // 模拟数据加载
      console.log('加载学习数据...')
    },
    
    /**
     * 选择学习模式
     */
    selectLearningMode(mode) {
      if (!mode.enabled) {
        uni.showToast({
          title: '该模式即将开放',
          icon: 'none'
        })
        return
      }
      
      console.log('选择学习模式:', mode.title)
      
      // 根据模式跳转到对应页面
      const routeMap = {
        'flashcard': '/pages/word-flashcard/word-flashcard',
        'spelling': '/pages/word-spelling/word-spelling',
        'listening': '/pages/listening/listening',
        'challenge': '/pages/word-challenge/word-challenge'
      }
      
      const route = routeMap[mode.id]
      if (route) {
        uni.navigateTo({
          url: route,
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
     * 预览单词详情
     */
    previewWord(word) {
      console.log('预览单词:', word.word)
      uni.navigateTo({
        url: `/pages/word-detail/word-detail?word=${word.word}`,
        fail: () => {
          uni.showToast({
            title: '单词详情页开发中...',
            icon: 'none'
          })
        }
      })
    },
    
    /**
     * 开始学习
     */
    startLearning() {
      console.log('开始学习')
      uni.navigateTo({
        url: '/pages/word-flashcard/word-flashcard',
        fail: () => {
          uni.showToast({
            title: '学习页面开发中...',
            icon: 'none'
          })
        }
      })
    },
    
    /**
     * 复习单词
     */
    reviewWords() {
      console.log('复习单词')
      uni.navigateTo({
        url: '/pages/word-review/word-review',
        fail: () => {
          uni.showToast({
            title: '复习页面开发中...',
            icon: 'none'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.word-learning-page {
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

.stats-section {
  margin-bottom: 60rpx;
  
  .stats-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 24rpx;
    padding: 40rpx;
    display: flex;
    justify-content: space-around;
    box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
    
    .stat-item {
      text-align: center;
      
      .stat-number {
        display: block;
        font-size: 48rpx;
        font-weight: bold;
        color: #333333;
        margin-bottom: 8rpx;
      }
      
      .stat-label {
        display: block;
        font-size: 24rpx;
        color: #666666;
      }
    }
  }
}

.learning-modes {
  margin-bottom: 60rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 32rpx;
  }
  
  .mode-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24rpx;
    
    .mode-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 20rpx;
      padding: 32rpx 24rpx;
      text-align: center;
      position: relative;
      transition: all 0.3s ease;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      &:active {
        transform: scale(0.95);
      }
      
      &.disabled {
        opacity: 0.6;
        
        .mode-badge {
          position: absolute;
          top: 12rpx;
          right: 12rpx;
          background: #ff6b6b;
          color: #ffffff;
          font-size: 20rpx;
          padding: 4rpx 12rpx;
          border-radius: 12rpx;
        }
      }
      
      .mode-icon {
        display: block;
        font-size: 48rpx;
        margin-bottom: 16rpx;
      }
      
      .mode-title {
        display: block;
        font-size: 28rpx;
        font-weight: bold;
        color: #333333;
        margin-bottom: 8rpx;
      }
      
      .mode-description {
        display: block;
        font-size: 24rpx;
        color: #666666;
      }
    }
  }
}

.today-words {
  margin-bottom: 60rpx;
  
  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 32rpx;
  }
  
  .word-preview-list {
    .word-preview-card {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16rpx;
      padding: 24rpx;
      margin-bottom: 16rpx;
      transition: all 0.3s ease;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
      
      &:active {
        transform: scale(0.98);
      }
      
      .word-main {
        display: flex;
        align-items: baseline;
        margin-bottom: 12rpx;
        
        .word-text {
          font-size: 32rpx;
          font-weight: bold;
          color: #333333;
          margin-right: 16rpx;
        }
        
        .word-phonetic {
          font-size: 24rpx;
          color: #666666;
          font-style: italic;
        }
      }
      
      .word-meaning {
        margin-bottom: 16rpx;
        
        .word-translation {
          font-size: 26rpx;
          color: #555555;
        }
      }
      
      .word-progress {
        height: 6rpx;
        background: #f0f0f0;
        border-radius: 3rpx;
        overflow: hidden;
        
        .progress-bar {
          height: 100%;
          background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
          border-radius: 3rpx;
          transition: width 0.3s ease;
        }
      }
    }
  }
}

.quick-actions {
  display: flex;
  gap: 24rpx;
  
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
</style>