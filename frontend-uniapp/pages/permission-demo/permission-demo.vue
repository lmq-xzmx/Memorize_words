<template>
  <BaseLayout 
    title="权限控制演示"
    :show-header="true"
    :show-sidebar="false"
    :show-tab-bar="true"
    layout-type="default"
    @menu-click="handleMenuClick"
  >
    <view class="permission-demo">
      <!-- 用户信息 -->
      <view class="user-section">
        <view class="section-title">当前用户信息</view>
        <view class="user-card">
          <view class="user-info">
            <text class="user-name">{{ displayName }}</text>
            <text class="user-role">角色: {{ currentRole || '未设置' }}</text>
            <text class="login-status">登录状态: {{ isLoggedIn ? '已登录' : '未登录' }}</text>
          </view>
          <view class="user-actions">
            <button 
              class="btn btn-primary" 
              @click="switchRole('student')"
              :disabled="currentRole === 'student'"
            >
              切换为学生
            </button>
            <button 
              class="btn btn-primary" 
              @click="switchRole('teacher')"
              :disabled="currentRole === 'teacher'"
            >
              切换为教师
            </button>
            <button 
              class="btn btn-primary" 
              @click="switchRole('admin')"
              :disabled="currentRole === 'admin'"
            >
              切换为管理员
            </button>
          </view>
        </view>
      </view>
      
      <!-- 权限指令演示 -->
      <view class="directive-section">
        <view class="section-title">权限指令演示</view>
        
        <!-- 角色权限 -->
        <view class="demo-group">
          <view class="group-title">角色权限控制</view>
          <view class="demo-items">
            <view class="demo-item" v-role="'student'">
              <text class="item-label">学生可见</text>
              <text class="item-desc">只有学生角色可以看到此内容</text>
            </view>
            <view class="demo-item" v-teacher>
              <text class="item-label">教师可见</text>
              <text class="item-desc">只有教师及以上角色可以看到此内容</text>
            </view>
            <view class="demo-item" v-admin>
              <text class="item-label">管理员可见</text>
              <text class="item-desc">只有管理员可以看到此内容</text>
            </view>
          </view>
        </view>
        
        <!-- 功能权限 -->
        <view class="demo-group">
          <view class="group-title">功能权限控制</view>
          <view class="demo-items">
            <view class="demo-item" v-permission="'word:create'">
              <text class="item-label">创建单词</text>
              <text class="item-desc">需要创建单词权限</text>
            </view>
            <view class="demo-item" v-permission="'word:edit'">
              <text class="item-label">编辑单词</text>
              <text class="item-desc">需要编辑单词权限</text>
            </view>
            <view class="demo-item" v-permission="'word:delete'">
              <text class="item-label">删除单词</text>
              <text class="item-desc">需要删除单词权限</text>
            </view>
          </view>
        </view>
        
        <!-- 菜单权限 -->
        <view class="demo-group">
          <view class="group-title">菜单权限控制</view>
          <view class="demo-items">
            <view class="demo-item" v-permission:menu="'vocabulary_management'">
              <text class="item-label">词汇管理</text>
              <text class="item-desc">需要词汇管理菜单权限</text>
            </view>
            <view class="demo-item" v-permission:menu="'user_management'">
              <text class="item-label">用户管理</text>
              <text class="item-desc">需要用户管理菜单权限</text>
            </view>
            <view class="demo-item" v-permission:menu="'system_settings'">
              <text class="item-label">系统设置</text>
              <text class="item-desc">需要系统设置菜单权限</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 编程式权限检查 -->
      <view class="programmatic-section">
        <view class="section-title">编程式权限检查</view>
        <view class="check-group">
          <view class="check-item">
            <text class="check-label">当前页面权限:</text>
            <text class="check-result" :class="{ success: hasCurrentPagePermission, error: !hasCurrentPagePermission }">
              {{ hasCurrentPagePermission ? '有权限' : '无权限' }}
            </text>
          </view>
          <view class="check-item">
            <text class="check-label">是否为管理员:</text>
            <text class="check-result" :class="{ success: isAdmin(), error: !isAdmin() }">
              {{ isAdmin() ? '是' : '否' }}
            </text>
          </view>
          <view class="check-item">
            <text class="check-label">是否为教师:</text>
            <text class="check-result" :class="{ success: isTeacher(), error: !isTeacher() }">
              {{ isTeacher() ? '是' : '否' }}
            </text>
          </view>
          <view class="check-item">
            <text class="check-label">是否为学生:</text>
            <text class="check-result" :class="{ success: isStudent(), error: !isStudent() }">
              {{ isStudent() ? '是' : '否' }}
            </text>
          </view>
        </view>
      </view>
      
      <!-- 安全导航演示 -->
      <view class="navigation-section">
        <view class="section-title">安全导航演示</view>
        <view class="nav-buttons">
          <button class="btn btn-outline" @click="testSafeNavigation('/pages/admin/admin')">
            访问管理页面
          </button>
          <button class="btn btn-outline" @click="testSafeNavigation('/pages/teacher/teacher')">
            访问教师页面
          </button>
          <button class="btn btn-outline" @click="testSafeNavigation('/pages/student/student')">
            访问学生页面
          </button>
        </view>
      </view>
      
      <!-- 权限测试 -->
      <view class="test-section">
        <view class="section-title">权限测试</view>
        <view class="test-buttons">
          <button class="btn btn-success" @click="testPermission('word:create')">
            测试创建权限
          </button>
          <button class="btn btn-warning" @click="testPermission('word:edit')">
            测试编辑权限
          </button>
          <button class="btn btn-danger" @click="testPermission('word:delete')">
            测试删除权限
          </button>
        </view>
      </view>
    </view>
  </BaseLayout>
</template>

<script>
import permissionMixin from '@/mixins/permissionMixin'
import { mapActions } from 'vuex'

export default {
  name: 'PermissionDemo',
  mixins: [permissionMixin],
  
  methods: {
    ...mapActions('permission', ['setCurrentRole']),
    
    // 处理菜单点击
    handleMenuClick(menuItem) {
      console.log('菜单点击:', menuItem)
    },
    
    // 切换角色
    async switchRole(role) {
      try {
        await this.setCurrentRole(role)
        uni.showToast({
          title: `已切换为${role}角色`,
          icon: 'success'
        })
        
        // 强制更新页面
        this.$forceUpdate()
      } catch (error) {
        console.error('切换角色失败:', error)
        uni.showToast({
          title: '切换角色失败',
          icon: 'error'
        })
      }
    },
    
    // 测试安全导航
    async testSafeNavigation(path) {
      const result = await this.safeNavigate({
        url: path,
        method: 'navigateTo'
      })
      
      if (!result) {
        uni.showToast({
          title: '导航被拦截',
          icon: 'none'
        })
      }
    },
    
    // 测试权限
    testPermission(permission) {
      const hasPermission = this.hasPermission(permission)
      
      uni.showModal({
        title: '权限测试结果',
        content: `权限 "${permission}" ${hasPermission ? '检查通过' : '检查失败'}`,
        showCancel: false
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.permission-demo {
  padding: 32rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
  padding-bottom: 16rpx;
  border-bottom: 2rpx solid #e0e0e0;
}

.user-section {
  margin-bottom: 40rpx;
  
  .user-card {
    background-color: white;
    border-radius: 16rpx;
    padding: 32rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
    
    .user-info {
      margin-bottom: 24rpx;
      
      .user-name {
        display: block;
        font-size: 36rpx;
        font-weight: 600;
        color: #333;
        margin-bottom: 12rpx;
      }
      
      .user-role,
      .login-status {
        display: block;
        font-size: 28rpx;
        color: #666;
        margin-bottom: 8rpx;
      }
    }
    
    .user-actions {
      display: flex;
      gap: 16rpx;
      flex-wrap: wrap;
    }
  }
}

.directive-section {
  margin-bottom: 40rpx;
  
  .demo-group {
    background-color: white;
    border-radius: 16rpx;
    padding: 32rpx;
    margin-bottom: 24rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
    
    .group-title {
      font-size: 28rpx;
      font-weight: 600;
      color: #555;
      margin-bottom: 20rpx;
    }
    
    .demo-items {
      .demo-item {
        padding: 20rpx;
        margin-bottom: 16rpx;
        background-color: #f8f9fa;
        border-radius: 12rpx;
        border-left: 6rpx solid #007bff;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .item-label {
          display: block;
          font-size: 28rpx;
          font-weight: 600;
          color: #333;
          margin-bottom: 8rpx;
        }
        
        .item-desc {
          display: block;
          font-size: 24rpx;
          color: #666;
        }
      }
    }
  }
}

.programmatic-section {
  margin-bottom: 40rpx;
  
  .check-group {
    background-color: white;
    border-radius: 16rpx;
    padding: 32rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
    
    .check-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16rpx 0;
      border-bottom: 1rpx solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .check-label {
        font-size: 28rpx;
        color: #333;
      }
      
      .check-result {
        font-size: 28rpx;
        font-weight: 600;
        
        &.success {
          color: #28a745;
        }
        
        &.error {
          color: #dc3545;
        }
      }
    }
  }
}

.navigation-section,
.test-section {
  margin-bottom: 40rpx;
  
  .nav-buttons,
  .test-buttons {
    background-color: white;
    border-radius: 16rpx;
    padding: 32rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
    display: flex;
    gap: 16rpx;
    flex-wrap: wrap;
  }
}

.btn {
  padding: 16rpx 32rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  
  &.btn-primary {
    background-color: #007bff;
    color: white;
    
    &:disabled {
      background-color: #6c757d;
      opacity: 0.6;
    }
  }
  
  &.btn-outline {
    background-color: transparent;
    color: #007bff;
    border: 2rpx solid #007bff;
  }
  
  &.btn-success {
    background-color: #28a745;
    color: white;
  }
  
  &.btn-warning {
    background-color: #ffc107;
    color: #212529;
  }
  
  &.btn-danger {
    background-color: #dc3545;
    color: white;
  }
  
  &:active {
    transform: scale(0.98);
  }
}
</style>