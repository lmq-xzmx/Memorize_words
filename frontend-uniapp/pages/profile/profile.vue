<template>
  <view class="profile-container">
    <!-- 状态栏占位 -->
    <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
    
    <!-- 头部用户信息 -->
    <view class="header-section">
      <view class="user-info">
        <view class="avatar-container" @tap="changeAvatar">
          <image 
            class="user-avatar" 
            :src="userInfo.avatar || '/static/images/default-avatar.png'" 
            mode="aspectFill"
          ></image>
          <view class="avatar-edit">
            <text class="edit-icon">📷</text>
          </view>
        </view>
        <view class="user-details">
          <text class="user-name">{{ userInfo.nickname || '未设置昵称' }}</text>
          <text class="user-level">{{ userInfo.levelName || 'Lv.1 初学者' }}</text>
          <view class="user-stats">
            <view class="stat-item">
              <text class="stat-number">{{ userInfo.studyDays || 0 }}</text>
              <text class="stat-label">学习天数</text>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-item">
              <text class="stat-number">{{ userInfo.wordsLearned || 0 }}</text>
              <text class="stat-label">已学单词</text>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-item">
              <text class="stat-number">{{ userInfo.streak || 0 }}</text>
              <text class="stat-label">连续天数</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 会员状态 -->
      <view class="vip-status" v-if="userInfo.isVip">
        <view class="vip-badge">
          <text class="vip-icon">👑</text>
          <text class="vip-text">VIP会员</text>
          <text class="vip-expire">{{ userInfo.vipExpireDate }}</text>
        </view>
      </view>
      
      <!-- 学习进度 -->
      <view class="progress-section">
        <view class="progress-header">
          <text class="progress-title">今日学习进度</text>
          <text class="progress-percent">{{ todayProgress }}%</text>
        </view>
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: todayProgress + '%' }"></view>
        </view>
        <view class="progress-info">
          <text class="progress-text">已完成 {{ userInfo.todayWords || 0 }} / {{ userInfo.dailyTarget || 20 }} 个单词</text>
        </view>
      </view>
    </view>
    
    <!-- 功能菜单 -->
    <view class="menu-section">
      <!-- 学习相关 -->
      <view class="menu-group">
        <view class="group-title">
          <text class="title-text">学习管理</text>
        </view>
        <view class="menu-list">
          <view class="menu-item" @tap="navigateToPage('/pages/study/history')">
            <view class="menu-icon study">
              <text class="icon-text">📚</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">学习记录</text>
              <text class="menu-desc">查看学习历史和统计</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/favorites/favorites')">
            <view class="menu-icon favorite">
              <text class="icon-text">⭐</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">我的收藏</text>
              <text class="menu-desc">收藏的单词和内容</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/plan/plan')">
            <view class="menu-icon plan">
              <text class="icon-text">🎯</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">学习计划</text>
              <text class="menu-desc">制定和管理学习目标</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/achievement/achievement')">
            <view class="menu-icon achievement">
              <text class="icon-text">🏆</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">成就徽章</text>
              <text class="menu-desc">查看获得的成就和徽章</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 账户相关 -->
      <view class="menu-group">
        <view class="group-title">
          <text class="title-text">账户设置</text>
        </view>
        <view class="menu-list">
          <view class="menu-item" @tap="navigateToPage('/pages/profile/edit')">
            <view class="menu-icon profile">
              <text class="icon-text">👤</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">个人信息</text>
              <text class="menu-desc">编辑个人资料</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/security/security')">
            <view class="menu-icon security">
              <text class="icon-text">🔒</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">账户安全</text>
              <text class="menu-desc">密码和安全设置</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/vip/vip')" v-if="!userInfo.isVip">
            <view class="menu-icon vip">
              <text class="icon-text">💎</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">开通VIP</text>
              <text class="menu-desc">享受更多学习特权</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 应用设置 -->
      <view class="menu-group">
        <view class="group-title">
          <text class="title-text">应用设置</text>
        </view>
        <view class="menu-list">
          <view class="menu-item" @tap="navigateToPage('/pages/settings/settings')">
            <view class="menu-icon settings">
              <text class="icon-text">⚙️</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">学习设置</text>
              <text class="menu-desc">学习偏好和提醒设置</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/notification/settings')">
            <view class="menu-icon notification">
              <text class="icon-text">🔔</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">通知设置</text>
              <text class="menu-desc">推送和提醒管理</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/theme/theme')">
            <view class="menu-icon theme">
              <text class="icon-text">🎨</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">主题设置</text>
              <text class="menu-desc">界面主题和外观</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 其他功能 -->
      <view class="menu-group">
        <view class="group-title">
          <text class="title-text">其他</text>
        </view>
        <view class="menu-list">
          <view class="menu-item" @tap="navigateToPage('/pages/feedback/feedback')">
            <view class="menu-icon feedback">
              <text class="icon-text">💬</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">意见反馈</text>
              <text class="menu-desc">帮助我们改进产品</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="navigateToPage('/pages/about/about')">
            <view class="menu-icon about">
              <text class="icon-text">ℹ️</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">关于我们</text>
              <text class="menu-desc">版本信息和帮助</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
          
          <view class="menu-item" @tap="shareApp">
            <view class="menu-icon share">
              <text class="icon-text">📤</text>
            </view>
            <view class="menu-content">
              <text class="menu-title">分享应用</text>
              <text class="menu-desc">推荐给朋友一起学习</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-icon">></text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 退出登录 -->
    <view class="logout-section">
      <button class="logout-btn" @tap="showLogoutConfirm">退出登录</button>
    </view>
    
    <!-- 版本信息 -->
    <view class="version-info">
      <text class="version-text">版本 {{ appVersion }}</text>
    </view>
    
    <!-- 头像选择弹窗 -->
    <view class="avatar-modal" v-if="showAvatarModal" @tap="hideAvatarModal">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">选择头像</text>
          <view class="close-btn" @tap="hideAvatarModal">
            <text class="close-icon">×</text>
          </view>
        </view>
        <view class="avatar-options">
          <view class="option-item" @tap="selectFromAlbum">
            <view class="option-icon">
              <text class="icon-text">📷</text>
            </view>
            <text class="option-text">从相册选择</text>
          </view>
          <view class="option-item" @tap="takePhoto">
            <view class="option-icon">
              <text class="icon-text">📸</text>
            </view>
            <text class="option-text">拍照</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  import { mapState, mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Profile',
    data() {
      return {
        showAvatarModal: false,
        appVersion: '1.0.0'
      }
    },
    
    computed: {
      ...mapState('user', ['userInfo', 'isLoggedIn']),
      ...mapGetters('app', ['statusBarHeight']),
      
      // 今日学习进度
      todayProgress() {
        const todayWords = this.userInfo.todayWords || 0
        const dailyTarget = this.userInfo.dailyTarget || 20
        return Math.min(Math.round((todayWords / dailyTarget) * 100), 100)
      }
    },
    
    onLoad() {
      this.initPage()
    },
    
    onShow() {
      this.refreshUserInfo()
    },
    
    onPullDownRefresh() {
      this.refreshUserInfo().finally(() => {
        uni.stopPullDownRefresh()
      })
    },
    
    methods: {
      ...mapActions('user', ['getUserInfo', 'logout']),
      ...mapActions('app', ['navigateTo', 'showToast', 'showModal']),
      
      // 初始化页面
      initPage() {
        if (!this.isLoggedIn) {
          this.navigateToLogin()
          return
        }
        this.refreshUserInfo()
      },
      
      // 刷新用户信息
      async refreshUserInfo() {
        try {
          await this.getUserInfo()
        } catch (error) {
          console.error('获取用户信息失败:', error)
        }
      },
      
      // 跳转到登录页
      navigateToLogin() {
        uni.reLaunch({
          url: '/pages/login/login'
        })
      },
      
      // 页面导航
      navigateToPage(url) {
        this.navigateTo({ url })
      },
      
      // 更换头像
      changeAvatar() {
        this.showAvatarModal = true
      },
      
      // 隐藏头像选择弹窗
      hideAvatarModal() {
        this.showAvatarModal = false
      },
      
      // 从相册选择
      selectFromAlbum() {
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          sourceType: ['album'],
          success: (res) => {
            this.uploadAvatar(res.tempFilePaths[0])
          },
          fail: (error) => {
            console.error('选择图片失败:', error)
            this.showToast({ title: '选择图片失败' })
          }
        })
        this.hideAvatarModal()
      },
      
      // 拍照
      takePhoto() {
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          sourceType: ['camera'],
          success: (res) => {
            this.uploadAvatar(res.tempFilePaths[0])
          },
          fail: (error) => {
            console.error('拍照失败:', error)
            this.showToast({ title: '拍照失败' })
          }
        })
        this.hideAvatarModal()
      },
      
      // 上传头像
      async uploadAvatar(filePath) {
        try {
          uni.showLoading({ title: '上传中...' })
          
          // 这里应该调用上传头像的API
          await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟上传
          
          this.showToast({ title: '头像更新成功' })
          this.refreshUserInfo()
        } catch (error) {
          console.error('上传头像失败:', error)
          this.showToast({ title: '上传失败，请重试' })
        } finally {
          uni.hideLoading()
        }
      },
      
      // 分享应用
      shareApp() {
        // #ifdef MP-WEIXIN
        uni.share({
          provider: 'weixin',
          scene: 'WXSceneSession',
          type: 0,
          href: 'https://your-app-url.com',
          title: '英语学习助手',
          summary: '让英语学习更简单有趣',
          imageUrl: '/static/images/share-logo.png'
        })
        // #endif
        
        // #ifdef H5
        if (navigator.share) {
          navigator.share({
            title: '英语学习助手',
            text: '让英语学习更简单有趣',
            url: window.location.href
          })
        } else {
          this.showToast({ title: '请手动分享链接' })
        }
        // #endif
        
        // #ifdef APP-PLUS
        uni.share({
          provider: 'weixin',
          scene: 'WXSceneSession',
          type: 0,
          href: 'https://your-app-url.com',
          title: '英语学习助手',
          summary: '让英语学习更简单有趣',
          imageUrl: '/static/images/share-logo.png'
        })
        // #endif
      },
      
      // 显示退出登录确认
      showLogoutConfirm() {
        this.showModal({
          title: '确认退出',
          content: '确定要退出登录吗？',
          showCancel: true,
          confirmText: '退出',
          cancelText: '取消',
          success: (res) => {
            if (res.confirm) {
              this.handleLogout()
            }
          }
        })
      },
      
      // 处理退出登录
      async handleLogout() {
        try {
          uni.showLoading({ title: '退出中...' })
          
          await this.logout()
          
          uni.reLaunch({
            url: '/pages/login/login'
          })
        } catch (error) {
          console.error('退出登录失败:', error)
          this.showToast({ title: '退出失败，请重试' })
        } finally {
          uni.hideLoading()
        }
      }
    }
  }
</script>

<style>
  .profile-container {
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  .status-bar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .header-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30rpx;
    color: #ffffff;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    margin-bottom: 30rpx;
  }
  
  .avatar-container {
    position: relative;
    margin-right: 30rpx;
  }
  
  .user-avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 60rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
  }
  
  .avatar-edit {
    position: absolute;
    bottom: -5rpx;
    right: -5rpx;
    width: 40rpx;
    height: 40rpx;
    background: #ffffff;
    border-radius: 20rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  }
  
  .edit-icon {
    font-size: 20rpx;
  }
  
  .user-details {
    flex: 1;
  }
  
  .user-name {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    margin-bottom: 8rpx;
  }
  
  .user-level {
    display: block;
    font-size: 24rpx;
    opacity: 0.9;
    margin-bottom: 20rpx;
  }
  
  .user-stats {
    display: flex;
    align-items: center;
  }
  
  .stat-item {
    text-align: center;
  }
  
  .stat-number {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    margin-bottom: 5rpx;
  }
  
  .stat-label {
    font-size: 20rpx;
    opacity: 0.8;
  }
  
  .stat-divider {
    width: 1rpx;
    height: 40rpx;
    background: rgba(255, 255, 255, 0.3);
    margin: 0 30rpx;
  }
  
  .vip-status {
    margin-bottom: 30rpx;
  }
  
  .vip-badge {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 25rpx;
    padding: 15rpx 25rpx;
    display: flex;
    align-items: center;
    gap: 10rpx;
  }
  
  .vip-icon {
    font-size: 24rpx;
  }
  
  .vip-text {
    font-size: 26rpx;
    font-weight: 600;
  }
  
  .vip-expire {
    font-size: 22rpx;
    opacity: 0.8;
    margin-left: auto;
  }
  
  .progress-section {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 16rpx;
    padding: 25rpx;
  }
  
  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15rpx;
  }
  
  .progress-title {
    font-size: 28rpx;
    font-weight: 600;
  }
  
  .progress-percent {
    font-size: 32rpx;
    font-weight: 700;
  }
  
  .progress-bar {
    height: 12rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6rpx;
    overflow: hidden;
    margin-bottom: 15rpx;
  }
  
  .progress-fill {
    height: 100%;
    background: #ffffff;
    border-radius: 6rpx;
    transition: width 0.3s ease;
  }
  
  .progress-info {
    text-align: center;
  }
  
  .progress-text {
    font-size: 24rpx;
    opacity: 0.9;
  }
  
  .menu-section {
    padding: 30rpx;
  }
  
  .menu-group {
    margin-bottom: 40rpx;
  }
  
  .group-title {
    margin-bottom: 20rpx;
  }
  
  .title-text {
    font-size: 28rpx;
    font-weight: 600;
    color: #333333;
  }
  
  .menu-list {
    background: #ffffff;
    border-radius: 16rpx;
    overflow: hidden;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  }
  
  .menu-item {
    display: flex;
    align-items: center;
    padding: 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .menu-item:last-child {
    border-bottom: none;
  }
  
  .menu-item:active {
    background-color: #f8f9fa;
  }
  
  .menu-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 25rpx;
  }
  
  .menu-icon.study {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .menu-icon.favorite {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }
  
  .menu-icon.plan {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }
  
  .menu-icon.achievement {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  }
  
  .menu-icon.profile {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  }
  
  .menu-icon.security {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  }
  
  .menu-icon.vip {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  }
  
  .menu-icon.settings {
    background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
  }
  
  .menu-icon.notification {
    background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
  }
  
  .menu-icon.theme {
    background: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);
  }
  
  .menu-icon.feedback {
    background: linear-gradient(135deg, #e0c3fc 0%, #9bb5ff 100%);
  }
  
  .menu-icon.about {
    background: linear-gradient(135deg, #a8caba 0%, #5d4e75 100%);
  }
  
  .menu-icon.share {
    background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
  }
  
  .icon-text {
    font-size: 32rpx;
    color: #ffffff;
  }
  
  .menu-content {
    flex: 1;
  }
  
  .menu-title {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 5rpx;
  }
  
  .menu-desc {
    font-size: 24rpx;
    color: #666666;
  }
  
  .menu-arrow {
    width: 40rpx;
    text-align: center;
  }
  
  .arrow-icon {
    font-size: 28rpx;
    color: #cccccc;
  }
  
  .logout-section {
    padding: 0 30rpx 30rpx;
  }
  
  .logout-btn {
    width: 100%;
    height: 80rpx;
    background: #ffffff;
    color: #ff4757;
    border: 2rpx solid #ff4757;
    border-radius: 40rpx;
    font-size: 28rpx;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .logout-btn:active {
    background: #ff4757;
    color: #ffffff;
  }
  
  .version-info {
    text-align: center;
    padding-bottom: 40rpx;
  }
  
  .version-text {
    font-size: 24rpx;
    color: #999999;
  }
  
  .avatar-modal {
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
    padding: 40rpx 30rpx;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
    padding-bottom: 20rpx;
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
  
  .avatar-options {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }
  
  .option-item {
    display: flex;
    align-items: center;
    padding: 30rpx;
    background: #f8f9fa;
    border-radius: 16rpx;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .option-item:active {
    background-color: #e9ecef;
  }
  
  .option-icon {
    width: 60rpx;
    height: 60rpx;
    background: #007aff;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 25rpx;
  }
  
  .option-icon .icon-text {
    font-size: 28rpx;
    color: #ffffff;
  }
  
  .option-text {
    font-size: 30rpx;
    color: #333333;
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .user-stats {
      flex-wrap: wrap;
      gap: 20rpx;
    }
    
    .stat-divider {
      display: none;
    }
    
    .menu-icon {
      width: 60rpx;
      height: 60rpx;
    }
    
    .icon-text {
      font-size: 24rpx;
    }
  }
</style>