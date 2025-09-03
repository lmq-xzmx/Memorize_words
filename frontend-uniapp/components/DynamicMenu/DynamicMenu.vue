<template>
  <view class="dynamic-menu">
    <!-- 底部导航菜单 -->
    <view v-if="menuType === 'tabbar'" class="tabbar-menu">
      <view 
        v-for="menu in tabBarMenus" 
        :key="menu.id"
        class="tabbar-item"
        :class="{ active: currentPath === menu.path }"
        @click="navigateToMenu(menu)"
      >
        <view class="tabbar-icon">
          <uni-icons :type="menu.icon" size="24" :color="currentPath === menu.path ? activeColor : inactiveColor"></uni-icons>
        </view>
        <text class="tabbar-text" :style="{ color: currentPath === menu.path ? activeColor : inactiveColor }">{{ menu.title }}</text>
      </view>
    </view>

    <!-- 侧边菜单 -->
    <view v-else-if="menuType === 'sidebar'" class="sidebar-menu">
      <scroll-view scroll-y class="menu-scroll">
        <view v-for="menu in sidebarMenus" :key="menu.id" class="menu-group">
          <view 
            class="menu-item"
            :class="{ active: currentPath === menu.path, 'has-children': menu.children && menu.children.length > 0 }"
            @click="handleMenuClick(menu)"
          >
            <view class="menu-content">
              <uni-icons :type="menu.icon" size="20" color="#666"></uni-icons>
              <text class="menu-title">{{ menu.title }}</text>
              <uni-icons 
                v-if="menu.children && menu.children.length > 0" 
                :type="menu.expanded ? 'arrowup' : 'arrowdown'" 
                size="16" 
                color="#999"
                class="expand-icon"
              ></uni-icons>
            </view>
          </view>
          
          <!-- 子菜单 -->
          <view v-if="menu.children && menu.children.length > 0 && menu.expanded" class="submenu">
            <view 
              v-for="child in menu.children" 
              :key="child.id"
              class="submenu-item"
              :class="{ active: currentPath === child.path }"
              @click="navigateToMenu(child)"
            >
              <view class="submenu-content">
                <uni-icons :type="child.icon" size="16" color="#999"></uni-icons>
                <text class="submenu-title">{{ child.title }}</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 网格菜单 -->
    <view v-else-if="menuType === 'grid'" class="grid-menu">
      <view class="grid-container">
        <view 
          v-for="menu in gridMenus" 
          :key="menu.id"
          class="grid-item"
          @click="navigateToMenu(menu)"
        >
          <view class="grid-icon">
            <uni-icons :type="menu.icon" size="32" color="#007AFF"></uni-icons>
          </view>
          <text class="grid-title">{{ menu.title }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import permissionService from '@/services/permissionService'

export default {
  name: 'DynamicMenu',
  props: {
    menuType: {
      type: String,
      default: 'tabbar', // tabbar, sidebar, grid
      validator: value => ['tabbar', 'sidebar', 'grid'].includes(value)
    },
    role: {
      type: String,
      default: 'student'
    },
    activeColor: {
      type: String,
      default: '#007AFF'
    },
    inactiveColor: {
      type: String,
      default: '#999'
    }
  },
  data() {
    return {
      currentPath: '',
      menuTree: [],
      expandedMenus: new Set()
    }
  },
  computed: {
    ...mapState('permission', {
      storeMenuTree: 'menuTree',
      tabBarMenus: 'tabBarMenus',
      currentRole: 'currentRole',
      permissionLoaded: 'permissionLoaded'
    }),
    
    // 底部导航菜单
    tabBarMenus() {
      return this.menuTree.filter(menu => 
        menu.level === 'root' && 
        this.isMenuInTabBar(menu)
      ).slice(0, 5) // 最多5个底部菜单
    },
    
    // 侧边栏菜单
    sidebarMenus() {
      return this.menuTree.map(menu => ({
        ...menu,
        expanded: this.expandedMenus.has(menu.id)
      }))
    },
    
    // 网格菜单
    gridMenus() {
      const allMenus = []
      this.menuTree.forEach(menu => {
        allMenus.push(menu)
        if (menu.children && menu.children.length > 0) {
          allMenus.push(...menu.children)
        }
      })
      return allMenus
    }
  },
  watch: {
    role: {
      handler(newRole) {
        this.loadMenuData(newRole)
      },
      immediate: true
    },
    storeMenuTree: {
      handler(newMenuTree) {
        this.menuTree = newMenuTree || []
      },
      immediate: true
    }
  },
  async mounted() {
    this.getCurrentPath()
    await this.initializeMenu()
  },
  methods: {
    ...mapActions('permission', [
      'loadPermissionData',
      'buildMenuTree',
      'setCurrentRole'
    ]),
    
    /**
     * 初始化菜单
     */
    async initializeMenu() {
      try {
        this.$showLoading('加载菜单中...')
        
        // 设置当前角色
        await this.setCurrentRole(this.role)
        
        // 加载权限数据
        if (!this.permissionLoaded) {
          await this.loadPermissionData()
        }
        
        // 构建菜单树
        await this.buildMenuTree()
        
        this.$hideLoading()
      } catch (error) {
        this.$hideLoading()
        console.error('初始化菜单失败:', error)
        this.$showToast('菜单加载失败')
      }
    },
    
    /**
     * 加载菜单数据
     */
    async loadMenuData(role) {
      try {
        // 从权限服务生成菜单树
        const menuTree = permissionService.generateMenuTree(role)
        this.menuTree = menuTree
        
        // 更新store中的菜单树
        this.$store.commit('permission/SET_MENU_TREE', menuTree)
      } catch (error) {
        console.error('加载菜单数据失败:', error)
      }
    },
    
    /**
     * 获取当前页面路径
     */
    getCurrentPath() {
      const pages = getCurrentPages()
      if (pages.length > 0) {
        const currentPage = pages[pages.length - 1]
        this.currentPath = '/' + currentPage.route
      }
    },
    
    /**
     * 处理菜单点击
     */
    handleMenuClick(menu) {
      if (menu.children && menu.children.length > 0) {
        // 展开/收起子菜单
        this.toggleMenuExpansion(menu)
      } else {
        // 导航到菜单页面
        this.navigateToMenu(menu)
      }
    },
    
    /**
     * 切换菜单展开状态
     */
    toggleMenuExpansion(menu) {
      if (this.expandedMenus.has(menu.id)) {
        this.expandedMenus.delete(menu.id)
      } else {
        this.expandedMenus.add(menu.id)
      }
      this.$forceUpdate()
    },
    
    /**
     * 导航到菜单页面
     */
    async navigateToMenu(menu) {
      try {
        // 检查菜单权限
        const hasPermission = await this.checkMenuPermission(menu)
        if (!hasPermission) {
          this.$showToast('您没有访问此菜单的权限')
          return
        }
        
        // 更新当前路径
        this.currentPath = menu.path
        
        // 根据菜单类型进行导航
        if (this.isTabBarPage(menu.path)) {
          uni.switchTab({
            url: menu.path,
            fail: (err) => {
              console.error('切换TabBar失败:', err)
              this.$showToast('页面跳转失败')
            }
          })
        } else {
          uni.navigateTo({
            url: menu.path,
            fail: (err) => {
              console.error('页面跳转失败:', err)
              this.$showToast('页面跳转失败')
            }
          })
        }
      } catch (error) {
        console.error('导航到菜单失败:', error)
        this.$showToast('页面跳转失败')
      }
    },
    
    /**
     * 检查菜单权限
     */
    async checkMenuPermission(menu) {
      try {
        return permissionService.hasMenuPermission(menu.name, menu.level, this.role)
      } catch (error) {
        console.error('检查菜单权限失败:', error)
        return false
      }
    },
    
    /**
     * 判断是否为TabBar页面
     */
    isTabBarPage(path) {
      const tabBarPages = [
        '/pages/word/word',
        '/pages/tools/tools',
        '/pages/profile/profile'
      ]
      return tabBarPages.includes(path)
    },
    
    /**
     * 判断菜单是否应该显示在底部导航
     */
    isMenuInTabBar(menu) {
      const tabBarMenus = ['斩词', '学习工具', '个人中心']
      return tabBarMenus.includes(menu.name)
    }
  }
}
</script>

<style lang="scss" scoped>
.dynamic-menu {
  width: 100%;
  height: 100%;
}

/* 底部导航样式 */
.tabbar-menu {
  display: flex;
  height: 100rpx;
  background-color: #fff;
  border-top: 1rpx solid #e5e5e5;
  
  .tabbar-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10rpx 0;
    
    &.active {
      .tabbar-icon, .tabbar-text {
        transform: scale(1.1);
      }
    }
    
    .tabbar-icon {
      margin-bottom: 4rpx;
      transition: transform 0.2s ease;
    }
    
    .tabbar-text {
      font-size: 20rpx;
      transition: color 0.2s ease, transform 0.2s ease;
    }
  }
}

/* 侧边菜单样式 */
.sidebar-menu {
  width: 100%;
  height: 100%;
  background-color: #fff;
  
  .menu-scroll {
    height: 100%;
  }
  
  .menu-group {
    border-bottom: 1rpx solid #f0f0f0;
    
    .menu-item {
      padding: 24rpx 32rpx;
      border-bottom: 1rpx solid #f8f8f8;
      
      &.active {
        background-color: #f0f8ff;
        
        .menu-title {
          color: #007AFF;
          font-weight: 500;
        }
      }
      
      &.has-children {
        .menu-content {
          justify-content: space-between;
        }
      }
      
      .menu-content {
        display: flex;
        align-items: center;
        
        .menu-title {
          margin-left: 16rpx;
          font-size: 28rpx;
          color: #333;
          flex: 1;
        }
        
        .expand-icon {
          transition: transform 0.2s ease;
        }
      }
    }
    
    .submenu {
      background-color: #fafafa;
      
      .submenu-item {
        padding: 20rpx 32rpx 20rpx 64rpx;
        border-bottom: 1rpx solid #f0f0f0;
        
        &.active {
          background-color: #e6f3ff;
          
          .submenu-title {
            color: #007AFF;
            font-weight: 500;
          }
        }
        
        .submenu-content {
          display: flex;
          align-items: center;
          
          .submenu-title {
            margin-left: 12rpx;
            font-size: 26rpx;
            color: #666;
          }
        }
      }
    }
  }
}

/* 网格菜单样式 */
.grid-menu {
  padding: 32rpx;
  
  .grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160rpx, 1fr));
    gap: 32rpx;
  }
  
  .grid-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 32rpx 16rpx;
    background-color: #fff;
    border-radius: 16rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    
    &:active {
      transform: scale(0.95);
      box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.1);
    }
    
    .grid-icon {
      margin-bottom: 16rpx;
    }
    
    .grid-title {
      font-size: 24rpx;
      color: #333;
      text-align: center;
    }
  }
}
</style>