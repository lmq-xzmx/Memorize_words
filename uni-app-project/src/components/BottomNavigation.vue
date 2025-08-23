<template>
  <view class="bottom-navigation">
    <view 
      v-for="item in filteredBottomMenus" 
      :key="item.id"
      class="nav-item"
      :class="{ 'active': activeTab === item.id, 'dropdown': item.isDropdown }"
      @click="handleNavClick(item)"
    >
      <!-- 普通菜单项 -->
      <view v-if="!item.isDropdown" class="nav-content">
        <text class="nav-icon">{{ item.icon }}</text>
        <text class="nav-title">{{ item.title }}</text>
      </view>
      
      <!-- 下拉菜单项 -->
      <view v-else class="nav-content dropdown-content">
        <text class="nav-icon">{{ item.icon }}</text>
        <text class="nav-title">{{ item.title }}</text>
        <text class="dropdown-arrow">{{ dropdownStates[item.id] ? '▲' : '▼' }}</text>
        
        <!-- 下拉菜单内容 -->
        <view 
          v-if="dropdownStates[item.id]" 
          class="dropdown-menu"
          @click.stop
        >
          <view 
            v-for="childItem in getChildMenus(item)"
            :key="childItem.id"
            class="dropdown-item"
            :class="{ 'expandable': childItem.isExpandable }"
            @click="handleDropdownItemClick(childItem)"
          >
            <text class="dropdown-icon">{{ childItem.icon }}</text>
            <text class="dropdown-title">{{ childItem.title }}</text>
            <text v-if="childItem.isExpandable" class="expand-arrow">
              {{ expandStates[childItem.id] ? '▲' : '▼' }}
            </text>
            
            <!-- 可展开子菜单 -->
            <view 
              v-if="childItem.isExpandable && expandStates[childItem.id]"
              class="expand-menu"
            >
              <view 
                v-for="subItem in getChildMenus(childItem)"
                :key="subItem.id"
                class="expand-item"
                :class="{ 'disabled': !subItem.enabled }"
                @click="handleExpandItemClick(subItem)"
              >
                <text class="expand-icon">{{ subItem.icon }}</text>
                <text class="expand-title">{{ subItem.title }}</text>
                <text class="expand-status" :class="subItem.enabled ? 'enabled' : 'disabled'">
                  {{ subItem.status }}
                </text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { MENU_ITEMS, MENU_UTILS } from '@/config/menuConfig.js'

export default {
  name: 'BottomNavigation',
  props: {
    userPermissions: {
      type: Array,
      default: () => ['view_word_learning', 'view_own_profile'] // 默认基础权限
    },
    activeTab: {
      type: String,
      default: 'word-slash'
    }
  },
  data() {
    return {
      dropdownStates: {}, // 下拉菜单展开状态
      expandStates: {}    // 可展开菜单状态
    }
  },
  computed: {
    // 根据权限过滤底部菜单
    filteredBottomMenus() {
      return MENU_UTILS.filterMenuByPermissions(
        MENU_ITEMS.BOTTOM_MENUS,
        this.userPermissions
      )
    }
  },
  methods: {
    /**
     * 处理导航点击事件
     */
    handleNavClick(item) {
      if (item.isDropdown) {
        // 切换下拉菜单状态
        this.$set(this.dropdownStates, item.id, !this.dropdownStates[item.id])
        // 关闭其他下拉菜单
        Object.keys(this.dropdownStates).forEach(key => {
          if (key !== item.id) {
            this.$set(this.dropdownStates, key, false)
          }
        })
      } else {
        // 普通菜单项导航
        this.navigateToPage(item)
        this.$emit('tab-change', item.id)
      }
    },

    /**
     * 处理下拉菜单项点击
     */
    handleDropdownItemClick(item) {
      if (item.isExpandable) {
        // 切换展开状态
        this.$set(this.expandStates, item.id, !this.expandStates[item.id])
      } else {
        this.navigateToPage(item)
      }
    },

    /**
     * 处理可展开菜单项点击
     */
    handleExpandItemClick(item) {
      if (!item.enabled) {
        uni.showToast({
          title: `${item.title}功能暂未启用`,
          icon: 'none'
        })
        return
      }
      this.navigateToPage(item)
    },

    /**
     * 获取子菜单
     */
    getChildMenus(item) {
      const childMenus = MENU_UTILS.getChildrenMenus(item)
      return MENU_UTILS.filterMenuByPermissions(childMenus, this.userPermissions)
    },

    /**
     * 页面导航
     */
    navigateToPage(item) {
      if (!item.path) return
      
      // 关闭所有下拉菜单
      Object.keys(this.dropdownStates).forEach(key => {
        this.$set(this.dropdownStates, key, false)
      })
      
      // 导航到目标页面
      uni.navigateTo({
        url: item.path,
        fail: (err) => {
          console.error('导航失败:', err)
          uni.showToast({
            title: '页面跳转失败',
            icon: 'none'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.bottom-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 120rpx;
  background: #ffffff;
  border-top: 1rpx solid #e5e5e5;
  display: flex;
  align-items: center;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
  z-index: 1000;

  .nav-item {
    flex: 1;
    position: relative;
    
    .nav-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 10rpx;
      height: 100rpx;
      transition: all 0.3s ease;
      
      .nav-icon {
        font-size: 44rpx;
        margin-bottom: 4rpx;
        transition: transform 0.2s ease;
      }
      
      .nav-title {
        font-size: 24rpx;
        color: #666666;
        transition: color 0.2s ease;
      }
      
      .dropdown-arrow {
        position: absolute;
        top: 8rpx;
        right: 8rpx;
        font-size: 20rpx;
        color: #999999;
        transition: transform 0.2s ease;
      }
    }
    
    &.active .nav-content {
      .nav-icon {
        transform: scale(1.1);
      }
      
      .nav-title {
        color: #007aff;
        font-weight: 500;
      }
    }
    
    &.dropdown .nav-content:hover {
      background: rgba(0, 122, 255, 0.05);
      border-radius: 12rpx;
    }
  }

  /* 下拉菜单样式 */
  .dropdown-menu {
    position: absolute;
    bottom: 120rpx;
    left: 50%;
    transform: translateX(-50%);
    min-width: 300rpx;
    background: #ffffff;
    border-radius: 16rpx;
    box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
    border: 1rpx solid #e5e5e5;
    overflow: hidden;
    animation: slideUp 0.3s ease;
  }
  
  .dropdown-item {
    padding: 24rpx 32rpx;
    border-bottom: 1rpx solid #f5f5f5;
    display: flex;
    align-items: center;
    position: relative;
    transition: background 0.2s ease;
  }
  
  .dropdown-item:last-child {
    border-bottom: none;
  }
  
  .dropdown-item:hover {
    background: rgba(0, 122, 255, 0.05);
  }
  
  .dropdown-icon {
    font-size: 32rpx;
    margin-right: 16rpx;
  }
  
  .dropdown-title {
    flex: 1;
    font-size: 28rpx;
    color: #333333;
  }
  
  .expand-arrow {
    font-size: 20rpx;
    color: #999999;
    transition: transform 0.2s ease;
  }
  
  .dropdown-item.expandable .expand-arrow {
    transform: rotate(0deg);
  }

  /* 可展开菜单样式 */
  .expand-menu {
    position: absolute;
    top: 0;
    left: 100%;
    min-width: 280rpx;
    background: #ffffff;
    border-radius: 12rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
    border: 1rpx solid #e5e5e5;
    margin-left: 8rpx;
    overflow: hidden;
    animation: slideRight 0.2s ease;
  }
  
  .expand-item {
    padding: 20rpx 24rpx;
    border-bottom: 1rpx solid #f5f5f5;
    display: flex;
    align-items: center;
    transition: background 0.2s ease;
  }
  
  .expand-item:last-child {
    border-bottom: none;
  }
  
  .expand-item:not(.disabled):hover {
    background: rgba(0, 122, 255, 0.05);
  }
  
  .expand-item.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .expand-icon {
    font-size: 28rpx;
    margin-right: 12rpx;
  }
  
  .expand-title {
    flex: 1;
    font-size: 26rpx;
    color: #333333;
  }
  
  .expand-status {
    font-size: 20rpx;
    padding: 4rpx 8rpx;
    border-radius: 8rpx;
  }
  
  .expand-status.enabled {
    background: #e8f5e8;
    color: #52c41a;
  }
  
  .expand-status.disabled {
    background: #f5f5f5;
    color: #999999;
  }
}

/* 动画效果 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes slideRight {
  from {
    opacity: 0;
    transform: translateX(-20rpx);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media screen and (max-width: 750rpx) {
  .bottom-navigation .dropdown-menu {
    min-width: 250rpx;
  }
  
  .bottom-navigation .expand-menu {
    min-width: 220rpx;
  }
}
</style>