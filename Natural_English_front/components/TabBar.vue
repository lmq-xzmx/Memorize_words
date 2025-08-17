<template>
  <div class="tab-bar-container">
    <!-- 底部导航栏 -->
    <div class="tab-bar">
      <div class="tab-container">
        <!-- 斩词 -->
        <div 
          class="tab-item"
          :class="{ active: activeMenu === 'word' }"
          @click="handleWordClick"
        >
          <div class="tab-icon">
            <span class="icon chinese-icon">斩</span>
          </div>
          <div class="tab-text">斩词</div>
        </div>

        <!-- 工具 -->
        <div 
          class="tab-item"
          :class="{ active: activeMenu === 'tools' }"
          @click="handleToolsClick"
          ref="toolsTab"
        >
          <div class="tab-icon">
            <span class="icon chinese-icon">新</span>
          </div>
          <div class="tab-text">工具</div>
        </div>

        <!-- 时尚 -->
        <div 
          class="tab-item"
          :class="{ active: activeMenu === 'fashion' }"
          @click="toggleMenu('fashion')"
          ref="fashionTab"
        >
          <div class="tab-icon">
            <span class="icon chinese-icon">榜</span>
          </div>
          <div class="tab-text">时尚</div>
        </div>

        <!-- 我的 -->
        <div 
          class="tab-item"
          :class="{ active: currentTab === '/profile' }"
          @click="navigateTo('/profile')"
        >
          <div class="tab-icon">
            <span class="icon">👤</span>
          </div>
          <div class="tab-text">我的</div>
        </div>
      </div>
    </div>

    <!-- 弹出层容器 -->
    <div class="popup-container">
      <!-- 工具一级菜单（开发中心） -->
      <transition name="popup-fade">
        <div v-if="activeMenu === 'tools'" class="popup-menu tools-menu level-1" :style="toolsMenuPosition" @click.stop>
          <!-- 开发中心菜单项 -->
          <div class="menu-item dev-center-item" @click.stop="toggleDevCenter">
            <span class="menu-icon">🛠️</span>
            <span class="menu-text">开发中心</span>
            <span class="menu-arrow">{{ showDevCenter ? '▼' : '▶' }}</span>
          </div>
          
          <!-- 启用的功能菜单项（单选框模式） -->
          <div v-if="enabledMenuItems.length > 0" class="enabled-tools">
            <div class="menu-divider"></div>
            <div v-for="item in enabledMenuItems" :key="item.id" class="tool-menu-item" @click.stop>
              <input 
                type="radio" 
                :id="'radio-' + item.id"
                :value="item.id"
                v-model="selectedTool"
                @change.stop="selectTool(item)"
                class="tool-radio"
              >
              <label :for="'radio-' + item.id" class="tool-label" @click.stop>
                <span class="tool-name">{{ item.name }}</span>
              </label>
            </div>
          </div>
          
          <!-- 无启用功能时的提示 -->
          <div v-else class="no-tools-tip">
            <div class="menu-divider"></div>
            <div class="tip-text">请在开发中心启用功能</div>
          </div>
        </div>
      </transition>

      <!-- 时尚弹出菜单 -->
      <transition name="popup-fade">
        <div v-if="activeMenu === 'fashion'" class="popup-menu fashion-menu" :style="fashionMenuPosition">
          <div class="menu-item" @click="navigateTo('/community')">
            <span class="menu-icon">👥</span>
            <span class="menu-text">社区互动</span>
          </div>
          <div class="menu-item" @click="navigateTo('/fashion')">
            <span class="menu-icon">🌟</span>
            <span class="menu-text">时尚趋势</span>
          </div>
          <div class="menu-item" @click="navigateTo('/dev-index')">
            <span class="menu-icon">🔍</span>
            <span class="menu-text">发现新工具</span>
          </div>
          <div class="menu-item" @click="navigateTo('/learning-modes?no-redirect=true')">
            <span class="menu-icon">📚</span>
            <span class="menu-text">词汇阅读中心</span>
          </div>
        </div>
      </transition>

      <!-- 开发中心二级菜单 -->
      <transition name="popup-fade">
        <div v-if="showDevCenter && activeMenu === 'tools'" class="popup-menu dev-center-menu level-2" :style="devCenterMenuPosition" @click.stop>
          <div class="dev-center-header">
            <h3>开发中心 ({{ enabledMenuItems.length }}/{{ allDevTools.length }})</h3>
          </div>
          <div class="dev-tool-list">
            <div v-for="tool in allDevTools" :key="tool.id" class="dev-tool-item">
              <div class="tool-info">
                <span class="tool-icon">{{ tool.icon }}</span>
                <div class="tool-details">
                  <span class="tool-name">{{ tool.title }}</span>
                  <span class="tool-desc">{{ tool.description }}</span>
                </div>
              </div>
              <div class="tool-switch" @click.stop>
                <input 
                  type="checkbox" 
                  :id="'dev-switch-' + tool.id"
                  v-model="tool.enabled"
                  @change.stop="toggleDevTool(tool)"
                >
                <label :for="'dev-switch-' + tool.id" class="switch-label" @click.stop></label>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- 遮罩层 -->
      <transition name="overlay-fade">
        <div v-if="activeMenu || showDevCenter" class="overlay" @click="handleOverlayClick"></div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TabBar',
  props: {
    current: {
      type: String,
      default: '/dashboard'
    }
  },
  data() {
    return {
      currentTab: this.current,
      activeMenu: null, // 当前激活的菜单
      showDevCenter: false, // 显示开发中心二级页面
      selectedTool: null, // 当前选中的工具
      enabledMenuItems: [], // 启用的菜单项
      toolsMenuPosition: {}, // 工具菜单位置
      fashionMenuPosition: {}, // 时尚菜单位置
      devCenterMenuPosition: {}, // 开发中心菜单位置
      userId: null, // 当前用户ID
      allDevTools: [
        {
          id: 'word-reading',
          title: '单词阅读',
          description: 'H5版单词阅读页面，支持音频播放和进度跟踪',
          path: '/word-reading',
          icon: '📖',
          enabled: false
        },
        {
          id: 'word-learning',
          title: '单词学习',
          description: 'H5版单词学习页面，展示单词详情和多种释义',
          path: '/word-learning',
          icon: '📚',
          enabled: false
        },
        {
          id: 'word-spelling',
          title: '拼写练习',
          description: '听音拼写练习页面，提升单词记忆',
          path: '/word-learning/spelling',
          icon: '✍️',
          enabled: false
        },
        {
          id: 'word-flashcard',
          title: '闪卡学习',
          description: '翻转卡片学习单词页面',
          path: '/word-learning/flashcard',
          icon: '🃏',
          enabled: false
        },
        {
          id: 'word-detail',
          title: '单词详情',
          description: '单词详情页面，包含音标、释义、例句、词根词缀等完整信息',
          path: '/word-detail/institution',
          icon: '📝',
          enabled: false
        },
        {
          id: 'word-root-analysis',
          title: '词根分解',
          description: '词根拆解展示页面，支持词根分析和学习进度管理',
          path: '/word-root-analysis',
          icon: '🌱',
          enabled: false
        },
        {
          id: 'pattern-memory',
          title: '模式匹配记忆',
          description: '三级学习模式：图片选择、选择题、单词补全，支持多种记忆方式',
          path: '/pattern-memory',
          icon: '🧠',
          enabled: false
        },
        {
          id: 'story-reading',
          title: '故事阅读',
          description: '交互式故事阅读页面，支持词性标注和生词收集功能',
          path: '/story-reading',
          icon: '📚',
          enabled: false
        },
        {
          id: 'word-challenge',
          title: '单词挑战',
          description: '单词挑战游戏页面',
          path: '/word-challenge',
          icon: '⚔️',
          enabled: false
        },
        {
          id: 'word-review',
          title: '单词复习',
          description: '单词复习页面',
          path: '/word-review',
          icon: '🔄',
          enabled: false
        },
        {
          id: 'word-selection',
          title: '单词选择',
          description: '单词选择练习页面',
          path: '/word-selection',
          icon: '✅',
          enabled: false
        },
        {
          id: 'resource-auth',
          title: '资源授权',
          description: '资源授权管理页面，管理订阅、权限和资源分享',
          path: '/resource-auth',
          icon: '🔐',
          enabled: false
        },
        {
          id: 'subscription-management',
          title: '订阅管理',
          description: '订阅功能管理页面，查看和管理您的订阅状态',
          path: '/subscription-management',
          icon: '💳',
          enabled: false
        },
        {
          id: 'resource-sharing',
          title: '资源分享',
          description: '资源分享管理页面，分享和管理您的学习资源',
          path: '/resource-sharing',
          icon: '📤',
          enabled: false
        }
      ]
    }
  },
  watch: {
    current(newVal) {
      this.currentTab = newVal
    },
    '$route.path'(newPath) {
      this.currentTab = newPath
    },
    // 监听用户变化，重新初始化偏好设置
    userId(newUserId, oldUserId) {
      if (newUserId && newUserId !== oldUserId) {
        this.restoreUserMenuPreferences()
      }
    }
  },
  mounted() {
    // 初始化当前路径
    if (this.$route) {
      this.currentTab = this.$route.path
    }
    
    // 获取用户ID并恢复菜单偏好
    this.initializeUserPreferences()
  },
  methods: {
    // 处理斩词点击
    handleWordClick() {
      this.navigateTo('/learning-modes')
    },
    // 处理工具点击
    handleToolsClick() {
      if (this.selectedTool && this.enabledMenuItems && this.enabledMenuItems.length > 0) {
        // 如果有选中的工具，导航到对应页面
        const selectedItem = this.enabledMenuItems.find(item => item && item.id === this.selectedTool)
        if (selectedItem && selectedItem.path) {
          this.navigateTo(selectedItem.path)
          return
        }
      }
      // 否则显示工具菜单
      this.calculateMenuPosition('tools')
      this.toggleMenu('tools')
    },
    // 计算菜单位置
     calculateMenuPosition(menuType) {
       this.$nextTick(() => {
         const tabRef = menuType === 'tools' ? this.$refs.toolsTab : this.$refs.fashionTab
         if (tabRef && typeof tabRef.getBoundingClientRect === 'function') {
           const rect = tabRef.getBoundingClientRect()
           if (!rect) return
           
           const menuWidth = menuType === 'tools' ? 200 : 160 // 菜单宽度
           const windowWidth = window.innerWidth || 375 // 默认移动端宽度
           const bottomNavHeight = 60 // 底部导航栏高度
           const menuGap = 12 // 菜单与按钮的间距
           
           // 计算菜单左侧位置，确保居中对齐按钮
           let leftPosition = (rect.left || 0) + (rect.width || 0) / 2 - menuWidth / 2
           
           // 确保菜单不超出屏幕边界
           if (leftPosition < 8) {
             leftPosition = 8
           } else if (leftPosition + menuWidth > windowWidth - 8) {
             leftPosition = windowWidth - menuWidth - 8
           }
           
           // 菜单显示在按钮正上方
           const position = {
             left: leftPosition + 'px',
             bottom: (bottomNavHeight + menuGap) + 'px'
           }
           
           if (menuType === 'tools') {
             this.toolsMenuPosition = position
           } else {
             this.fashionMenuPosition = position
           }
         }
       })
     },
     // 计算开发中心二级菜单位置
     calculateDevCenterPosition() {
       this.$nextTick(() => {
         const toolsMenu = document.querySelector('.tools-menu.level-1')
         if (toolsMenu) {
           const rect = toolsMenu.getBoundingClientRect()
           const windowWidth = window.innerWidth
           const menuWidth = 320 // 二级菜单的最大宽度
           const menuGap = 8 // 菜单间距
           const bottomNavHeight = 60 // 底部导航栏高度
           
           let leftPosition = rect.right + menuGap
           
           // 如果右侧空间不够，则显示在左侧
           if (leftPosition + menuWidth > windowWidth - 8) {
             leftPosition = rect.left - menuWidth - menuGap
           }
           
           // 如果左侧也放不下，则居中显示
           if (leftPosition < 8) {
             leftPosition = (windowWidth - menuWidth) / 2
           }
           
           // 二级菜单与一级菜单底部对齐
           this.devCenterMenuPosition = {
             left: leftPosition + 'px',
             bottom: (bottomNavHeight + 12) + 'px' // 与一级菜单同一高度
           }
         }
       })
     },
    // 切换菜单显示状态
    toggleMenu(menuType) {
      if (this.activeMenu === menuType) {
        this.activeMenu = null
        this.showDevCenter = false // 关闭开发中心
      } else {
        this.activeMenu = menuType
        // 只有在切换到非工具菜单时才关闭开发中心
        if (menuType !== 'tools') {
          this.showDevCenter = false
        }
        if (menuType === 'fashion') {
          this.calculateMenuPosition('fashion')
        }
      }
    },
    // 关闭菜单
    closeMenu() {
      this.activeMenu = null
      this.showDevCenter = false
    },
    // 处理遮罩层点击
    handleOverlayClick() {
      // 关闭所有菜单状态
      this.activeMenu = null
      this.showDevCenter = false
    },
    // 导航到指定页面
    navigateTo(path) {
      this.closeMenu()
      this.currentTab = path
      this.$emit('tab-change', { path, text: '导航' })
      
      // 路由跳转
      if (this.$router) {
        this.$router.push(path)
      }
    },
    // 切换开发中心显示
    toggleDevCenter() {
      this.showDevCenter = !this.showDevCenter
      if (this.showDevCenter) {
        this.calculateDevCenterPosition()
      } else {
        // 当关闭开发中心时，也关闭一级菜单
        this.activeMenu = null
      }
    },
    // 关闭开发中心
    closeDevCenter() {
      this.showDevCenter = false
      // 同时关闭一级菜单
      this.activeMenu = null
    },
    // 切换开发工具开关
    toggleDevTool(tool) {
      if (tool.enabled) {
        // 添加到启用列表
        if (!this.enabledMenuItems.find(item => item.id === tool.id)) {
          this.enabledMenuItems.push({
            id: tool.id,
            name: tool.title,
            path: tool.path
          })
        }
      } else {
        // 从启用列表移除
        this.enabledMenuItems = this.enabledMenuItems.filter(item => item.id !== tool.id)
        // 如果当前选中的工具被禁用，清除选择
        if (this.selectedTool === tool.id) {
          this.selectedTool = null
        }
      }
      
      // 保存用户菜单偏好
      this.saveUserMenuPreferences()
    },
    // 选择工具
    selectTool(item) {
      this.selectedTool = item.id
      // 立即跳转到对应页面
      this.navigateTo(item.path)
      // 关闭工具菜单
      this.activeMenu = null
      
      // 保存用户菜单偏好
      this.saveUserMenuPreferences()
    },
    // 更新徽章（保留原有功能）
    updateBadge(path, badge) {
      // 可以根据需要实现徽章功能
      console.log('更新徽章:', path, badge)
    },
    
    // 初始化用户偏好设置
    initializeUserPreferences() {
      // 获取用户ID
      this.getUserId()
      
      // 恢复用户菜单偏好
      this.restoreUserMenuPreferences()
    },
    
    // 获取用户ID
    getUserId() {
      try {
        // 从localStorage获取用户信息
        const userInfo = localStorage.getItem('user')
        if (userInfo) {
          const user = JSON.parse(userInfo)
          this.userId = user.id || user.user_id || 'default'
        } else {
          // 如果没有用户信息，使用默认ID
          this.userId = 'default'
        }
      } catch (error) {
        console.error('获取用户ID失败:', error)
        this.userId = 'default'
      }
    },
    
    // 恢复用户菜单偏好
    restoreUserMenuPreferences() {
      try {
        const storageKey = `menuPreferences_${this.userId}`
        const savedPreferences = localStorage.getItem(storageKey)
        
        if (savedPreferences) {
          const preferences = JSON.parse(savedPreferences)
          
          // 恢复启用的菜单项
          if (preferences.enabledMenuItems) {
            this.enabledMenuItems = preferences.enabledMenuItems
          }
          
          // 恢复选中的工具
          if (preferences.selectedTool) {
            this.selectedTool = preferences.selectedTool
          }
          
          // 恢复工具启用状态
          if (preferences.toolsEnabled) {
            this.allDevTools.forEach(tool => {
              const savedTool = preferences.toolsEnabled.find(t => t.id === tool.id)
              if (savedTool) {
                tool.enabled = savedTool.enabled
              }
            })
          }
          
          console.log('用户菜单偏好已恢复:', preferences)
        }
      } catch (error) {
        console.error('恢复用户菜单偏好失败:', error)
      }
    },
    
    // 保存用户菜单偏好
    saveUserMenuPreferences() {
      try {
        const preferences = {
          enabledMenuItems: this.enabledMenuItems,
          selectedTool: this.selectedTool,
          toolsEnabled: this.allDevTools.map(tool => ({
            id: tool.id,
            enabled: tool.enabled
          })),
          lastUpdated: new Date().toISOString()
        }
        
        const storageKey = `menuPreferences_${this.userId}`
        localStorage.setItem(storageKey, JSON.stringify(preferences))
        
        console.log('用户菜单偏好已保存:', preferences)
      } catch (error) {
         console.error('保存用户菜单偏好失败:', error)
       }
     },
     
     // 重置用户偏好（用于用户登出时调用）
     resetUserPreferences() {
       this.enabledMenuItems = []
       this.selectedTool = null
       this.allDevTools.forEach(tool => {
         tool.enabled = false
       })
       this.activeMenu = null
       this.showDevCenter = false
     },
     
     // 刷新用户偏好（用于用户登录时调用）
     refreshUserPreferences() {
       this.initializeUserPreferences()
     }
   },
   
   // 组件销毁前保存用户偏好
   beforeUnmount() {
     if (this.userId && this.userId !== 'default') {
       this.saveUserMenuPreferences()
     }
   }
 }
</script>

<style lang="scss" scoped>
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem 0 calc(0.5rem + env(safe-area-inset-bottom));
  z-index: 1000;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.1);
}

.tab-container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  max-width: 500px;
  margin: 0 auto;
  padding: 0 1rem;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: $spacing-3;
  position: relative;
  min-width: 60px;
}

.tab-item:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.tab-item.active {
  background: rgba(74, 144, 226, 0.1);
  transform: scale(1.05);
}

.tab-item.active::before {
  content: '';
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background: linear-gradient(90deg, #4a90e2, #357abd);
  border-radius: $border-radius-sm;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    width: 0;
    opacity: 0;
  }
  to {
    width: 30px;
    opacity: 1;
  }
}

.tab-icon {
  font-size: 1.5rem;
  margin-bottom: 0.2rem;
  transition: all 0.3s ease;
  position: relative;
}

.tab-item.active .tab-icon {
  color: #4a90e2;
  animation: bounce 0.5s ease-out;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-3px);
  }
  60% {
    transform: translateY(-1px);
  }
}

.tab-text {
  font-size: 0.75rem;
  font-weight: $font-weight-medium;
  color: #666;
  transition: all 0.3s ease;
  text-align: center;
  line-height: 1.2;
}

.tab-item.active .tab-text {
  color: #4a90e2;
  font-weight: $font-weight-semibold;
}

/* 中文图标样式 */
.chinese-icon {
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-weight: $font-weight-semibold;
  font-size: 1.2em;
  color: #666;
  transition: all 0.3s ease;
}

.tab-item.active .chinese-icon {
  color: #4a90e2;
}

.tab-item:hover .chinese-icon {
  color: #4a90e2;
  transform: scale(1.1);
}

/* 下拉菜单样式 */
.dropdown-menu {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1rem;
  margin-bottom: 0.5rem;
  min-width: 280px;
  max-width: 320px;
  z-index: 1001;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.dropdown-menu::before {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: $spacing-2 solid transparent;
  border-right: $spacing-2 solid transparent;
  border-top: $spacing-2 solid rgba(255, 255, 255, 0.98);
}

.menu-header {
  text-align: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.menu-title {
  font-size: 1.1rem;
  font-weight: $font-weight-semibold;
  color: #333;
  margin-bottom: 0.3rem;
}

.menu-subtitle {
  font-size: 0.9rem;
  color: #666;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.8rem;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0.5rem;
  border-radius: $spacing-3;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(74, 144, 226, 0.1), transparent);
  transition: left 0.5s ease;
}

.menu-item:hover::before {
  left: 100%;
}

.menu-item:hover {
  background: rgba(74, 144, 226, 0.05);
  border-color: rgba(74, 144, 226, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.menu-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-item.disabled:hover {
  background: rgba(0, 0, 0, 0.02);
  border-color: rgba(0, 0, 0, 0.05);
  transform: none;
  box-shadow: none;
}

.menu-item-icon {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.menu-item:hover .menu-item-icon {
  transform: scale(1.1);
}

.menu-item-title {
  font-size: 0.9rem;
  font-weight: $font-weight-semibold;
  color: #333;
  text-align: center;
  margin-bottom: 0.2rem;
  position: relative;
  z-index: 1;
}

.menu-item-desc {
  font-size: 0.75rem;
  color: #666;
  text-align: center;
  line-height: 1.3;
  position: relative;
  z-index: 1;
}

/* 启用状态指示器 */
.menu-item.enabled::after {
  content: '✓';
  position: absolute;
  top: 0.3rem;
  right: 0.3rem;
  width: 18px;
  height: 18px;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
  z-index: 2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tab-container {
    padding: 0 0.5rem;
  }
  
  .tab-item {
    min-width: 50px;
    padding: 0.3rem;
  }
  
  .tab-icon {
    font-size: 1.3rem;
  }
  
  .tab-text {
    font-size: 0.7rem;
  }
  
  .dropdown-menu {
    min-width: 260px;
    max-width: 90vw;
    padding: 0.8rem;
  }
  
  .menu-grid {
    gap: 0.6rem;
  }
  
  .menu-item {
    padding: 0.8rem 0.3rem;
  }
  
  .menu-item-icon {
    font-size: 1.5rem;
  }
  
  .menu-item-title {
    font-size: 0.8rem;
  }
  
  .menu-item-desc {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .tab-item {
    min-width: 45px;
  }
  
  .tab-icon {
    font-size: 1.2rem;
    margin-bottom: 0.1rem;
  }
  
  .tab-text {
    font-size: 0.65rem;
  }
  
  .dropdown-menu {
    min-width: 240px;
    padding: 0.6rem;
  }
  
  .menu-item {
    padding: 0.6rem 0.2rem;
  }
  
  .menu-item-icon {
    font-size: 1.3rem;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .tab-bar {
    background: rgba(30, 30, 30, 0.95);
    border-top-color: rgba(255, 255, 255, 0.1);
  }
  
  .tab-item:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  .tab-item.active {
    background: rgba(74, 144, 226, 0.2);
  }
  
  .tab-text {
    color: #ccc;
  }
  
  .tab-item.active .tab-text {
    color: #4a90e2;
  }
  
  .dropdown-menu {
    background: rgba(30, 30, 30, 0.98);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  .dropdown-menu::before {
    border-top-color: rgba(30, 30, 30, 0.98);
  }
  
  .menu-title {
    color: #fff;
  }
  
  .menu-subtitle {
    color: #ccc;
  }
  
  .menu-item {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  .menu-item:hover {
    background: rgba(74, 144, 226, 0.1);
    border-color: rgba(74, 144, 226, 0.3);
  }
  
  .menu-item-title {
    color: #fff;
  }
  
  .menu-item-desc {
    color: #ccc;
  }
}

/* 动画增强 */
.tab-item {
  animation: fadeInUp 0.5s ease-out;
}

.tab-item:nth-child(1) { animation-delay: 0.1s; }
.tab-item:nth-child(2) { animation-delay: 0.2s; }
.tab-item:nth-child(3) { animation-delay: 0.3s; }
.tab-item:nth-child(4) { animation-delay: 0.4s; }
.tab-item:nth-child(5) { animation-delay: 0.5s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 触摸反馈 */
.tab-item:active {
  transform: scale(0.95);
}

.menu-item:active {
  transform: scale(0.95);
}

/* 无障碍支持 */
.tab-item:focus {
  outline: 2px solid #4a90e2;
  outline-offset: 2px;
}

.menu-item:focus {
  outline: 2px solid #4a90e2;
  outline-offset: 2px;
}

/* 加载状态 */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

.loading .tab-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

