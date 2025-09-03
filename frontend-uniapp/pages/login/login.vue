<template>
  <view class="login-container">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>
    
    <!-- 登录表单 -->
    <view class="login-form">
      <!-- Logo和标题 -->
      <view class="header">
        <image class="logo" src="/static/images/logo.png" mode="aspectFit"></image>
        <text class="title">英语学习平台</text>
        <text class="subtitle">让学习更简单，让进步更明显</text>
      </view>
      
      <!-- 表单内容 -->
      <view class="form-content">
        <!-- 用户名输入 -->
        <view class="input-group">
          <view class="input-wrapper">
            <text class="input-icon">👤</text>
            <input 
              class="input" 
              type="text" 
              placeholder="请输入用户名/邮箱/手机号"
              v-model="loginForm.username"
              :disabled="loading"
            />
          </view>
        </view>
        
        <!-- 密码输入 -->
        <view class="input-group">
          <view class="input-wrapper">
            <text class="input-icon">🔒</text>
            <input 
              class="input" 
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              v-model="loginForm.password"
              :disabled="loading"
            />
            <text 
              class="password-toggle" 
              @tap="togglePassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </text>
          </view>
        </view>
        
        <!-- 记住密码和忘记密码 -->
        <view class="form-options">
          <view class="remember-password" @tap="toggleRemember">
            <text class="checkbox" :class="{ checked: rememberPassword }">✓</text>
            <text class="option-text">记住密码</text>
          </view>
          <text class="forgot-password" @tap="handleForgotPassword">忘记密码？</text>
        </view>
        
        <!-- 登录按钮 -->
        <button 
          class="login-btn" 
          :class="{ disabled: !canLogin || loading }"
          :disabled="!canLogin || loading"
          @tap="handleLogin"
        >
          <text v-if="loading">登录中...</text>
          <text v-else>登录</text>
        </button>
        
        <!-- 快速登录 -->
        <view class="quick-login">
          <view class="divider">
            <text class="divider-text">其他登录方式</text>
          </view>
          <view class="quick-login-methods">
            <view class="login-method" @tap="handleWechatLogin">
              <text class="method-icon">💬</text>
              <text class="method-text">微信</text>
            </view>
            <view class="login-method" @tap="handleQQLogin">
              <text class="method-icon">🐧</text>
              <text class="method-text">QQ</text>
            </view>
            <view class="login-method" @tap="handleGuestLogin">
              <text class="method-icon">👤</text>
              <text class="method-text">游客</text>
            </view>
          </view>
        </view>
        
        <!-- 注册链接 -->
        <view class="register-link">
          <text class="register-text">还没有账号？</text>
          <text class="register-btn" @tap="handleRegister">立即注册</text>
        </view>
      </view>
    </view>
    
    <!-- 版本信息 -->
    <view class="version-info">
      <text class="version-text">版本 1.0.0</text>
    </view>
  </view>
</template>

<script>
  import { mapActions } from 'vuex'
  
  export default {
    name: 'Login',
    data() {
      return {
        loginForm: {
          username: '',
          password: ''
        },
        showPassword: false,
        rememberPassword: false,
        loading: false
      }
    },
    computed: {
      canLogin() {
        return this.loginForm.username.trim() && this.loginForm.password.trim()
      }
    },
    onLoad() {
      this.loadSavedCredentials()
    },
    onShow() {
      // 检查是否已登录
      this.checkLoginStatus()
    },
    methods: {
      ...mapActions('user', ['login', 'checkLoginStatus']),
      ...mapActions('app', ['showToast', 'showModal']),
      
      // 加载保存的登录凭据
      loadSavedCredentials() {
        const savedUsername = uni.getStorageSync('savedUsername')
        const savedPassword = uni.getStorageSync('savedPassword')
        
        if (savedUsername) {
          this.loginForm.username = savedUsername
          this.rememberPassword = true
        }
        
        if (savedPassword && this.rememberPassword) {
          this.loginForm.password = savedPassword
        }
      },
      
      // 检查登录状态
      async checkLoginStatus() {
        try {
          const isLoggedIn = await this.checkLoginStatus()
          if (isLoggedIn) {
            // 已登录，跳转到首页
            uni.switchTab({
              url: '/pages/word/word'
            })
          }
        } catch (error) {
          console.log('未登录或登录已过期')
        }
      },
      
      // 切换密码显示
      togglePassword() {
        this.showPassword = !this.showPassword
      },
      
      // 切换记住密码
      toggleRemember() {
        this.rememberPassword = !this.rememberPassword
      },
      
      // 处理登录
      async handleLogin() {
        if (!this.canLogin || this.loading) return
        
        this.loading = true
        
        try {
          // 表单验证
          if (!this.validateForm()) {
            return
          }
          
          // 执行登录
          await this.login(this.loginForm)
          
          // 保存登录凭据
          if (this.rememberPassword) {
            uni.setStorageSync('savedUsername', this.loginForm.username)
            uni.setStorageSync('savedPassword', this.loginForm.password)
          } else {
            uni.removeStorageSync('savedUsername')
            uni.removeStorageSync('savedPassword')
          }
          
          // 登录成功提示
          this.showToast({
            title: '登录成功',
            icon: 'success'
          })
          
          // 跳转到首页
          setTimeout(() => {
            uni.switchTab({
              url: '/pages/word/word'
            })
          }, 1000)
          
        } catch (error) {
          console.error('登录失败:', error)
          this.showToast({
            title: error.message || '登录失败，请重试',
            icon: 'none'
          })
        } finally {
          this.loading = false
        }
      },
      
      // 表单验证
      validateForm() {
        const { username, password } = this.loginForm
        
        if (!username.trim()) {
          this.showToast({
            title: '请输入用户名',
            icon: 'none'
          })
          return false
        }
        
        if (!password.trim()) {
          this.showToast({
            title: '请输入密码',
            icon: 'none'
          })
          return false
        }
        
        if (password.length < 6) {
          this.showToast({
            title: '密码长度不能少于6位',
            icon: 'none'
          })
          return false
        }
        
        return true
      },
      
      // 处理忘记密码
      handleForgotPassword() {
        uni.navigateTo({
          url: '/pages/auth/forgot-password'
        })
      },
      
      // 处理注册
      handleRegister() {
        uni.navigateTo({
          url: '/pages/auth/register'
        })
      },
      
      // 微信登录
      async handleWechatLogin() {
        try {
          // 检查微信登录环境
          if (uni.getSystemInfoSync().platform === 'mp-weixin') {
            // 小程序环境
            uni.login({
              provider: 'weixin',
              success: (res) => {
                console.log('微信登录成功:', res)
                // 处理微信登录逻辑
              },
              fail: (err) => {
                console.error('微信登录失败:', err)
                this.showToast({
                  title: '微信登录失败',
                  icon: 'none'
                })
              }
            })
          } else {
            this.showToast({
              title: '当前环境不支持微信登录',
              icon: 'none'
            })
          }
        } catch (error) {
          console.error('微信登录错误:', error)
          this.showToast({
            title: '微信登录失败',
            icon: 'none'
          })
        }
      },
      
      // QQ登录
      async handleQQLogin() {
        this.showToast({
          title: 'QQ登录功能开发中',
          icon: 'none'
        })
      },
      
      // 游客登录
      async handleGuestLogin() {
        try {
          const confirmed = await this.showModal({
            title: '游客登录',
            content: '游客模式下部分功能受限，确定要以游客身份登录吗？'
          })
          
          if (confirmed) {
            // 设置游客登录状态
            uni.setStorageSync('isGuest', true)
            uni.setStorageSync('guestId', 'guest_' + Date.now())
            
            this.showToast({
              title: '游客登录成功',
              icon: 'success'
            })
            
            setTimeout(() => {
              uni.switchTab({
                url: '/pages/word/word'
              })
            }, 1000)
          }
        } catch (error) {
          console.error('游客登录失败:', error)
        }
      }
    }
  }
</script>

<style>
  .login-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40rpx 30rpx;
  }
  
  .bg-decoration {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
    z-index: 0;
  }
  
  .circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    animation: float 6s ease-in-out infinite;
  }
  
  .circle-1 {
    width: 200rpx;
    height: 200rpx;
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }
  
  .circle-2 {
    width: 150rpx;
    height: 150rpx;
    top: 60%;
    right: 15%;
    animation-delay: 2s;
  }
  
  .circle-3 {
    width: 100rpx;
    height: 100rpx;
    top: 30%;
    right: 30%;
    animation-delay: 4s;
  }
  
  @keyframes float {
    0%, 100% {
      transform: translateY(0px) rotate(0deg);
    }
    50% {
      transform: translateY(-20px) rotate(180deg);
    }
  }
  
  .login-form {
    width: 100%;
    max-width: 600rpx;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20rpx;
    padding: 60rpx 40rpx;
    box-shadow: 0 20rpx 40rpx rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    z-index: 1;
  }
  
  .header {
    text-align: center;
    margin-bottom: 60rpx;
  }
  
  .logo {
    width: 120rpx;
    height: 120rpx;
    margin-bottom: 20rpx;
  }
  
  .title {
    display: block;
    font-size: 48rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 10rpx;
  }
  
  .subtitle {
    display: block;
    font-size: 28rpx;
    color: #666666;
  }
  
  .form-content {
    width: 100%;
  }
  
  .input-group {
    margin-bottom: 30rpx;
  }
  
  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    background: #f8f9fa;
    border-radius: 12rpx;
    border: 2rpx solid #e9ecef;
    transition: all 0.3s ease;
  }
  
  .input-wrapper:focus-within {
    border-color: #007aff;
    background: #ffffff;
    box-shadow: 0 0 0 4rpx rgba(0, 122, 255, 0.1);
  }
  
  .input-icon {
    padding: 0 20rpx;
    font-size: 32rpx;
    color: #999999;
  }
  
  .input {
    flex: 1;
    padding: 25rpx 20rpx;
    font-size: 30rpx;
    color: #333333;
    background: transparent;
    border: none;
    outline: none;
  }
  
  .input::placeholder {
    color: #999999;
  }
  
  .password-toggle {
    padding: 0 20rpx;
    font-size: 32rpx;
    color: #999999;
    cursor: pointer;
  }
  
  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40rpx;
  }
  
  .remember-password {
    display: flex;
    align-items: center;
    cursor: pointer;
  }
  
  .checkbox {
    width: 32rpx;
    height: 32rpx;
    border: 2rpx solid #ddd;
    border-radius: 6rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15rpx;
    font-size: 20rpx;
    color: transparent;
    transition: all 0.3s ease;
  }
  
  .checkbox.checked {
    background: #007aff;
    border-color: #007aff;
    color: #ffffff;
  }
  
  .option-text {
    font-size: 28rpx;
    color: #666666;
  }
  
  .forgot-password {
    font-size: 28rpx;
    color: #007aff;
    cursor: pointer;
  }
  
  .login-btn {
    width: 100%;
    padding: 25rpx;
    background: linear-gradient(135deg, #007aff 0%, #5856d6 100%);
    color: #ffffff;
    border: none;
    border-radius: 12rpx;
    font-size: 32rpx;
    font-weight: 600;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 40rpx;
  }
  
  .login-btn:active {
    transform: translateY(2rpx);
    box-shadow: 0 4rpx 8rpx rgba(0, 122, 255, 0.3);
  }
  
  .login-btn.disabled {
    background: #cccccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  .quick-login {
    margin-bottom: 40rpx;
  }
  
  .divider {
    position: relative;
    text-align: center;
    margin-bottom: 30rpx;
  }
  
  .divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1rpx;
    background: #e9ecef;
  }
  
  .divider-text {
    background: rgba(255, 255, 255, 0.95);
    padding: 0 20rpx;
    font-size: 24rpx;
    color: #999999;
  }
  
  .quick-login-methods {
    display: flex;
    justify-content: center;
    gap: 40rpx;
  }
  
  .login-method {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .login-method:active {
    transform: scale(0.95);
  }
  
  .method-icon {
    width: 80rpx;
    height: 80rpx;
    background: #f8f9fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36rpx;
    margin-bottom: 10rpx;
    border: 2rpx solid #e9ecef;
  }
  
  .method-text {
    font-size: 24rpx;
    color: #666666;
  }
  
  .register-link {
    text-align: center;
  }
  
  .register-text {
    font-size: 28rpx;
    color: #666666;
  }
  
  .register-btn {
    font-size: 28rpx;
    color: #007aff;
    font-weight: 600;
    cursor: pointer;
    margin-left: 10rpx;
  }
  
  .version-info {
    position: absolute;
    bottom: 40rpx;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1;
  }
  
  .version-text {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.7);
  }
  
  /* 响应式设计 */
  @media screen and (max-width: 750rpx) {
    .login-form {
      padding: 40rpx 30rpx;
    }
    
    .title {
      font-size: 42rpx;
    }
    
    .subtitle {
      font-size: 26rpx;
    }
    
    .input {
      padding: 20rpx 15rpx;
      font-size: 28rpx;
    }
    
    .login-btn {
      padding: 20rpx;
      font-size: 30rpx;
    }
  }
</style>