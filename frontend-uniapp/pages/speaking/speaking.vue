<template>
  <view class="speaking-container">
    <!-- 自定义导航栏 -->
    <MobileNavBar title="口语练习" show-back />
    
    <!-- 功能开发中提示 -->
    <view class="placeholder-content">
      <view class="placeholder-icon">
        <text class="iconfont icon-speak"></text>
      </view>
      <view class="placeholder-title">口语练习</view>
      <view class="placeholder-desc">功能正在开发中，敬请期待...</view>
      
      <!-- 预期功能介绍 -->
      <view class="feature-preview">
        <view class="feature-title">即将上线的功能：</view>
        <view class="feature-list">
          <view class="feature-item">
            <text class="feature-icon">🎤</text>
            <text class="feature-text">语音录制与识别</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">🗣️</text>
            <text class="feature-text">发音纠正</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">💬</text>
            <text class="feature-text">口语对话练习</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">⭐</text>
            <text class="feature-text">发音评分系统</text>
          </view>
        </view>
      </view>
      
      <MobileButton 
        type="primary" 
        @click="goBack"
        class="back-button"
      >
        返回学习中心
      </MobileButton>
    </view>
  </view>
</template>

<script>
import MobileNavBar from '@/components/Mobile/MobileNavBar.vue'
import MobileButton from '@/components/Mobile/MobileButton.vue'

export default {
  name: 'SpeakingPage',
  components: {
    MobileNavBar,
    MobileButton
  },
  setup() {
    const goBack = () => {
      uni.navigateBack()
    }

    return {
      goBack
    }
  }
}
</script>

<style lang="scss" scoped>
.speaking-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 40rpx;
  text-align: center;
}

.placeholder-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;
}

.placeholder-icon .iconfont {
  font-size: 60rpx;
  color: #fff;
}

.placeholder-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 20rpx;
}

.placeholder-desc {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 60rpx;
}

.feature-preview {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20rpx;
  padding: 40rpx;
  margin-bottom: 60rpx;
  backdrop-filter: blur(10px);
}

.feature-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 30rpx;
  text-align: center;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 15rpx 0;
}

.feature-icon {
  font-size: 32rpx;
  width: 50rpx;
  text-align: center;
}

.feature-text {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.back-button {
  width: 300rpx;
}
</style>