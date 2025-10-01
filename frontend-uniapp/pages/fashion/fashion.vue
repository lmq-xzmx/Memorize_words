<template>
  <view class="fashion-container">
    <!-- 自定义导航栏 -->
    <MobileNavBar title="时尚内容" :showBack="false" />
    
    <!-- 时尚内容区域 -->
    <view class="content-area">
      <!-- 时尚轮播图 -->
      <view class="banner-section">
        <swiper class="banner-swiper" indicator-dots="true" autoplay="true" interval="3000" duration="500">
          <swiper-item>
            <view class="banner-item banner-1">
              <text class="banner-title">时尚英语</text>
              <text class="banner-subtitle">学习最新流行词汇</text>
            </view>
          </swiper-item>
          <swiper-item>
            <view class="banner-item banner-2">
              <text class="banner-title">潮流表达</text>
              <text class="banner-subtitle">掌握时尚英语表达</text>
            </view>
          </swiper-item>
          <swiper-item>
            <view class="banner-item banner-3">
              <text class="banner-title">英语时尚</text>
              <text class="banner-subtitle">提升语言魅力</text>
            </view>
          </swiper-item>
        </swiper>
      </view>
      
      <!-- 时尚分类 -->
      <view class="category-section">
        <view class="section-title">时尚分类</view>
        <view class="category-grid">
          <MobileCard 
            v-for="category in fashionCategories" 
            :key="category.id"
            :title="category.name"
            :subtitle="category.description"
            :icon="category.icon"
            @click="navigateToCategory(category)"
          />
        </view>
      </view>
      
      <!-- 热门时尚内容 -->
      <view class="hot-content-section">
        <view class="section-title">热门内容</view>
        <MobileList 
          :items="hotFashionContent"
          @itemClick="viewContent"
        />
      </view>
      
      <!-- 时尚词汇学习 -->
      <view class="vocabulary-section">
        <view class="section-title">时尚词汇</view>
        <view class="vocabulary-grid">
          <view 
            v-for="word in fashionVocabulary" 
            :key="word.id"
            class="vocabulary-item"
            @click="learnWord(word)"
          >
            <text class="word-text">{{ word.word }}</text>
            <text class="word-meaning">{{ word.meaning }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import MobileNavBar from '@/components/MobileNavBar.vue'
import MobileCard from '@/components/MobileCard.vue'
import MobileList from '@/components/MobileList.vue'

export default {
  name: 'Fashion',
  components: {
    MobileNavBar,
    MobileCard,
    MobileList
  },
  data() {
    return {
      fashionCategories: [
        {
          id: 1,
          name: '服装时尚',
          description: '学习服装相关英语',
          icon: '👗'
        },
        {
          id: 2,
          name: '美妆护肤',
          description: '美容英语词汇',
          icon: '💄'
        },
        {
          id: 3,
          name: '潮流趋势',
          description: '时尚趋势表达',
          icon: '✨'
        },
        {
          id: 4,
          name: '配饰搭配',
          description: '配饰英语学习',
          icon: '👜'
        }
      ],
      hotFashionContent: [
        {
          id: 1,
          title: '2024春季时尚趋势',
          subtitle: '学习最新时尚英语表达',
          time: '2小时前'
        },
        {
          id: 2,
          title: '时尚博主常用词汇',
          subtitle: '掌握时尚圈专业术语',
          time: '1天前'
        },
        {
          id: 3,
          title: '穿搭英语口语',
          subtitle: '日常穿搭英语对话',
          time: '2天前'
        }
      ],
      fashionVocabulary: [
        {
          id: 1,
          word: 'trendy',
          meaning: '时尚的'
        },
        {
          id: 2,
          word: 'chic',
          meaning: '别致的'
        },
        {
          id: 3,
          word: 'stylish',
          meaning: '时髦的'
        },
        {
          id: 4,
          word: 'elegant',
          meaning: '优雅的'
        }
      ]
    }
  },
  methods: {
    navigateToCategory(category) {
      console.log('Navigate to category:', category.name)
      uni.showToast({
        title: `进入${category.name}`,
        icon: 'none'
      })
    },
    viewContent(content) {
      console.log('View content:', content.title)
      uni.showToast({
        title: `查看${content.title}`,
        icon: 'none'
      })
    },
    learnWord(word) {
      console.log('Learn word:', word.word)
      uni.showToast({
        title: `学习单词: ${word.word}`,
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.fashion-container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.content-area {
  padding: 20rpx;
}

.banner-section {
  margin-bottom: 40rpx;
}

.banner-swiper {
  height: 300rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.banner-item {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  position: relative;
}

.banner-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.banner-2 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.banner-3 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.banner-title {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.banner-subtitle {
  font-size: 24rpx;
  opacity: 0.9;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.category-section {
  margin-bottom: 40rpx;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.hot-content-section {
  margin-bottom: 40rpx;
}

.vocabulary-section {
  margin-bottom: 40rpx;
}

.vocabulary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.vocabulary-item {
  background: white;
  padding: 30rpx;
  border-radius: 15rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.2s;
}

.vocabulary-item:active {
  transform: scale(0.95);
}

.word-text {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.word-meaning {
  display: block;
  font-size: 24rpx;
  color: #666;
}
</style>