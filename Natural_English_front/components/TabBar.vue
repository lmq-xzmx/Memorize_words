<template>
  <div class="tab-bar-container">
    <!-- 底部导航栏 -->
    <div class="tab-bar">
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
      if (this.selectedTool && this.enabledMenuItems.length > 0) {
        // 如果有选中的工具，导航到对应页面
        const selectedItem = this.enabledMenuItems.find(item => item.id === this.selectedTool)
        if (selectedItem) {
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
         if (tabRef) {
           const rect = tabRef.getBoundingClientRect()
           const position = {
             left: rect.left + rect.width / 2 + 'px',
             transform: 'translateX(-50%)'
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
           
           let leftPosition = rect.right + 8
           
           // 如果右侧空间不够，则显示在左侧
           if (leftPosition + menuWidth > windowWidth) {
             leftPosition = rect.left - menuWidth - 8
           }
           
           // 确保不超出屏幕左边界
           if (leftPosition < 8) {
             leftPosition = 8
           }
           
           this.devCenterMenuPosition = {
             left: leftPosition + 'px',
             bottom: '68px'
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

<style scoped>
.tab-bar-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
}

.tab-bar {
  height: 60px;
  background: #ffffff;
  border-top: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-around;
  /* 适配安全区域 */
  padding-bottom: env(safe-area-inset-bottom);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10000;
}

.popup-container {
  position: absolute;
  bottom: 60px;
  left: 0;
  right: 0;
  pointer-events: none;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tab-item:active {
  transform: scale(0.95);
}

.tab-icon {
  position: relative;
  margin-bottom: 2px;
}

.icon {
  font-size: 22px;
  display: block;
  transition: all 0.3s ease;
}

.chinese-icon {
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-weight: bold;
  font-size: 24px;
  color: #333;
}

.tab-item.active .icon {
  transform: scale(1.1);
}

.tab-item.active .chinese-icon {
  color: #007aff;
}

.badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff4757;
  color: white;
  border-radius: 10px;
  min-width: 16px;
  height: 16px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  box-sizing: border-box;
}

.tab-text {
  font-size: 10px;
  color: #999999;
  transition: all 0.3s ease;
  line-height: 1;
}

.tab-item.active .tab-text {
  color: #007aff;
  font-weight: 600;
}

.tab-item.active {
  color: #007aff;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .tab-bar {
    background: #1c1c1e;
    border-top-color: #38383a;
  }
  
  .tab-text {
    color: #8e8e93;
  }
  
  .tab-item.active .tab-text {
    color: #007aff;
  }
}

/* 小程序适配 */
@media screen and (max-width: 750px) {
  .tab-bar {
    height: 50px;
  }
  
  .icon {
    font-size: 20px;
  }
  
  .tab-text {
    font-size: 9px;
  }
}

/* iOS安全区域适配 */
@supports (bottom: env(safe-area-inset-bottom)) {
  .tab-bar {
    padding-bottom: calc(env(safe-area-inset-bottom) + 4px);
    height: calc(60px + env(safe-area-inset-bottom));
  }
}

/* 弹出菜单样式 */
.popup-menu {
  position: fixed;
  bottom: 68px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  padding: 8px 0;
  z-index: 10001;
  pointer-events: auto;
}

/* 一级菜单样式 */
.popup-menu.level-1 {
  z-index: 10001;
}

/* 二级菜单样式 */
.popup-menu.level-2 {
  z-index: 10002;
  min-width: 280px;
  max-width: 320px;
  max-height: 400px;
  overflow-y: auto;
  position: fixed;
}

.popup-menu::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: white;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.2s ease;
  white-space: nowrap;
  position: relative;
}

.menu-item:hover {
  background: #f5f5f5;
}

.menu-item:active {
  background: #e8e8e8;
  transform: scale(0.98);
}

.dev-center-item {
  justify-content: space-between;
}

.menu-arrow {
  font-size: 12px;
  color: #666;
  transition: transform 0.3s ease;
}

.menu-item:first-child {
  border-radius: 12px 12px 0 0;
}

.menu-item:last-child {
  border-radius: 0 0 12px 12px;
}

/* 工具菜单特殊样式 */
.tools-menu {
  min-width: 200px;
  max-width: 250px;
  padding: 8px 0;
}

.menu-icon {
  margin-right: 8px;
  font-size: 16px;
}

.menu-text {
  font-size: 14px;
}

/* 菜单分隔线 */
.menu-divider {
  height: 1px;
  background: #e5e5e5;
  margin: 8px 16px;
}

/* 启用的工具菜单项 */
.enabled-tools {
  padding: 0;
}

.tool-menu-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.tool-menu-item:hover {
  background: #f5f5f5;
}

.tool-radio {
  margin-right: 8px;
  cursor: pointer;
}

.tool-label {
  flex: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.tool-label .tool-name {
  font-size: 14px;
  color: #333;
}

/* 无功能提示样式 */
.no-tools-tip {
  padding: 0;
}

.tip-text {
  padding: 12px 16px;
  font-size: 13px;
  color: #999;
  text-align: center;
  font-style: italic;
}

/* 开发中心二级菜单样式 */
.dev-center-menu {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 0;
}

.dev-center-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #f8f9fa;
  border-radius: 12px 12px 0 0;
}

.dev-center-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.dev-tool-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 8px 0;
}

.dev-tool-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f5;
  transition: background-color 0.2s ease;
}

.dev-tool-item:hover {
  background-color: #f8f9fa;
}

.dev-tool-item:last-child {
  border-bottom: none;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s ease;
}

.close-btn:hover {
  background: #e9ecef;
}

/* 移除旧的dev-tool-cards样式，使用新的dev-tool-list */

.dev-tool-item .tool-info {
  flex: 1;
  display: flex;
  align-items: center;
}

.tool-icon {
  font-size: 24px;
  margin-right: 12px;
}

.tool-details {
  flex: 1;
}

.dev-tool-item .tool-name {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.dev-tool-item .tool-desc {
  display: block;
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

/* 开关按钮样式 */
.tool-switch {
  position: relative;
}

.tool-switch input[type="checkbox"] {
  display: none;
}

.switch-label {
  display: block;
  width: 44px;
  height: 24px;
  background: #ccc;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.3s ease;
  position: relative;
}

.switch-label::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.tool-switch input[type="checkbox"]:checked + .switch-label {
  background: #007aff;
}

.tool-switch input[type="checkbox"]:checked + .switch-label::after {
  transform: translateX(20px);
}

/* 遮罩层样式 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9998;
  pointer-events: auto;
}

/* 动画效果 */
/* 弹出菜单动画 */
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: all 0.3s ease;
}

.popup-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.popup-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 模态框动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-from {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
}

.modal-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
}

/* 遮罩层动画 */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.3s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* Android适配 */
@media screen and (max-height: 640px) {
  .tab-bar {
    height: 50px;
  }
  
  .tab-item {
    padding: 2px 0;
  }
  
  .tools-menu {
    min-width: 180px;
    max-width: 220px;
  }
  
  .dev-center-popup {
    width: 95vw;
    max-height: 70vh;
  }
  
  .dev-tool-cards {
    max-height: calc(70vh - 80px);
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .dev-center-popup {
    background: #1c1c1e;
    color: white;
  }
  
  .dev-center-header {
    background: #2c2c2e;
    border-bottom-color: #38383a;
  }
  
  .dev-center-header h3 {
    color: white;
  }
  
  .close-btn {
    color: #8e8e93;
  }
  
  .close-btn:hover {
    background: #38383a;
  }
  
  .dev-tool-card {
    background: #2c2c2e;
    border-color: #38383a;
  }
  
  .dev-tool-card:hover {
    background: #38383a;
  }
  
  .dev-tool-card .tool-name {
    color: white;
  }
  
  .dev-tool-card .tool-desc {
    color: #8e8e93;
  }
  
  .menu-divider {
    background: #38383a;
  }
  
  .tool-label .tool-name {
    color: white;
  }
}
</style>