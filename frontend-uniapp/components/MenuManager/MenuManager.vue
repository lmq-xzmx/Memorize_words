<template>
  <view class="menu-manager">
    <!-- 菜单加载状态 -->
    <view v-if="loading" class="loading-container">
      <uni-load-more status="loading" :content-text="loadingText"></uni-load-more>
    </view>
    
    <!-- 菜单内容 -->
    <view v-else class="menu-content">
      <!-- 动态菜单组件 -->
      <DynamicMenu 
        :menu-type="menuType"
        :role="currentRole"
        :active-color="activeColor"
        :inactive-color="inactiveColor"
        @menu-click="handleMenuClick"
        @menu-error="handleMenuError"
      />
    </view>
    
    <!-- 错误提示 -->
    <view v-if="error" class="error-container">
      <view class="error-content">
        <uni-icons type="info" size="48" color="#ff6b6b"></uni-icons>
        <text class="error-message">{{ error }}</text>
        <button class="retry-button" @click="retryLoad">重试</button>
      </view>
    </view>
  </view>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import DynamicMenu from '@/components/DynamicMenu/DynamicMenu.vue'
import permissionService from '@/services/permissionService'

export default {
  name: 'MenuManager',
  components: {
    DynamicMenu
  },
  props: {
    menuType: {
      type: String,
      default: 'tabbar'
    },
    activeColor: {
      type: String,
      default: '#007AFF'
    },
    inactiveColor: {
      type: String,
      default: '#999'
    },
    autoInit: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      loadingText: {
        contentdown: '加载菜单中...',
        contentrefresh: '正在加载...',
        contentnomore: '加载完成'
      },
      retryCount: 0,
      maxRetries: 3
    }
  },
  computed: {
    ...mapState('permission', {
      currentRole: 'currentRole',
      permissionLoaded: 'permissionLoaded',
      menuTree: 'menuTree',
      slotConfig: 'slotConfig',
      menuConfig: 'menuConfig'
    }),
    
    ...mapState('user', {
      userInfo: 'userInfo',
      isLoggedIn: 'isLoggedIn'
    })
  },
  watch: {
    currentRole: {
      handler(newRole, oldRole) {
        if (newRole !== oldRole && newRole) {
          this.initializeMenuSystem()
        }
      }
    },
    
    isLoggedIn: {
      handler(newValue, oldValue) {
        if (newValue !== oldValue) {
          this.initializeMenuSystem()
        }
      }
    }
  },
  async mounted() {
    if (this.autoInit) {
      await this.initializeMenuSystem()
    }
  },
  methods: {
    ...mapActions('permission', [
      'loadPermissionData',
      'buildMenuTree',
      'setCurrentRole',
      'clearPermissionData'
    ]),
    
    ...mapActions('user', [
      'getUserInfo'
    ]),
    
    /**
     * 初始化菜单系统
     */
    async initializeMenuSystem() {
      try {
        this.loading = true
        this.error = null
        
        // 检查用户登录状态
        if (!this.isLoggedIn) {
          await this.initGuestMenu()
          return
        }
        
        // 获取用户信息
        if (!this.userInfo) {
          await this.getUserInfo()
        }
        
        // 设置用户角色
        const userRole = this.userInfo?.role || 'student'
        await this.setCurrentRole(userRole)
        
        // 初始化权限服务
        await this.initPermissionService()
        
        // 加载权限数据
        await this.loadPermissionData()
        
        // 构建菜单树
        await this.buildMenuTree()
        
        this.loading = false
        this.retryCount = 0
        
        // 触发菜单初始化完成事件
        this.$emit('menu-initialized', {
          role: userRole,
          menuTree: this.menuTree
        })
        
      } catch (error) {
        this.loading = false
        this.handleInitError(error)
      }
    },
    
    /**
     * 初始化游客菜单
     */
    async initGuestMenu() {
      try {
        await this.setCurrentRole('guest')
        
        // 设置游客默认菜单
        const guestMenuTree = [
          {
            id: 'word',
            name: '单词学习',
            title: '单词学习',
            level: 'root',
            icon: 'book',
            path: '/pages/word/word',
            children: []
          },
          {
            id: 'login',
            name: '登录',
            title: '登录',
            level: 'root',
            icon: 'person',
            path: '/pages/login/login',
            children: []
          }
        ]
        
        this.$store.commit('permission/SET_MENU_TREE', guestMenuTree)
        this.loading = false
        
      } catch (error) {
        this.loading = false
        this.handleInitError(error)
      }
    },
    
    /**
     * 初始化权限服务
     */
    async initPermissionService() {
      try {
        await permissionService.init()
      } catch (error) {
        console.error('权限服务初始化失败:', error)
        throw new Error('权限服务初始化失败')
      }
    },
    
    /**
     * 处理初始化错误
     */
    handleInitError(error) {
      console.error('菜单系统初始化失败:', error)
      
      this.retryCount++
      
      if (this.retryCount <= this.maxRetries) {
        this.error = `加载失败，正在重试 (${this.retryCount}/${this.maxRetries})`
        
        // 延迟重试
        setTimeout(() => {
          this.initializeMenuSystem()
        }, 2000 * this.retryCount)
      } else {
        this.error = '菜单加载失败，请检查网络连接后重试'
        
        // 使用本地缓存的菜单数据
        this.loadCachedMenu()
      }
      
      this.$emit('menu-error', error)
    },
    
    /**
     * 加载缓存的菜单数据
     */
    loadCachedMenu() {
      try {
        const cachedMenuTree = uni.getStorageSync('menuTree')
        const cachedRole = uni.getStorageSync('currentRole')
        
        if (cachedMenuTree && cachedRole) {
          this.$store.commit('permission/SET_MENU_TREE', cachedMenuTree)
          this.$store.commit('permission/SET_CURRENT_ROLE', cachedRole)
          
          this.error = null
          this.loading = false
          
          this.$showToast('已加载缓存菜单')
        }
      } catch (error) {
        console.error('加载缓存菜单失败:', error)
      }
    },
    
    /**
     * 重试加载
     */
    async retryLoad() {
      this.retryCount = 0
      await this.initializeMenuSystem()
    },
    
    /**
     * 处理菜单点击事件
     */
    handleMenuClick(menu) {
      this.$emit('menu-click', menu)
    },
    
    /**
     * 处理菜单错误事件
     */
    handleMenuError(error) {
      this.$emit('menu-error', error)
    },
    
    /**
     * 刷新菜单
     */
    async refreshMenu() {
      // 清除权限数据缓存
      await this.clearPermissionData()
      
      // 重新初始化
      await this.initializeMenuSystem()
    },
    
    /**
     * 切换用户角色
     */
    async switchRole(newRole) {
      try {
        this.loading = true
        
        await this.setCurrentRole(newRole)
        await this.buildMenuTree()
        
        this.loading = false
        
        this.$emit('role-switched', newRole)
        
      } catch (error) {
        this.loading = false
        this.handleInitError(error)
      }
    },
    
    /**
     * 获取当前菜单树
     */
    getCurrentMenuTree() {
      return this.menuTree
    },
    
    /**
     * 检查菜单权限
     */
    async checkMenuPermission(menuName, menuLevel) {
      try {
        return await permissionService.checkMenuPermission(menuName, menuLevel)
      } catch (error) {
        console.error('检查菜单权限失败:', error)
        return false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.menu-manager {
  width: 100%;
  height: 100%;
  position: relative;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200rpx;
  background-color: #fff;
}

.menu-content {
  width: 100%;
  height: 100%;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400rpx;
  background-color: #fff;
  
  .error-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40rpx;
    
    .error-message {
      margin: 24rpx 0;
      font-size: 28rpx;
      color: #666;
      text-align: center;
      line-height: 1.5;
    }
    
    .retry-button {
      padding: 16rpx 32rpx;
      background-color: #007AFF;
      color: #fff;
      border: none;
      border-radius: 8rpx;
      font-size: 28rpx;
      
      &:active {
        background-color: #0056CC;
      }
    }
  }
}
</style>