<template>
  <view id="app">
    <!-- 页面内容区域 -->
    <view class="page-content">
      <!-- 这里会渲染具体的页面内容 -->
      <view class="temp-content">
        <text>Hello World - 测试页面</text>
      </view>
    </view>
    <BottomNavigation />
  </view>
</template>

<script>
import BottomNavigation from '@/components/BottomNavigation.vue'

export default {
  components: {
    BottomNavigation
  },
  onLaunch: function () {
    console.log('App Launch')
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
}
</script>

<style>
/*每个页面公共css */
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  margin-bottom: 70px; /* 为底部导航留出空间 */
  overflow-y: auto;
}

/* 全局样式重置 */
* {
  box-sizing: border-box;
}

page {
  height: 100%;
  background-color: #f8f9fa;
}

/* 通用按钮样式 */
.btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.btn-primary:hover {
  opacity: 0.9;
}

/* 通用卡片样式 */
.card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
