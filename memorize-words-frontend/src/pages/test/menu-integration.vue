<template>
  <view class="menu-test-page">
    <view class="header">
      <text class="title">菜单系统集成测试</text>
      <button class="refresh-btn" @tap="refreshMenus">刷新菜单</button>
    </view>
    
    <!-- API模式切换 -->
    <view class="api-mode-section">
      <text class="section-title">API模式设置</text>
      <view class="mode-controls">
        <button 
          class="mode-btn" 
          :class="{ active: useBackendApi }"
          @tap="setApiMode(true)"
        >
          后端API
        </button>
        <button 
          class="mode-btn" 
          :class="{ active: !useBackendApi }"
          @tap="setApiMode(false)"
        >
          本地配置
        </button>
      </view>
    </view>
    
    <!-- 用户信息 -->
    <view class="user-info-section">
      <text class="section-title">用户信息</text>
      <view class="user-details">
        <text>用户ID: {{ userInfo?.id || '未登录' }}</text>
        <text>用户名: {{ userInfo?.username || '未知' }}</text>
        <text>角色: {{ userInfo?.role || 'student' }}</text>
        <text>认证状态: {{ isAuthenticated ? '已认证' : '未认证' }}</text>
      </view>
    </view>
    
    <!-- 菜单数据展示 -->
    <view class="menu-sections">
      <!-- 主菜单 -->
      <view class="menu-section">
        <text class="section-title">主菜单 ({{ mainMenus.length }})</text>
        <view class="menu-list">
          <view 
            v-for="menu in mainMenus" 
            :key="menu.id"
            class="menu-item"
            @tap="testMenuAccess(menu)"
          >
            <text class="menu-icon">{{ getIconText(menu.icon) }}</text>
            <view class="menu-info">
              <text class="menu-title">{{ menu.title }}</text>
              <text class="menu-path">{{ menu.path }}</text>
              <text class="menu-permission">权限: {{ menu.permission || '无' }}</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 底部菜单 -->
      <view class="menu-section">
        <text class="section-title">底部菜单 ({{ bottomMenus.length }})</text>
        <view class="menu-list">
          <view 
            v-for="menu in bottomMenus" 
            :key="menu.id"
            class="menu-item"
            @tap="testMenuAccess(menu)"
          >
            <text class="menu-icon">{{ getIconText(menu.icon) }}</text>
            <view class="menu-info">
              <text class="menu-title">{{ menu.title }}</text>
              <text class="menu-path">{{ menu.path }}</text>
              <text class="menu-permission">权限: {{ menu.permission || '无' }}</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 工具菜单 -->
      <view class="menu-section">
        <text class="section-title">工具菜单 ({{ toolMenus.length }})</text>
        <view class="menu-list">
          <view 
            v-for="menu in toolMenus" 
            :key="menu.id"
            class="menu-item"
            @tap="testMenuAccess(menu)"
          >
            <text class="menu-icon">{{ getIconText(menu.icon) }}</text>
            <view class="menu-info">
              <text class="menu-title">{{ menu.title }}</text>
              <text class="menu-path">{{ menu.path }}</text>
              <text class="menu-permission">权限: {{ menu.permission || '无' }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- API测试结果 -->
    <view class="api-test-section">
      <text class="section-title">API测试结果</text>
      <view class="test-results">
        <text class="result-text">{{ apiTestResult }}</text>
      </view>
    </view>
    
    <!-- 错误信息 -->
    <view v-if="errorMessage" class="error-section">
      <text class="error-title">错误信息</text>
      <text class="error-text">{{ errorMessage }}</text>
    </view>
  </view>
</template>

<script>
import menuManager from '@/utils/menuManager.js'
import { menuApiService } from '@/utils/apiService.js'

export default {
  name: 'MenuIntegrationTest',
  data() {
    return {
      useBackendApi: true,
      userInfo: null,
      isAuthenticated: false,
      mainMenus: [],
      bottomMenus: [],
      toolMenus: [],
      apiTestResult: '等待测试...',
      errorMessage: ''
    }
  },
  mounted() {
    this.loadUserInfo()
    this.loadMenus()
    this.testApiConnection()
  },
  methods: {
    /**
     * 加载用户信息
     */
    loadUserInfo() {
      try {
        this.userInfo = menuManager.getCurrentUser()
        this.isAuthenticated = menuManager.isAuthenticated()
      } catch (error) {
        console.error('加载用户信息失败:', error)
        this.errorMessage = `加载用户信息失败: ${error.message}`
      }
    },
    
    /**
     * 加载菜单数据
     */
    async loadMenus() {
      try {
        uni.showLoading({ title: '加载菜单...' })
        
        const [mainMenus, bottomMenus, toolMenus] = await Promise.all([
          menuManager.getMainMenus(),
          menuManager.getBottomMenus(),
          menuManager.getToolMenus()
        ])
        
        this.mainMenus = mainMenus
        this.bottomMenus = bottomMenus
        this.toolMenus = toolMenus
        
        uni.hideLoading()
        
      } catch (error) {
        uni.hideLoading()
        console.error('加载菜单失败:', error)
        this.errorMessage = `加载菜单失败: ${error.message}`
      }
    },
    
    /**
     * 刷新菜单
     */
    async refreshMenus() {
      try {
        await menuManager.refreshMenus()
        await this.loadMenus()
        
        uni.showToast({
          title: '菜单已刷新',
          icon: 'success'
        })
      } catch (error) {
        console.error('刷新菜单失败:', error)
        uni.showToast({
          title: '刷新失败',
          icon: 'error'
        })
      }
    },
    
    /**
     * 设置API模式
     */
    async setApiMode(useBackend) {
      try {
        this.useBackendApi = useBackend
        menuManager.setApiMode(useBackend, true)
        
        // 重新加载菜单
        await this.loadMenus()
        
        uni.showToast({
          title: useBackend ? '已切换到后端API' : '已切换到本地配置',
          icon: 'success'
        })
      } catch (error) {
        console.error('切换API模式失败:', error)
        uni.showToast({
          title: '切换失败',
          icon: 'error'
        })
      }
    },
    
    /**
     * 测试API连接
     */
    async testApiConnection() {
      try {
        if (!this.userInfo?.id) {
          this.apiTestResult = 'API测试跳过: 用户未登录'
          return
        }
        
        // 测试获取用户菜单API
        const response = await menuApiService.getFrontendMenusForUser(this.userInfo.id)
        this.apiTestResult = `API连接成功: 获取到 ${response.data?.length || 0} 个菜单项`
        
      } catch (error) {
        console.error('API测试失败:', error)
        this.apiTestResult = `API连接失败: ${error.message}`
      }
    },
    
    /**
     * 测试菜单访问权限
     */
    async testMenuAccess(menu) {
      try {
        if (!this.userInfo?.id || !menu.id) {
          uni.showToast({
            title: '无法测试权限',
            icon: 'none'
          })
          return
        }
        
        uni.showLoading({ title: '检查权限...' })
        
        const hasAccess = await menuManager.checkBackendMenuAccess(menu.id)
        
        uni.hideLoading()
        uni.showModal({
          title: '权限检查结果',
          content: `菜单: ${menu.title}\n权限: ${hasAccess ? '有权限' : '无权限'}`,
          showCancel: false
        })
        
      } catch (error) {
        uni.hideLoading()
        console.error('权限检查失败:', error)
        uni.showToast({
          title: '权限检查失败',
          icon: 'error'
        })
      }
    },
    
    /**
     * 获取图标文本
     */
    getIconText(icon) {
      const iconMap = {
        'home': '🏠',
        'book': '📚',
        'user': '👤',
        'settings': '⚙️',
        'community': '👥',
        'tools': '🔧',
        'api': '🔌',
        'monitor': '📊'
      }
      return iconMap[icon] || '📱'
    }
  }
}
</script>

<style lang="scss" scoped>
.menu-test-page {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .title {
    font-size: 20px;
    font-weight: bold;
    color: #333;
  }
  
  .refresh-btn {
    padding: 8px 16px;
    background: #007AFF;
    color: white;
    border-radius: 4px;
    font-size: 14px;
  }
}

.api-mode-section {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  
  .mode-controls {
    display: flex;
    gap: 10px;
    margin-top: 10px;
    
    .mode-btn {
      flex: 1;
      padding: 10px;
      background: #f0f0f0;
      border-radius: 4px;
      text-align: center;
      font-size: 14px;
      
      &.active {
        background: #007AFF;
        color: white;
      }
    }
  }
}

.user-info-section {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  
  .user-details {
    margin-top: 10px;
    
    text {
      display: block;
      margin-bottom: 5px;
      font-size: 14px;
      color: #666;
    }
  }
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.menu-sections {
  .menu-section {
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    
    .menu-list {
      .menu-item {
        display: flex;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #f0f0f0;
        
        &:last-child {
          border-bottom: none;
        }
        
        .menu-icon {
          font-size: 20px;
          margin-right: 10px;
        }
        
        .menu-info {
          flex: 1;
          
          .menu-title {
            display: block;
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 2px;
          }
          
          .menu-path {
            display: block;
            font-size: 12px;
            color: #999;
            margin-bottom: 2px;
          }
          
          .menu-permission {
            display: block;
            font-size: 12px;
            color: #666;
          }
        }
      }
    }
  }
}

.api-test-section {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  
  .test-results {
    margin-top: 10px;
    
    .result-text {
      font-size: 14px;
      color: #666;
    }
  }
}

.error-section {
  background: #ffebee;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #f44336;
  
  .error-title {
    display: block;
    font-size: 16px;
    font-weight: bold;
    color: #d32f2f;
    margin-bottom: 5px;
  }
  
  .error-text {
    font-size: 14px;
    color: #d32f2f;
  }
}
</style>