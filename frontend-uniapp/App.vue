<template>
  <view id="app">
    <!-- 全局加载状态 -->
    <view v-if="appLoading" class="app-loading">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script>
  import { mapState, mapActions } from 'vuex'
  import permissionService from '@/services/permissionService.js'
  
  export default {
    data() {
      return {
        appLoading: true
      }
    },
    computed: {
      ...mapState('user', ['userInfo', 'isLoggedIn']),
      ...mapState('permission', ['menuConfig', 'slotConfig'])
    },
    async onLaunch() {
      console.log('App Launch')
      await this.initializeApp()
    },
    onShow() {
      console.log('App Show')
    },
    onHide() {
      console.log('App Hide')
    },
    methods: {
      ...mapActions('user', ['checkLoginStatus', 'getUserInfo']),
      ...mapActions('permission', ['loadPermissionConfig']),
      
      async initializeApp() {
        try {
          // 检查登录状态
          await this.checkLoginStatus()
          
          // 如果已登录，加载用户信息和权限配置
          if (this.isLoggedIn) {
            await Promise.all([
              this.getUserInfo(),
              this.loadPermissionConfig()
            ])
          }
          
          // 初始化权限服务
          await permissionService.init()
          
        } catch (error) {
          console.error('应用初始化失败:', error)
          uni.showToast({
            title: '初始化失败',
            icon: 'none'
          })
        } finally {
          this.appLoading = false
        }
      }
    }
  }
</script>

<style>
  /* 全局样式 */
  page {
    background-color: #f5f5f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
    font-size: 14px;
    line-height: 1.6;
  }
  
  /* 通用容器 */
  .container {
    padding: 20rpx;
  }
  
  .page-container {
    min-height: 100vh;
    background-color: #f5f5f5;
  }
  
  /* 卡片样式 */
  .card {
    background-color: #ffffff;
    border-radius: 12rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
    margin-bottom: 20rpx;
    overflow: hidden;
  }
  
  .card-header {
    padding: 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
  }
  
  .card-body {
    padding: 30rpx;
  }
  
  .card-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 10rpx;
  }
  
  /* 按钮样式 */
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 20rpx 40rpx;
    border-radius: 8rpx;
    font-size: 28rpx;
    font-weight: 500;
    text-align: center;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
  }
  
  .btn-primary {
    background-color: #007aff;
    color: #ffffff;
  }
  
  .btn-primary:active {
    background-color: #0056cc;
  }
  
  .btn-secondary {
    background-color: #f8f9fa;
    color: #6c757d;
    border: 1rpx solid #dee2e6;
  }
  
  .btn-secondary:active {
    background-color: #e9ecef;
  }
  
  .btn-success {
    background-color: #28a745;
    color: #ffffff;
  }
  
  .btn-success:active {
    background-color: #1e7e34;
  }
  
  .btn-warning {
    background-color: #ffc107;
    color: #212529;
  }
  
  .btn-warning:active {
    background-color: #e0a800;
  }
  
  .btn-danger {
    background-color: #dc3545;
    color: #ffffff;
  }
  
  .btn-danger:active {
    background-color: #c82333;
  }
  
  .btn-block {
    width: 100%;
  }
  
  .btn-small {
    padding: 15rpx 30rpx;
    font-size: 24rpx;
  }
  
  .btn-large {
    padding: 25rpx 50rpx;
    font-size: 32rpx;
  }
  
  /* 输入框样式 */
  .input {
    width: 100%;
    padding: 20rpx;
    border: 1rpx solid #ddd;
    border-radius: 8rpx;
    font-size: 28rpx;
    background-color: #ffffff;
    box-sizing: border-box;
  }
  
  .input:focus {
    border-color: #007aff;
    outline: none;
  }
  
  .input-group {
    margin-bottom: 30rpx;
  }
  
  .input-label {
    display: block;
    margin-bottom: 10rpx;
    font-size: 28rpx;
    color: #333333;
    font-weight: 500;
  }
  
  /* 文本样式 */
  .text-primary {
    color: #007aff;
  }
  
  .text-secondary {
    color: #6c757d;
  }
  
  .text-success {
    color: #28a745;
  }
  
  .text-warning {
    color: #ffc107;
  }
  
  .text-danger {
    color: #dc3545;
  }
  
  .text-muted {
    color: #999999;
  }
  
  .text-center {
    text-align: center;
  }
  
  .text-left {
    text-align: left;
  }
  
  .text-right {
    text-align: right;
  }
  
  /* 布局样式 */
  .flex {
    display: flex;
  }
  
  .flex-column {
    flex-direction: column;
  }
  
  .flex-row {
    flex-direction: row;
  }
  
  .justify-center {
    justify-content: center;
  }
  
  .justify-between {
    justify-content: space-between;
  }
  
  .justify-around {
    justify-content: space-around;
  }
  
  .align-center {
    align-items: center;
  }
  
  .align-start {
    align-items: flex-start;
  }
  
  .align-end {
    align-items: flex-end;
  }
  
  /* 间距样式 */
  .m-0 { margin: 0; }
  .m-1 { margin: 10rpx; }
  .m-2 { margin: 20rpx; }
  .m-3 { margin: 30rpx; }
  .m-4 { margin: 40rpx; }
  
  .mt-0 { margin-top: 0; }
  .mt-1 { margin-top: 10rpx; }
  .mt-2 { margin-top: 20rpx; }
  .mt-3 { margin-top: 30rpx; }
  .mt-4 { margin-top: 40rpx; }
  
  .mb-0 { margin-bottom: 0; }
  .mb-1 { margin-bottom: 10rpx; }
  .mb-2 { margin-bottom: 20rpx; }
  .mb-3 { margin-bottom: 30rpx; }
  .mb-4 { margin-bottom: 40rpx; }
  
  .ml-0 { margin-left: 0; }
  .ml-1 { margin-left: 10rpx; }
  .ml-2 { margin-left: 20rpx; }
  .ml-3 { margin-left: 30rpx; }
  .ml-4 { margin-left: 40rpx; }
  
  .mr-0 { margin-right: 0; }
  .mr-1 { margin-right: 10rpx; }
  .mr-2 { margin-right: 20rpx; }
  .mr-3 { margin-right: 30rpx; }
  .mr-4 { margin-right: 40rpx; }
  
  .p-0 { padding: 0; }
  .p-1 { padding: 10rpx; }
  .p-2 { padding: 20rpx; }
  .p-3 { padding: 30rpx; }
  .p-4 { padding: 40rpx; }
  
  .pt-0 { padding-top: 0; }
  .pt-1 { padding-top: 10rpx; }
  .pt-2 { padding-top: 20rpx; }
  .pt-3 { padding-top: 30rpx; }
  .pt-4 { padding-top: 40rpx; }
  
  .pb-0 { padding-bottom: 0; }
  .pb-1 { padding-bottom: 10rpx; }
  .pb-2 { padding-bottom: 20rpx; }
  .pb-3 { padding-bottom: 30rpx; }
  .pb-4 { padding-bottom: 40rpx; }
  
  .pl-0 { padding-left: 0; }
  .pl-1 { padding-left: 10rpx; }
  .pl-2 { padding-left: 20rpx; }
  .pl-3 { padding-left: 30rpx; }
  .pl-4 { padding-left: 40rpx; }
  
  .pr-0 { padding-right: 0; }
  .pr-1 { padding-right: 10rpx; }
  .pr-2 { padding-right: 20rpx; }
  .pr-3 { padding-right: 30rpx; }
  .pr-4 { padding-right: 40rpx; }
  
  /* 应用加载状态 */
  .app-loading {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  }
  
  .loading-spinner {
    width: 60rpx;
    height: 60rpx;
    border: 4rpx solid #f3f3f3;
    border-top: 4rpx solid #007aff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20rpx;
  }
  
  .loading-text {
    font-size: 28rpx;
    color: #666666;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .container {
      padding: 15rpx;
    }
    
    .card-body {
      padding: 20rpx;
    }
    
    .btn {
      padding: 18rpx 35rpx;
      font-size: 26rpx;
    }
  }
</style>